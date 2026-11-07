#!/usr/bin/env python3
"""Builds 6inInsert_rev2.6_PotMonoTop.3mf (nursery-pots, 3dp project): rev2.2_PotSettings (6in insert rev2's
ceiling cut at 1.08 mm, every 6in pot rev2 floor setting) with rev2.5_MonoTop's top surface pattern,
Monotonic, set as an object setting (the pot settings base uses Concentric). Nothing else changes from rev2.2
(asked 2026-10-09: "the same top and pot settings for the rest").
Needs beside it: nurseryPots_lib.py, nurseryPots_settings_base.json and 6inInsert_rev2.2_PotSettings.py; needs
trimesh and manifold3d.
"""
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = '6inInsert_rev2.6_PotMonoTop'
TOP_PATTERN = 'monotonic'       # rev2.5_MonoTop's top surface pattern

rev22 = runpy.run_path(os.path.join(HERE, '6inInsert_rev2.2_PotSettings.py'), run_name='rev22')   # also writes rev2.2
lib, C, obj = rev22['lib'], rev22['C'], dict(rev22['obj'])
obj['top_surface_pattern'] = TOP_PATTERN
path = os.path.join(HERE, NAME + '.3mf')
lib.write_3mf(path, C, NAME, rev22['Z_CUT'], rev22['np'].zeros(len(C.T), dtype=bool), sorted(obj.items()), [], {},
              fan_ramp=False, plate_name=NAME.replace('_', ' ') + ' (ceiling down)')
print(dict(path=path, top_surface_pattern=TOP_PATTERN))
