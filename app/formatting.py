import html
import re

_TAG = re.compile(r"<[^>]+>")

# A "signature" line is a promotional footer the ORIGINAL channel appends to its
# own posts: a bare @handle, a t.me link, or a short "join/subscribe" style line,
# optionally decorated with leading/trailing emoji or punctuation. We strip these
# because our own footer already credits + links the source, so the source's own
# self-promo is noise in the aggregated channel.
_HANDLE_ONLY = re.compile(
    r"^[\s\W_]*@[A-Za-z0-9_]{3,}(?:[\s|/،,-]+@?[A-Za-z0-9_]{3,})*[\s\W_]*$"
)
_TME_ONLY = re.compile(
    r"^[\s\W_]*(?:https?://)?t\.me/[^\s]+[\s\W_]*$", re.IGNORECASE
)
# A line that is ONLY an external (non-t.me) URL, optionally wrapped in emoji /
# punctuation. These are the "read the full article" style links the user wants
# to KEEP, so we treat them as part of the trailing footer region (scan past
# them) without deleting them.
_URL_ONLY = re.compile(
    r"^[\s\W_]*https?://[^\s]+[\s\W_]*$", re.IGNORECASE
)
# "Join / Subscribe / عضو شوید / کانال ما" promo lines that also contain a handle
# or a t.me link on the same line.
_JOIN_WORDS = re.compile(
    r"(join|subscribe|follow|channel|\u0639\u0636\u0648|\u06a9\u0627\u0646\u0627\u0644|"
    r"\u0627\u0634\u062a\u0631\u0627\u06a9|\u0641\u0648\u0644\u0648)",
    re.IGNORECASE,
)


def _is_signature_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if _HANDLE_ONLY.match(s):
        return True
    if _TME_ONLY.match(s):
        return True
    # A short promo line that mentions joining AND carries a handle / t.me link.
    if len(s) <= 60 and ("@" in s or "t.me/" in s.lower()) and _JOIN_WORDS.search(s):
        return True
    return False


def _is_external_link_line(line: str) -> bool:
    """True for a line that is only an external http(s) link (not t.me). We
    KEEP these but keep scanning above them, so a channel's trailing @handles
    are stripped even when they sit next to a real 'read more' link."""
    s = line.strip()
    if not s or _TME_ONLY.match(s):
        return False
    return bool(_URL_ONLY.match(s))


def strip_source_signature(text: str) -> str:
    """Remove the source channel's own trailing self-promo (bare @handles, t.me
    links, join/subscribe lines) from the END of a post, while PRESERVING a
    genuine external link (e.g. 'read the full article').

    We walk backwards over the trailing region: signature lines (handles / t.me
    / promo) are dropped, external-URL-only lines are kept but we keep scanning
    above them, and the first real content line stops the scan. This handles
    both orders the channels use:
        \u2026 / LINK / @a | @b        and        \u2026 / @a | @b / LINK
    """
    if not text:
        return text
    lines = text.split("\n")
    keep = [True] * len(lines)
    i = len(lines) - 1
    while i >= 0:
        stripped = lines[i].strip()
        if stripped == "":
            # blank line inside the footer region — drop it and continue
            keep[i] = False
            i -= 1
            continue
        if _is_signature_line(lines[i]):
            keep[i] = False
            i -= 1
            continue
        if _is_external_link_line(lines[i]):
            # keep the link, but it's still part of the footer region
            i -= 1
            continue
        break  # real content — stop stripping
    cleaned = "\n".join(l for l, k in zip(lines, keep) if k).rstrip()
    return cleaned


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
