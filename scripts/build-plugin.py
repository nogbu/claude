#!/usr/bin/env python3
"""Builds house-rules.plugin: the automatic checks and the reviewer helper as one plugin file
for Nwani to add on claude.ai (MANUAL.md, Automatic checks).

Project threads start with the repo's own settings switched off, so .claude/settings.json alone
never runs the checks there. Plugins added in Project settings load into each new cloud thread
(Projects docs). Whether a plugin's checks run there is still being tested. The plugin's
hooks are read from .claude/settings.json, so the two can't drift apart.

Run: python3 scripts/build-plugin.py OUTPUT_FOLDER
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[1]
NAME = "house-rules"
README = """# house-rules

Nwani's automatic checks for Claude in claude.ai project threads, plus the reviewer helper.
Before Claude sends a reply or a decision card, the checks look for the mistakes listed in the
nogbu/claude repo's MANUAL.md under Automatic checks, and send Claude back to fix them. The
reviewer helper checks longer answers before they are sent. The checks only run in cloud threads
that have the nogbu/claude repo, where the rules they enforce are written.
"""
# Each hook runs through this. Outside cloud threads, or in a thread without the nogbu/claude repo,
# the rules aren't loaded, so a check would block Claude without it knowing why. It stays off there.
RUN = """#!/bin/bash
[ "$CLAUDE_CODE_REMOTE" = true ] || exit 0
start="${CLAUDE_PROJECT_DIR:-$PWD}"
for checklist in "$start/checklists/review.md" "$start"/*/checklists/review.md; do
  [ -f "$checklist" ] && exec python3 "$(dirname "$0")/$1"
done
exit 0
"""


def command(script):
    return 'bash "${CLAUDE_PLUGIN_ROOT}/hooks/run.sh" %s' % script


def plugin_hooks():
    hooks = json.loads((REPO / ".claude" / "settings.json").read_text())["hooks"]
    for groups in hooks.values():
        for group in groups:
            for hook in group["hooks"]:
                hook["command"] = command(re.search(r"\.claude/hooks/([\w-]+\.py)", hook["command"]).group(1))
    return {"hooks": hooks}


def build(out):
    commits = subprocess.run(["git", "-C", str(REPO), "rev-list", "--count", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
    files = {
        ".claude-plugin/plugin.json": json.dumps({
            "name": NAME, "version": "0.1.%s" % commits,
            "description": "Nwani's automatic checks and reviewer helper for Claude in project threads.",
        }, indent=2),
        "hooks/hooks.json": json.dumps(plugin_hooks(), indent=2),
        "agents/reviewer.md": (REPO / ".claude" / "agents" / "reviewer.md").read_text(),
        "README.md": README,
        "hooks/run.sh": RUN,
    }
    for script in sorted((REPO / ".claude" / "hooks").glob("*.py")):
        if script.name != "test_hooks.py":
            files["hooks/" + script.name] = script.read_text()
    folder = pathlib.Path(out) / NAME
    shutil.rmtree(folder, ignore_errors=True)
    for path, text in files.items():
        (folder / path).parent.mkdir(parents=True, exist_ok=True)
        (folder / path).write_text(text)
    target = pathlib.Path(out) / (NAME + ".plugin")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(files):
            z.write(folder / path, path)
    return folder, target


if __name__ == "__main__":
    folder, target = build(sys.argv[1])
    print("folder:", folder)
    print("plugin:", target)
