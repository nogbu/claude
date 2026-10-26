#!/usr/bin/env python3
"""Stop hook (CLAUDE.md, Open questions, newest first).

Reads the thread's own record to find cards that were posted and not yet answered or withdrawn.
If any are open and this turn posted something but didn't end on a card, the turn is stopped
once and Claude is told to re-ask the newest open card.
"""
import json
import re
import sys

from nwani import queued_message

# Older threads name the tools reply and ask_decision, newer ones post_message and request_decision.
ASK = {"mcp__hearthbot__ask_decision", "mcp__hearthbot__request_decision"}
CLOSE = "mcp__hearthbot__close_decision"
REPLY = {"mcp__hearthbot__reply", "mcp__hearthbot__post_message"}
CARD_ID = re.compile(r'"message_id"\s*:\s*"(cmsg_\w+)"')
ANSWERED = re.compile(r"decision_id=(cmsg_\w+)")


def result_text(block):
    content = block.get("content")
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return content or ""


def read_record(path):
    """Returns (open card questions, oldest first; this turn's posts, in order)."""
    calls = {}    # tool_use id -> (tool name, card question)
    posted = {}   # card message id -> question, in posting order
    closed = set()
    turn = []     # "reply" or "card" for each post since the last message from Nwani
    with open(path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            content = (entry.get("message") or {}).get("content")
            queued = queued_message(entry)
            if queued:
                closed.update(ANSWERED.findall(queued))
                turn = []
            elif entry.get("type") == "assistant" and isinstance(content, list):
                for block in content:
                    if block.get("type") != "tool_use":
                        continue
                    name, args = block.get("name"), block.get("input") or {}
                    if name in ASK | REPLY:
                        calls[block.get("id")] = (name, args.get("question", ""))
                    elif name == CLOSE and args.get("message_id"):
                        closed.add(args["message_id"])
            elif entry.get("type") == "user" and entry.get("isMeta"):
                continue  # harness notes, like a helper's report, aren't Nwani's messages
            elif entry.get("type") == "user":
                if isinstance(content, str):
                    closed.update(ANSWERED.findall(content))
                    turn = []
                    continue
                for block in content or []:
                    if block.get("type") == "text":
                        closed.update(ANSWERED.findall(block.get("text", "")))
                        turn = []
                    elif block.get("type") == "tool_result" and block.get("tool_use_id") in calls \
                            and not block.get("is_error"):
                        name, question = calls[block["tool_use_id"]]
                        found = CARD_ID.search(result_text(block))
                        if name in ASK and found:
                            posted[found.group(1)] = question
                            turn.append("card")
                        elif name in REPLY:
                            turn.append("reply")
    return [q for card, q in posted.items() if card not in closed], turn


def main():
    hook = json.load(sys.stdin)
    if hook.get("stop_hook_active") or not hook.get("transcript_path"):
        return
    open_cards, turn = read_record(hook["transcript_path"])
    if open_cards and turn and turn[-1] != "card":
        print(json.dumps({"decision": "block", "reason": (
            "A card is still open, so this turn has to end on a card (CLAUDE.md, Open questions, "
            "newest first). Unless this turn already asked a new question, re-ask the newest open "
            "card: withdraw it with close_decision, send a reply ending with a \"Still open:\" "
            "bullet list of the rest, then post it again. Newest open card: \"%s\"" % open_cards[-1])}))


if __name__ == "__main__":
    main()
