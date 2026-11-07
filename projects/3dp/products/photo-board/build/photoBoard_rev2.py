#!/usr/bin/env python3
"""Builds photoBoard_rev2.3mf (product calibration-rig, 3dp project): the photo board for photographing
filament calibration test pieces, with inlaid ArUco markers on its rails and two marker posts.

Needs beside it: rfidSpring_settings_base.json (my P1S 0.6 printer and process settings, saved with
rfidSpring_rev1). make_settings() turns it into this file's project settings: both filaments set to the
Orca 2.4.2 system preset "Bambu PLA Matte @BBL X1C" (values in PLA_MATTE below; filament 1 the body,
color #CBC6B8 = Bambu PLA Matte Bone White, so AMS color matching picks it; filament 2 black #000000 =
Charcoal), skirt off, prime tower off, gyroid 15% infill, flushing 140 mm3 into black and 700 mm3 back
into the body color.
Needs: numpy, opencv-contrib-python (cv2.aruco), matplotlib (thumbnails).

Geometry (all mm, Orca plate coordinates; x left-right, y front-back, z up; z = 0 is the bed). Design
agreed 2026-10-02; changes 2026-10-03: 2-layer inlay, board shortened to clear the excluded corner,
3-bead label outline (rev1); fillets on every vertical edge and the Bone White color code (rev2):
- Board 252 x 224 at x 2-254, y 30-254, clear of the P1S's excluded corner (x 0-18, y 0-28). Orca checks
  an object's convex outline against that corner, so a notch can't clear it. Floor 4.2 (14 layers).
- Rails 17.55 wide (x 2-19.55 and x 236.45-254) and the closed-end strip (y 227-254) rise 2.1 (7 layers)
  to z 6.3, the marker plane. Open channel x 19.55-236.45, y 30-227; stop at y 227.
- Fillets (vertical edges only): 3 mm on the board's 4 outer corners, on the rails' front inner corners
  (19.55, 30) and (236.45, 30), and filling the channel's back inside corners (19.55, 227) and
  (236.45, 227); 1.5 mm on the posts' 8 edges. Markers, their white margins, the posts' markers and the
  label outline are untouched (asserted below); nearest clearance about 1 mm.
- Markers: ArUco DICT_4X4_50, 6 x 6 cells of 1.86 (3 beads at 0.62) = 11.16 square, black inlay 2 layers
  (0.6) deep, body color below. Left rail x 10.775, y 40-215 every 25 (IDs 0-7, front to back);
  closed-end row y 240.5, x 31.55-224.45 (IDs 9-17, left to right); right rail x 245.225, y 215-90
  every 25 (IDs 19-24, back to front). IDs 8, 18, 25 and 26 unused.
- Posts: 14.88 square, centered (10.775, 240.5) and (245.225, 240.5), from the rail top to z 34.2
  (30.0 above the floor), markers ID 27 (left) and 28 (right) on their tops.
- Label patch: x 237.7-252.7, y 32-80, outlined by a black band 3 beads (1.86) wide, 2 layers deep.
- Two parts: "body" on filament 1 and "markers" on filament 2. Each part is a set of separate closed
  convex prisms (boxes, rounded pieces and fan triangles for the inside fillets), every side pulled in
  by EPS so pieces never touch; Orca's 0.049 mm slice gap closing joins them.
- Orca's G-code puts the board 2.0 mm further forward (y 28-252) than these plate coordinates; the
  rev1.1 strip shows the same shift, so it is Orca's plate mapping, not a placement error (2026-10-03).
"""
import io, json, math, os, uuid, zipfile, datetime
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "photoBoard_rev2"

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
INLAY_LAYERS = 2                   # black in the top two layers (2026-10-03)
OUTLINE_W = CELL                   # 1.86, 3 beads (2026-10-03)
BX0, BX1, BY0, BY1 = 2.0, 254.0, 30.0, 254.0
RAIL_W = 17.55
LX1 = BX0 + RAIL_W                 # 19.55, left rail inner edge
RX0 = BX1 - RAIL_W                 # 236.45, right rail inner edge
STOP_Y = 227.0                     # closed-end strip inner edge
LEFT_RAIL_Y0 = BY0
LCX, RCX = (BX0 + LX1) / 2, (RX0 + BX1) / 2     # 10.775, 245.225
ROW_Y = 240.5
RAIL_MARKERS = ([(i, LCX, 40.0 + 25 * i) for i in range(8)] +
                [(9 + i, x, ROW_Y) for i, x in enumerate(np.linspace(31.55, 224.45, 9))] +
                [(19 + i, RCX, 215.0 - 25 * i) for i in range(6)])
POSTS = [(27, LCX, ROW_Y), (28, RCX, ROW_Y)]
LABEL = (237.7, 252.7, 32.0, 80.0)
R_OUTER = 3.0                      # board's 4 outer corners (2026-10-03)
R_RAIL_FRONT = 3.0                 # rails' front inner corners
R_CHANNEL = 3.0                    # channel's back inside corners (fillet fills the corner)
R_POST = 1.5                       # posts' vertical edges
ARC_SEGS = 12                      # segments per quarter circle (chord error 0.006 mm at 3 mm)
BODY_COLOR, BLACK_COLOR = "#CBC6B8", "#000000"   # Bambu PLA Matte Bone White, Charcoal
EPS = 0.005
FLUSH = ["0", "140", "700", "0"]   # mm3: body into black (costs black), black into body
DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
EXPECT_IDS = sorted([m[0] for m in RAIL_MARKERS] + [p[0] for p in POSTS])

for name, v in (("FLOOR", FLOOR), ("TOP", TOP), ("POST_TOP", POST_TOP), ("inlay", INLAY_LAYERS * LAYER)):
    n = v / LAYER
    assert abs(n - round(n)) < 1e-9, "%s %.3f is off the %.1f mm layer grid" % (name, v, LAYER)
assert abs(OUTLINE_W / LINE - round(OUTLINE_W / LINE)) < 1e-9, "outline is not whole beads"

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
    snap = lambda v: round(v, 6)   # merge edges that differ only by float error (rev1 got 23 sliver pieces)
    X = sorted({snap(rect[0]), snap(rect[1])} | {snap(v) for b in black for v in b[:2]})
    Y = sorted({snap(rect[2]), snap(rect[3])} | {snap(v) for b in black for v in b[2:]})
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
        self.V, self.T, self.shells, self.polys = [], [], [], []

    def prism(self, poly, z0, z1):
        """Closed prism over a convex CCW polygon."""
        b, n = len(self.V), len(poly)
        self.V += [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
        for i in range(1, n - 1):
            self.T.append((b, b + i + 1, b + i))              # bottom, facing down
            self.T.append((b + n, b + n + i, b + n + i + 1))  # top, facing up
        for i in range(n):
            j = (i + 1) % n
            self.T.append((b + i, b + j, b + n + j))
            self.T.append((b + i, b + n + j, b + n + i))
        self.shells.append((b, b + 2 * n))
        self.polys.append(list(poly))


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


def area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))


def clean(poly, tol=1e-7):
    """Drop repeated and collinear vertices; return [] for a degenerate polygon."""
    out = []
    for p in poly:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > tol:
            out.append(p)
    if len(out) > 1 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= tol:
        out.pop()
    changed = True
    while changed and len(out) >= 3:
        changed = False
        for i in range(len(out)):
            a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
            if abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) < 1e-10:
                out.pop(i)
                changed = True
                break
    return out if len(out) >= 3 and area(out) > 1e-6 else []


def rect_poly(r):
    x0, x1, y0, y1 = r
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rounded_rect(r, radii):
    """CCW convex outline of rect r with rounded corners; radii maps 'bl', 'br', 'tr', 'tl' to a radius."""
    x0, x1, y0, y1 = r
    pts = []
    for name, cx, cy, sx, sy, a0 in (("bl", x0, y0, 1, 1, math.pi), ("br", x1, y0, -1, 1, 1.5 * math.pi),
                                     ("tr", x1, y1, -1, -1, 0.0), ("tl", x0, y1, 1, -1, 0.5 * math.pi)):
        rad = radii.get(name, 0.0)
        if rad <= 0:
            pts.append((cx, cy))
            continue
        ox, oy = cx + sx * rad, cy + sy * rad
        pts += [(ox + rad * math.cos(a0 + math.pi / 2 * i / ARC_SEGS), oy + rad * math.sin(a0 + math.pi / 2 * i / ARC_SEGS))
                for i in range(ARC_SEGS + 1)]
    return clean(pts)


def clip(subject, clipper):
    """Sutherland-Hodgman: convex CCW subject clipped by convex CCW clipper."""
    out = subject
    for i in range(len(clipper)):
        (ax, ay), (bx, by) = clipper[i], clipper[(i + 1) % len(clipper)]
        inp, out = out, []
        if not inp:
            break
        side = lambda p: (bx - ax) * (p[1] - ay) - (by - ay) * (p[0] - ax)
        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            sp, sq = side(p), side(q)
            if sp >= -1e-12:
                out.append(p)
                if sq < -1e-12:
                    t = sp / (sp - sq)
                    out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
            elif sq >= -1e-12:
                t = sp / (sp - sq)
                out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return clean(out)


def shrink(poly, d=EPS):
    """Pull every edge of a convex CCW polygon in by d."""
    n, lines = len(poly), []
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        L = math.hypot(ex, ey)
        lines.append((ax - ey / L * d, ay + ex / L * d, ex, ey))
    out = []
    for i in range(n):
        x1, y1, dx1, dy1 = lines[i - 1]
        x2, y2, dx2, dy2 = lines[i]
        den = dx1 * dy2 - dy1 * dx2
        t = ((x2 - x1) * dy2 - (y2 - y1) * dx2) / den
        out.append((x1 + dx1 * t, y1 + dy1 * t))
    assert area(out) > 0, "polygon too small to shrink"
    return out


def inside_fillet(cx, cy, sx, sy, r):
    """Fan triangles filling an inside corner at (cx, cy); the open side points along (sx, sy)."""
    ox, oy = cx + sx * r, cy + sy * r
    a1, a2 = math.atan2(0, cx - ox), math.atan2(cy - oy, 0)    # arc ends on the two faces
    if abs(a1 - a2) > math.pi:
        a2 += 2 * math.pi if a2 < a1 else -2 * math.pi
    arc = [(ox + r * math.cos(a1 + (a2 - a1) * i / ARC_SEGS), oy + r * math.sin(a1 + (a2 - a1) * i / ARC_SEGS))
           for i in range(ARC_SEGS + 1)]
    tris = []
    for i in range(ARC_SEGS):
        t = [(cx, cy), arc[i], arc[i + 1]]
        if area(t) < 0:
            t = [t[0], t[2], t[1]]
        tris.append(t)
    return tris


def add(mesh, poly, z0, z1):
    if poly:
        mesh.prism(shrink(poly), z0, z1)


def label_band():
    x0, x1, y0, y1 = LABEL
    w = OUTLINE_W
    return [(x0, x1, y0, y0 + w), (x0, x1, y1 - w, y1), (x0, x0 + w, y0 + w, y1 - w), (x1 - w, x1, y0 + w, y1 - w)]


def inside(c, r):
    return c[0] >= r[0] - 1e-9 and c[1] <= r[1] + 1e-9 and c[2] >= r[2] - 1e-9 and c[3] <= r[3] + 1e-9


def build():
    body, marks = Mesh(), Mesh()
    zi = TOP - INLAY_LAYERS * LAYER                       # 5.7
    board = (BX0, BX1, BY0, BY1)
    add(body, rounded_rect(board, dict(bl=R_OUTER, br=R_OUTER, tr=R_OUTER, tl=R_OUTER)), 0.0, FLOOR)
    rails = [(BX0, LX1, LEFT_RAIL_Y0, STOP_Y), (BX0, BX1, STOP_Y, BY1), (RX0, BX1, BY0, STOP_Y)]
    clips = [rounded_rect(rails[0], dict(bl=R_OUTER, br=R_RAIL_FRONT)),
             rounded_rect(rails[1], dict(tl=R_OUTER, tr=R_OUTER)),
             rounded_rect(rails[2], dict(bl=R_RAIL_FRONT, br=R_OUTER))]
    black = [c for mid, x, y in RAIL_MARKERS for c in marker_cells(mid, x, y)] + label_band()
    used = 0
    for r, cl in zip(rails, clips):
        add(body, clip(rect_poly(r), cl), FLOOR, zi)
        mine = [c for c in black if inside(c, r)]
        used += len(mine)
        white, blk = split_rect(r, mine)
        for q in white:
            add(body, clip(rect_poly(q), cl), zi, TOP)
        for q in blk:
            p = clip(rect_poly(q), cl)
            assert abs(area(p) - area(rect_poly(q))) < 1e-9, "a fillet would cut a marker or the label outline"
            add(marks, p, zi, TOP)
    assert used == len(black), "a black cell straddles two rail rectangles"
    for cx, sx in ((LX1, 1), (RX0, -1)):                  # channel's back inside corners
        for t in inside_fillet(cx, STOP_Y, sx, -1, R_CHANNEL):
            add(body, t, FLOOR, TOP)
    pz = POST_TOP - INLAY_LAYERS * LAYER                  # 33.6
    for pid, px, py in POSTS:
        prect = (px - POST_W / 2, px + POST_W / 2, py - POST_W / 2, py + POST_W / 2)
        assert inside(prect, rails[1]), "post off the closed-end strip"
        pcl = rounded_rect(prect, dict(bl=R_POST, br=R_POST, tr=R_POST, tl=R_POST))
        add(body, pcl, TOP, pz)
        white, blk = split_rect(prect, marker_cells(pid, px, py))
        for q in white:
            add(body, clip(rect_poly(q), pcl), pz, POST_TOP)
        for q in blk:
            p = clip(rect_poly(q), pcl)
            assert abs(area(p) - area(rect_poly(q))) < 1e-9, "a post fillet would cut its marker"
            add(marks, p, pz, POST_TOP)
    vb, vm = check_closed(body), check_closed(marks)
    return body, marks, dict(body_cm3=vb / 1000, markers_cm3=vm / 1000, body_pieces=len(body.shells),
                             marker_pieces=len(marks.shells), height=POST_TOP, layers=round(POST_TOP / LAYER))


def top_view_check(marks, px_per_mm=8):
    """Rasterize the black pieces seen from above and confirm the markers decode to the intended IDs."""
    W, H = int((BX1 + 10) * px_per_mm), int((BY1 + 10) * px_per_mm)
    img = np.full((H, W), 235, np.uint8)
    for poly in marks.polys:
        pts = np.array([[(x + 5) * px_per_mm, H - (y + 5) * px_per_mm] for x, y in poly], np.float32)
        cv2.fillPoly(img, [np.round(pts).astype(np.int32)], 20)
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
    s["filament_colour"] = [BODY_COLOR, BLACK_COLOR]
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
        for M, col in ((body, BODY_COLOR), (marks, "#111111")):
            for poly in M.polys:
                ax.add_patch(plt.Polygon(poly, closed=True, fc=col, ec="none"))
        ax.set_xlim(BX0 - 3, BX1 + 3)
        ax.set_ylim(BY0 - 3, BY1 + 3)
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
    cx, cy = 128.0, 128.0   # board center = plate center
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
    expect = EXPECT_IDS
    if info["decoded_ids"] != expect:
        raise RuntimeError("markers decode as %s, expected %s" % (info["decoded_ids"], expect))
    info["path"] = write_3mf(os.path.join(out_dir, NAME + ".3mf"), body, marks)
    return info


if __name__ == "__main__":
    for k, v in main().items():
        print(k, v)
