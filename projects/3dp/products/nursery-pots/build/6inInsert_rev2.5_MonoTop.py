#!/usr/bin/env python3
"""Builds 6inInsert_rev2.5_MonoTop.3mf (nursery-pots, 3dp project): a one-change test for the rough 6in
insert ceiling. Plate 1 of my 2234567.3mf (2026-10-09: rev2.2's ceiling with plate 1's object settings, in
that file's project settings) printed rough; its top layer slices into 48 lines under 10 mm, and the rough
spots on rev2.4 sit where such short lines are (photos 20261009_172236-172258). This file is plate 1 with
only the top surface pattern changed from Monotonic line to Monotonic, which joins the top lines into
zigzags and slices with none under 10 mm (agreed 2026-10-09: test on our ceiling).

Geometry: 6inInsert_rev2.2_PotSettings.py's ceiling (values repeated below), cut at 1.2 mm instead of
1.08 mm so it sits on the 0.3 mm layer grid; Orca prints plate 1's 1.08 mm cut as 4 layers to 1.2 mm
anyway, and both cuts slice to the same extrusion (per-layer lengths within 0.2 mm; travel routes differ
slightly; checked 2026-10-09). The 0.4 mm bed-side chamfers stay off the 0.3 mm grid, as on plate 1, so the
test stays one change (dpcheck dp 12 FAIL, kept on purpose). Settings: rev2.3's settings base
(2234567.3mf's project settings) and plate 1's object settings (6inInsert_rev2.3_DiscSettings.py), plus
top_surface_pattern = monotonic as an object setting.
Needs beside it: nurseryPots_lib.py, 6inInsert_rev2.3_DiscSettings.py and its settings base json; needs
trimesh and manifold3d.
"""
import importlib.util
import math
import os

import numpy as np
import trimesh

import nurseryPots_lib as lib

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('rev23', os.path.join(HERE, '6inInsert_rev2.3_DiscSettings.py'))
rev23 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rev23)
W = rev23.W

NAME = '6inInsert_rev2.5_MonoTop'
TOP_PATTERN = 'monotonic'       # plate 1: monotonicline (the file's project setting)
Z_CUT = 1.2                     # 4 layers of 0.3 mm (rev2.2: 1.08, 3 layers of 0.36 mm)
SLOPE = 5.03                    # 6inInsert_rev2.2_PotSettings.py's insert values, unchanged
RHO = 1.2 / (math.sqrt(0.5) - math.sin(math.radians(SLOPE)))


def ceiling_mesh(z_cut=Z_CUT):
    M, _ = lib.build_insert_mesh(R=52.075, t=1.2, H=46.0, T=1.2, c=0.0, slot_w=3.0, slot_r0=11.52,
                                 slot_r1=39.66, hole_r=2.0, hole_radii=[18.83, 37.66], notch_w=3.0,
                                 notch_d=18.0, rim_chamfer=0.0, rim_round=0.0, open_chamfer=0.4,
                                 slope_deg=SLOPE, shoulder=(0.4, RHO))
    tm = trimesh.Trimesh(np.array(M.V), np.array(M.T), process=True)
    box = trimesh.creation.box(bounds=[[-80, -80, -1], [80, 80, z_cut]])
    cut = tm.intersection(box, engine='manifold')
    assert cut.is_watertight, 'cut mesh not watertight'
    return np.array(cut.vertices), np.array(cut.faces)


def write(name, V, T, top_pattern, plate_name):
    settings = W.base(os.path.join(HERE, '6inInsert_rev2.3_settings_base.json'))
    obj_settings = rev23.PLATE1_OBJECT_SETTINGS + ([('top_surface_pattern', top_pattern)] if top_pattern else [])
    ceiling = W.Obj(name, [W.Part(V, T)], settings=obj_settings, at=[(128, 128)])
    path = W.write(os.path.join(HERE, name + '.3mf'), [ceiling], settings, plate_name=plate_name)
    print(dict(path=path, verts=len(V), tris=len(T), size=(V.max(0) - V.min(0)).round(3).tolist(),
               plastic_cm3=round(trimesh.Trimesh(V, T).volume / 1000, 3)))


if __name__ == '__main__':
    write(NAME, *ceiling_mesh(), TOP_PATTERN, '6inInsert rev2.5 MonoTop')
