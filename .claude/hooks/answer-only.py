#!/usr/bin/env python3
"""PreToolUse hook (CLAUDE.md, Optimize: a question gets only an answer).

When every sentence of Nwani's newest message is a question, refuses the steps that change things, until Nwani
writes again:
- file edits (Write, Edit, NotebookEdit, and shell commands that write files)
- commits, pushes and merges, by git or through GitHub
- helpers other than the reviewer

It uses lookup.py's sentence test (Nwani, 2026-11-17): a sentence ending in "?" is a question, and
one that could be either counts as a question, so "can you fix X" waits for Nwani's next message
unless Claude offers the step on a one-tap card. A message with any request sentence lets edits through. A shell write hidden inside a script isn't seen (Nwani's Save card, 2026-11-16).
"""
import html
import json
import re
import sys

from lookup import is_question
from nwani import queued_message

NWANI = re.compile(r'<message\b(?=[^>]*\btrigger="true")(?=[^>]*\bfrom="human")[^>]*>(.*?)</message>', re.S)
EDITS = {"Write", "Edit", "NotebookEdit", "MultiEdit"}
GITHUB = {"mcp__github__push_files", "mcp__github__create_or_update_file", "mcp__github__delete_file",
          "mcp__github__merge_pull_request", "mcp__github__create_pull_request", "mcp__github__create_branch",
          "mcp__github__update_pull_request_branch"}
REVIEWERS = {"reviewer", "kernel:reviewer"}
# Quoted text is masked first, so a search for the words "git push" isn't counted.
QUOTED = re.compile(r"""(["'])(?:\\.|(?!\1).)*?\1""", re.S)
SHELL_CHANGE = re.compile(
    r"\bgit\b[^|;&\n]*?\s(?:commit|push|merge|rebase|reset|cherry-pick|revert|am|apply)\b"
    r"|\bgh\s+pr\s+(?:create|merge)\b"
    r"|\bsed\s+(?:-\w+\s+)*-i|\bperl\s+-\w*i|\btee\b|\bmv\s|\brm\s|\bcp\s|\btouch\s|\bmkdir\s"
    r"|(?<![0-9&])>>?\s*(?!/dev/)[^\s&|]")


def newest_message(path):
    newest = None
    try:
        with open(path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                texts = []
                queued = queued_message(entry)
                if queued:
                    texts.append(queued)
                content = (entry.get("message") or {}).get("content")
                if entry.get("type") == "user" and not entry.get("isMeta") and not entry.get("isCompactSummary"):
                    if isinstance(content, str):
                        texts.append(content)
                    for block in content if isinstance(content, list) else []:
                        if block.get("type") == "text":
                            texts.append(block.get("text", ""))
                for text in texts:
                    for message in NWANI.findall(text):
                        newest = html.unescape(message)
    except OSError:
        return None
    return newest


def changes(name, args):
    if name in EDITS or name in GITHUB:
        return True
    if name in ("Agent", "Task"):
        return (args.get("subagent_type") or "") not in REVIEWERS
    if name == "Bash":
        return bool(SHELL_CHANGE.search(QUOTED.sub('""', args.get("command") or "")))
    return False


def main():
    hook = json.load(sys.stdin)
    name, args = hook.get("tool_name"), hook.get("tool_input") or {}
    if not changes(name, args):
        return
    message = newest_message(hook.get("transcript_path") or "")
    if message is None or not is_question(message):
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Nwani's newest message is a question, so it gets only an answer: no "
            "edits, commits, pushes or non-reviewer helpers until Nwani writes again. If the message asks for this step, answer, then "
            "offer the step on a one-tap card, and Nwani's tap lets it through (CLAUDE.md, Optimize).",
    }}))


if __name__ == "__main__":
    main()
