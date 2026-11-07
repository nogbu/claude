"""mossPlank joint test piece rev1 fit check: the post's socket follows the pot's taper (narrower lower down) while the section's
spigot is straight, so the spigot's round back runs into the socket's back wall. Draws the 0.2 mm pair from
mossPlank_jointTest.py's geometry: seated as designed with the overlap in red, a cut down the middle seen from the side, and
the stub where it stops. Prints the overlap at the spigot's bottom and how far in each gap's stub goes before it stops.
Usage: python3 mossPlank_jointJam_pic.py [folder with 3.5inPot_rev10.2.3mf, 3.5inInsert_rev4.3mf] [out png]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
OUTPNG = sys.argv[2]; sys.argv[2] = "/tmp"
exec(open(os.path.join(HERE, "mossPlank_jointTest.py")).read().split("COLS = ")[0])   # pair() and the joint geometry
RED = np.array([0.90, 0.12, 0.10]); BLUE = np.array([0.40, 0.55, 0.70]); BROWN = np.array([0.62, 0.48, 0.32])
for g in GAPS:                                               # stub stops when the spigot's back meets the socket: rin(zl - u) = r1 - g
    lo, hi = 0.0, SPIG
    for _ in range(60):
        u = (lo + hi) / 2; lo, hi = (u, hi) if rin(zl - u) > r1 - g else (lo, u)
    print("gap %.1f: stub stops %.2f mm in of %.0f, overlap at the spigot bottom when pushed home %.2f mm" % (g, u, SPIG, r1 - rin(zl - SPIG) - g))
post, stub = pair(1, 0.2); setgap(0.2)
over = post ^ stub
print("overlap volume %.0f mm3" % over.volume())
half = lambda m: tm(m).slice_plane([0, 0, 0], [-1, 0, 0], cap=True)
fig, axs = plt.subplots(1, 3, figsize=(24, 10), gridspec_kw=dict(width_ratios=[1, 1, 1]))
ax = axs[0]; R.FACES.clear()
R.mesh(half(post - over), BROWN); R.mesh(half(stub - over), BLUE); R.mesh(half(over), RED)
cam = R.view(ax, eye=(1.2, 1.3, 0.6), pad=8)
R.call(ax, cam, (0, rin(zl - 15) - a, zl - 15), (-90, -40), "overlap (red)", color="#c0392b")
ax.set_title("0.2 mm pair pushed home as designed, cut down the middle,\nfrom behind: the spigot's back runs into the socket", fontsize=12)
R.source(ax, os.path.join(HERE, "mossPlank_jointTest.py"), cam, size=8)
ax = axs[1]; R.FACES.clear()
R.mesh(half(post - over), BROWN); R.mesh(half(stub - over), BLUE); R.mesh(half(over), RED)
cam = R.view(ax, eye=(1, 0, 0), pad=6)
yb = r1 - so; z0 = zl - SPIG
R.dim(ax, cam, (0, rin(z0) - a, z0), (0, yb, z0), (0, 0, -4))
R.call(ax, cam, (0, yb, z0 + 8), (110, 0), "spigot back, straight", size=10)
R.call(ax, cam, (0, rin(zl - 20) - a, zl - 20), (60, -60), "socket back, follows the pot", size=10)
ax.set_title("Same cut from the side: %.2f mm overlap at the spigot's bottom, shrinking to none\n%.1f mm below the shoulder; the spigot's back pokes %.2f mm out past the post's back" % (r1 - rin(z0) - 0.2, 0.2 / ((r1 - rin(z0)) / SPIG), yb - rin(z0)), fontsize=12)
R.source(ax, os.path.join(HERE, "mossPlank_jointTest.py"), cam, size=8)
ax = axs[2]; R.FACES.clear()
lo, hi = 0.0, SPIG
for _ in range(60):
    u = (lo + hi) / 2; lo, hi = (u, hi) if rin(zl - u) > r1 - 0.2 else (lo, u)
stop = stub.translate([0, 0, SPIG - u])
R.mesh(half(post), BROWN); R.mesh(half(stop), BLUE)
cam = R.view(ax, eye=(1, 0, 0), pad=6)
R.dim(ax, cam, (0, d, zl), (0, d, zl + SPIG - u), (0, -4, 0))
ax.set_title("Where the 0.2 mm stub stops: %.1f mm in of %.0f,\nso the tabs never reach their windows" % (u, SPIG), fontsize=12)
R.source(ax, os.path.join(HERE, "mossPlank_jointTest.py"), cam, size=8)
fig.suptitle("mossPlank joint test piece rev1: the stub can't seat in the post", fontsize=15)
R.save(fig, OUTPNG)
