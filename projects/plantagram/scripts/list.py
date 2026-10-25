#!/usr/bin/env python3
"""Show, add to, update and sort a list file (config redesign, section 5).

  python3 shared/scripts/list.py show LIST
  python3 shared/scripts/list.py add LIST "first column" [Column=value ...]
  python3 shared/scripts/list.py done LIST "text in the row"
  python3 shared/scripts/list.py set LIST "text in the row" Column=value [Column=value ...]
  python3 shared/scripts/list.py remove LIST "text in the row"
  python3 shared/scripts/list.py sort LIST
  python3 shared/scripts/list.py products LIST [STATUS]   add a row for each product folder of the list's project
                                                          (not retired/) that has none, with STATUS (default: the default);
                                                          a row naming it another way ("moss plank" for mossPlank) that
                                                          still has the default status takes the folder's name and STATUS

LIST is a path, or a short name looked up in this project's content folder
(/mnt/project-files/.project names the project), e.g. "todo" or "hopper.list".
The file's header gives the order (sort: Status, Added), the status values
in order (statuses: open, done) and the status for new rows (default: open).
New rows get today's date (US Eastern) in an Added column. Every change re-sorts
the list and rewrites the file; it doesn't commit (save.sh does that).
A row is matched by text appearing in it; when several rows hold the text, the one
whose first column is exactly that text wins (e.g. a plant whose name also appears as
another row's species); otherwise more than one match is refused.
"""
import os, re, sys
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from index import ROOT, header


def resolve(name):
    if os.path.exists(name):
        return name
    try:
        project = open("/mnt/project-files/.project").read().strip()
    except OSError:
        project = None
    for base in ([f"projects/{project}/content"] if project else []):
        for cand in (name, name + ".md"):
            path = os.path.join(ROOT, base, cand)
            if os.path.exists(path):
                return path
    sys.exit(f"list.py: can't find list '{name}' (give a path, or set /mnt/project-files/.project)")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def load(path):
    text = open(path, encoding="utf-8").read()
    fields, errors = header(path, text)
    if errors or "sort" not in fields:
        sys.exit(f"list.py: {path} has no list header ({'; '.join(errors) or 'no sort field'})")
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines)
                  if l.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1])), None)
    if start is None:
        sys.exit(f"list.py: {path} has no table")
    end = start + 2
    while end < len(lines) and lines[end].strip().startswith("|"):
        end += 1
    cols = cells(lines[start])
    rows = [cells(l) for l in lines[start + 2:end]]
    for r in rows:
        if len(r) != len(cols):
            sys.exit(f"list.py: a row has {len(r)} cells but the table has {len(cols)} columns: {r}")
    spec = {
        "sort": [c.strip() for c in fields["sort"].split(",")],
        "statuses": [s.strip() for s in fields["statuses"].split(",")],
        "default": fields["default"],
    }
    for c in spec["sort"]:
        if c not in cols:
            sys.exit(f"list.py: sort column '{c}' isn't in the table ({', '.join(cols)})")
    return lines, start, end, cols, rows, spec


def sort_rows(cols, rows, spec):
    def key(r):
        k = []
        for c in spec["sort"]:
            v = r[cols.index(c)]
            if c == "Status":
                k.append(spec["statuses"].index(v) if v in spec["statuses"] else len(spec["statuses"]))
            else:
                # dates are YYYY-MM-DD, so text order is date order; runs of digits sort as numbers ("9" before "10")
                k.append([(0, int(t), "") if t.isdigit() else (1, 0, t) for t in re.findall(r"\d+|\D+", v.lower())])
        return k
    return sorted(rows, key=key)


def write(path, lines, start, end, cols, rows, spec):
    rows = sort_rows(cols, rows, spec)
    table = lines[start:start + 2] + ["| " + " | ".join(r) + " |" for r in rows]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines[:start] + table + lines[end:]))
    return rows


def assign(cols, row, pairs, spec):
    for p in pairs:
        col, sep, val = p.partition("=")
        if not sep or col not in cols:
            sys.exit(f"list.py: '{p}' should be Column=value, with a column from: {', '.join(cols)}")
        if col == "Status" and val not in spec["statuses"]:
            sys.exit(f"list.py: status must be one of: {', '.join(spec['statuses'])}")
        if "|" in val:
            sys.exit("list.py: a value can't contain |")
        row[cols.index(col)] = val


def find(rows, text):
    hits = [r for r in rows if any(text.lower() in c.lower() for c in r)]
    exact = [r for r in hits if r[0].lower() == text.lower()]
    if len(hits) > 1 and len(exact) == 1:
        hits = exact
    if len(hits) != 1:
        sys.exit(f"list.py: '{text}' matches {len(hits)} rows; give text that matches exactly one"
                 + ("".join(f"\n  {' | '.join(r)}" for r in hits) if hits else ""))
    return hits[0]


def show(cols, rows):
    print("| " + " | ".join(cols) + " |")
    print("|" + " --- |" * len(cols))
    for r in rows:
        print("| " + " | ".join(r) + " |")
    print(f"({len(rows)} rows)")


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    cmd, path, args = argv[0], resolve(argv[1]), argv[2:]
    lines, start, end, cols, rows, spec = load(path)
    if cmd == "show":
        show(cols, sort_rows(cols, rows, spec))
        return
    if cmd == "add":
        if not args:
            sys.exit("list.py: add needs the first column's text")
        row = [""] * len(cols)
        row[0] = args[0]
        if "Status" in cols:
            row[cols.index("Status")] = spec["default"]
        if "Added" in cols:
            row[cols.index("Added")] = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
        assign(cols, row, args[1:], spec)
        if "|" in row[0]:
            sys.exit("list.py: a value can't contain |")
        if any(r[0].lower() == row[0].lower() for r in rows):
            sys.exit(f"list.py: '{row[0]}' is already in the list")
        rows.append(row)
        print("added: | " + " | ".join(row) + " |")
    elif cmd in ("done", "set", "remove"):
        if not args:
            sys.exit(f"list.py: {cmd} needs text that matches one row")
        row = find(rows, args[0])
        if cmd == "remove":
            rows.remove(row)
            print("removed: | " + " | ".join(row) + " |")
        else:
            pairs = ["Status=done"] if cmd == "done" else args[1:]
            if not pairs:
                sys.exit("list.py: set needs Column=value")
            assign(cols, row, pairs, spec)
            print("now: | " + " | ".join(row) + " |")
    elif cmd == "products":
        status = args[0] if args else spec["default"]
        if status not in spec["statuses"]:
            sys.exit(f"list.py: status must be one of: {', '.join(spec['statuses'])}")
        folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(path))), "products")
        key = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())  # "moss plank", "moss-plank" and mossPlank are one product
        have = {key(r[0]): r for r in rows}
        exact = {r[0] for r in rows}
        for name in sorted(os.listdir(folder)):
            if name == "retired" or not os.path.isdir(os.path.join(folder, name)) or name in exact:
                continue
            old = have.get(key(name))
            if old is not None and old[0] != name and "Status" in cols and old[cols.index("Status")] == spec["default"] != status:
                old[0] = name
                assign(cols, old, [f"Status={status}"], spec)
                print("now: | " + " | ".join(old) + " |")
            if old is None:
                row = [""] * len(cols)
                row[0] = name
                assign(cols, row, [f"Status={status}"] if "Status" in cols else [], spec)
                if "Added" in cols:
                    row[cols.index("Added")] = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
                rows.append(row)
                print("added: | " + " | ".join(row) + " |")
    elif cmd != "sort":
        sys.exit(f"list.py: unknown command '{cmd}'\n{__doc__}")
    write(path, lines, start, end, cols, rows, spec)
    print(f"saved to {os.path.relpath(path, ROOT)} (not yet committed)")


if __name__ == "__main__":
    main(sys.argv[1:])
