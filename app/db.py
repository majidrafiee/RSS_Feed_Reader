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
    dest_show_username BOOLEAN NOT NULL DEFAULT TRUE,
    ad_filter_enabled  BOOLEAN NOT NULL DEFAULT FALSE,
    dedup_enabled      BOOLEAN NOT NULL DEFAULT FALSE,
    dedup_window_min   INT NOT NULL DEFAULT 30,
    dedup_threshold    INT NOT NULL DEFAULT 90,
    dedup_min_len      INT NOT NULL DEFAULT 20
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
-- Per-source pause. `paused` = paused indefinitely until the owner resumes;
-- `paused_until` = paused only until that moment (timed pause). A source is
-- EFFECTIVELY paused when paused OR (paused_until IS NOT NULL AND in future).
-- While paused we skip delivery AND advance the watermark, so resuming does
-- NOT dump the whole pause gap at once.
ALTER TABLE sources ADD COLUMN IF NOT EXISTS paused BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS paused_until TIMESTAMPTZ;

-- Runtime-managed ad filter. The owner adds block phrases / @handles /
-- #hashtags / words through the bot (never hardcoded); when the toggle is on
-- we skip matching NEW incoming posts, and a separate confirm-gated action can
-- delete already-posted ads from the destinations.
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS ad_filter_enabled BOOLEAN NOT NULL DEFAULT FALSE;
CREATE TABLE IF NOT EXISTS ad_filters (
    id          BIGSERIAL PRIMARY KEY,
    owner_tg_id BIGINT NOT NULL,
    pattern     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_adfilters_owner_pattern
    ON ad_filters (owner_tg_id, lower(pattern));
CREATE INDEX IF NOT EXISTS idx_adfilters_owner
    ON ad_filters (owner_tg_id);

-- Near-duplicate suppression. The owner can toggle it, and tune the lookback
-- window (minutes), similarity threshold (percent) and the minimum caption
-- length below which dedup is skipped. All comparison is lexical and done in
-- memory — these columns only persist the per-user knobs.
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS dedup_enabled BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS dedup_window_min INT NOT NULL DEFAULT 30;
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS dedup_threshold INT NOT NULL DEFAULT 90;
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS dedup_min_len INT NOT NULL DEFAULT 20;

-- Per-source delivery timestamp. Updated ONLY on a real publish (never on a
-- skip), so /status can show each source's last-delivered time and flag a
-- source that is active+unpaused yet silently stalled.
ALTER TABLE sources ADD COLUMN IF NOT EXISTS last_delivered_at TIMESTAMPTZ;
-- When a TIMED pause is set we owe the owner one "resumed" notice once
-- paused_until passes; the resume-watch job sends it and clears this flag.
ALTER TABLE sources ADD COLUMN IF NOT EXISTS resume_notice_pending BOOLEAN NOT NULL DEFAULT FALSE;

-- Lightweight runtime heartbeats (last RSS poll / last backfill sweep), read
-- by /status so a stalled pipeline is visible.
CREATE TABLE IF NOT EXISTS runtime_kv (
    k   TEXT PRIMARY KEY,
    ts  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Pipeline event log for /stats: one row per published or dropped post, with
-- the drop reason. Pruned to the last 30 days by the resume-watch job.
CREATE TABLE IF NOT EXISTS events (
    id           BIGSERIAL PRIMARY KEY,
    owner_tg_id  BIGINT NOT NULL,
    dest_chat_id BIGINT,
    source_id    BIGINT,
    kind         TEXT NOT NULL,   -- 'pub' | 'drop'
    reason       TEXT,            -- drop reason: forwarded|paused|ad-filter|dedup
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_events_owner_time
    ON events (owner_tg_id, created_at);
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


async def toggle_ad_filter_enabled(pool, tg_id):
    # Default OFF, so the first tap turns it ON (insert TRUE for a new row).
    return await _toggle_bool(pool, tg_id, "ad_filter_enabled", True)


async def toggle_dedup_enabled(pool, tg_id):
    return await _toggle_bool(pool, tg_id, "dedup_enabled", True)


async def _set_int(pool, tg_id, column, value):
    """Generic integer setter for user_settings columns."""
    async with pool.acquire() as con:
        await con.execute(
            f"INSERT INTO user_settings (tg_user_id, {column}) VALUES ($1, $2) "
            f"ON CONFLICT (tg_user_id) DO UPDATE SET {column} = $2",
            tg_id, value,
        )


async def set_dedup_window(pool, tg_id, minutes):
    await _set_int(pool, tg_id, "dedup_window_min", int(minutes))


async def set_dedup_threshold(pool, tg_id, percent):
    await _set_int(pool, tg_id, "dedup_threshold", int(percent))


async def set_dedup_min_len(pool, tg_id, chars):
    await _set_int(pool, tg_id, "dedup_min_len", int(chars))


async def add_ad_filter(pool, owner, pattern):
    """Store one block phrase/@handle/#hashtag/word for this owner. Returns the
    new row, or None if it was blank or already present (case-insensitive)."""
    pattern = (pattern or "").strip()
    if not pattern:
        return None
    async with pool.acquire() as con:
        return await con.fetchrow(
            "INSERT INTO ad_filters (owner_tg_id, pattern) VALUES ($1, $2) "
            "ON CONFLICT (owner_tg_id, lower(pattern)) DO NOTHING "
            "RETURNING *",
            owner, pattern,
        )


async def list_ad_filters(pool, owner):
    async with pool.acquire() as con:
        return await con.fetch(
            "SELECT * FROM ad_filters WHERE owner_tg_id = $1 ORDER BY id",
            owner,
        )


async def delete_ad_filter(pool, owner, filter_id):
    async with pool.acquire() as con:
        return await con.fetchrow(
            "DELETE FROM ad_filters WHERE id = $1 AND owner_tg_id = $2 "
            "RETURNING *",
            filter_id, owner,
        )


async def get_ad_patterns(pool, owner):
    """Plain list of this owner's block patterns (used to gate new posts)."""
    if owner is None:
        return []
    async with pool.acquire() as con:
        rows = await con.fetch(
            "SELECT pattern FROM ad_filters WHERE owner_tg_id = $1", owner
        )
    return [r["pattern"] for r in rows]


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
            "       (s.paused OR (s.paused_until IS NOT NULL "
            "            AND s.paused_until > now())) AS is_paused, "
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
            "       s.paused AS paused, s.paused_until AS paused_until, "
            "       (s.paused OR (s.paused_until IS NOT NULL "
            "            AND s.paused_until > now())) AS is_paused, "
            "       GREATEST(0, CEIL(EXTRACT(EPOCH FROM "
            "            (s.paused_until - now())) / 60.0))::int "
            "            AS paused_minutes_left, "
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


async def pause_source(pool, source_id, owner, minutes=None):
    """Pause a source (owner-checked).

    minutes=None  -> pause INDEFINITELY (until the owner resumes).
    minutes=<int> -> pause only until now()+minutes (a timed pause).

    Returns True if a row was updated, False if the source isn't the owner's.
    """
    async with pool.acquire() as con:
        if minutes is None:
            row = await con.fetchrow(
                "UPDATE sources s SET paused = TRUE, paused_until = NULL "
                "FROM destinations d "
                "WHERE s.id = $1 AND s.destination_id = d.id "
                "      AND d.owner_tg_id = $2 "
                "RETURNING s.id",
                source_id, owner,
            )
        else:
            row = await con.fetchrow(
                "UPDATE sources s SET paused = FALSE, "
                "       paused_until = now() + make_interval(mins => $3) "
                "FROM destinations d "
                "WHERE s.id = $1 AND s.destination_id = d.id "
                "      AND d.owner_tg_id = $2 "
                "RETURNING s.id",
                source_id, owner, int(minutes),
            )
        return row is not None


async def resume_source(pool, source_id, owner):
    """Clear any pause (indefinite or timed) so the source delivers again.
    Returns True if a row was updated, False if not the owner's."""
    async with pool.acquire() as con:
        row = await con.fetchrow(
            "UPDATE sources s SET paused = FALSE, paused_until = NULL "
            "FROM destinations d "
            "WHERE s.id = $1 AND s.destination_id = d.id "
            "      AND d.owner_tg_id = $2 "
            "RETURNING s.id",
            source_id, owner,
        )
        return row is not None


async def destinations_for_tg_source(pool, tg_chat_id):
    async with pool.acquire() as con:
        return await con.fetch(
            "SELECT s.id AS source_id, "
            "       COALESCE(s.custom_label, s.label) AS source_label, "
            "       s.username AS source_username, "
            "       s.tg_chat_id AS source_tg_id, s.last_tg_msg_id, "
            "       (s.paused OR (s.paused_until IS NOT NULL "
            "            AND s.paused_until > now())) AS is_paused, "
            "       d.chat_id AS dest_chat_id, d.username AS dest_username, "
            "       d.title AS dest_title, "
            "       COALESCE(us.skip_forwarded, TRUE) AS skip_forwarded, "
            "       COALESCE(s.show_title, us.show_title, TRUE) AS show_title, "
            "       COALESCE(s.link_title, us.link_title, TRUE) AS link_title, "
            "       COALESCE(us.dest_show_username, TRUE) AS dest_show_username, "
            "       d.owner_tg_id AS owner_tg_id, "
            "       COALESCE(us.ad_filter_enabled, FALSE) AS ad_filter_enabled, "
            "       COALESCE(us.dedup_enabled, FALSE) AS dedup_enabled, "
            "       COALESCE(us.dedup_window_min, 30) AS dedup_window_min, "
            "       COALESCE(us.dedup_threshold, 90) AS dedup_threshold, "
            "       COALESCE(us.dedup_min_len, 20) AS dedup_min_len, "
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
            "       (s.paused OR (s.paused_until IS NOT NULL "
            "            AND s.paused_until > now())) AS is_paused, "
            "       d.chat_id AS dest_chat_id, d.username AS dest_username, "
            "       d.title AS dest_title, "
            "       COALESCE(us.skip_forwarded, TRUE) AS skip_forwarded, "
            "       COALESCE(s.show_title, us.show_title, TRUE) AS show_title, "
            "       COALESCE(s.link_title, us.link_title, TRUE) AS link_title, "
            "       COALESCE(us.dest_show_username, TRUE) AS dest_show_username, "
            "       d.owner_tg_id AS owner_tg_id, "
            "       COALESCE(us.ad_filter_enabled, FALSE) AS ad_filter_enabled, "
            "       COALESCE(us.dedup_enabled, FALSE) AS dedup_enabled, "
            "       COALESCE(us.dedup_window_min, 30) AS dedup_window_min, "
            "       COALESCE(us.dedup_threshold, 90) AS dedup_threshold, "
            "       COALESCE(us.dedup_min_len, 20) AS dedup_min_len, "
            "       COALESCE(us.language, 'en') AS owner_lang "
            "FROM sources s JOIN destinations d ON d.id = s.destination_id "
            "LEFT JOIN user_settings us ON us.tg_user_id = d.owner_tg_id "
            "WHERE s.kind = 'tg' AND s.tg_chat_id IS NOT NULL "
            "ORDER BY s.tg_chat_id, s.id"
        )


async def update_source_last_msg(pool, source_id, msg_id, delivered=False):
    """Advance the delivered-watermark for a source. Never moves backwards.

    When `delivered` is True this was a REAL publish (not a skip), so we also
    stamp last_delivered_at — used by /status for last-delivered + stall
    detection.
    """
    if msg_id is None:
        return
    async with pool.acquire() as con:
        if delivered:
            await con.execute(
                "UPDATE sources SET last_tg_msg_id = GREATEST("
                "COALESCE(last_tg_msg_id, 0), $2), last_delivered_at = now() "
                "WHERE id = $1",
                source_id, msg_id,
            )
        else:
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
            "       d.owner_tg_id AS owner_tg_id, "
            "       COALESCE(us.ad_filter_enabled, FALSE) AS ad_filter_enabled, "
            "       COALESCE(us.dedup_enabled, FALSE) AS dedup_enabled, "
            "       COALESCE(us.dedup_window_min, 30) AS dedup_window_min, "
            "       COALESCE(us.dedup_threshold, 90) AS dedup_threshold, "
            "       COALESCE(us.dedup_min_len, 20) AS dedup_min_len, "
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


# ---------- pipeline event log (for /stats) ----------
async def record_event(pool, owner_tg_id, kind, reason=None,
                       dest_chat_id=None, source_id=None):
    """Log one pipeline event. kind='pub' for a published post, kind='drop'
    with a reason (forwarded|paused|ad-filter|dedup) for a skipped one.
    Best-effort: a logging failure must never break delivery, so swallow
    errors here."""
    if owner_tg_id is None:
        return
    try:
        async with pool.acquire() as con:
            await con.execute(
                "INSERT INTO events (owner_tg_id, dest_chat_id, source_id, "
                "kind, reason) VALUES ($1, $2, $3, $4, $5)",
                owner_tg_id, dest_chat_id, source_id, kind, reason,
            )
    except Exception:
        pass


async def stats_counts(pool, owner_tg_id, days=7):
    """Return (published_count, [(reason, count), ...]) over the last `days`
    for this owner. Drop reasons are ordered most-frequent first."""
    async with pool.acquire() as con:
        pub = await con.fetchval(
            "SELECT COUNT(*) FROM events "
            "WHERE owner_tg_id = $1 AND kind = 'pub' "
            "      AND created_at >= now() - make_interval(days => $2)",
            owner_tg_id, int(days),
        )
        rows = await con.fetch(
            "SELECT reason, COUNT(*) AS n FROM events "
            "WHERE owner_tg_id = $1 AND kind = 'drop' "
            "      AND created_at >= now() - make_interval(days => $2) "
            "GROUP BY reason ORDER BY n DESC",
            owner_tg_id, int(days),
        )
    return int(pub or 0), [(r["reason"] or "other", int(r["n"])) for r in rows]


async def prune_events(pool, days=30):
    """Delete event rows older than `days` so the table stays small."""
    async with pool.acquire() as con:
        await con.execute(
            "DELETE FROM events WHERE created_at < now() - "
            "make_interval(days => $1)",
            int(days),
        )


# ---------- runtime heartbeats (for /status) ----------
async def touch_runtime(pool, key):
    """Record that `key` (e.g. 'rss_poll', 'backfill') just ran."""
    try:
        async with pool.acquire() as con:
            await con.execute(
                "INSERT INTO runtime_kv (k, ts) VALUES ($1, now()) "
                "ON CONFLICT (k) DO UPDATE SET ts = now()",
                key,
            )
    except Exception:
        pass


async def get_runtime(pool):
    """All runtime heartbeats as a {key: timestamp} dict."""
    async with pool.acquire() as con:
        rows = await con.fetch("SELECT k, ts FROM runtime_kv")
    return {r["k"]: r["ts"] for r in rows}


# ---------- bulk pause / resume ----------
async def pause_all_sources(pool, owner, minutes=None):
    """Pause EVERY source the owner has. minutes=None pauses indefinitely,
    otherwise a timed pause. Returns the number of sources affected."""
    async with pool.acquire() as con:
        if minutes is None:
            rows = await con.fetch(
                "UPDATE sources s SET paused = TRUE, paused_until = NULL, "
                "       resume_notice_pending = FALSE "
                "FROM destinations d "
                "WHERE s.destination_id = d.id AND d.owner_tg_id = $1 "
                "RETURNING s.id",
                owner,
            )
        else:
            rows = await con.fetch(
                "UPDATE sources s SET paused = FALSE, "
                "       paused_until = now() + make_interval(mins => $2), "
                "       resume_notice_pending = TRUE "
                "FROM destinations d "
                "WHERE s.destination_id = d.id AND d.owner_tg_id = $1 "
                "RETURNING s.id",
                owner, int(minutes),
            )
        return len(rows)


async def resume_all_sources(pool, owner):
    """Clear every pause for the owner. Returns the number of sources that were
    actually paused and are now resumed."""
    async with pool.acquire() as con:
        rows = await con.fetch(
            "UPDATE sources s SET paused = FALSE, paused_until = NULL, "
            "       resume_notice_pending = FALSE "
            "FROM destinations d "
            "WHERE s.destination_id = d.id AND d.owner_tg_id = $1 "
            "      AND (s.paused OR s.paused_until IS NOT NULL) "
            "RETURNING s.id",
            owner,
        )
        return len(rows)


async def pause_sources_for_dest(pool, dest_id, owner, minutes=None):
    """Pause every source feeding ONE destination (owner-checked). Returns the
    number of sources affected (0 if the destination isn't the owner's)."""
    async with pool.acquire() as con:
        if minutes is None:
            rows = await con.fetch(
                "UPDATE sources s SET paused = TRUE, paused_until = NULL, "
                "       resume_notice_pending = FALSE "
                "FROM destinations d "
                "WHERE s.destination_id = d.id AND d.id = $1 "
                "      AND d.owner_tg_id = $2 "
                "RETURNING s.id",
                dest_id, owner,
            )
        else:
            rows = await con.fetch(
                "UPDATE sources s SET paused = FALSE, "
                "       paused_until = now() + make_interval(mins => $3), "
                "       resume_notice_pending = TRUE "
                "FROM destinations d "
                "WHERE s.destination_id = d.id AND d.id = $1 "
                "      AND d.owner_tg_id = $2 "
                "RETURNING s.id",
                dest_id, owner, int(minutes),
            )
        return len(rows)


async def resume_sources_for_dest(pool, dest_id, owner):
    """Clear pauses for every source of one destination. Returns the count."""
    async with pool.acquire() as con:
        rows = await con.fetch(
            "UPDATE sources s SET paused = FALSE, paused_until = NULL, "
            "       resume_notice_pending = FALSE "
            "FROM destinations d "
            "WHERE s.destination_id = d.id AND d.id = $1 "
            "      AND d.owner_tg_id = $2 "
            "      AND (s.paused OR s.paused_until IS NOT NULL) "
            "RETURNING s.id",
            dest_id, owner,
        )
        return len(rows)


# ---------- auto-resume notices ----------
async def due_resume_notices(pool):
    """Sources whose TIMED pause just lapsed and that still owe a 'resumed'
    notice. Returns rows with the source label, owner and destination title.
    The caller sends the notice then calls clear_resume_notice."""
    async with pool.acquire() as con:
        return await con.fetch(
            "SELECT s.id AS source_id, "
            "       COALESCE(s.custom_label, s.label) AS source_label, "
            "       d.owner_tg_id AS owner_tg_id, "
            "       d.title AS dest_title, "
            "       COALESCE(us.language, 'en') AS owner_lang "
            "FROM sources s JOIN destinations d ON d.id = s.destination_id "
            "LEFT JOIN user_settings us ON us.tg_user_id = d.owner_tg_id "
            "WHERE s.resume_notice_pending = TRUE "
            "      AND s.paused = FALSE "
            "      AND (s.paused_until IS NULL OR s.paused_until <= now())",
        )


async def clear_resume_notice(pool, source_id):
    """Mark the resume notice as sent (and tidy the lapsed paused_until)."""
    async with pool.acquire() as con:
        await con.execute(
            "UPDATE sources SET resume_notice_pending = FALSE, "
            "       paused_until = NULL "
            "WHERE id = $1",
            source_id,
        )


# ---------- status overview ----------
async def status_overview(pool, owner):
    """Per-source rows for /status: destination, effective label, pause state,
    last-delivered time, and a `stalled` flag (active + not paused but nothing
    delivered in over 24h)."""
    async with pool.acquire() as con:
        return await con.fetch(
            "SELECT s.id AS source_id, s.kind, "
            "       COALESCE(s.custom_label, s.label) AS label, "
            "       d.title AS dest_title, "
            "       (s.paused OR (s.paused_until IS NOT NULL "
            "            AND s.paused_until > now())) AS is_paused, "
            "       s.last_delivered_at AS last_delivered_at, "
            "       (NOT (s.paused OR (s.paused_until IS NOT NULL "
            "            AND s.paused_until > now())) "
            "        AND (s.last_delivered_at IS NULL "
            "             OR s.last_delivered_at < now() - interval '24 hours')) "
            "            AS stalled "
            "FROM sources s JOIN destinations d ON d.id = s.destination_id "
            "WHERE d.owner_tg_id = $1 "
            "ORDER BY d.id, s.id",
            owner,
        )


async def posts_forwarded_since(pool, owner, hours=24):
    """Count published posts for this owner over the last `hours` (for
    /status)."""
    async with pool.acquire() as con:
        return int(await con.fetchval(
            "SELECT COUNT(*) FROM events WHERE owner_tg_id = $1 "
            "      AND kind = 'pub' "
            "      AND created_at >= now() - make_interval(hours => $2)",
            owner, int(hours),
        ) or 0)
