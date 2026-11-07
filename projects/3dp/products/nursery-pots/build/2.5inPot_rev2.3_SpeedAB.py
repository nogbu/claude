#!/usr/bin/env python3
"""Builds 2.5inPot_rev2.3_SpeedAB.3mf (nursery-pots, 3dp project): two 2.5in rev2 pots side by
side (5 mm gap, 76 mm pitch, centered), to test whether outer wall speed is why plate seams are
rougher than the solo pot's. Both pots get rev2.2_SeamTest's filament overrides (z-hop 0.6 mm,
retraction 0.8 mm).

- Pot A (left, as seen from the front): rev2 speeds, as on the plates: outer wall 28 mm/s in
  the floor and reservoir height ranges, 34 mm/s above the slot band.
- Pot B (right): the speeds the solo pot actually printed at, since the 8 s minimum layer time
  slows it (median in the solo rev2 G-code: 24.4 mm/s reservoir, 27.6 mm/s above the band):
  24 mm/s in the floor and reservoir ranges, 27 mm/s above the band.
The slot band (40 mm/s) and everything else are the same on both. Pot B is a second object
(per-object settings can't differ between instances), with its own copy of the mesh and paint.
Needs beside it: 2.5inPot_rev2.py, 2.5inPot_rev2.1_Full.py, 2.5inPot_rev2.2_SeamTest.py,
nurseryPots_lib.py and nurseryPots_settings_base.json (all used unchanged).
"""
import importlib.util
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('seamtest', os.path.join(HERE, '2.5inPot_rev2.2_SeamTest.py'))
st = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(st)
full, pot, lib = st.full, st.pot, st.lib

NAME = '2.5inPot_rev2.3_SpeedAB'
NAME_B = NAME + '_B'
SPEED_A = (28, 34)       # (floor + reservoir ranges, object outer wall) = rev2
SPEED_B = (24, 27)
POS_A = (full.CENTER - full.PITCH / 2, full.CENTER)
POS_B = (full.CENTER + full.PITCH / 2, full.CENTER)


def add_object_b(path):
    with zipfile.ZipFile(path) as zf:
        items = [(i, zf.read(i.filename)) for i in zf.infolist()]
    files = {i.filename: d for i, d in items}
    order = [i.filename for i, _ in items]
    z = lib._fmt(pot.H / 2.0)
    mesh_a = '3D/Objects/%s.model' % NAME
    mesh_b = '3D/Objects/%s.model' % NAME_B

    # mesh B: same mesh and paint, mesh object id 5
    mb = files[mesh_a].decode().replace('<object id="3" ', '<object id="5" ', 1)
    mb = mb.replace(lib._uuid(NAME, 'part'), lib._uuid(NAME_B, 'part'), 1)
    files[mesh_b] = mb.encode()
    order.insert(order.index(mesh_a) + 1, mesh_b)

    rels = files['3D/_rels/3dmodel.model.rels'].decode()
    rels = rels.replace('</Relationships>',
                        ' <Relationship Target="/%s" Id="rel-2" Type="http://schemas.microsoft.com/'
                        '3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>' % mesh_b)
    files['3D/_rels/3dmodel.model.rels'] = rels.encode()

    root = files['3D/3dmodel.model'].decode()
    obj_b = ('  <object id="6" p:UUID="%s" type="model">\n   <components>\n'
             '    <component p:path="/%s" objectid="5" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n'
             '   </components>\n  </object>\n' % (lib._uuid(NAME_B, 'object'), mesh_b,
                                                  lib._uuid(NAME_B, 'component')))
    root = root.replace(' </resources>', obj_b + ' </resources>', 1)
    root = root.replace(' </build>', '  <item objectid="6" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 %s %s %s" '
                        'printable="1" auto_drop="1"/>\n </build>'
                        % (lib._uuid(NAME_B, 'item'), lib._fmt(POS_B[0]), lib._fmt(POS_B[1]), z), 1)
    files['3D/3dmodel.model'] = root.encode()

    ms = files['Metadata/model_settings.config'].decode()
    oa = re.search(r'  <object id="4">\n.*?  </object>\n', ms, re.S).group(0)
    ob = (oa.replace('<object id="4">', '<object id="6">')
            .replace('<part id="3" ', '<part id="5" ')
            .replace('value="%s"' % NAME, 'value="%s"' % NAME_B)
            .replace('<metadata key="outer_wall_speed" value="%s"/>' % SPEED_A[1],
                     '<metadata key="outer_wall_speed" value="%s"/>' % SPEED_B[1]))
    assert ob.count('value="%s"/>' % SPEED_B[1]) >= 1 and '<object id="6">' in ob
    ms = ms.replace(oa, oa + ob, 1)
    ms = ms.replace('    </model_instance>\n  </plate>',
                    '    </model_instance>\n    <model_instance>\n'
                    '      <metadata key="object_id" value="6"/>\n'
                    '      <metadata key="instance_id" value="0"/>\n'
                    '      <metadata key="identify_id" value="301"/>\n'
                    '    </model_instance>\n  </plate>', 1)
    ms = ms.replace('  </assemble>',
                    '   <assemble_item object_id="6" instance_id="0" transform="1 0 0 0 1 0 0 0 1 %s %s %s" '
                    'offset="0 0 0" />\n  </assemble>' % (lib._fmt(POS_B[0]), lib._fmt(POS_B[1]), z), 1)
    files['Metadata/model_settings.config'] = ms.encode()

    # height ranges: object 2 = object 1 with the floor and reservoir outer wall speed changed
    lr = files['Metadata/layer_config_ranges.xml'].decode()
    o1 = re.search(r' <object id="1">\n.*? </object>\n', lr, re.S).group(0)
    o2 = o1.replace('<object id="1">', '<object id="2">')
    n = o2.count('<option opt_key="outer_wall_speed">%d</option>' % SPEED_A[0])
    assert n == 2, n      # floor and reservoir ranges
    o2 = o2.replace('<option opt_key="outer_wall_speed">%d</option>' % SPEED_A[0],
                    '<option opt_key="outer_wall_speed">%d</option>' % SPEED_B[0])
    files['Metadata/layer_config_ranges.xml'] = lr.replace(o1, o1 + o2, 1).encode()

    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fn in order:
            zf.writestr(fn, files[fn])


def main(out_dir='.'):
    full.NAME = NAME
    full.POS = [POS_A, POS_B]          # thumbnails show both; add_instances then trimmed to A
    M, info = pot.build_mesh()
    painted = lib.paint_seam(M, pot.PAINT_SPAN)
    obj = lib.POT_OBJECT_SETTINGS + [('outer_wall_speed', lib._fmt(SPEED_A[1])),
                                     ('outer_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH)),
                                     ('inner_wall_line_width', lib._fmt(pot.WALL_LINE_WIDTH))]
    path = os.path.join(out_dir, NAME + '.3mf')
    lib.write_3mf(path, M, NAME, pot.H, painted, obj, pot.layer_ranges(), st.overrides(),
                  fan_ramp=False, plate_name=NAME.replace('_', ' '))
    pot.replace_entry(path, 'Metadata/custom_gcode_per_layer.xml', pot.fan_ramp_xml())
    thumbs = full._thumbs()
    full.POS = [POS_A]
    full._thumbs = lambda: thumbs
    full.add_instances(path)
    add_object_b(path)
    info['path'] = path
    return info


if __name__ == '__main__':
    print(main())
