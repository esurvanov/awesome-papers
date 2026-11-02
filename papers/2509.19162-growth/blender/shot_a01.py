"""Сцена A01 в 3D. Станция: главный путь, четыре параллельных с горловинами-лестницами, съезд у состава, депо, вышка, фонари.
Состав 3-1-5-2-4 на главном пути; диспетчер у стрелочного рычага съезда. Манёвр «поменять соседей 2 и 4» — только по рельсам:
4 уходит вперёд по главному → 2 через съезд на путь 1 → 4 откатывается на место 2 → 2 через съезд возвращается на место 4.
Перед рендером — проверка, что вагоны не сталкиваются (station.collisions). Ключи — по началам фраз (film.phrases)."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import film as F
import station as S

args = sys.argv[sys.argv.index("--") + 1:]
out, draft, still = args[0], "--draft" in args, next((a.split("=")[1] for a in args if a.startswith("--still=")), None)
P, L = F.phrases("A01")
SP = S.TRACK_SPACING

S.setup(samples=24)
S.ground()
T = S.yard()
S.scenery()
S.nature()

wag = {}
for num, kind, x in [(3, "серый", -30), (1, "рок", -15), (5, "синий", 0), (2, "серый", 15), (4, "рок", 30)]:
    w = S.place(S.model(S.WAGONS[kind], 14.0, name=f"wagon{num}"), x)
    for m in S.number_plate(w, num):
        m.parent = w
        m.matrix_parent_inverse = w.matrix_world.inverted()
    wag[num] = w
others = []
for k, (kind, tr, x) in enumerate([("цистерна", 2, -60), ("хром", 2, -44), ("цистерна", 2, -28), ("платформа", 3, -10), ("рок", 3, 6),
                                     ("серый", 4, -40), ("синий", 4, -25), ("хром", 4, 20), ("цистерна", 4, 36)]):
    others.append(S.place(S.model(S.WAGONS[kind], 15.0 if kind in ("цистерна", "хром", "платформа") else 14.0, name=f"bg{k}"), x, -tr * SP))
loco = S.place(S.model(S.LOCO, 20.0, name="loco"), 120, -SP)
others.append(loco)
lever = S.place(S.model(S.LEVER, 1.6, name="lever"), 44.0, 2.7)
lever.location.z = 0.0
paint = S.pbr("lever_paint", color=(0.08, 0.09, 0.1), rough=0.45, metal=0.6)
for o in lever.children_recursive:
    if o.type == "MESH":
        o.data.materials.clear()
        o.data.materials.append(paint)
disp = S.person((46.2, 3.4, 0.0), rot_z=math.radians(200))
cam = S.camera((-90, -90, 60), (0, 5, 0), lens=30, dof=11)

# камера по фразам
F.cam_at(cam, 0.0, (-150, -120, 75), (0, -6, 0), lens=26)            # 1: станция сверху — горловины и пути
F.cam_at(cam, P[1] - 0.2, (-80, -60, 32), (-5, -2, 0), lens=30)
F.cam_at(cam, P[1] + 3.0, (-34, -24, 5.5), (0, 0, 2.4), lens=32)      # 2: состав сбоку
F.cam_at(cam, P[2], (40, -10, 2.4), (46.2, 3.4, 1.4), lens=40)        # 3: диспетчер у рычага
F.cam_at(cam, P[3] - 0.5, (38, -12, 3.0), (46.0, 3.0, 1.2), lens=40)
F.cam_at(cam, P[3] + 1.5, (20, -40, 18), (40, -2, 0), lens=30)        # 4: манёвры: главный путь и съезд
F.cam_at(cam, P[4], (52, -62, 30), (62, -3, 0), lens=28)              # 5–7: манёвр сверху — в кадре весь путь вагонов, x 15…95
F.cam_at(cam, P[6] + 1.5, (48, -66, 32), (58, -3, 0), lens=28)
F.cam_at(cam, P[7], (-60, -130, 70), (20, -8, 0), lens=26)            # 8: вся станция
F.cam_at(cam, P[8], (48, -22, 12), (70, 16, 9), lens=34)              # 9: вышка
F.cam_at(cam, L, (56, -8, 9), (70, 16, 9.5), lens=40)

# манёвр — только по путям
t = P[4] + 0.3
S.drive(wag[4], S.path((30, 0), (95, 0)), t, t + 2.8)
S.drive(wag[2], S.path((15, 0), (45, 0), (45 + 4 * SP, -SP), (92, -SP)), t + 2.8, t + 6.6)
S.drive(wag[4], S.path((95, 0), (15, 0)), t + 6.6, t + 9.6)
S.drive(wag[2], S.path((92, -SP), (45 + 4 * SP, -SP), (45, 0), (30, 0)), t + 9.6, t + 13.4)

bad = S.collisions(list(wag.values()) + others, L)
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
print(f"СЦЕНА A01 готова: {out}")
