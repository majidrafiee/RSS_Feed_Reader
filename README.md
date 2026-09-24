# 📰 Telegram News Aggregator Bot

Collect posts from **Telegram channels** and **RSS feeds** into your own
channels, each nicely labelled with its source. Telegram-channel posts are
re-published with a styled source header (with a plain forward as a fallback);
RSS items are rendered as a clean container with the article link at the end.

The bot speaks **English and Persian (فارسی)**, auto-detecting your Telegram
language on first `/start` and letting you switch any time from **Settings**.

---

## Features

- **Linked source header** — each re-published post carries an emoji-marked
  source title that links straight back to the original post (public
  `t.me/name/123` or private `t.me/c/…` links).
- **Self-link footer** — every post ends with a link back to your own channel
  (added by editing the message, or as a small follow-up when it doesn't fit).
- **No cut-off posts** — long posts are split across multiple messages instead
  of being truncated with an ellipsis (RSS summaries go up to ~3500 chars).
- **Skip forwarded ads** — forwarded cross-channel posts (the usual ad spam)
  are skipped by default; toggle it in **Settings**.
- **Per-source routing** — send sport feeds to your sport channel, politics to
  your politics channel, etc.
- **Adjustable RSS interval** — 5 / 10 / 15 / 20 / 30 minutes, changed live
  from **Settings** (no redeploy).
- **Manage / delete** — **📋 My Setup** opens two submenus, **📡 List of
  Sources** and **📢 List of Destinations**, each item with a 🗑 button to
  remove stale ones (removing a channel removes its sources too). Each
  destination also has a 🧪 button to send a **test post** and confirm the
  reader account can publish there.
- **Bilingual UI** — English + Persian (RTL), with Back / Cancel on every step.

---

## How it works (architecture)

One small Python process runs three things together on one asyncio loop:

| Part | Library | Job |
|------|---------|-----|
| **Control bot** | aiogram (Bot API) | The buttons/menus you talk to: add destinations, add sources, view setup |
| **Reader account** | Telethon (MTProto "userbot") | Reads posts from source channels **and** posts everything into your destination channels |
| **RSS poller** | feedparser + APScheduler | Polls each feed on a timer and publishes new items |
| **Storage** | PostgreSQL (asyncpg) | Destinations, sources and the "already seen" de-dup list |

### Why a "reader account" (userbot) is required

The Bot API **cannot read channels the bot is not an admin of**, so a normal
bot can never follow `@bbcpersian` or `@iranint`. The standard workaround is a
**userbot**: a normal Telegram user account (yours) logged in via Telethon,
which can join and read any public channel. That same account also posts into
your destination channels, so **the reader account must be an admin of each
destination channel** (with permission to post).

> ⚠️ The reader account is a real account subject to Telegram's anti-abuse
> rules. Keep volumes reasonable. Re-publishing copyrighted news is a legal
> gray area — that's your call.

---

## What you need before starting

1. A **Telegram bot token** — create a bot with [@BotFather](https://t.me/BotFather), copy the token.
2. **API ID + API HASH** — log in at <https://my.telegram.org> → *API development tools* → create an app.
3. A **Telegram account** to act as the reader (can be your main account or a second number).
4. A **Northflank** account (free tier is fine).
5. A **GitHub** account.
6. **Python 3.11** on your local machine (only to generate the session string).

---

## Step 0 — Generate the reader session string (local, one time)

The reader account can't type a login code inside a container, so you generate
a reusable **StringSession** on your own machine first.

```bash
# in a fresh local folder
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install telethon
python scripts/gen_session.py
```

Enter your API ID, API HASH, phone number and the login code Telegram sends.
It prints a long `SESSION_STRING`. **Copy it and keep it secret** — you'll
paste it into Northflank later. Never commit it to git.

---

## Step 1 — Push the code to GitHub

You already have this project folder. From inside it:

```bash
# 1. make sure secrets are ignored (this repo already has a .gitignore)
cat .gitignore   # should list .env and *.session

# 2. initialise the repo
git init
git add .
git commit -m "Initial commit: telegram news aggregator"
git branch -M main
```

Now create an **empty** repository on GitHub:

1. Go to <https://github.com/new>.
2. Name it e.g. `telegram-news-aggregator`.
3. **Do not** add a README, .gitignore or license (you already have them).
4. Click **Create repository**.

GitHub shows a URL. Connect and push:

```bash
git remote add origin https://github.com/<your-username>/telegram-news-aggregator.git
git push -u origin main
```

> 🔒 Double-check that `.env` and any `*.session` file are **not** in the
> repo (`git status` should not list them). Never commit tokens or the
> session string.

---

## Step 2 — Create the project & database on Northflank

1. Log in to Northflank and click **Create new** → **Project**. Give it a name
   (e.g. `news-bot`), pick a region, create it.
2. Inside the project, open the **Addons** tab → **Create addon** →
   **PostgreSQL**.
   - Choose the smallest / free-tier plan.
   - Name it e.g. `news-db`, then **Create**.
3. Wait until the addon status is **Running**. Open it and go to the
   **Connection details** tab. You'll need the connection string here in
   Step 4 — Northflank exposes it as a linkable secret, usually
   `DATABASE_URL` / `POSTGRES_URI`.

---

## Step 3 — Connect GitHub to Northflank

1. In Northflank go to **Account settings** → **Git integrations** (or the
   **Connect to Git** prompt when creating a service).
2. Click **Connect** next to GitHub and authorise the Northflank GitHub App.
3. Grant access to your `telegram-news-aggregator` repository (you can limit
   it to just that repo).

---

## Step 4 — Create the bot service on Northflank

1. In your project click **Create new** → **Service** → **Combined service**
   (build **and** deploy from source).
2. **Source:** pick your GitHub account and the `telegram-news-aggregator`
   repo, branch `main`.
3. **Build:** choose **Dockerfile**, path `/Dockerfile` (the repo root). No
   build args needed.
4. **Deploy / runtime:**
   - This is a **worker** (no incoming web traffic), so you do **not** need to
     expose any port. If Northflank asks for a port, you can leave ports
     empty / disabled — the process only makes outbound connections.
   - Pick the smallest instance (free-tier `nf-compute-10` style plan is
     enough).
5. **Environment variables** — open the **Environment** section and add:

   | Key | Value |
   |-----|-------|
   | `BOT_TOKEN` | your @BotFather token |
   | `API_ID` | from my.telegram.org |
   | `API_HASH` | from my.telegram.org |
   | `SESSION_STRING` | the string from Step 0 |
   | `RSS_POLL_SECONDS` | `300` (optional) |
   | `DATABASE_URL` | the Postgres connection string |

   For `DATABASE_URL`, prefer **linking the addon**: click *Add from addon* /
   *Link addon* and select `news-db`. Northflank injects the credentials as a
   secret. If the injected variable has a different name (e.g. `POSTGRES_URI`),
   either rename the link to `DATABASE_URL` or add `DATABASE_URL` referencing
   that secret. The connection string must start with `postgresql://`.

6. Click **Create service**. Northflank pulls the repo, builds the Docker
   image and starts the container.

---

## Step 5 — Verify it's running

Open the service **Logs** tab. You should see:

```
Database ready.
Userbot logged in as @yourreaderaccount (id=...)
Starting bot + userbot + RSS poller…
```

If you see a missing-env-var error, fix the variable and redeploy.

---

## Step 6 — Use the bot

1. Open your bot in Telegram and send **/start**.
2. **Create / pick a destination channel** (e.g. "Channel A"). Add the
   **reader account** as an **admin** of that channel with post rights.
3. Tap **➕ Add Destination** and **forward any message** from that
   channel to the bot. It's now saved.
4. Tap **📡 Add Source**, pick the destination, then send either:
   - a Telegram channel: `@bbcpersian` or `https://t.me/bbcpersian`
   - an RSS URL: `https://feeds.bbci.co.uk/persian/rss.xml`
5. Repeat to route sport feeds to "Channel B", etc. Use **📋 My Setup** to
   review everything.

New Telegram-channel posts appear almost instantly; RSS items appear on the
next poll (default every 5 minutes). Existing RSS items are marked as seen
when you add a feed, so your channel isn't flooded with the backlog.

---

## Redeploying after code changes

Just push to `main`:

```bash
git add .
git commit -m "your change"
git push
```

Enable **Continuous deployment** on the service (Settings → CI) so Northflank
rebuilds automatically on every push. Otherwise click **Deploy** manually.

---

## Troubleshooting

- **`Missing required environment variable`** → a var isn't set; check the
  Environment tab.
- **Userbot won't log in / `SESSION_STRING` invalid** → regenerate it with
  `scripts/gen_session.py` using the **same** API_ID/API_HASH and update the
  env var.
- **"Could not add channel"** → the channel must be public (or the reader
  account must already be a member). Private channels need the reader account
  invited first.
- **RSS items don't post** → confirm the reader account is an **admin with
  post rights** in the destination, and that the feed URL is valid.
- **Old channels/sources reappear after changing the bot token** → your
  destinations and sources live in the **PostgreSQL database**, not in the bot
  token. Changing `BOT_TOKEN`/bot id does **not** clear them — as long as the
  same `DATABASE_URL` and reader account are used, old rows persist. Open
  **📋 My Setup** and tap 🗑 next to a stale channel/source to remove it (or
  drop the tables to wipe everything).
  actually joined it (adding it as a source triggers a join). Check logs.
- **A channel keeps getting posts / errors in the log but is NOT in your
  📋 My Setup list** → that destination was added by **another user** (or an
  older bot) but lives in the **same database**, so the reader account still
  tries to post to it. "My Setup" only lists destinations **you** own, so you
  can't delete it from the bot. The reader now silences a known-unreachable
  channel for ~10 min (you'll see `not reachable (cached)` instead of
  flood-waits), but to remove it for good, run the maintenance script against
  the **same** database (set `DATABASE_URL` first):

  ```bash
  # see every destination in the DB (with owner + chat id)
  python scripts/purge_destination.py --list
  # delete the orphan by its Telegram chat id
  python scripts/purge_destination.py --chat-id -1004341905590
  ```

  On Northflank you can run this from the service **Shell/Exec** tab (the
  `DATABASE_URL` env var is already set there).
- **"Destination … not reachable / could not find input entity"** → the
  reader account is **not an admin of that destination channel**. Forwarding a
  message only tells the *bot* which channel you mean; it does **not** give the
  reader access. Open the destination channel → *Administrators* → *Add admin*,
  add the reader account with **Post messages** rights. The bot now checks this
  when you add a destination and warns you if the reader can't post yet — no
  need to re-add the destination, just fix the admin rights and it starts
  mirroring on the next post.
- **Posts not mirrored from a TG channel** → the reader account must have
- **Free-tier limits** → this design uses **one service + one Postgres addon**
  on purpose, to fit comfortably in the free tier.

---

## Notes & limits (Telegram)

- Text message limit 4096 chars; media caption limit 1024 chars — the code
  **splits** long posts across messages instead of truncating them.

### About "balancing" sources (why TG is instant but RSS is on a timer)

Telegram-channel posts arrive **in real time** via an event stream (the
reader account is notified the moment a source posts), so there's nothing to
"schedule" — they're mirrored immediately. RSS feeds have no push mechanism,
so they're **polled** on the interval you pick in Settings. This is why TG
sources feel instant and RSS lags by up to one interval. Forcing everything
through a single round-robin queue would only make TG posts *slower* with no
benefit, so the design intentionally keeps TG real-time and just throttles the
RSS polling. If a very busy channel floods your destination, lower its noise
by enabling *Skip forwarded ads* rather than delaying delivery.
- Channels with "restrict saving content" enabled can't be styled-copied;
  the code falls back to a plain forward.
- The Bot API alone cannot read third-party channels — that's exactly why the
  Telethon reader account exists.
