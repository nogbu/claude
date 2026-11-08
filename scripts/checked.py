#!/usr/bin/env python3
"""The checked record: facts a reviewer already verified in a file, so later reviews don't verify
them again (MANUAL.md, Reviewed answers).

Each entry is a claim, the file it was checked in, and what backs it:
- in a code or settings file (anything but .md and .txt), the whole file. Any change to the file
  makes the entry stale, because code behaves through many lines, not the one quoted.
- in a .md or .txt file, the exact text quoted from it. The entry stays settled while the file
  still holds that text, so notes that grow at the end don't make every fact stale.
A stale entry isn't shown, so the fact gets checked again. Facts that don't come from a file, like a
command's output or a web page, aren't recorded.

Run: python3 scripts/checked.py add < facts.json       (a JSON list of {"file", "text", "claim"})
     python3 scripts/checked.py list [--before "YYYY-MM-DD HH:MM"] [FILE ...]
                                                   (settled entries, newest first; --before skips
                                                    entries recorded at or after that UTC time)

Files in this repo are kept by their path inside it, so the record matches across threads wherever
the repo sits. The record lives in Project Files, so every thread shares it:
/mnt/project-files/review-record/checked.jsonl (CHECKED_RECORD overrides the path, for tests).
"""
import datetime
import hashlib
import json
import os
import pathlib
import sys

RECORD = pathlib.Path(os.environ.get("CHECKED_RECORD", "/mnt/project-files/review-record/checked.jsonl"))
REPO = pathlib.Path(__file__).resolve().parents[1]
PROSE = {".md", ".txt"}
SHOWN = 100  # newest settled entries shown by a plain list
STAMP = "%Y-%m-%d %H:%M"


def key(path):
    """How a file is kept in the record: repo:relative/path for this repo's files, else absolute."""
    path = os.path.abspath(path)
    real = os.path.realpath(path)
    for root in (str(REPO), os.path.realpath(str(REPO))):
        if real == root or real.startswith(root + os.sep):
            return "repo:" + os.path.relpath(real, root)
    return path


def where(stored):
    return str(REPO / stored[5:]) if stored.startswith("repo:") else stored


def text_of(path):
    try:
        return pathlib.Path(path).read_text(errors="replace")
    except OSError:
        return None


def normalize(text):
    return " ".join(text.split())


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


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
    stored = entry.get("file", "")
    if stored not in cache:
        cache[stored] = text_of(where(stored))
    text = cache[stored]
    if text is None:
        return False
    if entry.get("sha"):
        return digest(text) == entry["sha"]
    return bool(entry.get("text", "").strip()) and normalize(entry["text"]) in normalize(text)


def add(facts):
    now = datetime.datetime.now(datetime.timezone.utc).strftime(STAMP)
    lines, out = [], []
    for fact in facts:
        path, quote, claim = fact.get("file", ""), fact.get("text", ""), fact.get("claim", "").strip()
        text = text_of(path)
        if text is None:
            out.append("Not recorded, %s can't be read: %s" % (path, claim))
            continue
        if not quote.strip() or normalize(quote) not in normalize(text):
            out.append("Not recorded, %s doesn't hold that exact text: %s" % (path, claim))
            continue
        entry = {"claim": claim, "file": key(path), "text": quote.strip(), "checked": now}
        if os.path.splitext(path)[1].lower() not in PROSE:
            entry["sha"] = digest(text)
        lines.append(json.dumps(entry))
        out.append("Recorded: %s" % claim)
    if lines:
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        with RECORD.open("a") as f:
            f.write("\n".join(lines) + "\n")
    return "\n".join(out) or "Nothing to record."


def show(paths, before=None):
    wanted = {key(p) for p in paths}
    cache, seen, out = {}, set(), []
    for entry in reversed(entries()):
        if before and entry.get("checked", "") >= before:
            continue
        mark = (entry.get("file"), entry.get("text"), entry.get("claim"))
        if mark in seen or (wanted and entry.get("file") not in wanted) or not settled(entry, cache):
            continue
        seen.add(mark)
        out.append("- %s (%s, checked %s UTC, backed by %s)" % (
            entry.get("claim"), where(entry.get("file", "")), entry.get("checked"),
            "the whole file as it is now" if entry.get("sha") else "\"%s\"" % entry.get("text")))
    if not wanted:
        out = out[:SHOWN]
    return "\n".join(out) if out else "No settled facts recorded%s." % (" for those files" if wanted else "")


def main(argv):
    if argv == ["add"]:
        try:
            facts = json.load(sys.stdin)
        except ValueError:
            print("Not recorded: the input isn't a JSON list.")
            return 1
        print(add(facts if isinstance(facts, list) else [facts]))
        return 0
    if argv and argv[0] == "list":
        rest, before = argv[1:], None
        if rest[:1] == ["--before"] and len(rest) > 1:
            before, rest = rest[1], rest[2:]
        print(show(rest, before))
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
