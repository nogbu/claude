#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.2_SeamTest.3mf (nursery-pots, 3dp project): 2 instances of the 2.5in
rev2 pot, side by side with a 5 mm gap (76 mm pitch), centered on the bed, to test the fix for
the bad seams and far-side zits on the 3 x 3 plate (2.5inPot_rev2.1_Full, printed 2026-10-01).

Only change from rev2.1_Full (filament overrides, project settings):
- Z-hop 0.2 -> 0.6 mm (filament_z_hop, still Spiral Lift)
- Retraction 0.4 -> 0.8 mm (filament_retraction_length)
Needs beside it: 2.5inPot_rev2.py, 2.5inPot_rev2.1_Full.py, nurseryPots_lib.py and
nurseryPots_settings_base.json (all used unchanged).
Copies seen from the front of the printer: copy 1 left, copy 2 right.
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(mod, fname):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


full = _load('pot_full', '2.5inPot_rev2.1_Full.py')
pot, lib = full.pot, full.lib

NAME = '2.5inPot_rev2.2_SeamTest'
Z_HOP = 0.6
RETRACT = 0.8
full.NAME = NAME
full.POS = [(full.CENTER - full.PITCH / 2, full.CENTER), (full.CENTER + full.PITCH / 2, full.CENTER)]


def overrides():
    base = json.load(open(os.path.join(HERE, 'nurseryPots_settings_base.json')))
    zh = list(base['filament_z_hop']); zh[0] = lib._fmt(Z_HOP)
    rl = list(base['filament_retraction_length']); rl[0] = lib._fmt(RETRACT)
    return {'filament_z_hop': zh, 'filament_retraction_length': rl}


def main(out_dir='.'):
    M, info = pot.build_mesh()
    painted = lib.paint_seam(M, pot.PAINT_SPAN)
    obj = lib.POT_OBJECT_SETTINGS + [('outer_wall_speed', lib._fmt(pot.OUTER_WALL_SPEED)),
                                     ('outer_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH)),
                                     ('inner_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH))]
    path = os.path.join(out_dir, NAME + '.3mf')
    lib.write_3mf(path, M, NAME, pot.H, painted, obj, pot.layer_ranges(), overrides(),
                  fan_ramp=False, plate_name=NAME.replace('_', ' '))
    pot.replace_entry(path, 'Metadata/custom_gcode_per_layer.xml', pot.fan_ramp_xml())
    full.add_instances(path)
    info['path'] = path
    info['instances'] = full.POS
    return info


if __name__ == '__main__':
    print(main())
