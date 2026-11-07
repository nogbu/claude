#!/usr/bin/env python3
"""Builds 6inInsert_rev2.1_FanOff.3mf (nursery-pots, 3dp project): 6in insert rev2 cut flat at
1.2 mm (its 3 ceiling layers only, printed ceiling-down), to test whether the part fan causes the
rough top face of the ceiling.

One change from rev2 (agreed 2026-10-09): no part cooling for the first 4 layers instead of 3
(close_fan_the_first_x_layers, filament 1), so the fan stays off on layer 3, the ceiling's top
face, as on the pot floors, which print smooth. rev2 turns it on at 40% on layer 3.
Everything else (mesh below the cut, object settings, filament profile) is rev2's.
Needs beside it: 6inInsert_rev2.py's values (repeated below), nurseryPots_lib.py and
nurseryPots_settings_base.json (both used unchanged); needs trimesh and manifold3d for the cut.
"""
import math
import os

import numpy as np
import trimesh

import nurseryPots_lib as lib

NAME = '6inInsert_rev2.1_FanOff'
Z_CUT = 1.2              # 3 layers of 0.4 mm: the ceiling
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

over = dict(lib.INSERT_SETTINGS_OVERRIDES)
over['close_fan_the_first_x_layers'] = ['4', '1']
obj = [('layer_height', '0.4'), ('wall_loops', '2'), ('outer_wall_line_width', '0.64'),
       ('inner_wall_line_width', '0.64'), ('outer_wall_speed', '60'), ('inner_wall_speed', '60'),
       ('internal_solid_infill_speed', '200'), ('top_surface_speed', '60'),
       ('outer_wall_acceleration', '5000'), ('inner_wall_acceleration', '5000'),
       ('seam_position', 'aligned'), ('bottom_surface_pattern', 'monotonic'),
       ('top_surface_pattern', 'monotonic'), ('internal_solid_infill_pattern', 'monotonic')]
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME + '.3mf')
lib.write_3mf(path, C, NAME, Z_CUT, np.zeros(len(C.T), dtype=bool), obj, [], over,
              fan_ramp=False, plate_name=NAME.replace('_', ' ') + ' (ceiling down)')
zs = np.array(C.V)[:, 2]
print(dict(path=path, plastic_cm3=round(vol / 1000, 3), z=(zs.min(), zs.max()), tris=len(C.T)))
