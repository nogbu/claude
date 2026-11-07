"""Picture of a plant tag built with plantTags_lib, bed face up (text reading as printed), soil line at 70 mm.
  python3 tagpic.py out.png em lw "row1:fil" "row2:fil" ... [--indent 0,2]"""
import sys, os, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../scripts'))
import numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import render3d as R, plantTags_lib as L
COL = {2: np.array([0x9F, 0x33, 0x2A]) / 255, 3: np.array([0.16, 0.16, 0.17])}; CLEAR = np.array([0.80, 0.87, 0.90]); TIP = 66.697
def main(a):
    out, em, lw = a[0], float(a[1]), a[2]
    ind = [int(v) for v in a[a.index('--indent') + 1].split(',')] if '--indent' in a else None
    rows = [(r.rsplit(':', 1)[0], int(r.rsplit(':', 1)[1])) for r in a[3:] if ':' in r]
    polys, bases, gap = L.layout(rows, em, ind or [0] + [2] * (len(rows) - 1))   # Product rule indent
    tag = L.tag_mesh(); body = L.mf_(tag); texts = []
    for P, f in polys:
        m = trimesh.util.concatenate([trimesh.creation.extrude_polygon(g, L.DEPTH, engine='earcut') for g in getattr(P, 'geoms', [P])])
        m.apply_translation((0, 0, L.TH - L.DEPTH)); texts.append((m, f)); body = body - L.mf_(m)
    R.FACES.clear(); R.mesh(L.tm_(body), CLEAR)
    for m, f in texts: R.mesh(m, COL[f])
    fig, ax = plt.subplots(figsize=(16, 4.8))
    cam = R.view(ax, eye=(0, -0.25, 1), pad=6, edge_depth=0.3, title=f'{em:g} mm text, {lw} mm lines, bed face up (reads as printed), soil line at 70 mm')
    x = TIP - 70; p, q = R.proj(cam, (x, -11, L.TH)), R.proj(cam, (x, 11, L.TH)); ax.plot([p[0], q[0]], [p[1], q[1]], color='#6b4423', lw=2, ls='--')
    t = R.proj(cam, (x, 11.5, L.TH)); ax.text(t[0], t[1], 'soil at 70', color='#6b4423', ha='center', va='bottom', fontsize=10, fontweight='bold')
    b0 = polys[0][0].bounds; b1 = polys[-1][0].bounds
    R.dim(ax, cam, (max(b[0].bounds[2] for b in polys), -10, L.TH), (x, -10, L.TH), (0, -3.5, 0))
    if len(polys) > 1: R.dim(ax, cam, (b0[0], 10, L.TH), (b1[0], 10, L.TH), (0, 3.5, 0))
    R.source(ax, L.SRC, cam); fig.tight_layout(); R.save(fig, out)
if __name__ == '__main__':
    main(sys.argv[1:])
