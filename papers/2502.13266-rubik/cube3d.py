"""3D-детали ролика: кубик Рубика из маленьких кубиков с настоящими поворотами слоёв и рельеф лабиринта
(высота комнаты = расстояние до выхода). Используется сценами A01, A03 (scenes.py) и демо (demo3d.py)."""
import itertools

import numpy as np
from manimlib import *

import maze as M

C_POS, C_EXIT, C_WALK, C_COMP, C_NO, C_NOTE = "#58a6ff", "#3fb950", "#f0883e", "#e3b341", "#f85149", "#8b949e"
BODY = "#1b1f24"
# цвета наклеек по граням: (ось, сторона) → цвет; все из палитры паспорта
STICKER = {(2, 1): WHITE, (2, -1): C_COMP, (0, 1): C_NO, (0, -1): C_WALK, (1, 1): C_POS, (1, -1): C_EXIT}
RISE = 0.6  # высота ступени рельефа: комната на расстоянии d от выхода стоит на высоте d·RISE


def rubik(step=0.8, n=3):
    """n³ кубиков; наружные грани — цветные наклейки, внутренние — цвет корпуса."""
    half = (n - 1) / 2
    cubies = Group()
    for pos in itertools.product(np.arange(n) - half, repeat=3):
        c = Cube(side_length=step * 0.94, color=BODY, shading=(0.25, 0.4, 0.2)).move_to(np.array(pos) * step)
        for face in c:
            nrm = face.get_center() - c.get_center()
            ax = int(np.argmax(np.abs(nrm)))
            sgn = int(np.sign(nrm[ax]))
            if pos[ax] == sgn * half:
                face.set_color(STICKER[(ax, sgn)])
        c.grid_pos = np.array(pos)
        cubies.add(c)
    return cubies


def turn(cubies, ax, val, angle):
    """Поворот слоя (ось ax, координата val) на angle: анимация и обновление позиций кубиков в сетке."""
    lay = Group(*[c for c in cubies if round(c.grid_pos[ax] * 2) == round(val * 2)])
    axis = [RIGHT, UP, OUT][ax]
    rot = rotation_matrix(angle, axis)
    for c in lay:
        c.grid_pos = np.round(rot @ c.grid_pos * 2) / 2
    return Rotate(lay, angle, axis=axis, about_point=cubies.get_center())


def neighbours(step=0.22):
    """12 соседних позиций кубика: тот же собранный кубик после одного поворота грани (6 граней × 2 стороны) —
    настоящие соседи в лабиринте, а не условные кубики. Возвращает [(название хода, кубик)]."""
    out = []
    for ax, axis_name in ((0, "R/L"), (1, "U/D"), (2, "F/B")):
        for val in (1, -1):
            for angle in (PI / 2, -PI / 2):
                c = rubik(step=step)
                lay = Group(*[q for q in c if round(q.grid_pos[ax]) == val])
                lay.rotate(angle, axis=[RIGHT, UP, OUT][ax], about_point=c.get_center())
                out.append((f"{axis_name}{'+' if angle > 0 else '−'}", c))
    return out


def p3(k, rise=True):
    x, y = M.POS[k]
    return np.array([x, y, M.DIST[k] * RISE if rise else 0.0])


def relief():
    """Рельеф: двери — линии, комнаты — кубики; выход — зелёный, внизу."""
    doors = VGroup(*[Line(p3(a), p3(b)).set_stroke(C_POS, 2.5, opacity=0.6) for a, b in M.EDGES])
    rooms = Group(*[Cube(side_length=0.34, color=C_EXIT if k == M.EXIT else WHITE if k == M.START else C_POS,
                         shading=(0.3, 0.5, 0.2)).move_to(p3(k)) for k in range(len(M.POS))])
    return doors, rooms


def flat_room(k):
    """Комната плоской карты — как в 2D-сценах: контур и лёгкая заливка."""
    col = C_EXIT if k == M.EXIT else WHITE if k == M.START else C_POS
    fill = 0.5 if k == M.EXIT else 0.35 if k == M.START else 0.15
    return Square(0.34).move_to(p3(k, rise=False)).set_stroke(col, 2.5).set_fill(col, fill)
