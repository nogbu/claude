#!/usr/bin/env python3
"""Runs each hook the way the hook runner does and checks every verdict.
Run: python3 .claude/hooks/test_hooks.py"""
import json
import re
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
        if kind == "tap mid-turn":
            lines.append({"type": "attachment", "attachment": {"type": "queued_command", "prompt": value}})
            continue
        if kind == "note":
            lines.append({"type": "user", "isMeta": True, "message": {"content": value}})
            continue
        name = {"card": "mcp__hearthbot__ask_decision", "reply": "mcp__hearthbot__reply",
                "withdraw": "mcp__hearthbot__close_decision", "refused card": "mcp__hearthbot__ask_decision",
                "new card": "mcp__hearthbot__request_decision", "new reply": "mcp__hearthbot__post_message"}[kind]
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
    # Lists strung through a sentence
    ("Three are part of it: how a fixed draft gets checked again, retesting lighter repeat reviews, and whether cited files get reopened.", True),
    ("- Setup questions 2, 5 and 6", True),
    ("I add it in both copies, merge it, and send you the file.", True),
    ("Pick red, green, or blue.", True),
    ("Pick red, green or blue.", False),  # missed on purpose: the same shape as the next line
    ("Yes, merged and uploaded.", False),
    ("If it fails, Claude retries and stops.", False),
    ("On Nov 7, 2026, and again on Nov 8.", False),
    ("Unlike the reviewer, it runs on short replies too, and it blocks.", False),
    ("It costs a third as much, but it opened no files and missed a list.", False),
    ("Yes, that's fine.", False),
    ("A list like \"a, b and c\" in quotes is shown, not used.", False),
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
    # One source line just under a recipe table covers its rows
    ("| Amount | Ingredient |\n| --- | --- |\n| 2 tbsp | Cumin |\n\nSource: your steps", False),
    ("| Amount | Ingredient |\n| --- | --- |\n| 2 tbsp | Cumin |\n\nServe hot.\n\nSource: your steps", True),
    ("| Amount | Ingredient |\n| --- | --- |\n| 2 tbsp | Cumin |", True),
    ("| Product | Rate |\n| --- | --- |\n| TPS One | 5 ml |\n\nSource: label", True),
]

# Widgets are checked by the words they show, not their drawing code
DRAWN = ('<style>.a{fill:red;stroke:blue}</style><svg><text class="t">%s</text></svg>'
         '<script>let x = 1; if (x) { go(); }</script>')
WIDGETS = [
    ({"family": "visualize", "text": "A chart.", "input": {"title": "Plan", "widget_code": DRAWN % "Week one"}}, False),
    ({"family": "visualize", "text": "A chart.", "input": {"title": "Plan", "widget_code": DRAWN % "Ready?"}}, True),
    ({"widget": "show_widget", "text": "A chart.", "input": {"title": "Plan", "widget_code": DRAWN % "Week one"}}, False),
    ({"widget": "show_widget", "text": "A chart.", "input": {"title": "Plan", "widget_code": DRAWN % "Fast; cheap"}}, True),
    ({"widget": "step_card_display_v0", "text": "Steps; test.", "input": {"summary": "Test"}}, True),
    ({"family": "visualize", "text": "A chart.", "input": {"title": "Plan", "widget_code": DRAWN % "Salt &amp; pepper"}}, False),
    ({"family": "visualize", "text": "A chart.", "input": {"title": "Plan", "widget_code": DRAWN % "Fast; cheap"}}, True),
    ({"family": "card", "widget": "comparison_card_display_v0", "text": "Two options.",
      "input": {"summary": "Two options", "products": [{"name": "A", "url": "https://x.com/a?b=1;c",
                                                        "attributes": [{"label": "Speed", "value": "fast; cheap"}]}]}}, True),
    ({"family": "card", "widget": "comparison_card_display_v0", "text": "Two options.",
      "input": {"summary": "Two options", "products": [{"name": "A", "url": "https://x.com/a?b=1;c",
                                                        "attributes": [{"label": "Speed", "value": True}]}]}}, False),
    ({"family": "card", "widget": "message_compose_v1", "text": "A draft.",
      "input": {"kind": "email", "to": "a@x.com; b@x.com", "variants": [{"label": "Ask", "body": "Are you free Tuesday?"}]}}, False),
    ({"family": "card", "widget": "message_compose_v1", "text": "A draft.",
      "input": {"kind": "email", "variants": [{"label": "Ask", "body": "Hi; are you free"}]}}, True),
    ({"family": "card", "widget": "message_compose_v1", "text": "Which one should I send?",
      "input": {"kind": "email", "variants": [{"label": "Ask", "body": "Are you free Tuesday?"}]}}, True),
    ({"family": "card", "widget": "writing_draft_v0", "text": "A draft.", "input": {"body": "Should we go?"}}, True),
    ({"family": "visualize", "text": "Sales by crop.", "input": {"title": "Sales",
      "widget_code": "<svg><text>Rice 40%</text><text>Beans 60%</text></svg>"}}, True),
    ({"family": "visualize", "text": "Sales by crop, source: sales.csv.", "input": {"title": "Sales",
      "widget_code": "<svg><text>Rice 40%</text><text>Beans 60%</text></svg>"}}, False),
    ({"family": "card", "widget": "chart_display_v0", "text": "Weekly sales.",
      "input": {"title": "Sales (unverified)", "series": [{"name": "Rice 40%", "values": [1, 2]}], "style": "bar"}}, False),
    ({"family": "card", "widget": "step_card_display_v0", "text": "Steps. Ready?", "input": {"summary": "Steps"}}, True),
    ({"family": "card", "widget": "recipe_display_v0", "text": "A recipe.",
      "input": {"title": "Rice", "ingredients": [{"id": "0001", "name": "rice", "amount": 200, "unit": "g"}],
                "steps": [{"id": "1", "title": "Cook", "content": "Simmer for 15 min."}]}}, True),
]


def widget_refused(args, hook="reply-check.py"):
    out = run(hook, {"tool_name": "mcp__hearthbot__post_widget", "tool_input": args, "transcript_path": None})
    return bool(out) and out["hookSpecificOutput"]["permissionDecision"] == "deny"


# Citing a file:line needs that file opened since Nwani's last message
OPENED = record(("nwani", "what's the dose"))
with open(OPENED, "a") as f:
    f.write("\n" + json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file_path": "/repo/learnings.md"}}]}}))
OPENED_THEN_NOTE = record(("nwani", "what's the dose"))
with open(OPENED_THEN_NOTE, "a") as f:
    f.write("\n" + json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file_path": "/repo/learnings.md"}}]}}))
    f.write("\n" + json.dumps({"type": "user", "isMeta": True, "message": {"content": "a helper's report"}}))

OPENED_THEN_NWANI = record(("nwani", "what's the dose"))
with open(OPENED_THEN_NWANI, "a") as f:
    f.write("\n" + json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file_path": "/repo/learnings.md"}}]}}))
    f.write("\n" + json.dumps({"type": "attachment", "attachment": {"type": "queued_command",
                                "prompt": '<wake><message from="human">and the other one</message></wake>'}}))

CITES = [
    ("TPS One: 5 ml per gallon (learnings.md:3).", OPENED_THEN_NWANI, True),
    ("TPS One: 5 ml per gallon (learnings.md:3).", OPENED_THEN_NOTE, False),
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
SEVERAL = pathlib.Path(tempfile.mkdtemp())
(SEVERAL / "claude").mkdir()
(SEVERAL / "claude" / "CLAUDE.md").write_text("# Rules\n\n- Ask every question on a decision card.\n")
(SEVERAL / "claude" / "learnings.md").write_text("# Learnings\n\n- Pothos light: bright indirect (source: tag)\n")
(SEVERAL / "notes").mkdir()
(SEVERAL / "notes" / "learnings.md").write_text("- Pothos water: weekly (source: none)\n")

LOOKUPS = [
    ("what's the dosage for tps one", "TPS One dosage"),
    ("Is there a rule about questions in replies", "decision card"),
    ("thanks", None),
]


def looked_up(message, root=ROOT):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
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
    ("a helper's report mid-turn doesn't reset the turn",
     record(("card", "Save it"), ("nwani", "a question"), ("reply", "an answer"), ("note", "report")), True),
    ("newer tool names: open card, turn ends on a reply",
     record(("new card", "Save it"), ("nwani", "a question"), ("new reply", "an answer")), True),
    ("newer tool names: turn ends on a card",
     record(("nwani", "hi"), ("new reply", "here"), ("new card", "Save it")), False),
    ("card answered by a tap that arrived mid-turn",
     record(("card", "Save it"), ("nwani", "a question"), ("reply", "working"),
            ("tap mid-turn", '<wake><message from="human">Chose Save</message><system-note>decision_id=cmsg_Saveit'
                             '</system-note></wake>'), ("reply", "Saved.")), False),
    ("a helper's mid-turn report quoting a card's id doesn't answer it",
     record(("card", "Save it"), ("nwani", "a question"), ("reply", "working"),
            ("tap mid-turn", '<agent-message from="a1">It said decision_id=cmsg_Saveit</agent-message>'),
            ("reply", "Saved.")), True),
    ("Nwani's mid-turn message starts a new turn",
     record(("card", "Save it"), ("nwani", "a question"), ("reply", "working"), ("card", "Save it again"),
            ("tap mid-turn", '<wake><message from="human">one more thing</message></wake>'), ("reply", "ok")), True),
    ("refused card doesn't count as posted",
     record(("nwani", "hi"), ("reply", "here"), ("refused card", "Save it")), False),
    ("refused card doesn't count as ending on a card",
     record(("card", "Save it"), ("nwani", "a question"), ("reply", "an answer"), ("refused card", "Other")), True),
]

def reviewed(*events):
    """A thread record for review-check: "nwani" starts a turn, "review" runs the reviewer and gets its
    report, "background review" only launches it, "report back" is the launched reviewer's report
    arriving, "failed review" errors, "other helper" runs a different helper."""
    lines = []
    for n, kind in enumerate(events):
        if kind == "nwani":
            lines.append({"type": "user", "message": {"content": "<wake>a question</wake>"}})
            continue
        if kind == "nwani mid-turn":
            lines.append({"type": "attachment", "attachment": {"type": "queued_command",
                          "prompt": '<wake><message from="human">one more thing</message></wake>'}})
            continue
        if kind in ("report back", "named report back"):
            sender = {"from": "review-1", "senderTaskId": "a1"} if kind.startswith("named") else {"from": "a1"}
            lines.append({"type": "user", "isMeta": True, "origin": dict(handback=True, **sender),
                          "message": {"content": "Another Claude session sent a message"}})
            continue
        kind_name = {"other helper": "Explore", "plugin review": "kernel:reviewer"}.get(kind, "reviewer")
        args = {"subagent_type": kind_name, "prompt": "draft"}
        text = "Async agent launched successfully.\nagentId: a1" if kind == "background review" else "Verdict: PASS"
        lines.append({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "toolu_%d" % n, "name": "Agent", "input": args}]}})
        lines.append({"type": "user", "message": {"content": [
            {"type": "tool_result", "tool_use_id": "toolu_%d" % n, "is_error": kind == "failed review",
             "content": [{"type": "text", "text": text}]}]}})
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    f.write("\n".join(json.dumps(l) for l in lines))
    f.close()
    return f.name


LONG = " ".join(["word"] * 41)
REVIEWS = [
    ("short reply, no review", "Saving now.", reviewed("nwani"), False),
    ("40 words, no review", " ".join(["word"] * 40), reviewed("nwani"), False),
    ("long reply, no review", LONG, reviewed("nwani"), True),
    ("long reply, reviewed this turn", LONG, reviewed("nwani", "review"), False),
    ("long reply, reviewed last turn only", LONG, reviewed("nwani", "review", "nwani"), True),
    ("long reply, background review not back yet", LONG, reviewed("nwani", "background review"), True),
    ("long reply, background review came back", LONG, reviewed("nwani", "background review", "report back"), False),
    ("long reply, named background review came back", LONG,
     reviewed("nwani", "background review", "named report back"), False),
    ("long reply, a report back from an earlier turn", LONG,
     reviewed("nwani", "background review", "nwani", "report back"), True),
    ("long reply, review failed", LONG, reviewed("nwani", "failed review"), True),
    ("long reply, a different helper ran", LONG, reviewed("nwani", "other helper"), True),
    ("long reply, reviewed by the plugin's helper", LONG, reviewed("nwani", "plugin review"), False),
    ("long reply, reviewed before Nwani's mid-turn message", LONG, reviewed("nwani", "review", "nwani mid-turn"), True),
    ("long reply, reviewed after Nwani's mid-turn message", LONG, reviewed("nwani", "nwani mid-turn", "review"), False),
]


def review_refused(text, transcript):
    out = run("review-check.py", {"tool_input": {"text": text}, "transcript_path": transcript})
    return bool(out) and out["hookSpecificOutput"]["permissionDecision"] == "deny"


failures = []
for text, want in REPLIES:
    if reply_refused(text) != want:
        failures.append("reply-check, expected %s: %r" % ("refused" if want else "allowed", text))
for text, transcript, want in CITES:
    if reply_refused(text, transcript) != want:
        failures.append("reply-check citation, expected %s: %r" % ("refused" if want else "allowed", text))
got = looked_up("how much light does pothos need", SEVERAL)
if not got or "claude/learnings.md:3" not in got or "Pothos water" in got:
    failures.append("lookup, expected only the repo's line when the thread starts above its repos, got %r" % got)
for message, want in LOOKUPS:
    got = looked_up(message)
    if (want is None and got) or (want and (not got or want not in got)):
        failures.append("lookup, expected %r for %r, got %r" % (want, message, got))
# The new-project check, against a repo with one project folder and one project listed as needing none
NEW = pathlib.Path(tempfile.mkdtemp())
(NEW / "claude" / "checklists").mkdir(parents=True)
(NEW / "claude" / "checklists" / "review.md").write_text("1. Check it.\n")
(NEW / "claude" / "projects" / "nosh").mkdir(parents=True)
(NEW / "claude" / "projects" / "no-folder.md").write_text("# None\n\n- admin: shared rules (2026-11-07)\n")
FIRST = '<session-context nonce="1">\n## Where you are\n\nProject: "%s" (id: `chan_1`)\n</session-context nonce="1">\n<wake reason="spawn"><project id="chan_1" name="%s" type="project"><message trigger="true">hi</message></project></wake>'
NEW_PROJECTS = [
    (FIRST % ("3D Printing", "3D Printing"), "projects/3d-printing"),
    (FIRST % ("nosh", "nosh"), None),
    (FIRST % ("Nosh", "Nosh"), None),
    (FIRST % ("admin", "admin"), None),
    ('<wake reason="mention"><project id="chan_1" name="3dp" type="project"><message trigger="true">hi</message></project></wake>', None),
]
for prompt, want in NEW_PROJECTS:
    out = run("new-project.py", {"prompt": prompt}, dict(os.environ, CLAUDE_PROJECT_DIR=str(NEW)))
    got = out["hookSpecificOutput"]["additionalContext"] if out else None
    if (want is None and got) or (want and (not got or want not in got)):
        failures.append("new-project, expected %r, got %r" % (want, got))
FULL_REPLY = {"ok": True, "note": "attached_outputs_skipped_refs were not attached: the thread already has the maximum of 24 attached outputs.", "attached_outputs_skipped_refs": ["/mnt/project-files/kernel-plugin/kernel_rev3.plugin"]}
ATTACHES = [
    (FULL_REPLY, "kernel_rev3.plugin"),
    (json.dumps(FULL_REPLY), "kernel_rev3.plugin"),
    ({"message_id": "cmsg_1", "thread_id": "cmsg_2"}, None),
]
for response, want in ATTACHES:
    out = run("attach-limit.py", {"tool_name": "mcp__hearthbot__reply", "tool_response": response})
    got = out["hookSpecificOutput"]["additionalContext"] if out else None
    if (want is None and got) or (want and (not got or want not in got)):
        failures.append("attach-limit, expected %r, got %r" % (want, got))
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
for name, text, path, want in REVIEWS:
    if review_refused(text, path) != want:
        failures.append("review-check, expected %s: %s" % ("refused" if want else "allowed", name))
if stopped(TURNS[2][1], again=True):
    failures.append("open-cards, expected allowed: second stop in a row")
for args, want in WIDGETS:
    if widget_refused(args) != want:
        failures.append("reply-check widget, expected %s: %r" % ("refused" if want else "allowed", args))
LONG_WIDGET = {"family": "card", "widget": "writing_draft_v0", "text": "A draft.", "input": {"body": LONG}}
out = run("review-check.py", {"tool_name": "mcp__hearthbot__post_widget", "tool_input": LONG_WIDGET,
                              "transcript_path": reviewed("nwani")})
if not (out and out["hookSpecificOutput"]["permissionDecision"] == "deny"):
    failures.append("review-check, expected refused: a long widget with no review")
out = run("review-check.py", {"tool_name": "mcp__hearthbot__post_widget", "tool_input": LONG_WIDGET,
                              "transcript_path": reviewed("nwani", "review")})
if out:
    failures.append("review-check, expected allowed: a long widget reviewed this turn")
# Edits of a sent message: the matcher must cover both names, and an edit naming its text "body" is still read.
matchers = [g["matcher"] for g in json.loads((HOOKS.parent / "settings.json").read_text())["hooks"]["PreToolUse"]
            if "reply-check.py" in json.dumps(g)]
for name in ("reply", "post_message", "update_message", "edit_message", "post_widget"):
    if not any(re.fullmatch(m, "mcp__hearthbot__" + name) for m in matchers):
        failures.append("settings, expected the reply checks to match mcp__hearthbot__" + name)
out = run("reply-check.py", {"tool_input": {"message_id": "cmsg_1", "body": "Done; saved."}})
if not (out and out["hookSpecificOutput"]["permissionDecision"] == "deny"):
    failures.append("reply-check, expected refused: an edit whose text is called body")
# Saves to main: Nwani's newest message since the last save must be a Save tap or typed words.
def wake(body):
    return '<wake reason="x"><project><thread><message trigger="true" from="human" trust="principal">%s</message></thread></project></wake>' % body
TAPPED_SAVE = wake("Chose &#34;Save it&#34; on the decision card asking &#34;Save the check&#34;")
TAPPED_CHANGE = wake("Chose &#34;Change&#34; on the decision card asking &#34;Save the check&#34;")
TYPED = wake("yes save it")
MERGE = {"name": "mcp__github__merge_pull_request", "input": {"owner": "nogbu", "repo": "claude", "pullNumber": 30}}
def saves(*events):
    lines, n = [], 0
    for kind, value in events:
        n += 1
        if kind == "nwani":
            lines.append({"type": "user", "message": {"content": value}})
        elif kind == "tap mid-turn":
            lines.append({"type": "attachment", "attachment": {"type": "queued_command", "prompt": value}})
        elif kind == "note":
            lines.append({"type": "user", "isMeta": True, "message": {"content": value}})
        elif kind in ("save", "failed save"):
            lines.append({"type": "assistant", "message": {"content": [dict(value, type="tool_use", id="t%d" % n)]}})
            lines.append({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t%d" % n,
                                                                   "is_error": kind == "failed save", "content": "ok"}]}})
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    f.write("\n".join(json.dumps(l) for l in lines))
    f.close()
    return f.name
OTHER = tempfile.mkdtemp()
subprocess.run(["git", "init", "-q", "-b", "main", OTHER], check=True)
subprocess.run(["git", "-C", OTHER, "remote", "add", "origin", "https://github.com/nogbu/claude.old"], check=True)
OURS = tempfile.mkdtemp()
subprocess.run(["git", "init", "-q", "-b", "main", OURS], check=True)
subprocess.run(["git", "-C", OURS, "remote", "add", "origin", "https://github.com/nogbu/claude"], check=True)
subprocess.run(["git", "-C", OURS, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "start"], check=True)
SAVES = [
    ("merge after a Save tap", MERGE, saves(("nwani", TAPPED_SAVE)), False),
    ("merge after typed words", MERGE, saves(("nwani", TYPED)), False),
    ("merge after a Change tap", MERGE, saves(("nwani", TAPPED_CHANGE)), True),
    ("merge with no message from Nwani", MERGE, saves(("note", "a helper's report")), True),
    ("second merge after one Save tap", MERGE, saves(("nwani", TAPPED_SAVE), ("save", MERGE)), True),
    ("merge after a failed merge", MERGE, saves(("nwani", TAPPED_SAVE), ("failed save", MERGE)), False),
    ("merge after a Save tap mid-turn", MERGE, saves(("tap mid-turn", TAPPED_SAVE)), False),
    ("Change tap after a Save tap", MERGE, saves(("nwani", TAPPED_SAVE), ("nwani", TAPPED_CHANGE)), True),
    ("merge in another repo", {"name": MERGE["name"], "input": {"owner": "nogbu", "repo": "claude.old"}}, saves(), False),
    ("file written to main", {"name": "mcp__github__push_files", "input": {"owner": "nogbu", "repo": "claude", "branch": "main"}}, saves(), True),
    ("file written to a branch", {"name": "mcp__github__push_files", "input": {"owner": "nogbu", "repo": "claude", "branch": "claude/x"}}, saves(), False),
    ("git push to main", {"name": "Bash", "input": {"command": "cd %s && git push origin main" % OURS}}, saves(), True),
    ("git push HEAD:main", {"name": "Bash", "input": {"command": "git -C %s push -u origin HEAD:main" % OURS}}, saves(), True),
    ("bare git push on main", {"name": "Bash", "input": {"command": "cd %s && git push" % OURS}}, saves(), True),
    ("git push to a branch", {"name": "Bash", "input": {"command": "cd %s && git push -u origin claude/x" % OURS}}, saves(), False),
    ("git push in another repo", {"name": "Bash", "input": {"command": "cd %s && git push origin main" % OTHER}}, saves(), False),
    ("git push to main after a Save tap", {"name": "Bash", "input": {"command": "cd %s && git push origin main" % OURS}}, saves(("nwani", TAPPED_SAVE)), False),
    ("other shell command", {"name": "Bash", "input": {"command": "git log main"}}, saves(), False),
    ("search for the words git push", {"name": "Bash", "input": {"command": 'cd %s && grep -n "git push origin main" MANUAL.md' % OURS}}, saves(), False),
    ("git push from a folder that isn't a repo", {"name": "Bash", "input": {"command": "cd /nonexistent && git push origin main"}}, saves(), False),
    ("git push origin HEAD on main", {"name": "Bash", "input": {"command": "cd %s && git push -u origin HEAD" % OURS}}, saves(), True),
    ("gh pr merge here", {"name": "Bash", "input": {"command": "gh pr merge 30 --squash"}}, saves(), True),
    ("gh pr merge in another repo", {"name": "Bash", "input": {"command": "gh pr merge 5 -R someone/else"}}, saves(), False),
    ("merge after a harmless command that mentions git push", MERGE, saves(("nwani", TAPPED_SAVE), ("save", {"name": "Bash", "input": {"command": 'grep "git push" x'}})), False),
]
for name, call, path, want in SAVES:
    out = run("save-check.py", {"tool_name": call["name"], "tool_input": call["input"], "transcript_path": path, "cwd": OURS})
    got = bool(out) and out["hookSpecificOutput"]["permissionDecision"] == "deny"
    if got != want:
        failures.append("save-check, expected %s: %s" % ("refused" if want else "allowed", name))
total = len(REPLIES) + len(CITES) + len(LOOKUPS) + len(HELPERS) + 2 + len(CARDS) + len(TURNS) + len(REVIEWS) + 2 + 6 + len(WIDGETS) + 2 + len(NEW_PROJECTS) + len(ATTACHES) + len(SAVES)
for failure in failures:
    print("FAIL", failure)
print("%d of %d cases pass" % (total - len(failures), total))
sys.exit(1 if failures else 0)
