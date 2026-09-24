import os


def _req(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


API_ID = int(_req("API_ID"))
API_HASH = _req("API_HASH")
BOT_TOKEN = _req("BOT_TOKEN")
SESSION_STRING = _req("SESSION_STRING")
DATABASE_URL = _req("DATABASE_URL")

# How often (seconds) to poll RSS feeds.
RSS_POLL_SECONDS = int(os.environ.get("RSS_POLL_SECONDS", "300"))
