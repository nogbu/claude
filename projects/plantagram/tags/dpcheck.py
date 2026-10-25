#!/usr/bin/env python3
"""dpcheck: check a model against the design principles (build-3dp/design-principles.md) by measurement.

  python3 projects/3dp/scripts/dpcheck.py MODEL.3mf                       every check
  python3 projects/3dp/scripts/dpcheck.py MODEL.3mf --only flush           one check (or --only 3, --only edges,grid)
  python3 projects/3dp/scripts/dpcheck.py MODEL.3mf --only 3 --near 104.8,146.8 --radius 3   one spot
  python3 projects/3dp/scripts/dpcheck.py MODEL.stl --layer 0.3 --first 0.3 --lw 0.62
  Checks: plate, overhang (dp 1); edges, fillets (dp 2); flush (dp 3); bridge, islands, supports (dp 4); grid, beads (dp 12).
  --near takes x,y or x,y,z in the plate coordinates the report prints (z from the bed). --json writes every finding.
  --inventory INV.json writes the measured item inventory for dp-audit step 4, with the edge cells it settles (dpinv.py).

Reads the mesh in its print orientation and placement, and the 3mf's layer heights (height ranges
included), line widths (object and range overrides), plate, excluded corner and support settings.
Each line is FAIL (breaks a principle as measured), CHECK (a measured item a person must judge,
e.g. a step that may be a dp exception) or PASS, with where it is. It checks only what geometry and
settings show; the closing NOT CHECKED list names the principles that need judgement (dp-audit).
Needs numpy, scipy and shapely (trimesh only for STL).
"""
import argparse, json, math, re, sys, zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
import numpy as np
from shapely.geometry import Polygon, MultiPoint
from shapely.ops import polygonize, polygonize_full, unary_union

NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
P_NS = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}"
TOL = 0.005          # mm: on-grid tolerance and vertex weld
SHARP = 25.0         # degrees: a turn at one mesh edge above this is a sharp edge, not a fillet facet
BRIDGE_MAX = 10.0    # mm: clean bridge span until bridge tests set it (dp 4)
MIN_FILLET_V = 1.0   # mm: smallest fillet on a vertical edge (dp 2)
FLOAT_AREA, FLOAT_WIDTH = 0.02, 0.05   # mm2, mm: smallest floating region the island check reports (dp 4)


# ---------- loading ----------
def _xform(s):
    v = [float(x) for x in s.split()] if s else [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    M = np.eye(4); M[:3, :3] = np.array(v[:9]).reshape(3, 3).T; M[:3, 3] = v[9:12]
    return M


def _mesh_xml(root):
    """(vertices, triangles, painted-supports flag) per object id in a model XML root."""
    out = {}
    for obj in root.iter(f"{{{NS['m']}}}object"):
        mesh = obj.find("m:mesh", NS)
        if mesh is None:
            continue
        V = np.array([[float(v.get(a)) for a in "xyz"] for v in mesh.find("m:vertices", NS)])
        tris = mesh.find("m:triangles", NS)
        T = np.array([[int(t.get(a)) for a in ("v1", "v2", "v3")] for t in tris], np.int64)
        painted = any(t.get("paint_supports") for t in tris)
        out[obj.get("id")] = (V, T, painted)
    return out


def load_3mf(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    root = ET.fromstring(z.read("3D/3dmodel.model"))
    meshes = {("3D/3dmodel.model", k): v for k, v in _mesh_xml(root).items()}
    for n in names:
        if n.startswith("3D/Objects/") and n.endswith(".model"):
            meshes.update({(n, k): v for k, v in _mesh_xml(ET.fromstring(z.read(n))).items()})
    objs = {}  # top-level object id -> list of (V, T, painted) already in object coordinates
    for obj in root.iter(f"{{{NS['m']}}}object"):
        oid, parts = obj.get("id"), []
        if ("3D/3dmodel.model", oid) in meshes:
            parts.append(meshes[("3D/3dmodel.model", oid)])
        comps = obj.find("m:components", NS)
        for c in (comps if comps is not None else []):
            src = (c.get(P_NS + "path") or "/3D/3dmodel.model").lstrip("/")
            V, T, p = meshes[(src, c.get("objectid"))]
            M = _xform(c.get("transform"))
            parts.append((V @ M[:3, :3].T + M[:3, 3], T, p))
        objs[oid] = (obj.get("name") or oid, parts)
    items = []
    for it in root.find("m:build", NS).iter(f"{{{NS['m']}}}item"):
        name, parts = objs[it.get("objectid")]
        M = _xform(it.get("transform"))
        V = np.vstack([p[0] for p in parts]) @ M[:3, :3].T + M[:3, 3]
        off = np.cumsum([0] + [len(p[0]) for p in parts])
        T = np.vstack([p[1] + o for p, o in zip(parts, off)])
        items.append(dict(id=it.get("objectid"), name=name, V=V, T=T, painted=any(p[2] for p in parts)))
    cfg = json.loads(z.read("Metadata/project_settings.config")) if "Metadata/project_settings.config" in names else {}
    over, ranges = defaultdict(dict), defaultdict(list)
    if "Metadata/model_settings.config" in names:
        for o in ET.fromstring(z.read("Metadata/model_settings.config")).iter("object"):
            for md in o.findall("metadata"):
                over[o.get("id")][md.get("key")] = md.get("value")
    if "Metadata/layer_config_ranges.xml" in names:
        for o in ET.fromstring(z.read("Metadata/layer_config_ranges.xml")).iter("object"):
            for r in o.iter("range"):
                ranges[o.get("id")].append((float(r.get("min_z")), float(r.get("max_z")),
                                            {op.get("opt_key"): op.text for op in r.iter("option")}))
    # model_settings ids can differ from 3dmodel ids; match by name when they do
    by_name = {v.get("name"): k for k, v in over.items()}
    for it in items:
        oid = it["id"] if it["id"] in over else by_name.get(it["name"], it["id"])
        it["over"], it["ranges"] = over.get(oid, {}), sorted(ranges.get(oid, []))
        it["name"] = it["over"].get("name", it["name"])
    return items, cfg


def load_stl(path):
    import trimesh
    m = trimesh.load(path, force="mesh")
    return [dict(id="1", name=path, V=np.asarray(m.vertices), T=np.asarray(m.faces), painted=False, over={}, ranges=[])], {}


def _num(v, default):
    if isinstance(v, list):
        v = v[0]
    try:
        return float(str(v).rstrip("%"))
    except (TypeError, ValueError):
        return default


# ---------- mesh helpers ----------
def weld(V, T):
    """Merge vertices closer than TOL so faces share edges."""
    key = np.round(V / TOL).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    T = inv.reshape(-1)[T]
    T = T[(T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])]
    return V[first], T


def edges_and_faces(T):
    """Unique edges (k,2) and the two faces on each (k,2); edges not shared by exactly 2 faces are dropped."""
    E = np.sort(T[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), 1)
    F = np.repeat(np.arange(len(T)), 3)
    o = np.lexsort((E[:, 1], E[:, 0])); E, F = E[o], F[o]
    same = np.all(E[1:] == E[:-1], 1)
    pair = np.nonzero(same)[0]
    ok = np.ones(len(pair), bool)
    ok[1:] &= pair[1:] != pair[:-1] + 1  # skip edges with 3+ faces
    pair = pair[ok]
    return E[pair], np.c_[F[pair], F[pair + 1]]


def groups(pts, link):
    """Connected groups of points closer than link (union-find on a KD tree)."""
    from scipy.spatial import cKDTree
    if not len(pts):
        return []
    parent = np.arange(len(pts))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i, j in cKDTree(pts).query_pairs(link):
        a, b = find(i), find(j)
        if a != b:
            parent[a] = b
    lab = np.array([find(i) for i in range(len(pts))])
    return [np.nonzero(lab == g)[0] for g in np.unique(lab)]


def chains(E):
    """Groups of edges (k,2 vertex ids) joined end to end."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    v, inv = np.unique(E, return_inverse=True)
    inv = inv.reshape(-1, 2)
    n = len(E)
    # edges sharing a vertex: link each edge to the first edge at that vertex
    first = np.full(len(v), -1); order = np.repeat(np.arange(n), 2); flat = inv.ravel()
    first[flat[::-1]] = order[::-1]
    rows, cols = order, first[flat]
    _, lab = connected_components(coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n)), directed=False)
    return [np.nonzero(lab == g)[0] for g in np.unique(lab)]


def slice_z(V, T, z):
    """Cross-section polygon of the mesh at height z. Each crossing point is computed once per mesh edge (from its
    lower-numbered vertex), so the two triangles sharing an edge get the same point and every loop closes."""
    D = V[:, 2] - z
    above = D >= 0
    n_up = above[T].sum(1)
    T = T[(n_up == 1) | (n_up == 2)]
    pts = []
    for i, j in ((0, 1), (1, 2), (2, 0)):           # each triangle crosses exactly two of its edges
        a, b = np.minimum(T[:, i], T[:, j]), np.maximum(T[:, i], T[:, j])
        cross = above[a] != above[b]
        t = np.where(cross, D[a] / np.where(cross, D[a] - D[b], 1), 0)
        pts.append(np.where(cross[:, None], V[a, :2] + t[:, None] * (V[b, :2] - V[a, :2]), np.nan))
    P = np.stack(pts, 1)                              # (n, 3, 2), one row NaN
    ok = ~np.isnan(P[..., 0])
    segs = P[ok].reshape(-1, 2, 2)
    segs = np.round(segs, 6)
    segs = segs[np.any(segs[:, 0] != segs[:, 1], 1)]
    if not len(segs):
        return Polygon()
    lines = shapely_lines(segs)
    faces, cuts, dangles, bad = polygonize_full(lines)
    if not (cuts.is_empty and dangles.is_empty and bad.is_empty):   # zero-width slivers (coplanar boolean faces) overlap
        faces = polygonize(unary_union(lines))                         # other loops: node the lines first, then retry
    shape = Polygon()
    for f in getattr(faces, "geoms", faces):        # each closed loop once, by its outline; XOR nests the holes
        shape = shape.symmetric_difference(Polygon(f.exterior))
    return shape


def shapely_lines(segs):
    import shapely
    return list(shapely.linestrings(segs))


# ---------- layer grid and line widths ----------
def layer_tops(item, cfg, args, zmax):
    first = args.first or _num(item["over"].get("initial_layer_print_height", cfg.get("initial_layer_print_height")), 0.2)
    base = args.layer or _num(item["over"].get("layer_height", cfg.get("layer_height")), 0.2)
    tops, z = [0.0, first], first
    while z < zmax + 1e-6:
        lh = base
        for a, b, opt in item["ranges"]:
            if a - 1e-6 <= z < b - 1e-6 and "layer_height" in opt:
                lh = float(opt["layer_height"])
        z = round(z + lh, 6); tops.append(z)
    return np.array(tops), first, base


def line_width(item, cfg, args, z):
    if args.lw:
        return args.lw
    lw = _num(item["over"].get("outer_wall_line_width", cfg.get("outer_wall_line_width", cfg.get("line_width"))), 0.62)
    for a, b, opt in item["ranges"]:
        if a - 1e-6 <= z < b - 1e-6 and "outer_wall_line_width" in opt:
            lw = float(opt["outer_wall_line_width"])
    return lw


# ---------- checks ----------
def where(p):
    return "(" + ", ".join(f"{v:.2f}" for v in p) + ")"


class Model:
    """One placed object, welded, with z measured from its lowest point. Costly parts are computed once, on first use."""

    def __init__(self, item, cfg, args, out):
        V, T = weld(item["V"], item["T"])
        # faces shared by two touching solids (same three corners) are inside the part: drop both
        _, inv, cnt = np.unique(np.sort(T, 1), axis=0, return_inverse=True, return_counts=True)
        T = T[cnt[inv.reshape(-1)] == 1]
        tri = V[T]
        N = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        a2 = np.linalg.norm(N, axis=1); k = a2 > 1e-12
        self.item, self.cfg, self.args, self.out = item, cfg, args, out
        self.Vabs = V
        self.zmin = V[:, 2].min()
        self.V = V - [0, 0, self.zmin]
        self.T, self.N, self.area = T[k], N[k] / a2[k, None], a2[k] / 2
        self.tri = self.V[self.T]
        self.cen = self.tri.mean(1)
        self.tops, self.first, self.lh = layer_tops(item, cfg, args, self.V[:, 2].max())
        self._edges = self._zs = None

    def add(self, dp, status, text, at=None):
        if at is not None and self.args.near is not None:
            if np.linalg.norm(np.asarray(at)[:len(self.args.near)] - self.args.near) > self.args.radius:
                return
        self.out.append(dict(object=self.item["name"], dp=dp, status=status, text=text,
                             at=None if at is None else [round(float(v), 2) for v in at]))

    def edges(self):
        """Shared edges: (end a, end b, unit direction, length, the two faces' normals, turn in degrees)."""
        if self._edges is None:
            E, EF = edges_and_faces(self.T)
            a, b = self.V[E[:, 0]], self.V[E[:, 1]]
            d = b - a; L = np.linalg.norm(d, axis=1); d = d / np.maximum(L, 1e-12)[:, None]
            na, nb = self.N[EF[:, 0]], self.N[EF[:, 1]]
            turn = np.degrees(np.arccos(np.clip((na * nb).sum(1), -1, 1)))
            self._edges = dict(E=E, EF=EF, a=a, b=b, d=d, L=L, na=na, nb=nb, turn=turn, mid=(a + b) / 2)
        return self._edges

    def bed_edges(self):
        """(bed, opening): edges on the bed between a downward face and another, and those of them on an inner ring of
        the part's bed footprint (a hole's or slot's bed-side edge), which stay square (dp 2 Limits; learnings/walls,
        No bed-side chamfers on openings: 0.4 mm chamfers there roughened the top surface printed over them)."""
        e = self.edges()
        bed = (np.abs(e["a"][:, 2]) < TOL) & (np.abs(e["b"][:, 2]) < TOL) & \
              ((e["na"][:, 2] < -0.9999) | (e["nb"][:, 2] < -0.9999))
        opening = np.zeros(len(bed), bool)
        k = np.nonzero(bed)[0]
        down = (self.N[:, 2] < -0.9999) & (np.abs(self.tri[:, :, 2]).max(1) < TOL)
        if len(k) and down.any():
            import shapely
            foot = unary_union([Polygon(t[:, :2]) for t in self.tri[down]]).buffer(TOL).buffer(-TOL)
            rims = [g.exterior for g in getattr(foot, "geoms", [foot]) if not g.is_empty]
            if rims:
                opening[k] = shapely.distance(unary_union(rims), shapely.points(e["mid"][k, :2])) > 10 * TOL
        return bed, opening

    def zs(self):
        """Heights of flat faces and of edges where a wall meets a slope or curve (where fillets and chamfers end)."""
        if self._zs is None:
            e = self.edges()
            wall = np.abs(self.N[:, 2]) < 1e-3
            starts = (np.abs(e["d"][:, 2]) < 1e-3) & (wall[e["EF"][:, 0]] ^ wall[e["EF"][:, 1]]) & (e["turn"] > 0.5)
            z = np.r_[self.cen[np.abs(self.N[:, 2]) > 0.9999, 2], e["mid"][starts, 2]]
            self._zs = np.unique(np.round(z, 4))
        return self._zs


def c_plate(m):
    """dp 1: on the bed, inside the plate, convex outline clear of the excluded corner (Orca's test), and the skirt
    (skirt_loops loops of the first-layer line width, skirt_distance out) inside the plate too: a skirt must stay on
    the bed (learnings/walls, Long parts printed diagonally; 2026-10-14)."""
    if abs(m.zmin) > 0.01:
        m.add("1", "FAIL", f"lowest point is at z {m.zmin:.3f}, not on the bed")
    pts = m.cfg.get("printable_area", ["0x0", "256x0", "256x256", "0x256"])
    plate = Polygon([tuple(map(float, p.split("x"))) for p in pts])
    hull = MultiPoint(m.V[:, :2]).convex_hull
    ex = m.cfg.get("bed_exclude_area", ["0x0", "18x0", "18x28", "0x28"])
    ex = Polygon([tuple(map(float, p.split("x"))) for p in ex]) if len(ex) >= 3 else Polygon()
    bad = False
    if not plate.contains(hull):
        bad = True; m.add("1", "FAIL", f"outline leaves the plate (bounds {where(hull.bounds)})")
    if not ex.is_empty and hull.intersects(ex):
        bad = True; m.add("1", "FAIL", f"convex outline overlaps the excluded corner {where(ex.bounds)}")
    loops = int(_num(m.item["over"].get("skirt_loops", m.cfg.get("skirt_loops")), 0))
    if loops > 0 and not bad:
        reach = _num(m.cfg.get("skirt_distance"), 2) + loops * _num(m.cfg.get("initial_layer_line_width"), 0.62)
        skirt = hull.buffer(reach)
        if not plate.contains(skirt):
            bad = True; m.add("1", "FAIL", f"the skirt ({loops} loops, {reach:.2f} mm out) leaves the plate (bounds "
                                           f"{where(skirt.bounds)}): ask me how to handle it (skirt, layout or part)")
    if not bad:
        m.add("1", "PASS", f"fits the plate and clears the excluded corner (outline {where(hull.bounds)})")


def _patches(m, mask):
    """Groups of masked faces joined by shared edges."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    if not mask.any():
        return []
    EF = m.edges()["EF"]
    link = EF[mask[EF[:, 0]] & mask[EF[:, 1]]]
    n = len(mask)
    _, lab = connected_components(coo_matrix((np.ones(len(link)), (link[:, 0], link[:, 1])), shape=(n, n)), directed=False)
    f = np.nonzero(mask)[0]
    o = np.argsort(lab[f], kind="stable"); f = f[o]
    return np.split(f, np.nonzero(np.diff(lab[f]))[0] + 1)


def c_overhang(m):
    """dp 1: downward faces steeper than 45 degrees, above the first layer."""
    up = m.cen[:, 2] > m.first / 2
    found = False
    for f in _patches(m, up & (m.N[:, 2] < -math.sqrt(0.5) - 1e-3) & (m.N[:, 2] > -0.9999)):
        found = True
        worst = 90 - math.degrees(math.acos(min(1, -m.N[f, 2].min())))
        c = m.cen[f].mean(0)
        m.add("1", "FAIL", f"overhang past 45 deg: {m.area[f].sum():.1f} mm2, worst {worst:.0f} deg from vertical, "
                           f"z {m.cen[f, 2].min():.2f}-{m.cen[f, 2].max():.2f} near {where(c)}", c)
    if not found:
        m.add("1", "PASS", "no overhang past 45 deg")


def c_bridge(m):
    """dp 4: flat downward faces above the first layer (bridges and roofs over air), with the span each must cross."""
    import shapely
    down = np.nonzero((m.cen[:, 2] > m.first / 2) & (m.N[:, 2] <= -0.9999))[0]
    found = False
    for z in np.unique(np.round(m.cen[down, 2], 2)):
        f = down[np.abs(m.cen[down, 2] - z) < 0.006]
        polys = shapely.polygons(m.tri[f][:, :, :2])
        merged = shapely.union_all(shapely.buffer(polys, 1e-4, quad_segs=1))
        for poly in getattr(merged, "geoms", [merged]):
            if poly.area < 0.1:
                continue
            found = True
            circle = shapely.maximum_inscribed_circle(poly, 0.01)   # its length is the radius
            span, c = 2 * circle.length, np.array([*poly.representative_point().coords[0], z])
            long = span > BRIDGE_MAX
            m.add("4", "FAIL" if long else "CHECK",
                  f"bridge or roof over air at z {z:.2f}: {poly.area:.1f} mm2, span {span:.1f} mm near {where(c)}"
                  + (f" (over the {BRIDGE_MAX:.0f} mm clean span)" if long else "; allowed only where needed: hidden, with sag room"), c)
    if not found:
        m.add("4", "PASS", "no bridges or flat roofs over air")


def c_islands(m):
    """dp 4: layer regions with nothing under them, each layer's regions checked against the layer below. Catches a
    region that starts in midair, such as a 45 deg lip whose lowest edge hangs over a gap, which face angles miss.
    Also fails a piece reaching past the layer below grown one 45 deg step (+0.01) with no flat or steeper face under it."""
    import shapely
    found, prev = False, None
    down = np.nonzero(m.N[:, 2] < -math.sqrt(0.5) - 1e-3)[0]   # flat roofs and overhangs past 45 deg: bridge, overhang
    dlo, dhi = m.tri[down, :, 2].min(1), m.tri[down, :, 2].max(1)
    for i in range(len(m.tops) - 1):
        z = (m.tops[i] + m.tops[i + 1]) / 2
        if z > m.V[:, 2].max():
            break
        sh, thin = slice_z(m.V, m.T, z), []
        if prev is not None:
            held = []
            for poly in getattr(sh, "geoms", [sh]):
                if poly.is_empty or poly.area < 0.01:
                    continue
                on = poly.intersection(prev).area
                if on < 0.01:                           # bridges touch the layer below somewhere; this touches nothing
                    found = True
                    c = np.array([*poly.representative_point().coords[0], z]); b = poly.bounds
                    m.add("4", "FAIL", f"region over air on layer {i + 1} (z {z:.2f}): {poly.area:.2f} mm2, "
                                       f"{b[2] - b[0]:.2f} x {b[3] - b[1]:.2f}, nothing under it, near {where(c)}", c)
                else:
                    held.append(poly)
            # a strip growing along out of a held region (a 45 deg roof starting at an open edge) touches the layer
            # below at one end only: what reaches past one 45 deg step from the layer below, and from any flat roof or
            # steeper overhang under this layer (bridge and overhang report those), floats
            step = z - zp + 0.01
            f = down[(dhi > zp) & (dlo < z)]
            under = shapely.union_all(shapely.buffer(shapely.polygons(m.tri[f][:, :, :2]), 1e-3, quad_segs=1))
            rest = unary_union(held).difference(prev.union(under).buffer(step, join_style=2))
            for g in getattr(rest, "geoms", [rest]):
                w = 2 * g.area / max(g.length, 1e-9)    # mean width of a strip
                if g.area < FLOAT_AREA:
                    continue
                if w < FLOAT_WIDTH:                     # a hairline start: too thin to print, so it holds up nothing
                    thin.append(g); continue
                found = True
                c = np.array([*g.representative_point().coords[0], z]); b = g.bounds
                m.add("4", "FAIL", f"floating region: starts over air on layer {i + 1} (z {m.tops[i]:.2f}-{m.tops[i + 1]:.2f}): "
                                   f"{g.area:.2f} mm2, mean width {w:.2f}, x {b[0]:.2f}-{b[2]:.2f} y {b[1]:.2f}-{b[3]:.2f}, "
                                   f"past one 45 deg step ({step:.2f} mm) from the layer below, near {where(c)}", c)
        prev, zp = (sh.difference(unary_union(thin)) if thin else sh), z
    if not found:
        m.add("4", "PASS", "every layer region rests on the layer below, none past one 45 deg step from it")


def c_supports(m):
    """dp 4: support settings."""
    sup = m.item["over"].get("enable_support", m.cfg.get("enable_support"))
    if str(sup) == "1" and not m.item["painted"]:
        m.add("4", "FAIL", "Enable support is on with nothing painted: automatic supports, and the command-line slicer refuses PETG HF files (learnings/slicing-checks)")
    elif m.item["painted"]:
        m.add("4", "CHECK", "painted supports present: only where bridge supports can't work")
    else:
        m.add("4", "PASS", "supports off")


def c_edges(m):
    """dp 2: sharp edges (one mesh edge turning more than SHARP degrees); the bed edge of a 45 deg chamfer is allowed,
    and a hole's or slot's bed-side edge stays square (Model.bed_edges)."""
    e = m.edges()
    bed, opening = m.bed_edges()
    chamfer = np.minimum(np.abs(e["na"][:, 2] + math.sqrt(0.5)), np.abs(e["nb"][:, 2] + math.sqrt(0.5))) < 0.02
    sharp = (e["turn"] > SHARP) & ~(bed & chamfer) & ~opening
    if (opening & (e["turn"] > SHARP)).any():
        m.add("2", "PASS", f"{e['L'][opening & (e['turn'] > SHARP)].sum():.1f} mm of hole and slot edges on the bed left "
                           "square (dp 2 Limits; learnings/walls)")
    kinds = defaultdict(list)
    for i in np.nonzero(sharp)[0]:
        dz = abs(e["d"][i, 2])
        kinds["bed edge without a 45 deg chamfer" if bed[i] else
              "vertical edge" if dz > 0.95 else "horizontal edge" if dz < 0.05 else "sloped edge"].append(i)
    for kind, ids in kinds.items():
        ids = np.array(ids)
        for k in chains(e["E"][ids]):
            k = ids[k]; c = e["mid"][k].mean(0)
            lo, hi = e["mid"][k].min(0), e["mid"][k].max(0)
            place = f"near {where(c)}" if np.all(hi - lo < 10) else f"from {where(lo)} to {where(hi)}"
            m.add("2", "FAIL", f"sharp {kind}: {e['L'][k].sum():.1f} mm long, turn {e['turn'][k].max():.0f} deg, {place}", c)
    if not kinds:
        m.add("2", "PASS", f"no sharp edges (no edge turns more than {SHARP:.0f} deg)")


def c_fillets(m):
    """dp 2 Size: rounded vertical edges under MIN_FILLET_V, radius = facet width / facet turn."""
    e = m.edges()
    vr = (e["turn"] <= SHARP) & (e["turn"] > 0.5) & (np.abs(e["d"][:, 2]) > 0.95)
    if not vr.any():
        m.add("2", "PASS", "no rounded vertical edges to size"); return
    w = np.full(len(e["L"]), np.inf)
    for side in (0, 1):
        far = m.tri[e["EF"][:, side]] - e["a"][:, None]; far[..., 2] = 0
        w = np.minimum(w, np.linalg.norm(far, axis=2).max(1))
    r = w / np.radians(np.maximum(e["turn"], 1e-6))
    small = np.nonzero(vr & (r < MIN_FILLET_V - 0.05))[0]
    for g in groups(e["mid"][small][:, :2], 1.0):
        k = small[g]; c = e["mid"][k].mean(0)
        m.add("2", "FAIL", f"vertical fillet r about {np.median(r[k]):.2f} mm, under the {MIN_FILLET_V:.0f} mm minimum, "
                           f"z {e['mid'][k, 2].min():.2f}-{e['mid'][k, 2].max():.2f} near {where(c)}", c)
    if not len(small):
        m.add("2", "PASS", f"every rounded vertical edge is at least {MIN_FILLET_V:.0f} mm (smallest about {r[vr].min():.2f})")


def c_grid(m):
    """dp 12: heights of flat faces and fillet or chamfer ends sit on the layer grid (height ranges included)."""
    zs, tops = m.zs(), m.tops
    off = [z for z in zs if z > TOL and np.abs(tops - z).min() > TOL]
    for z in off:
        i = np.searchsorted(tops, z)
        m.add("12", "FAIL", f"height {z:.3f} is off the layer grid; nearest {tops[i - 1]:.3f} (layer {i - 1}) "
                            f"or {tops[min(i, len(tops) - 1)]:.3f} (layer {i})", (np.nan, np.nan, z))
    if not off:
        m.add("12", "PASS", f"all {len(zs)} flat-face and curve-start heights are on the layer grid "
                            f"(first layer {m.first}, layers {m.lh}{', plus height ranges' if m.item['ranges'] else ''})")


def c_beads(m):
    """dp 12: wall thicknesses under 5 beads per layer band, from the medial ridge of each slice."""
    from scipy import ndimage
    from PIL import Image, ImageDraw
    zs = m.zs()
    bands = np.unique(np.r_[0.0, zs, m.V[:, 2].max()])
    samples = defaultdict(list)
    for z0, z1 in zip(bands[:-1], bands[1:]):
        zc = (z0 + z1) / 2
        if z1 - z0 < m.lh / 2 or (m.args.near is not None and len(m.args.near) == 3 and abs(zc - m.args.near[2]) > m.args.radius + (z1 - z0) / 2):
            continue
        sec = slice_z(m.V, m.T, zc)
        if sec.is_empty:
            continue
        lw = line_width(m.item, m.cfg, m.args, zc)
        x0, y0, x1, y1 = sec.bounds
        px = max(lw / 12, max(x1 - x0, y1 - y0) / 3000)
        W, H = int((x1 - x0) / px) + 3, int((y1 - y0) / px) + 3
        X, Y = np.meshgrid(x0 + (np.arange(W) - 1) * px, y0 + (np.arange(H) - 1) * px)
        img = np.zeros((H, W), bool)
        for g in getattr(sec, "geoms", [sec]):     # fill each polygon with PIL (C speed), holes cut out
            layer = Image.new("1", (W, H), 0); dr = ImageDraw.Draw(layer)
            pix = lambda ring: [((x - x0) / px + 1, (y - y0) / px + 1) for x, y in np.asarray(ring.coords)[:, :2]]
            dr.polygon(pix(g.exterior), fill=1)
            for h in g.interiors:
                dr.polygon(pix(h), fill=0)
            img |= np.array(layer, bool)
        dist = ndimage.distance_transform_edt(img) * px
        ridge = img & (dist >= ndimage.maximum_filter(dist, 3) - 1e-9) & (dist > px)
        t = 2 * dist[ridge]            # thickness at the medial ridge (within a pixel on test walls)
        xs, ys = X[ridge], Y[ridge]
        thin = t < 5 * lw              # bead count matters only for thin walls
        t, xs, ys = t[thin], xs[thin], ys[thin]
        if not len(t):
            continue
        # keep the common thicknesses (5% of this band's ridge or more); corners and junctions read thicker
        b = np.round(t / 0.05).astype(int)
        vals, cnt = np.unique(b, return_counts=True)
        common = set(vals[cnt >= 0.05 * len(t)])
        for v, x, y in zip(b, xs, ys):
            if v in common:
                samples[(round(lw, 3), round(v * 0.05, 2))].append((x, y, zc))
    # neighboring 0.05 mm bins are one wall; report each as a range
    runs, prev = [], None
    for (lw, t) in sorted(samples):
        if prev and prev[0] == lw and t - prev[1] < 0.051:
            runs[-1].append((lw, t))
        else:
            runs.append([(lw, t)])
        prev = (lw, t)
    for run in runs:
        lw, t0, t1 = run[0][0], run[0][1], run[-1][1]
        at = np.array([p for k in run for p in samples[k]])
        if len(at) < 10:
            continue
        r0, r1 = t0 / lw, t1 / lw
        if r1 < 0.85:
            status, why = "FAIL", "thinner than one bead"
        elif any(abs(r - round(r)) < 0.08 and r > 1.5 for r in (r0, r1, (r0 + r1) / 2)):
            status, why = "CHECK", "beads about fill the wall exactly, where Arachne flips the bead count (learnings/walls); size it for a whole number of beads"
        else:
            status, why = "CHECK", "confirm the bead count with ; LINE_WIDTH in the G-code"
        c = at.mean(0)
        if m.args.near is not None:
            d = np.linalg.norm(at[:, :len(m.args.near)] - m.args.near, axis=1)
            if d.min() > m.args.radius:
                continue
            c = at[d.argmin()]
        size = f"{t0:.2f}" if t0 == t1 else f"{t0:.2f}-{t1:.2f}"
        beads = f"{r0:.2f}" if t0 == t1 else f"{r0:.2f}-{r1:.2f}"
        m.add("12", status, f"walls {size} mm at line width {lw} ({beads} line widths), z {at[:, 2].min():.2f}-{at[:, 2].max():.2f}: {why}", c)


def c_flush(m, ppm=8.0):
    """dp 3: depth jumps between two flat faces facing the same way, seen from above and from each side."""
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    from render3d import _rasterize
    found = False
    for e, side in (((0, 0, 1), "top"), ((1, 0, 0), "+x side"), ((-1, 0, 0), "-x side"), ((0, 1, 0), "+y side"), ((0, -1, 0), "-y side")):
        e = np.array(e, float)
        right = np.array([1.0, 0, 0]) if abs(e[2]) > 0.9 else np.cross(-e, [0, 0, 1.0])
        up = np.cross(right, -e) if abs(e[2]) < 0.9 else np.array([0, 1.0, 0])
        face = (m.N @ e) > 1e-9
        tri = m.tri[face]
        sx, sy = m.V @ right, m.V @ up
        xmin, ymax = sx.min() - 1, sy.max() + 1
        w_mm, h_mm = sx.max() + 1 - xmin, ymax - sy.min() + 1
        ppm_v = min(ppm, math.sqrt(16e6 / (w_mm * h_mm)))
        W, H = int(w_mm * ppm_v), int(h_mm * ppm_v)
        P = np.stack([(tri @ right - xmin) * ppm_v, (ymax - tri @ up) * ppm_v], -1)
        ids, z = _rasterize(P, tri @ e, H, W)
        ids, z = ids.reshape(H, W), z.reshape(H, W)
        fg = ids >= 0
        flat = np.zeros((H, W), bool); flat[fg] = (m.N[face][ids[fg]] @ e) > 0.9999
        jumps = defaultdict(list)
        for dy, dx in ((0, 1), (1, 0)):
            a = (slice(0, H - dy), slice(0, W - dx)); b = (slice(dy, H), slice(dx, W))
            hit = flat[a] & flat[b]
            hit[hit] = np.abs(z[a][hit] - z[b][hit]) > 0.05
            ys, xs = np.nonzero(hit)
            for yy, xx, lo, hi in zip(ys, xs, np.minimum(z[a][hit], z[b][hit]), np.maximum(z[a][hit], z[b][hit])):
                jumps[(round(float(lo), 2), round(float(hi), 2))].append((xx, yy))
        for (lo, hi), pix in sorted(jumps.items(), key=lambda kv: -len(kv[1])):
            pix = np.array(pix, float)
            for g in groups(pix, 2.0):
                if len(g) / ppm_v < 1.0:
                    continue
                xx, yy = pix[g].mean(0)
                p = right * (xx / ppm_v + xmin) + up * (ymax - yy / ppm_v) + e * hi
                found = True
                m.add("3", "CHECK", f"{side}: step of {hi - lo:.2f} mm between flat faces at depth {lo:.2f} and {hi:.2f}, "
                                    f"{len(g) / ppm_v:.0f} mm of edge near {where(p)}: make flush, or chamfer it toward the higher face (a dp exception)", p)
    if not found:
        m.add("3", "PASS", "no steps between parallel flat faces")


CHECKS = {"plate": c_plate, "overhang": c_overhang, "bridge": c_bridge, "islands": c_islands, "supports": c_supports, "edges": c_edges,
          "fillets": c_fillets, "flush": c_flush, "grid": c_grid, "beads": c_beads}
# dp-audit requirement numbers (dpreqs.py) each check settles: "all" fills the grid cell, "part" covers only what's
# named and the rest of that requirement is checked by hand
COVERS = {"plate": [("1.4", "all")], "overhang": [("1.3", "all")], "edges": [("2.1", "all")],
          "fillets": [("2.2", "part: at least 1 mm on vertical edges")], "flush": [("3.1", "all")],
          "bridge": [("4.2.1", "part: lists every flat roof over air and its span"), ("4.4", "part: spans over 10 mm")],
          "islands": [("4.6", "part: every layer region rests on the layer below")],
          "supports": [("4.5", "part: no automatic supports")], "grid": [("12.1", "all")],
          "beads": [("12.2", "part: modeled thicknesses; the G-code's ; LINE_WIDTH is checked by hand")]}
BY_DP = {"1": ["plate", "overhang"], "2": ["edges", "fillets"], "3": ["flush"], "4": ["bridge", "islands", "supports"], "12": ["grid", "beads"]}


NOT_CHECKED = [
    ("1", "fit features 1 mm above the bed, loads along the layers, how each part prints in a concept render"),
    ("2", "fillet sizes on non-vertical edges, a third of the thinnest feature, matching corners, inside/outside pairs "
          "(--inventory measures these per edge), corners matching by role, edges that do work (snap edges, seats) as "
          "exceptions, pictures"),
    ("3", "whether a step has a design reason"),
    ("4", "seen vs hidden bridges, sag room, bridge-support spacing; the slicer's warnings and the sliced Overhang wall and Bridge layers"),
    ("5", "widths that set a fit are in X-Y"), ("6", "clearances"), ("7", "test pieces"), ("8", "readable test pieces"),
    ("9", "design load and safety factor"), ("10", "human error"), ("11", "joined parts and seams"),
    ("12", "values from family or shared rules; ; LINE_WIDTH in the G-code"),
]


def find_doc(model):
    """The product state.md that names this model's file (rev name), if any."""
    import glob, os
    stem = os.path.basename(model).rsplit(".", 1)[0]
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "products")
    hits = [p for p in glob.glob(os.path.join(root, "*", "state.md")) if stem in open(p, encoding="utf-8").read()]
    if len(hits) > 1:
        print("dp exceptions: %s is named in %d product docs (%s); pass the doc to check its exceptions"
              % (stem, len(hits), ", ".join(os.path.basename(os.path.dirname(h)) for h in hits)))
    return os.path.realpath(hits[0]) if len(hits) == 1 else None


def dp_exceptions(doc):
    text = open(doc, encoding="utf-8").read()
    m = re.search(r"^#+ *dp exceptions\s*$(.*?)(?=^#+ |\Z)", text, re.M | re.S | re.I)
    return [l.strip()[2:] for l in m.group(1).splitlines() if l.strip().startswith(("- ", "* "))] if m else []


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check a model against the design principles; see the module docstring.")
    ap.add_argument("model")
    ap.add_argument("--only", help="comma list of checks (" + ", ".join(CHECKS) + ") or dp numbers (" + ", ".join(BY_DP) + ")")
    ap.add_argument("--near", help="x,y or x,y,z in the model's print position (z from the bed): report only findings there")
    ap.add_argument("--radius", type=float, default=5.0, help="mm around --near (default 5)")
    ap.add_argument("--layer", type=float); ap.add_argument("--first", type=float); ap.add_argument("--lw", type=float)
    ap.add_argument("--doc", help="product state.md whose dp exceptions to list (default: the one naming this file)")
    ap.add_argument("--json"); ap.add_argument("--inventory", help="write the measured item inventory (dpinv.py) here")
    ap.add_argument("--max", type=int, default=12, help="lines per principle (default 12)")
    args = ap.parse_args(argv)
    names = []
    for w in (args.only.split(",") if args.only else CHECKS):
        w = w.strip().lower().removeprefix("dp")
        if w in BY_DP:
            names += BY_DP[w]
        elif w in CHECKS:
            names.append(w)
        else:
            ap.error(f"unknown check {w!r}; use one of {', '.join(CHECKS)} or dp {', '.join(BY_DP)}")
    args.near = np.array([float(v) for v in args.near.split(",")]) if args.near else None
    items, cfg = load_3mf(args.model) if args.model.lower().endswith(".3mf") else load_stl(args.model)
    out, done, models = [], {}, []
    for it in items:
        # a copy of an object already checked in the same orientation gets only the plate check
        rot = hash(np.round(it["V"] - it["V"].min(0), 3).tobytes())
        m = Model(it, cfg, args, out)
        if rot in done:
            m.item = dict(it, name=f"{it['name']} (copy of {done[rot]}, same checks)")
            if "plate" in names:
                c_plate(m)
            continue
        done[rot] = it["name"] + (f" at {where(it['V'].min(0)[:2])}" if sum(i["name"] == it["name"] for i in items) > 1 else "")
        m.item = dict(it, name=done[rot])
        models.append(m)
        for n in dict.fromkeys(names):
            k = len(out)
            CHECKS[n](m)
            for r in out[k:]:
                r["check"], r["req"] = n, [q for q, _ in COVERS[n]]
    if args.inventory:
        sys.path.insert(0, __file__.rsplit("/", 1)[0])
        import dpinv
        inv = dpinv.inventory(models, out)
        json.dump(inv, open(args.inventory, "w"), indent=1)
        kinds = defaultdict(int)
        for i in inv:
            kinds[i["kind"]] += 1
        print(f"inventory {args.inventory}: " + ", ".join(f"{v} {k}" for k, v in kinds.items())
              + "; add joints and contact faces, load paths and ways to get it wrong by hand")
    if args.json:
        json.dump({"covers": {n: COVERS[n] for n in dict.fromkeys(names)}, "rows": out}, open(args.json, "w"), indent=1)
    print(f"dpcheck {args.model}: {len(items)} object(s); checks: {', '.join(dict.fromkeys(names))}"
          + (f"; near {where(args.near)} within {args.radius} mm" if args.near is not None else ""))
    if args.near is not None and not out:
        print(f"\nnothing found within {args.radius} mm of {where(args.near)}")
    for obj in dict.fromkeys(r["object"] for r in out):
        rows = [r for r in out if r["object"] == obj]
        if not rows:
            continue
        counts = {s: sum(r["status"] == s for r in rows) for s in ("FAIL", "CHECK", "PASS")}
        print(f"\n{obj}: {counts['FAIL']} FAIL, {counts['CHECK']} CHECK, {counts['PASS']} PASS")
        for dp in sorted({r["dp"] for r in rows}, key=int):
            rank = {"FAIL": 0, "CHECK": 1, "PASS": 2}
            rs = sorted((r for r in rows if r["dp"] == dp), key=lambda r: rank[r["status"]])
            for r in rs[:args.max]:
                print(f"  dp {r['dp']:>2} {r['status']:<5} {r['text']}")
            if len(rs) > args.max:
                print(f"  dp {dp:>2} ... {len(rs) - args.max} more (--max or --json)")
    doc = args.doc or find_doc(args.model)
    if doc:
        exc = dp_exceptions(doc)
        print(f"\nListed dp exceptions in {doc} (a FAIL or CHECK they cover stands):" + ("".join(f"\n  - {x}" for x in exc) if exc else " none"))
    if not args.only:
        print("\nNOT CHECKED (judgement, dp-audit): " + "; ".join(f"dp {d}: {t}" for d, t in NOT_CHECKED))
    return 1 if any(r["status"] == "FAIL" for r in out) else 0


if __name__ == "__main__":
    sys.exit(main())
