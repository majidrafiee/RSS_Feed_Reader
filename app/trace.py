"""Structured post-trace logging.

Every significant event in the publish pipeline gets a one-line trace entry
with a fixed prefix so you can grep it from the rotating log:

    grep 'TRACE' data/bot.log

Events logged
-------------
POST_RECV   A new post arrived (live or backfill) and passed the pre-checks.
POST_DROP    A post was intentionally dropped (ad-filter, duplicate, forwarded).
POST_EMPTY   A post arrived with empty text (diagnostic for the empty-body bug).
POST_PUB     A post was successfully published to a destination.
POST_FAIL    A publish attempt failed.
SESSION_BAD  The Telethon session is invalidated (two-IP conflict).
"""

import logging

log = logging.getLogger("trace")


def _tag(src, dest):
    s = src if isinstance(src, str) else str(src)
    d = dest if isinstance(dest, str) else str(dest)
    return f"src={s} dest={d}"


def post_recv(source, dest, msg_id, text_preview="", via="live"):
    """A new post arrived and is about to be published."""
    preview = (text_preview or "")[:80].replace("\n", "\\n")
    log.info("TRACE POST_RECV %s msg=%s via=%s text=%r", _tag(source, dest), msg_id, via, preview)


def post_drop(source, dest, msg_id, reason, text_preview=""):
    """A post was intentionally skipped."""
    preview = (text_preview or "")[:80].replace("\n", "\\n")
    log.info("TRACE POST_DROP %s msg=%s reason=%s text=%r", _tag(source, dest), msg_id, reason, preview)


def post_empty(source, dest, msg_id, text_preview=""):
    """A post arrived with empty or very short text (diagnostic)."""
    preview = (text_preview or "")[:80].replace("\n", "\\n")
    log.info("TRACE POST_EMPTY %s msg=%s text=%r", _tag(source, dest), msg_id, preview)


def post_pub(source, dest, msg_id, first_msg_id=None):
    """A post was successfully published."""
    log.info("TRACE POST_PUB %s msg=%s sent=%s", _tag(source, dest), msg_id, first_msg_id or msg_id)


def post_fail(source, dest, msg_id, error):
    """A publish attempt failed."""
    log.warning("TRACE POST_FAIL %s msg=%s error=%s", _tag(source, dest), msg_id, error)


def session_bad(chat_id, error):
    """The Telethon session is invalidated (two-IP conflict)."""
    log.error("TRACE SESSION_BAD src=%s error=%s", chat_id, error)
