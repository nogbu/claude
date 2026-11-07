#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.6_SoloControl.3mf (nursery-pots, 3dp project): one 2.5in rev2 pot alone at
rev2's original settings, cut flat at 40.68 mm (113 layers) like rev2.5, as the control for the
grainy patch right of the seam. rev2 had only been printed on plates (rev2.1-rev2.4) and in rev2.5
(16 s minimum layer time, walls about 12 mm/s, 0.6/0.8 mm hop/retraction), and rev2.5 still showed
the patch with no jump between pots.

Settings: rev2's, unchanged (agreed 2026-10-01): minimum layer time 8 s, filament z-hop 0.2 mm,
retraction 0.4 mm, no extra length on restart. Mesh: rev2.5's (rev2 cut at 40.68 mm, flat top).
Needs beside it: 2.5inPot_rev2.5_LayerTimeTest.py, 2.5inPot_rev2.2_SeamTest.py,
2.5inPot_rev2.1_Full.py, 2.5inPot_rev2.py, nurseryPots_lib.py and nurseryPots_settings_base.json
(all used unchanged).
"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('layertime', os.path.join(HERE, '2.5inPot_rev2.5_LayerTimeTest.py'))
lt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lt)
pot, lib = lt.pot, lt.lib

NAME = '2.5inPot_rev2.6_SoloControl'


def main(out_dir='.'):
    M, info = lt.build_mesh_cut()
    painted = lib.paint_seam(M, pot.PAINT_SPAN)
    info['painted_triangles'] = int(painted.sum())
    obj = lib.POT_OBJECT_SETTINGS + [('outer_wall_speed', lib._fmt(pot.OUTER_WALL_SPEED)),
                                     ('outer_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH)),
                                     ('inner_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH))]
    path = os.path.join(out_dir, NAME + '.3mf')
    lib.write_3mf(path, M, NAME, lt.Z_CUT, painted, obj, pot.layer_ranges(), {},
                  fan_ramp=False, plate_name=NAME.replace('_', ' '))
    pot.replace_entry(path, 'Metadata/custom_gcode_per_layer.xml', pot.fan_ramp_xml())
    info['path'] = path
    return info


if __name__ == '__main__':
    print(main())
