"""Twist-lock front piece 3D check picture (fe/front_twist_tet.py pickles): one row per variant, each the same views and scale: the whole
piece colored by the largest principal tension (element centers), a close-up of the hook from its open rear side and below, and the piece
seen end-on from inboard with its displacement drawn 5 times larger over the unloaded outline.
Usage: python3 front-twist_stress.py case out.png label1 pkl1 [label2 pkl2 ...]   (case: start | end | spread)"""
import importlib.util, os, sys, pickle, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import render3d as R
spec = importlib.util.spec_from_file_location("ftm", os.path.join(HERE, "front-twist_model.py"))
TW = importlib.util.module_from_spec(spec); spec.loader.exec_module(TW)
spec = importlib.util.spec_from_file_location("ftp", os.path.join(HERE, "fe", "front_twist_post.py"))
POST = importlib.util.module_from_spec(spec); spec.loader.exec_module(POST)          # hot(): peaks away from the rod contacts, as the run reads them
from scipy.spatial import cKDTree
case, OUT = sys.argv[1], sys.argv[2]; rows = list(zip(sys.argv[3::2], sys.argv[4::2]))
LIMIT = 75.0                                                    # PETG Basic bending strength along the layers (data sheet V3.0); across: 56
cmap = plt.get_cmap("Reds"); STEEL = np.array([0.30, 0.30, 0.33]); CLIP = np.array([0.6, 0.65, 0.7]); GHOST = np.array([0.82, 0.86, 0.92])
SCALE = 5.0
def surface(D):
    X, T = D["X"], D["T"]; fc = np.array([[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]])
    allf = np.concatenate([T[:, fc[k]] for k in range(4)]); el = np.tile(np.arange(len(T)), 4); opp = np.concatenate([T[:, k] for k in range(4)])
    _, inv, cnt = np.unique(np.sort(allf, 1), axis=0, return_inverse=True, return_counts=True)
    b = cnt[inv.ravel()] == 1; F3, E3, O3 = allf[b], el[b], opp[b]
    nrm = np.cross(X[F3[:, 1]] - X[F3[:, 0]], X[F3[:, 2]] - X[F3[:, 0]]); out = ((X[O3] - X[F3].mean(1)) * nrm).sum(1) > 0
    F3 = F3.copy(); F3[out] = F3[out][:, [0, 2, 1]]
    return F3, E3
def add_faces(P, F3, col):
    V = P[F3]; n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); L = np.linalg.norm(n, axis=1); k = L > 1e-12
    R.FACES.extend((v, nn, c, False) for v, nn, c in zip(V[k], n[k] / L[k, None], col[k] if col.ndim == 2 else np.broadcast_to(col, (k.sum(), 3))))
def zoom(ax, eye, lo, hi, ppm):
    e, right, up = R.camera(eye); cs = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    u, v = cs @ right, cs @ up
    img, cam = R.render(eye, ppm, frame=(u.min(), u.max(), v.min(), v.max())); ax.imshow(img); ax.axis("off"); return cam
R.MIN_PX = 0
HMAX = max(pickle.load(open(pk, "rb")).get("hh", 0.0) for _, pk in rows)    # raised tops (front-twist_model.py hh): every row keeps one frame
fig = plt.figure(figsize=(36, 12.5 * len(rows))); gs = fig.add_gridspec(len(rows), 4, width_ratios=[1.25, 1, 0.8, 0.04], wspace=0.05, hspace=0.12, left=0.01, right=0.96, top=0.93, bottom=0.03)
for r, (label, pk) in enumerate(rows):
    D = pickle.load(open(pk, "rb")); X, T, ec, d = D["X"], D["T"], D["ec"], D["d"]; o = D["out"][case]; S1, P = o["s1"], o["P"]
    ten = S1[:, 2]; F3, E3 = surface(D); val = np.clip(ten[E3], 0, None)
    col = np.where((val > LIMIT)[:, None], np.array([[0.35, 0.1, 0.45]]), cmap(0.08 + 0.85 * np.minimum(val / LIMIT, 1))[:, :3])
    clip = TW.box(TW.X0 + 0.5, TW.X0 + 15.5, d["YF"], d["YF"] + 12.4, TW.ZB - 0.9, TW.ZB)
    B = TW.BORE; XE = d["XH1"] - TW.LEAD
    cp = [(x, B * np.sin(t), B * np.cos(t)) for x in np.arange(d["XH0"], XE + 0.01, 0.25) for t in np.linspace(-0.6, 0.6, 9)] + \
         [(x, B * np.sin(t), -B * np.cos(t)) for x in np.arange(0, 2.51, 0.25) for t in np.linspace(-0.6, 0.6, 9)]
    near = cKDTree(np.array(cp)).query(ec, distance_upper_bound=2.0)[0] < 2.0
    edge = (np.hypot(ec[:, 0] - TW.J0, ec[:, 1] - TW.YI) < 0.4) | (np.hypot(ec[:, 0] - d["XH0"], ec[:, 1] - TW.YI) < 0.4)
    tpk, _, _, cpk = POST.hot(D, case, n=1, xmin=d["XH0"] + 0.5)[0][0]                 # the hook's peak away from the contact bands and sharp edges
    ax = fig.add_subplot(gs[r, 0]); R.FACES.clear(); add_faces(X, F3, col); R.mesh(TW.tm(clip), CLIP)
    R.mesh(TW.tm(TW.rod(50).translate([-1, 0, 0])), STEEL); R.mesh(TW.tm(TW.wires(L=22)), STEEL)
    cam = zoom(ax, (0.75, -0.8, 0.85), np.array([-48, -11, -16]), np.array([40, 22, 8 + HMAX]), 10.0)
    ax.set_title(f"{label}: whole piece, locked, from inboard, the front and above", fontsize=15, loc="left", fontweight="bold")
    R.call(ax, cam, (TW.X0 + 8, d["YF"] + 6, TW.ZB - 0.9), (-60, -60), "stock clip (held)", color="#3a4a5a", size=12)
    if r == 0: R.source(ax, os.path.abspath(__file__), cam)
    ax = fig.add_subplot(gs[r, 1]); R.FACES.clear(); add_faces(X, F3, col)
    cam = zoom(ax, (0.25, 1.0, -0.55), np.array([d["XH0"] - 1, -8, -4]), np.array([d["XH1"] + 1, 4, 6.5 + HMAX]), 22.0)
    ax.set_title(f"{label}: hook from its open rear side and below (rod hidden)", fontsize=15, loc="left", fontweight="bold")
    R.call(ax, cam, cpk, (70 if cpk[0] > (d["XH0"] + d["XH1"]) / 2 else -330, 110), f"{tpk:.0f} MPa tension, the hook's peak\naway from the rod contact (x {cpk[0]:.1f})", color="#8b1a1a", size=12)
    ax = fig.add_subplot(gs[r, 2]); ax.set_aspect("equal"); ax.axis("off"); U = o.get("U")
    if U is not None:
        import trimesh
        Ud = U.reshape(-1, 3); XS = d["XH1"] - 2.0                     # section 2 mm in from the hook end
        for P0, c, lw, lab in ((X, "#7a8aa0", 1.5, "unloaded"), (X + SCALE * Ud, "#c0392b", 2.2, f"loaded, displacement x{SCALE:g}")):
            sec = trimesh.Trimesh(P0, F3, process=False).section(plane_origin=[XS, 0, 0], plane_normal=[1, 0, 0])
            for k, ent in enumerate(sec.discrete): ax.plot(ent[:, 1], ent[:, 2], color=c, lw=lw, label=lab if k == 0 else None)
        th = np.linspace(0, 2 * np.pi, 90); ax.fill(TW.ROD * np.cos(th), TW.ROD * np.sin(th) + TW.RC, color=STEEL, alpha=0.35, label="rod (fixed)")
        sel = np.abs(X[:, 0] - XS) < 1.0; lift = Ud[sel, 2].max()
        ax.text(0.02, 0.02, f"hook top lifts up to {lift:.1f} mm here; the bore has 0.3 mm over the rod", transform=ax.transAxes, fontsize=13, color="#8b1a1a")
        ax.legend(loc="upper right", fontsize=12); ax.set_xlim(-12, 14); ax.set_ylim(-16, 12)
        ax.set_title(f"{label}: section x {XS:.1f} seen from inboard (front left)", fontsize=15, loc="left", fontweight="bold")
cax = fig.add_subplot(gs[:, 3]); sm = plt.cm.ScalarMappable(cmap=matplotlib.colors.LinearSegmentedColormap.from_list("r", cmap(np.linspace(0.08, 0.93, 64))), norm=plt.Normalize(0, LIMIT))
cb = fig.colorbar(sm, cax=cax); cb.set_label("largest tension, MPa (limit 75 along the layers, 56 across; purple = over 75)", fontsize=12)
fig.suptitle(f"Twist-lock front piece 3D check, hook load at the {case} ({P:.0f} N), 15 lb x 3 per corner. Rows share views and scale. "
             "Coarse mesh (the refined mesh read 18% higher at the curl root as drawn). Fillets left out; the rod's contact bands (dark at the load) are read by Hertz, not 3D. Inference.", fontsize=16)
R.save(fig, OUT)
