"""Значки станций — единый набор: линейный белый знак в круге своего цвета.
Активная станция — круг залит цветом, знак тёмный; пройденная — цветное кольцо, знак цветной; будущая — серое кольцо.
Одни и те же значки — в полосе «мы здесь» (film_bar), в обзоре и на карточках приложения."""
import numpy as np
from manimlib import *

INK = "#0f1115"
COLOR = {"Вопрос": "#ffffff", "Обзор": "#ffffff", "Все составы": "#e3b341", "Формула": "#d2a8ff", "Глушков": "#58a6ff",
         "Худшая станция": "#f0883e", "Проверка": "#e3b341", "Итог": "#3fb950", "Как устроено": "#d2a8ff"}
W = 4  # толщина линий знака


def _train():
    body = RoundedRectangle(width=0.62, height=0.3, corner_radius=0.05)
    wheels = VGroup(*[Circle(radius=0.06).move_to([x, -0.2, 0]) for x in (-0.18, 0.18)])
    rail = Line([-0.4, -0.29, 0], [0.4, -0.29, 0])
    return VGroup(body, wheels, rail)


def _metronome():
    body = Polygon([-0.22, -0.3, 0], [0.22, -0.3, 0], [0.08, 0.32, 0], [-0.08, 0.32, 0])
    arm = Line([0, -0.2, 0], [0.2, 0.3, 0])
    return VGroup(body, arm, Dot([0.13, 0.12, 0], radius=0.04))


def _ring():
    return VGroup(Circle(radius=0.27), Circle(radius=0.17), RoundedRectangle(width=0.22, height=0.12, corner_radius=0.03).move_to([0, 0.22, 0]))


def _tower():
    floors = VGroup(*[Line([-w, y, 0], [w, y, 0]) for w, y in ((0.3, -0.28), (0.22, -0.1), (0.14, 0.08), (0.06, 0.26))])
    return VGroup(floors, Line([0, -0.28, 0], [0, 0.34, 0]))


def _compass():
    ring = Circle(radius=0.28)
    a = rotate_vector(UP, -PI / 5)
    side = rotate_vector(a, PI / 2) * 0.07
    needle = Polygon(a * 0.24, side, -a * 0.24, -side)
    return VGroup(ring, needle)


def _check():
    return VGroup(VMobject().set_points_as_corners([[-0.24, 0.0, 0], [-0.07, -0.18, 0], [0.26, 0.2, 0]]))


def _gear():
    teeth = VGroup(*[Line(0.2 * np.array([np.cos(a), np.sin(a), 0]), 0.3 * np.array([np.cos(a), np.sin(a), 0])) for a in np.arange(8) * TAU / 8])
    return VGroup(Circle(radius=0.2), Circle(radius=0.08), teeth)


def _question():
    return Text("?", font="Arial", font_size=40)


def _grid():
    return VGroup(*[Square(0.14) for _ in range(6)]).arrange_in_grid(2, 3, buff=0.06)


GLYPH = {"Вопрос": _question, "Обзор": _grid, "Все составы": _train, "Формула": _metronome, "Глушков": _ring,
         "Худшая станция": _tower, "Проверка": _compass, "Итог": _check, "Как устроено": _gear}


def badge(name, state="active", s=1.0):
    """Значок станции. state: active — залит цветом; done — цветное кольцо; future — серое кольцо."""
    col = COLOR.get(name, "#ffffff")
    ring = Circle(radius=0.42)
    g = GLYPH[name]()
    if state == "active":
        ring.set_stroke(col, 3).set_fill(col, 1)
        g.set_stroke(INK, W).set_fill(opacity=0) if not isinstance(g, Text) else g.set_color(INK)
    elif state == "done":
        ring.set_stroke(col, 3).set_fill(INK, 0.9)
        g.set_stroke(col, W).set_fill(opacity=0) if not isinstance(g, Text) else g.set_color(col)
    else:
        ring.set_stroke("#8b949e", 2).set_fill(INK, 0.8)
        g.set_stroke("#8b949e", W * 0.8).set_fill(opacity=0) if not isinstance(g, Text) else g.set_color("#8b949e")
    if isinstance(g, VGroup):
        for m in g.get_family():
            if isinstance(m, Dot):
                m.set_fill(m.get_stroke_color(), 1)
    return VGroup(ring, g.move_to(ring)).scale(s)


def film_bar(stations, active, y=-3.35):
    """Полоса «мы здесь» для фильма: значки в кругах и подписи, на тёмной подложке; текущая — крупнее и подписана белым."""
    xs = np.linspace(-6.1, 6.1, len(stations))
    g = VGroup()
    line = Line([xs[0], y, 0], [xs[-1], y, 0]).set_stroke("#8b949e", 2, opacity=0.6)
    done = Line([xs[0], y, 0], [xs[active], y, 0]).set_stroke(WHITE, 3)
    g.add(line, done)
    for i, (x, name) in enumerate(zip(xs, stations)):
        state = "active" if i == active else "done" if i < active else "future"
        b = badge(name, state, 0.62 if i == active else 0.46).move_to([x, y, 0])
        lab = Text(name, font="Arial", font_size=19 if i == active else 16)
        lab.set_color(WHITE if i == active else "#c9d1d9" if i < active else "#8b949e").next_to(b, DOWN, buff=0.07)
        g.add(b, lab)
    bg = RoundedRectangle(width=13.4, height=1.15, corner_radius=0.2).set_stroke(width=0).set_fill(INK, 0.72).move_to([0, y - 0.16, 0])
    return VGroup(bg, g)
