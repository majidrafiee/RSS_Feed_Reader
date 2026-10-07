import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from telethon import TelegramClient
from telethon.sessions import StringSession

from app import config, db, scheduling
from app.backfill import backfill_tg_sources
from app.bot import router
from app.logconf import setup as _log_setup
from app.rss import poll_all_feeds
from app.publisher import prime_destinations
from app.userbot import register_userbot

# Central logging: stderr + rotating file. Must run before any getLogger().
_log_setup()
log = logging.getLogger("main")

# Global userbot health flag — set to True on successful login, stays False
# if the session is dead (AuthKeyDuplicatedError etc). The bot and
# /status command read this to show the owner what's going on.
userbot_alive = False
userbot_error = None   # human-readable reason when alive=False


def _is_session_fatal(exc):
    """Return True if this exception means the StringSession is permanently
    dead and can never connect again."""
    exc_name = type(exc).__name__
    exc_text = str(exc).lower()
    # Telethon raises AuthKeyDuplicatedError when two IPs used the same key.
    # Other auth-key errors (AuthKeyNotFound, AuthKeyUnregistered) are also
    # fatal for a StringSession — they all mean: throw it away and regenerate.
    if "authkey" in exc_name.lower():
        return True
    if "used under two different ip" in exc_text:
        return True
    if "auth key" in exc_text and ("invalid" in exc_text or "not found" in exc_text or "unregistered" in exc_text):
        return True
    # SessionPasswordNeededError is NOT fatal — it just means the account
    # has 2FA and needs the password. That's a config issue, not a dead key.
    return False


async def main() -> None:
    global userbot_alive, userbot_error

    pool = await db.create_pool()
    await db.init_db(pool)
    log.info("Database ready.")

    # --- Try to start the Telethon userbot. If the StringSession is dead
    # (AuthKeyDuplicatedError / any auth-key error), we log a clear message
    # and KEEP THE BOT RUNNING in degraded mode instead of crash-looping.
    client = TelegramClient(
        StringSession(config.SESSION_STRING), config.API_ID, config.API_HASH,
        flood_sleep_threshold=120,
        catch_up=True,
    )

    try:
        await client.start()
        me = await client.get_me()
        reader = ("@" + me.username) if me.username else (me.first_name or "the reader account")
        log.info("Userbot logged in as %s (id=%s)", reader, me.id)
        userbot_alive = True
    except Exception as exc:
        if _is_session_fatal(exc):
            userbot_alive = False
            userbot_error = (
                f"Session dead: {type(exc).__name__} — "
                f"the same StringSession was used from two different IPs, "
                f"so Telegram permanently killed it. You must generate a "
                f"new SESSION_STRING and update the env var."
            )
            log.error(
                "SESSION FATAL: %s — the StringSession is permanently dead. "
                "The bot will run in degraded mode (no userbot). "
                "Generate a new session string and update SESSION_STRING.",
                exc,
            )
            reader = "\u26A0\uFE0F reader (session dead)"
        else:
            # Some other startup error (network, 2FA password, etc).
            # Re-raise — these are not session-key deaths and may be transient.
            log.error("Userbot start failed (non-fatal session error): %s", exc)
            raise

    # --- Only set up userbot + publish pipeline if the session is alive.
    if userbot_alive:
        # Warm the entity cache so Telethon can resolve channel ids by number.
        async for _ in client.iter_dialogs():
            pass

        await prime_destinations(client, pool)
        register_userbot(client, pool)

        scheduling.start(poll_all_feeds, [pool, client], minutes=5)
        scheduling.start_backfill(backfill_tg_sources, [pool, client], minutes=3)
        scheduling.start_refresh(prime_destinations, [client, pool], minutes=15)
    else:
        log.warning(
            "Userbot is dead — running bot in DEGRADED mode. "
"No posts will be delivered until SESSION_STRING is regenerated."
        )

    # --- Always start the aiogram bot, even in degraded mode.
    # The user can still open Settings, toggle dedup, etc.
    bot = Bot(
        config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    log.info(
        "Starting bot (userbot=%s) + RSS poller + backfill\u2026",
        "alive" if userbot_alive else "DEAD",
    )

    # Expose the health state + reader label + pool + client so that
    # /status and other handlers can read them via workflow_data.
    dp["userbot_alive"] = userbot_alive
    dp["userbot_error"] = userbot_error
    dp["reader"] = reader
    dp["pool"] = pool
    dp["client"] = client

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Shutting down.")
