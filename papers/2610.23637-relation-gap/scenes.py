"""Ролик по статье arXiv 2610.23637 (Bartholdi, Bridson, Mikhailov, Nicholson, «Two-generator presentations with a relation gap») простыми словами.

Единый источник правил — паспорт passport.py в этой папке: законы сценария, вопрос, станции полосы «мы здесь»,
словарь (одно слово — один смысл, сцена, где понятие вводится), палитра (один цвет — один смысл), план сцен A01–A13.
Весь рассказ идёт на одной карте игры (единство места); справка — только в конце.
Проверка сцен и текста против паспорта: uv run python core/pipeline/check_passport.py papers/2610.23637-relation-gap

Основной мир — карта игры (в статье это граф Кэли группы ⟨x, t | x^6, [x^3, t·x^2·t^−1]⟩):
  • «шаг» (x) — ход по кругу из шести точек; шесть шагов возвращают на место;
  • «лифт» (t) — из каждой точки свой лифт на свой круг этажом выше; лифт вниз — тот же лифт обратно;
  • этаж = сколько раз поднялись минус сколько спустились (гомоморфизм G → Z, убивающий x) — образ точный;
  • «полкруга» = x^3, «крюк» = t·x^2·t^−1; второе правило — два маршрута в одну точку (SquareMap).
Круги C1 = t⟨x⟩ и C3 = x^3·t⟨x⟩ различны (по модулю x^2 группа равна C2 * Z, а t^−1·x·t там не лежит в ⟨x⟩), C2 ≠ C0 (по модулю x^3).
Равенства из доказательства для случая x^6 (p = 3, q = 2) пересчитаны вручную при подготовке ролика.
Запуск (из корня репозитория): uv run manimgl papers/2610.23637-relation-gap/scenes.py A05 -w --hd
Весь ролик с озвучкой: uv run python core/pipeline/build.py papers/2610.23637-relation-gap"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                  # корень репозитория
sys.path.insert(0, str(ROOT / "core"))  # общая часть: manimkit
sys.path.insert(0, str(HERE))           # своя часть статьи: паспорт, текст, модели
import numpy as np
from manimlib import *
from manimkit import *
from manimkit import Base as _Base
from passport import STATIONS, SCENES

# палитра паспорта: один цвет — один смысл
C_STEP = "#58a6ff"    # шаг и круги
C_LIFT = "#e3b341"    # лифт
C_PLAYER = "#d2a8ff"  # игрок и его маршруты (второй маршрут — пунктиром)
C_BOOK = "#3fb950"    # бухгалтер, записи, книга
C_NO = "#f85149"      # «нельзя», «не дружат»
C_NOTE = "#8b949e"    # подписи, справка

STATION_OF = {code: st for code, st, *_ in SCENES}


class Base(_Base):
    # темп: при сборке с озвучкой подгоняется под речь (переменная SLOW)
    SLOW = float(os.environ.get("SLOW", 1.6))

    def setup(self):
        super().setup()
        code = type(self).__name__
        if code in STATION_OF:
            self.add(story_bar(STATIONS.index(STATION_OF[code])))


def story_bar(active):
    """Полоса «мы здесь»: пройденные станции — серые, текущая — белая, будущие — тусклые."""
    n = len(STATIONS)
    xs = np.linspace(-6.0, 6.0, n)
    y = -3.62
    g = VGroup(Line([xs[0], y, 0], [xs[-1], y, 0]).set_stroke(C_NOTE, 1, opacity=0.4))
    for i, (x, name) in enumerate(zip(xs, STATIONS)):
        col, op = (WHITE, 1.0) if i == active else (C_NOTE, 0.9 if i < active else 0.35)
        g.add(Dot([x, y, 0], radius=0.07 if i != active else 0.1).set_color(col).set_opacity(op))
        g.add(tx(name, 16, col).set_opacity(op).move_to([x, y - 0.24, 0]))
    return g


def note(s, color=C_NOTE, y=-3.05):
    """Подпись внизу кадра — над полосой «мы здесь»."""
    return tx(s, 26, color).move_to(DOWN * (-y))


# ---------- карта игры ----------

RX, RY = 0.95, 0.38  # круг лежит на этаже, поэтому сплюснут — видим его чуть сверху


def ring_pts(c):
    """Точки круга: k = 0 — ближняя, дальше по шагам против часовой стрелки (если смотреть сверху)."""
    return [np.array(c, dtype=float) + np.array([RX * np.cos(np.radians(-90 + 60 * k)), RY * np.sin(np.radians(-90 + 60 * k)), 0])
            for k in range(6)]


def ring(c, op=1.0, dot=0.07):
    pts = ring_pts(c)
    line = Polygon(*pts).set_stroke(C_STEP, 3, opacity=0.7 * op)
    dots = VGroup(*[Dot(p, radius=dot).set_color(C_STEP).set_opacity(op) for p in pts])
    return VGroup(line, dots)


def lift(a, b, op=1.0, width=5):
    return Arrow(a, b, buff=0.08, stroke_width=width).set_color(C_LIFT).set_opacity(op)


def floors(ys=(-2.0, 1.0), x0=-6.9, x1=6.9):
    g = VGroup()
    for i, y in enumerate(ys):
        g.add(DashedLine([x0 + 1.0, y - 0.7, 0], [x1, y - 0.7, 0], dash_length=0.12).set_stroke(C_NOTE, 1, opacity=0.5))
        g.add(tx(f"этаж {i}", 20, C_NOTE).move_to([x0 + 0.5, y, 0]))
    return g


def walk(scene, tok, pts, rt=0.35, trail=None, dashed=False):
    """Провести фишку по точкам; trail — цвет следа (остаётся на экране), dashed — пунктирный след."""
    segs = VGroup()
    for p in pts:
        a = tok.get_center().copy()
        anims = [tok.animate.move_to(p)]
        if trail:
            seg = (DashedLine(a, p, dash_length=0.12) if dashed else Line(a, p)).set_stroke(trail, 7, opacity=0.9)
            segs.add(seg)
            anims.append(ShowCreation(seg))
        scene.play(*anims, run_time=rt)
    return segs


class SquareMap:
    """Фрагмент карты, на котором видно второе правило.
    s — старт на круге C0 (этаж 0). Маршрут 1: крюк (лифт вверх на C1, два шага, лифт вниз на C2), потом полкруга по C2.
    Маршрут 2: полкруга по C0 (в точку p), потом крюк (лифт вверх на C3, два шага, лифт вниз). Оба приходят в E на C2."""

    def __init__(self, shift=ORIGIN, ys=(-2.0, 1.0), op=1.0):
        y0, y1 = ys
        sh = np.array(shift, dtype=float)
        self.C = {"C0": np.array([-3.6, y0, 0]) + sh, "C2": np.array([0.4, y0, 0]) + sh,
                  "C1": np.array([-2.4, y1, 0]) + sh, "C3": np.array([1.6, y1, 0]) + sh}
        P = {k: ring_pts(c) for k, c in self.C.items()}
        self.P = P
        self.s, self.p = P["C0"][4], P["C0"][1]
        self.b, self.E = P["C2"][4], P["C2"][1]
        self.rings = VGroup(*[ring(c, op=op) for c in self.C.values()])
        self.lifts = VGroup(lift(self.s, P["C1"][4], op), lift(self.b, P["C1"][0], op),
                            lift(self.p, P["C3"][4], op), lift(self.E, P["C3"][0], op))
        self.route1 = [P["C1"][4], P["C1"][5], P["C1"][0], self.b, P["C2"][5], P["C2"][0], P["C2"][1]]
        self.route2 = [P["C0"][5], P["C0"][0], P["C0"][1], P["C3"][4], P["C3"][5], P["C3"][0], self.E]

    def group(self):
        return VGroup(self.rings, self.lifts)

    def loop2(self):
        """Петля второго правила: туда маршрутом 1, обратно маршрутом 2."""
        return [self.s] + self.route1 + list(reversed(self.route2[:-1])) + [self.s]


def mini_map(scale=0.32):
    return SquareMap().group().scale(scale)


# ---------- миниатюры: петли и маршруты с карты в малом виде ----------

def _tip(end, direction, color, size=0.14):
    """Наконечник стрелки в точке end по направлению direction."""
    d = np.array(direction, dtype=float)
    d = d / np.linalg.norm(d)
    n = np.array([-d[1], d[0], 0])
    return Polygon(end, end - d * size + n * size * 0.6, end - d * size - n * size * 0.6).set_stroke(width=0).set_fill(color, 1)


def thumb_circle(color, r=0.3):
    """Петля правила 1: обход по кругу со стрелкой — шесть шагов и снова старт."""
    arc = Arc(start_angle=-PI / 2 + 0.25, angle=TAU - 0.5, radius=r).set_stroke(color, 5)
    end = arc.get_end()
    tip = _tip(end, arc.get_end() - arc.point_from_proportion(0.97), color)
    start = Dot(arc.get_start(), radius=0.06).set_color(WHITE)
    return VGroup(arc, tip, start)


def thumb_loop2(color, w=0.75, h=0.32):
    """Петля правила 2: из старта в одну точку двумя путями — сплошным и пунктиром."""
    s_, e_ = LEFT * w / 2, RIGHT * w / 2
    up = ArcBetweenPoints(s_, e_, angle=-PI * 0.7).set_stroke(color, 5)
    lo = DashedVMobject(ArcBetweenPoints(s_, e_, angle=PI * 0.7).set_stroke(color, 5), num_dashes=7)
    tip1 = _tip(e_, e_ - up.point_from_proportion(0.95), color)
    dots = VGroup(Dot(s_, radius=0.06).set_color(WHITE), Dot(e_, radius=0.06).set_color(WHITE))
    return VGroup(up, lo, tip1, dots)


def thumb_half(color=None, r=0.3):
    """Полкруга: три шага из шести, со стрелкой."""
    color = color or C_STEP
    base = Circle(radius=r).set_stroke(color, 2, opacity=0.3)
    arc = Arc(start_angle=-PI / 2, angle=PI, radius=r).set_stroke(color, 6)
    tip = _tip(arc.get_end(), arc.get_end() - arc.point_from_proportion(0.95), color)
    return VGroup(base, arc, tip)


def thumb_two(color=None, r=0.3):
    """Два шага: треть круга, со стрелкой."""
    color = color or C_STEP
    base = Circle(radius=r).set_stroke(color, 2, opacity=0.3)
    arc = Arc(start_angle=-PI / 2, angle=TAU / 3, radius=r).set_stroke(color, 6)
    tip = _tip(arc.get_end(), arc.get_end() - arc.point_from_proportion(0.95), color)
    return VGroup(base, arc, tip)


def thumb_hook():
    """Крюк: лифт вверх, два шага наверху, лифт вниз — со стрелками по ходу."""
    a, b, c, d = LEFT * 0.35 + DOWN * 0.32, LEFT * 0.35 + UP * 0.3, RIGHT * 0.35 + UP * 0.3, RIGHT * 0.35 + DOWN * 0.32
    up = Line(a, b).set_stroke(C_LIFT, 6)
    top = Line(b, c).set_stroke(C_STEP, 6)
    dn = Line(c, d).set_stroke(C_LIFT, 6)
    return VGroup(up, top, dn, _tip(b, UP, C_LIFT), _tip(c, RIGHT, C_STEP), _tip(d, DOWN, C_LIFT))


def thumb_mix(color):
    """Хитрая запись: смесь двух петель."""
    return VGroup(thumb_circle(color, 0.22), tx("+", 26, color), thumb_loop2(color, 0.55, 0.24)).arrange(RIGHT, buff=0.1)


def framed(mob, label, color, size=24):
    box = RoundedRectangle(width=1.5, height=1.1, corner_radius=0.12).set_stroke(color, 3).set_fill(color, 0.08)
    mob.move_to(box)
    return VGroup(VGroup(box, mob), tx(label, size, color)).arrange(DOWN, buff=0.15)


def person(label="Игрок"):
    headc = Circle(radius=0.3).set_stroke(C_PLAYER, 4).set_fill(C_PLAYER, 0.25)
    body = Arc(start_angle=0, angle=PI, radius=0.55).set_stroke(C_PLAYER, 4).next_to(headc, DOWN, buff=0.08)
    return VGroup(VGroup(headc, body), tx(label, 28, C_PLAYER)).arrange(DOWN, buff=0.2)


def book(entries=(), label="Бухгалтер"):
    """Книга бухгалтера; entries — миниатюры петель, вписанные в страницу."""
    page = RoundedRectangle(width=1.5, height=1.8, corner_radius=0.1).set_stroke(C_BOOK, 4).set_fill(C_BOOK, 0.1)
    rows = VGroup(*[e.copy() for e in entries])  # миниатюры уже нужного цвета; перекраска заливала дуги
    if len(rows):
        rows.arrange(DOWN, buff=0.15).set_max_height(1.5).move_to(page)
    else:
        rows = VGroup(*[Line(LEFT * 0.45, RIGHT * 0.45).set_stroke(C_BOOK, 3).shift(UP * (0.45 - 0.3 * i)) for i in range(4)]).move_to(page)
    return VGroup(VGroup(page, rows), tx(label, 28, C_BOOK)).arrange(DOWN, buff=0.2)


def lead_tag():
    return pill("азы", C_NOTE, 20).to_corner(UL, buff=0.35)


def small_arrow(a, b, color, width=5):
    return Arrow(a, b, buff=0.05, stroke_width=width).set_color(color)


def tick(color=WHITE):
    return check(color).scale(0.6)


# ---------- акт 1: вопрос и мир ----------

class A01(Base):
    """О чём ролик: игру описывают ходами и правилами; два способа счёта — могут ли разойтись? 50 лет не знали."""
    def construct(self):
        q = tx("Сколько правил нужно, чтобы описать игру?", 40).to_edge(UP, buff=0.5)
        self.play(Write(q), run_time=1.5)
        mm = mini_map(0.42).move_to(UP * 0.9)
        eq = tx("игра = ходы + правила", 28, C_NOTE).next_to(mm, DOWN, buff=0.3)
        self.play(FadeIn(mm), FadeIn(eq))
        pl = VGroup(person(), tx("честно", 24, C_PLAYER)).arrange(DOWN, buff=0.15).move_to(LEFT * 4.6 + DOWN * 0.6)
        bk = VGroup(book(), tx("быстро", 24, C_BOOK)).arrange(DOWN, buff=0.15).scale(0.85).move_to(RIGHT * 4.6 + DOWN * 0.6)
        self.play(FadeIn(pl))
        self.play(FadeIn(bk))
        stake = pill("50 лет вопрос: могут ли два ответа разойтись?", C_LIFT, 26).move_to(DOWN * 2.75)
        self.play(FadeIn(stake))
        self.wait(2)


class A02(Base):
    """Карточка статьи: название, авторы, дата и суть одной фразой. Вход: карта и вопрос уходят в угол. Выход: карта возвращается."""
    def construct(self):
        mm = mini_map(0.42).move_to(UP * 0.9)
        self.add(mm)
        self.play(mm.animate.scale(0.6).to_corner(UL, buff=0.5), run_time=1)
        card = RoundedRectangle(width=9.6, height=4.2, corner_radius=0.2).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.06).move_to(RIGHT * 1.0 + UP * 0.6)
        lines = VGroup(
            tx("arXiv 2610.23637 · 16 октября 2026", 22, C_NOTE),
            tx("Two-generator presentations with a relation gap", 30),
            tx("«Копредставления с двумя образующими и разрывом соотношений»", 22, C_NOTE),
            tx("Лоран Бартольди · Мартин Бридсон · Роман Михайлов · Джон Николсон", 24),
        ).arrange(DOWN, buff=0.3).move_to(card.get_center() + UP * 0.6)
        self.play(FadeIn(card), FadeIn(lines[0]), Write(lines[1]), run_time=1.5)
        self.play(FadeIn(lines[2]), FadeIn(lines[3]))
        gist = VGroup(
            tx("Суть:", 26, C_LIFT),
            person().scale(0.45), tx("честно — 2 правила", 26, C_PLAYER),
            book().scale(0.38), tx("быстро — 1", 26, C_BOOK),
        ).arrange(RIGHT, buff=0.3).move_to(card.get_center() + DOWN * 1.35)
        self.play(FadeIn(gist))
        self.wait(1.5)
        # переходник обратно в мир карты: карточка уходит, карта возвращается в центр
        self.play(FadeOut(VGroup(card, lines, gist)), mm.animate.scale(1 / 0.6).move_to(ORIGIN), run_time=1.2)
        self.play(FadeIn(note("вот эта игра")))
        self.wait(1)


class A03(Base):
    """Шаг по кругу; правило 1: шесть шагов — на месте."""
    def construct(self):
        self.add(head("Игра: шаг"))
        c0 = np.array([-2.4, -0.6, 0])
        self.play(FadeIn(ring(c0).scale(1.5, about_point=c0)))
        P0 = [c0 + 1.5 * (p - c0) for p in ring_pts(c0)]
        tok = Dot(P0[0], radius=0.16).set_color(WHITE)
        self.play(FadeIn(tok))
        lab = VGroup(small_arrow(ORIGIN, RIGHT * 0.6, C_STEP), tx("шаг — по кругу", 30, C_STEP)).arrange(RIGHT, buff=0.25)
        lab.move_to(RIGHT * 3.2 + UP * 1.2)
        self.play(FadeIn(lab))
        walk(self, tok, [P0[k % 6] for k in range(1, 7)], rt=0.35)
        self.play(FadeIn(pill("Правило 1: шесть шагов — на месте", C_STEP, 28).move_to(RIGHT * 3.2 + DOWN * 0.2)))
        self.wait(2)


class A04(Base):
    """Лифт на свой круг этажом выше; из кругов и лифтов — карта."""
    def construct(self):
        self.add(head("Игра: лифт"))
        self.add(floors(ys=(-2.0, 1.0)))
        c0 = np.array([-2.6, -2.0, 0])
        P0 = ring_pts(c0)
        self.add(ring(c0))
        tok = Dot(P0[0], radius=0.15).set_color(WHITE)
        self.add(tok)
        tops = [np.array([-4.6, 1.0, 0]), np.array([-2.4, 1.0, 0]), np.array([-0.2, 1.0, 0])]
        src = [P0[4], P0[0], P0[2]]
        ups = VGroup(*[VGroup(ring(c, op=0.8), lift(s, ring_pts(c)[0])) for c, s in zip(tops, src)])
        lab = VGroup(small_arrow(ORIGIN, UP * 0.6, C_LIFT),
                     VGroup(tx("лифт — на свой круг", 28, C_LIFT), tx("этажом выше", 28, C_LIFT)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)).arrange(RIGHT, buff=0.25)
        lab.move_to([1.6 + lab.get_width() / 2, 2.0, 0])
        self.play(FadeIn(lab))
        self.play(LaggedStartMap(FadeIn, ups, lag_ratio=0.5), run_time=2)
        self.play(tok.animate.move_to(ring_pts(tops[1])[0]), run_time=0.8)
        self.play(tok.animate.move_to(P0[0]), run_time=0.8)
        nt = VGroup(tx("из каждой точки — свой лифт", 24), tx("лифт вниз — обратно", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        nt.next_to(lab, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(FadeIn(nt))
        self.play(FadeIn(note("круги и лифты вместе — карта игры")))
        self.wait(2)


class A05(Base):
    """Правило 2: полкруга и крюк приводят в одну точку — их можно менять местами."""
    def construct(self):
        self.add(head("Правило 2: полкруга и крюк"))
        m = SquareMap(shift=LEFT * 0.9 + DOWN * 0.2, ys=(-2.0, 0.9))
        self.add(floors(ys=(-2.2, 0.7), x1=3.6))
        self.play(FadeIn(m.group()))
        leg = VGroup(
            VGroup(thumb_half(), tx("полкруга = 3 шага", 24, C_STEP)).arrange(RIGHT, buff=0.25),
            VGroup(thumb_hook(), tx("крюк = лифт вверх, 2 шага, лифт вниз", 24, C_LIFT)).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_corner(UR, buff=0.3).shift(DOWN * 0.9)
        self.play(FadeIn(leg))
        self.add(Dot(m.s, radius=0.14).set_color(WHITE), tx("старт", 22).next_to(m.s, LEFT, buff=0.15).shift(UP * 0.15))
        t1 = Dot(m.s, radius=0.15).set_color(C_PLAYER)
        self.add(t1)
        walk(self, t1, m.route1, rt=0.4, trail=C_PLAYER)
        t2 = Dot(m.s, radius=0.15).set_color(C_PLAYER)
        self.add(t2)
        walk(self, t2, m.route2, rt=0.4, trail=C_PLAYER, dashed=True)
        fin = Circle(radius=0.3).move_to(m.E).set_stroke(WHITE, 4)
        self.play(ShowCreation(fin))
        self.add(tx("одна точка", 22).next_to(fin, RIGHT, buff=0.15))
        res = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.5).set_stroke(C_PLAYER, 6), tx("крюк, потом полкруга", 24, C_PLAYER)).arrange(RIGHT, buff=0.2),
            VGroup(DashedLine(ORIGIN, RIGHT * 0.5, dash_length=0.1).set_stroke(C_PLAYER, 6), tx("полкруга, потом крюк", 24, C_PLAYER)).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(RIGHT * 4.8 + DOWN * 1.0)
        self.play(FadeIn(res))
        self.play(FadeIn(note("эти два хода можно менять местами")))
        self.wait(2)


class A06(Base):
    """Зачем игра такая: каждая деталь понадобится — возвратный шаг и друзья игроку, числа 3 и 2 бухгалтеру («ружья» на стене)."""
    def construct(self):
        self.add(head("Почему игра именно такая"))
        self.add(tx("каждая деталь понадобится для ответа", 26, C_NOTE).move_to(UP * 2.55))
        who_pl = lambda: person().scale(0.42)
        who_bk = lambda: book().scale(0.36)
        rows = [
            (thumb_circle(C_STEP, 0.38), "шаг через 6 повторов возвращает на место", C_STEP, who_pl()),
            (VGroup(thumb_half(), tx("↔", 26, C_PLAYER), thumb_hook()).arrange(RIGHT, buff=0.12).scale(0.65),
             "полкруга и крюк — друзья: их можно менять местами", C_PLAYER, who_pl()),
            (VGroup(tx("3", 40, C_STEP), tx("и", 24, C_NOTE), tx("2", 40, C_LIFT)).arrange(RIGHT, buff=0.2),
             "3 шага в полкруга и 2 в крюке: нет общего делителя", WHITE, who_bk()),
        ]
        grid = VGroup()
        for k, (icon, text, col, who) in enumerate(rows):
            y = 1.35 - k * 1.55
            icon.move_to([-5.5, y, 0])
            t = tx(text, 25, col)
            t.move_to([-4.2 + t.get_width() / 2, y, 0])
            ar = Arrow([t.get_right()[0] + 0.3, y, 0], [4.9, y, 0], buff=0).set_color(C_NOTE)
            who.move_to([5.7, y, 0])
            grid.add(VGroup(icon, t, ar, who))
        for g in grid:
            self.play(FadeIn(g[0]), FadeIn(g[1]), run_time=0.8)
            self.play(GrowArrow(g[2]), FadeIn(g[3]), run_time=0.6)
        self.play(FadeIn(note("дальше эти детали «выстрелят» — в объяснении ответа")))
        self.wait(2)


# ---------- акт 2: два счёта, ответ и почему ----------

class A07(Base):
    """Игрок: правила — маршруты, лишние выбрасываем; у него 2."""
    def construct(self):
        self.add(head("Счёт игрока"))
        pl = person().scale(0.8).to_corner(UL, buff=0.4).shift(DOWN * 0.7)
        self.add(pl)
        c0 = LEFT * 2.6 + DOWN * 0.7
        self.play(FadeIn(ring(c0).scale(1.5, about_point=c0)))
        P0 = [c0 + 1.5 * (p - c0) for p in ring_pts(c0)]
        t = Dot(P0[0], radius=0.15).set_color(C_PLAYER)
        self.add(t)
        walk(self, t, [P0[k % 6] for k in range(1, 13)], rt=0.18, trail=C_PLAYER)
        rows = VGroup(
            pill("правило 1: 6 шагов — на месте", C_PLAYER, 24),
            pill("правило 2: полкруга и крюк меняются", C_PLAYER, 24),
            VGroup(pill("12 шагов — на месте", C_PLAYER, 24), tx("лишнее: правило 1 дважды", 22, C_NO)).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(RIGHT * 3.0 + UP * 1.1)
        for r in rows:
            self.play(FadeIn(r))
        strike = Line(rows[2][0].get_left(), rows[2][0].get_right()).set_stroke(C_NO, 5)
        self.play(ShowCreation(strike))
        self.add(VGroup(tx("правило — маршрут в старт,", 24), tx("порядок ходов важен", 24, C_PLAYER)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(RIGHT * 2.4 + DOWN * 1.3))
        self.play(FadeIn(note("у игрока — 2 правила, меньше не выходит", C_PLAYER)))
        self.wait(2)


class A08(Base):
    """Бухгалтер: правила — записи-петли, складываются в любом порядке; меньше бывает?"""
    def construct(self):
        self.add(head("Счёт бухгалтера"))
        bk = book().scale(0.7).to_corner(UR, buff=0.4).shift(DOWN * 0.6)
        self.add(bk)
        m = SquareMap(shift=LEFT * 1.6 + DOWN * 0.2, ys=(-2.0, 0.9), op=0.45)
        self.play(FadeIn(m.group()))
        lp = Polygon(*m.P["C0"]).set_stroke(C_PLAYER, 7).set_fill(C_PLAYER, 0.15)
        self.play(ShowCreation(lp))
        self.play(lp.animate.set_stroke(C_BOOK).set_fill(C_BOOK, 0.15), run_time=0.8)
        self.add(tx("петля → запись", 22, C_BOOK).next_to(lp, DOWN, buff=0.12))
        copies = VGroup(*[Polygon(*m.P[n]).set_stroke(C_BOOK, 5, opacity=0.7).set_fill(C_BOOK, 0.1) for n in ("C1", "C2", "C3")])
        self.play(LaggedStart(*[TransformFromCopy(lp, c) for c in copies], lag_ratio=0.4), run_time=2.2)
        sq = VMobject().set_points_as_corners(m.loop2()).set_stroke(C_BOOK, 5)
        self.play(ShowCreation(sq), run_time=1.5)
        rows = VGroup(
            tx("записи складываются", 26),
            tx("в любом порядке", 26, C_BOOK),
            tx("и переносятся по карте", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(RIGHT * 4.4 + DOWN * 0.3)
        self.play(FadeIn(rows))
        self.play(FadeIn(pill("записей не больше, чем правил у игрока. А меньше бывает?", C_LIFT, 24).move_to(DOWN * 2.85)))
        self.wait(2)


class A09(Base):
    """Бывает: бухгалтеру хватает 1 записи, игроку нужно 2 правила."""
    def construct(self):
        self.add(head("Ответ: бывает"))
        pl = person().scale(0.85).move_to(LEFT * 4.6 + UP * 1.0)
        bk = book().scale(0.75).move_to(LEFT * 4.6 + DOWN * 1.6)
        self.play(FadeIn(pl), FadeIn(bk))
        c2 = VGroup(framed(thumb_circle(C_PLAYER), "правило 1", C_PLAYER, 20), framed(thumb_loop2(C_PLAYER), "правило 2", C_PLAYER, 20)).arrange(RIGHT, buff=0.3)
        c2.next_to(pl, RIGHT, buff=0.8)
        c1 = framed(thumb_mix(C_BOOK), "одна запись", C_BOOK, 20).next_to(bk, RIGHT, buff=0.8)
        self.play(FadeIn(c2))
        self.add(tx("нужно 2 правила", 30, C_PLAYER).next_to(c2, RIGHT, buff=0.5))
        self.play(FadeIn(c1))
        self.add(tx("хватает 1 записи", 30, C_BOOK).next_to(c1, RIGHT, buff=0.5))
        self.play(FadeIn(note("почему так — с обеих сторон", WHITE)))
        self.wait(2)


class A10(Base):
    """Почему игроку 2: у полкруга два друга, которые не дружат — по Ньюману правило не одно."""
    def construct(self):
        self.add(head("Почему игроку мало одного правила"))
        dfn = VGroup(tx("друзья —", 26, C_PLAYER), tx("ходы, которые можно менять местами", 26)).arrange(RIGHT, buff=0.2).move_to(UP * 2.4)
        self.play(FadeIn(dfn))
        A = framed(thumb_half(), "полкруга", C_STEP, 22).move_to(LEFT * 3.2 + UP * 0.9)
        F1 = framed(thumb_two(), "2 шага", C_STEP, 22).move_to(LEFT * 5.0 + DOWN * 1.3)
        F2 = framed(thumb_hook(), "крюк", C_LIFT, 22).move_to(LEFT * 1.4 + DOWN * 1.3)
        self.play(FadeIn(A))
        e1 = Line(A.get_bottom(), F1[0].get_top(), buff=0.1).set_stroke(C_PLAYER, 5)
        e2 = Line(A.get_bottom(), F2[0].get_top(), buff=0.1).set_stroke(C_PLAYER, 5)
        self.play(FadeIn(F1), FadeIn(F2), ShowCreation(e1), ShowCreation(e2))
        e3 = DashedLine(F1[0].get_right(), F2[0].get_left(), buff=0.1).set_stroke(C_NO, 5)
        self.play(ShowCreation(e3))
        self.add(cross().scale(0.6).move_to(e3.get_center()))
        legend = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.5).set_stroke(C_PLAYER, 5), tx("друзья полкруга", 20, C_PLAYER)).arrange(RIGHT, buff=0.2),
            VGroup(DashedLine(ORIGIN, RIGHT * 0.5).set_stroke(C_NO, 5), tx("между собой — нет", 20, C_NO)).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(LEFT * 3.2 + DOWN * 2.85)
        self.add(legend)
        rule = VGroup(
            tx("Ньюман, 1973:", 28, C_LIFT),
            tx("если правило одно", 26),
            tx("и какой-то ход возвращает", 26),
            tx("на место, как шаг, —", 26),
            tx("друзья любого хода", 26),
            tx("дружат и между собой", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to(RIGHT * 3.4 + UP * 0.5)
        self.play(FadeIn(rule))
        self.play(FadeIn(pill("значит, одного правила мало", C_PLAYER, 26).move_to(RIGHT * 3.4 + DOWN * 2.0)))
        self.wait(2)


class A11(Base):
    """Почему бухгалтеру 1: одна хитрая запись, из копий которой получаются обе петли."""
    def construct(self):
        self.add(head("Почему бухгалтеру хватает одной записи"))
        e1 = framed(thumb_circle(C_BOOK), "петля правила 1", C_BOOK, 22).move_to(LEFT * 4.8 + UP * 1.0)
        e2 = framed(thumb_loop2(C_BOOK), "петля правила 2", C_BOOK, 22).move_to(LEFT * 4.8 + DOWN * 1.5)
        self.play(FadeIn(e1), FadeIn(e2))
        one = framed(thumb_mix(C_BOOK), "одна хитрая запись", C_BOOK, 26)
        one.scale(1.15).move_to(LEFT * 0.9 + DOWN * 0.25)
        m1 = Arrow(e1.get_right(), one.get_left() + UP * 0.3, buff=0.2).set_color(C_NOTE)
        m2 = Arrow(e2.get_right(), one.get_left() + DOWN * 0.3, buff=0.2).set_color(C_NOTE)
        self.play(GrowArrow(m1), GrowArrow(m2))
        self.play(FadeIn(one))
        self.add(tx("смесь двух петель", 22, C_NOTE).next_to(one, DOWN, buff=0.25))
        back = VGroup(
            tx("из её копий обратно:", 28),
            VGroup(tick(C_BOOK), tx("петля правила 2 — сразу", 28, C_BOOK)).arrange(RIGHT, buff=0.3),
            VGroup(tick(C_BOOK), tx("петля правила 1 — за три действия", 28, C_BOOK)).arrange(RIGHT, buff=0.3),
            VGroup(tx("3", 32, C_STEP), tx("и", 22, C_NOTE), tx("2", 32, C_LIFT), tx("без общего делителя —", 24), tx("поэтому слиплись", 24, C_BOOK)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to(RIGHT * 4.0 + UP * 0.5)
        for b in back:
            self.play(FadeIn(b))
        self.play(FadeIn(note("школьная алгебра; пересчитано вручную при подготовке ролика")))
        self.wait(2)


# ---------- акт 3: развязка ----------

class A12(Base):
    """Возврат к вопросу: быстрый счёт может дать меньше; задача закрыта; бонус Уолла одной строкой."""
    def construct(self):
        self.add(head("Главное"))
        q = VGroup(tx("Вопрос:", 26, C_NOTE), tx("может ли быстрый счёт бухгалтера дать меньше правил, чем честный счёт игрока?", 24)).arrange(RIGHT, buff=0.25)
        q.move_to(UP * 2.2)
        self.play(FadeIn(q))
        ans = tx("Может", 56, C_LIFT).move_to(UP * 1.1)
        self.play(Write(ans))
        rows = VGroup(
            VGroup(person().scale(0.5), tx("2 правила — друзья полкруга не дружат между собой", 24, C_PLAYER)).arrange(RIGHT, buff=0.35),
            VGroup(book().scale(0.42), tx("1 запись — одна хитрая запись даёт обе петли", 24, C_BOOK)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.7 + LEFT * 0.3)
        for r in rows:
            self.play(FadeIn(r))
        self.play(FadeIn(note("бонус: тот же пример решает задачу Уолла (1965) — если подтвердится свежий результат OpenAI")))
        self.wait(2)


# ---------- приложение: тот же путь формулами и аналогиями ----------

C_FORM = WHITE


def app_tag():
    return pill("приложение", C_NOTE, 20).to_corner(UL, buff=0.35)


def formal_card(scene, title, picture, formula, explain, analogy):
    """Карточка приложения: слева значок из рассказа, справа формула, под ней пояснение и аналогия."""
    scene.add(head(title), app_tag())
    pic = picture.move_to(LEFT * 4.7 + UP * 0.5)
    scene.play(FadeIn(pic), run_time=0.8)
    eq = (formula if isinstance(formula, Mobject) else tx(formula, 44, C_FORM)).move_to(RIGHT * 1.6 + UP * 0.9)
    scene.play(Write(eq), run_time=1.2)
    ex = tx(explain, 26).move_to(RIGHT * 1.6 + DOWN * 0.4)
    scene.play(FadeIn(ex))
    an = VGroup(tx("≈", 34, C_LIFT), tx(analogy, 26, C_LIFT)).arrange(RIGHT, buff=0.25).move_to(DOWN * 2.0)
    scene.play(FadeIn(an))
    scene.wait(2)


class F01(Base):
    """Переход в приложение: игра = группа, ходы — буквы, правила — соотношения."""
    def construct(self):
        self.add(app_tag())
        mm = mini_map(0.42).move_to(UP * 0.5)
        self.add(mm)
        self.play(mm.animate.scale(0.6).to_corner(UR, buff=0.5), run_time=1)
        self.add(head("Приложение: то же самое формулами"))
        rows = [("игра", "группа"), ("ход", "буква: x, t"), ("правило", "соотношение: … = 1")]
        tbl = VGroup()
        for k, (a, b) in enumerate(rows):
            r = VGroup(tx(a, 34, C_PLAYER), tx("→", 34, C_NOTE), tx(b, 34, C_FORM)).arrange(RIGHT, buff=0.5)
            tbl.add(r)
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(LEFT * 0.8 + DOWN * 0.2)
        for r in tbl:
            self.play(FadeIn(r), run_time=0.6)
        self.play(FadeIn(note("на каждом шаге: картинка из рассказа → формула → аналогия")))
        self.wait(2)


class F02(Base):
    """Шаг = x, лифт = t, лифт вниз = t⁻¹; цепочка ходов — слово."""
    def construct(self):
        pic = VGroup(thumb_half(C_STEP), VGroup(Line(DOWN * 0.3, UP * 0.3).set_stroke(C_LIFT, 6), _tip(UP * 0.3, UP, C_LIFT))).arrange(RIGHT, buff=0.5).scale(1.5)
        eq = VGroup(tx("шаг = x", 40, C_STEP), tx("лифт = t,  вниз = t^−1", 40, C_LIFT)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        formal_card(self, "Ходы — это буквы", pic, eq, "цепочка ходов пишется словом: x·x·t", "как команды робота: «вперёд, вперёд, вверх»")


class F03(Base):
    """Правило 1: x⁶ = 1."""
    def construct(self):
        formal_card(self, "Правило 1", thumb_circle(C_STEP, 0.6), "x^6 = 1",
                    "1 значит «ничего не сделали»", "шесть поворотов на 60° — полный оборот")


class F04(Base):
    """Полкруга = x³, крюк = t·x²·t⁻¹; правило 2."""
    def construct(self):
        pic = VGroup(thumb_half(C_STEP), thumb_hook()).arrange(RIGHT, buff=0.4).scale(1.5)
        eq = VGroup(tx("полкруга = x^3,   крюк = t·x^2·t^−1", 36), tx("x^3·(t·x^2·t^−1) = (t·x^2·t^−1)·x^3", 36, C_PLAYER)).arrange(DOWN, buff=0.3)
        formal_card(self, "Правило 2", pic, eq, "порядок этих двух ходов не важен", "вправо-вверх = вверх-вправо")


class F05(Base):
    """Вся игра одной строкой."""
    def construct(self):
        pic = mini_map(0.38)
        eq = VGroup(tx("⟨ x, t  |  x^6,  [x^3, t·x^2·t^−1] ⟩", 44),
                    VGroup(tx("ходы", 22, C_NOTE), tx("соотношения", 22, C_NOTE)).arrange(RIGHT, buff=2.4)).arrange(DOWN, buff=0.2)
        formal_card(self, "Вся игра одной строкой", pic, eq, "[a, b] — коротко «a и b можно менять местами»",
                    "как правила настольной игры на одной карточке")


class F06(Base):
    """Счёт игрока: самый короткий список соотношений — 2."""
    def construct(self):
        pic = person().scale(0.9)
        eq = VGroup(tx("x^6 = 1", 36, C_PLAYER), tx("[x^3, t·x^2·t^−1] = 1", 36, C_PLAYER),
                    VGroup(tx("x^12 = 1", 32, C_NOTE), tx("— лишнее", 26, C_NO)).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        formal_card(self, "Счёт игрока: 2", pic, eq, "самый короткий список соотношений для той же группы", "самый короткий свод правил без повторов")


class F07(Base):
    """Счёт бухгалтера: записи складываются, r + s = s + r; хватает 1."""
    def construct(self):
        pic = book([thumb_circle(C_BOOK), thumb_loop2(C_BOOK)]).scale(0.9)
        eq = VGroup(tx("r + s = s + r", 44, C_BOOK), tx("записей хватает: 1", 34, C_BOOK)).arrange(DOWN, buff=0.3)
        formal_card(self, "Счёт бухгалтера: 1", pic, eq, "соотношения складываются как числа — порядок теряется", "банковская выписка: итог не помнит порядок")


class F08(Base):
    """Почему 2: x⁶ = 1 и одно соотношение ⇒ друзья дружат (Ньюман); но x² и крюк не перестановочны."""
    def construct(self):
        pic = VGroup(framed(thumb_two(), "x^2", C_STEP, 22), framed(thumb_hook(), "крюк", C_LIFT, 22)).arrange(RIGHT, buff=0.3).scale(0.85)
        eq = VGroup(tx("x^6 = 1  и одно соотношение  ⇒  друзья дружат", 30),
                    tx("но  x^2·крюк ≠ крюк·x^2", 36, C_NO)).arrange(DOWN, buff=0.3)
        formal_card(self, "Почему игроку 2 (Ньюман, 1973)", pic, eq, "значит, одним соотношением группу не задать",
                    "если друзья друзей не ладят — один закон их не описывает")


class F09(Base):
    """Почему 1: НОД(3, 2) = 1, из 3 и 2 собирается 1 = 3 − 2."""
    def construct(self):
        pic = framed(thumb_mix(C_BOOK), "одна запись", C_BOOK, 22).scale(1.2)
        eq = VGroup(tx("НОД(3, 2) = 1", 44), tx("1 = 3 − 2", 40, C_BOOK)).arrange(DOWN, buff=0.3)
        formal_card(self, "Почему бухгалтеру 1", pic, eq, "так же из двух записей собирается одна, а из неё — обе",
                    "монетами в 3 и 2 рубля можно набрать 1 рубль сдачей")


class F10(Base):
    """Как это закодировать: три строки в GAP."""
    def construct(self):
        self.add(head("Как это закодировать"), app_tag())
        code = VGroup(*[Text(l, font="Menlo", font_size=28, color=c) for l, c in [
            ('F := FreeGroup("x", "t");;  x := F.1;;  t := F.2;;', WHITE),
            ("G := F / [ x^6, Comm(x^3, t*x^2*t^-1) ];;", C_BOOK),
            ("# G — наша игра: группа и два соотношения", C_NOTE)]]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        box = SurroundingRectangle(code, buff=0.4).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.06)
        VGroup(box, code).move_to(UP * 0.4)
        self.play(FadeIn(box))
        for l in code:
            self.play(Write(l), run_time=1.0)
        self.add(tx("GAP — программа компьютерной алгебры для групп", 24, C_NOTE).next_to(box, DOWN, buff=0.4))
        self.wait(2)


class F11(Base):
    """Где это встречается: прямо — компьютерная алгебра; по аналогии — данные, спецификации."""
    def construct(self):
        self.add(head("Где это встречается"), app_tag())
        rows = [
            ("прямо", "программы компьютерной алгебры (GAP, Magma): группы задают так же", WHITE),
            ("прямо", "топология: тот же пример строит фигуру из задачи Уолла (если подтвердится OpenAI)", WHITE),
            ("аналогия", "кубик Рубика: ходы и правила, сколько правил нужно", C_NOTE),
            ("аналогия", "анализ данных: быстрый счёт «дыр» может недосчитать сложность", C_NOTE),
            ("аналогия", "спецификации ПО: самый короткий набор правил против быстрой оценки", C_NOTE),
        ]
        tbl = VGroup()
        for k, (a, b, col) in enumerate(rows):
            tag = pill(a, C_BOOK if a == "прямо" else C_NOTE, 20)
            r = VGroup(tag, tx(b, 24, col)).arrange(RIGHT, buff=0.35)
            tbl.add(r)
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(UP * 0.4)
        for r in tbl:
            self.play(FadeIn(r), run_time=0.6)
        self.play(FadeIn(pill("урок: быстрая линейная оценка сложности может её занизить", C_LIFT, 24).move_to(DOWN * 2.6)))
        self.wait(2)


class A13(Base):
    """Кто и когда: авторы, история, роль ИИ, что условно, буквенная запись."""
    def construct(self):
        self.add(head("Кто и когда"))
        y = 1.9
        self.add(Line(LEFT * 6, RIGHT * 6).shift(UP * y).set_stroke(C_NOTE, 2))
        X = lambda yr: -5.5 + (yr - 1965) / 61 * 11
        for k, (yr, a) in enumerate([(1965, "Уолл"), (1976, "Грюнберг"), (1979, "список Уолла"), (2018, "обзор Харландера"), (2026, "решение")]):
            col = WHITE if yr == 2026 else C_NOTE
            self.add(Dot([X(yr), y, 0], radius=0.09).set_color(col))
            side = 0.5 if k % 2 == 0 else -0.5  # подписи по очереди сверху и снизу, чтобы близкие годы не слипались
            self.add(VGroup(tx(str(yr), 20, col), tx(a, 18, col)).arrange(DOWN, buff=0.05).move_to([X(yr), y + side, 0]))
        rows = [
            ("Авторы", "Бартольди, Бридсон, Михайлов, Николсон · 16 октября 2026", WHITE),
            ("Доказано", "основная теорема — полностью", WHITE),
            ("Условно", "бонус про Уолла опирается на свежий результат OpenAI", C_LIFT),
            ("Роль ИИ", "ChatGPT помог найти пример и доказательство; авторы всё перепроверили", WHITE),
            ("Проверка", "независимой проверки пока не было", C_NOTE),
            ("Образ", "карта игры — точная картина объекта из статьи, не аналогия", C_NOTE),
        ]
        tbl = VGroup()
        for k, (a, b, col) in enumerate(rows):
            r = VGroup(tx(a, 22, C_NOTE), tx(b, 24, col))
            r[0].move_to([-6.2 + r[0].get_width() / 2, 0, 0])
            r[1].move_to([-4.0 + r[1].get_width() / 2, 0, 0])
            r.shift(UP * (0.55 - k * 0.5))
            tbl.add(r)
        for r in tbl:
            self.play(FadeIn(r), run_time=0.5)
        self.wait(2)
