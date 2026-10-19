#!/usr/bin/env python3
"""Runs each hook the way the hook runner does and checks every verdict.
Run: python3 .claude/hooks/test_hooks.py"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

HOOKS = pathlib.Path(__file__).parent


def run(hook, data, env=None):
    out = subprocess.run([sys.executable, str(HOOKS / hook)], input=json.dumps(data),
                         capture_output=True, text=True, check=True, env=env).stdout
    return json.loads(out) if out else None


def reply_refused(text, transcript=None):
    out = run("reply-check.py", {"tool_input": {"text": text}, "transcript_path": transcript})
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
    # Numbers with units need a source
    ("TPS One: use 5 ml per gallon.", True),
    ("TPS One: use 5 ml per gallon (unverified).", False),
    ("TPS One: use 5 ml per gallon ([label](https://example.com/tps)).", False),
    ("Waiting on the model took 12 min, source: usage report.", False),
    ("Keep it at 65°F.", True),
    ("98% of it came from the cache.", True),
    ("You said \"5 ml\" earlier.", False),
    ("Pick 2 to 4 options, 1 in 5 threads.", False),
]

# Citing a file:line needs that file opened since Nwani's last message
OPENED = record(("nwani", "what's the dose"))
with open(OPENED, "a") as f:
    f.write("\n" + json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file_path": "/repo/learnings.md"}}]}}))
CITES = [
    ("TPS One: 5 ml per gallon (learnings.md:3).", OPENED, False),
    ("TPS One: 5 ml per gallon (projects/plantagram/learnings.md:3).", OPENED, False),
    ("The rule is at CLAUDE.md:7.", OPENED, True),
    ("TPS One: 5 ml per gallon (learnings.md:3).",
     record(("nwani", "earlier"), ("reply", "x"), ("nwani", "now")), True),
]

# The lookup, run against a small set of rules and learnings
ROOT = pathlib.Path(tempfile.mkdtemp())
(ROOT / "CLAUDE.md").write_text("# Rules\n\n- Ask every question on a decision card.\n")
(ROOT / "projects" / "plantagram").mkdir(parents=True)
(ROOT / "projects" / "plantagram" / "learnings.md").write_text(
    "# Learnings\n\n- TPS One dosage: 5 ml per gallon (source: label, confirmed 2026-10-19)\n")
LOOKUPS = [
    ("what's the dosage for tps one", "TPS One dosage"),
    ("Is there a rule about questions in replies", "decision card"),
    ("thanks", None),
]


def looked_up(message):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    out = run("lookup.py", {"prompt": '<wake><message trigger="true">%s</message></wake>' % message}, env)
    return out["hookSpecificOutput"]["additionalContext"] if out else None


GOOD = "---\nname: audit\nmodel: sonnet\neffort: medium\n---\nDo the audit.\n"
HELPERS = [
    ({"file_path": "/r/.claude/agents/audit.md", "content": GOOD}, False),
    ({"file_path": "/r/.claude/agents/audit.md", "content": GOOD.replace("effort: medium\n", "")}, True),
    ({"file_path": "/r/.claude/skills/audit/SKILL.md", "content": "---\nname: audit\n---\nDo it.\n"}, True),
    ({"file_path": "/r/.claude/skills/audit/SKILL.md", "content": "No header at all.\n"}, True),
    ({"file_path": "/r/CLAUDE.md", "content": "No header needed here.\n"}, False),
]


def helper_refused(args, tool="Write"):
    out = run("helper-check.py", {"tool_name": tool, "tool_input": args})
    return bool(out) and out["hookSpecificOutput"]["permissionDecision"] == "deny"


EDITED = pathlib.Path(tempfile.mkdtemp()) / ".claude" / "agents" / "audit.md"
EDITED.parent.mkdir(parents=True)
EDITED.write_text(GOOD)

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
for text, transcript, want in CITES:
    if reply_refused(text, transcript) != want:
        failures.append("reply-check citation, expected %s: %r" % ("refused" if want else "allowed", text))
for message, want in LOOKUPS:
    got = looked_up(message)
    if (want is None and got) or (want and (not got or want not in got)):
        failures.append("lookup, expected %r for %r, got %r" % (want, message, got))
for args, want in HELPERS:
    if helper_refused(args) != want:
        failures.append("helper-check, expected %s: %r" % ("refused" if want else "allowed", args["file_path"]))
if not helper_refused({"file_path": str(EDITED), "old_string": "model: sonnet\n", "new_string": ""}, "Edit"):
    failures.append("helper-check, expected refused: an edit that removes the model")
if helper_refused({"file_path": str(EDITED), "old_string": "Do the audit.", "new_string": "Do it."}, "Edit"):
    failures.append("helper-check, expected allowed: an edit that keeps both")
for context, want in CARDS:
    if card_refused(context) != want:
        failures.append("card-check, expected %s: %r" % ("refused" if want else "allowed", context))
for name, path, want in TURNS:
    if stopped(path) != want:
        failures.append("open-cards, expected %s: %s" % ("stopped" if want else "allowed", name))
if stopped(TURNS[2][1], again=True):
    failures.append("open-cards, expected allowed: second stop in a row")
total = len(REPLIES) + len(CITES) + len(LOOKUPS) + len(HELPERS) + 2 + len(CARDS) + len(TURNS) + 1
for failure in failures:
    print("FAIL", failure)
print("%d of %d cases pass" % (total - len(failures), total))
sys.exit(1 if failures else 0)
