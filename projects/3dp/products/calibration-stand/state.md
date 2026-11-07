---
about: Phone and light stand with its own small board for photographing calibration test pieces
readonly: no
---
calibration-stand  
Short name: calibration-stand

Phone and light stand for photographing filament calibration test pieces; the current design (the small stand) carries its own small photo board. Started 2026-10-03 in calibration-rig; split out 2026-10-05. Test piece sizes, photo routine: photo-board.

Product rules  
- Images of it never show the light bars unless I ask.

Current state  
- Latest: small stand, concept only, nothing built. clean8.py draws changes through 63; all 66 checks pass (2026-10-05). Picture: calibrationStand_clean8.png. Folder paths below are in /mnt/project-files/.  
- Design principles audit (2026-10-07; changes 132 to 165, settled 2026-10-09): outcomes written into the lines below (2026-10-09). Report notes/calibrationStand_audit132_report.md, grid _grid.md. Pictures: the working model (notes/calibrationStand_audit132Work/wm/, README; its mesh holds 133 to 135 (134's tip curve starts from the real corner since 2026-10-10; wm/clipfeat.py), 140 to 164's shape changes, and 121 and 125 on the board, 2026-10-10; not yet the face-edge profiles (90, 152) on the frames and top middle; check140.py, 40 checks), not the audit's. Pictures: images/calibrationStand_wmB_whole.png and _joints.png.  
- Next (2026-10-10): build the fit test, then rev1. Fit test fully designed, its clips brought to 129, 130, 133, 134 and 162 (2026-10-10), build decisions settled; the user said not yet to building it (2026-10-06). Pictures: images/calibrationStand_fitTest_rev0.1b.png (clips before 129) and calibrationStand_fitClips129to162.png. Scratch geometry: notes/calibrationStand_fitTestWork/run.sh (its header lists the scripts; fitpieces.py takes the clip changes from the working model's wm/clipfeat.py; checkclips.py, 52 checks). Clip check in place of a full audit (the user's pick, 2026-10-11): design principles 1 to 4 and 12 model check (dpcheck.py) on the three clips found nothing the changes added; it reads the new r1.0 curves as r0.3 to r0.7 (a circle fit on the profile gives r1.0), and its other flags were on the clips before (the scratch model's 0.1 bevel steps, the snap U, the slot and relief ends, the pressed numbers).

Open questions  
- Before build: repeat the slice checks on the real 3mfs (the 2026-10-06 pre-slice used scratch meshes); they also settle whether Arachne keeps the 1.86 and 3.10 walls at 3 and 5 beads (audit). (log: Small stand: clean8 and scratch-model checks)  

Build decisions (the user's choices, 2026-10-05; fit test details 2026-10-06)  
- Stand: calibrationStand_rev1.3mf, 2 plates: rev1.1 both side frames on their sides; rev1.2 top middle and board part. Bounding boxes (clean8.py) fit with a 5 mm gap, clear of the excluded corner: 195.4 and 208.8 of 255 (inference); the build script checks the real outlines.  
- Settings: my process settings unchanged on every part (2 walls, 3 top and 3 bottom layers, 15% Adaptive Cubic).  
- Fit test (64, 65; not built): calibrationStand_rev0.1_fit-test.3mf, six plates in the print order in values.md, one per test except the rings, which take two (three rings plus Orca's 2-loop skirt, 10 out, overran the 256 bed; 2026-10-06); all clear of the excluded corner (fitplates.py). Every piece has a marked end; steps read by position from it. Pieces, gaps, marks and checks: values.md (stand-fittest).
- Strength (95, all inference, hand calcs): top middle 6.1 MPa vs 53 along layers (60 N mid-span); post 3.5 MPa vs 53 (30 N side push at top); corner posts 0.9 MPa vs 32 across layers (30 N knock from test pieces); no top-bar lift case, as the stand is lifted by the base (2026-10-06); base seams: a 30 N side push at z 185 (half per seam) bends each 79.2 x 8.7 glue face to about 2.8 MPa (simple bending, tenon not counted; no source for glue on PLA, so the break pair decides); a front-to-back push goes to the dovetail's sides in plastic, about 2 MPa vs 53.  

Stand inputs: projects/3dp/content/calibration-stand.inputs.md (stand-inputs).  

Small stand (concept, nothing built; all values Estimated unless noted)  
- Scripts: projects/3dp/products/calibration-stand/build/concepts/photoStand/small/, run from that folder. clean8.py = current geometry and every check; render9.py = its picture (images/calibrationStand_clean8.png, no light bars); tippingPrinted.py = tipping at printed weight (28). clean8.py reads /mnt/project-files/3mfs/barrinaClip_rev2.3mf through clean7.py (imports barrinaClip_rev2.py, final_lib.py, renderlib, rev1_concept). Older scripts draw superseded geometry. The design picture, when redrawn, gets a how-it-prints panel: each part on the plate, plate face in orange, height and layers, no supports (149; images/calibrationStand_wm149.png).  
- Coordinates: x from the board's center line, z up from the desk, y front to back on the board (0 to 132); right side, left mirrored.  
- Parts (4, glued; Bone White Matte PLA): side frames (2): post, foot, top-bar end, brace and both light clips in one piece, printed on its side, front face down, 79.2 deep (264 layers), y 34.4 to 113.6; top middle + cradle, flat; board part (board + base middle), flat.  
- Side frame profile: post x 147 to 165 (18 wide); foot x 105 to 165, z 0 to 18; top-bar end from the top cut to x 165, z 167 to 185 (cuts x 130.40 right, -29.60 left). Foot outer corners r24, matching the elbows (135); elbow r24 outside, r6 inside on one center (141, 161), unbuilt (dp 2 pairs; the user, 2026-10-07). Stand 330 wide, 185 tall.  
- Clip blocks: solid between each snap U and the post. Corners r6 at the post; the brace (126) fills the high block's top corner.  
- Clips: snap U cut unchanged from barrinaClip_rev2.3mf's mesh (section 8.2 mm in, untilted; matches barrinaClip_rev2.py profile() to 0.000 mm²): walls, bumps, hinge slot (1.0 wide), 2.48 bridge, 45 deg pull tab, 3 mm swing room at the free wall's tip; then 91, 129, 130 and: tooth bases r1.0, tips sharp (133); each free wall tip one r1.0 convex curve from the bar face to the tab, filling the old notch (134); face edges sharp (162; dp exceptions). The block meets only the U's back and the fixed wall's outer face. High clip: mirrored, turned -45 deg at (131, 120), free wall lower, tab down. Low clip: turned -90 deg at (125, 31), free wall on top, tab up; the block fills the 0.64 under the fixed wall.  
- Top middle: x -29.60 to 130.40 (160.00) by 79.2 deep, z 167 to 185, flush with the frames front and back. Floor 3 (z 167 to 170), camera window (camera bar 65 x 22 plus 0.5 per side) cut through. Phone pocket 153.8 x 73.0, r4 corners, above the floor; walls 3.10 (5 beads; 66).  
- Board part: board 170 x 132, plan corners r5.8; floor 6.6 (22 layers); side rails 17.5 wide and back strip 27 deep (stop at y 105) at 8.7 (29 layers); channel 135 wide, back inside corners r3. Ends x 85 to 105 each side, y 34.4 to 113.6, 8.7 tall, flush with the rails (69); part 210 wide.  
  - Board edges: r5.8 vertical fillets, 0 to 8.7 tall, where the board's sides meet the ends' front and back faces (62); rails' front inner corners r5.8 from the 6.6 floor to the 8.7 rail top, ending at y 5.8, 2.3 clear of marker L1's margin (157; were r1.0, 70); rails' inner top edges and the stop's top edge a plain r0.9 curve (125, 121); every other top edge the 0.9 profile (90). A 0.9 top bevel stops at a taller block, whose corner curve runs down to meet it, no notch under the block (112).  
  - Markers (ArUco 11.16, 1.86 white margin, 2-layer inlay; photo-board): 3 per rail at y 10, 35, 60 (board x 3.2 and 155.6); 5 on the back row at board x 28 + 25i, y 112. IDs (114): left rail front to back 29, 30, 31; back row left to right 32 to 36; right rail back to front 37, 38, 39; left step 40, left column 41, right step 42, right column 43 (photo-board spares; none used on rev2).  
  - Corner posts (76, 84): 17.5 wide, flush with the board's side and back; step y 93.5 to 111, top 21.6; column y 111 to 132, top 36.6; front corners 2.0, back inner corner 5.8 (matches the board's back corner); top edges the 0.9 profile; r0.9 curve where each step top meets its column (106, z 21.6 to 22.5); r6.0 base curve, z 8.7 to 14.7 (49 layers; 160), at the front, the inner side over the back strip and the outer side over the end block, following the 0.9 bevels down where it reaches one (105); back-row marker 1's margin 2.99 clear. Step marker centered on the step top; column marker from y 114.36 (84: 0.5 toward the back).  
  - Brim groove: 1.5 wide x 5.7 deep, 0.9 floor under it, y 65 to 66.5 across the channel; ends r0.75 half-circles at the rails, bottom corners 0.6 (85). Brim check (2026-10-05, Measured): log.  
- Dovetail joints, all four cuts (92, 93): sliding dovetails, superglued. 45 deg sides, 0.15 gap per face (Estimated; the fit test sets it), all on the flat-printed tenons in X-Y. Tenons on the middle parts stick out 8.3 past the cut (140, 151), leaving 0.2 at each 8.5-deep frame slot's end; their 45 deg faces sit 0.3 further in below z 1.2 as printed, for elephant foot (142, 143).  
  - Top: 12.0 tall, 55.2 at the top, 31.2 neck. Base: 4.2 tall, 54.18 at the top, 45.78 neck (104); slot neck 46.2.  
  - Each tenon sits at the bottom edge of its joint face, neck on the underside, centered front to back (12.0 of frame each side); the frames slide on sideways over top and base tenons at once. Every face 45 deg or less, so no supports (inference). Slot edges on whole 0.3 layers (40, 80, 184, 224 at the top).  
  - Keying: one pair of arrows at each left-hand seam, top and base, on the underside, centered front to back; none at right-hand seams. Each a 90 deg tip, 7.2 base, 3.6 base to tip, 0.6 deep (2 layers), corners r1.0 (145, 107). Tips: the top middle's and board's 2 from the seam; the frame's 10.5 (2 past the 8.5 slot end; 144), layers 120 to 144, tip on 132. The top middle's is a 45 deg V-groove outline, 1.2 wide x 0.6 deep, inside solid (146); the others are recesses.  
  - Glue: medium or gel superglue, no crush ribs; shoulders glued face to face. Dry-fit all four joints first.  
- Edges: 0.9 (3 layers) 45 deg chamfer plus fillet on every outer face edge of all four parts, front and back (mirrored profiles), except the clip faces (162) and where the right brace bears on the top middle: none on either from x 98.14 to 130.40, front and back faces (152).  
- Lights: high bar centers at (131, 120), aimed 45 deg down and in; low at (125, 31).  
- Camera: Pixel 10 Pro main camera, 82 deg diagonal, 4:3, 8160 px long side across x; half-width factors 0.6955 (long) and 0.5215 (short) per mm of distance (inference). Lens over the board's center, 159.4 (bump 4.0) to 160.1 (bump 3.3) above the board floor, below the floor's underside, so the window can't show.  
- Tipping (28): accepted (the user's choice, 2026-10-05; kept 2026-10-08, 148 turned down): steady it by hand when handling, putty under the feet if needed. With the bars in (about 1,037 g printed) it tips at about 5.8 N pushed at the top front to back with the phone in (accepted 2026-10-06), 4.1 N back to front, about 7.2 N sideways with the r24 feet (inference, tippingPrinted.py, 135; a slice gives real grams).  
- Decisions and why:  
  - Small 170 x 132 board, cradle turned 90 deg, lens at H 170: gets every marker and test piece in frame (camera audit chain, staged).  
  - 4 glued parts, frames on their sides: the user's cut (2026-10-04).  
  - Frames 79.2 deep (66): cradle flush front and back (dp 3); the 73.0 pocket plus two 3.10 walls, on the grid (264 layers).  
  - Sliding dovetails (92): no overhang on either part, and the dovetail's sides take a front-to-back push in plastic (95); they replaced the ridge joints. Turned down: a diamond tenon on the frames, which would start as an 8 mm strand over air (staged).   
  - Arrows only for keying (93): the user's choice, knowing a reversed part still slides fully in. Turned down: notch and key, and different tenon widths (the narrow tenon would be loose in the wrong slot). Offset tenons turned down twice (119, 2026-10-06; 163, 2026-10-09): see dp exceptions.  
  - Base cuts at x ±105: 0.7 MPa vs 2.9 with the cut at the board's edge (inference). Trade-off: the seam shows on the foot's top.  
  - Change 81 (flatten the posts) dropped (the user, 2026-10-05); steps kept: dp exceptions.  
  - Face-edge size kept at chamfer 0.6 + fillet 0.9 (90; the user, 2026-10-07): a 0.9 chamfer cuts the step and column marker margins (notes/calibrationStand_edgeWork/edgecheck.py; images/calibrationStand_edgeMarkers90.png).  
  - Brim groove: the 50% MVS comb lies on its back, brim about 5 mm below the tooth tips; the brim drops into the groove, so the comb lies flat in the same spot each time (the user's request, 2026-10-04).  
  - Arrow recess (107, 108): solid on the frames and board; V-groove outline (117) turned down for them, taken for the top middle only (146).  
  - Light bars removable (2026-10-06): the clips are a removable joint (design principle 11); the fit test picks the gap that holds yet lets a bar out by hand.  
  - Hinge slots 10 deep (129) kept, 20 deep (132) turned down (2026-10-07): the clip fit test shows whether 2.85% strain holds.  
  - Post base curve r6.0 (160): at least a third of the 17.5 post, ending on the layer grid (5.8 ended at 48.33 layers); nothing past 45 deg, every marker margin clear (inference, scratch model).  
  - No arrow on the top middle (77, dropped 2026-10-05): the camera window shows which end the camera goes.  
  - Frames, top middle and board ends stay 79.2 deep, not 132 (88, turned down 2026-10-05): 132 cost about 78% more plastic and raised the snap to about 73 N.  
  - Column front corners stay r2.0 (131 undone, the user, 2026-10-07): squaring them to end the 2 mm step-top wrap at each corner was turned down.  
  - Finger slots (128) at x 61 to 91 (center 76; 164, 2026-10-08): at x 50.4 they opened 18.6 of the phone's button stretch; about 20.5 MPa vs 53 in the floor strip at 60 N (inference).  
- dp exceptions (dp 2 limits)  
  - Barrina snap U in both clips: copied from barrinaClip_rev2 (slot 10 deep, 129; teeth 133); its walls, teeth and hinge slot do the work.  
  - Hole 45 deg corners r3 (126, 136, 137), upper and lower, both frames, with the right frame under a bead from x 129.0 under the top middle: executive override (2026-10-08).  
  - Right brace tip at (98.14, 167) sharp (138): it bounds the brace's bearing face under the top middle. A curve on the frame would end in a feather thinner than one bead, and a curve on the top middle would hang below its bed face. The left frame's matching corner is r6 because its top bar is whole.  
  - Clip face edges sharp (162, the user's "leave it flat", 2026-10-09; 139): the U, bending wall and teeth, front and back, all four clips. Fit faces start on the bed (141); elephant foot sits on them, and the fit test sizes the gap with it.  
  - Clip tips r0.93 (86, 161): full rounds on the 1.86 walls, the largest they take, copied unchanged from barrinaClip_rev2.  
  - Tenons centered: executive override (119, 2026-10-06); arrows (93) mark the way (163).  
  - Dovetail glue faces and shoulders: flat mating faces, sharp; face-edge bevels stop at the glued cuts.  
  - Dovetail slot width runs across the frames' layers (slot edges on whole layers; gap on the tenons).  
  - Phone pocket's inside faces and floor: sized by the phone's fit.  
  - Marker faces: flat, sharp-edged inlays the camera audit measures.  
  - Stop foot sharp: the stop face is the zero line; towers stand base-first against it and the black insert lies against it, so a curve would hold both off it (photo-board).  
  - Channel floor's sharp inside corner along the side strips (71): the black insert lies against the strips.  
  - Channel back corners r3 (156): keeps a 124-wide test piece on the stop up to 2.5 off center (59); as on the rev2 board, clear of the marker margins.  
  - Slope foot curve r2.0 (73, 154): the largest that ends one bead (0.62) clear of the x 105 seam; the limit is r2.08.  
  - Face-edge size 0.9 (90, 155): one size, so the profiles meet across the seams. A larger one cuts the step and column marker margins (edgecheck.py); 2.1 cut into the rail markers' margins. Trade-off: less rounded than 6.0.  
  - Kept steps (dp 3; 158):  
    - Rails and stop, 2.1: the marker plane and the channel walls. Their top edges are a plain r0.9, not the chamfer, to leave 1.2 of flat for the insert (121, 125).  
    - Corner post steps (159): the retraction tower lies on its back with its face 15 mm above the board (photo-board log, Test piece sizes, Measured 2026-10-02), and the step tops are 15.0 above the channel floor (6.6 above the desk), so the step marker reads scale at its height; the scale-fit check from the 2.1 rail and 30.0 column markers stays inference. Photo-board decision 5 set the 30 mm columns.  
    - Brim groove, 5.7: holds the comb's brim (the user's request, 2026-10-04).  
    - Finger slots: let fingers reach under the phone (128).  
  - Corner posts printed across layers: see Strength; splitting turned down by photo-board decision 10.  
  - Corner posts' front corners 2.0 (84): the step marker's white margin must stay on the flat top inside the 0.9 edge; r2.0 leaves 0.05 clear, r2.3 cuts into it. The column's front corners match.  
  - Brim groove top edges sharp: a 0.9 curve on both would widen the 1.5 mouth to 3.45 and could let the comb shift; the groove strip tests both (116).  
  - Brim groove bottom corners 0.6, ends r0.75 half-circles (85): the most a 1.5 groove takes.  
  - Arrow recess (107, 108): 0.6-deep edges sharp (a 3-layer curve can't fit 0.6); roof a 6 mm flat bridge on the underside, unseen in use.  
  - Tenon free ends, base and top, sharp (118, 150): hidden in the slot once assembled; keeps the full glue length.  
  - The 0.9 profile's top corner stays sharp on the posts' step and column tops (122): a 3-layer curve there needs r3.07 (1.8 tall, 2.55 wide) and would cut the markers' margins.  
  - Base seams at x ±105 (123): the end blocks' four 0.9-profile edges each run straight across the cut, so no edge is thinner than one bead on either part.  
- dp trials: 2026-10-05, the dovetail tenons take the 0.15 gap in X-Y on the flat-printed parts (design principle 5).  

Agreed changes for the next rev (not yet built)  
- Changes 2 to 63 are drawn in clean8.py (numbered list in staging, history). None since is in a build script. Where the text above carries a change, its line points there (66 to 165).  
- Agreed after clean8 (all modeled in auditWork/_auditbase.py except 70):  
  - 64, 65: the fit test (Build decisions).  
  - 66: top middle walls 3.10 (5 beads), frames and top 79.2 deep (264 layers), pocket rim 0.9 bevel plus curve.  
  - 67: pocket floor-to-wall inside edge r0.9.  
  - 68: camera window corners r1.0, bed and top edges 0.9 bevel plus curve.  
  - 69: feet and board ends 8.7 tall (29 layers), slope under the low clip from (106, 8.7) to (115, 20.5) (start moved by 73).  
  - 70: curve on the two front corners where the side strips drop to the middle floor (2026-10-05), now r5.8 (157).  
- Agreed in the audit walkthrough (2026-10-05): 71, 72, 84 and 85 (lines above).  
  - 73: low-clip slope starts at x 106.7 (was 106), top still (115, 20.5), so the 2.0 foot curve ends about 0.66 clear of the base seam at x 105 (one bead 0.62; section 11; inference); 3.9 curve at the slope top (a third of the 11.8 block; thins the low clip's fixed-wall tip to 1.42 over its last 1.9, clear of the bar); the 0.02 V-notch in the high block's 45 deg face (about (131.70, 138.16)) filled flush to the face's line (dp 3), not the 0.6 curve in _auditafter.py.  
  - 90: every 0.9 face edge becomes a 45 deg chamfer z 0 to 0.6 plus an r1.273 fillet 0.6 to 1.5 (3 layers, both ends on layer lines); chamfer foot moves 0.9 to 0.973. The audit's r1.02 left both ends off the layer grid (fillet height is r x sin 45).  
  - 91 (clip fix, both clips, both frames): the hinge slot (1.0 wide) runs past the clip's old top into the frame block, ending in a full round; bending wall stays 1.86, with a 2.0 relief gap beside it ending in a full round (minus the snap tab); a 24 mm bending stretch from bump tip to the slot's round end on both clips. Low clip: the old r6 block-post fillet goes; an r1.0 curve fills that corner. Face edges: 0.9 on the slot's block side, the gap's post side and the round ends; the bending wall's are sharp (162). Figures (inference, simple beam, 2 mm bump push): 3.0 of post beside the high clip's slot end and 10 beside the low, 0.54 clearance at full push. Slot length since changed by 129 (its earlier strain and force: log). Scratch model: clipfix.py, build(30,30) (129: build(20,20)), wall 1.86, free wall's inner face at x -10.5 in the clip's own frame.  
- Asked 2026-10-06 (scratch only; notes/calibrationStand_render10/, run beside the small/ scripts: profs20.py writes the frame profiles, render15.py draws images/calibrationStand_frontBraces.png):  
  - 126 (corner braces): a 45 deg bar each side, 18 straight across like post and top bar; lower face continues the high clip's ceiling line from the fixed wall's outer corner (129.33, 135.81) to x 98.14 at z 167 (upper face at 123.60). Its upper face meets the post at z 143.6; the corner above stays open, a 273 mm2 through hole, its 45 deg corners r3 (the user, 2026-10-07). Edges: r1.0 at the fixed wall (90 deg; wall 1.86, so the 1 mm minimum); r6 at the top on the left frame; sharp on the right (dp exceptions). Right brace end bears on the top middle's underside, 32.26 x 79.2 (x 98.14 to 130.40), unglued, so no new joint (the user, 2026-10-07); fit test checks it (153). Scratch: notes/calibrationStand_braceWork/run.sh. About 680 mm2 more profile, about 12 g per frame (inference). Outer corners r24 (135).  
  - 128 (cradle finger slots; 2026-10-07, from images/calibrationStand_fingerSlotSketch.png): two 30-wide slots facing each other, now at x 61 to 91 (164), cut top to bottom through each long wall and the floor, 13.1 in from the face (10 past the wall); 53 of floor left between. Edges: horizontal ones the 0.9 profile (90); wall-end vertical edges and floor-notch inside corners r1.0. Scratch: notes/calibrationStand_fingerSlotWork/fslot.py (x 50.4); picture images/calibrationStand_fingerSlots128.png (no edges; 164's: images/calibrationStand_wm164.png).  
  - 129 (hinge slots): all four 10 deep (were 20), relief gaps end with them; bending wall free 14 from the bump tip (was 24). Inference, simple beam, 2 mm push: strain about 2.9% (was 1.0%), about 219 N (was 44).  
  - 130 (clip teeth): all eight sharp-tipped: tip 8.5 from the clip's center line (was a round reaching 8.853); bases r1.0 (133); each reaches 0.35 further into the bar's notch (inference). dp 2 limit (snap edges).  
