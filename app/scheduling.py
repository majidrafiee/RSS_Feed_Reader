import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

log = logging.getLogger("scheduling")

scheduler = AsyncIOScheduler()
_started = False


def start(coro, args, minutes: int) -> None:
    global _started
    scheduler.add_job(
        coro,
        "interval",
        minutes=minutes,
        args=args,
        id="rss",
        max_instances=1,
        coalesce=True,
    )
    if not _started:
        scheduler.start()
        _started = True
    log.info("RSS poller started, interval %s min", minutes)


def start_backfill(coro, args, minutes: int) -> None:
    """Schedule the Telegram backfill sweep (recovers missed source posts)."""
    global _started
    scheduler.add_job(
        coro,
        "interval",
        minutes=minutes,
        args=args,
        id="tg_backfill",
        max_instances=1,
        coalesce=True,
    )
    if not _started:
        scheduler.start()
        _started = True
    log.info("TG backfill started, interval %s min", minutes)


def start_refresh(coro, args, minutes: int) -> None:
    """Periodically re-resolve destinations and refresh their stored
    title/@username from the live channel, so renaming a destination channel
    is reflected in the footer without a restart."""
    global _started
    scheduler.add_job(
        coro,
        "interval",
        minutes=minutes,
        args=args,
        id="dest_refresh",
        max_instances=1,
        coalesce=True,
    )
    if not _started:
        scheduler.start()
        _started = True
    log.info("Destination refresh started, interval %s min", minutes)


def start_resume_watch(coro, args, minutes: int = 1) -> None:
    """Schedule the resume-watch job: it sends an auto-resume notice when a
    timed pause lapses, and prunes the old event log. Needs the aiogram Bot in
    `args` so it can message the owner."""
    global _started
    scheduler.add_job(
        coro,
        "interval",
        minutes=minutes,
        args=args,
        id="resume_watch",
        max_instances=1,
        coalesce=True,
    )
    if not _started:
        scheduler.start()
        _started = True
    log.info("Resume-watch started, interval %s min", minutes)


def reschedule(minutes: int) -> None:
    try:
        scheduler.reschedule_job("rss", trigger="interval", minutes=minutes)
        log.info("RSS interval changed to %s min", minutes)
    except Exception as exc:  # noqa: BLE001
        log.warning("reschedule failed: %s", exc)
