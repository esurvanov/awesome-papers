"""Образцовый кадр 1: ночной Сарань после толчка, час 0 — дроны с прожекторами над кварталами, очаги дыма, горы на фоне звёзд.
blender -b -P papers/ega1-film/blender/still_town.py -- <выход.png> [--draft]"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import world as W

args = sys.argv[sys.argv.index("--") + 1:]
out, is_draft = args[0], "--draft" in args

sc = W.setup(samples=32)
W.terrain()
W.town()
W.forest()
W.fires()
for k, (x, y, yaw) in enumerate(((-30, 20, 0.3), (10, -25, 1.2), (45, 30, 2.0), (-60, -50, 0.8), (70, -10, 2.6), (-15, 70, 1.6))):
    W.drone((x, y, W.height(x, y) + 38 + 4 * k), name=f"drone{k}", yaw=yaw, size=1.6)

W.camera((-150, -300, None), (0, 80, 70), lens=32, dof=None)
if is_draft:
    W.draft(sc)
W.render(out)
