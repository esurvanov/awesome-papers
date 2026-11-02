"""Мир ролика «Как сложить бесконечно много столбиков», версия 6: горка над осью и всё, что на ней строится.
Помощники закрывают классы дефектов из разбора № 51 (PLAYBOOK, законы 29–35):
  • одна геометрия на всё: горка F, ось 0…10, числа на экране считаются из того же рисунка (psum, area_to, archimedes_steps);
  • крупный план — это увеличенный кусок той же картинки (zoom), а не отдельный рисунок: верх столбика всегда на горке;
  • размерные стрелки — на выносных пунктирах и не пересекают данные (dim_v, dim_h);
  • подпись — никогда не на заливке (label ставит рядом или на тёмной плашке);
  • порядок слоёв по типу: заливки → столбики → ось → горка → точки → подписи (z_index в помощниках);
  • связь двух панелей — общий цвет и пунктир (link).
Координаты: ось лежит на y = AY, деление оси u ∈ [0, 10] стоит в x = u − 5. Горка: высота F(u) = 3·u·(10 − u)/25, площадь 20."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(HERE))
import numpy as np
from manimlib import *
from manimkit import *
from kit import C_PRICE, C_BET, C_SUM, C_NOISE, C_BAD, C_NOTE, C_AXIS, C_ADD, line, poly_line

__all__ = [
    "C_PRICE", "C_BET", "C_SUM", "C_NOISE", "C_BAD", "C_NOTE", "C_AXIS", "C_ADD", "C_TEXT", "C_PLATE",
    "AY", "SY", "F", "X", "pt", "tagged", "Z", "z", "line", "poly_line",
    "hill", "fill_between", "axis_", "ticks", "vscale", "cells", "bars", "bar", "psum", "area_to", "zoom", "zoom_bar",
    "dim_v", "dim_h", "label", "plate", "num", "cap", "plaque", "pill", "link", "dot", "marker",
    "tri", "archimedes_tris", "archimedes_steps", "ruler", "panel_lower", "lower_curve", "LOW_Y", "LOW_S",
    "jump", "one_zero", "noise", "lens", "lock", "scales", "node", "rules_row", "RULES", "spiral",
]

AY = -1.6          # ось
SY = 1.0           # единица высоты на экране
from manimkit.annot import Z, z, tagged, C_TEXT, C_PLATE


def F(u):
    return 3.0 * u * (10.0 - u) / 25.0


def X(u):
    return u - 5.0


def pt(u, y=0.0, base=None):
    return np.array([X(u), (AY if base is None else base) + y * SY, 0.0])




# ---------- горка, ось, клетки ----------
def hill(color=C_PRICE, w=6, u0=0.0, u1=10.0, base=None, s=1.0, tag="hill"):
    m = poly_line([pt(u, F(u) * s, base) for u in np.linspace(u0, u1, 120)], color, w)
    return tagged(z(m, "graph"), tag)


def fill_between(u0, u1, color=C_PRICE, op=0.30, base=None, f=None, tag="fill"):
    f = f or F
    us = np.linspace(u0, u1, 80)
    pts = [pt(u0, 0, base)] + [pt(u, f(u), base) for u in us] + [pt(u1, 0, base)]
    m = Polygon(*pts).set_stroke(width=0).set_fill(color, op)
    return tagged(z(m, "fill"), tag)


def axis_(base=None, color=C_AXIS, w=6, u0=-0.6, u1=10.6, tag="axis"):
    m = line(pt(u0, 0, base), pt(u1, 0, base), color, w)
    return tagged(z(m, "axis"), tag)


def ticks(base=None, every=1, labels=(0, 2, 4, 6, 8, 10), size=20):
    g = VGroup()
    for u in range(0, 11, every):
        g.add(line(pt(u, 0, base) + DOWN * 0.08, pt(u, 0, base) + UP * 0.08, C_AXIS, 2))
    for u in labels:
        g.add(tx(str(u), size, C_TEXT).move_to(pt(u, 0, base) + DOWN * 0.42 + RIGHT * (0.18 if u == 0 else 0)))
    return tagged(z(g, "axis"), "ticks")


def vscale(base=None, top=3, size=18, u=-0.9):
    g = VGroup(line(pt(u, 0, base), pt(u, top, base), C_BET, 2))
    for k in range(0, top + 1):
        g.add(line(pt(u, k, base) + LEFT * 0.07, pt(u, k, base) + RIGHT * 0.07, C_BET, 2), tx(str(k), size, C_BET).move_to(pt(u, k, base) + LEFT * 0.3))
    return tagged(z(g, "axis"), "vscale")


def cells():
    """Клетки 1×1 под горкой: целые — внутри фигуры, задетые — пересечённые кривой (A01: 12 и 26)."""
    full, cut = VGroup(), VGroup()
    for u in range(10):
        for k in range(3):
            lo, hi = min(F(u), F(u + 1)), max(F(u), F(u + 1))
            top = F(min(max(5.0, u), u + 1))     # максимум горки на клетке
            sq = Square(side_length=0.96 * SY).move_to(pt(u + 0.5, k + 0.5))
            if k + 1 <= lo:
                full.add(sq.set_stroke(C_SUM, 2).set_fill(C_SUM, 0.35))
            elif k < top:
                cut.add(sq.set_stroke(C_BAD, 2.5).set_fill(opacity=0))
    grid = VGroup(*[line(pt(u, 0), pt(u, 3.2), C_NOTE, 1) for u in range(11)], *[line(pt(0, k), pt(10, k), C_NOTE, 1) for k in range(4)])
    return z(grid, "fill"), tagged(z(full, "bar"), "full"), tagged(z(cut, "bar"), "cut")


# ---------- столбики и суммы (числа на экране — отсюда) ----------
def _sample(u0, u1, pick):
    return {"left": u0, "mid": (u0 + u1) / 2, "right": u1}[pick] if isinstance(pick, str) else u0 + pick * (u1 - u0)


def bar(u0, u1, pick="mid", color=C_BET, op=0.85, base=None, f=None):
    f = f or F
    h = max(f(_sample(u0, u1, pick)), 0.02)
    r = Rectangle(width=(u1 - u0) * 0.97, height=h * SY).set_stroke(color, 2).set_fill(color, op)
    r.move_to(pt((u0 + u1) / 2, h / 2, base))
    return z(r, "bar")


def bars(n=None, edges=None, pick="mid", color=C_BET, op=0.85, base=None, f=None, tag="bars"):
    edges = list(edges) if edges is not None else list(np.linspace(0, 10, n + 1))
    picks = pick if isinstance(pick, (list, tuple)) else [pick] * (len(edges) - 1)
    g = VGroup(*[bar(edges[i], edges[i + 1], picks[i], color, op, base, f) for i in range(len(edges) - 1)])
    return tagged(g, tag)


def psum(n=None, edges=None, pick="mid", f=None):
    f = f or F
    edges = list(edges) if edges is not None else list(np.linspace(0, 10, n + 1))
    picks = pick if isinstance(pick, (list, tuple)) else [pick] * (len(edges) - 1)
    return sum(f(_sample(edges[i], edges[i + 1], picks[i])) * (edges[i + 1] - edges[i]) for i in range(len(edges) - 1))


def area_to(u):
    """Площадь горки от 0 до u (нижний график Ньютона и Лейбница): 0,6u² − u³/25."""
    return 0.6 * u * u - u ** 3 / 25.0


def zoom_bar(u0=4.0, u1=6.0, pick="mid", k=1.5, margin=1.2, center=(0.0, 0.55)):
    """Крупный план одного столбика — увеличенный кусок той же картинки: столбик, кусок горки над ним, кусок оси и точка замера.
    Верх столбика лежит на горке по построению (в точке замера). Возвращает (группа, столбик) — по столбику ставят размеры."""
    b = bar(u0, u1, pick)
    seg = hill(u0=u0 - margin, u1=u1 + margin, tag="hillseg")
    ax = line(pt(u0 - margin - 0.3), pt(u1 + margin + 0.3), C_AXIS, 6)
    su = _sample(u0, u1, pick)
    d = dot(pt(su, F(su)), C_BET, 0.09)
    g = VGroup(b, ax, seg, d)
    about = pt((u0 + u1) / 2, F((u0 + u1) / 2) / 2)
    g.scale(k, about_point=about).shift(np.array([center[0], center[1], 0.0]) - about)
    return tagged(g, "zoom"), b


def zoom(group, about, k):
    """Крупный план той же картинки: копия, увеличенная в k раз вокруг точки about и поставленная в центр кадра."""
    g = group.copy()
    g.scale(k, about_point=np.array(about))
    g.shift(np.array([0.0, 0.3, 0.0]) - np.array(about))
    return g


# ---------- размеры, подписи, числа: из ядра (core/manimkit/annot.py), здесь — только цвета по умолчанию этого ролика ----------
from manimkit import annot as _A
plate, label, num, cap, link, dot, marker, plaque = _A.plate, _A.label, _A.num, _A.cap, _A.link, _A.dot, _A.marker, _A.plaque


def dim_v(edge_x, y0, y1, text, color=C_BET, side=RIGHT, gap=0.6, size=24):
    return _A.dim_v(edge_x, y0, y1, text, color, side, gap, size)


def dim_h(x0, x1, bottom_y, text, color=C_AXIS, gap=0.45, size=24):
    return _A.dim_h(x0, x1, bottom_y, text, color, gap, size)


def pill(s, color=C_BET, size=26):
    return _A.pill(s, color, size)


# ---------- Архимед ----------
def tri(a, b, color, op=0.85):
    """Треугольник Архимеда на хорде горки от u=a до u=b: третья вершина на горке над серединой хорды."""
    c = (a + b) / 2
    return z(Polygon(pt(a, F(a)), pt(b, F(b)), pt(c, F(c))).set_stroke(C_PLATE, 2).set_fill(color, op), "bar")


def archimedes_tris(level, color):
    """Треугольники шага level (1: один большой; 2: два; 3: четыре …)."""
    n = 2 ** (level - 1)
    edges = np.linspace(0, 10, n + 1)
    return VGroup(*[tri(edges[i], edges[i + 1], color) for i in range(n)])


def archimedes_steps(k=6):
    """Площади шагов Архимеда (из той же геометрии): 15, 3,75, 0,94, …; сумма → 20."""
    out = []
    for level in range(1, k + 1):
        n = 2 ** (level - 1)
        e = np.linspace(0, 10, n + 1)
        s = 0.0
        for i in range(n):
            a, b = e[i], e[i + 1]
            c = (a + b) / 2
            p, q, r = np.array([a, F(a)]), np.array([b, F(b)]), np.array([c, F(c)])
            d1, d2 = q - p, r - p
            s += abs(d1[0] * d2[1] - d1[1] * d2[0]) / 2
        out.append(s)
    return out


def ruler(values, colors, y=-2.1, x0=-5.0, unit=0.4, h=0.32):
    """Линейка площадей: полоски длиной пропорционально площади, подряд слева направо."""
    g, x = VGroup(), x0
    for v, c in zip(values, colors):
        w = max(v * unit, 0.02)
        g.add(Rectangle(width=w, height=h).set_stroke(C_PLATE, 1).set_fill(c, 0.95).move_to([x + w / 2, y, 0]))
        x += w
    return z(g, "bar")


# ---------- нижний график (Ньютон и Лейбниц) ----------
LOW_Y, LOW_S = -2.55, 0.06     # база нижней панели и масштаб: 20 единиц площади = 1,2 по высоте


def panel_lower():
    return VGroup(axis_(base=LOW_Y, w=4, tag="axis_low"), tagged(z(VGroup(line(pt(-0.6, 0, LOW_Y), pt(-0.6, 20 * LOW_S, LOW_Y), C_SUM, 2),
                  tx("20", 18, C_SUM).move_to(pt(-0.95, 20 * LOW_S, LOW_Y)), tx("0", 18, C_SUM).move_to(pt(-0.95, 0, LOW_Y))), "axis"), "lowscale"))


def lower_curve(u1=10.0, color=C_SUM, w=5):
    return tagged(z(poly_line([pt(u, area_to(u) * LOW_S, LOW_Y) for u in np.linspace(0, max(u1, 0.05), 80)], color, w), "graph"), "low")


# ---------- прыгающий график, шум ----------
def jump(n=48, hi=2.0, seed=7, r=0.085):
    """Высота 1 в точках-дробях (синие, наверху), 0 в остальных (белые, на оси). Одна точка на место, без разброса по вертикали."""
    rng = np.random.default_rng(seed)
    us = np.sort(rng.uniform(0.2, 9.8, n))
    up = rng.random(n) < 0.5
    ds = VGroup(*[dot(pt(u, hi if b else 0.0), C_PRICE if b else WHITE, r) for u, b in zip(us, up)])
    return tagged(ds, "dots"), us, up


def one_zero(hi=2.0):
    return tagged(z(VGroup(tx("1", 24, C_BET).move_to(pt(-0.9, hi)), tx("0", 24, C_BET).move_to(pt(-0.9, 0))), "label"), "oz")


def noise(u0=0.0, u1=10.0, y=1.4, amp=0.28, n=90, seed=11, color=C_NOISE, w=4, base=None):
    rng = np.random.default_rng(seed)
    us = np.linspace(u0, u1, n)
    b = np.cumsum(rng.normal(0, 1, n))
    ys = y + (b - (b.max() + b.min()) / 2) * (8 * amp / (b.max() - b.min()))
    return tagged(z(poly_line([pt(u, v, base) for u, v in zip(us, ys)], color, w), "graph"), "noise"), us, ys


def lens(p):
    ring = Circle(radius=0.3).set_stroke(WHITE, 4).move_to(p)
    return z(VGroup(ring, line(np.array(p) + np.array([0.21, -0.21, 0]), np.array(p) + np.array([0.5, -0.5, 0]), WHITE, 5)), "ui")


def lock(p, color=C_BAD):
    body = RoundedRectangle(width=0.5, height=0.4, corner_radius=0.06).set_stroke(color, 3).set_fill(color, 0.6).move_to(p)
    arc = Arc(start_angle=0, angle=PI, radius=0.17).set_stroke(color, 3).move_to(np.array(p) + UP * 0.3)
    return z(VGroup(body, arc), "ui")


def scales(color=C_SUM):
    pole = line([0, -0.8, 0], [0, 0.4, 0], WHITE, 3)
    beam = line([-1.2, 0.4, 0], [1.2, 0.4, 0], WHITE, 3)
    pans = VGroup(*[Arc(start_angle=PI, angle=PI, radius=0.4).set_stroke(color, 3).move_to([sx, -0.1, 0]) for sx in (-1.2, 1.2)])
    strings = VGroup(*[line([sx, 0.4, 0], [sx, 0.1, 0], color, 2) for sx in (-1.2, 1.2)])
    return z(VGroup(pole, beam, pans, strings, line([-0.5, -0.8, 0], [0.5, -0.8, 0], WHITE, 3)), "ui")


def spiral(p, color=C_ADD):
    m = VMobject().set_points_smoothly([np.array([0.6 * np.cos(t) * (1 - t / 14), 0.6 * np.sin(t) * (1 - t / 14), 0.0]) for t in np.linspace(0, 12, 60)])
    return z(m.set_stroke(color, 4).set_fill(opacity=0).move_to(p), "ui")


node = _A.node


# ---------- правила счёта: строка сверху с A12 ----------
RULES = [("1 · что складываем", C_PRICE), ("2 · ширина куска", C_AXIS), ("3 · где высота", C_BET), ("4 · как складываем", C_ADD)]


def rules_row(lit=(), y=3.45, size=20):
    g = VGroup()
    for i, (t, c) in enumerate(RULES):
        on = lit == "all" or i in lit
        col = c if on else C_NOTE
        txm = tx(t, size, col)
        r = RoundedRectangle(width=txm.get_width() + 0.35, height=txm.get_height() + 0.24, corner_radius=0.1).set_stroke(col, 3 if on else 1.5).set_fill(C_PLATE, 1)
        g.add(VGroup(r, txm.move_to(r)))
    g.arrange(RIGHT, buff=0.22).move_to([0, y, 0])
    return tagged(z(g, "ui"), "rules")
