"""Образцовый кадр 2: дрон крупно над крышами — прожектор в пыли, ходовые огни, вдали другие дроны.
blender -b -P papers/ega1-film/blender/still_drone.py -- <выход.png> [--draft]"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import world as W

args = sys.argv[sys.argv.index("--") + 1:]
out, is_draft = args[0], "--draft" in args

sc = W.setup(samples=32, haze=0.004)
W.terrain()
W.town()
W.forest(n=300)
W.fires(n=2)
z0 = W.height(0, 0)
hero = W.drone((0, 0, z0 + 22), name="hero", yaw=0.4, size=1.6)
hero.rotation_euler = (math.radians(6), math.radians(-4), 0.4)  # наклон вперёд: летит
for k, (x, y) in enumerate(((40, 60), (-70, 30), (20, -80))):
    W.drone((x, y, W.height(x, y) + 30 + 5 * k), name=f"drone{k}", yaw=k, size=1.6)

W.camera((6, -9, z0 + 23.5), (0, 0, z0 + 21.5), lens=50, dof=2.8)
if is_draft:
    W.draft(sc)
W.render(out)
