#!/usr/bin/env python3
"""Builds 6inInsert_rev2.4_DiscHoles.3mf (nursery-pots, 3dp project): rev2.3_DiscSettings (my Fusion disc with
a center hole and 4 slots, carrying plate 1's object settings), which printed smooth, plus our ceiling's 8
diagonal holes: diameter 4.0 mm (48 segments, as nurseryPots_lib builds them), at r 18.83 and 37.66 mm on the
45/135/225/315 degree diagonals, square edges. One change from rev2.3, so a rough print points at the holes
(agreed 2026-10-09).

Needs beside it: 6inInsert_rev2.3_DiscSettings.py and its two data files; needs trimesh and manifold3d.
"""
import importlib.util
import math
import os

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('rev23', os.path.join(HERE, '6inInsert_rev2.3_DiscSettings.py'))
rev23 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rev23)

NAME = '6inInsert_rev2.4_DiscHoles'
HOLE_R, HOLE_RADII, HOLE_ANGLES = 2.0, (18.83, 37.66), (45, 135, 225, 315)   # 6inInsert_rev2.py's holes

V, T = rev23.disc_mesh()
disc = trimesh.Trimesh(V, T, process=False)
cyls = []
for r in HOLE_RADII:
    for a in HOLE_ANGLES:
        c = trimesh.creation.cylinder(radius=HOLE_R, height=4.0, sections=48)
        c.apply_translation((r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0.6))
        cyls.append(c)
cut = disc.difference(trimesh.util.concatenate(cyls), engine='manifold')
assert cut.is_watertight, 'cut mesh not watertight'
removed = disc.volume - cut.volume
assert abs(removed - 8 * math.pi * HOLE_R ** 2 * 1.2) < 2.0, removed   # 8 full holes, 48-gon area
rev23.write(NAME, np.array(cut.vertices), np.array(cut.faces), '6inInsert rev2.4 DiscHoles')
