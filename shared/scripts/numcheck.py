#!/usr/bin/env python3
"""Check that tightening or moving text kept every number (pkg step 5; product skill, Log).

  python3 shared/scripts/numcheck.py FILE...   compare each file's last-commit copy with its working copy
  python3 shared/scripts/numcheck.py --repeats 45,0.3 FILE...   those numbers may lose copies (a cut repeat)
                                                                 while one copy remains
  python3 shared/scripts/numcheck.py --dups [FILE...]   each number with a unit (45 mm, 4 drops, 1,500 words) that
                                                        two or more files state, with the files: candidates for a
                                                        fact kept in one owner (refactor-config step 4); the default
                                                        files are the rule files and learnings (name product docs to add them)

A number that left one named file passes if it still appears in any named file (text moved to a log.md
counts), so name the source and every destination. Prints each lost number, or "all numbers kept".
Exit 1 when a number was lost.
"""
import glob, os, re, subprocess, sys
from collections import Counter, defaultdict

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or "."
# A number keeps a sign or symbol written against it (−5, ±0.2, Ø 4) and a leading point (.62);
# a comma before exactly three digits groups thousands (1,500), any other comma is a decimal (12,5).
NUM = re.compile(r"(?:(?:(?<=\s)|^)[-−]|[±Ø⌀]\s?)?(?<![\d.])\.?\d+(?:\.\d+|,\d+)*")


def norm(n):
    n = re.sub(r"\s", "", n).replace("−", "-")
    return re.sub(r",(\d{3})(?=,|\.|$)", r"\1", n)


def numbers(text):
    return Counter(norm(n) for n in NUM.findall(text))


UNITS = r"mm|cm|m|g|kg|s|min|h|MPa|GPa|%|°|deg|px|words?|drops?|mL|L|oz|gal|layers?|beads?|lines?|CPUs?|KB|MB|GB|A|V|W"
WITH_UNIT = re.compile(r"(?<![\d.,-])(\d+(?:[.,]\d+)*)\s?(" + UNITS + r")(?![\w'])")


def dups(files):
    """Print each number-with-unit stated in two or more of the files, most files first."""
    if not files:
        files = ["CLAUDE.md"] + sorted(glob.glob("projects/*/config.*.md", root_dir=ROOT)) \
            + sorted(glob.glob(".claude/skills/*/*.md", root_dir=ROOT)) \
            + sorted(glob.glob("projects/*/learnings/*.md", root_dir=ROOT)) + sorted(glob.glob("shared/learnings.*.md", root_dir=ROOT))
    where = defaultdict(set)
    for f in files:
        for m in WITH_UNIT.finditer(open(os.path.join(ROOT, f), encoding="utf-8").read()):
            where[f"{norm(m.group(1))} {m.group(2)}"].add(f)
    found = [(v, fs) for v, fs in where.items() if len(fs) > 1]
    for v, fs in sorted(found, key=lambda x: (-len(x[1]), x[0])):
        print(f"{v}: {', '.join(sorted(fs))}")
    print(f"{len(found)} values stated in more than one file" if found else "no value stated in more than one file")
    return 0


def main(files):
    repeats = set()
    if files[:1] == ["--dups"]:
        return dups(files[1:])
    if files[:1] == ["--repeats"] and len(files) > 1:
        repeats, files = {norm(n) for n in files[1].split(",")}, files[2:]
    if not files:
        print(__doc__.strip()); return 1
    before, after = Counter(), Counter()
    for f in files:
        old = subprocess.run(["git", "show", f"HEAD:{f}"], cwd=ROOT, capture_output=True, text=True)
        before += numbers(old.stdout if old.returncode == 0 else "")
        p = os.path.join(ROOT, f)
        after += numbers(open(p, encoding="utf-8").read() if os.path.exists(p) else "")
    lost = before - after
    lost = Counter({n: k for n, k in lost.items() if not (n in repeats and after[n])})
    for n, k in sorted(lost.items()):
        print(f"lost: {n}" + (f" (x{k})" if k > 1 else ""))
    if not lost:
        print("all numbers kept")
    return 1 if lost else 0


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet when piped to head
    sys.exit(main(sys.argv[1:]))
