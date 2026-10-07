"""In-memory, lexical near-duplicate suppression.

The bot runs as a single asyncio process, so a plain module-level dict keyed by
destination chat id is shared across the live userbot, the backfill task and the
RSS poller for free. Comparison is purely letter-by-letter (no embeddings, no
network): we normalise the text, then compare it against a short sliding window
of recently published captions for the same destination using difflib.

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
# never let the deque grow without bound.
_MAX_ITEMS = 400

# Arabic -> Persian letter unification and other common look-alikes.
_CHAR_MAP = {
    "\u0643": "\u06a9",  # Arabic kaf -> Persian keheh
    "\u064a": "\u06cc",  # Arabic yeh -> Persian yeh
    "\u0649": "\u06cc",  # Alef maksura -> Persian yeh
    "\u0629": "\u0647",  # Teh marbuta -> heh
    "\u200c": " ",       # ZWNJ -> space
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


def normalize(text):
    """Fold text to a comparable canonical form.

    Strips emoji/symbols, URLs, @handles and #hashtags, unifies Arabic vs
    Persian letters and digits, removes diacritics and collapses whitespace.
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
    s = re.sub(r"\s+", " ", s)
    return s


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
    for _ts, prev_norm, _h in dq:
        matcher.set_seq2(prev_norm)
        # quick_ratio is an upper bound; skip the expensive ratio() when the
        # candidate cannot possibly reach the threshold.
        if matcher.quick_ratio() < thr:
            continue
        if matcher.ratio() >= thr:
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
