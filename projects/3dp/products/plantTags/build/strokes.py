"""Thinnest stroke and narrowest space in the 3mf's text (6.5 mm), from a mid-depth section, by morphological opening."""
from parse import out
import trimesh, numpy as np
from shapely.ops import unary_union
from shapely.geometry import box
def section(oid):
    p, i, V, t = out[oid][1]; m = trimesh.Trimesh(V, t)
    z = (V[:, 2].min() + V[:, 2].max()) / 2
    s = m.section(plane_origin=(0, 0, z), plane_normal=(0, 0, 1)); pl, _ = s.to_planar()
    return unary_union(list(s.to_2D(to_2D=np.eye(4))[0].polygons_full) if False else s.to_planar()[0].polygons_full)
def lost(P, w):   # area an opening of width w removes, as a share of the area
    return 1 - P.buffer(-w / 2, join_style=1).buffer(w / 2, join_style=1).area / P.area
def thin(P, tol=0.002):
    for w in np.arange(0.10, 2.0, 0.01):
        if lost(P, w) > tol: return round(w - 0.01, 2)
for oid, n in (('6', 'name'), ('3', 'species')):
    T = section(oid)
    gaps = box(*T.bounds).buffer(2).difference(T)
    print(n, 'thinnest stroke', thin(T), 'narrowest space', thin(gaps), 'area', round(T.area, 2))
