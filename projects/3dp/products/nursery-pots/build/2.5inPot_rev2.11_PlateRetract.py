#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.11_PlateRetract.3mf (nursery-pots, 3dp project): rev2.9_SoloRetract's pot
(2.5in rev2 cut flat at 40.68 mm; 0.2 mm z-hop, 0.8 mm retraction, rev2's other settings) as a
two-pot plate, to check whether plates print a clean seam once the 0.6 mm hop is gone.

Only change from rev2.9 (agreed 2026-10-02): two instances side by side with a 5 mm gap (76 mm
pitch), centered on the bed, as rev2.2_SeamTest. Settings stay rev2.9's: 260 C, pressure advance
off, minimum layer time 8 s, z-hop 0.2 mm Spiral Lift, retraction 0.8 mm.
Why: rev2.10_SoloHop showed the 0.6 mm hop alone brings the plate seam patch back on a solo pot,
and rev2.9 showed 0.8 mm retraction alone leaves it clean.
Copies seen from the front of the printer: copy 1 left, copy 2 right.

Needs beside it: 2.5inPot_rev2.9_SoloRetract.py, 2.5inPot_rev2.6_SoloControl.py,
2.5inPot_rev2.5_LayerTimeTest.py, 2.5inPot_rev2.2_SeamTest.py, 2.5inPot_rev2.1_Full.py,
2.5inPot_rev2.py, nurseryPots_lib.py and nurseryPots_settings_base.json (all used unchanged).
"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(mod, fname):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


sr = _load('soloretract', '2.5inPot_rev2.9_SoloRetract.py')
full = _load('pot_full', '2.5inPot_rev2.1_Full.py')
lt, pot, lib = sr.lt, sr.pot, sr.lib

NAME = '2.5inPot_rev2.11_PlateRetract'
POS = [(full.CENTER - full.PITCH / 2, full.CENTER), (full.CENTER + full.PITCH / 2, full.CENTER)]


def add_instances(path):
    """rev2.1_Full's instancing, with the build height of the cut pot (40.68 mm) instead of the
    full pot's."""
    full.NAME, full.POS = NAME, POS
    full_h = full.pot.H
    full.pot.H = lt.Z_CUT
    try:
        full.add_instances(path)
    finally:
        full.pot.H = full_h


def main(out_dir='.'):
    M, info = lt.build_mesh_cut()
    painted = lib.paint_seam(M, pot.PAINT_SPAN)
    info['painted_triangles'] = int(painted.sum())
    obj = lib.POT_OBJECT_SETTINGS + [('outer_wall_speed', lib._fmt(pot.OUTER_WALL_SPEED)),
                                     ('outer_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH)),
                                     ('inner_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH))]
    path = os.path.join(out_dir, NAME + '.3mf')
    lib.write_3mf(path, M, NAME, lt.Z_CUT, painted, obj, pot.layer_ranges(), sr.overrides(),
                  fan_ramp=False, plate_name=NAME.replace('_', ' '))
    pot.replace_entry(path, 'Metadata/custom_gcode_per_layer.xml', pot.fan_ramp_xml())
    add_instances(path)
    info['path'] = path
    info['instances'] = POS
    return info


if __name__ == '__main__':
    print(main())
