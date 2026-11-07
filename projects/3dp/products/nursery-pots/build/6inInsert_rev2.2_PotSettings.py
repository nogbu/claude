#!/usr/bin/env python3
"""Builds 6inInsert_rev2.2_PotSettings.3mf (nursery-pots, 3dp project): 6in insert rev2's ceiling,
cut flat at 1.08 mm (3 layers of 0.36 mm, printed ceiling-down), sliced with every setting the
6in pot rev2 uses for its floor: the pot's project settings (the shared base, without the insert's
filament overrides), its object settings and its floor height range. Tests whether the 6in pot's
settings print the ceiling smooth (asked 2026-10-08).

Settings: 6inPot_rev2.py's build_pot values (outer wall 28 mm/s, wall line width 1.2 mm, slots
43.56-55.44 mm, band bead 0.64), repeated below, through nurseryPots_lib's POT_OBJECT_SETTINGS and
pot_layer_ranges; geometry from 6inInsert_rev2.py's values (repeated below). The pot's foot fan
ramp starts above 9 mm, so it is left out.
Needs beside it: nurseryPots_lib.py and nurseryPots_settings_base.json; needs trimesh and
manifold3d for the cut.
"""
import math
import os

import numpy as np
import trimesh

import nurseryPots_lib as lib

HERE = os.path.dirname(os.path.abspath(__file__))
POT_OUTER_WALL_SPEED, POT_WALL_LINE_WIDTH = 28, 1.2      # 6inPot_rev2.py
POT_Z_SB, POT_Z_ST, POT_BAND_BEAD = 43.56, 55.44, 0.64    # 6inPot_rev2.py

NAME = '6inInsert_rev2.2_PotSettings'
Z_CUT = 1.08             # 3 layers of 0.36 mm, the pot floor's layer height (rev2's ceiling: 3 x 0.4)
SLOPE = 5.03
RHO = 1.2 / (math.sqrt(0.5) - math.sin(math.radians(SLOPE)))

M, _ = lib.build_insert_mesh(R=52.075, t=1.2, H=46.0, T=1.2, c=0.0, slot_w=3.0, slot_r0=11.52,
                             slot_r1=39.66, hole_r=2.0, hole_radii=[18.83, 37.66], notch_w=3.0,
                             notch_d=18.0, rim_chamfer=0.0, rim_round=0.0, open_chamfer=0.4,
                             slope_deg=SLOPE, shoulder=(0.4, RHO))
tm = trimesh.Trimesh(np.array(M.V), np.array(M.T), process=True)
box = trimesh.creation.box(bounds=[[-80, -80, -1], [80, 80, Z_CUT]])
cut = tm.intersection(box, engine='manifold')
assert cut.is_watertight, 'cut mesh not watertight'
C = lib.Mesh()
C.V = [tuple(map(float, v)) for v in cut.vertices]
for a, b, c in cut.faces:
    C.tri(int(a), int(b), int(c))
vol = lib.orient_and_check(C)

# the pot's object settings, then its floor range (0-2.16 mm), which covers the whole piece
obj = dict(lib.POT_OBJECT_SETTINGS + [('outer_wall_speed', lib._fmt(POT_OUTER_WALL_SPEED)),
                                      ('outer_wall_line_width', lib._fmt(POT_WALL_LINE_WIDTH)),
                                      ('inner_wall_line_width', lib._fmt(POT_WALL_LINE_WIDTH))])
z0, z1, floor = lib.pot_layer_ranges(POT_Z_SB, POT_Z_ST, POT_BAND_BEAD)[0]
assert (z0, z1) == (0.0, 2.16), (z0, z1)
obj.update(floor)
path = os.path.join(HERE, NAME + '.3mf')
lib.write_3mf(path, C, NAME, Z_CUT, np.zeros(len(C.T), dtype=bool), sorted(obj.items()), [], {},
              fan_ramp=False, plate_name=NAME.replace('_', ' ') + ' (ceiling down)')
zs = np.array(C.V)[:, 2]
print(dict(path=path, plastic_cm3=round(vol / 1000, 3), z=(zs.min(), zs.max()), tris=len(C.T)))
