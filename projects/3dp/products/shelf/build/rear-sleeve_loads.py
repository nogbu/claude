"""Rear piece lip-rod sleeve (agreed change 27) with its strength-check loads: whole design plus a cut through the rod centers.
Geometry from rear-grip_options.py (unsized concept blocks). Loads: 15 lb x 3 per corner (agreed change 11) at the clip center,
moments about the stub's outer end (x 0), lip rod bearing up at x REACH (inference). Usage: python3 rear-sleeve_loads.py [out.png]"""
import importlib.util, os, sys, numpy as np, manifold3d as m, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("rear_grip", os.path.join(HERE, "rear-grip_options.py"))
G = importlib.util.module_from_spec(spec); sys.argv, argv = sys.argv[:1] + ["/dev/null"], sys.argv   # build only, don't redraw its picture
matplotlib.pyplot.savefig = lambda *a, **k: None
spec.loader.exec_module(G); sys.argv = argv; plt.close("all")
F, box = G.F, G.box
CLIPX = G.X0 + 8.0; REACH = 40.0
Fc = 15 * 4.448 * 3; M = Fc * (0 - CLIPX); P = M / REACH; Fs = Fc + P
piece = G.stub() + G.inside(); sec = G.section(); clip = G.clip
def half(man): return man ^ box(-60, 90, 0, 40, -60, 30)          # keep y >= 0: cut through both rod centers
GREY, ORANGE, WIREC, STEEL = G.GREY, G.GRIP, G.WIREC, G.STEEL
fig, axes = plt.subplots(1, 2, figsize=(26, 12), gridspec_kw=dict(width_ratios=[1, 1.25]))
ax = axes[0]; R.FACES.clear()
R.mesh(F.tm(G.stub()), GREY); R.mesh(F.tm(G.inside()), ORANGE); R.mesh(F.tm(sec), WIREC); R.mesh(F.tm(clip), STEEL)
cam = R.view(ax, eye=(0.35, -1.0, -0.45), ppm=6.0, pad=8)
ax.set_title("Whole rear piece end, from the front and below (unsized)", fontsize=15, loc="left", fontweight="bold")
R.call(ax, cam, (30, -13, G.LIPZ - 4), (40, -70), "lip-rod sleeve (agreed change 27)", color="#a85a00", size=11)
R.call(ax, cam, (-30, -13, G.ZB), (-40, -80), "stub sleeves on the clip", color="#555", size=11)
R.call(ax, cam, (G.X0 + 8, G.OF - 12.4, G.ZB - 0.9), (-60, 60), "stock clip", color="#3a4a5a", size=11)
ax = axes[1]; R.FACES.clear()
R.mesh(F.tm(half(G.stub())), GREY); R.mesh(F.tm(half(G.inside())), ORANGE); R.mesh(F.tm(half(sec)), WIREC); R.mesh(F.tm(clip), STEEL)
cam = R.view(ax, eye=(0.0, -1.0, 0.02), ppm=6.0, pad=18)
ax.set_title("Cut through both rod centers, seen from the front: loads at the design load", fontsize=15, loc="left", fontweight="bold")
def arrow(p, d, text, color, dy=0):
    a = np.array(R.proj(cam, p)); b = np.array(R.proj(cam, np.add(p, d)))
    ax.annotate("", xy=a, xytext=b, arrowprops=dict(arrowstyle="-|>", color=color, lw=3, mutation_scale=25))
    ax.text(b[0], b[1] + dy, text, color=color, fontsize=12, fontweight="bold", ha="center", va="center",
            bbox=dict(fc="white", ec="none", alpha=0.9))
arrow((CLIPX, 0, G.ZB - 0.9), (0, 0, -9), f"clip pushes up\n{Fc:.0f} N", "#1f5fa8", dy=25)
arrow((5.0, 0, G.LIPZ - G.BORE), (0, 0, 9), f"rod ends push down\n{Fs:.0f} N (both stubs)", "#c0392b", dy=-25)
arrow((REACH, 0, G.LIPZ + G.ROD + 0.6), (0, 0, -9), f"lip rod pushes up on the\nsleeve top: {P:.0f} N at x {REACH:.0f}", "#c0392b", dy=28)
R.dim(ax, cam, (28, 0, G.LIPZ + G.ROD), (28, 0, G.RC - G.ROD), (0, 0, 0))
R.call(ax, cam, (28, 0, (G.LIPZ + G.RC) / 2 + 6), (130, 30), "open space above the lip rod\n(the sleeve can grow into it)", color="#c0392b", size=11)
R.dim(ax, cam, (CLIPX, 0, G.ZB - 6), (0, 0, G.ZB - 6), (0, 0, 0))
R.call(ax, cam, (CLIPX / 2, 0, G.ZB - 6), (40, -70), f"tipping arm: {M / 1000:.1f} N·m", color="#c0392b", size=11)
R.call(ax, cam, (0, 0, G.TOP), (-40, 40), "rod ends (x 0)", color="#222", size=11)
R.call(ax, cam, (G.W1, 0, (G.RC + G.LIPZ) / 2 - 4), (-70, 20), "first crosswire", color="#222", size=11)
R.source(ax, os.path.abspath(__file__), cam)
fig.suptitle("Rear piece lip-rod sleeve and its strength-check loads (15 lb x 3 per corner; moments about the rod ends; inference). "
             "Unsized, fillets left out.", fontsize=16)
plt.savefig = matplotlib.figure.Figure.savefig
R.save(fig, sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/images/shelf_rearSleeve_loads.png")
print(f"F {Fc:.0f} N, arm {-CLIPX:.1f}, M {M/1000:.2f} N*m, lip rod up {P:.0f} N at {REACH}, rod ends down {Fs:.0f} N, gap {G.RC - G.LIPZ - 2*G.ROD:.1f}")
