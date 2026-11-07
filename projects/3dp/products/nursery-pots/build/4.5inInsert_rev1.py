#!/usr/bin/env python3
"""Builds 4.5inInsert_rev1.3mf (nursery-pots, 3dp project), printed ceiling-down.
Needs nurseryPots_lib.py and nurseryPots_settings_base.json beside it.
Features scaled x1.387 from 3.5inInsert_rev4 except the 4 mm holes and the notch
height (nearest 0.4 mm layer). Values from nursery-pots state.md."""
from nurseryPots_lib import build_insert
info = build_insert(name='4.5inInsert_rev1', R=40.425, t=1.0, H=41.2, T=1.2, c=4.16,
                    slot_w=2.77, slot_r0=8.95, slot_r1=30.79, hole_radii=[19.87],
                    notch_w=2.77, notch_d=14.0, bead=0.54)
print(info)
