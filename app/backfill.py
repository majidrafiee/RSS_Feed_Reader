import asyncio
import logging

from telethon import utils

from app import db
from app.publisher import publish_tg, publish_tg_album

log = logging.getLogger("backfill")

# Safety cap so a very busy channel that fell far behind can't flood the
# destination in a single run. Anything older than this many messages is
# skipped (the watermark still advances so we don't loop forever).
MAX_PER_RUN = 30


async def backfill_tg_sources(pool, client):
    """Recover Telegram source posts the live event stream may have missed.

    For each configured TG source we ask Telegram for every message newer than
    the last one we delivered (`last_tg_msg_id`). This closes the two gaps a
    pure event listener cannot cover:
      * channelDifferenceTooLong — busy channels whose backlog exceeds the
        catch-up limit after a reconnect (Telegram drops those events); and
      * downtime — posts made while the container was restarting/redeploying.

    On the very first sighting of a source (watermark is NULL) we do NOT dump
    history; we just record the latest id so backfill starts from 'now'.
    """
    try:
        rows = await db.all_tg_sources(pool)
    except Exception as exc:  # noqa: BLE001
        log.warning("backfill: could not load sources: %s", exc)
        return

    # Group destinations by source chat so we read each channel only once.
    by_chat = {}
    for r in rows:
        by_chat.setdefault(r["source_tg_id"], []).append(r)

    for chat_id, dest_rows in by_chat.items():
        try:
            await _backfill_one(pool, client, chat_id, dest_rows)
        except Exception as exc:  # noqa: BLE001
            log.warning("backfill: source %s failed: %s", chat_id, exc)


async def _backfill_one(pool, client, chat_id, dest_rows):
    # The watermark is per source ROW, but all rows for the same chat share the
    # channel read. Use the lowest watermark so no destination misses a post.
    watermarks = [r["last_tg_msg_id"] for r in dest_rows]
    first_time = any(w is None for w in watermarks)
    min_wm = min([w for w in watermarks if w is not None], default=0)

    try:
        entity = await client.get_input_entity(chat_id)
    except Exception as exc:  # noqa: BLE001
        log.info("backfill: cannot resolve source %s (%s); skipping", chat_id, exc)
        return

    # Fetch newest first, then replay oldest->newest.
    missed = []
    async for msg in client.iter_messages(entity, limit=MAX_PER_RUN):
        mid = getattr(msg, "id", None)
        if mid is None:
            continue
        if not first_time and mid <= min_wm:
            break
        missed.append(msg)

    if first_time:
        # Record the latest id per row without republishing history.
        latest = missed[0].id if missed else 0
        for r in dest_rows:
            if r["last_tg_msg_id"] is None:
                await db.update_source_last_msg(pool, r["source_id"], latest)
        if latest:
            log.info(
                "backfill: primed source %s watermark=%s (no history replayed)",
                chat_id, latest,
            )
        return

    if not missed:
        return

    missed.reverse()  # oldest first, natural reading order
    log.info(
        "backfill: source %s has %d missed post(s) since id=%s",
        chat_id, len(missed), min_wm,
    )

    # Group consecutive messages that share a grouped_id into albums so an
    # album missed by the live stream is republished as ONE media group, not
    # one post per photo. Non-grouped messages become singleton groups.
    items = []
    i = 0
    while i < len(missed):
        m = missed[i]
        gid = getattr(m, "grouped_id", None)
        if gid is None:
            items.append([m])
            i += 1
        else:
            grp = [m]
            j = i + 1
            while j < len(missed) and getattr(missed[j], "grouped_id", None) == gid:
                grp.append(missed[j])
                j += 1
            items.append(grp)
            i = j

    for item in items:
        item.sort(key=lambda mm: mm.id)
        is_album = len(item) > 1
        rep_id = item[0].id      # claim/link anchor (album's first id)
        max_id = item[-1].id     # watermark advances past the whole album
        head = item[0]
        chat = await head.get_chat()
        live_username = getattr(chat, "username", None)
        live_title = getattr(chat, "title", None)
        is_forwarded = head.fwd_from is not None
        for r in dest_rows:
            # Only (re)deliver rows that are actually behind this item.
            if r["last_tg_msg_id"] is not None and max_id <= r["last_tg_msg_id"]:
                continue
            # Atomic claim on the anchor id: if the live userbot already
            # delivered (or is mid-publishing) this post/album, its claim wins
            # and we skip here.
            if not await db.claim_tg_message(pool, r["source_id"], rep_id):
                continue
            if is_forwarded and r["skip_forwarded"]:
                await db.update_source_last_msg(pool, r["source_id"], max_id)
                continue
            meta = {
                "source_label": r["source_label"] or live_title,
                "source_username": r["source_username"] or live_username,
                "source_tg_id": r["source_tg_id"] or chat_id,
                "dest_username": r["dest_username"],
                "dest_title": r["dest_title"],
                "show_title": r["show_title"],
                "link_title": r["link_title"],
                "dest_show_username": r["dest_show_username"],
                "lang": r["owner_lang"],
            }
            try:
                if is_album:
                    await publish_tg_album(client, r["dest_chat_id"], meta, item)
                else:
                    await publish_tg(client, r["dest_chat_id"], meta, head)
                await db.update_source_last_msg(pool, r["source_id"], max_id)
                log.info(
                    "backfill: delivered src=%s ids=%s-%s (album=%s) -> dest=%s",
                    chat_id, rep_id, max_id, is_album, r["dest_chat_id"],
                )
            except Exception as exc:  # noqa: BLE001
                # Release the claim so a later sweep can retry this item.
                await db.release_tg_message(pool, r["source_id"], rep_id)
                log.warning(
                    "backfill: publish src=%s ids=%s-%s -> dest=%s failed: %s",
                    chat_id, rep_id, max_id, r["dest_chat_id"], exc,
                )
        await asyncio.sleep(0.6)
