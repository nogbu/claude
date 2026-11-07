"""Shared Orca 2.4.2 3mf writer for 3dp build scripts (one plate; objects, parts, instances, paint).

  import sys; sys.path.insert(0, "[repo]/projects/3dp/scripts")
  import write3mf as W
  s = W.base("nurseryPots_settings_base.json"); s.update(overrides)       # never edit a base in place
  pot = W.Obj("3.5inPot_rev11", [W.Part(V, T, paint=seam)],            # V (n,3) mm, T (m,3) ints
              settings=[("outer_wall_speed", "34")],                    # object settings
              ranges=[(0, 2.52, [("layer_height", "0.36")])],          # height-range modifiers
              at=[(128, 128)])                                          # instances: (x, y[, turn deg]); None: where V is
  W.write("3.5inPot_rev11.3mf", [pot], s, layer_gcode=[(9.72, "M106 S115")])

Each object's bounding-box center goes at each (x, y) in at, base on the bed; with at=None it stays where its
vertices put it (plate coordinates), only dropped onto the bed.
Part(extruder=2) makes a multi-color part; Part(settings=[...]) sets that part's own settings (plantTags' text line widths); paint is a per-triangle array of 3mf attribute strings
('paint_seam="4"' enforces a seam, as the pot files do; 'paint_supports="4"' should paint support the
same way, untested) or None. The thumbnail is drawn from the model itself, so it shows the real shape.
Tested 2026-10-07: the pot and photo board slice to the same G-code time and filament as their old
writers; Orca's estimate moves several seconds with a 0.00002 mm shift, so compare slices of one file.
"""
import datetime, io, json, math, os, uuid, zipfile
from dataclasses import dataclass, field
import numpy as np

NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"')
HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n'
EYE = (-1.0, -1.6, 0.8)


@dataclass
class Part:
    V: np.ndarray
    T: np.ndarray
    name: str = None
    extruder: int = 1
    paint: object = None
    settings: list = field(default_factory=list)   # part settings, e.g. [("outer_wall_line_width", "0.31")]


@dataclass
class Obj:
    name: str
    parts: list
    settings: list = field(default_factory=list)
    ranges: list = field(default_factory=list)
    at: list = None


def base(path):
    """A settings base (a saved file's project_settings.config) as a dict."""
    return json.load(open(path))


def _f(v):
    s = "%.5f" % v
    s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _mesh_xml(oid, uid, V, T, paint):
    """Vertices in one formatting pass per row (the old per-number helper cost 1 s per million numbers)."""
    V = np.round(np.asarray(V, float), 5) + 0.0          # + 0.0 turns -0.0 into 0.0
    vx = "\n".join('     <vertex x="%r" y="%r" z="%r"/>' % r for r in map(tuple, V.tolist()))
    T = np.asarray(T, int).tolist()
    if paint is None:
        tx = "\n".join('     <triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t) for t in T)
    else:
        tx = "\n".join('     <triangle v1="%d" v2="%d" v3="%d"%s/>' % (a, b, c, " " + p if p else "")
                       for (a, b, c), p in zip(T, paint))
    return ('  <object id="%d" p:UUID="%s" type="model">\n   <mesh>\n    <vertices>\n%s\n    </vertices>\n'
            '    <triangles>\n%s\n    </triangles>\n   </mesh>\n  </object>' % (oid, uid, vx, tx))


def _turn(x, y, z, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return "%s %s 0 %s %s 0 0 0 1 %s %s %s" % (_f(c), _f(s), _f(-s), _f(c), _f(x), _f(y), _f(z))


def _thumbs(objs, px=512):
    """plate_1.png (512 px) and plate_1_small.png (128 px): the model itself, shaded, from render3d's camera.
    One direct z-buffer pass at thumbnail size (no FACES list, outlines or supersampling) keeps it fast."""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import render3d as R
    from PIL import Image
    tri = np.concatenate([np.asarray(p.V, float)[np.asarray(p.T, int)] for o in objs for p in o.parts])
    col = np.concatenate([np.tile(R.BONE if p.extruder == 1 else (0.25, 0.25, 0.25), (len(p.T), 1)) for o in objs for p in o.parts])
    e, right, up = R.camera(EYE)
    N = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); n = np.linalg.norm(N, axis=1)
    k = (n > 1e-12) & (N @ e > 0); tri, N, col = tri[k], N[k] / n[k, None], col[k]
    Lt = np.array([0.3, -0.7, 1.0]); Lt /= np.linalg.norm(Lt)
    col = np.clip(col * (0.45 + 0.40 * np.maximum(0, N @ Lt) + 0.25 * np.maximum(0, N @ e))[:, None], 0, 1)
    X, Y = tri @ right, tri @ up
    x0, x1, y0, y1 = X.min(), X.max(), Y.min(), Y.max()
    s = 0.92 * px / max(x1 - x0, y1 - y0)
    P = np.stack([(X - (x0 + x1) / 2) * s + px / 2, ((y0 + y1) / 2 - Y) * s + px / 2], -1)
    ids, _ = R._rasterize(P, tri @ e, px, px)
    img = np.ones((px * px, 3)); img[ids >= 0] = col[ids[ids >= 0]]
    im = Image.fromarray((img.reshape(px, px, 3) * 255).astype(np.uint8))
    out = {}
    for name, size in (("plate_1.png", px), ("plate_1_small.png", 128)):
        buf = io.BytesIO(); (im if size == px else im.resize((size, size), Image.LANCZOS)).save(buf, "PNG"); out[name] = buf.getvalue()
    return out


def _range_opts(opts, settings):
    """Every height range carries layer_height and extruder, or Orca crashes opening the file (learnings/speed-and-cooling)."""
    keys = {k for k, _ in opts}
    return list(opts) + [kv for kv in (("layer_height", settings.get("layer_height", "0.2")), ("extruder", "1")) if kv[0] not in keys]


NOT_EDITS = {'filament_colour', 'filament_multi_colour', 'filament_self_index', 'print_compatible_printers'}   # not preset edits: two spools of one preset may differ here


def _guard(objs, settings):
    """Support off unless a part paints it, so the command-line slicer slices PETG HF; one edited filament per
    preset name, since Orca keeps one set of edits per name (learnings/slicing-checks). Returns the settings."""
    painted = any(p.paint is not None and any("paint_supports" in str(t) for t in p.paint) for o in objs for p in o.parts)
    if str(settings.get("enable_support", "0")) == "1" and not painted:
        settings = dict(settings, enable_support="0")
    ids = settings.get("filament_settings_id") or []
    for k in ("inherits_group", "different_settings_to_system"):   # [process, one per filament, printer]: a base copied from a file
        v = settings.get(k)                                         # with another filament count shifts the printer into a filament
        if isinstance(v, list) and len(v) >= 2 and len(v) != len(ids) + 2:   # slot and Orca shows Generic filaments (plantTags rev1.3)
            settings = dict(settings, **{k: [v[0]] + (list(v[1:-1]) + [""] * len(ids))[:len(ids)] + [v[-1]]})
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if ids[i] == ids[j]:
                diff = [k for k, v in settings.items() if isinstance(v, list) and len(v) == len(ids) and v[i] != v[j]
                        and k not in NOT_EDITS]
                if diff:
                    raise ValueError("filaments %d and %d share the preset name %r but differ in %s; give one a unique name"
                                     % (i + 1, j + 1, ids[i], ", ".join(diff[:5])))
    return settings


def write(path, objs, settings, layer_gcode=None, plate_name=None, thumbnails=True):
    """Write an Orca 2.4.2 3mf. layer_gcode: [(top_z, gcode)] for the layer slider (the command-line
    slicer drops these; put must-keep G-code in the printer's layer-change G-code instead). Returns path."""
    settings = _guard(objs, settings)
    stem = os.path.splitext(os.path.basename(path))[0]
    u = lambda tag: str(uuid.uuid5(uuid.NAMESPACE_URL, "3dp/%s/%s" % (stem, tag)))
    model_path = "/3D/Objects/%s.model" % stem
    meshes, comps, items, cfg, inst, asm, ranges = [], [], [], [], [], [], []
    mid, oid, ident = 1, len(sum((o.parts for o in objs), [])) + 1, 300
    for k, o in enumerate(objs):
        Vs = np.vstack([np.asarray(p.V, float) for p in o.parts])
        lo, hi = Vs.min(0), Vs.max(0); c = (lo + hi) / 2.0; zc = (hi[2] - lo[2]) / 2.0
        oc, pc = [], []
        for j, p in enumerate(o.parts):
            meshes.append(_mesh_xml(mid, u("mesh%d" % mid), np.asarray(p.V, float) - c, p.T, p.paint))
            oc.append('    <component p:path="%s" objectid="%d" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>'
                      % (model_path, mid, u("comp%d" % mid)))
            pc.append('    <part id="%d" subtype="normal_part">\n      <metadata key="name" value="%s"/>\n'
                      '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
                      '      <metadata key="extruder" value="%d"/>\n%s      <metadata key="source_file" value="%s.3mf"/>\n'
                      '      <metadata key="source_object_id" value="%d"/>\n      <metadata key="source_volume_id" value="%d"/>\n'
                      '      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n'
                      '    </part>' % (mid, p.name or (o.name if len(o.parts) == 1 else "%s part %d" % (o.name, j + 1)),
                                       p.extruder, "".join('      <metadata key="%s" value="%s"/>\n' % kv for kv in p.settings), stem, k, j))
            mid += 1
        comps.append('  <object id="%d" p:UUID="%s" type="model">\n   <components>\n%s\n   </components>\n  </object>'
                     % (oid, u("obj%d" % oid), "\n".join(oc)))
        cfg.append('  <object id="%d">\n    <metadata key="name" value="%s"/>\n    <metadata key="extruder" value="1"/>\n%s%s\n  </object>'
                   % (oid, o.name, "".join('    <metadata key="%s" value="%s"/>\n' % kv for kv in o.settings), "\n".join(pc)))
        for i, a in enumerate(o.at or [(c[0], c[1])]):
            tr = _turn(a[0], a[1], zc, a[2] if len(a) > 2 else 0.0)
            items.append('  <item objectid="%d" p:UUID="%s" transform="%s" printable="1"/>' % (oid, u("item%d.%d" % (oid, i)), tr))
            inst.append('    <model_instance>\n      <metadata key="object_id" value="%d"/>\n      <metadata key="instance_id" value="%d"/>\n'
                        '      <metadata key="identify_id" value="%d"/>\n    </model_instance>' % (oid, i, ident)); ident += 1
            asm.append('   <assemble_item object_id="%d" instance_id="%d" transform="%s" offset="0 0 0" />' % (oid, i, tr))
        if o.ranges:
            ranges.append(' <object id="%d">\n%s\n </object>' % (k + 1, "\n".join(
                '  <range min_z="%s" max_z="%s">\n%s\n  </range>' % (_f(a), _f(b), "\n".join(
                    '   <option opt_key="%s">%s</option>' % kv for kv in _range_opts(opts, settings))) for a, b, opts in o.ranges)))
        oid += 1
    today = datetime.date.today().isoformat()
    root = (HEAD + '<model unit="millimeter" xml:lang="en-US" %s>\n <metadata name="Application">BambuStudio-02.06.00.51</metadata>\n'
            ' <metadata name="OrcaSlicer">2.4.2</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
            ' <metadata name="CreationDate">%s</metadata>\n <metadata name="ModificationDate">%s</metadata>\n'
            ' <metadata name="Thumbnail_Middle">/Metadata/plate_1.png</metadata>\n <metadata name="Thumbnail_Small">/Metadata/plate_1_small.png</metadata>\n'
            ' <metadata name="Title"></metadata>\n <resources>\n%s\n </resources>\n <build p:UUID="%s">\n%s\n </build>\n</model>\n'
            % (NS, today, today, "\n".join(comps), u("build"), "\n".join(items)))
    objects = (HEAD + '<model unit="millimeter" xml:lang="en-US" %s>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
               ' <resources>\n%s\n </resources>\n <build/>\n</model>\n' % (NS, "\n".join(meshes)))
    model_settings = (HEAD + '<config>\n%s\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value="%s"/>\n'
                      '    <metadata key="locked" value="false"/>\n    <metadata key="filament_map_mode" value="Auto For Flush"/>\n'
                      '    <metadata key="filament_maps" value="1 1"/>\n%s\n  </plate>\n  <assemble>\n%s\n  </assemble>\n</config>\n'
                      % ("\n".join(cfg), plate_name or stem.replace("_", " "), "\n".join(inst), "\n".join(asm)))
    lr = '<?xml version="1.0" encoding="utf-8"?>\n<objects>\n%s</objects>\n' % "".join(r + "\n" for r in ranges)
    gc = "".join('<layer top_z="%s" type="4" extruder="1" color="" extra="" gcode="%s"/>\n'
                 % (_f(z), g.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace("\n", "&#10;"))
                 for z, g in (layer_gcode or []))
    gc = ('<?xml version="1.0" encoding="utf-8"?>\n<custom_gcodes_per_layer>\n'
          + ('<plate>\n<plate_info id="1"/>\n%s<mode value="SingleExtruder"/>\n</plate>\n' % gc if gc else "") + '</custom_gcodes_per_layer>\n')
    rels = (HEAD + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
            ' <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>\n'
            ' <Relationship Target="/Metadata/plate_1.png" Id="rel-4" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-middle"/>\n'
            ' <Relationship Target="/Metadata/plate_1_small.png" Id="rel-5" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-small"/>\n'
            '</Relationships>\n')
    files = {
        "[Content_Types].xml": HEAD + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
        ' <Default Extension="png" ContentType="image/png"/>\n <Default Extension="gcode" ContentType="text/x.gcode"/>\n</Types>\n',
        "_rels/.rels": rels,
        "3D/3dmodel.model": root,
        "3D/_rels/3dmodel.model.rels": HEAD + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        ' <Relationship Target="%s" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n' % model_path,
        model_path.lstrip("/"): objects,
        "Metadata/project_settings.config": json.dumps(settings, indent=4, ensure_ascii=False),
        "Metadata/model_settings.config": model_settings,
        "Metadata/layer_config_ranges.xml": lr,
        "Metadata/custom_gcode_per_layer.xml": gc,
        "Metadata/slice_info.config": HEAD + '<config>\n  <header>\n    <header_item key="X-BBL-Client-Type" value="slicer"/>\n'
        '    <header_item key="X-BBL-Client-Version" value="02.06.00.51"/>\n    <header_item key="OrcaSlicer-Version" value="2.4.2"/>\n  </header>\n</config>\n',
        "Metadata/filament_sequence.json": '{"plate_1": {"nozzle_sequence": [], "optimal_assignment": [], "sequence": []}}',
    }
    if thumbnails:
        files.update(("Metadata/" + k, v) for k, v in _thumbs(objs).items())
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as z:   # level 1: about 5x faster, a little larger
        for name, data in files.items():
            z.writestr(name, data)
    return path
