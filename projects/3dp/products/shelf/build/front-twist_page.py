"""Zoom page for a twist-lock 3D check (projects/3dp/scripts/zoompage.py; build-3dp, Pictures: zoom pages): each pickle from
fe/front_twist_tet.py becomes a turnable model colored by the largest tension in its load case (the stress pictures' colors, limit 75,
purple over it), with its displacement for the loaded-shape toggle and labels at its three highest tensions away from the rod
contacts and the sharp inside edges (fe/front_twist_post.py hot()), on the rod, the first two crosswires and the stock clip.
Usage: python3 front-twist_page.py out_dir "title" "intro" "label1" pkl1 case1 ["label2" pkl2 case2 ...] [--pic png "caption"]...
(case: start | end | spread, per model)
Prints the page path and the files map as JSON for the Artifact tool. Written 2026-10-11 (shelf thread, open decision 9)."""
import importlib.util, json, os, sys, pickle, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import zoompage as Z
def mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
TW = mod("ftm", os.path.join(HERE, "front-twist_model.py")); POST = mod("ftp", os.path.join(HERE, "fe", "front_twist_post.py"))
LIMIT = 75.0
def surface(D):
    """Outward boundary triangles of the tet mesh (corner nodes) and the element each belongs to (front-twist_stress.py surface())."""
    X, T = D["X"], D["T"]; fc = np.array([[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]])
    allf = np.concatenate([T[:, fc[k]] for k in range(4)]); el = np.tile(np.arange(len(T)), 4); opp = np.concatenate([T[:, k] for k in range(4)])
    _, inv, cnt = np.unique(np.sort(allf, 1), axis=0, return_inverse=True, return_counts=True)
    b = cnt[inv.ravel()] == 1; F3, E3, O3 = allf[b], el[b], opp[b]
    nrm = np.cross(X[F3[:, 1]] - X[F3[:, 0]], X[F3[:, 2]] - X[F3[:, 0]]); out = ((X[O3] - X[F3].mean(1)) * nrm).sum(1) > 0
    F3 = F3.copy(); F3[out] = F3[out][:, [0, 2, 1]]
    return F3, E3
if __name__ == "__main__":
    a = sys.argv[1:]; pics = []
    while "--pic" in a:
        i = a.index("--pic"); pics.append((a[i + 1], a[i + 2])); del a[i:i + 3]
    out_dir, title, intro = a[:3]; rows = list(zip(a[3::3], a[4::3], a[5::3])); models = []
    for label, pk, case in rows:
        D = pickle.load(open(pk, "rb")); o = D["out"][case]; F3, E3 = surface(D); X = D["X"]
        U = o.get("U"); disp = None if U is None else U.reshape(-1, 3)[F3]
        spots, _ = POST.hot(D, case, n=3)
        lift = "" if U is None else f"; hook lifts up to {U[2::3][X[:, 0] > TW.XH0].max():.1f} mm"
        models.append(Z.Model(label, X[F3], rgb=Z.reds(o["s1"][E3, 2], LIMIT), disp=disp, labels=[(c, f"{t:.0f} MPa") for t, _, _, c in spots],
                              note=f"{label.strip()}: hook load at the {case}, {o['P']:.0f} N{lift}. Labels: the three highest tensions away from the rod contacts and the two sharp inside edges."))
    YF = pickle.load(open(rows[0][1], "rb"))["d"]["YF"]                     # the clip drawn under the first row's front face, as the stress picture
    clip = TW.box(TW.X0 + 0.5, TW.X0 + 15.5, YF, YF + 12.4, TW.ZB - 0.9, TW.ZB)
    ctx = [(Z.tris(TW.tm(TW.rod(50).translate([-1, 0, 0]))), (0.42, 0.43, 0.47), "rod and crosswires"),
           (Z.tris(TW.tm(TW.wires(L=22))), (0.42, 0.43, 0.47), "rod and crosswires"),
           (Z.tris(TW.tm(clip)), (0.62, 0.67, 0.72), "stock clip")]
    html, files = Z.page(out_dir, title, intro, pictures=pics, models=models, context=ctx, eyebrow="Shelf · twist-lock front piece · 3D check",
                         legend=Z.stress_legend(LIMIT, "largest tension, MPa (limits 75 along the layers, 56 across)"),
                         source="Made by build/front-twist_page.py from fe/front_twist_tet.py pickles (coarse mesh unless named), "
                                "projects/3dp/products/shelf in nogbu/claude. All values are inference from a 3D check.")
    print(json.dumps(dict(html=html, files=files)))
