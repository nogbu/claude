"""bore-test-piece_rev2.1_PETG-Basic: bore-test-piece_rev2's geometry unchanged, sliced for Bambu PETG Basic
(preset "Bambu PETG Basic @BBL X1C 0.8 nozzle", the one Orca lists for the P1S 0.6 nozzle; user 2026-10-09).
Needs bore-test-piece_rev2.py and petgBasic_settings_base.json beside it. Run: python3 bore-test-piece_rev2.1_PETG-Basic.py OUTDIR."""
import importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rev2", os.path.join(HERE, "bore-test-piece_rev2.py"))
rev2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(rev2)
W = rev2.W
out = sys.argv[1] if len(sys.argv) > 1 else "."
tm = rev2.build(); name = "bore-test-piece_rev2.1_PETG-Basic"
print("watertight", tm.is_watertight, "volume mm3", round(tm.volume, 1))
s = json.load(open(os.path.join(HERE, "petgBasic_settings_base.json")))
W.write(os.path.join(out, name + ".3mf"), [W.Obj(name, [W.Part(tm.vertices, tm.faces)], at=[(128, 128)])], s)
print("wrote", os.path.join(out, name + ".3mf"))
