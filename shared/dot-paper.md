---
about: My 5 mm dot-grid paper and measuring photos of it (dotgrid.py)
read-when: before measuring from a photo on dot paper
readonly: no
---
dot-paper
Short name: dot-paper. The user's dot-grid paper and how Claude measures from photos of it. Read before measuring anything from a photo taken on it.

- Paper: dot grid, 5.00 mm pitch, gray dots about 0.55 mm across (Estimated 2026-10-06: a steel ruler in PXL_20261006_011047463 put the pitch at 4.96 to 5.02 mm; 5.00 is the standard). Brand and sheet size not recorded. The user has plenty and uses it for sketches, traced outlines and objects laid on it to measure.
- How Claude measures: shared/scripts/dotgrid.py PHOTO [--outline X0 Y0 X1 Y1] finds the dots, fits each to its grid position and writes the photo flattened into paper coordinates at 20 px/mm (PHOTO_flat.png), so tilt and zoom drop out. --outline fits a rounded rectangle (length, width, corner radius) to the darkest line inside that box, in mm on the flat image. Check the grid error it prints: a median under 0.05 of a cell is good.
- Accuracy (2026-10-06, one photo): drawn lines land within 0.16 mm (median) of the fitted shape; the scale is good to about 1% until a printed check confirms the pitch.
- Measuring things on it:
  - Only what lies in the paper's plane is to scale. An object's top is closer to the camera: about 1% bigger per 3 mm of height at 30 cm (learnings/measuring). Measure footprints, or trace them.
  - A traced outline runs outside the object by the pen's offset: 0.45 to 0.75 per side with the user's pen around the Pixel 10 Pro (Measured 2026-10-06). Take it off, or trace a known-size object in the same session to set it.
  - Pen lines and objects must be darker than the dots, at least 3 x 3 dots must show around what's measured, and the sheet must lie flat (no curl at a notebook's spine).
- Photo routine: straight down, about 30 cm, 1x (no zoom), even light with no glare on the dots. A rigid ruler in frame is optional and gives a scale check.
- Filing: like any measurement photo (build-3dp skill): copy it to /mnt/project-files/photos/[subject]/ and log it in that subject's photos index.
