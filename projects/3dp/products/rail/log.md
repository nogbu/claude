---
about: Parked and superseded rail material, newest first
read-when: before building it, at an item's trigger, or for a value state.md lacks
readonly: no
---
# rail log

## Dovetail groove, slot-fit test piece (alternative; 2026-10-09; back if the bar is ever printed groove-up)

- Replaced by the hook groove: printed on its side, the bar's upper dovetail lip started in midair (Orca: floating regions; images/rail_slotFit_lip.png, concepts/rail_slotfit_lip.py). Geometry: build/concepts/rail_slottest.py, which slotFit_rev1 first built unchanged. Text moved from state.md as it stood:  
- Latest rev: Slot-fit test piece designed 2026-10-09, not built: build/concepts/rail_slottest.py (pictures: rail_slottest_pics.py; images/rail_slotTest_parts.png, images/rail_slotTest_mounted.png).  
- Slot-fit test piece, anchors: Anchors (3): neck 1.6 × 1.6, drop 2.0 thick; hook 3.0 / 3.3 / 3.6 tall (drop 1.4 / 1.7 / 2.0 below the neck), marked by 1 / 2 / 3 V notches on the head's front. Width 7.8 (26 layers; 0.45 per side in the slot). Head 2.8 deep, trapezoid dovetail: 5.4 wide at the strip face, 45° out to 7.8 at 1.2 deep (a hexagon head would start as a 0.4 sliver on the bed).  
- Slot-fit test piece, groove bar: Groove bar: rail section 16.8 wide (56 layers) × 16 deep × 75 long. Groove sides 8.4 apart and bottom 3.1 deep (0.3 clear; they don't set the fit); 45° faces at an in-layer gap of 0.5 / 0.3 / 0.2 in 25 mm zones from the beveled end, 1 mm ramps between, V marks on the front at 25 and 50, 0.9 lead-ins. Bottom corners: 45° fill on the ceiling side, r0.6 on the floor side. No button relief.  
- Slot-fit test piece, printing: Printing: on their side like the final parts (cabinet X up), so hook profiles and marks are in the layer outline and hook loads run along the layers. About 12 g and half an hour (inference from volume).  
- Slot-fit test piece, dpcheck: dpcheck (2026-10-09, scratch STL): plate, overhangs and supports pass; the groove ceiling is a 1.5 mm hidden bridge with 0.3 sag room; the other flags are the dp exceptions below. Report: /mnt/project-files/reports/rail_slotTest_dpcheck.txt.  
- dp exceptions: Slot-fit test piece: fit faces sharp (dovetail faces and lips; the anchor's neck, throat and neck-top corners, which seat on the slot edge). Drop's bottom-front corner r0.7 (bearing face). Anchor top fillet 0.6 and bed chamfer 0.3: bigger ones thin the 1.6 neck band below a bead. Lips at 0.2 and 0.5 end between layers (5.2, 5.5, 11.3, 11.6); each layer's gap is exact, and on the grid only 0.3 steps fit. A 45° lip's first layers print under a bead; the test shows the effect. Lead-ins, ramps, marks and notches stay sharp to work and read.  
- dp trials: 2026-10-09, design principle 5: the groove's width runs in Z on the side-printed rail, so the fit is set by the 45° faces' in-layer gap (X-Y) and the groove's sides and bottom are held 0.3 clear.

## Braced clip (alternative; 2026-10-09; back if a clip ever gets two open sides)

- Concept A's first clip: plate 3 thick × 30 tall, ledge 15 deep × 5 thick, a solid brace from the ledge tip down to the plate bottom, tongue and pocket hook as now. With the side glass flush against the rail, the brace left nothing to pinch, so the plain-ledge clip replaced it. Without the brace, a 3 plate would see about 88 MPa (inference, clip_stress()).

## Height clips, concept C (alternative; 2026-10-09; back if the rail column is dropped)

- No rail: each shelf corner gets a one-piece clip, a 6 thick plate on the strip with a load hook in one slot and a keeper hook (0.3 slack) one pitch below, and its ledge at any height, hanging below or standing above the slots. 4 parts per shelf, strips stay clear. Hook neck 1.6 × 8: about 16 MPa at the design load (inference). Moving a shelf means printing new clips. Model: build_C() in build/concepts/rail_concepts.py.

## Stacked layout with built-in hooks (alternative; superseded 2026-10-09 by layout A; back if the anchors fail the slot test)

- Moved unchanged from state.md; its open questions and agreed changes follow.

### Key parameters and dimensions

A printed black PETG rail on each of the 4 slotted strips, giving shelf clip positions every 2" from 6" to 52" above the floor (24 positions, 152.4 to 1320.8 mm). Target load 40 lb per shelf, safety factor 3, assuming 75% of the load on the front two rails.

**Requirement: no external hardware.** No magnets or other bought components as part of rail/clip designs; everything is printed.

### Layout: stacked from the floor, 6 pieces per corner

The floor carries the weight through the stack; hooks only hold the rail against the steel.

| # | Piece | From → to (mm) | Length | Prints | Features |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 1 | Bottom | 0 → 234.6 | 234.6 | Straight | Stands on floor |
| 2 | Lower hooked | 234.6 → 437.8 | 203.2 | Straight | Hooks at 322/355/388, button notch at 260 |
| 3 | Spacer | 437.8 → 590.2 | 152.4 | Straight | None |
| 4 | Middle hooked | 590.2 → 844.2 | 254.0 | Diagonal | Hooks at 687/721/755, button notch at 626 |
| 5 | Spacer | 844.2 → 1047.4 | 203.2 | Straight | Button notch at 996 |
| 6 | Upper hooked + top | 1047.4 → 1340 | 292.6 | Diagonal | Hooks in the top two slots (1090/1121, top edges); top button about 10.75 mm above the piece's top for lift-off (button center 1359, 16.5 mm tall, photos 020238, 020620; inference) |

- Table hook heights are slot top edges (unicoly, ±7 mm until confirmed), not slot centers.  
- Diagonal prints: turn the skirt off.  
- Pieces with button notches come in left/right mirror versions.  
- Bottom piece and spacers designed 1.5 mm short; printed shims (0.5 mm steps) under each hooked piece take up tolerance.  
- Install bottom-up; remove top-down. Hooked pieces come off by lifting 1.5 mm and pulling forward.

### Rail section and hook

- Rail 17.0 mm wide × 10 mm deep, centered on the strip. Prints lying on its side, no supports.  
- Hook: 8.5 mm wide, shank 1.8 mm tall, drop 1.6 mm (lip behind the steel), drop 2.0 mm thick, 0.5 mm lead-in chamfers, 45° chamfer under the hook (supportless). Total height 3.4 mm fits the 4 mm slot, so the drop can only be about 1.6 mm. Photos read the slot at 3.3–3.7 mm (unicoly); at 3.3 the 3.4 mm hook doesn't fit; confirm the slot height with a pass/fail piece before the hooks are final.  
- **Gap from rail back face to hook drop: 1.5 mm** (inference: chosen between the 1.3 mm gauge, which won't go in, and the 1.6 mm gauge, which wiggles slightly; not yet printed or tested).  

### Joints

- Under each hooked piece: slide joint (tongue open to the front) so the piece can lift 1.5 mm and pull forward.  
- Under spacers: pin tenon, 4.5 mm, chamfered, 0.3 mm clearance. **Candidate replacement: snap tenon** (log: Snap tenon joint).

### Shelf clip

- Tongue 4 mm deep × 12 mm tall into a notch in the rail's front face, leaving 6 mm of rail behind each notch.  
- Ledge 15 mm deep × 17 mm wide × 5 mm thick, plain flat top (no TPU pad). Ledge top = shelf height.  
- Diagonal brace down to about 20 mm below the ledge, bearing on the rail face. Small detent bump on the tongue.  
- Prints on its side. For the factory shelves. The wire shelf rests on the stock clips instead (shelf, agreed change 10).

### Shelf cutouts

- Every shelf gets a 19 mm (inward from the side edge) × 12 mm (from the strip face plane) cutout at each corner, with a 3 mm inside radius. Leaves about 3.25 mm beside the rail with the shelf centered, 2 mm in front.  
- Install shelves bottom-up: set the clips, then lower the shelf onto them.  
- Rocking: level with the cabinet's threaded feet first, then shims under a hooked piece.

### Open questions / next steps

1. Slot pitch is 34.8 ± 0.3 by ruler (unicoly, photos 144310 and 144342). Pending question (2026-10-01): to get inside ±0.3 and settle hook spacing, print a pass/fail comb (recommended: pins at 34.0 / 34.5 / 35.0 / 35.5 mm, no photo or math) or photograph slotGuide rev2 beside a group?  
2. Test piece: lower hooked piece + one clip + shims. Hang it, then measure its height above the floor and print the bottom piece to that.  
3. Pin tenon vs snap tenon under spacers.  
4. The rail covers the slotted strips, so stock clips can't be used where a rail is installed (inference). A wire shelf on stock clips and the rail system can't share a cabinet unless the wire shelf also gets rail cutouts.  
5. Removal lift vs. hook drop: 1.5 mm lift < 1.6 mm drop. Lift must be 1.6 to (slot height − 1.8 mm shank): 1.6–2.2 in a 4 mm slot, 1.6–1.8 in a 3.6 mm slot, none in a 3.3 mm slot (inference). Affects the slide joint, the "1.5 mm short" rule and the button notch heights. Candidate fix (2026-10-03, not chosen; pending question: which hook and lift): shank 1.6 + drop 1.2 (total 3.0), lift stays 1.5. Fits 3.3–4.0 slots with ≥0.2 mm margin; keeps both. Strength unchecked: needs hook pull-out from the rail geometry and sourced PETG strength across/along layers per print orientation (inference).  
6. Hook size and placement: a 3.4 × 8.5 mm hook in a 3.3–4 × 8.7–9 mm slot may not fit at all, so ±0.3 pitch error can bind the outer hooks (inference). Hooks only hold the rail against the steel, so a smaller hook could buy tolerance; the stock clip tab is 8.1–8.4 wide (photo 151418). The slot sits about 0.75 mm off the strip center toward the fold (photo 144342, low confidence), so place hooks on the slot, not the rail center (inference).  
7. Rail width: 17.0 mm rail vs. a 16.6–17.6 mm strip (photos 144310, 144342); settle the strip width before fixing the rail width.  
8. Spacer lengths: slot heights are ±7 mm until confirmed (unicoly; photo 020416), more than the 1.5 mm-short design and 0.5 mm shims cover (inference). Consider printing spacers 3 and 5 to measured gaps, as open question 2 does for the bottom piece.  
9. Button notch depth: how far the glass buttons stand off the strip face isn't measured. Notch height = 16.5 mm + removal lift + clearance (inference).  
10. Clip notches at 10" (254 mm) and 40" (1016 mm) come within 0–2 mm of the button notches (buttons 251.75–268.25 and 987.75–1004.25); where they overlap, rail thickness is 10 − 4 − button notch depth (inference).  
11. Front-to-rear strip face distance isn't measured; the shelf cutout's 2 mm front clearance assumes the shelf edge sits at the strip face (inference).

### Agreed changes

1. slotGuide rev2: make it black-only for the Brother HL-L2390DW. Mark every 10th band as half black and half white across the strip instead of red. Add a no-tools scale check: lay a bank card (85.60 mm wide, a fixed ISO size) flat beside a check bar and photograph it.  
2. Hook spacing within a hooked piece is 34.8 mm (unicoly slot pitch), not 33. Pieces 2 and 4 center their three hooks on the group's middle slot (355 and 721, top edges). Piece 6's two hooks sit in the top two slots, at 1090 and 1124.8 (top edges; 1090 + 34.8, inference). The layout table's 1121 is the tape value, within its ±7 mm. Errors in those heights move the piece as a whole (see open question 2).


## Snap tenon joint (parked; staged 2026-10-07; back if snap tenon chosen)

- **Snap tenon joint (my design, saved for later).** For joints where a spacer drops onto the hooked piece below it (2→3 and 4→5). It can't go under a hooked piece, which only moves 1.5 mm vertically.  
  - The hooked piece's top has a tenon 6 mm deep × 11 mm wide × 20 mm long.  
  - A slit in the tenon makes a spring arm on its front side, 1.6 mm thick and 14 mm long, carrying a catch that sticks out 1.0 mm, with a ramp on top and a square face below.  
  - The spacer's bottom has a socket 6.4 × 11.4 mm, 20.4 mm deep, with a 4 × 7 mm window in its front wall.  
  - As the spacer drops on, the ramp pushes the catch in; it then springs into the window, and the window's lower edge holds the square face so the spacer can't lift off.  
  - Release: press the catch through the window with a pen tip, then lift the spacer.  
  - The catch and window are on the front because that's the only face reachable once installed. Arm strain about 1% at snap-in, fine for PETG; the arm prints along the layers.

## Hook gap and pitch derivation (history; staged 2026-10-07; back if hook gap reopened)

- Supported by the stock clip: its fold's inside gap, which wraps the strip's steel, is about 1.5 mm (photo 151317, ±0.5).  
- Three hooks in 4 mm slots tolerate only about ±0.3 mm of pitch error (hook 3.4 mm tall), so hook spacing needs a precise pitch measurement (inference). Measured 2026-09-30: 34.8 ± 0.3 mm by ruler (unicoly).

## Rejected rail alternatives (alternative; staged 2026-10-07; back if stacked layout dropped)

- **Splice (lap) joints rejected**: each tongue is half the 10 mm depth, so about 4× the bending stress.  
- **openGrid rail rejected**: 28 mm column is too wide for the 17.5 mm strip, snap loads untested for shelves, wrong print orientation, 28 mm pitch fights the joint layout. openGrid could suit the magnetic steel back wall as a separate accessory project (official files are CC-BY; some community generators are non-commercial).

## Test print results (history; staged 2026-10-07; back if retesting gauges)

* hookGauge_rev1: 4 stubs, one hook each, gaps 1.0 / 1.3 / 1.6 / 2.0 mm, marked by 1–4 ribs (files named hook_gauge_\*rib_G\*.stl, built before the naming rule). Result: 1.0 and 1.3 won't go in; 1.6 fits with the least wiggle; 2.0 fits loosely.  
* slotGuide_rev1.pdf: US Letter paper scale for measuring slot pitch from a photo. Six 120 mm strips (two each 3.0 / 3.5 / 4.0 mm wide), 1 mm black/white bands with every 10th band red, and 100 mm check bars across and down.  
