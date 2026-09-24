import asyncio
import logging

import feedparser

from app import db
from app.publisher import publish_rss

log = logging.getLogger("rss")

# Many news sites (e.g. varzesh3, some VOA endpoints) silently return an empty
# body or a block page to the DEFAULT feedparser user-agent, so a perfectly
# valid feed produced ZERO items and never posted. Presenting a normal browser
# UA + Accept header makes those servers serve the real feed.
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
_REQ_HEADERS = {
    "Accept": "application/rss+xml, application/atom+xml, application/xml, "
    "text/xml;q=0.9, */*;q=0.8",
}


async def _parse(url):
    # feedparser is blocking; run it off the event loop. Pass a browser UA so
    # sites that block the default agent still return the feed body.
    return await asyncio.to_thread(
        feedparser.parse, url, agent=_UA, request_headers=dict(_REQ_HEADERS)
    )


def _guid(entry):
    return entry.get("id") or entry.get("link") or entry.get("title")


async def validate_feed(url):
    """Check that `url` is a real, parseable feed with entries before we let the
    user add it.

    Returns (ok: bool, detail: str, title: str|None).

    Common failure: a feed-directory *page* (e.g. VOA's rssfeeds index) is HTML,
    not a feed, so feedparser returns 0 entries. We reject those with a helpful
    message instead of silently adding a source that never posts.
    """
    try:
        feed = await _parse(url)
    except Exception as exc:  # noqa: BLE001
        return False, f"Could not fetch this URL: {exc}", None

    entries = feed.entries or []
    if entries:
        title = None
        if getattr(feed, "feed", None):
            title = feed.feed.get("title")
        return True, "ok", title

    # No entries: figure out why so we can tell the user.
    bozo = getattr(feed, "bozo", 0)
    ctype = ""
    try:
        ctype = (feed.headers or {}).get("content-type", "")
    except Exception:  # noqa: BLE001
        ctype = ""
    if "html" in ctype.lower() or bozo:
        return (
            False,
            "This link is a web page, not an RSS feed. Open the site's RSS "
            "section and copy the address of a specific feed (it usually ends "
            "in .xml or /rss). Directory pages that just list feeds will not "
            "work.",
            None,
        )
    return False, "This feed has no items right now \u2014 try another feed URL.", None


async def seed_source(pool, source_id, url):
    """Mark current feed items as already seen so adding a source does not
    flood the channel with the whole backlog."""
    try:
        feed = await _parse(url)
        for entry in (feed.entries or [])[:20]:
            guid = _guid(entry)
            if guid:
                await db.mark_seen(pool, source_id, guid)
    except Exception as exc:  # noqa: BLE001
        log.warning("seed failed for %s: %s", url, exc)


async def poll_all_feeds(pool, client):
    """Poll every RSS source and publish new items."""
    sources = await db.all_rss_sources(pool)
    for src in sources:
        try:
            feed = await _parse(src["identifier"])
        except Exception as exc:  # noqa: BLE001
            log.warning("parse failed %s: %s", src["identifier"], exc)
            continue
        meta = {
            "source_label": src["label"],
            "dest_username": src["dest_username"],
            "dest_title": src["dest_title"],
            "show_title": src["show_title"],
            "link_title": src["link_title"],
            "dest_show_username": src["dest_show_username"],
            "lang": src["owner_lang"],
        }
        # Oldest first so the channel reads chronologically.
        for entry in reversed(list(feed.entries or [])[:10]):
            guid = _guid(entry)
            if not guid or await db.is_seen(pool, src["id"], guid):
                continue
            try:
                await publish_rss(client, src["dest_chat_id"], meta, entry)
                await db.mark_seen(pool, src["id"], guid)
                await asyncio.sleep(1)  # be gentle with rate limits
            except Exception as exc:  # noqa: BLE001
                log.warning("publish rss failed: %s", exc)
