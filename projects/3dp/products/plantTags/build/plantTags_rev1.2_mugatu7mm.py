"""plantTags_rev1.2_mugatu7mm: one name tag reading "mugatu", the plantTags.3mf stake with agreed changes 1-6.

Tag: the 3mf's own stake mesh (plantTagv2.stl, 133.4 x 20 x 0.96) scaled to 1.02 mm thick (change 3).
Text: Overpass ExtraBold (wght 800, the 3mf's Overpass Heavy; Overpass-ExtraBold.ttf beside this script, OFL)
at 7 mm (change 4, rev1.2), inlaid flush 0.54 mm into the bed face (change 1), left edge where the 3mf puts it,
centered across the tag, mirrored so it reads from the bed face. Text part line widths 0.37 (change 4, rev1.2: widest before two-bead coverage drops, 2.3% short at 0.37, 2.8% at 0.38, 4.2% at 0.40);
first layer line width 0.37 plate-wide (change 5). Body PETG Translucent (filament 1), text red-brown PETG-CF
(filament 2, #9F332A). Settings: rail's Orca P1S base (matches the 3mf's process) with the 3mf's 0.24 mm layers.
Run: python3 plantTags_rev1.1_mugatuTest.py [outdir]  (writes plantTags_rev1.2_mugatu7mm.3mf)
"""
import os, sys, json, zipfile, re
import numpy as np, trimesh, manifold3d as mf
from shapely.geometry import Polygon
from shapely import affinity
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '../../../../..'))
sys.path.insert(0, os.path.join(REPO, 'projects/3dp/scripts'))
import write3mf as W

SRC = '/mnt/project-files/uploads/hearth/2d275a95-3333-41da-b5db-5e6d8ff8cf77'   # plantTags.3mf, 2026-10-05
WORD, EM, TH, DEPTH, LW = 'mugatu', 7.0, 1.02, 0.54, '0.37'
X0 = -62.567          # left edge of the 3mf's text (its "species" mesh), kept
NAME = 'plantTags_rev1.2_mugatu7mm'
FIL = re.compile(r'(filament_|nozzle_temperature|(cool|eng|hot|textured|supertack)_plate_temp|fan_|additional_cooling|close_fan|overhang_fan|'
                 r'full_fan|reduce_fan|slow_down_|temperature_vitrification|required_nozzle|activate_air|complete_print_exhaust|during_print_exhaust|pellet_flow)')


def tag_mesh():
    """The 3mf's stake mesh (object 1 of 'species #1_44.model'), bottom on z = 0, scaled to TH thick."""
    z = zipfile.ZipFile(SRC); x = z.read('3D/Objects/species #1_44.model').decode()
    obj = re.search(r'<object id="1".*?</object>', x, re.S).group(0)
    V = np.array([[float(a) for a in v] for v in re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', obj)])
    T = np.array([[int(a) for a in t] for t in re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', obj)])
    V[:, 2] = (V[:, 2] - V[:, 2].min()) * TH / (V[:, 2].max() - V[:, 2].min())
    m = trimesh.Trimesh(V, T)
    if m.volume < 0: m.invert()
    return m


def text_poly(s, em):
    """Glyph outlines in reading orientation (y up), even-odd holes."""
    tp = TextPath((0, 0), s, size=em, prop=FontProperties(fname=os.path.join(HERE, 'Overpass-ExtraBold.ttf')))
    rings = sorted((Polygon(p) for p in tp.to_polygons() if len(p) > 2), key=lambda p: -p.area); P = Polygon()
    for r in rings:
        P = P.difference(r) if P.contains(r.representative_point()) else P.union(r)
    return P


def text_mesh():
    """Text read from the bed face: placed in reading coords, then y mirrored for print coords (the tag turned over)."""
    P = text_poly(WORD, EM); b = P.bounds
    P = affinity.translate(P, X0 - b[0], -(b[1] + b[3]) / 2)
    P = affinity.scale(P, 1, -1, origin=(0, 0))
    m = trimesh.util.concatenate([trimesh.creation.extrude_polygon(g, DEPTH, engine='earcut') for g in getattr(P, 'geoms', [P])])
    return m, P


def mf_(m): return mf.Manifold(mf.Mesh(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.uint32)))
def tm_(M): g = M.to_mesh(); return trimesh.Trimesh(g.vert_properties[:, :3], g.tri_verts)


def settings():
    """rail's Orca P1S base (its process matches the 3mf's) with two filaments: slot 1 PETG Translucent and slot 2 PETG-CF,
    Orca presets from the nursery-pots and shelf bases, every per-filament value then taken from the 3mf's filaments 1 and 3."""
    bdir = os.path.join(REPO, 'projects/3dp/products')
    s = W.base(os.path.join(bdir, 'rail/build/rail_settings_base.json'))
    tr = W.base(os.path.join(bdir, 'nursery-pots/build/nurseryPots_settings_base.json'))   # PETG Translucent preset in slot 1
    cf = W.base(os.path.join(bdir, 'shelf/build/shelf_settings_base.json'))                 # PETG-CF preset in slot 1
    B = json.loads(zipfile.ZipFile(SRC).read('Metadata/project_settings.config'))
    n, nb = len(s['filament_settings_id']), len(B['filament_settings_id'])
    for k, v in list(s.items()):
        if not isinstance(v, list) or len(v) % n or not FIL.match(k) or k in ('flush_volumes_matrix', 'filament_self_index'):
            continue
        blk = len(v) // n
        a, c = tr.get(k, v), cf.get(k, v)
        if not (isinstance(a, list) and isinstance(c, list) and len(a) == len(v) and len(c) == len(v)):
            continue
        new = a[:blk] + c[:blk]
        b = B.get(k)
        if k != 'filament_settings_id' and isinstance(b, list) and len(b) == nb:   # the 3mf's own value per filament
            new = [b[0]] * blk + [b[2]] * blk
        s[k] = new
    m = B['flush_volumes_matrix']; s['flush_volumes_matrix'] = [m[0], m[2], m[6], m[8]]   # 3x3 -> filaments 1 and 3
    s['filament_colour'] = ['#00000000', '#9F332A']
    s.update(layer_height='0.24', initial_layer_line_width=LW, wipe_tower_x=['110'], wipe_tower_y=['175'])   # rail's tower spot ran off the bed (y 258.8)
    return s


def build(outdir):
    tag = tag_mesh(); txt, P = text_mesh()
    body = tm_(mf_(tag) - mf_(txt))
    parts = [W.Part(body.vertices, body.faces, name='tag', extruder=1),
             W.Part(txt.vertices, txt.faces, name=WORD, extruder=2,
                    settings=[(k, LW) for k in ('outer_wall_line_width', 'inner_wall_line_width', 'internal_solid_infill_line_width',
                                                'top_surface_line_width', 'sparse_infill_line_width')])]
    out = os.path.join(outdir, NAME + '.3mf')
    W.write(out, [W.Obj(NAME, parts, at=[(128, 128)])], settings())
    print(out, 'text span %.2f x %.2f mm' % (P.bounds[2] - P.bounds[0], P.bounds[3] - P.bounds[1]),
          'body %.1f mm3, text %.1f mm3' % (body.volume, txt.volume))
    return out


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/3mfs')
