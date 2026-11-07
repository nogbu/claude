#!/bin/bash
# Rail concept models and pictures (layout A, concept C for comparison, the slot-fit test piece and its groove fix), in one step.
# Copies the scripts into out/ beside this file, runs them there (STLs land in out/A, out/C and out/T, pictures in
# /mnt/project-files/images), and skips the run when out/.fingerprint matches the scripts' hash.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../../../../.." && pwd)"
OUT="$HERE/out"; mkdir -p "$OUT"
SCRIPTS="rail_concepts.py rail_compare.py rail_clip_install.py rail_clip_grip.py rail_slottest.py rail_slottest_pics.py rail_slotfit_lip.py rail_slotfit_hook.py"
# install writes glass.stl, which grip reads; slottest writes T/, which its pics read; the slotfit pictures also read ../slotFit_rev1.py
FP=$(cd "$HERE" && cat $SCRIPTS ../slotFit_rev1.py "$REPO/projects/3dp/scripts/render3d.py" | sha256sum | cut -c1-16)
if [ -f "$OUT/.fingerprint" ] && [ "$(cat "$OUT/.fingerprint")" = "$FP" ]; then echo "up to date ($FP)"; exit 0; fi
python3 -c "import manifold3d, trimesh, shapely, matplotlib" 2>/dev/null || python3 -m pip install -q manifold3d trimesh shapely matplotlib
for s in $SCRIPTS; do cp "$HERE/$s" "$OUT/"; done
cd "$OUT"
for s in $SCRIPTS; do
  python3 "$s" 2>&1 | grep -v Warning || true
  [ "${PIPESTATUS[0]}" = 0 ] || { echo "failed: $s"; exit 1; }
done
echo "$FP" > "$OUT/.fingerprint"
