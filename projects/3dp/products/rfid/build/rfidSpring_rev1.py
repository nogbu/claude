#!/usr/bin/env python3
"""Builds rfidSpring_rev1.3mf (product rfid, 3dp project): the one-piece PETG HF spring that
wedges across a filament spool's center hole (52-58 mm and 72-75 mm holes).

Needs beside it: rfidSpring_settings_base.json (the 3mf's project settings).
Needs: numpy, scipy (Delaunay), matplotlib (contourpy contours, point-in-polygon, thumbnail).

Geometry (all mm; x along the spring, y across it, z up; z = 0 is the bed):
- 80 long crown to crown at rest, 50 fully compressed. 20 wide, 20.1 tall (67 layers of 0.3).
- End blocks: outer faces are arcs of radius 26 (fit a 52 mm hole at the middle), 1.5 thick at
  the edges, 3.5 at the middle. Inner faces flat at x = 3.5 and 76.5.
- 28 folds, each 1.00 thick (one 1.05 mm bead). Gaps are shaped so that at 50 mm every gap
  is a uniform 0.517: at rest each fold is pre-bent by the S-curve it straightens out of.
- Bends rounded inside (0.8 across, a bulb) and outside (1.4 radius). Bend centers 1.4 from
  the edges, so each fold spans 17.2 between bend centers.
- Two rails, 43 long: one from each end block's inner face (y = 7 from the fixed end,
  y = 13 from the moving end), so each tip meets the far block at 50 mm. Each fold has a
  notch around each rail. Profiles on the 0.3 layer grid (half-widths):
    rail : 0.6 to z 1.2, 45 deg out to 1.5 at z 2.1, straight to z 3.6, 45 deg roof to z 5.1
    notch: 1.05 to z 0.9, 45 deg out to 1.95 at z 1.8, straight to z 3.9, roof 5.85 - z,
           closed from z 5.7
  Clearance 0.45 sideways, about 0.53 across the 45 deg faces. Rail tips taper over 1.5 mm.
- The mesh is a stack of prisms, one per band of identical layer sections (each section is
  exact at the layer's mid-height), so the 45 deg faces are stepped the way they print.
"""
import io, json, math, os, uuid, zipfile, datetime
import numpy as np
from scipy.spatial import Delaunay
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
import contourpy

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "rfidSpring_rev1"

# ------------------------------------------------------------------ parameters
L0, LC = 80.0, 50.0
D = L0 - LC
W, H, LAYER = 20.0, 20.1, 0.3
NLAYERS = int(round(H / LAYER))                     # 67
R_END = 26.0
EB_EDGE = 1.5
EB_C = EB_EDGE + (R_END - math.sqrt(R_END ** 2 - (W / 2) ** 2))   # 3.5
X_IN_L, X_IN_R = EB_C, L0 - EB_C                    # 3.5, 76.5
N, T = 28, 1.00
G_C = (X_IN_R - X_IN_L - D - N * T) / (N + 1)        # gap at full compression
DELTA = D / N
R_I = 0.4
R_M, R_O = R_I + T / 2, R_I + T
Y_LO, Y_HI = R_O, W - R_O
BUMP_LEN = 1.5
C1, C2 = 7.0, 13.0
RAIL_LEN = LC - 2 * EB_C                              # 43
TIP_LEN, TIP_NARROW = 1.5, 0.3
GRID = 0.02          # section raster step (contours are interpolated well below this)
SEG_MAX = 0.2        # longest boundary segment (keeps every boundary edge in the Delaunay mesh)
DP_TOL = 0.003       # boundary simplification tolerance


def rail_hw(z):
    if z < 1.2: return 0.6
    if z < 2.1: return 0.6 + (z - 1.2)
    if z < 3.6: return 1.5
    if z < 5.1: return 1.5 - (z - 3.6)
    return 0.0


def notch_hw(z):
    if z < 0.9: return 1.05
    if z < 1.8: return 1.05 + (z - 0.9)
    if z < 3.9: return 1.95
    if z < 5.7: return 5.85 - z
    return 0.0


def side(j):                 # bend side of gap j (gap 0: block to fold 1)
    return "R" if j % 2 == 0 else "L"


def smooth(u):
    u = np.clip(u, 0.0, 1.0)
    return 3 * u * u - 2 * u ** 3


def dsmooth(u):
    inside = (u > 0) & (u < 1)
    return np.where(inside, 6 * u - 6 * u * u, 0.0)


X0 = [X_IN_L + G_C + T / 2 + (k - 1) * (T + G_C) for k in range(1, N + 1)]
DBUMP = (2 * R_M - (T + G_C)) / 2


def fold_center(k, y):
    """Centerline x of fold k (1..N) at rest, and dx/dy."""
    y = np.asarray(y, float)
    span = Y_HI - Y_LO
    sp = side(k - 1)
    s = (y - Y_LO) / span if sp == "L" else (Y_HI - y) / span
    ds = (1 / span) if sp == "L" else (-1 / span)
    x = X0[k - 1] + (k - 1) * DELTA + DELTA * smooth(s)
    dx = DELTA * dsmooth(s) * ds
    # bulb bumps: push this fold away from its partner at each bend end
    for gap, sign in ((k - 1, +1), (k, -1)):
        amp = DBUMP * (2 if gap in (0, N) else 1)
        yb = Y_LO if side(gap) == "L" else Y_HI
        d = np.abs(y - yb) / BUMP_LEN
        g = 1 - smooth(d)
        dg = -dsmooth(d) / BUMP_LEN * np.sign(y - yb)
        x = x + sign * amp * g
        dx = dx + sign * amp * dg
    return x, dx


def bend_centers():
    out = []
    for j in range(N + 1):
        yb = Y_LO if side(j) == "L" else Y_HI
        if j == 0:
            xc = X_IN_L + R_I
        elif j == N:
            xc = X_IN_R - R_I
        else:
            xc = 0.5 * (fold_center(j, yb)[0] + fold_center(j + 1, yb)[0])
        out.append((xc, yb, side(j)))
    return out


# ------------------------------------------------------------------ sections (2D)
XS = np.arange(-0.3, L0 + 0.3 + 1e-9, GRID)
YS = np.arange(-0.3, W + 0.3 + 1e-9, GRID)
XX, YY = np.meshgrid(XS, YS)          # shape (ny, nx)


def zigzag_field():
    f = np.full(XX.shape, 10.0)
    # end blocks
    bl = np.maximum.reduce([np.hypot(XX - R_END, YY - W / 2) - R_END, XX - X_IN_L, -YY, YY - W])
    br = np.maximum.reduce([np.hypot(XX - (L0 - R_END), YY - W / 2) - R_END, X_IN_R - XX, -YY, YY - W])
    f = np.minimum(f, np.minimum(bl, br))
    # folds
    ys = YS
    for k in range(1, N + 1):
        cx, dx = fold_center(k, ys)
        half = (T / 2) * np.sqrt(1 + dx ** 2)
        x_lo = int(max(0, np.searchsorted(XS, cx.min() - 1.0)))
        x_hi = int(min(len(XS), np.searchsorted(XS, cx.max() + 1.0)))
        sub = XX[:, x_lo:x_hi]
        # bands run 0.1 past the bend center lines so they overlap the bends (no seam)
        val = np.maximum.reduce([np.abs(sub - cx[:, None]) - half[:, None],
                                 (Y_LO - 0.1 - YY[:, x_lo:x_hi]), (YY[:, x_lo:x_hi] - Y_HI - 0.1)])
        f[:, x_lo:x_hi] = np.minimum(f[:, x_lo:x_hi], val)
    # bends (half annuli on the outer side of each bend center)
    for xc, yb, s in bend_centers():
        x_lo = int(max(0, np.searchsorted(XS, xc - 2.0)))
        x_hi = int(min(len(XS), np.searchsorted(XS, xc + 2.0)))
        sx, sy = XX[:, x_lo:x_hi], YY[:, x_lo:x_hi]
        ring = np.abs(np.hypot(sx - xc, sy - yb) - R_M) - T / 2
        cut = (sy - yb) if s == "L" else (yb - sy)
        f[:, x_lo:x_hi] = np.minimum(f[:, x_lo:x_hi], np.maximum(ring, cut))
    return f


def section_field(zig, z):
    f = zig.copy()
    wn, wr = notch_hw(z), rail_hw(z)
    if wn > 0:
        for c in (C1, C2):
            notch = np.maximum.reduce([np.abs(YY - c) - wn, X_IN_L - XX, XX - X_IN_R])
            f = np.maximum(f, -notch)
    if wr > 0:
        for c, x0, x1, tip_right in ((C1, X_IN_L - 0.1, X_IN_L + RAIL_LEN, True),
                                     (C2, X_IN_R - RAIL_LEN, X_IN_R + 0.1, False)):
            if tip_right:
                taper = np.clip((XX - (x1 - TIP_LEN)) / TIP_LEN, 0, 1)
            else:
                taper = np.clip(((x0 + TIP_LEN) - XX) / TIP_LEN, 0, 1)
            hw = np.maximum(wr - TIP_NARROW * taper, 0.05)
            rail = np.maximum.reduce([np.abs(YY - c) - hw, x0 - XX, XX - x1])
            f = np.minimum(f, rail)
    return f


def dp_simplify(pts, tol):
    """Douglas-Peucker on an open polyline (iterative)."""
    keep = np.zeros(len(pts), bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        p, q = pts[a], pts[b]
        seg = q - p
        L = np.hypot(*seg)
        rel = pts[a + 1:b] - p
        if L < 1e-12:
            d = np.hypot(rel[:, 0], rel[:, 1])
        else:
            d = np.abs(rel[:, 0] * seg[1] - rel[:, 1] * seg[0]) / L
        i = int(np.argmax(d))
        if d[i] > tol:
            m = a + 1 + i
            keep[m] = True
            stack += [(a, m), (m, b)]
    return pts[keep]


def clean_loop(line):
    pts = np.asarray(line, float)
    if np.hypot(*(pts[0] - pts[-1])) < 1e-9:
        pts = pts[:-1]
    # split the closed loop at its two farthest-apart points, simplify both halves
    i0 = 0
    i1 = int(np.argmax(np.hypot(pts[:, 0] - pts[0, 0], pts[:, 1] - pts[0, 1])))
    a = dp_simplify(pts[i0:i1 + 1], DP_TOL)
    b = dp_simplify(np.vstack([pts[i1:], pts[:1]]), DP_TOL)
    loop = np.vstack([a[:-1], b[:-1]])
    step = np.hypot(*(np.roll(loop, -1, axis=0) - loop).T)
    loop = loop[step > 1e-6]
    # subdivide long segments
    out = []
    n = len(loop)
    for i in range(n):
        p, q = loop[i], loop[(i + 1) % n]
        L = np.hypot(*(q - p))
        m = max(1, int(math.ceil(L / SEG_MAX - 1e-9)))
        for s in range(m):
            out.append(p + (q - p) * s / m)
    loop = np.array(out)
    area = 0.5 * np.sum(loop[:, 0] * np.roll(loop[:, 1], -1) - np.roll(loop[:, 0], -1) * loop[:, 1])
    return loop, area


def section_loops(f):
    gen = contourpy.contour_generator(XS, YS, f, line_type="Separate")
    loops = []
    for line in gen.lines(0.0):
        if len(line) < 4:
            continue
        loop, area = clean_loop(line)
        if abs(area) < 1e-4:
            continue
        loops.append((loop, area))
    return loops


def triangulate(loops, tries=8):
    """Delaunay of the boundary points, keep triangles inside the region (even-odd). Any
    boundary edge missing from the result gets its midpoint added, then it's redone."""
    for _ in range(tries):
        pts, keep, bnd, missing_edges = _triangulate_once(loops)
        if not missing_edges:
            return pts, keep, bnd, 0
        new = []
        for li, (l, area) in enumerate(loops):
            bad = {i for (lj, i) in missing_edges if lj == li}
            if not bad:
                new.append((l, area))
                continue
            out = []
            for i in range(len(l)):
                out.append(l[i])
                if i in bad:
                    out.append(0.5 * (l[i] + l[(i + 1) % len(l)]))
            new.append((np.array(out), area))
        loops = new
    return pts, keep, bnd, len(missing_edges)


def _triangulate_once(loops):
    pts = np.vstack([l for l, _ in loops])
    # joggled input: the end-face arcs are exactly cocircular, which otherwise gives flat triangles
    tri = Delaunay(pts, qhull_options="QJ")
    simp = tri.simplices
    p = pts[simp]
    area2 = (p[:, 1, 0] - p[:, 0, 0]) * (p[:, 2, 1] - p[:, 0, 1]) - (p[:, 1, 1] - p[:, 0, 1]) * (p[:, 2, 0] - p[:, 0, 0])
    simp = simp[np.abs(area2) > 1e-12]
    cen = pts[simp].mean(axis=1)
    inside = np.zeros(len(simp), int)
    for l, _ in loops:
        inside ^= Path(l).contains_points(cen).astype(int)
    keep = simp[inside.astype(bool)]
    # orient counterclockwise
    p = pts[keep]
    cross = (p[:, 1, 0] - p[:, 0, 0]) * (p[:, 2, 1] - p[:, 0, 1]) - (p[:, 1, 1] - p[:, 0, 1]) * (p[:, 2, 0] - p[:, 0, 0])
    keep = np.where((cross < 0)[:, None], keep[:, [0, 2, 1]], keep)
    # boundary edge check
    edges = set()
    for a, b, c in keep:
        edges.update(((a, b), (b, c), (c, a)))
    off = 0
    missing = []
    bnd = []
    for li, (l, area) in enumerate(loops):
        n = len(l)
        idx = np.arange(off, off + n)
        bnd.append((idx, area))
        for i in range(n):
            a, b = idx[i], idx[(i + 1) % n]
            if (a, b) not in edges and (b, a) not in edges:
                missing.append((li, i))
        off += n
    return pts, keep, bnd, missing


# ------------------------------------------------------------------ mesh
class Mesh:
    def __init__(self):
        self.V, self.T = [], []

    def prism(self, pts, tris, bnd, z0, z1):
        """Closed prism from a triangulated section (pts, ccw tris) between z0 and z1."""
        base = len(self.V)
        n = len(pts)
        self.V += [(x, y, z0) for x, y in pts]
        self.V += [(x, y, z1) for x, y in pts]
        for a, b, c in tris:
            self.T.append((base + a, base + c, base + b))           # bottom faces down
            self.T.append((base + n + a, base + n + b, base + n + c))  # top faces up
        # walls: walk each loop so the solid is on the left (ccw outer loops)
        for idx, area in bnd:
            order = idx if area > 0 else idx[::-1]
            for i in range(len(order)):
                a, b = order[i], order[(i + 1) % len(order)]
                self.T.append((base + a, base + b, base + n + b))
                self.T.append((base + a, base + n + b, base + n + a))
        return base, len(self.V)


def check_closed(M, ranges):
    """Every shell is closed: each directed edge appears once and its reverse once."""
    T = np.array(M.T)
    for v0, v1 in ranges:
        sel = T[(T[:, 0] >= v0) & (T[:, 0] < v1)]
        e = np.concatenate([sel[:, [0, 1]], sel[:, [1, 2]], sel[:, [2, 0]]])
        key = e[:, 0].astype(np.int64) * 10_000_000 + e[:, 1]
        rkey = e[:, 1].astype(np.int64) * 10_000_000 + e[:, 0]
        if len(np.unique(key)) != len(key) or not np.array_equal(np.sort(key), np.sort(rkey)):
            raise RuntimeError("shell %s is not closed" % ((v0, v1),))
    V = np.array(M.V)
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)


def build():
    zig = zigzag_field()
    # bands of identical layer sections
    bands = []
    for L in range(NLAYERS):
        zm = (L + 0.5) * LAYER
        key = (round(rail_hw(zm), 4), round(notch_hw(zm), 4))
        if bands and bands[-1][2] == key:
            bands[-1][1] = L + 1
        else:
            bands.append([L, L + 1, key])
    M = Mesh()
    shells, info = [], []
    for l0, l1, (wr, wn) in bands:
        zm = (l0 + 0.5) * LAYER
        f = section_field(zig, zm)
        loops = section_loops(f)
        pts, tris, bnd, missing = triangulate(loops)
        if missing:
            raise RuntimeError("band %d-%d: %d boundary edges missing" % (l0, l1, missing))
        shells.append(M.prism(pts, tris, bnd, l0 * LAYER, l1 * LAYER))
        info.append(dict(layers=(l0, l1), rail_hw=wr, notch_hw=wn, loops=len(loops), points=len(pts)))
    vol = check_closed(M, shells)
    return M, dict(volume_cm3=vol / 1000.0, bands=info, vertices=len(M.V), triangles=len(M.T),
                   gap_compressed=G_C, fold_step=DELTA, bump=DBUMP)


# ------------------------------------------------------------------ 3mf
def _uuid(tag):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "rfid/%s/%s" % (NAME, tag)))


def _fmt(v):
    s = ("%.5f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def thumbnails(M):
    out = {}
    V = np.array(M.V)
    for name, px in (("plate_1.png", 512), ("plate_1_small.png", 128)):
        fig = plt.figure(figsize=(px / 100, px / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor("#e8e8e8")
        T = np.array(M.T)
        top = V[T][:, :, 2].min(axis=1) >= H - 1e-6
        from matplotlib.collections import PolyCollection
        polys = V[T[top]][:, :, :2]
        ax.add_collection(PolyCollection(polys, facecolors="#6fa8dc", edgecolors="none"))
        ax.set_xlim(-5, L0 + 5)
        ax.set_ylim(W / 2 - (L0 + 10) / 2, W / 2 + (L0 + 10) / 2)
        ax.set_aspect("equal")
        ax.axis("off")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=100)
        plt.close(fig)
        out[name] = buf.getvalue()
    return out


OBJECT_SETTINGS = [("outer_wall_line_width", "1.05"), ("inner_wall_line_width", "1.05")]


def write_3mf(path, M):
    settings = json.load(open(os.path.join(HERE, "rfidSpring_settings_base.json")))
    zoff = H / 2.0
    cx, cy = L0 / 2.0, W / 2.0
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">',
             ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
             ' <resources>',
             '  <object id="3" p:UUID="%s" type="model">' % _uuid("part"),
             '   <mesh>', '    <vertices>']
    lines += ['     <vertex x="%s" y="%s" z="%s"/>' % (_fmt(x - cx), _fmt(y - cy), _fmt(z - zoff)) for x, y, z in M.V]
    lines += ['    </vertices>', '    <triangles>']
    lines += ['     <triangle v1="%d" v2="%d" v3="%d"/>' % t for t in M.T]
    lines += ['    </triangles>', '   </mesh>', '  </object>', ' </resources>', ' <build/>', '</model>', '']
    obj_path = "/3D/Objects/%s.model" % NAME
    today = datetime.date.today().isoformat()
    root = '''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">
 <metadata name="Application">BambuStudio-02.06.00.51</metadata>
 <metadata name="OrcaSlicer">2.4.2</metadata>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <metadata name="CreationDate">%s</metadata>
 <metadata name="ModificationDate">%s</metadata>
 <metadata name="Thumbnail_Middle">/Metadata/plate_1.png</metadata>
 <metadata name="Thumbnail_Small">/Metadata/plate_1_small.png</metadata>
 <metadata name="Title"></metadata>
 <resources>
  <object id="4" p:UUID="%s" type="model">
   <components>
    <component p:path="%s" objectid="3" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
   </components>
  </object>
 </resources>
 <build p:UUID="%s">
  <item objectid="4" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 128 128 %s" printable="1" auto_drop="1"/>
 </build>
</model>
''' % (today, today, _uuid("object"), obj_path, _uuid("component"), _uuid("build"), _uuid("item"), _fmt(zoff))
    ms = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>', '  <object id="4">',
          '    <metadata key="name" value="%s"/>' % NAME, '    <metadata key="extruder" value="1"/>']
    ms += ['    <metadata key="%s" value="%s"/>' % kv for kv in OBJECT_SETTINGS]
    ms += ['    <part id="3" subtype="normal_part">',
           '      <metadata key="name" value="%s"/>' % NAME,
           '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>',
           '      <metadata key="source_file" value="%s.3mf"/>' % NAME,
           '      <metadata key="source_object_id" value="0"/>',
           '      <metadata key="source_volume_id" value="0"/>',
           '      <metadata key="source_offset_x" value="0"/>',
           '      <metadata key="source_offset_y" value="0"/>',
           '      <metadata key="source_offset_z" value="0"/>',
           '      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>',
           '    </part>', '  </object>', '  <plate>',
           '    <metadata key="plater_id" value="1"/>',
           '    <metadata key="plater_name" value="%s"/>' % NAME.replace("_", " "),
           '    <metadata key="locked" value="false"/>',
           '    <metadata key="filament_map_mode" value="Auto For Flush"/>',
           '    <metadata key="filament_maps" value="1 1"/>',
           '    <model_instance>', '      <metadata key="object_id" value="4"/>',
           '      <metadata key="instance_id" value="0"/>', '      <metadata key="identify_id" value="300"/>',
           '    </model_instance>', '  </plate>', '  <assemble>',
           '   <assemble_item object_id="4" instance_id="0" transform="1 0 0 0 1 0 0 0 1 128 128 %s" offset="0 0 0" />' % _fmt(zoff),
           '  </assemble>', '</config>', '']
    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>
'''
    rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
 <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>
 <Relationship Target="/Metadata/plate_1.png" Id="rel-4" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-middle"/>
 <Relationship Target="/Metadata/plate_1_small.png" Id="rel-5" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-small"/>
</Relationships>
'''
    model_rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="%s" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
''' % obj_path
    slice_info = '''<?xml version="1.0" encoding="UTF-8"?>
<config>
  <header>
    <header_item key="X-BBL-Client-Type" value="slicer"/>
    <header_item key="X-BBL-Client-Version" value="02.06.00.51"/>
    <header_item key="OrcaSlicer-Version" value="2.4.2"/>
  </header>
</config>
'''
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", root)
        z.writestr("3D/_rels/3dmodel.model.rels", model_rels)
        z.writestr(obj_path.lstrip("/"), "\n".join(lines))
        z.writestr("Metadata/project_settings.config", json.dumps(settings, indent=4, ensure_ascii=False))
        z.writestr("Metadata/model_settings.config", "\n".join(ms))
        z.writestr("Metadata/layer_config_ranges.xml", '<?xml version="1.0" encoding="utf-8"?>\n<objects>\n</objects>\n')
        z.writestr("Metadata/custom_gcode_per_layer.xml", '<?xml version="1.0" encoding="utf-8"?>\n<custom_gcodes_per_layer>\n</custom_gcodes_per_layer>\n')
        z.writestr("Metadata/slice_info.config", slice_info)
        z.writestr("Metadata/filament_sequence.json", '{"plate_1": {"nozzle_sequence": [], "optimal_assignment": [], "sequence": []}}')
        for pname, data in thumbnails(M).items():
            z.writestr("Metadata/" + pname, data)
    return path


def main(out_dir="."):
    M, info = build()
    path = write_3mf(os.path.join(out_dir, NAME + ".3mf"), M)
    info["path"] = path
    return M, info


if __name__ == "__main__":
    M, info = main()
    for k, v in info.items():
        if k != "bands":
            print(k, v)
    for b in info["bands"]:
        print(b)
