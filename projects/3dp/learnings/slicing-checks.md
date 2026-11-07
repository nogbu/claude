---
about: Slicing learnings: G-code checks, command-line slicing, test plates, filament profiles
read-when: before checking slices or test plates, or editing filament profiles
readonly: no
---
# learnings/slicing-checks

Slicing learnings moved unchanged from process-settings' Learnings (2026-10-07).

### Supports can block command-line slicing (learned 2026-10-01, rfid spring; 2026-10-02, calibration tests)
- With Enable support on, Orca 2.4.2's command-line slicer refused to slice a PETG HF file ("temperature difference of the filaments used is too large"). The support interface filament (filament 2, Bambu Support For PLA/PETG, 210 °C) counts as used even with Tree (manual) and nothing painted, and PETG HF prints at 245 °C.
- Fix: turn Enable support off in files with no painted supports; write3mf.py does it (2026-10-07).
- 2026-10-02: Orca's calibration test files fail the same way. pa_test (Bambu PETG Translucent) stops on the temperature error, and mvs_test, a spiral vase print, on "enable_support: Invalid value when spiral vase mode is enabled". Both come from Enable support being on in my process settings.
- 2026-10-10 (shelf, front fit test): the same refusal (return code -62) for a PETG Basic file with support painted on, since neither filament's temperature falls in the other's range (PETG Basic 255 °C, range 230–270; Bambu Support For PLA/PETG 210 °C, range 190–240). Setting support_interface_filament to 1 (the part's own PETG) with support_top_z_distance and support_bottom_z_distance 0.3 sliced; front-roof-fix_options.py does it.

### Never put two filament profiles with the same name in one file (learned 2026-09-28)
- Orca keeps only one set of edits per preset name. If a 3MF has two filaments that are both edited copies of the same preset (e.g. both "Bambu PETG Translucent @BBL X1C 0.8 nozzle" with different settings), only one keeps its edits. The other slot silently loads a different preset.
- On the pot this meant rev9.4 and rev9.5 printed with unknown filament settings instead of the intended test values, and conclusions drawn from them had to be withdrawn.
- Fix: one tuned filament per file, or give every edited profile a unique name; write3mf.py refuses two differently edited filaments under one name (2026-10-07). Check the filament list after opening: an edited profile shows an asterisk (*).

### Checking a slice in the G-code (learned 2026-10-01)
- Orca's G-code marks each layer with '; CHANGE_LAYER' and '; Z_HEIGHT:', each feature with '; FEATURE:' and each bead width with '; LINE_WIDTH:'. Parsing those gives every layer's bead count and width, wall speeds and the outer loop's start point (the seam), which catches bead flips and seam drift that the summary figures hide.
- To check gaps between parts, measure across the straight stretches and check that beads stay inside the model outline. A straight cut through the rounded end of a slot or hole reads as a false narrow gap, and a sliver between two wall beads inside a solid block isn't a gap between parts. The command-line slicer writes arcs (G2/G3) when arc fitting is on, so parse arcs (2026-10-01).
- Map G-code to the mesh by the extrusion bounds plus half a line width, never by the 3mf placement: Orca re-centers objects when it slices (2026-10-04). This supersedes the fixed 2.0 mm y offset added to G-code y before comparing toolpaths (2026-10-03): the rfid spring sat 2 mm off the plate center (2026-10-01), every pot sat 2 mm toward the front of its 3mf position (2026-10-02), and the rev1.1 strip and the photo board sat 2.0 mm further forward than Orca's plate coordinates (2026-10-03). Mapping by placement put false hits in barrinaClip rev1's hinge slot and notches (2026-10-04). For round parts, projects/3dp/scripts/gcodeTrace.py --fit-centers fits each part's center from its printed path (2026-10-06).
- Orca writes '; FEATURE:' only when the feature changes, so it carries over into later layers; track the current feature across layer changes. To estimate layer times from the G-code, use arc length for G2/G3 moves, not the chord (2026-10-01).
- To see where travel passes over a wall, sample each straight travel move along its length, not just its ends, and compare the nozzle height with the top of each object's last printed layer: a jump within a layer passes one hop (0.2 mm) above the object it just left, and a layer change passes hop plus layer height above the others (2026-10-02).
- projects/3dp/scripts/gcodeTrace.py runs these checks in one go: print order per layer, where travel passes over each wall near its seam and how high, seam offsets, and band speed, flow, loop starts and time between layers (2026-10-02).
- With several objects on one plate, the command-line slicer's result.json gave one floating-cantilever warning naming one object: front-fit-test_rev1's plate named only the 0.4 piece, though all three had the strip; sliced one per plate (rev1.1 to rev1.3), each was named (2026-10-10, shelf). Slice each distinct object on its own plate to see which carry a warning.

### A/B tests on one plate need separate objects (learned 2026-10-01)
- Instances of one object share its object settings and height ranges, so they can't compare two settings. Use a second object (a copy of the mesh) with its own settings. Plate-wide settings (filament, printer, most process settings) can't be A/B'd on one plate at all; each needs its own print.

### Color changes without a prime tower (learned 2026-10-02, calibration rig rev1.1)
- Each change purges at the chute. A change into black pushed out 76 mm (0.24 g) of black: the 140 mm³ flush plus the 18 mm reload after the cut. The change back into the body color pushed out 309 mm (0.98 g) at 700 mm³. The strip's 3 markers hold only 0.12 g of black.
- Orca's filament total leaves part of the purge out: 0.36 g of black for the strip, against 0.60 g extruded in its G-code. When a filament is short, count it from the G-code.
- Orca estimated 23 min 50 s for the strip, 17 min 53 s of it printing the model; start-up and the 3 color changes take the rest. My hand guess of about 15 min was far off, so quote print times from a slice.

### Orca's max volumetric speed test brim (learned 2026-10-05, calibration stand)
- Orca 2.4.2 sets the test's brim on the object (src/slic3r/GUI/Plater.cpp, calib_max_vol_speed): outer and inner, 5 mm wide, 0 gap. The project settings still read no_brim. Measured in my mvs_test.gcode.3mf: one 0.3 layer of 0.62 lines, outer edge 4.63 past the first-layer wall and 4.47 past the 1.05 walls above.
- A .gcode.3mf holds its G-code at Metadata/plate_N.gcode, so toolpaths can be measured without slicing.

### Check the tested setting against earlier prints (learned 2026-10-09, nursery-pots rough ceiling)
- Before building a one-change slicer test, run projects/3dp/scripts/settingsdiff.py between the new file and every earlier print of the same problem, at the height in question. rev2.5 tested a Monotonic top that 6in insert rev2 and rev2.1 had already printed with (build_insert sets it as an object setting), rough both times.
