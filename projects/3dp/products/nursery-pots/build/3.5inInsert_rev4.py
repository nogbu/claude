#!/usr/bin/env python3
"""Builds 3.5inInsert_rev4.3mf (nursery-pots, 3dp project), printed ceiling-down.
Needs nurseryPots_lib.py and nurseryPots_settings_base.json beside it.
Values from nursery-pots state.md (Insert bullets, Geometry, agreed changes)."""
from nurseryPots_lib import build_insert
info = build_insert(name='3.5inInsert_rev4', R=29.15, t=1.0, H=36.0, T=1.2, c=3.0,
                    slot_w=2.0, slot_r0=6.45, slot_r1=22.2, hole_radii=[14.33],
                    notch_w=2.0, notch_d=10.0, bead=0.54)
print(info)
