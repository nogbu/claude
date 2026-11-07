#!/usr/bin/env python3
"""Lists every effective setting that differs between two Orca 3mfs at one height, for every plate.
Effective = project settings, then the object's settings, then its main part's settings, then the object's own
height ranges covering z. G-code templates and preset names are compared too.

Usage: settingsdiff.py A.3mf B.3mf Z [--plates P:Q ...]
  With no --plates, each plate of A is compared with the same plate of B; when one file has a single plate, every
  plate of the other is compared with it. --plates 1:3 compares A's plate 1 with B's plate 3 (repeatable).

Per-filament lists are compared at the entry the object's filament uses (Orca keeps one or two entries per
filament); differences only in other entries are listed separately. A filament setting left at "nil" falls back to
the printer setting of the same name without "filament_"; those resolved values are compared as "[name] (effective)".
Modifier parts are listed separately ("modifier [name]: [setting]"). Built 2026-10-02, extended 2026-10-09 after
partial checks (first object only, first list entry, G-code skipped, nil unresolved) hid differences.
"""
import json
import re
import sys
import zipfile

SKIP = ('name', 'thumbnails', 'different_settings_to_system', 'upward_compatible_machine')   # object names show in each header
PART_SKIP = ('name', 'matrix', 'source_file', 'source_object_id', 'source_volume_id', 'source_offset_x',
             'source_offset_y', 'source_offset_z')


def _meta(xml):
    return re.findall(r'<metadata key="([^"]+)" value="([^"]*)"', xml)


def load(path):
    """{plate number: [object dicts]} with each object's settings, main-part settings, modifiers and ranges."""
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        proj = json.loads(zf.read('Metadata/project_settings.config'))
        ms = zf.read('Metadata/model_settings.config').decode() if 'Metadata/model_settings.config' in names else ''
        rx = zf.read('Metadata/layer_config_ranges.xml').decode() if 'Metadata/layer_config_ranges.xml' in names else ''
    objs = {}
    for m in re.finditer(r'<object id="(\d+)">(.*?)</object>', ms, re.S):
        body = m.group(2)
        head = body.split('<part')[0]
        o = dict(id=m.group(1), settings=dict(_meta(head)), part={}, modifiers={}, ranges=[])
        for pm in re.finditer(r'<part id="\d+" subtype="([^"]+)">(.*?)</part>', body, re.S):
            kv = dict(_meta(pm.group(2)))
            pname = kv.get('name', '?')
            kv = {k: v for k, v in kv.items() if k not in PART_SKIP}
            if pm.group(1) == 'normal_part':
                o['part'].update(kv)
            else:
                o['modifiers'][pname] = kv
        objs[o['id']] = o
    order = list(objs)   # layer_config_ranges numbers objects 1, 2, ... in model_settings order, not by object id
    for m in re.finditer(r'<object id="(\d+)">(.*?)</object>', rx, re.S):
        k = int(m.group(1)) - 1
        if 0 <= k < len(order):
            for r in re.finditer(r'<range min_z="([\d.]+)" max_z="([\d.]+)">(.*?)</range>', m.group(2), re.S):
                opts = re.findall(r'<option opt_key="([^"]+)">([^<]*)</option>', r.group(3))
                objs[order[k]]['ranges'].append((float(r.group(1)), float(r.group(2)), opts))
    plates = {}
    for m in re.finditer(r'<plate>(.*?)</plate>', ms, re.S):
        pid = re.search(r'key="plater_id" value="(\d+)"', m.group(1))
        ids = re.findall(r'key="object_id" value="(\d+)"', m.group(1))
        plates[int(pid.group(1)) if pid else len(plates) + 1] = [objs[i] for i in ids if i in objs]
    if not plates:
        plates[1] = list(objs.values())
    return proj, plates


def effective(proj, obj, z):
    eff = dict(proj)
    if obj:
        eff.update(obj['settings'])
        eff.update(obj['part'])
        for z0, z1, opts in obj['ranges']:
            if z0 <= z < z1:
                eff.update(opts)
    return eff


def entry(v, n_fil, fil):
    """The list entry filament fil (0-based) uses; non-lists pass through."""
    if not isinstance(v, list):
        return v
    if not v:
        return ''
    per = len(v) // n_fil if n_fil and len(v) % n_fil == 0 else 0
    i = fil * per if per else 0
    return v[i] if i < len(v) else v[0]


def resolved(eff, n_fil, fil):
    """Effective value of each printer setting that a filament setting can override ("nil" = keep the printer's)."""
    out = {}
    for k, v in eff.items():
        if k.startswith('filament_') and k[9:] in eff:
            fv = entry(v, n_fil, fil)
            base = entry(eff[k[9:]], 1, 0)
            out[k[9:] + ' (effective)'] = base if fv in ('nil', '', None) else fv
    return out


def filament_of(eff):
    try:
        return max(int(str(eff.get('extruder', '1')) or '1'), 1) - 1
    except ValueError:
        return 0


def compare(pa, oa, pb, ob, z):
    a, b = effective(pa, oa, z), effective(pb, ob, z)
    fa, fb = filament_of(a), filament_of(b)
    na, nb = len(pa.get('filament_settings_id') or [1]), len(pb.get('filament_settings_id') or [1])
    rows, other = [], []
    for k in sorted(set(a) | set(b)):
        if k in SKIP:
            continue
        va, vb = a.get(k), b.get(k)
        ea, eb = entry(va, na, fa), entry(vb, nb, fb)
        if ea != eb:
            rows.append((k, ea, eb))
        elif va != vb and (isinstance(va, list) or isinstance(vb, list)):
            other.append((k, va, vb))
    ra, rb = resolved(a, na, fa), resolved(b, nb, fb)
    for k in sorted(set(ra) | set(rb)):
        if ra.get(k) != rb.get(k):
            rows.append((k, ra.get(k), rb.get(k)))
    ma, mb = (oa or {}).get('modifiers', {}), (ob or {}).get('modifiers', {})
    for name in sorted(set(ma) | set(mb)):
        da, db = ma.get(name, {}), mb.get(name, {})
        for k in sorted(set(da) | set(db)):
            if da.get(k) != db.get(k):
                rows.append((f'modifier {name}: {k}', da.get(k), db.get(k)))
    return rows, other


def show(v):
    s = repr(v)
    return s if len(s) <= 120 else s[:117] + '...'


def main():
    args = sys.argv[1:]
    pairs = [tuple(int(x) for x in args[i + 1].split(':')) for i, a in enumerate(args) if a == '--plates']
    pos = [a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or args[i - 1] != '--plates')]
    a_path, b_path, z = pos[0], pos[1], float(pos[2])
    pa, plates_a = load(a_path)
    pb, plates_b = load(b_path)
    if not pairs:
        if len(plates_a) == 1:
            pairs = [(next(iter(plates_a)), p) for p in plates_b]
        elif len(plates_b) == 1:
            pairs = [(p, next(iter(plates_b))) for p in plates_a]
        else:
            pairs = [(p, p) for p in plates_a if p in plates_b]
    total = 0
    for p, q in pairs:
        oa_list, ob_list = plates_a.get(p, []), plates_b.get(q, [])
        for i in range(max(len(oa_list), len(ob_list), 1)):
            oa = oa_list[i] if i < len(oa_list) else None
            ob = ob_list[i] if i < len(ob_list) else None
            label = (f"plate {p} '{(oa or {}).get('settings', {}).get('name', '-')}' vs "
                     f"plate {q} '{(ob or {}).get('settings', {}).get('name', '-')}'")
            rows, other = compare(pa, oa, pb, ob, z)
            print(f'== {label}: {len(rows)} differences at z = {z} mm')
            for k, va, vb in rows:
                print(f'{k}: A {show(va)} | B {show(vb)}')
            if other:
                print(f'   differences only in list entries this object does not use ({len(other)}):')
                for k, va, vb in other:
                    print(f'   {k}: A {show(va)} | B {show(vb)}')
            total += len(rows)
    print(f'{total} differences in all (A = {a_path}, B = {b_path})')


if __name__ == '__main__':
    main()
