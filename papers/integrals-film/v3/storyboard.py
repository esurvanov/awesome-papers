"""Раскадровка ролика «Как сложить бесконечно много столбиков»: схематичный кадр на каждую фразу диктора.
Мир — график: кривая, ось, столбики, слои, шкала веса, дрожащая линия (kit.py). Придуманных историй нет.
Рисует: uv run python core/pipeline/animatic.py papers/integrals-film --draw (или одна сцена: manimgl papers/integrals-film/storyboard.py A01 -s -w)."""
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

_Board = storyboard_base(P.STATIONS, P.SCENES, ICONS, HERE)

# ---------- сквозные сущности: верхняя полоса каждого кадра рассказа (закон 21) ----------
LEVERS = [("график", C_PRICE), ("ось", C_AXIS), ("высота", C_BET), ("сложение", C_ADD)]


def lamps(lit):
    on = list(lit) if isinstance(lit, (tuple, list)) else ([] if lit is None else [lit])
    g = VGroup()
    for n, c in LEVERS:
        lit_ = lit == "all" or n in on
        col, op = (c, 1.0) if lit_ else (C_NOTE, 0.5)
        g.add(VGroup(Dot(radius=0.1).set_color(col).set_opacity(op), tx(n, 14, col).set_opacity(op)).arrange(RIGHT, buff=0.1))
    return g.arrange(RIGHT, buff=0.22)


def hero_mini(kind):
    r = Rectangle(width=1.5, height=0.5).set_stroke(C_NOTE, 1.5)
    if kind == "smooth":
        body = curve_of(lambda x: 0.15 * np.sin(4 * x), -0.6, 0.6, 0.0, C_PRICE, 2, 30)
    elif kind == "dots":
        body = VGroup(dots(6, -0.6, 0.6, 0.12, 0.14, C_BET, 1, 0.025), dots(6, -0.6, 0.6, -0.14, -0.12, C_BET, 2, 0.025))
    else:
        body = jagged(-0.6, 0.6, 0.0, 0.05 if kind == "jag" else 0.1, 24, 5, C_NOISE, 2)[0]
    return VGroup(r, body.move_to(r.get_center()))


def piece_mini(kind):
    r = Rectangle(width=0.9, height=0.5).set_stroke(C_NOTE, 1.5)
    lit = {"any": [0, 1, 2], "left": [0], "mid": [1], "right": [2], "layer": [], "history": [0, 1, 2]}.get(kind, [])
    g = VGroup(r)
    for i, x in enumerate((-0.3, 0.0, 0.3)):
        col = (C_BAD if i == 0 else C_SUM if i == 1 else C_BET) if i in lit else C_NOTE
        g.add(Triangle().scale(0.07).rotate(PI).set_stroke(col, 1).set_fill(col, 1 if i in lit else 0.4).move_to([x, 0.05, 0]))
    if kind == "layer":
        g.add(line([-0.35, 0.05, 0], [0.35, 0.05, 0], C_BET, 3))
    if kind == "history":
        g.add(line([-0.4, -0.15, 0], [0.4, -0.15, 0], C_PRICE, 3))
    return g


def twins_mini(sign):
    col = C_BAD if sign == "≠" else C_SUM
    return VGroup(tx("А", 16), tx(sign, 26, col), tx("Б", 16)).arrange(RIGHT, buff=0.12)


def tablo_mini(val):
    r = RoundedRectangle(width=1.3, height=0.5, corner_radius=0.08).set_stroke(C_SUM, 2).set_fill(C_SUM, 0.12)
    return VGroup(r, tx(val, 22, C_SUM).move_to(r))


def sprout_mini(n):
    cols = [C_BET, C_PRICE, C_NOISE, C_AXIS, C_ADD, C_SUM, C_BET, C_PRICE, C_NOISE]
    g = VGroup(line([0, -0.35, 0], [0, 0.35, 0], C_SUM, 3))
    for i in range(min(n, 9)):
        y = -0.25 + 0.07 * i
        dx = 0.22 if i % 2 == 0 else -0.22
        g.add(line([0, y, 0], [dx, y + 0.12, 0], cols[i], 2))
    return g


def overlay(st):
    g = VGroup(lamps(st.get("lever")).move_to([-5.0, 3.62, 0]), hero_mini(st["hero"]).move_to([-2.2, 3.62, 0]),
               piece_mini(st["piece"]).move_to([-0.55, 3.62, 0]), twins_mini(st["twins"]).move_to([1.35, 3.62, 0]),
               tablo_mini(st["tablo"]).move_to([3.7, 3.62, 0]))
    if st.get("sprout"):
        g.add(sprout_mini(st["sprout"]).move_to([6.2, 3.5, 0]))
    return g


def S(lever, hero, piece, tablo, twins, sprout=0):
    return dict(lever=lever, hero=hero, piece=piece, tablo=tablo, twins=twins, sprout=sprout)


STATE = {  # сцена → состояние сущностей (одно на сцену или список по кадрам; None — без верхней полосы)
    "A04": S(None, "smooth", "any", "Σ", "≈"),
    "A05": S("график", "dots", "any", "?", "≠"),
    "A06": S("высота", "dots", "layer", "0", "=", 1),
    "A07": S("высота", "smooth", "layer", "Σ", "=", 2),
    "A08": S("ось", "smooth", "any", "Σ", "=", 3),
    "A09": S(("график", "ось"), "jag", "any", "?", "≠", 3),
    "A10": S("высота", "jag", "left", "0", "=", 4),
    "A11": S("высота", "jag", "mid", "0", "=", 5),
    "A12": [S("ось", "rough", "any", "?", "≠", 5)] * 2 + [S("ось", "rough", "any", "число", "=", 6)] * 3,
    "A13": S("высота", "jag", "history", "Σ", "=", 6),
    "A14": S("сложение", "smooth", "layer", "Σ", "=", 7),
    "A15": S("сложение", "smooth", "any", "Σ", "=", 8),
    "A16": S("all", "smooth", "any", "Σ", "=", 0),
}


def state_for(code, k):
    st = STATE.get(code)
    if isinstance(st, list):
        st = st[min(k, len(st) - 1)]
    return st


class Board(_Board):
    def snap(self, allow=()):
        old = getattr(self, "_ov", None)
        if old is not None:
            self.remove(old)
        st = state_for(type(self).__name__, self._k)
        self._ov = overlay(st) if st else None
        if self._ov is not None:
            self.add(self._ov)
        super().snap(allow=[*allow, *([self._ov] if self._ov is not None else [])])


B = -1.7                                        # ось — чуть ниже, чтобы график был крупным
F = lambda x: 1.3 + 0.9 * np.sin(0.8 * x)       # гладкий график
PEOPLE = [("Архимед", "III в. до н. э."), ("Ньютон и Лейбниц", "XVII в."), ("Риман", "1854"), ("Лебег", "1902"), ("Ито", "1944")]


def timeline(n, bad_from=None, y=0.2):
    g = VGroup(line([-6, y, 0], [6, y, 0], C_NOTE, 3))
    xs = np.linspace(-5, 5, 5)
    for i in range(n):
        name, yrs = PEOPLE[i]
        g.add(Dot([xs[i], y, 0], radius=0.09).set_color(WHITE), tx(name, 20).move_to([xs[i], y + 0.6, 0]), tx(yrs, 16, C_NOTE).move_to([xs[i], y - 0.4, 0]))
        if bad_from is not None and i >= bad_from:
            g.add(cross(C_BAD, 0.16).move_to([xs[i], y - 0.95, 0]))
    return g


def ax(x0=X0, x1=X1, y=B, name="ось"):
    return axis(x0, x1, y, name)


def piece(pick, w=2.0, h=2.2):
    """Один кусок разбиения с двумя точками графика: на высоте 1 и на высоте 0; лупа — на выбранной."""
    r = Rectangle(width=w, height=h).set_stroke(C_NOTE, 3)
    top, bot = Dot([-0.4, h / 2 - 0.35, 0], radius=0.08).set_color(C_BET), Dot([0.4, -h / 2 + 0.35, 0], radius=0.08).set_color(C_BET)
    pos = top.get_center() if pick == 1 else bot.get_center()
    return VGroup(r, top, bot, lens(pos[0], pos[1]))


class A01(Board):
    def construct(self):
        self.add(title2("График"), ax(), curve_of(F, y0=B, color=C_PRICE), lab("график", 24, C_PRICE).move_to([-4.2, 0.3, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Площадь под графиком"), ax(), area_of(F, y0=B, op=0.3), lab("площадь", 28, C_SUM).move_to([0, -0.6, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Столбики"), ax(), bars_of(F, 10, y0=B, color=C_BET, op=0.35), lab("столбики", 24, C_BET).move_to([0, 1.9, 0]))
        self.snap()
        self.clear_keep_bar()
        left = VGroup(bars_of(F, 6, -5.0, -0.5, B, C_BET, 0.35), lab("шесть столбиков", 20).move_to([-2.75, B - 0.45, 0]))
        right = VGroup(bars_of(F, 24, 0.5, 5.0, B, C_BET, 0.35), lab("много тонких", 20).move_to([2.75, B - 0.45, 0]))
        self.add(title2("Чем тоньше, тем точнее"), left, right, Arrow([-0.4, 0.2, 0], [0.4, 0.2, 0], buff=0).set_color(WHITE))
        self.snap()
        self.clear_keep_bar()
        self.add(tx("Как сложить столбики,", 38).move_to([0, 1.5, 0]), tx("чтобы сумма не зависела от способа счёта?", 38).move_to([0, 0.7, 0]),
                 bars_of(F, 12, -2.5, 2.5, -2.6, C_BET, 0.35))
        self.snap()
        self.clear_keep_bar()
        cards = VGroup()
        for i, (n, c, d) in enumerate((("график", C_PRICE, "что складываем"), ("ось", C_AXIS, "чем меряем ширину"), ("высота", C_BET, "где берём высоту"), ("сложение", C_ADD, "как складываем"))):
            r = RoundedRectangle(width=3.1, height=1.9, corner_radius=0.15).set_stroke(c, 3).set_fill(c, 0.1)
            cards.add(VGroup(r, tx(n, 34, c).move_to(r.get_center() + UP * 0.35), tx(d, 20, WHITE).move_to(r.get_center() + DOWN * 0.45)).move_to([-5.25 + 3.5 * i, 0.3, 0]))
        self.add(title2("Договор из четырёх пунктов"), cards)
        self.snap()
        self.clear_keep_bar()
        tl = VGroup(line([-6, 0, 0], [6, 0, 0], C_NOTE, 3), *[cross(C_BAD, 0.16).move_to([x, 0, 0]) for x in (-4, -1.5, 1, 3.5)])
        self.add(title2("Много веков"), tl, lab("каждый раз ломался какой-то пункт договора", 22).move_to([0, -1.0, 0]))
        self.snap()


class A02(Board):
    def construct(self):
        card = RoundedRectangle(width=9, height=3.0, corner_radius=0.2).set_stroke(WHITE, 2).set_fill("#0f1115", 1).move_to([0, 0.3, 0])
        self.add(card, tx("История интеграла", 44).move_to([0, 0.9, 0]), tx("как сложить бесконечно много столбиков", 26, C_NOTE).move_to([0, 0.0, 0]),
                 bars_of(F, 8, -6.7, -5.0, -2.2, C_BET, 0.35).scale(0.7))
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
    CARDS = [("Гладкий график", "гладкий график?"), ("Рваный график", "график рваный?"), ("Другая ось", "ось неровная?"),
             ("Случайный график", "график случайный?"), ("Итог", "какой способ выбрать?")]

    def card(self, i):
        name, q = self.CARDS[i]
        r = RoundedRectangle(width=2.2, height=2.6, corner_radius=0.15).set_stroke(C_NOTE, 2).set_fill("#0f1115", 1)
        ic = ICONS[name](1.6).move_to(r.get_center() + UP * 0.5)
        t = tx(q, 18).move_to(r.get_center() + DOWN * 0.7)
        return VGroup(r, ic, t).move_to([-4.8 + i * 2.4, 0.0, 0])

    def construct(self):
        self.add(title2("Путь вопросами"))
        self.snap()
        for i in range(5):
            self.add(self.card(i))
            if i == 4:
                self.add(lab("значки уезжают в полосу «мы здесь»", 20).move_to([0, -2.0, 0]))
            self.snap()


class A04(Board):
    def construct(self):
        self.add(title2("Гладкий график"), ax(), curve_of(F, y0=B, color=C_PRICE))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Разбиение оси на куски"), ax(), strips(9, y0=B, y1=0.9), bars_of(F, 9, y0=B, op=0.3))
        self.snap()
        self.clear_keep_bar()
        h = 1.8
        r = bar_w(0, 1.4, h, -1.2)
        self.add(title2("Один столбик"), r, lab("ширина", 22).move_to([0, -1.55, 0]), lab("высота — значение графика", 22, C_BET).move_to([3.1, -0.3, 0]),
                 pill("площадь = высота × ширина", C_BET, 24).move_to([0, 2.1, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Чем уже, тем ближе"), ax(), bars_of(F, 28, y0=B, color=C_SUM, op=0.5), pill("сумма → площадь", C_SUM, 24).move_to([0, 1.9, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(portrait("Архимед", "", WHITE).move_to([-1.8, 0.7, 0]), portrait("Ньютон", "", WHITE).move_to([1.8, 0.7, 0]),
                 check(C_SUM, 0.45).move_to([0, -1.3, 0]), lab("пока график гладкий — спорить не о чем", 22).move_to([0, -2.2, 0]))
        self.snap()


def row_dots(y, color=C_BET, seed=1):
    return dots(40, X0, X1, y - 0.05, y + 0.05, color, seed)


class A05(Board):
    def construct(self):
        self.add(title2("Рваный график"), row_dots(0.9, seed=1), row_dots(-1.0, seed=2),
                 lab("1", 24, C_BET).move_to([-5.4, 0.9, 0]), lab("0", 24, C_BET).move_to([-5.4, -1.0, 0]),
                 lab("в одних точках единица, в других ноль", 22).move_to([0, 2.1, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Один кусок разбиения"), piece(1).move_to([0, 0.2, 0]).set_opacity(0.0), Rectangle(width=2.0, height=2.2).set_stroke(C_NOTE, 3).move_to([0, 0.2, 0]),
                 Dot([-0.4, 1.05, 0], radius=0.08).set_color(C_BET), Dot([0.4, -0.65, 0], radius=0.08).set_color(C_BET),
                 lab("вперемешку: и единица, и ноль", 22).move_to([0, -1.4, 0]))
        self.snap()
        self.clear_keep_bar()
        p = piece(1).move_to([-2.5, 0.4, 0])
        self.add(title2("Замер"), p, bar_w(2.5, 1.0, 1.7, -1.1), lab("высота столбика = значение в выбранной точке", 22, C_BET).move_to([0, 2.2, 0]),
                 lab("замер", 22).move_to([-2.5, -1.2, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(piece(1).move_to([-4.0, 0.7, 0]), bar_w(-4.0, 1.0, 1.7, -2.4), piece(0).move_to([4.0, 0.7, 0]), bar_w(4.0, 1.0, 0.05, -2.4),
                 tx("≠", 60, C_BAD).move_to([0, 0.2, 0]), lab("сумма большая", 22, C_SUM).move_to([-1.3, -2.1, 0]), lab("сумма нулевая", 22, C_SUM).move_to([1.3, -2.1, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(tx("Риман: площадь не определена", 40).move_to([0, 0.9, 0]), cross(C_BAD, 0.6).move_to([0, -0.4, 0]),
                 lab("сумма зависит от выбранных замеров", 24).move_to([0, -1.6, 0]))
        self.snap()


class A06(Board):
    def construct(self):
        bands = VGroup(*[Rectangle(width=9.0, height=0.8).set_stroke(C_NOTE, 2, opacity=0.6).move_to([0.8, -1.6 + 0.8 * i, 0]) for i in range(4)])
        self.add(portrait("Лебег", "1902", WHITE, 1.2).move_to([-5.2, 0.8, 0]), bands, lab("делим высоту на слои", 24).move_to([0.8, 2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        b0 = Rectangle(width=9.0, height=0.7).set_stroke(C_NOTE, 3).set_fill(C_NOTE, 0.08).move_to([0.8, -1.2, 0])
        b1 = Rectangle(width=9.0, height=0.7).set_stroke(C_BET, 3).set_fill(C_BET, 0.1).move_to([0.8, 0.6, 0])
        self.add(title2("Точки — по слоям"), b0, b1, dots(40, -3.4, 4.9, -1.35, -1.05, WHITE, 3), dots(5, -3.4, 4.9, 0.45, 0.75, C_BET, 4),
                 lab("слой 0", 22).move_to([-5.4, -1.2, 0]), lab("слой 1", 22, C_BET).move_to([-5.4, 0.6, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Сколько оси занимает слой"), line([-3.4, -0.1, 0], [4.9, -0.1, 0], C_NOTE, 6), lab("весь слой 0: почти вся ось, высота 0", 20).move_to([0.8, -0.6, 0]),
                 line([-0.2, 1.5, 0], [0.0, 1.5, 0], C_BET, 6), lab("слой 1: крошечный кусочек оси, высота 1", 20, C_BET).move_to([0.8, 1.9, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Сумма определена"), formula_row([tx("слой 1", 28, C_BET), tx("→ длина 0", 28), tx("× 1", 28, C_BET), tx("=", 36), tx("0", 36, C_SUM)], y=0.4),
                 check(C_SUM, 0.4).move_to([0, -1.2, 0]))
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
        panels = VGroup()
        for i, (n, name) in enumerate(((3, "грубее"), (6, "точнее"), (12, "ещё точнее"))):
            panels.add(VGroup(bars_of(F, n, -1.2, 1.2, 0.0, C_BET, 0.45), lab(name, 20).move_to([0, -0.5, 0])).move_to([-5.0 + i * 3.1, 0.2, 0]))
        best = VGroup(curve_of(F, -1.2, 1.2, 0.0, WHITE, 4, 40), lab("предельный", 20).move_to([0, -0.5, 0])).move_to([4.3, 0.2, 0])
        self.add(title2("Приближения к предельному графику"), panels, best)
        self.snap()
        self.clear_keep_bar()
        hs = [0.5, 0.85, 1.0]
        row = VGroup(*[Rectangle(width=1.0, height=h * 2).set_stroke(C_SUM, 2).set_fill(C_SUM, 0.5).move_to([-3 + i * 1.6, -1.5 + h, 0]) for i, h in enumerate(hs)])
        self.add(title2("Площади тоже подходят"), row, line([-3.6, 0.5, 0], [1.7, 0.5, 0], WHITE, 2, True), lab("площадь предельного", 20).move_to([4.0, 0.5, 0]),
                 lab("площади приближений", 20, C_SUM).move_to([-1.3, -2.2, 0]))
        self.snap()
        self.clear_keep_bar()
        frame = Rectangle(width=4.0, height=3.0).set_stroke(C_NOTE, 2, opacity=0.8).move_to([-3.0, 0.2, 0])
        self.add(title2("Слои переживают предел"), frame, Rectangle(width=1.6, height=0.7).set_stroke(C_BET, 3).set_fill(C_BET, 0.15).move_to([-3.0, 0.6, 0]),
                 lab("слой", 20, C_BET).move_to([-3.0, -0.2, 0]), lab("мир Римана", 20).move_to([-3.0, 2.0, 0]),
                 curve_of(F, 1.0, 5.0, -0.8, C_BAD, 4, 30), lab("предельный график вне мира Римана", 20, C_BAD).move_to([3.0, -1.6, 0]))
        self.snap()
        self.clear_keep_bar()
        wave = curve_of(lambda x: 0.5 * np.sin(2.5 * x), -1.0, 1.0, 0.0, C_NOISE, 4, 40).move_to([-3.0, 0.5, 0])
        wheel = VGroup(Circle(radius=0.6).set_stroke(WHITE, 3), *[line([0, 0, 0], [0.6 * np.cos(a), 0.6 * np.sin(a), 0], WHITE, 2) for a in np.arange(6) * TAU / 6]).move_to([3.0, 0.5, 0])
        self.add(title2("На Лебеге стоят"), wave, lab("ряды Фурье", 24).move_to([-3.0, -0.8, 0]), wheel, lab("вероятность", 24).move_to([3.0, -0.8, 0]))
        self.snap()


class A08(Board):
    W = [0.6, 1.4, 0.4, 1.9, 0.8, 1.3]

    def construct(self):
        xs = [-4.8, -3.0, -1.4, -0.4, 1.2, 2.4, 4.2]
        ys = [0, 0.4, 0.9, 1.6, 1.8, 2.0, 2.2]
        scale = poly_line([[x, -1.9 + 0.35 * y, 0] for x, y in zip(xs, ys)], C_PRICE, 4)
        st = staircase([-4.2, -2.6, -1.0, 0.8, 2.6, 4.2], [0.0, 0.5, 0.5, 1.4, 1.4, 2.0], -2.2, C_PRICE)
        self.add(title2("Ось неровная"), ax(y=0.5, name="ось"), st, lab("вес растёт неровно, где-то скачками", 22, C_PRICE).move_to([0, 2.1, 0]), lab("вес", 20, C_PRICE).move_to([-5.4, -2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        x, g = -4.5, VGroup()
        for w in self.W:
            hh = F(x + w / 2) * 0.7
            g.add(bar_w(x + w / 2, w * 0.96, hh, B, C_BET, 0.45))
            x += w
        self.add(title2("Ширина столбика — прирост веса"), ax(y=B), g, lab("ширина = прирост веса", 22, C_PRICE).move_to([0, 2.1, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Скачок веса — широкий столбик"), ax(y=B), bar_w(-2.0, 0.4, 1.2, B), bar_w(1.2, 3.0, 1.6, B, C_PRICE, 0.35),
                 lab("плавный рост — тонкий", 20).move_to([-2.0, 0.0, 0]), lab("скачок — широкий", 20, C_PRICE).move_to([1.2, 0.5, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(portrait("Стилтьес", "1894", WHITE, 1.1).move_to([0, 1.4, 0]), curve_of(lambda x: 0.3 * (x + 5), -5.0, -1.2, -1.6, C_PRICE, 4, 30),
                 staircase([1.2, 2.4, 3.6, 4.8], [0, 0.6, 1.2, 1.8], -1.6, C_PRICE), lab("одна формула — и плавный вес, и скачки", 22).move_to([0, -2.75, 0]))
        self.snap()
        self.clear_keep_bar()
        ws = [0.4, 1.4, 0.7, 1.9, 0.5, 1.1]
        x, g = -4.8, VGroup()
        for w in ws:
            g.add(bar_w(x + w / 2, w * 0.96, F(x + w / 2) * 0.7, B, C_BET, 0.4))
            x += w
        self.add(title2("Курцвейль и Хенсток"), ax(y=B), g, lab("в каждом месте своя ширина", 22).move_to([0, 2.2, 0]))
        self.snap()


class A09(Board):
    def construct(self):
        self.add(title2("Случайный вес"), poly_line([[x, -1.4 + 0.4 * y, 0] for x, y in zip(np.linspace(-5, 5, 40), np.cumsum(np.random.default_rng(3).normal(0.05, 0.5, 40)))], C_NOISE, 4),
                 lab("вес", 22, C_NOISE).move_to([-5.4, -1.4, 0]), lab("случаен", 26).move_to([0, 1.6, 0]))
        self.snap()
        self.clear_keep_bar()
        j2, xs2, ys2 = jagged(-5, 5, 0.0, 0.3, 70, 8)
        self.add(title2("Шум: вверх или вниз — наугад"), j2, lab("шум", 28, C_NOISE).move_to([0, 2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        outer = Rectangle(width=3.2, height=1.8).set_stroke(WHITE, 2).move_to([-3.4, 0.0, 0])
        inner_j, _, _ = jagged(-4.6, -2.2, 0.0, 0.09, 40, 11, C_NOISE, 2)
        outer2 = Rectangle(width=2.0, height=1.2).set_stroke(WHITE, 2).move_to([2.6, 0.0, 0])
        inner2, _, _ = jagged(1.8, 3.4, 0.0, 0.04, 60, 12, C_NOISE, 2)
        self.add(title2("Сколько ни увеличивай"), outer, inner_j, outer2, inner2, Arrow([-1.6, 0, 0], [0.8, 0, 0], buff=0).set_color(WHITE),
                 lab("на любом куске снова дрожит", 22).move_to([0, -1.9, 0]), lens(-1.0, 1.4))
        self.snap()
        self.clear_keep_bar()
        j3, xs3, ys3 = jagged(-1.0, 1.0, 0.0, 0.25, 12, 31, C_NOISE, 3)
        piece3 = VGroup(Rectangle(width=2.2, height=2.4).set_stroke(C_NOTE, 3), j3.move_to([0, 0.0, 0]))
        hl, hr = float(ys3[0] - ys3.min() + 0.2), float(ys3[-1] - ys3.min() + 0.2)
        self.add(title2("Левый край и правый край"), piece3.move_to([0, 1.0, 0]),
                 bar_w(-2.6, 0.9, 0.4 + hl, -2.0, C_BAD, 0.45), bar_w(2.6, 0.9, 0.4 + hr, -2.0, C_SUM, 0.45),
                 lab("левый край", 22, C_BAD).move_to([-2.6, -2.3, 0]), lab("правый край", 22, C_SUM).move_to([2.6, -2.3, 0]), tx("≠", 60, C_BAD).move_to([0, -1.2, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Какой край берём?"), VGroup(tx("гладкий график", 26, C_PRICE), tx("=", 40), tx("краю всё равно", 26)).arrange(RIGHT, buff=0.4).move_to([0, 1.0, 0]),
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
        self.add(title2("Честная сумма"), scales().move_to([0, 0.3, 0]), pill("в среднем 0", C_SUM, 26).move_to([0, -1.9, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Пересчёт с добавкой"), formula_row([tx("пересчёт", 28), tx("+", 36), pill("добавка", C_BET, 28)], y=0.5),
                 lab("зависит от того, как сильно дрожит шум", 22).move_to([0, -0.7, 0]), ICONS["Случайный график"](1.4).move_to([0, -1.7, 0]))
        self.snap()


class A11(Board):
    def construct(self):
        r = Rectangle(width=3.0, height=2.0).set_stroke(C_NOTE, 3).move_to([1.8, 0.2, 0])
        self.add(portrait("Фиск", "1963", WHITE, 1.0).move_to([-4.5, 1.0, 0]), portrait("Стратонович", "1966", WHITE, 1.0).move_to([-2.8, 1.0, 0]),
                 r, marker(0.5, 1.4, C_NOTE), Arrow([0.7, 1.4, 0], [1.6, 1.4, 0], buff=0).set_color(C_BAD), marker(1.8, 1.4, C_SUM), lab("физикам удобнее", 20).move_to([-3.6, -1.0, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Середина куска"), r.copy().move_to([-2.5, 0.2, 0]), marker(-2.5, 1.4, C_SUM, "середина"),
                 pill("школьные правила, без добавки", C_SUM, 22).move_to([2.5, 0.4, 0]))
        self.snap()
        self.clear_keep_bar()
        tl = VGroup(line([-6, 0, 0], [6, 0, 0], C_NOTE, 3), Dot([0, 0, 0], radius=0.1).set_color(WHITE), tx("1963–66", 26).move_to([0, 0.6, 0]))
        self.add(title2("Фиск и Стратонович"), tl)
        self.snap()
        self.clear_keep_bar()
        a, b = pill("сумма Ито", C_SUM, 26).move_to([-3.6, 0.5, 0]), pill("сумма Стратоновича", C_SUM, 26).move_to([3.4, 0.5, 0])
        self.add(title2("Перевод между ними"), a, b, Arrow(a.get_right() + RIGHT * 0.1, b.get_left() + LEFT * 0.1, buff=0).set_color(C_BET), pill("+ добавка", C_BET, 24).move_to([0, 1.3, 0]))
        self.snap()
        self.clear_keep_bar()
        j, xs, ys = jagged(-4, 4, 0.5, 0.18, 50, 6)
        self.add(title2("Тот же шум"), j, lab("две записи — один шум", 24).move_to([0, -1.2, 0]))
        self.snap()


class A12(Board):
    def construct(self):
        j, xs, ys = jagged(-5, 5, 0.3, 0.45, 80, 21)
        self.add(title2("Шум грубее"), j, marker(-3.0, 1.9, C_BAD), marker(1.0, 1.9, C_SUM))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Ни левый край, ни середина"), pill("сумма = ?", C_NOTE, 40).move_to([0, 0.4, 0]), cross(C_BAD, 0.5).move_to([-3.0, 0.2, 0]), cross(C_BAD, 0.5).move_to([3.0, 0.2, 0]),
                 lab("левый край", 22, C_BAD).move_to([-3.0, -0.7, 0]), lab("середина", 22, C_SUM).move_to([3.0, -0.7, 0]))
        self.snap()
        self.clear_keep_bar()
        j2, xs, ys = jagged(-1.0, 5.0, 0.0, 0.3, 40, 22)
        sp = Arc(start_angle=0, angle=TAU * 1.3, radius=0.5).set_stroke(C_BET, 4).move_to([2.0, 1.4, 0])
        self.add(portrait("Лайонс", "1998", WHITE, 1.2).move_to([-4.0, 0.4, 0]), j2, sp, pill("подсказка", C_BET, 26).move_to([2.0, 2.4, 0]))
        self.snap()
        self.clear_keep_bar()
        j3, _, _ = jagged(-5.5, -1.0, 0.0, 0.3, 40, 23)
        self.add(title2("Каждая линия отдельно"), j3, Arrow([-0.6, 0, 0], [0.8, 0, 0], buff=0).set_color(WHITE), pill("сумма — число", C_SUM, 28).move_to([3.4, 0.0, 0]),
                 lab("без вероятностей", 22).move_to([3.4, -1.0, 0]))
        self.snap()
        self.clear_keep_bar()
        medal = VGroup(Circle(radius=0.5).set_stroke(C_BET, 4).set_fill(C_BET, 0.3), tx("★", 40, C_BET)).move_to([2.2, 0.6, 0])
        self.add(portrait("Хайрер", "", WHITE, 1.3).move_to([-2.2, 0.6, 0]), medal, lab("Филдсовская премия", 24).move_to([2.2, -0.5, 0]))
        self.snap()


def node(label, x, y, color, w=2.4, h=0.55):
    r = RoundedRectangle(width=w, height=h, corner_radius=0.12).set_stroke(color, 3).set_fill(color, 0.12)
    return VGroup(r, tx(label, 18, color).move_to(r)).move_to([x, y, 0])


def tree(labels=True, fixes=False):
    """Дерево способов: корень Лебег внизу, четыре ветви вверх."""
    g = VGroup()
    root = node("Лебег", 0, -2.0, C_BET, 1.6)
    g.add(root)
    xs, names, cols = [-5.0, -1.7, 1.6, 4.9], ["график: слои, приближения", "ось: вес, шум, подсказка", "высота: край, середина", "сложение: другие меры"], [C_PRICE, C_AXIS, C_BET, C_ADD]
    for x, n, c in zip(xs, names, cols):
        g.add(Arrow([0.0 + 0.4 * np.sign(x), -1.7, 0], [x, 0.3, 0], buff=0.05).set_stroke(C_NOTE, 3))
        g.add(node(n, x, 0.7, c, 3.1) if labels else Dot([x, 0.7, 0]).set_color(c))
        if fixes:
            g.add(cross(C_BAD, 0.14).move_to([x - 1.5, 1.4, 0]), Arrow([x - 1.2, 1.4, 0], [x - 0.3, 1.4, 0], buff=0).set_color(C_SUM))
    return g


class A13(Board):
    def construct(self):
        self.add(portrait("Ито", "1944", WHITE, 1.1).move_to([0, -1.8, 0]),
                 *[Arrow([0.0, -1.2, 0], [x, 0.6, 0], buff=0.05).set_stroke(C_NOTE, 3) for x in (-3.5, 0.0, 3.5)],
                 lab("дальше пути расходятся", 24).move_to([0, 2.2, 0]))
        self.snap()
        self.clear_keep_bar()
        j, xs, ys = jagged(-5, -0.4, 0.2, 0.25, 30, 41)
        jump = poly_line([[-0.4, ys[-1], 0], [0.0, ys[-1] + 1.2, 0]], C_BAD, 4)
        self.add(title2("Скачки в шуме"), j, jump, lab("скачок", 22, C_BAD).move_to([1.1, 1.0, 0]), Arrow([1.5, 0.2, 0], [2.4, 0.2, 0], buff=0).set_color(WHITE),
                 curve_of(lambda x: 1.2 * (1 / (1 + np.exp(-10 * (x - 0.5)))), 0.0, 1.0, -0.3, C_SUM, 4, 30).move_to([3.4, 0.4, 0]),
                 lab("быстрое непрерывное движение (Маркус)", 20, C_SUM).move_to([2.2, -1.3, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Столбик знает будущее"), bar_w(0, 1.2, 1.6, -1.2), lock(1.5, 0.3, C_SUM), lab("открыт", 20, C_SUM).move_to([1.5, -0.4, 0]),
                 pill("в среднем 0 — всё равно", C_SUM, 24).move_to([0, 2.2, 0]), lab("Скороход, Маллявэн", 20).move_to([0, -1.9, 0]))
        self.snap()
        self.clear_keep_bar()
        j2, xs2, ys2 = jagged(-5, 1.0, 0.0, 0.25, 40, 43)
        self.add(title2("Вся история линии"), j2, area_of(lambda x: 0.0, -5, 1.0, -1.0, C_PRICE, 0.0), line([-5, -1.1, 0], [1.0, -1.1, 0], C_PRICE, 6),
                 bar_w(1.0, 0.7, 1.4, -1.6, C_BET), Arrow([-1.0, -0.9, 0], [0.6, -1.4, 0], buff=0).set_color(C_BET),
                 lab("высота столбика зависит от всей истории (Конт, Фурнье)", 20, C_BET).move_to([0, 2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        fam = RoundedRectangle(width=7.0, height=2.6, corner_radius=0.3).set_stroke(C_NOISE, 3).move_to([0, 0.5, 0])
        self.add(title2("Граница"), fam, lab("семейство шумов, по которым можно складывать", 20, C_NOISE).move_to([0, 0.5, 0]),
                 cross(C_BAD, 0.45).move_to([4.6, 0.5, 0]), lab("шире нельзя (Бихтелер, Деллашери)", 22, C_BAD).move_to([0, -1.5, 0]))
        self.snap()


class A14(Board):
    def construct(self):
        a, b = bar_w(-2.4, 1.4, 1.0, -1.0, C_BET), bar_w(-0.8, 1.4, 1.0, -1.0, C_BET)
        whole = bar_w(2.4, 3.0, 2.4, -1.0, C_BAD, 0.3)
        self.add(title2("Целое и части"), a, b, tx("+", 40).move_to([-1.6, -0.3, 0]), tx("≠", 50, C_BAD).move_to([0.5, -0.1, 0]), whole,
                 lab("целое не равно сумме частей", 22).move_to([0, 1.9, 0]))
        self.snap()
        self.clear_keep_bar()
        bands = VGroup(*[Rectangle(width=6.0, height=0.7).set_stroke(C_BET, 2).set_fill(C_BET, 0.1).move_to([-1.0, -1.2 + 0.8 * i, 0]) for i in range(3)])
        ruler = VGroup(line([3.2, -1.5, 0], [3.2, 1.0, 0], WHITE, 4), *[line([3.0, -1.5 + 0.5 * k, 0], [3.4, -1.5 + 0.5 * k, 0], WHITE, 2) for k in range(6)])
        self.add(title2("Слой — особой мерой"), bands, ruler, lab("особая мера", 20).move_to([4.5, -0.2, 0]),
                 lab("Шоке, Сугено — выбор по многим критериям", 20, C_BET).move_to([-0.5, 2.1, 0]))
        self.snap()
        self.clear_keep_bar()
        pieces = VGroup(*[Circle(radius=0.45).set_stroke(C_SUM, 3).move_to([x, 0.3, 0]) for x in (-3.0, -1.2)],
                        VGroup(Circle(radius=0.8).set_stroke(C_SUM, 3), Circle(radius=0.3).set_stroke(C_BAD, 3)).move_to([1.2, 0.3, 0]))
        self.add(title2("Кусков минус дыр"), pieces, lab("кусков минус дыр", 24).move_to([-0.5, -1.2, 0]), lab("датчики считают цели", 20, C_NOTE).move_to([-0.5, -1.9, 0]))
        self.snap()
        self.clear_keep_bar()
        bundle = VGroup(*[curve_of(lambda x, k=k: 0.4 * np.sin(1.5 * x + k), -1.6, 1.6, 0.4 * k - 0.4, C_PRICE, 3, 30) for k in range(4)]).move_to([3.0, 0.2, 0])
        self.add(portrait("Концевич", "", WHITE, 0.9).move_to([-4.8, 0.8, 0]), portrait("Денеф", "", WHITE, 0.9).move_to([-3.2, 0.8, 0]), portrait("Лёзер", "1998", WHITE, 0.9).move_to([-1.6, 0.8, 0]),
                 bundle, lab("пространство кривых на многообразии", 20).move_to([3.0, -1.4, 0]), lab("мотивное интегрирование", 22, C_BET).move_to([-1.6, -1.0, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("График обычный"), ax(), curve_of(F, y0=B, color=C_PRICE), ruler.copy().scale(0.8).move_to([-5.2, 0.0, 0]), tx("→", 36).move_to([-4.2, 0.0, 0]),
                 lab("меняется только то, чем измеряют слой", 22).move_to([0, 2.1, 0]))
        self.snap()


class A15(Board):
    def construct(self):
        cards = VGroup(*[RoundedRectangle(width=3.0, height=2.0, corner_radius=0.15).set_stroke(c, 2) for c in (C_PRICE, C_BET, C_SUM)]).arrange(RIGHT, buff=0.5).move_to([0, 0.2, 0])
        self.add(title2("Другие сложения"), cards, *[tx(t, 22, c).move_to(card) for t, c, card in zip(("память", "перемножение", "шкала времени"), (C_PRICE, C_BET, C_SUM), cards)])
        self.snap()
        self.clear_keep_bar()
        g = VGroup(*[bar_w(-4.0 + 0.9 * i, 0.7, 1.5, -1.6, C_BET, 0.15 + 0.12 * i) for i in range(9)])
        self.add(title2("Сумма с памятью"), g, lab("далёкое прошлое", 20).move_to([-3.6, -2.2, 0]), lab("близкое прошлое весит больше", 20, C_BET).move_to([2.4, -2.2, 0]),
                 lab("Лиувилль, Риман", 22).move_to([0, 2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        row = VGroup(*[bar_w(0, 0.8, 0.5 + 0.35 * k, -0.6, C_BET, 0.45) for k in range(4)]).arrange(RIGHT, buff=0.9, aligned_edge=DOWN).move_to([0, -0.2, 0])
        ops = VGroup(*[tx("×", 36).move_to((row[k].get_center() + row[k + 1].get_center()) / 2) for k in range(3)])
        self.add(title2("Перемножаем"), row, ops, lab("Вольтерра, 1887", 22).move_to([0, 2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Шкала времени"), line([-5, 0.0, 0], [-1.0, 0.0, 0], C_PRICE, 6), *[Dot([x, 0.0, 0], radius=0.1).set_color(C_BET) for x in (1.0, 2.0, 3.0, 4.2, 5.0)],
                 lab("сплошная ось", 20, C_PRICE).move_to([-3.0, 0.7, 0]), lab("отдельные точки", 20, C_BET).move_to([3.0, 0.7, 0]), lab("Хильгер, 1988", 22).move_to([0, 2.0, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(*[pill(t, c, 26).move_to([x, 0.2, 0]) for t, c, x in (("память", C_PRICE, -4.0), ("рост в разы", C_BET, 0.0), ("дискретное время", C_SUM, 4.0))],
                 lab("каждый способ — своя задача", 24).move_to([0, -1.2, 0]))
        self.snap()


class A16(Board):
    def construct(self):
        self.add(bars_of(F, 10, -5.5, -1.0, -1.7, C_BET, 0.35), tx("как сложить столбики, чтобы сумма", 24).move_to([2.6, 1.2, 0]), tx("не зависела от способа счёта?", 24).move_to([2.6, 0.7, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Способы растут деревом"), tree(False))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Четыре пункта — четыре ветви"), tree(True))
        self.snap()
        self.clear_keep_bar()
        self.add(title2("Каждая починка — ветка"), tree(True, fixes=True))
        self.snap()
        self.clear_keep_bar()
        a = VGroup(tx("гладкая ширина", 28, C_PRICE), Arrow(LEFT, RIGHT, buff=0).scale(0.7), tx("Риман", 36)).arrange(RIGHT, buff=0.4).move_to([0, 1.2, 0])
        b = VGroup(tx("случайная ширина", 28, C_NOISE), Arrow(LEFT, RIGHT, buff=0).scale(0.7), tx("Ито", 36)).arrange(RIGHT, buff=0.4).move_to([0, 0.0, 0])
        self.add(title2("Какой брать — зависит от ширины"), a, b, lab("а дальше смотря какая задача", 24).move_to([0, -1.3, 0]))
        self.snap()


def card3(name, formula, note_, color=C_BET):
    r = RoundedRectangle(width=3.8, height=3.6, corner_radius=0.15).set_stroke(color, 2).set_fill("#0f1115", 1)
    t = tx(name, 28, color).move_to(r.get_top() + DOWN * 0.45)
    f = tx(formula, 20).move_to(r.get_center() + UP * 0.15)
    n = tx(note_, 18, C_NOTE).move_to(r.get_bottom() + UP * 0.55)
    return VGroup(r, t, f, n)


class F01(Board):
    def construct(self):
        self.add(title2("Образ → формула"), bars_of(F, 8, -4.0, -0.5, -0.6, C_BET, 0.35), Arrow(LEFT, RIGHT, buff=0).move_to([0.5, 0.4, 0]), tx("Σ", 60, C_SUM).move_to([2.0, 0.4, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(card3("Риман", "Σ значение в точке × ширина", "≈ столбики", C_BET).move_to([-2.2, 0.2, 0]),
                 lab("предел при дроблении", 20).move_to([-2.2, -2.2, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(card3("Лебег", "Σ высота слоя × размер слоя", "≈ слои", C_BET).move_to([2.2, 0.2, 0]), lab("предел по приближениям", 20).move_to([2.2, -2.2, 0]))
        self.snap()


class F02(Board):
    def construct(self):
        self.add(card3("Стилтьес", "Σ значение × приращение веса", "≈ шкала веса", C_PRICE).move_to([0, 0.2, 0]))
        self.snap()
        self.clear_keep_bar()
        self.add(card3("Ито", "значение в левой точке", "≈ замок на будущем", C_NOISE).move_to([0, 0.2, 0]))
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
        rows = [("Риман", "площадь"), ("Лебег", "пределы, рваный график"), ("Стилтьес", "неровная ширина"), ("Ито", "случайная ширина"),
                ("Стратонович", "привычные правила"), ("Лайонс", "грубая ширина")]
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
        self.add(tx("Какой способ — зависит от ширины", 40).move_to([0, 0.4, 0]))
        self.snap()
