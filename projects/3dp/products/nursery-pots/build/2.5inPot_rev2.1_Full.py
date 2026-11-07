#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.1_Full.3mf (nursery-pots, 3dp project): one plate with 9 instances of
the 2.5in rev2 pot in a 3 x 3 grid, 5 mm gaps (76 mm pitch), centered on the 256 mm bed.
The front-left pot clears the bed's excluded area (0-18 x 0-28 mm) by about 6.1 mm.
Needs beside it: 2.5inPot_rev2.py (the pot design), nurseryPots_lib.py and
nurseryPots_settings_base.json (all used unchanged).

Instances are copies of one object, so the mesh, seam paint, object settings, height ranges
and fan ramp are rev2's and shared by all nine. Copy numbers, seen from the front of the printer:
    copy 7 back-left     copy 8 back-center     copy 9 back-right
    copy 4 middle-left   copy 5 center          copy 6 middle-right
    copy 1 front-left    copy 2 front-center    copy 3 front-right
"""
import importlib.util
import io
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('pot_rev2', os.path.join(HERE, '2.5inPot_rev2.py'))
pot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pot)
lib = pot.lib

NAME = '2.5inPot_rev2.1_Full'
PITCH = 76.0             # 71.0 mm lip + 5 mm gap
CENTER = 128.0           # bed center (256 x 256 mm)
POS = [(CENTER + (c - 1) * PITCH, CENTER + (r - 1) * PITCH) for r in range(3) for c in range(3)]


def _thumbs():
    """plate_1.png (512) and plate_1_small.png (128): top view of the nine lips on the bed."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        out = {}
        for name, px in (('plate_1.png', 512), ('plate_1_small.png', 128)):
            fig = plt.figure(figsize=(px / 100, px / 100), dpi=100)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_facecolor('#e8e8e8')
            for x, y in POS:
                ax.add_patch(plt.Circle((x, y), pot.R_LIP, color='#6fa8dc'))
            ax.set_xlim(0, 256); ax.set_ylim(0, 256)
            ax.set_aspect('equal'); ax.axis('off')
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100)
            plt.close(fig)
            out[name] = buf.getvalue()
        return out
    except Exception:
        return {}


def add_instances(path):
    """Turn the single build item that lib.write_3mf writes into nine instances at POS."""
    z = lib._fmt(pot.H / 2.0)
    with zipfile.ZipFile(path) as zf:
        items = [(i, zf.read(i.filename)) for i in zf.infolist()]
    files = {i.filename: d for i, d in items}

    root = files['3D/3dmodel.model'].decode()
    pat = re.compile(r' *<item objectid="4" [^>]*/>\n')
    assert len(pat.findall(root)) == 1
    new_items = ''.join(
        '  <item objectid="4" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 %s %s %s" printable="1" auto_drop="1"/>\n'
        % (lib._uuid(NAME, 'item' if k == 0 else 'item%d' % k), lib._fmt(x), lib._fmt(y), z)
        for k, (x, y) in enumerate(POS))
    root = pat.sub(lambda m: new_items, root)

    ms = files['Metadata/model_settings.config'].decode()
    pat_mi = re.compile(r'    <model_instance>\n.*?    </model_instance>\n', re.S)
    assert len(pat_mi.findall(ms)) == 1
    new_mi = ''.join(
        '    <model_instance>\n'
        '      <metadata key="object_id" value="4"/>\n'
        '      <metadata key="instance_id" value="%d"/>\n'
        '      <metadata key="identify_id" value="%d"/>\n'
        '    </model_instance>\n' % (k, 300 + k) for k in range(len(POS)))
    ms = pat_mi.sub(lambda m: new_mi, ms)
    pat_as = re.compile(r'   <assemble_item object_id="4" instance_id="0" [^>]*/>\n')
    assert len(pat_as.findall(ms)) == 1
    new_as = ''.join(
        '   <assemble_item object_id="4" instance_id="%d" transform="1 0 0 0 1 0 0 0 1 %s %s %s" offset="0 0 0" />\n'
        % (k, lib._fmt(x), lib._fmt(y), z) for k, (x, y) in enumerate(POS))
    ms = pat_as.sub(lambda m: new_as, ms)

    files['3D/3dmodel.model'] = root.encode()
    files['Metadata/model_settings.config'] = ms.encode()
    files.update(_thumbs())
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, _ in items:
            zf.writestr(i, files[i.filename])


def main(out_dir='.'):
    M, info = pot.build_mesh()
    painted = lib.paint_seam(M, pot.PAINT_SPAN)
    info['painted_triangles'] = int(painted.sum())
    obj = lib.POT_OBJECT_SETTINGS + [('outer_wall_speed', lib._fmt(pot.OUTER_WALL_SPEED)),
                                     ('outer_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH)),
                                     ('inner_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH))]
    path = os.path.join(out_dir, NAME + '.3mf')
    lib.write_3mf(path, M, NAME, pot.H, painted, obj, pot.layer_ranges(), {}, fan_ramp=False,
                  plate_name=NAME.replace('_', ' '))
    pot.replace_entry(path, 'Metadata/custom_gcode_per_layer.xml', pot.fan_ramp_xml())
    add_instances(path)
    info['path'] = path
    info['instances'] = POS
    return info


if __name__ == '__main__':
    print(main())
