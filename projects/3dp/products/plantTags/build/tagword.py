"""Name tag with its word replaced (default "mugatu"): Overpass ExtraBold 5.5 mm, red-brown, inlaid flush 0.54 mm on the 1.02 mm tag,
left edge where the 3mf puts it, centered across the tag; whole tag plus a close-up."""
import sys, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0, '/home/user/claude/projects/3dp/scripts')
import numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely import affinity
import render3d as R, manifold3d as mf
from opts import textpoly, tag, TIP
from model import tm2mf, mf2tm, TH, DEPTH, X0
from pic import CLEAR, RED, SRC
from strokes import lost
WORD = sys.argv[1] if len(sys.argv) > 1 else 'mugatu'; EM = 5.5
P = textpoly(WORD, EM); b = P.bounds; P = affinity.translate(P, X0 - b[0], -(b[1] + b[3]) / 2)
w = trimesh.util.concatenate([trimesh.creation.extrude_polygon(g, DEPTH, engine='earcut') for g in getattr(P, 'geoms', [P])])
w.apply_translation((0, 0, TH - DEPTH)); body = mf2tm(tm2mf(tag) - tm2mf(w))
print(WORD, 'span', round(P.bounds[2] - P.bounds[0], 2), 'height', round(P.bounds[3] - P.bounds[1], 2), 'under two 0.31 beads %.1f%%' % (100 * lost(P, 0.62)))
fig = plt.figure(figsize=(16, 9)); gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.3])
ax = fig.add_subplot(gs[0]); R.FACES.clear(); R.mesh(body, CLEAR); R.mesh(w, RED)
cam = R.view(ax, eye=(0, -0.25, 1), pad=5, edge_depth=0.3, title=f'"{WORD}" name tag, bed face up: {EM} mm text, inlaid flush 0.54 mm, 1.02 mm tag')
x = TIP - 70; a, c = R.proj(cam, (x, -11, TH)), R.proj(cam, (x, 11, TH)); ax.plot([a[0], c[0]], [a[1], c[1]], color='#6b4423', lw=2, ls='--')
q = R.proj(cam, (x, 11.5, TH)); ax.text(q[0], q[1], 'soil at 70', color='#6b4423', ha='center', va='bottom', fontsize=10, fontweight='bold')
R.dim(ax, cam, (P.bounds[0], -10, TH), (P.bounds[2], -10, TH), (0, -3.5, 0))
ax = fig.add_subplot(gs[1]); B = mf.Manifold.cube(np.array([26, 22, 3.0])).translate(np.array([-67.5, -11, -1.0]))
R.FACES.clear(); R.mesh(mf2tm(tm2mf(body) ^ B), CLEAR); R.mesh(mf2tm(tm2mf(w) ^ B), RED)
cam2 = R.view(ax, eye=(-0.3, -0.6, 1), pad=1.5, edge_depth=0.1, title='Close-up: square end, letters inlaid flush')
R.dim(ax, cam2, (P.bounds[2] + 1, P.bounds[1], TH), (P.bounds[2] + 1, P.bounds[3], TH), (2.5, 0, 0))
R.source(ax, SRC, cam2); fig.tight_layout(); R.save(fig, f'/mnt/project-files/images/plantTags_{WORD}.png')
