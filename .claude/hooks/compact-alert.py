#!/usr/bin/env python3
"""SessionStart hook, matcher "compact" (CLAUDE.md, Answer by click, compaction alert).

Nwani asked on 2026-11-19: "If a thread gets compacted, alert me immediately". When the harness
compacts the thread, this tells Claude to post that alert to Nwani before any other step.
"""
import json
import sys

try:
    data = json.load(sys.stdin)
except ValueError:
    data = {}
if data.get("source") == "compact":
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": (
            "This thread was just compacted: earlier context is now a summary. Nwani asked to be "
            "alerted immediately (2026-11-19). Before any other step, post a message telling Nwani "
            "this thread was compacted, then carry on."),
    }}))
