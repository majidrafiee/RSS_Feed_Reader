import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from telethon import TelegramClient
from telethon.sessions import StringSession

from app import config, db, scheduling
from app.backfill import backfill_tg_sources
from app.bot import router
from app.rss import poll_all_feeds
from app.publisher import prime_destinations
from app.userbot import register_userbot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("main")


async def main() -> None:
    pool = await db.create_pool()
    await db.init_db(pool)
    log.info("Database ready.")

    client = TelegramClient(
        StringSession(config.SESSION_STRING), config.API_ID, config.API_HASH,
        # Auto-sleep through Telegram rate limits instead of raising, so a
        # burst of posts doesn't drop any. Replay buffered updates on connect.
        flood_sleep_threshold=120,
        catch_up=True,
    )
    await client.start()
    me = await client.get_me()
    reader = ("@" + me.username) if me.username else (me.first_name or "the reader account")
    log.info("Userbot logged in as %s (id=%s)", reader, me.id)

    # Warm the entity cache so Telethon can resolve channel ids by number.
    # The destination channel must be cached to be sendable.
    async for _ in client.iter_dialogs():
        pass

    # Resolve + cache every known destination up front. This avoids a
    # GetDialogs stampede (and the flood-waits it causes) when many posts
    # arrive at once, and logs by TITLE exactly which channel the reader
    # still can't post to.
    await prime_destinations(client, pool)

    register_userbot(client, pool)

    bot = Bot(
        config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # Start the RSS poller. Default interval 5 min; the user can change it
    # from Settings, which reschedules this same job live.
    scheduling.start(poll_all_feeds, [pool, client], minutes=5)

    # Safety net: every 3 min, sweep each Telegram source for any posts the
    # live event stream missed (channelDifferenceTooLong / restart downtime)
    # and deliver them, so nothing is silently dropped.
    scheduling.start_backfill(backfill_tg_sources, [pool, client], minutes=3)

    # Every 15 min, re-check each destination and refresh its stored
    # title/@username from the live channel, so renaming a destination (or
    # adding a username) shows up in the footer without a restart.
    scheduling.start_refresh(prime_destinations, [client, pool], minutes=15)

    log.info("Starting bot + userbot + RSS poller + backfill\u2026")
    await asyncio.gather(
        dp.start_polling(bot, pool=pool, client=client, reader=reader),
        client.run_until_disconnected(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Shutting down.")
