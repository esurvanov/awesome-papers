"""Сцены ролика «Как сложить бесконечно много столбиков» (версия 4): непрерывные превращения героя-холма.
Запуск одной сцены: uv run manimgl papers/integrals-film/scenes.py A04 -w --hd  ·  весь ролик: uv run python core/pipeline/build.py papers/integrals-film
Каждая сцена начинается с последнего кадра предыдущей (мгновенно, без склейки) и дальше превращает его: объекты с одной меткой (.tag)
в соседних кадрах — один и тот же объект, он плавно меняется; новые вырастают или рисуются, лишние гаснут. Кадр = фраза диктора (self.beat)."""
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
import narration as N
from kit import *
from icons import ICONS
from world import *

Base = story_base(P.STATIONS, P.SCENES, ICONS, N.TEXT, HERE)
ORDER = [c for c, *_ in P.SCENES]


def _is_line(m):
    leaves = [x for x in m.get_family() if x.has_points()]
    return bool(leaves) and all(isinstance(x, VMobject) and x.get_fill_opacity() < 0.01 for x in leaves)


def _same(a, b):
    """Один и тот же вид: превращать не нужно, объект просто заменяется."""
    try:
        if len(a.get_family()) != len(b.get_family()):
            return False
        if not (np.allclose(a.get_center(), b.get_center(), atol=0.02) and abs(a.get_width() - b.get_width()) < 0.02
                and abs(a.get_height() - b.get_height()) < 0.02):
            return False
        la = [x for x in a.get_family() if x.has_points()]
        lb = [x for x in b.get_family() if x.has_points()]
        return not la or (la[0].get_stroke_color() == lb[0].get_stroke_color() and abs(la[0].get_fill_opacity() - lb[0].get_fill_opacity()) < 0.02
                          and abs(la[0].get_stroke_opacity() - lb[0].get_stroke_opacity()) < 0.02)
    except Exception:
        return False


def _bright(m):
    """Плотные яркие заливки: полупрозрачное делаем почти сплошным."""
    for x in m.get_family():
        if x.has_points() and isinstance(x, VMobject):
            f = x.get_fill_opacity()
            if 0.04 < f < 0.9:
                x.set_fill(opacity=min(0.95, f * 2.0))
    return m


def _dry(code):
    """«Сухой прогон» сцены: только собрать её последний кадр (для начала следующей сцены)."""
    cls = globals()[code]
    o = object.__new__(cls)
    if hasattr(cls, "end2d"):                      # объёмная сцена: её последний кадр — плоский вид спереди
        o._k, o._cur, o._dry = cls.END_K, [_bright(m) for m in o.end2d()], True
        o._capm = cap(cls.END_CAP)
        return o
    o._init()
    o._dry = True
    o.construct()
    return o


class Film(Base):
    def _init(self):
        self._k, self._cur, self._capm, self._ov, self._dry = 0, [], None, None, False

    def setup(self):
        super().setup()
        self.camera.background_rgba = [0, 0, 0, 1]
        self._init()
        i = ORDER.index(type(self).__name__)
        if i > 0:                                  # начало = последний кадр предыдущей сцены, без анимации
            p = _dry(ORDER[i - 1])
            self._cur = list(p._cur)
            self.add(*self._cur)
            if p._capm is not None:
                self._capm = p._capm
                self.add(self._capm)
            st = state_for(ORDER[i - 1], p._k)
            if st:
                self._ov = overlay(st)
                self.add(self._ov)

    # ---- кадр фразы ----
    def _enter(self, m, tag, how):
        mode = how.get(tag) if tag else None
        if mode == "create" or (mode is None and _is_line(m)):
            return ShowCreation(m)
        if tag == "bars" or mode == "grow":
            return LaggedStart(*[GrowFromEdge(b, DOWN) for b in m], lag_ratio=0.08)
        if len(m.submobjects) >= 8:
            return LaggedStart(*[FadeIn(x) for x in m], lag_ratio=0.03)
        return FadeIn(m)

    def show(self, *mobs, c=None, how=None, morph=None, rt=1.0):
        self._k += 1
        items = [_bright(m) for m in mobs]
        capm = cap(c) if c else None
        if self._dry:
            self._cur, self._capm = items, capm
            return
        code = type(self).__name__
        self.beat(self._k - 1)
        how, morph = how or {}, morph or {}
        anims, old, used = [], list(self._cur), set()
        for m in items:
            t = getattr(m, "tag", None)
            match = None
            for j, o in enumerate(old):
                ot = getattr(o, "tag", None)
                if j not in used and ot is not None and (ot == t or morph.get(ot) == t):
                    match = j
                    break
            if match is not None:
                used.add(match)
                o = old[match]
                if _same(o, m):
                    self.remove(o)
                    self.add(m)
                else:
                    anims.append(ReplacementTransform(o, m))
            else:
                anims.append(self._enter(m, t, how))
        for j, o in enumerate(old):
            if j not in used:
                anims.append(FadeOut(o))
        if capm is not None:
            anims.append(FadeTransform(self._capm, capm) if self._capm is not None else FadeIn(capm))
        elif self._capm is not None:
            anims.append(FadeOut(self._capm))
        st = state_for(code, self._k)
        ov = overlay(st, INTRO.get((code, self._k))) if st else None
        if ov is not None:
            anims.append(ReplacementTransform(self._ov, ov) if self._ov is not None else FadeIn(ov))
        elif self._ov is not None:
            anims.append(FadeOut(self._ov))
        if anims:
            self.play(*anims, run_time=rt)
        self._cur, self._capm, self._ov = items, capm, ov

    def do(self, fn):
        """Своя анимация между кадрами (в сухом прогоне не выполняется)."""
        if not self._dry:
            fn()

    def track(self, *ms):
        if not self._dry:
            self._cur = list(self._cur) + list(ms)


# ============================== акт 0: с нуля ==============================
class A01(Film):
    def construct(self):
        self.show(hill(), axis_(False, C_NOTE), c="график")
        self.show(hill(), axis_(False, C_NOTE), area(C_PRICE, 0.22), tx("площадь", 34, WHITE).move_to([0, -0.2, 0]), c="сколько места в этой фигуре")
        rect = Rectangle(width=2.4, height=1.6).set_stroke(C_BET, 3).set_fill(C_BET, 0.25).move_to([-3.6, 0.2, 0])
        arch = poly_line([[x, 0.1 + 1.6 * (1 - (x / 2.0) ** 2), 0] for x in np.linspace(-2, 2, 40)], C_PRICE, 5).move_to([3.4, 0.4, 0])
        base = line([1.4, -0.7, 0], [5.4, -0.7, 0], C_NOTE, 3)
        self.show(rect, tx("у прямоугольника всё просто", 22, C_BET).move_to([-3.6, -1.3, 0]), arch, base,
                  tx("кривая сверху: простой формулы нет", 22, C_PRICE).move_to([3.4, -1.3, 0]), c="прямоугольник считается просто")
        self.show(hill(), axis_(False, C_NOTE), area(C_PRICE, 0.15), tx("как считали и почему способ менялся", 30, WHITE).move_to([0, 2.4, 0]),
                  c="способ счёта переделывали много раз")
        self.show(tx("Как посчитать площадь так, чтобы ответ", 38).move_to([0, 1.5, 0]), tx("не зависел от способа счёта?", 38).move_to([0, 0.7, 0]),
                  hill(C_PRICE, 4, -2.6, 2.6).scale(0.5).move_to([0, -1.3, 0]), c="вопрос ролика")


class A02(Film):
    def construct(self):
        self.show(hill(), axis_(False, C_NOTE), c="как читать график")
        sl = Dot(pt(-2.5), radius=0.14).set_color(C_AXIS)
        self.show(hill(), axis_(), sl, tx("точка", 20, C_AXIS).move_to(pt(-2.5, -0.55)), c="по оси выбираем точку")
        x = -2.5
        self.show(hill(), axis_(), sl, line(pt(x), pt(x, F(x)), C_BET, 4), Dot(pt(x, F(x)), radius=0.11).set_color(C_BET),
                  dim_v(x - 0.35, AY, AY + F(x), "высота", C_BET, 22, side=-1), c="над точкой стоит число — высота")
        self.show(axis_(), c="двигаем точку — высота меняется, кривая вычерчивается")
        self.do(self.trace)
        self.show(hill(), axis_(), line(pt(-2.0), pt(-2.0, F(-2.0)), C_BET, 4), tx("высота — жёлтая", 22, C_BET).move_to(pt(-3.6, 1.1)),
                  tx("график — синий", 24, C_PRICE).move_to(pt(0.0, 3.5)), tx("ось — оранжевая", 22, C_AXIS).move_to(pt(3.2, -0.55)), c="цвета ролика")

    def trace(self):
        t = ValueTracker(-5.0)
        X = lambda: t.get_value()
        dot = always_redraw(lambda: Dot(pt(X()), radius=0.14).set_color(C_AXIS))
        vl = always_redraw(lambda: line(pt(X()), pt(X(), F(X())), C_BET, 4))
        tip = always_redraw(lambda: Dot(pt(X(), F(X())), radius=0.11).set_color(C_BET))
        trail = always_redraw(lambda: poly_line([pt(x, F(x)) for x in np.linspace(XL, max(X(), XL + 0.05), 40)], C_PRICE, 5))
        self.add(trail, vl, dot, tip)
        self.play(t.animate.set_value(5.0), run_time=4.0, rate_func=linear)
        for m in (trail, vl, dot, tip):
            m.clear_updaters()
        self.remove(vl, dot, tip)
        self.remove(trail)
        full = hill()
        self.add(full)
        self.track(full)


class A03(Film):
    def construct(self):
        self.show(hill(), axis_(), cuts(8), VGroup(*[piece(XL + i * 1.25, XL + (i + 1) * 1.25, C_AXIS, AY - 0.12, 8) for i in range(8)]), c="ось делится на куски")
        self.show(hill(), axis_(), bars(8), c="на каждом куске — столбик")
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), tx("кусок оси", 24, C_AXIS).move_to([0, -1.95, 0]),
                  tx("верх на графике", 24, C_PRICE).move_to([2.4, 1.6, 0]), tx("столбик", 26, C_BET).move_to([0, 0.0, 0]),
                  c="столбик стоит на куске оси, верх касается графика")
        self.show(hill(), axis_(), bars(16), c="вся фигура — из столбиков")


class A04(Film):
    def construct(self):
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), dim_v(2.05, -1.4, 0.6, "высота", C_BET, 24), dim_h(-1.7, 1.7, -1.95, "ширина = длина куска", C_AXIS, 22),
                  c="у столбика есть высота и ширина")
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), tx("площадь = ширина × высота", 30, WHITE).move_to([0, 2.1, 0]),
                  dim_v(2.05, -1.4, 0.6, "высота", C_BET, 24), dim_h(-1.7, 1.7, -1.95, "ширина", C_AXIS, 22), c="площадь столбика")
        self.show(hill(), axis_(), bars(10), tx("складываем площади всех столбиков", 28, C_SUM).move_to([0, 2.4, 0]), c="получается сумма")

        def mini(cx, n, val):
            g = VGroup(bars_of(F, n, -2.2, 2.2, 0.0, C_BET, 0.45), curve_of(F, -2.2, 2.2, 0.0, C_PRICE, 3, 60))
            return VGroup(g.scale(0.5, about_point=ORIGIN).move_to([cx, 0.1, 0]), tx(val, 28, C_SUM).move_to([cx, -1.5, 0]), tx(f"столбиков: {n}", 20, C_NOTE).move_to([cx, -1.05, 0]))
        sums = {6: "17,9", 12: "19,4", 24: "19,8"}
        self.show(*[mini(cx, n, sums[n]) for cx, n in ((-4.3, 6), (0.0, 12), (4.3, 24))], tx("площадь фигуры = 20", 26, WHITE).move_to([0, 2.3, 0]),
                  c="тоньше столбики — сумма ближе к площади")
        self.show(hill(), axis_(), bars(40, 0.5), plaque("1854", "Риман", WHITE, 0, 2.5), c="без конца тоньше — сумма равна площади")


class A05(Film):
    def construct(self):
        T = lambda a, b, c, col, op: Polygon(pt(*a), pt(*b), pt(*c)).set_stroke(col, 3).set_fill(col, op)
        base = [hill(), axis_(False, C_NOTE)]
        self.show(*base, plaque("III в. до н. э.", "Архимед", WHITE, 0, 2.65), tx("кусок параболы", 26, C_PRICE).move_to([0, -0.4, 0]), c="Архимед искал площадь куска параболы")
        t1 = T((-5, 0), (5, 0), (0, H), C_BET, 0.3)
        t2 = [T((0, H), (5, 0), (2.5, F(2.5)), C_AXIS, 0.4), T((-5, 0), (0, H), (-2.5, F(2.5)), C_AXIS, 0.4)]
        self.show(*base, t1, *t2, tx("вписанный треугольник", 22, C_BET).move_to([0, -0.2, 0]), tx("поменьше", 20, C_AXIS).move_to([-3.2, 0.0, 0]), tx("поменьше", 20, C_AXIS).move_to([3.2, 0.0, 0]), c="в кусок вписан треугольник, в промежутки — поменьше")
        t3 = [T((0, H), (2.5, F(2.5)), (1.25, F(1.25)), C_ADD, 0.5) for _ in range(0)]
        sq = lambda s, col: Square(side_length=s).set_stroke(col, 3).set_fill(col, 0.4)
        row = VGroup(sq(1.6, C_BET), sq(0.8, C_AXIS), sq(0.4, C_ADD), sq(0.2, C_SUM), tx("…", 30, WHITE)).arrange(RIGHT, buff=0.35, aligned_edge=DOWN).move_to([0, 0.6, 0])
        self.show(row, tx("1", 22, WHITE).next_to(row[0], DOWN, buff=0.1), tx("¼", 22, WHITE).next_to(row[1], DOWN, buff=0.1), tx("1/16", 20, WHITE).next_to(row[2], DOWN, buff=0.1),
                  c="каждый следующий ряд — четверть предыдущего")
        self.show(row.copy().move_to([0, 1.6, 0]), tx("вместе: треугольник и ещё его треть", 30, WHITE).move_to([0, -0.2, 0]),
                  tx("сумма подходит к одному числу", 26, C_SUM).move_to([0, -1.2, 0]), c="ряды не кончаются, сумма подходит к числу")
        # пятая фраза: та же идея — части, число которых растёт без конца
        self.show(VGroup(bars_of(lambda x: 1.3 * (1 - (x / 2.5) ** 2), 10, -2.5, 2.5, 0.0, C_BET, 0.4), curve_of(lambda x: 1.3 * (1 - (x / 2.5) ** 2), -2.5, 2.5, 0.0, C_PRICE, 3, 40)).move_to([3.2, 0.2, 0]),
                  VGroup(Polygon(np.array([-1.5, -0.7, 0]), np.array([1.5, -0.7, 0]), np.array([0, 0.9, 0])).set_stroke(C_BET, 3).set_fill(C_BET, 0.3)).move_to([-3.2, 0.1, 0]),
                  tx("=", 40, WHITE).move_to([0, 0.2, 0]), tx("части, которых без конца больше", 26, C_NOTE).move_to([0, -1.8, 0]), c="та же идея, что у столбиков")


def _ncurve(x, y, w, h, color=C_SUM, n=40):
    return curve_of(lambda t: h * (1 / (1 + np.exp(-1.4 * t))), -w / 2, w / 2, y, color, 4, n).move_to([x, y + h / 2, 0])


class A06(Film):
    def _acc(self, x1):
        return [tagged(area_of(F, XL, x1, AY, C_SUM, 0.35), 'fill'), tagged(line(pt(x1), pt(x1, F(x1)), C_BET, 3), 'vl'), tagged(Dot(pt(x1), radius=0.14).set_color(C_AXIS), 'sl')]

    def accumulate(self):
        t = ValueTracker(-5.0)
        X = lambda: t.get_value()
        fill = always_redraw(lambda: area_of(F, XL, max(X(), XL + 0.05), AY, C_SUM, 0.35))
        vl = always_redraw(lambda: line(pt(X()), pt(X(), F(X())), C_BET, 3))
        dot = always_redraw(lambda: Dot(pt(X()), radius=0.14).set_color(C_AXIS))
        lab = always_redraw(lambda: tx('площадь слева от точки', 22, C_SUM).move_to([X() - 2.2, 0.3, 0]))
        self.add(fill, vl, dot, lab)
        self.play(t.animate.set_value(1.0), run_time=3.0, rate_func=smooth)
        for m in (fill, vl, dot, lab):
            m.clear_updaters()
        self.remove(fill, vl, dot, lab)
        fin = self._acc(1.0)
        self.add(*fin)
        self.track(*fin)

    def construct(self):
        x1 = 1.0
        left = lambda: [*self._acc(x1), hill(), axis_(False, C_NOTE)]
        self.show(hill(), axis_(False, C_NOTE), c="нашли короткий путь")
        self.do(self.accumulate)
        self.show(*left(), portrait("Ньютон", "", WHITE, 0.9).move_to([-5.4, 2.35, 0]), portrait("Лейбниц", "", WHITE, 0.9).move_to([-3.6, 2.35, 0]),
                  plaque("XVII в.", "независимо", WHITE, 3.5, 2.65), c="Ньютон и Лейбниц, XVII век")
        def panel(g, cx, cy, sc):
            g.scale(sc, about_point=pt(0)).shift(np.array([cx, cy, 0.0]) - pt(0))
            return g
        Gf = lambda x: 2.4 * (((x + 5) - (x ** 3 + 125) / 75.0) * H / 20.0 * 20.0 / 20.0) / (H * 10 * 2 / 3) * 1.0
        grow = lambda x: 2.4 * ((x + 5) - (x ** 3 + 125) / 75.0) / (10 - 250 / 75.0)     # площадь слева от точки, 0…2,4
        xs0 = 1.0
        L = lambda extra=(): panel(VGroup(hill(C_PRICE, 4), axis_(False, C_NOTE), *extra), -3.2, -0.6, 0.5)
        R = lambda extra=(): VGroup(line([0.4, -1.8, 0], [6.0, -1.8, 0], C_NOTE, 2), poly_line([[0.4 + 5.6 * (x + 5) / 10, -1.8 + grow(x), 0] for x in np.linspace(-5, 5, 60)], C_SUM, 5), *extra)
        dotL = lambda x: Dot(pt(x), radius=0.14).set_color(C_AXIS)
        self.show(L([line(pt(xs0), pt(xs0, F(xs0)), C_BET, 4), dotL(xs0)]), R([Dot([0.4 + 5.6 * (xs0 + 5) / 10, -1.8 + grow(xs0), 0], radius=0.12).set_color(C_SUM)]),
                  tx("высота графика", 22, C_BET).move_to([-3.2, 1.4, 0]), tx("площадь слева от точки", 22, C_SUM).move_to([3.2, 0.9, 0]),
                  c="где график выше, там площадь растёт быстрее")
        xa, xb = -2.0, 2.0
        ga, gb = [0.4 + 5.6 * (x + 5) / 10 for x in (xa, xb)], [-1.8 + grow(x) for x in (xa, xb)]
        self.show(L([area_of(F, xa, xb, AY, C_SUM, 0.45), line(pt(xa), pt(xa, F(xa)), C_BET, 3), line(pt(xb), pt(xb, F(xb)), C_BET, 3)]),
                  R([Dot([ga[0], gb[0], 0], radius=0.12).set_color(C_SUM), Dot([ga[1], gb[1], 0], radius=0.12).set_color(C_SUM), line([ga[1] + 0.35, gb[0], 0], [ga[1] + 0.35, gb[1], 0], C_SUM, 4)]),
                  tx("площадь между двумя точками", 22, C_SUM).move_to([-3.2, 1.4, 0]), tx("разность двух значений", 22, C_SUM).move_to([3.2, 1.0, 0]),
                  c="площадь между точками — разность двух значений")
        s = VMobject().set_points_smoothly([np.array(p, dtype=float) for p in
                                            [(-0.45, -1.0, 0), (-0.25, -1.25, 0), (-0.05, -1.05, 0), (0.0, -0.6, 0), (0.0, 0.7, 0), (0.05, 1.05, 0), (0.25, 1.25, 0), (0.45, 1.05, 0)]]).set_stroke(WHITE, 8).set_fill(opacity=0)
        self.show(s.scale(1.2).move_to([-2.0, 0.2, 0]), tx("вытянутая S от слова summa", 28, WHITE).move_to([2.2, 0.4, 0]), portrait("Лейбниц", "", WHITE, 1.0).move_to([2.2, -1.4, 0]),
                  c="знак суммы придумал Лейбниц")


class A07(Film):
    def construct(self):
        cards = lambda lit: VGroup(*[pill(t, col if i in lit else C_NOTE, 22) for i, (t, col) in enumerate(
            [("1 · что складываем", C_PRICE), ("2 · чем меряем ширину", C_AXIS), ("3 · где берём высоту", C_BET), ("4 · как складываем", C_ADD)])]).arrange(RIGHT, buff=0.25).move_to([0, 2.4, 0])
        bb = lambda **k: big_bar(0, -1.5, 3.4, 1.9, 0.6, 0.0, **k)
        self.show(bb(), cards([]), c="у счёта есть договор из четырёх пунктов")
        self.show(big_bar(0, -1.5, 3.4, 1.9, 0.6, 0.0, bar=False), poly_line([[t * 1.7, -1.5 + 1.9 + 0.6 * t, 0] for t in np.linspace(-1.3, 1.3, 30)], C_PRICE, 9),
                  bb(curve=False, pieceline=False).set_opacity(0.3), cards([0]), c="первый пункт — какой график")
        self.show(bb(), line([-1.7, -1.5, 0], [1.7, -1.5, 0], C_AXIS, 14), cards([1]), c="второй — чем меряем ширину куска")
        self.show(bb(), Dot([0.0, -1.5 + 1.9, 0], radius=0.17).set_color(C_BET), tx("точка", 22, C_BET).move_to([0.0, 1.0, 0]), cards([2]), c="третий — где в куске берём высоту")
        self.show(bb(), tx("+", 60, C_ADD).move_to([2.8, -0.2, 0]), tablo("Σ").move_to([4.6, -0.2, 0]), cards([3]), c="четвёртый — как складываем")

        def mini(cx, n, val):
            g = VGroup(bars_of(F, n, -2.2, 2.2, 0.0, C_BET, 0.45), curve_of(F, -2.2, 2.2, 0.0, C_PRICE, 3, 60))
            return VGroup(g.scale(0.55, about_point=ORIGIN).move_to([cx, 0.2, 0]), tx(val, 30, C_SUM).move_to([cx, -1.5, 0]), tx(f"режет на {n}", 22, C_NOTE).move_to([cx, 1.7, 0]))
        self.show(mini(-3.4, 8, "20"), mini(3.4, 13, "20"), twins("=").scale(1.6).move_to([0, 0.2, 0]), tx("счётчик А", 22, WHITE).move_to([-3.4, -2.2, 0]), tx("счётчик Б", 22, WHITE).move_to([3.4, -2.2, 0]),
                  c="разные нарезки — одна и та же сумма")


class A08(Film):
    def construct(self):
        stairs = poly_line([pt(-5, 1.0), pt(-3, 1.0), pt(-3, 2.2), pt(-1, 2.2), pt(-1, 0.6), pt(1.5, 0.6), pt(1.5, 2.6), pt(3.4, 2.6), pt(3.4, 1.4), pt(5, 1.4)], C_PRICE, 5)
        self.show(stairs, axis_(), hill(C_NOTE, 2).set_opacity(0.3), c="график не обязан быть гладким")
        d, xs, up = jump()
        self.show(d, axis_(), vaxis().scale(0.001), one_zero_marks(), tx("в части точек единица, в остальных ноль", 24, WHITE).move_to([0, 2.4, 0]), c="в каждой точке оси — единица или ноль", morph={"hill": "dots"}, rt=1.6)
        # увеличение куска: кусок оси и его крупный план в рамке; в крупном плане снова и единицы, и нули
        dd, _, _ = jump(-4.8, 4.8, AY, 1.2, 60, 7)
        sel = Rectangle(width=0.8, height=1.6).set_stroke(C_AXIS, 2).move_to([0.0, AY + 0.6, 0])

        def panel(cx, cy, w, h, n, seed):
            fr = Rectangle(width=w, height=h).set_stroke(C_AXIS, 2)
            pd, _, _ = jump(-w / 2 + 0.3, w / 2 - 0.3, -h / 2 + 0.3, h - 0.6, n, seed, 0.09)
            return VGroup(fr, pd).move_to([cx, cy, 0])
        p1 = panel(0.0, 1.4, 7.0, 1.8, 26, 21)
        self.show(dd.set_opacity(0.7), axis_(), one_zero_marks(hi=1.2), sel, p1,
                  line([-0.4, AY + 1.4, 0], [-3.5, 0.5, 0], C_AXIS, 2, True), line([0.4, AY + 1.4, 0], [3.5, 0.5, 0], C_AXIS, 2, True),
                  tx("тот же кусок крупно", 22, C_AXIS).move_to([5.0, 1.4, 0]), c="в любом куске есть и те, и другие")
        pa = panel(-3.3, 0.6, 4.4, 1.8, 20, 21)
        pb = panel(2.8, 0.6, 5.8, 1.8, 16, 33)
        self.show(pa, pb, Rectangle(width=0.7, height=1.4).set_stroke(C_AXIS, 2).move_to([-3.0, 0.6, 0]), Arrow([-0.8, 0.6, 0], [-0.1, 0.6, 0], buff=0).set_color(C_AXIS),
                  tx("ещё крупнее", 22, C_AXIS).move_to([2.8, -0.7, 0]), tx("и снова единицы и нули вперемешку", 24, WHITE).move_to([0, 2.3, 0]), c="увеличиваем — снова и то, и другое")
        self.show(d, axis_(), one_zero_marks(), tx("?", 90, C_BAD).move_to([0, 2.6, 0]), tx("выдержит ли договор такой график", 26, WHITE).move_to([0, -2.2, 0]))


class A09(Film):
    def construct(self):
        d, xs, up = jump()
        self.show(d, axis_(), one_zero_marks(), piece(-0.6, 0.6), tx("проверим договор", 28, WHITE).move_to([0, 2.5, 0]), c="возьмём кусок оси")
        row, _, upv = jump(-1.7, 1.7, -1.0, 1.9, 14, 5, 0.11)
        base = VGroup(line([-1.9, -1.0, 0], [1.9, -1.0, 0], C_AXIS, 9), Rectangle(width=3.8, height=1.9).set_stroke(C_BET, 2).move_to([0, -0.05, 0]).set_stroke(opacity=0.5))
        self.show(row, base, tx("кусок оси", 22, C_AXIS).move_to([0, -1.55, 0]), c="поставим на нём столбик")
        i_hi = int(np.argmax(upv)); i_lo = int(np.argmin(upv))
        lz = lens(row[i_hi].get_center()[0] - 0.05, row[i_hi].get_center()[1] + 0.05)
        self.show(row, base, lz, tx("замер", 30, C_BET).move_to([0, 2.0, 0]), c="высота берётся в одной точке куска")

        def hop():
            for k in (i_lo, i_hi, i_lo):
                p = row[k].get_center()
                self.play(lz.animate.move_to([p[0] + 0.2, p[1] - 0.2, 0]), run_time=0.7)
                self.wait(0.2)
        self.do(hop)
        hi_bar = Rectangle(width=3.0, height=1.9).set_stroke(C_BET, 3).set_fill(C_BET, 0.45).move_to([-3.4, -0.05, 0])
        lo_bar = line([2.0, -1.0, 0], [5.0, -1.0, 0], C_BET, 8)
        self.show(hi_bar, line([-4.9, -1.0, 0], [-1.9, -1.0, 0], C_AXIS, 9), Dot([-3.4, 0.9, 0], radius=0.13).set_color(C_BET), tx("точка с единицей: столбик высокий", 22, C_BET).move_to([-3.4, 1.6, 0]),
                  lo_bar, line([2.0, -1.0, 0], [5.0, -1.0, 0], C_AXIS, 9).shift(DOWN * 0.1), Dot([3.5, -1.0, 0], radius=0.13).set_color(WHITE), tx("точка с нулём: столбик плоский", 22, WHITE).move_to([3.5, -0.2, 0]),
                  c="единица — высокий, ноль — плоский")
        self.show(hi_bar.copy().move_to([-3.4, -0.05, 0]), line([-4.9, -1.0, 0], [-1.9, -1.0, 0], C_AXIS, 9), line([2.0, -1.0, 0], [5.0, -1.0, 0], C_BET, 8),
                  tx("≠", 100, C_BAD).move_to([0, -0.3, 0]), tx("один и тот же кусок", 22, C_AXIS).move_to([0, -2.2, 0]), c="кусок тот же, а столбики разные")
        self.show(d, axis_(), one_zero_marks(), cross(C_BAD, 0.9).move_to([0, 0.8, 0]), plaque("1854", "Риман", C_BAD, 0, 2.6), c="способ Римана здесь не работает")


class A10(Film):
    def construct(self):
        N = 6
        hs = np.linspace(0, H, N + 1)
        xk = lambda h: 5.0 * np.sqrt(max(0.0, 1 - h / H))
        layer = lambda k, col=C_BET, op=0.4: Rectangle(width=2 * xk(hs[k]), height=hs[k + 1] - hs[k]).set_stroke(col, 2).set_fill(col, op).move_to([0, AY + (hs[k] + hs[k + 1]) / 2, 0])
        self.show(hill(), axis_(), vaxis(), plaque("1902", "Лебег", WHITE, 0, 2.7).scale(0.9).move_to([3.0, 2.65, 0]), *[line([-5.8, AY + h, 0], [-5.5, AY + h, 0], C_BET, 3) for h in hs], c="начнём с высоты", morph={"dots": "hill"}, rt=1.6)
        self.show(hill(), axis_(), *[line([-xk(h), AY + h, 0], [xk(h), AY + h, 0], C_BET, 2) for h in hs[1:-1]], c="горизонтальные слои, как этажи")
        k = 2
        self.show(hill(), axis_(), layer(k, C_BET, 0.5), line([-xk(hs[k]), AY + hs[k], 0], [-xk(hs[k]), AY, 0], C_NOTE, 2, True), line([xk(hs[k]), AY + hs[k], 0], [xk(hs[k]), AY, 0], C_NOTE, 2, True),
                  piece(-xk(hs[k]), xk(hs[k]), C_AXIS), tx("слой", 24, C_BET).move_to([0, AY + (hs[k] + hs[k + 1]) / 2 + 0.55, 0]), tx("часть оси под слоем", 22, C_AXIS).move_to([0, AY - 0.55, 0]),
                  c="часть оси под слоем — где график достаёт до этой высоты")
        w = 2 * xk(hs[k])
        self.show(Rectangle(width=w, height=hs[k + 1] - hs[k]).set_stroke(C_BET, 3).set_fill(C_BET, 0.5).move_to([0, 0.4, 0]), dim_h(-w / 2, w / 2, -0.3, "длина части оси", C_AXIS, 22),
                  dim_v(-w / 2 - 0.3, 0.4 - (hs[k + 1] - hs[k]) / 2, 0.4 + (hs[k + 1] - hs[k]) / 2, "высота слоя", C_BET, 22, side=-1),
                  tx("площадь слоя = высота слоя × длина части оси", 26, WHITE).move_to([0, 2.0, 0]), c="площадь слоя")
        self.show(axis_(), hill(C_PRICE, 3), *[layer(i, C_BET, 0.35 + 0.08 * i) for i in range(N)], tx("сумма слоёв = площадь холма", 26, C_SUM).move_to([0, 2.3, 0]),
                  c="сложим слои — снова площадь холма")


class A11(Film):
    def construct(self):
        d, xs, up = jump()
        self.show(d, axis_(), one_zero_marks(), tx("слои — для прыгающего графика", 26, WHITE).move_to([0, 2.7, 0]), c="применим слои к прыгающему графику", morph={"hill": "dots"}, rt=1.6)
        b1 = Rectangle(width=11.4, height=0.7).set_stroke(C_BET, 2).set_fill(C_BET, 0.1).move_to([0, AY + 2.0, 0])
        b0 = Rectangle(width=11.4, height=0.7).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.1).move_to([0, AY, 0])
        self.show(d, axis_(False, C_NOTE), b1, b0, tx("слой единицы", 22, C_BET).move_to([-4.6, AY + 2.75, 0]), tx("слой нуля", 22, C_NOTE).move_to([-4.6, AY - 0.75, 0]), c="слоёв всего два")
        d1 = VGroup(*[m for m, u in zip(d, up) if u]).copy().set_color(C_BET)
        d0 = VGroup(*[m for m, u in zip(d, up) if not u]).copy().set_color(WHITE)
        self.show(d1, d0, b1, b0, axis_(False, C_NOTE), tx("все точки с единицей", 22, C_BET).move_to([-4.0, AY + 2.75, 0]), tx("все остальные", 22, WHITE).move_to([-4.6, AY - 0.75, 0]), c="каждая точка — в свой слой")
        lst = VGroup(*[tx(s, 22, C_BET) for s in ("точка 1", "точка 2", "точка 3", "точка 4", "…")]).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        self.show(d1.copy().scale(0.8).move_to([-2.4, 1.6, 0]), Arrow([1.0, 1.6, 0], [2.2, 1.6, 0], buff=0).set_color(WHITE), lst.move_to([4.2, 1.0, 0]),
                  tx("их можно выписать в список", 24, WHITE).move_to([0, -0.4, 0]), tx("длина такой россыпи = 0", 28, C_AXIS).move_to([0, -1.5, 0]), c="такие точки можно выписать списком — длины у них нет")
        self.show(tx("слой единицы: 1 × 0 = 0", 30, C_BET).move_to([0, 1.5, 0]), tx("слой нуля: 0 × вся ось = 0", 30, WHITE).move_to([0, 0.3, 0]), tx("сумма = 0", 40, C_SUM).move_to([0, -1.1, 0]),
                  c="сумма равна нулю при любом счёте")
        self.show(twins("=").scale(2.0).move_to([-2.4, 0.4, 0]), tablo("0").scale(1.8).move_to([2.4, 0.4, 0]), c="договор выполнен: А и Б сходятся")


class A12(Film):
    def construct(self):
        st = lambda n, op: poly_line(self._stair(n), C_PRICE, 4).set_stroke(opacity=op)
        self.show(hill(C_NOTE, 2), axis_(), tx("второй козырь Лебега", 32, WHITE).move_to([0, 2.6, 0]), c="пределы", morph={"dots": "hill"}, rt=1.6)
        self.show(hill(C_NOTE, 2), axis_(), st(3, 0.35), st(6, 0.6), st(12, 1.0), tx("приближения", 26, C_PRICE).move_to([0, 2.4, 0]), c="графики всё ближе к предельному — приближения")

        def mini(cx, n, val):
            g = VGroup(poly_line([np.array([x, y - 0.5, 0.0]) for x, y, _ in self._stair(n, -2.0, 2.0, 1.3, 0.0)], C_PRICE, 3), curve_of(lambda x: 1.3 * (1 - (x / 2.0) ** 2), -2.0, 2.0, -0.5, C_NOTE, 2, 40))
            return VGroup(g.move_to([cx, 0.4, 0]), tx(val, 30, C_SUM).move_to([cx, -1.3, 0]))
        self.show(mini(-4.4, 3, "10"), mini(0.0, 6, "16"), mini(4.4, 12, "18,5"), tx("площади растут к 20 — площади предельного графика", 26, WHITE).move_to([0, 2.4, 0]), c="площади подходят к площади предельного графика")
        ok = tx("✓", 80, C_SUM)
        self.show(VGroup(tx("слои Лебега", 30, C_BET), ok).arrange(DOWN, buff=0.4).move_to([-3.2, 0.5, 0]),
                  VGroup(tx("столбики Римана", 30, C_BET), tx("иногда застревают", 24, C_BAD)).arrange(DOWN, buff=0.4).move_to([3.2, 0.5, 0]), c="со слоями работает всегда")
        self.show(VGroup(curve_of(lambda x: 0.7 * np.sin(2.5 * x), -1.2, 1.2, 0, C_PRICE, 4, 40).scale(1.0), tx("ряды Фурье", 26, WHITE)).arrange(DOWN, buff=0.4).move_to([-3.0, 0.4, 0]),
                  VGroup(bell(0, 0), tx("вероятность", 26, WHITE)).arrange(DOWN, buff=0.4).move_to([3.0, 0.4, 0]), c="на Лебеге стоят Фурье и вероятность")

    def _stair(self, n, x0=-5.0, x1=5.0, hmax=H, y0=AY):
        pts = []
        w = (x1 - x0) / n
        for i in range(n):
            xm = x0 + (i + 0.5) * w
            h = hmax * (1 - (max(abs(x0 + i * w), abs(x0 + (i + 1) * w)) / (x1)) ** 2)
            pts += [np.array([x0 + i * w, y0 + h, 0.0]), np.array([x0 + (i + 1) * w, y0 + h, 0.0])]
        return pts


# ============================== акт 2: другая ось ==============================
def wfun(x):   # вес: растёт неровно, есть пологий участок и скачок при x = 1,5
    return 0.9 * (x + 5) * 0.4 + (1.6 if x > 1.5 else 0.0) + (0.8 * np.sin(0.5 * (x + 5)) if x < 1.5 else 0.0)


class A13(Film):
    def construct(self):
        self.show(hill(), axis_(), bars(8), c="поменяем ширину столбика — пункт про ось")
        edges = [-5.0, -3.6, -2.4, -1.5, -0.2, 1.5, 2.4, 3.6, 5.0]
        ub = bars_of(F, 8, -5.0, 5.0, AY, C_BET, 0.35)
        ubs = VGroup(*[Rectangle(width=edges[i + 1] - edges[i], height=F((edges[i] + edges[i + 1]) / 2)).set_stroke(C_BET, 2).set_fill(C_BET, 0.4).move_to([(edges[i] + edges[i + 1]) / 2, AY + F((edges[i] + edges[i + 1]) / 2) / 2, 0]) for i in range(8)])
        self.show(hill(), axis_(), ubs, dim_h(edges[1], edges[2], AY - 0.5, "прирост веса", C_AXIS, 20), c="ширина куска — прирост другой величины, веса")
        wpts = [(-5.0, 0.0), (-3.0, 0.5), (-1.2, 0.8), (0.4, 0.85), (1.2, 0.9), (2.0, 1.9), (3.2, 2.2), (5.0, 2.4)]
        wl = poly_line([[x, -2.55 + 0.5 * y, 0] for x, y in wpts], C_AXIS, 5)
        self.show(hill().scale(0.5, about_point=pt(0)).shift(UP * 2.0), line([-5.8, -0.55, 0], [5.8, -0.55, 0], C_AXIS, 4), tx("ось", 20, C_AXIS).move_to([5.4, -0.85, 0]), wl,
                  line([-5.0, -2.6, 0], [5.0, -2.6, 0], C_NOTE, 2), tx("вес", 28, C_AXIS).move_to([-5.5, -1.7, 0]), tx("почти стоит", 20, C_AXIS).move_to([0.4, -1.55, 0]),
                  tx("быстро растёт", 20, C_AXIS).move_to([3.6, -1.1, 0]), c="вес растёт неровно")
        wide = Rectangle(width=2.0, height=2.0).set_stroke(C_BET, 3).set_fill(C_BET, 0.45).move_to([0, -0.4, 0])
        step = poly_line([[-3.0, -1.5, 0], [-1.0, -1.5, 0], [-1.0, -0.5, 0], [1.0, -0.5, 0], [1.0, 0.8, 0], [3.0, 0.8, 0]], C_AXIS, 5)
        self.show(wide, dim_h(-1.0, 1.0, -1.75, "скачок веса = широкий столбик", C_AXIS, 22), step.shift(DOWN * 0.0), tx("скачок", 24, C_AXIS).move_to([1.5, 0.0, 0]), c="скачок веса — широкий столбик")
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), tx("площадь = высота × прирост веса", 30, WHITE).move_to([0, 2.2, 0]), dim_h(-1.7, 1.7, -1.95, "прирост веса", C_AXIS, 22), c="сумма считается так же")
        self.show(hill(), axis_(), bars(8), plaque("1894", "Стилтьес", WHITE, 0, 2.65), c="так предложил Стилтьес")


class A14(Film):
    def construct(self):
        self.show(hill(), axis_(), bars(8), tx("куски равны", 24, C_NOTE).move_to([0, 2.5, 0]), c="куски были одинаковые")
        edges = [-5.0, -3.0, -1.2, 0.4, 1.8, 2.9, 3.8, 4.5, 5.0]
        ubs = VGroup(*[Rectangle(width=edges[i + 1] - edges[i], height=F((edges[i] + edges[i + 1]) / 2)).set_stroke(C_BET, 2).set_fill(C_BET, 0.4).move_to([(edges[i] + edges[i + 1]) / 2, AY + F((edges[i] + edges[i + 1]) / 2) / 2, 0]) for i in range(8)])
        self.show(hill(), axis_(), ubs, plaque("1957–61", "Курцвейль и Хенсток", WHITE, 0, 2.65), c="куски могут быть разной ширины")
        self.show(hill(), axis_(), ubs, tx("круто — куски уже", 22, C_AXIS).move_to([-4.0, 0.6, 0]), tx("полого — шире", 22, C_AXIS).move_to([0.6, 2.2, 0]), c="где график круто меняется — куски уже")


class A15(Film):
    def construct(self):
        j, _, _ = noise(-5, 5, -1.7, 0.1, 70, 4, C_NOISE, 3)
        self.show(hill().scale(0.55, about_point=pt(0)).shift(UP * 2.1), line([-5.8, -0.5, 0], [5.8, -0.5, 0], C_AXIS, 4), tx("ось", 20, C_AXIS).move_to([5.4, -0.8, 0]), j, tx("вес", 24, C_AXIS).move_to([-5.5, -1.7, 0]), c="а если вес случаен")
        j1, _, _ = noise(-5.5, 5.5, 0.2, 0.3, 90, 11, C_NOISE, 4)
        self.show(j1, tx("шум", 44, C_NOISE).move_to([0, 2.0, 0]), c="шум — линия дрожит вверх и вниз наугад")
        j2, _, _ = noise(-3.2, 3.2, -0.9, 0.22, 90, 17, C_NOISE, 4)
        j1s, _, _ = noise(-5.5, 5.5, 2.0, 0.12, 90, 11, C_NOISE, 3)
        fr = Rectangle(width=0.9, height=1.0).set_stroke(C_AXIS, 2).move_to([0.8, 2.0, 0])
        self.show(j1s, fr, j2, line([0.3, 1.5, 0], [-3.2, 0.2, 0], C_AXIS, 2, True), line([1.3, 1.5, 0], [3.2, 0.2, 0], C_AXIS, 2, True), tx("увеличим", 22, C_AXIS).move_to([4.5, 1.1, 0]), c="сколько ни увеличивай — снова дрожь")
        jh, _, _ = noise(-4.6, 4.6, 1.5, 0.15, 70, 5, C_NOISE, 3)
        jw, _, _ = noise(-4.6, 4.6, -1.7, 0.15, 70, 7, C_NOISE, 3)
        self.show(jh, jw, line([-5.6, -0.1, 0], [5.6, -0.1, 0], C_AXIS, 3), tx("высота — от шума", 24, C_BET).move_to([0, 2.8, 0]),
                  tx("вес — от такого же шума", 24, C_AXIS).move_to([0, -0.65, 0]), c="и высоту, и вес даёт такая линия")


class A16(Film):
    def construct(self):
        j, xs, ys = noise(-4.0, 4.0, 0.4, 0.25, 40, 13, C_NOISE, 4)
        self.show(j, line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4), piece(-0.6, 0.6, C_AXIS, -1.3), tx("где в куске делать замер?", 30, WHITE).move_to([0, 2.5, 0]), c="в какой точке куска брать высоту")
        self.show(j, line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4), piece(-0.6, 0.6, C_AXIS, -1.3), marker(-0.6, 0.0, C_BAD), marker(0.6, 0.0, C_SUM), tx("левый край", 22, C_BAD).move_to([-1.6, -1.75, 0]), tx("правый край", 22, C_SUM).move_to([1.7, -1.75, 0]),
                  line([-0.6, -1.3, 0], [-0.6, 0.0, 0], C_BAD, 2, True), line([0.6, -1.3, 0], [0.6, 0.0, 0], C_SUM, 2, True), c="у куска два края: левый и правый")
        bl = Rectangle(width=2.0, height=1.9).set_stroke(C_BAD, 3).set_fill(C_BAD, 0.3).move_to([-2.5, -0.35, 0])
        br = Rectangle(width=2.0, height=2.0).set_stroke(C_SUM, 3).set_fill(C_SUM, 0.3).move_to([2.5, -0.3, 0])
        self.show(bl, br, tx("слева", 24, C_BAD).move_to([-2.5, 1.0, 0]), tx("справа", 24, C_SUM).move_to([2.5, 1.0, 0]), tx("=", 90, C_SUM).move_to([0, -0.3, 0]), tx("гладкий график: почти одно и то же", 24, WHITE).move_to([0, 2.4, 0]), c="гладкий график: суммы совпадают")
        bl2 = Rectangle(width=2.0, height=0.9).set_stroke(C_BAD, 3).set_fill(C_BAD, 0.3).move_to([-2.5, -0.85, 0])
        br2 = Rectangle(width=2.0, height=2.1).set_stroke(C_SUM, 3).set_fill(C_SUM, 0.3).move_to([2.5, -0.25, 0])
        self.show(bl2, br2, tx("≠", 90, C_BAD).move_to([0, -0.3, 0]), tx("4,5", 30, C_BAD).move_to([-2.5, 0.3, 0]), tx("5,5", 30, C_SUM).move_to([2.5, 1.1, 0]), tx("шум: суммы расходятся, тоньше — не помогает", 24, WHITE).move_to([0, 2.4, 0]),
                  c="шум: суммы расходятся и при тонких столбиках")
        self.show(pill("пункт про высоту", C_BET, 40).move_to([0, 0.6, 0]), cross(C_BAD, 0.6).move_to([0, -0.9, 0]), tx("придётся переписать", 28, WHITE).move_to([0, -1.9, 0]), c="договор нарушен")


class A17(Film):
    def construct(self):
        j, xs, ys = noise(-4.0, 4.0, 0.4, 0.25, 40, 13, C_NOISE, 4)
        ax = line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4)
        self.show(j, ax, piece(-0.6, 0.6, C_AXIS, -1.3), marker(-0.6, 0.0, C_BAD), tx("левый край", 22, C_BAD).move_to([-1.6, -1.75, 0]), plaque("1944", "Ито", WHITE, 0, 2.65), c="Ито: высоту берём на левом краю")
        fut = Rectangle(width=4.0, height=3.2).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.12).move_to([2.6, 0.2, 0])
        self.show(poly_line([[x, y, 0] for x, y in zip(xs[xs < -0.5], ys[xs < -0.5])], C_NOISE, 5), ax, fut, lock(0.9, 1.9, C_BAD), tx("будущее", 24, C_NOTE).move_to([2.6, 0.2, 0]), tx("прошлое известно", 24, C_NOISE).move_to([-2.4, 1.8, 0]),
                  c="высота известна заранее: в будущее не подглядываем")
        self.show(scales(C_SUM).scale(1.4).move_to([-1.4, 0.2, 0]), tablo("0").scale(1.8).move_to([2.8, 0.2, 0]), tx("если шум случаен, в среднем ноль", 26, WHITE).move_to([0, 2.2, 0]), c="сумма честная — в среднем ноль")
        self.show(tx("шум", 30, C_NOISE).move_to([-4.6, 1.0, 0]), tx("→", 40, WHITE).move_to([-3.4, 1.0, 0]), tx("квадрат шума", 30, WHITE).move_to([-0.8, 1.0, 0]),
                  pill("обычное правило: только часть ответа", C_BET, 24).move_to([0, -0.4, 0]), c="возьмём от шума квадрат")
        self.show(pill("обычное правило", C_BET, 28).move_to([-3.2, 0.5, 0]), tx("+", 50, WHITE).move_to([-0.8, 0.5, 0]), pill("добавка", C_ADD, 28).move_to([1.6, 0.5, 0]),
                  tx("добавка — от дрожи шума", 24, C_NOISE).move_to([1.6, -0.4, 0]), c="остальное — добавка")


class A18(Film):
    def construct(self):
        j, xs, ys = noise(-4.0, 4.0, 0.4, 0.25, 40, 13, C_NOISE, 4)
        ax = line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4)
        self.show(j, ax, piece(-0.6, 0.6, C_AXIS, -1.3), marker(-0.6, 0.0, C_BAD), tx("левый край", 22, C_BAD).move_to([-1.6, -1.75, 0]), tx("физикам нужны школьные правила пересчёта", 26, WHITE).move_to([0, 2.5, 0]), c="физикам левый край неудобен")
        self.show(j, ax, piece(-0.6, 0.6, C_AXIS, -1.3), marker(0.0, 0.0, C_SUM), tx("середина", 22, C_SUM).move_to([0.0, -1.75, 0]), plaque("1963–66", "Фиск и Стратонович", WHITE, 0, 2.65), c="Фиск и Стратонович взяли середину куска")
        self.show(pill("обычное правило", C_BET, 30).move_to([0, 0.6, 0]), tx("✓", 80, C_SUM).move_to([0, -0.8, 0]), tx("добавки нет", 28, WHITE).move_to([0, -1.9, 0]), c="с серединой добавки нет")
        a, b = pill("сумма Ито", C_NOISE, 28).move_to([-3.2, 0.5, 0]), pill("сумма Стратоновича", C_NOISE, 28).move_to([3.2, 0.5, 0])
        self.show(a, b, darrow(a.get_right() + RIGHT * 0.15, b.get_left() + LEFT * 0.15, C_BET), pill("+ добавка", C_ADD, 24).move_to([0, 1.3, 0]), c="одну сумму можно перевести в другую")
        jj, _, _ = noise(-5.5, 5.5, 0.4, 0.3, 90, 11, C_NOISE, 4)
        self.show(jj, pill("запись Ито", C_NOISE, 24).move_to([-3.2, -1.4, 0]), pill("запись Стратоновича", C_NOISE, 24).move_to([3.2, -1.4, 0]), Arrow([-3.2, -1.0, 0], [-1.5, 0.0, 0], buff=0).set_color(C_NOTE),
                  Arrow([3.2, -1.0, 0], [1.5, 0.0, 0], buff=0).set_color(C_NOTE), c="обе записи описывают одну линию шума")


class A19(Film):
    def construct(self):
        jr, _, _ = noise(-5.5, 5.5, 0.4, 0.28, 240, 29, C_NOISE, 3)
        self.show(jr, tx("шум грубее", 36, C_NOISE).move_to([0, 2.4, 0]), c="бывает шум ещё грубее")
        self.show(jr, marker(-1.0, -0.8, C_BAD), marker(0.2, -0.8, C_SUM), tx("левый край", 20, C_BAD).move_to([-1.6, -1.6, 0]), tx("середина", 20, C_SUM).move_to([0.9, -1.6, 0]), cross(C_BAD, 0.35).move_to([-1.0, -0.4, 0]), cross(C_BAD, 0.35).move_to([0.2, -0.4, 0]),
                  tx("надёжной суммы нет", 28, C_BAD).move_to([0, 2.4, 0]), c="ни край, ни середина не дают надёжной суммы")
        sp = VMobject().set_points_smoothly([np.array([0.6 * np.cos(t) * (1 - t / 14), 0.6 * np.sin(t) * (1 - t / 14), 0.0]) for t in np.linspace(0, 12, 60)]).set_stroke(C_ADD, 4).set_fill(opacity=0)
        self.show(jr.copy().scale(0.6).move_to([0, -0.8, 0]), sp.move_to([0, 1.2, 0]), portrait("Лайонс", "1998", WHITE, 1.0).move_to([-3.8, 1.8, 0]), tx("подсказка: как шум закручивается", 24, C_ADD).move_to([2.6, 1.6, 0]),
                  c="Лайонс: добавим к шуму подсказку")
        self.show(jr.copy().scale(0.6).move_to([-3.0, 0.3, 0]), sp.copy().scale(0.7).move_to([-3.0, 1.5, 0]), tx("→", 50, WHITE).move_to([0, 0.4, 0]), tablo("число").scale(1.8).move_to([3.4, 0.4, 0]),
                  c="с подсказкой сумма определена для каждой линии")
        self.show(portrait("Хайрер", "2014", WHITE, 1.4).move_to([-2.6, 0.4, 0]), VGroup(Circle(radius=0.7).set_stroke(C_BET, 5).set_fill(C_BET, 0.2), tx("★", 50, C_BET)).move_to([2.6, 0.7, 0]),
                  tx("Филдсовская премия", 26, C_BET).move_to([2.6, -0.5, 0]), c="Хайрер получил Филдсовскую премию")


class A20(Film):
    def construct(self):
        self.show(portrait("Ито", "1944", WHITE, 1.3).move_to([0, -1.2, 0]), *[Arrow([0.0, -0.4, 0], [x, 1.5, 0], buff=0.05).set_stroke(C_NOTE, 3) for x in (-4.2, -1.4, 1.4, 4.2)],
                  *[tx(t, 22, col).move_to([x, 1.95, 0]) for t, col, x in (("скачки", C_SUM, -4.2), ("будущее", C_SUM, -1.4), ("вся история", C_BET, 1.4), ("граница", C_BAD, 4.2))],
                  c="от Ито пути расходятся")
        jj, xs, ys = noise(-5, -0.6, 0.2, 0.25, 30, 41, C_NOISE, 4)
        self.show(jj, poly_line([[-0.6, ys[-1], 0], [-0.6, ys[-1] + 1.3, 0]], C_BAD, 5), tx("скачок", 24, C_BAD).move_to([0.5, 1.0, 0]), Arrow([1.0, 0.4, 0], [2.2, 0.4, 0], buff=0).set_color(WHITE),
                  curve_of(lambda x: 1.3 / (1 + np.exp(-9 * x)), -0.6, 0.6, -0.3, C_SUM, 5, 30).move_to([3.4, 0.4, 0]), tx("быстрое непрерывное движение (Маркус)", 22, C_SUM).move_to([1.8, -1.3, 0]), c="скачок как быстрое непрерывное движение")
        self.show(big_bar(0, -1.5, 2.6, 1.6, 0.4, 0.0), lock(1.9, 0.5, C_SUM), tx("открыт", 22, C_SUM).move_to([1.9, -0.1, 0]), pill("в среднем 0 — как раньше", C_SUM, 24).move_to([0, 2.2, 0]),
                  tx("Скороход, Маллявэн", 22, WHITE).move_to([0, -2.2, 0]), c="столбик знает будущее, сумма остаётся честной")
        j2, xs2, ys2 = noise(-5, 1.0, 0.0, 0.25, 40, 43, C_NOISE, 4)
        self.show(j2, line([-5, -0.9, 0], [1.0, -0.9, 0], C_PRICE, 6), bar_w(1.0, 0.7, 1.4, -1.6, C_BET), tx("высота зависит от всей истории (Конт, Фурнье)", 24, C_BET).move_to([0, 2.2, 0]), c="высота — от всей истории линии")
        fam = RoundedRectangle(width=7.0, height=2.6, corner_radius=0.3).set_stroke(C_NOISE, 3).move_to([-1.0, 0.5, 0])
        self.show(fam, tx("шумы, по которым можно считать", 24, C_NOISE).move_to([-1.0, 0.5, 0]), cross(C_BAD, 0.45).move_to([4.6, 0.5, 0]), tx("шире нельзя (Бихтелер, Деллашери)", 24, C_BAD).move_to([0, -1.5, 0]), c="граница: шире шумы — счёта нет")


class A21(Film):
    def construct(self):
        N = 5
        hs = np.linspace(0, H, N + 1)
        xk = lambda h: 5.0 * np.sqrt(max(0.0, 1 - h / H))
        layers = lambda col, op: VGroup(*[Rectangle(width=2 * xk(hs[k]), height=hs[k + 1] - hs[k]).set_stroke(col, 2).set_fill(col, op).move_to([0, AY + (hs[k] + hs[k + 1]) / 2, 0]) for k in range(N)])
        self.show(axis_(), hill(C_PRICE, 3), layers(C_BET, 0.35), tx("сложить слои — как?", 30, C_ADD).move_to([0, 2.6, 0]), c="пункт про сложение")
        a = Square(side_length=1.2).set_stroke(C_BET, 3).set_fill(C_BET, 0.3).move_to([-3.0, 0.4, 0]); b = Square(side_length=1.2).set_stroke(C_AXIS, 3).set_fill(C_AXIS, 0.3).move_to([-1.2, 0.4, 0])
        u = Rectangle(width=3.0, height=1.2).set_stroke(C_ADD, 3).move_to([3.0, 0.4, 0])
        self.show(a, b, tx("+", 40, WHITE).move_to([-2.1, 0.4, 0]), tx("≠", 60, C_BAD).move_to([0.9, 0.4, 0]), u, tx("целое", 24, C_ADD).move_to([3.0, 0.4, 0]), tx("выбор по нескольким критериям", 24, WHITE).move_to([0, 2.2, 0]),
                  c="целое бывает не равно сумме частей")
        self.show(axis_(), hill(C_PRICE, 3), layers(C_ADD, 0.3), tx("особая мера слоя: интегралы Шоке и Сугено", 26, C_ADD).move_to([0, 2.6, 0]), c="слои измеряют особой мерой")
        shape = VGroup(Rectangle(width=4.0, height=2.0).set_stroke(C_ADD, 3).set_fill(C_ADD, 0.2), Circle(radius=0.4).set_stroke(C_BAD, 3).set_fill("#0f1115", 1).shift(LEFT * 0.9), Circle(radius=0.4).set_stroke(C_BAD, 3).set_fill("#0f1115", 1).shift(RIGHT * 0.9))
        self.show(shape.move_to([-2.4, 0.4, 0]), tx("куски − дыры", 28, C_ADD).move_to([-2.4, -1.2, 0]), tx("эйлерова характеристика", 24, WHITE).move_to([-2.4, 2.0, 0]),
                  *[Dot([x, y, 0], radius=0.12).set_color(C_SUM) for x, y in ((2.2, 1.0), (3.6, 0.2), (4.8, 1.2))], tx("считаем цели, которые видят датчики", 22, C_SUM).move_to([3.6, -0.8, 0]), c="эйлерова характеристика считает куски минус дыры")
        self.show(*[portrait(n, "", WHITE, 0.9).move_to([x, 1.2, 0]) for n, x in (("Концевич", -4.0), ("Денеф", -1.3), ("Лёзер", 1.4))], plaque("1995–98", "мера на пространстве кривых", WHITE, 0, -1.0), c="мера на пространстве кривых")


class A22(Film):
    def construct(self):
        self.show(*[pill(t, col, 26).move_to([x, 0.6, 0]) for t, col, x in (("память", C_ADD, -4.2), ("произведение", C_ADD, 0.0), ("шкала времени", C_ADD, 4.2))], tx("другие сложения", 34, WHITE).move_to([0, 2.4, 0]), c="совсем другие сложения")
        bs = VGroup(*[Rectangle(width=0.8, height=1.4).set_stroke(C_ADD, 2).set_fill(C_ADD, 0.15 + 0.1 * i).move_to([-3.5 + i * 1.0, -0.8, 0]) for i in range(8)])
        self.show(bs, tx("недавнее прошлое весит больше далёкого", 24, WHITE).move_to([0, 1.4, 0]), tx("дробный интеграл", 26, C_ADD).move_to([0, 2.4, 0]), c="дробный интеграл — сумма с памятью")
        self.show(*[Rectangle(width=1.0, height=1.2).set_stroke(C_BET, 2).set_fill(C_BET, 0.3).move_to([-4.0 + i * 2.0, 0.2, 0]) for i in range(5)],
                  *[tx("×", 40, C_ADD).move_to([-3.0 + i * 2.0, 0.2, 0]) for i in range(4)], plaque("1887", "Вольтерра", WHITE, 0, 2.5), c="Вольтерра перемножал столбики")
        tl = VGroup(line([-5.0, 0.0, 0], [-0.5, 0.0, 0], C_ADD, 6), *[Dot([x, 0.0, 0], radius=0.1).set_color(C_ADD) for x in (1.0, 2.0, 3.2, 4.0, 5.0)])
        self.show(tl, tx("сплошная ось", 22, C_ADD).move_to([-2.7, -0.6, 0]), tx("отдельные точки", 22, C_ADD).move_to([3.0, -0.6, 0]), plaque("1988", "Хильгер", WHITE, 0, 2.5), c="шкала времени — и сплошная, и из точек")


class A23(Film):
    def construct(self):
        self.show(tx("Как посчитать площадь так, чтобы ответ", 34).move_to([0, 2.6, 0]), tx("не зависел от способа счёта?", 34).move_to([0, 1.9, 0]),
                  hill(), axis_(), bars(12, 0.4), c="возвращаемся к вопросу")
        self.show(tree(False), tx("способы растут деревом", 28, WHITE).move_to([0, 2.5, 0]), c="единого способа нет — договор переписывали по пунктам")
        self.show(tree(True), c="четыре пункта — четыре ветви")
        self.show(pill("гладкая ширина — Риман", C_BET, 28).move_to([-3.4, 0.9, 0]), pill("случайная — Ито", C_NOISE, 28).move_to([3.4, 0.9, 0]), tx("а дальше — смотря какая задача", 34, WHITE).move_to([0, -0.7, 0]),
                  c="какой способ взять, зависит от задачи")


# ============================== приложение ==============================
class F01(Film):
    def construct(self):
        self.show(title2("образ → формула"), bars_of(F, 8, -4.0, -0.5, -0.6, C_BET, 0.35).scale(0.5, about_point=ORIGIN).move_to([-3.0, 0.4, 0]), Arrow(LEFT, RIGHT, buff=0).move_to([0.0, 0.4, 0]), tx("Σ", 60, C_SUM).move_to([2.0, 0.4, 0]))
        self.show(card3("Риман", "Σ значение в точке × ширина", "≈ столбики", C_BET).move_to([-2.2, 0.2, 0]), tx("предел при дроблении", 20, C_NOTE).move_to([-2.2, -2.2, 0]))
        self.show(card3("Лебег", "Σ высота слоя × мера слоя", "≈ слои", C_BET).move_to([2.2, 0.2, 0]), tx("предел по приближениям", 20, C_NOTE).move_to([2.2, -2.2, 0]))


class F02(Film):
    def construct(self):
        self.show(title2("то же для веса"), card3("Стилтьес", "Σ значение × приращение веса", "≈ шкала веса", C_PRICE).move_to([0, 0.0, 0]))
        self.show(card3("Ито", "значение в левой точке", "≈ замок на будущем", C_NOISE).move_to([0, 0.2, 0]))
        self.show(card3("Стратонович", "среднее по краям, правила обычные", "≈ середина", C_NOISE).move_to([0, 0.2, 0]))
        a, b = pill("Ито", C_NOISE, 28).move_to([-3.0, 0.4, 0]), pill("Стратонович", C_NOISE, 28).move_to([3.0, 0.4, 0])
        self.show(a, b, Arrow(a.get_right() + RIGHT * 0.1, b.get_left() + LEFT * 0.1, buff=0).set_color(C_BET), pill("+ добавка", C_BET, 24).move_to([0, 1.2, 0]))
        rows = [("Риман", "площадь"), ("Лебег", "пределы, рваный график"), ("Стилтьес", "неровная ширина"), ("Ито", "случайная ширина"), ("Стратонович", "привычные правила"), ("Лайонс", "грубая ширина")]
        g = VGroup(*[VGroup(tx(a_, 22, WHITE), tx(b_, 22, C_NOTE)).arrange(RIGHT, buff=0.6) for a_, b_ in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([-1.5, 0.0, 0])
        self.show(title2("что чинили"), g, tx("где применяют: вероятность, финансы, физика шума", 22, C_SUM).move_to([0, -2.4, 0]))


# ============================== объёмные сцены: камера — рассказчик ==============================
Base3D = story_base3d(P.STATIONS, P.SCENES, ICONS, N.TEXT, HERE)
DEP = 2.2                      # глубина холма (ось y)


def ridge(op=0.45):
    """Холм как объём: профиль-парабола, вытянутый в глубину; передняя кромка светится. Вид спереди совпадает с плоским холмом."""
    surf = ParametricSurface(lambda u, v: np.array([u, v, F(u)]), u_range=(XL, XR), v_range=(0, DEP), resolution=(90, 4))
    surf.set_color(C_PRICE).set_opacity(op).set_shading(0.4, 0.3, 0.2)
    edge = ParametricCurve(lambda t: np.array([t, 0.0, F(t)]), t_range=(XL, XR, 0.05)).set_stroke(C_PRICE, 9)
    back = ParametricCurve(lambda t: np.array([t, DEP, F(t)]), t_range=(XL, XR, 0.05)).set_stroke(C_PRICE, 3).set_opacity(0.6)
    return surf, edge, back


def axis3():
    ax = Line([-5.8, 0, 0], [5.8, 0, 0]).set_stroke(C_AXIS, 10)
    grid = VGroup(*[Line([x, 0, 0], [x, DEP, 0]).set_stroke("#334", 1) for x in np.linspace(XL, XR, 11)],
                  *[Line([XL, y, 0], [XR, y, 0]).set_stroke("#334", 1) for y in np.linspace(0, DEP, 4)])
    return ax, grid


def tower(x0, x1, h, color=C_BET, op=0.96):
    p = Prism(width=x1 - x0 - 0.04, height=DEP, depth=h)
    p.set_color(color).set_opacity(op).set_shading(0.5, 0.35, 0.3)
    p.move_to([(x0 + x1) / 2, DEP / 2, h / 2])
    return p


def towers(n, color=C_BET):
    xs = np.linspace(XL, XR, n + 1)
    return Group(*[tower(xs[i], xs[i + 1], F((xs[i] + xs[i + 1]) / 2), color) for i in range(n)])


def plate(w, h0, h1, color, op=0.95):
    p = Prism(width=w, height=DEP, depth=h1 - h0 - 0.03)
    p.set_color(color).set_opacity(op).set_shading(0.5, 0.35, 0.3)
    p.move_to([0, DEP / 2, (h0 + h1) / 2])
    return p


FRONT = dict(theta=0, phi=90)


class Film3D(Base3D):
    """Объёмная сцена: тот же порядок кадров-фраз, но мир — в 3D. Вид спереди (theta=0, phi=90, центр на оси) совпадает с плоской сценой,
    поэтому вход и выход из объёма незаметны: плоские объекты предыдущей сцены закреплены в кадре и гаснут, когда проявляется объём."""
    def setup(self):
        super().setup()
        self.camera.background_rgba = [0, 0, 0, 1]
        self.camera.light_source.move_to([-6, -8, 12])
        self._k, self._capm, self._ov = 0, None, None
        self.frame.reorient(0, 90).move_to([0, 0, 1.5]).set_height(8)
        i = ORDER.index(type(self).__name__)
        prev = _dry(ORDER[i - 1])
        self._old = []
        for m in prev._cur:
            self._pin(m)
            self._old.append(m)
        if prev._capm is not None:
            self._capm = self._pin(prev._capm)
        st = state_for(ORDER[i - 1], prev._k)
        if st:
            self._ov = self._pin(overlay(st))

    def _pin(self, m):
        m.fix_in_frame()
        self.add(m, set_depth_test=False)
        return m

    def phrase(self, k, c=None, rt=0.7, extra=()):
        """Начало кадра фразы k (с 1): ждать речь, сменить подпись и сквозные сущности."""
        self._k = k
        self.beat(k - 1)
        code = type(self).__name__
        anims = list(extra)
        if c:
            new = cap(c).fix_in_frame()
            anims.append(FadeTransform(self._capm, new) if self._capm is not None else FadeIn(new))
            self._capm = new
        st = state_for(code, k)
        if st:
            ov = overlay(st, INTRO.get((code, k))).fix_in_frame()
            anims.append(ReplacementTransform(self._ov, ov) if self._ov is not None else FadeIn(ov))
            self._ov = ov
        self.play(*anims, run_time=rt)

    def leave(self, objs3d, rt=1.2):
        """Конец сцены: камера спереди, объём гаснет, плоский вид (END_2D) проявляется на его месте."""
        flat = [_bright(m) for m in self.end2d()]
        for m in flat:
            m.fix_in_frame()
        self.play(self.frame.animate.reorient(0, 90).move_to([0, 0, 1.5]).set_height(8), run_time=1.6)
        self.play(*[FadeIn(m) for m in flat], *[FadeOut(o) for o in objs3d], run_time=rt)

    def enter(self, objs3d, rt=1.4):
        """Начало: плоские объекты предыдущей сцены гаснут, объём проявляется на их месте."""
        self.play(*[FadeOut(m) for m in self._old], *[FadeIn(o) for o in objs3d], run_time=rt)
        self._old = []

    def cam(self, theta, phi, rt=3.0, center=(0, 0.8, 1.6), height=10.5):
        self.play(self.frame.animate.reorient(theta, phi).move_to(list(center)).set_height(height), run_time=rt, rate_func=smooth)


class A03(Film3D):
    END_K, END_CAP = 4, "вся фигура — из столбиков"

    def end2d(self):
        return [hill(), axis_(), bars(16)]

    def construct(self):
        surf, edge, back = ridge()
        ax, grid = axis3()
        xs = np.linspace(XL, XR, 9)
        cuts = VGroup(*[Line([x, 0, 0], [x, 0, F(x)]).set_stroke(WHITE, 2) for x in xs])
        self.phrase(1, "ось делится на куски")
        self.enter([surf, edge, back, ax, grid])
        self.play(ShowCreation(cuts), self.frame.animate.reorient(-12, 66).move_to([0, 1.0, 1.4]).set_height(10.5), run_time=2.0)
        t8 = towers(8)
        self.phrase(2, "на каждом куске — столбик")
        self.play(LaggedStart(*[GrowFromEdge(t, IN) for t in t8], lag_ratio=0.12), run_time=3.0)
        self.phrase(3, "столбик стоит на куске оси, верх касается графика")
        self.play(*[t.animate.set_opacity(0.25) for i, t in enumerate(t8) if i != 3], run_time=0.8)
        self.cam(-28, 62, 3.0, (-0.4, 0.8, 2.3), 9.2)
        t16 = towers(16)
        self.phrase(4, "вся фигура — из столбиков")
        self.play(FadeOut(t8), FadeOut(cuts), LaggedStart(*[GrowFromEdge(t, IN) for t in t16], lag_ratio=0.04), run_time=2.5)
        self.leave([surf, edge, back, ax, grid, t16])


class A04(Film3D):
    END_K, END_CAP = 5, "без конца тоньше — сумма равна площади"

    def end2d(self):
        return [hill(), axis_(), bars(40, 0.5), plaque("1854", "Риман", WHITE, 0, 2.5)]

    def construct(self):
        surf, edge, back = ridge(0.35)
        ax, grid = axis3()
        t16 = towers(16)
        self.phrase(1, "у столбика есть высота и ширина")
        self.enter([surf, edge, back, ax, grid, t16])
        self.play(*[t.animate.set_opacity(0.12) for i, t in enumerate(t16) if i != 8], self.frame.animate.reorient(0, 90).move_to([0, 0, 1.5]).set_height(8), run_time=2.0)
        lab = VGroup(dim_v(1.0, AY, AY + F(0.31), "высота", C_BET, 24), dim_h(0.0, 0.625, AY - 0.4, "ширина", C_AXIS, 22)).fix_in_frame()
        self.play(FadeIn(lab), run_time=0.8)
        self.phrase(2, "площадь столбика")
        f = tx("площадь = ширина × высота", 32, WHITE).move_to([0, 2.7, 0]).fix_in_frame()
        self.play(FadeIn(f), run_time=0.8)
        self.phrase(3, "получается сумма")
        self.play(FadeOut(lab), FadeOut(f), *[t.animate.set_opacity(0.96) for t in t16], self.frame.animate.reorient(-20, 62).move_to([0, 0.8, 1.6]).set_height(10.5), run_time=2.5)
        t6, t12, t24, t40 = towers(6), towers(12), towers(24), towers(40)
        self.phrase(4, "тоньше столбики — сумма ближе к площади")
        cur = t16
        for tt, val in ((t6, "17,9"), (t12, "19,4"), (t24, "19,8")):
            lbl = tx(val, 40, C_SUM).move_to([4.8, 1.0, 0]).fix_in_frame()
            self.play(FadeOut(cur), FadeIn(tt), FadeIn(lbl), run_time=1.0)
            self.wait(0.5)
            self.play(FadeOut(lbl), run_time=0.3)
            cur = tt
        self.phrase(5, "без конца тоньше — сумма равна площади")
        self.play(FadeOut(cur), FadeIn(t40), run_time=1.2)
        self.leave([surf, edge, back, ax, grid, t40])


class A10(Film3D):
    END_K, END_CAP = 5, "сложим слои — снова площадь холма"

    def end2d(self):
        return [hill(), axis_()]

    def construct(self):
        surf, edge, back = ridge(0.5)
        ax, grid = axis3()
        N = 6
        hs = np.linspace(0, H, N + 1)
        xk = lambda h: 5.0 * np.sqrt(max(0.0, 1 - h / H))
        cols = [C_BET, "#ffb347", C_AXIS, "#ff7043", C_ADD, C_NOISE]
        plates = Group(*[plate(2 * xk(hs[k]), hs[k], hs[k + 1], cols[k]) for k in range(N)])
        tick = VGroup(vaxis(), *[line([-5.8, AY + h, 0], [-5.5, AY + h, 0], C_BET, 3) for h in hs], plaque("1902", "Лебег", WHITE, 3.0, 2.65).scale(0.9)).fix_in_frame()
        self.phrase(1, "начнём с высоты")
        self.enter([surf, edge, back, ax, grid, tick])
        self.phrase(2, "горизонтальные слои, как этажи")
        self.play(FadeOut(tick), FadeOut(surf), LaggedStart(*[FadeIn(p) for p in plates], lag_ratio=0.15), self.frame.animate.reorient(-14, 68).move_to([0, 1.0, 1.4]).set_height(10.5), run_time=2.5)
        k = 2
        mark = Line([-xk(hs[k]), -0.2, 0], [xk(hs[k]), -0.2, 0]).set_stroke(C_AXIS, 14)
        self.phrase(3, "часть оси под слоем — где график достаёт до этой высоты")
        self.play(*[p.animate.set_opacity(0.18) for i, p in enumerate(plates) if i != k], ShowCreation(mark), self.frame.animate.reorient(-30, 58), run_time=2.5)
        w = 2 * xk(hs[k])
        self.phrase(4, "площадь слоя")
        lab = VGroup(dim_h(-w / 2, w / 2, AY - 0.55, "длина части оси", C_AXIS, 22), dim_v(w / 2 + 0.3, AY + hs[k], AY + hs[k + 1], "высота слоя", C_BET, 22),
                     tx("площадь слоя = высота слоя × длина части оси", 28, WHITE).move_to([0, 2.7, 0])).fix_in_frame()
        self.play(self.frame.animate.reorient(0, 90).move_to([0, 0, 1.5]).set_height(8), FadeIn(lab), run_time=2.0)
        self.phrase(5, "сложим слои — снова площадь холма")
        shadows = VGroup(*[Line([-xk(hs[j]), -0.2, 0], [xk(hs[j]), -0.2, 0]).set_stroke(cols[j], 14) for j in range(N)])
        self.play(FadeOut(lab), *[p.animate.set_opacity(0.95) for p in plates], self.frame.animate.reorient(-24, 60).move_to([0, 1.0, 1.8]).set_height(10.5), run_time=1.5)
        self.play(*[p.animate.shift(OUT * 0.5 * j) for j, p in enumerate(plates)], FadeOut(mark), ShowCreation(shadows), run_time=2.5)
        self.play(*[p.animate.shift(IN * 0.5 * j) for j, p in enumerate(plates)], run_time=1.5)
        self.leave([plates, ax, grid, shadows, edge, back])


class A11(Film3D):
    END_K, END_CAP = 6, "договор выполнен: А и Б сходятся"

    def end2d(self):
        d, _, _ = jump()
        return [d, axis_(), one_zero_marks()]

    def construct(self):
        ax, grid = axis3()
        d2, xs, up = jump()
        dots = Group(*[Sphere(radius=0.15).set_color(C_PRICE if u else "#f2f6ff").move_to([x, 0.6, 2.0 if u else 0.0]) for x, u in zip(xs, up)])
        dots.set_shading(0.15, 0.2, 0.0)
        s1 = Prism(width=11.6, height=DEP, depth=0.55).set_color(C_BET).set_opacity(0.5).set_shading(0.3, 0.2, 0.1).move_to([0, DEP / 2, 2.0])
        s0 = Prism(width=11.6, height=DEP, depth=0.55).set_color("#8fa3c4").set_opacity(0.5).set_shading(0.3, 0.2, 0.1).move_to([0, DEP / 2, 0.0])
        self.phrase(1, "применим слои к прыгающему графику")
        self.enter([ax, grid, dots])
        self.phrase(2, "слоёв всего два")
        self.play(FadeIn(s1), FadeIn(s0), self.frame.animate.reorient(-18, 64).move_to([0, 1.0, 1.4]).set_height(8.6), run_time=2.5)
        self.phrase(3, "каждая точка — в свой слой")
        ones = Group(*[d for d, u in zip(dots, up) if u])
        self.play(*[d.animate.set_opacity(0.25) for d, u in zip(dots, up) if not u], *[Indicate(d, scale_factor=1.5, color=C_BET) for d in list(ones)[:10]], run_time=2.0)
        self.play(*[d.animate.set_opacity(1.0) for d in dots], run_time=0.5)
        self.phrase(4, "такие точки можно выписать списком — длины у них нет")
        ticks_up = VGroup(*[Line([x, -0.2, 0], [x, -0.2, 0.0]).set_stroke(C_AXIS, 0) for x, u in zip(xs, up) if u])
        proj = VGroup(*[Line([x, 0.6, 2.0], [x, 0.6, 0.0]).set_stroke(C_BET, 2) for x, u in zip(xs, up) if u])
        self.play(ShowCreation(proj), self.frame.animate.reorient(-6, 78).move_to([0, 1.0, 1.0]).set_height(8.0), run_time=2.0)
        lab = tx("длина такой россыпи = 0", 30, C_AXIS).move_to([0, 2.4, 0]).fix_in_frame()
        self.play(FadeIn(lab), run_time=0.8)
        self.phrase(5, "сумма равна нулю при любом счёте")
        t = VGroup(tx("слой единицы: 1 × 0 = 0", 28, C_BET), tx("слой нуля: 0 × вся ось = 0", 28, WHITE), tx("сумма = 0", 36, C_SUM)).arrange(DOWN, buff=0.2).move_to([0, 2.3, 0]).fix_in_frame()
        self.play(FadeOut(lab), FadeIn(t), run_time=1.2)
        self.phrase(6, "договор выполнен: А и Б сходятся")
        self.play(FadeOut(t), FadeOut(proj), self.frame.animate.reorient(-10, 70), run_time=2.0)
        self.leave([ax, grid, dots, s1, s0])


def _noise_surf(xs, zs, color=C_NOISE, op=0.55):
    f = lambda u: float(np.interp(u, xs, zs))
    surf = ParametricSurface(lambda u, v: np.array([u, v, f(u)]), u_range=(float(xs[0]), float(xs[-1])), v_range=(0, DEP), resolution=(160, 4))
    surf.set_color(color).set_opacity(op).set_shading(0.4, 0.3, 0.2)
    edge = ParametricCurve(lambda t: np.array([t, 0.0, f(t)]), t_range=(float(xs[0]), float(xs[-1]), 0.03)).set_stroke(color, 8)
    back = ParametricCurve(lambda t: np.array([t, DEP, f(t)]), t_range=(float(xs[0]), float(xs[-1]), 0.03)).set_stroke(color, 3).set_opacity(0.6)
    return surf, edge, back, f


class A15(Film3D):
    END_K, END_CAP = 4, "и высоту, и вес даёт такая линия"

    def end2d(self):
        jh, _, _ = noise(-4.6, 4.6, 1.5, 0.15, 70, 5, C_NOISE, 3)
        jw, _, _ = noise(-4.6, 4.6, -1.7, 0.15, 70, 7, C_NOISE, 3)
        return [jh, jw, line([-5.6, -0.1, 0], [5.6, -0.1, 0], C_AXIS, 3), tx("высота — от шума", 24, C_BET).move_to([0, 2.8, 0]),
                tx("вес — от такого же шума", 24, C_AXIS).move_to([0, -0.65, 0])]

    def construct(self):
        surf, edge, back = ridge(0.5)
        ax, grid = axis3()
        xs = np.linspace(XL, XR, 90)
        rng = np.random.default_rng(5)
        b = np.cumsum(rng.normal(0, 1, 90))
        zs = 2.0 + (b - (b.max() + b.min()) / 2) * (1.5 / (b.max() - b.min()))
        nsurf, nedge, nback, nf = _noise_surf(xs, zs)
        wxs = np.linspace(XL, XR, 70)
        rw = np.cumsum(np.random.default_rng(4).normal(0, 1, 70))
        wz = -0.9 + (rw - (rw.max() + rw.min()) / 2) * (0.7 / (rw.max() - rw.min()))
        wline = ParametricCurve(lambda t: np.array([t, -1.0, float(np.interp(t, wxs, wz))]), t_range=(XL, XR, 0.04)).set_stroke(C_NOISE, 8)
        wlab = tx("вес", 26, C_AXIS).move_to([-5.5, -2.0, 0]).fix_in_frame()
        self.phrase(1, "а если вес случаен")
        self.enter([surf, edge, back, ax, grid, wline, wlab])
        self.play(self.frame.animate.reorient(-10, 72), run_time=2.0)
        shum = tx("шум", 44, C_NOISE).move_to([0, 2.7, 0]).fix_in_frame()
        self.phrase(2, "шум — линия дрожит вверх и вниз наугад")
        self.play(ReplacementTransform(surf, nsurf), ReplacementTransform(edge, nedge), ReplacementTransform(back, nback), FadeOut(wlab), FadeIn(shum), run_time=2.0)
        self.phrase(3, "сколько ни увеличивай — снова дрожь")
        fx = np.linspace(-0.6, 0.6, 140)
        fz = np.array([nf(x) for x in fx]) + np.cumsum(np.random.default_rng(9).normal(0, 0.03, 140))
        fine = ParametricCurve(lambda t: np.array([t, -0.1, float(np.interp(t, fx, fz))]), t_range=(-0.6, 0.6, 0.01)).set_stroke(WHITE, 4)
        self.play(FadeOut(shum), self.frame.animate.reorient(0, 86).move_to([0, 0, float(nf(0.0))]).set_height(4.2), run_time=2.5)
        self.play(ShowCreation(fine), run_time=1.5)
        self.phrase(4, "и высоту, и вес даёт такая линия")
        wl2 = ParametricCurve(lambda t: np.array([t, 0.0, float(np.interp(t, wxs, wz)) + 0.0]), t_range=(XL, XR, 0.04)).set_stroke(C_NOISE, 8)
        lab = VGroup(tx("высота — от шума", 24, C_BET).move_to([0, 2.8, 0]), tx("вес — от такого же шума", 24, C_AXIS).move_to([0, -0.65, 0])).fix_in_frame()
        self.play(FadeOut(fine), self.frame.animate.reorient(-8, 74).move_to([0, 0.8, 1.2]).set_height(10.0), FadeIn(wl2), FadeIn(lab), run_time=2.5)
        self.leave([nsurf, nedge, nback, ax, grid, wline, wl2, lab])


class A17(Film3D):
    END_K, END_CAP = 5, "остальное — добавка"

    def end2d(self):
        return [pill("обычное правило", C_BET, 28).move_to([-3.2, 0.5, 0]), tx("+", 50, WHITE).move_to([-0.8, 0.5, 0]), pill("добавка", C_ADD, 28).move_to([1.6, 0.5, 0]),
                tx("добавка — от дрожи шума", 24, C_NOISE).move_to([1.6, -0.4, 0])]

    def construct(self):
        _, nx, ny = noise(-4.0, 4.0, 0.4, 0.25, 40, 13, C_NOISE, 4)
        nzs = np.asarray(ny) - AY
        nsurf, nedge, nback, nf = _noise_surf(nx, nzs)
        ax, grid = axis3()
        mark = Line([-0.6, -0.2, 0], [0.6, -0.2, 0]).set_stroke(C_AXIS, 14)
        marker = Sphere(radius=0.22).set_color(C_BAD).set_shading(0.2, 0.2, 0.0).move_to([-0.6, 0.0, float(nf(-0.6))])
        plq = plaque("1944", "Ито", WHITE, 0, 2.65).fix_in_frame()
        self.phrase(1, "Ито: высоту берём на левом краю")
        self.enter([nsurf, nedge, nback, ax, grid, mark, marker, plq])
        self.play(self.frame.animate.reorient(-14, 68).move_to([0, 1.0, 1.4]).set_height(10.0), run_time=2.0)
        wall = Prism(width=4.4, height=DEP + 0.8, depth=4.6).set_color("#556").set_opacity(0.9).set_shading(0.3, 0.2, 0.1).move_to([2.8, DEP / 2, 2.3])
        lk = VGroup(lock(0.0, 0.0, C_BAD).scale(1.6), tx("будущее", 26, WHITE).move_to([0, -0.7, 0])).move_to([3.4, 1.2, 0]).fix_in_frame()
        past = tx("прошлое известно", 26, C_NOISE).move_to([-3.2, 2.5, 0]).fix_in_frame()
        self.phrase(2, "высота известна заранее: в будущее не подглядываем")
        self.play(FadeOut(plq), FadeIn(wall), FadeIn(lk), FadeIn(past), self.frame.animate.reorient(-24, 64), run_time=2.5)
        sc = VGroup(scales(C_SUM).scale(1.4), tx("если шум случаен, в среднем ноль", 28, WHITE).shift(UP * 1.9)).move_to([-1.2, 0.4, 0]).fix_in_frame()
        self.phrase(3, "сумма честная — в среднем ноль")
        self.play(FadeOut(lk), FadeOut(past), FadeOut(wall), *[m.animate.set_opacity(0.25) for m in (nsurf,)], FadeIn(sc), run_time=1.6)
        ch1 = VGroup(tx("шум", 30, C_NOISE), tx("→", 40, WHITE), tx("квадрат шума", 30, WHITE)).arrange(RIGHT, buff=0.5).move_to([0, 1.4, 0]).fix_in_frame()
        ch2 = pill("обычное правило: только часть ответа", C_BET, 26).move_to([0, -0.3, 0]).fix_in_frame()
        self.phrase(4, "возьмём от шума квадрат")
        self.play(FadeOut(sc), FadeIn(ch1), FadeIn(ch2), run_time=1.4)
        fin = self.end2d()
        for m in fin:
            m.fix_in_frame()
        self.phrase(5, "остальное — добавка")
        self.play(FadeOut(ch1), FadeOut(ch2), *[FadeIn(_bright(m)) for m in fin], FadeOut(nsurf), FadeOut(nedge), FadeOut(nback), FadeOut(ax), FadeOut(grid), FadeOut(mark), FadeOut(marker), run_time=1.5)


class A23(Film3D):
    END_K, END_CAP = 4, "какой способ взять, зависит от задачи"

    def end2d(self):
        return [pill("гладкая ширина — Риман", C_BET, 28).move_to([-3.4, 0.9, 0]), pill("случайная — Ито", C_NOISE, 28).move_to([3.4, 0.9, 0]),
                tx("а дальше — смотря какая задача", 34, WHITE).move_to([0, -0.7, 0])]

    def construct(self):
        surf, edge, back = ridge(0.4)
        ax, grid = axis3()
        t12 = towers(12)
        q = VGroup(tx("Как посчитать площадь так, чтобы ответ", 32), tx("не зависел от способа счёта?", 32)).arrange(DOWN, buff=0.15).move_to([0, 2.7, 0]).fix_in_frame()
        self.phrase(1, "возвращаемся к вопросу")
        self.enter([surf, edge, back, ax, grid, t12, q])
        self.play(self.frame.animate.reorient(-14, 66).move_to([0, 1.0, 1.4]).set_height(10.0), run_time=2.0)
        top = np.array([0.0, DEP / 2, F(0.0)])
        tips = [(-4.2, C_PRICE), (-1.4, C_AXIS), (1.4, C_BET), (4.2, C_ADD)]
        trunk = Line(top, top + OUT * 1.0).set_stroke(C_SUM, 18)
        base = top + OUT * 1.0
        branches = Group(*[Line(base, np.array([x, DEP / 2, F(0.0) + 3.4]), ).set_stroke(c, 12) for x, c in tips])
        balls = Group(*[Sphere(radius=0.28).set_color(c).set_shading(0.2, 0.2, 0.0).move_to([x, DEP / 2, F(0.0) + 3.4]) for x, c in tips])
        self.phrase(2, "единого способа нет — договор переписывали по пунктам")
        self.play(FadeOut(q), FadeOut(t12), FadeOut(surf), FadeOut(back), ShowCreation(trunk), self.frame.animate.reorient(-20, 70).move_to([0, 1.0, 3.2]).set_height(10.5), run_time=2.0)
        self.play(LaggedStart(*[ShowCreation(b) for b in branches], lag_ratio=0.2), run_time=1.6)
        self.play(LaggedStart(*[GrowFromCenter(b) for b in balls], lag_ratio=0.2), run_time=1.2)
        names = ["график: слои, приближения", "ось: вес, шум, подсказка", "высота: левый край, середина", "сложение: другие меры"]
        self.phrase(3, "четыре пункта — четыре ветви")
        self.play(self.frame.animate.reorient(0, 90).move_to([0, 0, 3.2]).set_height(8), run_time=2.0)
        labs = VGroup(*[node(n, x, 2.55, c, 3.1).scale(0.8) for n, (x, c) in zip(names, tips)]).fix_in_frame()
        self.play(FadeIn(labs), run_time=1.0)
        fin = self.end2d()
        for m in fin:
            m.fix_in_frame()
        self.phrase(4, "какой способ взять, зависит от задачи")
        self.play(*[FadeIn(_bright(m)) for m in fin], run_time=1.2)
