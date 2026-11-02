"""Элементы мира «сортировочная станция» (2D) — для раскадровки (storyboard.py) и сцен ролика.

Вагон — скруглённый прямоугольник с крупным номером и колёсами; состав — ряд вагонов на рельсах; вышка — этажи-площадки,
на площадке маленькие составы (настоящие, посчитаны перебором growth3d.floors); журнал — книга со строками-составами;
кольцевой путь — круг рельсов с вагонами и рамкой стрелки. Номера вагонов на экране — с единицы."""
import sys
from pathlib import Path

import numpy as np
from manimlib import *

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "core"))
from manimkit import tx, pill, check, cross  # noqa: E402

__all__ = ["C_BALL", "C_ORDER", "C_TOP", "C_RHYTHM", "C_SWING", "C_COMP", "C_NO", "C_NOTE",
           "wagon", "train", "rails", "mini_train", "tower2d", "journal", "dispatcher", "sign", "metronome",
           "stopwatch", "calendar", "compass", "ring_track", "chat_window", "bars", "wall", "arrow_label", "move_icon", "title2"]

C_BALL, C_ORDER, C_TOP, C_RHYTHM, C_SWING, C_COMP, C_NO, C_NOTE = (
    "#58a6ff", "#3fb950", "#f778ba", "#d2a8ff", "#f0883e", "#e3b341", "#f85149", "#8b949e")


def title2(s, size=34, color=WHITE):
    """Заголовок кадра — ниже верхней строки раскадровки."""
    return tx(s, size, color).move_to(UP * 2.75)


def wagon(num, color=C_BALL, w=0.9, h=0.55, show=True):
    body = RoundedRectangle(width=w, height=h, corner_radius=0.08).set_stroke(color, 2).set_fill(color, 0.85)
    wheels = VGroup(*[Circle(radius=h * 0.13).set_stroke(C_NOTE, 2).set_fill(BLACK, 1).move_to(body.get_bottom() + RIGHT * dx * w)
                      for dx in (-0.28, 0.28)])
    g = VGroup(body, wheels)
    if show:
        g.add(tx(str(num), int(h * 52), WHITE).move_to(body))
    g.num = num
    return g


def train(nums, color=C_BALL, w=0.9, h=0.55, gap=0.12, colors=None):
    ws = VGroup(*[wagon(n, (colors or {}).get(n, color), w, h) for n in nums]).arrange(RIGHT, buff=gap)
    links = VGroup(*[Line(ws[k].get_right(), ws[k + 1].get_left()).set_stroke(C_NOTE, 2) for k in range(len(ws) - 1)])
    return VGroup(ws, links)


def rails(length=8.0, y=0.0):
    r = VGroup(Line(LEFT * length / 2, RIGHT * length / 2).shift(UP * 0.04), Line(LEFT * length / 2, RIGHT * length / 2).shift(DOWN * 0.04))
    r.set_stroke(C_NOTE, 3)
    sleepers = VGroup(*[Line(UP * 0.1, DOWN * 0.1).set_stroke(C_NOTE, 2, opacity=0.5).shift(RIGHT * x)
                        for x in np.arange(-length / 2, length / 2 + 0.01, 0.35)])
    g = VGroup(sleepers, r).shift(UP * y)
    g.overlay = True  # фон: на рельсах стоят составы
    return g


def mini_train(perm, color=C_BALL, s=0.2):
    """Маленький состав на площадке вышки: квадратики с номерами."""
    g = VGroup()
    for v in perm:
        sq = Square(s).set_stroke(color, 1.5).set_fill(color, 0.6)
        g.add(VGroup(sq, tx(str(v + 1), int(s * 70), WHITE).move_to(sq)))
    return g.arrange(RIGHT, buff=s * 0.12)


def tower2d(by_floor, height=5.2, width=6.0, show=None, top_color=C_TOP, s=0.18):
    """Вышка: площадки снизу вверх; на площадке — составы этажа (by_floor[f] — список перестановок).
    show — сколько площадок показать (по умолчанию все). Возвращает (VGroup, площадки, составы по этажам)."""
    floors = sorted(by_floor)
    top = floors[-1]
    step = height / (top + 1)
    plates, rows = VGroup(), []
    g = VGroup()
    for f in floors:
        y = -height / 2 + f * step
        col = C_ORDER if f == 0 else top_color if f == top else C_BALL
        plate = Polygon([-width / 2, y, 0], [width / 2, y, 0], [width / 2 - 0.25, y + 0.12, 0], [-width / 2 + 0.25, y + 0.12, 0])
        plate.set_stroke(col, 1.5, opacity=0.8).set_fill(col, 0.12)
        num = tx(str(f), 18, C_NOTE).next_to(plate, LEFT, buff=0.15)
        trains = VGroup(*[mini_train(p, col, s) for p in by_floor[f]]).arrange(RIGHT, buff=0.18)
        if trains.get_width() > width - 0.4:
            trains.set_width(width - 0.4)
        trains.next_to(plate, UP, buff=0.03)
        plates.add(VGroup(plate, num))
        rows.append(trains)
        g.add(plates[-1], trains)
    if show is not None:
        for f in floors[show:]:
            g.remove(plates[f], rows[f])
    posts = VGroup(Line([-width / 2 + 0.1, -height / 2, 0], [-width / 2 + 0.1, height / 2 - step + 0.2, 0]),
                   Line([width / 2 - 0.1, -height / 2, 0], [width / 2 - 0.1, height / 2 - step + 0.2, 0])).set_stroke(C_NOTE, 2, opacity=0.5)
    g.add_to_back(posts)
    return g, plates, rows


def journal(lines, w=3.4, h=3.6, color=C_COMP):
    """Журнал: раскрытая книга, строки-записи (текст или VGroup)."""
    cover = RoundedRectangle(width=w, height=h, corner_radius=0.12).set_stroke(color, 3).set_fill(color, 0.08)
    spine = Line(cover.get_top(), cover.get_bottom()).set_stroke(color, 2, opacity=0.6).shift(LEFT * w * 0.42)
    head = tx("журнал", 22, color).next_to(cover.get_top(), DOWN, buff=0.15)
    rows = VGroup(*[l if isinstance(l, Mobject) else tx(l, 18, WHITE) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    rows.next_to(head, DOWN, buff=0.2).align_to(spine, LEFT).shift(RIGHT * 0.2)
    return VGroup(cover, spine, head, rows)


def dispatcher(color=WHITE):
    head = Circle(radius=0.18).set_stroke(color, 2).set_fill(color, 0.2)
    body = RoundedRectangle(width=0.5, height=0.7, corner_radius=0.18).set_stroke(color, 2).set_fill(color, 0.1).next_to(head, DOWN, buff=0.05)
    board = Rectangle(width=0.28, height=0.36).set_stroke(C_COMP, 2).set_fill(C_COMP, 0.25).move_to(body.get_right() + LEFT * 0.05)
    cap = Rectangle(width=0.42, height=0.08).set_fill(color, 0.8).set_stroke(width=0).next_to(head, UP, buff=-0.05)
    return VGroup(body, head, cap, board)


def move_icon(kind, color=C_BALL, s=0.5):
    """Значок манёвра: «соседи» ⇄, «головной с любым», «по кругу», «круг на четыре»."""
    if kind == "соседи":
        a = VGroup(Square(s * 0.5), Square(s * 0.5)).arrange(RIGHT, buff=s * 0.1).set_stroke(color, 2)
        return VGroup(a, tx("⇄", int(s * 50), color).next_to(a, UP, buff=0.02))
    if kind == "головной":
        a = VGroup(*[Square(s * 0.35) for _ in range(4)]).arrange(RIGHT, buff=s * 0.06).set_stroke(color, 2)
        arc = ArcBetweenPoints(a[0].get_top(), a[2].get_top(), angle=-PI / 2).set_stroke(color, 2)
        return VGroup(a, arc)
    if kind == "по кругу":
        return VGroup(Circle(radius=s * 0.45).set_stroke(color, 2), Arc(0, PI * 1.4, radius=s * 0.6).add_tip().set_stroke(color, 2))
    if kind == "круг на четыре":
        sq = VGroup(*[Square(s * 0.3).move_to(s * 0.3 * np.array([np.cos(a), np.sin(a), 0])) for a in np.arange(4) * PI / 2]).set_stroke(color, 2)
        return VGroup(sq, Arc(0, PI * 1.5, radius=s * 0.62).add_tip().set_stroke(color, 2))
    raise ValueError(kind)


def sign(title, icons, color=C_NOTE):
    """Табличка станции: название и значки разрешённых манёвров."""
    content = VGroup(tx(title, 22, WHITE), VGroup(*icons).arrange(RIGHT, buff=0.3)).arrange(DOWN, buff=0.15)
    board = RoundedRectangle(width=content.get_width() + 0.5, height=content.get_height() + 0.4, corner_radius=0.1)
    board.set_stroke(color, 2).set_fill(BLACK, 0.6).move_to(content)
    post = Line(board.get_bottom(), board.get_bottom() + DOWN * 0.6).set_stroke(color, 3)
    return VGroup(post, board, content)


def metronome(beat, color=C_RHYTHM, s=1.0):
    body = Polygon([-0.4, -0.6, 0], [0.4, -0.6, 0], [0.15, 0.6, 0], [-0.15, 0.6, 0]).set_stroke(color, 3).set_fill(color, 0.12)
    arm = Line([0, -0.45, 0], [0.32, 0.55, 0]).set_stroke(WHITE, 3)
    lab = tx(f"ритм {beat}", 20, color).next_to(body, DOWN, buff=0.12)
    return VGroup(body, arm, Dot([0.22, 0.25, 0], radius=0.05).set_color(WHITE), lab).scale(s)


def stopwatch(text, color=WHITE, frac=0.25):
    face = Circle(radius=0.45).set_stroke(color, 3)
    knob = Rectangle(width=0.14, height=0.1).set_fill(color, 1).set_stroke(width=0).next_to(face, UP, buff=0.02)
    hand = Line(ORIGIN, 0.36 * np.array([np.sin(TAU * frac), np.cos(TAU * frac), 0])).set_stroke(color, 3)
    return VGroup(face, knob, hand, tx(text, 24, color).next_to(face, DOWN, buff=0.12))


def calendar(text, color=WHITE, pages=1):
    g = VGroup()
    for k in range(pages):
        p = RoundedRectangle(width=0.9, height=0.9, corner_radius=0.08).set_stroke(color, 2).set_fill(BLACK, 1).shift((RIGHT + UP) * 0.1 * k)
        bar = Rectangle(width=0.9, height=0.18).set_fill(C_NO, 0.8).set_stroke(width=0).move_to(p.get_top() + DOWN * 0.09)
        g.add(VGroup(p, bar))
    return VGroup(g, tx(text, 22, color).next_to(g, DOWN, buff=0.15))


def compass(r=0.45, color=C_COMP):
    ring = Circle(radius=r).set_stroke(color, 4).set_fill(color, 0.1)
    a = rotate_vector(UP, -PI / 5)
    side = rotate_vector(a, PI / 2) * r * 0.22
    tip = Polygon(a * r * 0.85, side, -side).set_stroke(width=0).set_fill(color, 1)
    back = Polygon(-a * r * 0.85, side, -side).set_stroke(width=0).set_fill(C_NOTE, 1)
    return VGroup(ring, back, tip)


def ring_track(nums, R=1.6, color=C_BALL, switch=True):
    """Кольцевой путь: круг рельсов, вагоны по кругу (место 0 и 1 — наверху, у стрелки)."""
    n = len(nums)
    rail = VGroup(Circle(radius=R + 0.05), Circle(radius=R - 0.05)).set_stroke(C_NOTE, 3)
    cars = VGroup()
    for k, v in enumerate(nums):
        a = PI / 2 + PI / n - TAU * k / n
        w = wagon(v, color, 0.62, 0.42).rotate(a - PI / 2).move_to(R * np.array([np.cos(a), np.sin(a), 0]))
        cars.add(w)
    g = VGroup(rail, cars)
    if switch:
        frame = RoundedRectangle(width=2 * R * np.sin(PI / n) + 1.0, height=0.8, corner_radius=0.12).set_stroke(WHITE, 3)
        frame.move_to(UP * R * np.cos(PI / n))
        g.add(frame, tx("стрелка", 18, WHITE).next_to(frame, UP, buff=0.08))
    return g


def chat_window(lines, w=6.5):
    body = VGroup(*[tx(l, 22, WHITE) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    box = RoundedRectangle(width=w, height=body.get_height() + 0.9, corner_radius=0.2).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.08)
    top = Rectangle(width=w, height=0.3).set_fill(C_NOTE, 0.3).set_stroke(width=0).move_to(box.get_top() + DOWN * 0.15)
    dots = VGroup(*[Dot(radius=0.05).set_color(c) for c in (C_NO, C_COMP, C_ORDER)]).arrange(RIGHT, buff=0.08).move_to(top).align_to(top, LEFT).shift(RIGHT * 0.2)
    body.move_to(box).shift(DOWN * 0.12)
    return VGroup(box, top, dots, body)


def bars(values, colors, x0=-4.5, step=0.8, scale=0.2, y0=-2.1, width=0.5, labels=None, show_values=True):
    g = VGroup()
    for k, (v, c) in enumerate(zip(values, colors)):
        h = max(0.03, v * scale)
        r = Rectangle(width=width, height=h).set_stroke(c, 2).set_fill(c, 0.75).move_to([x0 + k * step, y0 + h / 2, 0])
        item = VGroup(r)
        if show_values:
            item.add(tx(str(v), 18, c).next_to(r, UP, buff=0.06))
        if labels:
            item.add(tx(str(labels[k]), 18, C_NOTE).next_to(r, DOWN, buff=0.08))
        g.add(item)
    return g


def wall(x, label, y0=-2.2, h=4.0, color=C_NO):
    w = Rectangle(width=0.08, height=h).set_fill(color, 0.85).set_stroke(width=0).move_to([x, y0 + h / 2, 0])
    w.overlay = True  # стена стоит между столбиками — так задумано
    return w, tx(label, 18, color).next_to(w, UP, buff=0.08)


def arrow_label(start, end, text, color=WHITE, size=20):
    a = Arrow(start, end, buff=0.05).set_color(color)
    return VGroup(a, tx(text, size, color).next_to(a, UP, buff=0.05))
