"""3D-детали ролика: кольцо из шариков с номерами и настоящими ходами (влево, вправо, обмен в окошке) и башня расстановок
по этажам (этаж = сколько ходов до порядка, посчитано перебором). Используется сценами scenes.py рядом.

Расстановка — кортеж: s[k] — номер шарика в гнезде k. Гнёзда 0 и 1 — окошко наверху, дальше по часовой стрелке.
Ходы — как в статье (LRX): влево L: s[1:] + s[:1], вправо R: s[-1:] + s[:-1], обмен X: (s[1], s[0]) + s[2:]."""
from collections import deque

import numpy as np
from manimlib import *

C_RING, C_ORDER, C_MIRROR, C_WALK, C_COMP, C_FRONT, C_NO, C_NOTE = (
    "#58a6ff", "#3fb950", "#f778ba", "#f0883e", "#e3b341", "#d2a8ff", "#f85149", "#8b949e")
BG = "#0f1115"


# ---------- расстановки и ходы ----------

def left(s):
    return s[1:] + s[:1]


def right(s):
    return s[-1:] + s[:-1]


def swap(s):
    return (s[1], s[0]) + s[2:]


MOVES = {"влево": left, "вправо": right, "обмен": swap}


def floors(n):
    """Перебор (поиск в ширину от порядка): этаж каждой расстановки."""
    e = tuple(range(n))
    d, q = {e: 0}, deque([e])
    while q:
        s = q.popleft()
        for f in (left, right, swap):
            t = f(s)
            if t not in d:
                d[t] = d[s] + 1
                q.append(t)
    return d


def mirror(n):
    """Зеркало (дальняя расстановка): (1 0 n−1 n−2 … 2) — кольцо, отражённое через окошко."""
    return (1, 0) + tuple(range(n - 1, 1, -1))


def pairs(n):
    return n * (n - 1) // 2


# ---------- кольцо ----------

def slot_angle(k, n):
    """Угол гнезда k: окошко (гнёзда 0 и 1) — наверху, по обе стороны от вертикали; дальше по часовой стрелке."""
    return PI / 2 + PI / n - TAU * k / n


def slot_pos(k, n, R, center=ORIGIN):
    a = slot_angle(k, n)
    return np.array(center) + R * np.array([np.cos(a), np.sin(a), 0])


def ball(num, r=0.32, color=C_RING, label=True, base=1):
    """Шарик с номером: объёмная сфера и номер на её «макушке», обращённый к зрителю. На экране номера с единицы (base=1)."""
    sph = Sphere(radius=r, resolution=(24, 12)).set_color(color).set_shading(0.35, 0.45, 0.25)
    g = Group(sph)
    if label:
        t = Text(str(num + base), font="Arial", font_size=max(14, int(r * 90))).set_color(WHITE)
        t.move_to(OUT * (r + 0.02))
        g.add(t)
    g.num = num
    return g


class Ring:
    """Кольцо на экране: обод, окошко наверху и шарики по гнёздам. Ходы — анимации, которые меняют и картинку, и расстановку."""

    def __init__(self, s, R=2.0, r=0.32, center=ORIGIN, color=C_RING, window=True, labels=True):
        self.s, self.n, self.R, self.r, self.c = tuple(s), len(s), R, r, np.array(center, dtype=float)
        self.rim = Circle(radius=R).move_to(self.c).set_stroke(C_NOTE, 3, opacity=0.6)
        self.balls = {v: ball(v, r, color, labels) for v in self.s}
        for k, v in enumerate(self.s):
            self.balls[v].move_to(self.pos(k))
        self.window = None
        if window:
            p0, p1 = self.pos(0), self.pos(1)
            w = RoundedRectangle(width=np.linalg.norm(p1 - p0) + 3.4 * r, height=3.4 * r, corner_radius=0.2)
            self.window = w.move_to((p0 + p1) / 2 + IN * 0.05).set_stroke(WHITE, 4).set_fill(WHITE, 0.08)
        self.group = Group(self.rim, *([self.window] if self.window is not None else []), *self.balls.values())

    def pos(self, k):
        return slot_pos(k, self.n, self.R, self.c)

    def ball_at(self, k):
        return self.balls[self.s[k]]

    def _along(self, step):
        """Все шарики едут по ободу на step гнёзд (−1 — влево, +1 — вправо), номера остаются обращены к зрителю."""
        n, start = self.n, {v: k for k, v in enumerate(self.s)}

        def upd(m, a, v, k0):
            ang = slot_angle(k0, n) - TAU * step * a / n
            m.move_to(self.c + self.R * np.array([np.cos(ang), np.sin(ang), 0]))

        anims = [UpdateFromAlphaFunc(self.balls[v], lambda m, a, v=v, k0=start[v]: upd(m, a, v, k0)) for v in self.s]
        return AnimationGroup(*anims)

    def move(self, name):
        """Анимация хода; расстановка обновляется сразу."""
        if name in ("влево", "вправо"):
            step = -1 if name == "влево" else 1
            anim = self._along(step)  # пути шариков считаются от старой расстановки
            self.s = left(self.s) if step < 0 else right(self.s)
            return anim
        a, b = self.ball_at(0), self.ball_at(1)
        p0, p1 = self.pos(0), self.pos(1)
        self.s = swap(self.s)
        lift = OUT * 0.9  # шарики перепрыгивают друг через друга над кольцом
        return AnimationGroup(
            UpdateFromAlphaFunc(a, lambda m, t: m.move_to(interpolate(p0, p1, t) + lift * np.sin(PI * t))),
            UpdateFromAlphaFunc(b, lambda m, t: m.move_to(interpolate(p1, p0, t) - lift * np.sin(PI * t) * 0.3)))

    def set_to(self, s):
        """Расставить шарики по новой расстановке (анимация перелёта)."""
        self.s = tuple(s)
        return AnimationGroup(*[self.balls[v].animate.move_to(self.pos(k)) for k, v in enumerate(self.s)])

    def paint(self, color):
        return AnimationGroup(*[b[0].animate.set_color(color) for b in self.balls.values()])


# ---------- башня этажей ----------

def tower(n=5, rise=0.5, spread=0.42):
    """Башня расстановок: каждая — точка на своём этаже (высота = этаж · rise), этажи — кольца точек, ходы — линии.
    Возвращает (точки {расстановка: координата}, линии VGroup, словарь этажей)."""
    d = floors(n)
    by = {}
    for s, f in d.items():
        by.setdefault(f, []).append(s)
    pos = {}
    for f, ss in by.items():
        ss.sort()
        m = len(ss)
        rad = 0 if m == 1 else spread * np.sqrt(m)
        for i, s in enumerate(ss):
            a = TAU * i / m + f * 0.37
            pos[s] = np.array([rad * np.cos(a), rad * np.sin(a), f * rise])
    lines = VGroup()
    seen = set()
    for s in d:
        for g in (left, right, swap):
            t = g(s)
            key = frozenset((s, t))
            if key not in seen:
                seen.add(key)
                lines.add(Line(pos[s], pos[t]).set_stroke(C_RING, 1, opacity=0.25))
    return pos, lines, d, by


def tower_dots(pos, d, r=0.07):
    top = max(d.values())
    out = Group()
    for s, p in pos.items():
        col = C_ORDER if d[s] == 0 else C_MIRROR if d[s] == top else C_RING
        out.add(Sphere(radius=r * (2.2 if d[s] in (0, top) else 1), resolution=(16, 8)).set_color(col).move_to(p))
    return out
