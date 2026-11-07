#!/bin/sh
# Plant tag picture and text checks. Run in a scratch folder: unzips the 3mf, fetches Overpass ExtraBold (wght 800), copies these scripts.
set -e
D=$(dirname "$0")
python3 -m pip install -q trimesh manifold3d shapely scikit-image fonttools mapbox-earcut
mkdir -p src fonts && unzip -o -q /mnt/project-files/uploads/hearth/2d275a95-3333-41da-b5db-5e6d8ff8cf77 -d src
[ -f fonts/ov800.ttf ] || { curl -sSL -o fonts/ov800.woff https://cdn.jsdelivr.net/npm/@fontsource/overpass@5.0.8/files/overpass-latin-800-normal.woff
  python3 -c "from fontTools.ttLib import TTFont; f=TTFont('fonts/ov800.woff'); f.flavor=None; f.save('fonts/ov800.ttf')"; }
cp "$D"/*.py .
