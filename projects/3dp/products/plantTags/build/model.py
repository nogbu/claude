"""Scratch working model of plantTags with agreed changes 1-2, from plantTags.3mf's own meshes.
Turned-over frame for pictures: bed face up at Z = 0.96, reading coords X = x, Y = -y (text reads from above)."""
from parse import out
import trimesh, numpy as np, manifold3d as mf
TH, DEPTH, S = 1.02, 0.54, 9 / 6.5
BASE0 = -1.969                      # baseline in the file's reading coords (6.5 mm text)
TOP_ASC = 2.821 - BASE0             # i-dot top above baseline at 6.5 mm (tallest mark in the words)
X0 = -62.567                        # left edge of the file's text, kept
b1 = 10 - 1 - TOP_ASC * S           # row 1 baseline: 1 mm margin to the tallest mark
b2 = b1 - 9.6                       # baselines 9.6 apart (agreed change 2)
def word(oid, base):
    p, i, V, t = out[oid][1]
    x, y, z = V[:, 0], -V[:, 1], V[:, 2]
    X = X0 + (x - X0) * S; Y = base + (y - BASE0) * S
    Z = TH - DEPTH + (z - z.min()) / (z.max() - z.min()) * DEPTH
    return trimesh.Trimesh(np.c_[X, Y, Z], t[:, ::-1] if True else t, process=True)
def tm2mf(m):
    return mf.Manifold(mf.Mesh(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.uint32)))
def mf2tm(M):
    g = M.to_mesh(); return trimesh.Trimesh(g.vert_properties[:, :3], g.tri_verts)
p, i, V, t = out['6'][0]
tag = trimesh.Trimesh(np.c_[V[:, 0], -V[:, 1], (V[:, 2] + 0.48) * TH / 0.96], t[:, ::-1])
name = word('6', b1); species = word('3', b2)
for m in (tag, name, species):
    if m.volume < 0: m.invert()
body = mf2tm(tm2mf(tag) - tm2mf(name) - tm2mf(species))
if __name__ == '__main__':
    print('b1', round(b1, 3), 'b2', round(b2, 3))
    for n, m in (('body', body), ('name', name), ('species', species)):
        print(n, m.is_watertight, round(m.volume, 2), m.bounds.round(3).tolist())
    print('row2 desc bottom', round(b2 - (BASE0 + 3.185) * S, 3))
