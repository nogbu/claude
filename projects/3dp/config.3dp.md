config.3dp  
Short name: 3dp

Cardinal sources  
Project theme: launching and running a small business that sells 3D printed consumer products, designed and optimized for printing on Bambu Lab printers.  
- Any data source that explicitly references 3D printing with a Bambu P1S or a Bambu X1C.  
- Any data source that explicitly references starting and running a 3D printing business.  
- Any data source that explicitly references designing and optimizing objects for 3D printing, particularly consumer products.

Rules  
- Setup (assume unless I say otherwise):
  - Bambu Lab P1S with an original AMS (not the AMS 2 Pro), so multicolor, multimaterial and same-layer inlay prints are available.
  - 0.6 mm hardened steel nozzle, an upgrade over the stock stainless nozzle. It can print abrasives such as PETG Carbon Fiber; the extruder gears may not be hardened (learnings/printer).
  - I slice in OrcaSlicer.
  - Primary filament is PETG High Flow (Bambu data sheet, Listed 2026-10-01: bending strength 64 MPa along layers, 48 across; stiffness 2,050 MPa). Also on hand: Bambu PETG Basic, JAYO PETG Translucent, PETG Carbon Fiber, 94A TPU, Bambu Matte PLA (white, Bone White and black), and Bambu Support For PLA/PETG.
- Requirements every recommendation is checked against (CLAUDE.md, Answers): strength and load, accuracy, risk of human error, printability on my setup, and cost, plus any directive from the conversation.
- Terms: "Default settings" (printer or process) means OrcaSlicer's stock presets "Bambu Lab P1S 0.6 nozzle" and "0.30mm Standard @BBL X1C 0.6 nozzle", in the Orca version orca-setup.sh installs; pull values from Orca with orcadefaults.py, never from memory. "My printer settings" means the default printer settings plus the differences in printer-settings; "my process settings" means process-settings. These are JSON in projects/3dp/data/; look a setting up with shared/scripts/lookup.py. A 3mf can customize them for one model. "The printer" means only the physical P1S; never shorten "printer settings" to "printer."
- Product scope: treat each new design or question on its own; tie it to other products or content docs (e.g. the rail, wire shelf, pots, lights, plants) only when I bring them in or a Product rule or read-when names them. A reference doc for where a part goes (e.g. unicoly) applies once I say the part goes there.
