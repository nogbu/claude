#!/usr/bin/env python3
"""Builds 6inInsert_rev2.7_NoChamfer.3mf (nursery-pots, 3dp project): a one-change test for the rough 6in
insert ceiling. Plate 1 of my 2234567.3mf (rev2.2's ceiling with plate 1's object settings) printed rough;
rev2.4 (the Fusion disc plus our 8 holes, square edges) printed much better, rough only near holes and slot
ends. The clearest mesh difference is plate 1's 0.4 mm bed-side chamfers on the ceiling openings. This file is
plate 1 with those chamfers removed (square opening edges, as agreed change 1 makes every insert) and nothing
else changed: plate 1's top pattern (Monotonic line), its object settings and 2234567's project settings.

Geometry: rev2.5_MonoTop's ceiling (6inInsert_rev2.5_MonoTop.py, cut at 1.2 mm on the 0.3 mm grid, which
slices to the same extrusion as plate 1's 1.08 mm cut) with open_chamfer 0.4 -> 0.
Needs beside it: nurseryPots_lib.py, 6inInsert_rev2.5_MonoTop.py, 6inInsert_rev2.3_DiscSettings.py and its
settings base json; needs trimesh and manifold3d.
"""
import importlib.util
import os

import numpy as np
import trimesh

import nurseryPots_lib as lib

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('rev25', os.path.join(HERE, '6inInsert_rev2.5_MonoTop.py'))
rev25 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rev25)

NAME = '6inInsert_rev2.7_NoChamfer'
OPEN_CHAMFER = 0.0              # plate 1: 0.4


def ceiling_mesh(z_cut=rev25.Z_CUT):
    M, _ = lib.build_insert_mesh(R=52.075, t=1.2, H=46.0, T=1.2, c=0.0, slot_w=3.0, slot_r0=11.52,
                                 slot_r1=39.66, hole_r=2.0, hole_radii=[18.83, 37.66], notch_w=3.0,
                                 notch_d=18.0, rim_chamfer=0.0, rim_round=0.0, open_chamfer=OPEN_CHAMFER,
                                 slope_deg=rev25.SLOPE, shoulder=(0.4, rev25.RHO))
    tm = trimesh.Trimesh(np.array(M.V), np.array(M.T), process=True)
    box = trimesh.creation.box(bounds=[[-80, -80, -1], [80, 80, z_cut]])
    cut = tm.intersection(box, engine='manifold')
    assert cut.is_watertight, 'cut mesh not watertight'
    return np.array(cut.vertices), np.array(cut.faces)


if __name__ == '__main__':
    rev25.write(NAME, *ceiling_mesh(), None, '6inInsert rev2.7 NoChamfer')
