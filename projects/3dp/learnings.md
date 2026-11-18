# 3dp learnings

Settled facts for 3dp only. Facts every project shares go in the repo's top-level `learnings.md`.

One fact per line, with where it came from and when it was confirmed:
- 3mf app tags: OrcaSlicer saves 3mfs with an <metadata name="Application"> tag naming BambuStudio as a format tag (2.4.2 writes BambuStudio-02.06.00.51, 2.5.1 writes BambuStudio-02.08.01.55). The app that saved a file is the <metadata name="OrcaSlicer"> tag. Nwani has no Bambu Studio and does everything in OrcaSlicer (Nwani 2026-11-18, 3mfs/6inPot_rev3.1_Slot2mm.3mf and 3mfs/defaults.3mf).
- Nwani's OrcaSlicer is 2.5.1. Nwani's own profiles are in 3mfs/defaults.3mf in Project Files: printer "P1S 0.6mm", process "0.6mm default" (0.3 layers, 0.62 line width, 2 walls, 15% adaptive cubic), filament "Bambu PETG Translucent @BBL X1C 0.6 nozzle" plus "Bambu Support For PLA/PETG @BBL X1C", Textured PEI Plate. Build 3mfs on top of that file (Nwani 2026-11-18, "ingest and update your records"). The older "0.60mm default" in the pot 3mfs isn't a process Nwani's Orca has, so it opened as 0.30mm Standard (Nwani's screenshot 2026-11-18).
