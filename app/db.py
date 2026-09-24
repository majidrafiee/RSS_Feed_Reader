import asyncpg

from app import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS destinations (
    id           BIGSERIAL PRIMARY KEY,
    owner_tg_id  BIGINT NOT NULL,
    chat_id      BIGINT NOT NULL,
    title        TEXT,
    username     TEXT,
    created_at   TIMESTAMPTZ DEFAULT now(),
    UNIQUE (owner_tg_id, chat_id)
);

CREATE TABLE IF NOT EXISTS sources (
    id             BIGSERIAL PRIMARY KEY,
    destination_id BIGINT NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
    kind           TEXT NOT NULL,
    identifier     TEXT NOT NULL,
    tg_chat_id     BIGINT,
    username       TEXT,
    label          TEXT,
    -- Per-source display overrides. NULL means "inherit the user's global
    -- setting" so existing behaviour is preserved until the user changes it.
    custom_label   TEXT,      -- user-chosen name; NULL = use the auto label
    show_title     BOOLEAN,   -- NULL = inherit user_settings.show_title
    link_title     BOOLEAN,   -- NULL = inherit user_settings.link_title
    created_at     TIMESTAMPTZ DEFAULT now(),
    UNIQUE (destination_id, kind, identifier)
);

CREATE TABLE IF NOT EXISTS seen_items (
    id         BIGSERIAL PRIMARY KEY,
    source_id  BIGINT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    guid       TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (source_id, guid)
);

CREATE TABLE IF NOT EXISTS user_settings (
    tg_user_id     BIGINT PRIMARY KEY,
    language       TEXT NOT NULL DEFAULT 'en',
    check_interval INT  NOT NULL DEFAULT 5,
    skip_forwarded BOOLEAN NOT NULL DEFAULT TRUE,
    show_title         BOOLEAN NOT NULL DEFAULT TRUE,
    link_title         BOOLEAN NOT NULL DEFAULT TRUE,
    dest_show_username BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_sources_tgchat
    ON sources (tg_chat_id) WHERE kind = 'tg';

-- migrations for older deployments
ALTER TABLE destinations ADD COLUMN IF NOT EXISTS username TEXT;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS username TEXT;
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS show_title BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS link_title BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS dest_show_username BOOLEAN NOT NULL DEFAULT TRUE;
-- tracks the highest source message id we have already delivered, so a
-- periodic backfill can recover any posts the live event stream missed
-- (channelDifferenceTooLong / restarts).
ALTER TABLE sources ADD COLUMN IF NOT EXISTS last_tg_msg_id BIGINT;
-- per-source display overrides (nullable = inherit the user default)
ALTER TABLE sources ADD COLUMN IF NOT EXISTS custom_label TEXT;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS show_title BOOLEAN;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS link_title BOOLEAN;
"""


async def create_pool():
    return await asyncpg.create_pool(config.DATABASE_URL, min_size=1, max_size=5)


async def init_db(pool):
    async with pool.acquire() as con:
        await con.execute(SCHEMA)


# ---------- settings ----------
async def get_settings(pool, tg_id, default_lang="en"):
    async with pool.acquire() as con:
        row = await con.fetchrow(
            "SELECT * FROM user_settings WHERE tg_user_id = $1", tg_id
        )
        if row is None:
            await con.execute(
                "INSERT INTO user_settings (tg_user_id, language) VALUES ($1, $2) "
                "ON CONFLICT DO NOTHING",
                tg_id, default_lang,
            )
            row = await con.fetchrow(
                "SELECT * FROM user_settings WHERE tg_user_id = $1", tg_id
            )
        return row


async def set_language(pool, tg_id, lang):
    async with pool.acquire() as con:
        await con.execute(
            "INSERT INTO user_settings (tg_user_id, language) VALUES ($1, $2) "
            "ON CONFLICT (tg_user_id) DO UPDATE SET language = EXCLUDED.language",
            tg_id, lang,
        )


async def set_interval(pool, tg_id, minutes):
    async with pool.acquire() as con:
        await con.execute(
            "INSERT INTO user_settings (tg_user_id, check_interval) VALUES ($1, $2) "
            "ON CONFLICT (tg_user_id) DO UPDATE SET check_interval = EXCLUDED.check_interval",
            tg_id, minutes,
        )


async def toggle_skip_forwarded(pool, tg_id):
    async with pool.acquire() as con:
        return await con.fetchval(
            "INSERT INTO user_settings (tg_user_id, skip_forwarded) VALUES ($1, FALSE) "
            "ON CONFLICT (tg_user_id) DO UPDATE "
            "SET skip_forwarded = NOT user_settings.skip_forwarded "
            "RETURNING skip_forwarded",
            tg_id,
        )


async def _toggle_bool(pool, tg_id, column, default_when_new):
    """Generic boolean toggle for user_settings columns."""
    async with pool.acquire() as con:
        return await con.fetchval(
            f"INSERT INTO user_settings (tg_user_id, {column}) VALUES ($1, $2) "
            f"ON CONFLICT (tg_user_id) DO UPDATE "
            f"SET {column} = NOT user_settings.{column} "
            f"RETURNING {column}",
            tg_id, default_when_new,
        )


async def toggle_show_title(pool, tg_id):
    return await _toggle_bool(pool, tg_id, "show_title", False)


async def toggle_link_title(pool, tg_id):
    return await _toggle_bool(pool, tg_id, "link_title", False)


async def toggle_dest_show_username(pool, tg_id):
    return await _toggle_bool(pool, tg_id, "dest_show_username", False)


# ---------- destinations ----------
async def add_destination(pool, owner, chat_id, title, username):
    async with pool.acquire() as con:
        return await con.fetchrow(
            "INSERT INTO destinations (owner_tg_id, chat_id, title, username) "
            "VALUES ($1, $2, $3, $4) "
            "ON CONFLICT (owner_tg_id, chat_id) DO UPDATE "
            "SET title = EXCLUDED.title, username = EXCLUDED.username RETURNING *",
            owner, chat_id, title, username,
        )


async def list_destinations(pool, owner):
    async with pool.acquire() as con:
        return await con.fetch(
            "SELECT * FROM destinations WHERE owner_tg_id = $1 ORDER BY id", owner
        )


async def all_destinations(pool):
    async with pool.acquire() as con:
        return await con.fetch("SELECT * FROM destinations ORDER BY id")


async def update_destination_meta(pool, chat_id, title, username):
    """Refresh a destination's stored display name / @username from the LIVE
    channel. The title/username were captured once when the channel was first
    forwarded to the bot; if the user later renames the channel or adds a
    username, the footer kept showing the stale value. Calling this keeps the
    footer label in sync (and lets the @username toggle actually differ).
    `username` may be NULL when the channel is private / has no username.
    """
    async with pool.acquire() as con:
        await con.execute(
            "UPDATE destinations SET title = COALESCE($2, title), "
            "username = $3 WHERE chat_id = $1",
            chat_id, title, username,
        )


async def get_destination(pool, dest_id, owner):
    async with pool.acquire() as con:
        return await con.fetchrow(
            "SELECT * FROM destinations WHERE id = $1 AND owner_tg_id = $2",
            dest_id, owner,
        )


async def delete_destination(pool, dest_id, owner):
    """Delete a destination (its sources + seen items cascade away)."""
    async with pool.acquire() as con:
        return await con.fetchrow(
            "DELETE FROM destinations WHERE id = $1 AND owner_tg_id = $2 "
            "RETURNING title",
            dest_id, owner,
        )


# ---------- sources ----------
async def add_source(pool, dest_id, kind, identifier, tg_chat_id, username, label):
    async with pool.acquire() as con:
        return await con.fetchrow(
            "INSERT INTO sources (destination_id, kind, identifier, tg_chat_id, username, label) "
            "VALUES ($1, $2, $3, $4, $5, $6) "
            "ON CONFLICT (destination_id, kind, identifier) DO UPDATE "
            "SET label = EXCLUDED.label, tg_chat_id = EXCLUDED.tg_chat_id, "
            "username = EXCLUDED.username RETURNING *",
            dest_id, kind, identifier, tg_chat_id, username, label,
        )


async def list_sources(pool, dest_id):
    async with pool.acquire() as con:
        return await con.fetch(
            "SELECT * FROM sources WHERE destination_id = $1 ORDER BY id", dest_id
        )


async def list_sources_for_owner(pool, owner):
    """All sources for a user, each with its destination title. The label is
    the effective display name (custom name if the user set one, else the
    auto-detected name)."""
    async with pool.acquire() as con:
        return await con.fetch(
            "SELECT s.id, s.kind, "
            "       COALESCE(s.custom_label, s.label) AS label, "
            "       d.title AS dest_title "
            "FROM sources s JOIN destinations d ON s.destination_id = d.id "
            "WHERE d.owner_tg_id = $1 ORDER BY d.id, s.id",
            owner,
        )


async def delete_source(pool, source_id, owner):
    """Delete a single source, checking it belongs to the owner."""
    async with pool.acquire() as con:
        return await con.fetchrow(
            "DELETE FROM sources s USING destinations d "
            "WHERE s.id = $1 AND s.destination_id = d.id AND d.owner_tg_id = $2 "
            "RETURNING s.label",
            source_id, owner,
        )


# ---------- per-source display settings ----------
# Only these source columns may be toggled; whitelisted so the column name can
# never be attacker-controlled in the f-string below.
_SOURCE_BOOL_COLUMNS = {"show_title", "link_title"}


async def get_source_detail(pool, source_id, owner):
    """Fetch one source (owner-checked) with everything the edit menu needs:
    the auto/default name, the custom name (if any), and the EFFECTIVE
    show_title / link_title (per-source override, else the user default)."""
    async with pool.acquire() as con:
        return await con.fetchrow(
            "SELECT s.id, s.kind, s.label, s.custom_label, s.username, "
            "       s.identifier, "
            "       COALESCE(s.custom_label, s.label) AS effective_label, "
            "       (s.custom_label IS NOT NULL) AS has_custom_label, "
            "       COALESCE(s.show_title, us.show_title, TRUE) AS show_title, "
            "       COALESCE(s.link_title, us.link_title, TRUE) AS link_title, "
            "       d.title AS dest_title "
            "FROM sources s JOIN destinations d ON d.id = s.destination_id "
            "LEFT JOIN user_settings us ON us.tg_user_id = d.owner_tg_id "
            "WHERE s.id = $1 AND d.owner_tg_id = $2",
            source_id, owner,
        )


async def toggle_source_flag(pool, source_id, owner, column):
    """Flip a per-source boolean display flag (show_title / link_title).

    The stored value may be NULL (inherit the user default), so we first read
    the EFFECTIVE current value, then write the explicit opposite. Returns the
    new boolean value, or None if the source doesn't belong to the owner."""
    if column not in _SOURCE_BOOL_COLUMNS:
        raise ValueError(f"illegal source column: {column}")
    async with pool.acquire() as con:
        row = await con.fetchrow(
            f"SELECT COALESCE(s.{column}, us.{column}, TRUE) AS eff "
            "FROM sources s JOIN destinations d ON d.id = s.destination_id "
            "LEFT JOIN user_settings us ON us.tg_user_id = d.owner_tg_id "
            "WHERE s.id = $1 AND d.owner_tg_id = $2",
            source_id, owner,
        )
        if row is None:
            return None
        new_val = not row["eff"]
        await con.execute(
            f"UPDATE sources SET {column} = $2 WHERE id = $1",
            source_id, new_val,
        )
        return new_val


async def set_source_custom_label(pool, source_id, owner, label):
    """Set a user-chosen display name for a source (owner-checked). Returns the
    saved label, or None if the source isn't the owner's."""
    label = (label or "").strip()
    if not label:
        return None
    async with pool.acquire() as con:
        return await con.fetchval(
            "UPDATE sources s SET custom_label = $3 "
            "FROM destinations d "
            "WHERE s.id = $1 AND s.destination_id = d.id AND d.owner_tg_id = $2 "
            "RETURNING s.custom_label",
            source_id, owner, label,
        )


async def reset_source_custom_label(pool, source_id, owner):
    """Clear the custom name so the source falls back to its auto-detected
    name. Returns the default (auto) label, or None if not the owner's."""
    async with pool.acquire() as con:
        return await con.fetchval(
            "UPDATE sources s SET custom_label = NULL "
            "FROM destinations d "
            "WHERE s.id = $1 AND s.destination_id = d.id AND d.owner_tg_id = $2 "
            "RETURNING s.label",
            source_id, owner,
        )


async def destinations_for_tg_source(pool, tg_chat_id):
    async with pool.acquire() as con:
        return await con.fetch(
            "SELECT s.id AS source_id, "
            "       COALESCE(s.custom_label, s.label) AS source_label, "
            "       s.username AS source_username, "
            "       s.tg_chat_id AS source_tg_id, s.last_tg_msg_id, "
            "       d.chat_id AS dest_chat_id, d.username AS dest_username, "
            "       d.title AS dest_title, "
            "       COALESCE(us.skip_forwarded, TRUE) AS skip_forwarded, "
            "       COALESCE(s.show_title, us.show_title, TRUE) AS show_title, "
            "       COALESCE(s.link_title, us.link_title, TRUE) AS link_title, "
            "       COALESCE(us.dest_show_username, TRUE) AS dest_show_username, "
            "       COALESCE(us.language, 'en') AS owner_lang "
            "FROM sources s JOIN destinations d ON d.id = s.destination_id "
            "LEFT JOIN user_settings us ON us.tg_user_id = d.owner_tg_id "
            "WHERE s.kind = 'tg' AND s.tg_chat_id = $1",
            tg_chat_id,
        )


async def all_tg_sources(pool):
    """Every Telegram source with its destination + owner formatting settings
    and the last delivered message id. Used by the periodic backfill to recover
    posts the live event stream may have missed."""
    async with pool.acquire() as con:
        return await con.fetch(
            "SELECT s.id AS source_id, "
            "       COALESCE(s.custom_label, s.label) AS source_label, "
            "       s.username AS source_username, "
            "       s.tg_chat_id AS source_tg_id, s.last_tg_msg_id, "
            "       d.chat_id AS dest_chat_id, d.username AS dest_username, "
            "       d.title AS dest_title, "
            "       COALESCE(us.skip_forwarded, TRUE) AS skip_forwarded, "
            "       COALESCE(s.show_title, us.show_title, TRUE) AS show_title, "
            "       COALESCE(s.link_title, us.link_title, TRUE) AS link_title, "
            "       COALESCE(us.dest_show_username, TRUE) AS dest_show_username, "
            "       COALESCE(us.language, 'en') AS owner_lang "
            "FROM sources s JOIN destinations d ON d.id = s.destination_id "
            "LEFT JOIN user_settings us ON us.tg_user_id = d.owner_tg_id "
            "WHERE s.kind = 'tg' AND s.tg_chat_id IS NOT NULL "
            "ORDER BY s.tg_chat_id, s.id"
        )


async def update_source_last_msg(pool, source_id, msg_id):
    """Advance the delivered-watermark for a source. Never moves backwards."""
    if msg_id is None:
        return
    async with pool.acquire() as con:
        await con.execute(
            "UPDATE sources SET last_tg_msg_id = GREATEST("
            "COALESCE(last_tg_msg_id, 0), $2) WHERE id = $1",
            source_id, msg_id,
        )


async def all_rss_sources(pool):
    async with pool.acquire() as con:
        return await con.fetch(
            "SELECT s.id, s.identifier, "
            "       COALESCE(s.custom_label, s.label) AS label, "
            "       d.chat_id AS dest_chat_id, d.username AS dest_username, "
            "       d.title AS dest_title, "
            "       COALESCE(s.show_title, us.show_title, TRUE) AS show_title, "
            "       COALESCE(s.link_title, us.link_title, TRUE) AS link_title, "
            "       COALESCE(us.dest_show_username, TRUE) AS dest_show_username, "
            "       COALESCE(us.language, 'en') AS owner_lang "
            "FROM sources s JOIN destinations d ON d.id = s.destination_id "
            "LEFT JOIN user_settings us ON us.tg_user_id = d.owner_tg_id "
            "WHERE s.kind = 'rss'"
        )


async def is_seen(pool, source_id, guid) -> bool:
    async with pool.acquire() as con:
        row = await con.fetchval(
            "SELECT 1 FROM seen_items WHERE source_id = $1 AND guid = $2",
            source_id, guid,
        )
        return row is not None


async def mark_seen(pool, source_id, guid) -> None:
    async with pool.acquire() as con:
        await con.execute(
            "INSERT INTO seen_items (source_id, guid) VALUES ($1, $2) "
            "ON CONFLICT DO NOTHING",
            source_id, guid,
        )


def _tg_guid(msg_id) -> str:
    # Namespaced so a Telegram message id can never collide with an RSS guid
    # stored for the same source row.
    return f"tg:{msg_id}"


async def claim_tg_message(pool, source_id, msg_id) -> bool:
    """Atomically claim a Telegram (source, message) for delivery.

    Returns True if THIS caller won the claim and should publish; False if the
    message was already claimed by a concurrent path. The live userbot and the
    3-minute backfill sweep can both see the same post before either has
    advanced the watermark (the duplicate bug the user saw). This turns the
    check-and-set into a SINGLE race-free DB operation via the
    seen_items UNIQUE(source_id, guid) constraint, so exactly one path
    publishes each post.
    """
    if msg_id is None:
        return False
    async with pool.acquire() as con:
        row = await con.fetchval(
            "INSERT INTO seen_items (source_id, guid) VALUES ($1, $2) "
            "ON CONFLICT (source_id, guid) DO NOTHING RETURNING id",
            source_id, _tg_guid(msg_id),
        )
        return row is not None


async def release_tg_message(pool, source_id, msg_id) -> None:
    """Undo a claim when publishing FAILED, so the backfill sweep can retry the
    post later instead of it being silently lost (preserves the no-drop
    guarantee)."""
    if msg_id is None:
        return
    async with pool.acquire() as con:
        await con.execute(
            "DELETE FROM seen_items WHERE source_id = $1 AND guid = $2",
            source_id, _tg_guid(msg_id),
        )
