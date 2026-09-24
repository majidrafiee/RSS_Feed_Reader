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
        "on": "ON",
        "off": "OFF",
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
        "on": "\u0631\u0648\u0634\u0646",
        "off": "\u062E\u0627\u0645\u0648\u0634",
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
