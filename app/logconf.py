"""Central logging configuration.

Adds a **RotatingFileHandler** alongside the default stderr stream so logs
survive a container restart (within the volume) and don't grow unbounded.
Every app module already uses named loggers (``logging.getLogger('userbot')``,
``logging.getLogger('publisher')``, etc) so this config is applied once at
startup and inherited everywhere.

Two log destinations, same content:
  - **stderr** — consumed by Northflank / Docker (ephemeral, lost on redeploy)
  - **Rotating file** — ``data/bot.log`` (survives redeploy if ``data/`` is a
    mounted volume, 2 files × 5 MB = 10 MB ceiling)

Optional env vars
-----------------
``LOG_DIR`` (default ``data``)
    Where to write ``bot.log``. Make this a persistent volume on Northflank
    and the log survives redeploy.
``LOG_MAX_BYTES`` (default ``5242880``, i.e. 5 MB)
    Size at which the file is rotated.
``LOG_BACKUP_COUNT`` (default ``1``)
    Number of rotated files to keep. Total ceiling = max_bytes × (count+1).
"""

import logging
import os
from logging.handlers import RotatingFileHandler

_FMT = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup():
    """Apply the rotating-file + stderr logging configuration.

    Call once from ``main.py`` **before** anything else logs.
    """
    log_dir = os.environ.get("LOG_DIR", "data")
    max_bytes = int(os.environ.get("LOG_MAX_BYTES", "5242880"))
    backup_count = int(os.environ.get("LOG_BACKUP_COUNT", "1"))
    level = os.environ.get("LOG_LEVEL", "INFO").upper()

    # Ensure the directory exists.
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "bot.log")

    # Root logger — reset handlers so we control both outputs.
    root = logging.getLogger()
    root.setLevel(getattr(logging, level, logging.INFO))
    root.handlers.clear()

    # Stream handler (stderr) — what Northflank captures today.
    sh = logging.StreamHandler()
    sh.setFormatter(_FMT)
    root.addHandler(sh)

    # Rotating file handler — persists across container restarts if LOG_DIR
    # is a mounted volume.
    fh = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    fh.setFormatter(_FMT)
    root.addHandler(fh)

    # Third-party noise reduction: only show WARNING+ from aiogram internals,
    # telethon internals, and APScheduler internals.
    for noisy in ("aiogram.dispatcher", "telethon.client", "apscheduler"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Our own modules keep the root level (INFO by default).
    logging.getLogger("app.logconf").info(
        "Logging: stderr + rotating file (%s, %d×%d MB)",
        log_path, backup_count + 1, max_bytes // (1024 * 1024),
    )
