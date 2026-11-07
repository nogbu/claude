"""slotGuide_rev1 build script (unicoly-rail). US Letter slot scale. Run: python3 slotGuide_rev1.py -> out/slotGuide_rev1.pdf"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
W, H = 215.9, 279.4
fig = plt.figure(figsize=(W/25.4, H/25.4))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal"); ax.axis("off")
R = "#D62728"
def rect(x, y, w, h, fc, ec="none", lw=0):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=lw, antialiased=False))
def t(x, y, s, size=9, **k):
    ax.text(x, y, s, fontsize=size, family="DejaVu Sans", **k)

t(15, 262, "slotGuide rev1  ·  UNICOLY slot scale", 14, weight="bold")
lines = [
 "1. Print at 100% / \"Actual size\" (no \"Fit to page\").",
 "2. Measure both 100 mm check bars with calipers or a ruler; send me both readings.",
 "3. Cut out one strip on its outline: the widest one that lies flat beside the slots",
 "    without covering any slot.",
 "4. Tape it flat on the slotted strip, beside a whole slot group, taping only the ends.",
 "5. Photograph straight on from about 15 cm, with the whole group and strip in frame.",
]
for i, s in enumerate(lines):
    t(15, 250 - 6.2*i, s, 9.5)

# check bars
y0 = 200
rect(15, y0, 100, 1.5, "black")
for xx in (15, 115):
    rect(xx - 0.15, y0 - 3, 0.3, 7.5, "black")
t(15, y0 + 6, "Check bar A (across): should measure 100.0 mm", 8.5)
x0 = 196
rect(x0, 40, 1.5, 100, "black")
for yy in (40, 140):
    rect(x0 - 3, yy - 0.15, 7.5, 0.3, "black")
t(x0 - 4, 90, "Check bar B (down): should measure 100.0 mm", 8.5, rotation=90, va="center", ha="center")

# strips
widths = [3.0, 3.0, 3.5, 3.5, 4.0, 4.0]
xs = 20
ys = 45
for i, w in enumerate(widths):
    x = xs + i * 22
    for k in range(120):
        c = R if k % 10 == 0 else ("black" if k % 2 == 0 else "white")
        rect(x, ys + k, w, 1.0, c)
    ax.add_patch(Rectangle((x, ys), w, 120, facecolor="none", edgecolor="#9a9a9a", linewidth=0.3))
    t(x + w/2, ys - 5, f"{w:.1f} mm", 8, ha="center")
t(20, 172, "Scale strips: 1 mm bands, every 10th band red. Cut on the gray outline.", 8.5)
t(15, 22, "Bands and bars are drawn at exact size. Printer scaling is corrected with the check-bar readings.", 7.5, color="#555555")
os.makedirs("out", exist_ok=True)
fig.savefig("out/slotGuide_rev1.pdf")
fig.savefig("slotGuide_rev1_preview.png", dpi=110)
