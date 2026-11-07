#!/usr/bin/env python3
"""PostToolUse hook (CLAUDE.md, Answer by click).

A thread holds at most 24 attached files. When a reply's file is skipped because the thread is
full, tells Claude to hand the thread over to a new one with the same title and attach the file
there, so Nwani still gets the file to click.
"""
import json
import re
import sys

FULL = re.compile(r"maximum of \d+ attached outputs")


def main():
    hook = json.load(sys.stdin)
    response = json.dumps(hook.get("tool_response") or "")
    if not FULL.search(response):
        return
    skipped = re.findall(r'"(/mnt/project-files/[^"\\]+)', response.replace('\\"', '"'))
    files = ", ".join(sorted(set(skipped))) or "the file this reply tried to attach"
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": (
            "This thread is full, so %s was not attached (CLAUDE.md, Answer by click). Hand the "
            "thread over now, without asking: withdraw any open card, resolve this thread, then ask the "
            "coordinator to start a new thread with exactly this thread's title, briefed with the task in "
            "progress, the open questions and that card, and told to attach %s in its first reply. Once "
            "the coordinator says it has started, post a link to it here." % (files, files)),
    }}))


if __name__ == "__main__":
    main()
