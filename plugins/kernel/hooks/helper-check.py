#!/usr/bin/env python3
"""PreToolUse hook on Write and Edit (CLAUDE.md, Helpers and skills).

Refuses saving a helper (.claude/agents/*.md) or a skill (.claude/skills/*/SKILL.md) whose header
doesn't name both a model and an effort level, so neither is ever left to a default by accident.
"""
import json
import pathlib
import re
import sys

HELPER = re.compile(r"(^|/)\.claude/(agents/[^/]+\.md|skills/[^/]+/SKILL\.md)$")
HEADER = re.compile(r"\A---\n(.*?)\n---", re.S)


def result(tool, args):
    """The file's text as it would be after this Write or Edit."""
    if tool == "Write":
        return args.get("content") or ""
    path = pathlib.Path(args.get("file_path", ""))
    text = path.read_text() if path.exists() else ""
    old, new = args.get("old_string") or "", args.get("new_string") or ""
    return text.replace(old, new) if args.get("replace_all") else text.replace(old, new, 1)


def main():
    hook = json.load(sys.stdin)
    args = hook.get("tool_input") or {}
    if not HELPER.search(args.get("file_path", "")):
        return
    header = HEADER.match(result(hook.get("tool_name"), args))
    missing = [field for field in ("model", "effort")
               if not (header and re.search(r"^%s:\s*\S" % field, header.group(1), re.M))]
    if missing:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "A helper or skill names its %s in its header (CLAUDE.md, Helpers and skills). "
                "Ask Nwani on a card which to use, then add it." % " and ".join(missing)),
        }}))


if __name__ == "__main__":
    main()
