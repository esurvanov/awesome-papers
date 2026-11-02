"""Сцена A05 в 3D: вышка этажей целиком; верхняя площадка — потолок, на ней 4-3-2-1 (подсвечен); камера поднимается к потолку,
затем к диспетчеру у вышки (журнал — в слое подписей); составы этажа «пробуют манёвры» — дуги к соседним площадкам.
Фразы: 1 потолок · 2 задом наперёд · 3 шесть манёвров · 4 как строит · 5 журнал · 6 все манёвры · 7 новый — выше · 8 повтор — пропуск."""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import film as F
import station as S

args = sys.argv[sys.argv.index("--") + 1:]
out, draft, still = args[0], "--draft" in args, next((a.split("=")[1] for a in args if a.startswith("--still=")), None)
P, L = F.phrases("A05")

S.setup(samples=24)
S.ground()
T = S.yard()
S.scenery()
S.nature()
by = S.bfs_floors(4, S.neighbours(4))
TW = (40.0, 26.0, 0.6)
tw = S.floors_tower(by, TW, step=2.4, width=30.0)
top = max(by)
# потолок: состав 4-3-2-1 крупнее и розовый
for o in tw[top][2]:
    o.hide_render = True
S.mini_train(by[top][0], (TW[0], TW[1] - 0.2, TW[2] + top * 2.4 + 0.06), car=1.5, highlight=(0.97, 0.47, 0.73))
glow = S.pbr("top_glow", color=(0.97, 0.47, 0.73), rough=0.3)
glow.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (0.97, 0.47, 0.73, 1)
glow.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.5
tw[top][1].data.materials[0] = glow
disp = S.person((30.0, 21.0, 0.0), rot_z=math.radians(150))  # диспетчер у вышки этажей


def arc(a, b, color, t, h=1.6):
    """Дуга-манёвр от состава к составу (появляется к t)."""
    curve = bpy.data.curves.new("arc", "CURVE")
    curve.dimensions, curve.bevel_depth = "3D", 0.05
    sp = curve.splines.new("BEZIER")
    sp.bezier_points.add(1)
    for k, p in enumerate((a, b)):
        sp.bezier_points[k].co = p
        sp.bezier_points[k].handle_left_type = sp.bezier_points[k].handle_right_type = "AUTO"
    o = bpy.data.objects.new("arc", curve)
    bpy.context.scene.collection.objects.link(o)
    m = S.pbr(f"arc_{color}", color=color, rough=0.4)
    m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (*color, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0
    o.data.materials.append(m)
    curve.bevel_factor_end = 0.0
    curve.keyframe_insert("bevel_factor_end", frame=F.frame(t))
    curve.bevel_factor_end = 1.0
    curve.keyframe_insert("bevel_factor_end", frame=F.frame(t + 0.8))
    return o


def train_pos(f, k):
    span = 30.0 / len(by[f])
    return (TW[0] - 15 + span * (k + 0.5), TW[1] - 0.4, TW[2] + f * 2.4 + 0.6)


# фраза 6: от состава первого этажа — все манёвры (к этажам 0 и 2); фраза 7: новый — на этаж выше
src = train_pos(1, 1)
for f, k in ((0, 0), (2, 1), (2, 2)):
    arc(src, train_pos(f, k), (1, 1, 1), P[5] + 0.3 * k)
arc(train_pos(2, 1), train_pos(3, 2), (0.24, 0.73, 0.31), P[6])
arc(train_pos(3, 2), train_pos(2, 1), (0.97, 0.32, 0.29), P[7])  # обратно вниз — уже записан, пропуск

cam = S.camera((10, -30, 14), (40, 26, 8), lens=30, dof=16)
F.cam_at(cam, 0.0, (12, -26, 18), (40, 26, 13), lens=30)           # 1: потолок
F.cam_at(cam, P[1], (32, 6, 16.5), (40, 26, 15.0), lens=45)         # 2: 4-3-2-1 крупно
F.cam_at(cam, P[2] + 3.0, (30, 4, 15.5), (40, 26, 14.6), lens=45)   # 3: шесть манёвров (счётчик — в подписях)
F.cam_at(cam, P[3], (16, 2, 3.0), (30, 21, 1.6), lens=40)           # 4: диспетчер
F.cam_at(cam, P[4], (18, 0, 4.0), (32, 22, 2.0), lens=38)           # 5: журнал
F.cam_at(cam, P[5], (24, -4, 6.5), (40, 26, 3.5), lens=34)          # 6–8: манёвры между этажами
F.cam_at(cam, P[7], (26, -2, 8.5), (40, 26, 5.5), lens=34)
F.cam_at(cam, L, (20, -12, 12), (40, 26, 7.0), lens=30)

if still:
    bpy.context.scene.frame_set(F.frame(float(still)))
    bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = 1920, 1080
    S.render(out)
else:
    F.finish(out, L, draft)
print(f"СЦЕНА A05 готова: {out}")
