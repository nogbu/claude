# Moved to projects/3dp/scripts/render3d.py (the vectorized 3dp concept renderer); kept so older concept scripts still run.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../../scripts"))
from render3d import FACES, newell, render, proj  # noqa: E402,F401
