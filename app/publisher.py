import asyncio
import logging
import re
import time

from telethon.tl.types import MessageMediaWebPage

from app.formatting import chunk, esc, strip_html, strip_source_signature, truncate
from app.links import post_link

log = logging.getLogger("publisher")

SEP = "<code>\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500</code>"

# Resolved input entities are cached in memory so we don't call GetDialogs on
# every single incoming post (that triggers Telegram flood-waits, which is why
# only some posts were getting through). One lock serializes the expensive
# refresh so concurrent posts don't all stampede GetDialogs at once.
_dest_cache = {}
_resolve_lock = asyncio.Lock()
# Negative cache: dest_id -> monotonic time it last failed. While a channel is
# known-unreachable we fail fast instead of calling GetDialogs again (that was
# causing the repeated 22-28s flood-wait sleeps in the logs).
_unreachable = {}
_UNREACHABLE_COOLDOWN = 600  # seconds


async def _try_input(client, key):
    try:
        return await client.get_input_entity(key)
    except (ValueError, TypeError):
        return None
    except Exception as exc:  # noqa: BLE001
        log.info("get_input_entity(%r) failed: %s", key, exc)
        return None


async def resolve_dest(client, dest_chat_id, dest_username=None, force=False):
    """Numeric destination id -> sendable input entity.

    Resolution order (cheapest first):
      1. in-memory cache
      2. session entity cache (get_input_entity by id)
      3. by @username if the channel is public  ← works even when the channel
         is not in the reader's dialog list
      4. one dialog refresh + scan (serialized by a lock, flood-wait safe)

    `force=True` bypasses the negative cache (used by the manual test-post).
    """
    ent = _dest_cache.get(dest_chat_id)
    if ent is not None:
        return ent

    # Fail fast if we recently found this destination unreachable, unless the
    # caller explicitly forces a fresh attempt.
    if not force:
        ts = _unreachable.get(dest_chat_id)
        if ts is not None and (time.monotonic() - ts) < _UNREACHABLE_COOLDOWN:
            raise ValueError(f"destination {dest_chat_id} not reachable (cached)")

    ent = await _try_input(client, dest_chat_id)
    if ent is not None:
        _dest_cache[dest_chat_id] = ent
        _unreachable.pop(dest_chat_id, None)
        return ent

    if dest_username:
        ent = await _try_input(client, dest_username)
        if ent is not None:
            _dest_cache[dest_chat_id] = ent
            _unreachable.pop(dest_chat_id, None)
            return ent

    async with _resolve_lock:
        # Another coroutine may have resolved it while we waited for the lock.
        ent = _dest_cache.get(dest_chat_id)
        if ent is not None:
            return ent
        ent = await _try_input(client, dest_chat_id)
        if ent is not None:
            _dest_cache[dest_chat_id] = ent
            _unreachable.pop(dest_chat_id, None)
            return ent

        log.info("entity %s not cached; refreshing dialogs", dest_chat_id)
        try:
            await client.get_dialogs()
        except Exception as exc:  # noqa: BLE001
            log.warning("get_dialogs failed: %s", exc)
        ent = await _try_input(client, dest_chat_id)
        if ent is not None:
            _dest_cache[dest_chat_id] = ent
            _unreachable.pop(dest_chat_id, None)
            return ent
        try:
            async for d in client.iter_dialogs():
                if d.id == dest_chat_id:
                    _dest_cache[dest_chat_id] = d.input_entity
                    _unreachable.pop(dest_chat_id, None)
                    return d.input_entity
        except Exception as exc:  # noqa: BLE001
            log.warning("iter_dialogs failed: %s", exc)

        _unreachable[dest_chat_id] = time.monotonic()
        log.error(
            "Destination %s not reachable \u2014 the reader account cannot see "
            "this channel. Add the reader as an ADMIN (with Post messages) of "
            "that exact channel. (Silencing retries for %ds.)",
            dest_chat_id, _UNREACHABLE_COOLDOWN,
        )
        raise ValueError(f"destination {dest_chat_id} not reachable")


async def _live_channel_meta(client, chat_id):
    """Fetch the CURRENT title + @username of a channel straight from the
    server. We use GetFullChannelRequest (not get_entity) on purpose: Telethon
    caches entities in the session file, and that cache does NOT learn that a
    channel just became public / gained a username — so get_entity kept
    returning the old private name. GetFullChannelRequest always round-trips to
    Telegram, so a channel renamed to 'ایران فید' with @iraanfeed is seen at
    once. Returns (title, username) or (None, None) on failure.
    """
    from telethon import utils
    from telethon.tl import functions

    try:
        input_ch = await client.get_input_entity(chat_id)
        res = await client(
            functions.channels.GetFullChannelRequest(channel=input_ch)
        )
    except Exception as exc:  # noqa: BLE001
        log.debug("live meta fetch failed for %s: %s", chat_id, exc)
        return None, None
    ch = None
    for c in getattr(res, "chats", None) or []:
        try:
            if utils.get_peer_id(c) == chat_id:
                ch = c
                break
        except Exception:  # noqa: BLE001
            continue
    if ch is None and getattr(res, "chats", None):
        ch = res.chats[0]
    if ch is None:
        return None, None
    title = getattr(ch, "title", None)
    username = getattr(ch, "username", None)
    # Newer channels can carry several usernames; fall back to the first
    # active one when the primary `username` field is empty.
    if not username:
        for u in getattr(ch, "usernames", None) or []:
            uname = getattr(u, "username", None)
            if uname and getattr(u, "active", True):
                username = uname
                break
    return title, username


async def refresh_destinations(client, pool, dests):
    """Update each destination's stored title/@username from the live channel
    so the footer label + self-link stay current after a rename or after the
    channel goes public. `dests` is a list of destination rows."""
    from app import db

    for d in dests:
        new_title, new_username = await _live_channel_meta(client, d["chat_id"])
        if new_title is None and new_username is None:
            continue
        if new_title != d["title"] or new_username != d["username"]:
            try:
                await db.update_destination_meta(
                    pool, d["chat_id"], new_title, new_username
                )
                log.info(
                    "destination meta refreshed (%s): title '%s' -> '%s', "
                    "username %r -> %r",
                    d["chat_id"], d["title"], new_title,
                    d["username"], new_username,
                )
            except Exception as exc:  # noqa: BLE001
                log.debug("could not update dest meta for %s: %s",
                          d["chat_id"], exc)


async def prime_destinations(client, pool):
    """At startup, resolve every known destination once and cache it. Logs a
    clear per-channel report so the user knows exactly which channel (by title)
    the reader still can't post to."""
    from app import db

    try:
        dests = await db.all_destinations(pool)
    except Exception as exc:  # noqa: BLE001
        log.warning("could not load destinations for priming: %s", exc)
        return
    ok, bad = 0, 0
    for d in dests:
        try:
            await resolve_dest(client, d["chat_id"], d["username"])
            ok += 1
            log.info("destination OK: '%s' (%s)", d["title"], d["chat_id"])
            # Refresh the stored display name / @username from the LIVE channel
            # so renaming the channel (or adding a username) is reflected in
            # the footer without needing to re-add the destination.
            await refresh_destinations(client, pool, [d])
        except Exception:  # noqa: BLE001
            bad += 1
            log.error(
                "destination UNREACHABLE: '%s' (%s) \u2014 add the reader as "
                "admin of THIS channel.",
                d["title"], d["chat_id"],
            )
    log.info("destination priming done: %d reachable, %d unreachable", ok, bad)


def _source_line(label, link, lang="en", show_title=True, link_title=True):
    """Build the source credit line shown at the BOTTOM of a post, e.g.
    'منبع: <b>Iran International</b>' (linked to the original post when a link
    is available).

    show_title=False -> no source line at all.
    link_title=False -> plain (non-linked) source name even when a link exists.
    Returns the line prefixed with two blank lines so it detaches from the body.
    """
    if not show_title:
        return ""
    from app.i18n import t
    prefix = t(lang, "source_prefix")
    label = esc(label or "Source")
    if link and link_title:
        name = f'<a href="{link}"><b>{label}</b></a>'
    else:
        name = f"<b>{label}</b>"
    return f"\n\n{esc(prefix)}: {name}"


def _dest_label(dest_username, dest_title, show_username=True):
    """Pick the destination label for the footer: @username when available and
    requested, otherwise the channel's name."""
    if show_username and dest_username:
        return "@" + dest_username
    return dest_title or "View in channel"


def _footer(dest_username, dest_chat_id, dest_title, msg_id, show_username=True):
    link = post_link(dest_username, dest_chat_id, msg_id)
    if not link:
        return None
    label = esc(_dest_label(dest_username, dest_title, show_username))
    # Bold, colourful megaphone marker, linked to the destination channel.
    return f'\n\n\U0001F4E3 <b><a href="{link}">{label}</a></b>'


def _entity_summary(msg):
    """Compact description of the entities Telegram actually stored on a
    message, so the logs PROVE whether the source hyperlink survived. Each
    text link is shown as 'TextUrl@offset+len->url'."""
    ents = getattr(msg, "entities", None) or []
    out = []
    for e in ents:
        name = type(e).__name__.replace("MessageEntity", "")
        url = getattr(e, "url", None)
        out.append(
            f"{name}@{getattr(e, 'offset', '?')}+{getattr(e, 'length', '?')}"
            + (f"->{url}" if url else "")
        )
    return out


async def verify_links(client, dest, msg_id, tag=""):
    """Re-fetch the delivered message and log its stored link entities. This is
    the ground truth: if a 'TextUrl->...t.me...' entity is present the source
    hyperlink IS live in the channel; if none is present Telegram stripped it."""
    try:
        fresh = await client.get_messages(dest, ids=msg_id)
    except Exception as exc:  # noqa: BLE001
        log.info("%s STEP7 verify: could not re-fetch msg %s (%s)", tag, msg_id, exc)
        return
    ents = _entity_summary(fresh)
    has_link = any("->" in e for e in ents)
    log.info(
        "%s STEP7 VERIFY delivered msg %s: has_link=%s entities=%s",
        tag, msg_id, has_link, ents,
    )
    if not has_link:
        log.warning(
            "%s STEP7 VERIFY: NO link entity in delivered msg %s — Telegram "
            "dropped it. (Private t.me/c/ links to a channel the target isn't a "
            "member of are commonly stripped.)", tag, msg_id,
        )


async def _add_footer(client, dest, msg, footer, base_html=None, tag=""):
    """Append the self-link footer, editing the message when it fits, else
    sending it as a small follow-up message.

    CRITICAL: we edit using `base_html` (the exact HTML we originally sent,
    WITH the <a>/<b> tags) — NOT `msg.message`. Telegram stores formatting as
    message *entities*, so `msg.message` returns PLAIN text with the source
    hyperlink already stripped; editing with that silently destroyed the
    'منبع:' link (the bug the user kept seeing). Re-editing with the original
    HTML preserves the source-post hyperlink.
    """
    if not footer or msg is None:
        return
    base = base_html if base_html is not None else (msg.message or "")
    combined = base + footer
    limit = 1024 if msg.media else 4096
    # Telegram counts VISIBLE characters, not markup, against the limit.
    visible = len(strip_html(combined))
    try:
        if visible <= limit:
            edited = await client.edit_message(
                dest, msg.id, combined, parse_mode="html"
            )
            log.info(
                "%s STEP6 footer edited into msg %s; entities=%s",
                tag, msg.id, _entity_summary(edited),
            )
            return
    except Exception as exc:  # noqa: BLE001
        log.info("%s footer edit failed (%s); sending separately", tag, exc)
    try:
        sent = await client.send_message(
            dest, footer.strip(), parse_mode="html", link_preview=False
        )
        log.info(
            "%s STEP6 footer sent as follow-up msg (source link untouched on "
            "main msg); entities=%s", tag, _entity_summary(sent),
        )
    except Exception as exc:  # noqa: BLE001
        log.warning("%s footer send failed: %s", tag, exc)


async def publish_tg(client, dest_chat_id, meta, message):
    """Re-publish a Telegram channel post. The source credit ('منبع: <name>')
    is placed at the BOTTOM and linked to the original post; a self-link footer
    to our own channel follows it. Full text is preserved (split if long).
    """
    # --- STEP 0: gather inputs and log them so we can diagnose link building.
    src_username = meta.get("source_username")
    src_tg_id = meta.get("source_tg_id")
    src_label = meta.get("source_label")
    msg_id = getattr(message, "id", None)
    lang = meta.get("lang", "en")
    show_title = meta.get("show_title", True)
    link_title = meta.get("link_title", True)
    dest_show_username = meta.get("dest_show_username", True)
    tag = f"[post src={src_username or src_tg_id} msg={msg_id} -> dest={dest_chat_id}]"

    log.info(
        "%s STEP0 inputs: source_label=%r source_username=%r source_tg_id=%r "
        "msg_id=%r show_title=%s link_title=%s dest_show_username=%s lang=%s",
        tag, src_label, src_username, src_tg_id, msg_id,
        show_title, link_title, dest_show_username, lang,
    )

    # --- STEP 1: build the source-post link.
    source_link = post_link(src_username, src_tg_id, msg_id)
    if source_link:
        log.info("%s STEP1 source_link BUILT: %s", tag, source_link)
    else:
        log.warning(
            "%s STEP1 source_link is NONE (need msg_id AND (username OR "
            "tg_chat_id)). msg_id=%r username=%r tg_chat_id=%r",
            tag, msg_id, src_username, src_tg_id,
        )

    # --- STEP 2: build the bottom source credit line.
    source_line = _source_line(
        src_label, source_link, lang, show_title, link_title
    )
    will_hyperlink = bool(source_link) and link_title and show_title
    log.info(
        "%s STEP2 source_line: show_title=%s link_title=%s -> hyperlinked=%s | %r",
        tag, show_title, link_title, will_hyperlink, source_line,
    )

    dest = await resolve_dest(client, dest_chat_id, meta.get("dest_username"))
    body = strip_source_signature(message.message or "")

    # A MessageMediaWebPage is just an auto-generated link preview, NOT an
    # attachable file — trying to send_file() it raises "Cannot use ... as
    # file" and we'd fall back to an ugly forward. Treat it as a plain text
    # post (the link is already in the body).
    is_webpage = isinstance(message.media, MessageMediaWebPage)
    has_file = bool(message.media) and not is_webpage
    log.info(
        "%s STEP3 media: has_media=%s is_webpage=%s -> send_as_file=%s",
        tag, bool(message.media), is_webpage, has_file,
    )

    # The source line rides at the END of the (first) message body/caption.
    first_msg = None
    last_msg = None
    last_html = ""  # the exact HTML of last_msg, needed for a link-safe footer
    try:
        if has_file:
            caption = body + source_line
            if len(caption) <= 1024:
                m = await client.send_file(
                    dest, file=message.media, caption=caption, parse_mode="html"
                )
                first_msg = last_msg = m
                last_html = caption
            else:
                cap = truncate(body, 900) + source_line
                m = await client.send_file(
                    dest, file=message.media, caption=cap, parse_mode="html"
                )
                first_msg = last_msg = m
                last_html = cap
                rest = body[900:]
                for part in chunk(rest, 4096):
                    if part.strip():
                        last_msg = await client.send_message(
                            dest, part, parse_mode="html", link_preview=False
                        )
                        last_html = part
                        await asyncio.sleep(0.4)
        else:
            parts = chunk(body, 4096)
            for i, part in enumerate(parts):
                # Append the source line only to the LAST chunk.
                text = part + (source_line if i == len(parts) - 1 else "")
                m = await client.send_message(
                    dest, text, parse_mode="html", link_preview=False
                )
                if i == 0:
                    first_msg = m
                last_msg = m
                last_html = text
                await asyncio.sleep(0.4)
        log.info(
            "%s STEP4 sent OK: first_msg_id=%s last_msg_id=%s",
            tag, getattr(first_msg, "id", None), getattr(last_msg, "id", None),
        )
    except Exception as exc:  # noqa: BLE001
        log.warning("%s STEP4 styled publish FAILED (%s); forwarding instead",
                    tag, exc)
        await client.forward_messages(dest, message)
        return

    footer = _footer(
        meta.get("dest_username"), dest_chat_id, meta.get("dest_title"),
        first_msg.id if first_msg else None, dest_show_username,
    )
    log.info("%s STEP5 footer=%r", tag, footer)
    await _add_footer(client, dest, last_msg, footer, base_html=last_html, tag=tag)
    # STEP7: ground-truth check that the source hyperlink is live in the channel.
    if last_msg is not None and will_hyperlink:
        await verify_links(client, dest, last_msg.id, tag=tag)


async def publish_tg_album(client, dest_chat_id, meta, messages):
    """Re-publish a Telegram ALBUM (media group) as ONE media group in the
    destination instead of N separate posts. The album caption carries the
    bottom source credit ('\u0645\u0646\u0628\u0639: <name>'); the self-link footer is edited
    into the caption-bearing (first) message afterwards.

    `messages` is the list of Telethon messages that share one grouped_id.
    """
    messages = [m for m in messages if m is not None]
    if not messages:
        return
    messages = sorted(messages, key=lambda m: m.id)
    src_username = meta.get("source_username")
    src_tg_id = meta.get("source_tg_id")
    src_label = meta.get("source_label")
    lang = meta.get("lang", "en")
    show_title = meta.get("show_title", True)
    link_title = meta.get("link_title", True)
    dest_show_username = meta.get("dest_show_username", True)
    rep_id = messages[0].id
    grp = getattr(messages[0], "grouped_id", None)
    tag = (
        f"[album src={src_username or src_tg_id} grp={grp} "
        f"n={len(messages)} -> dest={dest_chat_id}]"
    )

    # Source-post link points at the album's first message.
    source_link = post_link(src_username, src_tg_id, rep_id)
    source_line = _source_line(
        src_label, source_link, lang, show_title, link_title
    )
    will_hyperlink = bool(source_link) and link_title and show_title

    # The caption is whichever album item actually carries text (Telegram puts
    # the album's text on exactly one of the items).
    raw_caption = ""
    for m in messages:
        if (m.message or "").strip():
            raw_caption = m.message
            break
    body = strip_source_signature(raw_caption)
    caption = body + source_line
    # Album captions obey the 1024-char caption limit.
    if len(strip_html(caption)) > 1024:
        caption = truncate(body, 900) + source_line

    dest = await resolve_dest(client, dest_chat_id, meta.get("dest_username"))
    media = [
        m.media for m in messages
        if m.media and not isinstance(m.media, MessageMediaWebPage)
    ]
    if not media:
        # No attachable media (all link previews) — fall back to a text post.
        await publish_tg(client, dest_chat_id, meta, messages[0])
        return

    first_msg = None
    try:
        # Passing a LIST of files makes Telethon send a single media group;
        # the caption is applied to the first item.
        sent = await client.send_file(
            dest, file=media, caption=caption, parse_mode="html"
        )
        first_msg = sent[0] if isinstance(sent, (list, tuple)) else sent
        log.info(
            "%s STEP4 album sent OK: first_msg_id=%s items=%d",
            tag, getattr(first_msg, "id", None), len(media),
        )
    except Exception as exc:  # noqa: BLE001
        log.warning("%s STEP4 album publish FAILED (%s); forwarding instead",
                    tag, exc)
        try:
            await client.forward_messages(dest, messages)
        except Exception as exc2:  # noqa: BLE001
            log.warning("%s album forward also failed: %s", tag, exc2)
        return

    footer = _footer(
        meta.get("dest_username"), dest_chat_id, meta.get("dest_title"),
        first_msg.id if first_msg else None, dest_show_username,
    )
    log.info("%s STEP5 footer=%r", tag, footer)
    await _add_footer(client, dest, first_msg, footer, base_html=caption, tag=tag)
    if first_msg is not None and will_hyperlink:
        await verify_links(client, dest, first_msg.id, tag=tag)


async def send_test_post(client, dest_chat_id, dest_username=None, dest_title=None):
    """Post a small styled test message to a destination to verify the reader
    account can actually post there. `force=True` bypasses the negative cache
    so the user can re-check right after fixing admin rights.

    Returns (ok: bool, detail: str).
    """
    try:
        dest = await resolve_dest(client, dest_chat_id, dest_username, force=True)
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    text = (
        "\u2705 <b>Test post</b>\n"
        f"{SEP}\n"
        "This channel is correctly connected. News will be delivered here."
    )
    if dest_title:
        text += f"\n\n\U0001F4E2 <b>{esc(dest_title)}</b>"
    try:
        await client.send_message(dest, text, parse_mode="html", link_preview=False)
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    return True, "ok"


async def publish_rss(client, dest_chat_id, meta, entry):
    """Publish a single RSS entry as a styled container, with the article photo
    when one can be extracted from the feed entry."""
    dest = await resolve_dest(client, dest_chat_id, meta.get("dest_username"))
    show_title = meta.get("show_title", True)
    link_title = meta.get("link_title", True)
    dest_show_username = meta.get("dest_show_username", True)
    lang = meta.get("lang", "en")

    title = _clean_rss_title(entry)
    link = entry.get("link", "")
    summary = _clean_rss_summary(entry)
    image = _entry_image(entry)

    # Source credit goes at the BOTTOM, linked to the article.
    source_line = _source_line(
        meta.get("source_label"), link, lang, show_title, link_title
    )
    body = f"<b>{esc(title)}</b>"
    if summary:
        body += f"\n\n{esc(truncate(summary, 3800))}"
    if link:
        body += (
            f'\n\n\U0001F517 <a href="{esc(link)}">'
            f"Read the full article \u2192</a>"
        )

    text = body + source_line
    first_msg = None
    last_msg = None
    last_html = ""

    # Try to lead with the article image (caption limit 1024). If it fails or
    # the text is too long, fall back to a plain text post.
    if image and len(text) <= 1024:
        try:
            m = await client.send_file(
                dest, file=image, caption=text, parse_mode="html"
            )
            first_msg = last_msg = m
            last_html = text
        except Exception as exc:  # noqa: BLE001
            log.info("rss image send failed (%s); posting text only", exc)

    if first_msg is None:
        for i, part in enumerate(chunk(text, 4096)):
            m = await client.send_message(
                dest, part, parse_mode="html", link_preview=False
            )
            if i == 0:
                first_msg = m
            last_msg = m
            last_html = part
            await asyncio.sleep(0.4)

    footer = _footer(
        meta.get("dest_username"), dest_chat_id, meta.get("dest_title"),
        first_msg.id if first_msg else None, dest_show_username,
    )
    await _add_footer(
        client, dest, last_msg, footer, base_html=last_html, tag="[rss]"
    )
    if last_msg is not None and link and link_title and show_title:
        await verify_links(client, dest, last_msg.id, tag="[rss]")


_IMG_SRC_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
_IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")


def _looks_like_image(url, mime=""):
    if mime and mime.lower().startswith("image/"):
        return True
    low = (url or "").lower().split("?")[0]
    return low.endswith(_IMG_EXT)


def _entry_image(entry):
    """Best-effort extraction of a representative image URL from a feedparser
    entry: media_content, media_thumbnail, enclosures, then <img> in summary/
    content."""
    # media_content / media_thumbnail (Media RSS)
    for key in ("media_content", "media_thumbnail"):
        items = entry.get(key) or []
        for it in items:
            url = it.get("url") if isinstance(it, dict) else None
            if url and _looks_like_image(url, (it.get("type") if isinstance(it, dict) else "") or ""):
                return url
    # enclosures
    for enc in entry.get("enclosures") or []:
        url = enc.get("href") or enc.get("url") if isinstance(enc, dict) else None
        if url and _looks_like_image(url, (enc.get("type") if isinstance(enc, dict) else "") or ""):
            return url
    # <img> inside summary or content HTML
    html_blobs = [entry.get("summary", "")]
    for c in entry.get("content") or []:
        if isinstance(c, dict) and c.get("value"):
            html_blobs.append(c["value"])
    for blob in html_blobs:
        if not blob:
            continue
        m = _IMG_SRC_RE.search(blob)
        if m and _looks_like_image(m.group(1)):
            return m.group(1)
    return None


def _clean_rss_title(entry):
    """Return a sane title. Some feeds leak image credits (e.g. 'Getty Images')
    or leave the title empty; fall back to the first summary sentence."""
    title = strip_html(entry.get("title", "") or "").strip()
    bad = {"", "getty images", "etty images", "image", "images", "(no title)"}
    if title.lower() in bad or len(title) < 3:
        summary = strip_html(entry.get("summary", "") or "").strip()
        if summary:
            # first sentence / first 120 chars
            first = re.split(r"(?<=[.!?])\s", summary, maxsplit=1)[0]
            return truncate(first, 120)
        return "(no title)"
    return title


def _clean_rss_summary(entry):
    """Strip HTML, drop stray image-credit noise, and avoid echoing the title."""
    summary = strip_html(entry.get("summary", "") or "").strip()
    # Remove leading 'Getty Images' style credit fragments.
    summary = re.sub(r"^(getty images|etty images)[:\s\-]*", "", summary,
                     flags=re.IGNORECASE).strip()
    return summary
