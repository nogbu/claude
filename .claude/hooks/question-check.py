#!/usr/bin/env python3
"""PreToolUse hook on thread replies (CLAUDE.md, Answer by click).

Refuses a reply that still has a "?" after code, quoted lines, text in
quotation marks and links are set aside, unless that line starts with
"Typed answer:". Questions go on a decision card instead.
"""
import json
import re
import sys

IGNORED = [
    re.compile(r"```.*?```", re.S),          # code blocks
    re.compile(r"`[^`\n]*`"),                # inline code
    re.compile(r"^\s*>.*$", re.M),           # quoted lines
    re.compile(r'"[^"\n]*"'),                # "straight quotes"
    re.compile(r"“[^”\n]*”"),                # “curly quotes”
    re.compile(r"\]\([^)\s]*\)"),            # markdown link targets
    re.compile(r"https?://\S+"),             # bare links
]
TYPED = re.compile(r"^[\s*_]*Typed answer:")


def question_line(text):
    for pattern in IGNORED:
        text = pattern.sub(" ", text)
    for line in text.splitlines():
        if "?" in line and not TYPED.match(line):
            return line.strip()
    return None


def main():
    hook = json.load(sys.stdin)
    line = question_line((hook.get("tool_input") or {}).get("text") or "")
    if line:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Questions go on a decision card, not in a reply (CLAUDE.md, Answer by click). "
                "Found: \"%s\". If only Nwani's own words can answer it, put it on its own line "
                "starting \"Typed answer:\"." % line[:120]),
        }}))


if __name__ == "__main__":
    main()
