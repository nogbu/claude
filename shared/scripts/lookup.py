#!/usr/bin/env python3
"""Look up a setting by its OrcaSlicer UI label (config redesign, sections 5 and 6; phase 4 decision 6).

Run from anywhere in the repo:
  python3 shared/scripts/lookup.py LABEL [printer|process]   every setting whose label (or tab, section or Orca key)
                                                             contains LABEL
  python3 shared/scripts/lookup.py --notes [printer|process]   my files' notes
  python3 shared/scripts/lookup.py --check   rows in my files that match no Orca setting (fix with ALIASES below)

My files are projects/3dp/data/printer-settings.json and process-settings.json, shaped
{about, notes, settings: {tab: {section: {label: value}}}} (section "" is a tab's own table; G-code blocks are strings).
Defaults are Orca's stock presets, pulled from Orca by projects/3dp/scripts/orcadefaults.py with Orca's on-screen
tabs, sections, labels and units (2026-10-10; this replaced the screenshot copies p1s-default-settings.json and
p1s-default-process-settings.json). Each row prints mine beside the default:
  printer: printer-settings.json (my differences) over the default printer settings
  process: process-settings.json (my full settings) beside the default process settings
A row of mine matches an Orca setting by tab and label (section breaks ties), else by ALIASES. "(same)" ignores case,
spaces, units' spacing, "*" and notes in parentheses such as "(greyed out)". Matching ignores case. A G-code value
prints in full only when one setting matches; otherwise its first line.
"""
import json, os, re, subprocess, sys

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or "."
DATA = os.path.join(ROOT, "projects", "3dp", "data")
sys.path.insert(0, os.path.join(ROOT, "projects", "3dp", "scripts"))
import orcadefaults  # noqa: E402

KINDS = {"printer": ("printer-settings.json", True), "process": ("process-settings.json", False)}
# (kind, tab, label) of mine -> Orca key(s), where my label isn't Orca's (screenshot wording or a row I split)
ALIASES = {
    ("process", "Speed", "Bridge, external"): ["bridge_speed"],
    ("process", "Speed", "Bridge, internal"): ["internal_bridge_speed"],
}


def load(name):
    return json.load(open(os.path.join(DATA, name), encoding="utf-8"))


def rows(settings):
    for tab, sections in settings.items():
        for section, labels in sections.items():
            for label, value in labels.items():
                yield tab, section, label, value


def norm(text):
    return re.sub(r"[^a-z0-9%]", "", text.lower())


def same(a, b):
    """Equal once case, spacing, '*', notes in parentheses and number formatting are set aside."""
    def n(x):
        x = re.sub(r"\((greyed out|confirmed|not shown[^)]*)\)", "", x)
        x = x.replace("−", "-").replace("*", "").replace("`", "").lower()
        x = re.sub(r"-?\d+(\.\d+)?", lambda m: repr(float(m.group(0))), x)
        return re.sub(r"[\s_-]|layers?\b", "", x)
    return n(a) == n(b)


def match(kind, tab, section, label, orca):
    """The Orca row my (tab, section, label) means, or None."""
    alias = ALIASES.get((kind, tab, label))
    pool = [r for r in orca if r["group"] == kind]
    if alias:
        hits = [r for r in pool if r["keys"] == alias]
    else:
        hits = [r for r in pool if norm(r["tab"]) == norm(tab) and norm(r["label"]) == norm(label)]
        if len(hits) > 1:
            hits = [r for r in hits if norm(r["section"]) == norm(section)] or hits
        if len(hits) > 1:
            hits = [r for r in hits if len(r["keys"]) == 1] or hits
    return hits[0] if hits else None


def table(kinds):
    """[(kind, tab, section, label, keys, mine, default)] over every Orca row and every row of mine."""
    orca = orcadefaults.rows()
    singles = {(r["group"], r["keys"][0]) for r in orca if len(r["keys"]) == 1}
    out = []
    for k in kinds:
        mine_file, diffs_only = KINDS[k]
        used = set()
        for t, s, l, v in rows(load(mine_file)["settings"]):
            r = match(k, t, s, l, orca)
            if r:
                used.add(id(r))
                out.append((k, t, s, l, r["keys"], v, r["value"]))
            else:
                out.append((k, t, s, l, [], v, "(not in Orca's settings)"))
        for r in orca:
            if r["group"] != k or id(r) in used:
                continue
            if len(r["keys"]) > 1 and all((k, key) in singles for key in r["keys"]):
                continue    # a line of several settings, each also listed on its own
            mine = r["value"] if diffs_only else "(not in my file)"
            out.append((k, r["tab"], r["section"], r["label"], r["keys"], mine, r["value"]))
    return out


def main(argv):
    kinds = [a for a in argv if a in KINDS] or list(KINDS)
    words = [a for a in argv if a not in KINDS and not a.startswith("--")]
    if "--notes" in argv:
        for k in kinds:
            for n in load(KINDS[k][0]).get("notes", []):
                print(f"{KINDS[k][0]}: {n}")
        return 0
    if "--check" in argv:
        bad = [row for row in table(kinds) if not row[4] and row[6] == "(not in Orca's settings)"]
        for k, t, s, l, _, m, _ in bad:
            print(f"{k}: {' > '.join(x for x in (t, s, l) if x)}: no Orca setting matches")
        print(f"{len(bad)} rows unmatched")
        return 1 if bad else 0
    if not words:
        print(__doc__.strip().split("\n\n")[1])
        return 1
    query = " ".join(words).lower()
    found = [row for row in table(kinds)
             if query in " ".join(row[1:4]).lower() or any(query.replace(" ", "_") in key for key in row[4])]
    if not found:
        print(f"lookup: no setting matches '{query}'")
        return 1
    full = len(found) == 1
    for k, t, s, l, keys, m, v in found:
        where = " > ".join(x for x in (t, s, l) if x)
        short = lambda x: x if full or "\n" not in x else x.split("\n")[0] + " … (G-code; look it up alone for all of it)"
        tag = " (same)" if same(m, v) else ""
        print(f"{k}: {where}: mine {short(m)}{tag}; default {short(v)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
