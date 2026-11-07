#!/usr/bin/env python3
"""meshmeasure: measure a part from its mesh by ray casts, so picture labels and checks come from the model,
never from build-script inputs (3dp project, 2026-10-09; first used for the 2.5in insert concept).

  from meshmeasure import load_part, first_hit, bisect, outer_r, inner_r, solid_top, lean_deg
  m, H = load_part('part.3mf', flip=True)    # centered in x-y, z from 0; flip turns it over as (x, -y, H - z)

Needs trimesh and numpy; reads 3mf files with dpcheck.load_3mf (same folder).
"""
import math
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dpcheck import load_3mf  # noqa: E402


def load_part(path, item=0, flip=False):
    """Mesh of one object in a 3mf (or any file trimesh reads), centered in x-y with its lowest point at z = 0.
    flip=True turns it over as a rotation, (x, -y, H - z): a part printed upside down, shown as used.
    Returns (trimesh.Trimesh, height)."""
    if path.endswith('.3mf'):
        items, _ = load_3mf(path)
        V, T = np.array(items[item]['V'], float), np.array(items[item]['T'])
    else:
        mm = trimesh.load(path, force='mesh')
        V, T = np.array(mm.vertices, float), np.array(mm.faces)
    lo, hi = V.min(0), V.max(0)
    V = V - [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]]
    H = float(V[:, 2].max())
    if flip:
        V = np.c_[V[:, 0], -V[:, 1], H - V[:, 2]]
    return trimesh.Trimesh(V, T, process=True), H


def first_hit(m, origin, direction):
    """Nearest point where a ray from origin along direction meets the mesh, or None."""
    o = np.asarray(origin, float)
    loc, _, _ = m.ray.intersects_location([o], [np.asarray(direction, float)])
    if len(loc) == 0:
        return None
    return loc[np.argmin(np.linalg.norm(loc - o, axis=1))]


def bisect(f, a, b, n=40):
    """The x between a and b where the yes/no test f(x) changes (f(a) != f(b))."""
    fa = f(a)
    assert fa != f(b), f'no change between {a} and {b}'
    for _ in range(n):
        c = (a + b) / 2
        if f(c) == fa:
            a = c
        else:
            b = c
    return (a + b) / 2


def unit(angle_deg):
    a = math.radians(angle_deg)
    return np.array([math.cos(a), math.sin(a), 0.0])


def outer_r(m, z, angle_deg=22.5, reach=1000.0):
    """Outer surface radius at height z along angle_deg (ray from outside toward the axis)."""
    u = unit(angle_deg)
    p = first_hit(m, u * reach + [0, 0, z], -u)
    return None if p is None else float(math.hypot(p[0], p[1]))


def inner_r(m, z, angle_deg=22.5, start=1.0):
    """Inner surface radius at height z along angle_deg (ray from near the axis outward)."""
    u = unit(angle_deg)
    p = first_hit(m, u * start + [0, 0, z], u)
    return None if p is None else float(math.hypot(p[0], p[1]))


def solid_top(m, x, y, ztop, tol=1e-3):
    """True where a ray from above at (x, y) first meets the mesh at ztop (a flat top face there)."""
    p = first_hit(m, (x, y, ztop + 5.0), (0, 0, -1))
    return p is not None and p[2] > ztop - tol


def lean_deg(m, zs, angle_deg=22.5):
    """Wall angle from vertical, from outer radii at heights zs (positive: radius shrinks as z rises)."""
    rs = [outer_r(m, z, angle_deg) for z in zs]
    return math.degrees(math.atan(-np.polyfit(zs, rs, 1)[0])), rs


def true_runs(f, a, b, n=800):
    """Intervals of [a, b] where the yes/no test f is True, each end refined by bisect (features narrower than
    (b - a) / n can be missed)."""
    xs = np.linspace(a, b, n)
    v = [bool(f(x)) for x in xs]
    out, start = [], (a if v[0] else None)
    for i in range(1, n):
        if v[i] and not v[i - 1]:
            start = bisect(f, xs[i - 1], xs[i])
        elif v[i - 1] and not v[i]:
            out.append((start, bisect(f, xs[i - 1], xs[i])))
            start = None
    if start is not None:
        out.append((start, b))
    return out
