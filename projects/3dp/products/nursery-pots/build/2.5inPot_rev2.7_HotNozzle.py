#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.7_HotNozzle.3mf (nursery-pots, 3dp project): the rev2.2 two-pot plate (5 mm gap,
76 mm pitch, centered) with each pot cut flat at 40.68 mm (113 layers) as in rev2.5/rev2.6, and the
nozzle at 265 C instead of 260 C (first layer stays 250 C), to test whether more heat fixes the
grainy patch right of the seam that plates leave (the patch follows the time between layers at the
seam; rev2.5, rev2.6).

Settings (agreed 2026-10-02): filament 1 nozzle temperature 260 -> 265 C (both extruder-variant
entries), first layer 250 C; z-hop 0.6 mm and retraction 0.8 mm as rev2.2; no extra length on
restart; minimum layer time 8 s. JAYO lists 220-250 C for its PETG; 265 C is outside that range.
Needs beside it: 2.5inPot_rev2.5_LayerTimeTest.py, 2.5inPot_rev2.2_SeamTest.py,
2.5inPot_rev2.1_Full.py, 2.5inPot_rev2.py, nurseryPots_lib.py and nurseryPots_settings_base.json
(all used unchanged).
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('layertime', os.path.join(HERE, '2.5inPot_rev2.5_LayerTimeTest.py'))
lt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lt)
st, pot, lib = lt.st, lt.pot, lt.lib
full = st.full            # its POS is rev2.2's two positions

NAME = '2.5inPot_rev2.7_HotNozzle'
NOZZLE = 265


def overrides():
    o = st.overrides()   # z-hop 0.6, retraction 0.8
    base = json.load(open(os.path.join(HERE, 'nurseryPots_settings_base.json')))
    nt = list(base['nozzle_temperature'])
    nt[0] = nt[1] = lib._fmt(NOZZLE)   # filament 1, Standard and High Flow variants
    o['nozzle_temperature'] = nt
    return o


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
    full.NAME = NAME
    pot.H = lt.Z_CUT     # add_instances places items at z = H/2
    full.add_instances(path)
    info['path'] = path
    info['instances'] = full.POS
    return info


if __name__ == '__main__':
    print(main())
