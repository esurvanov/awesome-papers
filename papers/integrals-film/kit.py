"""Элементы мира «касса»: игрок, касса с табло, дорожка цены, столбики ставки, полоски, ящики, маркеры края, весы, замок, портреты.
Цвета — только смысловые, из палитры паспорта (C_PRICE дорожка, C_BET ставка, C_SUM итог, C_NOISE шум, C_BAD поломка)."""
import numpy as np
from manimlib import *
from manimkit import *

C_PRICE, C_BET, C_SUM, C_NOISE, C_BAD, C_NOTE = "#3aa6ff", "#ffd23f", "#2ee66b", "#c88bff", "#ff4d5e", "#8b949e"
C_AXIS, C_ADD = "#ff8c1a", "#ff5fb0"   # ось и сложение — пункты договора
X0, X1, BASE = -4.8, 4.8, -1.5   # ось времени: от X0 до X1 на высоте BASE


def title2(s, size=34, color=WHITE):
    return tx(s, size, color).move_to(UP * 3.0)


def lab(s, size=20, color=C_NOTE):
    return tx(s, size, color)


def line(a, b, color=WHITE, w=3, dashed=False):
    m = Line(np.array(a, dtype=float), np.array(b, dtype=float)).set_stroke(color, w)
    return DashedLine(np.array(a, dtype=float), np.array(b, dtype=float)).set_stroke(color, w) if dashed else m


def poly_line(pts, color, w=4):
    m = VMobject()
    m.set_points_as_corners([np.array(p, dtype=float) for p in pts])
    return m.set_stroke(color, w).set_fill(opacity=0)


def axis(x0=X0, x1=X1, y=BASE, name="время"):
    return VGroup(line([x0, y, 0], [x1, y, 0], C_NOTE, 2), lab(name, 18).move_to([x1 - 0.1, y - 0.3, 0]))


def smooth_bet(x):  # гладкая кривая из старой версии (касса); имя «smooth» занято плавностью анимаций manimlib — не затенять (закон 30)
    return 0.9 + 0.55 * np.sin(0.85 * x)


def curve_of(f, x0=X0, x1=X1, y0=BASE, color=C_BET, w=4, n=80):
    xs = np.linspace(x0, x1, n)
    return poly_line([[x, y0 + f(x), 0] for x in xs], color, w)


def bars_of(f, n, x0=X0, x1=X1, y0=BASE, color=C_BET, op=0.45, gap=0.0):
    w = (x1 - x0) / n
    g = VGroup()
    for i in range(n):
        xm = x0 + (i + 0.5) * w
        h = max(0.02, f(xm))
        r = Rectangle(width=w * (1 - gap), height=h).set_stroke(color, 1.5).set_fill(color, op)
        r.move_to([xm, y0 + h / 2, 0])
        g.add(r)
    return g


def strips(n, x0=X0, x1=X1, y0=BASE, y1=2.3):
    w = (x1 - x0) / n
    return VGroup(*[line([x0 + i * w, y0, 0], [x0 + i * w, y1, 0], C_NOTE, 1.5, dashed=True) for i in range(n + 1)])


def ball(x, y, r=0.17):
    return Circle(radius=r).set_stroke(WHITE, 2).set_fill(C_PRICE, 1).move_to([x, y, 0])


def track(x0=-5.5, x1=5.5, y=-1.0, color=C_PRICE):
    return line([x0, y, 0], [x1, y, 0], color, 4, dashed=True)


def stick(x, y, s=1.0, color=WHITE):
    parts = [Circle(radius=0.2 * s).move_to([x, y + 0.6 * s, 0]),
             Line([x, y + 0.4 * s, 0], [x, y - 0.3 * s, 0]), Line([x - 0.32 * s, y + 0.2 * s, 0], [x + 0.32 * s, y + 0.2 * s, 0]),
             Line([x, y - 0.3 * s, 0], [x - 0.22 * s, y - 0.8 * s, 0]), Line([x, y - 0.3 * s, 0], [x + 0.22 * s, y - 0.8 * s, 0])]
    return VGroup(*parts).set_stroke(color, 3).set_fill(opacity=0)


def kassa(s=1.0, value="0"):
    """Касса: прилавок и табло «итог»."""
    counter = RoundedRectangle(width=2.6, height=0.9, corner_radius=0.1).set_stroke(WHITE, 2).set_fill("#0f1115", 1)
    screen = RoundedRectangle(width=2.0, height=0.7, corner_radius=0.08).set_stroke(C_SUM, 2).set_fill(C_SUM, 0.12)
    screen.next_to(counter, UP, buff=0.12)
    txt = tx(value, 28, C_SUM).move_to(screen)
    return VGroup(counter, screen, txt).scale(s)


def portrait(name, years="", color=WHITE, s=1.0):
    c = Circle(radius=0.32).set_stroke(color, 3).set_fill(color, 0.1)
    ini = tx(name[0], 26, color).move_to(c)
    nm = tx(name, 20, color).next_to(c, DOWN, buff=0.12)
    g = VGroup(c, ini, nm)
    if years:
        g.add(tx(years, 16, C_NOTE).next_to(nm, DOWN, buff=0.06))
    return g.scale(s)


def box(label, w=1.8, h=1.3, color=C_BET):
    r = Rectangle(width=w, height=h).set_stroke(color, 3).set_fill(color, 0.08)
    return VGroup(r, lab(label, 20, color).next_to(r, DOWN, buff=0.1))


def dots(n, x0, x1, y0, y1, color=WHITE, seed=1, r=0.05):
    rng = np.random.default_rng(seed)
    return VGroup(*[Dot([rng.uniform(x0, x1), rng.uniform(y0, y1), 0], radius=r).set_color(color) for _ in range(n)])


def marker(x, y, color, tag=""):
    m = Triangle().scale(0.14).rotate(PI).set_stroke(color, 2).set_fill(color, 1).move_to([x, y, 0])
    return VGroup(m, lab(tag, 18, color).next_to(m, UP, buff=0.08)) if tag else m


def lens(x, y):
    ring = Circle(radius=0.3).set_stroke(WHITE, 3).set_fill(opacity=0).move_to([x, y, 0])
    handle = line([x + 0.21, y - 0.21, 0], [x + 0.5, y - 0.5, 0], WHITE, 4)
    return VGroup(ring, handle)


def scales(color=C_SUM):
    pole = line([0, -0.8, 0], [0, 0.4, 0], WHITE, 3)
    beam = line([-1.2, 0.4, 0], [1.2, 0.4, 0], WHITE, 3)
    pans = VGroup(*[Arc(start_angle=PI, angle=PI, radius=0.4).set_stroke(color, 3).move_to([sx, -0.1, 0]) for sx in (-1.2, 1.2)])
    strings = VGroup(*[line([sx, 0.4, 0], [sx, 0.1, 0], color, 2) for sx in (-1.2, 1.2)])
    foot = line([-0.5, -0.8, 0], [0.5, -0.8, 0], WHITE, 3)
    return VGroup(pole, beam, pans, strings, foot)


def lock(x, y, color=C_BAD):
    body = RoundedRectangle(width=0.5, height=0.4, corner_radius=0.06).set_stroke(color, 3).set_fill(color, 0.3).move_to([x, y, 0])
    arc = Arc(start_angle=0, angle=PI, radius=0.17).set_stroke(color, 3).move_to([x, y + 0.3, 0])
    return VGroup(body, arc)


def formula_row(parts, y=0.0, size=26, gap=0.55):
    """Ряд: [картинка или текст] ... — выровнен по центру."""
    items = [p if isinstance(p, Mobject) else tx(p, size) for p in parts]
    return VGroup(*items).arrange(RIGHT, buff=gap).move_to([0, y, 0])


def staircase(xs, ys, y0, color=C_PRICE, w=4):
    pts = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        if i:
            pts.append([x, y0 + ys[i - 1], 0])
        pts.append([x, y0 + y, 0])
    return poly_line(pts, color, w)


def jagged(x0, x1, y, amp, n, seed, color=C_NOISE, w=3):
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, n)
    ys = y + np.cumsum(rng.normal(0, amp, n))
    ys -= np.linspace(ys[0] - y, ys[-1] - y, n)
    return poly_line([[x, v, 0] for x, v in zip(xs, ys)], color, w), xs, ys


def area_of(f, x0=X0, x1=X1, y0=BASE, color=C_SUM, op=0.3, n=80):
    xs = np.linspace(x0, x1, n)
    pts = [[x0, y0, 0]] + [[x, y0 + f(x), 0] for x in xs] + [[x1, y0, 0]]
    m = VMobject()
    m.set_points_as_corners([np.array(p, dtype=float) for p in pts] + [np.array([x0, y0, 0.0])])
    return m.set_stroke(width=0).set_fill(color, op)


def bar_w(x, w, h, y0, color=C_BET, op=0.45):
    return Rectangle(width=w, height=max(h, 0.03)).set_stroke(color, 2).set_fill(color, op).move_to([x, y0 + max(h, 0.03) / 2, 0])
