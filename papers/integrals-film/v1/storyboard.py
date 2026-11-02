"""Раскадровка ролика «Как сложить бесконечно много кусочков»: схематичный кадр на каждую фразу диктора.
Кадр — инфографика из элементов kit.py. Рисует: uv run python core/pipeline/animatic.py papers/integrals-film --draw
(или одна сцена: manimgl papers/integrals-film/storyboard.py A01 -s -w)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(HERE))
import numpy as np
from manimlib import *
from manimkit import *
import passport as P
from kit import *
from icons import ICONS

Board = storyboard_base(P.STATIONS, P.SCENES, ICONS, HERE)

PEOPLE = [("Архимед", "III в. до н. э."), ("Ньютон и Лейбниц", "XVII в."), ("Риман", "1854"), ("Лебег", "1902"), ("Ито", "1944")]


def timeline(n, bad_from=None, y=0.2):
    g = VGroup(line([-6, y, 0], [6, y, 0], C_NOTE, 3))
    xs = np.linspace(-5, 5, 5)
    for i in range(n):
        name, yrs = PEOPLE[i]
        g.add(Dot([xs[i], y, 0], radius=0.09).set_color(WHITE))
        g.add(tx(name, 20).move_to([xs[i], y + 0.6, 0]), tx(yrs, 16, C_NOTE).move_to([xs[i], y - 0.4, 0]))
        if bad_from is not None and i >= bad_from:
            g.add(cross(C_BAD, 0.16).move_to([xs[i], y - 0.95, 0]))
    return g


class A01(Board):
    def construct(self):
        k = kassa().move_to([-3.6, 0.4, 0])
        pl = stick(-5.7, 0.2)
        tr = track(-1.2, 6.0, -0.2)
        self.add(title2("Касса игрока"), k, pl, tr, ball(0.2, -0.2), lab("касса", 20).next_to(k, DOWN, buff=0.6),
                 lab("игрок", 20).next_to(pl, DOWN, buff=0.25), lab("дорожка — цена", 20, C_PRICE).move_to([3.6, -0.75, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Миг игры"), tr.copy(), ball(3.3, -0.2),
                 Rectangle(width=0.4, height=1.4).set_stroke(C_BET, 3).set_fill(C_BET, 0.5).move_to([0.8, 0.5, 0]),
                 lab("ставка", 22, C_BET).move_to([0.8, 1.5, 0]),
                 Arrow([0.9, -0.55, 0], [3.0, -0.55, 0], buff=0).set_color(C_PRICE), lab("цена сдвинулась", 20, C_PRICE).move_to([2.0, -1.1, 0]))
        self.snap()
        self.clear_keep_bar()
        row = formula_row([Rectangle(width=0.4, height=1.2).set_stroke(C_BET, 3).set_fill(C_BET, 0.5), "×",
                           Arrow(LEFT * 0.7, RIGHT * 0.7, buff=0).set_color(C_PRICE), "=",
                           Square(0.5).set_stroke(C_SUM, 3).set_fill(C_SUM, 0.6)], y=0.4)
        self.add(title2("Выигрыш за миг"), row, lab("ставка", 22, C_BET).move_to([row[0].get_center()[0], -0.6, 0]),
                 lab("сдвиг", 22, C_PRICE).move_to([row[2].get_center()[0], -0.6, 0]), lab("выигрыш", 22, C_SUM).move_to([row[4].get_center()[0], -0.6, 0]))
        self.snap()
        self.clear_keep_bar()
        k2 = kassa(1.2, "итог").move_to([0, -0.9, 0])
        rain = VGroup(*[Square(0.12).set_stroke(C_SUM, 1).set_fill(C_SUM, 0.8).move_to([-2.4 + 0.2 * i, 1.5 - 0.25 * (i % 3), 0]) for i in range(25)])
        self.add(title2("Итог копится"), k2, rain, lab("бесконечно много крошечных кусочков", 22).move_to([0, 2.15, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(tx("Как сложить кусочки,", 38).move_to([0, 1.5, 0]), tx("чтобы итог не зависел от способа счёта?", 38).move_to([0, 0.7, 0]),
                 kassa(0.6, "итог").move_to([0, -0.9, 0]))
        self.snap()
        self.clear_keep_bar()
        tl = VGroup(line([-6, 0, 0], [6, 0, 0], C_NOTE, 3), *[cross(C_BAD, 0.16).move_to([x, 0, 0]) for x in (-4, -1.5, 1, 3.5)])
        self.add(title2("Много веков"), tl, lab("каждый раз способ счёта ломался на новом случае", 22).move_to([0, -1.0, 0]))
        self.snap()


class A02(Board):
    def construct(self):
        card = RoundedRectangle(width=9, height=3.0, corner_radius=0.2).set_stroke(WHITE, 2).set_fill("#0f1115", 1).move_to([0, 0.3, 0])
        self.add(card, tx("История интеграла", 44).move_to([0, 0.9, 0]), tx("как сложить бесконечно много кусочков", 26, C_NOTE).move_to([0, 0.0, 0]),
                 kassa(0.4).move_to([-5.7, -2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Лента"), timeline(2))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Лента"), timeline(5))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Лента"), timeline(5, bad_from=2), pill("каждый шаг — поломка и починка", C_BAD, 24).move_to([0, -1.9, 0]))
        self.snap()


class A03(Board):
    CARDS = [("Плавная цена", "цена ползёт плавно?"), ("Скачущая ставка", "ставка скачет?"), ("Цена скачками", "цена скачет?"),
             ("Случайная цена", "цена дрожит наугад?"), ("Итог", "какой способ выбрать?")]

    def card(self, i):
        name, q = self.CARDS[i]
        r = RoundedRectangle(width=2.2, height=2.6, corner_radius=0.15).set_stroke(C_NOTE, 2).set_fill("#0f1115", 1)
        ic = ICONS[name](1.6).move_to(r.get_center() + UP * 0.5)
        t = tx(q, 17).move_to(r.get_center() + DOWN * 0.7)
        return VGroup(r, ic, t).move_to([-4.8 + i * 2.4, 0.0, 0])

    def construct(self):
        self.add(title2("Путь вопросами игрока"))
        self.snap()
        shown = VGroup()
        for i in range(5):
            c = self.card(i)
            self.add(c)
            shown.add(c)
            if i == 4:
                self.add(lab("значки уезжают в полосу «мы здесь»", 20).move_to([0, -2.0, 0]))
            self.snap()


class A04(Board):
    def construct(self):
        self.add(title2("Цена ползёт плавно"), axis(), curve_of(smooth), lab("ставка", 22, C_BET).move_to([-4.3, 1.5, 0]),
                 track(X0, X1, -2.0), ball(1.5, -2.0), lab("цена", 20, C_PRICE).move_to([-5.5, -2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Режем время на полоски"), axis(), strips(9), bars_of(smooth, 9, op=0.3))
        self.snap()
        self.clear_keep_bar()
        w = 1.4
        r = Rectangle(width=w, height=1.8).set_stroke(C_BET, 3).set_fill(C_BET, 0.5).move_to([0, 0.0, 0])
        self.add(title2("Одна полоска"), r, lab("ширина", 22).move_to([0, -1.2, 0]), lab("ставка", 22, C_BET).move_to([-1.5, 0, 0]),
                 pill("ставка × ширина = столбик", C_BET, 24).move_to([0, 2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Итог — площадь"), axis(), bars_of(smooth, 24, color=C_SUM, op=0.5),
                 pill("итог = площадь под ставкой", C_SUM, 24).move_to([0, -2.1, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(portrait("Архимед", "", WHITE).move_to([-1.8, 0.7, 0]), portrait("Ньютон", "", WHITE).move_to([1.8, 0.7, 0]),
                 check(C_SUM, 0.45).move_to([0, -1.3, 0]), lab("пока гладко — спорить не о чем", 22).move_to([0, -2.2, 0]))
        self.snap()


def jump_heights(n, seed=3):
    rng = np.random.default_rng(seed)
    return [0.2 if rng.random() < 0.5 else 1.6 for _ in range(n)]


class A05(Board):
    def construct(self):
        hs = jump_heights(16)
        w = (X1 - X0) / 16
        bars = VGroup(*[Rectangle(width=w, height=h).set_stroke(C_BET, 1.5).set_fill(C_BET, 0.45).move_to([X0 + (i + 0.5) * w, BASE + h / 2, 0])
                        for i, h in enumerate(hs)])
        self.add(title2("Ставка скачет"), axis(), bars, pill("ломается", C_BAD, 24).move_to([0, 2.45, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("То единица, то ноль"), line([X0, 1.0, 0], [X1, 1.0, 0], C_NOTE, 1.5, True), line([X0, -0.6, 0], [X1, -0.6, 0], C_NOTE, 1.5, True),
                 dots(40, X0, X1, 0.9, 1.1, C_BET, 1), dots(40, X0, X1, -0.7, -0.5, C_BET, 2),
                 lab("1", 24, C_BET).move_to([-5.4, 1.0, 0]), lab("0", 24, C_BET).move_to([-5.4, -0.6, 0]))
        self.snap()
        self.clear_keep_bar()
        r = Rectangle(width=2.4, height=2.4).set_stroke(C_NOTE, 3).move_to([0, 0.2, 0])
        self.add(title2("Замер"), r, Dot([-0.5, 1.0, 0], radius=0.08).set_color(C_BET), Dot([0.4, -0.6, 0], radius=0.08).set_color(C_BET), lens(-0.5, 1.0),
                 lab("полоска", 22).move_to([0, -1.4, 0]), lab("замер — одна точка полоски", 22, C_BET).move_to([0, -2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        left = VGroup(Rectangle(width=1.6, height=1.6).set_stroke(C_NOTE, 3), Dot([-0.4, 0.5, 0], radius=0.08).set_color(C_BET), lens(-0.4, 0.5)).move_to([-3.2, 0.5, 0])
        right = VGroup(Rectangle(width=1.6, height=1.6).set_stroke(C_NOTE, 3), Dot([0.3, -0.5, 0], radius=0.08).set_color(C_BET), lens(0.3, -0.5)).move_to([3.2, 0.5, 0])
        self.add(left, right, pill("итог большой", C_SUM, 24).move_to([-3.2, -1.1, 0]), pill("итог нулевой", C_SUM, 24).move_to([3.2, -1.1, 0]),
                 tx("≠", 60, C_BAD).move_to([0, 0.5, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(tx("Риман: итог не определён", 40).move_to([0, 0.9, 0]), cross(C_BAD, 0.6).move_to([0, -0.4, 0]),
                 lab("зависит от выбранных замеров", 24).move_to([0, -1.6, 0]))
        self.snap()


class A06(Board):
    def construct(self):
        self.add(portrait("Лебег", "1902", WHITE, 1.3).move_to([-4.2, 0.6, 0]), box("ящик", 1.6, 1.2, C_NOTE).move_to([0, 0.3, 0]),
                 box("ящик", 1.6, 1.2, C_NOTE).move_to([3.4, 0.3, 0]), lab("делим иначе", 26).move_to([0, 2.2, 0]))
        self.snap()
        self.clear_keep_bar()
        b0 = box("ставка 0", 2.0, 1.6, C_NOTE).move_to([-2.0, 0.2, 0])
        b1 = box("ставка 1", 2.0, 1.6, C_BET).move_to([2.0, 0.2, 0])
        self.add(title2("Раскладываем моменты по ящикам"), b0, b1, dots(18, -2.8, -1.2, -0.4, 0.9, WHITE, 5), dots(4, 1.4, 2.6, -0.4, 0.2, C_BET, 6))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Время в ящике × ставка"), b0, b1, dots(18, -2.8, -1.2, -0.4, 0.9, WHITE, 5), dots(4, 1.4, 2.6, -0.4, 0.2, C_BET, 6),
                 Rectangle(width=2.0, height=0.2).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.5).move_to([-2.0, 1.55, 0]),
                 Rectangle(width=0.4, height=0.2).set_stroke(C_BET, 2).set_fill(C_BET, 0.5).move_to([2.0, 1.55, 0]),
                 tx("× 0", 28, C_NOTE).move_to([-2.0, 2.2, 0]), tx("× 1", 28, C_BET).move_to([2.0, 2.2, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Ящик с единицей почти пуст"), box("ставка 1", 2.0, 1.6, C_BET).move_to([-2.5, 0.2, 0]), dots(2, -3.0, -2.0, -0.4, 0.2, C_BET, 7),
                 lab("время почти нулевое", 22).move_to([-2.5, -1.7, 0]), kassa(1.2, "итог 0").move_to([2.5, -0.1, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(tx("Риман", 44).move_to([-2.2, 0.5, 0]), cross(C_BAD, 0.4).move_to([-2.2, -0.5, 0]), tx("Лебег", 44).move_to([2.2, 0.5, 0]),
                 check(C_SUM, 0.5).move_to([2.2, -0.5, 0]), lab("слабое место починили", 24).move_to([0, -1.8, 0]))
        self.snap()


class A07(Board):
    def construct(self):
        self.add(portrait("Лебег", "", WHITE, 1.3).move_to([-3.0, 0.4, 0]), pill("второй козырь", C_BET, 32).move_to([2.5, 0.4, 0]))
        self.snap()
        self.clear_keep_bar()
        ideal = lambda x: 0.9 + 0.5 * np.sin(0.85 * x)
        panels = VGroup()
        for i, (n, name) in enumerate(((3, "грубее"), (6, "точнее"), (12, "ещё точнее"))):
            panels.add(VGroup(bars_of(ideal, n, -1.2, 1.2, 0.0, C_BET, 0.45), lab(name, 20).move_to([0, -0.5, 0])).move_to([-5.0 + i * 3.1, 0.2, 0]))
        best = VGroup(curve_of(ideal, -1.2, 1.2, 0.0, WHITE, 4, 40), lab("идеальная", 20).move_to([0, -0.5, 0])).move_to([4.3, 0.2, 0])
        self.add(title2("Приближения к идеальной ставке"), panels, best, lab("каждое точнее прежнего", 22).move_to([0, 2.2, 0]))
        self.snap()
        self.clear_keep_bar()
        hs = [0.5, 0.85, 1.0]
        row = VGroup(*[Rectangle(width=1.0, height=h * 2).set_stroke(C_SUM, 2).set_fill(C_SUM, 0.5).move_to([-3 + i * 1.6, -1.5 + h, 0]) for i, h in enumerate(hs)])
        ideal_line = line([-3.6, 0.5, 0], [1.7, 0.5, 0], WHITE, 2, True)
        self.add(title2("Итоги тоже подходят"), row, ideal_line, lab("итог идеальной", 20).move_to([4.0, 0.5, 0]), lab("итоги приближений", 20, C_SUM).move_to([-1.3, -2.2, 0]))
        self.snap()
        self.clear_keep_bar()
        frame = Rectangle(width=4.0, height=3.0).set_stroke(C_NOTE, 2, opacity=0.8).move_to([-3.0, 0.2, 0])
        self.add(title2("Ящики переживают предел"), frame, box("ящик", 1.2, 0.9, C_BET).move_to([-3.0, 0.6, 0]), lab("мир Римана", 20).move_to([-3.0, 2.0, 0]),
                 curve_of(ideal, 1.0, 5.0, -0.5, C_BAD, 4, 30), lab("идеальная ставка вне мира Римана", 20, C_BAD).move_to([3.0, -1.2, 0]))
        self.snap()
        self.clear_keep_bar()
        wave = curve_of(lambda x: 0.5 * np.sin(2.5 * x), -1.0, 1.0, 0.0, C_NOISE, 4, 40).move_to([-3.0, 0.5, 0])
        wheel = VGroup(Circle(radius=0.6).set_stroke(WHITE, 3), *[line([0, 0, 0], [0.6 * np.cos(a), 0.6 * np.sin(a), 0], WHITE, 2) for a in np.arange(6) * TAU / 6]).move_to([3.0, 0.5, 0])
        self.add(title2("На Лебеге стоят"), wave, lab("ряды Фурье", 24).move_to([-3.0, -0.8, 0]), wheel, lab("вероятность", 24).move_to([3.0, -0.8, 0]))
        self.snap()


class A08(Board):
    def construct(self):
        xs = [-5, -3, -1, 1, 3, 5]
        ys = [0, 0.5, 0.5, 1.2, 1.2, 1.8]
        st = staircase(xs, ys, -1.5)
        self.add(title2("Цена идёт рывками"), st, ball(5, 0.3), lab("цена", 20, C_PRICE).move_to([-5.2, -1.9, 0]))
        self.snap()
        self.clear_keep_bar()
        jx = [-3, 0, 3]
        g = VGroup()
        for i, x in enumerate(jx):
            g.add(Rectangle(width=0.4, height=1.0 + 0.4 * i).set_stroke(C_BET, 2).set_fill(C_BET, 0.5).move_to([x, 0.2 + 0.2 * i, 0]),
                  Arrow([x + 0.5, -0.8, 0], [x + 1.5, -0.8, 0], buff=0).set_color(C_PRICE))
        self.add(title2("Рывок — ставка — рывок"), g, lab("заплатили", 20).move_to([-2.0, -1.5, 0]), lab("подождали", 20).move_to([0.8, -1.5, 0]),
                 lab("заплатили ещё", 20).move_to([4.0, -1.5, 0]))
        self.snap()
        self.clear_keep_bar()
        row = formula_row([Rectangle(width=0.4, height=1.2).set_stroke(C_BET, 3).set_fill(C_BET, 0.5), "×", Arrow(UP * 0.0, UP * 1.0, buff=0).set_color(C_PRICE),
                           "=", Square(0.5).set_stroke(C_SUM, 3).set_fill(C_SUM, 0.6)], y=0.5)
        self.add(title2("Сумма ставок × размер рывка"), row, lab("ставка", 22, C_BET).move_to([row[0].get_center()[0], -0.5, 0]),
                 lab("рывок", 22, C_PRICE).move_to([row[2].get_center()[0], -0.5, 0]), lab("итог", 22, C_SUM).move_to([row[4].get_center()[0], -0.5, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(portrait("Стилтьес", "1894", WHITE, 1.1).move_to([0, 1.4, 0]),
                 curve_of(lambda x: 0.3 * (x + 5), -5.0, -1.2, -1.6, C_PRICE, 4, 30), staircase([1.2, 2.4, 3.6, 4.8], [0, 0.6, 1.2, 1.8], -1.6, C_PRICE),
                 lab("одна формула — гладкая и рваная цена", 22).move_to([0, -2.75, 0]))
        self.snap()
        self.clear_keep_bar()
        ws = [0.4, 1.4, 0.7, 1.9, 0.5, 1.1]
        x = -4.8
        g = VGroup()
        for w in ws:
            g.add(Rectangle(width=w, height=smooth(x + w / 2) + 0.2).set_stroke(C_BET, 2).set_fill(C_BET, 0.4).move_to([x + w / 2, BASE + (smooth(x + w / 2) + 0.2) / 2, 0]))
            x += w
        self.add(title2("Курцвейль и Хенсток"), axis(), g, lab("в каждом месте своя ширина полоски", 22).move_to([0, 2.2, 0]))
        self.snap()


class A09(Board):
    def construct(self):
        j, xs, ys = jagged(-5, 5, -0.3, 0.18, 60, 4)
        self.add(title2("Цена дрожит"), j, ball(5, ys[-1]), lab("шум", 30, C_NOISE).move_to([0, 1.6, 0]), kassa(0.45).move_to([-5.7, 2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        j2, xs2, ys2 = jagged(-5, 5, 0.0, 0.3, 70, 8)
        self.add(title2("Вверх или вниз — наугад"), j2, ball(xs2[35], ys2[35]), Arrow([xs2[35], ys2[35] + 0.7, 0], [xs2[35], ys2[35] + 0.3, 0], buff=0).set_color(WHITE))
        self.snap()
        self.clear_keep_bar()
        outer = Rectangle(width=3.2, height=1.8).set_stroke(WHITE, 2).move_to([-3.4, 0.0, 0])
        inner_j, _, _ = jagged(-4.6, -2.2, 0.0, 0.09, 40, 11, C_NOISE, 2)
        outer2 = Rectangle(width=2.0, height=1.2).set_stroke(WHITE, 2).move_to([2.6, 0.0, 0])
        inner2, _, _ = jagged(1.8, 3.4, 0.0, 0.04, 60, 12, C_NOISE, 2)
        self.add(title2("Сколько ни увеличивай"), outer, inner_j, outer2, inner2, Arrow([-1.6, 0, 0], [0.8, 0, 0], buff=0).set_color(WHITE),
                 lab("в любой полоске рывков бесконечно много", 22).move_to([0, -1.9, 0]), lens(-1.0, 1.4))
        self.snap()
        self.clear_keep_bar()
        L = VGroup(Rectangle(width=2.0, height=1.6).set_stroke(C_NOTE, 3), marker(-1.0, 1.0, C_BAD)).move_to([-3.2, 0.2, 0])
        R = VGroup(Rectangle(width=2.0, height=1.6).set_stroke(C_NOTE, 3), marker(1.0, 1.0, C_SUM)).move_to([3.2, 0.2, 0])
        self.add(title2("Левый край и правый край"), L, R, lab("левый край", 22, C_BAD).move_to([-3.2, -1.1, 0]), lab("правый край", 22, C_SUM).move_to([3.2, -1.1, 0]),
                 tx("≠", 60, C_BAD).move_to([0, 0.2, 0]), lab("итоги разошлись", 22).move_to([0, -2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Какой край берём?"), VGroup(tx("гладкая цена", 26, C_PRICE), tx("=", 40), tx("краю всё равно", 26)).arrange(RIGHT, buff=0.4).move_to([0, 1.0, 0]),
                 VGroup(tx("шум", 26, C_NOISE), tx("≠", 40, C_BAD), tx("край важен", 26)).arrange(RIGHT, buff=0.4).move_to([0, -0.3, 0]),
                 pill("надо договориться, какой край", C_BAD, 26).move_to([0, -1.8, 0]))
        self.snap()


class A10(Board):
    def construct(self):
        r = Rectangle(width=3.0, height=2.0).set_stroke(C_NOTE, 3)
        self.add(portrait("Ито", "1944", WHITE, 1.2).move_to([-4.0, 0.4, 0]), r.copy().move_to([1.6, 0.4, 0]), marker(0.2, 1.6, C_BAD, "левый край").move_to([0.1, 1.9, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Будущее закрыто"), r.copy().move_to([0, 0.5, 0]), marker(-1.5, 1.7, C_BAD), line([0, -0.5, 0], [0, 1.5, 0], C_NOTE, 2, True),
                 lock(1.0, 0.5), lab("уже известно", 20).move_to([-0.7, -0.9, 0]), lab("закрыто", 20, C_BAD).move_to([1.0, -0.9, 0]))
        self.snap()
        self.clear_keep_bar()
        sc = scales().move_to([0, 0.3, 0])
        self.add(title2("Честная игра"), sc, kassa(0.7, "в среднем 0").move_to([0, -1.9, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Пересчёт с добавкой"), formula_row([tx("пересчёт", 28), tx("+", 36), pill("добавка", C_BET, 28)], y=0.5),
                 lab("зависит от того, как сильно цена дрожит", 22).move_to([0, -0.7, 0]), icons_noise())
        self.snap()


def icons_noise():
    return ICONS["Случайная цена"](1.4).move_to([0, -1.7, 0])


class A11(Board):
    def construct(self):
        r = Rectangle(width=3.0, height=2.0).set_stroke(C_NOTE, 3).move_to([1.8, 0.2, 0])
        self.add(portrait("Фиск", "1963", WHITE, 1.0).move_to([-4.5, 1.0, 0]), portrait("Стратонович", "1966", WHITE, 1.0).move_to([-2.8, 1.0, 0]),
                 r, marker(0.5, 1.4, C_NOTE), Arrow([0.7, 1.4, 0], [1.6, 1.4, 0], buff=0).set_color(C_BAD), marker(1.8, 1.4, C_SUM), lab("физикам удобнее", 20).move_to([-3.6, -1.0, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Середина полоски"), r.copy().move_to([-2.5, 0.2, 0]), marker(-2.5, 1.4, C_SUM, "середина"),
                 pill("школьные правила, без добавки", C_SUM, 22).move_to([2.5, 0.4, 0]))
        self.snap()
        self.clear_keep_bar()
        tl = VGroup(line([-6, 0, 0], [6, 0, 0], C_NOTE, 3), Dot([0, 0, 0], radius=0.1).set_color(WHITE), tx("шестидесятые", 26).move_to([0, 0.6, 0]))
        pend = VGroup(line([0, 0, 0], [0.5, -1.0, 0], WHITE, 3), Circle(radius=0.2).set_stroke(WHITE, 3).set_fill(C_BET, 0.8).move_to([0.5, -1.2, 0])).move_to([0, -1.2, 0])
        self.add(title2("Фиск и Стратонович"), tl, pend)
        self.snap()
        self.clear_keep_bar()
        a, b = pill("итог Ито", C_SUM, 26).move_to([-3.6, 0.5, 0]), pill("итог Стратоновича", C_SUM, 26).move_to([3.4, 0.5, 0])
        self.add(title2("Перевод между ними"), a, b, Arrow(a.get_right() + RIGHT * 0.1, b.get_left() + LEFT * 0.1, buff=0).set_color(C_BET), pill("+ добавка", C_BET, 24).move_to([0, 1.3, 0]))
        self.snap()
        self.clear_keep_bar()
        j, xs, ys = jagged(-4, 4, 0.5, 0.18, 50, 6)
        self.add(title2("Та же игра"), j, ball(4, ys[-1]), lab("две записи — один шум", 24).move_to([0, -1.2, 0]))
        self.snap()


class A12(Board):
    def construct(self):
        j, xs, ys = jagged(-5, 5, 0.3, 0.45, 80, 21)
        self.add(title2("Шум грубее"), j, marker(-3.0, 1.9, C_BAD), marker(1.0, 1.9, C_SUM))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Ни левый край, ни середина"), kassa(1.2, "?").move_to([0, 0.4, 0]), cross(C_BAD, 0.5).move_to([-3.0, 0.2, 0]), cross(C_BAD, 0.5).move_to([3.0, 0.2, 0]),
                 lab("левый край", 22, C_BAD).move_to([-3.0, -0.7, 0]), lab("середина", 22, C_SUM).move_to([3.0, -0.7, 0]))
        self.snap()
        self.clear_keep_bar()
        j2, xs, ys = jagged(-1.0, 5.0, 0.0, 0.3, 40, 22)
        sp = Arc(start_angle=0, angle=TAU * 1.3, radius=0.5).set_stroke(C_BET, 4).move_to([2.0, 1.4, 0])
        self.add(portrait("Лайонс", "1998", WHITE, 1.2).move_to([-4.0, 0.4, 0]), j2, sp, pill("подсказка", C_BET, 26).move_to([2.0, 2.4, 0]))
        self.snap()
        self.clear_keep_bar()
        j3, _, _ = jagged(-5.5, -1.0, 0.0, 0.3, 40, 23)
        self.add(title2("Каждый путь отдельно"), j3, Arrow([-0.6, 0, 0], [0.8, 0, 0], buff=0).set_color(WHITE), kassa(1.2, "число").move_to([3.4, 0.0, 0]),
                 lab("без вероятностей", 22).move_to([3.4, -1.5, 0]))
        self.snap()
        self.clear_keep_bar()
        medal = VGroup(Circle(radius=0.5).set_stroke(C_BET, 4).set_fill(C_BET, 0.3), tx("★", 40, C_BET)).move_to([2.2, 0.6, 0])
        self.add(portrait("Хайрер", "", WHITE, 1.3).move_to([-2.2, 0.6, 0]), medal, lab("Филдсовская премия", 24).move_to([2.2, -0.5, 0]))
        self.snap()


class A13(Board):
    LAYERS = [("Риман", C_BET), ("Лебег", C_BET), ("Стилтьес", C_PRICE), ("Ито и Стратонович", C_NOISE), ("Грубые пути", C_NOISE)]

    def stack(self, arrows=False):
        g = VGroup()
        for i, (n, c) in enumerate(self.LAYERS):
            r = Rectangle(width=2.6 + 0.9 * i, height=0.55).set_stroke(c, 3).set_fill(c, 0.15)
            g.add(VGroup(r, tx(n, 20, c).move_to(r)).move_to([0, -1.4 + 0.75 * i, 0]))
        if arrows:
            for i in range(4):
                g.add(Arrow([4.2, -1.4 + 0.75 * i, 0], [4.2, -1.4 + 0.75 * (i + 1), 0], buff=0.05).set_color(C_BAD))
            g.add(lab("поломка → починка", 20, C_BAD).move_to([5.0, 0.3, 0]))
        return g

    def construct(self):
        self.add(kassa(0.9, "итог").move_to([-3.0, -0.3, 0]), stick(-5.3, -0.4), tx("как сложить кусочки, чтобы итог не зависел от способа?", 24).move_to([2.2, 1.0, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(tx("Единого способа нет", 48).move_to([0, 0.3, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Слои"), self.stack())
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Ни один не выбросили"), self.stack(True))
        self.snap()
        self.clear_keep_bar()
        a = VGroup(tx("гладкая цена", 28, C_PRICE), Arrow(LEFT, RIGHT, buff=0).scale(0.7), tx("Риман", 36)).arrange(RIGHT, buff=0.4).move_to([0, 0.8, 0])
        b = VGroup(tx("случайная цена", 28, C_NOISE), Arrow(LEFT, RIGHT, buff=0).scale(0.7), tx("Ито", 36)).arrange(RIGHT, buff=0.4).move_to([0, -0.5, 0])
        self.add(title2("Какой брать — зависит от цены"), a, b)
        self.snap()


def card3(name, formula, note_, color=C_BET):
    r = RoundedRectangle(width=3.8, height=3.6, corner_radius=0.15).set_stroke(color, 2).set_fill("#0f1115", 1)
    t = tx(name, 28, color).move_to(r.get_top() + DOWN * 0.45)
    f = tx(formula, 20).move_to(r.get_center() + UP * 0.15)
    n = tx(note_, 18, C_NOTE).move_to(r.get_bottom() + UP * 0.55)
    return VGroup(r, t, f, n)


class F01(Board):
    def construct(self):
        self.add(title2("Образ → формула"), ICONS["Плавная цена"](2.0).move_to([-2.0, 0.4, 0]), Arrow(LEFT, RIGHT, buff=0).move_to([0, 0.4, 0]), tx("Σ", 60, C_SUM).move_to([2.0, 0.4, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(card3("Риман", "Σ ставка в точке × ширина", "≈ столбики", C_BET).move_to([-2.2, 0.2, 0]),
                 lab("предел при дроблении полосок", 20).move_to([-2.2, -2.2, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(card3("Лебег", "Σ значение × размер ящика", "≈ ящики", C_BET).move_to([2.2, 0.2, 0]), lab("предел по приближениям", 20).move_to([2.2, -2.2, 0]))
        self.snap()


class F02(Board):
    def construct(self):
        self.add(card3("Стилтьес", "Σ ставка × приращение цены", "≈ оплата кусками", C_PRICE).move_to([0, 0.2, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(card3("Ито", "ставка в левой точке", "≈ замок на будущем", C_NOISE).move_to([0, 0.2, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(card3("Стратонович", "среднее по краям, правила обычные", "≈ середина", C_NOISE).move_to([0, 0.2, 0]))
        self.snap()
        self.clear_keep_bar()
        a, b = pill("Ито", C_NOISE, 28).move_to([-3.0, 0.4, 0]), pill("Стратонович", C_NOISE, 28).move_to([3.0, 0.4, 0])
        self.add(a, b, Arrow(a.get_right() + RIGHT * 0.1, b.get_left() + LEFT * 0.1, buff=0).set_color(C_BET), pill("+ добавка", C_BET, 24).move_to([0, 1.2, 0]))
        self.snap()


class F03(Board):
    def construct(self):
        rows = [("Риман", "площадь"), ("Лебег", "пределы, рваная ставка"), ("Стилтьес", "рваная цена"), ("Ито", "случайная цена"),
                ("Стратонович", "привычные правила"), ("Лайонс", "грубая цена")]
        g = VGroup(*[VGroup(tx(a, 22, WHITE), tx(b, 22, C_NOTE)).arrange(RIGHT, buff=0.6) for a, b in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([-2.5, 0.0, 0])
        self.add(title2("Что чинили"), g)
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Где применяют"), VGroup(*[tx(s, 24, C_SUM) for s in ("вероятность", "финансы", "физика шума", "уравнения в частных производных")]).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([0, 0.2, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(pill("прямо", C_SUM, 28).move_to([-2.5, 0.8, 0]), pill("по аналогии", C_NOISE, 28).move_to([2.5, 0.8, 0]),
                 lab("интегралы по траекториям в квантовой механике", 22).move_to([2.5, -0.2, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(tx("Какой способ — зависит от цены", 40).move_to([0, 0.4, 0]))
        self.snap()
