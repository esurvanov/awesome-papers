"""Сцена A06 в 3D: длинный состав — тепловоз и 15 вагонов с номерами 1–15 — медленно идёт по главному пути; камера провожает его,
затем поднимается над всей станцией. Числа (триллион, 40 000 лет, секундомеры) — в слое подписей."""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import film as F
import station as S

args = sys.argv[sys.argv.index("--") + 1:]
out, draft, still = args[0], "--draft" in args, next((a.split("=")[1] for a in args if a.startswith("--still=")), None)
P, L = F.phrases("A06")

S.setup(samples=24)
S.ground()
S.yard()
S.scenery()
S.nature()
kinds = ["серый", "рок", "синий", "цистерна", "хром", "платформа"]
cars = []
x0 = -120.0
loco = S.place(S.model(S.LOCO, 20.0, name="loco"), x0 + 18.0)
cars.append(loco)
for k in range(15):
    kind = kinds[k % len(kinds)]
    w = S.place(S.model(S.WAGONS[kind], 15.0 if kind in ("цистерна", "хром", "платформа") else 14.0, name=f"car{k + 1}"), x0 - k * 15.5)
    for m in S.number_plate(w, k + 1):
        m.parent = w
        m.matrix_parent_inverse = w.matrix_world.inverted()
    cars.append(w)
# весь состав едет вперёд на 120 м за сцену
for c in cars:
    x = c.location.x
    S.drive(c, S.path((x, 0), (x + 120, 0)), 0.3, L)
cam = S.camera((-80, -30, 6), (-100, 0, 2), lens=32, dof=20)
F.cam_at(cam, 0.0, (-150, -26, 5.0), (-140, 0, 2.5), lens=32)
F.cam_at(cam, P[1], (-120, -40, 9.0), (-90, 0, 2.5), lens=26)     # 2: весь длинный состав
F.cam_at(cam, P[2], (-60, -70, 30), (-40, 0, 2.0), lens=26)
F.cam_at(cam, P[4], (-20, -120, 60), (0, -6, 0), lens=26)          # 5: станция сверху
F.cam_at(cam, L, (0, -130, 70), (10, -6, 0), lens=26)
bad = S.collisions(cars, L)
if bad:
    print("СТОЛКНОВЕНИЯ:\n  " + "\n  ".join(bad[:20]))
    raise SystemExit(1)
if still:
    bpy.context.scene.frame_set(F.frame(float(still)))
    bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = 1920, 1080
    S.render(out)
else:
    F.finish(out, L, draft)
print(f"СЦЕНА A06 готова: {out}")
