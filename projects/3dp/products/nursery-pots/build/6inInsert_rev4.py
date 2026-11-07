#!/usr/bin/env python3
"""Builds 6inInsert_rev4.3mf (nursery-pots, 3dp project), printed ceiling-down: rev3 with every fillet and chamfer
removed (my ask 2026-10-10), so the shoulder's 45 deg chamfer and curve go and the wall meets the ceiling in a
square corner; four on one plate (my ask). Everything else as rev3 (6inInsert_rev3.py): rim R 50.321, wall 1.24 mm
leaning in 5.03 deg, ceiling 1.6 mm, height 46.4 mm, slots and notches 3.0 mm with rounded ends (not fillets:
agreed change 1 keeps them), slot ends kept at rev3's r 35.57, no opening chamfers.
Plate: 2 x 2, 5 mm between rims (the family's pot gap), centered on the 256 mm bed; the front-left insert clears
the excluded corner (0-18 x 0-28 mm). Same object and project settings as nurseryPots_lib.build_insert.
Needs beside it: nurseryPots_lib.py, nurseryPots_settings_base.json, 6inInsert_rev3.py, 2.5inPot_rev2.py; needs
projects/3dp/scripts (write3mf, render3d) three folders up; numpy, scipy.
Picture: python3 insertPicture.py 6inInsert_rev4_single.3mf 6inPot_rev2.3mf OUT.png --waterline 43.56 --ray-start 50
(--single writes the one-insert file the picture script reads).
"""
import importlib.util
import os
import sys

import numpy as np

import nurseryPots_lib as lib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'scripts'))
import write3mf as W  # noqa: E402

spec = importlib.util.spec_from_file_location('rev3', os.path.join(HERE, '6inInsert_rev3.py'))
rev3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(rev3)

NAME = '6inInsert_rev4'
V3 = rev3.values()
SLOT_R1 = 35.57                           # rev3's slot ends, unchanged
GAP_BETWEEN = 5.0                         # mm between rims
PITCH = 2 * V3['R'] + GAP_BETWEEN         # 105.642
AT = [(128 + sx * PITCH / 2, 128 + sy * PITCH / 2) for sy in (-1, 1) for sx in (-1, 1)]


def mesh():
    M, info = lib.build_insert_mesh(V3['R'], rev3.t, V3['H'], rev3.T, 0.0, rev3.SLOT_W, rev3.SLOT_R0, SLOT_R1, 2.0,
                                    rev3.HOLE_R, rev3.NOTCH_W, rev3.NOTCH_D, rim_chamfer=0.0, rim_round=0.0,
                                    open_chamfer=rev3.OPEN_CH, slope_deg=rev3.SLOPE, shoulder=None)
    return np.array(M.V), np.array(M.T), info


def obj_settings(bead):
    """build_insert's object settings, unchanged."""
    f = lib._fmt(bead)
    return [('layer_height', '0.4'), ('wall_loops', '2'), ('outer_wall_line_width', f), ('inner_wall_line_width', f),
            ('outer_wall_speed', '60'), ('inner_wall_speed', '60'), ('internal_solid_infill_speed', '200'),
            ('top_surface_speed', '60'), ('outer_wall_acceleration', '5000'), ('inner_wall_acceleration', '5000'),
            ('seam_position', 'aligned'), ('bottom_surface_pattern', 'monotonic'), ('top_surface_pattern', 'monotonic'),
            ('internal_solid_infill_pattern', 'monotonic')]


if __name__ == '__main__':
    single = '--single' in sys.argv
    V, T, info = mesh()
    s = W.base(os.path.join(HERE, 'nurseryPots_settings_base.json')); s.update(lib.INSERT_SETTINGS_OVERRIDES)
    name = NAME + ('_single' if single else '')
    o = W.Obj(NAME, [W.Part(V, T)], settings=obj_settings(rev3.BEAD), at=[(128, 128)] if single else AT)
    path = W.write(os.path.join(HERE, name + '.3mf'), [o], s, plate_name=NAME.replace('_', ' ') + ' x4 (ceiling down)')
    print(dict(path=path, at=[tuple(round(c, 2) for c in a) for a in o.at], R=V3['R'], H=V3['H'],
               air_gap=V3['air_gap'], plastic_cm3=round(float(info['plastic_cm3']), 3)))
