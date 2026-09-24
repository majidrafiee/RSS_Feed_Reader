from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.i18n import t

INTERVALS = [5, 10, 15, 20, 30]


def main_menu(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_add_dest"), callback_data="add_dest")],
            [InlineKeyboardButton(text=t(lang, "btn_add_source"), callback_data="add_source")],
            [InlineKeyboardButton(text=t(lang, "btn_my_setup"), callback_data="my_setup")],
            [InlineKeyboardButton(text=t(lang, "btn_settings"), callback_data="settings")],
        ]
    )


def nav_kb(lang: str = "en", back_to: str = "home") -> InlineKeyboardMarkup:
    """Back + Cancel row shown under every prompt."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "btn_back"), callback_data=back_to),
                InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="cancel"),
            ]
        ]
    )


def destinations_kb(dests, action: str, lang: str = "en") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=(d["title"] or str(d["chat_id"])),
            callback_data=f"{action}:{d['id']}",
        )]
        for d in dests
    ]
    rows.append([
        InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="home"),
        InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="cancel"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def setup_kb(items, lang: str = "en") -> InlineKeyboardMarkup:
    """Top-level My Setup menu: choose to manage sources or destinations."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_list_sources"), callback_data="list_src")],
            [InlineKeyboardButton(text=t(lang, "btn_list_dests"), callback_data="list_dest")],
            [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="home")],
        ]
    )


def sources_manage_kb(sources, lang: str = "en") -> InlineKeyboardMarkup:
    """sources: list of rows with id/label/dest_title. Tapping a source opens
    its edit menu (rename, toggle title visibility / hyperlink, delete)."""
    rows = []
    for s in sources:
        label = s["label"]
        dtitle = s.get("dest_title")
        text = f"\u2699\uFE0F {label}"
        if dtitle:
            text += f" \u2192 {dtitle}"
        rows.append([InlineKeyboardButton(
            text=text, callback_data=f"src_edit:{s['id']}",
        )])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="my_setup")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def source_edit_kb(src, lang: str = "en") -> InlineKeyboardMarkup:
    """Per-source edit menu: toggle source-title visibility, toggle its
    hyperlink, rename it, reset the name to the auto default, or delete it.
    `src` is a row from db.get_source_detail."""
    sid = src["id"]
    show_title = bool(src["show_title"])
    link_title = bool(src["link_title"])
    show_key = "btn_src_showtitle_on" if show_title else "btn_src_showtitle_off"
    link_key = "btn_src_linktitle_on" if link_title else "btn_src_linktitle_off"
    rows = [
        [InlineKeyboardButton(
            text=t(lang, show_key), callback_data=f"src_show:{sid}")],
        [InlineKeyboardButton(
            text=t(lang, link_key), callback_data=f"src_link:{sid}")],
        [InlineKeyboardButton(
            text=t(lang, "btn_src_rename"), callback_data=f"src_rename:{sid}")],
    ]
    # Offer "reset name" only when a custom name is actually set.
    if src["has_custom_label"]:
        rows.append([InlineKeyboardButton(
            text=t(lang, "btn_src_resetname"), callback_data=f"src_reset:{sid}")])
    rows.append([InlineKeyboardButton(
        text=t(lang, "btn_delete"), callback_data=f"del_src:{sid}")])
    rows.append([InlineKeyboardButton(
        text=t(lang, "btn_back"), callback_data="list_src")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dests_manage_kb(dests, lang: str = "en") -> InlineKeyboardMarkup:
    """One test + delete button per destination."""
    rows = []
    for d in dests:
        title = d["title"] or str(d["chat_id"])
        rows.append([
            InlineKeyboardButton(
                text=f"\U0001F9EA {title}", callback_data=f"test_dest:{d['id']}"),
            InlineKeyboardButton(
                text=t(lang, "btn_delete"), callback_data=f"del_dest:{d['id']}"),
        ])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="my_setup")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def test_dest_kb(dest_id, lang: str = "en") -> InlineKeyboardMarkup:
    """Shown right after a destination is added: verify with a test post."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=t(lang, "btn_send_test"), callback_data=f"test_dest:{dest_id}")],
            [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="home")],
        ]
    )


def settings_kb(settings, lang: str = "en") -> InlineKeyboardMarkup:
    skip = settings["skip_forwarded"]
    skip_key = "btn_skipfwd_on" if skip else "btn_skipfwd_off"
    # New per-user display toggles (default TRUE when the row predates them).
    def _flag(name):
        try:
            val = settings[name]
        except (KeyError, IndexError):
            return True
        return True if val is None else val
    show_title = _flag("show_title")
    link_title = _flag("link_title")
    dest_user = _flag("dest_show_username")
    show_key = "btn_showtitle_on" if show_title else "btn_showtitle_off"
    link_key = "btn_linktitle_on" if link_title else "btn_linktitle_off"
    du_key = "btn_destuser_on" if dest_user else "btn_destuser_off"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=t(lang, "btn_interval", min=settings["check_interval"]),
                callback_data="set_interval",
            )],
            [InlineKeyboardButton(text=t(lang, skip_key), callback_data="toggle_fwd")],
            [InlineKeyboardButton(text=t(lang, show_key), callback_data="toggle_show_title")],
            [InlineKeyboardButton(text=t(lang, link_key), callback_data="toggle_link_title")],
            [InlineKeyboardButton(text=t(lang, du_key), callback_data="toggle_dest_user")],
            [InlineKeyboardButton(text=t(lang, "btn_language"), callback_data="set_lang")],
            [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="home")],
        ]
    )


def interval_kb(lang: str = "en") -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=f"{m} min", callback_data=f"interval:{m}")]
            for m in INTERVALS]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def language_kb(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="English \U0001F1EC\U0001F1E7", callback_data="lang:en"),
                InlineKeyboardButton(text="\u0641\u0627\u0631\u0633\u06CC \U0001F1EE\U0001F1F7", callback_data="lang:fa"),
            ],
            [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="settings")],
        ]
    )
