# Simple i18n: T[lang][key]. Use t(lang, key, **kwargs).

T = {
    "en": {
        "welcome": (
            "\U0001F4F0 <b>News Aggregator Bot</b>\n\n"
            "I collect posts from Telegram channels and RSS feeds into your "
            "own channels, each labelled with its source.\n\n"
            "<b>How to set up:</b>\n"
            "1\uFE0F\u20E3 Create a channel (or use one you already have).\n"
            "2\uFE0F\u20E3 Add <b>{reader}</b> as an <b>admin</b> of that channel, "
            "with permission to post messages.\n"
            "3\uFE0F\u20E3 Tap <b>\u2795 Add Destination</b> and forward any message "
            "from your channel to me.\n"
            "4\uFE0F\u20E3 Tap <b>\U0001F4E1 Add Source</b> and send a Telegram channel "
            "(<code>@name</code>) or an RSS link.\n\n"
            "You can route different sources to different channels "
            "(e.g. sport news \u2192 your sport channel)."
        ),
        "btn_add_dest": "\u2795 Add Destination",
        "btn_add_source": "\U0001F4E1 Add Source",
        "btn_my_setup": "\U0001F4CB My Setup",
        "btn_settings": "\u2699\uFE0F Settings",
        "btn_language": "\U0001F310 Language",
        "btn_back": "\u2B05\uFE0F Back",
        "btn_cancel": "\u274C Cancel",
        "add_dest_prompt": (
            "<b>Add a destination channel</b>\n\n"
            "1\uFE0F\u20E3 Make sure <b>{reader}</b> is an <b>admin</b> of the channel "
            "(with post rights).\n"
            "2\uFE0F\u20E3 Then <b>forward any message</b> from that channel to me."
        ),
        "dest_saved": "\u2705 Destination saved: <b>{title}</b>",
        "dest_unreachable": (
            "\u26A0\uFE0F Saved <b>{title}</b>, but I <b>can't post there yet</b>.\n\n"
            "The reader account <b>{reader}</b> is not an admin of that channel. "
            "Open the channel \u2192 <i>Administrators</i> \u2192 <i>Add admin</i>, "
            "add <b>{reader}</b> with <b>Post messages</b> permission, then send "
            "any post in the source \u2014 it will start mirroring automatically. "
            "No need to add the destination again."
        ),
        "forward_a_channel": "Please <b>forward</b> a message that comes from a <b>channel</b>.",
        "choose_dest": "Choose the destination for this source:",
        "source_prompt": (
            "Send a source for <b>{title}</b>:\n\n"
            "\u2022 Telegram channel: <code>@username</code> or "
            "<code>https://t.me/username</code>\n"
            "\u2022 RSS feed: <code>https://\u2026/rss.xml</code>"
        ),
        "source_added_tg": "\u2705 Telegram source added: <b>{label}</b>",
        "source_added_rss": "\u2705 RSS source added: <b>{label}</b>",
        "source_error": "\u274C Could not add <code>{name}</code>: {err}",
        "need_dest_first": "Add a destination channel first.",
        "setup_empty": "Nothing configured yet.",
        "setup_hint": "\n\n<i>Tap \U0001F5D1 to remove a channel or source.</i>",
        "dest_deleted": "\U0001F5D1 Removed destination: {title}",
        "source_deleted": "\U0001F5D1 Removed source: {label}",
        "no_sources": "  <i>(no sources yet)</i>",
        "cancelled": "Cancelled.",
        "settings_title": "\u2699\uFE0F <b>Settings</b>",
        "btn_interval": "\u23F1 Check every: {min} min",
        "btn_skipfwd_on": "\U0001F6AB Skip forwarded ads: ON",
        "btn_skipfwd_off": "\U0001F6AB Skip forwarded ads: OFF",
        "btn_showtitle_on": "\U0001F4F0 Show source title: ON",
        "btn_showtitle_off": "\U0001F4F0 Show source title: OFF",
        "btn_linktitle_on": "\U0001F517 Link the title: ON",
        "btn_linktitle_off": "\U0001F517 Link the title: OFF",
        "btn_destuser_on": "\U0001F4E3 Footer shows @username: ON",
        "btn_destuser_off": "\U0001F4E3 Footer shows @username: OFF",
        "dest_user_warn": "\u26A0\uFE0F These channels are private (no @username), so their name will be shown instead: {names}",
        "source_prefix": "Source",
        "continued": "(continued\u2026)",
        "rss_invalid": "\u274C {detail}",
        "choose_interval": "How often should I check RSS feeds?",
        "choose_language": "Choose your language:",
        "saved": "\u2705 Saved.",
        "btn_list_sources": "\U0001F4E1 List of Sources",
        "btn_list_dests": "\U0001F4E2 List of Destinations",
        "btn_delete": "\U0001F5D1 Delete",
        "btn_send_test": "\U0001F9EA Send test post",
        "setup_menu": "\U0001F4CB <b>My Setup</b>\n\nManage your sources and destinations.",
        "sources_title": "\U0001F4E1 <b>List of Sources</b>\n\n<i>Tap a source to edit its name and display options.</i>",
        "dests_title": "\U0001F4E2 <b>List of Destinations</b>\n\n<i>Tap the test button to send a test post, or Delete to remove.</i>",
        "no_sources_yet": "No sources yet.",
        "no_dests_yet": "No destinations yet.",
        "test_added": "\u2705 Destination saved: <b>{title}</b>\n\nSend a test post to make sure I can publish there.",
        "test_ok": "\u2705 Test post delivered to <b>{title}</b>. It's working!",
        "test_fail": "\u274C Couldn't post to <b>{title}</b>.\n\nMake sure <b>{reader}</b> is an admin of that channel with <b>Post messages</b> permission, then try again.",
        "testing": "\u23F3 Sending a test post\u2026",
        "btn_src_showtitle_on": "\U0001F4F0 Show source name: ON",
        "btn_src_showtitle_off": "\U0001F4F0 Show source name: OFF",
        "btn_src_linktitle_on": "\U0001F517 Hyperlink the name: ON",
        "btn_src_linktitle_off": "\U0001F517 Hyperlink the name: OFF",
        "btn_src_rename": "\u270F\uFE0F Edit name",
        "btn_src_resetname": "\u267B\uFE0F Reset name to default",
        "source_edit_title": (
            "\u2699\uFE0F <b>Edit source</b>\n\n"
            "Name: <b>{name}</b>\n"
            "Handle: <b>{handle}</b>\n"
            "Destination: <b>{dest}</b>\n\n"
            "\u2022 <b>Show source name</b>: {show}\n"
            "\u2022 <b>Hyperlink the name</b>: {link}\n\n"
            "<i>The hyperlink only appears when the source name is shown.</i>"
        ),
        "source_rename_prompt": (
            "\u270F\uFE0F Send the new name for <b>{name}</b>.\n\n"
            "<i>You can reset it to the original name later.</i>"
        ),
        "source_name_saved": "\u2705 Source name changed to: <b>{name}</b>",
        "source_name_reset": "\u267B\uFE0F Source name reset to default: <b>{name}</b>",
        "btn_ad_filter": "\U0001F9F9 Ad filter",
        "btn_ad_on": "\U0001F7E2 Ad filter: ON",
        "btn_ad_off": "\u26AA Ad filter: OFF",
        "btn_ad_add": "\u2795 Add block word / @handle / #hashtag",
        "btn_ad_item": "\U0001F5D1 {pattern}",
        "btn_ad_clean": "\U0001F9FD Clean existing ads",
        "btn_ad_clean_yes": "\u2705 Yes, delete them",
        "btn_ad_clean_no": "\u2B05\uFE0F No, go back",
        "ad_filter_title": (
            "\U0001F9F9 <b>Ad filter</b>\n\n"
            "Status: <b>{status}</b>\n\n"
            "When ON, any <b>new</b> incoming post that contains one of your "
            "block words, <code>@handles</code> or <code>#hashtags</code> is "
            "skipped. Tap a pattern below to remove it.{hint}"
        ),
        "ad_filter_hint_empty": "\n\n<i>No block patterns yet \u2014 tap Add.</i>",
        "ad_add_prompt": (
            "Send the word, phrase, <code>@handle</code> or <code>#hashtag</code> "
            "to block.\n\n<i>You can send several at once, one per line.</i>"
        ),
        "ad_added": "\u2705 Added {count} block pattern(s).",
        "ad_added_none": "Nothing added (blank or already in the list).",
        "ad_deleted": "\U0001F5D1 Removed: <b>{pattern}</b>",
        "ad_clean_confirm": (
            "\u26A0\uFE0F <b>Delete existing ads?</b>\n\n"
            "I'll scan the recent history of your destination channel(s) and "
            "<b>permanently delete</b> every post that matches your block "
            "patterns. This cannot be undone.\n\n"
            "Do you want me to continue?"
        ),
        "ad_clean_none_patterns": "Add at least one block pattern first.",
        "ad_clean_running": "\u23F3 Scanning your channels and deleting matching ads\u2026",
        "ad_clean_done": "\u2705 Deleted <b>{n}</b> ad post(s) from your channel(s).",
        "ad_clean_nomatch": "\u2705 Scan complete \u2014 no matching posts found.",
        "btn_dedup": "\U0001F500 Duplicate filter",
        "btn_dedup_on": "\U0001F7E2 Duplicate filter: ON",
        "btn_dedup_off": "\u26AA Duplicate filter: OFF",
        "btn_dedup_window": "\u23F1 Lookback window: {min} min",
        "btn_dedup_threshold": "\U0001F3AF Similarity threshold: {pct}%",
        "btn_dedup_minlen": "\u270F\uFE0F Minimum length: {n} chars",
        "btn_dedup_window_opt": "{min} min",
        "btn_dedup_threshold_opt": "{pct}%",
        "btn_dedup_minlen_opt": "{n} chars",
        "dedup_title": (
            "\U0001F500 <b>Duplicate filter</b>\n\n"
            "Status: <b>{status}</b>\n\n"
            "When ON, a post whose text is nearly identical to something already "
            "published to the same channel is skipped \u2014 the first copy wins. "
            "Comparison ignores emoji, links and Arabic/Persian spelling.\n\n"
            "\u2022 Lookback window: <b>{min} min</b>\n"
            "\u2022 Similarity threshold: <b>{pct}%</b>\n"
            "\u2022 Minimum length: <b>{n} chars</b>"
        ),
        "dedup_choose_window": (
            "How far back should I look for duplicates?\n\n"
            "<i>Only posts from the last N minutes are compared.</i>"
        ),
        "dedup_choose_threshold": (
            "How similar must two posts be to count as duplicates?\n\n"
            "<i>Higher = stricter (only near-identical posts dropped).</i>"
        ),
        "dedup_choose_minlen": (
            "Shortest caption to check.\n\n"
            "<i>Posts shorter than this are never treated as duplicates.</i>"
        ),
        "on": "ON",
        "off": "OFF",
        "btn_status": "\U0001F4CA Status",
        "userbot_dead_hint": (
            "\U0001F534 <b>Userbot session is dead!</b>\n\n"
            "The reader account\u2019s session string was used from two different "
            "IPs (e.g. two containers running at the same time), so Telegram "
            "killed it permanently. No posts will be delivered until you fix "
            "this.\n\n"
            "<b>How to fix:</b>\n"
            "1\uFE0F\u20E3 Generate a new session string (run gen_session.py or "
            "use Telethon locally).\n"
            "2\uFE0F\u20E3 Update the SESSION_STRING env var on your hosting "
            "platform.\n"
            "3\uFE0F\u20E3 Redeploy.\n\n"
            "Make sure only ONE container runs with the same session string, "
            "or it will die again."
        ),
        "status_text": (
            "\U0001F4CA <b>Bot Status</b>\n\n"
            "\u2022 Userbot session: {alive_icon} <b>{alive_word}</b>\n"
            "{err_line}"
            "\u2022 Duplicate filter checks: <b>{dedup_checked}</b>\n"
            "\u2022 Duplicates blocked: <b>{dedup_dropped}</b>\n"
            "\u2022 Destinations tracked: <b>{dedup_tracked}</b>"
        ),
        "status_err_line": "\u26A0\uFE0F <i>{err_detail}</i>\n",
    },
    "fa": {
        "welcome": (
            "\U0001F4F0 <b>\u0631\u0628\u0627\u062A \u062A\u062C\u0645\u06CC\u0639 \u0627\u062E\u0628\u0627\u0631</b>\n\n"
            "\u067E\u0633\u062A\u200C\u0647\u0627\u06CC \u06A9\u0627\u0646\u0627\u0644\u200C\u0647\u0627\u06CC \u062A\u0644\u06AF\u0631\u0627\u0645 \u0648 \u0641\u06CC\u062F\u0647\u0627\u06CC RSS \u0631\u0627 "
            "\u062F\u0631 \u06A9\u0627\u0646\u0627\u0644\u200C\u0647\u0627\u06CC \u062E\u0648\u062F\u062A \u06AF\u0631\u062F\u0622\u0648\u0631\u06CC \u0645\u06CC\u200C\u06A9\u0646\u0645\u060C \u0628\u0627 \u0628\u0631\u0686\u0633\u0628 \u0645\u0646\u0628\u0639.\n\n"
            "<b>\u0631\u0627\u0647\u200C\u0627\u0646\u062F\u0627\u0632\u06CC:</b>\n"
            "1\uFE0F\u20E3 \u06CC\u06A9 \u06A9\u0627\u0646\u0627\u0644 \u0628\u0633\u0627\u0632 (\u06CC\u0627 \u06A9\u0627\u0646\u0627\u0644 \u0645\u0648\u062C\u0648\u062F).\n"
            "2\uFE0F\u20E3 <b>{reader}</b> \u0631\u0627 \u0628\u0647 \u0639\u0646\u0648\u0627\u0646 <b>\u0627\u062F\u0645\u06CC\u0646</b> \u06A9\u0627\u0646\u0627\u0644 "
            "\u0628\u0627 \u062F\u0633\u062A\u0631\u0633\u06CC \u0627\u0631\u0633\u0627\u0644 \u067E\u06CC\u0627\u0645 \u0627\u0636\u0627\u0641\u0647 \u06A9\u0646.\n"
            "3\uFE0F\u20E3 \u062F\u06A9\u0645\u0647 <b>\u2795 \u0627\u0641\u0632\u0648\u062F\u0646 \u0645\u0642\u0635\u062F</b> \u0631\u0627 \u0628\u0632\u0646 \u0648 \u06CC\u06A9 \u067E\u06CC\u0627\u0645 \u0627\u0632 \u06A9\u0627\u0646\u0627\u0644\u062A \u0631\u0627 \u0641\u0648\u0631\u0648\u0627\u0631\u062F \u06A9\u0646.\n"
            "4\uFE0F\u20E3 \u062F\u06A9\u0645\u0647 <b>\U0001F4E1 \u0627\u0641\u0632\u0648\u062F\u0646 \u0645\u0646\u0628\u0639</b> \u0631\u0627 \u0628\u0632\u0646 \u0648 \u06CC\u06A9 \u06A9\u0627\u0646\u0627\u0644 "
            "(<code>@name</code>) \u06CC\u0627 \u0644\u06CC\u0646\u06A9 RSS \u0628\u0641\u0631\u0633\u062A.\n\n"
            "\u0645\u06CC\u200C\u062A\u0648\u0627\u0646\u06CC \u0645\u0646\u0627\u0628\u0639 \u0645\u062E\u062A\u0644\u0641 \u0631\u0627 \u0628\u0647 \u06A9\u0627\u0646\u0627\u0644\u200C\u0647\u0627\u06CC \u0645\u062E\u062A\u0644\u0641 \u0628\u0641\u0631\u0633\u062A\u06CC."
        ),
        "btn_add_dest": "\u2795 \u0627\u0641\u0632\u0648\u062F\u0646 \u0645\u0642\u0635\u062F",
        "btn_add_source": "\U0001F4E1 \u0627\u0641\u0632\u0648\u062F\u0646 \u0645\u0646\u0628\u0639",
        "btn_my_setup": "\U0001F4CB \u062A\u0646\u0638\u06CC\u0645\u0627\u062A \u0645\u0646",
        "btn_settings": "\u2699\uFE0F \u062A\u0646\u0638\u06CC\u0645\u0627\u062A",
        "btn_language": "\U0001F310 \u0632\u0628\u0627\u0646",
        "btn_back": "\u2B05\uFE0F \u0628\u0627\u0632\u06AF\u0634\u062A",
        "btn_cancel": "\u274C \u0644\u063A\u0648",
        "add_dest_prompt": (
            "<b>\u0627\u0641\u0632\u0648\u062F\u0646 \u06A9\u0627\u0646\u0627\u0644 \u0645\u0642\u0635\u062F</b>\n\n"
            "1\uFE0F\u20E3 \u0645\u0637\u0645\u0626\u0646 \u0634\u0648 <b>{reader}</b> \u0627\u062F\u0645\u06CC\u0646 \u06A9\u0627\u0646\u0627\u0644 \u0627\u0633\u062A.\n"
            "2\uFE0F\u20E3 \u0633\u067E\u0633 \u06CC\u06A9 \u067E\u06CC\u0627\u0645 \u0627\u0632 \u0622\u0646 \u06A9\u0627\u0646\u0627\u0644 \u0631\u0627 \u0641\u0648\u0631\u0648\u0627\u0631\u062F \u06A9\u0646."
        ),
        "dest_saved": "\u2705 \u0645\u0642\u0635\u062F \u0630\u062E\u06CC\u0631\u0647 \u0634\u062F: <b>{title}</b>",
        "dest_unreachable": (
            "\u26A0\uFE0F <b>{title}</b> \u0630\u062E\u06CC\u0631\u0647 \u0634\u062F\u060C \u0627\u0645\u0627 \u0647\u0646\u0648\u0632 "
            "<b>\u0646\u0645\u06CC\u200C\u062A\u0648\u0627\u0646\u0645 \u062F\u0631 \u0622\u0646 \u067E\u0633\u062A \u0628\u06AF\u0630\u0627\u0631\u0645</b>.\n\n"
            "\u062D\u0633\u0627\u0628 \u062E\u0648\u0627\u0646\u0646\u062F\u0647 <b>{reader}</b> \u0627\u062F\u0645\u06CC\u0646 \u0627\u06CC\u0646 \u06A9\u0627\u0646\u0627\u0644 \u0646\u06CC\u0633\u062A. "
            "\u06A9\u0627\u0646\u0627\u0644 \u0631\u0627 \u0628\u0627\u0632 \u06A9\u0646 \u2190 <i>\u0645\u062F\u06CC\u0631\u0627\u0646</i> \u2190 <i>\u0627\u0641\u0632\u0648\u062F\u0646 \u0645\u062F\u06CC\u0631</i>\u060C "
            "\u0648 <b>{reader}</b> \u0631\u0627 \u0628\u0627 \u062F\u0633\u062A\u0631\u0633\u06CC <b>\u0627\u0631\u0633\u0627\u0644 \u067E\u06CC\u0627\u0645</b> \u0627\u0636\u0627\u0641\u0647 \u06A9\u0646\u060C "
            "\u0633\u067E\u0633 \u06CC\u06A9 \u067E\u0633\u062A \u062F\u0631 \u0645\u0646\u0628\u0639 \u0628\u06AF\u0630\u0627\u0631 \u2014 \u062E\u0648\u062F\u06A9\u0627\u0631 \u0634\u0631\u0648\u0639 \u0645\u06CC\u200C\u0634\u0648\u062F. "
            "\u0646\u06CC\u0627\u0632\u06CC \u0628\u0647 \u0627\u0641\u0632\u0648\u062F\u0646 \u062F\u0648\u0628\u0627\u0631\u0647 \u0645\u0642\u0635\u062F \u0646\u06CC\u0633\u062A."
        ),
        "forward_a_channel": "\u0644\u0637\u0641\u0627\u064B \u06CC\u06A9 \u067E\u06CC\u0627\u0645 \u0627\u0632 \u06CC\u06A9 <b>\u06A9\u0627\u0646\u0627\u0644</b> \u0641\u0648\u0631\u0648\u0627\u0631\u062F \u06A9\u0646.",
        "choose_dest": "\u0645\u0642\u0635\u062F \u0627\u06CC\u0646 \u0645\u0646\u0628\u0639 \u0631\u0627 \u0627\u0646\u062A\u062E\u0627\u0628 \u06A9\u0646:",
        "source_prompt": (
            "\u06CC\u06A9 \u0645\u0646\u0628\u0639 \u0628\u0631\u0627\u06CC <b>{title}</b> \u0628\u0641\u0631\u0633\u062A:\n\n"
            "\u2022 \u06A9\u0627\u0646\u0627\u0644 \u062A\u0644\u06AF\u0631\u0627\u0645: <code>@username</code> \u06CC\u0627 "
            "<code>https://t.me/username</code>\n"
            "\u2022 \u0641\u06CC\u062F RSS: <code>https://\u2026/rss.xml</code>"
        ),
        "source_added_tg": "\u2705 \u0645\u0646\u0628\u0639 \u062A\u0644\u06AF\u0631\u0627\u0645 \u0627\u0636\u0627\u0641\u0647 \u0634\u062F: <b>{label}</b>",
        "source_added_rss": "\u2705 \u0645\u0646\u0628\u0639 RSS \u0627\u0636\u0627\u0641\u0647 \u0634\u062F: <b>{label}</b>",
        "source_error": "\u274C \u0627\u0641\u0632\u0648\u062F\u0646 <code>{name}</code> \u0646\u0627\u0645\u0648\u0641\u0642 \u0628\u0648\u062F: {err}",
        "need_dest_first": "\u0627\u0648\u0644 \u06CC\u06A9 \u06A9\u0627\u0646\u0627\u0644 \u0645\u0642\u0635\u062F \u0627\u0636\u0627\u0641\u0647 \u06A9\u0646.",
        "setup_empty": "\u0647\u0646\u0648\u0632 \u0686\u06CC\u0632\u06CC \u062A\u0646\u0638\u06CC\u0645 \u0646\u0634\u062F\u0647.",
        "setup_hint": "\n\n<i>\u0628\u0631\u0627\u06CC \u062D\u0630\u0641 \u06A9\u0627\u0646\u0627\u0644 \u06CC\u0627 \u0645\u0646\u0628\u0639 \u0631\u0648\u06CC \U0001F5D1 \u0628\u0632\u0646.</i>",
        "dest_deleted": "\U0001F5D1 \u0645\u0642\u0635\u062F \u062D\u0630\u0641 \u0634\u062F: {title}",
        "source_deleted": "\U0001F5D1 \u0645\u0646\u0628\u0639 \u062D\u0630\u0641 \u0634\u062F: {label}",
        "no_sources": "  <i>(\u0628\u062F\u0648\u0646 \u0645\u0646\u0628\u0639)</i>",
        "cancelled": "\u0644\u063A\u0648 \u0634\u062F.",
        "settings_title": "\u2699\uFE0F <b>\u062A\u0646\u0638\u06CC\u0645\u0627\u062A</b>",
        "btn_interval": "\u23F1 \u0628\u0631\u0631\u0633\u06CC \u0647\u0631: {min} \u062F\u0642\u06CC\u0642\u0647",
        "btn_skipfwd_on": "\U0001F6AB \u0631\u062F \u062A\u0628\u0644\u06CC\u063A\u0627\u062A \u0641\u0648\u0631\u0648\u0627\u0631\u062F\u06CC: \u0631\u0648\u0634\u0646",
        "btn_skipfwd_off": "\U0001F6AB \u0631\u062F \u062A\u0628\u0644\u06CC\u063A\u0627\u062A \u0641\u0648\u0631\u0648\u0627\u0631\u062F\u06CC: \u062E\u0627\u0645\u0648\u0634",
        "choose_interval": "\u0647\u0631 \u0686\u0646\u062F \u0648\u0642\u062A \u0641\u06CC\u062F\u0647\u0627\u06CC RSS \u0628\u0631\u0631\u0633\u06CC \u0634\u0648\u0646\u062F\u061F",
        "choose_language": "\u0632\u0628\u0627\u0646 \u062E\u0648\u062F \u0631\u0627 \u0627\u0646\u062A\u062E\u0627\u0628 \u06A9\u0646:",
        "saved": "\u2705 \u0630\u062E\u06CC\u0631\u0647 \u0634\u062F.",
        "btn_showtitle_on": "\U0001F4F0 \u0646\u0645\u0627\u06CC\u0634 \u0639\u0646\u0648\u0627\u0646 \u0645\u0646\u0628\u0639: \u0631\u0648\u0634\u0646",
        "btn_showtitle_off": "\U0001F4F0 \u0646\u0645\u0627\u06CC\u0634 \u0639\u0646\u0648\u0627\u0646 \u0645\u0646\u0628\u0639: \u062E\u0627\u0645\u0648\u0634",
        "btn_linktitle_on": "\U0001F517 \u0644\u06CC\u0646\u06A9\u200C\u062F\u0627\u0631 \u0634\u062F\u0646 \u0639\u0646\u0648\u0627\u0646: \u0631\u0648\u0634\u0646",
        "btn_linktitle_off": "\U0001F517 \u0644\u06CC\u0646\u06A9\u200C\u062F\u0627\u0631 \u0634\u062F\u0646 \u0639\u0646\u0648\u0627\u0646: \u062E\u0627\u0645\u0648\u0634",
        "btn_destuser_on": "\U0001F4E3 \u0646\u0645\u0627\u06CC\u0634 @\u06CC\u0648\u0632\u0631\u0646\u06CC\u0645 \u062F\u0631 \u067E\u0627\u0648\u0631\u0642\u06CC: \u0631\u0648\u0634\u0646",
        "btn_destuser_off": "\U0001F4E3 \u0646\u0645\u0627\u06CC\u0634 @\u06CC\u0648\u0632\u0631\u0646\u06CC\u0645 \u062F\u0631 \u067E\u0627\u0648\u0631\u0642\u06CC: \u062E\u0627\u0645\u0648\u0634",
        "dest_user_warn": "\u26A0\uFE0F \u0627\u06CC\u0646 \u06A9\u0627\u0646\u0627\u0644\u200C\u0647\u0627 \u062E\u0635\u0648\u0635\u06CC \u0647\u0633\u062A\u0646\u062F\u060C \u0646\u0627\u0645 \u0622\u0646\u200C\u0647\u0627 \u0646\u0645\u0627\u06CC\u0634 \u062F\u0627\u062F\u0647 \u0645\u06CC\u200C\u0634\u0648\u062F: {names}",
        "source_prefix": "\u0645\u0646\u0628\u0639",
        "continued": "(\u0627\u062f\u0627\u0645\u0647\u2026)",
        "rss_invalid": "\u274C {detail}",
        "btn_list_sources": "\U0001F4E1 \u0641\u0647\u0631\u0633\u062A \u0645\u0646\u0627\u0628\u0639",
        "btn_list_dests": "\U0001F4E2 \u0641\u0647\u0631\u0633\u062A \u0645\u0642\u0627\u0635\u062F",
        "btn_delete": "\U0001F5D1 \u062D\u0630\u0641",
        "btn_send_test": "\U0001F9EA \u0627\u0631\u0633\u0627\u0644 \u067E\u0633\u062A \u0622\u0632\u0645\u0627\u06CC\u0634\u06CC",
        "setup_menu": "\U0001F4CB <b>\u062A\u0646\u0638\u06CC\u0645\u0627\u062A \u0645\u0646</b>\n\n\u0645\u062F\u06CC\u0631\u06CC\u062A \u0645\u0646\u0627\u0628\u0639 \u0648 \u0645\u0642\u0627\u0635\u062F.",
        "sources_title": "\U0001F4E1 <b>\u0641\u0647\u0631\u0633\u062A \u0645\u0646\u0627\u0628\u0639</b>\n\n<i>\u0628\u0631\u0627\u06CC \u0648\u06CC\u0631\u0627\u06CC\u0634 \u0646\u0627\u0645 \u0648 \u062A\u0646\u0638\u06CC\u0645\u0627\u062A \u0646\u0645\u0627\u06CC\u0634\u060C \u0631\u0648\u06CC \u0645\u0646\u0628\u0639 \u0628\u0632\u0646.</i>",
        "dests_title": "\U0001F4E2 <b>\u0641\u0647\u0631\u0633\u062A \u0645\u0642\u0627\u0635\u062F</b>\n\n<i>\u0628\u0631\u0627\u06CC \u0627\u0631\u0633\u0627\u0644 \u067E\u0633\u062A \u0622\u0632\u0645\u0627\u06CC\u0634\u06CC \u0631\u0648\u06CC \u062F\u06A9\u0645\u0647 \u062A\u0633\u062A \u06CC\u0627 \u062D\u0630\u0641 \u0628\u0632\u0646.</i>",
        "no_sources_yet": "\u0647\u0646\u0648\u0632 \u0645\u0646\u0628\u0639\u06CC \u0646\u06CC\u0633\u062A.",
        "no_dests_yet": "\u0647\u0646\u0648\u0632 \u0645\u0642\u0635\u062F\u06CC \u0646\u06CC\u0633\u062A.",
        "test_added": "\u2705 \u0645\u0642\u0635\u062F \u0630\u062E\u06CC\u0631\u0647 \u0634\u062F: <b>{title}</b>\n\n\u06CC\u06A9 \u067E\u0633\u062A \u0622\u0632\u0645\u0627\u06CC\u0634\u06CC \u0628\u0641\u0631\u0633\u062A \u062A\u0627 \u0645\u0637\u0645\u0626\u0646 \u0634\u0648\u06CC \u0642\u0627\u0628\u0644 \u0627\u0631\u0633\u0627\u0644 \u0627\u0633\u062A.",
        "test_ok": "\u2705 \u067E\u0633\u062A \u0622\u0632\u0645\u0627\u06CC\u0634\u06CC \u0628\u0647 <b>{title}</b> \u0627\u0631\u0633\u0627\u0644 \u0634\u062F. \u06A9\u0627\u0631 \u0645\u06CC\u200C\u06A9\u0646\u062F!",
        "test_fail": "\u274C \u0627\u0631\u0633\u0627\u0644 \u0628\u0647 <b>{title}</b> \u0646\u0627\u0645\u0648\u0641\u0642 \u0628\u0648\u062F.\n\n\u0645\u0637\u0645\u0626\u0646 \u0634\u0648 <b>{reader}</b> \u0627\u062F\u0645\u06CC\u0646 \u0622\u0646 \u06A9\u0627\u0646\u0627\u0644 \u0628\u0627 \u062F\u0633\u062A\u0631\u0633\u06CC <b>\u0627\u0631\u0633\u0627\u0644 \u067E\u06CC\u0627\u0645</b> \u0627\u0633\u062A\u060C \u0633\u067E\u0633 \u062F\u0648\u0628\u0627\u0631\u0647 \u0627\u0645\u062A\u062D\u0627\u0646 \u06A9\u0646.",
        "testing": "\u23F3 \u062F\u0631 \u062D\u0627\u0644 \u0627\u0631\u0633\u0627\u0644 \u067E\u0633\u062A \u0622\u0632\u0645\u0627\u06CC\u0634\u06CC\u2026",
        "btn_src_showtitle_on": "\U0001F4F0 \u0646\u0645\u0627\u06CC\u0634 \u0646\u0627\u0645 \u0645\u0646\u0628\u0639: \u0631\u0648\u0634\u0646",
        "btn_src_showtitle_off": "\U0001F4F0 \u0646\u0645\u0627\u06CC\u0634 \u0646\u0627\u0645 \u0645\u0646\u0628\u0639: \u062E\u0627\u0645\u0648\u0634",
        "btn_src_linktitle_on": "\U0001F517 \u0644\u06CC\u0646\u06A9\u200C\u062F\u0627\u0631 \u06A9\u0631\u062F\u0646 \u0646\u0627\u0645: \u0631\u0648\u0634\u0646",
        "btn_src_linktitle_off": "\U0001F517 \u0644\u06CC\u0646\u06A9\u200C\u062F\u0627\u0631 \u06A9\u0631\u062F\u0646 \u0646\u0627\u0645: \u062E\u0627\u0645\u0648\u0634",
        "btn_src_rename": "\u270F\uFE0F \u0648\u06CC\u0631\u0627\u06CC\u0634 \u0646\u0627\u0645",
        "btn_src_resetname": "\u267B\uFE0F \u0628\u0627\u0632\u0646\u0634\u0627\u0646\u06CC \u0646\u0627\u0645 \u0628\u0647 \u067E\u06CC\u0634\u200C\u0641\u0631\u0636",
        "source_edit_title": (
            "\u2699\uFE0F <b>\u0648\u06CC\u0631\u0627\u06CC\u0634 \u0645\u0646\u0628\u0639</b>\n\n"
            "\u0646\u0627\u0645: <b>{name}</b>\n"
            "\u0634\u0646\u0627\u0633\u0647: <b>{handle}</b>\n"
            "\u0645\u0642\u0635\u062F: <b>{dest}</b>\n\n"
            "\u2022 <b>\u0646\u0645\u0627\u06CC\u0634 \u0646\u0627\u0645 \u0645\u0646\u0628\u0639</b>: {show}\n"
            "\u2022 <b>\u0644\u06CC\u0646\u06A9\u200C\u062F\u0627\u0631 \u0628\u0648\u062F\u0646 \u0646\u0627\u0645</b>: {link}\n\n"
            "<i>\u0644\u06CC\u0646\u06A9 \u0641\u0642\u0637 \u0632\u0645\u0627\u0646\u06CC \u0646\u0634\u0627\u0646 \u062F\u0627\u062F\u0647 \u0645\u06CC\u200C\u0634\u0648\u062F \u06A9\u0647 \u0646\u0627\u0645 \u0645\u0646\u0628\u0639 \u0646\u0645\u0627\u06CC\u0634 \u062F\u0627\u062F\u0647 \u0634\u0648\u062F.</i>"
        ),
        "source_rename_prompt": (
            "\u270F\uFE0F \u0646\u0627\u0645 \u062C\u062F\u06CC\u062F \u0631\u0627 \u0628\u0631\u0627\u06CC <b>{name}</b> \u0628\u0641\u0631\u0633\u062A.\n\n"
            "<i>\u0628\u0639\u062F\u0627\u064B \u0645\u06CC\u200C\u062A\u0648\u0627\u0646\u06CC \u0622\u0646 \u0631\u0627 \u0628\u0647 \u0646\u0627\u0645 \u0627\u0648\u0644\u06CC\u0647 \u0628\u0627\u0632\u06AF\u0631\u062F\u0627\u0646\u06CC.</i>"
        ),
        "source_name_saved": "\u2705 \u0646\u0627\u0645 \u0645\u0646\u0628\u0639 \u062A\u063A\u06CC\u06CC\u0631 \u06A9\u0631\u062F \u0628\u0647: <b>{name}</b>",
        "source_name_reset": "\u267B\uFE0F \u0646\u0627\u0645 \u0645\u0646\u0628\u0639 \u0628\u0647 \u067E\u06CC\u0634\u200C\u0641\u0631\u0636 \u0628\u0627\u0632\u06AF\u0634\u062A: <b>{name}</b>",
        "btn_ad_filter": "\U0001f9f9 \u0641\u06cc\u0644\u062a\u0631 \u062a\u0628\u0644\u06cc\u063a\u0627\u062a",
        "btn_ad_on": "\U0001f7e2 \u0641\u06cc\u0644\u062a\u0631 \u062a\u0628\u0644\u06cc\u063a\u0627\u062a: \u0631\u0648\u0634\u0646",
        "btn_ad_off": "\u26aa \u0641\u06cc\u0644\u062a\u0631 \u062a\u0628\u0644\u06cc\u063a\u0627\u062a: \u062e\u0627\u0645\u0648\u0634",
        "btn_ad_add": "\u2795 \u0627\u0641\u0632\u0648\u062f\u0646 \u06a9\u0644\u0645\u0647/\u200f@\u0622\u06cc\u062f\u06cc/\u200f#\u0647\u0634\u062a\u06af \u0645\u0633\u062f\u0648\u062f",
        "btn_ad_item": "\U0001f5d1 {pattern}",
        "btn_ad_clean": "\U0001f9fd \u067e\u0627\u06a9\u200c\u0633\u0627\u0632\u06cc \u062a\u0628\u0644\u06cc\u063a\u0627\u062a \u0645\u0648\u062c\u0648\u062f",
        "btn_ad_clean_yes": "\u2705 \u0628\u0644\u0647\u060c \u062d\u0630\u0641 \u0634\u0648\u0646\u062f",
        "btn_ad_clean_no": "\u2b05\ufe0f \u062e\u06cc\u0631\u060c \u0628\u0627\u0632\u06af\u0634\u062a",
        "ad_filter_title": "\U0001f9f9 <b>\u0641\u06cc\u0644\u062a\u0631 \u062a\u0628\u0644\u06cc\u063a\u0627\u062a</b>\n\n\u0648\u0636\u0639\u06cc\u062a: <b>{status}</b>\n\n\u0648\u0642\u062a\u06cc \u0631\u0648\u0634\u0646 \u0628\u0627\u0634\u062f\u060c \u0647\u0631 \u067e\u0633\u062a <b>\u062c\u062f\u06cc\u062f\u06cc</b> \u06a9\u0647 \u0634\u0627\u0645\u0644 \u06cc\u06a9\u06cc \u0627\u0632 \u06a9\u0644\u0645\u0647\u200c\u0647\u0627\u060c <code>@\u0622\u06cc\u062f\u06cc\u200c\u0647\u0627</code> \u06cc\u0627 <code>#\u0647\u0634\u062a\u06af\u200c\u0647\u0627\u06cc</code> \u0645\u0633\u062f\u0648\u062f \u0634\u0645\u0627 \u0628\u0627\u0634\u062f \u0646\u0627\u062f\u06cc\u062f\u0647 \u06af\u0631\u0641\u062a\u0647 \u0645\u06cc\u200c\u0634\u0648\u062f. \u0628\u0631\u0627\u06cc \u062d\u0630\u0641 \u06cc\u06a9 \u0645\u0648\u0631\u062f \u0631\u0648\u06cc \u0622\u0646 \u0628\u0632\u0646\u06cc\u062f.{hint}",
        "ad_filter_hint_empty": "\n\n<i>\u0647\u0646\u0648\u0632 \u0645\u0648\u0631\u062f\u06cc \u0627\u0636\u0627\u0641\u0647 \u0646\u0634\u062f\u0647 \u2014 \u0631\u0648\u06cc \u0627\u0641\u0632\u0648\u062f\u0646 \u0628\u0632\u0646\u06cc\u062f.</i>",
        "ad_add_prompt": "\u06a9\u0644\u0645\u0647\u060c \u0639\u0628\u0627\u0631\u062a\u060c <code>@\u0622\u06cc\u062f\u06cc</code> \u06cc\u0627 <code>#\u0647\u0634\u062a\u06af</code> \u0645\u0648\u0631\u062f\u0646\u0638\u0631 \u0628\u0631\u0627\u06cc \u0645\u0633\u062f\u0648\u062f\u0633\u0627\u0632\u06cc \u0631\u0627 \u0628\u0641\u0631\u0633\u062a\u06cc\u062f.\n\n<i>\u0645\u06cc\u200c\u062a\u0648\u0627\u0646\u06cc\u062f \u0686\u0646\u062f \u0645\u0648\u0631\u062f \u0631\u0627 \u0647\u0645\u200c\u0632\u0645\u0627\u0646\u060c \u0647\u0631 \u06a9\u062f\u0627\u0645 \u062f\u0631 \u06cc\u06a9 \u062e\u0637\u060c \u0628\u0641\u0631\u0633\u062a\u06cc\u062f.</i>",
        "ad_added": "\u2705 {count} \u0645\u0648\u0631\u062f \u0645\u0633\u062f\u0648\u062f \u0627\u0636\u0627\u0641\u0647 \u0634\u062f.",
        "ad_added_none": "\u0686\u06cc\u0632\u06cc \u0627\u0636\u0627\u0641\u0647 \u0646\u0634\u062f (\u062e\u0627\u0644\u06cc \u0628\u0648\u062f \u06cc\u0627 \u0627\u0632 \u0642\u0628\u0644 \u062f\u0631 \u0641\u0647\u0631\u0633\u062a \u0628\u0648\u062f).",
        "ad_deleted": "\U0001f5d1 \u062d\u0630\u0641 \u0634\u062f: <b>{pattern}</b>",
        "ad_clean_confirm": "\u26a0\ufe0f <b>\u062a\u0628\u0644\u06cc\u063a\u0627\u062a \u0645\u0648\u062c\u0648\u062f \u062d\u0630\u0641 \u0634\u0648\u0646\u062f\u061f</b>\n\n\u062a\u0627\u0631\u06cc\u062e\u0686\u0647 \u0627\u062e\u06cc\u0631 \u06a9\u0627\u0646\u0627\u0644\u200c(\u0647\u0627\u06cc) \u0645\u0642\u0635\u062f \u0634\u0645\u0627 \u0631\u0627 \u0628\u0631\u0631\u0633\u06cc \u0645\u06cc\u200c\u06a9\u0646\u0645 \u0648 \u0647\u0631 \u067e\u0633\u062a\u06cc \u0631\u0627 \u06a9\u0647 \u0628\u0627 \u0627\u0644\u06af\u0648\u0647\u0627\u06cc \u0645\u0633\u062f\u0648\u062f \u0634\u0645\u0627 \u0645\u0637\u0627\u0628\u0642\u062a \u062f\u0627\u0631\u062f <b>\u0628\u0631\u0627\u06cc \u0647\u0645\u06cc\u0634\u0647 \u062d\u0630\u0641</b> \u0645\u06cc\u200c\u06a9\u0646\u0645. \u0627\u06cc\u0646 \u06a9\u0627\u0631 \u0642\u0627\u0628\u0644 \u0628\u0627\u0632\u06af\u0634\u062a \u0646\u06cc\u0633\u062a.\n\n\u0627\u062f\u0627\u0645\u0647 \u0628\u062f\u0647\u0645\u061f",
        "ad_clean_none_patterns": "\u0627\u0628\u062a\u062f\u0627 \u062d\u062f\u0627\u0642\u0644 \u06cc\u06a9 \u0627\u0644\u06af\u0648\u06cc \u0645\u0633\u062f\u0648\u062f \u0627\u0636\u0627\u0641\u0647 \u06a9\u0646\u06cc\u062f.",
        "ad_clean_running": "\u23f3 \u062f\u0631 \u062d\u0627\u0644 \u0628\u0631\u0631\u0633\u06cc \u06a9\u0627\u0646\u0627\u0644\u200c\u0647\u0627 \u0648 \u062d\u0630\u0641 \u062a\u0628\u0644\u06cc\u063a\u0627\u062a \u0645\u0646\u0637\u0628\u0642\u2026",
        "ad_clean_done": "\u2705 \u062a\u0639\u062f\u0627\u062f <b>{n}</b> \u067e\u0633\u062a \u062a\u0628\u0644\u06cc\u063a\u0627\u062a\u06cc \u0627\u0632 \u06a9\u0627\u0646\u0627\u0644\u200c(\u0647\u0627\u06cc) \u0634\u0645\u0627 \u062d\u0630\u0641 \u0634\u062f.",
        "ad_clean_nomatch": "\u2705 \u0628\u0631\u0631\u0633\u06cc \u06a9\u0627\u0645\u0644 \u0634\u062f \u2014 \u067e\u0633\u062a \u0645\u0646\u0637\u0628\u0642\u06cc \u06cc\u0627\u0641\u062a \u0646\u0634\u062f.",
        "btn_dedup": "\U0001f500 \u0641\u06cc\u0644\u062a\u0631 \u062a\u06a9\u0631\u0627\u0631\u06cc\u200c\u0647\u0627",
        "btn_dedup_on": "\U0001f7e2 \u0641\u06cc\u0644\u062a\u0631 \u062a\u06a9\u0631\u0627\u0631\u06cc\u200c\u0647\u0627: \u0631\u0648\u0634\u0646",
        "btn_dedup_off": "\u26aa \u0641\u06cc\u0644\u062a\u0631 \u062a\u06a9\u0631\u0627\u0631\u06cc\u200c\u0647\u0627: \u062e\u0627\u0645\u0648\u0634",
        "btn_dedup_window": "\u23f1 \u0628\u0627\u0632\u0647 \u0628\u0631\u0631\u0633\u06cc: {min} \u062f\u0642\u06cc\u0642\u0647",
        "btn_dedup_threshold": "\U0001f3af \u0622\u0633\u062a\u0627\u0646\u0647 \u0634\u0628\u0627\u0647\u062a: {pct}\u066a",
        "btn_dedup_minlen": "\u270f\ufe0f \u062d\u062f\u0627\u0642\u0644 \u0637\u0648\u0644: {n} \u06a9\u0627\u0631\u0627\u06a9\u062a\u0631",
        "btn_dedup_window_opt": "{min} \u062f\u0642\u06cc\u0642\u0647",
        "btn_dedup_threshold_opt": "{pct}\u066a",
        "btn_dedup_minlen_opt": "{n} \u06a9\u0627\u0631\u0627\u06a9\u062a\u0631",
        "dedup_title": "\U0001f500 <b>\u0641\u06cc\u0644\u062a\u0631 \u062a\u06a9\u0631\u0627\u0631\u06cc\u200c\u0647\u0627</b>\n\n\u0648\u0636\u0639\u06cc\u062a: <b>{status}</b>\n\n\u0648\u0642\u062a\u06cc \u0631\u0648\u0634\u0646 \u0628\u0627\u0634\u062f\u060c \u067e\u0633\u062a\u06cc \u06a9\u0647 \u0645\u062a\u0646 \u0622\u0646 \u062a\u0642\u0631\u06cc\u0628\u0627\u064b \u0645\u0634\u0627\u0628\u0647 \u0686\u06cc\u0632\u06cc \u0628\u0627\u0634\u062f \u06a9\u0647 \u067e\u06cc\u0634\u200c\u062a\u0631 \u062f\u0631 \u0647\u0645\u0627\u0646 \u06a9\u0627\u0646\u0627\u0644 \u0645\u0646\u062a\u0634\u0631 \u0634\u062f\u0647 \u0646\u0627\u062f\u06cc\u062f\u0647 \u06af\u0631\u0641\u062a\u0647 \u0645\u06cc\u200c\u0634\u0648\u062f \u2014 \u0646\u0633\u062e\u0647 \u0627\u0648\u0644 \u0628\u0631\u0646\u062f\u0647 \u0627\u0633\u062a. \u062f\u0631 \u0645\u0642\u0627\u06cc\u0633\u0647\u060c \u0627\u06cc\u0645\u0648\u062c\u06cc\u060c \u0644\u06cc\u0646\u06a9\u200c\u0647\u0627 \u0648 \u062a\u0641\u0627\u0648\u062a \u0627\u0645\u0644\u0627\u06cc \u0639\u0631\u0628\u06cc/\u0641\u0627\u0631\u0633\u06cc \u0646\u0627\u062f\u06cc\u062f\u0647 \u06af\u0631\u0641\u062a\u0647 \u0645\u06cc\u200c\u0634\u0648\u0646\u062f.\n\n\u2022 \u0628\u0627\u0632\u0647 \u0628\u0631\u0631\u0633\u06cc: <b>{min} \u062f\u0642\u06cc\u0642\u0647</b>\n\u2022 \u0622\u0633\u062a\u0627\u0646\u0647 \u0634\u0628\u0627\u0647\u062a: <b>{pct}\u066a</b>\n\u2022 \u062d\u062f\u0627\u0642\u0644 \u0637\u0648\u0644: <b>{n} \u06a9\u0627\u0631\u0627\u06a9\u062a\u0631</b>",
        "dedup_choose_window": "\u062a\u0627 \u0686\u0646\u062f \u062f\u0642\u06cc\u0642\u0647 \u0642\u0628\u0644 \u0628\u0631\u0627\u06cc \u06cc\u0627\u0641\u062a\u0646 \u062a\u06a9\u0631\u0627\u0631\u06cc\u200c\u0647\u0627 \u0628\u0631\u0631\u0633\u06cc \u0634\u0648\u062f\u061f\n\n<i>\u0641\u0642\u0637 \u067e\u0633\u062a\u200c\u0647\u0627\u06cc N \u062f\u0642\u06cc\u0642\u0647 \u0627\u062e\u06cc\u0631 \u0645\u0642\u0627\u06cc\u0633\u0647 \u0645\u06cc\u200c\u0634\u0648\u0646\u062f.</i>",
        "dedup_choose_threshold": "\u062f\u0648 \u067e\u0633\u062a \u0686\u0642\u062f\u0631 \u0628\u0627\u06cc\u062f \u0634\u0628\u06cc\u0647 \u0628\u0627\u0634\u0646\u062f \u062a\u0627 \u062a\u06a9\u0631\u0627\u0631\u06cc \u0645\u062d\u0633\u0648\u0628 \u0634\u0648\u0646\u062f\u061f\n\n<i>\u0628\u0627\u0644\u0627\u062a\u0631 = \u0633\u062e\u062a\u200c\u06af\u06cc\u0631\u0627\u0646\u0647\u200c\u062a\u0631 (\u0641\u0642\u0637 \u067e\u0633\u062a\u200c\u0647\u0627\u06cc \u062a\u0642\u0631\u06cc\u0628\u0627\u064b \u06cc\u06a9\u0633\u0627\u0646 \u062d\u0630\u0641 \u0645\u06cc\u200c\u0634\u0648\u0646\u062f).</i>",
        "dedup_choose_minlen": "\u06a9\u0648\u062a\u0627\u0647\u200c\u062a\u0631\u06cc\u0646 \u0645\u062a\u0646\u06cc \u06a9\u0647 \u0628\u0631\u0631\u0633\u06cc \u0634\u0648\u062f.\n\n<i>\u067e\u0633\u062a\u200c\u0647\u0627\u06cc \u06a9\u0648\u062a\u0627\u0647\u200c\u062a\u0631 \u0627\u0632 \u0627\u06cc\u0646 \u0647\u0631\u06af\u0632 \u062a\u06a9\u0631\u0627\u0631\u06cc \u062f\u0631 \u0646\u0638\u0631 \u06af\u0631\u0641\u062a\u0647 \u0646\u0645\u06cc\u200c\u0634\u0648\u0646\u062f.</i>",
        "on": "\u0631\u0648\u0634\u0646",
        "off": "\u062E\u0627\u0645\u0648\u0634",
        "btn_status": "\U0001F4CA \u0648\u0636\u0639\u06cc\u062a",
        "userbot_dead_hint": (
            "\U0001F534 <b>\u062c\u0644\u0633\u0647 \u06cc\u0648\u0632\u0631\u0628\u0627\u062a \u0645\u0631\u062f\u0647!</b>\n\n"
            "\u0631\u0634\u062a\u0647 \u062c\u0644\u0633\u0647 \u062d\u0633\u0627\u0628 \u062e\u0648\u0627\u0646\u0646\u062f\u0647 \u0627\u0632 \u062f\u0648 IP \u0645\u062e\u062a\u0644\u0641 "
            "\u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u0634\u062f\u0647 \u0648 \u062a\u0644\u06af\u0631\u0627\u0645 \u0622\u0646 \u0631\u0627 \u0628\u0631\u0627\u06cc \u0647\u0645\u06cc\u0634\u0647 \u0627\u0628\u0637\u0627\u0644 \u06a9\u0631\u062f\u0647. "
            "\u0647\u06cc\u0686 \u067e\u0633\u062a\u06cc \u062a\u0627 \u0632\u0645\u0627\u0646 \u062a\u0635\u0631\u06cc\u062d \u0627\u06cc\u0646 \u0645\u0634\u06a9\u0644 \u0627\u0631\u0633\u0627\u0644 \u0646\u0645\u06cc\u200c\u0634\u0648\u062f.\n\n"
            "<b>\u0631\u0627\u0647 \u062d\u0644:</b>\n"
            "1\uFE0F\u20E3 \u06cc\u06a9 \u0631\u0634\u062a\u0647 \u062c\u0644\u0633\u0647 \u062c\u062f\u06cc\u062f \u0628\u0633\u0627\u0632\u06cc\u062f (gen_session.py).\n"
            "2\uFE0F\u20E3 SESSION_STRING \u0631\u0627 \u062f\u0631 \u0645\u06cc\u0632\u0628\u0627\u0646 \u0645\u06cc\u0632\u0628\u0627\u0646\u06cc \u062e\u0648\u062f \u0628\u0647\u200c\u0631\u0648\u0632\u0631\u0633\u0627\u0646\u06cc \u06a9\u0646\u06cc\u062f.\n"
            "3\uFE0F\u20E3 \u062f\u0648\u0628\u0627\u0631\u0647 \u0627\u0632 \u0646\u0634\u0633\u062a \u06a9\u0646\u06cc\u062f.\n\n"
            "\u0645\u0637\u0645\u0626\u0646 \u0634\u0648\u06cc\u062f \u0641\u0642\u0637 \u06cc\u06a9 \u06a9\u0646\u062a\u06cc\u0646\u0631 \u0628\u0627 \u06cc\u0646 \u062c\u0644\u0633\u0647 \u0627\u062c\u0631\u0627 \u0645\u06cc\u200c\u0634\u0648\u062f\u060c \u0648\u0631\u0646\u0627 \u062f\u0648\u0628\u0627\u0631\u0647 \u0645\u06cc\u0645\u06cc\u0631\u062f."
        ),
        "status_text": (
            "\U0001F4CA <b>\u0648\u0636\u0639\u06cc\u062a \u0631\u0628\u0627\u062a</b>\n\n"
            "\u2022 \u062c\u0644\u0633\u0647 \u06cc\u0648\u0632\u0631\u0628\u0627\u062a: {alive_icon} <b>{alive_word}</b>\n"
            "{err_line}"
            "\u2022 \u0628\u0631\u0631\u0633\u06cc \u062a\u06a9\u0631\u0627\u0631\u06cc: <b>{dedup_checked}</b>\n"
            "\u2022 \u062a\u06a9\u0631\u0627\u0631\u06cc \u0645\u0633\u062f\u0648\u062f: <b>{dedup_dropped}</b>\n"
            "\u2022 \u0645\u0642\u0635\u062f\u0647\u0627\u06cc \u067e\u06cc\u06af\u06cc\u0631\u06cc: <b>{dedup_tracked}</b>"
        ),
        "status_err_line": "\u26A0\uFE0F <i>{err_detail}</i>\n",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in T else "en"
    template = T[lang].get(key) or T["en"].get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template
