#!/usr/bin/env python3
"""Runs question-check.py the way the hook runner does and checks each verdict.
Run: python3 .claude/hooks/test_question_check.py"""
import json
import pathlib
import subprocess
import sys

HOOK = pathlib.Path(__file__).with_name("question-check.py")

# (reply text, refused?)
CASES = [
    # Lines from real replies in the thread that set this rule up (2026-10-19)
    ("That replaces my default for #4. Does it work for you?", True),
    ("3. **Enforcement:** written rules only, or hooks that block actions? [written rules only for now]", True),
    ("You can say \"start a thread for X\" here, or post the request in the project chat.", False),
    ("My \"Does it work for you?\" earlier in this thread would have passed it.", False),
    ("> - Never ask Nwani to paste prompts.\n> Was this right?", False),
    # Typed answers
    ("Typed answer: what went wrong before, in your words?", False),
    ("**Typed answer:** what went wrong before?", False),
    ("Some context first.\nTyped answer: what went wrong?\nAnd is this ok?", True),
    # Code and links
    ("Run `ls -la?` to see it.", False),
    ("```\nif x?\n```\nDone.", False),
    ("Open [the thread](https://claude.ai/code/project/x?thread=y).", False),
    ("See https://example.com/page?id=3 for details.", False),
    ("Curly quotes: “why?” is what you asked.", False),
    # Plain questions
    ("Should I save it?", True),
    ("Which one do you want ?", True),
    ("Saved. Nothing else is needed.", False),
    ("", False),
]


def refused(text):
    hook_input = {"tool_name": "mcp__hearthbot__reply", "tool_input": {"text": text}}
    out = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(hook_input),
                         capture_output=True, text=True, check=True).stdout
    return bool(out) and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"


failures = [(text, want) for text, want in CASES if refused(text) != want]
for text, want in failures:
    print("FAIL (expected %s): %r" % ("refused" if want else "allowed", text))
print("%d of %d cases pass" % (len(CASES) - len(failures), len(CASES)))
sys.exit(1 if failures else 0)
