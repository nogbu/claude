---
about: Cache pot for the nursery pots, with a built-in drip tray
readonly: no
---
cache-pot  
Short name: cache-pot

Current state  
- Latest rev: none built. Concept drawn 2026-10-02 (cachePot_concept.png, a section through the 3.5in pot). The 3.5in size is designed first; every nursery pot size (2.5in, 3.5in, 4.5in, 6in) will get one.

Design values (3.5in; pot figures Listed from nursery-pots, 3.5in rev10.2 model)  
- Fits: 3.5in pot rev10.2: height 105.12 mm, lip Ø 96.14 mm, base Ø 60 mm, drip groove under the floor at Ø 47–50 mm (Ø 47–51 mm from the next pot build, agreed 2026-10-03; its inner edge, which the collar depends on, doesn't move).  
- Shape: minimalist, round, straight vertical walls.  
- Inner diameter Ø 97.14 mm: 0.5 mm clearance per side around the pot's lip. The pot tapers, so it touches the cache wall only at the lip.  
- Rim 3 mm above the pot's lip. Overall height = floor + collar + 105.12 mm + 3 mm (floor and collar heights still open).  
- Collar: a raised ring, Ø 40 mm, that the pot rests on. About 5 mm tall (Estimated; the grid height is still open). Its outside stays inside the drip groove's inner edge (Ø 47 mm), so water dripping off the groove lands in the tray, not on the collar.  
- Finger hole: Ø 25 mm through the collar and floor, for pushing the pot up and out.  
- Drip tray: the ring between the collar and the wall. It holds about 30 mL before water reaches the pot (Estimated: about 61.5 cm² of floor, so about 6 mL per mm of collar height, a little less at the chamfer corner; inference).  
- Bottom outer edge: a 10 mm 45° chamfer at the base, then a 10 mm round where the chamfer meets the wall (as drawn in cachePot_concept.png).  
- Filament: Bambu Matte PLA (color still open).

Settings changes (printer, process and filament changes the 3mf makes)  
- None yet.

Build script  
- None yet. Concept drawing: projects/3dp/products/cache-pot/build/cachePot_concept.py ( needs numpy and matplotlib). It redraws cachePot_concept.png as sent 2026-10-02, with its placeholders: cache inner Ø 96.8 mm, 2.0 mm wall, 2.0 mm floor, 8.0 mm collar.

Decisions and why  
- Collar around the finger hole (2026-10-02): overflow from the slots runs down the pot wall, around the foot curve and under the floor. The drip groove stops it creeping farther in, so it drips off the groove into the tray. The collar keeps those drips and the tray water away from the finger hole (inference; untested).  
- Clearance 0.5 mm per side (2026-10-02): my pick, chosen over a rim fit test piece.  
- Tray about 30 mL (2026-10-02): enough for small spills, and it keeps the cache pot short. Chosen over 70 and 140 mL.  
- Finger hole Ø 25 mm, collar Ø 40 mm (2026-10-02): fits a thumb or two fingers, and the collar is 7 mm smaller than the groove's Ø 47 mm. Chosen over Ø 20/36 and Ø 30/42.  
- Matte PLA (2026-10-02): chosen over PETG High Flow (recommended because the tray must be watertight) and PETG Transparent.

Open questions  
1. Wall thickness, in whole beads at 0.62 mm (my process settings): 1.24 mm (2 beads), 1.86 mm (3, recommended) or 2.48 mm (4). Asked 2026-10-02 and not yet answered.  
2. Layer height. That sets the collar's grid height (at 0.3 mm layers: 4.8 mm, 16 layers, or 5.1 mm, 17 layers) and the floor thickness.  
3. Matte PLA color: white, Bone White or black. Black is low, so use it only on surfaces that show, with another color behind it.  
4. Watertight tray in Matte PLA: untested, since all the pots' waterproofing settings are for PETG. Water-test the first print.  
5. Past about 30 mL, tray water rises over the collar top and can run out the finger hole (inference). Check in use whether 30 mL is enough.  
6. Other sizes: the 2.5in pot has a flat floor with no drip groove (rev2), so its cache pot needs a groove added to the pot or a different fix. The 4.5in and 6in grooves' inner edges sit 6.5 mm inside the base edge (unchanged by the 2026-10-03 groove change), so their collars scale with them.

Agreed changes (rev1)  
- Every design value above was agreed 2026-10-02. None of it is built yet.  
