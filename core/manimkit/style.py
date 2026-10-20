"""Общий стиль роликов: цвета, текст, плашки, значки, базовая сцена."""
import math
import numpy as np
from manimlib import *

FONT = "Arial"
BG = "#0f1115"
C_BLUE, C_GREEN, C_RED, C_YEL, C_GREY = "#58a6ff", "#3fb950", "#f85149", "#e3b341", "#8b949e"


def tx(s, size=30, color=WHITE):
    """Текст. Степени пишутся как x^6, t^−1 — выводятся верхним индексом (LaTeX не нужен)."""
    if "^" in s:
        import re
        return MarkupText(re.sub(r"\^([−\-0-9]+)", r"<sup>\1</sup>", s), font=FONT, font_size=size, color=color)
    return Text(s, font=FONT, font_size=size, color=color)


def title(s):
    t = tx(s, 40, WHITE).to_edge(UP, buff=0.45)
    return t


def pill(s, color, size=26):
    t = tx(s, size, WHITE)
    box = RoundedRectangle(width=t.get_width() + 0.5, height=t.get_height() + 0.35, corner_radius=0.15)
    box.set_stroke(color, 2).set_fill(color, 0.18)
    t.move_to(box)
    return VGroup(box, t)


def poly(points, color, opacity=0.35):
    m = VMobject()
    m.set_points_as_corners(points + [points[0]])
    m.set_stroke(width=0).set_fill(color, opacity)
    return m


def curve(axes, xs, ys, color, width=4):
    m = VMobject()
    m.set_points_smoothly([axes.c2p(x, y) for x, y in zip(xs, ys)])
    m.set_stroke(color, width).set_fill(opacity=0)
    return m


def check(color=C_GREEN, s=0.35):
    m = VMobject()
    m.set_points_as_corners([[-s, 0, 0], [-s * 0.3, -s * 0.7, 0], [s, s * 0.8, 0]])
    return m.set_stroke(color, 8).set_fill(opacity=0)


def cross(color=C_RED, s=0.3):
    return VGroup(Line([-s, -s, 0], [s, s, 0]), Line([-s, s, 0], [s, -s, 0])).set_stroke(color, 8)


def head(s):
    return tx(s, 44).to_edge(UP, buff=0.4)


def cap(s, color=C_GREY, y=-3.55):
    return tx(s, 28, color).move_to(DOWN * (-y))


def warn_icon(color=C_YEL, s=0.32):
    tri = Polygon([-s, -s * 0.8, 0], [s, -s * 0.8, 0], [0, s, 0]).set_stroke(color, 4).set_fill(color, 0.2)
    bang = tx("!", 26, color).move_to(tri.get_center() + DOWN * 0.04)
    return VGroup(tri, bang)


class Base(Scene):
    """Базовая сцена. SLOW > 1 растягивает все анимации и паузы (чтобы успевать читать и слушать озвучку)."""
    SLOW = 1.0

    def setup(self):
        self.camera.background_rgba = [0.059, 0.067, 0.082, 1]

    def play(self, *args, **kwargs):
        if self.SLOW != 1.0:
            kwargs["run_time"] = kwargs.get("run_time", 1.0) * self.SLOW
        super().play(*args, **kwargs)

    def wait(self, duration=1.0, *args, **kwargs):
        super().wait(duration * self.SLOW, *args, **kwargs)
