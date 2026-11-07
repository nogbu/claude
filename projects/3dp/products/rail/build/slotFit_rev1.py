"""slotFit_rev1 build script (rail, layout A): slot-fit test piece, one plate in PETG High Flow, my process settings.
Geometry from concepts/rail_slottest.py (2026-10-09), with the groove changed from a dovetail (its upper lip
started in midair when printed) to a square hook on the fold side and a 45 deg roof on the glass side.
  - three anchors, hook 3.0 / 3.3 / 3.6 total (neck 1.6 + drop 1.4 / 1.7 / 2.0), told apart by 1 / 2 / 3 notches;
  - one groove bar, 75 long, with 0.5 / 0.3 / 0.2 in-layer gap on the hook face in 25 mm zones from the beveled end.
The hook face holds the rail to the strip; the lip top and the groove floor (one layer each) hold it sideways;
the roof only clears the head (0.6), so the anchor's bed side carries no fit face.
All print on their side. The bar lies on its fold side (cabinet X up), so its lip builds up from the groove floor;
the anchors lie on their glass side (cabinet X down), so the head's hook is on top and the head stands on a 1.18
foot along its length, rising at 45 deg. Both layer grids fall on the same cabinet X values, so every layer's gap is exact.
Cabinet frame: X across the strip (fold side -X), Y out from the strip face, Z up. Print frame, bar: X = cab Z,
Y = -cab Y, Z = cab X - RX0; anchors: X = cab Z, Y = cab Y, Z = (XS + AW/2) - cab X.
Run: python3 slotFit_rev1.py [outdir] -> slotFit_rev1.3mf (and one STL per part) in outdir."""
import os, sys, math, json
import numpy as np, manifold3d as m, trimesh
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import write3mf as W

LAYER = 0.3
# ---- cabinet (unicoly, as rail_concepts.py 2026-10-09) ----
SW = 17.0                   # strip width
SLOT_W, SLOT_H = 8.7, 3.6   # slot 8.7 wide, 3.3-4 tall: 3.6 drawn
XS = -SW / 2 + 3.5 + SLOT_W / 2   # slot center across the strip: -0.75
# ---- anchor ----
AW = 7.8                    # width across the slot = print height: 26 layers; 0.45 per side in the 8.7 slot
NECK_T, NECK_H = 1.6, 1.6   # neck through the steel and its height
DROP_T = 2.0                # drop behind the steel
HOOKS = [3.0, 3.3, 3.6]     # total hook height (neck + drop below it)
HEAD_D, HEAD_L = 2.8, 20.0  # head depth off the strip face and length
# head and groove across the strip in u = cab X - XS (fold side negative)
HOOK_T = 1.24               # head's hook thickness in Y: 2 beads
T_A = HEAD_D - HOOK_T       # hook face 1.56 off the strip face (the throat's depth)
LIP_TOP = -2.7              # top of the bar's lip (bar Z 5.7, 19 layers); the hook reaches 1.2 below it, to -3.9
G_TOP = 0.3                 # lip top to throat bottom: one layer
S_ARC = LAYER / (1 + 1 / math.sqrt(2))   # tangent length of a one-layer arc between a 45 deg face and a wall (as bed_inset)
R_ARC = S_ARC / math.tan(math.radians(22.5))   # its radius, 0.42
FOOT = HEAD_D - 1.5 - S_ARC / math.sqrt(2)     # head's glass side: on the anchor's bed for 1.18 off the strip face, then
                            # 45 deg to print Z 1.5 and an R_ARC arc into the head's front, ending at print Z 1.8
KB = 5.7                    # the roof meets the bar's back face at u 5.7 (bar Z 14.1, 47 layers)
R_CL = KB - AW / 2 - FOOT   # roof's in-layer clearance over the head's 45 deg face, 0.62 (not a fit face)
# ---- groove bar ----
RW, RD = 16.8, 16.0         # rail width (print height: 56 layers) and depth
RX0, RX1 = XS - RW / 2, XS + RW / 2
G_FLAT = 0.3                # clearance at the groove's fold-side floor (pocket floor to hook end)
GX = AW / 2 + G_FLAT        # groove half-width at its sides, 4.2
GD = KB - 2.4 - S_ARC       # groove depth 3.12 (0.32 past the head): the roof's R_ARC arc into the groove bottom
                            # runs from u 2.4 to 2.7 (bar Z 10.8 to 11.1)
ZONES = [0.5, 0.3, 0.2]     # in-layer gap on the hook face, from the beveled end
ZL = 25.0                   # zone length (head 20)
BL = ZL * len(ZONES)        # bar length 75
FLARE = 0.9                 # 45 deg lead-in at both groove mouths (3 layers)
BEVEL = 5.0                 # 45 deg bevel on the front corner of the marked end

def tm(man):
    g = man.to_mesh(); return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts))
def ccw(pts):
    a = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(pts, pts[1:] + pts[:1]))
    return pts if a > 0 else pts[::-1]
def prism_z(pts, z0, z1):     # XY polygon along Z
    return m.Manifold.extrude(m.CrossSection([ccw(pts)]), z1 - z0).translate([0, 0, z0])
def prism_x(pts, x0, x1):     # YZ polygon along X
    return m.Manifold.extrude(m.CrossSection([ccw(pts)]), x1 - x0).rotate([90, 0, 90]).translate([x0, 0, 0])

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
    zc = hc + LAYER
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
        n1 = np.array([(b - a)[1], -(b - a)[0]]) / np.linalg.norm(b - a)
        n2 = np.array([(c - b)[1], -(c - b)[0]]) / np.linalg.norm(c - b)
        bis = n1 + n2; out.append(b - e * bis / (1 + n1 @ n2))
    return np.array(out)

def stack_x(pts, x0, x1, top_r=0.0, bed_hc=None, n_top=8, n_bed=4):
    """YZ outline extruded along X from x0 (bed side) to x1 (top side), lofted so its horizontal print edges are
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
    T += [tuple(t[::-1]) for t in cap]
    top = np.asarray(m.triangulate([rings[-1]])) + (len(lv) - 1) * N
    T += [tuple(t) for t in top]
    return m.Manifold(m.Mesh(np.asarray(V, np.float32), np.asarray(T, np.uint32)))

def anchor(top, total, marks):
    """Anchor seated in the slot whose top edge is at `top`: neck on the slot's bottom edge, drop behind the steel."""
    zb = top - SLOT_H; d = total - NECK_H; zc = zb + NECK_H / 2; h0, h1 = zc - HEAD_L / 2, zc + HEAD_L / 2
    yz = [(0, h0), (HEAD_D, h0), (HEAD_D, h1), (0, h1), (0, zb + NECK_H), (-NECK_T - DROP_T, zb + NECK_H),
          (-NECK_T - DROP_T, zb - d), (-NECK_T, zb - d), (-NECK_T, zb), (0, zb)]
    r = [1.0, 1.0, 1.0, 1.0, 0, 1.0, 1.0, 0.7, 0, 0]   # neck and throat corners sharp: they seat on the slot edge
    a = stack_x(fillet_poly(yz, r), XS - AW / 2, XS + AW / 2, top_r=0.6, bed_hc=0.3)
    a = a.mirror([1, 0, 0]).translate([2 * XS, 0, 0])  # prints glass side down: bed chamfer at +X, top fillet at -X
    w = AW / 2                                          # head: hook on the fold side, 45 deg face on the glass side
    uc = w + FOOT - HEAD_D                              # where the 45 deg face would meet the head's front
    arc = fillet_poly([(w, FOOT), (uc, HEAD_D), (uc - 1, HEAD_D)], [0, R_ARC, 0], n=6)[1:-1]   # that corner, rounded
    xy = [(-w, -NECK_T - DROP_T - 1), (w, -NECK_T - DROP_T - 1), (w, FOOT)] + arc + [(arc[-1][0], HEAD_D + 1),
          (-w, HEAD_D + 1), (-w, T_A), (LIP_TOP + G_TOP, T_A), (LIP_TOP + G_TOP, -0.005), (-w, -0.005)]   # notch starts 5 um behind
          # the strip face so it doesn't share the head's back face (a shared face leaves zero-thickness fins)
    a ^= prism_z([(XS + x, y) for x, y in xy], h0 - 1, h1 + 1)
    u0, u1 = -1.5, LIP_TOP + G_TOP                      # marks stop short of the hook (u -3.9 to -2.4), which a 0.8 V would cut
    for k in range(marks):                              # through: full depth to u -1.5 (print Z 5.4), then a 45 deg-ish taper
        zm = h1 - 3.0 - 2.5 * k                         # gone by the throat bottom (u -2.4, print Z 6.3); from the head's top end
        V = [(HEAD_D + 0.01, zm - 0.8), (HEAD_D - 0.8, zm), (HEAD_D + 0.01, zm + 0.8)]
        tip = [(HEAD_D + 0.01, zm - 0.05), (HEAD_D + 0.005, zm), (HEAD_D + 0.01, zm + 0.05)]
        a -= prism_x(V, XS + u0, XS + AW) + m.Manifold.hull(prism_x(V, XS + u0, XS + u0 + 0.01) + prism_x(tip, XS + u1 - 0.01, XS + u1))
    return max(a.decompose(), key=lambda c: c.volume())   # drop any zero-volume slivers the head cut leaves on the strip face

def groove(c, ge=0.0):
    """Groove profile (x, y) as two convex pieces, gap c on the hook face, flared out by ge:
    A, mouth and roof: from the lip top up to the 45 deg roof, rounded into the groove bottom;
    B, pocket behind the lip, r0.6 at its deep floor corner."""
    kb, mt, l, b, dd = KB + ge, LIP_TOP - ge, T_A - c - ge, GX + ge, GD + ge
    A = fillet_poly([(mt, -1), (kb + 1, -1), (kb - dd, dd), (mt, dd)], [0, 0, R_ARC, 0], n=6)
    B = fillet_poly([(-b, l), (mt + 0.5, l), (mt + 0.5, dd), (-b, dd)], [0, 0, 0, 0.6], n=6)
    return [[(XS + x, y) for x, y in P] for P in (A, B)]
def slice_z(pts, z):
    return prism_z(pts, z - 0.005, z + 0.005)
def hull_z(g0, z0, g1, z1):     # each convex piece hulled from profile g0 at z0 to g1 at z1
    return [m.Manifold.hull(slice_z(p, z0) + slice_z(q, z1)) for p, q in zip(g0, g1)]

def bar(z0):
    """Groove bar standing as mounted, beveled end at the bottom (z0); zones 0.5, 0.3, 0.2 upward."""
    z1 = z0 + BL
    yz = [(0, z0), (RD - BEVEL, z0), (RD, z0 + BEVEL), (RD, z1), (0, z1)]
    b = stack_x(fillet_poly(yz, [2.0, 2.0, 2.0, 2.0, 2.0]), RX0, RX1, top_r=1.5, bed_hc=1.2)
    cut = []
    for i, c in enumerate(ZONES):
        cut += [prism_z(p, z0 - 1 + (i > 0) * (1 + ZL * i), z0 + ZL * (i + 1) + (i == len(ZONES) - 1)) for p in groove(c)]
        if i:                                           # 1 mm ramp from the looser zone into this one
            zb = z0 + ZL * i
            cut += hull_z(groove(ZONES[i - 1]), zb, groove(c), zb + 1.0)
    cut += hull_z(groove(ZONES[0], FLARE), z0, groove(ZONES[0]), z0 + FLARE)
    cut += hull_z(groove(ZONES[-1], FLARE), z1, groove(ZONES[-1]), z1 - FLARE)
    for i in range(1, len(ZONES)):                      # V marks across the front face at the zone boundaries
        zb = z0 + ZL * i
        cut.append(prism_x([(RD + 0.01, zb - 0.6), (RD - 0.6, zb), (RD + 0.01, zb + 0.6)], RX0 - 1, RX1 + 1))
    return b - m.Manifold.batch_boolean(cut, m.OpType.Add)

def to_print(man, xbed, px, py, flip=False):
    """Cabinet frame -> print frame, bed at cab X = xbed, min corner placed at (px, py).
    flip False (bar): X = cab Z, Y = -cab Y, Z = cab X - xbed; True (anchors): X = cab Z, Y = cab Y, Z = xbed - cab X."""
    M = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]] if flip else [[0, 0, 1], [0, -1, 0], [1, 0, 0]], float)
    t = tm(man); t.vertices = t.vertices @ M.T; t.vertices[:, 2] += xbed if flip else -xbed
    lo = t.vertices.min(axis=0); t.vertices[:, 0] += px - lo[0]; t.vertices[:, 1] += py - lo[1]
    return t

# plate layout (plate coordinates, min corners): bar across the middle, anchors 12 in front of it, 7.5 apart
BAR_AT = (90.5, 128.0)
ANCHOR_AT = [(90.5 + 27.5 * k, 109.6) for k in range(3)]

def build():
    parts = {"slotFit_rev1_bar": to_print(bar(0.0), RX0, *BAR_AT)}
    for k in range(3):
        parts[f"slotFit_rev1_anchor{k + 1}"] = to_print(anchor(SLOT_H + 10.0, HOOKS[k], k + 1), XS + AW / 2, *ANCHOR_AT[k], flip=True)
    return parts

SEAM = 'paint_seam="4"'
def seam_paint(name, t):
    """Seam enforcers, so no seam lands on a fit or seat face (Aligned alone put them in the anchor's throat corner,
    where the slot edge seats, and on the bar's lip face at the zone ramps). Anchors: the drop's back face with its bed
    chamfer and top fillet (free, facing into the post), and the head's front (0.32 clear of the groove bottom). In the
    hook layers, where the hook prints as its own 2-bead island, its seam then sits on the head's end corner.
    (A narrower strip on the head's front sent two layers' seams to the neck-top corner; checked in the G-code.) Bar: the lip's lead-out at the
    far (unmarked) end, on the layers where the lip prints as its own island; the bar's main loop keeps its seam in the
    V mark on the front face."""
    c, n = t.triangles_center, t.face_normals
    lo, hi = t.bounds
    if "anchor" in name:                                # print Z = (XS + AW/2) - cab X: the hook layers are above Z 6.3
        sel = (((n[:, 1] < -0.99) & (c[:, 1] < lo[1] + 0.01))                                     # drop back
               | ((n[:, 1] < -0.5) & (n[:, 2] < -0.3) & (c[:, 1] < lo[1] + 0.5) & (c[:, 2] < 0.7))   # its bed chamfer
               | ((n[:, 1] < -0.3) & (n[:, 2] > 0.3) & (c[:, 1] < lo[1] + 0.7) & (c[:, 2] > hi[2] - 0.7))   # its top fillet
               | ((n[:, 1] > 0.99) & (c[:, 1] > hi[1] - 0.01)))                                    # head front
    else:                                               # print Z = u + RW / 2: the lip is its own island above the pocket floor (Z 4.2)
        sel = ((c[:, 0] > hi[0] - FLARE + 0.05) & (c[:, 1] > hi[1] - 1.5) & (c[:, 2] > RW / 2 - GX + 0.05)
               & (c[:, 2] < LIP_TOP + RW / 2 + 0.1) & (n[:, 1] < 0.9) & (np.abs(n[:, 2]) < 0.9))
    return [SEAM if s else "" for s in sel]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    parts = build()
    for n, t in parts.items():
        e = t.extents
        print(n, "watertight", t.is_watertight, "size %.2f x %.2f x %.2f" % tuple(e), "volume %.2f cm3" % (t.volume / 1000),
              "min", np.round(t.vertices.min(axis=0), 2).tolist())
        t.export(os.path.join(out, n + ".stl"))
    s = W.base(os.path.join(HERE, "rail_settings_base.json"))       # PETG HF profile from rfidSpring (never edit a base in place)
    s["filament_colour"] = ["#000000"] + s["filament_colour"][1:]    # PETG HF Black
    objs = [W.Obj(n, [W.Part(t.vertices, t.faces, paint=seam_paint(n, t))]) for n, t in parts.items()]   # at=None: plate coordinates kept
    print("wrote", W.write(os.path.join(out, "slotFit_rev1.3mf"), objs, s))
