def channel_c_id(tg_chat_id) -> str:
    """Return the internal channel id used in https://t.me/c/<id>/<msg> links
    (the numeric part after the -100 prefix)."""
    s = str(tg_chat_id)
    if s.startswith("-100"):
        return s[4:]
    return s.lstrip("-")


def post_link(username, tg_chat_id, msg_id):
    """Build a public or private t.me link to a specific message.
    Public channels use the username; private channels use the c/ form
    (only openable by members of that channel)."""
    if not msg_id:
        return None
    if username:
        return f"https://t.me/{username}/{msg_id}"
    if tg_chat_id is not None:
        return f"https://t.me/c/{channel_c_id(tg_chat_id)}/{msg_id}"
    return None
