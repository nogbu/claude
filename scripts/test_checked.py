#!/usr/bin/env python3
"""Tests for checked.py. Run: python3 scripts/test_checked.py"""
import os
import pathlib
import subprocess
import sys
import tempfile

SCRIPT = pathlib.Path(__file__).parent / "checked.py"
DIR = pathlib.Path(tempfile.mkdtemp())
ENV = dict(os.environ, CHECKED_RECORD=str(DIR / "record" / "checked.jsonl"))
NOTES = DIR / "notes.md"
OTHER = DIR / "other.md"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT)] + list(args), capture_output=True, text=True,
                          env=ENV).stdout.strip()


failures = []


def expect(name, got, want):
    if want not in got:
        failures.append("%s: expected %r in %r" % (name, want, got))


NOTES.write_text("Line one.\nNever open claude.old/old-config.\nThe queue:\n- question 5\n")
OTHER.write_text("Other file.\n")
expect("add with the exact text", run("add", str(NOTES), "Never open claude.old/old-config.", "Old-config is off limits"), "Recorded")
expect("add with spacing that differs", run("add", str(NOTES), "The queue:  - question 5", "Question 5 is queued"), "Recorded")
expect("add with text the file lacks", run("add", str(NOTES), "Open old-config freely.", "Wrong"), "Not recorded")
expect("add with empty text", run("add", str(NOTES), "  ", "Empty"), "Not recorded")
expect("add for a missing file", run("add", str(DIR / "gone.md"), "x", "Gone"), "Not recorded")
expect("add for another file", run("add", str(OTHER), "Other file.", "Other is there"), "Recorded")
listed = run("list")
expect("list shows a settled fact", listed, "Old-config is off limits")
expect("list shows the other file", listed, "Other is there")
if "Wrong" in listed:
    failures.append("list shows a fact that was never recorded")
only = run("list", str(OTHER))
expect("list for one file", only, "Other is there")
if "Old-config" in only:
    failures.append("list for one file shows another file's fact")
NOTES.write_text("Line one.\nOpen claude.old/old-config when asked.\nThe queue:\n- question 5\n")
after = run("list")
if "Old-config is off limits" in after:
    failures.append("list still shows a fact whose text changed")
expect("list keeps a fact whose text is unchanged", after, "Question 5 is queued")
OTHER.unlink()
if "Other is there" in run("list"):
    failures.append("list still shows a fact whose file is gone")
run("add", str(NOTES), "Line one.", "Line one is there")
run("add", str(NOTES), "Line one.", "Line one is there")
if run("list").count("Line one is there") != 1:
    failures.append("list shows a repeated fact twice")
(DIR / "record" / "checked.jsonl").open("a").write("not json\n")
expect("list skips a broken line", run("list"), "Line one is there")
expect("no arguments shows how to run it", run(), "Run:")

total = 17
for failure in failures:
    print("FAIL", failure)
print("%d of %d cases pass" % (total - len(failures), total))
sys.exit(1 if failures else 0)
