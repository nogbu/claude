import sys; sys.path.insert(0, '/home/user/claude/projects/3dp/scripts')
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import render3d as R, manifold3d as mf, trimesh
from model import body, name, species, tm2mf, mf2tm, TH, DEPTH
CLEAR = np.array([0.80, 0.87, 0.90]); BLACK = np.array([0.16, 0.16, 0.17]); RED = np.array([0x9F, 0x33, 0x2A]) / 255
SRC = '/mnt/project-files/uploads/hearth/2d275a95-3333-41da-b5db-5e6d8ff8cf77'
def put(parts):
    R.FACES.clear()
    for m, c in parts: R.mesh(m, c)
def crop(box):
    a, b = np.array(box[0], float), np.array(box[1], float); B = mf.Manifold.cube(b - a).translate(a)
    return [(mf2tm(tm2mf(m) ^ B), c) for m, c in ((body, CLEAR), (name, RED), (species, BLACK))]
ALL = [(body, CLEAR), (name, RED), (species, BLACK)]
def main():
    fig = plt.figure(figsize=(16, 15))
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.5])
    ax = fig.add_subplot(gs[0, :]); put(ALL)
    cam = R.view(ax, eye=(0, -0.25, 1), pad=4, edge_depth=0.3, title='Bed face (text side), seen from above with the tag turned over')
    R.dim(ax, cam, (-66.697, -10, TH), (66.697, -10, TH), (0, -5, 0))
    R.dim(ax, cam, (66.697 - 14, 10, TH), (66.697, 10, TH), (0, 4, 0))
    R.dim(ax, cam, (-66.697, -10, TH), (-66.697, 10, TH), (-4, 0, 0))
    R.source(ax, SRC, cam)
    ax = fig.add_subplot(gs[1, :]); put(ALL)
    cam = R.view(ax, eye=(0, 0.25, -1), pad=4, edge_depth=0.3, title='Top face as printed (clear body; text shows through in the print, not drawn here)')
    ax = fig.add_subplot(gs[2, 0]); put(crop(((-70, -11, -1), (-28, 11, 2))))
    cam = R.view(ax, eye=(-0.35, -0.6, 1), pad=1.5, edge_depth=0.15, title='Close-up: text end, 9 mm rows')
    R.dim(ax, cam, (-29, -10, TH), (-29, 10, TH), (3, 0, 0))
    ax = fig.add_subplot(gs[2, 1]); put(crop(((-58.9, -11, -1), (-50, 11, 2))))
    cam = R.view(ax, eye=(1, -0.55, 0.45), pad=0.8, edge_depth=0.05, title='Cut at x = -50 through "m" and "e": inlay flush, 0.54 deep')
    R.dim(ax, cam, (-50, -10, 0), (-50, -10, TH), (0, -1.5, 0))
    z = np.array; R.dim(ax, cam, (-50, 10, TH - DEPTH), (-50, 10, TH), (0, 1.5, 0))
    fig.suptitle('plantTags with agreed changes 1-2 (inlaid flush text, two 9 mm rows); not built', fontsize=17, fontweight='bold')
    fig.tight_layout()
    R.save(fig, '/mnt/project-files/images/plantTags_agreed12.png')
if __name__ == "__main__":
    main()
