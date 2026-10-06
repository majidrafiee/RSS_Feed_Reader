import html
import re

_TAG = re.compile(r"<[^>]+>")

# ---------------------------------------------------------------------------
# Trailing-footer stripping.
#
# Our own bottom credit line already NAMES and LINKS the source, so any trailing
# links the source channel tacked on (full-article URLs, bare domains, t.me
# links, @handles, "read more / details below" call-to-action lines and
# photo-credit lines) are redundant clutter and must go. We only ever touch the
# CONTIGUOUS trailing block, and only when that block actually contains a
# link/handle/domain — so a normal closing sentence is never deleted by accident.
# ---------------------------------------------------------------------------

# "Read the full story at the link below", "details below", etc. (Persian + English).
_CTA_WORDS = re.compile(
    r"\u0644\u06cc\u0646\u06a9 \u0632\u06cc\u0631|\u0627\u0632 \u0644\u06cc\u0646\u06a9|"
    r"\u0627\u062f\u0627\u0645\u0647 \u062e\u0628\u0631|\u0627\u062f\u0627\u0645\u0647 \u0645\u0637\u0644\u0628|"
    r"\u0627\u062f\u0627\u0645\u0647 \u0645\u0637\u0627\u0644\u0628|\u0627\u062f\u0627\u0645\u0647 \u062f\u0631|"
    r"\u062c\u0632\u0626\u06cc\u0627\u062a \u062f\u0631|\u062c\u0632\u0626\u06cc\u0627\u062a \u0628\u06cc\u0634\u062a\u0631|"
    r"\u0645\u062a\u0646 \u06a9\u0627\u0645\u0644|\u0628\u06cc\u0634\u062a\u0631 \u0628\u062e\u0648\u0627\u0646\u06cc\u062f|"
    r"\u06a9\u0644\u06cc\u06a9 \u06a9\u0646\u06cc\u062f|\u0627\u06cc\u0646\u062c\u0627 \u06a9\u0644\u06cc\u06a9|"
    r"\u0645\u0634\u0627\u0647\u062f\u0647 \u06a9\u0646\u06cc\u062f|\u0645\u0637\u0627\u0644\u0639\u0647 \u0628\u06cc\u0634\u062a\u0631|"
    r"\u0628\u0631\u0627\u06cc \u0645\u0637\u0627\u0644\u0639\u0647|\u0644\u06cc\u0646\u06a9 \u062e\u0628\u0631|"
    r"\u062f\u0631 \u0644\u06cc\u0646\u06a9|"
    r"read more|read the full|full (?:article|story|report|text)|"
    r"click here|see more|link below|more details",
    re.IGNORECASE,
)
# Down-pointer emoji "details below/here" — a strong CTA signal.
_DOWN_POINTER = re.compile("[\U0001F447\U0001F449]")
# Camera / photo-credit lines, e.g. a camera emoji then 'Getty Images'.
_PHOTO_CREDIT = re.compile("^[\\s\\W_]*[\U0001F4F7\U0001F4F8\U0001F3A5\U0001F5BC]")

_HTTP_TOKEN = re.compile(r"^https?://", re.IGNORECASE)
_HANDLE_TOKEN = re.compile(r"^@[A-Za-z0-9_]{3,}$")
# bare domain, optionally with a path: khabaronline.ir/xqrqX, bbc.in/4yAJJ8V,
# t.me/foo. ASCII-only, so Persian/Arabic words can never match it.
_DOMAIN_TOKEN = re.compile(
    r"^(?:[a-z0-9][a-z0-9-]*\.)+[a-z]{2,}(?:/[^\s]*)?$", re.IGNORECASE
)


def _classify_token(tok: str) -> str:
    """Classify one whitespace/pipe-separated token of a trailing line as a
    'link' (url/handle/domain), a 'sep' (emoji/punctuation only), or a 'word'
    (real text)."""
    core = tok.strip().strip("\u200c\u200f\u200e\u2066\u2067\u2068\u2069")
    core = re.sub(r"^[^\w@]+", "", core)              # peel leading emoji/punct
    core = re.sub(r"[^\w/.:=?&%#@~+-]+$", "", core)   # peel trailing emoji/punct
    if not core:
        return "sep"
    low = core.lower()
    if _HTTP_TOKEN.match(core) or low.startswith("t.me/"):
        return "link"
    if _HANDLE_TOKEN.match(core) or _DOMAIN_TOKEN.match(core):
        return "link"
    if re.fullmatch(r"[\W_]+", core):
        return "sep"
    return "word"


def _is_link_line(line: str) -> bool:
    """True when a line is made up ONLY of links/handles/domains (plus emoji or
    separators) — e.g. a bare URL or '@KhabarOnline_ir | Khabaronline.ir'."""
    s = line.strip()
    if not s:
        return False
    toks = [t for t in re.split(r"[\s|]+", s) if t]
    has_link = False
    for t in toks:
        c = _classify_token(t)
        if c == "word":
            return False
        if c == "link":
            has_link = True
    return has_link


def _is_cta_line(line: str) -> bool:
    """True for short 'read more / details below' call-to-action lines."""
    s = line.strip()
    if not s or len(s) > 80:
        return False
    if _DOWN_POINTER.search(s):
        return True
    return bool(_CTA_WORDS.search(s))


def _is_photo_credit_line(line: str) -> bool:
    s = line.strip()
    if not s or len(s) > 50:
        return False
    return bool(_PHOTO_CREDIT.match(s))


def strip_source_signature(text: str) -> str:
    """Remove the source channel's trailing footer — links, bare domains, t.me
    links, @handles, 'read more' call-to-action lines and photo credits — from
    the END of a post. Our own bottom credit line already links the source, so
    these are redundant clutter.

    Only the CONTIGUOUS trailing block is examined, and it is stripped ONLY if
    it contains at least one real link/handle/domain. That safety rule means a
    normal closing sentence (even one that happens to match a CTA phrase) is
    never deleted when there is no link to justify it.
    """
    if not text:
        return text
    lines = text.split("\n")
    i = len(lines) - 1
    block_start = len(lines)
    has_link = False
    while i >= 0:
        s = lines[i].strip()
        if s == "":
            block_start = i
            i -= 1
            continue
        if _is_link_line(lines[i]):
            has_link = True
            block_start = i
            i -= 1
            continue
        if _is_cta_line(lines[i]) or _is_photo_credit_line(lines[i]):
            block_start = i
            i -= 1
            continue
        break  # real content line — stop
    if not has_link:
        return text.rstrip()
    return "\n".join(lines[:block_start]).rstrip()


def esc(text: str) -> str:
    """HTML-escape text for Telegram HTML parse mode."""
    return html.escape(text or "", quote=False)


def strip_html(text: str) -> str:
    """Remove HTML tags (common in RSS summaries) and unescape entities."""
    if not text:
        return ""
    text = _TAG.sub("", text)
    return html.unescape(text).strip()


def truncate(text: str, limit: int) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "\u2026"


def chunk(text: str, size: int):
    """Split plain text into pieces no longer than size, preferring to break
    on a newline so we never cut in the middle of a word/sentence."""
    text = text or ""
    if len(text) <= size:
        return [text]
    parts = []
    while text:
        if len(text) <= size:
            parts.append(text)
            break
        cut = text.rfind("\n", 0, size)
        if cut < size // 2:
            cut = text.rfind(" ", 0, size)
        if cut <= 0:
            cut = size
        parts.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return parts


def _cut(text: str, size: int):
    """Split `text` into (head, tail) where head is at most `size` characters,
    breaking on a newline/space near the limit. CRITICAL: head and tail use the
    SAME cut index, so no character is ever dropped between the two pieces
    (only the single breaking space/newline at the boundary is consumed). This
    is what fixes the 'first letter of the next post disappears' bug."""
    if len(text) <= size:
        return text, ""
    cut = text.rfind("\n", 0, size)
    if cut < size // 2:
        cut = text.rfind(" ", 0, size)
    if cut <= 0:
        cut = size            # no whitespace to break on: hard cut, keep every char
        head, tail = text[:cut], text[cut:]
    else:
        head, tail = text[:cut], text[cut:].lstrip("\n ")
    return head, tail


def paginate(body: str, first_limit: int, later_limit: int, cont_prefix: str = ""):
    """Split plain `body` into a list of pieces for multi-message delivery.

    - The FIRST piece is at most `first_limit` characters.
    - Every LATER piece is at most `later_limit` characters and is prefixed
      with `cont_prefix` (e.g. '(continued\u2026)\n') so readers know it's a
      continuation.
    - No content characters are dropped (see `_cut`); only the whitespace at a
      break point is consumed.
    """
    body = body or ""
    if len(body) <= first_limit:
        return [body]
    head, rest = _cut(body, first_limit)
    parts = [head]
    avail = max(1, later_limit - len(cont_prefix))
    while rest:
        piece, rest = _cut(rest, avail)
        parts.append(cont_prefix + piece)
    return parts
