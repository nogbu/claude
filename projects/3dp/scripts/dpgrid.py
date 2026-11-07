#!/usr/bin/env python3
"""dpgrid: write a dp audit's check grid (dp-audit step 5), leaving only the cells that need a hand check.

  python3 projects/3dp/scripts/dpgrid.py make DPCHECK.json INVENTORY.json -o GRID.tsv --script projects/3dp/products/x/build/x.py [--audit form|function]
  python3 projects/3dp/scripts/dpgrid.py todo GRID.tsv [--req 2.3] [--kind edge]    list the cells still TODO
  python3 projects/3dp/scripts/dpgrid.py done GRID.tsv                              counts; exit 1 if any cell is blank or TODO

INVENTORY.json is step 4's item list: [{"id": "E12", "kind": "edge", "text": "base front edge, x 0-120 at z 0"}, ...],
dpcheck.py --inventory's list plus the items added by hand; an item may carry "cells": {"2.2": [status, evidence], ...}.
with kind one of dpreqs.KINDS; a "design" item for the design as a whole is added if missing.
--audit keeps only that half's requirements (dpreqs.audit_of); without it the grid covers both halves.
The header names the half ("form", "function" or "full"), the script and its last commit.
The grid has one row per (requirement, item), columns req, item, kind, status, evidence:
  - a requirement dpcheck covers as "all" gets dpcheck's rows as they stand (item "dpcheck: object");
  - a "part" requirement gets dpcheck's rows, plus TODO cells for its items;
  - an item whose kind the requirement can't apply to (dpreqs APPLIES) gets N/A with the map's reason;
  - a cell the item's own "cells" settle (dpcheck --inventory measures them; dpinv.py) gets that status and evidence,
    TODO with the measurements where they leave the call to a person;
  - every other cell is TODO, to be set to PASS, FAIL or N/A with evidence by hand.
"""
import argparse, json, os, subprocess, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dpreqs

COLS = ("req", "item", "kind", "status", "evidence")


def _clean(s):
    return " ".join(str(s).split())


def make(dpcheck, inventory, head, audit=None):
    reqs = [r for r in dpreqs.requirements() if dpreqs.in_audit(r[0], audit)]
    dc = json.load(open(dpcheck, encoding="utf-8"))
    cover = {}
    for pairs in dc.get("covers", {}).values():
        for rid, how in pairs:
            cover[rid] = "all" if how == "all" else "part"
    items = json.load(open(inventory, encoding="utf-8"))
    bad = [i for i in items if i.get("kind") not in dpreqs.KINDS]
    if bad:
        sys.exit("unknown kind in inventory (use %s): %s" % (", ".join(dpreqs.KINDS), bad[:3]))
    if not any(i["kind"] == "design" for i in items):
        items = [{"id": "D", "kind": "design", "text": "the design as a whole"}] + items
    rows = []
    for rid, title, text in reqs:
        kinds = dpreqs.applies(rid, text)
        for r in dc.get("rows", []):
            if rid in r.get("req", []):
                rows.append((rid, "dpcheck: " + r["object"], r["check"], r["status"], r["text"]))
        if cover.get(rid) == "all":
            continue
        why = "dpreqs: %s applies only to %s" % (rid, ", ".join(kinds))
        for it in items:
            label = "%s %s" % (it["id"], it["text"])
            if it["kind"] in kinds and rid in it.get("cells", {}):
                rows.append((rid, label, it["kind"]) + tuple(it["cells"][rid]))
            elif it["kind"] in kinds:
                note = "dpcheck covers part (see its rows)" if cover.get(rid) == "part" else ""
                rows.append((rid, label, it["kind"], "TODO", note))
            else:
                rows.append((rid, label, it["kind"], "N/A", why))
    lines = ["# dp %s audit grid: %s" % (audit or "full", head), "# " + "\t".join(COLS)]
    lines += ["\t".join(_clean(c) for c in r) for r in rows]
    return lines, items, rows


def read(path):
    out = []
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        if line.startswith("#") or not line.strip():
            continue
        c = line.rstrip("\n").split("\t")
        out.append(dict(zip(COLS, c + [""] * (len(COLS) - len(c))), line=n))
    return out


def summary(rows):
    st = Counter(r["status"] if not isinstance(r, tuple) else r[3] for r in rows)
    return "%d cells: %s" % (len(rows), ", ".join("%d %s" % (v, k) for k, v in sorted(st.items())))


def main(argv=None):
    ap = argparse.ArgumentParser(description="dp audit check grid; see the module docstring.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make"); m.add_argument("dpcheck"); m.add_argument("inventory")
    m.add_argument("-o", required=True); m.add_argument("--script", required=True, help="the build (or audit-model) script audited")
    m.add_argument("--audit", choices=dpreqs.AUDITS, help="one half only; default both")
    t = sub.add_parser("todo"); t.add_argument("grid"); t.add_argument("--req"); t.add_argument("--kind")
    d = sub.add_parser("done"); d.add_argument("grid")
    a = ap.parse_args(argv)
    if a.cmd == "make":
        sha = subprocess.run(["git", "log", "-1", "--format=%h", "--", os.path.basename(a.script)], cwd=os.path.dirname(os.path.abspath(a.script)),
                             capture_output=True, text=True).stdout.strip() or "uncommitted"
        lines, items, rows = make(a.dpcheck, a.inventory, "%s %s" % (a.script, sha), a.audit)
        open(a.o, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        kinds = Counter(i["kind"] for i in items)
        nreq = sum(dpreqs.in_audit(r[0], a.audit) for r in dpreqs.requirements())
        print("%s: %s audit, %d requirements, %d items (%s); %s" % (a.o, a.audit or "full", nreq, len(items),
              ", ".join("%d %s" % (v, k) for k, v in kinds.items()), summary(rows)))
        return 0
    rows = read(a.grid)
    if a.cmd == "todo":
        for r in rows:
            if r["status"] == "TODO" and (not a.req or r["req"] == a.req) and (not a.kind or r["kind"] == a.kind):
                print("%d\t%s\t%s" % (r["line"], r["req"], r["item"]))
        return 0
    bad = [r for r in rows if r["status"] not in ("PASS", "FAIL", "N/A", "CHECK") or not r["evidence"]]
    print(summary(rows) + ("; %d cells missing a status or evidence (first at line %d)" % (len(bad), bad[0]["line"]) if bad else "; complete"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
