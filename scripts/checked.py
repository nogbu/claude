#!/usr/bin/env python3
"""The checked record: facts a reviewer already verified in a file, so later reviews don't verify
them again (MANUAL.md, Reviewed answers).

Each entry is a claim, the file it was checked in, and the exact text in that file that backs it.
An entry counts as settled only while the file still holds that exact text. Once the text changes or
goes, the entry is stale and the fact gets checked again. Facts that don't come from a file, like a
command's output or a web page, aren't recorded.

Run: python3 scripts/checked.py add FILE "EXACT TEXT" "CLAIM"   (refused unless FILE holds the text)
     python3 scripts/checked.py list [FILE ...]                (settled entries, newest first)

The record lives in Project Files, so every thread shares it: /mnt/project-files/review-record/checked.jsonl
(CHECKED_RECORD overrides the path, for tests).
"""
import datetime
import json
import os
import pathlib
import sys

RECORD = pathlib.Path(os.environ.get("CHECKED_RECORD", "/mnt/project-files/review-record/checked.jsonl"))
SHOWN = 100  # newest settled entries shown by a plain list


def text_of(path):
    try:
        return pathlib.Path(path).read_text(errors="replace")
    except OSError:
        return None


def normalize(text):
    return " ".join(text.split())


def entries():
    try:
        lines = RECORD.read_text().splitlines()
    except OSError:
        return []
    found = []
    for line in lines:
        try:
            found.append(json.loads(line))
        except ValueError:
            continue
    return found


def settled(entry, cache):
    path = entry.get("file", "")
    if path not in cache:
        text = text_of(path)
        cache[path] = normalize(text) if text is not None else None
    return cache[path] is not None and normalize(entry.get("text", "")) in cache[path]


def add(path, quote, claim):
    path = os.path.abspath(path)
    text = text_of(path)
    if text is None:
        return "Not recorded: %s can't be read." % path
    if not quote.strip() or normalize(quote) not in normalize(text):
        return "Not recorded: %s doesn't hold that exact text." % path
    entry = {"claim": claim.strip(), "file": path, "text": quote.strip(),
             "checked": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    with RECORD.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return "Recorded: %s" % entry["claim"]


def show(paths):
    wanted = {os.path.abspath(p) for p in paths}
    cache, seen, out = {}, set(), []
    for entry in reversed(entries()):
        key = (entry.get("file"), entry.get("text"), entry.get("claim"))
        if key in seen or (wanted and entry.get("file") not in wanted) or not settled(entry, cache):
            continue
        seen.add(key)
        out.append("- %s (%s, checked %s, backed by: \"%s\")" % (
            entry.get("claim"), entry.get("file"), entry.get("checked"), entry.get("text")))
    if not wanted:
        out = out[:SHOWN]
    return "\n".join(out) if out else "No settled facts recorded%s." % (" for those files" if wanted else "")


def main(argv):
    if len(argv) == 4 and argv[0] == "add":
        print(add(*argv[1:]))
        return 0
    if argv and argv[0] == "list":
        print(show(argv[1:]))
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
