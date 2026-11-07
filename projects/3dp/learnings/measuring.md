---
about: Measuring and photo-reading learnings
read-when: before planning a measurement, or taking, requesting or measuring from a photo
readonly: no
---
learnings.measuring

- Measuring hierarchy, from least to most error-prone: design the measurement out; a printed pass/fail test piece; a photo on a printed reference sheet with corner circles, which Claude measures; calipers. Phone 3D-scanning apps are off by 1–5 mm and fail on thin, dark or shiny parts.

- Photo measurements: the scale must lie in the feature's plane. A scale on top of a feature is closer to the camera: at the phone's usual 0.25–0.35 m, every 3 mm of height difference changes the scale by about 1%, and the photo's EXIF SubjectDistance gives the distance to correct with. A tape measure bows toward the camera, so pitches measured against a tape came out 1–3 mm short over 35 mm; use a rigid ruler or a printed scale for pitch, and hook the tape over the feature for lengths. A tape on the UNICOLY back wall instead of the slotted strip gave slot heights about 7 mm off (2026-09-26).

- Photo reading: identify parts by their physical attributes (thickness, where they end, what they cross), never by their orientation in the frame. Reading the thin lines in one photo as rods cost a round of questions (2026-09-30).

- Printed marker targets (2026-10-02, calibration rig; the cell-width and post figures are Estimated from simulated photos): ArUco markers inlaid with the 0.6 mm nozzle need cells at least 3 beads wide (1.86 mm at the 0.62 mm line width); in simulated phone photos every 3-bead marker read, but only 13–18 of 27 with 2-bead cells. Straight-down photos of markers on one flat plane can't pin down the camera's distance, so sizes 100 mm above them can be off by 0.39–1.14 mm per 100 mm; markers on two 30 mm posts cut that to about 0.05 mm. OpenCV isn't preinstalled in thread workspaces; pip install opencv-contrib-python for ArUco (checked 2026-10-03). Detector settings for printed markers (Measured 2026-10-03, rev1.1 test strip): run OpenCV's ArUco detector on the photo after a 5 px median blur, with errorCorrectionRate 1.0, perspectiveRemoveIgnoredMarginPerCell 0.13, adaptiveThreshWinSizeMax 53, adaptiveThreshWinSizeStep 6 and polygonalApproxAccuracyRate 0.05. The defaults found 9 of 27 markers across 9 photos; these settings found all 27 with no wrong IDs. Throw out any ID that isn't on the board's layout.

- Check the camera data first (2026-10-03): the rev1.1 strip photos were taken at about 11 cm with 2x digital zoom (EXIF SubjectDistance 0.105–0.141 m, DigitalZoomRatio 1.97), not at the 30 cm and 1x asked for. Read SubjectDistance and DigitalZoomRatio before measuring, and say when a photo doesn't match the routine.  
- Light glare (2026-10-04, calibration rig, inference from the lighting research): with the lens at H above a flat area of half-width a, a light at height z and distance r from the lens axis puts no glare on glossy pieces in that area only if r > a(1 + z/H). Ceiling lights count: one 2 m up within about 830 mm of the lens axis glares at a 108.5 mm half-width.  
