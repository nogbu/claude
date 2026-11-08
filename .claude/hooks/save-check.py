#!/usr/bin/env python3
"""PreToolUse hook (CLAUDE.md, Answer by click: approving a save also approves merging it).

Refuses a save to main in nogbu/claude unless Nwani approved one since Claude's last save. A save is
merging a pull request, writing files straight to main through GitHub, or a git push to main.
Approval is Nwani's newest message since that save being a tap on a card option that starts with
"Save", or anything Nwani typed. The check can't read what typed words mean, so a typed message
always passes, and it can't tell which change a tap was for. A push in the record is judged by the
branch checked out now, so an old push that named no branch, or named HEAD, can be misread. A merge through gh api, or a push hidden inside a script or a quoted string, isn't seen.
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
# Only git run as a command counts, not the words "git push" inside a search or a quote.
START = r"(?:^|[;&|(\n]|\bthen\b|\bdo\b)\s*"
# Words that run the command after them, like timeout 60 or bash -c ", and git's own options.
WRAP = r"(?:(?:timeout\s+\S+|env|sudo|nice|nohup|command|exec|\w+=\S*)\s+)*(?:(?:ba)?sh\s+-l?c\s+[\"']?)?"
# Quoted text that mentions a push or merge is masked first, unless it's the command a shell runs
# (bash -c "..."), so a push written inside a string, a search or a test case isn't counted.
QUOTED = re.compile(r"""(?<!-c )(?<!-lc )(["'])(?:\\.|(?!\1).)*?\1""", re.S)
GIT_OPTS = r"(?:\s+(?:-[Cc]\s+\S+|--git-dir[=\s]\S+|--work-tree[=\s]\S+|--no-pager|-P))*"
PUSH = re.compile(START + WRAP + r"git\b" + GIT_OPTS + r"\s+push\b[^|;&\n]*")
PR_MERGE = re.compile(START + WRAP + r"gh\s+pr\s+merge\b[^|;&\n]*")
OTHER_REPO = re.compile(r"(?:-R|--repo)[\s=]+(\S+)")


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
    command = QUOTED.sub(lambda q: '""' if re.search(r"push|merge", q.group(0)) else q.group(0), command)
    for merge in PR_MERGE.finditer(command):
        other = OTHER_REPO.search(merge.group(0))
        if not other or other.group(1).strip("'\"").lower() == "nogbu/claude":
            return True
    for push in PUSH.finditer(command):
        before = command[:push.start()]
        folder = cwd
        moved = re.findall(r"\bcd\s+(\S+)", before)
        if moved:
            folder = moved[-1].strip("\"'")
        given = re.search(r"\s-C\s+(\S+)", push.group(0).split(" push")[0])
        if given:
            folder = given.group(1).strip("\"'")
        if not git(folder, "rev-parse", "--git-dir"):
            continue  # not a repo, so nothing gets pushed from there
        try:
            words = shlex.split(push.group(0))
        except ValueError:
            words = push.group(0).split()
        words = words[words.index("push") + 1:] if "push" in words else []
        words = [w.strip("\"'") for w in words]
        plain = [w for w in words if not w.startswith("-")]
        remote = plain[0] if plain else "origin"
        url = git(folder, "remote", "get-url", remote) or remote
        if not REPO.search(url) and "/" in url:
            continue  # another repo
        if "--all" in words or "--mirror" in words:
            return True  # every branch, main among them
        branch = git(folder, "rev-parse", "--abbrev-ref", "HEAD")
        refs = [r.lstrip("+") for r in plain[1:]] or ["HEAD"]
        for ref in refs:
            target = ref.split(":")[-1] or ref.split(":")[0]
            if target in ("HEAD", "@"):
                target = branch
            if re.fullmatch(r"(?:refs/heads/)?main", target):
                return True
    return False


def is_save(name, args, cwd):
    if name == MERGE:  # any merge in nogbu/claude, whatever its base branch
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
