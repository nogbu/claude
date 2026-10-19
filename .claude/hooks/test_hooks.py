#!/usr/bin/env python3
"""Runs each hook the way the hook runner does and checks every verdict.
Run: python3 .claude/hooks/test_hooks.py"""
import json
import pathlib
import subprocess
import sys
import tempfile

HOOKS = pathlib.Path(__file__).parent


def run(hook, data):
    out = subprocess.run([sys.executable, str(HOOKS / hook)], input=json.dumps(data),
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out) if out else None


def reply_refused(text):
    out = run("reply-check.py", {"tool_input": {"text": text}})
    return bool(out) and out["hookSpecificOutput"]["permissionDecision"] == "deny"


def card_refused(context):
    out = run("card-check.py", {"tool_input": {"question": "Save it", "context": context}})
    return bool(out) and out["hookSpecificOutput"]["permissionDecision"] == "deny"


# A small thread record: posts are (kind, text or card id); "nwani" starts a new turn.
def record(*events):
    lines, n = [], 0
    for kind, value in events:
        n += 1
        tid = "toolu_%d" % n
        if kind == "nwani":
            lines.append({"type": "user", "message": {"content": value}})
            continue
        name = {"card": "mcp__hearthbot__ask_decision", "reply": "mcp__hearthbot__reply",
                "withdraw": "mcp__hearthbot__close_decision", "refused card": "mcp__hearthbot__ask_decision"}[kind]
        args = {"message_id": value} if kind == "withdraw" else {"question": value} if "card" in kind else {"text": value}
        lines.append({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": tid, "name": name, "input": args}]}})
        result = {"type": "tool_result", "tool_use_id": tid,
                  "content": [{"type": "text", "text": json.dumps({"message_id": "cmsg_" + value.replace(" ", "")})}]}
        if kind == "refused card":
            result = {"type": "tool_result", "tool_use_id": tid, "is_error": True, "content": "denied"}
        lines.append({"type": "user", "message": {"content": [result]}})
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    f.write("\n".join(json.dumps(l) for l in lines))
    f.close()
    return f.name


def stopped(path, again=False):
    out = run("open-cards.py", {"transcript_path": path, "stop_hook_active": again})
    return bool(out) and out["decision"] == "block"


REPLIES = [
    # Lines from real replies in the thread that set these rules up (2026-10-19)
    ("That replaces my default for #4. Does it work for you?", True),
    ("3. **Enforcement:** written rules only, or hooks that block actions? [written rules only for now]", True),
    ("You can say \"start a thread for X\" here, or post the request in the project chat.", False),
    ("My \"Does it work for you?\" earlier in this thread would have passed it.", False),
    ("> - Never ask Nwani to paste prompts.\n> Was this right?", False),
    ("Still open: the usage script and checklist; removing claude.old; setup questions 2, 5 and 6.", True),
    ("Still open:\n- The usage script and checklist\n- Removing claude.old", False),
    # Typed answers
    ("Typed answer: what went wrong before, in your words?", False),
    ("**Typed answer:** what went wrong before?", False),
    ("Some context first.\nTyped answer: what went wrong?\nAnd is this ok?", True),
    # Code, quotes and links
    ("Run `ls -la?` to see it.", False),
    ("```\nif x?\n```\nDone.", False),
    ("Open [the thread](https://claude.ai/code/project/x?thread=y).", False),
    ("See https://example.com/page?id=3 for details.", False),
    ("Curly quotes: “why?” is what you asked.", False),
    ("Run `a; b` to see it.", False),
    # Plain questions, semicolons and open lists
    ("Should I save it?", True),
    ("Which one do you want ?", True),
    ("It's saved; nothing else is needed.", True),
    ("**Still open:**\n\n- One item", False),
    ("Still open:\nThe usage script", True),
    ("Still open:", True),
    ("Saved. Nothing else is needed.", False),
    ("", False),
]

CARDS = [("", False), ("   ", False), ("Still open after this: the usage script.", True)]

TURNS = [
    ("no cards at all", record(("nwani", "hi"), ("reply", "hello")), False),
    ("turn ends on a card", record(("nwani", "hi"), ("reply", "here"), ("card", "Save it")), False),
    ("open card, turn ends on a reply",
     record(("card", "Save it"), ("nwani", "a question"), ("reply", "an answer")), True),
    ("open card re-asked",
     record(("card", "Save it"), ("nwani", "a question"), ("reply", "an answer"),
            ("withdraw", "cmsg_Saveit"), ("card", "Save it again")), False),
    ("card answered by tap", record(("card", "Save it"), ("nwani", "Chose Save. decision_id=cmsg_Saveit"),
                                    ("reply", "Saved.")), False),
    ("card withdrawn", record(("card", "Save it"), ("nwani", "drop it"), ("withdraw", "cmsg_Saveit"),
                              ("reply", "Dropped.")), False),
    ("open card, turn posted nothing", record(("card", "Save it"), ("nwani", "thanks")), False),
    ("refused card doesn't count as posted",
     record(("nwani", "hi"), ("reply", "here"), ("refused card", "Save it")), False),
    ("refused card doesn't count as ending on a card",
     record(("card", "Save it"), ("nwani", "a question"), ("reply", "an answer"), ("refused card", "Other")), True),
]

failures = []
for text, want in REPLIES:
    if reply_refused(text) != want:
        failures.append("reply-check, expected %s: %r" % ("refused" if want else "allowed", text))
for context, want in CARDS:
    if card_refused(context) != want:
        failures.append("card-check, expected %s: %r" % ("refused" if want else "allowed", context))
for name, path, want in TURNS:
    if stopped(path) != want:
        failures.append("open-cards, expected %s: %s" % ("stopped" if want else "allowed", name))
if stopped(TURNS[2][1], again=True):
    failures.append("open-cards, expected allowed: second stop in a row")
total = len(REPLIES) + len(CARDS) + len(TURNS) + 1
for failure in failures:
    print("FAIL", failure)
print("%d of %d cases pass" % (total - len(failures), total))
sys.exit(1 if failures else 0)
