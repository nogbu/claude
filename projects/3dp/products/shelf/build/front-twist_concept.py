"""Twist-lock front piece concept picture (front-twist_model.py build(zs=ZB)): row 1 the three install steps on the rod and first two
crosswires, one view and scale (turned THETA and sliding on; seated and turning back; locked, on the clip); row 2 the piece alone from
the hook side and from the front below, and end-on sections through the crosswire zone and the hook with the rod and wire.
Usage: python3 front-twist_concept.py [out.png]"""
import importlib.util, os, sys, numpy as np, trimesh, manifold3d as m, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import render3d as R
spec = importlib.util.spec_from_file_location("ftm", os.path.join(HERE, "front-twist_model.py"))
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
THETA = 100.0
PIECE = np.array([0.93, 0.62, 0.30]); HOOK = np.array([0.95, 0.42, 0.18]); STEEL = np.array([0.30, 0.30, 0.33]); CLIP = np.array([0.6, 0.65, 0.7])
p, d = T.build(zs=T.ZB)
hook = p ^ T.box(d["XH0"], d["XH1"] + 1, d["YF"] - 1, d["OR"] + 1, -T.BORE - 0.01, T.TOP + 1)      # the hook's cap, colored
hook = hook - T.box(d["XH0"] - 1, d["XH1"] + 2, d["YF"] - 1, T.YI, -20, 20)
rest = p - hook
clip = T.box(T.X0 + 0.5, T.X0 + 15.5, d["YF"], d["YF"] + 12.4, T.ZB - 0.9, T.ZB)
rod, wires = T.rod(52).translate([-2, 0, 0]), T.wires(L=24)

def zoom(ax, eye, lo, hi, ppm):
    e, right, up = R.camera(eye); cs = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    u, v = cs @ right, cs @ up
    img, cam = R.render(eye, ppm, frame=(u.min(), u.max(), v.min(), v.max())); ax.imshow(img); ax.axis("off"); return cam

def scene(theta, s, with_clip=False):
    R.FACES.clear()
    for man, col in ((rest, PIECE), (hook, HOOK)):
        R.mesh(T.tm(T.turned(man, theta).translate([-s, 0, 0])), col)
    R.mesh(T.tm(rod), STEEL); R.mesh(T.tm(wires), STEEL)
    if with_clip: R.mesh(T.tm(clip), CLIP)

R.MIN_PX = 0; PPM = 12.0
fig = plt.figure(figsize=(36, 20)); gs = fig.add_gridspec(2, 3, height_ratios=[1, 1], wspace=0.04, hspace=0.12, left=0.01, right=0.99, top=0.93, bottom=0.03)
EYE = (0.75, -0.8, 0.85); LO, HI = np.array([-50, -12, -16]), np.array([46, 24, 8])
steps = [(THETA, 14.0, False, f"1  Turned {THETA:.0f}° (top toward the front), slid on: hook and front wall pass under the first crosswire"),
         (THETA / 2, 0.0, False, "2  Seated against the first crosswire, turned back"),
         (0.0, 0.0, True, "3  Locked: hook behind the first crosswire, top flush with the crosswires")]
cams = []
for i, (th, s, wc, title) in enumerate(steps):
    ax = fig.add_subplot(gs[0, i]); scene(th, s, wc); cams.append(zoom(ax, EYE, LO, HI, PPM))
    ax.set_title(title, fontsize=14, loc="left", fontweight="bold", wrap=True)
c = cams[2]; ax2 = fig.axes[2]
R.call(ax2, c, (28, 0.5, T.TOP), (90, -90), "hook over the rod, x 13.75 to 34.85", color="#a03a00", size=13)
R.call(ax2, c, (T.W1, 14, T.TOP), (-40, 80), "first crosswire", color="#222", size=13)
R.call(ax2, c, (T.W2, 14, T.TOP), (60, 60), "second crosswire", color="#222", size=13)
R.call(ax2, c, (-38, d["YF"] + 6, T.ZB - 0.9), (-60, -60), "stock clip", color="#444", size=13)
R.call(ax2, c, (5, d["YF"], 0), (-140, 60), "closed stub sleeve (bore as now)", color="#7a4a00", size=13)
R.call(fig.axes[0], cams[0], (T.W1, 10, T.TOP), (60, 70), "first crosswire", color="#222", size=13)

# row 2: piece alone, two sides, and two end-on sections
R.FACES.clear(); R.mesh(T.tm(rest), PIECE); R.mesh(T.tm(hook), HOOK)
ax = fig.add_subplot(gs[1, 0]); cA = zoom(ax, (0.7, 1.0, 0.8), np.array([-50, -8, -16]), np.array([38, 7, 7]), PPM)
ax.set_title("Piece alone, from the hook end, the rear and above", fontsize=14, loc="left", fontweight="bold")
R.call(ax, cA, (30, 2.6, 4.2), (60, -60), "hook tip cut at 45°", color="#a03a00", size=13)
R.call(ax, cA, (11.5, -3.25, -6), (60, 110), "front wall only where\nthe crosswire passes", color="#7a4a00", size=13)
R.call(ax, cA, (-20, 5.45, -10), (-40, -120), "body on the clip (as now)", color="#7a4a00", size=13)
ax = fig.add_subplot(gs[1, 1]); cB = zoom(ax, (0.5, -1.0, -0.6), np.array([-50, -8, -16]), np.array([38, 7, 7]), PPM)
ax.set_title("Piece alone, from the front and below: front face one 20 mm band", fontsize=14, loc="left", fontweight="bold")
ax = fig.add_subplot(gs[1, 2]); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("End-on sections, seen from inboard (front left, rear right)", fontsize=14, loc="left", fontweight="bold")
tp = T.tm(p)
for k, (x, dx, lab) in enumerate(((12.0, 0.0, "at the first crosswire (x 12)"), (24.0, 22.0, "through the hook (x 24)"))):
    sec = tp.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
    for ent in sec.discrete:
        ax.fill(ent[:, 1] + dx, ent[:, 2], color=PIECE, ec="k", lw=1.2)
    th = np.linspace(0, 2 * np.pi, 90)
    ax.fill(T.ROD * np.cos(th) + dx, T.ROD * np.sin(th) + T.RC, color=STEEL)
    if k == 0:
        ax.fill([-T.ROD, 9, 9, -T.ROD], [T.WB, T.WB, T.TOP, T.TOP], color=STEEL)        # the crosswire, cut along its length
        ax.text(9.5, T.TOP - 1.45, "crosswire", va="center", fontsize=12)
    ax.text(dx, T.ZB - 2.0, lab, ha="center", va="top", fontsize=12)
ax.set_xlim(-10, 32); ax.set_ylim(T.ZB - 5, T.TOP + 3)
R.source(fig.axes[0], os.path.abspath(__file__), cams[0])
fig.suptitle(f"Twist-lock front piece concept (left hand), on the front edge rod and first two crosswires; one scale per row. Prints on its front face like "
             f"the current piece. Solid {p.volume() * 1.27e-3:.1f} g (current piece {21.3:.1f}). Fillets left out.", fontsize=16)
R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_frontTwist_concept.png")
