#!/usr/bin/env python3
"""Tests for checked.py. Run: python3 scripts/test_checked.py"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

SCRIPT = pathlib.Path(__file__).parent / "checked.py"
REPO = SCRIPT.resolve().parents[1]
DIR = pathlib.Path(tempfile.mkdtemp())
RECORD = DIR / "record" / "checked.jsonl"
ENV = dict(os.environ, CHECKED_RECORD=str(RECORD))
NOTES = DIR / "notes.md"
CODE = DIR / "check.py"

failures = []
cases = 0


def run(*args, facts=None):
    return subprocess.run([sys.executable, str(SCRIPT)] + list(args), capture_output=True, text=True, env=ENV,
                          input=json.dumps(facts) if facts is not None else "").stdout.strip()


def expect(name, ok):
    global cases
    cases += 1
    if not ok:
        failures.append(name)


def fact(path, text, claim):
    return {"file": str(path), "text": text, "claim": claim}


NOTES.write_text("Line one.\nNever open claude.old/old-config.\nThe queue:\n- question 5\n")
CODE.write_text("def check():\n    return 'main'\n")
out = run("add", facts=[
    fact(NOTES, "Never open claude.old/old-config.", "Old-config is off limits"),
    fact(NOTES, "The queue:  - question 5", "Question 5 is queued"),
    fact(NOTES, "Open old-config freely.", "Wrong"),
    fact(NOTES, "  ", "Empty"),
    fact(DIR / "gone.md", "x", "Gone"),
    fact(CODE, "return 'main'", "check returns main"),
])
expect("several facts recorded in one call", out.count("Recorded") == 3)
expect("text the file lacks is refused", "doesn't hold that exact text: Wrong" in out)
expect("empty text is refused", "doesn't hold that exact text: Empty" in out)
expect("a missing file is refused", "can't be read: Gone" in out)
listed = run("list")
expect("list shows a settled fact", "Old-config is off limits" in listed)
expect("list shows a fact whose spacing differed", "Question 5 is queued" in listed)
expect("list never shows a refused fact", "Wrong" not in listed)
expect("a code fact is backed by the whole file", "check returns main" in listed and "the whole file" in listed)
only = run("list", str(CODE))
expect("list for one file shows only that file", "check returns main" in only and "Old-config" not in only)
NOTES.write_text("Line one.\nOpen claude.old/old-config when asked.\nThe queue:\n- question 5\nNew line.\n")
CODE.write_text("def check():\n    x = 1\n    return 'main'\n")
after = run("list")
expect("a note fact goes stale when its text changes", "Old-config is off limits" not in after)
expect("a note fact stays when other text is added", "Question 5 is queued" in after)
expect("a code fact goes stale when any line changes", "check returns main" not in after)
NOTES.unlink()
expect("a fact goes stale when its file is gone", "Question 5 is queued" not in run("list"))
NOTES.write_text("Line one.\n")
run("add", facts=[fact(NOTES, "Line one.", "Line one is there")])
run("add", facts=[fact(NOTES, "Line one.", "Line one is there")])
expect("a repeated fact is shown once", run("list").count("Line one is there") == 1)
expect("--before skips facts recorded since", "Line one is there" not in run("list", "--before", "2000-01-01 00:00"))
expect("--before keeps older facts", "Line one is there" in run("list", "--before", "2999-01-01 00:00"))
readme = REPO / "MANUAL.md"
first = readme.read_text().splitlines()[0]
run("add", facts=[fact(readme, first, "The manual has a title")])
expect("a repo file is kept by its path in the repo", '"file": "repo:MANUAL.md"' in RECORD.read_text())
expect("a repo file's fact is listed by its real path", "The manual has a title" in run("list", str(readme)))
RECORD.open("a").write("not json\n")
expect("a broken line is skipped", "Line one is there" in run("list"))
expect("bad input is refused", "isn't a JSON list" in subprocess.run(
    [sys.executable, str(SCRIPT), "add"], input="nope", capture_output=True, text=True, env=ENV).stdout)
expect("no arguments shows how to run it", "Run:" in run())

for failure in failures:
    print("FAIL", failure)
print("%d of %d cases pass" % (cases - len(failures), cases))
sys.exit(1 if failures else 0)
