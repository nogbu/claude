"""Separate name and species tags as in plantTags.3mf, with changes 1 and 3 (flush 0.54 mm inlay, 1.02 mm tag),
text at 9 mm about the file's own text center (left edge kept)."""
import sys; sys.path.insert(0, '/home/user/claude/projects/3dp/scripts')
import numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import render3d as R
from parse import out
from model import tm2mf, mf2tm, TH, DEPTH, S, X0
from pic import CLEAR, BLACK, RED, SRC
def word(oid):
    p, i, V, t = out[oid][1]
    x, y, z = V[:, 0], -V[:, 1], V[:, 2]
    yc = (y.min() + y.max()) / 2
    X = x.min() + (x - x.min()) * S; Y = yc + (y - yc) * S
    Z = TH - DEPTH + (z - z.min()) / (z.max() - z.min()) * DEPTH
    m = trimesh.Trimesh(np.c_[X, Y, Z], t); 
    if m.volume < 0: m.invert()
    return m
p, i, V, t = out['6'][0]
tag = trimesh.Trimesh(np.c_[V[:, 0], -V[:, 1], (V[:, 2] + 0.48) * TH / 0.96], t)
if tag.volume < 0: tag.invert()
fig, axs = plt.subplots(2, 1, figsize=(16, 8))
for ax, oid, col, lab in ((axs[0], '6', RED, 'Plate 2 "name" tags (4), red-brown text'), (axs[1], '3', BLACK, 'Plate 1 "species" tags (4), black text')):
    w = word(oid); body = mf2tm(tm2mf(tag) - tm2mf(w))
    R.FACES.clear(); R.mesh(body, CLEAR); R.mesh(w, col)
    cam = R.view(ax, eye=(0, -0.25, 1), pad=4, edge_depth=0.3, title=lab + ', bed face up')
    R.dim(ax, cam, (-66.697, -10, TH), (-66.697, 10, TH), (-4, 0, 0))
    lo, hi = w.bounds; R.dim(ax, cam, (hi[0] + 1, lo[1], TH), (hi[0] + 1, hi[1], TH), (3, 0, 0))
    print(oid, w.bounds.round(2).tolist())
R.source(axs[1], SRC, cam)
fig.suptitle('plantTags as laid out in your 3mf: one word per tag, inlaid flush 0.54 mm, 9 mm text, 1.02 mm tag', fontsize=15, fontweight='bold')
fig.tight_layout(); R.save(fig, '/mnt/project-files/images/plantTags_separate.png')
