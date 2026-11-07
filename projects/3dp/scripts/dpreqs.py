"""Print the design principles as the dp audit's numbered requirements list, word for word (dp-audit step 3).

  python3 projects/3dp/scripts/dpreqs.py [--audit form|function] [--json]

Numbers: G.1, G.2 ... for the general bullets (Short name and Talking to me are left out, as step 3 says);
N.k for principle N's k-th bullet, N.k.j for a bullet nested under it. Each line carries the principle's
title, so a grid row citing "2.3" reads on its own. --json adds each requirement's "applies": the item kinds
(dp-audit step 4) it can apply to; dpgrid.py marks every other item's cell N/A with that reason.
--audit lists only one half's requirements (audit_of): the form audit (how it looks and prints) or the function audit
(fits, loads and use); the General bullets are in both.
"""
import json, os, re, sys

DP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".claude", "skills", "build-3dp", "design-principles.md")
SKIP = ("Short name:", "Talking to me:")

# Item kinds, from dp-audit step 4's inventory, plus "design": one item for the design as a whole.
KINDS = {"design": "the design as a whole", "part": "part and how it prints", "edge": "edge",
         "step": "step between surfaces", "contact": "joint, fit or contact face",
         "overhang": "overhang, bridge or spot over air", "load": "load path", "misuse": "way to print, assemble or use it wrong"}
# Which kinds each requirement can apply to, with the start of its text: if design-principles.md changes
# so an id no longer starts that way, the map is out of date and dpgrid.py stops until it is updated.
APPLIES = {
    'G.1': ('design', 'Goal: consumer parts'),
    'G.2': ('design', 'Applies to every'),
    'G.3': ('design', 'Exceptions: a product'),
    '1.1': ('part', 'Before showing a'),
    '1.2': ('contact', 'Keep fit features'),
    '1.3': ('overhang', 'Keep overhangs within'),
    '1.4': ('part', 'Fit it on'),
    '1.5': ('load', 'Run loads along'),
    '1.6': ('design', 'Each concept render'),
    '2.1': ('edge', 'Every edge gets'),
    '2.2': ('edge', 'Size: start at'),
    '2.3': ('edge', 'Matching corners: corners'),
    '2.4': ('edge', 'Inside/outside pairs: where'),
    '2.5': ('edge contact', 'Limits: make it'),
    '2.6': ('edge overhang', 'Overhanging horizontal edges:'),
    '2.7': ('design', 'Images: pictures after'),
    '3.1': ('step', 'Make surfaces that'),
    '3.2': ('step', 'Where a step'),
    '4.1': ('overhang', 'First, design bridges'),
    '4.1.1': ('overhang', 'Peaked roof: two'),
    '4.1.2': ('overhang', 'Chamfered roof: 45-degree'),
    '4.1.3': ('overhang', 'One-sided roof: ramp'),
    '4.2': ('overhang', 'Bridges and spots'),
    '4.2.1': ('overhang', 'Seen surfaces: no'),
    '4.2.2': ('overhang', 'Hidden surfaces (e.g.'),
    '4.3': ('overhang', 'Supports, in order'),
    '4.4': ('overhang', 'Bridge supports: triangle'),
    '4.5': ('overhang', 'Painted supports: only'),
    '4.6': ('design', 'Before calling a'),
    '5.1': ('contact', 'Put any width'),
    '5.2': ('contact', 'Why: a width'),
    '5.3': ('design', 'Trial: each time'),
    '6.1': ('contact', 'Friction grip (stays'),
    '6.2': ('contact', 'Snug, removable with'),
    '6.3': ('contact', 'Slip fit (slides'),
    '6.4': ('contact', 'Other materials: use'),
    '7.1': ('contact', 'A new joint,'),
    '8.1': ('part', 'Make each step'),
    '8.2': ('part', 'Labels are only'),
    '9.1': ('load', 'Before recommending geometry'),
    '9.2': ('load', 'Check every load'),
    '9.3': ('design', 'Concept pictures can'),
    '10.1': ('part contact misuse', 'Design every part'),
    '10.2': ('contact misuse', 'For example: joints'),
    '11.1': ('contact', 'Parts glued or'),
    '11.2': ('edge step contact', 'On a joined'),
    '11.3': ('part', 'Everything about printing'),
    '11.4': ('contact', 'Put seams on'),
    '11.5': ('contact', 'The joint still'),
    '11.6': ('step contact', 'Seams are flush,'),
    '12.1': ('part', 'Every dimension that'),
    '12.2': ('part', 'Every horizontal thickness'),
    '12.3': ('design', 'When a value'),
    '12.4': ('design', 'Run this check'),
}

# The function audit's requirements (dp-audit, Two halves): whole principles, plus single bullets from 1 and 11.
# Every other requirement is the form audit's, and the General bullets (G.n) are in both.
FUNCTION = ("5.", "6.", "7.", "8.", "9.", "10.")
FUNCTION_IDS = ("1.2", "11.1", "11.5")
AUDITS = ("form", "function")


def audit_of(rid):
    """The audit half requirement rid belongs to: "form", "function" or "both"."""
    if rid.startswith("G."):
        return "both"
    return "function" if rid.startswith(FUNCTION) or rid in FUNCTION_IDS else "form"


def in_audit(rid, audit):
    """True if requirement rid is checked in audit ("form", "function", or None for both halves)."""
    return audit is None or audit_of(rid) in ("both", audit)


def applies(rid, text=None):
    """The kinds requirement rid applies to; every kind if the map lacks it. Raises if the map is out of date."""
    if rid not in APPLIES:
        return list(KINDS)
    kinds, start = APPLIES[rid]
    if text is not None and not text.startswith(start):
        raise SystemExit("dpreqs APPLIES is out of date: %s now reads %r; update the map" % (rid, text[:60]))
    return kinds.split()


def requirements(path=DP):
    out, sec, title, k, j, g = [], None, "General", 0, 0, 0
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip()
        m = re.match(r"^(\d+)\. (.+?)\s*$", line)
        if m:
            sec, title, k = m.group(1), m.group(2), 0
            continue
        m = re.match(r"^( *)- (.+?)\s*$", line)
        if not m:
            continue
        depth, text = len(m.group(1)), m.group(2)
        if sec is None:
            if text.startswith(SKIP):
                continue
            g += 1; out.append(("G.%d" % g, title, text))
        elif depth <= 3:
            k += 1; j = 0; out.append(("%s.%d" % (sec, k), title, text))
        else:
            j += 1; out.append(("%s.%d.%d" % (sec, k, j), title, text))
    return out


if __name__ == "__main__":
    audit = sys.argv[sys.argv.index("--audit") + 1] if "--audit" in sys.argv else None
    if audit not in (None,) + AUDITS:
        sys.exit("--audit takes form or function")
    reqs = [r for r in requirements() if in_audit(r[0], audit)]
    if "--json" in sys.argv:
        print(json.dumps([dict(id=i, principle=t, text=x, applies=applies(i, x), audit=audit_of(i)) for i, t, x in reqs], indent=1))
    else:
        for i, t, x in reqs:
            print("%-7s [%s] %s" % (i, t, x))
        print("%d requirements" % len(reqs))
