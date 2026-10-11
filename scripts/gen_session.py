"""Run this LOCALLY (once) to generate a Telethon StringSession.

    pip install telethon
    python scripts/gen_session.py

You will be asked for your API ID / API HASH (from https://my.telegram.org),
your phone number, and the login code Telegram sends you. The printed
SESSION_STRING is then set as the SESSION_STRING environment variable on
your hosting platform. Never commit it to git.

--------------------------------------------------------------------------
CONNECTING FROM A FILTERED NETWORK (TimeoutError / "Connection to Telegram
failed")
--------------------------------------------------------------------------
If you get repeated "Attempt N at connecting failed: TimeoutError", your PC
cannot reach Telegram directly. Either:

  (a) Turn on a system-wide VPN and just run the script again, OR
  (b) Point the script at a local proxy using environment variables:

      SOCKS5 proxy (e.g. a VPN client exposing 127.0.0.1:1080):
          # PowerShell
          $env:TG_PROXY_TYPE="socks5"
          $env:TG_PROXY_HOST="127.0.0.1"
          $env:TG_PROXY_PORT="1080"
          python scripts/gen_session.py

      MTProto proxy (host, port, secret):
          $env:TG_PROXY_TYPE="mtproto"
          $env:TG_PROXY_HOST="1.2.3.4"
          $env:TG_PROXY_PORT="443"
          $env:TG_PROXY_SECRET="ee..."   # the proxy secret
          python scripts/gen_session.py

  SOCKS5/HTTP proxies need the python-socks package:
          pip install "python-socks[asyncio]"
"""
import os

from telethon import TelegramClient
from telethon.sessions import StringSession


def _build_proxy():
    """Read optional proxy settings from env vars. Returns a value suitable for
    TelegramClient(proxy=...), or None when no proxy is configured."""
    ptype = (os.environ.get("TG_PROXY_TYPE") or "").strip().lower()
    if not ptype:
        return None
    host = (os.environ.get("TG_PROXY_HOST") or "").strip()
    port = int(os.environ.get("TG_PROXY_PORT", "0") or "0")
    if not host or not port:
        print("TG_PROXY_TYPE set but TG_PROXY_HOST/TG_PROXY_PORT missing; "
              "ignoring proxy.")
        return None

    if ptype == "mtproto":
        secret = (os.environ.get("TG_PROXY_SECRET") or "").strip()
        # Telethon accepts an MTProxy as a (host, port, secret) tuple.
        print(f"Using MTProto proxy {host}:{port}")
        return (host, port, secret)

    # SOCKS5 / SOCKS4 / HTTP need python-socks.
    try:
        import python_socks  # noqa: F401
    except ImportError:
        print('This proxy type needs: pip install "python-socks[asyncio]"')
        raise SystemExit(1)

    from python_socks import ProxyType
    mapping = {
        "socks5": ProxyType.SOCKS5,
        "socks4": ProxyType.SOCKS4,
        "http": ProxyType.HTTP,
    }
    if ptype not in mapping:
        print(f"Unknown TG_PROXY_TYPE={ptype!r}; use socks5/socks4/http/mtproto.")
        raise SystemExit(1)
    user = os.environ.get("TG_PROXY_USER") or None
    pwd = os.environ.get("TG_PROXY_PASS") or None
    print(f"Using {ptype} proxy {host}:{port}")
    return {
        "proxy_type": mapping[ptype],
        "addr": host,
        "port": port,
        "username": user,
        "password": pwd,
        "rdns": True,
    }


def main() -> None:
    api_id = int(input("API ID: ").strip())
    api_hash = input("API HASH: ").strip()
    proxy = _build_proxy()
    client = TelegramClient(
        StringSession(), api_id, api_hash,
        proxy=proxy,
        # Give slow/filtered links more room before giving up.
        timeout=30,
        connection_retries=5,
    )
    with client:
        print("\n================ SESSION_STRING ================\n")
        print(client.session.save())
        print("\n===============================================")
        print("Copy the string above into the SESSION_STRING env var.")


if __name__ == "__main__":
    main()
