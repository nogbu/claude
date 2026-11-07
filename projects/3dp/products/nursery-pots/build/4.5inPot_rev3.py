#!/usr/bin/env python3
"""Builds 4.5inPot_rev3.3mf (nursery-pots, 3dp project).
Needs nurseryPots_lib.py and nurseryPots_settings_base.json beside it.
Values from nursery-pots state.md (size table, Shared design, Geometry, agreed changes)."""
from nurseryPots_lib import build_pot
info = build_pot(name='4.5inPot_rev3', H=129.96, R_lip=61.125, t=1.00, floor=1.80,
                 slot_w=2.0, z_sb=38.52, z_st=48.60, band_bead=0.54, outer_wall_speed=34,
                 wall_line_width=1.05, paint_span=(88.0, 90.5))
print(info)
