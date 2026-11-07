#!/usr/bin/env python3
"""Commit check for the config redesign (sections 4, 7 and 12). The pre-commit hook runs it.

  python3 shared/scripts/check.py         check the staged files (what the hook runs)
  python3 shared/scripts/check.py --all   check every file

Blocks (exit 1): an edit to a file whose header says readonly: yes; a new learning with no
date learned; a content file with no valid header, or whose about plus read-when runs
past index.LINE_CAP words (index.py); CLAUDE.md changed without a new version line; added
git conflict markers; a project with no card, no Cardinal sources bullet or no content/todo.md; a config extension (retired in phase 3); a file outside the product
layout (a product doc not in products/[name]/state.md, a staging folder, a learnings file
outside learnings/); a project card over its word cap; and 8
or more words repeated across the rule files.
Reports only: the core, skills, files in a skill's folder, product state.md files, learnings files and
other reference files over their cap (skills and state.md warn only since 2026-10-09, the core and
learnings files since 2026-10-10: blocked saves and tightening passes cost more than the extra words). A product's log.md and values.md,
retired docs and list files have no cap. With --all it also reports each section pointer
("(repo-edit, Files)"), repo path and script name in a rule file that names nothing that exists.
"""
import glob, os, re, subprocess, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from index import ROOT, LINE_CAP, content_files, header, line_words
from rules import rule_files, split, is_learnings

RUN = 8  # words in a repeated run
CORE, CARD, SKILL, REFERENCE = 1500, 400, 1000, 1500
WARN_ONLY = ("core", "skill", "file in a skill's folder", "product state.md", "learnings file")  # caps that warn, not block (2026-10-09; core and learnings 2026-10-10)
SKILL_FILE = 2000  # a file in a skill's folder other than SKILL.md (raised from 1500, 2026-10-09)
CARD_PATH = re.compile(r"^projects/([^/]+)/config\.\1\.md$")
BLOCKING = re.compile(r"^(CLAUDE\.md|\.claude/skills/.+\.md|projects/([^/]+)/config\.\2\.md)$")  # caps and repeats that block
BLOCKING_CONTENT = re.compile(r"^(projects/[^/]+/products/[^/]+/state\.md|projects/[^/]+/learnings/[^/]+\.md|shared/learnings\.[^/]+\.md)$")
OFF_LAYOUT = [  # (glob, what to do instead): the phase 4 product layout
    ("projects/*/products/*.md", "move it to projects/[project]/products/[name]/state.md"),
    ("projects/*/staging/*", "staging is retired; move its text to the product's log.md"),
    ("projects/*/content/learnings.*.md", "move it to projects/[project]/learnings/[topic].md"),
]


def staged():
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                         cwd=ROOT, capture_output=True, text=True).stdout
    return set(out.split())


DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")


def added_lines(path):
    """Line numbers the staged copy adds to path."""
    diff = subprocess.run(["git", "diff", "--cached", "-U0", "--", path], cwd=ROOT, capture_output=True, text=True).stdout
    for m in re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", diff, re.M):
        start, n = int(m.group(1)), int(m.group(2) or 1)
        yield from range(start, start + n)


def text_of(path, from_index):
    """The staged copy when checking a commit, else the working copy."""
    if from_index:
        return subprocess.run(["git", "show", f":{path}"], cwd=ROOT, capture_output=True, text=True).stdout
    return open(os.path.join(ROOT, path), encoding="utf-8").read()


def count(path, text):
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
        lines = lines[end + 1:]
    return sum(len(l.split()) for l in lines)


def cap(path, text):
    """(cap, layer) for a file, or None when its layer has no cap."""
    name = os.path.basename(path)
    if path == "CLAUDE.md":
        return CORE, "core"
    if CARD_PATH.match(path):
        return CARD, "project card"
    if re.fullmatch(r"\.claude/skills/[^/]+/SKILL\.md", path):
        return SKILL, "skill"
    if path.startswith(".claude/skills/"):
        return SKILL_FILE, "file in a skill's folder"
    if "/retired/" in path or name in ("log.md", "values.md"):
        return None
    fields, _ = header(path, text)
    if "sort" in fields:  # list files are data
        return None
    if name == "state.md":
        return REFERENCE, "product state.md"
    if BLOCKING_CONTENT.match(path):
        return REFERENCE, "learnings file"
    return REFERENCE, "reference file"


def head_count(path):
    """Words in the last commit's copy, or 0 for a new file (a state.md over its cap may shrink, not grow)."""
    r = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=ROOT, capture_output=True, text=True)
    return count(path, r.stdout) if r.returncode == 0 else 0


def runs(path, text):
    """Each 8-word run in a rule file, with its line."""
    for start, end, section, kind, row in split(path, text):
        words = re.findall(r"[a-z0-9']+", row.lower())
        for i in range(len(words) - RUN + 1):
            yield " ".join(words[i:i + RUN]), start


POINTER = re.compile(r"\((CLAUDE\.md|[A-Za-z0-9.-]+)(?: skill)?, \"?([A-Z][^);\"]*)\"?[);]")


def bad_pointers():
    """(file, line, target, section) for each pointer whose target is a rule or content file without that section."""
    from index import short_name, header
    targets = {"CLAUDE.md": "CLAUDE.md"}
    targets.update({os.path.basename(os.path.dirname(f)): f for f in glob.glob(".claude/skills/*/SKILL.md", root_dir=ROOT)})
    for f in content_files():
        targets.setdefault(short_name(f, header(f)[0]), f)
    sections = {}
    for f in rule_files() + content_files():
        for n, line in enumerate(open(os.path.join(ROOT, f), encoding="utf-8"), 1):
            for m in POINTER.finditer(line):
                target, section = m.group(1), m.group(2).strip()
                if target not in targets:
                    continue
                if target not in sections:
                    rows = list(split(targets[target]))  # sections, plus bullet labels ("- Slicing: ...")
                    sections[target] = {s.strip("#* ").lower() for _, _, s, _, _ in rows} | {
                        re.split(r"[:(]", r)[0].strip("* ").lower() for _, _, _, _, r in rows if ":" in r}
                if not any(s == section.lower() or s.startswith(section.lower()) for s in sections[target]):
                    yield f, n, target, section


NAME = re.compile(r"(?<![\w/\[\].-])((?:projects|shared|\.claude|\.githooks)/[\w./-]+|[\w-]+\.py)\b")


def bad_names():
    """(file, line, name) for each repo path or .py script name a rule file names that doesn't exist.
    Names with [placeholders] or * are skipped; a bare script name needs a file of that name anywhere in the repo."""
    tracked = set(subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split())
    basenames = {os.path.basename(p) for p in tracked}
    for f in rule_files():
        for n, line in enumerate(open(os.path.join(ROOT, f), encoding="utf-8"), 1):
            for m in NAME.finditer(line):
                name = m.group(1).rstrip(".,;:)")
                if any(c in name for c in "[]*{}"):
                    continue
                if "/" in name:
                    d = name.rstrip("/") + "/"
                    ok = name in tracked or any(p.startswith(d) for p in tracked)
                else:
                    ok = name in basenames
                if not ok:
                    yield f, n, name


def main(argv):
    every = "--all" in argv
    changed = staged() if not every else None
    scope = lambda f: every or f in changed
    blocked = False

    # Headers and index line length (blocking)
    for f in content_files():
        if not scope(f):
            continue
        fields, errors = header(f, text_of(f, not every))
        for e in errors:
            print(f"check: {f}: {e}", file=sys.stderr)
            blocked = True
        n = line_words(fields)
        if n > LINE_CAP and "/retired/" not in f:
            print(f"check: {f}: about plus read-when is {n} words, over the {LINE_CAP}-word index line cap", file=sys.stderr)
            blocked = True

    # Read-only files (blocking): a file whose committed header says readonly: yes is never edited
    if not every:
        for f in sorted(changed):
            old = subprocess.run(["git", "show", f"HEAD:{f}"], cwd=ROOT, capture_output=True, text=True)
            if old.returncode == 0 and f.endswith(".md") and header(f, old.stdout)[0].get("readonly") == "yes":
                print(f"check: {f} is read-only (readonly: yes); leave it unchanged", file=sys.stderr)
                blocked = True

    # Learnings (blocking): each added learning carries the date learned, on its line or its ### heading
    if not every:
        for f in sorted(changed):
            if not (BLOCKING_CONTENT.match(f) and is_learnings(f)):
                continue
            added = set(added_lines(f))
            heading = ""
            for n, line in enumerate(text_of(f, True).split("\n"), 1):
                if line.startswith("#"):
                    heading = line
                if n in added and re.match(r"^(>\s*)*(### |[-*] )", line) and not (DATE.search(line) or DATE.search(heading)):
                    print(f"check: {f}:{n}: a new learning needs the date learned (YYYY-MM-DD) on its line or heading", file=sys.stderr)
                    blocked = True

    # Config extensions are retired (phase 3): rules go in the card or a skill
    for f in glob.glob("projects/*/config.*.md", root_dir=ROOT):
        if scope(f) and not CARD_PATH.match(f):
            print(f"check: {f} is a config extension; those are retired, so move its rules to the card or a skill", file=sys.stderr)
            blocked = True

    # Project basics (blocking): every project has a card with Cardinal sources and a todo
    touched = every or subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for d in sorted(glob.glob("projects/*/", root_dir=ROOT)):
        p = os.path.basename(d.rstrip("/"))
        if not (every or any(f.startswith(f"projects/{p}/") for f in touched)):
            continue
        for need in (f"projects/{p}/config.{p}.md", f"projects/{p}/content/todo.md"):
            try:
                text = text_of(need, not every)
            except FileNotFoundError:
                text = ""
            if not text:
                print(f"check: projects/{p}/ has no {need.split('/', 2)[2]}; new-project creates it", file=sys.stderr)
                blocked = True
            elif need.endswith(".md") and "/config." in need and not any(
                    s.strip("#* ").lower() == "cardinal sources" and k == "rule" for _, _, s, k, _ in split(need, text)):
                print(f"check: {need} has no Cardinal sources bullet (research skill); add them or \"None (waived [date])\"", file=sys.stderr)
                blocked = True

    # Product layout (blocking)
    for g, fix in OFF_LAYOUT:
        for f in glob.glob(g, root_dir=ROOT):
            if scope(f) and os.path.basename(f) != ".gitkeep":
                print(f"check: {f} is outside the product layout; {fix}", file=sys.stderr)
                blocked = True

    # Word caps: project cards block; every other cap only reports (WARN_ONLY)
    for f in rule_files() + content_files():
        if not scope(f):
            continue
        text = text_of(f, not every)
        c = cap(f, text)
        if c:
            n = count(f, text)
            if n > c[0] and c[1] in WARN_ONLY:
                print(f"check (report only): {f} is {n:,} words, over the {c[0]:,} cap ({c[1]})")
            elif n > c[0] and (BLOCKING.match(f) or BLOCKING_CONTENT.match(f)):
                print(f"check: {f} is {n:,} words, over the {c[0]:,} cap ({c[1]})", file=sys.stderr)
                blocked = True
            elif n > c[0]:
                print(f"check (report only): {f} is {n:,} words, over the {c[0]:,} cap ({c[1]})")

    # CLAUDE.md version line (blocking)
    if not every and "CLAUDE.md" in changed:
        old = subprocess.run(["git", "show", "HEAD:CLAUDE.md"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")[0]
        if old and old == text_of("CLAUDE.md", True).split("\n")[0]:
            print("check: CLAUDE.md changed but its version line didn't; bump it.", file=sys.stderr)
            blocked = True

    # Section pointers (report only, --all): "(CLAUDE.md, Answers)" or "(repo-edit, Files)" names a section that exists
    if every:
        for f, line, target, section in bad_pointers():
            print(f"check (report only): {f}:{line} points to {target}, {section}, which has no such section")
        for f, line, name in bad_names():
            print(f"check (report only): {f}:{line} names {name}, which doesn't exist in the repo")

    # Conflict markers (blocking)
    if not every:
        diff = subprocess.run(["git", "diff", "--cached", "-U0"], cwd=ROOT, capture_output=True, text=True).stdout
        if re.search(r"^\+(<<<<<<< |=======$|>>>>>>> )", diff, re.M):
            print("check: a staged file adds git conflict markers (<<<<<<<, =======, >>>>>>>); resolve them.", file=sys.stderr)
            blocked = True

    # Repeated wording across rule files (blocking where every place is the core, a card or a skill)
    files = rule_files()
    if every or any(f in changed for f in files):
        seen = defaultdict(dict)
        for f in files:
            for run, line in runs(f, text_of(f, not every and f in changed)):
                seen[run].setdefault(f, line)
        passages = {}
        for run, where in seen.items():
            if len(where) < 2 or not (every or any(f in changed for f in where)):
                continue
            key = tuple(sorted(where.items()))
            passages.setdefault(key, run)  # first run of each place pair stands for the passage
        for key, run in sorted(passages.items()):
            places = ", ".join(f"{f}:{l}" for f, l in key)
            if all(BLOCKING.match(f) for f, _ in key):
                print(f"check: repeated wording \"{run}…\" in {places}; word it once", file=sys.stderr)
                blocked = True
            else:
                print(f"check (report only): repeated wording \"{run}…\" in {places}")

    if blocked:
        print("check: fix the above before committing (shared/scripts/index.py shows the header format).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
