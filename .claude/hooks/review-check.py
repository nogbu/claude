#!/usr/bin/env python3
"""PreToolUse hook on thread replies (CLAUDE.md, Review before answering).

Refuses a reply longer than a short acknowledgment unless the reviewer helper ran and finished
since Nwani's last message.
"""
import json
import sys

SHORT = 40  # words; a reply this long or shorter is an acknowledgment and skips review


def reviewed_this_turn(transcript_path):
    asked, done = set(), False
    with open(transcript_path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            content = (entry.get("message") or {}).get("content")
            if entry.get("type") == "user" and isinstance(content, str):
                asked, done = set(), False
            elif entry.get("type") == "assistant" and isinstance(content, list):
                for block in content:
                    args = block.get("input") or {}
                    # A background run returns before the review exists, so only a foreground run counts.
                    if block.get("type") == "tool_use" and block.get("name") == "Agent" \
                            and args.get("subagent_type") == "reviewer" and args.get("run_in_background") is False:
                        asked.add(block.get("id"))
            elif entry.get("type") == "user" and isinstance(content, list):
                for block in content:
                    if block.get("type") == "tool_result" and block.get("tool_use_id") in asked \
                            and not block.get("is_error"):
                        done = True
    return done


def main():
    hook = json.load(sys.stdin)
    text = (hook.get("tool_input") or {}).get("text") or ""
    if len(text.split()) <= SHORT or not hook.get("transcript_path"):
        return
    if not reviewed_this_turn(hook["transcript_path"]):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "This reply needs review first (CLAUDE.md, Review before answering). Run the reviewer "
                "helper (subagent_type \"reviewer\", run_in_background false) with Nwani's message, the "
                "conversation around it and this draft. Fix what it finds, or say it in the reply."),
        }}))


if __name__ == "__main__":
    main()
