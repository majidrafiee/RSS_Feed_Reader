from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.i18n import t

INTERVALS = [5, 10, 15, 20, 30]


def main_menu(lang: str = "en", alive: bool = True) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=t(lang, "btn_add_dest"), callback_data="add_dest")],
        [InlineKeyboardButton(text=t(lang, "btn_add_source"), callback_data="add_source")],
        [InlineKeyboardButton(text=t(lang, "btn_my_setup"), callback_data="my_setup")],
        [InlineKeyboardButton(text=t(lang, "btn_settings"), callback_data="settings")],
    ]
    # Always show Status button; when userbot is dead, also show a red alert.
    rows.append(
        [
            InlineKeyboardButton(text=t(lang, "btn_status"), callback_data="status"),
            InlineKeyboardButton(text=t(lang, "btn_stats"), callback_data="stats"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


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
        paused = False
        try:
            paused = bool(s["is_paused"])
        except (KeyError, IndexError, TypeError):
            paused = False
        # A paused source gets a clear ⏸ marker so the list shows state.
        icon = "\u23F8\uFE0F" if paused else "\u2699\uFE0F"
        text = f"{icon} {label}"
        if dtitle:
            text += f" \u2192 {dtitle}"
        rows.append([InlineKeyboardButton(
            text=text, callback_data=f"src_edit:{s['id']}",
        )])
    # Bulk controls: pause / resume every source at once. Kept on this same
    # list message so the owner never has to scroll to find them.
    if sources:
        rows.append([
            InlineKeyboardButton(
                text=t(lang, "btn_pause_all"), callback_data="pause_all"),
            InlineKeyboardButton(
                text=t(lang, "btn_resume_all"), callback_data="resume_all"),
        ])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="my_setup")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def bulk_pause_kb(target: str, lang: str = "en") -> InlineKeyboardMarkup:
    """Duration picker for a BULK pause. `target` is either "all" (every
    source) or "dest:<id>" (one channel). Buttons stay on the current message.
    """
    rows = [[InlineKeyboardButton(
        text=t(lang, "btn_src_pause_inf"),
        callback_data=f"bpause_inf:{target}")]]
    btns = [InlineKeyboardButton(
        text=t(lang, "btn_src_pause_min", mins=m),
        callback_data=f"bpause_min:{target}:{m}") for m in PAUSE_MINUTES]
    rows += [btns[i:i + 2] for i in range(0, len(btns), 2)]
    rows.append([InlineKeyboardButton(
        text=t(lang, "btn_src_pause_custom"),
        callback_data=f"bpause_custom:{target}")])
    back = "list_src" if target == "all" else "list_dest"
    rows.append([InlineKeyboardButton(
        text=t(lang, "btn_back"), callback_data=back)])
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
    # Pause / resume: a paused source shows Resume; an active one shows Pause
    # (which opens the duration sub-menu).
    try:
        is_paused = bool(src["is_paused"])
    except (KeyError, IndexError, TypeError):
        is_paused = False
    if is_paused:
        rows.append([InlineKeyboardButton(
            text=t(lang, "btn_src_resume"), callback_data=f"src_resume:{sid}")])
    else:
        rows.append([InlineKeyboardButton(
            text=t(lang, "btn_src_pause"), callback_data=f"src_pause:{sid}")])
    rows.append([InlineKeyboardButton(
        text=t(lang, "btn_delete"), callback_data=f"del_src:{sid}")])
    rows.append([InlineKeyboardButton(
        text=t(lang, "btn_back"), callback_data="list_src")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Pause-duration options (minutes) offered when pausing a source.
PAUSE_MINUTES = [30, 60, 180, 360, 720, 1440]


def source_pause_kb(src_id, lang: str = "en") -> InlineKeyboardMarkup:
    """Choose how long to pause a source: indefinitely, a preset number of
    minutes (two per row), or a custom amount typed by the owner."""
    rows = [[InlineKeyboardButton(
        text=t(lang, "btn_src_pause_inf"),
        callback_data=f"src_pause_inf:{src_id}")]]
    btns = [InlineKeyboardButton(
        text=t(lang, "btn_src_pause_min", mins=m),
        callback_data=f"src_pause_min:{src_id}:{m}") for m in PAUSE_MINUTES]
    rows += [btns[i:i + 2] for i in range(0, len(btns), 2)]
    rows.append([InlineKeyboardButton(
        text=t(lang, "btn_src_pause_custom"),
        callback_data=f"src_pause_custom:{src_id}")])
    rows.append([InlineKeyboardButton(
        text=t(lang, "btn_back"), callback_data=f"src_edit:{src_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dests_manage_kb(dests, lang: str = "en") -> InlineKeyboardMarkup:
    """One test + pause/resume + delete button per destination."""
    rows = []
    for d in dests:
        title = d["title"] or str(d["chat_id"])
        rows.append([
            InlineKeyboardButton(
                text=f"\U0001F9EA {title}", callback_data=f"test_dest:{d['id']}"),
            InlineKeyboardButton(
                text=t(lang, "btn_dest_pause"), callback_data=f"destpause:{d['id']}"),
            InlineKeyboardButton(
                text=t(lang, "btn_dest_resume"), callback_data=f"destresume:{d['id']}"),
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
            [InlineKeyboardButton(text=t(lang, "btn_ad_filter"), callback_data="ad_filter")],
            [InlineKeyboardButton(text=t(lang, "btn_dedup"), callback_data="dedup")],
            [InlineKeyboardButton(text=t(lang, "btn_language"), callback_data="set_lang")],
            [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="home")],
        ]
    )


def ad_filter_kb(settings, filters, lang: str = "en") -> InlineKeyboardMarkup:
    """Ad-filter MAIN menu: just the on/off toggle, a button that opens the
    block-words sub-menu (with a live count), the confirm-gated 'clean existing
    ads' action, and back. The actual word list lives in its own sub-menu so
    this screen stays short and tidy."""
    try:
        enabled = bool(settings["ad_filter_enabled"])
    except (KeyError, IndexError):
        enabled = False
    toggle_key = "btn_ad_on" if enabled else "btn_ad_off"
    count = len(filters)
    rows = [
        [InlineKeyboardButton(text=t(lang, toggle_key), callback_data="ad_toggle")],
        [InlineKeyboardButton(
            text=t(lang, "btn_ad_words", n=count), callback_data="ad_words")],
        [InlineKeyboardButton(text=t(lang, "btn_ad_clean"), callback_data="ad_clean")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="settings")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def ad_words_kb(filters, lang: str = "en") -> InlineKeyboardMarkup:
    """Block-words SUB-menu: an Add button on top, then one tappable
    (delete) button per stored word / @handle / #hashtag, then back to the
    ad-filter main menu."""
    rows = [[InlineKeyboardButton(text=t(lang, "btn_ad_add"), callback_data="ad_add")]]
    for f in filters:
        rows.append([InlineKeyboardButton(
            text=t(lang, "btn_ad_item", pattern=f["pattern"]),
            callback_data=f"ad_del:{f['id']}",
        )])
    rows.append([InlineKeyboardButton(
        text=t(lang, "btn_back"), callback_data="ad_filter")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def ad_clean_confirm_kb(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=t(lang, "btn_ad_clean_yes"), callback_data="ad_clean_yes")],
            [InlineKeyboardButton(
                text=t(lang, "btn_ad_clean_no"), callback_data="ad_filter")],
        ]
    )


DEDUP_WINDOWS = [15, 30, 60, 180, 360]
DEDUP_THRESHOLDS = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
DEDUP_MIN_LENS = [10, 20, 40, 80]


def _dedup_flag(settings, name, default):
    try:
        val = settings[name]
    except (KeyError, IndexError):
        return default
    return default if val is None else val


def dedup_kb(settings, lang: str = "en") -> InlineKeyboardMarkup:
    """Duplicate-filter menu: on/off toggle plus the three tunable knobs
    (lookback window, similarity threshold, minimum length)."""
    enabled = bool(_dedup_flag(settings, "dedup_enabled", False))
    window = _dedup_flag(settings, "dedup_window_min", 30)
    threshold = _dedup_flag(settings, "dedup_threshold", 90)
    min_len = _dedup_flag(settings, "dedup_min_len", 20)
    toggle_key = "btn_dedup_on" if enabled else "btn_dedup_off"
    rows = [
        [InlineKeyboardButton(text=t(lang, toggle_key), callback_data="dedup_toggle")],
        [InlineKeyboardButton(
            text=t(lang, "btn_dedup_window", min=window),
            callback_data="dedup_set_window")],
        [InlineKeyboardButton(
            text=t(lang, "btn_dedup_threshold", pct=threshold),
            callback_data="dedup_set_threshold")],
        [InlineKeyboardButton(
            text=t(lang, "btn_dedup_minlen", n=min_len),
            callback_data="dedup_set_minlen")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="settings")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dedup_window_kb(lang: str = "en") -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(
        text=t(lang, "btn_dedup_window_opt", min=m),
        callback_data=f"dedup_window:{m}")] for m in DEDUP_WINDOWS]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="dedup")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dedup_threshold_kb(lang: str = "en") -> InlineKeyboardMarkup:
    # Lay the options out two-per-row so a long list (50%..95%) stays compact.
    buttons = [InlineKeyboardButton(
        text=t(lang, "btn_dedup_threshold_opt", pct=p),
        callback_data=f"dedup_threshold:{p}") for p in DEDUP_THRESHOLDS]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="dedup")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dedup_minlen_kb(lang: str = "en") -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(
        text=t(lang, "btn_dedup_minlen_opt", n=n),
        callback_data=f"dedup_minlen:{n}")] for n in DEDUP_MIN_LENS]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="dedup")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


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
