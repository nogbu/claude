#!/usr/bin/env python3
"""PreToolUse checks that block a rule break before it happens (.claude/settings.json runs it).

  reply (mcp__hearthbot__reply): the thread's first reply must start with "config v[version] loaded."
      (CLAUDE.md, First reply); a notice that a config file couldn't be read may come before it.
  Bash: no commit that skips the commit checks (--no-verify, commit -n) and no change to core.hooksPath
      other than .githooks (check.py runs on every commit).
Prints a deny decision, or nothing to allow.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))
    sys.exit(0)


def replied_before(transcript):
    try:
        with open(transcript, encoding="utf-8") as f:
            return any('"name":"mcp__hearthbot__reply"' in line.replace(" ", "") for line in f)
    except OSError:
        return False


def main():
    h = json.load(sys.stdin)
    tool, inp = h.get("tool_name", ""), h.get("tool_input") or {}
    if tool == "mcp__hearthbot__reply":
        marker = "/tmp/claude-first-reply-%s" % h.get("session_id", "")
        if os.path.exists(marker) or replied_before(h.get("transcript_path", "")):
            return
        m = re.search(r"v(\d+(?:\.\d+)*)", open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8").readline())
        want = "config v%s loaded." % (m.group(1) if m else "?")
        if want not in "\n".join((inp.get("text") or "").strip().split("\n")[:3]):
            deny('First reply: start with "%s" on its own line (CLAUDE.md, First reply).' % want)
        open(marker, "w").close()
    elif tool == "Bash":
        cmd = inp.get("command") or ""
        if re.search(r"--no-verify|\bgit\b[^;&|]*\bcommit\b[^;&|]*\s-[a-zA-Z]*n\b", cmd) or \
                re.search(r"core\.hooksPath(?!\s+\.githooks\b)\s+\S", cmd):
            deny("Commits run check.py through .githooks; fix what it reports instead of skipping it (repo-edit).")


if __name__ == "__main__":
    main()
