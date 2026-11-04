"""In-memory, lexical near-duplicate suppression.

The bot runs as a single asyncio process, so a plain module-level dict keyed by
destination chat id is shared across the live userbot, the backfill task and the
RSS poller for free. Comparison is purely letter-by-letter (no embeddings, no
network): we normalise the text, then compare it against a short sliding window
of recently published captions for the same destination.

TWO complementary similarity signals are computed for every candidate, and a
pair counts as a duplicate when EITHER one reaches the threshold (the stronger
signal wins):

  1. char-order ratio  — difflib SequenceMatcher on the normalised strings.
     Sensitive to word ORDER; great at catching copy-paste re-posts.
  2. order-free ratio  — a bag-of-words / bag-of-letters overlap that ignores
     ordering entirely; great at catching a re-worded or re-arranged re-post
     of the SAME story that signal 1 misses.

Taking max(signal1, signal2) means a re-post is caught whether it is a literal
copy OR a re-ordering, WITHOUT having to lower the threshold. This is strictly
ADDITIVE: the original char-order check is unchanged, the second signal only
adds detections.

The window is keyed by destination and is INTENTIONALLY CROSS-SOURCE: posts
from every source feeding a destination share one window, so the same story
republished by two different feeds is caught. (A per-source exact-id watermark
still runs separately in the delivery path and is unaffected.)

`is_duplicate()` is intentionally a synchronous function. Because it both reads
and mutates the window with no `await` in between, the asyncio event loop can
never interleave two callers mid-check — this closes the live-vs-backfill race
where the same story arriving on two sources could both pass the gate.
"""

import re
import time
import unicodedata
from collections import deque
from difflib import SequenceMatcher

# dest_chat_id -> deque[(ts_epoch, norm_text, exact_hash)]
_WINDOWS = {}
# dest_chat_id -> set of exact normalised hashes currently in the window
_HASHES = {}

# Hard cap on window size per destination, so a very long/high threshold can
# never let the deque grow without bound. Kept modest for free-tier CPU safety
# (the per-candidate comparison is O(window) with a cheap pre-check).
_MAX_ITEMS = 300

# Arabic -> Persian letter unification and other common look-alikes.
_CHAR_MAP = {
    "\u0643": "\u06a9",  # Arabic kaf -> Persian keheh
    "\u064a": "\u06cc",  # Arabic yeh -> Persian yeh
    "\u0649": "\u06cc",  # Alef maksura -> Persian yeh
    "\u0629": "\u0647",  # Teh marbuta -> heh
    "\u0622": "\u0627",  # Alef with madda -> alef
    "\u0623": "\u0627",  # Alef with hamza above -> alef
    "\u0625": "\u0627",  # Alef with hamza below -> alef
    "\u0624": "\u0648",  # Waw with hamza -> waw
    "\u0626": "\u06cc",  # Yeh with hamza -> Persian yeh
    "\u200c": " ",       # ZWNJ -> space
    "\u200d": "",        # ZWJ
    "\u200f": "",        # RTL mark
    "\u200e": "",        # LTR mark
    "\u0640": "",        # Tatweel/kashida
}

# Arabic/Persian diacritics (harakat) to strip.
_DIACRITICS = re.compile("[\u064b-\u0652\u0670]")

# Persian/Arabic-Indic digits -> ASCII.
_DIGIT_MAP = {}
for _base in ("\u06f0", "\u0660"):  # Persian 0, Arabic 0
    for _i in range(10):
        _DIGIT_MAP[chr(ord(_base) + _i)] = str(_i)

_NON_WORD = re.compile(r"[^\w\u0600-\u06ff]+", re.UNICODE)

# ---------------------------------------------------------------------------
# Runtime-editable synonym dictionary (owner-managed from the Settings menu).
# Maps an alternate spelling -> its canonical form, applied as whole-word
# replacements during normalisation so two spellings of the same word collapse
# to one token before comparison. Seeded with a few common Persian pairs; the
# owner can add/remove entries at runtime (see set_synonyms / get_synonyms).
# ---------------------------------------------------------------------------
_DEFAULT_SYNONYMS = [
    ("\u0647\u0633\u062a", "\u0627\u0633\u062a"),          # هست -> است
    ("\u062a\u0628\u0644\u06cc\u063a\u0627\u062a", "\u062a\u0628\u0644\u06cc\u063a"),  # تبلیغات -> تبلیغ
    ("\u067e\u0647\u0628\u0627\u062f", "\u067e\u0647\u067e\u0627\u062f"),  # پهباد -> پهپاد
    ("\u0627\u0645\u0631\u06cc\u06a9\u0627", "\u0622\u0645\u0631\u06cc\u06a9\u0627"),  # امریکا -> آمریکا (then fold Å/آ below)
]

# In-memory overlay of the owner-managed synonyms (loaded from the DB at
# startup and updated whenever the owner edits them). List of (from, to).
_SYNONYMS = list(_DEFAULT_SYNONYMS)
# Compiled whole-word matchers, rebuilt only when the dictionary changes.
_SYNONYM_RE = None


def _rebuild_synonym_re():
    """Compile one whole-word alternation for all synonym keys so replacement
    is a single pass and can never partially rewrite a longer word."""
    global _SYNONYM_RE
    pairs = [(a, b) for (a, b) in _SYNONYMS if a and b and a != b]
    if not pairs:
        _SYNONYM_RE = None
        return
    # Longest keys first so a longer synonym is tried before a shorter prefix.
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    _SYNONYM_RE = (pairs, re.compile(
        r"(?<!\w)(" + "|".join(re.escape(a) for a, _ in pairs) + r")(?!\w)"
    ))


def get_synonyms():
    """Return the current synonym list as a list of (from, to) tuples."""
    return list(_SYNONYMS)


def set_synonyms(pairs):
    """Replace the runtime synonym dictionary (list of (from, to))."""
    global _SYNONYMS
    cleaned = []
    for a, b in pairs or []:
        a = (a or "").strip()
        b = (b or "").strip()
        if a and b and a != b:
            cleaned.append((a, b))
    _SYNONYMS = cleaned
    _rebuild_synonym_re()


_rebuild_synonym_re()


def _apply_synonyms(s):
    """Whole-word synonym folding on an already lower-cased string."""
    if not s or _SYNONYM_RE is None:
        return s
    pairs, rx = _SYNONYM_RE
    table = dict(pairs)
    return rx.sub(lambda m: table.get(m.group(1), m.group(1)), s)


def normalize(text):
    """Fold text to a comparable canonical form.

    Strips emoji/symbols, URLs, @handles and #hashtags, unifies Arabic vs
    Persian letters and digits, removes diacritics, applies the owner's synonym
    dictionary and collapses whitespace.
    """
    if not text:
        return ""
    s = unicodedata.normalize("NFKC", text)
    # Drop URLs and @mentions / #tags — these are the noisy bits that differ
    # between re-posts of the same story.
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"[@#]\w+", " ", s)
    s = s.translate(str.maketrans(_CHAR_MAP))
    s = s.translate(str.maketrans(_DIGIT_MAP))
    s = _DIACRITICS.sub("", s)
    # Remove emoji and pictographs by category (So = Symbol, other).
    s = "".join(ch for ch in s if unicodedata.category(ch) not in ("So", "Sk", "Cf"))
    s = _NON_WORD.sub(" ", s)
    s = s.lower().strip()
    # Owner-managed synonym folding (است = هست, تبلیغ = تبلیغات, ...).
    s = _apply_synonyms(s)
    s = re.sub(r"\s+", " ", s)
    return s


def _tokens(norm):
    return norm.split()


def _order_free_ratio(norm_a, norm_b):
    """Order-free similarity in three layers, strongest applicable wins.

    Layer 1 — multi-word bag-of-words Jaccard (word multiset overlap):
        ignores word ORDER and duplicate repetition; the primary signal.
    Layer 2 — micro containment on words (shared / smaller side):
        catches a short post fully contained inside a longer one.
    Layer 3 — bag-of-letters (character multiset) over the long no-space
        strings: catches a scrambled-order re-post where even the words were
        reshuffled («امروز چهارشنبه است» vs «چهارشنبه هست امروز»).

    Returns a value in 0..1, the max of the applicable layers.
    """
    if not norm_a or not norm_b:
        return 0.0
    ta, tb = _tokens(norm_a), _tokens(norm_b)

    best = 0.0
    if ta and tb:
        from collections import Counter as _C
        ca, cb = _C(ta), _C(tb)
        inter = sum((ca & cb).values())
        union = sum((ca | cb).values())
        if union:
            best = inter / union                      # layer 1: word Jaccard
        smaller = min(sum(ca.values()), sum(cb.values()))
        if smaller:
            best = max(best, inter / smaller)          # layer 2: containment over words
        if len(ta) == len(tb):
            # equal-length posts (common for near-copies): order-free equality
            best = max(best, inter / max(sum(ca.values()), sum(cb.values())))

    # layer 3: bag-of-letters over the long string (order entirely ignored).
    na, nb = norm_a.replace(" ", ""), norm_b.replace(" ", "")
    if na and nb:
        from collections import Counter as _C
        ca, cb = _C(na), _C(nb)
        inter = sum((ca & cb).values())
        letters = inter / max(sum(ca.values()), sum(cb.values()))
        best = max(best, letters)
    return best


def _prune(dq, hashes, now, window_sec):
    cutoff = now - window_sec
    while dq and dq[0][0] < cutoff:
        _, _, h = dq.popleft()
        hashes.discard(h)
    while len(dq) > _MAX_ITEMS:
        _, _, h = dq.popleft()
        hashes.discard(h)


def is_duplicate(dest_chat_id, text, window_min, threshold_pct, min_len):
    """Return True if `text` is a near-duplicate of something recently posted
    to `dest_chat_id`. First-seen wins: a non-duplicate is recorded, a
    duplicate is reported and NOT recorded.

    A candidate is a duplicate when EITHER the char-order ratio OR the
    order-free ratio reaches the threshold (max of the two signals).

    Synchronous on purpose (atomic within the event loop).
    """
    global _checked, _dropped
    _checked += 1

    norm = normalize(text)
    # Too short to judge reliably — never treat as a duplicate, never record.
    if len(norm) < max(1, int(min_len)):
        return False

    now = time.time()
    window_sec = max(1, int(window_min)) * 60
    thr = max(0.0, min(1.0, float(threshold_pct) / 100.0))

    dq = _WINDOWS.setdefault(dest_chat_id, deque())
    hashes = _HASHES.setdefault(dest_chat_id, set())
    _prune(dq, hashes, now, window_sec)

    h = hash(norm)
    if h in hashes:
        _dropped += 1
        return True  # exact normalised match, cheap path

    matcher = SequenceMatcher(a=norm)
    # Pre-compute the order-free token multiset for the candidate ONCE; the
    # per-comparison work is then a cheap Counter intersection.
    from collections import Counter as _C
    cand_tokens = _C(_tokens(norm))
    cand_letters = _C(norm.replace(" ", ""))
    cand_len = len(norm)

    for _ts, prev_norm, _h in dq:
        # --- cheap pre-check: length ratio bound (differs by >2.2x -> skip).
        plen = len(prev_norm)
        if plen and cand_len:
            ratio = cand_len / plen
            if ratio > 2.2 or ratio < (1 / 2.2):
                # Even a perfect containment can't reach a high threshold when
                # the lengths differ this much; skip the expensive compare.
                if thr > 0.6:
                    continue
        # --- signal 1: char-order ratio (the original check, unchanged).
        matcher.set_seq2(prev_norm)
        if matcher.quick_ratio() >= thr and matcher.ratio() >= thr:
            _dropped += 1
            return True
        # --- signal 2: order-free ratio (word + letter bag overlap).
        prev_tokens = _C(_tokens(prev_norm))
        inter = sum((cand_tokens & prev_tokens).values())
        union = sum((cand_tokens | prev_tokens).values())
        jac = (inter / union) if union else 0.0
        smaller = min(sum(cand_tokens.values()), sum(prev_tokens.values()))
        cont = (inter / smaller) if smaller else 0.0
        prev_letters = _C(prev_norm.replace(" ", ""))
        linter = sum((cand_letters & prev_letters).values())
        ldenom = max(sum(cand_letters.values()), sum(prev_letters.values()))
        letters = (linter / ldenom) if ldenom else 0.0
        if max(jac, cont, letters) >= thr:
            _dropped += 1
            return True

    # First time we've seen this — record and let it through.
    dq.append((now, norm, h))
    hashes.add(h)
    return False


def reset(dest_chat_id=None):
    """Clear window state (mainly for tests)."""
    if dest_chat_id is None:
        _WINDOWS.clear()
        _HASHES.clear()
    else:
        _WINDOWS.pop(dest_chat_id, None)
        _HASHES.pop(dest_chat_id, None)


# Running counters for /status display.
_checked = 0
_dropped = 0


def stats():
    """Return a snapshot of dedup stats for /status display."""
    global _checked, _dropped
    # Recount tracked destinations from the live data structures.
    tracked = len(_WINDOWS)
    return {"checked": _checked, "dropped": _dropped, "tracked": tracked}
