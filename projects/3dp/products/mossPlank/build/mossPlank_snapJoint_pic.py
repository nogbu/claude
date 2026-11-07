"""mossPlank snap-tab joint, spigot on the bottom of each upper section (my ask 2026-10-10: nothing sticks up at the top).
Base section (3.5in pot) has a plain open top with two windows; the extension's 30 mm open spigot slides down into it
(0.2 mm gap per side). Tabs on the spigot's side walls: arm 20 x 8 x 1.24 mm rooted near the shoulder, free end down, in a
1.2 mm U-cut; hook 1.44 mm proud near the free end, peaked 45 deg top (the catch: a pull has no inward push), 45 deg lead-in
underneath. Windows: hook + 0.2 mm, peaked top, V floor. Extensions print upside down (top end on the bed), so the
body-to-spigot step is an inward 1.44 mm ledge filled by a hidden 45 deg ramp and the hook's peaked top prints as a V."""
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
EX = 70.0
ext, hooks = extension(zs + EX)
ext_seat, hooks_seat = extension(zs)
hook_m = hooks[0] + hooks[1]; hook_s = hooks_seat[0] + hooks_seat[1]
def tm(m):
    m = m.to_mesh(); return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=True)
half = pot.slice_plane([0, 0, 0], [0, 1, 0], cap=False)
GREEN = np.array([0.45, 0.62, 0.40]); UP = np.array([0.40, 0.55, 0.70]); HOOK = np.array([0.90, 0.55, 0.20])
CLEAR = np.array([0.80, 0.86, 0.90]); INS = np.array([0.86, 0.84, 0.78])
fig, axs = plt.subplots(2, 2, figsize=(16, 17), gridspec_kw=dict(height_ratios=[1.4, 1]))
ax = axs[0, 0]; R.FACES.clear(); R.mesh(half, CLEAR); R.mesh(ins, INS); R.mesh(tm(base), GREEN); R.mesh(tm(ext), UP); R.mesh(tm(hook_m), HOOK)
cam = R.view(ax, eye=(-1.0, -1.6, 0.55), pad=8)
ax.set_title("Base (green, prints upright) and extension (blue, lifted %d mm;\nprints upside down); plain open top on every section" % EX, fontsize=13)
R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
zse = zs + EX
crop = mf.Manifold.cube([W + 40, 120, 60]).translate([-W / 2 - 20, -20, zse - 40])
ax = axs[0, 1]; R.FACES.clear(); R.mesh(tm(ext ^ crop), UP); R.mesh(tm(hook_m), HOOK)
cam = R.view(ax, eye=(-1.7, -0.6, -0.25), pad=6)
ax.set_title("Extension's spigot, from below: 30 mm, open; arm 20 mm, free end down;\nhook (orange) 1.44 mm proud, peaked top, 45 deg lead-in underneath", fontsize=13)
R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
crop2 = mf.Manifold.cube([W + 40, 120, 50]).translate([-W / 2 - 20, -20, zs - 40])
ax = axs[1, 0]; R.FACES.clear(); R.mesh(tm(base ^ crop2), GREEN)
cam = R.view(ax, eye=(-1.7, -0.8, 0.45), pad=6); ax.set_title("Base top: window with a peaked top and V floor\n(the V prints as a 45 deg roof on upside-down extensions)", fontsize=13)
R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
sl = mf.Manifold.cube([W + 20, 60, 90]).translate([-W / 2 - 10, yc, zs - 45])
ax = axs[1, 1]; R.FACES.clear(); R.mesh(tm(base ^ sl), GREEN); R.mesh(tm(ext_seat ^ sl), UP); R.mesh(tm(hook_s ^ sl), HOOK)
cam = R.view(ax, eye=(-0.25, -1.0, 0.15), pad=6); ax.set_title("Assembled, cut through both tabs (front half removed)", fontsize=13)
R.source(ax, S + "/3.5inPot_rev10.2.3mf", cam, size=8)
fig.suptitle("Snap-tab joint with the spigot on the bottom of each extension (fillets not drawn)", fontsize=14)
R.save(fig, sys.argv[2])
print("hook z in base", zhb, zht)
