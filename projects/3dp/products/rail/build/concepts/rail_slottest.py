"""Slot-fit test piece for rail layout A (design, not a build): one groove bar and three anchors. Run with run.sh.
Answers two things before the full set (design principle 7):
  - anchors: which hook height passes the real slots and hooks behind the steel: 3.0 / 3.3 / 3.6 total
    (neck 1.6 + drop 1.4 / 1.7 / 2.0), told apart by 1 / 2 / 3 notches across the head's front;
  - groove: how the rail slides on and holds an anchor head at 0.5 / 0.3 / 0.2 clearance, in three
    25 mm zones counted from the bar's beveled end (loosest first, so a tight zone never blocks a looser one).
Both print on their side (cabinet X up), as the rail and anchors will, so hook profiles, notches and
groove depths are in the layer outline and hook loads run along the layers.
Coords as rail_concepts.py: X across the strip, Y out from the strip face, Z up. Print frame: X = cab Z,
Y = -cab Y, Z = cab X - (part's lowest X). Writes T/*.stl (cabinet frame, for pictures) and
T/plate_slotTest.stl (all four parts in print position)."""
import os, math
import numpy as np, manifold3d as m, trimesh
from shapely.geometry import Polygon
from rail_concepts import XS, SLOT_H, TOPS, tm, box, ccw, prism_z, prism_x, strip, buttons
HERE = os.path.dirname(os.path.abspath(__file__))

LAYER = 0.3
# ---- anchor (the agreed concept's hook, grid-locked; head changed from hexagon to trapezoid) ----
AW = 7.8                    # width across the slot = print height: 26 layers; 0.45 per side in the 8.7 slot
NECK_T, NECK_H = 1.6, 1.6   # neck through the steel (hook gauge: a 1.6 gap fits 1.3-1.5 steel) and its height
DROP_T = 2.0                # drop behind the steel
HOOKS = [3.0, 3.3, 3.6]     # total hook height (neck + drop below it) to try against the 3.3-4 slot
HEAD_D, HEAD_L = 2.8, 20.0  # head depth off the strip face and length
UND = 1.2                   # dovetail undercut per side: 45 deg from 5.4 wide at the strip face to 7.8 (4 layers)
HN = AW / 2 - UND           # head half-width at the strip face, 2.7
# ---- groove bar (rail section, grid-locked) ----
RW, RD = 16.8, 16.0         # rail width (print height: 56 layers) and depth
RX0, RX1 = XS - RW / 2, XS + RW / 2
G_FLAT = 0.3                # clearance at the groove's sides and bottom, which don't set the fit
GX = AW / 2 + G_FLAT        # groove half-width at its sides, 4.2 (groove 8.4 = 28 layers, centered on 28)
GD = HEAD_D + G_FLAT        # groove depth, 3.1
ZONES = [0.5, 0.3, 0.2]     # in-layer gap on the 45 deg faces, from the beveled end
ZL = 25.0                   # zone length (head 20)
BL = ZL * len(ZONES)        # bar length 75
FLARE = 0.9                 # 45 deg lead-in at both groove mouths (3 layers)
BEVEL = 5.0                 # 45 deg bevel on the front corner of the marked end

def fillet_poly(pts, radii, n=10):
    """Polygon with each corner replaced by an arc tangent to both edges (convex or concave); r 0 stays sharp."""
    out, k = [], len(pts)
    for i in range(k):
        p0, p1, p2 = (np.array(pts[(i - 1) % k], float), np.array(pts[i], float), np.array(pts[(i + 1) % k], float))
        r = radii[i]
        if r <= 0:
            out.append(tuple(p1)); continue
        d1, d2 = (p0 - p1) / np.linalg.norm(p0 - p1), (p2 - p1) / np.linalg.norm(p2 - p1)
        th = math.acos(np.clip(d1 @ d2, -1, 1))
        t = r / math.tan(th / 2)
        assert t <= 0.5 * min(np.linalg.norm(p0 - p1), np.linalg.norm(p2 - p1)) + 1e-9, (pts[i], r)
        a, b = p1 + d1 * t, p1 + d2 * t
        bis = (d1 + d2) / np.linalg.norm(d1 + d2); c = p1 + bis * r / math.sin(th / 2)
        a0, a1 = math.atan2(*(a - c)[::-1]), math.atan2(*(b - c)[::-1])
        sw = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        out += [tuple(c + r * np.array([math.cos(a0 + sw * j / n), math.sin(a0 + sw * j / n)])) for j in range(n + 1)]
    return out

def top_inset(r):           # fillet of radius r on the top edges: inset at a height h below the top face
    return lambda h: r - math.sqrt(max(r * r - (r - h) ** 2, 0.0)) if h < r else 0.0
def bed_inset(hc):          # 45 deg chamfer ending at hc (on the grid), blended into the wall by an arc ending one layer higher
    s = LAYER / (1 + 1 / math.sqrt(2)); rf = s / math.tan(math.radians(22.5)); a = hc + s / math.sqrt(2)
    zc = hc + LAYER          # arc center height (tangent point on the wall)
    def f(z):
        if z <= hc:
            return a - z
        if z < zc:
            return rf - math.sqrt(max(rf * rf - (z - zc) ** 2, 0.0))
        return 0.0
    return f, zc

def offset_in(P, e):
    """Mitre offset of a CCW polygon inward by e (every vertex kept, so offset rings can be joined vertex to vertex)."""
    if e <= 0:
        return np.array(P, float)
    P = np.array(P, float); k = len(P); out = []
    for i in range(k):
        a, b, c = P[i - 1], P[i], P[(i + 1) % k]
        n1 = np.array([(b - a)[1], -(b - a)[0]]) / np.linalg.norm(b - a)    # outward normals of the two edges
        n2 = np.array([(c - b)[1], -(c - b)[0]]) / np.linalg.norm(c - b)
        bis = n1 + n2; out.append(b - e * bis / (1 + n1 @ n2))
    return np.array(out)

def stack_x(pts, x0, x1, top_r=0.0, bed_hc=None, n_top=8, n_bed=4):
    """YZ outline (y, z) extruded along X from x0 (bed side) to x1 (top side), lofted so its horizontal print edges are
    rounded: a fillet of top_r on the top face's edges and a 45 deg chamfer plus fillet on the bed face's edges."""
    P = np.array(ccw([tuple(p) for p in pts]), float); N = len(P)
    lv = []
    if bed_hc is not None:
        f, zt = bed_inset(bed_hc)
        lv += [(x0, f(0.0))] + [(x0 + bed_hc + (zt - bed_hc) * j / n_bed, f(bed_hc + (zt - bed_hc) * j / n_bed)) for j in range(n_bed + 1)]
    else:
        lv.append((x0, 0.0))
    if top_r > 0:
        g = top_inset(top_r)
        lv += [(x1 - top_r * (1 - j / n_top), g(top_r * (1 - j / n_top))) for j in range(n_top + 1)]
    else:
        lv.append((x1, 0.0))
    rings = [offset_in(P, e) for _, e in lv]
    V = np.concatenate([np.column_stack([np.full(N, x), r[:, 0], r[:, 1]]) for (x, _), r in zip(lv, rings)])
    T = []
    for k in range(len(lv) - 1):
        for i in range(N):
            a, b, c, d = k * N + i, k * N + (i + 1) % N, (k + 1) * N + (i + 1) % N, (k + 1) * N + i
            T += [(a, b, c), (a, c, d)]
    cap = np.asarray(m.triangulate([rings[0]]))
    T += [tuple(t[::-1]) for t in cap]                              # bed cap faces -X
    top = np.asarray(m.triangulate([rings[-1]])) + (len(lv) - 1) * N
    T += [tuple(t) for t in top]
    # (u=y, v=z) ring CCW about +X: x = level, y = u, z = v is a rotation of (u, v, w), so faces point outward
    return m.Manifold(m.Mesh(np.asarray(V, np.float32), np.asarray(T, np.uint32)))

def anchor(top, total, marks):
    """Anchor seated in the slot whose top edge is at `top`: neck on the slot's bottom edge, drop behind the steel."""
    zb = top - SLOT_H; d = total - NECK_H; zc = zb + NECK_H / 2; h0, h1 = zc - HEAD_L / 2, zc + HEAD_L / 2
    yz = [(0, h0), (HEAD_D, h0), (HEAD_D, h1), (0, h1), (0, zb + NECK_H), (-NECK_T - DROP_T, zb + NECK_H),
          (-NECK_T - DROP_T, zb - d), (-NECK_T, zb - d), (-NECK_T, zb), (0, zb)]
    r = [1.0, 1.0, 1.0, 1.0, 0, 1.0, 1.0, 0.7, 0, 0]   # neck and throat corners sharp: they seat on the slot edge
    a = stack_x(fillet_poly(yz, r), XS - AW / 2, XS + AW / 2, top_r=0.6, bed_hc=0.3)   # small: bigger thins the 1.6 neck band below a bead
    w = AW / 2                                          # head: trapezoid dovetail; neck and drop full width
    xy = [(-w, -NECK_T - DROP_T - 1), (w, -NECK_T - DROP_T - 1), (w, 0), (HN, 0), (w, UND), (w, HEAD_D + 1),
          (-w, HEAD_D + 1), (-w, UND), (-HN, 0), (-w, 0)]
    a ^= prism_z([(XS + x, y) for x, y in xy], h0 - 1, h1 + 1)
    for k in range(marks):                              # notches across the head's front, from its top end
        zm = h1 - 3.0 - 2.5 * k
        a -= prism_x([(HEAD_D + 0.01, zm - 0.8), (HEAD_D - 0.8, zm), (HEAD_D + 0.01, zm + 0.8)], XS - AW, XS + AW)
    return a

def groove(c, ge=0.0):      # groove profile (x, y): 45 deg faces at in-layer gap c from the head's, flared out by ge
    a, b, dd = HN + c + ge, GX + ge, GD + ge     # bottom corners: 45 deg fill under the ceiling (top side), r0.6 on the floor side
    pts = [(-(a - 1), -1), (a - 1, -1), (b, b - a), (b, dd - 0.6), (b - 0.6, dd)]
    pts += fillet_poly([(-(b - 1.3), dd), (-b, dd), (-b, dd - 1.3)], [0, 0.6, 0], n=6)[1:-1] + [(-b, b - a)]
    return [(XS + x, y) for x, y in pts]
def slice_z(pts, z):
    return prism_z(pts, z - 0.005, z + 0.005)

def bar(z0):
    """Groove bar standing as mounted, beveled end at the bottom (z0); zones 0.5, 0.3, 0.2 upward."""
    z1 = z0 + BL
    yz = [(0, z0), (RD - BEVEL, z0), (RD, z0 + BEVEL), (RD, z1), (0, z1)]
    b = stack_x(fillet_poly(yz, [2.0, 2.0, 2.0, 2.0, 2.0]), RX0, RX1, top_r=1.5, bed_hc=1.2)
    cut = []
    for i, c in enumerate(ZONES):
        cut.append(prism_z(groove(c), z0 - 1 + (i > 0) * (1 + ZL * i), z0 + ZL * (i + 1) + (i == len(ZONES) - 1)))
        if i:                                           # 1 mm ramp from the looser zone into this one
            zb = z0 + ZL * i
            cut.append(m.Manifold.hull(slice_z(groove(ZONES[i - 1]), zb) + slice_z(groove(c), zb + 1.0)))
    cut.append(m.Manifold.hull(slice_z(groove(ZONES[0], FLARE), z0) + slice_z(groove(ZONES[0]), z0 + FLARE)))
    cut.append(m.Manifold.hull(slice_z(groove(ZONES[-1], FLARE), z1) + slice_z(groove(ZONES[-1]), z1 - FLARE)))
    for i in range(1, len(ZONES)):                      # V marks across the front face at the zone boundaries
        zb = z0 + ZL * i
        cut.append(prism_x([(RD + 0.01, zb - 0.6), (RD - 0.6, zb), (RD + 0.01, zb + 0.6)], RX0 - 1, RX1 + 1))
    return b - m.Manifold.batch_boolean(cut, m.OpType.Add)

def to_print(man, xlow, px, py):
    """Cabinet frame -> print frame (X = cab Z, Y = -cab Y, Z = cab X - xlow), then placed with its min corner at (px, py)."""
    M = np.array([[0, 0, 1], [0, -1, 0], [1, 0, 0]], float)
    t = tm(man); t.vertices = t.vertices @ M.T; t.vertices[:, 2] -= xlow
    lo = t.vertices.min(axis=0); t.vertices[:, 0] += px - lo[0]; t.vertices[:, 1] += py - lo[1]
    return t

if __name__ == "__main__":
    out = os.path.join(HERE, "T"); os.makedirs(out, exist_ok=True)
    # mounted example on the lower slot group: anchors 3.0, 3.3 and 3.6 in the top, middle and bottom slots;
    # the bar slid down over the top anchor so it sits in zone 1 (0.5)
    lower = [t for t in TOPS if t < 500][::-1]          # 389.8, 355.0, 320.2
    anchors = [anchor(t, h, k + 1) for k, (t, h) in enumerate(zip(lower, HOOKS))]
    for k, a in enumerate(anchors):
        tm(a).export(os.path.join(out, f"anchor{k + 1}.stl"))
    zc = lower[0] - SLOT_H + NECK_H / 2
    for i in range(3):                                  # the bar with the top anchor centered in zone i+1
        tm(bar(zc - ZL * (i + 0.5))).export(os.path.join(out, f"bar_zone{i + 1}.stl"))
    tm(strip(250, 470)).export(os.path.join(out, "strip.stl"))
    # print plate: bar and anchors in print position
    parts = [to_print(bar(0.0), RX0, 90, 100)]
    for k in range(3):
        parts.append(to_print(anchor(TOPS[0], HOOKS[k], k + 1), XS - AW / 2, 90 + 27 * k, 80))
    trimesh.util.concatenate(parts).export(os.path.join(out, "plate_slotTest.stl"))
    for k, p in enumerate(parts):
        p.export(os.path.join(out, f"print_{['bar', 'anchor1', 'anchor2', 'anchor3'][k]}.stl"))
        e = p.vertices.max(axis=0) - p.vertices.min(axis=0)
        print(["bar", "anchor1", "anchor2", "anchor3"][k], "print size %.2f x %.2f x %.2f" % tuple(e),
              "volume %.2f cm3" % (p.volume / 1000))
