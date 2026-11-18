#!/usr/bin/env python3
"""Stop hook (CLAUDE.md, Open questions, newest first).

Reads the thread's own record to find cards that were posted and not yet answered or withdrawn.
If a card posted this turn is open and the turn posted something but didn't end on a card, the turn
is stopped once and Claude is told to re-ask the newest open card. A card from an earlier turn stays
open and answerable without being re-posted, so an off-topic answer can end on a reply (Nwani's Save
card, 2026-11-16). The card can scroll out of view.

It also stops a turn whose reviewer gave the verdict ASK, meaning Nwani's request could mean more
than one thing, until a card goes out after that report or a reply after it says Claude disagreed
and why (CLAUDE.md, Review before answering, 2026-11-11).

With no card open, a turn that posted something can't end on a reply unless Nwani's latest tap was on a
Done option and no card has gone out since, so finished work always gets a Done card (2026-11-15). A
reply asking a "Typed answer:" question, and a turn that resolves the thread or messages the coordinator
(a test thread reporting, or a full thread handing over), are exempt.
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
ASK_VERDICT = re.compile(r"Verdict:?\**:?\s*ASK\b")
DISAGREE = re.compile(r"\bdisagree", re.I)
TAP = re.compile(r'Chose\s+(?:&#34;|"|\u201c)?(\w+)')
TYPED = re.compile(r"^\W*Typed answer:", re.M)
EXEMPT = {"mcp__hearthbot__set_thread_resolved", "mcp__hearthbot__message_coordinator"}


def tapped(text, done):
    """Whether Nwani's latest tap was a Done option, given this message and the state before it."""
    found = TAP.search(text or "")
    if not found or "decision_id=" not in text and "decision card" not in text:
        return done
    return found.group(1).lower() == "done"


def result_text(block):
    content = block.get("content")
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return content or ""


def read_record(path):
    """Returns (open card questions, oldest first; this turn's posts, in order; whether an ASK
    verdict this turn is still unanswered; whether Nwani's latest tap was a Done option with no card
    since; whether this turn resolved the thread or messaged the coordinator)."""
    calls = {}    # tool_use id -> (tool name, card question)
    posted = {}   # card message id -> question, in posting order
    closed = set()
    turn = []     # "reply" or "card" for each post since the last message from Nwani
    turn_no = 0   # counts Nwani's messages, so a card's turn can be told apart from this one
    asking = False  # a reviewer said ASK this turn, and no card or disagreeing reply came after
    done = False    # Nwani's latest tap was on a Done option, and no card has gone out since
    exempt = False  # this turn resolved the thread or messaged the coordinator
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
                turn, asking, exempt, turn_no = [], False, False, turn_no + 1
                done = tapped(queued, done)
            elif entry.get("type") == "assistant" and isinstance(content, list):
                for block in content:
                    if block.get("type") != "tool_use":
                        continue
                    name, args = block.get("name"), block.get("input") or {}
                    if name in ASK | REPLY:
                        calls[block.get("id")] = (name, args.get("question", "") or args.get("text", ""))
                    elif name == "Agent":
                        calls[block.get("id")] = (name, "")
                    elif name == CLOSE and args.get("message_id"):
                        closed.add(args["message_id"])
                    elif name in EXEMPT:
                        exempt = True
            elif entry.get("type") == "user" and entry.get("isMeta"):
                # Harness notes, like a helper's report, aren't Nwani's messages. A reviewer's report
                # coming back can still carry an ASK verdict.
                note = content if isinstance(content, str) else json.dumps(content)
                if ASK_VERDICT.search(note or ""):
                    asking = True
                continue
            elif entry.get("type") == "user":
                if isinstance(content, str):
                    closed.update(ANSWERED.findall(content))
                    turn, asking, exempt, turn_no = [], False, False, turn_no + 1
                    done = tapped(content, done)
                    continue
                for block in content or []:
                    if block.get("type") == "text":
                        closed.update(ANSWERED.findall(block.get("text", "")))
                        turn, asking, exempt, turn_no = [], False, False, turn_no + 1
                        done = tapped(block.get("text", ""), done)
                    elif block.get("type") == "tool_result" and block.get("tool_use_id") in calls \
                            and not block.get("is_error"):
                        name, question = calls[block["tool_use_id"]]
                        found = CARD_ID.search(result_text(block))
                        if name == "Agent":
                            if ASK_VERDICT.search(result_text(block)):
                                asking = True
                        elif name in ASK and found:
                            posted[found.group(1)] = (question, turn_no)
                            turn.append("card")
                            asking, done = False, False
                        elif name in REPLY:
                            turn.append("typed" if TYPED.search(question) else "reply")
                            if DISAGREE.search(question):
                                asking = False
    return [(q, n == turn_no) for card, (q, n) in posted.items() if card not in closed], turn, asking, done, exempt


def main():
    hook = json.load(sys.stdin)
    if hook.get("stop_hook_active") or not hook.get("transcript_path"):
        return
    open_cards, turn, asking, done, exempt = read_record(hook["transcript_path"])
    if asking:
        print(json.dumps({"decision": "block", "reason": (
            "The reviewer's verdict was ASK: Nwani's request could mean more than one thing (CLAUDE.md, "
            "Review before answering). Reread Nwani's words on it first (CLAUDE.md, Answer by click). If "
            "they leave it open, ask which one Nwani meant on a card. If they settle it, send a reply that "
            "says you disagree with the reviewer and why.")}))
        return
    if any(current for _, current in open_cards) and turn and turn[-1] != "card":
        print(json.dumps({"decision": "block", "reason": (
            "A card is still open, so this turn has to end on a card (CLAUDE.md, Open questions, "
            "newest first). Unless this turn already asked a new question: if Nwani hasn't said the "
            "current task is done, end on a card about that task, like asking whether it's done. A thread "
            "started only to run a test reports its results and resolves itself instead. "
            "Only once Nwani has said so, re-ask the newest open card: withdraw it with close_decision, "
            "send a reply ending with a \"Still open:\" bullet list of the rest, then post it again. "
            "Newest open card: \"%s\"" % open_cards[-1][0])}))

    elif not open_cards and turn and turn[-1] == "reply" and not done and not exempt:
        print(json.dumps({"decision": "block", "reason": (
            "No card is open and Nwani hasn't tapped Done, so this turn has to end on a card (CLAUDE.md, "
            "Open questions, newest first). If the work looks finished, ask on a Done card. Otherwise ask "
            "the question this turn leaves open on a card, or a \"Typed answer:\" line if only Nwani's "
            "words can answer it.")}))


if __name__ == "__main__":
    main()
