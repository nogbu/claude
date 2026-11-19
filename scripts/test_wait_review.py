#!/usr/bin/env python3
"""Tests scripts/wait-review.py on entries copied from real records
(scripts/real-records/moved-review.jsonl), as CLAUDE.md asks for any check
that reads a record. The fixture's first lines are setup entries that name
SubagentHandback, one with the exact bytes that stopped a hand-written loop
early on 2026-11-19. Its last line is a helper's real report, with the text
replaced by REPORT PLACEHOLDER. Run: python3 scripts/test_wait_review.py"""
import pathlib, subprocess, sys, tempfile, threading, time

HERE = pathlib.Path(__file__).parent
SCRIPT = HERE / "wait-review.py"
LINES = (HERE / "real-records" / "moved-review.jsonl").read_text().splitlines(True)
SETUP, REPORT = LINES[:-1], LINES[-1]


def wait(path, limit):
    return subprocess.run([sys.executable, str(SCRIPT), path, str(limit)],
                          capture_output=True, text=True, check=True).stdout


def temp(lines):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    f.writelines(lines)
    f.close()
    return f.name


results = []
def case(name, ok):
    results.append(ok)
    print(("pass  " if ok else "FAIL  ") + name)


setup_only = temp(SETUP)
case("the fixture holds the bytes that fooled the old loop",
     '"name":"SubagentHandback"' in "".join(SETUP))
case("setup mentions alone don't stop it, it times out",
     "TIMEOUT" in wait(setup_only, 6))
case("a finished record returns the report",
     "REPORT PLACEHOLDER" in wait(temp(LINES), 30))

# Live: the report lands while the script is already waiting.
growing = temp(SETUP)
def append_later():
    time.sleep(7)
    with open(growing, "a") as f:
        f.write(REPORT)
threading.Thread(target=append_later).start()
start = time.time()
out = wait(growing, 60)
case("a report written while it waits is found", "REPORT PLACEHOLDER" in out and time.time() - start >= 7)

print("%d of %d cases pass" % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
