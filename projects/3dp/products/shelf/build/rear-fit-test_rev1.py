"""rear-fit-test_rev1 (shelf state.md agreed change 38): three cut-down left rear pieces, rod ends to the sleeve tip,
lip bore 31.8 / 32.3 / 32.8 below the rear corner bore, marked by 1, 2, 3 grooves on the glass-end face. Sharp (dp exception,
user 2026-10-10). Each prints on its side, front face on the bed (agreed change 30). Bambu PETG Basic (agreed change 12).
Needs rear-fittest_options.py, rear-piece_model.py, front-piece_model.py and petgBasic_settings_base.json beside it.
Run: python3 rear-fit-test_rev1.py OUTDIR [plates]  (plates: 1 = all three on one plate, 3 = one piece per plate)."""
import importlib.util, json, os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../scripts"))
import write3mf as W
spec = importlib.util.spec_from_file_location("opts", os.path.join(HERE, "rear-fittest_options.py"))
O = importlib.util.module_from_spec(spec); spec.loader.exec_module(O)
STEPS = [(31.8, 1), (32.3, 2), (32.8, 3)]

def printed(spacing, marks):
    """Mesh in print orientation: model -y face (front) on the bed, so print z = model y - yf; print y = -model z."""
    p, d = O.piece(spacing, True, marks); t = O.RP.tm(p)
    v = t.vertices; V = np.c_[v[:, 0], -v[:, 2], v[:, 1] - d["yf"]]
    return V, np.asarray(t.faces)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."; plates = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    s = json.load(open(os.path.join(HERE, "petgBasic_settings_base.json")))
    objs = []
    for i, (sp, mk) in enumerate(STEPS):
        V, T = printed(sp, mk)
        objs.append(W.Obj(f"rear-fit-test_{sp:.1f}_{mk}groove", [W.Part(V, T)], at=[(78 + 50 * i, 128)]))
    name = "rear-fit-test_rev1"
    if plates == 1:
        W.write(os.path.join(out, name + ".3mf"), objs, s); print("wrote", name + ".3mf")
    else:
        for i, o in enumerate(objs):
            o.at = [(128, 128)]; n = f"{name}.{i + 1}"
            W.write(os.path.join(out, n + ".3mf"), [o], s); print("wrote", n + ".3mf")
