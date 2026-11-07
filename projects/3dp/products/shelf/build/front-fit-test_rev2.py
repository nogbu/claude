"""front-fit-test_rev2 (shelf state.md agreed changes 39, 40): rev1 with one change, the open corner along the sleeve (agreed
change 40: rev1's roof strip between the channel and the bore started over air and printed as strings). Three cut-down left
front pieces, rod end to the sleeve tip,
gap over the crosswire band 0.2 / 0.3 / 0.4, marked by 1, 2, 3 grooves on the glass-end face. Sharp (dp exception,
user 2026-10-10). Each prints on its side, front face on the bed (agreed change 14). Bambu PETG Basic (agreed change 12).
Needs front-fittest_options.py (piece(..., open_corner=True)), front-piece_model.py and petgBasic_settings_base.json beside it.
Run: python3 front-fit-test_rev2.py OUTDIR [plates]  (plates: 1 = all three on one plate, 3 = one piece per plate)."""
import importlib.util, json, os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import write3mf as W
spec = importlib.util.spec_from_file_location("opts", os.path.join(HERE, "front-fittest_options.py"))
O = importlib.util.module_from_spec(spec); spec.loader.exec_module(O)
STEPS = [(0.2, 1), (0.3, 2), (0.4, 3)]

def printed(gap, marks):
    """Mesh in print orientation: model -y face (front) on the bed, so print z = model y - yf; print y = -model z."""
    p, d = O.piece(gap, True, marks, open_corner=True); t = O.F.tm(p)
    v = t.vertices; V = np.c_[v[:, 0], -v[:, 2], v[:, 1] + d["OF"]]
    return V, np.asarray(t.faces)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."; plates = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    s = json.load(open(os.path.join(HERE, "petgBasic_settings_base.json")))
    objs = []
    for i, (sp, mk) in enumerate(STEPS):
        V, T = printed(sp, mk)
        objs.append(W.Obj(f"front-fit-test_{sp:.1f}_{mk}groove", [W.Part(V, T)], at=[(78 + 50 * i, 128)]))
    name = "front-fit-test_rev2"
    if plates == 1:
        W.write(os.path.join(out, name + ".3mf"), objs, s); print("wrote", name + ".3mf")
    else:
        for i, o in enumerate(objs):
            o.at = [(128, 128)]; n = f"{name}.{i + 1}"
            W.write(os.path.join(out, n + ".3mf"), [o], s); print("wrote", n + ".3mf")
