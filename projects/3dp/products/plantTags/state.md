---
about: Plant tags
readonly: no
---
plantTags  
Short name: plantTags  
Status: rev1.2_mugatu7mm, rev1.3_aceOfSpades (rebuilt 2026-10-11) and rev1.4_nicetySet built, not printed.

Product rules  
- A tag's second row starts 2 spaces (2 space widths) to the right of the first row's start.

Latest version  
- Built: plantTags_rev1.4_nicetySet.3mf (2026-10-11), script build/plantTags_rev1.4_nicetySet.py (plantTags_lib.build_set). One plate, three tags 28 mm apart (my words): blank; name tag "nicety" red-brown; species tag "doc block michelle" black, wrapped to "doc block" over "  michelle" because one row (61.4 mm) runs 2.1 mm past the 70 mm soil line (my default, inference). 7 mm text, 0.35 mm lines (best_lw knee for every row), first layer 0.35. Prime tower at (205, 175), clear of the tags. Slice (Orca 2.4.2): 4 layers, 35 min 53 s, 10.98 g Translucent + 0.93 g red-brown + 0.70 g black PETG-CF.  
- rev1.3 rebuilt 2026-10-11 under the same name: its base-preset lists (inherits_group, different_settings_to_system) had 4 entries for 3 filaments, so Orca opened it with Generic filaments (my report; the 2-filament rev1.1 and rev1.2 opened with Bambu presets). write3mf now sizes both lists to the filament count.  
- Built: plantTags_rev1.3_aceOfSpades.3mf (2026-10-10), script build/plantTags_rev1.3_aceOfSpades.py on build/plantTags_lib.py (any rows, size, line width, indent; tagpic.py draws one). One tag, two rows at 7 mm (my words): "ace of spades" red-brown over "x dark phoenix" black, second row indented 2 spaces (3.57 mm pen offset, 3.44 mm between glyph edges). Rows on font baselines (ascender 0.722 em, descender 0.213 em, band 6.54 mm), margins and gap equal at 2.30 mm (inference: even spacing reads best). Line width 0.35 mm: the widest before two-bead coverage drops for these words (1.4% / 2.5% under two beads at 0.35, 3.4% / 3.7% at 0.37). Row 2 ends 6.8 mm short of the 70 mm soil line. Slice (Orca 2.4.2): 4 layers, 1.02 mm, 24 min 36 s, 4.90 g Translucent + 0.75 g red-brown + 0.54 g black PETG-CF.  
- Built: plantTags_rev1.2_mugatu7mm.3mf (2026-10-10), script build/plantTags_rev1.2_mugatu7mm.py: rev1.1 with 7 mm text and 0.37 mm text and first layer lines. Slice (Orca 2.4.2): 4 layers, 1.02 mm, 19 min 19 s total (13 min 22 s model), 4.74 g PETG Translucent + 0.74 g PETG-CF. G-code: text walls 0.34-0.67 mm on layers 1-2; body first layer 0.37-0.59.  
- Built: plantTags_rev1.1_mugatuTest.3mf (2026-10-10), script projects/3dp/products/plantTags/build/plantTags_rev1.1_mugatuTest.py. One mugatu tag, changes 1-6, OrcaSlicer P1S, the 3mf's filaments 1 and 3 values, prime tower moved to (110, 175). Command-line slice (Orca 2.4.2): 4 layers (0.3 + 3 x 0.24), 1.02 mm, 19 min 57 s total (14 min 1 s model), 4.75 g PETG Translucent + 0.71 g PETG-CF. G-code: text on layers 1-2 only, all walls, 0.28-0.57 mm (Arachne); body first layer 0.31-0.66, above it 0.62.  
- Source file: my plantTags.3mf, attached 2026-10-05 (copy at /mnt/project-files/uploads/hearth/, named by its ID). Saved in Bambu Studio 2.3.1, not OrcaSlicer, with X1C profiles ("0.6mm default", based on "0.24mm Standard @BBL X1C 0.6 nozzle"; printer "X1C 0.6mm"). Not yet built by Claude. Picture and text-check scripts (no build script yet): projects/3dp/products/plantTags/build/ (run.sh sets up a scratch folder; opts.py draws text options with the real font, strokes.py measures two-bead coverage).

Details (from the source file's mesh and settings, 2026-10-05)  
- Tag: flat stake 133.4 × 20 × 0.96 mm. Square end with 2 mm corner fillets; the other end tapers to a rounded point over its last 14 mm. Mesh source named plantTagv2.stl.  
- Text: Overpass Heavy (wght 800), size 6.5 mm (the em size), 0.4 mm deep, on the bed face, mirrored so it reads from that face, at the square end. Placeholder words "name" and "species". As saved, the text hangs 0.385 mm below the tag, so the tag body starts over air (fixed by agreed change 1).  
- Filaments: 1 Bambu PETG Translucent, clear (#00000000), tag body; 2 Bambu PETG-CF, black (#000000), "species" text; 3 Bambu PETG-CF, red-brown (#9F332A), "name" text.  
- Settings in the file: layer 0.24 mm, first layer 0.3 mm, line width 0.62 mm (first layer 0.62); the text parts set their wall, solid infill and top surface line widths to 0.45 mm; 2 walls, 3 top and 3 bottom layers, 15% adaptive cubic infill; Textured PEI plate; prime tower on.  
- Plates: 1 "species" (4 tags), 2 "name" (4 tags), 3 "blank" (1 tag with no text).

Decisions and why  
- Test tag first (2026-10-10, my choice): one "mugatu" tag with all agreed changes, in its own file, before the full plates, because 0.31 mm lines on the 0.6 mm nozzle are untested.  
- Move to OrcaSlicer with my P1S settings (2026-10-10, my choice): matches my setup and lets Claude slice-check it. The file's layout, colors and per-part settings carry over.  
- Layout follows my 3mf (2026-10-10, my words): separate tags, one word each, "name" tags in red-brown and "species" tags in black, each word at the file's own position (left edge kept, centered across the tag). Agreed changes apply onto that layout; change 2's "two rows" doesn't merge the two tags.  
- Soil depth (2026-10-10, my words): the stake goes 60 to 70 mm into the soil from the tip, leaving 63.4 to 73.4 mm above it. At 70 mm, each row has about 57 mm from the text's start (4.1 mm from the square end) to 2 mm above the soil, about 11 lowercase letters at 9 mm (inference: "name" averages 5.7 mm per letter, "species" 4.5).  
- Text inlaid flush in the bed face (2026-10-05): fixes the floating tag body and gives the crispest, matte letters on the Textured PEI plate.  
- Two rows of text on the 20 mm tag at a 9 mm size (2026-10-05): the largest size that fits two rows. Strokes are about 1.0–1.3 mm (two of the text parts' 0.45 mm beads, not two 0.62 mm beads) and every space in or between letters is at least 0.62 mm (Measured from the mesh and the font). At 6.5 mm, some spaces were under 0.62 mm and would fill in.  
- Smallest size for two-bead strokes (2026-10-10, Measured from the 3mf's text mesh by opening each word's mid-depth section): with the text parts' 0.45 mm lines, two beads cover all but about 1.5% of the letter area (rounded ends and corners) at 8.5 and 9 mm, about 4% at 8 mm and 7% at 7.5 mm. Two 0.62 mm beads don't fit even at 9 mm (27% of "name" and 49% of "species" too thin).  
- Narrower text lines (2026-10-10, Measured the same way): two beads cover all but about 1.5% at 7.5 mm with 0.40 mm lines and at 6.5 mm with 0.35 mm lines. Untested: how narrow a line the 0.6 mm nozzle lays cleanly. The text parts set no first layer line width, so the bed face layer prints at 0.62 mm (learnings/walls); whether Orca takes it per part is unchecked. Spaces between letters shrink too; at 6.5 mm some are under 0.62 mm.  
- Body stays clear PETG Translucent (2026-10-05, my choice), accepting lower contrast than an opaque light body.  
- Turned down: one row at 13 mm (I want two rows); widening the tag to 30 mm for two 13 mm rows (the tag stays 20 mm); an opaque light PETG High Flow body and an all-Matte-PLA tag (I kept the clear body).

Open questions  

Agreed changes (current revision)  
1. Text inlaid flush in the bed face, 2 layers (0.3 + 0.24 = 0.54 mm deep).  
2. Two rows of text at a 9 mm size: each row 8.4 mm from the top of the tallest letters to the bottom of the descenders, 1 mm margins at the tag's long edges, 1.1 mm between rows, baselines 9.6 mm apart.
3. Tag 1.02 mm thick (agreed 2026-10-10), up from 0.96, to sit on the 0.3 + 0.24 mm layer grid (4 whole layers) and leave 0.48 mm of clear body behind the 0.54 mm text. Turned down: 0.78 mm (one layer behind the text, floppier) and keeping 0.96 (off the grid).
4. Text 7 mm (em size), one row per tag, with the text parts' wall, solid infill, top surface and sparse infill line widths at 0.37 mm (2026-10-10, my words: "change it to 7, optimize the line widths"; replaces 5.5 mm with 0.31 mm lines, agreed earlier the same day, and change 2's 9 mm). 0.37 is the widest before two-bead coverage drops on "mugatu" at 7 mm: 1.5% of letter area under two beads at 0.31, 2.0% at 0.35, 2.3% at 0.37, 2.8% at 0.38, 4.2% at 0.40, 7.7% at 0.42 (Measured from the font). At 7 mm a row above the 70 mm soil line holds about 15 lowercase letters, not 20 (inference, 0.54 em per letter). Orca's line width floor is 0.31 (learnings/walls).
5. First layer line width for the whole plate equal to the text line width, now 0.37 mm (agreed 2026-10-10 at 0.31; follows change 4), so the bed face, the side people read, prints two-bead strokes like the text above it. Orca takes it only plate-wide, so the clear body's first layer matches; in a 20 × 20 mm test it added 22 s to one first layer (Measured, Orca estimate). Turned down: keeping 0.62 (one bead per stroke on the face).
6. The name tags read "mugatu" in place of "name" (2026-10-10, my words), lowercase, red-brown, at the file's position: 19.1 mm long, 5.1 mm tall at 5.5 mm; 3.8% of its letter area under two 0.31 mm beads (Measured from the font, build/tagword.py).

Next step  
- Print plantTags_rev1.2_mugatu7mm and check the letters (0.37 mm lines on the 0.6 mm nozzle, bed face sharpness), then build the full file's plates.
