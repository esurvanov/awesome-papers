"""Раскадровка ролика «Как сложить бесконечно много столбиков», версия 4: кадр на каждую фразу диктора, понятный без подготовки.
Герой — холм-парабола над осью; один опорный столбик на куске оси; сквозные сущности (договор, счётчики А и Б, табло, росток)
вводятся по одной (кольцо и подпись в кадре введения) и дальше стоят в верхней полосе.
Рисует: uv run python core/pipeline/animatic.py papers/integrals-film --draw (или одна сцена: manimgl papers/integrals-film/storyboard.py A01 -s -w)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(HERE))
import numpy as np
from manimlib import *
from manimkit import *
import passport as P
from kit import *
from icons import ICONS

_Board = storyboard_base(P.STATIONS, P.SCENES, ICONS, HERE)

# ---------- мир: холм-парабола над осью ----------
AY, XL, XR, H = -1.5, -5.0, 5.0, 3.0
F = lambda x: H * (1 - (x / 5.0) ** 2)          # герой: холм-парабола, площадь под ним 20


def pt(x, y=0.0):
    return np.array([x, AY + y, 0.0])


def hill(color=C_PRICE, w=5, x0=XL, x1=XR, n=100):
    return poly_line([pt(x, F(x)) for x in np.linspace(x0, x1, n)], color, w)


def axis_(label=True, color=C_AXIS):
    g = VGroup(line([-5.8, AY, 0], [5.8, AY, 0], color, 4))
    if label:
        g.add(tx("ось", 22, color).move_to([5.35, AY - 0.35, 0]))
    return g


def vaxis():
    return VGroup(line([-5.8, AY, 0], [-5.8, AY + 3.2, 0], C_BET, 3), tx("высота", 20, C_BET).move_to([-5.0, AY + 3.45, 0]))


def area(color=C_PRICE, op=0.18):
    return area_of(F, XL, XR, AY, color, op)


def bars(n, op=0.45, x0=XL, x1=XR):
    return bars_of(F, n, x0, x1, AY, C_BET, op)


def cuts(n):
    return VGroup(*[line([x, AY, 0], [x, AY + F(x), 0], C_NOTE, 1.5, dashed=True) for x in np.linspace(XL, XR, n + 1)])


def piece(x0, x1, color=C_AXIS, y=AY - 0.12, w=9):
    return line([x0, y, 0], [x1, y, 0], color, w)


def cap(s, color=C_NOTE, size=24):
    return tx(s, size, color).move_to([0, -2.65, 0])


def pill(s, color=C_BET, size=24):
    t = tx(s, size, color)
    return VGroup(RoundedRectangle(width=t.get_width() + 0.5, height=t.get_height() + 0.35, corner_radius=0.12).set_stroke(color, 2).set_fill("#0f1115", 1), t)


def plaque(year, who, color=WHITE, x=0.0, y=2.65):
    return pill(f"{year} · {who}", color, 24).move_to([x, y, 0])


def darrow(p, q, color):
    p, q = np.array(p, dtype=float), np.array(q, dtype=float)
    m = (p + q) / 2
    return VGroup(Arrow(m, p, buff=0).set_stroke(color, 3), Arrow(m, q, buff=0).set_stroke(color, 3)).set_color(color)


def dim_h(x0, x1, y, text, color=C_AXIS, size=20, up=False):
    a = darrow([x0, y, 0], [x1, y, 0], color)
    return VGroup(a, tx(text, size, color).move_to([(x0 + x1) / 2, y + (0.3 if up else -0.3), 0]))


def dim_v(x, y0, y1, text, color=C_BET, size=20, side=1):
    a = darrow([x, y0, 0], [x, y1, 0], color)
    return VGroup(a, tx(text, size, color).move_to([x + side * (0.12 + 0.55), (y0 + y1) / 2, 0]))


def ring(m, color=C_BET, pad=0.14):
    return RoundedRectangle(width=m.get_width() + 2 * pad, height=m.get_height() + 2 * pad, corner_radius=0.15).set_stroke(color, 3).move_to(m)


# опорный столбик: кусок оси (оранжевый) и столбик над ним; верх касается графика (наклонная линия), замер — в точке t0 ∈ [−1, 1]
def big_bar(cx=0.0, y0=-1.4, w=3.0, hh=2.0, slope=0.7, t0=0.0, bar=True, curve=True, op=0.45, pieceline=True):
    ys = lambda t: hh + slope * t
    g = VGroup()
    if bar:
        h = ys(t0)
        g.add(Rectangle(width=w, height=h).set_stroke(C_BET, 3).set_fill(C_BET, op).move_to([cx, y0 + h / 2, 0]))
    if curve:
        g.add(poly_line([[cx + t * w / 2, y0 + ys(t), 0] for t in np.linspace(-1.3, 1.3, 30)], C_PRICE, 5))
    if pieceline:
        g.add(line([cx - w / 2, y0, 0], [cx + w / 2, y0, 0], C_AXIS, 9))
    return g


# прыгающий график: каждой точке оси соответствует либо 1, либо 0 (одна точка на каждое место, без вертикального разброса)
def jump(x0=-4.8, x1=4.8, y0=AY, hi=2.0, n=60, seed=7, r=0.075, color=C_PRICE, share=0.5):
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, n) + rng.uniform(-0.3, 0.3, n) * (x1 - x0) / n
    up = rng.random(n) < share
    ds = [Dot([x, y0 + (hi if u else 0.0), 0], radius=r).set_color(color if u else WHITE) for x, u in zip(xs, up)]
    return VGroup(*ds), xs, up


def one_zero_marks(x=-5.8, y0=AY, hi=2.0):
    return VGroup(tx("1", 24, C_BET).move_to([x, y0 + hi, 0]), tx("0", 24, C_BET).move_to([x, y0, 0]),
                  line([x + 0.35, y0 + hi, 0], [x + 0.55, y0 + hi, 0], C_BET, 2), line([x + 0.35, y0, 0], [x + 0.55, y0, 0], C_BET, 2))


def noise(x0=-5.0, x1=5.0, y=0.0, amp=0.25, n=70, seed=11, color=C_NOISE, w=3):
    """Дрожащая линия в полосе y ± 4·amp: блуждание, растянутое по высоте; чем больше n, тем она грубее."""
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, n)
    b = np.cumsum(rng.normal(0, 1, n))
    ys = y + (b - (b.max() + b.min()) / 2) * (8 * amp / (b.max() - b.min()))
    return poly_line([[x, v, 0] for x, v in zip(xs, ys)], color, w), xs, ys


def bell(cx, cy, s=1.0, color=C_SUM):
    return curve_of(lambda x: 0.8 * np.exp(-x * x / 0.8), -1.6 * s, 1.6 * s, cy, color, 3, 40).move_to([cx, cy + 0.4, 0])


# ---------- сквозные сущности: верхняя полоса ----------
LEVERS = [("график", C_PRICE), ("ось", C_AXIS), ("высота", C_BET), ("сложение", C_ADD)]
TOPY = 3.42


def lamps(lit):
    on = list(lit) if isinstance(lit, (tuple, list)) else []
    g = VGroup()
    for n, c in LEVERS:
        lit_ = lit == "all" or n in on
        col, op = (c, 1.0) if lit_ else (C_NOTE, 0.55)
        g.add(VGroup(Dot(radius=0.11).set_color(col).set_opacity(op), tx(n, 19, col).set_opacity(op)).arrange(RIGHT, buff=0.1))
    return g.arrange(RIGHT, buff=0.28)


def twins(sign):
    col = C_BAD if sign == "≠" else C_SUM
    return VGroup(tx("А", 24), tx(sign, 34, col), tx("Б", 24)).arrange(RIGHT, buff=0.14)


def tablo(val):
    r = RoundedRectangle(width=1.7, height=0.62, corner_radius=0.1).set_stroke(C_SUM, 2.5).set_fill(C_SUM, 0.14)
    return VGroup(r, tx(val, 26, C_SUM).move_to(r))


def sprout(n):
    cols = [C_BET, C_PRICE, C_NOISE, C_AXIS, C_ADD, C_SUM, C_BET, C_PRICE, C_NOISE]
    g = VGroup(line([0, -0.4, 0], [0, 0.4, 0], C_SUM, 4))
    for i in range(min(n, 9)):
        y = -0.3 + 0.08 * i
        dx = 0.28 if i % 2 == 0 else -0.28
        g.add(line([0, y, 0], [dx, y + 0.15, 0], cols[i], 3))
    return g


POS = {"lamps": [-3.6, TOPY], "twins": [1.2, TOPY], "tablo": [3.7, TOPY], "sprout": [6.1, TOPY - 0.05]}
NAME = {"lamps": "договор", "twins": "счётчики", "tablo": "табло суммы", "sprout": "росток"}


def overlay(st, intro=None):
    g = VGroup()
    parts = {}
    if st.get("lit") is not None:
        parts["lamps"] = lamps(st["lit"])
    if st.get("twins"):
        parts["twins"] = twins(st["twins"])
    if st.get("tablo"):
        parts["tablo"] = tablo(st["tablo"])
    if st.get("sprout"):
        parts["sprout"] = sprout(st["sprout"])
    for k, m in parts.items():
        m.move_to([*POS[k], 0])
        g.add(m)
        if k == intro:
            g.add(ring(m, C_BET), tx(NAME[k], 18, C_BET).move_to([POS[k][0], POS[k][1] - 0.62, 0]))
    return g


def S(lit=None, twins=None, tablo=None, sprout=0):
    return dict(lit=lit, twins=twins, tablo=tablo, sprout=sprout)


# сцена → список (с какого кадра, состояние); INTRO: (сцена, кадр) → сущность, которая вводится в этом кадре
STATE = {
    "A04": [(3, S(tablo="Σ"))],
    "A05": [(1, S(tablo="Σ"))], "A06": [(1, S(tablo="Σ"))],
    "A07": [(1, S([])), (2, S(["график"])), (3, S(["ось"])), (4, S(["высота"])), (5, S(["сложение"])), (6, S("all", "=", "20"))],
    "A08": [(1, S(["график"], "=", "Σ")), (5, S(["график"], "=", "?"))],
    "A09": [(1, S(["высота"], "=", "?")), (5, S(["высота"], "≠", "?"))],
    "A10": [(1, S(["высота"], "=", "Σ")), (5, S(["высота"], "=", "20", 1))],
    "A11": [(1, S(["высота"], "≠", "?", 1)), (5, S(["высота"], "≠", "0", 1)), (6, S(["высота"], "=", "0", 1))],
    "A12": [(1, S(["высота"], "=", "Σ", 2))],
    "A13": [(1, S(["ось"], "=", "Σ", 3))],
    "A14": [(1, S(["ось"], "=", "Σ", 3))],
    "A15": [(1, S(["график", "ось"], "=", "?", 3))],
    "A16": [(1, S(["высота"], "=", "Σ", 3)), (4, S(["высота"], "≠", "?", 3))],
    "A17": [(1, S(["высота"], "=", "0", 4))],
    "A18": [(1, S(["высота"], "=", "0", 5))],
    "A19": [(1, S(["ось"], "≠", "?", 5)), (3, S(["ось"], "=", "число", 6))],
    "A20": [(1, S(["высота"], "=", "Σ", 6))],
    "A21": [(1, S(["сложение"], "=", "Σ", 7))],
    "A22": [(1, S(["сложение"], "=", "Σ", 8))],
    "A23": [(1, S("all", "=", "Σ")), (2, S("all"))],
}
INTRO = {("A04", 3): "tablo", ("A07", 1): "lamps", ("A07", 6): "twins", ("A10", 5): "sprout"}


def state_for(code, k):
    st = None
    for frm, s in STATE.get(code, []):
        if k >= frm:
            st = s
    return st


class Board(_Board):
    def snap(self, allow=()):
        old = getattr(self, "_ov", None)
        if old is not None:
            self.remove(old)
        code = type(self).__name__
        st = state_for(code, self._k + 1)           # _k — число уже сохранённых кадров; сейчас сохраняется кадр _k + 1
        self._ov = overlay(st, INTRO.get((code, self._k + 1))) if st else None
        if self._ov is not None:
            self.add(self._ov)
        super().snap(allow=[*allow, *([self._ov] if self._ov is not None else [])])

    def show(self, *mobs, c=None):
        old = getattr(self, "_content", None)
        if old:
            self.remove(*old)
        items = list(mobs) + ([cap(c)] if c else [])
        self._content = items
        self.add(*items)
        self.snap()


# ============================== акт 0: с нуля ==============================
class A01(Board):
    def construct(self):
        self.show(hill(), axis_(False, C_NOTE), c="график")
        self.show(hill(), axis_(False, C_NOTE), area(C_PRICE, 0.22), tx("площадь", 34, WHITE).move_to([0, -0.2, 0]), c="сколько места в этой фигуре")
        rect = Rectangle(width=2.4, height=1.6).set_stroke(C_BET, 3).set_fill(C_BET, 0.25).move_to([-3.6, 0.2, 0])
        arch = poly_line([[x, 0.1 + 1.6 * (1 - (x / 2.0) ** 2), 0] for x in np.linspace(-2, 2, 40)], C_PRICE, 5).move_to([3.4, 0.4, 0])
        base = line([1.4, -0.7, 0], [5.4, -0.7, 0], C_NOTE, 3)
        self.show(rect, tx("у прямоугольника всё просто", 22, C_BET).move_to([-3.6, -1.3, 0]), arch, base,
                  tx("кривая сверху: простой формулы нет", 22, C_PRICE).move_to([3.4, -1.3, 0]), c="прямоугольник считается просто")
        self.show(hill(), axis_(False, C_NOTE), area(C_PRICE, 0.15), tx("как считали и почему способ менялся", 30, WHITE).move_to([0, 2.4, 0]),
                  c="способ счёта переделывали много раз")
        self.show(tx("Как посчитать площадь так, чтобы ответ", 38).move_to([0, 1.5, 0]), tx("не зависел от способа счёта?", 38).move_to([0, 0.7, 0]),
                  hill(C_PRICE, 4, -2.6, 2.6).scale(0.5).move_to([0, -1.3, 0]), c="вопрос ролика")


class A02(Board):
    def construct(self):
        self.show(hill(), axis_(False, C_NOTE), c="как читать график")
        sl = Dot(pt(-2.5), radius=0.14).set_color(C_AXIS)
        self.show(hill(), axis_(), sl, tx("точка", 20, C_AXIS).move_to(pt(-2.5, -0.55)), c="по оси выбираем точку")
        x = -2.5
        self.show(hill(), axis_(), sl, line(pt(x), pt(x, F(x)), C_BET, 4), Dot(pt(x, F(x)), radius=0.11).set_color(C_BET),
                  dim_v(x - 0.35, AY, AY + F(x), "высота", C_BET, 22, side=-1), c="над точкой стоит число — высота")
        ghosts = VGroup(*[line(pt(xx), pt(xx, F(xx)), C_BET, 2).set_opacity(0.45) for xx in (-4.0, -3.2, -1.5, -0.5, 0.8)])
        part = poly_line([pt(xx, F(xx)) for xx in np.linspace(XL, 1.5, 60)], C_PRICE, 5)
        self.show(part, axis_(), ghosts, line(pt(1.5), pt(1.5, F(1.5)), C_BET, 4), Dot(pt(1.5), radius=0.14).set_color(C_AXIS),
                  Dot(pt(1.5, F(1.5)), radius=0.11).set_color(C_BET), c="двигаем точку — высота меняется, кривая вычерчивается")
        chips = VGroup(*[VGroup(Square(side_length=0.3).set_stroke(col, 2).set_fill(col, 1), tx(t, 24, col)).arrange(RIGHT, buff=0.15)
                         for t, col in (("ось — оранжевая", C_AXIS), ("высота — жёлтая", C_BET), ("график — синий", C_PRICE))]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        self.show(hill().scale(0.8, about_point=ORIGIN).shift(LEFT * 1.6 + UP * 0.3), axis_().scale(0.8, about_point=ORIGIN).shift(LEFT * 1.6 + UP * 0.3), line([-3.0, AY * 0.8 + 0.3, 0], [-3.0, AY * 0.8 + 0.3 + F(-2.0) * 0.8, 0], C_BET, 4), chips.move_to([4.6, 0.2, 0]), c="цвета ролика")


class A03(Board):
    def construct(self):
        self.show(hill(), axis_(), cuts(8), VGroup(*[piece(XL + i * 1.25, XL + (i + 1) * 1.25, C_AXIS, AY - 0.12, 8) for i in range(8)]), c="ось делится на куски")
        self.show(hill(), axis_(), bars(8), c="на каждом куске — столбик")
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), tx("кусок оси", 24, C_AXIS).move_to([0, -1.95, 0]),
                  tx("верх на графике", 24, C_PRICE).move_to([2.4, 1.6, 0]), tx("столбик", 26, C_BET).move_to([0, 0.0, 0]),
                  c="столбик стоит на куске оси, верх касается графика")
        self.show(hill(), axis_(), bars(16), c="вся фигура — из столбиков")


class A04(Board):
    def construct(self):
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), dim_v(2.05, -1.4, 0.6, "высота", C_BET, 24), dim_h(-1.7, 1.7, -1.95, "ширина = длина куска", C_AXIS, 22),
                  c="у столбика есть высота и ширина")
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), tx("площадь = ширина × высота", 30, WHITE).move_to([0, 2.1, 0]),
                  dim_v(2.05, -1.4, 0.6, "высота", C_BET, 24), dim_h(-1.7, 1.7, -1.95, "ширина", C_AXIS, 22), c="площадь столбика")
        self.show(hill(), axis_(), bars(10), tx("складываем площади всех столбиков", 28, C_SUM).move_to([0, 2.4, 0]), c="получается сумма")

        def mini(cx, n, val):
            g = VGroup(bars_of(F, n, -2.2, 2.2, 0.0, C_BET, 0.45), curve_of(F, -2.2, 2.2, 0.0, C_PRICE, 3, 60))
            return VGroup(g.scale(0.5, about_point=ORIGIN).move_to([cx, 0.1, 0]), tx(val, 28, C_SUM).move_to([cx, -1.5, 0]), tx(f"столбиков: {n}", 20, C_NOTE).move_to([cx, -1.05, 0]))
        sums = {6: "17,9", 12: "19,4", 24: "19,8"}
        self.show(*[mini(cx, n, sums[n]) for cx, n in ((-4.3, 6), (0.0, 12), (4.3, 24))], tx("площадь фигуры = 20", 26, WHITE).move_to([0, 2.3, 0]),
                  c="тоньше столбики — сумма ближе к площади")
        self.show(hill(), axis_(), bars(40, 0.5), plaque("1854", "Риман", WHITE, 0, 2.5), c="без конца тоньше — сумма равна площади")


class A05(Board):
    def construct(self):
        T = lambda a, b, c, col, op: Polygon(pt(*a), pt(*b), pt(*c)).set_stroke(col, 3).set_fill(col, op)
        base = [hill(), axis_(False, C_NOTE)]
        self.show(*base, plaque("III в. до н. э.", "Архимед", WHITE, 0, 2.65), tx("кусок параболы", 26, C_PRICE).move_to([0, -0.4, 0]), c="Архимед искал площадь куска параболы")
        t1 = T((-5, 0), (5, 0), (0, H), C_BET, 0.3)
        t2 = [T((0, H), (5, 0), (2.5, F(2.5)), C_AXIS, 0.4), T((-5, 0), (0, H), (-2.5, F(2.5)), C_AXIS, 0.4)]
        self.show(*base, t1, *t2, tx("вписанный треугольник", 22, C_BET).move_to([0, -0.2, 0]), tx("поменьше", 20, C_AXIS).move_to([-3.2, 0.0, 0]), tx("поменьше", 20, C_AXIS).move_to([3.2, 0.0, 0]), c="в кусок вписан треугольник, в промежутки — поменьше")
        t3 = [T((0, H), (2.5, F(2.5)), (1.25, F(1.25)), C_ADD, 0.5) for _ in range(0)]
        sq = lambda s, col: Square(side_length=s).set_stroke(col, 3).set_fill(col, 0.4)
        row = VGroup(sq(1.6, C_BET), sq(0.8, C_AXIS), sq(0.4, C_ADD), sq(0.2, C_SUM), tx("…", 30, WHITE)).arrange(RIGHT, buff=0.35, aligned_edge=DOWN).move_to([0, 0.6, 0])
        self.show(row, tx("1", 22, WHITE).next_to(row[0], DOWN, buff=0.1), tx("¼", 22, WHITE).next_to(row[1], DOWN, buff=0.1), tx("1/16", 20, WHITE).next_to(row[2], DOWN, buff=0.1),
                  c="каждый следующий ряд — четверть предыдущего")
        self.show(row.copy().move_to([0, 1.6, 0]), tx("вместе: треугольник и ещё его треть", 30, WHITE).move_to([0, -0.2, 0]),
                  tx("сумма подходит к одному числу", 26, C_SUM).move_to([0, -1.2, 0]), c="ряды не кончаются, сумма подходит к числу")
        # пятая фраза: та же идея — части, число которых растёт без конца
        self.show(VGroup(bars_of(lambda x: 1.3 * (1 - (x / 2.5) ** 2), 10, -2.5, 2.5, 0.0, C_BET, 0.4), curve_of(lambda x: 1.3 * (1 - (x / 2.5) ** 2), -2.5, 2.5, 0.0, C_PRICE, 3, 40)).move_to([3.2, 0.2, 0]),
                  VGroup(Polygon(np.array([-1.5, -0.7, 0]), np.array([1.5, -0.7, 0]), np.array([0, 0.9, 0])).set_stroke(C_BET, 3).set_fill(C_BET, 0.3)).move_to([-3.2, 0.1, 0]),
                  tx("=", 40, WHITE).move_to([0, 0.2, 0]), tx("части, которых без конца больше", 26, C_NOTE).move_to([0, -1.8, 0]), c="та же идея, что у столбиков")


def _ncurve(x, y, w, h, color=C_SUM, n=40):
    return curve_of(lambda t: h * (1 / (1 + np.exp(-1.4 * t))), -w / 2, w / 2, y, color, 4, n).move_to([x, y + h / 2, 0])


class A06(Board):
    def construct(self):
        x1 = 1.0
        left = lambda: VGroup(area_of(F, XL, x1, AY, C_SUM, 0.35), hill(), axis_(False, C_NOTE), line(pt(x1), pt(x1, F(x1)), C_BET, 3), Dot(pt(x1), radius=0.13).set_color(C_AXIS))
        self.show(left(), tx("площадь слева от точки", 24, C_SUM).move_to([-2.0, 0.4, 0]), c="нашли короткий путь")
        self.show(left(), portrait("Ньютон", "", WHITE, 0.9).move_to([-5.4, 2.35, 0]), portrait("Лейбниц", "", WHITE, 0.9).move_to([-3.6, 2.35, 0]),
                  plaque("XVII в.", "независимо", WHITE, 3.5, 2.65), c="Ньютон и Лейбниц, XVII век")
        def panel(g, cx, cy, sc):
            g.scale(sc, about_point=pt(0)).shift(np.array([cx, cy, 0.0]) - pt(0))
            return g
        Gf = lambda x: 2.4 * (((x + 5) - (x ** 3 + 125) / 75.0) * H / 20.0 * 20.0 / 20.0) / (H * 10 * 2 / 3) * 1.0
        grow = lambda x: 2.4 * ((x + 5) - (x ** 3 + 125) / 75.0) / (10 - 250 / 75.0)     # площадь слева от точки, 0…2,4
        xs0 = 1.0
        L = lambda extra=(): panel(VGroup(hill(C_PRICE, 4), axis_(False, C_NOTE), *extra), -3.2, -0.6, 0.5)
        R = lambda extra=(): VGroup(line([0.4, -1.8, 0], [6.0, -1.8, 0], C_NOTE, 2), poly_line([[0.4 + 5.6 * (x + 5) / 10, -1.8 + grow(x), 0] for x in np.linspace(-5, 5, 60)], C_SUM, 5), *extra)
        dotL = lambda x: Dot(pt(x), radius=0.14).set_color(C_AXIS)
        self.show(L([line(pt(xs0), pt(xs0, F(xs0)), C_BET, 4), dotL(xs0)]), R([Dot([0.4 + 5.6 * (xs0 + 5) / 10, -1.8 + grow(xs0), 0], radius=0.12).set_color(C_SUM)]),
                  tx("высота графика", 22, C_BET).move_to([-3.2, 1.4, 0]), tx("площадь слева от точки", 22, C_SUM).move_to([3.2, 0.9, 0]),
                  c="где график выше, там площадь растёт быстрее")
        xa, xb = -2.0, 2.0
        ga, gb = [0.4 + 5.6 * (x + 5) / 10 for x in (xa, xb)], [-1.8 + grow(x) for x in (xa, xb)]
        self.show(L([area_of(F, xa, xb, AY, C_SUM, 0.45), line(pt(xa), pt(xa, F(xa)), C_BET, 3), line(pt(xb), pt(xb, F(xb)), C_BET, 3)]),
                  R([Dot([ga[0], gb[0], 0], radius=0.12).set_color(C_SUM), Dot([ga[1], gb[1], 0], radius=0.12).set_color(C_SUM), line([ga[1] + 0.35, gb[0], 0], [ga[1] + 0.35, gb[1], 0], C_SUM, 4)]),
                  tx("площадь между двумя точками", 22, C_SUM).move_to([-3.2, 1.4, 0]), tx("разность двух значений", 22, C_SUM).move_to([3.2, 1.0, 0]),
                  c="площадь между точками — разность двух значений")
        s = VMobject().set_points_smoothly([np.array(p, dtype=float) for p in
                                            [(-0.45, -1.0, 0), (-0.25, -1.25, 0), (-0.05, -1.05, 0), (0.0, -0.6, 0), (0.0, 0.7, 0), (0.05, 1.05, 0), (0.25, 1.25, 0), (0.45, 1.05, 0)]]).set_stroke(WHITE, 8).set_fill(opacity=0)
        self.show(s.scale(1.2).move_to([-2.0, 0.2, 0]), tx("вытянутая S от слова summa", 28, WHITE).move_to([2.2, 0.4, 0]), portrait("Лейбниц", "", WHITE, 1.0).move_to([2.2, -1.4, 0]),
                  c="знак суммы придумал Лейбниц")


class A07(Board):
    def construct(self):
        cards = lambda lit: VGroup(*[pill(t, col if i in lit else C_NOTE, 22) for i, (t, col) in enumerate(
            [("1 · что складываем", C_PRICE), ("2 · чем меряем ширину", C_AXIS), ("3 · где берём высоту", C_BET), ("4 · как складываем", C_ADD)])]).arrange(RIGHT, buff=0.25).move_to([0, 2.4, 0])
        bb = lambda **k: big_bar(0, -1.5, 3.4, 1.9, 0.6, 0.0, **k)
        self.show(bb(), cards([]), c="у счёта есть договор из четырёх пунктов")
        self.show(big_bar(0, -1.5, 3.4, 1.9, 0.6, 0.0, bar=False), poly_line([[t * 1.7, -1.5 + 1.9 + 0.6 * t, 0] for t in np.linspace(-1.3, 1.3, 30)], C_PRICE, 9),
                  bb(curve=False, pieceline=False).set_opacity(0.3), cards([0]), c="первый пункт — какой график")
        self.show(bb(), line([-1.7, -1.5, 0], [1.7, -1.5, 0], C_AXIS, 14), cards([1]), c="второй — чем меряем ширину куска")
        self.show(bb(), Dot([0.0, -1.5 + 1.9, 0], radius=0.17).set_color(C_BET), tx("точка", 22, C_BET).move_to([0.0, 1.0, 0]), cards([2]), c="третий — где в куске берём высоту")
        self.show(bb(), tx("+", 60, C_ADD).move_to([2.8, -0.2, 0]), tablo("Σ").move_to([4.6, -0.2, 0]), cards([3]), c="четвёртый — как складываем")

        def mini(cx, n, val):
            g = VGroup(bars_of(F, n, -2.2, 2.2, 0.0, C_BET, 0.45), curve_of(F, -2.2, 2.2, 0.0, C_PRICE, 3, 60))
            return VGroup(g.scale(0.55, about_point=ORIGIN).move_to([cx, 0.2, 0]), tx(val, 30, C_SUM).move_to([cx, -1.5, 0]), tx(f"режет на {n}", 22, C_NOTE).move_to([cx, 1.7, 0]))
        self.show(mini(-3.4, 8, "20"), mini(3.4, 13, "20"), twins("=").scale(1.6).move_to([0, 0.2, 0]), tx("счётчик А", 22, WHITE).move_to([-3.4, -2.2, 0]), tx("счётчик Б", 22, WHITE).move_to([3.4, -2.2, 0]),
                  c="разные нарезки — одна и та же сумма")


class A08(Board):
    def construct(self):
        stairs = poly_line([pt(-5, 1.0), pt(-3, 1.0), pt(-3, 2.2), pt(-1, 2.2), pt(-1, 0.6), pt(1.5, 0.6), pt(1.5, 2.6), pt(3.4, 2.6), pt(3.4, 1.4), pt(5, 1.4)], C_PRICE, 5)
        self.show(stairs, axis_(), hill(C_NOTE, 2).set_opacity(0.3), c="график не обязан быть гладким")
        d, xs, up = jump()
        self.show(d, axis_(), vaxis().scale(0.001), one_zero_marks(), tx("в части точек единица, в остальных ноль", 24, WHITE).move_to([0, 2.4, 0]), c="в каждой точке оси — единица или ноль")
        # увеличение куска: кусок оси и его крупный план в рамке; в крупном плане снова и единицы, и нули
        dd, _, _ = jump(-4.8, 4.8, AY, 1.2, 60, 7)
        sel = Rectangle(width=0.8, height=1.6).set_stroke(C_AXIS, 2).move_to([0.0, AY + 0.6, 0])

        def panel(cx, cy, w, h, n, seed):
            fr = Rectangle(width=w, height=h).set_stroke(C_AXIS, 2)
            pd, _, _ = jump(-w / 2 + 0.3, w / 2 - 0.3, -h / 2 + 0.3, h - 0.6, n, seed, 0.09)
            return VGroup(fr, pd).move_to([cx, cy, 0])
        p1 = panel(0.0, 1.4, 7.0, 1.8, 26, 21)
        self.show(dd.set_opacity(0.7), axis_(), one_zero_marks(hi=1.2), sel, p1,
                  line([-0.4, AY + 1.4, 0], [-3.5, 0.5, 0], C_AXIS, 2, True), line([0.4, AY + 1.4, 0], [3.5, 0.5, 0], C_AXIS, 2, True),
                  tx("тот же кусок крупно", 22, C_AXIS).move_to([5.0, 1.4, 0]), c="в любом куске есть и те, и другие")
        pa = panel(-3.3, 0.6, 4.4, 1.8, 20, 21)
        pb = panel(2.8, 0.6, 5.8, 1.8, 16, 33)
        self.show(pa, pb, Rectangle(width=0.7, height=1.4).set_stroke(C_AXIS, 2).move_to([-3.0, 0.6, 0]), Arrow([-0.8, 0.6, 0], [-0.1, 0.6, 0], buff=0).set_color(C_AXIS),
                  tx("ещё крупнее", 22, C_AXIS).move_to([2.8, -0.7, 0]), tx("и снова единицы и нули вперемешку", 24, WHITE).move_to([0, 2.3, 0]), c="увеличиваем — снова и то, и другое")
        self.show(d, axis_(), one_zero_marks(), tx("?", 90, C_BAD).move_to([0, 2.6, 0]), tx("выдержит ли договор такой график", 26, WHITE).move_to([0, -2.2, 0]))


class A09(Board):
    def construct(self):
        d, xs, up = jump()
        self.show(d, axis_(), one_zero_marks(), piece(-0.6, 0.6), tx("проверим договор", 28, WHITE).move_to([0, 2.5, 0]), c="возьмём кусок оси")
        row, _, upv = jump(-1.7, 1.7, -1.0, 1.9, 14, 5, 0.11)
        base = VGroup(line([-1.9, -1.0, 0], [1.9, -1.0, 0], C_AXIS, 9), Rectangle(width=3.8, height=1.9).set_stroke(C_BET, 2).move_to([0, -0.05, 0]).set_stroke(opacity=0.5))
        self.show(row, base, tx("кусок оси", 22, C_AXIS).move_to([0, -1.55, 0]), c="поставим на нём столбик")
        i_hi = int(np.argmax(upv)); i_lo = int(np.argmin(upv))
        self.show(row, base, lens(row[i_hi].get_center()[0] - 0.05, row[i_hi].get_center()[1] + 0.05), tx("замер", 30, C_BET).move_to([0, 2.0, 0]), c="высота берётся в одной точке куска")
        hi_bar = Rectangle(width=3.0, height=1.9).set_stroke(C_BET, 3).set_fill(C_BET, 0.45).move_to([-3.4, -0.05, 0])
        lo_bar = line([2.0, -1.0, 0], [5.0, -1.0, 0], C_BET, 8)
        self.show(hi_bar, line([-4.9, -1.0, 0], [-1.9, -1.0, 0], C_AXIS, 9), Dot([-3.4, 0.9, 0], radius=0.13).set_color(C_BET), tx("точка с единицей: столбик высокий", 22, C_BET).move_to([-3.4, 1.6, 0]),
                  lo_bar, line([2.0, -1.0, 0], [5.0, -1.0, 0], C_AXIS, 9).shift(DOWN * 0.1), Dot([3.5, -1.0, 0], radius=0.13).set_color(WHITE), tx("точка с нулём: столбик плоский", 22, WHITE).move_to([3.5, -0.2, 0]),
                  c="единица — высокий, ноль — плоский")
        self.show(hi_bar.copy().move_to([-3.4, -0.05, 0]), line([-4.9, -1.0, 0], [-1.9, -1.0, 0], C_AXIS, 9), line([2.0, -1.0, 0], [5.0, -1.0, 0], C_BET, 8),
                  tx("≠", 100, C_BAD).move_to([0, -0.3, 0]), tx("один и тот же кусок", 22, C_AXIS).move_to([0, -2.2, 0]), c="кусок тот же, а столбики разные")
        self.show(d, axis_(), one_zero_marks(), cross(C_BAD, 0.9).move_to([0, 0.8, 0]), plaque("1854", "Риман", C_BAD, 0, 2.6), c="способ Римана здесь не работает")


class A10(Board):
    def construct(self):
        N = 6
        hs = np.linspace(0, H, N + 1)
        xk = lambda h: 5.0 * np.sqrt(max(0.0, 1 - h / H))
        layer = lambda k, col=C_BET, op=0.4: Rectangle(width=2 * xk(hs[k]), height=hs[k + 1] - hs[k]).set_stroke(col, 2).set_fill(col, op).move_to([0, AY + (hs[k] + hs[k + 1]) / 2, 0])
        self.show(hill(), axis_(), vaxis(), plaque("1902", "Лебег", WHITE, 0, 2.7).scale(0.9).move_to([3.0, 2.65, 0]), *[line([-5.8, AY + h, 0], [-5.5, AY + h, 0], C_BET, 3) for h in hs], c="начнём с высоты")
        self.show(hill(), axis_(), *[line([-xk(h), AY + h, 0], [xk(h), AY + h, 0], C_BET, 2) for h in hs[1:-1]], c="горизонтальные слои, как этажи")
        k = 2
        self.show(hill(), axis_(), layer(k, C_BET, 0.5), line([-xk(hs[k]), AY + hs[k], 0], [-xk(hs[k]), AY, 0], C_NOTE, 2, True), line([xk(hs[k]), AY + hs[k], 0], [xk(hs[k]), AY, 0], C_NOTE, 2, True),
                  piece(-xk(hs[k]), xk(hs[k]), C_AXIS), tx("слой", 24, C_BET).move_to([0, AY + (hs[k] + hs[k + 1]) / 2 + 0.55, 0]), tx("часть оси под слоем", 22, C_AXIS).move_to([0, AY - 0.55, 0]),
                  c="часть оси под слоем — где график достаёт до этой высоты")
        w = 2 * xk(hs[k])
        self.show(Rectangle(width=w, height=hs[k + 1] - hs[k]).set_stroke(C_BET, 3).set_fill(C_BET, 0.5).move_to([0, 0.4, 0]), dim_h(-w / 2, w / 2, -0.3, "длина части оси", C_AXIS, 22),
                  dim_v(-w / 2 - 0.3, 0.4 - (hs[k + 1] - hs[k]) / 2, 0.4 + (hs[k + 1] - hs[k]) / 2, "высота слоя", C_BET, 22, side=-1),
                  tx("площадь слоя = высота слоя × длина части оси", 26, WHITE).move_to([0, 2.0, 0]), c="площадь слоя")
        self.show(axis_(), hill(C_PRICE, 3), *[layer(i, C_BET, 0.35 + 0.08 * i) for i in range(N)], tx("сумма слоёв = площадь холма", 26, C_SUM).move_to([0, 2.3, 0]),
                  c="сложим слои — снова площадь холма")


class A11(Board):
    def construct(self):
        d, xs, up = jump()
        self.show(d, axis_(), one_zero_marks(), tx("слои — для прыгающего графика", 26, WHITE).move_to([0, 2.7, 0]), c="применим слои к прыгающему графику")
        b1 = Rectangle(width=11.4, height=0.7).set_stroke(C_BET, 2).set_fill(C_BET, 0.1).move_to([0, AY + 2.0, 0])
        b0 = Rectangle(width=11.4, height=0.7).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.1).move_to([0, AY, 0])
        self.show(d, axis_(False, C_NOTE), b1, b0, tx("слой единицы", 22, C_BET).move_to([-4.6, AY + 2.75, 0]), tx("слой нуля", 22, C_NOTE).move_to([-4.6, AY - 0.75, 0]), c="слоёв всего два")
        d1 = VGroup(*[m for m, u in zip(d, up) if u]).copy().set_color(C_BET)
        d0 = VGroup(*[m for m, u in zip(d, up) if not u]).copy().set_color(WHITE)
        self.show(d1, d0, b1, b0, axis_(False, C_NOTE), tx("все точки с единицей", 22, C_BET).move_to([-4.0, AY + 2.75, 0]), tx("все остальные", 22, WHITE).move_to([-4.6, AY - 0.75, 0]), c="каждая точка — в свой слой")
        lst = VGroup(*[tx(s, 22, C_BET) for s in ("точка 1", "точка 2", "точка 3", "точка 4", "…")]).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        self.show(d1.copy().scale(0.8).move_to([-2.4, 1.6, 0]), Arrow([1.0, 1.6, 0], [2.2, 1.6, 0], buff=0).set_color(WHITE), lst.move_to([4.2, 1.0, 0]),
                  tx("их можно выписать в список", 24, WHITE).move_to([0, -0.4, 0]), tx("длина такой россыпи = 0", 28, C_AXIS).move_to([0, -1.5, 0]), c="такие точки можно выписать списком — длины у них нет")
        self.show(tx("слой единицы: 1 × 0 = 0", 30, C_BET).move_to([0, 1.5, 0]), tx("слой нуля: 0 × вся ось = 0", 30, WHITE).move_to([0, 0.3, 0]), tx("сумма = 0", 40, C_SUM).move_to([0, -1.1, 0]),
                  c="сумма равна нулю при любом счёте")
        self.show(twins("=").scale(2.0).move_to([-2.4, 0.4, 0]), tablo("0").scale(1.8).move_to([2.4, 0.4, 0]), c="договор выполнен: А и Б сходятся")


class A12(Board):
    def construct(self):
        st = lambda n, op: poly_line(self._stair(n), C_PRICE, 4).set_stroke(opacity=op)
        self.show(hill(C_NOTE, 2), axis_(), tx("второй козырь Лебега", 32, WHITE).move_to([0, 2.6, 0]), c="пределы")
        self.show(hill(C_NOTE, 2), axis_(), st(3, 0.35), st(6, 0.6), st(12, 1.0), tx("приближения", 26, C_PRICE).move_to([0, 2.4, 0]), c="графики всё ближе к предельному — приближения")

        def mini(cx, n, val):
            g = VGroup(poly_line([np.array([x, y - 0.5, 0.0]) for x, y, _ in self._stair(n, -2.0, 2.0, 1.3, 0.0)], C_PRICE, 3), curve_of(lambda x: 1.3 * (1 - (x / 2.0) ** 2), -2.0, 2.0, -0.5, C_NOTE, 2, 40))
            return VGroup(g.move_to([cx, 0.4, 0]), tx(val, 30, C_SUM).move_to([cx, -1.3, 0]))
        self.show(mini(-4.4, 3, "10"), mini(0.0, 6, "16"), mini(4.4, 12, "18,5"), tx("площади растут к 20 — площади предельного графика", 26, WHITE).move_to([0, 2.4, 0]), c="площади подходят к площади предельного графика")
        ok = tx("✓", 80, C_SUM)
        self.show(VGroup(tx("слои Лебега", 30, C_BET), ok).arrange(DOWN, buff=0.4).move_to([-3.2, 0.5, 0]),
                  VGroup(tx("столбики Римана", 30, C_BET), tx("иногда застревают", 24, C_BAD)).arrange(DOWN, buff=0.4).move_to([3.2, 0.5, 0]), c="со слоями работает всегда")
        self.show(VGroup(curve_of(lambda x: 0.7 * np.sin(2.5 * x), -1.2, 1.2, 0, C_PRICE, 4, 40).scale(1.0), tx("ряды Фурье", 26, WHITE)).arrange(DOWN, buff=0.4).move_to([-3.0, 0.4, 0]),
                  VGroup(bell(0, 0), tx("вероятность", 26, WHITE)).arrange(DOWN, buff=0.4).move_to([3.0, 0.4, 0]), c="на Лебеге стоят Фурье и вероятность")

    def _stair(self, n, x0=-5.0, x1=5.0, hmax=H, y0=AY):
        pts = []
        w = (x1 - x0) / n
        for i in range(n):
            xm = x0 + (i + 0.5) * w
            h = hmax * (1 - (max(abs(x0 + i * w), abs(x0 + (i + 1) * w)) / (x1)) ** 2)
            pts += [np.array([x0 + i * w, y0 + h, 0.0]), np.array([x0 + (i + 1) * w, y0 + h, 0.0])]
        return pts


# ============================== акт 2: другая ось ==============================
def wfun(x):   # вес: растёт неровно, есть пологий участок и скачок при x = 1,5
    return 0.9 * (x + 5) * 0.4 + (1.6 if x > 1.5 else 0.0) + (0.8 * np.sin(0.5 * (x + 5)) if x < 1.5 else 0.0)


class A13(Board):
    def construct(self):
        self.show(hill(), axis_(), bars(8), c="поменяем ширину столбика — пункт про ось")
        edges = [-5.0, -3.6, -2.4, -1.5, -0.2, 1.5, 2.4, 3.6, 5.0]
        ub = bars_of(F, 8, -5.0, 5.0, AY, C_BET, 0.35)
        ubs = VGroup(*[Rectangle(width=edges[i + 1] - edges[i], height=F((edges[i] + edges[i + 1]) / 2)).set_stroke(C_BET, 2).set_fill(C_BET, 0.4).move_to([(edges[i] + edges[i + 1]) / 2, AY + F((edges[i] + edges[i + 1]) / 2) / 2, 0]) for i in range(8)])
        self.show(hill(), axis_(), ubs, dim_h(edges[1], edges[2], AY - 0.5, "прирост веса", C_AXIS, 20), c="ширина куска — прирост другой величины, веса")
        wpts = [(-5.0, 0.0), (-3.0, 0.5), (-1.2, 0.8), (0.4, 0.85), (1.2, 0.9), (2.0, 1.9), (3.2, 2.2), (5.0, 2.4)]
        wl = poly_line([[x, -2.55 + 0.5 * y, 0] for x, y in wpts], C_AXIS, 5)
        self.show(hill().scale(0.5, about_point=pt(0)).shift(UP * 2.0), line([-5.8, -0.55, 0], [5.8, -0.55, 0], C_AXIS, 4), tx("ось", 20, C_AXIS).move_to([5.4, -0.85, 0]), wl,
                  line([-5.0, -2.6, 0], [5.0, -2.6, 0], C_NOTE, 2), tx("вес", 28, C_AXIS).move_to([-5.5, -1.7, 0]), tx("почти стоит", 20, C_AXIS).move_to([0.4, -1.55, 0]),
                  tx("быстро растёт", 20, C_AXIS).move_to([3.6, -1.1, 0]), c="вес растёт неровно")
        wide = Rectangle(width=2.0, height=2.0).set_stroke(C_BET, 3).set_fill(C_BET, 0.45).move_to([0, -0.4, 0])
        step = poly_line([[-3.0, -1.5, 0], [-1.0, -1.5, 0], [-1.0, -0.5, 0], [1.0, -0.5, 0], [1.0, 0.8, 0], [3.0, 0.8, 0]], C_AXIS, 5)
        self.show(wide, dim_h(-1.0, 1.0, -1.75, "скачок веса = широкий столбик", C_AXIS, 22), step.shift(DOWN * 0.0), tx("скачок", 24, C_AXIS).move_to([1.5, 0.0, 0]), c="скачок веса — широкий столбик")
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), tx("площадь = высота × прирост веса", 30, WHITE).move_to([0, 2.2, 0]), dim_h(-1.7, 1.7, -1.95, "прирост веса", C_AXIS, 22), c="сумма считается так же")
        self.show(hill(), axis_(), bars(8), plaque("1894", "Стилтьес", WHITE, 0, 2.65), c="так предложил Стилтьес")


class A14(Board):
    def construct(self):
        self.show(hill(), axis_(), bars(8), tx("куски равны", 24, C_NOTE).move_to([0, 2.5, 0]), c="куски были одинаковые")
        edges = [-5.0, -3.0, -1.2, 0.4, 1.8, 2.9, 3.8, 4.5, 5.0]
        ubs = VGroup(*[Rectangle(width=edges[i + 1] - edges[i], height=F((edges[i] + edges[i + 1]) / 2)).set_stroke(C_BET, 2).set_fill(C_BET, 0.4).move_to([(edges[i] + edges[i + 1]) / 2, AY + F((edges[i] + edges[i + 1]) / 2) / 2, 0]) for i in range(8)])
        self.show(hill(), axis_(), ubs, plaque("1957–61", "Курцвейль и Хенсток", WHITE, 0, 2.65), c="куски могут быть разной ширины")
        self.show(hill(), axis_(), ubs, tx("круто — куски уже", 22, C_AXIS).move_to([-4.0, 0.6, 0]), tx("полого — шире", 22, C_AXIS).move_to([0.6, 2.2, 0]), c="где график круто меняется — куски уже")


class A15(Board):
    def construct(self):
        j, _, _ = noise(-5, 5, -1.7, 0.1, 70, 4, C_NOISE, 3)
        self.show(hill().scale(0.55, about_point=pt(0)).shift(UP * 2.1), line([-5.8, -0.5, 0], [5.8, -0.5, 0], C_AXIS, 4), tx("ось", 20, C_AXIS).move_to([5.4, -0.8, 0]), j, tx("вес", 24, C_AXIS).move_to([-5.5, -1.7, 0]), c="а если вес случаен")
        j1, _, _ = noise(-5.5, 5.5, 0.2, 0.3, 90, 11, C_NOISE, 4)
        self.show(j1, tx("шум", 44, C_NOISE).move_to([0, 2.0, 0]), c="шум — линия дрожит вверх и вниз наугад")
        j2, _, _ = noise(-3.2, 3.2, -0.9, 0.22, 90, 17, C_NOISE, 4)
        j1s, _, _ = noise(-5.5, 5.5, 2.0, 0.12, 90, 11, C_NOISE, 3)
        fr = Rectangle(width=0.9, height=1.0).set_stroke(C_AXIS, 2).move_to([0.8, 2.0, 0])
        self.show(j1s, fr, j2, line([0.3, 1.5, 0], [-3.2, 0.2, 0], C_AXIS, 2, True), line([1.3, 1.5, 0], [3.2, 0.2, 0], C_AXIS, 2, True), tx("увеличим", 22, C_AXIS).move_to([4.5, 1.1, 0]), c="сколько ни увеличивай — снова дрожь")
        jh, _, _ = noise(-4.6, 4.6, 1.5, 0.15, 70, 5, C_NOISE, 3)
        jw, _, _ = noise(-4.6, 4.6, -1.7, 0.15, 70, 7, C_NOISE, 3)
        self.show(jh, jw, line([-5.6, -0.1, 0], [5.6, -0.1, 0], C_AXIS, 3), tx("высота — от шума", 24, C_BET).move_to([0, 2.8, 0]),
                  tx("вес — от такого же шума", 24, C_AXIS).move_to([0, -0.65, 0]), c="и высоту, и вес даёт такая линия")


class A16(Board):
    def construct(self):
        j, xs, ys = noise(-4.0, 4.0, 0.4, 0.25, 40, 13, C_NOISE, 4)
        self.show(j, line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4), piece(-0.6, 0.6, C_AXIS, -1.3), tx("где в куске делать замер?", 30, WHITE).move_to([0, 2.5, 0]), c="в какой точке куска брать высоту")
        self.show(j, line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4), piece(-0.6, 0.6, C_AXIS, -1.3), marker(-0.6, 0.0, C_BAD), marker(0.6, 0.0, C_SUM), tx("левый край", 22, C_BAD).move_to([-1.6, -1.75, 0]), tx("правый край", 22, C_SUM).move_to([1.7, -1.75, 0]),
                  line([-0.6, -1.3, 0], [-0.6, 0.0, 0], C_BAD, 2, True), line([0.6, -1.3, 0], [0.6, 0.0, 0], C_SUM, 2, True), c="у куска два края: левый и правый")
        bl = Rectangle(width=2.0, height=1.9).set_stroke(C_BAD, 3).set_fill(C_BAD, 0.3).move_to([-2.5, -0.35, 0])
        br = Rectangle(width=2.0, height=2.0).set_stroke(C_SUM, 3).set_fill(C_SUM, 0.3).move_to([2.5, -0.3, 0])
        self.show(bl, br, tx("слева", 24, C_BAD).move_to([-2.5, 1.0, 0]), tx("справа", 24, C_SUM).move_to([2.5, 1.0, 0]), tx("=", 90, C_SUM).move_to([0, -0.3, 0]), tx("гладкий график: почти одно и то же", 24, WHITE).move_to([0, 2.4, 0]), c="гладкий график: суммы совпадают")
        bl2 = Rectangle(width=2.0, height=0.9).set_stroke(C_BAD, 3).set_fill(C_BAD, 0.3).move_to([-2.5, -0.85, 0])
        br2 = Rectangle(width=2.0, height=2.1).set_stroke(C_SUM, 3).set_fill(C_SUM, 0.3).move_to([2.5, -0.25, 0])
        self.show(bl2, br2, tx("≠", 90, C_BAD).move_to([0, -0.3, 0]), tx("4,5", 30, C_BAD).move_to([-2.5, 0.3, 0]), tx("5,5", 30, C_SUM).move_to([2.5, 1.1, 0]), tx("шум: суммы расходятся, тоньше — не помогает", 24, WHITE).move_to([0, 2.4, 0]),
                  c="шум: суммы расходятся и при тонких столбиках")
        self.show(pill("пункт про высоту", C_BET, 40).move_to([0, 0.6, 0]), cross(C_BAD, 0.6).move_to([0, -0.9, 0]), tx("придётся переписать", 28, WHITE).move_to([0, -1.9, 0]), c="договор нарушен")


class A17(Board):
    def construct(self):
        j, xs, ys = noise(-4.0, 4.0, 0.4, 0.25, 40, 13, C_NOISE, 4)
        ax = line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4)
        self.show(j, ax, piece(-0.6, 0.6, C_AXIS, -1.3), marker(-0.6, 0.0, C_BAD), tx("левый край", 22, C_BAD).move_to([-1.6, -1.75, 0]), plaque("1944", "Ито", WHITE, 0, 2.65), c="Ито: высоту берём на левом краю")
        fut = Rectangle(width=4.0, height=3.2).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.12).move_to([2.6, 0.2, 0])
        self.show(poly_line([[x, y, 0] for x, y in zip(xs[xs < -0.5], ys[xs < -0.5])], C_NOISE, 5), ax, fut, lock(0.9, 1.9, C_BAD), tx("будущее", 24, C_NOTE).move_to([2.6, 0.2, 0]), tx("прошлое известно", 24, C_NOISE).move_to([-2.4, 1.8, 0]),
                  c="высота известна заранее: в будущее не подглядываем")
        self.show(scales(C_SUM).scale(1.4).move_to([-1.4, 0.2, 0]), tablo("0").scale(1.8).move_to([2.8, 0.2, 0]), tx("если шум случаен, в среднем ноль", 26, WHITE).move_to([0, 2.2, 0]), c="сумма честная — в среднем ноль")
        self.show(tx("шум", 30, C_NOISE).move_to([-4.6, 1.0, 0]), tx("→", 40, WHITE).move_to([-3.4, 1.0, 0]), tx("квадрат шума", 30, WHITE).move_to([-0.8, 1.0, 0]),
                  pill("обычное правило: только часть ответа", C_BET, 24).move_to([0, -0.4, 0]), c="возьмём от шума квадрат")
        self.show(pill("обычное правило", C_BET, 28).move_to([-3.2, 0.5, 0]), tx("+", 50, WHITE).move_to([-0.8, 0.5, 0]), pill("добавка", C_ADD, 28).move_to([1.6, 0.5, 0]),
                  tx("добавка — от дрожи шума", 24, C_NOISE).move_to([1.6, -0.4, 0]), c="остальное — добавка")


class A18(Board):
    def construct(self):
        j, xs, ys = noise(-4.0, 4.0, 0.4, 0.25, 40, 13, C_NOISE, 4)
        ax = line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4)
        self.show(j, ax, piece(-0.6, 0.6, C_AXIS, -1.3), marker(-0.6, 0.0, C_BAD), tx("левый край", 22, C_BAD).move_to([-1.6, -1.75, 0]), tx("физикам нужны школьные правила пересчёта", 26, WHITE).move_to([0, 2.5, 0]), c="физикам левый край неудобен")
        self.show(j, ax, piece(-0.6, 0.6, C_AXIS, -1.3), marker(0.0, 0.0, C_SUM), tx("середина", 22, C_SUM).move_to([0.0, -1.75, 0]), plaque("1963–66", "Фиск и Стратонович", WHITE, 0, 2.65), c="Фиск и Стратонович взяли середину куска")
        self.show(pill("обычное правило", C_BET, 30).move_to([0, 0.6, 0]), tx("✓", 80, C_SUM).move_to([0, -0.8, 0]), tx("добавки нет", 28, WHITE).move_to([0, -1.9, 0]), c="с серединой добавки нет")
        a, b = pill("сумма Ито", C_NOISE, 28).move_to([-3.2, 0.5, 0]), pill("сумма Стратоновича", C_NOISE, 28).move_to([3.2, 0.5, 0])
        self.show(a, b, darrow(a.get_right() + RIGHT * 0.15, b.get_left() + LEFT * 0.15, C_BET), pill("+ добавка", C_ADD, 24).move_to([0, 1.3, 0]), c="одну сумму можно перевести в другую")
        jj, _, _ = noise(-5.5, 5.5, 0.4, 0.3, 90, 11, C_NOISE, 4)
        self.show(jj, pill("запись Ито", C_NOISE, 24).move_to([-3.2, -1.4, 0]), pill("запись Стратоновича", C_NOISE, 24).move_to([3.2, -1.4, 0]), Arrow([-3.2, -1.0, 0], [-1.5, 0.0, 0], buff=0).set_color(C_NOTE),
                  Arrow([3.2, -1.0, 0], [1.5, 0.0, 0], buff=0).set_color(C_NOTE), c="обе записи описывают одну линию шума")


class A19(Board):
    def construct(self):
        jr, _, _ = noise(-5.5, 5.5, 0.4, 0.28, 240, 29, C_NOISE, 3)
        self.show(jr, tx("шум грубее", 36, C_NOISE).move_to([0, 2.4, 0]), c="бывает шум ещё грубее")
        self.show(jr, marker(-1.0, -0.8, C_BAD), marker(0.2, -0.8, C_SUM), tx("левый край", 20, C_BAD).move_to([-1.6, -1.6, 0]), tx("середина", 20, C_SUM).move_to([0.9, -1.6, 0]), cross(C_BAD, 0.35).move_to([-1.0, -0.4, 0]), cross(C_BAD, 0.35).move_to([0.2, -0.4, 0]),
                  tx("надёжной суммы нет", 28, C_BAD).move_to([0, 2.4, 0]), c="ни край, ни середина не дают надёжной суммы")
        sp = VMobject().set_points_smoothly([np.array([0.6 * np.cos(t) * (1 - t / 14), 0.6 * np.sin(t) * (1 - t / 14), 0.0]) for t in np.linspace(0, 12, 60)]).set_stroke(C_ADD, 4).set_fill(opacity=0)
        self.show(jr.copy().scale(0.6).move_to([0, -0.8, 0]), sp.move_to([0, 1.2, 0]), portrait("Лайонс", "1998", WHITE, 1.0).move_to([-3.8, 1.8, 0]), tx("подсказка: как шум закручивается", 24, C_ADD).move_to([2.6, 1.6, 0]),
                  c="Лайонс: добавим к шуму подсказку")
        self.show(jr.copy().scale(0.6).move_to([-3.0, 0.3, 0]), sp.copy().scale(0.7).move_to([-3.0, 1.5, 0]), tx("→", 50, WHITE).move_to([0, 0.4, 0]), tablo("число").scale(1.8).move_to([3.4, 0.4, 0]),
                  c="с подсказкой сумма определена для каждой линии")
        self.show(portrait("Хайрер", "2014", WHITE, 1.4).move_to([-2.6, 0.4, 0]), VGroup(Circle(radius=0.7).set_stroke(C_BET, 5).set_fill(C_BET, 0.2), tx("★", 50, C_BET)).move_to([2.6, 0.7, 0]),
                  tx("Филдсовская премия", 26, C_BET).move_to([2.6, -0.5, 0]), c="Хайрер получил Филдсовскую премию")


class A20(Board):
    def construct(self):
        self.show(portrait("Ито", "1944", WHITE, 1.3).move_to([0, -1.2, 0]), *[Arrow([0.0, -0.4, 0], [x, 1.5, 0], buff=0.05).set_stroke(C_NOTE, 3) for x in (-4.2, -1.4, 1.4, 4.2)],
                  *[tx(t, 22, col).move_to([x, 1.95, 0]) for t, col, x in (("скачки", C_SUM, -4.2), ("будущее", C_SUM, -1.4), ("вся история", C_BET, 1.4), ("граница", C_BAD, 4.2))],
                  c="от Ито пути расходятся")
        jj, xs, ys = noise(-5, -0.6, 0.2, 0.25, 30, 41, C_NOISE, 4)
        self.show(jj, poly_line([[-0.6, ys[-1], 0], [-0.6, ys[-1] + 1.3, 0]], C_BAD, 5), tx("скачок", 24, C_BAD).move_to([0.5, 1.0, 0]), Arrow([1.0, 0.4, 0], [2.2, 0.4, 0], buff=0).set_color(WHITE),
                  curve_of(lambda x: 1.3 / (1 + np.exp(-9 * x)), -0.6, 0.6, -0.3, C_SUM, 5, 30).move_to([3.4, 0.4, 0]), tx("быстрое непрерывное движение (Маркус)", 22, C_SUM).move_to([1.8, -1.3, 0]), c="скачок как быстрое непрерывное движение")
        self.show(big_bar(0, -1.5, 2.6, 1.6, 0.4, 0.0), lock(1.9, 0.5, C_SUM), tx("открыт", 22, C_SUM).move_to([1.9, -0.1, 0]), pill("в среднем 0 — как раньше", C_SUM, 24).move_to([0, 2.2, 0]),
                  tx("Скороход, Маллявэн", 22, WHITE).move_to([0, -2.2, 0]), c="столбик знает будущее, сумма остаётся честной")
        j2, xs2, ys2 = noise(-5, 1.0, 0.0, 0.25, 40, 43, C_NOISE, 4)
        self.show(j2, line([-5, -0.9, 0], [1.0, -0.9, 0], C_PRICE, 6), bar_w(1.0, 0.7, 1.4, -1.6, C_BET), tx("высота зависит от всей истории (Конт, Фурнье)", 24, C_BET).move_to([0, 2.2, 0]), c="высота — от всей истории линии")
        fam = RoundedRectangle(width=7.0, height=2.6, corner_radius=0.3).set_stroke(C_NOISE, 3).move_to([-1.0, 0.5, 0])
        self.show(fam, tx("шумы, по которым можно считать", 24, C_NOISE).move_to([-1.0, 0.5, 0]), cross(C_BAD, 0.45).move_to([4.6, 0.5, 0]), tx("шире нельзя (Бихтелер, Деллашери)", 24, C_BAD).move_to([0, -1.5, 0]), c="граница: шире шумы — счёта нет")


class A21(Board):
    def construct(self):
        N = 5
        hs = np.linspace(0, H, N + 1)
        xk = lambda h: 5.0 * np.sqrt(max(0.0, 1 - h / H))
        layers = lambda col, op: VGroup(*[Rectangle(width=2 * xk(hs[k]), height=hs[k + 1] - hs[k]).set_stroke(col, 2).set_fill(col, op).move_to([0, AY + (hs[k] + hs[k + 1]) / 2, 0]) for k in range(N)])
        self.show(axis_(), hill(C_PRICE, 3), layers(C_BET, 0.35), tx("сложить слои — как?", 30, C_ADD).move_to([0, 2.6, 0]), c="пункт про сложение")
        a = Square(side_length=1.2).set_stroke(C_BET, 3).set_fill(C_BET, 0.3).move_to([-3.0, 0.4, 0]); b = Square(side_length=1.2).set_stroke(C_AXIS, 3).set_fill(C_AXIS, 0.3).move_to([-1.2, 0.4, 0])
        u = Rectangle(width=3.0, height=1.2).set_stroke(C_ADD, 3).move_to([3.0, 0.4, 0])
        self.show(a, b, tx("+", 40, WHITE).move_to([-2.1, 0.4, 0]), tx("≠", 60, C_BAD).move_to([0.9, 0.4, 0]), u, tx("целое", 24, C_ADD).move_to([3.0, 0.4, 0]), tx("выбор по нескольким критериям", 24, WHITE).move_to([0, 2.2, 0]),
                  c="целое бывает не равно сумме частей")
        self.show(axis_(), hill(C_PRICE, 3), layers(C_ADD, 0.3), tx("особая мера слоя: интегралы Шоке и Сугено", 26, C_ADD).move_to([0, 2.6, 0]), c="слои измеряют особой мерой")
        shape = VGroup(Rectangle(width=4.0, height=2.0).set_stroke(C_ADD, 3).set_fill(C_ADD, 0.2), Circle(radius=0.4).set_stroke(C_BAD, 3).set_fill("#0f1115", 1).shift(LEFT * 0.9), Circle(radius=0.4).set_stroke(C_BAD, 3).set_fill("#0f1115", 1).shift(RIGHT * 0.9))
        self.show(shape.move_to([-2.4, 0.4, 0]), tx("куски − дыры", 28, C_ADD).move_to([-2.4, -1.2, 0]), tx("эйлерова характеристика", 24, WHITE).move_to([-2.4, 2.0, 0]),
                  *[Dot([x, y, 0], radius=0.12).set_color(C_SUM) for x, y in ((2.2, 1.0), (3.6, 0.2), (4.8, 1.2))], tx("считаем цели, которые видят датчики", 22, C_SUM).move_to([3.6, -0.8, 0]), c="эйлерова характеристика считает куски минус дыры")
        self.show(*[portrait(n, "", WHITE, 0.9).move_to([x, 1.2, 0]) for n, x in (("Концевич", -4.0), ("Денеф", -1.3), ("Лёзер", 1.4))], plaque("1995–98", "мера на пространстве кривых", WHITE, 0, -1.0), c="мера на пространстве кривых")


class A22(Board):
    def construct(self):
        self.show(*[pill(t, col, 26).move_to([x, 0.6, 0]) for t, col, x in (("память", C_ADD, -4.2), ("произведение", C_ADD, 0.0), ("шкала времени", C_ADD, 4.2))], tx("другие сложения", 34, WHITE).move_to([0, 2.4, 0]), c="совсем другие сложения")
        bs = VGroup(*[Rectangle(width=0.8, height=1.4).set_stroke(C_ADD, 2).set_fill(C_ADD, 0.15 + 0.1 * i).move_to([-3.5 + i * 1.0, -0.8, 0]) for i in range(8)])
        self.show(bs, tx("недавнее прошлое весит больше далёкого", 24, WHITE).move_to([0, 1.4, 0]), tx("дробный интеграл", 26, C_ADD).move_to([0, 2.4, 0]), c="дробный интеграл — сумма с памятью")
        self.show(*[Rectangle(width=1.0, height=1.2).set_stroke(C_BET, 2).set_fill(C_BET, 0.3).move_to([-4.0 + i * 2.0, 0.2, 0]) for i in range(5)],
                  *[tx("×", 40, C_ADD).move_to([-3.0 + i * 2.0, 0.2, 0]) for i in range(4)], plaque("1887", "Вольтерра", WHITE, 0, 2.5), c="Вольтерра перемножал столбики")
        tl = VGroup(line([-5.0, 0.0, 0], [-0.5, 0.0, 0], C_ADD, 6), *[Dot([x, 0.0, 0], radius=0.1).set_color(C_ADD) for x in (1.0, 2.0, 3.2, 4.0, 5.0)])
        self.show(tl, tx("сплошная ось", 22, C_ADD).move_to([-2.7, -0.6, 0]), tx("отдельные точки", 22, C_ADD).move_to([3.0, -0.6, 0]), plaque("1988", "Хильгер", WHITE, 0, 2.5), c="шкала времени — и сплошная, и из точек")


def node(s, x, y, color, w=3.0):
    t = tx(s, 20, color)
    return VGroup(RoundedRectangle(width=max(w, t.get_width() + 0.4), height=0.7, corner_radius=0.12).set_stroke(color, 2).set_fill("#0f1115", 1), t).move_to([x, y, 0])


def tree(labels=True):
    g = VGroup(node("договор", 0, -2.0, WHITE, 1.8))
    xs, names, cols = [-5.0, -1.7, 1.6, 4.9], ["график: слои, приближения", "ось: вес, шум, подсказка", "высота: левый край, середина", "сложение: другие меры"], [C_PRICE, C_AXIS, C_BET, C_ADD]
    for x, n, c in zip(xs, names, cols):
        g.add(Arrow([0.0 + 0.4 * np.sign(x), -1.6, 0], [x, 0.3, 0], buff=0.05).set_stroke(C_NOTE, 3))
        g.add(node(n, x, 0.8, c, 3.2) if labels else Dot([x, 0.8, 0]).set_color(c))
    return g


class A23(Board):
    def construct(self):
        self.show(tx("Как посчитать площадь так, чтобы ответ", 34).move_to([0, 2.6, 0]), tx("не зависел от способа счёта?", 34).move_to([0, 1.9, 0]),
                  hill(), axis_(), bars(12, 0.4), c="возвращаемся к вопросу")
        self.show(tree(False), tx("способы растут деревом", 28, WHITE).move_to([0, 2.5, 0]), c="единого способа нет — договор переписывали по пунктам")
        self.show(tree(True), c="четыре пункта — четыре ветви")
        self.show(pill("гладкая ширина — Риман", C_BET, 28).move_to([-3.4, 0.9, 0]), pill("случайная — Ито", C_NOISE, 28).move_to([3.4, 0.9, 0]), tx("а дальше — смотря какая задача", 34, WHITE).move_to([0, -0.7, 0]),
                  c="какой способ взять, зависит от задачи")


# ============================== приложение ==============================
def card3(name, formula, note_, color=C_BET):
    r = RoundedRectangle(width=3.8, height=3.6, corner_radius=0.15).set_stroke(color, 2).set_fill("#0f1115", 1)
    return VGroup(r, tx(name, 28, color).move_to(r.get_top() + DOWN * 0.45), tx(formula, 20).move_to(r.get_center() + UP * 0.15), tx(note_, 18, C_NOTE).move_to(r.get_bottom() + UP * 0.55))


class F01(Board):
    def construct(self):
        self.show(title2("образ → формула"), bars_of(F, 8, -4.0, -0.5, -0.6, C_BET, 0.35).scale(0.5, about_point=ORIGIN).move_to([-3.0, 0.4, 0]), Arrow(LEFT, RIGHT, buff=0).move_to([0.0, 0.4, 0]), tx("Σ", 60, C_SUM).move_to([2.0, 0.4, 0]))
        self.show(card3("Риман", "Σ значение в точке × ширина", "≈ столбики", C_BET).move_to([-2.2, 0.2, 0]), tx("предел при дроблении", 20, C_NOTE).move_to([-2.2, -2.2, 0]))
        self.show(card3("Лебег", "Σ высота слоя × мера слоя", "≈ слои", C_BET).move_to([2.2, 0.2, 0]), tx("предел по приближениям", 20, C_NOTE).move_to([2.2, -2.2, 0]))


class F02(Board):
    def construct(self):
        self.show(title2("то же для веса"), card3("Стилтьес", "Σ значение × приращение веса", "≈ шкала веса", C_PRICE).move_to([0, 0.0, 0]))
        self.show(card3("Ито", "значение в левой точке", "≈ замок на будущем", C_NOISE).move_to([0, 0.2, 0]))
        self.show(card3("Стратонович", "среднее по краям, правила обычные", "≈ середина", C_NOISE).move_to([0, 0.2, 0]))
        a, b = pill("Ито", C_NOISE, 28).move_to([-3.0, 0.4, 0]), pill("Стратонович", C_NOISE, 28).move_to([3.0, 0.4, 0])
        self.show(a, b, Arrow(a.get_right() + RIGHT * 0.1, b.get_left() + LEFT * 0.1, buff=0).set_color(C_BET), pill("+ добавка", C_BET, 24).move_to([0, 1.2, 0]))
        rows = [("Риман", "площадь"), ("Лебег", "пределы, рваный график"), ("Стилтьес", "неровная ширина"), ("Ито", "случайная ширина"), ("Стратонович", "привычные правила"), ("Лайонс", "грубая ширина")]
        g = VGroup(*[VGroup(tx(a_, 22, WHITE), tx(b_, 22, C_NOTE)).arrange(RIGHT, buff=0.6) for a_, b_ in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([-1.5, 0.0, 0])
        self.show(title2("что чинили"), g, tx("где применяют: вероятность, финансы, физика шума", 22, C_SUM).move_to([0, -2.4, 0]))
