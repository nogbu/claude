---
about: Photo board with inlaid ArUco markers for photographing calibration test pieces
readonly: no
---
photo-board  
Short name: photo-board

Photo board: a 3D printed board with inlaid markers for photographing filament calibration test pieces, so Claude can do as much of the evaluation as possible. Started 2026-10-02 in calibration-rig; split out 2026-10-05. Phone and light stand: calibration-stand.

Current state  
- Latest rev: rev2, the full board (photoBoard_rev2.3mf), built and printed 2026-10-03; measures 251 x 223 mm (Measured 2026-10-03), 1 mm under design each way.  
- Next: nothing open on the board; the stand is next (calibration-stand).  
- Parts: photo board (photoBoard_rev2.3mf), build script projects/3dp/products/photo-board/build/photoBoard_rev2.py, reading rfidSpring_settings_base.json (a copy of rfid's) from the same folder.  

Board design, rev2 (agreed 2026-10-02, changed and built 2026-10-03; sizes Estimated until printed and measured)  
- Plate fit: 252 x 224 mm at x 2-254, y 30-254 on the P1S plate (256 x 256 mm; excluded corner x 0-18, y 0-28, front left; Listed, default printer settings). Open end front, closed end back.  
- Floor: 4.2 mm (14 layers): 3 solid bottom and 3 top layers, 15% gyroid infill between. No ironing.  
- Channel: open (no lips), 216.9 mm wide (x 19.55-236.45); free area about 217 x 197 mm (y 30-227). The Bone White floor is the light background; clear or light pieces lie on a black insert (matte black cardstock or felt, Letter-sized or cut to the channel) against the stop. No white paper.  
- Rails: 17.55 mm wide (x 2-19.55, 236.45-254). They and the closed-end strip (27 mm deep, y 227-254) rise 2.1 mm (7 layers) above the floor; their tops are the marker plane, about level with flat test pieces' tops.  
- Fillets (vertical edges only, 2026-10-03, decision 12): 3 mm on the 4 outer corners, the rails' front inner corners (x 19.55 and 236.45, y 30) and filling the channel's back inside corners (y 227); 1.5 mm on the posts' 8 edges. Markers, white margins and label outline untouched (the build script checks); nearest clearance 0.98 mm, from the label outline. Stop face straight for 210.9 mm.  
- Stop and zero line: the closed-end strip's inner edge, y 227. Towers go base-first against it, centered on the closed-end row's middle marker, on the centerline (x 128).  
- Markers: ArUco 4x4 (OpenCV DICT_4X4_50), cells 3 beads (1.86 mm at the 0.62 mm line width), markers 11.16 mm with at least one white cell of margin; black flush inlay 2 layers (0.6 mm) deep, Bone White below (the user's rule, 2026-10-02: black only where it shows, to save black).  
  - Rail height, 23 markers: left rail y 40-215 every 25 mm (IDs 0-7, front to back); closed-end row of 9 at y 240.5, x 31.55-224.45 every 24.11 mm (IDs 9-17, left to right); right rail y 215-90 every 25 mm (IDs 19-24, back to front). IDs 8, 18, 25, 26 unused: their spots went to the posts, label patch and shortening.  
  - Posts: on the rail ends at the closed-end corners (x 10.78 and 245.23, y 240.5); tops 14.9 x 14.9 mm, 30.0 mm above the floor (100 layers), one marker each (ID 27 left, ID 28 right), so Claude can solve camera distance in each photo and correct scale at any height. IDs 29-49 spare.  
- Label patch: right rail front end, about 15 x 48 mm (x 237.7-252.7, y 32-80), black outline 3 beads (1.86 mm) wide inlaid on the marker layers (width chosen 2026-10-03). Write in pencil, or on masking tape inside it.  
- Filaments: Bambu PLA Matte, Bone White body (filament 1), black for the markers' top two layers and label outline (filament 2); no white (the user's choice, 2026-10-03: a color they have plenty of). Filament 1's 3mf color is #CBC6B8, Bambu's PLA Matte Bone White code (Listed, Orca 2.4.2 filament color list), so AMS matching picks Bone White; #FFFFFF is Ivory White's (2026-10-03). Preset "Bambu PLA Matte @BBL X1C" (covers the P1S 0.6 nozzle; 1.32 g/cm3, $24.99/kg, 55 C textured plate, 22 mm3/s cap; Listed, Orca 2.4.2).  
- Build settings: 0.3 mm layers (first too), 0.62 mm line width, skirt off (the board fills the plate), no prime tower, supports or brim, one plate, flushing 140 mm3 into black and 700 mm3 back (set in the build script).  

Decisions and why (2026-10-02)  
1. Scale lives on the board as inlaid markers, not paper: inlaid spacing stays fixed, unlike a laser print that can shrink or stretch, and marker IDs let Claude find the board when a piece covers some. One known spacing gets checked with calipers once.  
2. Wide board with rail markers, over a shorter board with a prime tower: markers on three sides of the free area. Trade-off: no prime tower, so color changes purge into the chute.  
3. Open channel, over 3 mm lips on a 0.9 mm slot: nothing overhangs to droop, felt works, and rail height is free to match flat pieces. Trade-off: the insert's edges aren't held down.  
4. Markers every 25 mm with 3-bead cells, over about 18 mm: in simulated photos (5-11 px/mm, edges spread 0.1 mm, corners rounded 0.3 mm) every marker read, 0.05-0.07 mm RMS and 0.10 mm worst mapping error across the free area; 2-bead cells read only 13-18 of 27 (Estimated, simulation).  
5. Two 30 mm posts, over 15 mm: simulated length error per 100 mm at 100 mm height 0.05 vs 0.12 mm, 0.39-1.14 mm with no posts (Estimated, Monte Carlo).  
6. The stop as the fence, over a corner fence: nothing new to add, and centered pieces lean least in the photo.  
7. Label patch about 15 x 48 mm, over 15 x 30: costs one rail marker.  
8. 4.2 mm floor, over 3.0: about 2.5x stiffer for about 15 g more (Estimated); flatness matters because all rail-height markers are assumed coplanar.  
9. Build: 2-layer inlay (2026-10-03: white showed through gaps in the test strip's single black layer; reverses the 2026-10-02 1-layer choice made to save black; trade-off: about twice the inlay's black), no ironing (roughly +1-3 h), gyroid core.  
10. From the concept stage: one piece, not joined prints (a joint adds offset and flatness risk); Bone White Matte PLA body, black Matte PLA markers (Bone White replaced white 2026-10-03: two colors, 3 color changes (4 since decision 9), none of the user's white; trade-off: cream background, not bright white); the phone stand a separate part, fixing camera height and angle for hands-free timer shots; one doc for board and stand (split into photo-board and calibration-stand 2026-10-05).  
11. Shortened board (252 x 224, front edge y 30), over a 38 x 58 mm full-depth corner cutout (2026-10-03, the user's choice): Orca refused the notched board (it checks an object's convex outline against the excluded corner), and the cutout would have cost the left rail IDs 0 and 1 and a channel strip. Trade-off: 28 mm less free depth (still deeper than the largest test piece), ID 25 lost.  
12. Fillets on all vertical edges (the user's request, 2026-10-03), sized so no marker, white margin or label outline changes. Rounded outer corners also lower corner-lift risk, since no brim fits (inference).  
13. Audit of rev1 (2026-10-03, the user's choices): internal bridges kept at 45 mm/s (75 saves 12.5 min, but layer 19 is the inlay's base); gyroid over grid (grid saves 5.5 min). Left out: first layer 55 to 70 mm/s (-6 min), 10% infill (-11 min), flow cap above 22 mm3/s (Bambu's Matte presets use 22 for 0.6 and 0.8 nozzles), prime tower (+7 min, +6 g).

Open questions  
- Calibrate JAYO PETG Translucent on the rig once built, from Orca's "Bambu PETG Translucent @BBL X1C 0.8 nozzle" preset; the pots' tuned values and parked PA calibration (D2) are in 3.5pot-modlog. Re-check JAYO's published specs then (2026-10-03).  
- Put the 9 rev1.1 strip photos (PXL_20261003_063346461 to 063530089, zip sent 2026-10-03) into /mnt/project-files/photos/calibration-rig/ (attach them in a 3dp thread), per the photo rule. Then Claude creates the photos.calibration-rig index and adds it to the Content index.  

Photo routine (draft 2026-10-03; revise after the test strip and the phone stand)  
- Lay each piece in the channel as in Stop and zero line; towers lie on their backs (log: Test piece sizes).  
- Clear or light pieces go on the black insert; on a clear PA Pattern, color the label strip with a marker first (learnings/speed-and-cooling: Pressure advance test in clear filament).  
- Until the phone stand exists, hold the phone straight down at about 30 cm, whole board in frame: one photo in even light, one with a lamp low at one side.  
- Send originals in a zip; photos attached directly get compressed.

Agreed changes for the next rev (not yet built)  
- None yet.

Use: the filament calibration procedure (temperature, max volumetric speed, pressure advance, flow ratio, retraction, then a confirmation print, in Orca's calibration guide order) photographs each test piece on this board.  
