"""picture.py: a 3dp picture in one command, always drawn from the model's own mesh (redesign 2026-10-05, section 11).

  picture.py MODEL [--before MODEL] [--set NAME=VALUE ...] [--change [words: ]NAME=VALUE[,NAME=VALUE] ...]
             [--master] [--letters] [--with MESH ...] [--spot x,y,z,r] [--views iso,top,section:x=40] [--labels labels.json] [--title TEXT]
             [--out out.png] [--args "the build script's own arguments"] [--width 4000] [--check 1200]

MODEL is a 3mf, an STL or a build script. A build script runs with write3mf.py's --preview, so nothing is built, and
--set gives it proposed values (write3mf.py preview); with --set and no --before, the script's own values are the before.
Views: iso and iso-back (shaded 3D), top, bottom, front, back, left, right (flat, drawn as vector shapes),
section:x=40 (or y=, z=; the cut through the model at that plane, vector), close:x,y,z,r (a 3D close-up framed r mm
around a point), exploded (each separate body pulled apart from the others). Default: iso,iso-back,top.
--before: each view is drawn before and after at one scale, the changed material colored (added green in the after
panels, removed red in the before panels), plus a section through the changed spot unless --views names a section:
there, kept material is pale, added green and removed red. Default views with --before: iso.
--change (build scripts only, repeatable): one numbered panel per change on one sheet, each against the script's own
values, added material green and removed material red where it was; the first panel is the model as it is now, and
each view in --views (default iso) is one row.
Change panel titles and --set's sheet title (section 11 item 8) give each value's plain name with its old and new
value, "drop behind the steel: 2.0 → 2.5": the name is the string's leading "words: ", else the comment on the
script's NAME = line up to its first : ; ( or =, else NAME (describe()).
--master (section 11 item 7, lean): each distinct printed part once, by its 3mf name, in a row; a number on each in the
3D view and a legend line under the title with each part's size as printed (x × y × z mm, copies counted); a single
part gets measured x, y and z lines instead of a number. write3mf.py draws [file]_master.png this way on every build.
--letters letters those panels A, B, C for options to choose between (build-3dp, Comparing options), not numbers.
--with (repeatable): a 3mf or STL of what holds the part (a mount, a pot, a bar), drawn gray in every panel; a section
cuts it on the same plane, framed on the part, so a rod or wire through a bore shows where it sits (2026-10-17).
--spot x,y,z,r: the part's own faces within r mm of the point colored bright amber in every 3D and flat panel, for a
picture about one spot (build-3dp); pair it with a close:x,y,z,r view, whose title says where it is and which way it
looks (build-3dp's spot pictures; audit 2026-10-17).
labels.json: [{"text": "rim", "at": [x, y, z], "off": [30, 20], "views": ["iso"]},
              {"dim": [[x, y, z], [x, y, z]], "off": [0, 0, 5]}]
  "off" is points for a callout, a 3D vector (mm) for a dimension line, whose number is the measured distance.
  "va" (callouts): where the text sits on its end of the line, "top" hanging below it; default "baseline".
  "views" names panels (a view name, or "before:iso", "after:iso", "change 2", "option B"); default every panel but sections.
Writes out.png (width px wide, 3D views drawn at 3x and averaged down), out_check.png (check px wide: the copy
Claude looks at, so checking costs the same at any width) and, when a flat view or section is on the sheet, out.svg
(sharp at any zoom there; 3D panels are embedded images). Prints the changed volume and where it is, the files
written and LAYOUT OK or LAYOUT FLAG (render3d.layout_check). The 3D viewer is zoompage.py.
Needs numpy, trimesh, shapely, scipy, matplotlib, pillow and manifold3d (shared/scripts/setup-env.sh installs them).
"""
import argparse, hashlib, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render3d as R

R.MIN_PX = 0                                   # picture.py sets each panel's scale itself
ADD = np.array([0.30, 0.72, 0.36])             # added material
REM = np.array([0.88, 0.30, 0.24])             # removed material
GRAY = np.array([0.62, 0.64, 0.68])            # --with meshes: what holds the part
SPOT = np.array([1.0, 0.70, 0.10])             # --spot: the spot a picture is about
CUT = R.BONE * 0.45 + 0.52                     # a cut face, as render3d draws one
SS = 3                                         # supersampling of 3D views
EYES = {"iso": ((-1.0, -1.6, 0.8), "3D view"), "iso-back": ((1.0, 1.6, 0.8), "3D view from the back"),
        "top": ((0, -1e-4, 1.0), "Top"), "bottom": ((0, 1e-4, -1.0), "Bottom"), "front": ((0, -1.0, 0), "Front"),
        "back": ((0, 1.0, 0), "Back"), "left": ((-1.0, 0, 0), "Left side"), "right": ((1.0, 0, 0), "Right side")}
FLAT = {"top", "bottom", "front", "back", "left", "right"}
SEC_AXES = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}   # a section at x = c is drawn in (y, z), and so on


def load(path, values=None, out=None, args=()):
    """(file drawn, [(name, trimesh)]) from a 3mf or STL, or a build script run with --preview, values and its own args."""
    import trimesh
    from dpcheck import load_3mf, load_stl
    if path.endswith(".py"):
        import write3mf as W
        stls = W.preview(path, values, out, args)
        if len(stls) > 1:
            print("picture: the script wrote %d files; drawing %s" % (len(stls), os.path.basename(stls[0])))
        path = stls[0]
    items, _ = load_3mf(path) if path.lower().endswith(".3mf") else load_stl(path)
    return path, [(it["over"].get("name", it["name"]), trimesh.Trimesh(it["V"], it["T"])) for it in items]


def whole(meshes):
    import trimesh
    return trimesh.util.concatenate([m for _, m in meshes])


def solid_diff(a, b):
    """Material in a and not in b, as a mesh (slivers from shared faces dropped), or None when the boolean fails."""
    import trimesh
    try:
        d = trimesh.boolean.difference([a, b], engine="manifold")
    except Exception as ex:                    # not a closed volume
        print("picture: changed material not colored (%s)" % ex)
        return None
    if d is None or not len(d.faces):
        return trimesh.Trimesh()
    keep = [p for p in d.split(only_watertight=False) if abs(p.volume) > 1e-3 and min(p.extents) > 0.01]
    return trimesh.util.concatenate(keep) if keep else trimesh.Trimesh()


def changed_spot(parts):
    """A point on the changed material nearest its center, and the horizontal axis across which it runs longest."""
    import trimesh
    parts = [p for p in parts if p is not None and len(p.faces)]
    if not parts:
        return None
    m = trimesh.util.concatenate(parts)
    c = m.center_mass if m.is_volume else m.centroid
    p = c if m.is_volume and m.contains([c])[0] else m.vertices[np.argmin(np.linalg.norm(m.vertices - c, axis=1))]
    ext = m.extents
    return p, ("y" if ext[1] >= ext[0] else "x")   # cut across the longer run, so the cut shows the profile


def explode(meshes):
    """Bodies moved apart: each away from the assembly's center, all by one factor, raised until no two bounding boxes
    overlap; bodies at the center move up, stacked in order."""
    bodies = []
    for _, m in meshes:
        bodies += list(m.split(only_watertight=False)) if len(meshes) == 1 else [m]
    if len(bodies) < 2:
        return [b.copy() for b in bodies]
    B = np.array([b.bounds for b in bodies]); C = B.mean(1); c0 = C.mean(0); size = (B[:, 1] - B[:, 0]).max()
    D = C - c0
    mid = np.linalg.norm(D, axis=1) < 0.05 * size
    D[mid] = 0; D[mid, 2] = np.arange(mid.sum()) * size    # stacked up in their order
    for k in (0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4):
        lo, hi = B[:, 0] + k * D, B[:, 1] + k * D
        hit = (lo[:, None] < hi[None] - 0.5) & (lo[None] < hi[:, None] - 0.5)
        if not (hit.all(2) & ~np.eye(len(B), dtype=bool)).any():
            break
    out = []
    for b, d in zip(bodies, D):
        b = b.copy(); b.apply_translation(k * d); out.append(b)
    return out


def master(meshes, stem=""):
    """The master sheet's model (redesign 2026-10-05, section 11 item 7, lean): each distinct printed part once, by its
    3mf name (less a leading "[stem]_"), in a row along x in print orientation; a number on each part; its legend line (name, copies, size); and,
    for a single part, its overall sizes as measured dimension lines. Returns (meshes, labels, legend)."""
    seen = {}
    for n, m in meshes:
        n = os.path.splitext(os.path.basename(n))[0] if os.sep in n else n     # an STL's item name is its path
        n = n[len(stem) + 1:] if stem and n.startswith(stem + "_") else n
        seen.setdefault(n, [m, 0])[1] += 1
    out, labels, legend, x = [], [], [], 0.0
    gap = 0.15 * max(float(np.max(m.extents)) for m, _ in seen.values())
    rise = 0.07 * (sum(float(m.extents[0]) for m, _ in seen.values()) + gap * (len(seen) - 1))   # scales with the row
    for k, (n, (m, cnt)) in enumerate(seen.items(), 1):
        m = m.copy(); lo, hi = m.bounds
        m.apply_translation([x - lo[0], -(lo[1] + hi[1]) / 2, -lo[2]]); x += hi[0] - lo[0] + gap
        e = m.extents; lo, hi = m.bounds
        legend.append("%s%s%s: %s mm" % ("%d " % k if len(seen) > 1 else "", n, " (x%d)" % cnt if cnt > 1 else "",
                                         " x ".join(("%.2f" % v).rstrip("0").rstrip(".") for v in e)))
        if len(seen) > 1:
            labels.append({"text": str(k), "at": [(lo[0] + hi[0]) / 2, hi[1], hi[2] + rise], "off": [0, 0],
                           "va": "top", "views": ["iso"]})     # hung from above its back top edge, which the frame holds
        out.append((n, m))
    if len(seen) == 1:                         # x, y and z along edges the iso eye sees, measured
        lo, hi = out[0][1].bounds; d = 0.12 * float(np.max(out[0][1].extents))
        labels += [{"dim": [[lo[0], lo[1], lo[2]], [hi[0], lo[1], lo[2]]], "off": [0, -d, 0], "views": ["iso"]},
                   {"dim": [[lo[0], lo[1], lo[2]], [lo[0], hi[1], lo[2]]], "off": [-d, 0, 0], "views": ["iso"]},
                   {"dim": [[hi[0], lo[1], lo[2]], [hi[0], lo[1], hi[2]]], "off": [d, 0, 0], "views": ["iso"]}]
    import textwrap
    return out, labels, "\n".join(textwrap.wrap("Sizes as printed, x × y × z. " + "; ".join(legend), 150))


# ---- flat (vector) views and sections

def _patch(poly, **kw):
    """A matplotlib patch for a shapely (Multi)Polygon, holes included."""
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    verts, codes = [], []
    for p in getattr(poly, "geoms", [poly]):
        for ring in [p.exterior] + list(p.interiors):
            xy = np.asarray(ring.coords)
            verts += xy.tolist(); codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
    return PathPatch(Path(verts, codes), **kw) if verts else None


def _fill(segs):
    """The area closed by 2D segments (n, 2, 2), even-odd (holes stay open), as one shapely shape."""
    import shapely
    from shapely.geometry import MultiLineString, Polygon
    from shapely.ops import polygonize, unary_union
    if not len(segs):
        return Polygon()
    faces = list(polygonize(unary_union(MultiLineString(list(np.round(segs, 4))))))   # rounded so ends meet
    keep = []
    for f in faces:                            # material lies inside an odd number of outer rings
        pt = f.representative_point()
        if sum(Polygon(g.exterior).contains(pt) for g in faces) % 2:
            keep.append(f)
    return shapely.union_all(keep) if keep else Polygon()


def flat_regions(scene, eye, angle=20.0):
    """Shapes for an axis-aligned view: the faces that look toward the eye, joined into smooth regions (neighbors
    under angle degrees apart), each one shapely shape with its shade, farthest first, for drawing over each other."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    e, right, up = R.camera(eye)
    Lt = np.array([0.3, -0.7, 1.0]); Lt /= np.linalg.norm(Lt)
    out = []
    for m, col in scene:
        N = m.face_normals; seen = np.nonzero(N @ e > 0.02)[0]
        if not len(seen):
            continue
        idx = -np.ones(len(N), int); idx[seen] = np.arange(len(seen))
        A = m.face_adjacency; ok = (idx[A[:, 0]] >= 0) & (idx[A[:, 1]] >= 0) & (m.face_adjacency_angles < math.radians(angle))
        g = coo_matrix((np.ones(ok.sum()), (idx[A[ok, 0]], idx[A[ok, 1]])), shape=(len(seen), len(seen)))
        n, lab = connected_components(g, directed=False)
        F = m.faces[seen]; V2 = np.stack([m.vertices @ right, m.vertices @ up], -1)
        shade = 0.45 + 0.40 * np.maximum(0, N[seen] @ Lt) + 0.25 * np.maximum(0, N[seen] @ e)
        depth = (m.vertices[F] @ e).mean(1)
        E = np.sort(np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), 1)
        key = np.c_[np.tile(lab, 3), E]          # an edge used by one face of its region is that region's outline
        u, cnt = np.unique(key, axis=0, return_counts=True)
        rim = u[cnt == 1]; order = np.argsort(rim[:, 0], kind="stable"); rim = rim[order]
        cuts = np.searchsorted(rim[:, 0], np.arange(n + 1))
        sh = np.bincount(lab, shade, n) / np.maximum(np.bincount(lab, None, n), 1)
        dp = np.bincount(lab, depth, n) / np.maximum(np.bincount(lab, None, n), 1)
        for k in range(n):
            r = rim[cuts[k]:cuts[k + 1]]
            shape = _fill(V2[r[:, 1:]])
            if shape.is_empty:
                continue
            out.append((float(dp[k]), shape, np.clip(np.asarray(col) * float(sh[k]), 0, 1)))
    out.sort(key=lambda t: t[0])
    return out


def section(m, axis, at, quiet=False):
    """The material of mesh m cut by the plane axis = at, as a shapely shape in the section's two axes."""
    from trimesh.intersections import mesh_plane
    n = np.zeros(3); n["xyz".index(axis)] = 1.0
    seg = mesh_plane(m, n, n * at)
    shape = _fill(seg[:, :, list(SEC_AXES[axis])] if len(seg) else [])
    if shape.is_empty and not quiet:
        k = "xyz".index(axis)
        print("picture: the section at %s = %g cuts nothing (the model spans %s %.1f to %.1f)" % (axis, at, axis, *m.bounds[:, k]))
    return shape


def grid_step(span):
    for s in (0.5, 1, 2, 5, 10, 20, 50, 100):
        if span / s <= 14:
            return s
    return 200


# ---- the sheet

def spot_faces(m, c, r):
    """Mesh m's surface within r mm of point c: faces touching the sphere's box, cut into pieces under r / 8 mm, kept
    where a piece's center lies within r (so a big face colors only its part inside)."""
    import trimesh
    T = m.triangles
    hit = np.nonzero((T.min(1) <= c + r).all(1) & (T.max(1) >= c - r).all(1))[0]
    if not len(hit):
        return None
    V, F = trimesh.remesh.subdivide_to_size(m.vertices, m.faces[hit], max_edge=r / 8, max_iter=12)
    keep = np.linalg.norm(V[F].mean(1) - c, axis=1) < r
    return trimesh.Trimesh(V, F[keep], process=False) if keep.any() else None


def view(v, meshes, scene, tag, title):
    """A panel of view v: scene drawn as is, except exploded (meshes pulled apart) and close (iso, framed on a spot)."""
    if v == "exploded":
        return dict(kind="3d", view=v, tag=tag, title=title, eye=EYES["iso"][0], scene=[(b, R.BONE) for b in explode(meshes)])
    if v.startswith("close:"):
        x, y, z, r = (float(t) for t in v.split(":", 1)[1].split(","))
        _, right, up = R.camera(EYES["iso"][0]); c = np.array([x, y, z])
        return dict(kind="3d", view=v, tag=tag, title=title, eye=EYES["iso"][0], scene=scene,
                    frame=(c @ right - r, c @ right + r, c @ up - r, c @ up + r))
    return dict(kind="flat" if v in FLAT else "3d", view=v, tag=tag, title=title, scene=scene)


def view_name(v):
    if v.startswith("close:"):                 # drawn from the iso eye (view())
        return "Close-up at (%s), seen from the front left, above" % ", ".join(v.split(":", 1)[1].split(",")[:3])
    return "Exploded" if v == "exploded" else EYES[v][1]


def panel_list(a, before, views, changes, letters=False):
    """Each panel: dict(kind, title, view, frame group, scene or shapes)."""
    P = []
    secs = [v for v in views if v.startswith("section:")]
    flat = [v for v in views if not v.startswith("section:")]
    if changes:                                # one row per view: now, then each change
        now = whole(a[1]); row = []
        for k, (label, m, f) in enumerate(changes, 1):
            add, rem = solid_diff(m, now), solid_diff(now, m)
            print("picture: change %d (%s): " % (k, label) + ("changed volume unknown" if add is None or rem is None
                  else "added %.1f mm3, removed %.1f mm3" % (vol(add), vol(rem))))
            n = chr(64 + k) if letters else str(k)
            row.append((n, label, f, m, [(x, c) for x, c in ((add, ADD), (rem, REM)) if x is not None and len(x.faces)] + [(m, R.BONE)]))
        for i, v in enumerate(flat):
            P.append(view(v, a[1], [(now, R.BONE)], "now", "Now" if not i else "Now: " + view_name(v).lower()))
            for n, label, f, m, sc in row:
                P.append(dict(view(v, [("", m)], sc, ("option " if letters else "change ") + n,
                                   "%s  %s" % (n, label if not i else view_name(v).lower())), src=f))
        P[0]["cols"] = 1 + len(changes)
        return P
    if before is None:
        for v in views:
            if v.startswith("section:"):
                ax, at = v.split(":", 1)[1].split("="); at = float(at); sh = section(whole(a[1]), ax, at)
                if not sh.is_empty:                # an empty cut is left off the sheet (section() says so)
                    P.append(dict(kind="section", view=v, tag=v, title="Section at %s = %g" % (ax, at), axis=ax, at=at, layers=[(sh, CUT)]))
            else:
                P.append(view(v, a[1], [(whole(a[1]), R.BONE)], v, view_name(v)))
        return P
    A, B = whole(a[1]), whole(before[1])
    add, rem = solid_diff(A, B), solid_diff(B, A)
    spot = changed_spot([add, rem])
    if add is None or rem is None:
        print("picture: the changed volume is unknown, so no section is added; name one with --views section:x=...")
    elif spot is None:
        print("picture: no change found between the two models")
    else:
        print("picture: added %.1f mm3, removed %.1f mm3, nearest the change's center at (%.2f, %.2f, %.2f)"
              % (vol(add), vol(rem), *spot[0]))
    ae = [(x, ADD) for x in [add] if x is not None and len(x.faces)]
    re = [(x, REM) for x in [rem] if x is not None and len(x.faces)]
    for v in flat:
        name = view_name(v); name = name[0].lower() + name[1:]
        P.append(view(v, before[1], re + [(B, R.BONE)], "before:" + v, "Before: " + name))
        P.append(view(v, a[1], ae + [(A, R.BONE)], "after:" + v, "After: " + name))
    if not secs and spot is not None:
        p, ax = spot; secs = ["section:%s=%.2f" % (ax, p["xyz".index(ax)])]
    if len(flat) > 1:
        P[0]["cols"] = 2                       # each view's before and after side by side
    for v in secs:
        ax, at = v.split(":", 1)[1].split("="); at = float(at)
        sa, sb = section(A, ax, at), section(B, ax, at)
        if sa.is_empty and sb.is_empty:
            continue
        P.append(dict(kind="section", view=v, tag=v, title="Section at %s = %g, before and after" % (ax, at), axis=ax, at=at,
                      layers=[(sa.intersection(sb), CUT), (sa.difference(sb), ADD), (sb.difference(sa), REM)]))
    return P


def vol(m):
    return 0.0 if m is None or not len(m.faces) else abs(float(m.volume))


def applies(L, p):
    """Whether label L goes on panel p: the panels its "views" name, else every panel but sections."""
    want = L.get("views")
    return p["kind"] != "section" if want is None else bool({p["tag"], p["view"]} & set(want))


def label_points(p, labels):
    """The 3D points panel p's labels and dimension lines sit on, so the frame holds them."""
    pts = []
    for L in labels:
        if applies(L, p):
            if "at" in L:
                pts.append(L["at"])
            if "dim" in L:
                off = np.asarray(L.get("off", (0, 0, 0)), float)
                pts += [np.asarray(q, float) + o for q in L["dim"] for o in (0 * off, 1.5 * off)]   # 1.5: room for its number
    return np.array(pts, float).reshape(-1, 3)


def frame_of(p, pad, labels=()):
    X = label_points(p, labels)
    if p["kind"] == "section":
        b = [g.bounds for g, _ in p["layers"] if not g.is_empty]
        i, j = SEC_AXES[p["axis"]]
        b += [(q[i], q[j], q[i], q[j]) for q in X]
        b = np.array(b); return (b[:, 0].min() - pad, b[:, 2].max() + pad, b[:, 1].min() - pad, b[:, 3].max() + pad)
    if "frame" in p:
        return p["frame"]
    eye = p.get("eye") or EYES[p["view"]][0]
    return R.fit(eye, pad, faces=[(t, None, None, None) for t in [m.vertices[m.faces].reshape(-1, 3) for m, _ in p["scene"]] + [X] if len(t)])


def draw(model, before=None, views=None, changes=None, labels=None, title=None, out="picture.png", width=4000, check=1200, src=None,
         letters=False, context=(), spot=None, subtitle=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    views = views or (["iso"] if (before or changes) else ["iso", "iso-back", "top"])
    P = panel_list(model, before, views, changes, letters)
    for p in P:                                # what holds the part, gray, in every panel
        if p["kind"] == "section":             # cut on the same plane, clipped to the part's frame (learnings/design)
            p["ctx"] = [s for s in (section(m, p["axis"], p["at"], quiet=True) for m in context) if not s.is_empty]
        else:
            p["scene"] = p["scene"] + [(m, GRAY) for m in context]
            if spot is not None:               # the spot's own faces, bright, drawn first so they win over the part's
                near = [spot_faces(m, np.asarray(spot[:3], float), float(spot[3])) for m, col in p["scene"] if col is R.BONE]
                p["scene"] = [(m, SPOT) for m in near if m is not None] + p["scene"]
    ext = max(float(np.max(m.extents)) for p in P if p["kind"] != "section" for m, _ in p["scene"]) if any(
        p["kind"] != "section" for p in P) else 50.0
    pad = 0.04 * ext
    labels = labels or []
    frames = {}
    for p in P:                                # panels of one view share one frame and scale
        f = frame_of(p, pad, labels or ()); g = frames.get(p["view"])
        frames[p["view"]] = f if g is None else (min(f[0], g[0]), max(f[1], g[1]), min(f[2], g[2]), max(f[3], g[3]))
    n = len(P); cols = P[0].get("cols") or (2 if n == 4 else min(n, 3)); rows = math.ceil(n / cols)
    dpi = width / 13.33; pt = dpi / 72.0
    M = 0.012 * width; colw = (width - M * (cols + 1)) / cols
    ppm = {v: min(colw / (f[1] - f[0]), 1.1 * colw / (f[3] - f[2])) for v, f in frames.items()}
    import textwrap                            # panel titles and captions wrap to their column
    tw, cw = max(12, int(colw / (13 * pt * 0.58))), max(20, int(colw / (9 * pt * 0.5)))
    for p in P:
        p["title"] = "\n".join(textwrap.wrap(p["title"], tw, break_long_words=False, break_on_hyphens=False))
    tl = max(p["title"].count("\n") + 1 for p in P); cl = math.ceil(75 / cw)   # a caption runs to about 75 characters
    title_h = (34 + (22 * (subtitle.count("\n") + 1) if subtitle else 0)) * pt
    ptitle_h, cap_h = (26 + 17 * (tl - 1)) * pt, (18 + 12 * (cl - 1)) * pt
    rowh = [max((frames[p["view"]][3] - frames[p["view"]][2]) * ppm[p["view"]] for p in P[r * cols:(r + 1) * cols]) for r in range(rows)]
    H = title_h + sum(ptitle_h + h + cap_h + M for h in rowh) + M
    fig = plt.figure(figsize=(width / dpi, H / dpi), dpi=dpi)
    srcs = src or {}
    fig.text(M / width, 1 - (M * 0.6) / H, title or "", fontsize=16, fontweight="bold", va="top")
    if subtitle:                               # a line under the title (--master's legend)
        fig.text(M / width, 1 - (M * 0.6 + 26 * pt) / H, subtitle, fontsize=12, va="top")
    if before is not None or changes:
        fig.legend(handles=[Patch(color=ADD, label="added material"), Patch(color=REM, label="removed material")],
                   loc="upper right", ncol=2, fontsize=11, frameon=False, bbox_to_anchor=(1 - M / width, 1 - (M * 0.3) / H))
    y = title_h
    edge_px = max(1, round(width / 1400))
    for k, p in enumerate(P):
        r, c = divmod(k, cols)
        if c == 0 and k:
            y += ptitle_h + rowh[r - 1] + cap_h + M
        f = frames[p["view"]]; s = ppm[p["view"]]
        w, h = (f[1] - f[0]) * s, (f[3] - f[2]) * s
        x0 = M + c * (colw + M) + (colw - w) / 2; y0 = y + ptitle_h + (rowh[r] - h) / 2
        ax = fig.add_axes([x0 / width, 1 - (y0 + h) / H, w / width, h / H])
        ax.set_title(p["title"], fontsize=13, fontweight="bold")
        if p["kind"] == "3d":
            R.FACES.clear()
            for m, col in p["scene"]:
                R.mesh(m, col)
            img, cam = R.render(p.get("eye") or EYES[p["view"]][0], ppm=s * SS, frame=f, ss=SS, edge_px=edge_px,
                                edge_depth=float(np.clip(0.02 * ext, 0.3, 5.0)))
            R.place(ax, img, img.shape[1], img.shape[0])
            to2 = lambda q, cam=cam: np.array(R.proj(cam, q))
            note = "1 px = %.3f mm" % (1 / s)
        else:
            if p["kind"] == "flat":
                for _, shape, col in flat_regions(p["scene"], EYES[p["view"]][0]):
                    pa = _patch(shape, fc=col, ec="#333", lw=0.7, joinstyle="round")
                    pa and ax.add_patch(pa)
                _, right, up = R.camera(EYES[p["view"]][0])
                to2 = lambda q, right=right, up=up: np.array([np.asarray(q) @ right, np.asarray(q) @ up])
            else:
                for shape in p.get("ctx", []):
                    pa = _patch(shape, fc=GRAY, ec="#333", lw=0.7)
                    pa and ax.add_patch(pa)
                for shape, col in p["layers"]:
                    if not shape.is_empty:
                        pa = _patch(shape, fc=col, ec="#333", lw=0.7)
                        pa and ax.add_patch(pa)
                i, j = SEC_AXES[p["axis"]]
                to2 = lambda q, i=i, j=j: np.asarray(q)[[i, j]]
            st = grid_step(max(f[1] - f[0], f[3] - f[2]))
            ax.set_xticks(np.arange(math.ceil(f[0] / st) * st, f[1], st)); ax.set_yticks(np.arange(math.ceil(f[2] / st) * st, f[3], st))
            ax.grid(True, color="#ccc", lw=0.4, zorder=-1); ax.set_axisbelow(True)
            ax.tick_params(length=0, labelbottom=False, labelleft=False)
            for sp in ax.spines.values():
                sp.set_visible(False)
            ax.set_xlim(f[0], f[1]); ax.set_ylim(f[2], f[3]); ax.set_aspect("equal")
            note = "grid %g mm" % st
        for L in labels:
            if applies(L, p):
                put_label(ax, p["kind"], to2, L)
        fn = p.get("src") or srcs.get(p["tag"].split(":")[0]) or srcs.get("after") or ""
        cap = ("Drawn from %s (%s), %s" % (os.path.basename(fn), hashlib.sha256(open(fn, "rb").read()).hexdigest()[:8], note)
               if fn and os.path.exists(fn) else note)
        ax.text(0.0, -0.02, "\n".join(textwrap.wrap(cap, cw)), transform=ax.transAxes, fontsize=9, color="#555", va="top",
                gid="source")
    bad = R.layout_check(fig)
    print("LAYOUT OK (no need to look at the picture again)" if not bad else
          "LAYOUT FLAG (" + os.path.basename(out) + "): look at the picture and fix these\n  " + "\n  ".join(bad))
    fig.savefig(out, dpi=dpi, facecolor="white")
    written = [out]
    if any(p["kind"] != "3d" for p in P):
        svg = os.path.splitext(out)[0] + ".svg"; fig.savefig(svg, facecolor="white"); written.append(svg)
    plt.close(fig)
    from PIL import Image
    im = Image.open(out); chk = os.path.splitext(out)[0] + "_check.png"
    im.resize((check, round(im.height * check / im.width)), Image.LANCZOS).save(chk); written.insert(1, chk)
    print("picture: wrote " + ", ".join(written) + " (%d x %d px)" % im.size)
    return written


def put_label(ax, kind, to2, L):
    """A callout or a measured dimension line, in a 3D panel's pixels or a flat panel's mm."""
    if "text" in L:
        x, y = to2(L["at"]); off = L.get("off", (30, 25))
        ax.annotate(L["text"], xy=(x, y), xytext=off, textcoords="offset points", fontsize=11, fontweight="bold", color="#1f5fa8",
                    ha="center", va=L.get("va", "baseline"), arrowprops=dict(arrowstyle="-", color="#1f5fa8"),
                    bbox=dict(fc="white", ec="none", alpha=0.9))
    if "dim" in L:
        a, b = (np.asarray(q, float) for q in L["dim"]); off = np.asarray(L.get("off", (0, 0, 0)), float)
        txt = L.get("label") or ("%.2f" % np.linalg.norm(b - a)).rstrip("0").rstrip(".")
        A2, B2, A3, B3 = (to2(q) for q in (a, b, a + off, b + off))
        for p, q in ((A2, A3), (B2, B3)):
            ax.plot([p[0], q[0]], [p[1], q[1]], color="#c0392b", lw=0.7, ls=(0, (3, 2)))
        ax.annotate("", xy=B3, xytext=A3, arrowprops=dict(arrowstyle="<|-|>", color="#c0392b", lw=1.2, shrinkA=0, shrinkB=0))
        m = (A3 + B3) / 2
        ax.text(m[0], m[1], txt, color="#c0392b", fontsize=10, fontweight="bold", ha="center", va="center", gid="dim",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))


def _values(items):
    """{NAME: expression} from NAME=VALUE strings; a --change string splits only at a comma before the next NAME=,
    and a leading "words: " (its plain name) is left off."""
    import re
    out = {}
    for x in items or []:
        for kv in re.split(r",\s*(?=[A-Za-z_]\w*=)", _plain(x)[1]):
            k, v = kv.split("=", 1); out[k.strip()] = v
    return out


def _plain(x):
    """(plain name or None, NAME=VALUE part) of a --set or --change string that may start with "words: "."""
    import re
    m = re.match(r"\s*([^=]+?):\s*(?=[A-Za-z_]\w*=)", x)
    return (m.group(1), x[m.end():]) if m else (None, x)


def describe(script, x):
    """A change's words for a title (section 11 item 8): each value's plain name with its old and new value,
    "drop behind the steel: 2.0 → 2.5". The plain name is the string's leading "words: ", else the comment on the
    script's NAME = line (up to its first : ; ( or =), else NAME; the old value is that line's, worked out from the
    script's earlier top-level lines when it's a sum, the new one likewise."""
    import ast, re
    name, rest = _plain(x)
    src = open(script).read(); lines = src.splitlines(); tree = ast.parse(src)
    env, old, note = {"math": math, "np": np, "pi": math.pi}, {}, {}
    safe = {"min", "max", "round", "abs", "int", "float", "len", "sum", "range", "list", "tuple"}

    def plain_math(v):                         # no calls but math, numpy and simple built-ins: nothing the script builds runs
        return all(not isinstance(c, ast.Call) or (isinstance(c.func, ast.Name) and c.func.id in safe) or (
            isinstance(c.func, ast.Attribute) and isinstance(c.func.value, ast.Name) and c.func.value.id in ("math", "np"))
            for c in ast.walk(v))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
            tg = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [n.id for t in tg for n in ast.walk(t) if isinstance(n, ast.Name)]
            ok = plain_math(node.value)
            if ok:
                try:
                    exec(compile(ast.Module([node], []), script, "exec"), env)
                except Exception:
                    ok = False
            c = lines[node.lineno - 1].split("#", 1)
            for k in names:
                if not ok:
                    env.pop(k, None)
                old[k] = env[k] if k in env else ast.get_source_segment(src, node.value)
                note[k] = re.split(r"[:;(=]", c[1])[0].strip() if len(c) > 1 else None

    def num(v):
        if isinstance(v, float):
            return ("%.3f" % v).rstrip("0").rstrip(".") if v != int(v) else "%.1f" % v
        return str(v).replace(" ", "\u00a0")    # no-break spaces: a value, and old → new, stay on one line
    vals = _values([rest]); out = []
    for k, e in vals.items():
        try:
            new = eval(e, dict(env))
        except Exception:
            new = e
        out.append("%s: %s\u00a0→\u00a0%s" % ((name if len(vals) == 1 and name else note.get(k) or k), num(old.get(k, "?")), num(new)))
    return (name + ": " if name and len(vals) > 1 else "") + ", ".join(out)


def main(argv=None):
    try:
        run(argv)
    except RuntimeError as ex:                 # a build script that failed or wrote no 3mf through write3mf
        sys.exit("picture: %s" % ex)


def run(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("model"); ap.add_argument("--before"); ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--change", action="append", default=[]); ap.add_argument("--views")
    ap.add_argument("--spot"); ap.add_argument("--letters", action="store_true"); ap.add_argument("--master", action="store_true"); ap.add_argument("--with", dest="ctx", action="append", default=[])
    ap.add_argument("--labels"); ap.add_argument("--title"); ap.add_argument("--out", default="picture.png")
    ap.add_argument("--args", default="", help="the build script's own arguments, as one string")
    ap.add_argument("--width", type=int, default=4000); ap.add_argument("--check", type=int, default=1200)
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out); work = os.path.splitext(out)[0] + "_preview"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    is_py = a.model.endswith(".py")
    if a.master and (a.before or a.change):
        sys.exit("picture: --master draws one model; leave out --before and --change")
    if (a.set or a.change) and not is_py:
        sys.exit("picture: --set and --change need a build script")
    import shlex
    sa = shlex.split(a.args)
    model = load(a.model, _values(a.set), os.path.join(work, "after"), sa)
    src = {"after": model[0], "now": model[0]}
    before = None
    if a.before or (is_py and a.set):
        before = load(a.before or a.model, None, os.path.join(work, "before"), sa); src["before"] = before[0]
    changes = []
    for k, ch in enumerate(a.change, 1):
        f, ms = load(a.model, _values([ch]), os.path.join(work, "change%d" % k), sa)
        changes.append((describe(a.model, ch), whole(ms), f))
    stem = os.path.splitext(os.path.basename(model[0]))[0]
    title = a.title or (stem + (": " + ", ".join(describe(a.model, x) for x in a.set) if a.set else "")
                         + (" (before and after)" if before else ""))
    labels = json.load(open(a.labels)) if a.labels else None
    subtitle = None
    if a.master:
        parts, auto, subtitle = master(model[1], stem); model = (model[0], parts); labels = auto + (labels or [])
        title = a.title or stem + ", master picture"
    context = [whole(load(c)[1]) for c in a.ctx]
    import re
    views = re.split(r",(?=[a-z])", a.views) if a.views else None   # close:x,y,z,r keeps its commas
    draw(model, before, views, changes, labels, title, out, a.width, a.check, src, a.letters, context,
         [float(t) for t in a.spot.split(",")] if a.spot else None, subtitle)


if __name__ == "__main__":
    main()
