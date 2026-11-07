"""Rail concept models, layout A (agreed 2026-10-09) and concept C, scratch working models, not builds. Run with run.sh.
Coords: X across the strip (fold edge -8.5, glass edge +8.5), Y out from the strip face (steel at Y<0,
rail and shelf at Y>0), Z up from the cabinet floor. All cabinet values from unicoly (2026-10-09).
Concept A: floor-standing rail column held to the strip by small anchors that hook into the slots and
slide in a groove up the rail's back. Concept C: one-piece height clips that hook into two slots.
Writes one STL per object into ./A and ./C, then the pictures. Fillets not modeled yet."""
import os, sys
import numpy as np, manifold3d as m, trimesh
from shapely.geometry import Polygon
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- cabinet (unicoly) ----
SW = 17.0                     # strip width (16.6-17.6 photos; 17 drawn)
ST = 1.5                      # steel thickness (1.3-1.5 from the hook gauge)
SLOT_W, SLOT_H = 8.7, 3.6     # slot 8.7 wide (144310), 3.3-4 tall: 3.6 drawn
SLOT_X0 = -SW / 2 + 3.5       # 3.5 from the fold edge (144342, low confidence)
XS = SLOT_X0 + SLOT_W / 2     # slot center across the strip: -0.75
PITCH = 34.8
GROUPS = [355.0, 721.0, 1090.0]                        # middle-slot top edges (agreed change 2)
TOPS = sorted(g + k * PITCH for g in GROUPS for k in (-1, 0, 1))
BUTTONS = [260.0, 626.0, 996.0, 1359.0]                # glass button centers, 16.5 tall
ZMAX = 1400.0

def tm(man):
    g = man.to_mesh(); return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts))
def box(x0, x1, y0, y1, z0, z1):
    return m.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
def ccw(pts):
    a = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(pts, pts[1:] + pts[:1]))
    return pts if a > 0 else pts[::-1]
def prism_z(pts, z0, z1):     # XY polygon along Z
    return m.Manifold.extrude(m.CrossSection([ccw(pts)]), z1 - z0).translate([0, 0, z0])
def prism_x(pts, x0, x1):     # YZ polygon along X
    return m.Manifold.extrude(m.CrossSection([ccw(pts)]), x1 - x0).rotate([90, 0, 90]).translate([x0, 0, 0])

def strip(z0=0.0, z1=ZMAX):
    s = box(-SW / 2, SW / 2, -ST, 0, z0, z1) + box(-SW / 2 - 1.5, -SW / 2, -20, 0, z0, z1)   # strip + fold flange
    for t in TOPS:
        if z0 - 5 < t < z1 + 5:
            s -= box(SLOT_X0, SLOT_X0 + SLOT_W, -ST - 1, 1, t - SLOT_H, t)
    return s
def buttons(z0=0.0, z1=ZMAX):  # guessed size: reach 3.5 onto the strip, 2 proud (not measured)
    b = m.Manifold()
    for c in BUTTONS:
        if z0 - 10 < c < z1 + 10:
            b += box(SW / 2 - 3.5, SW / 2 + 2, 0, 2.0, c - 8.25, c + 8.25)
    return b

# ---- concept A: anchored rail column ----
RD = 16.0                     # rail depth off the strip face: 16 keeps the pocket section at 34 MPa (section_stress)
RX0, RX1 = XS - SW / 2, XS + SW / 2      # rail centered on the slot, so one part fits every corner
POS = [152.4 + 50.8 * k for k in range(24)]           # ledge tops, 6in to 52in every 2in
JOFF = 33.0                   # joint sits 33 below a ledge top
JOINTS = [221.0, 424.2, 627.4, 830.6, 1033.8]           # bottom 221, four 203.2 pieces, top 304.8
TOP_END = 1320.8 + 17.8
C = 0.2                       # groove and notch clearance per side (dp 6 snug; to test)
# groove: hexagon so every roof is 45 deg when the rail prints on its side
GROOVE = [(-3.0, 0), (-4.2, 1.2), (-4.2, 1.8), (-3.0, 3.0), (3.0, 3.0), (4.2, 1.8), (4.2, 1.2), (3.0, 0)]
GROOVE = [(XS + x, y) for x, y in GROOVE]
REL_W, REL_D = 3.0, 2.5       # button relief on both back edges (size waits on the button measurement)

def notch(pos):               # front opening + pocket the clip's hook drops into, cut through the width
    o = box(RX0 - 1, RX1 + 1, RD - 4 - C, RD + 1, pos - 12 - C, pos + C)
    p = box(RX0 - 1, RX1 + 1, RD - 7 - C, RD - 4, pos - 15 - C, pos - 3 + C)
    return o + p
TEN = (XS - 4, XS + 4, 5.0, 10.0, 10.0)   # tenon x0, x1, y0, y1, height
def rail_piece(z0, z1, tenon_top=True, socket_bottom=True):
    r = box(RX0, RX1, 0, RD, z0, z1)
    r -= prism_z([(x, y - 0.01) if y == 0 else (x, y) for x, y in GROOVE], z0 - 1, z1 + 1)
    r -= box(RX0 - 1, RX0 + REL_W, -1, REL_D, z0 - 1, z1 + 1) + box(RX1 - REL_W, RX1 + 1, -1, REL_D, z0 - 1, z1 + 1)
    for p in POS:
        if z0 < p - 15 and p < z1:
            r -= notch(p)
    x0, x1, y0, y1, h = TEN
    if tenon_top:
        t = box(x0, x1, y0, y1, z1, z1 + h - 1.0)
        t += m.Manifold.hull(box(x0, x1, y0, y1, z1 + h - 1.0, z1 + h - 0.99) + box(x0 + 1, x1 - 1, y0 + 1, y1 - 1, z1 + h - 0.01, z1 + h))
        r += t
    if socket_bottom:
        r -= box(x0 - C, x1 + C, y0 - C, y1 + C, z0 - 1, z0 + h + C)
    return r

def anchor(top):              # rests on the slot's bottom edge; neck + drop = 3.0 tall to pass a 3.3 slot
    zb = top - SLOT_H
    neck = box(XS - 4, XS + 4, -1.6, 0.0, zb, zb + 1.6)
    drop = box(XS - 4, XS + 4, -3.6, -1.6, zb - 1.4, zb + 1.6)
    head_pts = [(-2.8, 0), (-4.0, 1.2), (-4.0, 1.6), (-2.8, 2.8), (2.8, 2.8), (4.0, 1.6), (4.0, 1.2), (2.8, 0)]
    head = prism_z([(XS + x, y) for x, y in head_pts], zb + 0.8 - 10, zb + 0.8 + 10)
    return neck + drop + head

def clip(pos):                # seated: hook in the pocket, ledge top = shelf height
    x0, x1 = RX0, RX1
    plate = box(x0, x1, RD, RD + 3, pos - 30, pos)
    ledge = box(x0, x1, RD, RD + 15, pos - 5, pos)
    brace = prism_x([(RD + 3, pos - 30), (RD + 15, pos - 5), (RD + 3, pos - 5)], x0, x1)
    tongue = box(x0, x1, RD - 4, RD, pos - 12, pos - 3)
    hook = box(x0, x1, RD - 7, RD - 4, pos - 15, pos - 6)
    return plate + ledge + brace + tongue + hook

def clip_plain(pos):          # no brace: 6 plate carries the moment, 9 of ledge underside left to pinch
    x0, x1 = RX0, RX1
    plate = box(x0, x1, RD, RD + 6, pos - 30, pos)
    ledge = box(x0, x1, RD, RD + 15, pos - 6, pos)
    tongue = box(x0, x1, RD - 4, RD, pos - 12, pos - 3)
    hook = box(x0, x1, RD - 7, RD - 4, pos - 15, pos - 6)
    return plate + ledge + tongue + hook

def clip_stress():            # tip load 200 N, 15 out from the rail face (inference)
    P = 200.0
    def sig(M, t): return M * (t / 2) / (SW * t ** 3 / 12)
    F = P * 15.0 / 20.0       # couple between the hook (pocket, ~pos-10) and the plate's bottom bearing (pos-30)
    return dict(ledge_root=sig(P * 9.0, 6.0), plate_at_pocket=sig(F * 15.0, 6.0), plate3_if_no_brace=sig(F * 15.0, 3.0))

def section_stress():         # rail at a pocket: material between the strip face and the pocket
    from shapely.ops import unary_union
    W = RD - 7 - C
    full = Polygon([(RX0, 0), (RX1, 0), (RX1, W), (RX0, W)])
    cut = unary_union([Polygon(GROOVE), Polygon([(RX0 - 1, -1), (RX0 + REL_W, -1), (RX0 + REL_W, REL_D), (RX0 - 1, REL_D)]),
                       Polygon([(RX1 - REL_W, -1), (RX1 + 1, -1), (RX1 + 1, REL_D), (RX1 - REL_W, REL_D)])])
    s = full.difference(cut)
    import numpy as np
    xs, ys = np.meshgrid(np.linspace(RX0, RX1, 341), np.linspace(0, W, 141))
    import shapely
    inside = shapely.contains_xy(s, xs, ys); dA = (SW / 340) * (W / 140)
    yc = ys[inside].mean(); I = (((ys[inside] - yc) ** 2).sum()) * dA
    cmax = max(yc, W - yc)
    M = 200.0 * 15.0           # N*mm: 40 lb x 0.75 / 2 x SF 3 = 200 N at the ledge tip, 15 out
    return s.area, I, M * cmax / I

def build_A():
    os.makedirs(os.path.join(HERE, "A"), exist_ok=True)
    ends = [0.0] + JOINTS + [TOP_END]
    names = ["bottom", "p2", "p3", "p4", "p5", "top"]
    for i, n in enumerate(names):
        r = rail_piece(ends[i], ends[i + 1], tenon_top=(i < 5), socket_bottom=(i > 0))
        tm(r).export(os.path.join(HERE, "A", f"rail_{n}.stl"))
    a = m.Manifold()
    for t in TOPS:
        a += anchor(t)
    tm(a).export(os.path.join(HERE, "A", "anchors.stl"))
    tm(strip()).export(os.path.join(HERE, "A", "strip.stl"))
    tm(buttons()).export(os.path.join(HERE, "A", "buttons.stl"))
    c = clip_plain(POS[3]) + clip_plain(POS[14]) + clip_plain(POS[19])   # plain ledge (agreed 2026-10-09)   # 12in, 34in, 44in: the same heights as concept C
    tm(c).export(os.path.join(HERE, "A", "clips.stl"))
    tm(clip_plain(POS[3])).export(os.path.join(HERE, "A", "clip_plain12.stl"))
    print("plain clip stresses (MPa, inference):", {k: round(v, 1) for k, v in clip_stress().items()})
    print("A lengths:", [round(ends[i + 1] - ends[i], 1) for i in range(6)])
    print("A section at pocket: area %.1f mm2, I %.0f mm4, stress %.1f MPa (inference)" % section_stress())

# ---- concept C: height clips ----
def hookC(top, slack=0.0):    # same 3.0 hook as the anchor; slack lifts a keeper hook off the slot edge
    zb = top - SLOT_H + slack
    return box(XS - 4, XS + 4, -1.6, 0.01, zb, zb + 1.6) + box(XS - 4, XS + 4, -3.6, -1.6, zb - 1.4, zb + 1.6)
def bracket(upper_top, ledge):
    """Plate 6 thick on the strip, load hook in the upper slot, keeper hook one pitch below, ledge at any height."""
    x0, x1 = RX0, RX1
    lo_hook = upper_top - PITCH
    z0 = min(ledge - 30, lo_hook - SLOT_H - 6); z1 = max(ledge, upper_top + 6)
    b = box(x0, x1, 0, 6, z0, z1)
    b += box(x0, x1, 6, 21, ledge - 6, ledge)          # plain ledge, no brace (agreed 2026-10-09)
    b -= box(RX0 - 1, RX0 + REL_W, -1, REL_D, z0 - 1, z1 + 1) + box(RX1 - REL_W, RX1 + 1, -1, REL_D, z0 - 1, z1 + 1)   # button relief
    b += hookC(upper_top) + hookC(lo_hook, slack=0.3)
    return b
def build_C():
    os.makedirs(os.path.join(HERE, "C"), exist_ok=True)
    tm(strip()).export(os.path.join(HERE, "C", "strip.stl"))
    tm(buttons()).export(os.path.join(HERE, "C", "buttons.stl"))
    br = bracket(389.8, 304.8) + bracket(721.0, 863.6) + bracket(1124.8, 1117.6)   # 12in, 34in, 44in: the same heights as concept A
    tm(br).export(os.path.join(HERE, "C", "brackets.stl"))

if __name__ == "__main__":
    build_A(); build_C()
