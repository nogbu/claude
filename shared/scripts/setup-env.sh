#!/bin/bash
# Started in the background by the session-start hook: installs the libraries the build and scratch scripts
# need, then, in a 3dp thread or when run as "setup-env.sh orca", OrcaSlicer at /opt/orca
# (projects/3dp/scripts/orca-setup.sh, 381 MB), once per container.
# Log: /tmp/setup-env.log; /tmp/setup-env.done appears when the run finished.
R=$(cd "$(dirname "$0")/../.." && pwd)
orca=$1; [ "$(tr -d '[:space:]' < /mnt/project-files/.project 2>/dev/null)" = 3dp ] && orca=orca
[ -f /tmp/setup-env.done ] && { [ "$orca" != orca ] || [ -x /opt/orca/slice ]; } && exit 0
python3 -m pip install -q numpy scipy shapely trimesh mapbox_earcut manifold3d rtree matplotlib contourpy opencv-contrib-python-headless pillow networkx lxml \
  && { [ "$orca" != orca ] || bash "$R/projects/3dp/scripts/orca-setup.sh"; } && touch /tmp/setup-env.done
