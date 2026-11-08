#!/usr/bin/env python3
"""PreToolUse hook (CLAUDE.md, Answer by click: approving a save also approves merging it).

Refuses a save to main in nogbu/claude unless Nwani approved one since Claude's last save. A save is
merging a pull request, writing files straight to main through GitHub, or a git push to main.
Approval is Nwani's newest message since that save being a tap on a card option that starts with
"Save", or anything Nwani typed. The check can't read what typed words mean, so a typed message
always passes, and it can't tell which change a tap was for.
"""
import json
import re
import shlex
import subprocess
import sys

from nwani import queued_message

REPO = re.compile(r"github\.com[/:]nogbu/claude(?:\.git)?/?$", re.I)
WRITES = {"mcp__github__push_files", "mcp__github__create_or_update_file", "mcp__github__delete_file"}
MERGE = "mcp__github__merge_pull_request"
NWANI = re.compile(r'<message\b(?=[^>]*\btrigger="true")(?=[^>]*\bfrom="human")[^>]*>(.*?)</message>', re.S)
TAP = re.compile(r'^Chose (?:&#34;|")(.*?)(?:&#34;|") on the decision card asking', re.S)
PUSH = re.compile(r"\bgit\b(?:\s+-C\s+\S+)?\s+push\b[^|;&\n]*")
PR_MERGE = re.compile(r"\bgh\s+pr\s+merge\b")


def ours(args):
    return (args.get("owner") or "").lower() == "nogbu" and (args.get("repo") or "").lower() == "claude"


def git(folder, *args):
    try:
        return subprocess.run(["git", "-C", folder] + list(args), capture_output=True, text=True,
                              timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def pushes_to_main(command, cwd):
    """True if this shell command pushes to main in nogbu/claude, or might and can't be told apart."""
    if PR_MERGE.search(command):
        return True
    for push in PUSH.finditer(command):
        before = command[:push.start()]
        folder = cwd
        moved = re.findall(r"\bcd\s+(\S+)", before)
        if moved:
            folder = moved[-1]
        given = re.search(r"\bgit\s+-C\s+(\S+)", push.group(0))
        if given:
            folder = given.group(1)
        try:
            words = shlex.split(push.group(0))
        except ValueError:
            words = push.group(0).split()
        words = words[words.index("push") + 1:] if "push" in words else []
        plain = [w for w in words if not w.startswith("-")]
        remote = plain[0] if plain else "origin"
        url = git(folder, "remote", "get-url", remote) or remote
        if url and not REPO.search(url) and "/" in url:
            continue  # another repo
        if not url:
            return True
        refs = plain[1:]
        if refs:
            if any(re.search(r"(?:^|:)(?:refs/heads/)?main$", r.lstrip("+")) for r in refs):
                return True
        elif git(folder, "rev-parse", "--abbrev-ref", "HEAD") in ("main", ""):
            return True
    return False


def is_save(name, args, cwd):
    if name == MERGE:
        return ours(args)
    if name in WRITES:
        return ours(args) and (args.get("branch") or "") == "main"
    if name == "Bash":
        return pushes_to_main(args.get("command") or "", cwd)
    return False


def approved(path, cwd):
    """True if Nwani's newest message since Claude's last save approves a save."""
    ok = False
    saves = {}  # tool_use id -> True for a save call, waiting for its result
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
            if entry.get("type") == "assistant" and isinstance(content, list):
                for block in content:
                    if block.get("type") == "tool_use" and is_save(block.get("name"), block.get("input") or {}, cwd):
                        saves[block.get("id")] = True
            elif entry.get("type") == "user" and not entry.get("isMeta"):
                if isinstance(content, str):
                    texts.append(content)
                for block in content if isinstance(content, list) else []:
                    if block.get("type") == "text":
                        texts.append(block.get("text", ""))
                    elif block.get("type") == "tool_result" and saves.pop(block.get("tool_use_id"), None) \
                            and not block.get("is_error"):
                        ok = False  # that save used up the approval
            for text in texts:
                for message in NWANI.findall(text):
                    tap = TAP.match(message.strip())
                    ok = bool(tap and tap.group(1).strip().lower().startswith("save")) if tap else True
    return ok


def main():
    hook = json.load(sys.stdin)
    name, args = hook.get("tool_name"), hook.get("tool_input") or {}
    if name == "Bash" and not (PUSH.search(args.get("command") or "") or PR_MERGE.search(args.get("command") or "")):
        return
    cwd = hook.get("cwd") or "."
    if not is_save(name, args, cwd) or not hook.get("transcript_path"):
        return
    if approved(hook["transcript_path"], cwd):
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Nwani hasn't approved a save since the last one (CLAUDE.md, Answer by click). Show the change "
            "and ask on a Save card whose yes option starts with \"Save\", then save once Nwani taps it or "
            "approves it in words."),
    }}))


if __name__ == "__main__":
    main()
