"""plantTags_rev1.4_nicetySet: three tags on one plate (my words, 2026-10-11): a blank tag, a name tag "nicety" (red-brown)
and a species tag "doc block michelle" (black), 7 mm text. "doc block michelle" is 61.4 mm on one row, 2.1 mm into the
70 mm soil line, so it wraps to two rows, "doc block" over "  michelle" (Product rule indent). Line width 0.35 mm, the knee for
every row (best_lw: 0.37 loses 1.9% to 2.6% more on "nicety" and "michelle"); first layer 0.35 plate-wide.
Run: python3 plantTags_rev1.4_nicetySet.py [outdir]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plantTags_lib as P
if __name__ == '__main__':
    P.build_set('plantTags_rev1.4_nicetySet',
                [('blank', []), ('nicety', [('nicety', 2)]), ('doc block michelle', [('doc block', 3), ('michelle', 3)])],
                em=7.0, lw='0.35', outdir=sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/3mfs')
