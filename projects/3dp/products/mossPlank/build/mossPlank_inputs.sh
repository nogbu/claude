#!/bin/bash
# mossPlank picture scripts' input folder: builds 3.5inPot_rev10.2.3mf and 3.5inInsert_rev4.3mf from the nursery-pots build
# scripts and copies nurseryPots_lib.py beside them, reusing them when present.
# Usage: bash mossPlank_inputs.sh [folder]   then: python3 mossPlank_[x]_pic.py [folder] [out png]
set -e
OUT=$(mkdir -p "$1" && cd "$1" && pwd); NP=/home/user/claude/projects/3dp/products/nursery-pots/build
cp "$NP/nurseryPots_lib.py" "$OUT/"
for f in 3.5inPot_rev10.2 3.5inInsert_rev4; do
  [ -f "$OUT/$f.3mf" ] || (cd "$OUT" && python3 "$NP/$f.py" "$OUT" > /dev/null && [ -f "$OUT/$f.3mf" ] || mv "./$f.3mf" "$OUT/" 2>/dev/null || true)
done
ls "$OUT"
