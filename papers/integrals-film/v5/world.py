"""Мир ролика «Как сложить бесконечно много столбиков»: холм-парабола, ось, столбики, прыгающий график, шум, сквозные сущности.
Общие элементы раскадровки (storyboard.py) и сцен с анимацией (scenes.py). У элементов-героев есть метка .tag: сцена по ней
узнаёт «тот же объект» в соседних кадрах и превращает его, а не рисует заново."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(HERE))
import numpy as np
from manimlib import *
from manimkit import *
from kit import *


def tagged(m, t):
    m.tag = t
    return m


# ---------- мир: холм-парабола над осью ----------
AY, XL, XR, H = -1.5, -5.0, 5.0, 3.0
F = lambda x: H * (1 - (x / 5.0) ** 2)          # герой: холм-парабола, площадь под ним 20


def pt(x, y=0.0):
    return np.array([x, AY + y, 0.0])


def hill(color=C_PRICE, w=5, x0=XL, x1=XR, n=100):
    return tagged(poly_line([pt(x, F(x)) for x in np.linspace(x0, x1, n)], color, w), 'hill')


def axis_(label=True, color=C_AXIS):
    g = VGroup(line([-5.8, AY, 0], [5.8, AY, 0], color, 4))
    if label:
        g.add(tx("ось", 22, color).move_to([5.35, AY - 0.35, 0]))
    return tagged(g, 'axis')


def vaxis():
    return VGroup(line([-5.8, AY, 0], [-5.8, AY + 3.2, 0], C_BET, 3), tx("высота", 20, C_BET).move_to([-5.0, AY + 3.45, 0]))


def area(color=C_PRICE, op=0.18):
    return tagged(area_of(F, XL, XR, AY, color, op), 'fill')


def bars(n, op=0.45, x0=XL, x1=XR):
    return tagged(bars_of(F, n, x0, x1, AY, C_BET, op), 'bars')


def cuts(n):
    return tagged(VGroup(*[line([x, AY, 0], [x, AY + F(x), 0], C_NOTE, 1.5, dashed=True) for x in np.linspace(XL, XR, n + 1)]), 'cuts')


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
    return tagged(VGroup(*ds), 'dots'), xs, up


def one_zero_marks(x=-5.8, y0=AY, hi=2.0):
    return VGroup(tx("1", 24, C_BET).move_to([x, y0 + hi, 0]), tx("0", 24, C_BET).move_to([x, y0, 0]),
                  line([x + 0.35, y0 + hi, 0], [x + 0.55, y0 + hi, 0], C_BET, 2), line([x + 0.35, y0, 0], [x + 0.55, y0, 0], C_BET, 2))


def noise(x0=-5.0, x1=5.0, y=0.0, amp=0.25, n=70, seed=11, color=C_NOISE, w=3):
    """Дрожащая линия в полосе y ± 4·amp: блуждание, растянутое по высоте; чем больше n, тем она грубее."""
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, n)
    b = np.cumsum(rng.normal(0, 1, n))
    ys = y + (b - (b.max() + b.min()) / 2) * (8 * amp / (b.max() - b.min()))
    return tagged(poly_line([[x, v, 0] for x, v in zip(xs, ys)], color, w), 'noise'), xs, ys


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


# сцена → список (с какого кадра, состояние сквозных сущностей); LABELS: имя сущности остаётся под ней с первого кадра введения до конца сцены
STATE = {
    "A04": [(3, S(tablo="Σ")), (4, S(tablo="20,02")), (5, S(tablo="20"))],
    "A07": [(1, S(tablo="Σ")), (4, S(tablo="20"))],
    "A08": [(1, S([], None, "Σ")), (2, S(["график"], None, "Σ")), (3, S(["ось"], None, "Σ")), (4, S(["высота"], None, "Σ")),
            (5, S(["сложение"], None, "Σ")), (6, S("all", "=", "20"))],
    "A09": [(1, S(["ось"], "=", "Σ")), (6, S(["ось"], "=", "Σ", 1))],
    "A10": [(1, S(["график"], "=", "Σ", 1)), (5, S(["график"], "=", "?", 1))],
    "A11": [(1, S(["высота"], "=", "?", 1)), (5, S(["высота"], "≠", "?", 1))],
    "A12": [(1, S(["высота"], "≠", "?", 1)), (3, S(["высота"], "=", "Σ", 1)), (5, S(["высота"], "=", "20", 2))],
    "A13": [(1, S(["высота"], "=", "Σ", 2)), (5, S(["высота"], "=", "0", 2))],
    "A14": [(1, S(["высота"], "=", "Σ", 2)), (5, S(["высота"], "=", "Σ", 3))],
    "A15": [(1, S(["график", "ось"], "=", "?", 3))],
    "A16": [(1, S(["высота"], "=", "Σ", 3)), (4, S(["высота"], "≠", "?", 3))],
    "A17": [(1, S(["высота"], "≠", None, 3)), (2, S(["высота"], "=", None, 3)), (5, S(["высота"], "=", None, 4))],
    "A18": [(1, S(["ось"], "=", "Σ", 4)), (3, S(["ось"], "=", "Σ", 5))],
    "A19": [(1, S(["высота"], "=", None, 5)), (5, S(["высота"], "=", None, 6))],
    "A20": [(1, S(["ось"], "≠", "?", 6)), (3, S(["ось"], "=", "число", 6)), (5, S(["ось"], "=", "число", 7))],
    "A21": [(1, S(["высота"], "=", "Σ", 7)), (5, S(["высота"], "=", "Σ", 8))],
    "A22": [(1, S(["сложение"], "=", "Σ", 8)), (5, S(["сложение"], "=", "Σ", 9))],
    "A23": [(1, S(["сложение"], "=", "Σ", 9))],
    "A24": [(1, S("all", "=", "Σ")), (2, S("all"))],
}
LABELS = {"A04": {"tablo": 3}, "A08": {"lamps": 1, "twins": 6}, "A09": {"sprout": 6}}


def state_for(code, k):
    st = None
    for frm, s in STATE.get(code, []):
        if k >= frm:
            st = s
    return st




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




def card3(name, formula, note_, color=C_BET):
    r = RoundedRectangle(width=3.8, height=3.6, corner_radius=0.15).set_stroke(color, 2).set_fill("#0f1115", 1)
    return VGroup(r, tx(name, 28, color).move_to(r.get_top() + DOWN * 0.45), tx(formula, 20).move_to(r.get_center() + UP * 0.15), tx(note_, 18, C_NOTE).move_to(r.get_bottom() + UP * 0.55))


