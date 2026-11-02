"""3D-детали ролика: ряд шариков с номерами, кольцо Глушкова (поворот влево и обмен двух верхних), башни расстановок по этажам
для любых наборов ходов (этаж = сколько ходов до порядка, посчитано перебором) и рисунок ходов линиями между местами.

Расстановка — кортеж: s[k] — номер шарика на месте k. Ход — перестановка мест g: новая расстановка t[k] = s[g[k]].
Наборы — как в статье: соседи (i, i+1), «первый с любым» (0, i), Глушков L и X, круги по четыре (i … i+3) с обратными."""
from collections import deque

import numpy as np
from manimlib import *

C_BALL, C_ORDER, C_TOP, C_RHYTHM, C_SWING, C_COMP, C_NO, C_NOTE = (
    "#58a6ff", "#3fb950", "#f778ba", "#d2a8ff", "#f0883e", "#e3b341", "#f85149", "#8b949e")


# ---------- наборы ходов ----------

def apply(s, g):
    return tuple(s[i] for i in g)


def neighbours(n):
    """Обмены соседей (i, i+1)."""
    out = []
    for i in range(n - 1):
        g = list(range(n))
        g[i], g[i + 1] = g[i + 1], g[i]
        out.append(tuple(g))
    return out


def star(n):
    """«Первый с любым»: (0, i)."""
    out = []
    for i in range(1, n):
        g = list(range(n))
        g[0], g[i] = g[i], g[0]
        out.append(tuple(g))
    return out


def glushkov(n):
    """L — поворот влево, X — обмен двух первых (верхних на кольце); без обратных ходов."""
    return [tuple((i + 1) % n for i in range(n)), (1, 0) + tuple(range(2, n))]


def cycles4(n):
    """Круги по четыре соседа (i … i+3) и обратные им."""
    out = []
    for i in range(n - 3):
        g = list(range(n))
        g[i], g[i + 1], g[i + 2], g[i + 3] = g[i + 1], g[i + 2], g[i + 3], g[i]
        inv = [0] * n
        for a, b in enumerate(g):
            inv[b] = a
        out += [tuple(g), tuple(inv)]
    return out


def perm(n, cycles):
    """Перестановка мест из циклов: (2, 3) — обмен мест 2 и 3."""
    p = list(range(n))
    for c in cycles:
        for a, b in zip(c, c[1:] + c[:1]):
            p[a] = b
    return tuple(p)


def floors(n, gens):
    """Перебор (поиск в ширину от порядка): этаж каждой расстановки."""
    e = tuple(range(n))
    d, q = {e: 0}, deque([e])
    while q:
        s = q.popleft()
        for g in gens:
            t = apply(s, g)
            if t not in d:
                d[t] = d[s] + 1
                q.append(t)
    return d


def growth(n, gens):
    d = floors(n, gens)
    out = [0] * (max(d.values()) + 1)
    for f in d.values():
        out[f] += 1
    return out


# ---------- шарики ----------

def ball(num, r=0.32, color=C_BALL, label=True):
    """Шарик с номером (на экране с единицы): сфера и номер на «макушке», обращённый к зрителю."""
    sph = Sphere(radius=r, resolution=(24, 12)).set_color(color).set_shading(0.35, 0.45, 0.25)
    g = Group(sph)
    if label:
        t = Text(str(num + 1), font="Arial", font_size=max(14, int(r * 90))).set_color(WHITE)
        t.move_to(OUT * (r + 0.02))
        g.add(t)
    g.num = num
    return g


class Row:
    """Ряд шариков на полке. Ход — анимация: шарики, которые меняют место, перепрыгивают дугой над рядом."""

    def __init__(self, s, gap=0.85, r=0.3, center=ORIGIN, color=C_BALL, labels=True):
        self.s, self.n, self.gap, self.r = tuple(s), len(s), gap, r
        self.c = np.array(center, dtype=float)
        self.balls = {v: ball(v, r, color, labels) for v in self.s}
        for k, v in enumerate(self.s):
            self.balls[v].move_to(self.pos(k))
        w = gap * (self.n - 1) + 2.4 * r
        self.shelf = Line(self.c + LEFT * w / 2 + DOWN * 1.15 * r, self.c + RIGHT * w / 2 + DOWN * 1.15 * r)
        self.shelf.set_stroke(C_NOTE, 3, opacity=0.6)
        self.group = Group(self.shelf, *self.balls.values())

    def pos(self, k):
        return self.c + RIGHT * self.gap * (k - (self.n - 1) / 2)

    def move(self, g, lift=0.9):
        """Анимация хода g; расстановка обновляется сразу."""
        old = {v: k for k, v in enumerate(self.s)}
        self.s = apply(self.s, g)
        anims = []
        for k, v in enumerate(self.s):
            a, b = self.pos(old[v]), self.pos(k)
            if old[v] != k:
                h = lift * (1 if k > old[v] else -0.35)
                anims.append(UpdateFromAlphaFunc(self.balls[v], lambda m, t, a=a, b=b, h=h:
                                                 m.move_to(interpolate(a, b, t) + OUT * h * np.sin(PI * t))))
        return AnimationGroup(*anims)

    def set_to(self, s):
        self.s = tuple(s)
        return AnimationGroup(*[self.balls[v].animate.move_to(self.pos(k)) for k, v in enumerate(self.s)])

    def paint(self, color):
        return AnimationGroup(*[b[0].animate.set_color(color) for b in self.balls.values()])


# ---------- кольцо Глушкова ----------

def slot_pos(k, n, R, center=ORIGIN):
    """Место k на кольце: места 0 и 1 — наверху, по обе стороны от вертикали; дальше по часовой стрелке."""
    a = PI / 2 + PI / n - TAU * k / n
    return np.array(center) + R * np.array([np.cos(a), np.sin(a), 0])


class Ring:
    """Кольцо из прошлого ролика с двумя ходами Глушкова: поворот влево и обмен двух верхних шариков."""

    def __init__(self, s, R=1.8, r=0.32, center=ORIGIN, color=C_BALL, labels=True):
        self.s, self.n, self.R, self.r, self.c = tuple(s), len(s), R, r, np.array(center, dtype=float)
        self.rim = Circle(radius=R).move_to(self.c).set_stroke(C_NOTE, 3, opacity=0.6)
        self.balls = {v: ball(v, r, color, labels) for v in self.s}
        for k, v in enumerate(self.s):
            self.balls[v].move_to(self.pos(k))
        p0, p1 = self.pos(0), self.pos(1)
        w = RoundedRectangle(width=np.linalg.norm(p1 - p0) + 3.4 * r, height=3.4 * r, corner_radius=0.2)
        self.window = w.move_to((p0 + p1) / 2 + IN * 0.05).set_stroke(WHITE, 4).set_fill(WHITE, 0.08)
        self.group = Group(self.rim, self.window, *self.balls.values())

    def pos(self, k):
        return slot_pos(k, self.n, self.R, self.c)

    def left(self):
        n, start = self.n, {v: k for k, v in enumerate(self.s)}
        self.s = self.s[1:] + self.s[:1]

        def upd(m, a, k0):
            ang = PI / 2 + PI / n - TAU * k0 / n + TAU * a / n
            m.move_to(self.c + self.R * np.array([np.cos(ang), np.sin(ang), 0]))

        return AnimationGroup(*[UpdateFromAlphaFunc(self.balls[v], lambda m, a, k0=start[v]: upd(m, a, k0)) for v in start])

    def swap(self):
        a, b = self.balls[self.s[0]], self.balls[self.s[1]]
        p0, p1 = self.pos(0), self.pos(1)
        self.s = (self.s[1], self.s[0]) + self.s[2:]
        lift = OUT * 0.9
        return AnimationGroup(
            UpdateFromAlphaFunc(a, lambda m, t: m.move_to(interpolate(p0, p1, t) + lift * np.sin(PI * t))),
            UpdateFromAlphaFunc(b, lambda m, t: m.move_to(interpolate(p1, p0, t) - lift * np.sin(PI * t) * 0.3)))


# ---------- башня этажей ----------

def tower(n, gens, rise=0.5, spread=0.42, lines=True):
    """Башня расстановок: каждая — точка на своём этаже (высота = этаж · rise), этажи — кольца точек, ходы — линии.
    Возвращает (точки {расстановка: координата}, линии VGroup, словарь этажей, этажи по списку)."""
    d = floors(n, gens)
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
    ls = VGroup()
    if lines:
        seen = set()
        for s in d:
            for g in gens:
                t = apply(s, g)
                key = frozenset((s, t))
                if key not in seen and t != s:
                    seen.add(key)
                    ls.add(Line(pos[s], pos[t]).set_stroke(C_BALL, 1, opacity=0.22))
    return pos, ls, d, by


def tower_dots(pos, d, r=0.07):
    top = max(d.values())
    out = Group()
    for s, p in pos.items():
        col = C_ORDER if d[s] == 0 else C_TOP if d[s] == top else C_BALL
        out.add(Sphere(radius=r * (2.2 if d[s] in (0, top) else 1), resolution=(12, 6)).set_color(col).move_to(p))
    return out


def profile(sizes, width=2.4, step=0.16, color=C_BALL):
    """Профиль башни сбоку: этаж — горизонтальная полоска, ширина — сколько на нём расстановок (снизу вверх)."""
    mx = max(sizes)
    g = VGroup()
    for f, m in enumerate(sizes):
        col = C_ORDER if f == 0 else C_TOP if f == len(sizes) - 1 else color
        w = max(0.04, width * m / mx)
        g.add(Rectangle(width=w, height=step * 0.8).set_stroke(width=0).set_fill(col, 0.85).move_to(UP * f * step))
    return g


# ---------- рисунок ходов ----------

def move_picture(n, gens, colors, layout=None, R=0.18):
    """Ходы линиями между местами шариков: место — точка, ход — линии его цвета (i → g(i)); обмен — просто линия.
    layout — координаты мест (по умолчанию в ряд)."""
    pts = layout or [np.array([0.7 * (k - (n - 1) / 2), 0, 0]) for k in range(n)]
    dots = VGroup(*[Dot(p, radius=R * 0.6).set_color(WHITE) for p in pts])
    nums = VGroup(*[Text(str(k + 1), font="Arial", font_size=16).set_color(C_NOTE).next_to(p, DOWN, buff=0.12) for k, p in enumerate(pts)])
    edges = VGroup()  # по группе линий на ход
    for g, col in zip(gens, colors):
        done, eg = set(), VGroup()
        for i in range(n):
            j = g[i]
            if j == i or frozenset((i, j)) in done:
                continue
            done.add(frozenset((i, j)))
            eg.add(Line(pts[i], pts[j]).set_stroke(col, 5))
        edges.add(eg)
    return VGroup(edges, dots, nums)
