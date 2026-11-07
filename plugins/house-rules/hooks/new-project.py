#!/usr/bin/env python3
"""UserPromptSubmit hook (CLAUDE.md, Projects).

On a thread's first message, reads the project's name and tells Claude when the repo has no
projects/[name] folder for it, so a new project's rules and learnings files get offered without
Nwani asking. Projects listed in projects/no-folder.md are skipped.
"""
import html
import json
import os
import pathlib
import re
import sys

# The first message of a thread carries the session context, which names the project.
NAME = [re.compile(r'^Project: "([^"\n]+)"', re.M), re.compile(r'<project\b[^>]*\bname="([^"]+)"')]


def project(prompt):
    if "<session-context" not in prompt:
        return None
    for pattern in NAME:
        m = pattern.search(prompt)
        if m:
            return html.unescape(m.group(1)).strip()
    return None


def folder(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def repo(start):
    """The folder the thread started in, or the repo right under it that has the checklists."""
    for root in [start] + sorted(p for p in start.iterdir() if p.is_dir()):
        if (root / "checklists" / "review.md").is_file():
            return root
    return None


def skipped(root):
    path = root / "projects" / "no-folder.md"
    if not path.is_file():
        return set()
    return {folder(m.group(1)) for m in re.finditer(r"^- ([^:\n]+)", path.read_text(), re.M)}


def main():
    hook = json.load(sys.stdin)
    name = project(hook.get("prompt") or "")
    root = repo(pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or hook.get("cwd") or "."))
    if not name or not root or not folder(name):
        return
    slug = folder(name)
    existing = {p.name.lower() for p in (root / "projects").iterdir() if p.is_dir()} if (root / "projects").is_dir() else set()
    if slug in existing or slug in skipped(root):
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": (
            'This thread is in the "%s" project, and the nogbu/claude repo has no projects/%s folder '
            "for it (CLAUDE.md, Projects). After answering Nwani's message, offer on a Save card to "
            "create projects/%s/CLAUDE.md and projects/%s/learnings.md, starting like projects/nosh's. "
            "If Nwani says this project needs no folder, add it to projects/no-folder.md instead, so "
            "later threads don't ask." % (name, slug, slug, slug)),
    }}))


if __name__ == "__main__":
    main()
