# 3dp rules

Rules for the 3dp project only. The shared rules are in the repo's top-level CLAUDE.md.

Being brought over from nogbu/claude.old, starting 2026-11-09. Rules get added here one at a time as Nwani approves them.

## Cardinal sources
Project theme: launching and running a small business that sells 3D printed consumer products, designed and optimized for printing on Bambu Lab printers.  
- Any data source that explicitly references:  
  - 3D printing with a Bambu P1S or a Bambu X1C.  
  - starting and running a 3D printing business.  
  - designing and optimizing objects for 3D printing, particularly consumer products.

## Rules
- Setup (assume unless I say otherwise):
  - Bambu Lab P1S with an original AMS (not the AMS 2 Pro), so multicolor, multimaterial and same-layer inlay prints are available.
  - 0.6 mm hardened steel nozzle, an upgrade over the stock stainless one (abrasive filaments: learnings/printer).
  - I slice in OrcaSlicer.
  - Primary filament is PETG High Flow (Bambu data sheet, Listed 2026-10-01: bending strength 64 MPa along layers, 48 across; stiffness 2,050 MPa). Also on hand: Bambu PETG Basic, JAYO PETG Translucent, PETG Carbon Fiber, 94A TPU, Bambu Matte PLA (white, Bone White and black), and Bambu Support For PLA/PETG.
- Before showing a design, Claude checks that anything that slides into it clears every part, that each number Nwani settled holds in the model (2026-11-15), and that every requirement Nwani settled in words, like "mirror the floor", holds in the model too (2026-11-15).
- Before showing a design, Claude renders a close-up of each place a new feature meets an older one and looks for any gap or step there (2026-11-15). When a close-up finds a gap or step in work Nwani has already seen, Claude shows it and asks on a card before fixing it. A gap or step Claude's own unshown change made is fixed before showing (2026-11-15).
- A design complaint is an example of a larger issue, not the full list of fixes. Claude finds every place in the model with the same kind of problem and fixes it without a card, overriding for design complaints the shared rule on asking before changing a part Nwani's words didn't name and the close-up card rule above. Numbers and requirements Nwani settled still hold. When showing the result, Claude lists each change. Untested trial: if Claude again fixes only the named spot, it offers to remove this rule (Nwani 2026-11-18, card "Save the rule": "you are treating my feedback as a complete and comprehensive list of corrections that need to be made, instead of a handful of examples of the larger issue, which is what it is.").
- Before changing geometry from words that name a part, Claude reads that part's history and sends the planned change to the reviewer before building it (2026-11-15).
- Every 3mf Claude builds uses Nwani's own OrcaSlicer printer, process and filament profiles, copied from Nwani's newest own 3mf in Project Files, not Bambu's system presets (2026-11-18).
