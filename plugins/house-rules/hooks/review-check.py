#!/usr/bin/env python3
"""PreToolUse hook on thread replies (CLAUDE.md, Review before answering).

Refuses a reply longer than a short acknowledgment unless the reviewer helper ran and finished
since Nwani's last message.
"""
import json
import re
import sys

SHORT = 40  # words; a reply this long or shorter is an acknowledgment and skips review
AGENT_ID = re.compile(r"agentId: (\w+)")


def result_text(block):
    content = block.get("content")
    if isinstance(content, list):
        return " ".join(part.get("text", "") for part in content if isinstance(part, dict))
    return content or ""


def reviewed_this_turn(transcript_path):
    """True once a reviewer's report exists since Nwani's last message. A reviewer that runs in the
    background returns right away, so it only counts once its report comes back."""
    asked, waiting, done = set(), set(), False
    with open(transcript_path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            content = (entry.get("message") or {}).get("content")
            if entry.get("type") == "user" and entry.get("isMeta"):
                # Harness notes, like a helper's report coming back, aren't Nwani's messages.
                origin = entry.get("origin") or {}
                if origin.get("handback") and (origin.get("senderTaskId") or origin.get("from")) in waiting:
                    done = True
            elif entry.get("type") == "user" and isinstance(content, str):
                asked, waiting, done = set(), set(), False
            elif entry.get("type") == "assistant" and isinstance(content, list):
                for block in content:
                    # The repo's own helper is "reviewer"; the plugin's copy is "house-rules:reviewer".
                    kind = str((block.get("input") or {}).get("subagent_type") or "")
                    if block.get("type") == "tool_use" and block.get("name") == "Agent" \
                            and kind.split(":")[-1] == "reviewer":
                        asked.add(block.get("id"))
            elif entry.get("type") == "user" and isinstance(content, list):
                for block in content:
                    if block.get("type") == "tool_result" and block.get("tool_use_id") in asked \
                            and not block.get("is_error"):
                        text = result_text(block)
                        if text.lstrip().startswith("Async agent launched"):
                            waiting.update(AGENT_ID.findall(text))
                        else:
                            done = True
    return done


def main():
    hook = json.load(sys.stdin)
    args = hook.get("tool_input") or {}
    text = args.get("text") or args.get("body") or ""  # edits may call it "body"
    if len(text.split()) <= SHORT or not hook.get("transcript_path"):
        return
    if not reviewed_this_turn(hook["transcript_path"]):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "This reply needs review first (CLAUDE.md, Review before answering). Run the reviewer "
                "helper (subagent_type \"house-rules:reviewer\", or \"reviewer\" where the repo's own "
                "helper loads) with Nwani's message, the "
                "conversation around it and this draft, and wait for its report. Fix what it finds, or say it in "
                "the reply."),
        }}))


if __name__ == "__main__":
    main()
