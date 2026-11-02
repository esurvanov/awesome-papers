"""Помощники кадра для любого ролика (PLAYBOOK, законы 29–31): закрывают классы дефектов, найденные на ролике про интегралы.
  • подпись никогда не стоит на цветной заливке без плашки: label(..., on_fill=True), plate();
  • размерные стрелки — на выносных пунктирах и не пересекают данные: dim_v, dim_h;
  • порядок слоёв по типу объекта, а не по порядку в коде: z(m, "fill" | "bar" | "axis" | "graph" | "dot" | "dim" | "label" | "ui");
  • связь двух панелей — пунктир одного цвета: link; точка с тёмной обводкой: dot;
  • подпись кадра внизу — белая, крупная, на плашке: cap; плашка с годом: plaque;
  • метка .tag — «тот же объект» в соседних кадрах (по ней основа сцен превращает объект, а не рисует заново): tagged."""
import numpy as np
from manimlib import (VGroup, VMobject, Line, DashedLine, Arrow, Dot, Triangle, RoundedRectangle, WHITE, UP, DOWN, LEFT, RIGHT, PI)
from .style import tx

__all__ = ["C_TEXT", "C_PLATE", "C_MUTED", "Z", "z", "tagged", "line", "poly_line", "plate", "label", "num", "cap", "pill",
           "plaque", "link", "dot", "marker", "dim_v", "dim_h", "node", "CAP_Y", "SAFE_TOP", "SAFE_BOTTOM"]

C_TEXT, C_PLATE, C_MUTED = WHITE, "#0f1115", "#8b949e"
CAP_Y = -2.55          # подпись кадра (над полосой «мы здесь»)
SAFE_BOTTOM = -2.3     # ниже — подпись кадра и полоса; свои объекты сцены ставить выше
SAFE_TOP = 3.15        # выше — строка сквозной сущности (если есть)
Z = {"fill": 0, "bar": 1, "axis": 2, "graph": 3, "dot": 4, "dim": 5, "label": 6, "ui": 7}


def z(m, kind):
    m.set_z_index(Z[kind])
    return m


def tagged(m, t):
    m.tag = t
    return m


def line(a, b, color=WHITE, w=3, dashed=False):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    return (DashedLine(a, b) if dashed else Line(a, b)).set_stroke(color, w)


def poly_line(pts, color, w=4):
    m = VMobject()
    m.set_points_as_corners([np.array(p, dtype=float) for p in pts])
    return m.set_stroke(color, w).set_fill(opacity=0)


def plate(m, pad=0.14, op=0.88):
    r = RoundedRectangle(width=m.get_width() + 2 * pad, height=m.get_height() + 2 * pad, corner_radius=0.1)
    return r.set_stroke(width=0).set_fill(C_PLATE, op).move_to(m)


def label(text, at, color=C_TEXT, size=26, on_fill=False, direction=None, buff=0.2):
    """Подпись. on_fill=True — на тёмной плашке (обязательно, если стоит на заливке). direction — рядом с объектом/точкой at."""
    t = tx(text, size, color)
    t.next_to(at, direction, buff=buff) if direction is not None else t.move_to(at)
    return z(VGroup(plate(t), t) if on_fill else t, "label")


def num(v, d=2):
    """Число для экрана с запятой, без лишних нулей: num(20.025, 3) → «20,025»."""
    s = f"{v:.{d}f}".rstrip("0").rstrip(".") if d else f"{v:.0f}"
    return s.replace(".", ",")


def cap(s, size=28):
    t = tx(s, size, C_TEXT).move_to([0, CAP_Y, 0])
    return z(VGroup(plate(t, 0.12, 0.7), t), "ui")


def pill(s, color=WHITE, size=26):
    t = tx(s, size, color)
    r = RoundedRectangle(width=t.get_width() + 0.5, height=t.get_height() + 0.32, corner_radius=0.12).set_stroke(color, 2).set_fill(C_PLATE, 1)
    return z(VGroup(r, t.move_to(r)), "label")


def plaque(year, who, x=4.4, y=2.6, color=WHITE):
    return pill(f"{year} · {who}", color, 26).move_to([x, y, 0])


def link(p, q, color, w=3):
    return z(DashedLine(np.array(p, dtype=float), np.array(q, dtype=float), dash_length=0.12).set_stroke(color, w), "dim")


def dot(p, color, r=0.12):
    d = Dot(np.array(p, dtype=float), radius=r).set_color(color)
    d.set_stroke(C_PLATE, 2)
    return z(d, "dot")


def marker(p, color):
    m = Triangle().scale(0.15).rotate(PI).set_stroke(C_PLATE, 2).set_fill(color, 1).move_to(np.array(p) + UP * 0.2)
    return z(m, "dot")


def _arrow2(p, q, color, w=4):
    p, q = np.array(p, dtype=float), np.array(q, dtype=float)
    m = (p + q) / 2
    return VGroup(Arrow(m, p, buff=0, stroke_width=w).set_color(color), Arrow(m, q, buff=0, stroke_width=w).set_color(color))


def dim_v(edge_x, y0, y1, text, color, side=RIGHT, gap=0.6, size=24):
    """Вертикальный размер объекта: стрелка вынесена от края edge_x на gap, к ней — горизонтальные выносные пунктиры от y0 и y1."""
    sgn = 1 if np.array_equal(side, RIGHT) else -1
    x = edge_x + sgn * gap
    ext = VGroup(DashedLine([edge_x, y0, 0], [x + 0.15 * sgn, y0, 0]).set_stroke(color, 2),
                 DashedLine([edge_x, y1, 0], [x + 0.15 * sgn, y1, 0]).set_stroke(color, 2))
    lab = tx(text, size, color).next_to(np.array([x, (y0 + y1) / 2, 0]), side, buff=0.18)
    return z(VGroup(ext, _arrow2([x, y0, 0], [x, y1, 0], color), lab), "dim")


def dim_h(x0, x1, bottom_y, text, color, gap=0.45, size=24):
    """Горизонтальный размер под объектом: стрелка ниже на gap, вертикальные выносные пунктиры от краёв."""
    y = bottom_y - gap
    ext = VGroup(DashedLine([x0, bottom_y, 0], [x0, y - 0.12, 0]).set_stroke(color, 2),
                 DashedLine([x1, bottom_y, 0], [x1, y - 0.12, 0]).set_stroke(color, 2))
    lab = tx(text, size, color).next_to(np.array([(x0 + x1) / 2, y, 0]), DOWN, buff=0.15)
    return z(VGroup(ext, _arrow2([x0, y, 0], [x1, y, 0], color), lab), "dim")


def node(s, x, y, color, w=3.0, size=22):
    t = tx(s, size, color)
    r = RoundedRectangle(width=max(w, t.get_width() + 0.4), height=0.7, corner_radius=0.12).set_stroke(color, 2).set_fill(C_PLATE, 1)
    return z(VGroup(r, t).move_to([x, y, 0]), "label")
