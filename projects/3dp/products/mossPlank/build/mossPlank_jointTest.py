"""mossPlank joint test piece (design principle 7): three pairs, one per gap per side (0.1, 0.2, 0.3 mm), each pair the top
35 mm of the post (cut 30 mm past the 3.5in pot's lip base, fix A agreed 2026-10-10, so its socket is straight) and a section stub (20 mm of body, ramp, 30 mm
spigot with its two snap tabs). Pieces print as the full parts do: post upright, section stub upside down (top end on the
bed). Notches on each piece's front-face bed edge mark the step: 1, 2, 3 notches for 0.1, 0.2, 0.3 mm (dp 8).
Joint geometry as in mossPlank_snapJoint_pic.py; GAP sets both the spigot gap and the hook-to-window clearance.
Usage: python3 mossPlank_jointTest.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out folder]
Writes mossPlank-jointTest_rev2.3mf (rev1, cut at the lip base, jammed: its socket tapered) and mossPlank_jointTest.png drawn from it."""
import sys, os, math, numpy as np, trimesh, manifold3d as mf
REPO = "/home/user/claude"
sys.path.insert(0, REPO + "/projects/3dp/scripts"); sys.path.insert(0, sys.argv[1])
import render3d as R, write3mf as W
from dpcheck import load_3mf
from nurseryPots_lib import pot_profile
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
S, OUT = sys.argv[1], sys.argv[2]
P = pot_profile(105.12, 48.07, 1.0); rin = P['r_in']
zb, W_, zl = 37.80, 60.0, P['z_lb']
r0, r1 = rin(zb), rin(zl)
d = math.sqrt(r0**2 - 900) - 15.0
FRONT, SIDE, SPIG = 1.86, 1.24, 30.0
a = SIDE / math.cos(math.radians(5.03)); T = SIDE
ARM, AW, SLOT = 20.0, 8.0, 1.2
hw = AW / 2
POST_H, STUB_H = 35.0, 20.0
ZC = zl + SPIG                       # post cut (fix A): the whole socket sits where the pot is straight
GAPS = (0.1, 0.2, 0.3)

def setgap(g):
    global GAP, PROT, so, xs, y_front, y_back, yc
    GAP = g; PROT = SIDE + GAP; so = a + GAP; xs = W_ / 2 - SIDE - GAP
    y_front = d + FRONT + GAP; y_back = math.sqrt((r1 - so)**2 - xs**2); yc = (y_front + y_back) / 2
def lower_out(off, front, side, z0, z1):
    cone = mf.Manifold.cylinder(zl - zb, r0 - off, r1 - off, 512).translate([0, 0, zb])
    cap = mf.Manifold.cylinder(800, r1 - off, r1 - off, 512).translate([0, 0, zl])
    return (cone + cap) ^ mf.Manifold.cube([W_ - 2 * side, 200, z1 - z0]).translate([-W_ / 2 + side, d + front, z0])
def prism(off, front, side, z0, z1):
    return mf.Manifold.cylinder(z1 - z0, r1 - off, r1 - off, 512).translate([0, 0, z0]) ^ \
        mf.Manifold.cube([W_ - 2 * side, 200, z1 - z0]).translate([-W_ / 2 + side, d + front, z0])
def ccw(poly):
    a2 = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))
    return poly if a2 > 0 else poly[::-1]
def ext_yz(poly, x0, x1):
    cs = mf.CrossSection([ccw([(y, z) for y, z in poly])])
    return mf.Manifold.extrude(cs, x1 - x0).warp(lambda v: (v[2] + x0, v[0], v[1]))
def spigot_with_tabs(zsh):
    z0 = zsh - SPIG
    sp = prism(so, FRONT + GAP, SIDE + GAP, z0, zsh) - prism(so + T, FRONT + GAP + T, SIDE + GAP + T, z0 - 1, zsh + 1)
    zr = zsh - 3.0; zt = zr - ARM
    u = [(yc - hw - SLOT, zr), (yc - hw, zr), (yc - hw, zt), (yc, zt - hw), (yc + hw, zt), (yc + hw, zr), (yc + hw + SLOT, zr),
         (yc + hw + SLOT, zt - SLOT * 0.414), (yc, zt - hw - SLOT * 1.414), (yc - hw - SLOT, zt - SLOT * 0.414)]
    hooks = []
    zh = zt + 1.0
    hook2d = [(yc - hw, zh), (yc + hw, zh), (yc + hw, zh + 5.0), (yc, zh + 5.0 + hw), (yc - hw, zh + 5.0)]
    for sg in (1, -1):
        x_in, x_out = (xs - T - 0.5, xs + 0.5) if sg > 0 else (-xs - 0.5, -xs + T + 0.5)
        sp = sp - ext_yz(u, x_in, x_out)
        hx0, hx1 = (xs - 0.01, xs + PROT) if sg > 0 else (-xs - PROT, -xs + 0.01)
        hk = ext_yz(hook2d, hx0, hx1)
        tri = [(0.0, zh), (PROT + 1, zh + PROT + 1), (PROT + 1, zh - 1), (0.0, zh - 1)]
        lead = mf.Manifold.extrude(mf.CrossSection([ccw([(u_, z) for u_, z in tri])]), 40).warp(lambda v, sg=sg: (sg * (xs + v[0]), yc - 20 + v[2], v[1]))
        hooks.append(hk - lead)
    return sp, hooks, (zh, zh + 5.0 + hw)
def ramp(zsh):
    """Hidden 45 deg ramp above the shoulder, inside the body: its inner face moves in linearly from the body's inner face
    (at zsh + PROT) to the spigot's inner face (at zsh), so printed upside down it is a 45 deg overhang all round.
    The cut is a cone (round back) intersected with a hull of two rectangles (front and sides), both exact lofts."""
    Wd = globals().get("W_", globals().get("W"))
    def e_at(z): return PROT - (z - zsh)                 # inward step at height z
    z0, z1 = zsh - 1.0, zsh + PROT + 1.0
    cone = mf.Manifold.cylinder(z1 - z0, r1 - a - e_at(z0), r1 - a - e_at(z1), 512).translate([0, 0, z0])
    def rect(z):
        e = e_at(z); x0, x1, y0 = -Wd / 2 + SIDE + e, Wd / 2 - SIDE - e, d + FRONT + e
        return [(x0, y0, z), (x1, y0, z), (x1, 200, z), (x0, 200, z)]
    box = mf.Manifold.hull_points(rect(z0) + rect(z1))
    return prism(a, FRONT, SIDE, zsh, zsh + PROT) - (cone ^ box)
def window(zlo, sign):
    w = hw + GAP; zl0 = zlo - GAP
    w2d = [(yc - w, zl0), (yc, zl0 - w), (yc + w, zl0), (yc + w, zl0 + 5.0 + 2 * GAP), (yc, zl0 + 5.0 + 2 * GAP + w), (yc - w, zl0 + 5.0 + 2 * GAP)]
    x0, x1 = (W_ / 2 - SIDE - 0.5, W_ / 2 + 0.5) if sign > 0 else (-W_ / 2 - 0.5, -W_ / 2 + SIDE + 0.5)
    return ext_yz(w2d, x0, x1)
def notches(n, z_bed, up):
    """n V notches through the front face at its bed edge (2.4 mm wide, 1.6 mm tall, sides 37 deg from vertical)."""
    m = mf.Manifold()
    for i in range(n):
        x = (i - (n - 1) / 2) * 5.0
        tri = [(x - 1.2, z_bed - up * 0.5), (x + 1.2, z_bed - up * 0.5), (x + 1.2, z_bed), (x, z_bed + up * 1.6), (x - 1.2, z_bed)]
        cs = mf.CrossSection([ccw(tri)])
        m = m + mf.Manifold.extrude(cs, FRONT + 2).warp(lambda v: (v[0], d + FRONT + 1 - v[2], v[1]))   # swap plus mirror keeps the solid right side out
    return m
def pair(i, g):
    setgap(g)
    _, _, (zlo, _) = spigot_with_tabs(ZC)
    post = lower_out(0, 0, 0, ZC - POST_H, ZC) - lower_out(a, FRONT, SIDE, ZC - POST_H - 1, ZC + 1)
    for sg in (1, -1):
        post = post - window(zlo, sg)
    post = post - notches(i + 1, ZC - POST_H, 1)
    sp, hooks, _ = spigot_with_tabs(ZC)
    stub = prism(0, 0, 0, ZC, ZC + STUB_H) - prism(a, FRONT, SIDE, ZC - 1, ZC + STUB_H + 1)
    stub = stub + ramp(ZC) + sp + hooks[0] + hooks[1]
    stub = stub - notches(i + 1, ZC + STUB_H, -1)
    return post, stub
def tm(m):
    m = m.to_mesh(); return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=False)

COLS = (52.0, 128.0, 204.0)
pieces, seat = [], {}
for i, g in enumerate(GAPS):
    post, stub = pair(i, g)
    pm, sm = tm(post), tm(stub)
    seat[g] = (pm.copy(), sm.copy())
    pm.apply_translation([COLS[i], 70 - d, -(ZC - POST_H)])                  # post upright, bottom on the bed
    sm.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))   # stub upside down: (x, -y, -z)
    sm.apply_translation([COLS[i], 150 + d + 45, ZC + STUB_H])
    for nm, t in (("post %.1f" % g, pm), ("section %.1f" % g, sm)):
        print(nm, "watertight", t.is_watertight, "size %.2f x %.2f x %.2f" % tuple(t.extents), "volume %.2f cm3" % (t.volume / 1000),
              "min", np.round(t.vertices.min(0), 2).tolist())
        pieces.append((nm, t))
s = W.base(REPO + "/projects/3dp/products/rail/build/rail_settings_base.json")
f3 = os.path.join(OUT, "mossPlank-jointTest_rev2.3mf")
print("wrote", W.write(f3, [W.Obj(n, [W.Part(t.vertices, t.faces)]) for n, t in pieces], s))

# picture: plate as printed (from the 3mf), the 0.2 mm pair seated and pulled apart, and a cut through the hooks
BLUE = np.array([0.40, 0.55, 0.70]); BROWN = np.array([0.62, 0.48, 0.32]); HOOK = np.array([0.90, 0.55, 0.20])
items, _ = load_3mf(f3)
fig, axs = plt.subplots(1, 4, figsize=(24, 8.5), gridspec_kw=dict(width_ratios=[1.25, 1, 1, 0.9]))
R.FACES.clear()
for it in items:
    nm = it["over"].get("name", it["name"]); col = BROWN if nm.startswith("post") else BLUE
    R.mesh(trimesh.Trimesh(it["V"], it["T"], process=False), col)
cam = R.view(axs[0], eye=(-0.6, -1.4, 1.0), pad=22); axs[0].set_title("As printed: post upright, section stub upside down\nnotches on the bed edge: 1, 2, 3 = gap 0.1, 0.2, 0.3 mm", fontsize=12)
for it in items:
    nm = it["over"].get("name", it["name"]); V = it["V"]; c = V.mean(0)
    if nm.startswith("post"):
        R.call(axs[0], cam, (c[0], V[:, 1].min(), 0.0), (0, -26), nm + " mm", size=10)
    else:
        R.call(axs[0], cam, (c[0], V[:, 1].max(), V[:, 2].max()), (0, 22), nm + " mm", size=10)
R.source(axs[0], f3, cam, size=8)
pm, sm = seat[0.2]; setgap(0.2)
R.FACES.clear()
lift = sm.copy(); lift.apply_translation([0, 0, 45])
R.mesh(pm, BROWN); R.mesh(lift, BLUE)
cam = R.view(axs[1], eye=(-1.0, -1.6, 0.45), pad=8); axs[1].set_title("Gap 0.2 mm pair, pulled apart\n(post brown, section stub blue)", fontsize=12)
R.call(axs[1], cam, (-xs - PROT, yc, ZC + 45 - 3 - ARM + 3.5), (-70, 0), "snap tab", color="#b35900", size=11)
R.call(axs[1], cam, (-W_ / 2, yc, ZC - 3 - ARM + 3.5), (-70, -10), "window", color="#6b4423", size=11)
R.source(axs[1], f3, cam, size=8)
_, _, (zh, zt) = spigot_with_tabs(ZC)
zc = zh + 2.5
R.FACES.clear()
for t, col in ((pm, BROWN), (sm, BLUE)):
    h = t.slice_plane([0, 0, zc], [0, 0, -1], cap=True)
    R.mesh(h, col)
cam = R.view(axs[2], eye=(-0.35, -0.9, 1.0), pad=6); axs[2].set_title("Seated, cut through the hooks (%.1f mm above the post's\nbottom), looking down: hooks caught in the windows" % (zc - (ZC - POST_H)), fontsize=12)
R.dim(axs[2], cam, (xs, yc - hw - 3, zc), (xs + PROT, yc - hw - 3, zc), (0, -6, 0))
R.source(axs[2], f3, cam, size=8)
R.FACES.clear()
it = [i for i in items if i["over"].get("name", i["name"]) == "post 0.3"][0]
R.mesh(trimesh.Trimesh(it["V"], it["T"], process=False), BROWN)
cam = R.view(axs[3], eye=(-0.25, -1.0, 0.2), pad=4); axs[3].set_title("Close-up: post 0.3 front face, looking from the front;\n3 notches on its bed edge (2.4 mm wide, 1.6 mm tall)", fontsize=12)
V = it["V"]; xm = (V[:, 0].min() + V[:, 0].max()) / 2; y0 = V[:, 1].min()
R.dim(axs[3], cam, (xm + 5 - 1.2, y0, 0), (xm + 5 + 1.2, y0, 0), (0, 0, -3))
R.source(axs[3], f3, cam, size=8)
fig.suptitle("mossPlank joint test piece: 3 pairs, gap per side 0.1 / 0.2 / 0.3 mm (rev2: post cut 30 mm past the lip base)", fontsize=14)
R.save(fig, os.path.join(OUT, "mossPlank_jointTest.png"))
