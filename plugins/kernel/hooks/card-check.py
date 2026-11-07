#!/usr/bin/env python3
"""PreToolUse hook on decision cards (CLAUDE.md, Answer by click).

Refuses a card whose context box is filled in, since the app often doesn't show it.
"""
import json
import sys


def main():
    hook = json.load(sys.stdin)
    if ((hook.get("tool_input") or {}).get("context") or "").strip():
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Leave the card's context empty (CLAUDE.md, Answer by click). Put what Nwani needs "
                "in the reply just before the card, then post the card again without context."),
        }}))


if __name__ == "__main__":
    main()
