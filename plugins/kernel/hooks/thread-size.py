#!/usr/bin/env python3
"""UserPromptSubmit hook (CLAUDE.md, Answer by click, a thread that's too long).

Reads the size of the thread's last model step from its own record: the tokens it read, new and
from cache. Every step rereads the whole thread, so a long thread makes each step cost more. When
the last step passed LIMIT, Claude is told to hand over to a fresh thread the way a full thread
does. Nwani picked 500,000 tokens per step on a card (2026-11-19, up from 200,000).

It adds a line to LOG in Project Files the first time it runs in a thread, so a new thread can check
on its first turn that the hook loaded, and another line each time it fires.
"""
import datetime
import json
import os
import sys

LIMIT = 500000
LOG = os.environ.get("CLAUDE_THREAD_SIZE_LOG", "/mnt/project-files/new-config/thread-size-log.md")


def last_size(path):
    """The tokens the last main-thread step read, or None when the record has none."""
    size = None
    try:
        with open(path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(entry, dict) or entry.get("isSidechain"):
                    continue
                message = entry.get("message")
                if not isinstance(message, dict) or message.get("role") != "assistant":
                    continue
                usage = message.get("usage")
                if not isinstance(usage, dict):
                    continue
                total = sum(usage.get(k) or 0 for k in
                            ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
                if total:
                    size = total
    except OSError:
        return None
    return size


def log(what, hook):
    session = hook.get("session_id") or "unknown"
    try:
        if what == "ran":
            try:
                if "ran, session %s\n" % session in open(LOG).read():
                    return
            except OSError:
                pass
        with open(LOG, "a") as f:
            f.write("- %s UTC: %s, session %s\n" % (
                datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"), what, session))
    except OSError:
        pass


def main():
    hook = json.load(sys.stdin)
    log("ran", hook)
    size = last_size(hook.get("transcript_path") or "")
    if not size or size <= LIMIT:
        return
    log("fired at %s tokens per step" % format(size, ","), hook)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": (
            "This thread's last step read %s tokens, past the %s limit Nwani picked (CLAUDE.md, Answer "
            "by click). Answer this message first if it needs an answer, then hand over without asking, "
            "the way a full thread does: withdraw any open card, write the brief with the task, the open "
            "questions and that card, ask the coordinator for a new thread with exactly the same title, "
            "post its link once it's started, and only then resolve this thread."
            % (format(size, ","), format(LIMIT, ","))),
    }}))


if __name__ == "__main__":
    main()
