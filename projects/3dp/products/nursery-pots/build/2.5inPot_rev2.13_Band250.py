#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.13_Band250.3mf (nursery-pots, 3dp project): rev2.9_SoloRetract (one 2.5in
rev2 pot alone at the bed center, cut flat at 40.68 mm, 0.2 mm z-hop, 0.8 mm retraction, 260 C,
8 s minimum layer time, pressure advance off) with the slot band printed at 250 C, to test whether
nozzle temperature drives the slot-band bubbles (rev2.7 at 265 C frosted the band more).

Only change from rev2.9 (agreed 2026-10-02): two temperature commands added to the printer's
layer-change G-code (layer_change_gcode), each conditional on the layer number (layer_num counts
from 0, so layer N is layer_num N - 1):
- M104 S250 at the start of layer 64 (22.68-23.04 mm), the first layer with slots. M104 doesn't
  wait, so the first slot layer or so prints while the nozzle cools. The waterline layer below
  (layer 63, 22.32-22.68 mm, two-bead, seam gap 0%, flow 1.03) stays at 260 C.
- M104 S260 at the start of layer 86 (30.60-30.96 mm), the band's top two-bead ring, which prints
  while the nozzle reheats, so the single-bead walls from layer 87 print at 260 C as in rev2.9.
Why the layer-change G-code instead of the layer slider's custom G-code: the command-line slicer
keeps it, so the sliced G-code can be checked against rev2.9 before printing (the fan ramp is
layer-slider G-code, which the command-line slicer drops; check it in Orca's preview).
layer_change_gcode is also added to the printer settings' list of changes (different_settings_to_system).

Needs beside it (all used unchanged): 2.5inPot_rev2.9_SoloRetract.py, 2.5inPot_rev2.6_SoloControl.py,
2.5inPot_rev2.5_LayerTimeTest.py, 2.5inPot_rev2.2_SeamTest.py, 2.5inPot_rev2.1_Full.py,
2.5inPot_rev2.py, nurseryPots_lib.py and nurseryPots_settings_base.json.
Run: python3 2.5inPot_rev2.13_Band250.py (needs numpy, scipy, matplotlib).
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('soloretract', os.path.join(HERE, '2.5inPot_rev2.9_SoloRetract.py'))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)
lt, pot, lib = sr.lt, sr.pot, sr.lib

NAME = '2.5inPot_rev2.13_Band250'
BAND_TEMP = 250          # C, slot band (layers 64-85)
WALL_TEMP = 260          # C, filament 1 nozzle temperature, restored for layer 86 up
DROP_LAYER = 64          # 1-based layer numbers, as Orca's layer slider shows them
RETURN_LAYER = 86
L = 0.36
assert abs((DROP_LAYER - 1) * L - pot.Z_SB) < 1e-6        # layer 64 starts at the slot bottom, 22.68 mm
assert abs((RETURN_LAYER - 1) * L - pot.Z_ST) < 1e-6      # layer 86 starts at the slot top, 30.60 mm

# Appended to the last line of the layer-change G-code, with each newline inside its branch, so
# every other layer's G-code stays byte-identical to rev2.9's (no blank lines added).
BAND_GCODE = ('{if layer_num == %d}\nM104 S%d ; rev2.13: slot band at %d C'
              '{elsif layer_num == %d}\nM104 S%d ; rev2.13: back to %d C'
              '{endif}' % (DROP_LAYER - 1, BAND_TEMP, BAND_TEMP,
                           RETURN_LAYER - 1, WALL_TEMP, WALL_TEMP))


def overrides():
    o = sr.overrides()                    # rev2.9: filament retraction 0.8 mm
    base = json.load(open(os.path.join(HERE, 'nurseryPots_settings_base.json')))
    assert base['nozzle_temperature'][0] == str(WALL_TEMP)
    o['layer_change_gcode'] = base['layer_change_gcode'] + BAND_GCODE
    diff = list(base['different_settings_to_system'])
    keys = set(k for k in diff[3].split(';') if k)   # printer settings
    keys.add('layer_change_gcode')
    diff[3] = ';'.join(sorted(keys))
    o['different_settings_to_system'] = diff
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
    info['path'] = path
    return info


if __name__ == '__main__':
    print(main())
