#!/usr/bin/env python3
"""PreToolUse hook on thread replies (CLAUDE.md, Answer by click and Lists are bulleted).

After code, quoted lines, text in quotation marks and links are set aside, a reply is refused when:
- a line has a "?" and doesn't start with "Typed answer:"
- it has a semicolon
- a "Still open:" line isn't followed by bullets
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
STILL_OPEN = re.compile(r"^[\s*_]*Still open:[*_]*(.*)$")
BULLET = re.compile(r"^\s*[-*•]\s")


def problem(text):
    for pattern in IGNORED:
        text = pattern.sub(" ", text)
    lines = text.splitlines()
    for line in lines:
        if "?" in line and not TYPED.match(line):
            return ("Questions go on a decision card, not in a reply (CLAUDE.md, Answer by click). "
                    "Found: \"%s\". If only Nwani's own words can answer it, put it on its own line "
                    "starting \"Typed answer:\"." % line.strip()[:120])
    for line in lines:
        if ";" in line:
            return ("No semicolons in replies (CLAUDE.md, Lists are bulleted). Found: \"%s\". "
                    "Put a list of three or more items on bullets, or split the sentence." % line.strip()[:120])
    for i, line in enumerate(lines):
        m = STILL_OPEN.match(line)
        if m:
            rest = [l for l in lines[i + 1:] if l.strip()]
            if m.group(1).strip() or not rest or not BULLET.match(rest[0]):
                return ("Put each item after \"Still open:\" on its own bullet line (CLAUDE.md, "
                        "Lists are bulleted).")
    return None


def main():
    hook = json.load(sys.stdin)
    reason = problem((hook.get("tool_input") or {}).get("text") or "")
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}))


if __name__ == "__main__":
    main()
