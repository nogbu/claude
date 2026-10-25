"""Plant tag builder: the plantTags.3mf stake (1.02 mm) with rows of Overpass ExtraBold text inlaid flush in the bed face.

  python3 plantTags_lib.py tags.txt plantTags_rev2_ferns [outdir]   (make_set: name, species and blank tags from a list)

  import plantTags_lib as P
  P.build('plantTags_rev1.3_aceOfSpades', [('ace of spades', 2), ('x dark phoenix', 1)], em=7.0, lw='0.37', indent=[0, 2])

rows: (text, filament) top to bottom; filament 1 is the clear PETG Translucent body, 2 red-brown PETG-CF, 3 black Bambu PETG Basic (2026-10-11)
(the 3mf's colors). indent: leading spaces per row (space advance 0.255 em). Rows sit on font baselines: each row's band
runs from the ascender (0.722 em) to the descender (0.213 em), and margins and gaps between bands are equal.
Settings: rail's Orca P1S base (its process matches the 3mf's) with the 3mf's per-filament values, 0.24 mm layers,
first layer line width = lw (plate-wide), text parts' line widths = lw, prime tower at (110, 175).
"""
import os, sys, json, zipfile, re
import numpy as np, trimesh, manifold3d as mf
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import write3mf as W

SRC = os.path.join(HERE, 'plantTags_source.3mf')   # my plantTags.3mf (2026-10-05), copied here so any project can build tags
FONT = os.path.join(HERE, 'Overpass-ExtraBold.ttf')
TH, DEPTH, X0, HALF_W = 1.02, 0.30, -62.567, 10.0   # text one layer deep: the 0.3 mm first layer (my pick 2026-10-13)
LW = '0.40'   # text and first-layer line width for make_set: the cleanest lwTest print (my pick 2026-10-13; was best_lw, about 0.35)
FIRST_SPEED = '20'   # make_set's first layer speed, mm/s (my pick 2026-10-13, untested; the lwTest print used 15; was 35)
ASC, DESC, SPACE = 0.722, 0.213, 0.255       # em fractions, from the font (k/d/h top, g bottom, space advance)
COLORS = {2: '#9F332A', 3: '#000000'}
FIL = re.compile(r'(filament_|nozzle_temperature|(cool|eng|hot|textured|supertack)_plate_temp|fan_|additional_cooling|close_fan|overhang_fan|'
                 r'full_fan|reduce_fan|slow_down_|temperature_vitrification|required_nozzle|activate_air|complete_print_exhaust|during_print_exhaust|pellet_flow)')


def tag_mesh():
    z = zipfile.ZipFile(SRC); x = z.read('3D/Objects/species #1_44.model').decode()
    obj = re.search(r'<object id="1".*?</object>', x, re.S).group(0)
    V = np.array([[float(a) for a in v] for v in re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', obj)])
    T = np.array([[int(a) for a in t] for t in re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', obj)])
    V[:, 2] = (V[:, 2] - V[:, 2].min()) * TH / (V[:, 2].max() - V[:, 2].min())
    m = trimesh.Trimesh(V, T)
    if m.volume < 0: m.invert()
    return m


def text_poly(s, em):
    """Glyph outlines on the baseline y = 0, x from the pen start (reading orientation)."""
    tp = TextPath((0, 0), s, size=em, prop=FontProperties(fname=FONT))
    rings = sorted((Polygon(p) for p in tp.to_polygons() if len(p) > 2), key=lambda p: -p.area); P = Polygon()
    for r in rings:
        P = P.difference(r) if P.contains(r.representative_point()) else P.union(r)
    return P


def layout(rows, em, indent):
    """Reading-orientation polygons per row and the baselines used."""
    band = (ASC + DESC) * em; n = len(rows)
    gap = (2 * HALF_W - n * band) / (n + 1)
    out, bases = [], []
    for i, (s, fil) in enumerate(rows):
        top = HALF_W - gap - i * (band + gap); base = top - ASC * em
        P = text_poly(s, em)
        if i == 0: first_left = P.bounds[0]
        P = affinity.translate(P, X0 - first_left + indent[i] * SPACE * em, base)
        out.append((P, fil)); bases.append(base)
    return out, bases, gap


def extrude(P):
    P = affinity.scale(P, 1, -1, origin=(0, 0))     # read from the bed face: mirror y for print coordinates
    return trimesh.util.concatenate([trimesh.creation.extrude_polygon(g, DEPTH, engine='earcut') for g in getattr(P, 'geoms', [P])])


def mf_(m): return mf.Manifold(mf.Mesh(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.uint32)))
def tm_(M): g = M.to_mesh(); return trimesh.Trimesh(g.vert_properties[:, :3], g.tri_verts)


def settings(lw, fils):
    """fils: the filament numbers used (1 always; 2 and/or 3), in slot order."""
    bdir = os.path.join(HERE, 'settings')
    s = W.base(os.path.join(bdir, 'rail_settings_base.json'))
    tr = W.base(os.path.join(bdir, 'nurseryPots_settings_base.json'))
    cf = W.base(os.path.join(bdir, 'shelf_settings_base.json'))
    pb = W.base(os.path.join(bdir, 'petgBasic_settings_base.json'))   # black text is Bambu PETG Basic (my words 2026-10-11)
    B = json.loads(zipfile.ZipFile(SRC).read('Metadata/project_settings.config'))
    n, nb = len(s['filament_settings_id']), len(B['filament_settings_id'])
    src_idx = {1: 0, 2: 2, 3: 1}            # the 3mf's filament index for each color: 1 clear, 2 red-brown (#3), 3 black (#2)
    for k, v in list(s.items()):
        if not isinstance(v, list) or len(v) % n or not FIL.match(k) or k in ('flush_volumes_matrix', 'filament_self_index'):
            continue
        blk = len(v) // n
        a, c, g = tr.get(k, v), cf.get(k, v), pb.get(k, v)
        if not all(isinstance(x, list) and len(x) == len(v) for x in (a, c, g)):
            continue
        per = {1: a[:blk], 2: c[:blk], 3: g[:blk]}
        b = B.get(k)
        if k != 'filament_settings_id' and isinstance(b, list) and len(b) == nb:
            per = {f: ([b[src_idx[f]]] * blk if f != 3 else per[3]) for f in per}
        s[k] = sum((per[f] for f in fils), [])
    m = B['flush_volumes_matrix']; idx = [src_idx[f] for f in fils]
    s['flush_volumes_matrix'] = [m[i * nb + j] for i in idx for j in idx]
    s['filament_colour'] = ['#00000000'] + [COLORS[f] for f in fils[1:]]
    s['filament_self_index'] = [str(i + 1) for i in range(len(fils)) for _ in range(len(s['filament_self_index']) // n)]
    s.update(layer_height='0.24', initial_layer_line_width=lw, wipe_tower_x=['110'], wipe_tower_y=['175'])
    return s


def build(name, rows, em, lw, indent=None, outdir='/mnt/project-files/3mfs'):
    indent = indent or [0] + [2] * (len(rows) - 1)   # Product rule: second row indented 2 spaces
    polys, bases, gap = layout(rows, em, indent)
    fils = [1] + sorted({f for _, f in polys})
    tag = tag_mesh(); texts = [(extrude(P), f) for P, f in polys]
    body = mf_(tag)
    for m, _ in texts: body = body - mf_(m)
    body = tm_(body)
    wset = [(k, lw) for k in ('outer_wall_line_width', 'inner_wall_line_width', 'internal_solid_infill_line_width',
                              'top_surface_line_width', 'sparse_infill_line_width')]
    parts = [W.Part(body.vertices, body.faces, name='tag', extruder=1)]
    parts += [W.Part(m.vertices, m.faces, name=rows[i][0], extruder=fils.index(f) + 1, settings=wset) for i, (m, f) in enumerate(texts)]
    out = os.path.join(outdir, name + '.3mf')
    W.write(out, [W.Obj(name, parts, at=[(128, 128)])], settings(lw, fils))
    return _report(out, polys, bases, rows, em, gap)


def _report(out, polys, bases, rows, em, gap):
    for (P, f), b, (s, _) in zip(polys, bases, rows):
        print('%-16s filament %d  x %.2f..%.2f  baseline %.2f  span %.2f mm' % (s, f, P.bounds[0], P.bounds[2], b, P.bounds[2] - P.bounds[0]))
    print('band %.2f mm, margins and gap %.2f mm' % ((ASC + DESC) * em, gap))
    return out, polys


def under_two_beads(P, lw):
    """Share of the letters' area thinner than two beads of width lw (a morphological opening by 2*lw)."""
    w = 2 * float(lw)
    return 1 - P.buffer(-w / 2, join_style=1).buffer(w / 2, join_style=1).area / P.area


def best_lw(polys, cands=(0.31, 0.33, 0.35, 0.37, 0.38, 0.40, 0.42, 0.45), jump=0.01):
    """Widest line width before two-bead coverage drops: stop at the first step that loses more than `jump` (1%) of letter area
    on any row (the knee the rev1.2 and rev1.3 picks used). Returns (lw, {lw: [share per row]})."""
    tab = {lw: [under_two_beads(P, lw) for P in polys] for lw in cands}
    best = cands[0]
    for a, b in zip(cands, cands[1:]):
        if max(tb - ta for ta, tb in zip(tab[a], tab[b])) > jump: break
        best = b
    return best, tab


def tag_parts(rows, em, lw, fils, indent=None):
    """Parts for one tag: the body plus one part per row (no rows: a blank tag)."""
    wset = [(k, lw) for k in ('outer_wall_line_width', 'inner_wall_line_width', 'internal_solid_infill_line_width',
                              'top_surface_line_width', 'sparse_infill_line_width')]
    tag = tag_mesh()
    if not rows:
        return [W.Part(tag.vertices, tag.faces, name='tag', extruder=1)], []
    polys, bases, gap = layout(rows, em, indent or [0] + [2] * (len(rows) - 1))
    texts = [(extrude(P), f) for P, f in polys]
    body = mf_(tag)
    for m, _ in texts: body = body - mf_(m)
    body = tm_(body)
    parts = [W.Part(body.vertices, body.faces, name='tag', extruder=1)]
    parts += [W.Part(m.vertices, m.faces, name=rows[i][0], extruder=fils.index(f) + 1, settings=wset) for i, (m, f) in enumerate(texts)]
    return parts, polys


def build_set(name, tags, em, lw, outdir='/mnt/project-files/3mfs', pitch=28.0, plates=None, first_speed=None):
    """Several tags on one plate, stacked across y at `pitch` mm. tags: [(object name, rows)], rows as in build ([] = blank).
    plates: [(plate name, [tag indexes])], each group stacked and centered on its own plate, in order."""
    fils = [1] + sorted({f for _, rows in tags for _, f in rows})
    objs, report = [], []
    groups = plates or [(None, list(range(len(tags))))]
    ys = {i: 128 - pitch * (len(ks) - 1) / 2 + j * pitch for _, ks in groups for j, i in enumerate(ks)}
    for i, (oname, rows) in enumerate(tags):
        parts, polys = tag_parts(rows, em, lw, fils)
        objs.append(W.Obj(oname, parts, at=[(128, ys[i])]))
        report.append((oname, [(s, P.bounds[2] - P.bounds[0], P.bounds[2]) for (s, _), (P, _) in zip(rows, polys)]))
    s = settings(lw, fils); s.update(wipe_tower_x=['205'], wipe_tower_y=['175'])   # clear of the tags (x 61-195)
    if first_speed: s.update(initial_layer_speed=first_speed)
    out = os.path.join(outdir, name + '.3mf')
    W.write(out, objs, s, plates=plates)
    for oname, rr in report:
        print(oname, ', '.join('%r span %.2f ends x %.2f' % r for r in rr) or 'blank')
    return out


SOIL_X = 66.697 - 70.0      # 70 mm soil line from the tip (x max 66.697); no row may end past it (soil depth, my words 2026-10-10)
PER_PLATE = 8               # tags per plate at the 28 mm pitch: y 10 to 246 on the 256 mm bed (inference)
KIND_FIL = {'name': 2, 'species': 3}   # the 3mf's colors: name tags red-brown, species tags black


def wrap(text, fil, em):
    """Rows for one tag: one row if it ends before the soil line, else two split at the last word break that fits (row 2
    indented 2 spaces, Product rule). Text with " x " (a cross) always splits before its first " x ", so row 2 starts
    with the "x" (my words 2026-10-11). Raises ValueError when no split fits."""
    words = text.split()
    if ' x ' in text:
        a, b = text.split(' x ', 1); rows = [(a.strip(), fil), ('x ' + b.strip(), fil)]
        if max(P.bounds[2] for P, _ in layout(rows, em, [0, 2])[0]) <= SOIL_X:
            return rows
        raise ValueError('%r does not fit two rows split at the " x " at %g mm before the soil line; shorten it or pick a smaller size' % (text, em))
    if layout([(text, fil)], em, [0])[0][0][0].bounds[2] <= SOIL_X:
        return [(text, fil)]
    for k in range(len(words) - 1, 0, -1):
        rows = [(' '.join(words[:k]), fil), (' '.join(words[k:]), fil)]
        if max(P.bounds[2] for P, _ in layout(rows, em, [0, 2])[0]) <= SOIL_X:
            return rows
    raise ValueError('%r does not fit two rows at %g mm before the soil line; shorten it or pick a smaller size' % (text, em))


def parse_list(path):
    """Lines 'name: x', 'species: x' or 'blank' / 'blank: 3'; blank lines and '#' comments skipped. Returns [(kind, text)]."""
    tags = []
    for ln in open(path, encoding='utf-8'):
        ln = ln.split('#')[0].strip()
        if not ln: continue
        kind, _, text = ln.partition(':'); kind, text = kind.strip().lower(), text.strip()
        if kind == 'blank':
            tags += [('blank', '')] * (int(text) if text else 1)
        elif kind in KIND_FIL and text:
            tags.append((kind, text))
        else:
            raise ValueError('cannot read line %r: use "name: x", "species: x" or "blank[: n]"' % ln)
    return tags


def make_set(name, tags, em=7.0, outdir='/mnt/project-files/3mfs', by_kind=False, blank_per_file=False):
    """Name, species and blank tags, PER_PLATE per file in list order. Every file's text and first-layer line width is LW and its first layer speed FIRST_SPEED. Returns [(3mf path, [(kind, text, rows)])]. by_kind (my words 2026-10-11): a file's name tags share one plate, its species tags the next and its blanks the last,
    up to PER_PLATE tags per plate (so 8 plants per file).
    blank_per_file: a file with no blank in it gets one blank tag last (my words 2026-10-11: "only one blank tag per 3mf"). Files: name.3mf, or with more than PER_PLATE tags the plate number after the rev ("_rev2" -> "_rev2.1")."""
    tag_rows, bad = [], []
    for k, text in tags:
        try: tag_rows.append((k, text, wrap(text, KIND_FIL[k], em) if k != 'blank' else []))
        except ValueError as e: bad.append(str(e))
    if bad: raise ValueError('\n'.join(bad))     # every tag that doesn't fit, at once
    if by_kind:
        chunks, cnt = [[]], {}
        for t in tag_rows:
            if cnt.get(t[0], 0) == PER_PLATE: chunks.append([]); cnt = {}
            chunks[-1].append(t); cnt[t[0]] = cnt.get(t[0], 0) + 1
    else:
        chunks = [tag_rows[i:i + PER_PLATE] for i in range(0, len(tag_rows), PER_PLATE)]
    outs = []
    for c, chunk in enumerate(chunks, 1):
        if blank_per_file and not any(k == 'blank' for k, _, _ in chunk):
            chunk = chunk + [('blank', '', [])]
        fname = name if len(chunks) == 1 else re.sub(r'(_rev[\d.]*\d)', r'\g<1>.%d' % c, name, count=1) if '_rev' in name else '%s.%d' % (name, c)
        lw = LW
        objs = [((text or 'blank') + ('' if k == 'blank' else ' (%s)' % k), rows) for k, text, rows in chunk]
        print('%s: %d tags, line width %s mm' % (fname, len(chunk), lw))
        plates = [(k, [i for i, t in enumerate(chunk) if t[0] == k]) for k in ('name', 'species', 'blank')] if by_kind else None
        outs.append((build_set(fname, objs, em, lw, outdir, plates=[p for p in plates if p[1]] if plates else None, first_speed=FIRST_SPEED), chunk))
    return outs


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) < 2: sys.exit('usage: python3 plantTags_lib.py tags.txt NAME [outdir]')
    make_set(a[1], parse_list(a[0]), outdir=a[2] if len(a) > 2 else '/mnt/project-files/3mfs')
