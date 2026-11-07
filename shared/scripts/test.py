#!/usr/bin/env python3
"""Run every repo script once on a small real input and check its result (refactor-config step 3, Tests).

  python3 shared/scripts/test.py            every test
  python3 shared/scripts/test.py NAME...    only tests whose name contains NAME
  python3 shared/scripts/test.py --covers   which scripts each test runs, and the scripts no test runs
  python3 shared/scripts/test.py --for SCRIPT...   the tests to run for those scripts (refactor-check.sh)

Prints one line per test (ok, FAIL with the reason, or skip with why) and its time; exit 1 if any failed.
Inputs are the repo's own files (rule files, hopper.list, the 3dp settings, barrinaClip_rev2's build),
copied to a temporary folder before any script writes, so the repo is never changed. save.sh, undo.sh
and pull.sh push or pull, and the start hook pulls, so they aren't run; setup-env.sh's test waits for the
start hook's install and then checks its skip path, and the slice test installs OrcaSlicer first if it's missing.
"""
import json, os, re, shutil, subprocess, sys, tempfile, time

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
SH, P3 = os.path.join(ROOT, "shared", "scripts"), os.path.join(ROOT, "projects", "3dp", "scripts")
TMP = tempfile.mkdtemp(prefix="repo-test-")
CLIP = os.path.join(ROOT, "projects", "3dp", "products", "barrina-clips", "build", "barrinaClip_rev2.py")


def run(*cmd, stdin=None, cwd=ROOT):
    r = subprocess.run(list(cmd), input=stdin, capture_output=True, text=True, cwd=cwd, timeout=300)
    return r.returncode, r.stdout + r.stderr


def need(cond, why):
    if not cond:
        raise AssertionError(why)


def clip_3mf():
    path = os.path.join(TMP, "barrinaClip_rev2.3mf")
    if not os.path.exists(path):
        code, out = run("python3", CLIP, TMP)
        need(code == 0 and os.path.exists(path), "barrinaClip_rev2.py didn't write its 3mf: " + out[-200:])
    return path


def t_check():
    code, out = run("python3", f"{SH}/check.py", "--all")
    need(code == 0, "check.py --all blocks: " + out[-300:])


def t_index():
    code, out = run("python3", f"{SH}/index.py", "admin")
    need(code == 0 and "projects/admin/content/todo.md" in out, "admin's index has no todo line")


def t_rules():
    code, out = run("python3", f"{SH}/rules.py", "--find", "config v\\[version\\] loaded")
    need(code == 0 and out.startswith("CLAUDE.md:"), "--find didn't find the First reply rule")
    code, out = run("python3", f"{SH}/rules.py", "--summary")
    need(code == 0 and "CLAUDE.md:" in out, "--summary printed no CLAUDE.md row")
    last = run("git", "log", "-1", "--format=%h", "--grep=^refactor (")[1].strip() or "HEAD~20"
    code, out = run("python3", f"{SH}/rules.py", "--since", last)
    rows = [l for l in out.split("\n")[1:] if l]
    need(code == 0 and out.startswith("id\tfile") and rows and all(l.split("\t")[6] > "2026-10" for l in rows),
         f"--since {last}: no rows, or a row dated before the commit: " + out[:300])
    code, out = run("python3", f"{SH}/rules.py", "--pairs", "--since", last)
    need(code == 0 and out.startswith("# ") and out.count("\n== ") == len(rows) and "\n   " in out,
         f"--pairs --since {last} didn't list every changed row with candidates: " + out[:300])


def t_index_load():
    code, out = run("python3", f"{SH}/index.py", "--load", "admin")
    need(code == 0 and out.startswith("every admin thread at start: CLAUDE.md ") and "  pkg: " in out, "--load admin: " + out[:200])


def t_check_names():
    repo = os.path.join(TMP, "names")  # a scratch clone with a rule file naming a script that doesn't exist
    run("git", "clone", "-q", ROOT, repo)
    skill = os.path.join(repo, ".claude", "skills", "pkg", "SKILL.md")
    open(skill, "a").write("\n- Run shared/scripts/nosuch.py, then gone-script.py; [name]_model.py is a placeholder.\n")
    code, out = run("python3", f"{SH}/check.py", "--all", cwd=repo)
    need("names shared/scripts/nosuch.py, which doesn't exist" in out and "names gone-script.py" in out and "_model.py" not in out,
         "check.py --all didn't report the planted names (or flagged the placeholder): " + out[-400:])
    code, out = run("python3", f"{SH}/check.py", "--all")
    need(not any("names " in l and "doesn't exist" in l for l in out.split("\n")), "check.py --all reports a missing name in the repo: " + out[-300:])


def t_numcheck_dups():
    d = os.path.join(TMP, "dups")
    os.makedirs(d)
    open(os.path.join(d, "a.md"), "w").write("Nozzle 0.6 mm; walls 3 beads; 2026-10-09.\n")
    open(os.path.join(d, "b.md"), "w").write("The 0.6 mm nozzle; 4 drops per gallon; 2026-10-09.\n")
    code, out = run("python3", f"{SH}/numcheck.py", "--dups", f"{d}/a.md", f"{d}/b.md")
    need(code == 0 and out.startswith("0.6 mm: ") and "1 values stated" in out and "2026" not in out, "--dups: " + out)


def t_refactor_prep():
    out_dir = os.path.join(TMP, "prep")
    code, out = run("bash", f"{SH}/refactor-prep.sh", out_dir, "--no-pull", "--no-tests")
    need(code == 0 and "refactor-prep: last refactor commit" in out, "refactor-prep.sh: " + out[-400:])
    for f in ("summary.txt", "rules.tsv", "new-rows.tsv", "pairs.txt", "check.txt", "load.txt", "words.txt", "commits.txt", "changed.txt", "untested.txt", "dups.txt", "env.txt"):
        need(os.path.getsize(os.path.join(out_dir, f)) > 0, f"refactor-prep.sh wrote no {f}")
    need(not os.path.exists(os.path.join(out_dir, "tests.txt")), "--no-tests still ran test.py")


def t_refactor_check():
    diff = os.path.join(TMP, "small.diff")  # one dated learning added to a learnings file
    f = "projects/admin/learnings/claude.md"
    text = open(os.path.join(ROOT, f), encoding="utf-8").read()
    new = text.rstrip("\n") + "\n- refactor-check.sh test line (2026-10-09).\n"
    a, b = os.path.join(TMP, "a.md"), os.path.join(TMP, "b.md")
    open(a, "w", encoding="utf-8").write(text); open(b, "w", encoding="utf-8").write(new)
    d = subprocess.run(["git", "diff", "--no-index", "--", a, b], capture_output=True, text=True).stdout
    open(diff, "w", encoding="utf-8").write(d.replace(f"a{a}", f"a/{f}").replace(f"b{b}", f"b/{f}").replace(a, f"/{f}").replace(b, f"/{f}"))
    code, out = run("bash", f"{SH}/refactor-check.sh", diff, os.path.join(TMP, "rc"))
    need(code == 0 and "refactor-check: ok" in out and "--- check.py" in out, "refactor-check.sh: " + out[-400:])
    open(diff, "w", encoding="utf-8").write(re.sub(r"^ (.*)$", r" not in the file: \1", open(diff, encoding="utf-8").read(), count=1, flags=re.M))
    code, out = run("bash", f"{SH}/refactor-check.sh", diff, os.path.join(TMP, "rc2"))  # a context line no longer matches
    need(code == 1 and "FAILED" in out, "refactor-check.sh passed a diff that doesn't apply: " + out[-300:])


def t_list():
    src = os.path.join(ROOT, "projects", "3dp", "content")
    dst = os.path.join(TMP, "projects", "3dp")
    shutil.copytree(os.path.join(ROOT, "projects", "3dp", "products"), os.path.join(dst, "products"), dirs_exist_ok=True)
    os.makedirs(os.path.join(dst, "content"), exist_ok=True)
    hop = shutil.copy(os.path.join(src, "hopper.list.md"), os.path.join(dst, "content"))
    run("python3", f"{SH}/list.py", "products", hop, "active")
    code, out = run("python3", f"{SH}/list.py", "products", hop, "active")
    need(code == 0 and "added:" not in out, "products added rows twice")
    code, out = run("python3", f"{SH}/list.py", "add", hop, "zz test row")
    need(code == 0 and "| zz test row | pending |" in out, "add didn't give the default status: " + out)
    code, out = run("python3", f"{SH}/list.py", "show", hop)
    rows = [l for l in out.split("\n") if l.startswith("| ") and "---" not in l][1:]
    need(rows and rows[-1].startswith("| zz test row"), "show didn't sort the new pending row last")


def t_lookup():
    if not os.path.exists("/opt/orca/squashfs-root/bin/orca-slicer"):
        return "skip: no Orca at /opt/orca (orca-setup.sh); lookup.py pulls the defaults from it"
    code, out = run("python3", f"{SH}/lookup.py", "Nozzle diameter", "printer")
    need(code == 0 and "mine 0.6 mm (same); default 0.6 mm" in out, "lookup.py didn't show the 0.6 mm nozzle: " + out)
    code, out = run("python3", f"{SH}/lookup.py", "Sparse infill pattern", "process")
    need(code == 0 and "default Cross Hatch" in out, "lookup.py didn't show Orca's default infill pattern: " + out)
    code, out = run("python3", f"{SH}/lookup.py", "--check")
    need(code == 0, "rows in my settings files match no Orca setting: " + out[-300:])


def t_numcheck():
    repo = os.path.join(TMP, "numrepo")  # a scratch repo, so edits in progress in this one don't matter
    os.makedirs(repo)
    f = os.path.join(repo, "a.md")
    open(f, "w").write("Edges at least 1 mm. Overhangs within 45 degrees. Chamfers at 45 degrees.\n")
    for cmd in (["init", "-q"], ["add", "a.md"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "a"]):
        run("git", *cmd, cwd=repo)
    kept = run("python3", f"{SH}/numcheck.py", "a.md", cwd=repo)
    open(f, "w").write("Edges at least 1 mm. Overhangs and chamfers within 45 degrees.\n")
    cut = run("python3", f"{SH}/numcheck.py", "a.md", cwd=repo)
    allowed = run("python3", f"{SH}/numcheck.py", "--repeats", "45", "a.md", cwd=repo)
    need(kept[0] == 0 and cut[0] == 1 and "lost: 45" in cut[1] and allowed[0] == 0,
         f"numcheck.py: unchanged {kept}, a cut repeat {cut}, the same with --repeats {allowed}")


def t_pretool():
    deny = run("python3", f"{SH}/pretool.py", stdin=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit --no-verify -m x"}}))[1]
    allow = run("python3", f"{SH}/pretool.py", stdin=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}}))[1]
    need('"deny"' in deny and not allow.strip(), "pretool.py didn't deny --no-verify and allow git status")


def t_setup_env():
    for _ in range(180):  # the start hook's background install (about 45 s)
        if os.path.exists("/tmp/setup-env.done"):
            break
        time.sleep(1)
    else:
        return "skip: the start hook's install didn't finish in 3 minutes (log /tmp/setup-env.log)"
    if not os.path.exists("/opt/orca/slice"):
        run("bash", f"{SH}/setup-env.sh", "orca")  # about 7 s; the slice test needs it too
    code, out = run("bash", f"{SH}/setup-env.sh", "orca")
    need(code == 0 and not out.strip(), "setup-env.sh reinstalled although both were done: " + out[-200:])


def t_dotgrid():
    photo = os.path.join(TMP, "dots.png")  # a clean 5 mm grid at 10 px/mm, drawn in its own process
    run("python3", "-I", "-c", "import numpy as np, cv2; img = np.full((1200, 1600), 255, np.uint8); "
        "[cv2.circle(img, (x, y), 4, 0, -1) for y in range(60, 1150, 50) for x in range(60, 1550, 50)]; "
        f"cv2.imwrite({photo!r}, img)")
    code, out = run("python3", f"{SH}/dotgrid.py", photo, cwd=TMP)  # as dot-paper.md runs it
    need(code == 0, "dotgrid.py failed on a clean grid: " + out.strip().split("\n")[-1][:200])


def t_dpreqs():
    code, out = run("python3", f"{P3}/dpreqs.py", "--json")
    need(code == 0 and len(json.loads(out)) > 20, "dpreqs.py --json listed under 20 requirements")
    n = {a: len(json.loads(run("python3", f"{P3}/dpreqs.py", "--audit", a, "--json")[1])) for a in ("form", "function")}
    need(n["form"] + n["function"] == len(json.loads(out)) + 3, "dpreqs.py --audit halves don't split the list (General in both): %s" % n)


def t_dpcheck_dpgrid():
    dc, inv, grid = (os.path.join(TMP, n) for n in ("dc.json", "inv.json", "grid.tsv"))
    code, out = run("python3", f"{P3}/dpcheck.py", clip_3mf(), "--json", dc)
    need(os.path.exists(dc), "dpcheck.py wrote no --json: " + out[-300:])
    json.dump([{"id": "E1", "kind": "edge", "text": "front edge"}], open(inv, "w"))
    code, out = run("python3", f"{P3}/dpgrid.py", "make", dc, inv, "-o", grid, "--script", CLIP)
    need(code == 0 and "barrinaClip_rev2.py " in open(grid).readline(), "dpgrid.py header lacks the script: " + out[-200:])
    code, out = run("python3", f"{P3}/dpgrid.py", "make", dc, inv, "-o", grid, "--script", CLIP, "--audit", "form")
    need(code == 0 and open(grid).readline().startswith("# dp form audit grid"), "dpgrid.py --audit form header: " + out[-200:])
    code, out = run("python3", f"{P3}/dpcheck.py", clip_3mf(), "--only", "edges", "--inventory", inv)
    items = json.load(open(inv)) if os.path.exists(inv) else []
    need(any(i["kind"] == "edge" and "2.2" in i.get("cells", {}) for i in items), "dpcheck.py --inventory listed no measured edges: " + out[-300:])
    code, out = run("python3", f"{P3}/dpgrid.py", "make", dc, inv, "-o", grid, "--script", CLIP)
    need(code == 0 and "(dpinv)" in open(grid).read(), "dpgrid.py didn't write the inventory's measured cells: " + out[-200:])


def t_write3mf():
    code, out = run("python3", "-c", f"""
import sys, numpy as np; sys.path.insert(0, {P3!r}); import write3mf as W, zipfile
V = np.array([[0,0,0],[10,0,0],[10,10,0],[0,10,0],[0,0,5],[10,0,5],[10,10,5],[0,10,5]], float)
T = np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
s = W.base({os.path.join(ROOT, 'projects/3dp/products/barrina-clips/build/barrinaClip_settings_base.json')!r})
W.write({os.path.join(TMP, 'box.3mf')!r}, [W.Obj('box', [W.Part(V, T)], at=[(128, 128)])], s)
print(len(zipfile.ZipFile({os.path.join(TMP, 'box.3mf')!r}).namelist()))""")
    need(code == 0 and int(out.split()[-1]) > 3, "write3mf.py didn't write a 3mf: " + out[-300:])


def t_render3d():
    code, out = run("python3", "-c", f"""
import sys; sys.path.insert(0, {P3!r}); import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import render3d as R
R.FACES.clear(); R.box(0, 10, 0, 10, 0, 5, R.BONE)
fig, ax = plt.subplots(); R.view(ax, title='box'); R.save(fig, {os.path.join(TMP, 'box.png')!r})""")
    need(code == 0 and os.path.exists(os.path.join(TMP, "box.png")) and "LAYOUT OK" in out, "render3d.py: " + out[-300:])
    code, out = run("python3", "-c", f"""
import sys; sys.path.insert(0, {P3!r}); import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import render3d as R
fig, (a, b) = plt.subplots(1, 2, figsize=(8, 4)); a.text(0.5, 0.5, 'ok'); b.text(0.5, 0.5, 'ok too')
print('clean', R.layout_check(fig))
a.annotate('callout across', (0.5, 0.5), xytext=(1.6, 0.5), annotation_clip=False)
print('cross', R.layout_check(fig))""")
    need(code == 0 and "clean []" in out and "cross ['crosses into another panel: 'callout across'" in out.replace('"', "'"),
         "render3d.py panel check: " + out[-300:])


def t_slice_gcode():
    if not os.path.exists("/opt/orca/slice"):
        run("bash", f"{SH}/setup-env.sh", "orca")
        need(os.path.exists("/opt/orca/slice"), "setup-env.sh orca didn't install OrcaSlicer (log /tmp/setup-env.log)")
    out_dir = os.path.join(TMP, "slice")
    code, out = run("/opt/orca/slice", clip_3mf(), out_dir)
    need('"Success."' in out, "slice failed: " + out[-300:])
    note = "ok"
    if "plate_1.gcode: model printing time" not in out:
        need("G-code header" not in open("/opt/orca/slice").read(), "slice printed no plate summary")
        note = "ok (this container's slicer predates the plate summary)"
    code, out = run("python3", f"{P3}/gcodeTrace.py", os.path.join(out_dir, "plate_1.gcode"), "--centers", "128,128")
    need(code == 0 and out.strip(), "gcodeTrace.py failed: " + out[-300:])
    g = os.path.join(out_dir, "plate_1.gcode")
    code, out = run("python3", f"{P3}/gcodeStats.py", "layers", g, "--layers", "0-1")
    need(code == 0 and "-- layer 0" in out and "-- layer 1" in out and "-- layer 2" not in out and " len " in out,
         "gcodeStats.py layers: " + out[-300:])
    code, out = run("python3", f"{P3}/gcodeStats.py", "runs", g, "--feature", "Outer wall", "--list", "3")
    need(code == 0 and re.search(r"Outer wall: \d+ runs, \d+ under", out), "gcodeStats.py runs: " + out[-300:])
    return note


def t_meshmeasure():
    code, out = run("python3", "-c", f"""
import sys; sys.path.insert(0, {P3!r}); import trimesh, meshmeasure as M
trimesh.creation.annulus(18, 20, 10, sections=256).export({os.path.join(TMP, 'tube.stl')!r})
m, H = M.load_part({os.path.join(TMP, 'tube.stl')!r})
runs = M.true_runs(lambda x: M.solid_top(m, x, 0, H), -25, 25, n=200)
print(H, M.outer_r(m, 5), M.inner_r(m, 5), M.lean_deg(m, [2, 5, 8])[0], len(runs), runs[0][0], runs[0][1])
print(M.load_part({clip_3mf()!r})[1])""")
    v = [float(x) for x in out.split()] if code == 0 else []
    need(len(v) == 8 and abs(v[0] - 10) < 1e-6 and abs(v[1] - 20) < 0.01 and abs(v[2] - 18) < 0.01 and abs(v[3]) < 0.01
         and v[4] == 2 and abs(v[5] + 20) < 0.01 and abs(v[6] + 18) < 0.01 and v[7] > 0,
         "meshmeasure.py: tube 20/18 x 10 measured wrong, or the clip 3mf didn't load: " + out[-300:])


def t_settingsdiff():
    import zipfile
    a = clip_3mf()
    b = os.path.join(TMP, "clip_changed.3mf")
    with zipfile.ZipFile(a) as zi, zipfile.ZipFile(b, "w") as zo:
        for n in zi.namelist():
            d = zi.read(n)
            if n == "Metadata/project_settings.config":
                j = json.loads(d); j["sparse_infill_density"] = "37%"; d = json.dumps(j).encode()
            zo.writestr(n, d)
    code, same = run("python3", f"{P3}/settingsdiff.py", a, a, "1")
    code2, out = run("python3", f"{P3}/settingsdiff.py", a, b, "1")
    need(code == 0 and "0 differences in all" in same, "settingsdiff.py: a file differs from itself: " + same[-300:])
    need(code2 == 0 and "sparse_infill_density: A" in out and "| B '37%'" in out and re.search(r"\n[1-9]\d* differences in all", out),
         "settingsdiff.py missed a changed project setting: " + out[-300:])


def t_work():
    import random
    random.seed(1)
    def report(path, n):
        rows = ["Search term\tCampaign\tImpr.\tClicks\tCost\tConversions"]
        for i in range(n):
            rows.append(f"dental plan {i % 40}\tDD_{random.choice(['NB', 'Brand', 'CO'])}_Enroll_x\t{random.randint(1, 900)}\t{random.randint(0, 9)}\t{random.random() * 20:.2f}\t{random.randint(0, 2)}")
        open(path, "w", encoding="utf-16").write("Search terms report\n\"Sep 1, 2026 - Sep 30, 2026\"\n" + "\n".join(rows) + "\n")
    a, b = os.path.join(TMP, "a.tsv"), os.path.join(TMP, "b.tsv")
    report(a, 200); report(b, 250)
    w = os.path.join(ROOT, "projects", "work", "scripts")
    code, out = run("python3", f"{w}/sqr_compare_rev1.py", a, b, os.path.join(TMP, "cmp.xlsx"))
    need(code == 0 and "impr totals" in out, "sqr_compare_rev1.py: " + out[-300:])
    code, out = run("python3", f"{w}/NB_Negatives_List_Map_rev1.py", a, os.path.join(TMP, "nb.xlsx"))
    need(code == 0 and os.path.exists(os.path.join(TMP, "nb.xlsx")), "NB_Negatives_List_Map_rev1.py: " + out[-300:])


def t_commit_msg():
    hook, msg = os.path.join(ROOT, ".githooks", "commit-msg"), os.path.join(TMP, "msg")
    open(msg, "w").write("test.py: a change (admin)\n")
    good = run("bash", hook, msg)[0]
    open(msg, "w").write("a change\n")
    bad = run("bash", hook, msg)[0]
    need(good == 0 and bad != 0, "commit-msg didn't pass \"[file]: [change] ([project])\" and block a bare message")


TESTS = [(n[2:], f) for n, f in list(globals().items()) if n.startswith("t_")]
COVERS = {  # test: the scripts it runs (by file name)
    "check": ["check.py", "pre-commit"], "index": ["index.py"], "rules": ["rules.py"], "list": ["list.py"],
    "lookup": ["lookup.py", "orcadefaults.py"], "numcheck": ["numcheck.py"], "pretool": ["pretool.py"], "setup_env": ["setup-env.sh"],
    "dotgrid": ["dotgrid.py"], "dpreqs": ["dpreqs.py"], "dpcheck_dpgrid": ["dpcheck.py", "dpgrid.py", "dpinv.py"],
    "write3mf": ["write3mf.py"], "render3d": ["render3d.py"], "slice_gcode": ["orca-setup.sh", "gcodeTrace.py", "gcodeStats.py"],
    "meshmeasure": ["meshmeasure.py"], "settingsdiff": ["settingsdiff.py"],
    "work": ["NB_Negatives_List_Map_rev1.py", "sqr_compare_rev1.py"], "commit_msg": ["commit-msg"],
    "index_load": ["index.py"], "check_names": ["check.py"], "numcheck_dups": ["numcheck.py"],
    "refactor_prep": ["refactor-prep.sh"], "refactor_check": ["refactor-check.sh"],
}
NOT_RUN = ["pull.sh", "save.sh", "undo.sh", "session-start.sh", "test.py"]  # they push or pull, or are this file


def covers():
    """Print each test's scripts, then the scripts under shared/scripts, projects/*/scripts and the hooks no test runs."""
    import glob
    for t, scripts in COVERS.items():
        print(f"{t}\t{' '.join(scripts)}")
    covered = {s for ss in COVERS.values() for s in ss} | set(NOT_RUN)
    found = sorted(os.path.basename(f) for g in ("shared/scripts/*", "projects/*/scripts/*", ".githooks/*", ".claude/hooks/*")
                   for f in glob.glob(os.path.join(ROOT, g)) if os.path.isfile(f))
    print("not run (push, pull or this file): " + " ".join(NOT_RUN))
    print("untested: " + (" ".join(s for s in found if s not in covered) or "none"))


def tests_for(scripts):
    names = {os.path.basename(s) for s in scripts}
    if "test.py" in names:
        return [t for t, _ in TESTS]
    return [t for t, ss in COVERS.items() if names & set(ss)]


def main(argv):
    if argv[:1] == ["--covers"]:
        return covers()
    if argv[:1] == ["--for"]:
        return print(" ".join(tests_for(argv[1:])))
    picked = [(n, f) for n, f in TESTS if not argv or any(a in n for a in argv)]
    failed = skipped = 0
    try:
        for name, f in picked:
            t = time.time()
            try:
                note = f() or "ok"
            except Exception as e:  # an assertion or a crash in the test itself
                note, failed = f"FAIL: {e}", failed + 1
            skipped += note.startswith("skip")
            print(f"{name:16} {time.time() - t:6.2f} s  {note}")
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    passed = len(picked) - failed - skipped
    print(f"{passed} of {len(picked)} passed" + (f", {failed} failed" if failed else "") + (f", {skipped} skipped" if skipped else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
