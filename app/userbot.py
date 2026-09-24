import logging

from telethon import events, utils

from app import db
from app.publisher import publish_tg, publish_tg_album

log = logging.getLogger("userbot")


def register_userbot(client, pool):
    """Attach the NewMessage handler that mirrors source channel posts into
    the configured destination channels."""

    @client.on(events.NewMessage())
    async def _handler(event):  # noqa: ANN001
        try:
            # Only broadcast channels (not groups / supergroups).
            if not (event.is_channel and not event.is_group):
                log.debug(
                    "IN skip (not a broadcast channel): chat_id=%s is_channel=%s "
                    "is_group=%s",
                    getattr(event, "chat_id", None), event.is_channel,
                    event.is_group,
                )
                return
            chat = await event.get_chat()
            chat_id = utils.get_peer_id(chat)
            msg_id = getattr(event.message, "id", None)
            # Album members arrive as individual NewMessage events that share a
            # grouped_id. We let the dedicated Album handler (below) republish
            # them as ONE media group, so skip them here to avoid posting each
            # photo of an album as its own separate post.
            if getattr(event.message, "grouped_id", None) is not None:
                log.debug(
                    "IN skip album member msg=%s grouped_id=%s (Album handler "
                    "republishes it as one media group)",
                    msg_id, event.message.grouped_id,
                )
                return
            live_username = getattr(chat, "username", None)
            live_title = getattr(chat, "title", None)
            # Look up configured destinations FIRST. The reader account belongs
            # to many channels it merely reads; logging every one of their
            # posts at INFO floods the log with unrelated traffic. Only the
            # channels the user actually configured as sources are logged at
            # INFO — everything else is quiet debug.
            rows = await db.destinations_for_tg_source(pool, chat_id)
            if not rows:
                log.debug(
                    "IN ignore unconfigured chat_id=%s username=%r title=%r "
                    "msg_id=%s", chat_id, live_username, live_title, msg_id,
                )
                return
            log.info(
                "IN channel post: chat_id=%s username=%r title=%r msg_id=%s "
                "-> %d destination(s)",
                chat_id, live_username, live_title, msg_id, len(rows),
            )
            # Skip forwarded posts (usually cross-channel ads) when the owner
            # of that destination has the skip_forwarded setting on.
            is_forwarded = event.message.fwd_from is not None
            for row in rows:
                # Deduplicate: a "Got difference" catch-up can re-fire
                # NewMessage events for posts we already delivered. Skip any
                # message id at or below this source's watermark so we never
                # publish the same post twice.
                last = row["last_tg_msg_id"]
                if last is not None and msg_id is not None and msg_id <= last:
                    log.info(
                        "IN skip duplicate: src=%s msg=%s already delivered "
                        "(watermark=%s)", chat_id, msg_id, last,
                    )
                    continue
                # Gap detection: if this id jumped past the watermark by more
                # than 1, some ids in between were never delivered here (could
                # be deletions / service messages / forwarded-skips, or a real
                # miss). The 3-min backfill will recover any genuine misses.
                if (
                    last is not None and msg_id is not None
                    and msg_id > last + 1
                ):
                    log.info(
                        "IN gap: src=%s jumped %s -> %s (%d id(s) in between; "
                        "backfill will verify)", chat_id, last, msg_id,
                        msg_id - last - 1,
                    )
                # Atomic claim closes the live-vs-backfill race: the watermark
                # is only advanced AFTER a post finishes publishing (~1s), so a
                # backfill sweep firing in that window would re-send the same
                # post (the duplicate the user saw). Whoever claims the
                # (source, msg) first publishes; the other path skips.
                if not await db.claim_tg_message(pool, row["source_id"], msg_id):
                    log.info(
                        "IN skip duplicate: src=%s msg=%s already claimed by "
                        "another path", chat_id, msg_id,
                    )
                    continue
                if is_forwarded and row["skip_forwarded"]:
                    log.info(
                        "skipping forwarded post from %s -> dest %s",
                        chat_id, row["dest_chat_id"],
                    )
                    # Advance watermark so the skip doesn't look like a gap.
                    await db.update_source_last_msg(pool, row["source_id"], msg_id)
                    continue
                meta = {
                    "source_label": row["source_label"] or live_title,
                    "source_username": row["source_username"] or live_username,
                    "source_tg_id": row["source_tg_id"] or chat_id,
                    "dest_username": row["dest_username"],
                    "dest_title": row["dest_title"],
                    "show_title": row["show_title"],
                    "link_title": row["link_title"],
                    "dest_show_username": row["dest_show_username"],
                    "lang": row["owner_lang"],
                }
                try:
                    await publish_tg(client, row["dest_chat_id"], meta, event.message)
                    # Advance the delivered watermark so the backfill job knows
                    # this message id is already handled for this source.
                    await db.update_source_last_msg(pool, row["source_id"], msg_id)
                except Exception as exc:  # noqa: BLE001
                    # Publish failed: release the claim so the backfill sweep
                    # can retry it (don't silently drop the post).
                    await db.release_tg_message(pool, row["source_id"], msg_id)
                    # One unreachable destination must not block the others.
                    log.warning(
                        "publish to dest %s failed: %s", row["dest_chat_id"], exc
                    )
        except Exception as exc:  # noqa: BLE001
            log.warning("userbot handler error: %s", exc)

    @client.on(events.Album())
    async def _album_handler(event):  # noqa: ANN001
        """Republish a source ALBUM (media group) as a single media group in
        each destination, instead of one post per photo. Telethon buffers the
        grouped messages and fires this once with `event.messages`."""
        try:
            if not (event.is_channel and not event.is_group):
                return
            chat = await event.get_chat()
            chat_id = utils.get_peer_id(chat)
            live_username = getattr(chat, "username", None)
            live_title = getattr(chat, "title", None)
            msgs = sorted(event.messages, key=lambda m: m.id)
            if not msgs:
                return
            rep_id = msgs[0].id   # album's first (lowest) id = watermark anchor
            max_id = msgs[-1].id
            rows = await db.destinations_for_tg_source(pool, chat_id)
            if not rows:
                log.debug(
                    "IN ignore unconfigured album chat_id=%s ids=%s-%s",
                    chat_id, rep_id, max_id,
                )
                return
            log.info(
                "IN album: chat_id=%s username=%r title=%r ids=%s-%s (%d items) "
                "-> %d destination(s)",
                chat_id, live_username, live_title, rep_id, max_id,
                len(msgs), len(rows),
            )
            is_forwarded = msgs[0].fwd_from is not None
            for row in rows:
                last = row["last_tg_msg_id"]
                # Whole album already delivered (watermark covers its top id).
                if last is not None and max_id <= last:
                    log.info(
                        "IN skip duplicate album: src=%s ids=%s-%s already "
                        "delivered (watermark=%s)", chat_id, rep_id, max_id, last,
                    )
                    continue
                # Atomic claim on the album anchor id closes the live-vs-
                # backfill race (backfill claims the same rep_id).
                if not await db.claim_tg_message(pool, row["source_id"], rep_id):
                    log.info(
                        "IN skip duplicate album: src=%s anchor=%s already "
                        "claimed by another path", chat_id, rep_id,
                    )
                    continue
                if is_forwarded and row["skip_forwarded"]:
                    log.info(
                        "skipping forwarded album from %s -> dest %s",
                        chat_id, row["dest_chat_id"],
                    )
                    await db.update_source_last_msg(pool, row["source_id"], max_id)
                    continue
                meta = {
                    "source_label": row["source_label"] or live_title,
                    "source_username": row["source_username"] or live_username,
                    "source_tg_id": row["source_tg_id"] or chat_id,
                    "dest_username": row["dest_username"],
                    "dest_title": row["dest_title"],
                    "show_title": row["show_title"],
                    "link_title": row["link_title"],
                    "dest_show_username": row["dest_show_username"],
                    "lang": row["owner_lang"],
                }
                try:
                    await publish_tg_album(
                        client, row["dest_chat_id"], meta, msgs
                    )
                    # Advance the watermark past the WHOLE album (max id) so
                    # none of its members re-fire through backfill.
                    await db.update_source_last_msg(
                        pool, row["source_id"], max_id
                    )
                except Exception as exc:  # noqa: BLE001
                    await db.release_tg_message(pool, row["source_id"], rep_id)
                    log.warning(
                        "album publish to dest %s failed: %s",
                        row["dest_chat_id"], exc,
                    )
        except Exception as exc:  # noqa: BLE001
            log.warning("userbot album handler error: %s", exc)
