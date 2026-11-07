"""plantTags_rev1.3_aceOfSpades: one tag, two rows at 7 mm: "ace of spades" (red-brown) over "x dark phoenix" (black),
the second row indented 2 spaces (my words, 2026-10-10). Line width 0.35 mm, the widest before two-bead coverage drops
for these words: under two beads 1.4% / 2.5% at 0.35, 3.4% / 3.7% at 0.37, 7.3% / 5.8% at 0.40 (font measurement).
Run: python3 plantTags_rev1.3_aceOfSpades.py [outdir]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plantTags_lib as P
if __name__ == '__main__':
    P.build('plantTags_rev1.3_aceOfSpades', [('ace of spades', 2), ('x dark phoenix', 3)], em=7.0, lw='0.35', indent=[0, 2],
            outdir=sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/3mfs')
