#!/usr/bin/env python3
"""Wait for a moved review's report (CLAUDE.md, Review before answering).

Usage: python3 scripts/wait-review.py OUTPUT_FILE
Run it in one foreground Bash call with a timeout of 600000. It checks the
task's output file every 5 seconds, reading only new bytes, and stops at the
first assistant entry whose content has a tool_use named SubagentHandback.
A plain text match isn't enough: the helper's own setup text names the tool
too, which stopped a hand-written loop early on 2026-11-19.
"""
import json, os, sys, time

path = sys.argv[1]
start, pos, rest, found = time.time(), 0, b"", None
while time.time() - start < 580 and found is None:
    if os.path.exists(path):
        with open(path, "rb") as f:
            f.seek(pos)
            chunk = f.read()
            pos = f.tell()
        lines = (rest + chunk).split(b"\n")
        rest = lines.pop()
        for line in lines:
            if b"SubagentHandback" not in line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") != "assistant":
                continue
            content = (entry.get("message") or {}).get("content") or []
            for part in content if isinstance(content, list) else []:
                if isinstance(part, dict) and part.get("type") == "tool_use" \
                        and part.get("name") == "SubagentHandback":
                    found = part.get("input")
    if found is None:
        time.sleep(5)
print("waited %ds" % (time.time() - start))
print(json.dumps(found, indent=1) if found is not None else "TIMEOUT: no report yet")
