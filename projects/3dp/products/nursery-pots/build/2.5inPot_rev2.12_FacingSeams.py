#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.12_FacingSeams.3mf (nursery-pots, 3dp project): rev2.11_PlateRetract's two-pot
plate (2.5in rev2 cut flat at 40.68 mm; 0.2 mm z-hop Spiral Lift, 0.8 mm retraction, 260 C, pressure
advance off, 8 s minimum layer time) with the two copies turned so their seams face each other.

Only change from rev2.11 (agreed 2026-10-02): copy 1 (left, x 90) is turned 90 deg clockwise, so its
seam faces +X (toward copy 2), and copy 2 (right, x 166) is turned 90 deg counterclockwise, so its seam
faces -X (toward copy 1). Positions, mesh, seam paint, settings, height ranges and fan ramp are rev2.11's.
Why: in rev2.11's G-code both seams face the back, so each jump between the pots runs along the wall
top for 6.2 mm (copy 1) and 7.1 mm (copy 2) next to the seam, on the side facing the other pot, which
is where the patches were. With the seams facing each other the jump is 21 mm and meets each seam
head-on (checked in a scratch slice, Orca 2.4.2). The seam setting stays Back, so the seams sit
0.4-1.1 mm right (copy 1) and 0.7-2.5 mm left (copy 2) of center between the slots, seen from outside
(rev2.11: 0.1-0.5 mm left); accepted for this test (2026-10-02).
Copies seen from the front of the printer: copy 1 left, copy 2 right.

Needs beside it: 2.5inPot_rev2.11_PlateRetract.py, 2.5inPot_rev2.9_SoloRetract.py,
2.5inPot_rev2.6_SoloControl.py, 2.5inPot_rev2.5_LayerTimeTest.py, 2.5inPot_rev2.2_SeamTest.py,
2.5inPot_rev2.1_Full.py, 2.5inPot_rev2.py, nurseryPots_lib.py and nurseryPots_settings_base.json
(all used unchanged).
"""
import importlib.util
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(mod, fname):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


pr = _load('plateretract', '2.5inPot_rev2.11_PlateRetract.py')
lib = pr.lib

NAME = '2.5inPot_rev2.12_FacingSeams'
# 3mf transforms are row-major 3x4 (point row vector times matrix): 'm00 m01 m02 m10 m11 m12 m20 m21 m22'.
# 90 deg clockwise maps +Y to +X; 90 deg counterclockwise maps +Y to -X.
TURN = {lib._fmt(pr.POS[0][0]): '0 -1 0 1 0 0 0 0 1',    # copy 1, x 90: seam to +X
        lib._fmt(pr.POS[1][0]): '0 1 0 -1 0 0 0 0 1'}    # copy 2, x 166: seam to -X


def turn_copies(path):
    """Replace the identity rotation of each copy's build item and assemble item with its turn."""
    with zipfile.ZipFile(path) as zf:
        items = [(i, zf.read(i.filename)) for i in zf.infolist()]
    files = {i.filename: d for i, d in items}
    y = lib._fmt(pr.POS[0][1])
    for entry in ('3D/3dmodel.model', 'Metadata/model_settings.config'):
        text = files[entry].decode()
        for x, rot in TURN.items():
            old = 'transform="1 0 0 0 1 0 0 0 1 %s %s ' % (x, y)
            assert text.count(old) == 1, (entry, old, text.count(old))
            text = text.replace(old, 'transform="%s %s %s ' % (rot, x, y))
        files[entry] = text.encode()
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, _ in items:
            zf.writestr(i, files[i.filename])


def main(out_dir='.'):
    pr.NAME = NAME          # rev2.11's main and add_instances use the module name for the file,
    info = pr.main(out_dir)  # plate name and instance UUIDs
    turn_copies(info['path'])
    info['turns'] = TURN
    return info


if __name__ == '__main__':
    print(main())
