"""Образцовый кадр 3: штаб в спортзале, час 0 — столы с ноутбуками, фонари, большой экран со столбцами чисел (картинки нет).
blender -b -P papers/ega1-film/blender/still_hq.py -- <выход.png> [--draft]"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import world as W

args = sys.argv[sys.argv.index("--") + 1:]
out, is_draft = args[0], "--draft" in args
rnd = random.Random(2)

sc = W.setup(samples=48, sky_strength=0.0, moon=0.0, haze=0.0, exposure=-0.5)
L, D, H = 36.0, 20.0, 8.0   # спортзал: длина, ширина, высота
W.haze_box(0.004, size=(L, D, H), loc=(0, 0, H / 2))

wood = W.pbr("floor", "wood", rough=0.5, scale=0.4, box=True)
brick = W.pbr("walls", "brick", rough=0.9, scale=0.35, box=True)
dark = W.pbr("dark", color=(0.05, 0.05, 0.055), rough=0.8)
W.box("floor", (L, D, 0.2), (0, 0, -0.1), wood)
W.box("ceiling", (L, D, 0.2), (0, 0, H + 0.1), dark)
W.box("wall_n", (L, 0.3, H), (0, D / 2 + 0.15, H / 2), brick)
W.box("wall_s", (L, 0.3, H), (0, -D / 2 - 0.15, H / 2), brick)
W.box("wall_e", (0.3, D, H), (L / 2 + 0.15, 0, H / 2), brick)
W.box("wall_w", (0.3, D, H), (-L / 2 - 0.15, 0, H / 2), brick)
# разметка площадки на полу
line = W.pbr("line", color=(0.9, 0.9, 0.85), rough=0.5)
W.box("line_mid", (0.1, D - 2, 0.01), (0, 0, 0.005), line)
W.box("line_side", (L - 4, 0.1, 0.01), (0, D / 2 - 1.5, 0.005), line)

# большой экран на северной стене: столбцы чисел с 40 дронов
screen = W.box("screen", (12, 0.2, 5.5), (-4, D / 2 - 0.2, 4.2), W.pbr("screen_bg", color=(0.01, 0.015, 0.02), emit=((0.02, 0.05, 0.08), 1.5)))
cols = ["t°C", "CO₂", "h м", "дБ", "сигн"]
txt = "\n".join("   ".join(f"{rnd.uniform(-3, 41):5.1f}" for _ in range(9)) for _ in range(14))
bpy.ops.object.text_add(location=(-9.6, D / 2 - 0.32, 6.3), rotation=(math.pi / 2, 0, 0))
t = bpy.context.object
t.data.body, t.data.font, t.data.size = txt, W.font(), 0.36
t.data.space_line = 1.15
t.data.materials.append(W.pbr("screen_text", color=(0, 0, 0), emit=((0.55, 0.95, 0.75), 6)))
bpy.ops.object.text_add(location=(-9.6, D / 2 - 0.32, 6.75), rotation=(math.pi / 2, 0, 0))
h = bpy.context.object
h.data.body, h.data.font, h.data.size = "дрон 01    02    03    04    05    06    07    08    09", W.font(), 0.3
h.data.materials.append(W.pbr("screen_head", color=(0, 0, 0), emit=((1.0, 0.8, 0.4), 6)))

# столы штаба: школьные парты в два ряда, на них ноутбуки, планшеты, фонари
desk, chair, laptop, lantern, clip = W.ph("SchoolDesk_01"), W.ph("SchoolChair_01"), W.ph("classic_laptop"), W.ph("Lantern_01"), W.ph("clipboard")
for i in range(5):
    for row, y in ((0, 2.0), (1, -1.5)):
        x = -11 + i * 3.2 + rnd.uniform(-0.2, 0.2)
        W.instance(desk, (x, y, 0), rot_z=rnd.uniform(-0.1, 0.1))
        W.instance(chair, (x, y - 0.8, 0), rot_z=math.pi + rnd.uniform(-0.4, 0.4))
        if rnd.random() < 0.8:
            W.instance(laptop, (x + rnd.uniform(-0.2, 0.2), y + 0.1, 0.74), rot_z=math.pi + rnd.uniform(-0.3, 0.3))
        elif rnd.random() < 0.5:
            W.instance(clip, (x, y, 0.74), rot_z=rnd.uniform(-1, 1))
for x, y in ((-12.5, 2.0), (2.5, -1.5), (-5, 2.0)):
    W.instance(lantern, (x, y, 0.74))
    bpy.ops.object.light_add(type="POINT", location=(x, y, 1.0))
    bpy.context.object.data.energy, bpy.context.object.data.color = 60, (1.0, 0.75, 0.45)
# прожектор на штативе от генератора — главный свет; ящики, канистры, лестница у стены
bpy.ops.object.light_add(type="AREA", location=(8, -6, 3.2), rotation=(math.radians(55), 0, math.radians(120)))
lamp = bpy.context.object
lamp.data.energy, lamp.data.color, lamp.data.size = 1500, (1.0, 0.9, 0.78), 0.6
bpy.ops.object.light_add(type="AREA", location=(-14, -6, 3.0), rotation=(math.radians(50), 0, math.radians(-120)))
lamp2 = bpy.context.object
lamp2.data.energy, lamp2.data.color, lamp2.data.size = 900, (1.0, 0.9, 0.78), 0.6
med, jerry, ladder, ext = W.ph("medical_box"), W.ph("metal_jerrycan"), W.ph("ladder_sectioned_01"), W.ph("korean_fire_extinguisher_01")
for k in range(4):
    W.instance(med, (12 + 0.7 * k, 7.5, 0), rot_z=rnd.uniform(-0.3, 0.3))
for k in range(3):
    W.instance(jerry, (13 + 0.5 * k, -8, 0), rot_z=rnd.uniform(-1, 1))
W.instance(ladder, (L / 2 - 0.6, 4, 0), rot_z=math.pi / 2)
W.instance(ext, (-L / 2 + 0.4, -6, 0))
# ноутбуки светят экранами
for o in list(bpy.data.objects):
    if o.instance_collection is laptop:
        bpy.ops.object.light_add(type="POINT", location=(o.location.x, o.location.y + 0.15, 0.95))
        bpy.context.object.data.energy, bpy.context.object.data.color, bpy.context.object.data.shadow_soft_size = 6, (0.6, 0.8, 1.0), 0.3

W.camera((4, -7.5, 1.9), (-4, 6, 2.6), lens=30, dof=4.0)
if is_draft:
    W.draft(sc)
W.render(out)
