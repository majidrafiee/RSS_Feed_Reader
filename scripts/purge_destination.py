"""Maintenance helper: list and delete destinations directly in the database.

Use this to remove an ORPHAN destination that no longer belongs to you (for
example a channel someone else added with an older bot/token) but that the
reader account still tries to post to — you can't delete it from the bot's
"My Setup" menu because that only lists destinations you own.

Run it against the SAME database the bot uses (set DATABASE_URL first).

  # list every destination in the database
  python scripts/purge_destination.py --list

  # delete by the numeric Telegram chat id (recommended, unambiguous)
  python scripts/purge_destination.py --chat-id -1004341905590

  # delete by the internal row id shown in --list
  python scripts/purge_destination.py --id 3

Deleting a destination cascades to its sources and seen-item history.
"""
import argparse
import asyncio
import os

import asyncpg


async def _list(con):
    rows = await con.fetch(
        "SELECT id, owner_tg_id, chat_id, title, username "
        "FROM destinations ORDER BY id"
    )
    if not rows:
        print("(no destinations in the database)")
        return
    print(f"{'id':>4}  {'owner_tg_id':>12}  {'chat_id':>16}  username / title")
    print("-" * 70)
    for r in rows:
        uname = ("@" + r["username"]) if r["username"] else ""
        print(
            f"{r['id']:>4}  {r['owner_tg_id']:>12}  {r['chat_id']:>16}  "
            f"{uname} {r['title'] or ''}".rstrip()
        )


async def _delete(con, *, dest_id=None, chat_id=None):
    if chat_id is not None:
        row = await con.fetchrow(
            "DELETE FROM destinations WHERE chat_id = $1 "
            "RETURNING id, chat_id, title",
            chat_id,
        )
    else:
        row = await con.fetchrow(
            "DELETE FROM destinations WHERE id = $1 "
            "RETURNING id, chat_id, title",
            dest_id,
        )
    if row:
        print(f"Deleted destination id={row['id']} chat_id={row['chat_id']} "
              f"title={row['title']!r} (sources + seen items cascaded).")
    else:
        print("No matching destination found — nothing deleted.")


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list all destinations")
    parser.add_argument("--id", type=int, help="delete by internal row id")
    parser.add_argument("--chat-id", type=int, help="delete by Telegram chat id")
    args = parser.parse_args()

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("Set DATABASE_URL to the bot's PostgreSQL connection string.")

    con = await asyncpg.connect(dsn)
    try:
        if args.chat_id is not None:
            await _delete(con, chat_id=args.chat_id)
        elif args.id is not None:
            await _delete(con, dest_id=args.id)
        else:
            await _list(con)
    finally:
        await con.close()


if __name__ == "__main__":
    asyncio.run(main())
