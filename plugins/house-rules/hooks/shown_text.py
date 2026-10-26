"""The words Nwani will see from a reply, an edit or a widget, for reply-check and review-check.

A widget's words are its stand-in line and every text field of its card. A drawn widget's words are
the text inside its SVG or HTML: tags, styles and scripts are code, not words, so they're skipped,
and words a script writes onto the page at display time aren't seen.
"""
import html
import re

# Card fields that are addresses, settings or ids rather than words Nwani reads.
NOT_WORDS = {"url", "color", "format", "scale", "id", "unit", "kind", "to", "from_account"}
# The parts of a message draft that go to the other person.
DRAFT = {"body", "subject"}
CODE = re.compile(r"<!--.*?-->|<(script|style)\b.*?</\1\s*>", re.S | re.I)
TAG = re.compile(r"<[^>]*>")


def drawn_words(code):
    return html.unescape(TAG.sub("\n", CODE.sub(" ", code)))


def card_words(value, draft, key=None):
    """(words, whether they're draft text for someone else) for each text field."""
    if isinstance(value, str):
        return [] if key in NOT_WORDS else [(value, draft and key in DRAFT)]
    if isinstance(value, dict):
        return [w for k, v in value.items() for w in card_words(v, draft, k)]
    if isinstance(value, list):
        return [w for v in value for w in card_words(v, draft, key)]
    return []


def shown(hook):
    """Returns the parts to check, each as (text, questions allowed), and the widget's heading: its
    stand-in line, title and summary, where one source can cover a whole chart. Message drafts for
    other people can rightly ask them questions, so only their draft text skips the question check."""
    args = hook.get("tool_input") or {}
    if not hook.get("tool_name", "").endswith("post_widget"):
        # Edits of a sent message go through here too, and may name the new text "body".
        return [(args.get("text") or args.get("body") or "", False)], ""
    card = args.get("input") or {}
    heading = "\n".join(str(w) for w in (args.get("text"), card.get("title"), card.get("summary")) if w)
    # Newer threads have no family field, so a drawn widget is known by its widget_code.
    if args.get("family") == "visualize" or isinstance(card.get("widget_code"), str):
        parts = [(args.get("text") or "", False), (card.get("title") or "", False),
                 (drawn_words(card.get("widget_code") or ""), False)]
    else:
        draft = str(args.get("widget", "")).startswith("message_compose")
        parts = [(args.get("text") or "", False)] + card_words(card, draft)
    return [(text, ok) for text, ok in parts if text.strip()], heading
