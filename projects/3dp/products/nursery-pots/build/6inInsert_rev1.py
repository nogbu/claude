#!/usr/bin/env python3
"""Builds 6inInsert_rev1.3mf (nursery-pots, 3dp project), printed ceiling-down.
Needs nurseryPots_lib.py and nurseryPots_settings_base.json beside it.
Features scaled x1.786 from 3.5inInsert_rev4 except the 4 mm holes (two per diagonal)
and the notch height (nearest 0.4 mm layer). Values from nursery-pots state.md."""
from nurseryPots_lib import build_insert
info = build_insert(name='6inInsert_rev1', R=52.075, t=1.2, H=46.4, T=1.6, c=5.36,
                    slot_w=3.57, slot_r0=11.52, slot_r1=39.66, hole_radii=[18.83, 37.66],
                    notch_w=3.57, notch_d=18.0, bead=0.64)
print(info)
