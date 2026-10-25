"""Plant tag run: my pasted names and species to 3mfs in one command (plantagram rules, Collection thread).

  python3 tags.py list.txt LABEL [outdir] [--past-soil MM]   outdir defaults to /mnt/project-files/3mfs
  --past-soil MM lets rows run up to MM past the 70 mm soil line, which is a suggestion (my words 2026-10-13),
  when I okay it for a tag that doesn't fit.

list.txt holds my list as I pasted it, one plant or tag per line, in my order:
  name / species             one name tag (red-brown) and one species tag (black)
  name<TAB>species           a row of a two-column list: the same
  name                       the same, with its species from collection.md (plantagram, matched ignoring case; 2026-10-11);
                             names not there stop the run (exit 3) and the thread asks me for each species
  name: x  or  species: x    one tag of that kind
  blank: n  or  blank        n blank tags; a file without one gets one blank tag last (2026-10-11)
Text keeps my exact spelling, all lowercase (my words 2026-10-11), and " x " starts row 2 (plantTags_lib.wrap). Installs the builder's libraries (LIBS), then writes tags.txt
(the builder's input) to outdir, then builds plantTags_LABEL with plantTags_lib.make_set (by_kind: name tags on plate 1,
species on plate 2, one blank on plate 3; 8 plants per file, more as .1, .2 ...) and prints one TAG line per tag: file, kind, text and whether it wrapped to a second row.
A tag that doesn't fit two rows stops the run before building: each one is listed (exit 2), and the thread asks me
whether to let it run past the soil line (saying how far), abbreviate it (suggesting an abbreviation) or skip it,
asking each time (my pick 2026-10-13); it never shortens my text itself.
Shape, text size, colors and slicer settings come from plantTags_lib and change only when I ask.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLANTS = '/mnt/project-files/views/collection.md'
LIBS = 'numpy scipy shapely trimesh mapbox_earcut manifold3d matplotlib'


def species_of():
    """{lowercased plant name: species} from collection.md's table."""
    out = {}
    for ln in open(PLANTS, encoding='utf-8'):
        c = [x.strip() for x in ln.strip().strip('|').split('|')]
        if ln.startswith('|') and len(c) >= 3 and c[0] not in ('Name', '') and not c[0].startswith(':'):
            out[c[0].lower()] = c[2]
    return out


def to_tags(path):
    """[(kind, text)] from my pasted list."""
    tags, sp, missing = [], None, []
    for ln in open(path, encoding='utf-8'):
        ln = ln.strip()
        if not ln: continue
        head, sep, rest = ln.partition(':')
        kind = head.strip().lower()
        if sep and kind in ('name', 'species') and rest.strip():
            tags.append((kind, rest.strip().lower()))
        elif (sep and kind == 'blank') or ln.lower() == 'blank':
            tags += [('blank', '')] * (int(rest) if rest.strip() else 1)
        else:
            parts = ln.split('\t') if '\t' in ln else ln.split(' / ') if ' / ' in ln else []
            parts = [p.strip() for p in parts if p.strip()]
            if not parts and not sep:
                sp = sp or species_of()
                if ln.lower() not in sp: missing.append(ln); continue
                parts = [ln, sp[ln.lower()]]
            if len(parts) != 2:
                sys.exit('cannot read line %r: use "name / species", a two-column row, "name: x", "species: x" or "blank: n"' % ln)
            tags += [('name', parts[0].lower()), ('species', parts[1].lower())]
    if missing:
        print('NOT IN collection.md (ask me for each species):\n  ' + '\n  '.join(missing))
        sys.exit(3)
    return tags


def main(src, label, outdir='/mnt/project-files/3mfs', past_soil=0.0):
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q'] + LIBS.split(), check=True)
    sys.path.insert(0, HERE)
    import plantTags_lib as P
    P.SOIL_X += past_soil
    tags = to_tags(src)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, 'tags.txt'), 'w', encoding='utf-8') as f:
        f.writelines('%s: %s\n' % (k, t) if k != 'blank' else 'blank\n' for k, t in tags)
    rows, bad = [], []
    for k, t in tags:
        try: rows.append(P.wrap(t, P.KIND_FIL[k], 7.0) if k != 'blank' else [])
        except ValueError: bad.append('%s: %s' % (k, t))
    if bad:
        print("DOESN'T FIT TWO ROWS (ask me: run past the soil line by how far, abbreviate, with a suggestion, or skip):\n  " + '\n  '.join(bad))
        sys.exit(2)
    for path, chunk in P.make_set('plantTags_' + label, tags, outdir=outdir, by_kind=True, blank_per_file=True):
        for k, t, r in chunk:
            print('TAG %s | %s | %s | %s' % (os.path.basename(path), k, t or '(no text)',
                  'wrapped: "%s" / "%s"' % (r[0][0], r[1][0]) if len(r) > 1 else 'one row' if r else 'blank'))

if __name__ == '__main__':
    a = sys.argv[1:]
    past = 0.0
    if '--past-soil' in a:
        i = a.index('--past-soil'); past = float(a[i + 1]); del a[i:i + 2]
    if len(a) < 2: sys.exit('usage: python3 tags.py list.txt LABEL [outdir]')
    main(*a[:3], past_soil=past)
