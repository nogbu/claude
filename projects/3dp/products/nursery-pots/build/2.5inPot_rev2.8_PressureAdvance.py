#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.8_PressureAdvance.3mf (nursery-pots, 3dp project): the rev2.2 two-pot plate (5 mm
gap, 76 mm pitch, centered), each pot cut flat at 40.68 mm (113 layers) as in rev2.5-rev2.7, with
pressure advance turned on at 0.04 for filament 1, to test whether the grainy patch right of the
seam on plates comes from how the extruder restarts each loop.

Settings (agreed 2026-10-02): enable_pressure_advance on and pressure_advance 0.04 for filament 1
(Orca PA Pattern test on JAYO PETG, 0-0.08 step 0.005, chevron 9 sharpest); nozzle 260 C, first
layer 250 C; z-hop 0.6 mm and retraction 0.8 mm as rev2.2; no extra length on restart; minimum
layer time 8 s.
Needs beside it: 2.5inPot_rev2.7_HotNozzle.py, 2.5inPot_rev2.5_LayerTimeTest.py,
2.5inPot_rev2.2_SeamTest.py, 2.5inPot_rev2.1_Full.py, 2.5inPot_rev2.py, nurseryPots_lib.py and
nurseryPots_settings_base.json (all used unchanged).
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('hotnozzle', os.path.join(HERE, '2.5inPot_rev2.7_HotNozzle.py'))
hn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hn)
lt, st, lib = hn.lt, hn.st, hn.lib

NAME = '2.5inPot_rev2.8_PressureAdvance'
PA = 0.04


def overrides():
    o = st.overrides()   # z-hop 0.6, retraction 0.8; nozzle stays 260
    base = json.load(open(os.path.join(HERE, 'nurseryPots_settings_base.json')))
    en = list(base['enable_pressure_advance']); en[0] = '1'
    pa = list(base['pressure_advance']); pa[0] = lib._fmt(PA)
    o['enable_pressure_advance'] = en
    o['pressure_advance'] = pa
    return o


def main(out_dir='.'):
    hn.NAME = NAME
    hn.overrides = overrides
    return hn.main(out_dir)


if __name__ == '__main__':
    print(main())
