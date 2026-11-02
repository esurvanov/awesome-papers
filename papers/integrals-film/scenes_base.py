"""Основа сцен ролика про интегралы (версия 6): общая основа — core/manimkit/film.py (film_base), здесь — только своё:
сквозная строка «правила счёта» (overlay) и объёмные тела этого мира (башни, плиты, гребень горки)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(HERE))
import numpy as np
from manimlib import *
from manimkit import *
from manimkit.film import film_base
import passport as P
import narration as N
from icons import ICONS
from world import *

ORDER = [c for c, *_ in P.SCENES]
# какие правила счёта горят в строке сверху: сцена → [(с какого кадра, номера правил)]; строка вводится в A12
RULES_LIT = {
    "A12": [(1, ()), (2, (0,)), (3, (1,)), (4, (2,)), (5, (3,)), (6, "all")],
    "A13": [(1, (1,))], "A14": [(1, (0,))], "A15": [(1, (0, 2))], "A16": [(1, (2,))], "A17": [(1, (2,))], "A18": [(1, (2,))],
    "A19": [(1, (0, 1))], "A20": [(1, (2,))], "A21": [(1, (2,))], "A22": [(1, (1,))], "A23": [(1, (2,))], "A24": [(1, (2,))],
    "A25": [(1, (2,))], "A26": [(1, (3,))], "A27": [(1, (3,))], "A28": [(1, "all")],
}


def rules_for(code, k):
    lit = None
    for frm, l in RULES_LIT.get(code, []):
        if k >= frm:
            lit = l
    return lit


_Film, _Film3D = film_base(P.STATIONS, P.SCENES, ICONS, N.TEXT, HERE)


class Film(_Film):
    def overlay(self, code, k):
        lit = rules_for(code, k)
        return rules_row(lit) if lit is not None else None


class Film3D(_Film3D):
    AXIS_Y = AY

    def overlay(self, code, k):
        lit = rules_for(code, k)
        return rules_row(lit) if lit is not None else None


DEP = 2.2


def tower(u0, u1, h, color=C_BET):
    p = Prism(width=(u1 - u0) - 0.08, height=DEP, depth=max(h - 0.04, 0.02))
    p.set_color(color).set_opacity(1).set_shading(0.2, 0.2, 0.15)
    p.move_to([X((u0 + u1) / 2), DEP / 2, h / 2])
    return p


def slab(u0, u1, h0, h1, color):
    p = Prism(width=(u1 - u0), height=DEP, depth=h1 - h0 - 0.08)
    p.set_color(color).set_opacity(1).set_shading(0.2, 0.2, 0.15)
    p.move_to([X((u0 + u1) / 2), DEP / 2, (h0 + h1) / 2])
    return p


def ridge3():
    edge = ParametricCurve(lambda t: np.array([X(t), 0.0, F(t)]), t_range=(0, 10, 0.05)).set_stroke(C_PRICE, 9)
    back = ParametricCurve(lambda t: np.array([X(t), DEP, F(t)]), t_range=(0, 10, 0.05)).set_stroke(C_PRICE, 4)
    ribs = VGroup(*[Line([X(u), 0, F(u)], [X(u), DEP, F(u)]).set_stroke(C_PRICE, 3) for u in np.linspace(0, 10, 9)])
    return edge, back, ribs


def axis3():
    ax = Line([X(-0.6), 0, 0], [X(10.6), 0, 0]).set_stroke(C_AXIS, 10)
    grid = VGroup(*[Line([X(u), 0, 0], [X(u), DEP, 0]).set_stroke(C_NOTE, 1.5) for u in range(11)],
                  *[Line([X(0), y, 0], [X(10), y, 0]).set_stroke(C_NOTE, 1.5) for y in np.linspace(0, DEP, 4)])
    return ax, grid


FRONT_CENTER = np.array([0.0, 0.0, -AY])     # вид спереди: ось в 3D (z = 0) совпадает с осью плоского кадра (y = AY)
