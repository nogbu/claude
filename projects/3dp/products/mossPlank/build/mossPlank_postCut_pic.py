"""mossPlank post cut options: where the base section is cut so its bottom becomes a swappable post for deeper pots
(my ask 2026-10-10). Draws two options side by side on the 3.5in pot: A cut at the lip base (post 63 mm) and B cut 30 mm
above the rim (post 97.3 mm); post brown, standard 200 mm section blue (lifted 40 mm), tabs orange. Joint geometry as in
mossPlank_snapJoint_pic.py. Usage: python3 mossPlank_postCut_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf]."""
import sys, math, numpy as np, trimesh, manifold3d as mf
sys.path.insert(0, "/home/user/claude/projects/3dp/scripts"); sys.path.insert(0, sys.argv[1])
import render3d as R
from dpcheck import load_3mf
from nurseryPots_lib import pot_profile
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
S = sys.argv[1]
P = pot_profile(105.12, 48.07, 1.0); rin = P['r_in']
def get(p):
    it = load_3mf(p)[0][0]; V = it["V"].copy(); c = (V.min(0) + V.max(0)) / 2; V[:, 0] -= c[0]; V[:, 1] -= c[1]; V[:, 2] -= V[:, 2].min()
    return trimesh.Trimesh(V, it["T"], process=False)
pot = get(S + "/3.5inPot_rev10.2.3mf"); ins = get(S + "/3.5inInsert_rev4.3mf")
ins.vertices[:, 2] = 36.0 - ins.vertices[:, 2] + 1.80
zb, H, W = 37.80, 200.0, 60.0; zl = P['z_lb']; zs = zb + H
r0, r1 = rin(zb), rin(zl)
d = math.sqrt(r0**2 - 900) - 15.0
FRONT, SIDE, GAP, SPIG = 1.86, 1.24, 0.2, 30.0
a = SIDE / math.cos(math.radians(5.03)); T = SIDE
ARM, AW, SLOT, PROT = 20.0, 8.0, 1.2, SIDE + GAP
def lower_out(off, front, side, z0, z1):
    cone = mf.Manifold.cylinder(zl - zb, r0 - off, r1 - off, 512).translate([0, 0, zb])
    cap = mf.Manifold.cylinder(800, r1 - off, r1 - off, 512).translate([0, 0, zl])
    return (cone + cap) ^ mf.Manifold.cube([W - 2 * side, 200, z1 - z0]).translate([-W / 2 + side, d + front, z0])
def prism(off, front, side, z0, z1):
    return mf.Manifold.cylinder(z1 - z0, r1 - off, r1 - off, 512).translate([0, 0, z0]) ^ \
        mf.Manifold.cube([W - 2 * side, 200, z1 - z0]).translate([-W / 2 + side, d + front, z0])
def ccw(poly):
    a2 = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))
    return poly if a2 > 0 else poly[::-1]
def ext_yz(poly, x0, x1):
    cs = mf.CrossSection([ccw([(y, z) for y, z in poly])])
    return mf.Manifold.extrude(cs, x1 - x0).warp(lambda v: (v[2] + x0, v[0], v[1]))
so = a + GAP; xs = W / 2 - SIDE - GAP
y_front = d + FRONT + GAP; y_back = math.sqrt((r1 - so)**2 - xs**2); yc = (y_front + y_back) / 2
hw = AW / 2
def spigot_with_tabs(zsh):
    """Spigot hanging below a shoulder at zsh, its tabs and hooks. Returns (spigot solid, hooks)."""
    z0 = zsh - SPIG
    sp = prism(so, FRONT + GAP, SIDE + GAP, z0, zsh) - prism(so + T, FRONT + GAP + T, SIDE + GAP + T, z0 - 1, zsh + 1)
    zr = zsh - 3.0; zt = zr - ARM                      # arm root (top) and free end (bottom)
    u = [(yc - hw - SLOT, zr), (yc - hw, zr), (yc - hw, zt), (yc, zt - hw), (yc + hw, zt), (yc + hw, zr), (yc + hw + SLOT, zr),
         (yc + hw + SLOT, zt - SLOT * 0.414), (yc, zt - hw - SLOT * 1.414), (yc - hw - SLOT, zt - SLOT * 0.414)]
    hooks = []
    zh = zt + 1.0                                      # hook bottom, just above the free end's point
    hook2d = [(yc - hw, zh), (yc + hw, zh), (yc + hw, zh + 5.0), (yc, zh + 5.0 + hw), (yc - hw, zh + 5.0)]
    for sg in (1, -1):
        x_in, x_out = (xs - T - 0.5, xs + 0.5) if sg > 0 else (-xs - 0.5, -xs + T + 0.5)
        sp = sp - ext_yz(u, x_in, x_out)
        hx0, hx1 = (xs, xs + PROT) if sg > 0 else (-xs - PROT, -xs)
        hk = ext_yz(hook2d, hx0, hx1)
        tri = [(0.0, zh), (PROT + 1, zh + PROT + 1), (PROT + 1, zh - 1), (0.0, zh - 1)]   # 45 deg lead-in underneath
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
    """Window through a socket wall: hook + 0.2 mm, V floor, peaked top; zlo is the hook's bottom."""
    w = hw + GAP; zl0 = zlo - GAP
    w2d = [(yc - w, zl0), (yc, zl0 - w), (yc + w, zl0), (yc + w, zl0 + 5.0 + 2 * GAP), (yc, zl0 + 5.0 + 2 * GAP + w), (yc - w, zl0 + 5.0 + 2 * GAP)]   # V floor below the hook: prints as a 45 deg roof when the extension is upside down
    x0, x1 = (W / 2 - SIDE - 0.5, W / 2 + 0.5) if sign > 0 else (-W / 2 - 0.5, -W / 2 + SIDE + 0.5)
    return ext_yz(w2d, x0, x1)
# base: open top socket with windows matching an extension seated at zs
_, _, (zhb, zht) = spigot_with_tabs(zs)
base = lower_out(0, 0, 0, zb, zs) - lower_out(a, FRONT, SIDE, zb - 1, zs + 1)
for sg in (1, -1):
    base = base - window(zhb, sg)
def extension(zsh):
    body = prism(0, 0, 0, zsh, zsh + H) - prism(a, FRONT, SIDE, zsh - 1, zsh + H + 1)
    sp, hooks, (zlo, _) = spigot_with_tabs(zsh)
    body = body + ramp(zsh) + sp
    for sg in (1, -1):
        body = body - window(zlo + H, sg)          # its own socket windows for the next section
    return body, hooks

def tm(m):
    m = m.to_mesh(); return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=True)
half = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False)
GREEN = np.array([0.45, 0.62, 0.40]); UP = np.array([0.40, 0.55, 0.70]); HOOK = np.array([0.90, 0.55, 0.20]); POST = np.array([0.62, 0.48, 0.32])
CLEAR = np.array([0.80, 0.86, 0.90]); INS = np.array([0.86, 0.84, 0.78])
rim = 105.12
cases = [(zl, "A: cut at the lip base (%.1f mm)\npost %.1f mm; joint and tabs below the rim, in the pon" % (zl, zl - zb)),
         (rim + 30.0, "B: cut 30 mm above the rim (%.1f mm)\npost %.1f mm; tabs just above the rim, easy to press" % (rim + 30.0, rim + 30.0 - zb))]
fig, axs = plt.subplots(1, 2, figsize=(15, 11))
for j, (zc, title) in enumerate(cases):
    _, _, (zlo, _) = spigot_with_tabs(zc)
    post = lower_out(0, 0, 0, zb, zc) - lower_out(a, FRONT, SIDE, zb - 1, zc + 1)
    for sg in (1, -1):
        post = post - window(zlo, sg)
    sec, hooks = extension(zc + 40)
    ax = axs[j]; R.FACES.clear(); R.mesh(half, CLEAR); R.mesh(ins, INS); R.mesh(tm(post), POST); R.mesh(tm(sec), UP); R.mesh(tm(hooks[0] + hooks[1]), HOOK)
    cam = R.view(ax, eye=(-1.0, -1.6, 0.45), pad=8); ax.set_title(title + "\n(section lifted 40 mm)", fontsize=13)
    R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
fig.suptitle("Where the post ends on the 3.5in pot (post brown, standard 200 mm section blue)", fontsize=14)
R.save(fig, sys.argv[2])
