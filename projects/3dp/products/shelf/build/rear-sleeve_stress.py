"""Rear piece 3D check picture: the piece's surface colored by the largest stress magnitude (element centers, fe/rear_tet.py),
mounted on its rods and clip, whole design plus a close-up of the sleeve root. Usage: python3 rear-sleeve_stress.py [pkl] [case] [out.png]"""
import importlib.util, os, sys, pickle, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, REPO + "/scripts")
import render3d as R
spec = importlib.util.spec_from_file_location("rear_piece_model", os.path.join(HERE, "rear-piece_model.py"))
RP = importlib.util.module_from_spec(spec); spec.loader.exec_module(RP)
pk = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "fe", "rear_tet_40.pkl")
D = pickle.load(open(pk, "rb")); case = sys.argv[2] if len(sys.argv) > 2 else "tip, stubs on the lip rod"
X, T, ec = D["X"], D["T"], D["ec"]; S1 = D["out"][case]["s1"]; s1 = np.maximum(S1[:, 2], -S1[:, 0]); reach = D["args"][0]   # largest magnitude, tension or compression
LIMIT = 75.0                                                   # PETG Basic bending along the layers (data sheet V3.0)
fc = np.array([[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]])
allf = np.concatenate([T[:, fc[k]] for k in range(4)]); el = np.tile(np.arange(len(T)), 4); opp = np.concatenate([T[:, k] for k in range(4)])
_, inv, cnt = np.unique(np.sort(allf, 1), axis=0, return_inverse=True, return_counts=True)
b = cnt[inv.ravel()] == 1; F3, E3, O3 = allf[b], el[b], opp[b]
V = X[F3]; nrm = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); out = ((X[O3] - V.mean(1)) * nrm).sum(1) > 0
V[out] = V[out][:, [0, 2, 1]]; nrm[out] *= -1; nrm /= np.linalg.norm(nrm, axis=1)[:, None]
cmap = plt.get_cmap("Reds"); val = np.clip(s1[E3], 0, None)
col = np.where((val > LIMIT)[:, None], np.array([[0.35, 0.1, 0.45]]), cmap(0.08 + 0.85 * np.minimum(val / LIMIT, 1))[:, :3])
ROD = np.array([0.22, 0.22, 0.24]); STEEL = np.array([0.55, 0.6, 0.66])
clip = RP.box(RP.X0 + 0.5, RP.X0 + 15.5, D["d"]["yr"] - 12.4, D["d"]["yr"], RP.ZB - 0.9, RP.ZB)
def scene():
    R.FACES.clear()
    R.FACES.extend((v, n, c, False) for v, n, c in zip(V, nrm, col))
    R.mesh(RP.tm(RP.rods(reach + 15)), ROD); R.mesh(RP.tm(clip), STEEL)
def zoom(ax, eye, lo, hi, ppm):
    """Render the whole scene framed on the box lo..hi (no face cropping, so no jagged cut edges)."""
    e, right, up = R.camera(eye); corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    u, v = corners @ right, corners @ up
    img, cam = R.render(eye, ppm, frame=(u.min(), u.max(), v.min(), v.max())); ax.imshow(img); ax.axis("off"); return cam
fig = plt.figure(figsize=(26, 13)); gs = fig.add_gridspec(1, 3, width_ratios=[1.2, 1.2, 0.06])
ax = fig.add_subplot(gs[0]); scene(); cam = R.view(ax, eye=(0.35, 1.0, -0.45), ppm=8.5, pad=4)
ax.set_title("Whole rear piece end, from the rear (the lip's wire side) and below", fontsize=15, loc="left", fontweight="bold")
O = D.get("opts", {}); STUB = O.get("stub", 2.5); B = RP.BORE
from scipy.spatial import cKDTree                              # rod contact zones: the lip rod on the sleeve top near its tip, the stubs on the bore floors
cpts = [(x, B * np.sin(t), z0 + sgn * B * np.cos(t)) for x in np.arange(0, reach + 0.01, 0.25) for t in np.linspace(-0.6, 0.6, 9)
        for z0, sgn, ok in ((RP.LIPB, 1, x > reach - 2.5), (RP.LIPB, -1, x < STUB), (0.0, -1, x < STUB)) if ok]
near = cKDTree(np.array(cpts)).query(ec, distance_upper_bound=1.5)[0] < 1.5
i = np.argmax(np.where(~near, s1, -1e9)); j = np.argmax(np.where(near, s1, -1e9))
R.call(ax, cam, ec[i], (-150, 40), f"peak away from the rod contacts: {s1[i]:.0f} MPa ({'compression' if -S1[i, 0] > S1[i, 2] else 'tension'})", color="#8b1a1a", size=12)
print(f"peak away from contacts {s1[i]:.1f} at {np.round(ec[i], 1)}; at contacts {s1[j]:.1f} at {np.round(ec[j], 1)}")
R.call(ax, cam, (RP.X0 + 8, D["d"]["yr"] - 6, RP.ZB - 0.9), (-60, 70), "stock clip (held)", color="#3a4a5a", size=11)
R.call(ax, cam, (reach - 1, D["d"]["rear"], RP.LIPB + 3), (60, 60), f"lip rod pushes up here (x {reach - 2.5:.1f}..{reach:.0f})", color="#222", size=11)
R.source(ax, os.path.abspath(__file__), cam)
ax2 = fig.add_subplot(gs[1]); lo = np.array([RP.J0 - 4, -8, -40]); hi = np.array([reach + 2, 8, -22])
cam2 = zoom(ax2, (0.35, 1.0, 0.25), lo, hi, 26.0)
ax2.set_title("Close-up: the lip sleeve from root to tip, from the rear and a little above", fontsize=15, loc="left", fontweight="bold")
R.call(ax2, cam2, ec[i], (-60, -90), f"peak away from the rod contacts: {s1[i]:.0f} MPa", color="#8b1a1a", size=11)
R.call(ax2, cam2, (RP.J0 + 0.5, D["d"]["rear"], D["d"]["zt"] + 0.5), (-90, 60), "root fillet r1.0 (rear end)", color="#222", size=11)
closed = O.get("close_below") is not None; trimmed = O.get("trim", False)
if closed: R.call(ax2, cam2, (RP.J0 + 14, D["d"]["yr"], RP.LIPB - 3.5), (-40, -80), f"rear wall, closed below the wire ends ({-O['close_below']:.2f} under the rod center)", color="#8b1a1a", size=11)
else: R.call(ax2, cam2, (RP.J0 + 4, D["d"]["rear"], RP.LIPB - 1.61), (90, -70), "lower lip of the rear opening" + (" (one bead)" if trimmed else " (knife edge)"), color="#8b1a1a", size=11)
R.call(ax2, cam2, (RP.J0 + 6, D["d"]["rear"], RP.LIPB + (RP.bore_z(D["d"]["rear"] - RP.F.BEAD) if trimmed else 1.61)), (90, 60),
       "upper lip" + (" (one bead)" if trimmed else " (knife edge)"), color="#8b1a1a", size=11)
cax = fig.add_subplot(gs[2]); sm = plt.cm.ScalarMappable(cmap=matplotlib.colors.LinearSegmentedColormap.from_list("r", cmap(np.linspace(0.08, 0.93, 64))),
                                                          norm=plt.Normalize(0, LIMIT))
cb = fig.colorbar(sm, cax=cax); cb.set_label("largest stress, tension or compression, MPa (limit 75 along the layers; purple = over)", fontsize=12)
fig.suptitle(f"Rear piece 3D check, {case}: 15 lb x 3 per corner, sleeve reach x {reach:g}" + (", rear wall closed below the wires" if closed else "")
             + (f", stub bearing x 0..{O['stub']:g}" if "stub" in O else "") + ". Walls 2.48 / 2.35; fillets left out except the sleeve root. Inference.", fontsize=15)
R.save(fig, sys.argv[3] if len(sys.argv) > 3 else "/mnt/project-files/images/shelf_rearSleeve_3D.png")
