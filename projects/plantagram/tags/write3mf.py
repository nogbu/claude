"""Shared Orca 2.4.2 3mf writer for 3dp build scripts (one plate, or several with plates=; objects, parts, instances, paint).

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
same way; front-roof-fix_options.py's painted fit test sliced with it) or None. The thumbnail is drawn from the model
itself, so it shows the real shape.
write(..., cli=True) makes a copy for /opt/orca/slice: with supports painted, the support interface prints in the
painted part's own filament with 0.3 mm top and bottom z gaps, since the command-line slicer refuses a support
filament whose temperature range misses the part's (learnings/slicing-checks); leave it off for the file I print.
Every write() but a cli copy also draws [file]_master.png beside the 3mf (picture.py --master: each printed part
once, numbered, with its size; a single part gets measured size lines), about 10 to 16 s.
write(..., plates=[(name, [object indexes]), ...]) puts each group on its own plate, in order; each object's at is
its spot on its own plate. Plates sit on Bambu Studio's grid (as in plantTags_source.3mf): a stride of 1.2 bed widths
(307.2 mm on the 256 mm bed), ceil(sqrt(plates)) columns, rows going -y.
Tested 2026-10-07: the pot and photo board slice to the same G-code time and filament as their old
writers; Orca's estimate moves several seconds with a 0.00002 mm shift, so compare slices of one file.

Preview (redesign 2026-10-05, section 11): any build script run with --preview (python3 build.py --preview ...) writes
each 3mf's mesh as [name].stl instead, in plate placement, with no 3mf, thumbnails or settings checks; importing this
file takes the flag out of sys.argv, so the script's own arguments read as before. For proposed values, without
editing the script:
  python3 write3mf.py preview build.py NAME=VALUE ... [--out DIR] [-- the script's own arguments]
sets each top-level NAME = ... line of the script to VALUE (a Python expression), so the lines after it follow,
runs it in DIR (default: here) and prints "preview: wrote [path]" per STL. Values set inside another module the
script loads aren't reached; run preview on that module if it writes the 3mf. picture.py draws these STLs.
"""
import datetime, io, json, math, os, sys, uuid, zipfile
from dataclasses import dataclass, field
import numpy as np

NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"')
HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n'
EYE = (-1.0, -1.6, 0.8)
PREVIEW = "--preview" in sys.argv or os.environ.get("WRITE3MF_PREVIEW") == "1"
while "--preview" in sys.argv:
    sys.argv.remove("--preview")


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


def _thumbs(objs, px=512, plate=1):
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
    for name, size in (("plate_%d.png" % plate, px), ("plate_%d_small.png" % plate, 128)):
        buf = io.BytesIO(); (im if size == px else im.resize((size, size), Image.LANCZOS)).save(buf, "PNG"); out[name] = buf.getvalue()
    return out


def _range_opts(opts, settings):
    """Every height range carries layer_height and extruder, or Orca crashes opening the file (learnings/speed-and-cooling)."""
    keys = {k for k, _ in opts}
    return list(opts) + [kv for kv in (("layer_height", settings.get("layer_height", "0.2")), ("extruder", "1")) if kv[0] not in keys]


NOT_EDITS = {'filament_colour', 'filament_multi_colour', 'filament_self_index', 'print_compatible_printers'}   # not preset edits: two spools of one preset may differ here


def _guard(objs, settings, cli=False):
    """Support off unless a part paints it, so the command-line slicer slices PETG HF; with cli, painted support's
    interface in the part's filament with 0.3 z gaps; one edited filament per preset name, since Orca keeps one set
    of edits per name (learnings/slicing-checks). Returns the settings."""
    painted = [p for o in objs for p in o.parts if p.paint is not None and any("paint_supports" in str(t) for t in p.paint)]
    if str(settings.get("enable_support", "0")) == "1" and not painted:
        settings = dict(settings, enable_support="0")
    if cli and painted and str(settings.get("enable_support", "0")) == "1":
        gap = lambda k: "%g" % max(0.3, float(settings.get(k, 0) or 0))
        settings = dict(settings, support_interface_filament=str(painted[0].extruder),
                        support_top_z_distance=gap("support_top_z_distance"), support_bottom_z_distance=gap("support_bottom_z_distance"))
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


def write(path, objs, settings, layer_gcode=None, plate_name=None, thumbnails=True, cli=False, plates=None, bed=256.0):
    """Write an Orca 2.4.2 3mf. layer_gcode: [(top_z, gcode)] for the layer slider (the command-line
    slicer drops these; put must-keep G-code in the printer's layer-change G-code instead). cli: a copy for
    /opt/orca/slice (module docstring). Returns path (with --preview, the STL's path)."""
    plates = plates or [(plate_name, list(range(len(objs))))]
    if PREVIEW:
        return _preview_stl(path, objs, plates, bed)
    settings = _guard(objs, settings, cli)
    cols = math.ceil(math.sqrt(len(plates))); stride = 1.2 * bed
    plate_of = {k: n for n, (_, ks) in enumerate(plates) for k in ks}
    pinst = [[] for _ in plates]
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
        n = plate_of[k]; dx, dy = (n % cols) * stride, -(n // cols) * stride
        for i, a in enumerate(o.at or [(c[0], c[1])]):
            tr = _turn(a[0] + dx, a[1] + dy, zc, a[2] if len(a) > 2 else 0.0)
            items.append('  <item objectid="%d" p:UUID="%s" transform="%s" printable="1"/>' % (oid, u("item%d.%d" % (oid, i)), tr))
            pinst[n].append('    <model_instance>\n      <metadata key="object_id" value="%d"/>\n      <metadata key="instance_id" value="%d"/>\n'
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
    model_settings = (HEAD + '<config>\n%s\n%s\n  <assemble>\n%s\n  </assemble>\n</config>\n'
                      % ("\n".join(cfg), "\n".join(
                          '  <plate>\n    <metadata key="plater_id" value="%d"/>\n    <metadata key="plater_name" value="%s"/>\n'
                          '    <metadata key="locked" value="false"/>\n    <metadata key="filament_map_mode" value="Auto For Flush"/>\n'
                          '    <metadata key="filament_maps" value="1 1"/>\n%s\n  </plate>'
                          % (n + 1, pn or stem.replace("_", " "), "\n".join(pinst[n])) for n, (pn, _) in enumerate(plates)),
                         "\n".join(asm)))
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
        "Metadata/filament_sequence.json": json.dumps({"plate_%d" % (n + 1): {"nozzle_sequence": [], "optimal_assignment": [], "sequence": []}
                                                       for n in range(len(plates))}),
    }
    if thumbnails:
        for n, (_, ks) in enumerate(plates):
            files.update(("Metadata/" + k, v) for k, v in _thumbs([objs[k] for k in ks], plate=n + 1).items())
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as z:   # level 1: about 5x faster, a little larger
        for name, data in files.items():
            z.writestr(name, data)
    if not cli:
        _master(path)
    return path


def _master(path):
    """Draw [file]_master.png beside the 3mf (picture.py --master, redesign 2026-10-05 section 11 item 7); a failed
    drawing is reported, never stops the build."""
    import subprocess
    out = os.path.splitext(os.path.abspath(path))[0] + "_master.png"
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "picture.py"), path,
                        "--master", "--out", out], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.startswith(("LAYOUT", "  ", "picture: wrote"))]
    print("\n".join(lines) if r.returncode == 0 else "master picture failed:\n" + (r.stdout + r.stderr)[-1500:], flush=True)


def _preview_stl(path, objs, plates, bed):
    """The 3mf's mesh as one STL, each instance where write() puts it (centered at its at, base on the bed, plate offset)."""
    import trimesh
    cols = math.ceil(math.sqrt(len(plates))); stride = 1.2 * bed
    plate_of = {k: n for n, (_, ks) in enumerate(plates) for k in ks}
    Vs, Ts, base = [], [], 0
    for k, o in enumerate(objs):
        V = np.vstack([np.asarray(p.V, float) for p in o.parts])
        T = np.vstack([np.asarray(p.T, int) + off for p, off in
                       zip(o.parts, np.cumsum([0] + [len(p.V) for p in o.parts[:-1]]))])
        lo, hi = V.min(0), V.max(0); c = (lo + hi) / 2.0; V = V - c
        n = plate_of[k]; dx, dy = (n % cols) * stride, -(n // cols) * stride
        for a in (o.at or [(c[0], c[1])]):
            t = math.radians(a[2] if len(a) > 2 else 0.0); cs, sn = math.cos(t), math.sin(t)
            P = np.c_[V[:, 0] * cs - V[:, 1] * sn + a[0] + dx, V[:, 0] * sn + V[:, 1] * cs + a[1] + dy, V[:, 2] + (hi[2] - lo[2]) / 2.0]
            Vs.append(P); Ts.append(T + base); base += len(P)
    out = os.environ.get("WRITE3MF_PREVIEW_DIR") or os.path.dirname(os.path.abspath(path))
    stl = os.path.join(out, os.path.splitext(os.path.basename(path))[0] + ".stl")
    trimesh.Trimesh(np.vstack(Vs), np.vstack(Ts), process=False).export(stl)
    print("preview: wrote", stl, flush=True)
    return stl


def _override(src, values, script):
    """The script's source tree with each top-level NAME = ... set to the expression VALUE."""
    import ast
    tree = ast.parse(src, script)
    for name, expr in values.items():
        hit = False
        for node in tree.body:
            tg = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
            if any(isinstance(t, ast.Name) and t.id == name for t in tg):
                if len(tg) != 1:
                    sys.exit("preview: %s is set together with other names on one line in %s; split it first" % (name, script))
                node.value = ast.parse(expr, mode="eval").body; hit = True
        if not hit:
            sys.exit("preview: %s isn't set at the top level of %s" % (name, script))
    return ast.fix_missing_locations(tree)


def preview(script, values=None, out=None, args=()):
    """Run build script with --preview and values {NAME: "expression"}; returns the STL paths it wrote."""
    import subprocess
    out = os.path.abspath(out or "."); os.makedirs(out, exist_ok=True)
    env = dict(os.environ, WRITE3MF_PREVIEW="1", WRITE3MF_PREVIEW_DIR=out)
    cmd = [sys.executable, os.path.abspath(__file__), "_run", os.path.abspath(script)] + ["%s=%s" % kv for kv in (values or {}).items()] + ["--"] + list(args)
    r = subprocess.run(cmd, cwd=out, env=env, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("preview of %s failed:\n%s" % (script, (r.stdout + r.stderr)[-3000:]))
    paths = [l.split("preview: wrote ", 1)[1].strip() for l in r.stdout.splitlines() if l.startswith("preview: wrote ")]
    if not paths:
        raise RuntimeError("preview: %s wrote no 3mf through write3mf.write (an older script with its own writer?)\n%s" % (script, r.stdout[-2000:]))
    return paths


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "_run":   # inside preview(): run the script as __main__ with its values set
        script = sys.argv[2]; rest = sys.argv[3:]; cut = rest.index("--") if "--" in rest else len(rest)
        values = dict(a.split("=", 1) for a in rest[:cut])
        sys.modules.setdefault("write3mf", sys.modules["__main__"])   # the script's import of write3mf finds this one
        sys.argv = [script] + rest[cut + 1:]; sys.path.insert(0, os.path.dirname(script))
        g = {"__name__": "__main__", "__file__": script}
        exec(compile(_override(open(script).read(), values, script), script, "exec"), g)
    elif len(sys.argv) > 2 and sys.argv[1] == "preview":
        a = sys.argv[2:]; cut = a.index("--") if "--" in a else len(a); rest, sargs = a[:cut], a[cut + 1:]
        out = rest[rest.index("--out") + 1] if "--out" in rest else "."
        rest = [x for i, x in enumerate(rest) if x != "--out" and (i == 0 or rest[i - 1] != "--out")]
        for p in preview(rest[0], dict(x.split("=", 1) for x in rest[1:]), out, sargs):
            print("preview: wrote", p)
    else:
        sys.exit(__doc__)
