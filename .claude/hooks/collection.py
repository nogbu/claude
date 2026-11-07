#!/usr/bin/env python3
"""UserPromptSubmit hook (projects/plantagram/CLAUDE.md, Collection thread).

Runs plantagram's plant.py hook on Nwani's message, so collection.md's commands (headcount,
/headcount, /increment, /confirm, /remove, /[plant], /print) print their steps before Claude answers.
plant.py acts only in plantagram threads and prints nothing otherwise.
"""
import os
import pathlib
import subprocess
import sys


def main():
    data = sys.stdin.read()
    start = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or ".")
    for root in [start] + sorted(p for p in start.iterdir() if p.is_dir()):
        script = root / "projects" / "plantagram" / "scripts" / "plant.py"
        if script.is_file():
            out = subprocess.run([sys.executable, str(script), "hook"], input=data, capture_output=True, text=True, timeout=8)
            print(out.stdout, end="")
            return


if __name__ == "__main__":
    main()
