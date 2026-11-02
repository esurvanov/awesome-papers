"""Сцена 2 кубической зарисовки: Зал Тринадцати Столов. Ильва кладёт слово-карточку на все столы; на Дарн и Эшан оно краснеет;
Советник: «в оригинале ясно» — Ильва: «верно везде, кроме двух»; крючок — список на амнистию.
blender -b -P papers/ega1-film/blender/shot_s02.py -- <выход.mp4|png> [--draft] [--still=сек]"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import voxel as V

args = sys.argv[sys.argv.index("--") + 1:]
out, draft = args[0], "--draft" in args
still = next((a.split("=")[1] for a in args if a.startswith("--still=")), None)

VALLEYS = ["Ур", "Таш", "Сайма", "Кора", "Вель", "Инги", "Дарн", "Хо", "Лазет", "Мирт", "Эшан", "Циб", "Ору"]
BAD = {"Эшан", "Дарн"}

sc = V.setup(samples=16)
V.hall()
# тёплые лампы под потолком
for x in (-10, 0, 10):
    bpy.ops.object.light_add(type="POINT", location=(x, 0, 5.4))
    bpy.context.object.data.energy, bpy.context.object.data.color, bpy.context.object.data.shadow_soft_size = 600, (1.0, 0.85, 0.65), 1.0

tables = {}
xs = {}
for i, name in enumerate(["Нулевой"] + VALLEYS):
    x = -13 + i * 2.0
    xs[name] = x
    tables[name] = V.table(x, 0.0, label=name, zero=(i == 0))

ilva, ip = V.person("ilva", (0.12, 0.18, 0.4), (-17, -4.5, 0), scarf=(0.75, 0.2, 0.15), hair=(0.1, 0.08, 0.06))
sov, sp = V.person("sovetnik", (0.35, 0.35, 0.37), (6, -5, 0), hair=(0.7, 0.7, 0.7))

# ---- тайминг (секунды) ----
T_WALK0, T_WALK1 = 6.0, 11.0        # Ильва идёт к Нулевому столу
T_CARD = 12.5                        # кладёт карточку
T_SPREAD0, T_SPREAD1 = 14.0, 19.0    # карточки появляются на всех столах
T_RED = 21.0                         # Дарн и Эшан краснеют
T_SOV0, T_SOV1 = 27.0, 31.0          # Советник подходит
T_END = 43.0

# Ильва: вход, путь к столу, кладёт карточку
V.stand(ilva, ip, 0.0, (-17, -4.5, 0), math.radians(-90))
V.walk(ilva, ip, T_WALK0, T_WALK1, (-17, -4.5, 0), (-13, -1.3, 0))
V.stand(ilva, ip, T_WALK1 + 0.1, (-13, -1.3, 0), 0.0)
V.reach(ip, T_CARD - 0.6, T_CARD + 0.6)
# карточка в руке → на столе
hand_card = V.card(ip["arm_r"], (0, -0.1, -0.85))
V.show(hand_card, T_WALK0, T_CARD)
cards = {}
for i, name in enumerate(["Нулевой"] + VALLEYS):
    c = V.card(tables[name], (-0.3, -0.1, 0.82), name=f"card_{name}")
    t0 = T_CARD if i == 0 else T_SPREAD0 + (i - 1) * (T_SPREAD1 - T_SPREAD0) / 12
    if name in BAD:
        V.show(c, t0, T_RED)
        r = V.card(tables[name], (-0.3, -0.1, 0.82), red=True, name=f"redcard_{name}")
        V.show(r, T_RED)
        glow = V.block((0, 0, 0.805), V.flat("table_red", (0.5, 0.05, 0.03), emit=((1, 0.15, 0.05), 0.5)), size=(1.62, 0.82, 0.012), parent=tables[name], name="glow")
        V.show(glow, T_RED)
    else:
        V.show(c, t0)
    cards[name] = c
# бумага со списком на столе Эшан: крупно в финале
lst = V.text("Список на амнистию\n(чтение Эшан)\n1. Ору Сайм-Хет\n2. Нарек Лазет-Ур\n3. Карим Вель-Ота", size=0.045, color=(0.1, 0.08, 0.06))
lst.parent = tables["Эшан"]
lst.location, lst.rotation_euler = (0.18, 0.22, 0.832), (0, 0, 0)
lst.data.align_x = "LEFT"
lst.data.space_line = 1.2

# Советник: подходит и встаёт напротив Ильвы
V.stand(sov, sp, 0.0, (6, -5, 0), math.radians(90))
V.walk(sov, sp, T_SOV0, T_SOV1, (6, -5, 0), (-11.2, -1.4, 0))
V.stand(sov, sp, T_SOV1 + 0.1, (-11.2, -1.4, 0), math.radians(-90))
V.key(ilva, T_SOV1 + 0.2, rot=(0, 0, math.radians(90)))  # Ильва поворачивается к нему

# ---- планы ----
cam = V.camera()
X0, XE, XD = xs["Нулевой"], xs["Эшан"], xs["Дарн"]
V.shot(cam, 0.0, 6.0, (-15.5, -6.3, 3.2), (-4, 0, 1.0), (-12.5, -6.2, 2.8), (2, 0, 1.0), lens=28)              # A: общий, проезд
V.shot(cam, 6.0, 12.0, (-15.8, -6.2, 1.9), (-15, -3, 1.3), (-13.6, -5.6, 1.9), (-13, -1, 1.2), lens=35)   # B: за Ильвой к столу
V.shot(cam, 12.0, 14.0, (-14.2, -2.6, 1.9), (-13.1, -0.1, 0.85), lens=45)                                # C: карточка ложится
V.shot(cam, 14.0, 20.0, (-14, -4, 2.2), (-10, 0, 0.9), (0, -6.3, 3.4), (0, 0, 0.9), lens=32)              # D: карточки по столам, отъезд
V.shot(cam, 20.0, 24.0, (XD - 2.5, -3.2, 1.9), (XD + 1.0, 0, 0.9), (XE - 1.5, -3.0, 1.7), (XE, 0, 0.9), lens=40)  # E: два стола краснеют
V.shot(cam, 24.0, 27.0, (-2, -6.4, 2.6), (-2, 0, 1.0), lens=30)                                            # F: общий: два красных пятна
V.shot(cam, 27.0, 36.0, (-15.5, -5.5, 1.8), (-12.3, -1.3, 1.4), (-14.8, -4.6, 1.7), (-12.2, -1.3, 1.4), lens=40)  # G: двое у стола
V.shot(cam, 36.0, T_END, (XE - 0.2, -1.6, 1.8), (XE + 0.2, 0.2, 0.84), (XE + 0.15, -0.5, 1.25), (XE + 0.2, 0.2, 0.84), lens=50)  # H: наезд на список

# ---- субтитры ----
V.caption(cam, "Кейван-Перевал. Зал Тринадцати Столов. До подписания шесть дней.", 0.8, 5.6)
V.caption(cam, "Ильва Таш-Керу, Старший толмач. Оригинал — на Нулевом столе.", 6.5, 11.5)
V.caption(cam, "— Одно слово. На все столы сразу.", 12.3, 14.0)
V.caption(cam, "«неприкосновенность» — на каждом столе своим языком", 14.5, 19.5)
V.caption(cam, "На столах Дарн и Эшан это слово — то же, что «безнаказанность».", 20.5, 24.0)
V.caption(cam, "Где слово гаснет — короткий список. Два стола из тринадцати.", 24.2, 26.8)
V.caption(cam, "СОВЕТНИК: В оригинале всё ясно. Подписываем?", 31.2, 33.4)
V.caption(cam, "ИЛЬВА: Что верно на Нулевом столе — верно на всех. Кроме двух. Их и проверяем.", 33.6, 36.0)
V.caption(cam, "Список на амнистию при чтении Эшана. Третья строка — убийца её брата.", 38.5, 42.5)

V.finish(out, T_END, draft=draft, still=still)
