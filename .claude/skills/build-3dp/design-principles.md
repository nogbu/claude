design-principles (build-3dp skill)  

Design principles (dp)  
- Goal: consumer parts good enough to sell that print right the first time on my setup (no supports, cleanup or reprints), fit and hold up in use, and use as little filament and printer time as possible. Use it to decide cases no principle covers and conflicts between principles, and tell me when it decided one.  
- Short name: dp ("save this to dp" adds to this section).  
- Talking to me: in replies, cards and pictures, say "design principles" (or "design principle 6" for a section), never "dp". Files and docs may keep "dp".  
- Applies to every 3D-printed design and concept, tests included.  
- Exceptions: a product doc lists each exception under "dp exceptions", with the reason ("executive override", my choice to break dp, counts).  

1. Print orientation  
   - Before showing a design or concept, optimize every part for ease of printing on my setup, part reliability, part quality, design minimalism and ease of use: size each part to its loads, put material and features only where the job needs them, and compare options at their best, never at placeholder sizes.  
   - Keep fit features at least 1 mm above the bed (elephant foot).  
   - Keep overhangs within 45 degrees.  
   - Fit it on the plate, clearing the excluded corner.  
   - Run loads along the layers.  
   - Each concept render notes how every part prints.  
2. Edges  
   - Every edge gets a fillet, outside and inside corners alike, for looks; overhanging horizontal edges follow the chamfer bullet below.  
   - Size: start at about a third of the thinnest feature meeting at the edge, at least 1 mm on vertical edges and 3 layers on horizontal edges, so it prints as a curve and not a step.  
   - Matching corners: corners that match by position or role (e.g. a face's four outer corners, or a symmetrical profile's top and bottom) get the same profile and size, all chamfer-plus-fillet if one needs it, unless a design reason calls for another (a dp exception).  
   - Inside/outside pairs: where an inside corner sits behind an outside corner across a wall, the inside fillet is the outside fillet minus the wall thickness, so both curves share a center and the wall stays one thickness around the bend. Size the outside fillet up if needed so the inside one reaches the starting size above; smaller looks square. Only where both legs have the same wall; read both legs' widths, and what the outer curve hits, from the build script.  
   - Limits: make it smaller where it would thin a wall below its bead count or cut into a fit, mating or contact face; leave sharp, or size by the fit, any edge whose shape does the work (snap edges, wire notches, seating faces), each a dp exception.  
   - Overhanging horizontal edges: a 45-degree chamfer with a fillet where the chamfer meets the wall, never a plain fillet.  
   - Images: pictures after the first, made while iterating, may leave fillets out if they slow rendering, and say so on the image; the picture before a build question shows every fillet as it will print.  
3. Flush surfaces  
   - Make surfaces that meet flush wherever the design allows: raise the lower surface (or lower the higher one) to remove the step.  
   - Where a step has to stay for a design reason (saving filament or time isn't one; that's the Goal settling a conflict, so say so), chamfer its edge so it slopes toward the higher surface and fillet the chamfer's corners (a dp exception).  
4. Bridges and supports  
   - First, design bridges away or shorten them:  
     - Peaked roof: two 45-degree slopes meeting at a point, so nothing bridges.  
     - Chamfered roof: 45-degree chamfers leaving a short flat, so the bridge is short.  
     - One-sided roof: ramp it at about 45 degrees.  
   - Bridges and spots over air that are left are allowed where the design needs them; a floating region isn't one (below).  
     - Seen surfaces: no one-sided bridges or flat roofs over a gap.  
     - Hidden surfaces (e.g. a bore's ceiling): a bridge is fine, with room for sag so it doesn't affect the fit.  
   - Supports, in order of preference: none; bridge supports; painted supports.  
   - Bridge supports: triangle walls modeled into the part, in the same filament, from the bed (or the surface below) up to the underside, spaced so every bridge between them is no longer than a clean bridge span (10 mm until bridge tests set it). The tip touching the part is one line wide and one layer tall, so it snaps off.  
   - Painted supports: only where bridge supports can't work; as little as possible, painted by hand in the 3mf, never automatic supports.  
   - Before calling a design ready to build (tests included), slice a scratch 3mf of it and check the slicer's warnings, that every layer region rests on the layer below (dpcheck's island check), and each layer marked Overhang wall or Bridge against these bullets. A floating region (the slicer's floating-cantilever warning, or a strip that starts over air as a hairline) fails: the slicer skips it until it's a bead wide, then lays full lines over air. Design it away (e.g. cut the strip so a 45° face runs through) or support it; a card may offer keeping one as a dp exception only beside those options, each pictured and priced.  
5. Critical widths in X-Y (trial)  
   - Put any width that sets a fit, or that a test piece steps through, in X-Y rather than Z.  
   - Why: a width in Z is limited to whole layers.  
   - Trial: each time this changes a design, add a line under "dp trials" in its product doc (date, the width, and what it changed, e.g. the orientation) and mention it in that thread, so I can judge it in use.  
6. Clearance (gap per side; my setup, PETG High Flow)  
   - Friction grip (stays put): 0.1 mm (Measured: my use).  
   - Snug, removable with moderate effort: 0.2 mm (Measured: my use).  
   - Slip fit (slides freely): 0.5 mm (Estimated: my pick for the cache pot, untested).  
   - Other materials: use these as a starting point and mark them Estimated; a fit test piece's result replaces them for that product and material.  
7. Test first  
   - A new joint, fit or grip gets a test piece printed in the final part's orientation, filament and process settings (each joint at 2 or 3 clearances, starting from dp 6), or a test pair, before the full set is built.  
8. Readable test pieces  
   - Make each step identifiable by its position from a marked end.  
   - Labels are only a backup.  
9. Load-bearing parts  
   - Before recommending geometry or print orientation, get a design load from me (including what knocks, pulls or levers the part in use) and a safety factor.  
10. Human error  
   - Design every part so it's hard to print, assemble or use wrong, and so a mistake that does happen does as little harm as possible.  
   - For example: joints that fit only one way, orientation or assembly marks that show which way a part goes, fits that still work if a print comes out slightly off, and no step that relies on remembering a detail written nowhere on the part or in its doc.  
11. Joined parts  
   - Parts glued or otherwise fixed together for good count as one object. Where a snap or friction fit is involved, confirm with me whether the joint is permanent before treating the parts as one object or as separate.  
   - On a joined object, apply Edges (dp 2) and Flush surfaces (dp 3) as if it were one piece: a seam isn't an edge and faces that meet at a seam are made flush.  
   - Everything about printing stays per printed part, in that part's own print direction: orientation, overhangs, bridges and supports, plate fit, grid lock and bead counts.  
   - Put seams on flat, straight stretches, clear of every curve, so no curve is split between parts. Where a curve must cross a seam, neither part may be left with an edge thinner than one bead at the cut; list it under "dp exceptions".  
   - The joint still counts as a joint: it gets its clearance (dp 6), a test piece (dp 7) and a strength check as its own load path (dp 9).  
   - Seams are flush, with no deliberate groove. If a test print shows a visible lip, tell me before changing the seam.  
12. Grid lock  
   - Every dimension that runs in Z (heights, floors, slot tops and bottoms, height-range boundaries, fillet and chamfer ends) sits on the file's layer grid.  
   - Every horizontal thickness that prints as whole beads (walls, bands) is sized for a whole number of beads, with line widths set so the G-code's ; LINE_WIDTH shows that count on every layer (learnings/walls). A single-bead wall may be a little thinner than its line width, so Arachne keeps one bead.  
   - When a value I give isn't on the grid, propose the nearest grid values with their layer or bead counts, say which is closest, and use my pick. Never store or build an off-grid value that isn't a dp exception.  
   - Run this check on the whole model, shared values included (feet, lips, chamfers, curve ends), whenever this principle or a design value changes and before calling a design ready to build.
