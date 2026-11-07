---
about: Parked and superseded photo-board material, newest first
read-when: before building it, at an item's trigger, or for a value state.md lacks
readonly: no
---
# photo-board log

## rev1, the test strip and replaced choices (history; staged 2026-10-07; back if: rev1 or the test strip is compared or rebuilt, or a replaced choice is reconsidered)
- Current state, Latest rev: Replaces rev1 (built 2026-10-03, never printed). Earlier, rev1.1, the marker test strip: built 2026-10-02, printed and photographed 2026-10-03 (staged, photo-board log).
- Current state, Parts: ; rev1's photoBoard_rev1.py, same folder, is superseded
- Plate fit: Shortened from 252 x 252 on 2026-10-03 (decision 11).
- Markers, inlay depth: (1 layer until 2026-10-03; decision 9)
- Decision 3: Replaces a Letter sheet sliding between the rails, with white paper for opaque pieces.
- Decision 5: Replaces raised markers at each piece's height (about 2 and 15 mm).
- Decision 9: , and a marker test strip before the full board
- Decision 13: ; no 2-layer test strip: the toolpath fill check predicts the fix and rev1.1's 1-layer markers all read with the tuned detector

## rev2 slice (history; staged 2026-10-07; back if: re-slicing rev2 or checking its print time, weight or inlay coverage)
- Sliced rev2 (Measured 2026-10-03 from the G-code, Orca 2.4.2 command line): 114 layers, 34.2 mm tall, about 3 h 02 m; 186.4 g of Bone White and 2.37 g of black (Orca's totals), about $4.72 at the preset price; 4 color changes, 2 of them into black (at 6.0 and 33.9 mm). All 25 markers decode from the sliced black paths, and the toolpath fill check shows 0.20 mm2 where white could show through the 2-layer inlay, with no speck larger than 0.3 x 0.3 mm.

## Test piece sizes (parked; staged 2026-10-07; back if: sizing the stand's camera height, placing a test piece, or adding a new test piece)
Test piece sizes (Measured 2026-10-02, from Orca 2.4.2's calibration models and the user's test files mvs_test.3mf, pa_test.gcode.3mf)  
- Temperature tower: 44.5 x 10 mm footprint, 10 mm per temperature step. Lies on its back: 44.5 wide x 10 per step long (about 100 mm for 220-265 C at 5 C steps, Estimated), face 10 mm above the board. Self-scaling: its 10 mm sections are a known size in the face's plane.  
- Max volumetric speed: single-wall E-shaped comb, 180 x 100 footprint, cut to 32 mm tall (mvs_test). Lies on its back edge: the 180 x 32 wall faces up about 100 mm above the board, the tallest item the rig photographs, which sets the stand's minimum camera height. Self-scaling: the wall's 32.0 mm height.  
- PA Pattern: 98.8 x 55.4 mm footprint, 4 layers of 0.3 mm = 1.2 mm thick (pa_test, K 0-0.08 step 0.005, 87 mm/s, 5000 mm/s2). Flat.  
- Flow ratio: pass 1 124 x 94, pass 2 124 x 126 mm, 2 mm thick. Flat.  
- Retraction tower: 40 x 15 footprint, up to 80.4 mm tall. Lies on its back: 40 x up to 80, face 15 mm above the board.  
- Raised markers: the two 30 mm posts (decision 5) let Claude correct the scale at any height. The temperature tower and MVS test also scale themselves from their own known sizes.

## Test strip results (rev1.1) (history; staged 2026-10-04; back if: marker detection or inlay problems on the rev2 board or the small board need the strip's raw results)
Test strip results (rev1.1, Measured 2026-10-03, photos PXL_20261003_063346461 to PXL_20261003_063530089, taken at about 11 cm with 2x zoom)  
- Detection, default OpenCV settings: ID 0 in 8 of 9 photos, ID 1 in 1, ID 27 (post) in none.  
- Detection, tuned settings (learnings.measuring): all 3 markers in all 9 photos, no wrong IDs, in both even and low-lamp light; still all 3 after shrinking the photos to about 6-8 px/mm (Estimated: shrinking only approximates a whole-board photo).  
- Cell edges: cell sizes within about 0.1 mm of design on average (Estimated, from white area). Defects: white showing through gaps in the single black layer and black strings and a blob on ID 1; rounded white corners and a diagonal bridge on ID 27; ID 0 clean. The full board uses a 2-layer inlay because of this (decision 9).  
- Spacing: ID 0 to ID 1 measured 24.93-25.06 mm in 6 of 9 photos (design 25.00); 24.78-25.50 in the other 3, put down to the close, tilted shots (inference).  
- Label outline: black 1-layer inlaid outline kept, as in the rev1 design (the user's choice, 2026-10-03; now 2 layers with the markers).
- Test strip built 2026-10-02 (printed 2026-10-03): photoBoard_rev1.1_marker-test.3mf, build script photoBoard_rev1.1_marker-test.py (projects/3dp/products/photo-board/build/photoBoard_rev1.1_marker-test.py), which reads rfidSpring_settings_base.json (projects/3dp/products/photo-board/build/rfidSpring_settings_base.json, a copy of rfid's) from the same folder. Print it with filament 1 mapped to Bone White and filament 2 to black (the file's preview shows white).
