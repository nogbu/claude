#!/usr/bin/env python3
"""dpinv: the measured part of a dp audit's item inventory (dp-audit step 4), with the edge cells it can settle.

Run through dpcheck: python3 projects/3dp/scripts/dpcheck.py MODEL.3mf --json DC.json --inventory INV.json
Writes every part, edge (sharp chain or rounded strip), step (dpcheck flush rows) and overhang, bridge or roof
(dpcheck overhang and bridge rows) of each printed object, in dpgrid.py's inventory format. Joints, fits and contact
faces, load paths and ways to get it wrong need judgement: add them by hand before dpgrid.py make.

Each edge carries "cells": the dp 2 requirements (dpreqs.py numbers) whose cell its measurements settle, as
[status, evidence]; dpgrid.py writes them into the grid. TODO means measured but left to a person, with the numbers:
  2.2 Size: a sharp edge FAILs; a vertical curve under 1 mm or a horizontal one over fewer than 3 layers FAILs;
      a curve within 30% of a third of the thinnest wall meeting it PASSes; any other size is TODO (a Limits reason?).
  2.3 Matching corners: an edge at the mirror position across the object's middle (x or y), with the same
      orientation, must have the same profile and size (PASS or FAIL); with none, TODO (corners matching by role).
  2.4 Inside/outside pairs: a ray from an outside curve's middle into the wall; if it leaves through an inside curve,
      that curve's radius must be the outside radius minus the wall (PASS or FAIL, within 0.1 mm or 15%); if it
      leaves through a flat face, N/A. An inside edge no ray reached is N/A.
  2.6 Overhanging horizontal edges: a horizontal outside edge with a face below it pointing down needs a 45 deg
      chamfer face (PASS or FAIL); any other edge is N/A.
Radii come from the mesh facets (facet width / facet turn), so they are as good as the mesh's curve resolution.
"""
import math, re
from collections import defaultdict
import numpy as np

ROUND_MIN = 0.5      # degrees: a smaller turn at a mesh edge is flat
PARALLEL = 0.95      # cos: facet edges this parallel on one facet belong to one curve
FOLLOW = 0.8         # cos: edges meeting end to end at under about 37 deg follow one edge item
C45 = math.sqrt(0.5)


def _uf(n):
    parent = np.arange(n)

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i

    def join(i, j):
        a, b = find(i), find(j)
        if a != b:
            parent[a] = b
    return find, join


def _rays(m, O, D):
    """First hit distance along each ray (O + t D) and the face hit; inf and -1 where none. Start rays just
    inside the surface, so the face they start from is behind them."""
    if getattr(m, "_ray", None) is None:
        import trimesh
        m._ray = trimesh.Trimesh(m.V, m.T, process=False).ray
    O, D = np.asarray(O, float), np.asarray(D, float)
    T, F = np.full(len(O), np.inf), np.full(len(O), -1)
    if not len(O):
        return T, F
    loc, ri, ti = m._ray.intersects_location(O, D, multiple_hits=False)
    T[ri] = np.linalg.norm(loc - O[ri], axis=1); F[ri] = ti
    return T, F


def edge_items(m):
    """Edge items of one object: sharp chains and rounded strips, each with its measurements."""
    e = m.edges()
    import dpcheck
    # the bed edge of a 45 deg chamfer is part of that chamfer's profile, not an edge item (as dpcheck edges)
    on_bed = (np.abs(e["a"][:, 2]) < dpcheck.TOL) & (np.abs(e["b"][:, 2]) < dpcheck.TOL)
    bottom = (e["na"][:, 2] < -0.9999) | (e["nb"][:, 2] < -0.9999)
    chamfer = np.minimum(np.abs(e["na"][:, 2] + C45), np.abs(e["nb"][:, 2] + C45)) < 0.02
    cand = np.nonzero((e["turn"] > ROUND_MIN) & ~(on_bed & bottom & chamfer))[0]
    if not len(cand):
        return []
    find, join = _uf(len(cand))
    pos = {k: i for i, k in enumerate(cand)}
    sharp = e["turn"][cand] > _sharp()
    # facets: triangles joined across flat mesh edges (a quad's diagonal), so a curve's facet edges share a facet
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    flat = e["EF"][e["turn"] <= ROUND_MIN]
    _, facet = connected_components(coo_matrix((np.ones(len(flat)), (flat[:, 0], flat[:, 1])),
                                               shape=(len(m.T), len(m.T))), directed=False)
    by_face, by_vert = defaultdict(list), defaultdict(list)
    for i, k in enumerate(cand):
        for f in e["EF"][k]:
            by_face[facet[f]].append(i)
        for v in e["E"][k]:
            by_vert[v].append(i)
    d = e["d"][cand]
    # how far each side's triangle reaches across each facet edge
    w = np.zeros((len(cand), 2))
    for side in (0, 1):
        far = m.tri[e["EF"][cand, side]] - e["a"][cand][:, None]
        far -= (far @ d[:, :, None]) * d[:, None, :]
        w[:, side] = np.linalg.norm(far, axis=2).max(1)
    for key, ids in by_face.items():
        # a curve's facet edges share a facet no more than 3 times as wide as the facets on their other sides
        # (meshes alternate widths and halve the end facets); a wider facet between two curves (a flat land, at
        # least r wide under dp 2's sizes) keeps them apart; sharp edges never join across a face
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                i, j = ids[a], ids[b]
                if sharp[i] or sharp[j] or abs(d[i] @ d[j]) <= PARALLEL:
                    continue
                si = int(facet[e["EF"][cand[i], 1]] == key); sj = int(facet[e["EF"][cand[j], 1]] == key)
                if max(w[i, si], w[j, sj]) <= 3 * max(w[i, 1 - si], w[j, 1 - sj]) + 1e-6:
                    join(i, j)
    for ids in by_vert.values():
        # edges meeting end to end follow one edge item when they turn less than about 37 deg; sharp and round never mix
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                i, j = ids[a], ids[b]
                if sharp[i] == sharp[j] and abs(d[i] @ d[j]) > FOLLOW:
                    join(i, j)
    lab = np.array([find(i) for i in range(len(cand))])
    items = []
    for g in np.unique(lab):
        k = cand[lab == g]
        items.append(_measure(m, k))
    return items


def _sharp():
    import dpcheck
    return dpcheck.SHARP


def _measure(m, k):
    e = m.edges()
    L = e["L"][k]
    dirs = e["d"][k] * np.sign(e["d"][k] @ e["d"][k][np.argmax(L)])[:, None]
    dmean = (dirs * L[:, None]).sum(0); dmean /= max(np.linalg.norm(dmean), 1e-12)
    dz = (np.abs(dirs[:, 2]) * L).sum() / max(L.sum(), 1e-12)
    orient = "vertical" if dz > 0.95 else "horizontal" if dz < 0.05 else "sloped"
    faces = np.unique(e["EF"][k])
    # outside (convex) if each face's far side lies behind the other face
    other = m.cen[e["EF"][k, 1]] - e["mid"][k]
    convex = ((e["na"][k] * other).sum(1) < 0)
    outside = (convex * L).sum() >= L.sum() / 2
    sharp = e["turn"][k].max() > _sharp()
    pts = np.r_[e["a"][k], e["b"][k]]
    # radius: facet width across the edge over the facet's turn, per facet edge
    if sharp:
        r = 0.0
    else:
        w = np.full(len(k), np.inf)
        for side in (0, 1):
            far = m.tri[e["EF"][k, side]] - e["a"][k][:, None]
            far -= (far @ dmean)[..., None] * dmean
            w = np.minimum(w, np.linalg.norm(far, axis=2).max(1))
        r = float(np.median(w / np.radians(e["turn"][k])))
    # length along the edge: extent along its direction for a straight item, else total length over the strip's rails
    ext = np.ptp(pts @ dmean)
    straight = np.abs(dirs @ dmean).min() > 0.995
    length = ext if straight else L.sum() / max(1, _rail_count(m, k, dmean))
    n_ab = np.r_[e["na"][k], e["nb"][k]]
    bis = (e["na"][k] + e["nb"][k]).sum(0); bis /= max(np.linalg.norm(bis), 1e-12)
    mid = e["mid"][k][np.argmin(np.abs((e["mid"][k] - e["mid"][k].mean(0)) @ dmean))]
    return dict(edges=k, faces=faces, dir=dmean, orient=orient, outside=bool(outside), sharp=bool(sharp), r=r,
                zlo=float(pts[:, 2].min()), zhi=float(pts[:, 2].max()), length=float(length), mid=mid,
                center=pts.mean(0), bis=bis, normals=n_ab, straight=bool(straight))


def _rail_count(m, k, dmean):
    """How many facet edges sit side by side across a strip (1 for a chain)."""
    e = m.edges()
    c = e["mid"][k]
    s = c @ dmean
    near = np.abs(s - np.median(s)) < max(np.median(e["L"][k]), 0.05)
    return max(1, int(near.sum()))


def _thinnest(m, items):
    """Each edge's two legs and thinnest wall: from just beside the edge on each face, straight into the part."""
    e = m.edges()
    O, D = [], []
    for it in items:
        k = it["edges"]
        j = k[np.argmin(np.linalg.norm(e["mid"][k] - it["mid"], axis=1))]
        for side, n in ((0, e["na"][j]), (1, e["nb"][j])):
            # step off the edge onto the face (past the strip for a curve), then go in against its normal
            away = m.cen[e["EF"][j, side]] - e["mid"][j]
            away -= (away @ n) * n; away /= max(np.linalg.norm(away), 1e-12)
            O.append(e["mid"][j] + away * (it["r"] + 0.05) - n * 1e-3); D.append(-n)
    T, _ = _rays(m, O, D)
    for i, it in enumerate(items):
        legs = T[2 * i:2 * i + 2]
        it["legs"] = [float(t) for t in legs]
        it["t"] = float(legs[np.isfinite(legs)].min()) if np.isfinite(legs).any() else None


def _mirrors(items, box):
    """For each edge, the edges at its mirror position across the object's middle in x or in y, of the same kind."""
    from scipy.spatial import cKDTree
    C = np.array([it["center"] for it in items])
    tree = cKDTree(C)
    out = [[] for _ in items]
    for ax in (0, 1):
        P = C.copy(); P[:, ax] = box[0][ax] + box[1][ax] - P[:, ax]
        for i, js in enumerate(tree.query_ball_point(P, 0.5)):
            if np.linalg.norm(P[i] - C[i]) < 0.5:
                continue
            out[i] += [j for j in js if j != i and items[j]["orient"] == items[i]["orient"]
                       and items[j]["outside"] == items[i]["outside"]]
    return out


def _r(it):
    return "sharp" if it["sharp"] else f"r {it['r']:.2f}"


def cells(m, items):
    """The dp 2 cells each edge's measurements settle (see the module docstring)."""
    lh = m.lh
    box = (m.V.min(0), m.V.max(0))
    face_item = {}
    for i, it in enumerate(items):
        for f in it["faces"]:
            face_item.setdefault(int(f), i)
    _thinnest(m, items)
    mirrors = _mirrors(items, box) if items else []
    paired = set()
    out = [dict() for _ in items]
    # 2.4: rays from outside edges into the wall
    rays = [i for i, it in enumerate(items) if it["outside"] and it["t"] is not None]
    RT, RF = _rays(m, [items[i]["mid"] - items[i]["bis"] * 1e-3 for i in rays], [-items[i]["bis"] for i in rays])
    for i, t, f in zip(rays, RT, RF):
        it = items[i]
        if not np.isfinite(t):
            continue
        T = [t]
        j = face_item.get(int(f))
        if j is None or items[j]["outside"]:
            out[i]["2.4"] = ["N/A", f"no inside corner behind it: a ray from its middle into the wall leaves through a flat face {T[0]:.2f} mm in (dpinv)"]
            continue
        o = items[j]; paired.add(j)
        t0, t1 = it["legs"]
        if not (np.isfinite(t0) and np.isfinite(t1)) or abs(t0 - t1) > 0.05:
            out[i]["2.4"] = out[j]["2.4"] = ["N/A", f"legs differ ({t0:.2f} and {t1:.2f} mm), so the pair rule doesn't apply (dpinv)"]
            continue
        wall, least = t0, (1.0 if it["orient"] == "vertical" else 3 * lh)
        want = it["r"] - wall
        if want < least - 0.05:
            st, ev = "FAIL", (f"outside {_r(it)} over a {wall:.2f} wall leaves the inside edge {o['id']} r {max(want, 0):.2f}, under "
                              f"{least:.2f}; the outside needs r {wall + least:.2f} or more (inside {o['id']} is {_r(o)}) (dpinv)")
        else:
            ok = abs(o["r"] - want) <= max(0.1, 0.15 * want)
            st, ev = ("PASS" if ok else "FAIL"), (f"outside {_r(it)}, wall {wall:.2f}, so the inside should be r {want:.2f}; "
                                                  f"inside edge {o['id']} is {_r(o)} (dpinv)")
        out[i]["2.4"] = out[j]["2.4"] = [st, ev]
    for i, it in enumerate(items):
        c = out[i]
        # 2.2 size
        span = it["zhi"] - it["zlo"]
        if it["sharp"]:
            c["2.2"] = ["FAIL", "sharp: no curve to size (dpinv)"]
        elif it["orient"] == "vertical" and it["r"] < 1.0 - 0.05:
            c["2.2"] = ["FAIL", f"vertical {_r(it)}, under the 1 mm minimum (dpinv)"]
        elif it["orient"] == "horizontal" and it["r"] < 3 * lh - 0.01:
            c["2.2"] = ["FAIL", f"horizontal {_r(it)}, under 3 layers ({3 * lh:.2f} mm) (dpinv)"]
        elif it["t"] is None:
            c["2.2"] = ["TODO", f"{_r(it)}; no wall measured beside it (dpinv)"]
        else:
            third = it["t"] / 3
            ok = 0.7 * third <= it["r"] <= 1.3 * third
            c["2.2"] = ["PASS" if ok else "TODO",
                        f"{_r(it)}; thinnest wall meeting it {it['t']:.2f}, a third is {third:.2f}"
                        + ("" if ok else "; check for a Limits reason (2.5) or resize") + " (dpinv)"]
        # 2.3 matching corners
        mates = mirrors[i]
        if mates:
            bad = [items[j] for j in mates if items[j]["sharp"] != it["sharp"] or abs(items[j]["r"] - it["r"]) > max(0.05, 0.05 * it["r"])]
            names = ", ".join(items[j]["id"] for j in mates)
            c["2.3"] = (["FAIL", f"{_r(it)}, but its mirror match " + ", ".join(f"{o['id']} is {_r(o)}" for o in bad) + " (dpinv)"] if bad
                        else ["TODO", f"{_r(it)}, same as its mirror match {names}; check corners matching by role (dpinv)"])
        else:
            c["2.3"] = ["TODO", f"{_r(it)}; no edge at its mirror position; check corners matching by role (dpinv)"]
        # 2.4 for edges no ray reached
        if "2.4" not in c and (not it["outside"]) and i not in paired:
            c["2.4"] = ["N/A", "inside edge with no outside curve in front of it across a wall (rays from every outside curve, dpinv)"]
        elif "2.4" not in c:
            c["2.4"] = ["TODO", "no wall measured; check for an inside corner behind it (dpinv)"]
        # 2.6 overhanging horizontal edges
        down = it["normals"][:, 2].min() < -0.1
        if it["orient"] == "horizontal" and it["outside"] and down:
            chamfer = np.abs(it["normals"][:, 2] + C45).min() < 0.02
            c["2.6"] = (["PASS", "overhanging horizontal edge with a 45 deg chamfer face (dpinv)"] if chamfer else
                        ["FAIL", f"overhanging horizontal edge without a 45 deg chamfer ({_r(it)}) (dpinv)"])
        else:
            why = ("not horizontal" if it["orient"] != "horizontal" else "an inside edge" if not it["outside"]
                   else "no face below it points down")
            c["2.6"] = ["N/A", f"not an overhanging horizontal edge: {why} (dpinv)"]
    return out


def where(p):
    return "(" + ", ".join(f"{v:.2f}" for v in p) + ")"


def inventory(models, rows):
    """Inventory items for dpgrid.py from each checked Model and dpcheck's rows."""
    inv, n = [], defaultdict(int)

    def nid(kind):
        n[kind] += 1
        return "%s%d" % ({"part": "P", "edge": "E", "step": "S", "overhang": "O"}[kind], n[kind])
    for m in models:
        name = m.item["name"]
        x0, y0, _ = m.V.min(0); x1, y1, z1 = m.V.max(0)
        inv.append(dict(id=nid("part"), kind="part", text=f"{name}: {x1 - x0:.1f} x {y1 - y0:.1f} x {z1:.1f} mm as it prints, "
                                                          f"layers {m.lh} (first {m.first})"))
        items = edge_items(m)
        items.sort(key=lambda it: (round(it["center"][2], 1), round(it["center"][1], 1), round(it["center"][0], 1)))
        for k, it in enumerate(items):
            it["id"] = "#%d#" % k
        cs = cells(m, items)
        # identical edges repeated across the object (a pattern, a texture) are one item, listing where each is
        same = defaultdict(list)
        for k, it in enumerate(items):
            same[(it["orient"], it["outside"], it["sharp"], round(it["r"], 2), round(it["length"], 1),
                  round(it["zlo"], 2), round(it["zhi"], 2))].append(k)
        final = {}
        for ks in sorted(same.values()):
            new = nid("edge")
            for k in ks:
                final["#%d#" % k] = new
        groups = sorted(same.values(), key=lambda ks: int(final["#%d#" % ks[0]][1:]))
        rank = {"FAIL": 0, "TODO": 1, "PASS": 2, "N/A": 3}
        fix = lambda t: re.sub(r"#\d+#", lambda g: final[g.group(0)], t)
        for ks in groups:
            it = items[ks[0]]
            c = {}
            for rid in cs[ks[0]]:
                got = [cs[k][rid] for k in ks]
                worst = min(got, key=lambda g: rank[g[0]])
                n_worst = sum(g[0] == worst[0] for g in got)
                c[rid] = [worst[0], fix(worst[1]) if len(ks) == 1 else f"{n_worst} of {len(ks)}: {fix(worst[1])}"]
            span = f"z {it['zlo']:.2f}-{it['zhi']:.2f}" if it["orient"] != "horizontal" else f"z {it['center'][2]:.2f}"
            mids = np.array([items[k]["mid"] for k in ks])
            at = (f"middle {where(mids[0])}" if len(ks) == 1 else
                  f"{len(ks)} alike, middles " + ", ".join(where(p) for p in mids) if len(ks) <= 4 else
                  f"{len(ks)} alike, middles from {where(mids.min(0))} to {where(mids.max(0))} (all in \"at\")")
            inv.append(dict(id=final[it["id"]], kind="edge", object=name, cells=c,
                            at=[[round(float(v), 2) for v in p] for p in mids],
                            text=f"{name}: {'outside' if it['outside'] else 'inside'} {it['orient']} edge, {_r(it)}, "
                                 f"{it['length']:.1f} mm long, {span}, {at}"))
        # steps and overhangs from dpcheck's rows; alike ones (same text but where) are one item
        alike = defaultdict(list)
        for r in rows:
            kind = ("step" if r.get("check") == "flush" and r["status"] == "CHECK" else
                    "overhang" if r.get("check") in ("overhang", "bridge") and r["status"] in ("FAIL", "CHECK") else None)
            if r["object"] == name and kind:
                alike[(kind, re.sub(r" near \([^)]*\)", "", r["text"]))].append(r)
        for (kind, text), rs in alike.items():
            at = [r["at"] for r in rs if r.get("at")]
            where_ = (f" near {where(at[0])}" if len(rs) == 1 and at else
                      f"; {len(rs)} alike, near " + ", ".join(where(p) for p in at) if len(rs) <= 4 else
                      f"; {len(rs)} alike, from {where(np.min(at, 0))} to {where(np.max(at, 0))} (all in \"at\")")
            inv.append(dict(id=nid(kind), kind=kind, object=name, at=at, text=f"{name}: {text}{where_}"))
    return inv
