import logging
from urllib.parse import urlparse

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, ErrorEvent, Message
from telethon import utils
from telethon.tl.functions.channels import JoinChannelRequest

from app import db, scheduling
from app.formatting import esc
from app.i18n import t
from app.keyboards import (
    destinations_kb,
    dests_manage_kb,
    interval_kb,
    language_kb,
    main_menu,
    nav_kb,
    settings_kb,
    setup_kb,
    source_edit_kb,
    sources_manage_kb,
    test_dest_kb,
)
from app.publisher import refresh_destinations, resolve_dest, send_test_post
from app.rss import seed_source, validate_feed

log = logging.getLogger("bot")
router = Router()


@router.errors()
async def on_error(event: ErrorEvent):
    """Swallow transient network errors (VPN drops / "Connection reset by
    peer") so they don't crash update handling with a full traceback. The
    update is simply retried on the next poll."""
    exc = event.exception
    if isinstance(exc, TelegramNetworkError):
        log.warning("transient network error (ignored): %s", exc)
        return True
    log.exception("unhandled error while processing update: %s", exc)
    return True


async def _safe_edit(cb: CallbackQuery, text: str, reply_markup=None):
    """Edit a message, ignoring Telegram's harmless "message is not modified"
    error (raised when the new content equals the current content)."""
    try:
        await cb.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc):
            raise


class AddDest(StatesGroup):
    waiting_forward = State()


class AddSource(StatesGroup):
    waiting_input = State()


class EditSourceName(StatesGroup):
    waiting_name = State()


async def _lang(pool, tg_id, fallback="en"):
    row = await db.get_settings(pool, tg_id, fallback)
    return row["language"]


def _detect_lang(message: Message) -> str:
    code = (message.from_user.language_code or "").lower()
    return "fa" if code.startswith("fa") else "en"


def _forward_chat(message: Message):
    origin = getattr(message, "forward_origin", None)
    if origin is not None:
        chat = getattr(origin, "chat", None)
        if chat is not None:
            return chat
    return getattr(message, "forward_from_chat", None)


def _normalize_username(text: str) -> str:
    text = text.strip()
    for prefix in ("https://t.me/", "http://t.me/", "t.me/"):
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    text = text.strip("/")
    if not text.startswith("@"):
        text = "@" + text
    return text


def _rss_label(url: str) -> str:
    host = urlparse(url).netloc.replace("www.", "")
    return host or url


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, pool, reader: str):
    await state.clear()
    row = await db.get_settings(pool, message.from_user.id, _detect_lang(message))
    lang = row["language"]
    await message.answer(
        t(lang, "welcome", reader=reader), reply_markup=main_menu(lang)
    )


@router.callback_query(F.data == "home")
async def cb_home(cb: CallbackQuery, state: FSMContext, pool, reader: str):
    await state.clear()
    lang = await _lang(pool, cb.from_user.id)
    await _safe_edit(cb, t(lang, "welcome", reader=reader), reply_markup=main_menu(lang))
    await cb.answer()


@router.callback_query(F.data == "cancel")
async def cb_cancel(cb: CallbackQuery, state: FSMContext, pool, reader: str):
    await state.clear()
    lang = await _lang(pool, cb.from_user.id)
    await _safe_edit(cb, t(lang, "welcome", reader=reader), reply_markup=main_menu(lang))
    await cb.answer(t(lang, "cancelled"))


@router.callback_query(F.data == "add_dest")
async def cb_add_dest(cb: CallbackQuery, state: FSMContext, pool, reader: str):
    lang = await _lang(pool, cb.from_user.id)
    await state.set_state(AddDest.waiting_forward)
    await _safe_edit(cb, t(lang, "add_dest_prompt", reader=reader), reply_markup=nav_kb(lang))
    await cb.answer()


@router.message(AddDest.waiting_forward)
async def on_dest_forwarded(message: Message, state: FSMContext, pool, client, reader: str):
    lang = await _lang(pool, message.from_user.id)
    chat = _forward_chat(message)
    if not chat or chat.type != ChatType.CHANNEL:
        await message.answer(t(lang, "forward_a_channel"), reply_markup=nav_kb(lang))
        return
    await db.add_destination(
        pool, message.from_user.id, chat.id, chat.title,
        getattr(chat, "username", None),
    )
    await state.clear()
    dest_row = await _find_dest_by_chat(pool, message.from_user.id, chat.id)
    dest_id = dest_row["id"] if dest_row else None
    # Offer a one-tap test post so the user can immediately verify the reader
    # account can actually publish there (forwarding only tells the *bot*
    # about the channel; the reader userbot must be an admin to post).
    if dest_id is not None:
        await message.answer(
            t(lang, "test_added", title=chat.title),
            reply_markup=test_dest_kb(dest_id, lang),
        )
    else:
        await message.answer(
            t(lang, "dest_saved", title=chat.title), reply_markup=main_menu(lang)
        )


async def _find_dest_by_chat(pool, owner, chat_id):
    for d in await db.list_destinations(pool, owner):
        if d["chat_id"] == chat_id:
            return d
    return None


@router.callback_query(F.data == "add_source")
async def cb_add_source(cb: CallbackQuery, pool):
    lang = await _lang(pool, cb.from_user.id)
    dests = await db.list_destinations(pool, cb.from_user.id)
    if not dests:
        await cb.answer(t(lang, "need_dest_first"), show_alert=True)
        return
    await _safe_edit(cb, t(lang, "choose_dest"), reply_markup=destinations_kb(dests, "src", lang))
    await cb.answer()


@router.callback_query(F.data.startswith("src:"))
async def cb_src_dest_chosen(cb: CallbackQuery, state: FSMContext, pool):
    lang = await _lang(pool, cb.from_user.id)
    dest_id = int(cb.data.split(":", 1)[1])
    dest = await db.get_destination(pool, dest_id, cb.from_user.id)
    if not dest:
        await cb.answer("not found", show_alert=True)
        return
    await state.set_state(AddSource.waiting_input)
    await state.update_data(dest_id=dest_id)
    await _safe_edit(cb, t(lang, "source_prompt", title=dest["title"]), reply_markup=nav_kb(lang))
    await cb.answer()


@router.message(AddSource.waiting_input)
async def on_source_input(message: Message, state: FSMContext, pool, client):
    lang = await _lang(pool, message.from_user.id)
    data = await state.get_data()
    dest_id = data.get("dest_id")
    if dest_id is None:
        await state.clear()
        await message.answer(t(lang, "cancelled"), reply_markup=main_menu(lang))
        return

    text = (message.text or "").strip()
    is_rss = text.startswith("http") and "t.me/" not in text

    if is_rss:
        # Validate the feed before saving so we never add a source that can't
        # post (e.g. a feed-directory web page instead of a real feed).
        ok, detail, feed_title = await validate_feed(text)
        if not ok:
            await message.answer(
                t(lang, "rss_invalid", detail=detail), reply_markup=nav_kb(lang)
            )
            return
        label = feed_title or _rss_label(text)
        src = await db.add_source(pool, dest_id, "rss", text, None, None, label)
        await seed_source(pool, src["id"], text)
        await state.clear()
        await message.answer(
            t(lang, "source_added_rss", label=label), reply_markup=main_menu(lang)
        )
        return

    username = _normalize_username(text)
    try:
        entity = await client.get_entity(username)
        # Surface join errors instead of swallowing them: on a fresh account
        # a silent join failure is the usual reason posts never arrive.
        try:
            await client(JoinChannelRequest(entity))
        except Exception as exc:  # noqa: BLE001
            log.warning("join %s failed: %s", username, exc)
        tg_id = utils.get_peer_id(entity)
        uname = getattr(entity, "username", None)
        label = getattr(entity, "title", None) or username
        await db.add_source(pool, dest_id, "tg", username, tg_id, uname, label)
        await state.clear()
        await message.answer(
            t(lang, "source_added_tg", label=label), reply_markup=main_menu(lang)
        )
    except Exception as exc:  # noqa: BLE001
        await message.answer(
            t(lang, "source_error", name=username, err=str(exc)),
            reply_markup=nav_kb(lang),
        )


@router.callback_query(F.data == "my_setup")
async def cb_my_setup(cb: CallbackQuery, pool):
    lang = await _lang(pool, cb.from_user.id)
    await _safe_edit(cb, t(lang, "setup_menu"), reply_markup=setup_kb(None, lang))
    await cb.answer()


@router.callback_query(F.data == "list_src")
async def cb_list_src(cb: CallbackQuery, pool):
    lang = await _lang(pool, cb.from_user.id)
    await _show_sources(cb, pool, lang)
    await cb.answer()


@router.callback_query(F.data == "list_dest")
async def cb_list_dest(cb: CallbackQuery, pool):
    lang = await _lang(pool, cb.from_user.id)
    await _show_dests(cb, pool, lang)
    await cb.answer()


async def _show_sources(cb: CallbackQuery, pool, lang):
    sources = await db.list_sources_for_owner(pool, cb.from_user.id)
    if not sources:
        await _safe_edit(cb, t(lang, "no_sources_yet"), reply_markup=setup_kb(None, lang))
        return
    await _safe_edit(cb, t(lang, "sources_title"),
                     reply_markup=sources_manage_kb(sources, lang))


async def _show_dests(cb: CallbackQuery, pool, lang):
    dests = await db.list_destinations(pool, cb.from_user.id)
    if not dests:
        await _safe_edit(cb, t(lang, "no_dests_yet"), reply_markup=setup_kb(None, lang))
        return
    await _safe_edit(cb, t(lang, "dests_title"),
                     reply_markup=dests_manage_kb(dests, lang))


@router.callback_query(F.data.startswith("del_dest:"))
async def cb_del_dest(cb: CallbackQuery, pool):
    lang = await _lang(pool, cb.from_user.id)
    dest_id = int(cb.data.split(":", 1)[1])
    row = await db.delete_destination(pool, dest_id, cb.from_user.id)
    await cb.answer(
        t(lang, "dest_deleted", title=(row["title"] if row else "")),
        show_alert=False,
    )
    await _show_dests(cb, pool, lang)


@router.callback_query(F.data.startswith("del_src:"))
async def cb_del_src(cb: CallbackQuery, pool):
    lang = await _lang(pool, cb.from_user.id)
    src_id = int(cb.data.split(":", 1)[1])
    row = await db.delete_source(pool, src_id, cb.from_user.id)
    await cb.answer(
        t(lang, "source_deleted", label=(row["label"] if row else "")),
        show_alert=False,
    )
    await _show_sources(cb, pool, lang)


# ---------- per-source edit menu ----------
def _source_handle(src):
    """Human-readable @username / URL for a source, shown in the edit menu so
    the user can tell channels with similar names apart. Telegram sources show
    @username (falling back to the stored identifier like '@name'); RSS
    sources show their feed URL."""
    kind = src["kind"]
    if kind == "tg":
        username = src["username"]
        if username:
            return "@" + username
        ident = src["identifier"] or ""
        # Stored identifiers are already '@name' or a t.me link; show as-is.
        return ident or "—"
    # RSS: show the feed URL (identifier), trimmed so the menu stays tidy.
    ident = src["identifier"] or "—"
    return ident if len(ident) <= 60 else ident[:57] + "…"


def _source_edit_text(src, lang):
    """Render the edit-menu body for one source (name, handle/@username,
    destination, and the current ON/OFF state of each display option)."""
    on = t(lang, "on")
    off = t(lang, "off")
    return t(
        lang, "source_edit_title",
        name=esc(src["effective_label"] or ""),
        handle=esc(_source_handle(src)),
        dest=esc(src["dest_title"] or ""),
        show=on if src["show_title"] else off,
        link=on if src["link_title"] else off,
    )


async def _show_source_edit(cb: CallbackQuery, pool, lang, src_id):
    src = await db.get_source_detail(pool, src_id, cb.from_user.id)
    if not src:
        await cb.answer(t(lang, "cancelled"), show_alert=False)
        await _show_sources(cb, pool, lang)
        return
    await _safe_edit(
        cb, _source_edit_text(src, lang), reply_markup=source_edit_kb(src, lang)
    )


@router.callback_query(F.data.startswith("src_edit:"))
async def cb_src_edit(cb: CallbackQuery, state: FSMContext, pool):
    await state.clear()
    lang = await _lang(pool, cb.from_user.id)
    src_id = int(cb.data.split(":", 1)[1])
    await _show_source_edit(cb, pool, lang, src_id)
    await cb.answer()


@router.callback_query(F.data.startswith("src_show:"))
async def cb_src_toggle_show(cb: CallbackQuery, pool):
    lang = await _lang(pool, cb.from_user.id)
    src_id = int(cb.data.split(":", 1)[1])
    await db.toggle_source_flag(pool, src_id, cb.from_user.id, "show_title")
    await _show_source_edit(cb, pool, lang, src_id)
    await cb.answer(t(lang, "saved"))


@router.callback_query(F.data.startswith("src_link:"))
async def cb_src_toggle_link(cb: CallbackQuery, pool):
    lang = await _lang(pool, cb.from_user.id)
    src_id = int(cb.data.split(":", 1)[1])
    await db.toggle_source_flag(pool, src_id, cb.from_user.id, "link_title")
    await _show_source_edit(cb, pool, lang, src_id)
    await cb.answer(t(lang, "saved"))


@router.callback_query(F.data.startswith("src_reset:"))
async def cb_src_reset_name(cb: CallbackQuery, pool):
    lang = await _lang(pool, cb.from_user.id)
    src_id = int(cb.data.split(":", 1)[1])
    default_name = await db.reset_source_custom_label(pool, src_id, cb.from_user.id)
    await cb.answer(
        t(lang, "source_name_reset", name=(default_name or "")), show_alert=False
    )
    await _show_source_edit(cb, pool, lang, src_id)


@router.callback_query(F.data.startswith("src_rename:"))
async def cb_src_rename(cb: CallbackQuery, state: FSMContext, pool):
    lang = await _lang(pool, cb.from_user.id)
    src_id = int(cb.data.split(":", 1)[1])
    src = await db.get_source_detail(pool, src_id, cb.from_user.id)
    if not src:
        await cb.answer(t(lang, "cancelled"), show_alert=False)
        await _show_sources(cb, pool, lang)
        return
    await state.set_state(EditSourceName.waiting_name)
    await state.update_data(src_id=src_id)
    await _safe_edit(
        cb, t(lang, "source_rename_prompt", name=esc(src["effective_label"] or "")),
        reply_markup=nav_kb(lang, back_to="list_src"),
    )
    await cb.answer()


@router.message(EditSourceName.waiting_name)
async def on_source_rename(message: Message, state: FSMContext, pool):
    lang = await _lang(pool, message.from_user.id)
    data = await state.get_data()
    src_id = data.get("src_id")
    await state.clear()
    if src_id is None:
        await message.answer(t(lang, "cancelled"), reply_markup=main_menu(lang))
        return
    new_name = (message.text or "").strip()
    if not new_name:
        await message.answer(t(lang, "cancelled"), reply_markup=main_menu(lang))
        return
    saved = await db.set_source_custom_label(
        pool, src_id, message.from_user.id, new_name
    )
    src = await db.get_source_detail(pool, src_id, message.from_user.id)
    if src is None:
        await message.answer(t(lang, "cancelled"), reply_markup=main_menu(lang))
        return
    await message.answer(t(lang, "source_name_saved", name=esc(saved or new_name)))
    await message.answer(
        _source_edit_text(src, lang), reply_markup=source_edit_kb(src, lang)
    )


@router.callback_query(F.data.startswith("test_dest:"))
async def cb_test_dest(cb: CallbackQuery, pool, client, reader: str):
    lang = await _lang(pool, cb.from_user.id)
    dest_id = int(cb.data.split(":", 1)[1])
    dest = await db.get_destination(pool, dest_id, cb.from_user.id)
    if not dest:
        await cb.answer()
        return
    await cb.answer(t(lang, "testing"))
    ok, _ = await send_test_post(
        client, dest["chat_id"], dest.get("username"), dest["title"],
    )
    if ok:
        text = t(lang, "test_ok", title=dest["title"])
    else:
        text = t(lang, "test_fail", title=dest["title"], reader=reader)
    await _safe_edit(cb, text, reply_markup=main_menu(lang))


# ---------- settings ----------
@router.callback_query(F.data == "settings")
async def cb_settings(cb: CallbackQuery, state: FSMContext, pool):
    await state.clear()
    row = await db.get_settings(pool, cb.from_user.id)
    lang = row["language"]
    await _safe_edit(cb, t(lang, "settings_title"), reply_markup=settings_kb(row, lang))
    await cb.answer()


@router.callback_query(F.data == "set_interval")
async def cb_set_interval(cb: CallbackQuery, pool):
    lang = await _lang(pool, cb.from_user.id)
    await _safe_edit(cb, t(lang, "choose_interval"), reply_markup=interval_kb(lang))
    await cb.answer()


@router.callback_query(F.data.startswith("interval:"))
async def cb_interval_chosen(cb: CallbackQuery, pool):
    minutes = int(cb.data.split(":", 1)[1])
    await db.set_interval(pool, cb.from_user.id, minutes)
    scheduling.reschedule(minutes)
    row = await db.get_settings(pool, cb.from_user.id)
    lang = row["language"]
    await _safe_edit(cb, t(lang, "settings_title"), reply_markup=settings_kb(row, lang))
    await cb.answer(t(lang, "saved"))


@router.callback_query(F.data == "toggle_fwd")
async def cb_toggle_fwd(cb: CallbackQuery, pool):
    await db.toggle_skip_forwarded(pool, cb.from_user.id)
    row = await db.get_settings(pool, cb.from_user.id)
    lang = row["language"]
    await _safe_edit(cb, t(lang, "settings_title"), reply_markup=settings_kb(row, lang))
    await cb.answer(t(lang, "saved"))


@router.callback_query(F.data == "toggle_show_title")
async def cb_toggle_show_title(cb: CallbackQuery, pool):
    await db.toggle_show_title(pool, cb.from_user.id)
    row = await db.get_settings(pool, cb.from_user.id)
    lang = row["language"]
    await _safe_edit(cb, t(lang, "settings_title"), reply_markup=settings_kb(row, lang))
    await cb.answer(t(lang, "saved"))


@router.callback_query(F.data == "toggle_link_title")
async def cb_toggle_link_title(cb: CallbackQuery, pool):
    await db.toggle_link_title(pool, cb.from_user.id)
    row = await db.get_settings(pool, cb.from_user.id)
    lang = row["language"]
    await _safe_edit(cb, t(lang, "settings_title"), reply_markup=settings_kb(row, lang))
    await cb.answer(t(lang, "saved"))


@router.callback_query(F.data == "toggle_dest_user")
async def cb_toggle_dest_user(cb: CallbackQuery, pool, client):
    enabled = await db.toggle_dest_show_username(pool, cb.from_user.id)
    row = await db.get_settings(pool, cb.from_user.id)
    lang = row["language"]
    # When enabling "@username in footer", warn if the user owns any private
    # destination (no username) — those will fall back to the channel name.
    if enabled:
        # Refresh live so a channel that just became public / was renamed is
        # picked up immediately (not only on the 15-min sweep). This is why the
        # warning + old name lingered after you added @iraanfeed.
        dests = await db.list_destinations(pool, cb.from_user.id)
        try:
            await refresh_destinations(client, pool, dests)
            dests = await db.list_destinations(pool, cb.from_user.id)
        except Exception:  # noqa: BLE001
            pass
        private = [d["title"] for d in dests if not d.get("username")]
        if private:
            await cb.answer(
                t(lang, "dest_user_warn", names=", ".join(private[:5])),
                show_alert=True,
            )
        else:
            await cb.answer(t(lang, "saved"))
    else:
        await cb.answer(t(lang, "saved"))
    await _safe_edit(cb, t(lang, "settings_title"), reply_markup=settings_kb(row, lang))


@router.callback_query(F.data == "set_lang")
async def cb_set_lang(cb: CallbackQuery, pool):
    lang = await _lang(pool, cb.from_user.id)
    await _safe_edit(cb, t(lang, "choose_language"), reply_markup=language_kb(lang))
    await cb.answer()


@router.callback_query(F.data.startswith("lang:"))
async def cb_lang_chosen(cb: CallbackQuery, pool):
    new_lang = cb.data.split(":", 1)[1]
    await db.set_language(pool, cb.from_user.id, new_lang)
    row = await db.get_settings(pool, cb.from_user.id)
    await _safe_edit(cb, t(new_lang, "settings_title"), reply_markup=settings_kb(row, new_lang))
    await cb.answer(t(new_lang, "saved"))
