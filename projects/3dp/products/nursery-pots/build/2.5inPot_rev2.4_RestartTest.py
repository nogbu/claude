#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.4_RestartTest.3mf (nursery-pots, 3dp project): rev2.2_SeamTest (two
2.5in rev2 pots, 5 mm gap; filament z-hop 0.6 mm, retraction 0.8 mm) plus 0.1 mm extra length
on restart (filament_retract_restart_extra), to test whether the grainy patch at the start of
each loop on plates comes from plastic oozing during the jump between pots.
Background: the speed A/B (rev2.3_SpeedAB) ruled out wall speed; both pots had the patch.
Needs beside it: 2.5inPot_rev2.py, 2.5inPot_rev2.1_Full.py, 2.5inPot_rev2.2_SeamTest.py,
nurseryPots_lib.py and nurseryPots_settings_base.json (all used unchanged).
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('seamtest', os.path.join(HERE, '2.5inPot_rev2.2_SeamTest.py'))
st = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(st)
full, pot, lib = st.full, st.pot, st.lib

NAME = '2.5inPot_rev2.4_RestartTest'
RESTART_EXTRA = 0.1
_base_overrides = st.overrides


def overrides():
    o = _base_overrides()
    base = json.load(open(os.path.join(HERE, 'nurseryPots_settings_base.json')))
    rx = list(base['filament_retract_restart_extra']); rx[0] = lib._fmt(RESTART_EXTRA)
    o['filament_retract_restart_extra'] = rx
    return o


def main(out_dir='.'):
    st.NAME = NAME
    full.NAME = NAME
    st.overrides = overrides
    return st.main(out_dir)


if __name__ == '__main__':
    print(main())
