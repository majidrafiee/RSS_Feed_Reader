"""Run this LOCALLY (once) to generate a Telethon StringSession.

    pip install telethon
    python scripts/gen_session.py

You will be asked for your API ID / API HASH (from https://my.telegram.org),
your phone number, and the login code Telegram sends you. The printed
SESSION_STRING is then set as the SESSION_STRING environment variable on
Northflank. Never commit it to git.
"""
from telethon import TelegramClient
from telethon.sessions import StringSession


def main() -> None:
    api_id = int(input("API ID: ").strip())
    api_hash = input("API HASH: ").strip()
    with TelegramClient(StringSession(), api_id, api_hash) as client:
        print("\n================ SESSION_STRING ================\n")
        print(client.session.save())
        print("\n===============================================")
        print("Copy the string above into the SESSION_STRING env var.")


if __name__ == "__main__":
    main()
