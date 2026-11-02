"""Значки станций полосы «мы здесь» — маленькие версии образов мира: каждый значок — кусок той же кассы."""
import numpy as np
from manimlib import *
from kit import *


def _mk(parts, s):
    return VGroup(*parts).scale(s)


def icon_question(s=1.0):
    return tx("?", 40, WHITE).scale(s)


def icon_smooth(s=1.0):
    return _mk([curve_of(lambda x: 0.35 * np.sin(2.2 * x), -0.5, 0.5, 0, C_PRICE, 3, 30)], s)


def icon_steps(s=1.0):
    return _mk([Rectangle(width=0.18, height=h).set_stroke(C_BET, 2).set_fill(C_BET, 0.5).move_to([x, h / 2 - 0.3, 0])
                for x, h in ((-0.3, 0.35), (-0.1, 0.7), (0.1, 0.2), (0.3, 0.55))], s)


def icon_jump(s=1.0):
    return _mk([poly_line([[-0.5, -0.3, 0], [-0.15, -0.3, 0], [-0.15, 0.0, 0], [0.2, 0.0, 0], [0.2, 0.3, 0], [0.5, 0.3, 0]], C_PRICE, 3)], s)


def icon_noise(s=1.0):
    pts = [[-0.5, 0, 0], [-0.35, 0.25, 0], [-0.2, -0.2, 0], [-0.05, 0.3, 0], [0.1, -0.1, 0], [0.25, 0.2, 0], [0.5, -0.25, 0]]
    return _mk([poly_line(pts, C_NOISE, 3)], s)


def icon_total(s=1.0):
    return _mk([poly_line([[-0.35, 0.0, 0], [-0.1, -0.25, 0], [0.4, 0.3, 0]], C_SUM, 5)], s)


def icon_gear(s=1.0):
    teeth = [line([0.2 * np.cos(a), 0.2 * np.sin(a), 0], [0.3 * np.cos(a), 0.3 * np.sin(a), 0], WHITE, 3) for a in np.arange(8) * TAU / 8]
    return _mk([Circle(radius=0.2).set_stroke(WHITE, 3), *teeth], s)


def icon_tree(s=1.0):
    return _mk([line([0, -0.3, 0], [0, 0.0, 0], C_SUM, 3), line([0, 0.0, 0], [-0.3, 0.3, 0], C_SUM, 3), line([0, 0.0, 0], [0.3, 0.3, 0], C_SUM, 3), line([0, 0.0, 0], [0, 0.35, 0], C_SUM, 3)], s)


ICONS = {"Вопрос": icon_question, "Гладкий график": icon_smooth, "Рваный график": icon_steps, "Другая линейка": icon_jump,
         "Случайный график": icon_noise, "Что дальше": icon_tree, "Итог": icon_total, "Как устроено": icon_gear}
