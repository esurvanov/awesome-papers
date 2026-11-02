"""Раскадровка ролика arXiv 2509.19162 (версия 2, мир — сортировочная станция): схематичный кадр на каждую фразу диктора.
Кадр — инфографика из элементов station.py; числа — посчитаны перебором (growth3d) или из статьи, как в паспорте.
Рисует: uv run python core/pipeline/animatic.py papers/2509.19162-growth --draw (или одна сцена: manimgl … storyboard.py A04 -s -w)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(HERE))
import random

import numpy as np
from manimlib import *
from manimkit import *
import passport as P
from growth3d import floors, growth, neighbours, star, glushkov, cycles4, perm, move_picture, profile
from station import *

GL = {5: 11, 6: 18, 7: 25, 8: 35, 9: 45, 10: 58, 11: 71, 12: 87}  # кольцевая станция: потолки (пересчитано)
STAR = {n: 3 * (n - 1) // 2 for n in range(3, 13)}                 # «головной с любым»


def c4_top(n):
    return n * (n - 1) // 6 + 1 if n % 3 != 2 else (n * (n - 1) + 4) // 6


# ---------- значки станций: те же в обзоре, в полосе «мы здесь» и на карточках приложения ----------

def icon_journal(s=1.0):
    book = RoundedRectangle(width=0.8, height=1.0, corner_radius=0.08).set_stroke(C_COMP, 3).set_fill(C_COMP, 0.12)
    lines = VGroup(*[Line(LEFT * 0.25, RIGHT * 0.25).set_stroke(C_COMP, 2).shift(UP * (0.25 - 0.17 * k)) for k in range(4)])
    return VGroup(book, lines).scale(s)


def icon_rhythm(s=1.0):
    return VGroup(*[Rectangle(width=0.16, height=0.09 * h).set_stroke(C_RHYTHM, 2).set_fill(C_RHYTHM, 0.9 if k % 2 == 0 else 0.3)
                    for k, h in enumerate([3, 4, 6, 7, 9, 10])]).arrange(RIGHT, buff=0.05, aligned_edge=DOWN).scale(s)


def icon_ring(s=1.0):
    return VGroup(Circle(radius=0.45).set_stroke(C_BALL, 3),
                  *[Square(0.16).set_fill(C_BALL, 0.9).set_stroke(width=0).move_to(0.45 * np.array([np.cos(a), np.sin(a), 0]))
                    for a in np.linspace(0, TAU, 6, endpoint=False)]).scale(s)


SQ = {2: (-0.5, 0.5), 3: (0.5, 0.5), 5: (0.5, -0.5), 6: (-0.5, -0.5), 0: (-1.4, -1.0), 4: (1.4, -1.0), 1: (2.2, -0.4)}


def record7():
    return [perm(7, [(2, 3), (5, 6)]), perm(7, [(1, 4), (2, 6), (3, 5)]), perm(7, [(0, 6), (2, 3), (4, 5)])]


def icon_records(s=1.0):
    pic = move_picture(7, record7(), [C_SWING] * 3, layout=[np.array([*SQ[k], 0]) * 0.33 for k in range(7)], R=0.12)
    pic.remove(pic[2])
    return pic.move_to(ORIGIN).scale(s)


def icon_compass(s=1.0):
    return compass(0.45).scale(s)


def icon_main(s=1.0):
    return VGroup(Circle(radius=0.45).set_stroke(C_ORDER, 3), check(C_ORDER, 0.22)).scale(s)


def icon_formal(s=1.0):
    box = RoundedRectangle(width=1.0, height=0.8, corner_radius=0.12).set_stroke(C_RHYTHM, 3)
    return VGroup(box, tx("f(n)", 26, C_RHYTHM).move_to(box)).scale(s)


ICONS = {"Все составы": icon_journal, "Формула": icon_rhythm, "Глушков": icon_ring, "Худшая станция": icon_records,
         "Проверка": icon_compass, "Итог": icon_main, "Как устроено": icon_formal}
Board = storyboard_base(P.STATIONS, P.SCENES, ICONS, HERE)


def by_floor(n, gens):
    d = floors(n, gens)
    out = {}
    for s, f in d.items():
        out.setdefault(f, []).append(s)
    return {f: sorted(v) for f, v in out.items()}


TOWER4 = by_floor(4, neighbours(4))


# ---------- акт 1 ----------

class A01(Board):
    def construct(self):
        fan = VGroup(*[rails(9, y).rotate(a, about_point=LEFT * 4.5 + UP * y) for y, a in [(1.2, 0.08), (0.4, 0.03), (-0.4, -0.03), (-1.2, -0.08)]])
        small = VGroup(*[train(random.Random(k).sample(range(1, 5), 4), w=0.45, h=0.28, gap=0.05).move_to([x, y + 0.2, 0])
                         for k, (x, y) in enumerate([(-1.5, 1.2), (1.8, 0.4), (-0.5, -0.4), (2.4, -1.2)])])
        tw = VGroup(*[Rectangle(width=w, height=0.18).set_stroke(C_NOTE, 2) for w in (0.4, 0.8, 1.0, 0.8, 0.4)]).arrange(UP, buff=0.05).move_to(RIGHT * 5.3 + UP * 0.8)
        self.add(title2("Сортировочная станция"), fan, small, tw, tx("диспетчерская", 18, C_NOTE).next_to(tw, DOWN, buff=0.1))
        self.snap()
        self.clear_keep_bar()
        t = train([3, 1, 5, 2, 4]).move_to(UP * 0.25)
        self.add(rails(10, -0.07), t, tx("состав", 26, C_BALL).next_to(t, DOWN, buff=0.35))
        self.snap()
        goal = train([1, 2, 3, 4, 5], C_ORDER).set_opacity(0.35).move_to(UP * 1.7)
        self.add(dispatcher().move_to(LEFT * 4.8 + UP * 0.3), goal, tx("цель — по порядку", 22, C_ORDER).next_to(goal, UP, buff=0.12))
        self.snap()
        no = VGroup(*[VGroup(move_icon(k, C_NOTE), cross(C_NO, 0.18)) for k in ("головной", "по кругу")]).arrange(RIGHT, buff=0.4)
        sg = sign("станция «соседи»", [move_icon("соседи")]).move_to(RIGHT * 4.6 + DOWN * 1.2)
        self.add(sg, VGroup(tx("нельзя:", 18, C_NOTE), no).arrange(RIGHT, buff=0.2).scale(0.8).next_to(sg, LEFT, buff=0.4))
        self.snap()
        self.remove(t)
        t2 = train([3, 5, 1, 2, 4], colors={5: C_SWING, 1: C_SWING}).move_to(UP * 0.25)
        arc = ArcBetweenPoints(t2[0][1].get_top(), t2[0][2].get_top(), angle=-PI / 2).add_tip().set_color(C_SWING)
        self.add(t2, arc, pill("манёвр 1", C_SWING, 22).move_to(LEFT * 2.9 + DOWN * 1.2))
        self.snap()
        self.clear_keep_bar()
        q = tx("Сколько манёвров нужно", 40).move_to(UP * 1.9)
        q2 = tx("на самый запутанный состав?", 40).next_to(q, DOWN, buff=0.15)
        hard = train([5, 4, 3, 2, 1], C_TOP).move_to(DOWN * 0.3)
        self.add(q, q2, hard)
        self.snap()
        many = VGroup(*[mini_train(random.Random(k).sample(range(5), 5), C_BALL, 0.17) for k in range(24)]).arrange_in_grid(4, 6, buff=0.25)
        many.scale(0.9).move_to(DOWN * 1.3)
        self.remove(hard)
        self.add(many, tx("…и можно ли узнать, не пробуя все составы?", 24, C_NOTE).next_to(many, UP, buff=0.2))
        self.snap()
        self.add(pill("для компьютера — из самых трудных задач", C_NO, 24).move_to(DOWN * 2.6))
        self.snap()
        self.clear_keep_bar()
        line = Line(LEFT * 5, RIGHT * 5).set_stroke(C_NOTE, 2).shift(DOWN * 0.6)
        dot = Dot(LEFT * 2.5 + DOWN * 0.6, radius=0.12).set_color(WHITE)
        self.add(line, dot, tx("1968", 36).next_to(dot, UP, buff=0.2), tx("кибернетик Глушков", 26, C_NOTE).next_to(dot, DOWN, buff=0.2),
                 ring_track([1, 2, 3, 4, 5, 6], R=1.1, switch=False).move_to(RIGHT * 2.6 + UP * 0.4).set_opacity(0.6))
        self.snap()


class A02(Board):
    def construct(self):
        card = RoundedRectangle(width=11.4, height=5.0, corner_radius=0.2).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.06).move_to(UP * 0.1)
        head = VGroup(tx("arXiv 2509.19162 · проект CayleyPy · 49 авторов", 22, C_NOTE),
                      tx("CayleyPy Growth: быстрый подсчёт роста", 30), tx("и сотни новых гипотез о графах Кэли", 30)).arrange(DOWN, buff=0.12)
        head.move_to(card.get_top() + DOWN * 0.95)
        self.add(card, head)
        self.snap()
        cube = VGroup(*[Square(0.16).set_stroke(C_BALL, 1.5) for _ in range(9)]).arrange_in_grid(3, 3, buff=0.04)
        ser = VGroup(VGroup(cube, tx("кубики", 18, C_NOTE)).arrange(DOWN, buff=0.08), VGroup(icon_ring(0.6), tx("кольцо", 18, C_NOTE)).arrange(DOWN, buff=0.08),
                     VGroup(icon_journal(0.6), tx("станции · эта статья", 18, WHITE)).arrange(DOWN, buff=0.08)).arrange(RIGHT, buff=0.9)
        arr = VGroup(*[Arrow(ser[k].get_right(), ser[k + 1].get_left(), buff=0.1).set_color(C_NOTE) for k in range(2)])
        VGroup(ser, arr).move_to(card.get_center() + DOWN * 0.15)
        self.add(ser, arr)
        self.snap()
        self.add(tx("23 сентября 2025 · версия 2 — 1 апреля 2026", 22, C_NOTE).move_to(card.get_center() + DOWN * 1.05))
        self.snap()
        g = VGroup(pill("составы — во много раз быстрее", C_BALL, 22), tx("→", 26, C_NOTE), pill("ответ — простые формулы", C_RHYTHM, 22),
                   tx("→", 26, C_NOTE), pill("≈ 200 гипотез", C_TOP, 22)).arrange(RIGHT, buff=0.2).move_to(card.get_center() + DOWN * 1.85)
        self.add(g[0])
        self.snap()
        self.add(g[1:])
        self.snap()


QUESTIONS = [("Все составы", "как записать все составы,", "даже если их триллионы?"),
             ("Формула", "можно ли посчитать ответ", "формулой, не записывая?"),
             ("Глушков", "что нашли на вопрос", "Глушкова 1968 года?"),
             ("Худшая станция", "какая станция хуже всех?", "есть ли общий предел?"),
             ("Проверка", "как проверить там,", "где записать всё нельзя?"),
             ("Итог", "что из этого", "следует")]


class A03(Board):
    def construct(self):
        self.add(title2("Шесть вопросов"))
        boxes = VGroup(*[RoundedRectangle(width=4.1, height=1.55, corner_radius=0.15).set_stroke(C_NOTE, 1.5).set_fill(C_NOTE, 0.04)
                         for _ in range(6)]).arrange_in_grid(2, 3, buff=0.25).move_to(UP * 0.55)
        self.add(boxes)
        self.snap()
        icons = VGroup()
        for k, ((st, q1, q2), b) in enumerate(zip(QUESTIONS, boxes)):
            ic = ICONS[st](0.62)
            body = VGroup(tx(str(k + 1), 26, WHITE), VGroup(tx(q1, 19), tx(q2, 19)).arrange(DOWN, aligned_edge=LEFT, buff=0.06)).arrange(RIGHT, buff=0.25)
            row = VGroup(ic, body).arrange(RIGHT, buff=0.25)
            row.set_width(min(row.get_width(), b.get_width() - 0.35)).move_to(b)
            b.set_stroke(WHITE, 2)
            self.add(row)
            icons.add(ic)
            if k == 5:
                app = VGroup(icon_formal(0.45), tx("в конце: те же вопросы формулами и как это устроено", 20, C_RHYTHM)).arrange(RIGHT, buff=0.25)
                self.add(app.next_to(boxes, DOWN, buff=0.25))
            self.snap()
        xs = np.linspace(-6.0, 6.0, len(P.STATIONS))
        rings = VGroup(*[Circle(radius=0.27).set_stroke(WHITE, 3).move_to([xs[P.STATIONS.index(st)], -3.17, 0]) for st, *_ in QUESTIONS])
        self.add(rings, tx("те же значки — внизу, в полосе «мы здесь»", 20, WHITE).move_to(DOWN * 2.6))
        self.snap(allow=[rings])


class A04(Board):
    def construct(self):
        sg = sign("станция «соседи»", [move_icon("соседи")]).scale(0.8).move_to(LEFT * 5.2 + UP * 1.3)
        self.add(title2("Маленькая станция"), rails(4.2, -1.6).shift(LEFT * 4.3), sg)
        self.snap()
        t = train([1, 3, 2, 4], colors={3: C_SWING, 2: C_SWING}).scale(0.75).move_to(LEFT * 4.3 + DOWN * 1.35)
        arc = ArcBetweenPoints(t[0][1].get_top(), t[0][2].get_top(), angle=-PI / 2).add_tip().set_color(C_SWING)
        self.add(t, arc, tx("4 вагона", 22, C_BALL).next_to(t, DOWN, buff=0.35))
        self.snap()
        tower, plates, rows = tower2d(TOWER4, height=5.0, width=5.4)
        tower.scale(0.92).move_to(RIGHT * 3.4 + UP * 0.05)
        for r in rows:
            r.set_opacity(0)
        self.add(tower, tx("вышка", 24, WHITE).next_to(tower, UP, buff=0.05))
        self.snap()
        rows[2][TOWER4[2].index((1, 0, 3, 2))].set_opacity(1)
        steps = VGroup(mini_train((1, 0, 3, 2), C_BALL, 0.24), mini_train((0, 1, 3, 2), C_BALL, 0.24), mini_train((0, 1, 2, 3), C_ORDER, 0.24))
        steps.arrange(DOWN, buff=0.35).move_to(LEFT * 1.3 + UP * 1.0)
        arrs = VGroup(*[Arrow(steps[k].get_bottom(), steps[k + 1].get_top(), buff=0.05).set_color(WHITE) for k in range(2)])
        self.add(steps, arrs, tx("этаж 2 = 2 манёвра", 22, WHITE).next_to(steps, DOWN, buff=0.25),
                 SurroundingRectangle(rows[2][TOWER4[2].index((1, 0, 3, 2))], buff=0.05).set_stroke(WHITE, 2))
        self.snap()
        self.remove(steps, arrs, *[m for m in self.mobjects if isinstance(m, Text) and "этаж 2" in m.text])
        rows[0].set_opacity(1)
        self.add(tx("порядок · этаж 0", 20, C_ORDER).next_to(rows[0], RIGHT, buff=0.3))
        self.snap()
        rows[1].set_opacity(1)
        self.add(SurroundingRectangle(rows[1], buff=0.08).set_stroke(C_SWING, 2),
                 tx("3 состава: перепутаны два соседа", 20, C_SWING).move_to(LEFT * 1.6 + DOWN * 0.2))
        self.snap()
        for r in rows:
            r.set_opacity(1)
        cnt = VGroup(*[tx(str(len(TOWER4[f])), 20, C_NOTE).next_to(plates[f], RIGHT, buff=0.15) for f in sorted(TOWER4)])
        self.remove(*[m for m in self.mobjects if isinstance(m, Text) and m.text == "Маленькая станция"])
        self.add(cnt, title2("справа — сколько составов на этаже", 28))
        self.snap()


def tower_scene_base(self, scale=0.95, x=-2.8):
    tower, plates, rows = tower2d(TOWER4, height=5.0, width=5.6)
    tower.scale(scale).move_to(RIGHT * x + UP * 0.05)
    self.add(tower)
    return tower, plates, rows


class A05(Board):
    def construct(self):
        tower, plates, rows = tower_scene_base(self)
        self.add(tx("потолок", 26, C_TOP).next_to(plates[6], UP, buff=0.35), title2("Потолок"))
        self.snap()
        big = train([4, 3, 2, 1], C_TOP).scale(0.9).move_to(RIGHT * 3.2 + UP * 1.6)
        self.add(big)
        self.snap()
        seq = [(3, 2, 1, 0), (2, 3, 1, 0), (2, 1, 3, 0), (1, 2, 3, 0), (1, 2, 0, 3), (1, 0, 2, 3), (0, 1, 2, 3)]
        col = VGroup(*[VGroup(tx(str(k), 18, C_NOTE), mini_train(p, C_ORDER if k == 6 else C_BALL, 0.22)).arrange(RIGHT, buff=0.2)
                       for k, p in enumerate(seq)]).arrange(DOWN, buff=0.1, aligned_edge=LEFT).next_to(big, DOWN, buff=0.3)
        self.add(col, pill("6 манёвров", C_TOP, 22).next_to(col, RIGHT, buff=0.3))
        self.snap()
        self.clear_keep_bar()
        tower, plates, rows = tower_scene_base(self, 0.85, -3.6)
        jr = journal([], w=4.4, h=4.6).move_to(RIGHT * 2.6 + DOWN * 0.1)
        self.add(dispatcher().move_to(LEFT * 0.4 + DOWN * 1.6), jr)
        self.snap()

        def line(f):
            return VGroup(tx(f"этаж {f}:", 18, C_NOTE), *[mini_train(p, C_BALL, 0.15) for p in TOWER4[f][:3]]).arrange(RIGHT, buff=0.15)

        lines = VGroup(line(0), line(1)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(jr[2], DOWN, buff=0.25).align_to(jr[0], LEFT).shift(RIGHT * 0.5)
        self.add(lines)
        self.snap()
        src = rows[1][1]
        arrs = VGroup(*[Arrow(src.get_top(), rows[2][k].get_bottom(), buff=0.03).set_color(WHITE).set_stroke(width=2) for k in range(3)])
        self.add(SurroundingRectangle(src, buff=0.05).set_stroke(WHITE, 2), arrs, tx("все манёвры", 18, WHITE).next_to(arrs, RIGHT, buff=0.1))
        self.snap()
        new = line(2).next_to(lines, DOWN, buff=0.15, aligned_edge=LEFT)
        self.add(new, SurroundingRectangle(new, buff=0.05).set_stroke(C_ORDER, 2), tx("новый → следующий этаж", 18, C_ORDER).next_to(new, DOWN, buff=0.1))
        self.snap()
        dup = VGroup(tx("повтор:", 18, C_NOTE), mini_train(TOWER4[1][0], C_NOTE, 0.15)).arrange(RIGHT, buff=0.15).next_to(new, DOWN, buff=0.55, aligned_edge=LEFT)
        self.add(dup, Line(dup.get_left(), dup.get_right()).set_stroke(C_NO, 4), tx("уже есть — пропускаем", 16, C_NO).next_to(dup, DOWN, buff=0.1, aligned_edge=LEFT))
        self.snap()


class A06(Board):
    def construct(self):
        t = train(list(range(1, 16)), w=0.72, h=0.45, gap=0.1)
        t.set_width(13.2).move_to(UP * 0.6)
        self.add(title2("Станции бывают больше"), rails(13.6, 0.33), t, tx("15 вагонов", 26, C_BALL).move_to(UP * 1.65))
        self.snap()
        self.add(VGroup(tx("составов:", 26, C_NOTE), tx("1 307 674 368 000", 44, C_BALL)).arrange(RIGHT, buff=0.3).move_to(DOWN * 0.8),
                 tx("больше триллиона", 22, C_BALL).move_to(DOWN * 1.45))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Если по составу в секунду"), calendar("> 40 000 лет", WHITE, 4).scale(1.4).move_to(LEFT * 3 + DOWN * 0.1))
        self.snap()
        self.add(calendar("программа авторов: несколько дней", C_ORDER, 3).scale(1.2).move_to(RIGHT * 2.8 + DOWN * 0.1))
        self.snap()
        self.clear_keep_bar()
        sw = VGroup(stopwatch("прежняя: 39 мин", C_NOTE, 0.65).scale(1.5), stopwatch("новая: 0,6 с", C_ORDER, 0.01).scale(1.5)).arrange(RIGHT, buff=2.5)
        self.add(title2("11 вагонов, одна и та же работа"), sw.move_to(DOWN * 0.1), tx("медленнее до тысячи раз", 26, C_NO).move_to(DOWN * 2.3))
        self.snap()


# ---------- акт 2 ----------

class A07(Board):
    def construct(self):
        sets = [neighbours(4), star(4), glushkov(4), neighbours(5), star(5), glushkov(5)]
        shelf = VGroup(*[profile(growth(len(g[0]), g), width=0.7, step=0.07) for g in sets * 2]).arrange(RIGHT, buff=0.3, aligned_edge=DOWN)
        shelf.move_to(UP * 0.6)
        self.add(title2("Полсотни станций"), shelf, Line(shelf.get_corner(DL) + DOWN * 0.05, shelf.get_corner(DR) + DOWN * 0.05).set_stroke(C_NOTE, 3))
        self.snap()
        books = VGroup(*[icon_journal(0.35) for _ in range(12)]).arrange(RIGHT, buff=0.36).next_to(shelf, DOWN, buff=0.35)
        self.add(books, tx("у каждой — составы разной длины", 22, C_NOTE).next_to(books, DOWN, buff=0.2))
        self.snap()
        self.clear_keep_bar()
        sg = sign("станция «головной с любым»", [move_icon("головной")]).scale(0.8).move_to(LEFT * 4.6 + UP * 1.6)
        t = train([3, 2, 1, 4, 5], colors={3: C_SWING, 1: C_SWING}).scale(0.7).move_to(RIGHT * 1.0 + UP * 1.9)
        self.add(sg, t, ArcBetweenPoints(t[0][0].get_top(), t[0][2].get_top(), angle=-PI / 2).add_tip().set_color(C_SWING))
        self.snap()
        ns = list(STAR)
        vals = [STAR[n] for n in ns]
        b = bars(vals, [C_BALL] * len(vals), x0=-3.8, step=0.85, scale=0.17, y0=-2.3, labels=ns)
        self.add(b, tx("потолок", 20, C_NOTE).next_to(b, LEFT, buff=0.2), tx("вагонов", 18, C_NOTE).next_to(b, DOWN, buff=0.05).shift(RIGHT * 4))
        self.snap()
        for k, n in enumerate(ns):
            col = C_RHYTHM if n % 2 else C_BALL
            b[k][0].set_stroke(col).set_fill(col, 0.75)
            b[k][1].set_color(col)
        steps = VGroup(*[tx(f"+{vals[k + 1] - vals[k]}", 18, C_RHYTHM if vals[k + 1] - vals[k] == 2 else C_BALL)
                         .move_to([-3.8 + (k + 0.5) * 0.85, -2.3 + max(vals[k], vals[k + 1]) * 0.17 + 0.55, 0]) for k in range(len(vals) - 1)])
        leg = VGroup(pill("нечётные", C_RHYTHM, 20), pill("чётные", C_BALL, 20)).arrange(DOWN, buff=0.1).move_to(RIGHT * 5.0 + DOWN * 0.3)
        steps.overlay = True
        self.add(steps, leg)
        self.snap()
        self.add(metronome(2).move_to(RIGHT * 5.0 + UP * 1.3), pill("ритм", C_RHYTHM, 30).move_to(RIGHT * 3.4 + UP * 2.4))
        self.snap()


class A08(Board):
    def construct(self):
        self.add(pill("главная гипотеза", C_RHYTHM, 32).move_to(UP * 2.2))
        self.snap()
        ch = VGroup(pill("простое правило станции", C_BALL, 24), tx("→", 30, C_NOTE), pill("потолок = формула с ритмом", C_RHYTHM, 24)).arrange(RIGHT, buff=0.3)
        self.add(ch.move_to(UP * 1.1))
        self.snap()
        self.add(VGroup(*[metronome(k, s=0.8) for k in (4, 6, 8)]).arrange(RIGHT, buff=1.0).move_to(DOWN * 0.6))
        self.snap()
        self.clear_keep_bar()
        self.add(VGroup(warn_icon(C_NO, 0.4), tx("в общем случае потолок заранее не узнать", 30, C_NO)).arrange(RIGHT, buff=0.3).move_to(UP * 1.9))
        self.snap()
        vals = [3 * (n - 1) // 2 for n in range(3, 17)]
        b = bars(vals[:7], [C_RHYTHM if n % 2 else C_BALL for n in range(3, 10)], x0=-5.2, step=0.7, scale=0.15, y0=-2.3, show_values=False)
        w = wall(-5.2 + 6.5 * 0.7, "предел журнала", y0=-2.3, h=2.6)
        ghost = VGroup(*[DashedVMobject(Rectangle(width=0.5, height=v * 0.15), num_dashes=20).set_stroke(C_RHYTHM, 2)
                         .move_to([-5.2 + (k + 7) * 0.7, -2.3 + v * 0.075, 0]) for k, v in enumerate(vals[7:])])
        chain = VGroup(pill("маленькие станции", C_BALL, 20), tx("→", 24, C_NOTE), pill("услышать ритм", C_RHYTHM, 20), tx("→", 24, C_NOTE),
                       pill("формула дальше", C_RHYTHM, 20)).arrange(RIGHT, buff=0.15).move_to(UP * 1.25)
        ghost.overlay = True
        self.add(b, *w, ghost, chain)
        self.snap()


class A09(Board):
    def construct(self):
        line = Line(LEFT * 5, RIGHT * 0).set_stroke(C_NOTE, 2).shift(UP * 0.0)
        self.add(line, Dot(LEFT * 3, radius=0.1), tx("1968 · Глушков", 26).next_to(LEFT * 3, UP, buff=0.25),
                 Arrow(LEFT * 0.4, RIGHT * 1.0).set_color(C_NOTE), ring_track([1, 2, 3, 4, 5, 6], R=1.3).move_to(RIGHT * 3.2))
        self.snap()
        self.clear_keep_bar()
        ring = ring_track([1, 2, 3, 4, 5, 6], R=1.7).move_to(LEFT * 1.5 + DOWN * 0.1)
        self.add(title2("Кольцевая станция"), ring)
        self.snap()
        rot = Arc(-PI / 3, -PI / 2.2, radius=2.4).add_tip().set_color(C_BALL).move_arc_center_to(ring[0].get_center())
        sw = ArcBetweenPoints(ring[1][0].get_center() + UP * 0.35, ring[1][1].get_center() + UP * 0.35, angle=-PI / 2).add_tip().set_color(C_SWING)
        m = VGroup(VGroup(move_icon("по кругу"), tx("1 · прокатить на место вперёд", 22)).arrange(RIGHT, buff=0.3),
                   VGroup(move_icon("соседи", C_SWING), tx("2 · поменять у стрелки", 22, C_SWING)).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        self.add(rot, sw, m.move_to(RIGHT * 3.6 + UP * 0.2))
        self.snap()
        self.clear_keep_bar()
        ns = list(GL)
        b = bars([GL[n] for n in ns], [C_RHYTHM if n % 2 else C_BALL for n in ns], x0=-3.6, step=0.95, scale=0.045, y0=-2.3, labels=ns)
        leg = VGroup(pill("нечётные — формула 1", C_RHYTHM, 18), pill("чётные — формула 2", C_BALL, 18)).arrange(DOWN, buff=0.1).move_to(LEFT * 5.4 + UP * 2.0)
        self.add(b, leg, tx("вагонов", 18, C_NOTE).next_to(b, DOWN, buff=0.05))
        self.snap()
        self.add(*[check(C_ORDER, 0.1).next_to(item[1], UP, buff=0.08) for item in b],
                 tx("пересчитали сами: до 12 вагонов", 22, C_ORDER).move_to(RIGHT * 2.6 + UP * 2.2))
        self.snap()
        self.add(pill("на октябрь 2026 — гипотеза", C_COMP, 18).move_to(LEFT * 5.4 + UP * 0.8))
        self.snap()


class A10(Board):
    def construct(self):
        gl = profile(growth(6, glushkov(6)), width=3.6, step=0.26).move_to(RIGHT * 2.8 + DOWN * 0.1)
        self.add(title2("Форма вышки"), gl, tx("кольцевая · 6 вагонов", 22, C_BALL).next_to(gl, DOWN, buff=0.15))
        self.snap()
        fib = growth(6, glushkov(6))[:6]
        labs = VGroup(*[tx(str(v), 18, C_RHYTHM).next_to(gl[k], LEFT, buff=0.25) for k, v in enumerate(fib)])
        cap = tx("каждый = сумма двух предыдущих", 20, C_RHYTHM).next_to(labs, LEFT, buff=0.3)
        labs.overlay = cap.overlay = True
        self.add(labs, cap)
        self.snap()
        self.remove(*[m for m in self.mobjects if isinstance(m, Text) and "сумма" in m.text])
        nb = profile(growth(6, neighbours(6)), width=3.6, step=0.26).move_to(LEFT * 3.0 + DOWN * 0.2)
        self.add(nb, tx("«соседи» · 6 вагонов", 22, C_BALL).next_to(nb, DOWN, buff=0.15))
        self.snap()
        sizes = growth(6, neighbours(6))
        mx = max(sizes)
        left = [nb[k].get_left() + LEFT * 0.05 for k in range(len(sizes))]
        right = [nb[k].get_right() + RIGHT * 0.05 for k in range(len(sizes))]
        bell = VMobject().set_points_smoothly(left + right[::-1] + [left[0]]).set_stroke(WHITE, 3)
        bell.overlay = True
        self.add(bell, DashedLine(nb.get_bottom(), nb.get_top()).set_stroke(C_NOTE, 2), pill("колокол", C_BALL, 24).next_to(nb, UP, buff=0.2))
        self.snap()
        top = gl[-1]
        self.add(Arrow(top.get_right() + RIGHT * 1.4 + UP * 0.4, top.get_right() + RIGHT * 0.1, buff=0.05).set_color(C_TOP),
                 tx("обрыв", 22, C_TOP).next_to(top, RIGHT, buff=1.5).shift(UP * 0.4),
                 tx("широко у потолка", 20, C_TOP).next_to(gl[13], RIGHT, buff=0.2), pill("перекос", C_TOP, 24).next_to(gl, UP, buff=0.2))
        self.snap()
        self.remove(*[m for m in self.mobjects if isinstance(m, Text) and m.text == "Форма вышки"])
        self.add(title2("авторы: перекос — при любой длине состава", 28).move_to(UP * 3.35))
        self.snap()


class A11(Board):
    def construct(self):
        hs = [12, 16, 10, 21, 14, 30, 18, 15]
        cols = [C_SWING if h == 30 else C_BALL for h in hs]
        b = bars(hs, cols, x0=-4.2, step=1.2, scale=0.1, y0=-2.2, show_values=False)
        self.add(title2("Самая неудобная станция?"), b, pill("рекорд", C_SWING, 22).next_to(b[5], UP, buff=0.15), tx("схема", 16, C_NOTE).next_to(b, RIGHT))
        self.snap()
        self.add(VGroup(pill("до 9 вагонов — все подряд", C_NOTE, 20), pill("дальше — выборочно", C_NOTE, 20)).arrange(RIGHT, buff=0.3).move_to(UP * 2.15))
        self.snap()
        self.clear_keep_bar()
        g = record7()[1]
        t1 = train([1, 2, 3, 4, 5, 6, 7], w=0.6, h=0.4).move_to(UP * 1.6)
        t2 = train([1 + g[k] for k in range(7)], w=0.6, h=0.4, colors={v: C_SWING for v in range(1, 8)}).move_to(UP * 0.1)
        t3 = train([1, 2, 3, 4, 5, 6, 7], w=0.6, h=0.4).move_to(DOWN * 1.4)
        self.add(t1, t2, t3, Arrow(t1.get_bottom(), t2.get_top(), buff=0.08).set_color(C_SWING), Arrow(t2.get_bottom(), t3.get_top(), buff=0.08).set_color(C_SWING),
                 tx("⇄ тот же манёвр", 20, C_SWING).next_to(t2, RIGHT, buff=0.3), pill("качели: дважды — как было", C_SWING, 22).move_to(DOWN * 2.6))
        self.snap()
        self.clear_keep_bar()
        row = move_picture(7, record7(), [C_SWING, C_BALL, WHITE], layout=[np.array([0.55 * (k - 3), 0, 0]) for k in range(7)], R=0.14).move_to(LEFT * 3.8 + UP * 0.6)
        sq = move_picture(7, record7(), [C_SWING, C_BALL, WHITE], layout=[np.array([*SQ[k], 0]) * 1.05 for k in range(7)], R=0.16).move_to(RIGHT * 2.4 + UP * 0.3)
        self.add(tx("схема путей: место — точка, манёвр — линии", 22, WHITE).move_to(UP * 2.3), row, Arrow(row.get_right(), sq.get_left(), buff=0.3).set_color(C_NOTE), sq,
                 pill("квадрат с усами", C_SWING, 26).next_to(sq, DOWN, buff=0.35))
        self.snap()


class A12(Board):
    def construct(self):
        self.add(pill("предел для любой станции?", C_TOP, 30).move_to(UP * 2.2))
        self.snap()
        n, c = 6, LEFT * 3.6 + DOWN * 0.3
        pts = [c + 1.5 * np.array([np.cos(PI / 2 - TAU * k / n), np.sin(PI / 2 - TAU * k / n), 0]) for k in range(n)]
        ch = VGroup(*[Line(pts[i], pts[j]).set_stroke(C_ORDER, 2) for i in range(n) for j in range(i + 1, n)])
        cars = VGroup(*[wagon(k + 1, C_BALL, 0.5, 0.36).move_to(p) for k, p in enumerate(pts)])
        self.add(ch, cars, tx("пар: 15", 26, C_ORDER).next_to(cars, DOWN, buff=0.25))
        self.snap()
        f = VGroup(tx("потолок не выше", 24), VGroup(pill("число пар", C_ORDER, 24), tx("+", 30), pill("4,5 манёвра на вагон", C_TOP, 24)).arrange(RIGHT, buff=0.2)).arrange(DOWN, buff=0.15)
        self.add(f.move_to(RIGHT * 2.6 + UP * 1.1))
        self.snap()
        x, y0, sc = 2.6, -2.3, 0.015
        lim = DashedLine([x - 1.5, y0 + 150 * sc, 0], [x + 1.5, y0 + 150 * sc, 0]).set_stroke(C_TOP, 4)
        rec = Rectangle(width=1.0, height=148 * sc).set_fill(C_SWING, 0.8).set_stroke(width=0).move_to([x, y0 + 148 * sc / 2, 0])
        self.add(lim, tx("предел 150", 20, C_TOP).next_to(lim, RIGHT, buff=0.1), rec, tx("рекорд · 15 вагонов · 148", 20, C_SWING).next_to(rec, LEFT, buff=0.2),
                 tx("не хватило 2", 20, C_TOP).next_to(lim, UP, buff=0.05))
        self.snap()
        self.add(VGroup(pill("прежде: ≈ вдвое выше", C_NOTE, 20), tx("и даже не доказан", 20, C_NO)).arrange(DOWN, buff=0.1).move_to(LEFT * 5.6 + UP * 1.75))
        self.snap()


class A13(Board):
    def construct(self):
        jr = journal(["этаж 0 …", "этаж 1 …", "этаж 2 …", "…", "…"], w=3.6, h=4.2).move_to(LEFT * 2.5)
        self.add(title2("Журнал упирается в память"), jr, *wall(0.5, "память", y0=-2.4, h=4.6))
        self.snap()
        self.clear_keep_bar()
        prof = profile(growth(6, glushkov(6)), width=3.0, step=0.22).move_to(LEFT * 3 + DOWN * 0.2)
        cp = compass(0.5).next_to(prof, UP, buff=0.2)
        path = VGroup(*[Arrow(prof[k + 1].get_center(), prof[k].get_center(), buff=0.02).set_color(C_COMP).set_stroke(width=3) for k in range(len(prof) - 1)])
        self.add(prof, cp, path, tx("угадывает этаж и ведёт вниз", 24, C_COMP).move_to(RIGHT * 2.4 + UP * 0.6))
        self.snap()
        self.clear_keep_bar()
        n = 4
        pts = [0.9 * np.array([np.cos(a), np.sin(a), 0]) for a in np.arange(n) * PI / 2 + PI / 4]
        circ = VGroup(Circle(radius=0.9).set_stroke(C_NOTE, 3), *[wagon(k + 1, C_BALL, 0.55, 0.38).move_to(p) for k, p in enumerate(pts)])
        rot = Arc(0, PI * 1.5, radius=1.5).add_tip().set_color(C_BALL)
        self.add(title2("Поворотный круг на 4 вагона"), VGroup(circ, rot).move_to(DOWN * 0.1))
        self.snap()
        self.clear_keep_bar()
        ns = list(range(6, 21))
        vals = [c4_top(k) for k in ns]
        b = bars(vals[:8], [C_BALL] * 8, x0=-5.4, step=0.7, scale=0.045, y0=-2.3, show_values=False)
        w = wall(-5.4 + 7.5 * 0.7, "память", y0=-2.3, h=3.5)
        ghost = VGroup(*[DashedVMobject(Rectangle(width=0.5, height=v * 0.045), num_dashes=20).set_stroke(C_RHYTHM, 2)
                         .move_to([-5.4 + (k + 8) * 0.7, -2.3 + v * 0.0225, 0]) for k, v in enumerate(vals[8:])])
        ghost.overlay = True
        self.add(b, *w, ghost, tx("формула потолка дальше", 22, C_RHYTHM).move_to(LEFT * 3.3 + UP * 2.0))
        self.snap()
        cb = VGroup(*[Rectangle(width=0.4, height=v * 0.045).set_fill(C_COMP, 0.8).set_stroke(width=0).move_to([-5.4 + (k + 8) * 0.7, -2.3 + v * 0.0225, 0])
                      for k, v in enumerate(vals[8:])])
        self.add(cb, compass(0.4).move_to(RIGHT * 5.5 + UP * 1.9), VGroup(check(C_ORDER, 0.14), tx("путь компаса = формула", 24, C_ORDER)).arrange(RIGHT).move_to(UP * 1.4 + LEFT * 3.3))
        self.snap()


class A14(Board):
    def construct(self):
        self.add(title2("А чат-боты?"), chat_window(["…"]).move_to(UP * 0.6))
        self.snap()
        self.clear_keep_bar()
        win = chat_window(["напиши программу:", "собери любой состав", "только манёврами этой станции"]).move_to(UP * 1.0)
        self.add(title2("А чат-боты?"), win, sign("станция", [move_icon("соседи"), move_icon("головной")]).scale(0.7).next_to(win, RIGHT, buff=0.4))
        self.snap()
        self.add(VGroup(pill("▶ запустить", C_ORDER, 22), check(C_ORDER, 0.15), tx("проверить легко", 22, C_ORDER)).arrange(RIGHT, buff=0.25).move_to(DOWN * 0.9))
        self.snap()
        self.add(VGroup(check(C_ORDER, 0.14), tx("известные станции — программу пишут", 22, C_ORDER)).arrange(RIGHT, buff=0.2).move_to(DOWN * 1.6))
        self.snap()
        self.add(VGroup(cross(C_NO, 0.14), tx("новые — даже правильной нет (на момент статьи)", 22, C_NO)).arrange(RIGHT, buff=0.2).move_to(DOWN * 2.2))
        self.snap()
        self.add(pill("экзамен для ИИ", C_COMP, 26).move_to(DOWN * 0.9 + RIGHT * 4.9))
        self.snap()


class A15(Board):
    def construct(self):
        prof = profile(growth(6, glushkov(6)), width=3.2, step=0.24).move_to(LEFT * 4.0 + DOWN * 0.3)
        self.add(tx("Сколько манёвров на самый запутанный состав?", 28).move_to(UP * 2.7), prof)
        self.snap()
        rows = [(icon_rhythm(0.45), "простое правило → формула с ритмом", C_RHYTHM), (icon_ring(0.4), "станция Глушкова: формула есть", C_BALL),
                (icon_records(0.35), "предел: пары + 4,5 манёвра на вагон", C_TOP)]
        items = [VGroup(i, tx(t, 24, c)).arrange(RIGHT, buff=0.25) for i, t, c in rows]
        VGroup(*items).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(RIGHT * 1.8 + UP * 0.6)
        self.add(pill("похоже, да", C_ORDER, 28).move_to(RIGHT * 1.8 + UP * 2.0), items[0])
        self.snap()
        self.add(items[1])
        self.snap()
        self.add(items[2], DashedLine(prof.get_corner(UL) + UP * 0.4, prof.get_corner(UR) + UP * 0.4).set_stroke(C_TOP, 3))
        self.snap()
        self.add(VGroup(warn_icon(C_COMP, 0.25), tx("на октябрь 2026 — гипотезы: журналы и компас, без доказательства", 22, C_COMP)).arrange(RIGHT, buff=0.2).move_to(DOWN * 2.7))
        self.snap()


# ---------- приложение: формулы по фразам ----------

def card(self, station, title, picture, items):
    """Карточка приложения: значок станции слева, формулы справа; items — по элементу на фразу (None — без нового элемента)."""
    chip = VGroup(ICONS.get(station, icon_formal)(0.45), tx(f"пара к «{station}»", 20, C_NOTE)).arrange(RIGHT, buff=0.2).move_to(LEFT * 4.6 + UP * 2.75)
    self.add(chip, tx(title, 34).move_to(UP * 2.75 + RIGHT * 1.0), picture.move_to(LEFT * 4.8 + UP * 0.1))
    y = 1.8
    for it in items:
        if it is not None:
            m = it if isinstance(it, Mobject) else tx(it, 28, WHITE)
            m.move_to([1.3, y, 0])
            if m.get_width() > 8.0:
                m.set_width(8.0)
            m.move_to([1.3 + 0 * m.get_width(), y, 0])
            self.add(m)
            y -= m.get_height() + 0.35
        self.snap()


def fact(s):
    return VGroup(pill("по факту", C_COMP, 20), tx(s, 22, WHITE)).arrange(RIGHT, buff=0.25)


class F01(Board):
    def construct(self):
        self.add(tx("Образ → формула", 36).move_to(UP * 2.75), icon_journal(0.8).move_to(LEFT * 5.5 + UP * 2.6))
        self.snap()
        self.add(VGroup(tx("у каждой карточки — значок её сцены:", 22, C_NOTE),
                        VGroup(*[ICONS[s](0.45) for s in ("Все составы", "Формула", "Глушков", "Худшая станция", "Проверка")]).arrange(RIGHT, buff=0.4)).arrange(RIGHT, buff=0.3).move_to(DOWN * 2.3))
        self.snap()
        rows = [("вышка со всеми манёврами", "граф Кэли  Γ(Sn, S)"), ("состав 3-1-4-2", "перестановка (3 1 4 2)"), ("манёвры станции", "образующие S")]
        tbl = VGroup(*[VGroup(tx(a, 26, C_BALL), tx("→", 26, C_NOTE), tx(b, 26)).arrange(RIGHT, buff=0.3) for a, b in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        self.add(tbl.move_to(UP * 0.4))
        self.snap()


class F02(Board):
    def construct(self):
        card(self, "Все составы", "Этаж, потолок, рост", icon_journal(1.4),
             ["этаж(σ) = d(e, σ) · потолок = диаметр", tx("рост γ = 1 3 5 6 5 3 1", 28, C_TOP), "E(k+1) = манёвры от E(k) − записанное",
              fact("3 бита на состав · манёвр сразу для всего этажа"), fact("11 вагонов: 2352 с → 0,6 с")])


class F03(Board):
    def construct(self):
        card(self, "Формула", "Ритм = квазимногочлен", icon_rhythm(1.6),
             [None, "D(n) = p_i(n),  i — остаток n при делении на s", tx("квазимногочлен", 30, C_RHYTHM),
              fact("точки маленьких станций → парабола на остаток → проверка"), tx("≈ високосный год: ритм 4", 26, C_COMP)])


class F04(Board):
    def construct(self):
        card(self, "Глушков", "Формула Глушкова", icon_ring(1.6),
             [None, tx("нечётные:  D = (3n^2 − 8n + 9) / 4", 32, C_RHYTHM), tx("чётные:  D = (3n^2 − 8n + 12) / 4", 32, C_BALL), "от n = 5",
              "3n^2/4 — известно давно; новое — точная формула", fact("пересчитали n = 5…12 · для 12: 87 = 87"), "γ(k) = γ(k − 1) + γ(k − 2)"])


class F05(Board):
    def construct(self):
        pics = VGroup(profile(growth(6, neighbours(6)), width=1.3, step=0.12), profile(growth(6, glushkov(6)), width=1.3, step=0.12)).arrange(RIGHT, buff=0.4, aligned_edge=DOWN)
        card(self, "Глушков", "Колокол = распределение", pics,
             ["рост γ(k) / n! — доля составов на этаже", tx("соседи → нормальный закон (Диаконис) · середина = D/2", 26, C_BALL),
              tx("кольцевая → перекос < −0,5 · похоже на Гумбеля ≈ паводки", 26, C_TOP)])


class F06(Board):
    def construct(self):
        card(self, "Худшая станция", "Рекорды формулами", icon_records(1.5),
             [None, "качели:  g·g = e", "квадрат с усами: цикл из 4 мест + два хвоста", tx("D ≤ n^2/2 + 4n = n(n − 1)/2 + 4,5n", 32, C_TOP),
              fact("подгонка n ≤ 14 · n = 15: 150 и 148")])


class F07(Board):
    def construct(self):
        card(self, "Проверка", "Компас и поворотный круг", icon_compass(1.6),
             ["компас: нейросеть(σ) ≈ d(e, σ) · поиск лучом", tx("D = n(n − 1)/6 + 1  (n = 3k, 3k + 1)", 30, C_RHYTHM),
              tx("в статье «− 1» — журнал n = 6…12 даёт «+ 1»", 26, C_NO)])


class F08(Board):
    def construct(self):
        lines = [("from cayleypy import CayleyGraph, PermutationGroups", WHITE),
                 ("graph = CayleyGraph(PermutationGroups.lx(7))   # станция Глушкова", C_BALL),
                 ("graph.bfs().layer_sizes   # [1, 2, 3, 5, 8, 13, 21, …]", C_ORDER), (" ", WHITE),
                 ("def growth(start, moves):          # журнал этажами", C_NOTE),
                 ("    seen, layer, sizes = {start}, {start}, []", WHITE), ("    while layer:", WHITE),
                 ("        sizes.append(len(layer))", C_BALL), ("        layer = {m(s) for s in layer for m in moves} - seen", C_BALL),
                 ("        seen |= layer", WHITE), ("    return sizes", C_ORDER)]
        code = VGroup(*[Text(l, font="Menlo", font_size=21).set_color(c) for l, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        cw = Text("m" * 10, font="Menlo", font_size=21).get_width() / 10
        for l, (s, _) in zip(code, lines):
            l.shift(RIGHT * cw * (len(s) - len(s.lstrip(" "))))
        box = SurroundingRectangle(code, buff=0.3).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.06)
        VGroup(box, code).move_to(DOWN * 0.1)
        self.add(box, tx("В коде", 34).move_to(UP * 2.75))
        self.snap()
        self.add(code[:3])
        self.snap()
        self.add(SurroundingRectangle(code[2], buff=0.05).set_stroke(C_ORDER, 2))
        self.snap()
        self.add(code[3:])
        self.snap()


class F09(Board):
    def construct(self):
        self.add(tx("Где это встречается", 36).move_to(UP * 2.75))
        self.snap()
        rows = [("прямо", "сортировка данных: числа переставляются разрешёнными операциями"), ("прямо", "сети процессоров: потолок = самая долгая задержка"),
                ("прямо", "ДНК: переворот участка = манёвр, расстояние между геномами = этаж"), ("аналогия", "настоящие станции, планирование мелкими шагами")]
        y = 1.8
        for a, b in rows:
            self.add(VGroup(pill(a, C_ORDER if a == "прямо" else C_NOTE, 20), tx(b, 23, WHITE if a == "прямо" else C_NOTE)).arrange(RIGHT, buff=0.3).move_to(UP * y))
            y -= 0.8
            self.snap()
        self.add(VGroup(pill("быстрый журнал", C_BALL, 22), tx("→", 26), pill("ритм", C_RHYTHM, 22), tx("→", 26), pill("гипотеза", C_TOP, 22), tx("→", 26),
                        pill("компас проверяет дальше", C_COMP, 22)).arrange(RIGHT, buff=0.2).move_to(DOWN * 1.9))
        self.snap()


class A16(Board):
    def construct(self):
        line = Line(LEFT * 6, RIGHT * 6).set_stroke(C_NOTE, 2).shift(UP * 1.3)
        self.add(tx("Кто и когда", 36).move_to(UP * 2.75), line)
        self.snap()
        ev = [(-4.8, "1968", "Глушков: кольцевая станция"), (0.0, "02.2025", "CayleyPy: кубики, кольцо"), (2.5, "09.2025", "эта статья"), (4.9, "04.2026", "версия 2")]

        def put(k):
            x, yr, t = ev[k]
            self.add(Dot([x, 1.3, 0], radius=0.1), tx(yr, 24).move_to([x, 1.75, 0]), tx(t, 17, C_NOTE).move_to([x, 0.85, 0]))

        put(0)
        self.snap()
        self.add(pill("Перси Диаконис: колокол для соседей", C_BALL, 20).move_to(LEFT * 2.9 + DOWN * 0.1))
        self.snap()
        self.add(pill("Ласло Бабаи: потолок мал по сравнению с вышкой", C_TOP, 20).move_to(RIGHT * 2.9 + DOWN * 0.1))
        self.snap()
        for k in (1, 2, 3):
            put(k)
        self.snap()
        rows = [("Гипотезы на 10.2026", "ритм, формула Глушкова, предел n²/2 + 4n, рекорды", C_RHYTHM),
                ("Неточность", "поворотный круг: в статье «− 1», журнал даёт «+ 1»", C_NO), ("Образ", "станция и вышка = граф Кэли — точно", C_NOTE)]
        tbl = VGroup(*[VGroup(tx(a, 20, C_NOTE), tx(b, 20, c)).arrange(RIGHT, buff=0.4) for a, b, c in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        self.add(tbl.move_to(DOWN * 1.6))
        self.snap()
