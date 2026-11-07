"""mossPlank snap-tab sizing (inference, beam formulas). Loads: 2.5 kg lifted pot x factor 3 on two tabs (pull-out);
1 kg sideways at the upper section's top x 3 (spigot bending). PETG HF: E 2,050 MPa, bending 48 MPa across layers."""
import math
E, allow = 2050.0, 48.0 / 3
t, gap, wall = 1.24, 0.2, 1.24
delta = wall + gap                       # hook protrusion: flush with the upper section's outer face
for L in (15, 20, 25):
    eps = 1.5 * t * delta / L**2; sig = E * eps
    print("arm %d mm: snap strain %.2f%%, stress %.1f MPa (allow %.1f)" % (L, 100 * eps, sig, allow))
F = 2.5 * 9.81 * 3 / 2                   # per tab
b = 8.0
print("pull per tab %.1f N; arm tension %.1f MPa" % (F, F / (b * t)))
h = 3.0                                  # hook height at its root (z)
M = F * delta / 2; S = b * h**2 / 6
print("hook root bending %.1f MPa; shear %.1f MPa" % (M / S, F / (b * h)))
Mj = 9.81 * 3 * (200 - 30 + 30 / 2)      # load at the upper top, lever to the middle of a 30 mm overlap (inference)
print("joint moment %.0f N.mm; spigot stress %.1f MPa (S 1552 mm3)" % (Mj, Mj / 1552))
