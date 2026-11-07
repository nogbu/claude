#!/usr/bin/env python3
"""Builds photoBoard_rev1.1_marker-test.3mf (product calibration-rig, 3dp project): a test strip for the
photo board's marker inlay, printed before the full board (photoBoard_rev1.3mf).

Needs beside it: rfidSpring_settings_base.json (my P1S 0.6 printer and process settings, saved with
rfidSpring_rev1). make_settings() turns it into this file's project settings: both filaments set to the
Orca 2.4.2 system preset "Bambu PLA Matte @BBL X1C" (values in PLA_MATTE below; filament 1 white,
filament 2 black), skirt off, prime tower off, gyroid 15% infill, flushing 140 mm3 into black and
700 mm3 into white.
Needs: numpy, opencv-contrib-python (cv2.aruco), matplotlib (thumbnails).

Geometry (all mm; x across the rail, y along it, z up; z = 0 is the bed):
- A section of the board's rail: 17.55 wide x 75 long, 6.3 tall (4.2 floor + 2.1 rail = 21 layers of 0.3).
- Markers: ArUco DICT_4X4_50, 6 x 6 cells of 1.86 (3 beads at the 0.62 line width) = 11.16 square.
  IDs 0 and 1 on the rail top, centered on the strip's width at y 12 and 37 (25 apart, as on the board).
- Post: 14.88 x 14.88 (the marker plus one white cell each side), centered at y 60, from the rail top
  to z 34.2 (30.0 above the 4.2 floor; 114 layers in all). Marker ID 27 on its top.
- Black is used only in the top layer of each marker (z 6.0-6.3 and 33.9-34.2), white below it
  (the user's rule: black on the visible surfaces only).
- Two parts: "body" on filament 1 (white) and "markers" on filament 2 (black, or any dark color).
- Each part is a set of separate closed boxes. Boxes that would touch inside a part are inset by
  EPS in x-y so nothing touches; Orca's 0.049 mm slice gap closing joins them back up.
"""
import io, json, math, os, uuid, zipfile, datetime
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "photoBoard_rev1.1_marker-test"

# ------------------------------------------------------------------ parameters
LAYER = 0.3
LINE = 0.62
CELL = 3 * LINE                    # 1.86
MK = 6 * CELL                      # 11.16, marker incl. its black border
FLOOR, RAIL_RISE = 4.2, 2.1        # 14 and 7 layers
TOP = FLOOR + RAIL_RISE            # 6.3, rail top = marker plane
POST_ABOVE_FLOOR = 30.0            # 100 layers
POST_TOP = FLOOR + POST_ABOVE_FLOOR  # 34.2
POST_W = MK + 2 * CELL             # 14.88
INLAY_LAYERS = 1                   # black only in the top layer
STRIP_W, STRIP_L = 17.55, 75.0
CX = STRIP_W / 2
RAIL_MARKERS = [(0, CX, 12.0), (1, CX, 37.0)]
POST = (27, CX, 60.0)
EPS = 0.005
FLUSH = ["0", "140", "700", "0"]   # mm3: white into black (costs black), black into white
DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

for name, v in (("FLOOR", FLOOR), ("TOP", TOP), ("POST_TOP", POST_TOP), ("inlay", INLAY_LAYERS * LAYER)):
    n = v / LAYER
    assert abs(n - round(n)) < 1e-9, "%s %.3f is off the %.1f mm layer grid" % (name, v, LAYER)


def marker_cells(mid, cx, cy):
    """Black cells of marker mid centered at (cx, cy): list of (x0, x1, y0, y1). Image row 0 is the
    back edge (+y), so the marker reads unmirrored from above."""
    img = cv2.aruco.generateImageMarker(DICT, mid, 6)
    x0, y0 = cx - MK / 2, cy - MK / 2
    cells = []
    for r in range(6):
        for c in range(6):
            if img[r, c] < 128:
                xa = x0 + c * CELL
                ya = y0 + (5 - r) * CELL
                cells.append((xa, xa + CELL, ya, ya + CELL))
    return cells


def split_rect(rect, black):
    """Split rect (x0, x1, y0, y1) into white and black rectangles on the grid of all edges,
    merged into runs along x, then identical runs merged along y."""
    X = sorted({rect[0], rect[1]} | {v for b in black for v in b[:2]})
    Y = sorted({rect[2], rect[3]} | {v for b in black for v in b[2:]})
    def is_black(xm, ym):
        return any(b[0] < xm < b[1] and b[2] < ym < b[3] for b in black)
    out = {False: [], True: []}
    rows = []
    for j in range(len(Y) - 1):
        ym = (Y[j] + Y[j + 1]) / 2
        runs, i = [], 0
        while i < len(X) - 1:
            col = is_black((X[i] + X[i + 1]) / 2, ym)
            k = i
            while k + 1 < len(X) - 1 and is_black((X[k + 1] + X[k + 2]) / 2, ym) == col:
                k += 1
            runs.append((X[i], X[k + 1], col))
            i = k + 1
        rows.append((Y[j], Y[j + 1], runs))
    # merge identical consecutive rows
    merged = []
    for y0, y1, runs in rows:
        if merged and merged[-1][2] == runs and abs(merged[-1][1] - y0) < 1e-9:
            merged[-1][1] = y1
        else:
            merged.append([y0, y1, runs])
    for y0, y1, runs in merged:
        for xa, xb, col in runs:
            out[col].append((xa, xb, y0, y1))
    return out[False], out[True]


class Mesh:
    def __init__(self):
        self.V, self.T, self.shells = [], [], []

    def box(self, x0, x1, y0, y1, z0, z1):
        b = len(self.V)
        self.V += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                   (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        f = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
             (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
        self.T += [(b + i, b + j, b + k) for i, j, k in f]
        self.shells.append((b, b + 8))


def inset(r, outer):
    """Pull each side of r in by EPS unless that side lies on the outer boundary."""
    x0, x1, y0, y1 = r
    ox0, ox1, oy0, oy1 = outer
    return (x0 + (EPS if abs(x0 - ox0) > 1e-9 else 0), x1 - (EPS if abs(x1 - ox1) > 1e-9 else 0),
            y0 + (EPS if abs(y0 - oy0) > 1e-9 else 0), y1 - (EPS if abs(y1 - oy1) > 1e-9 else 0))


def check_closed(M):
    T = np.array(M.T)
    for v0, v1 in M.shells:
        sel = T[(T[:, 0] >= v0) & (T[:, 0] < v1)]
        e = np.concatenate([sel[:, [0, 1]], sel[:, [1, 2]], sel[:, [2, 0]]])
        key = e[:, 0].astype(np.int64) * 10_000_000 + e[:, 1]
        rkey = e[:, 1].astype(np.int64) * 10_000_000 + e[:, 0]
        if len(np.unique(key)) != len(key) or not np.array_equal(np.sort(key), np.sort(rkey)):
            raise RuntimeError("shell %s is not closed" % ((v0, v1),))
    V = np.array(M.V)
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)


def build():
    body, marks = Mesh(), Mesh()
    zi = TOP - INLAY_LAYERS * LAYER                       # 6.0
    strip = (0.0, STRIP_W, 0.0, STRIP_L)
    body.box(*strip, 0.0, zi)
    black = [c for mid, x, y in RAIL_MARKERS for c in marker_cells(mid, x, y)]
    white, blk = split_rect(strip, black)
    for r in white:
        body.box(*inset(r, strip), zi, TOP)
    for r in blk:
        marks.box(*inset(r, strip), zi, TOP)
    pid, px, py = POST
    prect = (px - POST_W / 2, px + POST_W / 2, py - POST_W / 2, py + POST_W / 2)
    pz = POST_TOP - INLAY_LAYERS * LAYER                  # 33.9
    body.box(*prect, TOP, pz)
    white, blk = split_rect(prect, marker_cells(pid, px, py))
    for r in white:
        body.box(*inset(r, prect), pz, POST_TOP)
    for r in blk:
        marks.box(*inset(r, prect), pz, POST_TOP)
    vb, vm = check_closed(body), check_closed(marks)
    return body, marks, dict(body_cm3=vb / 1000, markers_cm3=vm / 1000, body_boxes=len(body.shells),
                             marker_boxes=len(marks.shells), height=POST_TOP, layers=round(POST_TOP / LAYER))


def top_view_check(marks, px_per_mm=20):
    """Rasterize the black boxes seen from above and confirm the markers decode to the intended IDs."""
    W, H = int((STRIP_W + 10) * px_per_mm), int((STRIP_L + 10) * px_per_mm)
    img = np.full((H, W), 235, np.uint8)
    V = np.array(marks.V)
    for v0, v1 in marks.shells:
        x0, y0 = V[v0:v1, 0].min(), V[v0:v1, 1].min()
        x1, y1 = V[v0:v1, 0].max(), V[v0:v1, 1].max()
        c0, c1 = int(round((x0 + 5) * px_per_mm)), int(round((x1 + 5) * px_per_mm))
        r0, r1 = int(round(H - (y1 + 5) * px_per_mm)), int(round(H - (y0 + 5) * px_per_mm))
        img[r0:r1, c0:c1] = 20
    c, ids, _ = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters()).detectMarkers(img)
    return sorted([] if ids is None else ids.ravel().tolist())


PLA_MATTE = {  # Orca 2.4.2 system preset "Bambu PLA Matte @BBL X1C", one filament's values per key
    "activate_air_filtration": ["0", "0"],
    "additional_cooling_fan_speed": ["70"],
    "additional_fan_full_speed_layer": ["0"],
    "close_additional_fan_first_x_layers": ["3"],
    "close_fan_the_first_x_layers": ["1"],
    "complete_print_exhaust_fan_speed": ["70", "70"],
    "cool_plate_temp": ["35"],
    "cool_plate_temp_initial_layer": ["35"],
    "during_print_exhaust_fan_speed": ["70", "70"],
    "eng_plate_temp": ["0"],
    "eng_plate_temp_initial_layer": ["0"],
    "fan_cooling_layer_time": ["100"],
    "fan_max_speed": ["100"],
    "fan_min_speed": ["100"],
    "filament_adaptive_volumetric_speed": ["0", "0"],
    "filament_adhesiveness_category": ["100"],
    "filament_cost": ["24.99"],
    "filament_density": ["1.32"],
    "filament_deretraction_speed": ["nil", "nil"],
    "filament_diameter": ["1.75"],
    "filament_end_gcode": ["; filament end gcode \n\n"],
    "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
    "filament_flow_ratio": ["0.98", "0.98"],
    "filament_flush_temp": ["0", "0"],
    "filament_flush_volumetric_speed": ["0", "0"],
    "filament_is_support": ["0"],
    "filament_long_retractions_when_cut": ["1", "1"],
    "filament_max_volumetric_speed": ["22", "22"],
    "filament_minimal_purge_on_wipe_tower": ["15"],
    "filament_printable": ["3"],
    "filament_retract_before_wipe": ["nil", "nil"],
    "filament_retract_restart_extra": ["nil", "nil"],
    "filament_retract_when_changing_layer": ["nil", "nil"],
    "filament_retraction_distances_when_cut": ["18", "18"],
    "filament_retraction_length": ["nil", "nil"],
    "filament_retraction_minimum_travel": ["nil", "nil"],
    "filament_retraction_speed": ["nil", "nil"],
    "filament_shrink": ["100%"],
    "filament_soluble": ["0"],
    "filament_start_gcode": ["; filament start gcode\n{if  (bed_temperature[current_extruder] >55)||(bed_temperature_initial_layer[current_extruder] >55)}M106 P3 S200\n{elsif(bed_temperature[current_extruder] >50)||(bed_temperature_initial_layer[current_extruder] >50)}M106 P3 S150\n{elsif(bed_temperature[current_extruder] >45)||(bed_temperature_initial_layer[current_extruder] >45)}M106 P3 S50\n{endif}\nM142 P1 R35 S40\n{if activate_air_filtration[current_extruder] && support_air_filtration}\nM106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n{endif}"],
    "filament_tower_interface_pre_extrusion_dist": ["10"],
    "filament_tower_interface_pre_extrusion_length": ["0"],
    "filament_tower_interface_print_temp": ["-1"],
    "filament_tower_interface_purge_volume": ["20"],
    "filament_tower_ironing_area": ["4"],
    "filament_type": ["PLA"],
    "filament_vendor": ["Bambu Lab"],
    "filament_wipe": ["nil", "nil"],
    "filament_wipe_distance": ["nil", "nil"],
    "filament_z_hop": ["nil", "nil"],
    "filament_z_hop_types": ["nil", "nil"],
    "full_fan_speed_layer": ["0"],
    "hot_plate_temp": ["55"],
    "hot_plate_temp_initial_layer": ["55"],
    "long_retractions_when_ec": ["0", "0"],
    "nozzle_temperature": ["220", "220"],
    "nozzle_temperature_initial_layer": ["220", "220"],
    "nozzle_temperature_range_high": ["240"],
    "nozzle_temperature_range_low": ["190"],
    "overhang_fan_speed": ["100"],
    "overhang_fan_threshold": ["50%"],
    "reduce_fan_stop_start_freq": ["1"],
    "required_nozzle_HRC": ["3"],
    "retraction_distances_when_ec": ["0", "0"],
    "slow_down_for_layer_cooling": ["1"],
    "slow_down_layer_time": ["4"],
    "slow_down_min_speed": ["20"],
    "supertack_plate_temp": ["45"],
    "supertack_plate_temp_initial_layer": ["45"],
    "temperature_vitrification": ["45"],
    "textured_plate_temp": ["55"],
    "textured_plate_temp_initial_layer": ["55"],
    "volumetric_speed_coefficients": ["0 0 0 0 0 0", "0 0 0 0 0 0"],
}


def make_settings():
    s = json.load(open(os.path.join(HERE, "rfidSpring_settings_base.json")))
    for k, v in PLA_MATTE.items():
        assert len(s[k]) == 2 * len(v), k
        s[k] = list(v) * 2
    s["filament_settings_id"] = ["Bambu PLA Matte @BBL X1C"] * 2
    s["filament_ids"] = ["GFA01"] * 2
    s["filament_colour"] = ["#FFFFFF", "#000000"]
    s["filament_change_length"] = ["10", "10"]
    s["flush_volumes_matrix"] = list(FLUSH)
    s["skirt_loops"] = "0"
    s["enable_prime_tower"] = "0"
    s["sparse_infill_pattern"] = "gyroid"
    s["sparse_infill_density"] = "15%"
    proc = set(s["different_settings_to_system"][0].split(";")) | {"enable_prime_tower", "skirt_loops", "sparse_infill_pattern"}
    s["different_settings_to_system"] = [";".join(sorted(proc)), "", "", s["different_settings_to_system"][3]]
    return s


# ------------------------------------------------------------------ 3mf
def _uuid(tag):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "calibration-rig/%s/%s" % (NAME, tag)))


def _fmt(v):
    s = ("%.5f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def thumbnails(body, marks):
    out = {}
    for name, px in (("plate_1.png", 512), ("plate_1_small.png", 128)):
        fig = plt.figure(figsize=(px / 100, px / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor("#e8e8e8")
        for M, col in ((body, "#f4f4f4"), (marks, "#111111")):
            V = np.array(M.V)
            for v0, v1 in M.shells:
                x0, y0 = V[v0:v1, 0].min(), V[v0:v1, 1].min()
                x1, y1 = V[v0:v1, 0].max(), V[v0:v1, 1].max()
                ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fc=col, ec="none"))
        ax.set_xlim(CX - STRIP_L / 2 - 5, CX + STRIP_L / 2 + 5)
        ax.set_ylim(-5, STRIP_L + 5)
        ax.set_aspect("equal")
        ax.axis("off")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=100)
        plt.close(fig)
        out[name] = buf.getvalue()
    return out


def mesh_xml(oid, M, cx, cy, zoff, tag):
    lines = ['  <object id="%d" p:UUID="%s" type="model">' % (oid, _uuid(tag)), '   <mesh>', '    <vertices>']
    lines += ['     <vertex x="%s" y="%s" z="%s"/>' % (_fmt(x - cx), _fmt(y - cy), _fmt(z - zoff)) for x, y, z in M.V]
    lines += ['    </vertices>', '    <triangles>']
    lines += ['     <triangle v1="%d" v2="%d" v3="%d"/>' % t for t in M.T]
    lines += ['    </triangles>', '   </mesh>', '  </object>']
    return lines


def write_3mf(path, body, marks):
    settings = make_settings()
    zoff = POST_TOP / 2.0
    cx, cy = STRIP_W / 2.0, STRIP_L / 2.0
    obj_path = "/3D/Objects/%s.model" % NAME
    head = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">',
            ' <metadata name="BambuStudio:3mfVersion">1</metadata>', ' <resources>']
    objs = mesh_xml(1, body, cx, cy, zoff, "body") + mesh_xml(2, marks, cx, cy, zoff, "markers")
    model = "\n".join(head + objs + [' </resources>', ' <build/>', '</model>', ''])
    today = datetime.date.today().isoformat()
    root = '''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">
 <metadata name="Application">BambuStudio-02.06.00.51</metadata>
 <metadata name="OrcaSlicer">2.4.2</metadata>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <metadata name="CreationDate">%s</metadata>
 <metadata name="ModificationDate">%s</metadata>
 <metadata name="Thumbnail_Middle">/Metadata/plate_1.png</metadata>
 <metadata name="Thumbnail_Small">/Metadata/plate_1_small.png</metadata>
 <metadata name="Title"></metadata>
 <resources>
  <object id="3" p:UUID="%s" type="model">
   <components>
    <component p:path="%s" objectid="1" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
    <component p:path="%s" objectid="2" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
   </components>
  </object>
 </resources>
 <build p:UUID="%s">
  <item objectid="3" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 128 128 %s" printable="1" auto_drop="1"/>
 </build>
</model>
''' % (today, today, _uuid("object"), obj_path, _uuid("component-body"), obj_path, _uuid("component-markers"),
       _uuid("build"), _uuid("item"), _fmt(zoff))

    def part(pid, name, extruder):
        return [' <part id="%d" subtype="normal_part">' % pid,
                '  <metadata key="name" value="%s"/>' % name,
                '  <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>',
                '  <metadata key="extruder" value="%d"/>' % extruder,
                '  <metadata key="source_file" value="%s.3mf"/>' % NAME,
                '  <metadata key="source_object_id" value="0"/>',
                '  <metadata key="source_volume_id" value="%d"/>' % (pid - 1),
                '  <metadata key="source_offset_x" value="0"/>',
                '  <metadata key="source_offset_y" value="0"/>',
                '  <metadata key="source_offset_z" value="0"/>',
                '  <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>',
                ' </part>']
    ms = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>', ' <object id="3">',
          '  <metadata key="name" value="%s"/>' % NAME, '  <metadata key="extruder" value="1"/>']
    ms += part(1, "body", 1) + part(2, "markers", 2)
    ms += [' </object>', ' <plate>',
           '  <metadata key="plater_id" value="1"/>',
           '  <metadata key="plater_name" value="%s"/>' % NAME.replace("_", " "),
           '  <metadata key="locked" value="false"/>',
           '  <metadata key="filament_map_mode" value="Auto For Flush"/>',
           '  <metadata key="filament_maps" value="1 1"/>',
           '  <model_instance>', '   <metadata key="object_id" value="3"/>',
           '   <metadata key="instance_id" value="0"/>', '   <metadata key="identify_id" value="300"/>',
           '  </model_instance>', ' </plate>', ' <assemble>',
           '  <assemble_item object_id="3" instance_id="0" transform="1 0 0 0 1 0 0 0 1 128 128 %s" offset="0 0 0" />' % _fmt(zoff),
           ' </assemble>', '</config>', '']
    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>
'''
    rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
 <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>
 <Relationship Target="/Metadata/plate_1.png" Id="rel-4" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-middle"/>
 <Relationship Target="/Metadata/plate_1_small.png" Id="rel-5" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-small"/>
</Relationships>
'''
    model_rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="%s" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
''' % obj_path
    slice_info = '''<?xml version="1.0" encoding="UTF-8"?>
<config>
  <header>
    <header_item key="X-BBL-Client-Type" value="slicer"/>
    <header_item key="X-BBL-Client-Version" value="02.06.00.51"/>
    <header_item key="OrcaSlicer-Version" value="2.4.2"/>
  </header>
</config>
'''
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", root)
        z.writestr("3D/_rels/3dmodel.model.rels", model_rels)
        z.writestr(obj_path.lstrip("/"), model)
        z.writestr("Metadata/project_settings.config", json.dumps(settings, indent=4, ensure_ascii=False))
        z.writestr("Metadata/model_settings.config", "\n".join(ms))
        z.writestr("Metadata/layer_config_ranges.xml", '<?xml version="1.0" encoding="utf-8"?>\n<objects>\n</objects>\n')
        z.writestr("Metadata/custom_gcode_per_layer.xml", '<?xml version="1.0" encoding="utf-8"?>\n<custom_gcodes_per_layer>\n</custom_gcodes_per_layer>\n')
        z.writestr("Metadata/slice_info.config", slice_info)
        z.writestr("Metadata/filament_sequence.json", '{"plate_1": {"nozzle_sequence": [], "optimal_assignment": [], "sequence": []}}')
        for pname, data in thumbnails(body, marks).items():
            z.writestr("Metadata/" + pname, data)
    return path


def main(out_dir="."):
    body, marks, info = build()
    info["decoded_ids"] = top_view_check(marks)
    expect = sorted([m[0] for m in RAIL_MARKERS] + [POST[0]])
    if info["decoded_ids"] != expect:
        raise RuntimeError("markers decode as %s, expected %s" % (info["decoded_ids"], expect))
    info["path"] = write_3mf(os.path.join(out_dir, NAME + ".3mf"), body, marks)
    return info


if __name__ == "__main__":
    for k, v in main().items():
        print(k, v)
