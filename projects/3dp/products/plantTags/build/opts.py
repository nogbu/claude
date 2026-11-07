"""Plant tag text options: a 21-character name in Overpass ExtraBold (wght 800, the file's Overpass Heavy) inlaid flush 0.54 mm
on the 1.02 mm tag, one row centered across the tag, left edge where the 3mf puts it, soil lines at 60 and 70 mm."""
import sys, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0, '/home/user/claude/projects/3dp/scripts')
import numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.textpath import TextPath; from matplotlib.font_manager import FontProperties
from shapely.geometry import Polygon; from shapely.ops import unary_union
import render3d as R
from parse import out
from model import tm2mf, mf2tm, TH, DEPTH, X0
from pic import CLEAR, BLACK, SRC
from strokes import lost
FP = FontProperties(fname='fonts/ov800.ttf'); TIP = 66.697
def textpoly(s, em):
    tp = TextPath((0, 0), s, size=em, prop=FP)
    rings = [Polygon(p) for p in tp.to_polygons() if len(p) > 2]
    rings.sort(key=lambda p: -p.area); P = Polygon()
    for r in rings:   # even-odd: holes inside earlier rings
        P = P.difference(r) if P.contains(r.representative_point()) else P.union(r)
    return P
def check():   # the font matches the 3mf's text: "name" width at 6.5 mm
    P = textpoly('name', 6.5); print('font name width', round(P.bounds[2] - P.bounds[0], 2), '(3mf 16.36)')
p, i, V, t = out['6'][0]
tag = trimesh.Trimesh(np.c_[V[:, 0], -V[:, 1], (V[:, 2] + 0.48) * TH / 0.96], t)
if tag.volume < 0: tag.invert()
TEXT = 'Alocasia Black Velvet'
OPTS = [('A', 6.0, 0.30), ('B', 5.5, 0.30)]
if __name__ == '__main__':
    check()
    fig, axs = plt.subplots(len(OPTS), 1, figsize=(16, 4.2 * len(OPTS)))
    for ax, (L, em, lw) in zip(axs, OPTS):
        P = textpoly(TEXT, em); b = P.bounds
        from shapely import affinity
        P = affinity.translate(P, X0 - b[0], -(b[1] + b[3]) / 2)
        thin = 100 * lost(P, 2 * lw)
        w = trimesh.util.concatenate([trimesh.creation.extrude_polygon(g, DEPTH, engine='earcut') for g in getattr(P, 'geoms', [P])]); w.apply_translation((0, 0, TH - DEPTH))
        body = mf2tm(tm2mf(tag) - tm2mf(w))
        R.FACES.clear(); R.mesh(body, CLEAR); R.mesh(w, BLACK)
        cam = R.view(ax, eye=(0, -0.25, 1), pad=6, edge_depth=0.3,
                     title=f'{L}: {em:g} mm text, {lw:.2f} mm lines; {len(TEXT)} characters span {P.bounds[2]-P.bounds[0]:.1f} mm; {thin:.1f}% of letter area under two beads')
        for d in (60, 70):
            x = TIP - d; a, c = R.proj(cam, (x, -11, TH)), R.proj(cam, (x, 11, TH))
            ax.plot([a[0], c[0]], [a[1], c[1]], color='#6b4423', lw=2, ls='--')
            q = R.proj(cam, (x, 11.5, TH)); ax.text(q[0], q[1], f'soil at {d}', color='#6b4423', ha='center', va='bottom', fontsize=10, fontweight='bold')
        R.dim(ax, cam, (P.bounds[0], -10, TH), (P.bounds[2], -10, TH), (0, -3.5, 0))
        print(L, em, lw, 'span', round(P.bounds[2] - P.bounds[0], 2), 'end x', round(P.bounds[2], 2), 'soil70 x', TIP - 70, 'thin%', round(thin, 1))
    R.source(axs[-1], SRC, cam); fig.tight_layout()
    R.save(fig, '/mnt/project-files/images/plantTags_textOptions2.png')
