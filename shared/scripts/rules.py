#!/usr/bin/env python3
"""List every rule bullet, skill step and learning as one row (config redesign, section 12).

Run from anywhere in the repo:
  python3 shared/scripts/rules.py            one row per rule, tab-separated
  python3 shared/scripts/rules.py --summary  rows and words per file
  python3 shared/scripts/rules.py FILE...    only those files
  python3 shared/scripts/rules.py --find REGEX   only rows matching REGEX (any case), undated, so it's quick:
                                                 the rows a new rule may contradict or repeat (repo-edit, Where things go)
  python3 shared/scripts/rules.py --since COMMIT   only rows added or changed after that commit
  python3 shared/scripts/rules.py --pairs [--since COMMIT]   for each row (or each row changed since COMMIT), the rows
                                                 sharing the most key words with it: the pairs refactor-config step 2 reads

Columns: id (file:line), file, section, kind (rule, step, learning or text),
words, added (oldest line's commit date), changed (newest line's commit date), text.
It also lists each product doc's Product rules section and each content file's
rules header field (CLAUDE.md, How the rules load).
check.py imports rule_files() and split() from here.
"""
import functools, glob, os, re, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or "."
# A config section heading is a bare capitalized line ("Rules  "); markdown files use "#" headings.
PLAIN_HEADING = re.compile(r"^[A-Z][A-Za-z ]*\s*$")
MD_HEADING = re.compile(r"^#{1,6} +(.+?)\s*#*\s*$")
BULLET = re.compile(r"^(\s*)[-*] +(.*)$")
STEP = re.compile(r"^(\s*)\d+[.)] +(.*)$")


def rule_files():
    """Files that are all rules: CLAUDE.md, every project card, and every file in a skill's folder."""
    files = ["CLAUDE.md"] + sorted(glob.glob("projects/*/config.*.md", root_dir=ROOT)) \
        + sorted(glob.glob(".claude/skills/*/*.md", root_dir=ROOT))
    return [f for f in files if os.path.exists(os.path.join(ROOT, f))]


def learning_files():
    """Content files that hold only learnings."""
    return sorted(glob.glob("projects/*/learnings/*.md", root_dir=ROOT)) \
        + sorted(glob.glob("shared/learnings.*.md", root_dir=ROOT))


def is_learnings(path):
    return "/learnings/" in path or os.path.basename(path).startswith("learnings.")


def file_rules():
    """(path, line, section, text) for each Product rules bullet and rules header field."""
    from index import content_files, header
    for f in content_files():
        if f.endswith("/log.md") or "/retired/" in f:
            continue
        fields, _ = header(f)
        if fields.get("rules"):
            yield f, 1, "rules header", fields["rules"]
        if f.endswith("/state.md"):
            for start, end, section, kind, text in split(f):
                if section.strip("* ").lower() == "product rules" and kind == "rule":
                    yield f, start, section, text


def split(path, text=None):
    """Yield (line, end_line, section, kind, text) for each rule, step, learning or paragraph."""
    if text is None:
        text = open(os.path.join(ROOT, path), encoding="utf-8").read()
    lines = text.split("\n")
    is_config = os.path.basename(path).startswith("config.") or "/products/" in path  # bare-line headings
    learnings = is_learnings(path)
    section, start, body, kind, indent = "", 0, [], None, 0
    i = 0
    if lines and lines[0].strip() == "---":  # front matter (skills, content headers)
        end = next((j for j in range(1, len(lines)) if lines[j].strip() == "---"), 0)
        i = end + 1

    def flush():
        if body:
            k = kind
            if learnings or section.lower() == "learnings":
                k = "learning"
            yield (start, start + len(body) - 1, section, k, " ".join(s.strip() for s in body))

    while i < len(lines):
        line = re.sub(r"^(\s*>)+ ?", "", lines[i].rstrip())  # blockquoted lists read the same
        n = i + 1
        i += 1
        m = MD_HEADING.match(line)
        heading = m.group(1) if m else (line.strip() if is_config and PLAIN_HEADING.match(line) else None)
        if heading is not None:
            yield from flush()
            section, body, kind = heading, [], None
            continue
        if not line.strip() or line.strip().startswith("```"):
            yield from flush()
            body, kind = [], None
            continue
        b, s = BULLET.match(line), STEP.match(line)
        if b or s:
            yield from flush()
            start, body, kind, indent = n, [(b or s).group(2)], "rule" if b else "step", len((b or s).group(1))
            continue
        if body and kind != "text" and indent and len(line) - len(line.lstrip()) <= indent:
            yield from flush()  # a paragraph closing a nested list isn't part of its last item
            body = []
        if not body:  # a new paragraph
            start, kind = n, "text"
        body.append(line)
    yield from flush()


@functools.lru_cache(maxsize=None)
def blame_dates(path):
    """Commit time (YYYY-MM-DD HH:MM, US Eastern) of each line, from git blame, following lines moved or
    copied from other files; uncommitted lines get now. A shallow clone is deepened first, or every line
    older than the clone's first commit would get that commit's date."""
    out = subprocess.run(["git", "blame", "-w", "-C", "-C", "--line-porcelain", "--", path], cwd=ROOT,
                         capture_output=True, text=True).stdout
    dates, t = [], None
    for line in out.split("\n"):
        if line.startswith("author-time "):
            t = int(line.split()[1])
        elif line.startswith("\t"):
            dates.append(t)
    tz = ZoneInfo("America/New_York")  # CLAUDE.md, Project setup: US Eastern
    return [datetime.fromtimestamp(d or datetime.now().timestamp(), tz).strftime("%Y-%m-%d %H:%M") for d in dates]


def find(pattern):
    rx = re.compile(pattern, re.I)
    rows = [(f, start, section, text) for f in rule_files() + learning_files() for start, _, section, _, text in split(f)]
    rows += list(file_rules())
    for f, start, section, text in rows:
        if rx.search(text):
            print(f"{f}:{start}\t{section}\t{text}")


def unshallow():
    """Deepen a shallow clone before blaming. Runs started together (refactor-prep.sh, test.py) race for
    .git/shallow.lock, so a failed fetch waits for the other one and checks again, rather than blaming a
    shallow clone (every older line dated the clone's first commit)."""
    import time
    for _ in range(120):
        if subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=ROOT, capture_output=True,
                          text=True).stdout.strip() != "true":
            return
        if subprocess.run(["git", "fetch", "-q", "--unshallow", "origin", "main"], cwd=ROOT,
                          capture_output=True).returncode == 0:
            return
        time.sleep(1)
    sys.exit("rules.py: still a shallow clone after 2 min; dates would be wrong")


HEADER = "id\tfile\tsection\tkind\twords\tadded\tchanged\ttext"


def all_rows():
    """Every row as (id, file, section, kind, text, added, changed), dated like the full list."""
    rows = []
    for f in rule_files() + learning_files():
        dates = blame_dates(f)
        for start, end, section, kind, text in split(f):
            span = dates[start - 1:end] or ["?"]
            rows.append((f"{f}:{start}", f, section, kind, text, min(span), max(span)))
    for f, start, section, text in file_rules():
        d = blame_dates(f)[start - 1:start] or ["?"]
        rows.append((f"{f}:{start}", f, section, "rule", text, d[0], d[0]))
    return rows


def row_line(r):
    return f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{len(r[4].split())}\t{r[5]}\t{r[6]}\t{r[4]}"


def commit_stamp(commit):
    """The commit's time in the list's date format, so a row is newer when its changed date sorts after it."""
    t = subprocess.run(["git", "log", "-1", "--format=%at", commit], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if not t:
        sys.exit(f"rules.py: no commit {commit}")
    return datetime.fromtimestamp(int(t), ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M")


STOP = set("""a about an and any are as at be been before but by can could do does each either else every for from get
give has have how if in into is it its just may more most much must never no not of on once one only or other our
out over per same so some than that the their them then there these they this those to too until up was we were what
when where whether which while who will with would you your""".split())
WORD = re.compile(r"[a-z][a-z0-9'-]{2,}")


def key_words(text):
    return {w for w in WORD.findall(text.lower()) if w not in STOP}


def pairs(subjects, rows, top=8, least=2, bar=10.0, cut=160):
    """For each subject row, the rows that share its rarer key words (refactor-config step 2 reads these pairs instead
    of every row; the full row is in the list by id). A shared word counts log(rows / rows holding it) and a candidate
    needs a sum of `bar`: about three words each in 20 rows or fewer, or four in 45 or fewer. Words in over a twentieth
    of all rows carry no signal and are dropped. Tested on the 64 rows changed 2026-10-08 to 10-09: 79 KB against
    the 171 KB list, 4 to 5 candidates a row."""
    import math
    kw = {r[0]: key_words(r[4]) for r in rows}
    df = Counter(w for ws in kw.values() for w in ws)
    n = len(rows)
    common = {w for w, k in df.items() if k > n / 20}
    kw = {k: ws - common for k, ws in kw.items()}
    print(f"# {len(subjects)} rows, each with up to {top} candidate rows that share its rarer key words "
          f"(of {n} rows; words in over a twentieth of them ignored; a candidate's text is cut at {cut} characters, "
          f"the full row is in rules.tsv)")
    for s in subjects:
        scored = []
        for r in rows:
            if r[0] == s[0]:
                continue
            shared = kw[s[0]] & kw[r[0]]
            score = sum(math.log(n / df[w]) for w in shared)
            if len(shared) >= least and score >= bar:
                scored.append((score, r[0], r[4], shared))
        scored.sort(key=lambda x: (-x[0], x[1]))
        print(f"\n== {s[0]} [{s[2]}] (changed {s[6]}): {s[4]}")
        for score, rid, text, shared in scored[:top]:
            print(f"   {rid} ({', '.join(sorted(shared))}): {text[:cut]}" + ("..." if len(text) > cut else ""))
        if len(scored) > top:
            print(f"   ... {len(scored) - top} more")


def main(argv):
    if [a for a in argv if a.startswith("-") and a not in ("--find", "--summary", "--since", "--pairs")]:
        return print(__doc__.split("\n\n")[1])
    if argv[:1] == ["--find"] and len(argv) == 2:
        return find(argv[1])
    if "--since" in argv or "--pairs" in argv:
        unshallow()
        commit = argv[argv.index("--since") + 1] if "--since" in argv else None
        stamp = commit_stamp(commit) if commit else ""
        rows = all_rows()
        new = [r for r in rows if r[6] > stamp]
        if "--pairs" in argv:
            return pairs(new, rows)
        print(HEADER)
        for r in new:
            print(row_line(r))
        return
    summary = "--summary" in argv
    unshallow()
    files = [a for a in argv if not a.startswith("--")] or rule_files() + learning_files()
    totals = defaultdict(lambda: [0, 0])
    if not summary:
        print(HEADER)
    for f in files:
        dates = [] if summary else blame_dates(f)
        for start, end, section, kind, text in split(f):
            words = len(text.split())
            totals[f][0] += 1
            totals[f][1] += words
            if summary:
                continue
            span = dates[start - 1:end] or ["?"]
            print(f"{f}:{start}\t{f}\t{section}\t{kind}\t{words}\t{min(span)}\t{max(span)}\t{text}")
    if not [a for a in argv if not a.startswith("--")]:
        for f, start, section, text in file_rules():
            totals[f][0] += 1
            totals[f][1] += len(text.split())
            if not summary:
                d = blame_dates(f)[start - 1:start] or ["?"]
                print(f"{f}:{start}\t{f}\t{section}\trule\t{len(text.split())}\t{d[0]}\t{d[0]}\t{text}")
    if summary:
        for f, (rows, words) in totals.items():
            print(f"{f}: {rows} rows, {words} words")


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet when piped to head
    main(sys.argv[1:])
