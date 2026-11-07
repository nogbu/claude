"""Roof sizing for the front piece's raised roof (inference throughout; PETG Basic data sheet V3.0 strengths, 75 along / 56 across).
Moments about the bore's deep-end floor contact (x 0): clip load at the clip center, roof contacts at the two crosswires,
shared in proportion to x (rigid rotation, equal contact stiffness)."""
import numpy as np
F = 15 * 4.448 * 3                  # 15 lb per corner x safety factor 3 (agreed change 11), N
SIDE_TO_ROD_END = (690 - 597) / 2   # 46.5 (Key data, inference)
CLIP = 8.0                          # clip center from the side edge (0.5-15.5 patch)
d1 = SIDE_TO_ROD_END - CLIP
X = np.array([12.0, 12.0 + 25.3])
M = F * d1; k = M / (X ** 2).sum(); P = k * X
print(f"F {F:.0f} N, arm {d1:.1f} mm, moment {M/1000:.2f} N*m; roof loads at wires {P.round(0)} N; floor {F + P.sum():.0f} N")
WIRE_END = -2.95                    # wire end flush with the rod's front face
for r_f, overlap in ((0.3, 2.0), (0.6, 2.0), (0.6, 3.0)):
    root = WIRE_END - r_f           # front wall's rear face
    tip = WIRE_END + overlap
    for arm_name, arm in (("centroid", (tip + WIRE_END) / 2 - root), ("tip", tip - root)):
        Mr = P.max() * arm
        for b in (8.0,):
            for s, name in ((75, "along"), (56, "across")):
                t = np.sqrt(6 * Mr / (b * s))
                print(f"gap {r_f} overlap {overlap} {arm_name:8s} arm {arm:.2f} M {Mr:.0f} N*mm b {b}: t {t:.2f} mm ({name} layers)")
