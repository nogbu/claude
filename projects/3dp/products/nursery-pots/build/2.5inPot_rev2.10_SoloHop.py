#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.10_SoloHop.3mf (nursery-pots, 3dp project): rev2.6_SoloControl
(one 2.5in rev2 pot alone at the bed center, cut flat at 40.68 mm, rev2's settings) with one
setting changed, to test whether the 0.6 mm z-hop causes the grainy patch right of the seam
seen on every plate print (rev2.2-rev2.5, rev2.7, rev2.8), and whether 0.6 mm hop alone is
safe to keep for the plates' far-side zits.

Only change from rev2.6 (agreed 2026-10-02): filament z-hop 0.2 -> 0.6 mm (filament_z_hop,
filament 1, still Spiral Lift). Retraction stays 0.4 mm, minimum layer time stays 8 s, no extra
length on restart, pressure advance off.
In the rev2.5 vs rev2.6 G-code the spiral lift's radius grows from 0.61 to 1.83 mm with the
0.6 mm hop, and the nozzle drops 0.6 instead of 0.2 mm onto each loop's start point.

Needs beside it: 2.5inPot_rev2.6_SoloControl.py, 2.5inPot_rev2.5_LayerTimeTest.py,
2.5inPot_rev2.2_SeamTest.py, 2.5inPot_rev2.1_Full.py, 2.5inPot_rev2.py, nurseryPots_lib.py and
nurseryPots_settings_base.json (all used unchanged).
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('solocontrol', os.path.join(HERE, '2.5inPot_rev2.6_SoloControl.py'))
sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sc)
lt, pot, lib = sc.lt, sc.pot, sc.lib

NAME = '2.5inPot_rev2.10_SoloHop'
Z_HOP = 0.6               # mm, filament 1 (rev2.6: 0.2)


def overrides():
    base = json.load(open(os.path.join(HERE, 'nurseryPots_settings_base.json')))
    zh = list(base['filament_z_hop']); zh[0] = lib._fmt(Z_HOP)
    return {'filament_z_hop': zh}


def main(out_dir='.'):
    M, info = lt.build_mesh_cut()
    painted = lib.paint_seam(M, pot.PAINT_SPAN)
    info['painted_triangles'] = int(painted.sum())
    obj = lib.POT_OBJECT_SETTINGS + [('outer_wall_speed', lib._fmt(pot.OUTER_WALL_SPEED)),
                                     ('outer_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH)),
                                     ('inner_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH))]
    path = os.path.join(out_dir, NAME + '.3mf')
    lib.write_3mf(path, M, NAME, lt.Z_CUT, painted, obj, pot.layer_ranges(), overrides(),
                  fan_ramp=False, plate_name=NAME.replace('_', ' '))
    pot.replace_entry(path, 'Metadata/custom_gcode_per_layer.xml', pot.fan_ramp_xml())
    info['path'] = path
    return info


if __name__ == '__main__':
    print(main())
