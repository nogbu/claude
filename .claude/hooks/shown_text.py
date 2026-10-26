"""The words Nwani will see from a reply, an edit or a widget, for reply-check and review-check.

A widget's words are its stand-in line and every text field of its card. A drawn widget's words are
the text inside its SVG or HTML: tags, styles and scripts are code, not words, so they're skipped.
"""
import html
import re

# Card fields that are addresses, settings or ids rather than words Nwani reads.
NOT_WORDS = {"url", "color", "format", "scale", "id", "unit", "kind", "to", "from_account"}
CODE = re.compile(r"<!--.*?-->|<(script|style)\b.*?</\1\s*>", re.S | re.I)
TAG = re.compile(r"<[^>]*>")


def drawn_words(code):
    return html.unescape(TAG.sub("\n", CODE.sub(" ", code)))


def card_words(value, key=None):
    if isinstance(value, str):
        return [] if key in NOT_WORDS else [value]
    if isinstance(value, dict):
        return [w for k, v in value.items() for w in card_words(v, k)]
    if isinstance(value, list):
        return [w for v in value for w in card_words(v, key)]
    return []


def shown(hook):
    """Returns the text to check and whether questions are allowed in it. Message drafts for other
    people can rightly ask them questions, so only the question check is skipped for those."""
    args = hook.get("tool_input") or {}
    if not hook.get("tool_name", "").endswith("post_widget"):
        # Edits of a sent message go through here too, and may name the new text "body".
        return args.get("text") or args.get("body") or "", False
    card = args.get("input") or {}
    words = [args.get("text") or ""]
    if args.get("family") == "visualize":
        words += [card.get("title") or "", drawn_words(card.get("widget_code") or "")]
    else:
        words += card_words(card)
    return "\n".join(w for w in words if w.strip()), str(args.get("widget", "")).startswith("message_compose")
