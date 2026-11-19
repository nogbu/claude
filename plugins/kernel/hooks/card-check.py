#!/usr/bin/env python3
"""PreToolUse hook on decision cards (CLAUDE.md, Answer by click).

Refuses a card whose context box is filled in, since the app often doesn't show it.

Also refuses a card unless the newest post this turn is a reply that has already gone through, so a
card can't reach Nwani before the reply that explains it. A reply sent in the same step as the card
has no result yet, so that card is refused whether or not this hook can see the reply. Nwani picked
testing this before saving it (card, 2026-11-19).
"""
import json
import sys

from nwani import queued_message

REPLIES = {"mcp__hearthbot__reply", "mcp__hearthbot__post_message"}
CARDS = {"mcp__hearthbot__ask_decision", "mcp__hearthbot__request_decision"}


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


def newest_post(path, this_card):
    """(kind, outcome) of the newest reply or card this turn, before this card. outcome is "sent",
    "refused" or "waiting" (no result yet, as when it went out in the same step). None when the turn
    has no post yet."""
    posts, results = [], {}
    with open(path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if not isinstance(entry, dict):
                continue
            content = (entry.get("message") or {}).get("content")
            if (entry.get("type") == "user" and isinstance(content, str) and not entry.get("isMeta")) \
                    or queued_message(entry):
                posts, results = [], {}
            elif entry.get("type") == "assistant" and isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict) or block.get("type") != "tool_use" or block.get("id") == this_card:
                        continue
                    if block.get("name") in REPLIES:
                        posts.append(("reply", block.get("id")))
                    elif block.get("name") in CARDS:
                        posts.append(("card", block.get("id")))
            elif entry.get("type") == "user" and isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        results[block.get("tool_use_id")] = "refused" if block.get("is_error") else "sent"
    # A card that was refused never reached Nwani, so the post before it still counts.
    posts = [(kind, tid) for kind, tid in posts if not (kind == "card" and results.get(tid) == "refused")]
    if not posts:
        return None
    kind, tid = posts[-1]
    return kind, results.get(tid, "waiting")


def main():
    hook = json.load(sys.stdin)
    if ((hook.get("tool_input") or {}).get("context") or "").strip():
        deny("Leave the card's context empty (CLAUDE.md, Answer by click). Put what Nwani needs "
             "in the reply just before the card, then post the card again without context.")
        return
    path = hook.get("transcript_path")
    if not path:
        return
    try:
        newest = newest_post(path, hook.get("tool_use_id"))
    except OSError:
        return
    if newest == ("reply", "sent"):
        return
    why = {
        None: "nothing has been posted this turn",
        ("reply", "waiting"): "the reply before it hasn't gone through yet, as when both go out in the same step",
        ("reply", "refused"): "the reply before it was refused",
    }.get(newest, "the newest post this turn is a card, not a reply")
    deny("A card goes out only after the reply just before it has gone through (CLAUDE.md, Answer by click), "
         "and %s. Post the reply on its own, and once it's through, post the card in the next step." % why)


if __name__ == "__main__":
    main()
