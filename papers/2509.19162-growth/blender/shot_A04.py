"""Сцена A04 в 3D: та же станция; маленький состав 1-2-3-4 на главном пути; манёвр «поменять соседей 3 и 4» через съезд;
рядом поднимается вышка этажей — стеклянные площадки, на каждой миниатюрные составы своего этажа (все 24, перебор).
Фразы: 1 станция · 2 манёвр · 3 вышка · 4 этаж = манёвров до порядка · 5 низ — порядок · 6 первый этаж — три состава · 7 все этажи."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import film as F
import station as S

args = sys.argv[sys.argv.index("--") + 1:]
out, draft, still = args[0], "--draft" in args, next((a.split("=")[1] for a in args if a.startswith("--still=")), None)
P, L = F.phrases("A04")
SP = S.TRACK_SPACING

S.setup(samples=24)
S.ground()
T = S.yard()
S.scenery()
S.nature()

wag = {}
for num, kind, x in [(1, "серый", -22.5), (2, "рок", -7.5), (3, "синий", 7.5), (4, "серый", 22.5)]:
    w = S.place(S.model(S.WAGONS[kind], 14.0, name=f"wagon{num}"), x)
    for m in S.number_plate(w, num):
        m.parent = w
        m.matrix_parent_inverse = w.matrix_world.inverted()
    wag[num] = w
disp = S.person((46.2, 3.4, 0.0), rot_z=math.radians(200))

by = S.bfs_floors(4, S.neighbours(4))
TW = (40.0, 26.0, 0.6)
tw = S.floors_tower(by, TW, step=2.4, width=30.0)
# площадки поднимаются по одной к фразе 3, составы — к фразам 5–7
for f, (pl, rim, objs, num) in tw.items():
    S.appear([pl, rim, num], P[2] + 0.25 * f, 0.5)
S.appear(tw[0][2], P[4], 0.5)
S.appear(tw[1][2], P[5], 0.6)
# пример фразы 4: один состав второго этажа виден заранее (остальные его соседи — к фразе 7)
ex = by[2].index((1, 0, 3, 2))
ex_objs = tw[2][2][ex * 8:(ex + 1) * 8]
S.appear(ex_objs, P[3], 0.4)
for f in range(2, max(by) + 1):
    S.appear([o for o in tw[f][2] if o not in ex_objs], P[6] + 0.5 * (f - 2), 0.5)

cam = S.camera((-40, -45, 18), (10, 5, 2), lens=30, dof=14)
F.cam_at(cam, 0.0, (-45, -48, 20), (5, 2, 2), lens=30)            # 1: маленькая станция
F.cam_at(cam, P[1], (10, -55, 26), (40, -2, 0), lens=28)           # 2: манёвр через съезд
F.cam_at(cam, P[2] + 0.5, (10, -40, 16), (40, 26, 6), lens=30)     # 3: вышка поднимается
F.cam_at(cam, P[3], (25, -6, 7.5), (40, 26, 4.5), lens=40)          # 4: этаж 2 — пример
F.cam_at(cam, P[4], (22, 4, 3.5), (40, 26, 1.0), lens=40)           # 5: низ — порядок
F.cam_at(cam, P[5], (24, 4, 5.5), (40, 26, 3.0), lens=40)           # 6: первый этаж
F.cam_at(cam, P[6], (8, -22, 14), (40, 26, 7.0), lens=30)           # 7: все этажи
F.cam_at(cam, L, (0, -14, 20), (40, 26, 7.5), lens=28)

t = P[1] + 0.2  # манёвр: поменять соседей 3 и 4
S.drive(wag[4], S.path((22.5, 0), (95, 0)), t, t + 1.8)
S.drive(wag[3], S.path((7.5, 0), (45, 0), (45 + 4 * SP, -SP), (92, -SP)), t + 1.8, t + 3.7)
S.drive(wag[4], S.path((95, 0), (7.5, 0)), t + 3.7, t + 5.3)
S.drive(wag[3], S.path((92, -SP), (45 + 4 * SP, -SP), (45, 0), (22.5, 0)), t + 5.3, t + 7.1)

bad = S.collisions(list(wag.values()), L)
if bad:
    print("СТОЛКНОВЕНИЯ:\n  " + "\n  ".join(bad[:20]))
    raise SystemExit(1)
if still:
    import bpy
    bpy.context.scene.frame_set(F.frame(float(still)))
    bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = 1920, 1080
    S.render(out)
else:
    F.finish(out, L, draft)
print(f"СЦЕНА A04 готова: {out}")
