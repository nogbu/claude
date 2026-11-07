#!/usr/bin/env python3
"""Builds 3.5inPot_rev10.2.3mf (nursery-pots, 3dp project).
Needs nurseryPots_lib.py and nurseryPots_settings_base.json beside it.
Values from nursery-pots state.md (size table, Shared design, Geometry, agreed changes)."""
from nurseryPots_lib import build_pot
info = build_pot(name='3.5inPot_rev10.2', H=105.12, R_lip=48.07, t=1.00, floor=1.80,
                 slot_w=1.5, z_sb=33.48, z_st=41.40, band_bead=0.54, outer_wall_speed=34,
                 wall_line_width=1.05, paint_span=(87.5, 90.5))
print(info)
