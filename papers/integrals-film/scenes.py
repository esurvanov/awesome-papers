"""Сцены ролика «Как сложить бесконечно много столбиков» (версия 6). Основа — scenes_base.py, мир — world.py, текст — narration.py,
кадры по фразам — passport.STORYBOARD. Кадр = фраза: self.show(...) на каждую фразу, свои движения — self.do(...).
Запуск одной сцены: uv run manimgl papers/integrals-film/scenes.py A04 -w -l  ·  весь ролик: uv run python core/pipeline/build.py papers/integrals-film"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from scenes_base import *


# =============================== Вопрос и гладкий график ===============================
class A01(Film):
    def construct(self):
        grid, full, cut = cells()
        self.show(grid, axis_(), ticks(), hill(), c="график", how={"hill": "create"}, rt=2.0)
        self.show(grid, axis_(), ticks(), fill_between(0, 10), hill(), label("площадь ?", pt(5, 1.2), size=34, on_fill=True), c="сколько в ней места")
        rect = VGroup(*[Square(side_length=0.48).set_stroke(C_SUM, 2).set_fill(C_SUM, 0.35).move_to([4.0 + 0.5 * i, 1.6 + 0.5 * j, 0])
                        for i in range(3) for j in range(2)])
        self.show(grid, axis_(), ticks(), fill_between(0, 10), hill(), rect, label("6 клеток", rect, size=24, direction=DOWN), c="у прямоугольника клетки легко пересчитать")
        self.show(grid, axis_(), ticks(), hill(), cut, c="у края клетки разрезаны кривой")
        self.show(grid, axis_(), ticks(), hill(), full, cut, label("целых 12", pt(1.6, 2.6), C_SUM, 26), label("задетых всего 26", pt(8.4, 2.6), C_BAD, 26),
                  c="точнее по клеткам не сказать")
        q = VGroup(tx("Как найти площадь точно,", 36), tx("чтобы у всех вышло одно и то же число?", 36)).arrange(DOWN, buff=0.15).move_to([0, 2.75, 0])
        self.show(axis_(), ticks(), fill_between(0, 10), hill(), z(q, "label"), c="вопрос ролика")


class A02(Film):
    def construct(self):
        u = 3.0
        self.show(axis_(), ticks(), hill(C_NOTE, 3, tag="hill_dim"), c="как читать график")
        self.show(axis_(), ticks(), hill(C_NOTE, 3, tag="hill_dim"), label("ось", pt(10.6, 0), C_AXIS, 28, direction=UR), c="линия внизу — ось")
        self.show(axis_(), ticks(), hill(C_NOTE, 3, tag="hill_dim"), tagged(dot(pt(u), C_AXIS, 0.14), "sl"), c="выбираем точку")
        seg = tagged(z(line(pt(u), pt(u, F(u)), C_BET, 5), "graph"), "seg")
        self.show(axis_(), ticks(), hill(C_NOTE, 3, tag="hill_dim"), seg, tagged(dot(pt(u), C_AXIS, 0.14), "sl"),
                  dim_v(X(u), AY, AY + F(u), "высота", C_BET, RIGHT, gap=0.5), c="длина отрезка — высота")
        self.show(axis_(), ticks(), hill(C_NOTE, 3, tag="hill_dim"), c="точку двигаем — высота меняется")
        self.do(lambda: self._run(u, 9.0, 0.6))
        self.show(axis_(), ticks(), c="след верхних концов — сам график")
        self.do(lambda: self._run(0.0, 10.0, 10.0, trail=True))

    def _run(self, a, b, back, trail=False):
        t = ValueTracker(a)
        U = lambda: t.get_value()
        seg = always_redraw(lambda: z(line(pt(U()), pt(U(), F(U())), C_BET, 5), "graph"))
        d = always_redraw(lambda: dot(pt(U()), C_AXIS, 0.14))
        val = always_redraw(lambda: label(num(F(U()), 1), pt(U(), F(U())) + UP * 0.35 + RIGHT * 0.3, C_BET, 24))
        ms = [seg, d, val]
        if trail:
            tr = always_redraw(lambda: z(poly_line([pt(x, F(x)) for x in np.linspace(0, max(U(), 0.05), 60)], C_PRICE, 6), "graph"))
            ms.insert(0, tr)
        self.add(*ms)
        self.play(t.animate.set_value(b), run_time=3.0, rate_func=smooth)
        if back != b:
            self.play(t.animate.set_value(back), run_time=2.0, rate_func=smooth)
        for m in ms:
            m.clear_updaters()
        self.remove(*ms)
        if trail:
            h = hill()
            self.add(h)
            self.keep(h)


class A03(Film):
    def construct(self):
        _, _, cut = cells()
        self.show(axis_(), ticks(), hill(), cut, c="с клетками у края неудобно")
        edges = np.linspace(0, 10, 6)
        cuts = tagged(VGroup(*[DashedLine(pt(u), pt(u, 3.2)).set_stroke(C_AXIS, 2) for u in edges]), "cuts")
        self.show(axis_(), ticks(), hill(), cuts, label("2 деления", pt(5, 0.35), C_AXIS, 24), c="ось режем на пять равных кусков")
        mids = VGroup(*[dot(pt(u + 1, F(u + 1)), C_BET, 0.1) for u in edges[:-1]])
        self.show(axis_(), ticks(), bars(5), hill(), cuts, tagged(mids, "mids"), c="верх столбика — на графике посередине куска")
        big, b = zoom_bar()
        self.show(big, label("кусок оси", b.get_bottom(), C_AXIS, 26, direction=DOWN, buff=0.3),
                  label("верх касается графика", b.get_top() + UP * 0.1, C_BET, 24, direction=UP, buff=0.5), c="столбик стоит на куске и касается графика")
        self.show(axis_(), ticks(), bars(5), hill(), label("почти вся фигура", pt(5, 3.5), C_TEXT, 28), c="щели остаются только у кривой")


class A04(Film):
    def construct(self):
        big, b = zoom_bar()
        x0, x1 = b.get_left()[0], b.get_right()[0]
        y0, y1 = b.get_bottom()[1], b.get_top()[1]
        rect6 = label("как у прямоугольника: ширина × высота", [0, 3.1, 0], C_TEXT, 28)
        self.show(big, rect6, c="площадь столбика: ширина × высота")
        self.show(big, dim_h(x0, x1, y0, "ширина 2", C_AXIS, gap=0.35), dim_v(x1, y0, y1, "высота 3", C_BET, RIGHT, gap=1.6),
                  label("2 × 3 = 6", b, C_TEXT, 34, on_fill=True), c="ширина 2, высота 3, площадь 6")
        n5 = bars(5)
        areas = VGroup(*[label(num(F(u + 1) * 2, 1), pt(u + 1, F(u + 1) / 2), C_TEXT, 24, on_fill=True) for u in np.linspace(0, 8, 5)])
        total = label(num(psum(5), 2), [5.6, 1.7, 0], C_SUM, 40)
        self.show(axis_(), ticks(), n5, hill(), areas, tagged(total, "total"), label("сумма", [5.6, 2.3, 0], C_SUM, 24), c="сумма — чуть больше 20")
        self.show(axis_(), ticks(), bars(10), hill(), tagged(label(num(psum(10), 2), [5.6, 1.7, 0], C_SUM, 40), "total"),
                  label("сумма", [5.6, 2.3, 0], C_SUM, 24), c="тоньше — ближе к 20")
        self.do(lambda: self._thinner())
        self.show(axis_(), ticks(), bars(20), hill(), tagged(label(num(psum(20), 3), [5.6, 1.7, 0], C_SUM, 40), "total"),
                  label("площадь горки = 20", [0, 3.0, 0], C_TEXT, 32), c="площадь горки равна 20")

    def _thinner(self):
        self.wait(1.5)
        b20 = bars(20)
        t20 = label(num(psum(20), 3), [5.6, 1.7, 0], C_SUM, 40)
        old_b = [m for m in self._cur if getattr(m, "tag", None) == "bars"][0]
        old_t = [m for m in self._cur if getattr(m, "tag", None) == "total"][0]
        self.play(ReplacementTransform(old_b, tagged(b20, "bars")), ReplacementTransform(old_t, tagged(t20, "total")), run_time=1.2)
        self._cur = [b20 if m is old_b else t20 if m is old_t else m for m in self._cur]




# =============================== блок B1 ===============================
# ====================== общее для A05–A06 (Архимед) ======================
_B1_S = archimedes_steps(6)            # 15; 3,75; 0,94; …
_B1_UNIT, _B1_RX0, _B1_RY = 0.4, -5.0, 2.35
_B1_C1, _B1_C2, _B1_C3 = C_BET, C_AXIS, C_ADD


def _b1_ticks_bare():
    """Те же деления, но подписи погашены (под осью место нужно размеру «10»); число детей то же — превращение плавное."""
    t = ticks(labels=())
    pad = Rectangle(width=10.2, height=0.78).set_stroke(width=0).set_fill(opacity=0).move_to([0, (-2.3 + AY + 0.08) / 2, 0])
    t.add(pad)
    return t


def _b1_segs(n=2, color=C_PRICE, op=0.35):
    edges = np.linspace(0, 10, n + 1)
    g = VGroup()
    for a, b in zip(edges[:-1], edges[1:]):
        p = Polygon(*[pt(u, F(u)) for u in np.linspace(a, b, 30)]).set_stroke(width=0).set_fill(color, op)
        g.add(p)
    return tagged(z(g, "fill"), "segs")


def _b1_cum(k):
    return _B1_RX0 + _B1_UNIT * sum(_B1_S[:k])


def _b1_r1():
    return tagged(ruler([_B1_S[0]], [_B1_C1], y=_B1_RY, x0=_B1_RX0), "r1")


def _b1_r2():
    h = _B1_S[1] / 2
    return tagged(ruler([h, h], [_B1_C2, _B1_C2], y=_B1_RY, x0=_b1_cum(1)), "r2")


def _b1_r3():
    return tagged(ruler([_B1_S[2]], [_B1_C3], y=_B1_RY, x0=_b1_cum(2)), "r3")


def _b1_rt():
    return tagged(ruler(_B1_S[3:6], [_B1_C3] * 3, y=_B1_RY, x0=_b1_cum(3)), "rt")


def _b1_ruler_lab(text, x, color, y=None, size=24, tag=None, on_top=False):
    yy = _B1_RY + (0.42 if on_top else -0.45) if y is None else y
    m = label(text, [x, yy, 0], color, size)
    return tagged(m, tag) if tag else m


def _b1_mark20():
    x = _B1_RX0 + _B1_UNIT * area_to(10)
    g = VGroup(line([x, _B1_RY - 0.3, 0], [x, _B1_RY + 0.3, 0], C_SUM, 5), label(num(area_to(10), 0), [x + 0.4, _B1_RY, 0], C_SUM, 28))
    return tagged(z(g, "label"), "mark20")


def _b1_cur_swap(scene, rem, add):
    ids = {id(m) for m in rem}
    scene._cur = [m for m in scene._cur if id(m) not in ids] + list(add)


# ====================== A05 ======================
class A05(Film):
    def construct(self):
        S = _B1_S
        base = lambda: [axis_(), hill(), tagged(z(plaque("III в. до н. э.", "Архимед"), "label"), "plaque"),
                        tagged(label(f"наша площадь {num(area_to(10), 0)}", [-4.3, 3.0, 0], C_NOTE, 26), "ours")]
        tri1 = lambda: tagged(tri(0, 10, _B1_C1), "tri1")
        apex = lambda: tagged(dot(pt(5, F(5)), _B1_C1, 0.11), "apex")
        # 1
        self.show(*base(), ticks(), c="Архимед нашёл площадь такой горки")
        # 2
        self.show(*base(), _b1_ticks_bare(), tri1(), apex(), c="самый большой треугольник")
        # 3
        d_base = dim_h(X(0), X(10), AY - 0.09, "10", C_AXIS, gap=0.14, size=24)
        d_h = dim_v(5.0, AY, AY + 3, "3", C_BET, RIGHT, gap=0.55)
        lk_h = tagged(link(pt(5, F(5)), [5.0, AY + 3, 0], C_BET), "lkh")
        eq = tagged(label(f"10 × 3 ÷ 2 = {num(S[0], 0)}", pt(5, 0.95), WHITE, 30, on_fill=True), "eq")
        lk_r = tagged(link([0.0, _B1_RY - 0.16, 0], pt(5, F(5)), C_BET), "lkr")
        lab1 = tagged(label(f"площадь треугольника {num(S[0], 0)}", [-2.4, _B1_RY - 0.5, 0], C_BET, 24), "lab1")
        self.show(*base(), _b1_ticks_bare(), tri1(), apex(), d_base, d_h, lk_h, eq, _b1_r1(), lk_r, lab1, c="площадь = основание × высота ÷ 2")
        # 4
        segs = _b1_segs()
        tris2 = lambda: tagged(archimedes_tris(2, _B1_C2), "tri2")
        lk_r4 = tagged(link([0.0, _B1_RY - 0.16, 0], pt(5, F(5)), C_BET), "lkr")
        lab1b = tagged(label(f"площадь треугольника {num(S[0], 0)}", [-2.4, _B1_RY - 0.5, 0], C_BET, 24), "lab1")
        common4 = lambda: [*base(), _b1_ticks_bare(), segs, tri1(), apex(), _b1_r1(), lk_r4, lab1b]
        self.show(*common4(), c="по бокам два пустых кусочка")

        def grow():
            t2 = tris2()
            self.play(LaggedStart(*[GrowFromCenter(t) for t in t2], lag_ratio=0.3), run_time=1.2)
            self.keep(t2)
        self.do(grow)
        # 5: два оранжевых треугольника ложатся в одну полоску ¼ от жёлтой
        r2 = _b1_r2()
        halves = list(r2)
        lab2 = tagged(label(f"¼ от {num(S[0], 0)} = {num(S[1], 2)}", [_b1_cum(1) + _B1_UNIT * S[1] / 2, _B1_RY - 0.5, 0], _B1_C2, 24), "lab2")
        common5 = lambda: [*base(), _b1_ticks_bare(), tri1(), apex(), tris2(), _b1_r1(), lk_r4, lab1b]
        pieces_end = [r2, lab2]
        self.show(*(common5() + pieces_end if self._dry else common5()), c="два малых вместе — четверть первого")

        def fly():
            olds = [m for m in self._cur if getattr(m, "tag", None) == "tri2"][0]
            cps = [t.copy() for t in olds]
            self.add(*cps)
            self.play(*[ReplacementTransform(c, h) for c, h in zip(cps, halves)], run_time=1.4)
            self.remove(*cps)
            self.add(r2)
            self.play(FadeIn(lab2), run_time=0.4)
            self.keep(r2, lab2)
        self.do(fly)


# ====================== A06 ======================
class A06(Film):
    def construct(self):
        S = _B1_S
        hl = lambda: [axis_(), hill(), _b1_ticks_bare()]
        t1 = lambda: tagged(tri(0, 10, _B1_C1), "tri1")
        t2 = lambda: tagged(archimedes_tris(2, _B1_C2), "tri2")
        t3 = lambda: tagged(archimedes_tris(3, _B1_C3), "tri3")
        n1 = lambda: _b1_ruler_lab(num(S[0], 0), _B1_RX0 + _B1_UNIT * S[0] / 2, _B1_C1, size=26, tag="n1", on_top=True)
        n2 = lambda: _b1_ruler_lab(num(S[1], 2), _b1_cum(1) + _B1_UNIT * S[1] / 2, _B1_C2, size=26, tag="n2", on_top=True)
        n3 = lambda: _b1_ruler_lab(num(S[2], 2), _b1_cum(2) + _B1_UNIT * S[2] / 2 + 0.25, _B1_C3, size=26, tag="n3", on_top=True)
        lab2 = lambda: tagged(label(f"¼ от {num(S[0], 0)} = {num(S[1], 2)}", [_b1_cum(1) + _B1_UNIT * S[1] / 2, _B1_RY - 0.5, 0], _B1_C2, 24), "lab2")
        lab3 = lambda: tagged(label(f"¼ от {num(S[1], 2)}", [_b1_cum(2) + 0.2, _B1_RY - 1.05, 0], _B1_C3, 24), "lab3")
        lab1 = lambda: tagged(label(f"площадь треугольника {num(S[0], 0)}", [-2.4, _B1_RY - 0.5, 0], C_BET, 24), "lab1")
        lk = lambda: tagged(link([0.0, _B1_RY - 0.16, 0], pt(5, F(5)), C_BET), "lkr")
        # 1
        start1 = [*hl(), t1(), t2(), _b1_r1(), _b1_r2(), lab1(), lab2(), lk()]
        end1 = [*hl(), t1(), t2(), t3(), _b1_r1(), _b1_r2(), _b1_r3(), lab1(), lab2(), lab3(), lk()]
        self.show(*(end1 if self._dry else start1), c="шаг 3: четыре треугольника")
        if not self._dry:
            self._b1_do1()
        # 2
        f2 = [*hl(), t1(), t2(), t3(), _b1_r1(), _b1_r2(), _b1_r3(), n1(), n2(), n3()]
        self.show(*f2, c="складываем площади шагов")
        # 3
        tail = _b1_rt()
        dots = tagged(label("…", [_b1_cum(6) + 0.1, _B1_RY - 0.5, 0], WHITE, 30), "dots")
        f3 = [*hl(), t1(), t2(), t3(), _b1_r1(), _b1_r2(), _b1_r3(), tail, dots, n1(), n2(), n3(), _b1_mark20()]
        self.show(*f3, c="каждый шаг в четыре раза меньше")
        # 4: хвост перекладывается в пунктирную добавку длиной в треть
        ext_w = S[0] / 3 * _B1_UNIT
        ext = lambda: tagged(z(Rectangle(width=ext_w, height=0.32).set_stroke(C_BET, 3).set_fill(C_BET, 0.3).move_to([_b1_cum(1) + ext_w / 2, _B1_RY, 0]), "bar"), "ext")
        extlab = lambda: tagged(label(f"его треть = {num(S[0] / 3, 0)}", [_b1_cum(1) + ext_w / 2, _B1_RY - 0.5, 0], C_BET, 24), "extlab")
        sumlab = lambda: tagged(label(f"{num(S[0], 0)} + {num(S[0] / 3, 0)} = {num(area_to(10), 0)}", [-2.4, _B1_RY - 1.05, 0], C_SUM, 28), "sumlab")
        base4 = lambda: [*hl(), t1(), _b1_r1(), n1(), _b1_mark20(), lab1(), lk()]
        start4 = [*hl(), t1(), t2(), t3(), _b1_r1(), _b1_r2(), _b1_r3(), tail, dots, n1(), n2(), n3(), _b1_mark20(), lab1(), lk()]
        end4 = base4() + [ext(), extlab(), sumlab()]
        self.show(*(end4 if self._dry else start4), c="первый треугольник и ещё его треть")
        if not self._dry:
            self._b1_do4(ext(), extlab(), sumlab(), tail)
        # 5
        self.show(*self._b1_cards(), c="два пути — одно число")

    def _b1_do1(self):
        S = _B1_S
        t3 = tagged(archimedes_tris(3, _B1_C3), "tri3")
        r3 = _b1_r3()
        lab3 = tagged(label(f"¼ от {num(S[1], 2)}", [_b1_cum(2) + 0.2, _B1_RY - 1.05, 0], _B1_C3, 24), "lab3")
        self.play(LaggedStart(*[GrowFromCenter(t) for t in t3], lag_ratio=0.2), run_time=1.2)
        self.play(FadeIn(r3), FadeIn(lab3), run_time=0.6)
        self.keep(t3, r3, lab3)

    def _b1_do4(self, ext, extlab, sumlab, tail):
        olds = [m for m in self._cur if getattr(m, "tag", None) in ("r2", "r3", "rt", "dots", "n2", "n3", "tri2", "tri3", "lab2", "lab3")]
        strips = VGroup(*[m for m in olds if getattr(m, "tag", None) in ("r2", "r3", "rt")])
        others = [m for m in olds if m not in list(strips)]
        self.play(ReplacementTransform(strips, ext), *[FadeOut(m) for m in others], run_time=1.4)
        self.play(FadeIn(extlab), FadeIn(sumlab), run_time=0.5)
        ids = {id(m) for m in olds}
        self._cur = [m for m in self._cur if id(m) not in ids] + [ext, extlab, sumlab]

    def _b1_cards(self):
        def card(cx, kind):
            g = VGroup()
            hh = hill(base=0.0)
            ax = axis_(base=0.0, w=4, tag="ax_c")
            g.add(ax, hh)
            if kind == "bars":
                g.add(bars(20, base=0.0, color=C_BET, op=0.85))
            else:
                g.add(tri(0, 10, _B1_C1).shift(UP * (AY * -1)))  # треугольник построен над осью AY — переносим на ось 0
                for lv, col in ((2, _B1_C2), (3, _B1_C3)):
                    g.add(archimedes_tris(lv, col).shift(UP * (-AY)))
            g.scale(0.45).move_to([cx, 0.9, 0])
            return g
        left, right = card(-3.4, "bars"), card(3.4, "tris")
        eq = tagged(label("=", [0, 0.9, 0], C_SUM, 90), "eq")
        l1 = tagged(label(f"столбики → {num(area_to(10), 0)}", [-3.4, -0.45, 0], C_BET, 30), "l1")
        l2 = tagged(label(f"треугольники → {num(area_to(10), 0)}", [3.4, -0.45, 0], C_AXIS, 30), "l2")
        return [tagged(left, "cardL"), tagged(right, "cardR"), eq, l1, l2]


# ====================== общее для A07–A10 (две панели) ======================
UB, US = 0.55, 0.75            # верхняя панель: ось и сжатие горки по высоте
LB, LS = -2.0, 0.08            # нижняя панель: ось и масштаб (20 единиц = 1,6)
_B1_F = lambda u: US * F(u)
_B1_FF = lambda u: 0.997 * US * F(u)      # заливка чуть ниже линии горки (на глаз не видно), чтобы рамки не совпадали до пикселя
C_RUN = C_AXIS


def _b1_up_axis():
    return axis_(base=UB)


def _b1_up_hill():
    return hill(base=UB, s=US)


def _b1_up_ticks(show=(0, 10)):
    t = ticks(base=UB, labels=show)
    t.add(Rectangle(width=10.2, height=0.96).set_stroke(width=0).set_fill(opacity=0).move_to([0, (UB + 0.08 - 0.33 + 0.0) / 2 + 0.0, 0]))
    return t


def _b1_low_axis():
    return axis_(base=LB, w=4, tag="axis_low")


def _b1_low_ticks():
    t = ticks(base=LB, labels=())
    t.add(Rectangle(width=13.4, height=1.87).set_stroke(width=0).set_fill(opacity=0).move_to([0, (-2.12 - 0.25) / 2, 0]))
    return tagged(t, "ticks_low")


def _b1_low_scale():
    g = VGroup(line(pt(-0.6, 0, LB), pt(-0.6, 20 * LS, LB), C_SUM, 2),
               tx("20", 18, C_SUM).move_to(pt(-0.95, 20 * LS, LB)), tx("0", 18, C_SUM).move_to(pt(-0.95, 0, LB)))
    return tagged(z(g, "axis"), "lowscale")


def _b1_up_scale():
    g = VGroup(line(pt(-0.9, 0, UB), pt(-0.9, 3 * US, UB), C_BET, 2))
    for k in range(4):
        g.add(line(pt(-0.9, k * US, UB) + LEFT * 0.07, pt(-0.9, k * US, UB) + RIGHT * 0.07, C_BET, 2),
              tx(str(k), 18, C_BET).move_to(pt(-0.9, k * US, UB) + LEFT * 0.3))
    return tagged(z(g, "axis"), "upscale")


def _b1_low(u1=10.0):
    return tagged(z(poly_line([pt(u, area_to(u) * LS, LB) for u in np.linspace(0, max(u1, 0.03), 80)], C_SUM, 5), "graph"), "low")


def _b1_fill(u0, u1, op=0.30, tag="fill"):
    u1 = max(u1, u0 + 0.02)
    return fill_between(u0, u1, C_SUM, op, base=UB, f=_B1_FF, tag=tag)


def _b1_dot(u):
    return tagged(dot(pt(u, 0, UB), C_RUN, 0.13), "run")


def _b1_ldot(u, tag="ldot"):
    return tagged(dot(pt(u, area_to(u) * LS, LB), C_RUN, 0.11), tag)


def _b1_rlink(u, tag="rlink"):
    return tagged(link(pt(u, 0, UB), pt(u, area_to(u) * LS, LB), C_RUN), tag)


def _b1_areanum(u):
    m = label(f"площадь до точки  {num(area_to(u), 1)}", [0, 3.4, 0], C_SUM, 28)
    m.align_to(np.array([-6.5, 0, 0]), LEFT)
    return tagged(m, "areanum")


def _b1_lnum(u):
    p = pt(u, area_to(u) * LS, LB) + np.array([0.65, 0.3, 0])
    return tagged(label(num(area_to(u), 1), p, C_SUM, 26), "lnum")


def _b1_panels(ticks_show=(0, 10)):
    return [_b1_up_axis(), _b1_up_ticks(ticks_show), _b1_up_hill(), _b1_low_axis(), _b1_low_ticks(), _b1_low_scale()]


def _b1_plaque(text_who, x=4.2):
    return tagged(z(plaque(text_who[0], text_who[1], x=x, y=3.05), "label"), "plaque")


def _b1_run_dyn(tr, areanum=True, low=False, lnum=False, extra_fill=None):
    """Живые объекты бегунка: заливка 0…u, точка, точка внизу, пунктир, число; по желанию — след графика и число внизу."""
    o = []
    for fn, tg in ((lambda: _b1_fill(0, tr.get_value()), "fill"), (lambda: _b1_dot(tr.get_value()), "run"),
                   (lambda: _b1_ldot(tr.get_value()), "ldot"), (lambda: _b1_rlink(tr.get_value()), "rlink")):
        d = always_redraw(fn)
        d.tag = tg
        o.append(d)
    if areanum:
        d = always_redraw(lambda: _b1_areanum(tr.get_value()))
        d.tag = "areanum"
        o.append(d)
    if low:
        d = always_redraw(lambda: _b1_low(tr.get_value()))
        d.tag = "low"
        o.append(d)
    if lnum:
        d = always_redraw(lambda: _b1_lnum(tr.get_value()))
        d.tag = "lnum"
        o.append(d)
    return o


def _b1_replace_cur(scene, dyn):
    tags = {m.tag for m in dyn}
    olds = [m for m in scene._cur if getattr(m, "tag", None) in tags]
    scene.remove(*olds)
    scene.add(*dyn)
    scene._cur = [m for m in scene._cur if getattr(m, "tag", None) not in tags] + list(dyn)


def _b1_freeze(dyn):
    for d in dyn:
        d.clear_updaters()


# ====================== A07 ======================
class A07(Film):
    def construct(self):
        plq = lambda: _b1_plaque(("XVII в.", "Ньютон и Лейбниц"))
        # 1 — геометрия A04
        self.show(axis_(), ticks(), bars(20), hill(), tagged(label("складывать долго", [-3.6, 2.7, 0], C_NOTE, 30), "long"), plq(),
                  c="складывать столбики долго")
        # 2 — две панели, точка и заливка слева
        u0 = 3.0
        up = lambda u: [_b1_fill(0, u), _b1_dot(u), _b1_areanum(u)]
        base = [_b1_up_axis(), _b1_up_ticks(), _b1_up_hill()]
        self.show(*base, *up(u0), plq(), c="площадь до точки")
        # 3 — ведём вправо
        self.show(*base, *up(u0), plq(), c="ведём точку вправо")

        def go():
            tr = ValueTracker(u0)
            dyn = [d for d in _b1_run_dyn(tr) if d.tag in ("fill", "run", "areanum")]
            _b1_replace_cur(self, dyn)
            self.play(tr.animate.set_value(7.0), run_time=2.0, rate_func=smooth)
            _b1_freeze(dyn)
        self.do(go)
        # 4 — число откладываем вниз над той же точкой
        u1 = 7.0
        low_part = lambda: [_b1_low_axis(), _b1_low_ticks(), _b1_low_scale()]
        f4 = lambda: [*base, *up(u1), plq(), *low_part(), _b1_ldot(u1), _b1_rlink(u1), _b1_lnum(u1)]
        self.show(*f4(), c="число откладываем внизу")
        # 5 — вся ось, рисуется график
        end5 = [*base, _b1_fill(0, 10), _b1_dot(10), _b1_areanum(10), plq(), *low_part(), _b1_low(10), _b1_ldot(10), _b1_rlink(10), _b1_lnum(10)]
        self.show(*(end5 if self._dry else f4()), c="так рисуется нижний график")

        def sweep():
            tr = ValueTracker(u1)
            dyn = _b1_run_dyn(tr, low=False, lnum=True)
            _b1_replace_cur(self, dyn)
            self.play(tr.animate.set_value(0.0), run_time=0.7, rate_func=smooth)
            low = always_redraw(lambda: _b1_low(tr.get_value()))
            low.tag = "low"
            self.add(low)
            self._cur = list(self._cur) + [low]
            self.play(tr.animate.set_value(10.0), run_time=2.6, rate_func=smooth)
            _b1_freeze(dyn + [low])
        self.do(sweep)


# ====================== A08 ======================
def _b1_ov(m):
    m.overlay = True
    return m


def _b1_bar(u0, u1, color=C_BET):
    """Столбик: основание чуть выше оси (на 0,006), чтобы рамка столбика целиком лежала внутри рамки горки."""
    h = _B1_F((u0 + u1) / 2)
    r = Rectangle(width=(u1 - u0) * 0.97, height=h - 0.006).set_stroke(color, 2).set_fill(color, 0.85)
    r.move_to(pt((u0 + u1) / 2, (h + 0.006) / 2, UB))
    return z(r, "bar")


def _b1_step(ua, ub, tagp, color=C_BET, labtext=None):
    """Ступенька нижнего графика: ход на одно деление и подъём; тот же цвет, что у столбика."""
    pa = pt(ua, area_to(ua) * LS, LB)
    pb = pt(ub, area_to(ub) * LS, LB)
    corner = np.array([pb[0], pa[1], 0.0])
    run_ = tagged(z(line(pa, corner, color, 5), "graph"), "run" + tagp)
    rise = tagged(z(line(corner, pb, color, 9), "graph"), "rise" + tagp)
    lab = tagged(label(labtext, corner + np.array([0.5, -0.3, 0]), color, 26), "stlab" + tagp)
    return run_, rise, lab


def _b1_ylink(um, ua, tagp):
    return tagged(link(pt(um, 0, UB), [X(um), pt(ua, area_to(ua) * LS, LB)[1], 0], C_BET, 2), "ylink" + tagp)


class A08(Film):
    def construct(self):
        base = lambda: [_b1_up_axis(), _b1_up_ticks(), _b1_up_hill(), _b1_low_axis(), _b1_low_ticks(), _b1_low_scale(), _b1_low(10)]
        pos = lambda u, a=None: [_b1_dot(u), _b1_ldot(u), _b1_rlink(u), _b1_areanum(u)]
        h1 = F(5.5)
        rise1 = area_to(6) - area_to(5)
        bar1 = lambda: tagged(_b1_bar(5, 6), "fillB")
        # 1
        start1 = [*base(), _b1_fill(0, 5), *pos(5)]
        self.show(*start1, c="сдвигаем точку на одно деление")

        def move1():
            tr = ValueTracker(5.0)
            dyn = _b1_run_dyn(tr)
            # заливка 0…5 остаётся, добавляется полоска 5…u
            dyn = [d for d in dyn if d.tag != "fill"]
            strip = always_redraw(lambda: _b1_fill(5, tr.get_value(), 0.30, "fillB"))
            strip.tag = "fillB"
            dyn.append(strip)
            _b1_replace_cur(self, dyn)
            self.play(tr.animate.set_value(6.0), run_time=1.5, rate_func=smooth)
            _b1_freeze(dyn)
        self.do(move1)
        # 2
        d1 = dim_h(X(5), X(6), UB - 0.1, "1", C_AXIS, gap=0.3, size=24)
        lbar = tagged(label(f"1 × {num(h1, 0)} = {num(h1, 0)}", [X(5.5), 3.3, 0], C_BET, 28), "labbar")
        fA = lambda: _b1_fill(0, 5)
        f2 = [*base(), fA(), bar1(), *pos(6), d1, lbar]
        self.show(*f2, c="столбик шириной в одно деление")
        # 3
        run1, rs1, st1 = _b1_step(5, 6, "1", C_BET, f"+{num(rise1, 0)}")
        yl1 = _b1_ylink(5.5, 5, "1")
        lbar3 = tagged(label(f"высота {num(h1, 0)}", [X(5.5), 3.3, 0], C_BET, 28), "labbar")
        f3 = [*base(), fA(), bar1(), *pos(6), run1, rs1, st1, yl1, lbar3]
        self.show(*f3, c="площадь +3, график +3")
        # 4
        scale = _b1_up_scale()
        ring_u = tagged(z(Circle(radius=0.26).set_stroke(C_BET, 4).move_to(pt(-0.9, 3 * US, UB) + LEFT * 0.3), "dim"), "ringu")
        ring_l = tagged(z(Circle(radius=0.34).set_stroke(C_BET, 4).move_to(st1.get_center()), "dim"), "ringl")
        self.show(*f3[:-1], scale, ring_u, ring_l, lbar3, c="шкалы разные, числа те же")
        # 5
        h2 = F(8.5)
        rise2 = area_to(9) - area_to(8)
        bar2 = tagged(_b1_bar(8, 9), "bar2")
        run2, rs2, st2 = _b1_step(8, 9, "2", C_BET, f"+{num(rise2, 1)}")
        yl2 = _b1_ylink(8.5, 8, "2")
        lbar5 = tagged(label(f"высота {num(h1, 0)}", [X(5.5), 3.3, 0], C_BET, 28), "labbar")
        lbar2 = tagged(label(num(h2, 1), [X(8.5), UB + h2 * US + 0.35, 0], C_BET, 28), "labbar2")
        f5 = [*base(), _b1_fill(0, 8), bar1(), bar2, *pos(9), run1, rs1, st1, yl1, run2, rs2, st2, yl2, scale, lbar5, lbar2]
        self.show(*f5, c="у края горка ниже — график положе")
        # 6
        us = [1, 3, 5, 7, 9]
        stems = _b1_ov(tagged(z(VGroup(*[line(pt(u, 0, UB), pt(u, F(u) * US, UB), C_BET, 3) for u in us]), "bar"), "stems"))

        def tang(u):
            c = pt(u, area_to(u) * LS, LB)
            k = LS * F(u)
            return line(c + np.array([-0.6, -0.6 * k, 0]), c + np.array([0.6, 0.6 * k, 0]), C_BET, 6)
        tans = _b1_ov(tagged(z(VGroup(*[tang(u) for u in us]), "dim"), "tans"))
        sl = _b1_ov(tagged(z(VGroup(*[link(pt(u, 0, UB), pt(u, area_to(u) * LS, LB), C_BET, 2) for u in us]), "dim"), "slinks"))
        self.show(*base(), stems, tans, sl, c="выше горка — круче график")


# ====================== A09 ======================
class A09(Film):
    def construct(self):
        tk = (0, 2, 8, 10)
        a2, a8 = area_to(2), area_to(8)
        base = lambda: [_b1_up_axis(), _b1_up_ticks(tk), _b1_up_hill(), _b1_low_axis(), _b1_low_ticks(), _b1_low_scale(), _b1_low(10)]
        m28 = lambda: [tagged(dot(pt(2, 0, UB), C_RUN, 0.12), "m2"), tagged(dot(pt(8, 0, UB), C_RUN, 0.12), "m8")]
        # 1
        self.show(*base(), _b1_fill(2, 8), *m28(), c="площадь между отметками 2 и 8")
        # 2
        def lowmarks():
            seg2 = tagged(z(line(pt(2, 0, LB), pt(2, a2 * LS, LB), C_SUM, 5), "graph"), "seg2")
            seg8 = tagged(z(line(pt(8, 0, LB), pt(8, a8 * LS, LB), C_SUM, 5), "graph"), "seg8")
            l2 = _b1_ldot(2, "l2")
            l8 = _b1_ldot(8, "l8")
            rl2 = _b1_rlink(2, "rl2")
            rl8 = _b1_rlink(8, "rl8")
            t2 = tagged(label(f"≈ {num(a2, 0)}", pt(2, a2 * LS, LB) + np.array([-0.75, 0.32, 0]), C_SUM, 26), "t2")
            t8 = tagged(label(f"≈ {num(a8, 0)}", pt(8, a8 * LS, LB) + np.array([0.8, -0.38, 0]), C_SUM, 26), "t8")
            return [seg2, seg8, l2, l8, rl2, rl8, t2, t8]
        self.show(*base(), _b1_fill(0, 8), _b1_fill(0, 2, 0.55, "fill2"), *m28(), *lowmarks(), c="слева от 8 и слева от 2")
        # 3 — миниатюры «слева от 8 − слева от 2 = между»
        def mini(cx, u0, u1, op):
            g = VGroup(fill_between(u0, u1, C_SUM, op, base=0.0), axis_(base=0.0, w=3, u0=0, u1=10), hill(base=0.0, w=4))
            g.scale(0.2).move_to([cx, 3.25, 0])
            return g
        sig = lambda s, x: tagged(label(s, [x, 3.25, 0], WHITE, 36), "sg" + s)
        minis = [tagged(mini(-3.4, 0, 8, 0.4), "mi1"), sig("−", -1.8), tagged(mini(0.0, 0, 2, 0.4), "mi2"), sig("=", 1.8), tagged(mini(3.4, 2, 8, 0.7), "mi3")]
        self.show(*base(), _b1_fill(2, 8, 0.55), _b1_fill(0, 2, 0.15, "fill2"), *m28(), *lowmarks(), *minis, c="большее минус меньшее = кусок между")
        # 4 — разница высот на нижнем графике
        y2, y8 = pt(2, a2 * LS, LB)[1], pt(8, a8 * LS, LB)[1]
        xr = 5.1
        h2 = tagged(link([X(2), y2, 0], [xr, y2, 0], C_SUM, 2), "h2")
        h8 = tagged(link([X(8), y8, 0], [xr, y8, 0], C_SUM, 2), "h8")
        br = tagged(dim_v(xr, y2, y8, f"≈ {num(a8 - a2, 0)}", C_SUM, RIGHT, gap=0.45, size=28), "brace")
        f4 = [*base(), _b1_fill(2, 8, 0.55), _b1_fill(0, 2, 0.15, "fill2"), *m28(), *lowmarks(), h2, h8, br]
        self.show(*f4, c="разница высот — это площадь между")
        # 5
        short = tagged(pill("путь короче", C_SUM, 28).move_to([-3.6, 3.15, 0]), "short")
        self.show(*base(), *m28(), *lowmarks(), h2, h8, br, short, c="складывать не пришлось")


# ====================== A10 ======================
def _b1_sign(cx=5.8, cy=2.2, h=1.5, color=C_SUM):
    raw = [(-0.30, -0.38), (-0.22, -0.47), (-0.12, -0.50), (-0.05, -0.42), (-0.02, -0.25), (0.0, 0.0),
           (0.02, 0.25), (0.05, 0.42), (0.12, 0.50), (0.22, 0.47), (0.30, 0.38)]
    pts_ = [np.array([cx + x * h, cy + y * h, 0.0]) for x, y in raw]
    m = VMobject().set_points_smoothly(pts_)
    m.set_stroke(color, 8).set_fill(opacity=0)
    return tagged(z(m, "graph"), "sign")


class A10(Film):
    def construct(self):
        tk = (0, 2, 8, 10)
        base = lambda: [_b1_up_axis(), _b1_up_ticks(tk), _b1_up_hill(), _b1_low_axis(), _b1_low_ticks(), _b1_low_scale(), _b1_low(10)]
        us = [1, 3, 5, 7, 9]

        def tang(u):
            c = pt(u, area_to(u) * LS, LB)
            k = LS * F(u)
            return line(c + np.array([-0.6, -0.6 * k, 0]), c + np.array([0.6, 0.6 * k, 0]), C_BET, 6)
        # 1
        q = tagged(label("?", [-2.6, -0.85, 0], C_NOTE, 60), "q")
        self.show(*base(), q, c="откуда нижний график")
        # 2
        tans = _b1_ov(tagged(z(VGroup(*[tang(u) for u in us]), "dim"), "tans"))

        def arr(u):
            a = Arrow(pt(u, F(u) * US, UB), pt(u, area_to(u) * LS, LB) + UP * 0.12, buff=0, stroke_width=3).set_color(C_BET)
            return a
        arrows = _b1_ov(tagged(z(VGroup(*[arr(u) for u in us]), "dim"), "arrows"))
        hl = tagged(label("высота горки", [X(5) + 1.1, 1.0, 0], C_BET, 24), "hlab")
        rl = tagged(label("подъём", [X(5) + 0.9, -1.75, 0], C_BET, 24), "rlab")
        self.show(*base(), tans, arrows, hl, rl, c="подъём = высота горки")
        # 3
        chk = tagged(z(poly_line([np.array([-4.1, -0.8, 0]), np.array([-3.85, -1.05, 0]), np.array([-3.35, -0.45, 0])], C_SUM, 9), "graph"), "chk")
        known = tagged(label("известен", [-2.3, -0.8, 0], C_SUM, 30), "known")
        self.show(*base(), chk, known, c="для многих горок известен")
        # 4
        plq = lambda: tagged(z(plaque("1675", "Лейбниц", x=-3.9, y=3.05), "label"), "plaque")
        sign = _b1_sign()
        n8 = tagged(label("8", [6.35, 3.0, 0], C_AXIS, 26), "n8")
        n2 = tagged(label("2", [5.25, 1.4, 0], C_AXIS, 26), "n2")
        fl = lambda: _b1_fill(2, 8)
        bars_ = lambda: bars(edges=np.linspace(2, 8, 49), pick="mid", color=C_BET, op=0.85, base=UB, f=_B1_F, tag="nbars")
        self.show(*(base() + [plq(), sign, n8, n2] if self._dry else base() + [fl(), plq()]), c="сумма узких столбиков — буква эс")

        def merge():
            f = [m for m in self._cur if getattr(m, "tag", None) == "fill"][0]
            nb = bars_()
            self.play(FadeOut(f), FadeIn(nb), run_time=0.8)
            self.wait(0.3)
            self.play(FadeOut(nb), ShowCreation(sign), run_time=1.0)
            self.play(FadeIn(n8), FadeIn(n2), run_time=0.4)
            ids = {id(f)}
            self._cur = [m for m in self._cur if id(m) not in ids] + [sign, n8, n2]
        self.do(merge)
        # 5
        summa = tagged(label("summa", [5.8, 1.0, 0], WHITE, 24), "summa")
        word = tagged(label(f"интеграл ≈ {num(area_to(8) - area_to(2), 0)}", [5.0, 3.5, 0], C_SUM, 28), "word")
        self.show(*base(), plq(), _b1_sign(), n8, n2, summa, word, c="интеграл — сумма узких столбиков")


# =============================== блок B2 ===============================
# ---------- помощники B2 ----------
def _b2_place(m, s, cx, cy):
    """Уменьшенная копия картинки (ось на y = AY, центр u = 5) — в центр (cx, cy)."""
    m.scale(s, about_point=pt(5, 0))
    m.shift(np.array([cx, cy, 0.0]) - pt(5, 0) * 1.0 + np.array([0, 0, 0]) * 0)
    return m


def _b2_T(*ms, pre="p"):
    """Уникальные метки для объектов, которые переходят из кадра в кадр (иначе основа гасит и снова показывает их)."""
    for i, m in enumerate(ms):
        m.tag = f"{pre}{i}"
    return ms


def _b2_thin_edges(n=20, seed=3):
    rng = np.random.default_rng(seed)
    w = rng.uniform(0.5, 1.5, n)
    return list(np.concatenate([[0], np.cumsum(w / w.sum() * 10)]))


EA = [0, 1.5, 3, 5.5, 8, 10]
EB = [0, 2.5, 4, 6.5, 8.5, 10]
EC = [0, 1.2, 3.5, 5.2, 7.8, 10]


def _b2_mini(edges, pick, cx, cy, s=0.32, tag_main=False, color=C_BET):
    """Три слоя мини-картинки: ось, горка, столбики, плюс число суммы под ней."""
    ax = _b2_place(axis_(w=3, u0=-0.3, u1=10.3, tag="axis" if tag_main else "ax_m"), s, cx, cy)
    hl = _b2_place(hill(C_PRICE, 3, tag="hill" if tag_main else "hill_m"), s, cx, cy)
    bs = _b2_place(bars(edges=edges, pick=pick, color=color, tag="bars" if tag_main else "bars_m"), s, cx, cy)
    bs.set_stroke(width=1.2)
    return ax, hl, bs


def _b2_sum(v, cx, cy, d=2, size=30, prefix=""):
    return label(prefix + num(v, d), [cx, cy, 0], C_SUM, size)


def _b2_swap(scene, pairs, rt=1.2):
    """Плавная замена объектов (старый → новый) внутри кадра; новые становятся частью кадра."""
    scene.play(*[ReplacementTransform(o, n) for o, n in pairs], run_time=rt)
    for o, n in pairs:
        scene._cur = [n if m is o else m for m in scene._cur]


def _b2_call(n, at, to, color=C_NOTE):
    at, to = np.array([at[0], at[1], 0.0]), np.array([to[0], to[1], 0.0])
    d = (to - at) / np.linalg.norm(to - at)
    ln = line(at + d * 0.28, to, color, 2.5)
    c = Circle(radius=0.28).set_stroke(color, 3).set_fill(C_PLATE, 1).move_to(at)
    t = tx(str(n), 26, color).move_to(at)
    return tagged(z(VGroup(ln, c, t), "label"), f"c{n}")


def _b2_dots(hi=2.0, r=0.085, dim=1.0):
    """Прыгающий график: синие точки на высоте hi — в дробях p/q; белые на оси. Позиции общие для A14 и A15."""
    blues = set()
    for q in range(2, 10):
        for p in range(1, q):
            blues.add(round(10 * p / q, 3))
    blues |= {5.33, 4.58, 5.45}
    rng = np.random.default_rng(7)
    whites = [w for w in rng.uniform(0.25, 9.75, 55) if all(abs(w - b) > 0.12 for b in blues)] + [4.93, 5.07, 5.28, 5.4, 4.66]
    g = VGroup()
    for u in sorted(blues):
        g.add(dot(pt(u, hi), C_PRICE, r))
    for u in sorted(whites):
        g.add(dot(pt(u, 0.0), WHITE, r))
    if dim < 1:
        g.set_opacity(dim)
    return tagged(g, "dots"), sorted(blues), sorted(whites)


# =============================== A11 · Риман ===============================
class A11(Film):
    def construct(self):
        plq = tagged(plaque("1854", "Риман"), "plq")
        self.show(axis_(), ticks(), hill(), bars(5), plq, label("= 20 ?", [0, 2.4, 0], C_SUM, 40),
                  c="Риман спросил: всегда ли выйдет двадцать")
        cuts = lambda E: tagged(VGroup(*[DashedLine(pt(u), pt(u, 3.2)).set_stroke(C_AXIS, 2) for u in E]), "cuts")
        self.show(axis_(), ticks(), hill(), bars(edges=EC, pick="mid"), cuts(EC), plq, c="куски разной ширины")
        picks = ["right", "left", "mid", "right", "left"]
        b3 = bars(edges=EC, pick=picks)
        dots, labs = VGroup(), VGroup()
        for i, (nm, d) in enumerate([("справа", UL), ("слева", UL), ("посередине", UP), ("справа", UR), ("слева", UR)]):
            if i in (0, 4):
                u = _sample_pick(EC, i, picks[i])
                dots.add(dot(pt(u, F(u)), C_BET, 0.1))
                continue
        for i in (1, 2, 3):
            u = _sample_pick(EC, i, picks[i])
            dots.add(dot(pt(u, F(u)), C_BET, 0.1))
        u1, u2, u3 = [_sample_pick(EC, i, picks[i]) for i in (1, 2, 3)]
        labs.add(label("слева", pt(u1, F(u1)), C_BET, 24, on_fill=True, direction=UL, buff=0.15),
                 label("посередине", pt(u2, F(u2)), C_BET, 24, on_fill=True, direction=UP, buff=0.3),
                 label("справа", pt(u3, F(u3)), C_BET, 24, on_fill=True, direction=UR, buff=0.15))
        self.show(axis_(), ticks(), hill(), b3, cuts(EC), dots, labs, plq, c="высота слева, справа, посередине")
        # три маленькие картинки
        cy = 0.7
        ax1, hl1, b1 = _b2_mini(EA, "left", -4.4, cy)
        ax2, hl2, b2 = _b2_mini(EC, "mid", 0.0, cy, tag_main=True)
        ax3, hl3, b3_ = _b2_mini(EB, "right", 4.4, cy)
        s1, s2, s3 = psum(edges=EA, pick="left"), psum(edges=EC, pick="mid"), psum(edges=EB, pick="right")
        l1, l2, l3 = _b2_sum(s1, -4.4, cy - 0.55), _b2_sum(s2, 0, cy - 0.55), _b2_sum(s3, 4.4, cy - 0.55)
        print("A11 coarse sums", s1, s2, s3)
        # тонкие
        T1, T2, T3 = _b2_thin_edges(20, 3), _b2_thin_edges(20, 4), _b2_thin_edges(20, 5)
        _, _, t1 = _b2_mini(T1, "left", -4.4, cy)
        _, _, t2 = _b2_mini(T2, "mid", 0.0, cy)
        _, _, t3 = _b2_mini(T3, "right", 4.4, cy)
        q1, q2, q3 = psum(edges=T1, pick="left"), psum(edges=T2, pick="mid"), psum(edges=T3, pick="right")
        print("A11 thin sums", q1, q2, q3)
        n1, n2, n3 = _b2_sum(q1, -4.4, cy - 0.55), _b2_sum(q2, 0, cy - 0.55), _b2_sum(q3, 4.4, cy - 0.55)
        k5 = tagged(label("5 кусков", [0, cy + 1.45, 0], C_AXIS, 26), "kk")
        k20 = tagged(label("20 кусков", [0, cy + 1.45, 0], C_AXIS, 26), "kk")
        _b2_T(ax1, ax3, hl1, hl3, pre="m")
        _b2_T(b1, b3_, l1, l3, pre="s")
        _b2_T(t1, t3, n1, n3, pre="s")
        _b2_T(l2, n2, pre="s2")
        ax2.tag, hl2.tag, b2.tag = "axis", "hill", "bars"
        t2.tag = "bars"
        self.show(ax1, ax2, ax3, hl1, hl2, hl3, b1, b2, b3_, l1, l2, l3, k5, morph={}, c="суммы чуть разные")
        self.do(lambda: self._thin([(b1, t1), (b2, t2), (b3_, t3), (l1, n1), (l2, n2), (l3, n3), (k5, k20)]))
        tgt = tagged(z(VGroup(RoundedRectangle(width=4.0, height=0.8, corner_radius=0.12).set_stroke(C_SUM, 3).set_fill(C_PLATE, 1),
                              tx("20 = площадь", 38, C_SUM)), "label"), "tgt")
        tgt[1].move_to(tgt[0])
        tgt.move_to([0, -1.7, 0])
        arrows = VGroup(*[Arrow([x, cy - 0.85, 0], [x * 0.35, -1.25, 0], buff=0.05, stroke_width=5).set_color(C_SUM) for x in (-4.4, 0.0, 4.4)])
        self.show(ax1, ax2, ax3, hl1, hl2, hl3, t1, t2, t3, n1, n2, n3, k20, tgt, z(arrows, "dim"), c="число Риман назвал площадью")

    def _thin(self, pairs):
        self.wait(1.2)
        _b2_swap(self, pairs, 1.4)


def _b2_blink(scene):
    """Строка правил сверху мигает: вырастает и возвращается."""
    r = scene._rules
    scene.play(r.animate.scale(1.12), run_time=0.45)
    scene.play(r.animate.scale(1 / 1.12), run_time=0.45)
    scene.play(r.animate.scale(1.12), run_time=0.45)
    scene.play(r.animate.scale(1 / 1.12), run_time=0.45)


def _sample_pick(E, i, pick):
    return {"left": E[i], "mid": (E[i] + E[i + 1]) / 2, "right": E[i + 1]}[pick]


# =============================== A12 · правила счёта ===============================
def _b2_zt(m, k=1.3, center=(0.0, 0.5)):
    about = pt(5, F(5) / 2)
    m.scale(k, about_point=about)
    m.shift(np.array([center[0], center[1], 0.0]) - about)
    return m


def _b2_zp(u, h, k=1.3, center=(0.0, 0.5)):
    about = pt(5, F(5) / 2)
    return np.array([center[0], center[1], 0.0]) + k * (pt(u, h) - about)


class A12(Film):
    def construct(self):
        K, CEN = 1.3, (0.0, 0.5)
        big, b = zoom_bar(4.0, 6.0, "mid", k=K, margin=2.0, center=CEN)
        bx0, bx1 = b.get_left()[0], b.get_right()[0]
        by0, by1 = b.get_bottom()[1], b.get_top()[1]
        top = _b2_zp(5, F(5))
        p1, p2 = _b2_zp(3.0, F(3.0)), np.array([bx0, 0.0, 0.0])
        calls = lambda lit=None: [
            _b2_call(1, (-5.6, 1.9), p1, C_PRICE if lit == 1 else C_NOTE),
            _b2_call(2, (-5.6, -0.3), p2 + UP * 0.0, C_AXIS if lit == 2 else C_NOTE),
            _b2_call(3, (-2.4, 2.75), top + LEFT * 0.1, C_BET if lit == 3 else C_NOTE),
            _b2_call(4, (5.6, 2.2), np.array([bx1, by1 - 0.05, 0.0]), C_ADD if lit == 4 else C_NOTE)]
        self.show(big, *calls(), c="четыре правила")
        self.show(big, *calls(1), label("горка", [-5.6, 1.3, 0], C_PRICE, 26), c="первое: что складываем")
        self.show(big, *calls(2), dim_h(bx0, bx1, by0, "ширина 2", C_AXIS, gap=0.4, size=24), c="второе: ширина куска")
        pts = VGroup(); lns = VGroup(); lb = VGroup()
        for u, nm in [(4.0, "слева"), (5.0, "посередине"), (6.0, "справа")]:
            p = _b2_zp(u, F(u))
            lns.add(DashedLine([p[0], by0, 0], p).set_stroke(WHITE, 2))
            pts.add(dot(p, WHITE, 0.1))
            lb.add(label(nm, [p[0], by0 - 0.5, 0], WHITE, 22))
        self.show(big, *calls(3), z(lns, "dim"), pts, lb, c="третье: где высота")
        nb = _b2_zt(bar(6, 8, "mid"))
        plus = label("+", [bx1 + 0.0, 0.5, 0], C_ADD, 54, on_fill=True)
        a1 = label(num(2 * F(5), 1), [0, 0.5, 0], C_TEXT, 30, on_fill=True)
        a2 = label(num(2 * F(7), 2), [nb.get_center()[0], 0.5, 0], C_TEXT, 30, on_fill=True)
        self.show(big, nb, *calls(4), a1, a2, plus, c="четвёртое: как складываем")
        # двое режут по-разному
        EL = _b2_thin_edges(12, 11)
        ER = _b2_thin_edges(16, 12)
        cy = 0.3
        A = _b2_mini(EL, "mid", -3.4, cy, 0.5)
        B = _b2_mini(ER, "right", 3.4, cy, 0.5)
        sa, sb = psum(edges=EL, pick="mid"), psum(edges=ER, pick="right")
        print("A12 sums", sa, sb)
        la, lbb = _b2_sum(sa, -3.4, cy - 0.65, 1, 34, "≈ "), _b2_sum(sb, 3.4, cy - 0.65, 1, 34, "≈ ")
        eq = label("=", [0, cy + 0.7, 0], C_SUM, 90)
        pair = [*A, *B, la, lbb, eq]
        _b2_T(*pair, pre="pr")
        self.show(*pair, c="двое режут по-разному")
        self.show(*pair, c="правила в строку сверху")
        self.do(lambda: _b2_blink(self))


# =============================== A13 · Стилтьес ===============================
B13 = -0.35
WB, WS = -2.2, 0.95
_WL = [(0, 0), (1.5, .06), (3.5, .40), (5, .60), (7, .64)]
_WR = [(7, .97), (10, 1.0)]


def _b2_w(u):
    pts = _WL if u < 7 else _WR
    return float(np.interp(u, [p[0] for p in pts], [p[1] for p in pts]))


def _b2_wy(u):
    return WB + _b2_w(u) * WS


E13 = [0, 1.5, 3.5, 5, 6, 8, 10]


def _b2_wcurve():
    pts = [pt(u, 0, 0)[:2] for u, _ in _WL]
    P = [np.array([X(u), WB + w * WS, 0.0]) for u, w in _WL + _WR]
    return tagged(z(poly_line(P, C_AXIS, 6), "graph"), "wline")


class A13(Film):
    def construct(self):
        base = lambda: (axis_(base=B13), ticks(base=B13, labels=()), hill(base=B13))
        jb = 4   # кусок [6, 8] со скачком
        self.show(*base(), bars(edges=E13, base=B13), tagged(plaque("1894", "Стилтьес", y=2.85), "pl"), c="Стилтьес поменял ширину")
        wax = tagged(z(line([X(-0.6), WB, 0], [X(10.6), WB, 0], C_NOTE, 2), "axis"), "wax")
        wl = _b2_wcurve()
        wlab = tagged(label("вес", [-5.95, WB + 0.6, 0], C_AXIS, 28), "wlab")
        cuts = tagged(z(VGroup(*[DashedLine([X(u), _b2_wy(u) + 0.0, 0], pt(u, F(u), B13)).set_stroke(C_AXIS, 2) for u in E13]), "dim"), "cuts")
        bs = lambda hi=None: self._bars(hi)
        pl = tagged(plaque("1894", "Стилтьес", y=2.85), "pl")
        self.show(*base(), bs(), cuts, wax, wl, wlab, pl, how={"wline": "create"}, c="ширина — прирост веса")
        fast = label("быстро", [X(2.5), -1.45, 0], C_AXIS, 24)
        slow = label("почти стоит", [X(5.5), -2.0, 0], C_AXIS, 22)
        self.show(*base(), bs(), cuts, wax, wl, wlab, fast, slow, pl, c="вес растёт неровно")
        d_j = _b2_w(8) - _b2_w(6)
        jump_lab = label("скачок", [X(7) - 1.05, WB + 0.62 * 1.0 + 0.55, 0], C_AXIS, 26)
        dj = dim_v(X(7), _b2_wy(6.99), _b2_wy(7.01) + 0.0, "", C_AXIS, LEFT, gap=0.6, size=20)
        self.show(*base(), bs(jb), cuts, wax, wl, wlab, jump_lab, pl, c="скачок — широкий столбик")
        dlt = _b2_w(8) - _b2_w(6)
        h = F(7)
        pr1 = label(f"{num(h, 1)} × {num(dlt, 2)}", [X(7), B13 + h / 2 + 0.2, 0], C_TEXT, 24, on_fill=True)
        pr2 = label(f"= {num(h * dlt, 1)}", [X(7), B13 + h / 2 - 0.35, 0], C_SUM, 28, on_fill=True)
        self.show(*base(), bs(jb), cuts, wax, wl, wlab, pr1, pr2, pl, c="высота × прирост веса")

    def _bars(self, hi=None):
        g = bars(edges=E13, base=B13)
        if hi is not None:
            for i, r in enumerate(g):
                if i != hi:
                    r.set_fill(C_BET, 0.3).set_stroke(C_BET, 1.5, 0.5)
        return g


# =============================== A14 · прыгающий график ===============================
class A14(Film):
    def construct(self):
        dots, blues, whites = _b2_dots()
        oz = one_zero().shift(LEFT * 0.25)
        self.show(axis_(), ticks(), dots, morph={"hill": "dots"}, c="график совсем не гладкий")
        fr = VGroup(label("½", pt(5, 2.0) + UP * 0.42, C_PRICE, 28), label("⅓", pt(10 / 3, 2.0) + UP * 0.42, C_PRICE, 28),
                    label("¼", pt(2.5, 2.0) + UP * 0.42, C_PRICE, 28))
        self.show(axis_(), ticks(), dots, oz, fr, c="единица в точках-дробях")
        # увеличение
        sx, py, cxA, cxB = 4.33, 1.4, -3.2, 3.2
        r = lambda cx: z(Rectangle(width=5.2, height=2.0).set_stroke(C_NOTE, 2).set_fill(opacity=0).move_to([cx, 2.05, 0]), "ui")

        def zoom_panel(cx, u0, u1, sc):
            g = VGroup(z(line([cx - 2.5, py, 0], [cx + 2.5, py, 0], C_AXIS, 5), "axis"))
            for u in blues:
                if u0 <= u <= u1:
                    g.add(dot([cx + (u - (u0 + u1) / 2) * sc, py + 1.1, 0], C_PRICE, 0.13))
            for u in whites:
                if u0 <= u <= u1:
                    g.add(dot([cx + (u - (u0 + u1) / 2) * sc, py, 0], WHITE, 0.13))
            return g
        wA = (4.4, 5.6)
        panA = VGroup(r(cxA), zoom_panel(cxA, *wA, 5.0 / 1.2))
        frm = z(Rectangle(width=1.2, height=2.5).set_stroke(WHITE, 3).set_fill(opacity=0).move_to(pt(5, 0.95)), "ui")
        lk = VGroup(link(frm.get_corner(UL), [cxA + 2.6, 1.05, 0], WHITE, 2), link(frm.get_corner(UR) + UP * 0.0, [cxA - 2.6 + 5.2 * 0 + 5.2, 1.05, 0], WHITE, 2))
        # линии рамки к панели: от верхних углов рамки к нижним углам панели
        lk = VGroup(link(frm.get_corner(UL), [cxA - 2.6, 1.05, 0], WHITE, 2), link(frm.get_corner(UR), [cxA + 2.6, 1.05, 0], WHITE, 2))
        _b2_T(frm, lk, panA, pre="z")
        self.show(axis_(), ticks(), dots, oz, frm, lk, panA, c="в любом кусочке есть и те и другие")
        # ещё крупнее
        u_c = 5.35
        sf = z(Rectangle(width=0.22 * 5.0 / 1.2, height=1.9).set_stroke(WHITE, 3).set_fill(opacity=0).move_to([cxA + (u_c - 5.0) * 5.0 / 1.2, 2.05, 0]), "ui")
        panB = VGroup(r(cxB), zoom_panel(cxB, 5.24, 5.46, 5.0 / 0.22))
        lk2 = VGroup(link(sf.get_corner(UR), [cxB - 2.6, 3.05, 0], WHITE, 2), link(sf.get_corner(DR), [cxB - 2.6, 1.05, 0], WHITE, 2))
        self.show(axis_(), ticks(), dots, oz, frm, lk, panA, sf, lk2, panB, c="ещё крупнее")
        q = label("?", [0, 2.2, 0], C_BAD, 110)
        self.show(axis_(), ticks(), dots, oz, q, c="выдержат ли правила")
        self.do(lambda: _b2_blink(self))


# =============================== A15 · замер ===============================
H1 = 2.0


class A15(Film):
    def construct(self):
        U0, U1 = 4.5, 5.5
        dots, blues, whites = _b2_dots(dim=0.4)
        oz = one_zero().shift(LEFT * 0.25)
        piece = lambda: tagged(z(line(pt(U0), pt(U1), C_AXIS, 14), "axis"), "piece")
        outline = tagged(z(VGroup(DashedLine(pt(U0), pt(U0, H1)).set_stroke(WHITE, 3), DashedLine(pt(U1), pt(U1, H1)).set_stroke(WHITE, 3),
                                  DashedLine(pt(U0, H1), pt(U1, H1)).set_stroke(WHITE, 3)), "dim"), "outline")
        lab_k = label("кусок", pt(5, H1 + 0.45), WHITE, 26)
        self.show(axis_(), ticks(), dots, oz, piece(), outline, lab_k, c="кусок оси и столбик")
        pb, pw = pt(5.0, H1), pt(5.07, 0.0)
        lens_ = tagged(lens(pb), "lens")
        vert = z(DashedLine(pt(5.0), pt(5.0, H1)).set_stroke(C_BET, 3), "dim")
        self.show(axis_(), ticks(), dots, oz, piece(), outline, lens_, vert, label("замер", pb + LEFT * 0.9 + UP * 0.05, C_BET, 28), c="высота в одной точке — замер")
        hi_bar = tagged(bar(U0, U1, "mid", f=lambda u: H1), "bar")
        self.show(axis_(), ticks(), dots, oz, piece(), hi_bar, lens_, c="попали в единицу — высокий")
        self.do(lambda: self._flip(lens_, hi_bar, pb, pw, U0, U1))
        # два столбика на одном куске
        ax = line([-3.3, -1.0, 0], [3.3, -1.0, 0], C_AXIS, 6)
        tall = z(Rectangle(width=1.8, height=2.2).set_stroke(C_BET, 2).set_fill(C_BET, 0.85).move_to([-1.3, -1.0 + 1.1, 0]), "bar")
        flat = z(Rectangle(width=1.8, height=0.04).set_stroke(C_BET, 2).set_fill(C_BET, 0.85).move_to([1.3, -1.0 + 0.02, 0]), "bar")
        d1, d0 = dot([-1.3, 1.2, 0], C_PRICE, 0.13), dot([1.3, -1.0, 0], WHITE, 0.13)
        l1, l0 = label("1", [-1.3, 1.65, 0], C_BET, 34), label("0", [1.3, -0.45, 0], C_BET, 34)
        neq = label("≠", [0, 0.7, 0], C_BAD, 100)
        dh = dim_h(-2.2, 2.2, -1.0, "один кусок", C_AXIS, gap=0.4, size=24)
        self.show(z(ax, "axis"), tall, flat, d1, d0, l1, l0, neq, dh, c="кусок тот же, столбики разные")
        # два счётчика
        fa = lambda u: H1
        fz = lambda u: 0.0
        cy = 0.2
        PA = _b2_mini_f(fa, -3.4, cy)
        PZ = _b2_mini_f(fz, 3.4, cy)
        sa, sz = psum(10, f=lambda u: fa(u) / H1), psum(10, f=lambda u: fz(u) / H1)
        ca = _b2_sum(sa, -3.4, cy - 0.65, 0, 34, "сумма ")
        cz = _b2_sum(sz, 3.4, cy - 0.65, 0, 34, "сумма ")
        neq2 = label("≠", [0, cy + 0.6, 0], C_BAD, 100)
        _b2_T(*PA, *PZ, ca, cz, neq2, pre="q")
        self.show(*PA, *PZ, ca, cz, neq2, c="двое считают — разное")
        cross_p = plaque("1854", "Риман").scale(1.3).move_to([0, 2.3, 0])
        cr = z(VGroup(line(cross_p.get_corner(DL) + np.array([-0.1, -0.1, 0]), cross_p.get_corner(UR) + np.array([0.1, 0.1, 0]), C_BAD, 8),
                      line(cross_p.get_corner(UL) + np.array([-0.1, 0.1, 0]), cross_p.get_corner(DR) + np.array([0.1, -0.1, 0]), C_BAD, 8)), "ui")
        self.show(*PA, *PZ, ca, cz, neq2, cross_p, cr, c="способ Римана не работает")

    def _flip(self, lens_, hi_bar, pb, pw, U0, U1):
        self.wait(1.0)
        flat = tagged(bar(U0, U1, "mid", f=lambda u: 0.0), "bar")
        self.play(lens_.animate.shift(pw - pb), ReplacementTransform(hi_bar, flat), run_time=1.6, rate_func=smooth)
        self._cur = [flat if m is hi_bar else m for m in self._cur]


def _b2_mini_f(f, cx, cy, s=0.45):
    ax = _b2_place(axis_(w=3, u0=-0.3, u1=10.3, tag="ax_m"), s, cx, cy)
    bs = _b2_place(bars(10, f=f, tag="bars_m"), s, cx, cy)
    bs.set_stroke(width=1.2)
    return ax, bs


# =============================== блок B3 ===============================
# ---------------------------------- помощники ----------------------------------
def _L(text, at, *a, **k):
    at = np.array(list(at) + [0.0] * (3 - len(at)), dtype=float)
    return label(text, at, *a, **k)


def _b3_swap(self, news, rt=1.2):
    """Превращение объектов текущего кадра в новые с теми же метками (внутри кадра, своей анимацией)."""
    cur, anims = list(self._cur), []
    for new in news:
        for i, o in enumerate(cur):
            if getattr(o, "tag", None) == new.tag:
                anims.append(ReplacementTransform(o, new))
                cur[i] = new
                break
    self.play(*anims, run_time=rt)
    self._cur = cur


def _b3_steps(n):
    """Ступени «снизу»: высота куска — у края, дальнего от середины горки (там горка ниже). Возвращает (рёбра, высоты)."""
    e = np.linspace(0, 10, n + 1)
    return e, [min(F(e[i]), F(e[i + 1])) for i in range(n)]


def _b3_area(n):
    e, h = _b3_steps(n)
    return sum(h[i] * (e[i + 1] - e[i]) for i in range(n))


def _b3_mini(cx, n, base=0.2, kx=0.37, ky=0.5, htag=None, atag=None, steps=True):
    """Маленькая картинка: горка, ось и ступенчатый график снизу."""
    X_ = lambda u: cx + (u - 5) * kx
    hl = poly_line([[X_(u), base + F(u) * ky, 0] for u in np.linspace(0, 10, 80)], C_PRICE, 4)
    ax = line([X_(0) - 0.25, base, 0], [X_(10) + 0.25, base, 0], C_AXIS, 4)
    z(hl, "graph"), z(ax, "axis")
    if htag:
        tagged(hl, htag)
    if atag:
        tagged(ax, atag)
    g = VGroup(hl, ax)
    if steps:
        e, h = _b3_steps(n)
        bs = VGroup()
        for i in range(n):
            hh = max(h[i] * ky, 0.02)
            r = Rectangle(width=(e[i + 1] - e[i]) * kx * 0.96, height=hh).set_stroke(C_BET, 1.5).set_fill(C_BET, 0.55)
            r.move_to([X_((e[i] + e[i + 1]) / 2), base + hh / 2, 0])
            bs.add(z(r, "bar"))
        g.add(tagged(bs, f"st{n}"))
    return g


def _b3_check(p, color=C_SUM, w=7):
    return z(poly_line([p + np.array(d) for d in [(-0.25, 0.0, 0), (-0.07, -0.2, 0), (0.28, 0.3, 0)]], color, w), "label")


def _b3_cross(p, color=C_BAD, w=7):
    a = 0.22
    return z(VGroup(line(p + np.array([-a, -a, 0]), p + np.array([a, a, 0]), color, w), line(p + np.array([-a, a, 0]), p + np.array([a, -a, 0]), color, w)), "label")


def _b3_wig(x0, x1, yc, amp, n, seed, color=C_NOISE, w=4, tag=None):
    rng = np.random.default_rng(seed)
    b = np.cumsum(rng.normal(0, 1, n))
    ys = yc + (b - (b.max() + b.min()) / 2) * (2 * amp / (b.max() - b.min()))
    m = z(poly_line([[x, y, 0] for x, y in zip(np.linspace(x0, x1, n), ys)], color, w), "graph")
    return tagged(m, tag) if tag else m


def _b3_rect(x0, x1, y0, y1, color=WHITE, w=3):
    return z(Rectangle(width=x1 - x0, height=y1 - y0).set_stroke(color, w).set_fill(opacity=0).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0]), "dim")


# ---------------------------------- A18 ----------------------------------
class A18(Film):
    def construct(self):
        cxs = (-4.5, 0.0, 4.5)
        ns = (3, 6, 12)
        areas = [_b3_area(n) for n in ns]
        self.show(hill(), axis_(), ticks(), pill("слои Лебега", C_SUM, 30).move_to([0, 2.6, 0]), c="ещё одно достоинство слоёв")

        def minis(with_steps=True):
            return [_b3_mini(c, n, htag="hill" if c == 0 else None, atag="axis" if c == 0 else None, steps=with_steps) for c, n in zip(cxs, ns)]

        def counts():
            return [tagged(_L(f"{n} ступ.", [c, -0.45], C_TEXT, 24), f"cnt{n}") for c, n in zip(cxs, ns)]

        self.show(*minis(), *counts(), c="ступеньки всё точнее повторяют горку", how={"st3": "grow", "st6": "grow", "st12": "grow"})
        nums = [tagged(_L(num(a, 1), [c, -1.15], C_SUM, 36), f"ar{n}") for c, n, a in zip(cxs, ns, areas)]
        goal = _L("горка: 20", [0, 2.5, 0], C_PRICE, 34)
        self.show(*minis(), *counts(), *nums, goal, c="площади растут к 20")

        def card(cx, good):
            if good:
                hl = poly_line([[cx + (u - 5) * 0.4, 0.3 + F(u) * 0.5, 0] for u in np.linspace(0, 10, 80)], C_PRICE, 4)
                g = VGroup(*[z(Rectangle(width=2 * np.sqrt(25 * (1 - 0.25 * j)) * 0.4, height=0.375).set_stroke(C_SUM, 1.5).set_fill(C_SUM, 0.5)
                                .move_to([cx, 0.3 + 0.375 * (j - 0.5) * 1.0 + 0.0, 0]), "bar") for j in (1, 2, 3)])
                # слои по 0,75 по высоте горки: вдвое меньше масштаб по y (ky = 0.5) → толщина 0.375
            else:
                hl = poly_line([[cx + (u - 5) * 0.4, 0.3 + F(u) * 0.5, 0] for u in np.linspace(0, 10, 80)], C_PRICE, 4)
                e = np.linspace(0, 10, 7)
                g = VGroup(*[z(Rectangle(width=(e[i + 1] - e[i]) * 0.4 * 0.96, height=max(F((e[i] + e[i + 1]) / 2) * 0.5, 0.02)).set_stroke(C_BET, 1.5).set_fill(C_BET, 0.55)
                                .move_to([cx + ((e[i] + e[i + 1]) / 2 - 5) * 0.4, 0.3 + F((e[i] + e[i + 1]) / 2) * 0.25, 0]), "bar") for i in range(6)])
            ax = z(line([cx - 2.25, 0.3, 0], [cx + 2.25, 0.3, 0], C_AXIS, 4), "axis")
            return VGroup(z(hl, "graph"), ax, g)

        self.show(card(-3.4, True), card(3.4, False), _L("слои — всегда работают", [-3.4, 1.9, 0], C_SUM, 28),
                  _L("столбики — бывают сбои", [3.4, 1.9, 0], C_BAD, 28), _b3_check(np.array([-3.4, -0.5, 0])), _b3_cross(np.array([3.4, -0.5, 0])),
                  c="у слоёв сбоев не бывает")
        xs = np.linspace(-1.2, 1.2, 80)
        wave = z(poly_line([[-3.5 + x, 0.95 + 0.5 * np.sin(x * 2.6), 0] for x in xs], C_PRICE, 5), "graph")
        bell = z(poly_line([[3.5 + x, 0.35 + 1.3 * np.exp(-(x * 1.3) ** 2 / 0.9), 0] for x in xs], C_PRICE, 5), "graph")
        fr = lambda cx: z(RoundedRectangle(width=3.4, height=1.9, corner_radius=0.15).set_stroke(C_NOTE, 2).set_fill(opacity=0).move_to([cx, 0.95, 0]), "dim")
        self.show(fr(-3.5), wave, fr(3.5), bell, _L("разделы математики", [-3.5, -0.45, 0], C_TEXT, 28), _L("теория вероятностей", [3.5, -0.45, 0], C_TEXT, 28),
                  c="на слоях стоят разделы математики")


# ---------------------------------- A19 ----------------------------------
class A19(Film):
    AX = 2.2

    def construct(self):
        A = self.AX
        smooth = tagged(z(poly_line([[X(u), 0.9 + 0.12 * np.sin(u * 1.1), 0] for u in np.linspace(0, 10, 90)], C_NOTE, 5), "graph"), "noise")
        tiny, _, _ = noise(0, 10, 0.9, 0.05, 90, 11, C_NOISE, 5, base=0)
        big, _, _ = noise(0, 10, 0.4, 0.18, 90, 11, C_NOISE, 6, base=0)
        mid, us, ys = noise(0, 10, 0.9, 0.1, 90, 11, C_NOISE, 5, base=0)
        ax, tk = axis_(base=A), ticks(base=A)
        self.show(ax, tk, smooth, tagged(_L("вес", [5.8, 0.9, 0], C_AXIS, 28), "wl"), c="вес — линия под осью")
        self.do(lambda: _b3_swap(self, [tiny], 1.6))
        self.show(ax, tk, big, tagged(_L("шум", [5.8, 0.4, 0], C_NOISE, 32), "wl"), c="шум: дрожит вверх и вниз")
        # крупный план: рамки на маленьком куске, рядом он же крупно
        p1x0, p1x1, p2x0, p2x1, py0, py1 = -6.3, -0.9, 0.9, 6.3, -1.65, 0.05
        panel = lambda x0, x1: z(RoundedRectangle(width=x1 - x0, height=py1 - py0, corner_radius=0.1).set_stroke(C_NOTE, 2).set_fill(opacity=0).move_to([(x0 + x1) / 2, (py0 + py1) / 2, 0]), "dim")
        box1 = _b3_rect(-4.0, -3.0, 0.3, 1.5)
        zoom1 = _b3_wig(-6.1, -1.1, -0.8, 0.5, 220, 3, C_NOISE, 4)
        l1 = VGroup(link([-4.0, 0.3, 0], [p1x0, py1, 0], C_NOTE, 2), link([-3.0, 0.3, 0], [p1x1, py1, 0], C_NOTE, 2))
        self.show(ax, tk, mid, tagged(_L("шум", [5.8, 0.9, 0], C_NOISE, 28), "wl"), box1, l1, panel(p1x0, p1x1), zoom1, c="увеличили — та же дрожь")

        def second():
            self.wait(1.0)
            box2 = _b3_rect(-2.5, -1.6, -1.45, -0.15)
            l2 = VGroup(link([-1.6, -0.15, 0], [p2x0, py1, 0], C_NOTE, 2), link([-1.6, -1.45, 0], [p2x0, py0, 0], C_NOTE, 2))
            zoom2 = _b3_wig(p2x0 + 0.2, p2x1 - 0.2, -0.8, 0.5, 400, 8, C_NOISE, 4)
            objs = [box2, l2, panel(p2x0, p2x1), zoom2]
            self.play(*[FadeIn(o) for o in objs], run_time=1.0)
            self.keep(*objs)

        self.do(second)
        ax2, tk2 = axis_(base=0.3), ticks(base=0.3)
        hgt, _, _ = noise(0, 10, 1.6, 0.1, 90, 23, C_NOISE, 5, base=0)
        wgt, _, _ = noise(0, 10, -0.9, 0.1, 90, 11, C_NOISE, 5, base=0)
        self.show(ax2, tk2, tagged(hgt, "noise_h"), wgt, _L("высота", [5.9, 1.6, 0], C_BET, 26), tagged(_L("вес", [5.7, -0.9, 0], C_AXIS, 26), "wl"),
                  c="одна линия — высота, другая — вес")


# ---------------------------------- A20 ----------------------------------
_B3_PATH = {}


def _b3_path():
    """Плотный путь шума для панелей A20 (121 точка, высоты 0,3…2,1) с заметно разными концами у кусков."""
    if "p" in _B3_PATH:
        return _B3_PATH["p"]
    for seed in range(1, 4000):
        rng = np.random.default_rng(seed)
        b = np.cumsum(rng.normal(0, 1, 121))
        h = 0.3 + 1.8 * (b - b.min()) / (b.max() - b.min())
        d3 = np.abs(np.diff(h[::40]))
        d10 = np.abs(np.diff(h[::12][:11]))
        if d3.min() > 0.35 and d10.mean() > 0.2 and d10.min() > 0.05:
            _B3_PATH["p"] = h
            return h
    raise RuntimeError("нет пути")


def _b3_pairs(nb, wtext, bar_w=3.6, yb=-1.0):
    h = _b3_path()
    xs0 = np.linspace(0, bar_w, 121)
    edges = np.linspace(0, 120, nb + 1).astype(int)
    out = []
    for side, cx, col in (("L", -3.1, C_BAD), ("R", 3.1, C_SUM)):
        ox = cx - bar_w / 2
        out.append(tagged(z(line([ox - 0.2, yb, 0], [ox + bar_w + 0.2, yb, 0], C_AXIS, 4), "axis"), "ax" + side))
        bs = VGroup()
        for i in range(nb):
            hh = h[edges[i]] if side == "L" else h[edges[i + 1]]
            w = bar_w / nb * 0.96
            r = Rectangle(width=w, height=hh).set_stroke(col, 1.5).set_fill(col, 0.5).move_to([ox + (i + 0.5) * bar_w / nb, yb + hh / 2, 0])
            bs.add(z(r, "bar"))
        out.append(tagged(bs, "b" + side))
        out.append(tagged(z(poly_line([[ox + x, yb + y, 0] for x, y in zip(xs0, h)], C_NOISE, 4), "graph"), "pn" + side))
        out.append(tagged(_L("по левому краю" if side == "L" else "по правому краю", [cx, yb - 0.5, 0], col, 24), "cap" + side))
    out.append(tagged(_L(wtext, [0, 1.0, 0], C_TEXT, 24), "wid"))
    return out


class A20(Film):
    def construct(self):
        AYY, xl, xr = -0.5, -2.5, 2.5
        nz, us, ys = noise(0, 10, 1.3, 0.1, 90, 11, C_NOISE, 5, base=0)
        piece = tagged(z(line([xl, AYY, 0], [xr, AYY, 0], C_AXIS, 10), "axis"), "piece")
        axis = axis_(base=AYY, tag="axis")
        base = [axis, piece, nz]
        self.show(*base, _L("где брать высоту?", [0, 2.6, 0], C_BET, 34), _L("кусок", [0, AYY - 0.6, 0], C_AXIS, 26), c="где в куске брать высоту?")
        idx = lambda x: int(round((x + 5) / 10 * 89))
        yl, yr = ys[idx(xl)], ys[idx(xr)]
        mk = lambda x, y, c: [marker([x, AYY, 0], c), link([x, AYY + 0.45, 0], [x, y - 0.05, 0], c, 3)]
        self.show(*base, *mk(xl, yl, C_BAD), *mk(xr, yr, C_SUM), _L("левый край", [xl, AYY - 0.6, 0], C_BAD, 26), _L("правый край", [xr, AYY - 0.6, 0], C_SUM, 26),
                  _L("кусок", [0, AYY - 0.6, 0], C_AXIS, 26) if False else VGroup(), c="у куска два края")

        # гладкая горка: два столбика от левого и правого края
        def smooth_panel(cx, pick, col):
            kx, ky, yb = 0.9, 0.75, -1.0
            Xp = lambda u: cx + (u - 4.5) * kx
            hl = z(poly_line([[Xp(u), yb + F(u) * ky, 0] for u in np.linspace(2.5, 6.5, 60)], C_PRICE, 5), "graph")
            ax_ = z(line([Xp(2.5) - 0.2, yb, 0], [Xp(6.5) + 0.2, yb, 0], C_AXIS, 5), "axis")
            hh = F(3.5 if pick == "L" else 5.5) * ky
            r = z(Rectangle(width=2 * kx * 0.97, height=hh).set_stroke(col, 2).set_fill(col, 0.5).move_to([Xp(4.5), yb + hh / 2, 0]), "bar")
            return VGroup(ax_, r, hl)

        sm = [smooth_panel(-3.1, "L", C_BAD), smooth_panel(3.1, "R", C_SUM), _L("по левому краю", [-3.1, -1.5, 0], C_BAD, 24),
              _L("по правому краю", [3.1, -1.5, 0], C_SUM, 24), _L("≈", [0, 0.2, 0], C_TEXT, 80)]
        self.show(*sm, c="у гладкой горки почти одно и то же")
        wide = _b3_pairs(3, "широкие")
        neq = _L("≠", [0, 0.1, 0], C_BAD, 80)
        self.show(*wide, neq, c="у шума суммы расходятся")
        thin = _b3_pairs(10, "тонкие")
        self.do(lambda: (self.wait(1.2), _b3_swap(self, [t for t in thin if t.tag in ("bL", "bR", "wid")], 1.4)))
        top = pill("правило про высоту — переписать", C_BAD, 26).move_to([0, 2.6, 0])
        self.show(*thin, _L("≠", [0, 0.1, 0], C_BAD, 80), top, c="правило про высоту придётся переписать")


# ---------------------------------- A21 ----------------------------------
class A21(Film):
    def construct(self):
        AYY, xl = -0.8, -2.0
        plq = plaque("1944", "Ито", 4.2, 2.85)
        axis = axis_(base=AYY)
        nz, us, ys = noise(0, 10, 0.7, 0.12, 90, 31, C_NOISE, 5, base=0)
        yn = ys[int(round((xl + 5) / 10 * 89))]
        pin = marker([xl, AYY, 0], C_BAD)
        pinl = link([xl, AYY + 0.45, 0], [xl, yn - 0.05, 0], C_BAD, 3)
        lk = lock([xl, 1.75, 0])
        lab = _L("левый край", [xl, AYY - 0.55, 0], C_BAD, 26)
        self.show(axis, nz, pin, pinl, lk, lab, plq, c="высоту берём на левом краю")
        w = 6.0 - xl
        shade = z(Rectangle(width=w, height=3.4).set_stroke(width=0).set_fill(C_PLATE, 0.82).move_to([xl + w / 2 + 0.03, 0.9, 0]), "dim")
        k = int(round((xl + 5) / 10 * 89))
        pl = tagged(z(poly_line([[X(u), v, 0] for u, v in zip(us[:k + 1], ys[:k + 1])], C_NOISE, 5), "graph"), "noise")
        pr = z(poly_line([[X(u), v, 0] for u, v in zip(us[k:], ys[k:])], C_NOISE, 5), "graph")
        self.show(axis, pl, pr, pin, pinl, lk, lab, plq, shade, _L("будущее не видно", [xl + w / 2, 2.1, 0], C_TEXT, 30, on_fill=True), c="правее края будущее не видно")
        sc = scales().shift(np.array([0, 1.0, 0]))
        self.show(plq, sc, _L("в среднем 0", [0, -0.7, 0], C_SUM, 44), c="сумма честная: в среднем 0")
        kx, ky = 0.6, 1.2
        nz2, us2, ys2 = noise(0, 10, 0.0, 0.25, 70, 5, C_NOISE, 5, base=0)
        y0 = 0.1

        def panel(cx, vals, col, name):
            ln = z(poly_line([[cx + (u - 5) * kx, y0 + v * ky, 0] for u, v in zip(us2, vals)], col, 5), "graph")
            ax_ = z(line([cx - 3.2, y0, 0], [cx + 3.2, y0, 0], C_AXIS, 4), "axis")
            return VGroup(ax_, ln, _L(name, [cx, 2.2, 0], col, 28))

        arr = z(Arrow([-0.3, 0.6, 0], [0.3, 0.6, 0], buff=0, stroke_width=6).set_color(WHITE), "dim")
        self.show(plq, panel(-3.4, ys2, C_NOISE, "шум"), panel(3.4, ys2 ** 2, WHITE, "шум × шум"), arr, c="шум умножили сам на себя")
        n1 = node("обычное правило", -2.6, 0.6, WHITE, 3.8, 28)
        n2 = node("добавка", 2.4, 0.6, C_ADD, 2.6, 30)
        plus = _L("+", [-0.1, 0.6, 0], C_ADD, 48)
        wig = _b3_wig(1.4, 3.4, -0.7, 0.18, 40, 17, C_NOISE, 4)
        up = z(Arrow([2.4, -0.35, 0], [2.4, 0.22, 0], buff=0, stroke_width=5).set_color(C_NOISE), "dim")
        self.show(plq, n1, plus, n2, wig, up, _L("от дрожи шума", [2.4, -1.3, 0], C_NOISE, 28), c="остальное добавляет дрожь шума")


# ---------------------------------- A22 ----------------------------------
def _b3_edges1(k=8):
    u = np.linspace(0, 10, 400)
    w = 0.3 + np.abs(0.12 * (10 - 2 * u))
    s = np.concatenate([[0], np.cumsum((w[1:] + w[:-1]) / 2 * np.diff(u))])
    return np.interp(np.linspace(0, s[-1], k + 1), s, u)


def _b3_cuts(edges, tag="cuts"):
    g = VGroup(*[DashedLine(pt(e, 0.03), pt(e, F(e) - 0.03), dash_length=0.12).set_stroke(C_AXIS, 2.5) for e in edges if 0.01 < e < 9.99])
    return tagged(z(g, "dim"), tag)


class A22(Film):
    def construct(self):
        e0, e1 = np.linspace(0, 10, 9), _b3_edges1(8)
        plq = plaque("1957–61", "Курцвейль и Хенсток", 3.4, 2.85)
        base = lambda: [hill(), axis_(), ticks(), plq]
        self.show(*base(), _b3_cuts(e0), c="сначала куски равные")
        self.show(*base(), _b3_cuts(e0), c="куски подгоняем под график")

        def move():
            t = ValueTracker(0.0)
            live = always_redraw(lambda: _b3_cuts((1 - t.get_value()) * e0 + t.get_value() * e1))
            old = [m for m in self._cur if getattr(m, "tag", None) == "cuts"][0]
            self.remove(old)
            self.add(live)
            self.wait(0.3)
            self.play(t.animate.set_value(1.0), run_time=3.0, rate_func=smooth)
            live.clear_updaters()
            fin = _b3_cuts(e1)
            self.remove(live)
            self.add(fin)
            self._cur = [fin if m is old else m for m in self._cur]

        self.do(move)
        self.show(*base(), _b3_cuts(e1), _L("круто — уже", [-4.3, 1.8, 0], C_TEXT, 28), _L("полого — шире", [-1.2, 2.2, 0], C_TEXT, 28),
                  c="круто — куски уже, полого — шире")


# =============================== блок B4 ===============================
# ---------- помощники B4 ----------
def _b4_ov(m):
    m.overlay = True
    return m


def _b4_t(m, name):
    return tagged(m, name)


def _b4_at(us, ys, u):
    return float(np.interp(u, us, ys))


def _b4_strike(lab_m, color=C_BAD):
    x0, y0, _ = lab_m.get_corner(DL)
    x1, y1, _ = lab_m.get_corner(UR)
    return _b4_ov(z(VGroup(line([x0, y0, 0], [x1, y1, 0], color, 4), line([x0, y1, 0], [x1, y0, 0], color, 4)), "ui"))


def _b4_star(r=0.2, color=C_PLATE):
    pts = []
    for i in range(10):
        a = PI / 2 + i * PI / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append([rr * np.cos(a), rr * np.sin(a), 0])
    return Polygon(*pts).set_stroke(width=0).set_fill(color, 1)


def _b4_medal(p):
    c = Circle(radius=0.34).set_stroke(WHITE, 3).set_fill(C_BET, 1).move_to(p)
    s = _b4_star(0.22).move_to(np.array(p) + DOWN * 0.01)
    return z(VGroup(c, s), "ui")


def _b4_pieceline(u0, u1):
    return _b4_t(z(line(pt(u0), pt(u1), C_AXIS, 10), "axis"), "piece")


def _b4_dashes(us, ys, ulist, top=None):
    g = VGroup(*[link(pt(u), pt(u, _b4_at(us, ys, u) - 0.08), C_AXIS, 2) for u in ulist])
    return _b4_t(_b4_ov(g), "pcl")


# =============================== A23: середина куска ===============================
def _b4_n23():
    return noise(y=1.4, amp=0.28, n=90, seed=11)


class A23(Film):
    def construct(self):
        ln, us, ys = _b4_n23()
        mk = lambda: _b4_n23()[0]
        y3, y5 = _b4_at(us, ys, 3), _b4_at(us, ys, 5)
        base = lambda: (axis_(), ticks(), mk())
        pc = lambda: (_b4_pieceline(3, 7), _b4_dashes(us, ys, [3, 7]))
        # 1: левый край неудобен
        lab1 = _b4_t(label("левый край", [X(3), 2.0, 0], C_BET, 24, on_fill=True), "lab1")
        l1 = _b4_t(link([X(3), 1.75, 0], pt(3, y3), C_BET, 2), "l1")
        self.show(*base(), *pc(), _b4_t(dot(pt(3, y3), C_BET, 0.13), "mk"), lab1, l1, c="физикам нужны школьные правила")
        # 2: метка переезжает на середину
        d = _b4_t(dot(pt(3, y3), C_BET, 0.13), "mk")
        self.show(*base(), *pc(), d, _b4_t(plaque("1963–66", "Фиск и Стратонович", 3.3, 2.75), "plq"), c="Стратонович взял середину")
        self.do(lambda: self.play(d.animate.move_to(pt(5, y5)), run_time=1.6))
        # 3: школьное правило, добавки нет
        lab3 = _b4_t(label("школьное правило, добавки нет", [0.5, 2.0, 0], C_TEXT, 24, on_fill=True), "lab3")
        ok = _b4_t(z(check(C_SUM, 0.22).move_to([lab3.get_left()[0] - 0.4, 2.0, 0]), "ui"), "ok")
        l3 = _b4_t(link([0, 1.75, 0], pt(5, y5), C_BET, 2), "l1")
        self.show(*base(), *pc(), _b4_t(dot(pt(5, y5), C_BET, 0.13), "mk"), lab3, ok, l3, _b4_t(plaque("1963–66", "Фиск и Стратонович", 3.3, 2.75), "plq"),
                  c="середина: добавки нет")
        # 4: две суммы и добавка
        pI = _b4_t(pill("сумма Ито", C_NOISE, 26).move_to([-3.6, 1.9, 0]), "pI")
        pS = _b4_t(pill("сумма Стратоновича", C_BET, 26).move_to([3.3, 1.9, 0]), "pS")
        ar = _b4_t(z(Arrow([pS.get_left()[0] - 0.1, 1.9, 0], [pI.get_right()[0] + 0.1, 1.9, 0], buff=0, stroke_width=5).set_color(WHITE), "ui"), "ar")
        al = _b4_t(label("+ добавка", [(pS.get_left()[0] + pI.get_right()[0]) / 2, 2.35, 0], C_ADD, 26), "al")
        self.show(*base(), *pc(), _b4_t(dot(pt(5, y5), C_BET, 0.13), "mk"), pI, pS, ar, al, c="добавка возвращается")
        # 5: обе плашки — на одну линию шума
        lI = _b4_t(link(pI.get_bottom(), pt(5, y5) + UP * 0.12 + LEFT * 0.08, C_NOISE, 3), "lI")
        lS = _b4_t(link(pS.get_bottom(), pt(5, y5) + UP * 0.12 + RIGHT * 0.08, C_BET, 3), "lS")
        self.show(*base(), *pc(), _b4_t(dot(pt(5, y5), C_BET, 0.13), "mk"), pI, pS, ar, al, lI, lS, c="одна и та же линия шума")


# =============================== A24: грубый шум ===============================
def _b4_n24():
    return noise(y=1.55, amp=0.33, n=220, seed=11)


class A24(Film):
    def construct(self):
        ln, us, ys = _b4_n24()
        mk = lambda: _b4_n24()[0]
        base = lambda: (axis_(), ticks(), mk())
        self.show(*base(), c="грубее")
        # 2: перечёркнутые метки
        lL = _b4_t(label("левый край", [X(3), 2.0, 0], C_BET, 24, on_fill=True), "lL")
        lM = _b4_t(label("середина", [X(5), 2.0, 0], C_BET, 24, on_fill=True), "lM")
        links = _b4_t(_b4_ov(VGroup(link([X(3), 1.75, 0], pt(3, _b4_at(us, ys, 3)), C_BET, 2), link([X(5), 1.75, 0], pt(5, _b4_at(us, ys, 5)), C_BET, 2))), "ll")
        dots = _b4_t(VGroup(dot(pt(3, _b4_at(us, ys, 3)), C_BET, 0.13), dot(pt(5, _b4_at(us, ys, 5)), C_BET, 0.13)), "dd")
        self.show(*base(), lL, lM, links, dots, _b4_t(_b4_ov(VGroup(_b4_strike(lL), _b4_strike(lM))), "st"), c="надёжной суммы нет")
        # 3: подсказка Лайонса
        seg = _b4_t(z(poly_line([pt(u, v) for u, v in zip(us, ys) if 4.5 <= u <= 5.5], WHITE, 8), "graph"), "seg")
        sp = _b4_t(spiral([X(5), 2.1, 0]), "sp")
        ls = _b4_t(link([X(5), 1.5, 0], pt(5, _b4_at(us, ys, 5)), C_ADD, 3), "ls")
        lb = _b4_t(label("подсказка", [X(5) - 1.7, 2.1, 0], C_ADD, 26), "lb")
        self.show(*base(), seg, sp, ls, lb, _b4_t(plaque("1998", "Лайонс", 4.2, 2.75), "plq"), c="как шум закручивается")
        # 4: у линии число
        e = _b4_at(us, ys, 10)
        pn = _b4_t(pill("сумма есть", C_SUM, 26).move_to([4.2, 2.0, 0]), "pn")
        ln_ = _b4_t(link([4.9, 1.7, 0], pt(10, e), C_SUM, 3), "ln")
        ed = _b4_t(dot(pt(10, e), C_SUM, 0.13), "ed")
        self.show(*base(), pn, ln_, ed, c="сумма есть для каждой линии")
        # 5: Хайрер и премия
        self.show(*base(), pn, ln_, ed, _b4_t(plaque("2014", "Хайрер", -3.4, 2.75), "plq"), _b4_t(_b4_medal([-1.1, 2.75, 0]), "medal"))


# =============================== A25: четыре тропинки ===============================
_B4_X = [-5.1, -1.7, 1.7, 5.1]
_B4_CY = -0.2
_B4_NAMES = ["Маркус", "Скороход, Маллявэн", "Конт, Фурнье", "Бихтелер, Деллашери"]


def _b4_frame(i):
    r = RoundedRectangle(width=3.0, height=2.2, corner_radius=0.12).set_stroke(C_NOTE, 2).set_fill(opacity=0).move_to([_B4_X[i], _B4_CY, 0])
    return _b4_t(z(r, "fill"), f"fr{i}")


def _b4_walk(n, seed, x0, x1, y0, amp):
    rng = np.random.default_rng(seed)
    b = np.cumsum(rng.normal(0, 1, n))
    b = (b - b.min()) / (b.max() - b.min()) - 0.5
    return [np.array([x, y0 + amp * v, 0.0]) for x, v in zip(np.linspace(x0, x1, n), b)]


def _b4_panel(i):
    cx, cy = _B4_X[i], _B4_CY
    c = np.array([cx, cy, 0.0])
    g = VGroup()
    if i == 0:
        g.add(poly_line([c + [-1.3, -0.5, 0], c + [-0.7, -0.5, 0], c + [-0.7, 0.45, 0], c + [-0.35, 0.45, 0]], C_NOISE, 5))
        g.add(z(Arrow(c + [-0.2, 0, 0], c + [0.2, 0, 0], buff=0, stroke_width=4).set_color(WHITE), "ui"))
        xs = np.linspace(0.3, 1.3, 30)
        g.add(poly_line([c + [x, -0.5 + 0.95 / (1 + np.exp(-(x - 0.8) * 9)), 0] for x in xs], C_NOISE, 5))
    elif i == 1:
        b = Rectangle(width=0.45, height=0.8).set_stroke(C_BET, 2).set_fill(C_BET, 0.85).move_to(c + [-0.6, 0.1, 0])
        lk = lock(c + [0.6, 0.0, 0], C_SUM)
        arc = lk[1]
        arc.shift(UP * 0.1 + RIGHT * 0.1).rotate(0.7, about_point=arc.get_corner(DR))
        g.add(z(b, "bar"), lk, label("в среднем 0", c + [0, -0.7, 0], C_TEXT, 20))
    elif i == 2:
        pts = _b4_walk(40, 5, cx - 1.3, cx + 1.3, cy + 0.35, 0.7)
        k = 26
        g.add(poly_line(pts, C_NOTE, 3), z(poly_line(pts[:k], C_NOISE, 9), "graph"), dot(pts[k - 1], C_BET, 0.1))
        g.add(z(Rectangle(width=0.3, height=0.5).set_stroke(C_BET, 2).set_fill(C_BET, 0.85).move_to([pts[k - 1][0], cy - 0.55, 0]), "bar"))
    else:
        fr = RoundedRectangle(width=1.3, height=1.2, corner_radius=0.1).set_stroke(C_SUM, 4).set_fill(opacity=0).move_to(c + [-0.65, 0.1, 0])
        g.add(fr, poly_line(_b4_walk(14, 9, cx - 1.15, cx - 0.15, cy + 0.1, 0.5), C_NOISE, 3))
        g.add(z(cross(C_BAD, 0.35).move_to(c + [0.85, 0.1, 0]), "ui"), label("где счёт работает", c + [0, -0.75, 0], C_TEXT, 20))
    return _b4_t(g, f"pn{i}")


def _b4_name(i):
    return _b4_t(label(_B4_NAMES[i], [_B4_X[i], _B4_CY - 1.45, 0], C_TEXT, 20), f"nm{i}")


class A25(Film):
    def construct(self):
        ito = lambda: _b4_t(pill("Ито", C_NOISE, 28).move_to([0, 2.35, 0]), "ito")
        arr = lambda: [_b4_t(z(Arrow([0.25 * _B4_X[i] / 5.1, 2.0, 0], [_B4_X[i], _B4_CY + 1.15, 0], buff=0.05, stroke_width=5).set_color(WHITE), "ui"), f"ar{i}") for i in range(4)]
        frs = lambda: [_b4_frame(i) for i in range(4)]
        self.show(ito(), *arr(), *frs(), c="после Ито — четыре тропинки")
        for k in range(4):
            caps = ["скачок → быстрое плавное движение", None, None, None]
            self.show(ito(), *arr(), *frs(), *[_b4_panel(i) for i in range(k + 1)], *[_b4_name(i) for i in range(k + 1)], c=caps[k])


# =============================== A26: другие меры слоёв ===============================
_B4_PINK = ["#ffd1e8", "#ffa9d3", "#ff7fbd", "#e0489a", "#a82672"]


def _b4_layers():
    g = VGroup()
    h = 0.55
    for k in range(5):
        a, b = k * h, (k + 1) * h
        half = 5 * np.sqrt(1 - b / 3.0)
        r = Rectangle(width=2 * half, height=h).set_stroke(C_PLATE, 2).set_fill(_B4_PINK[k], 1).move_to(pt(5, (a + b) / 2))
        g.add(r)
    return _b4_t(z(g, "bar"), "layers")


def _b4_ruler():
    u = -0.9
    g = VGroup(line(pt(u), pt(u, 3.0), C_ADD, 3))
    for h in [0, 0.2, 0.55, 1.1, 1.9, 3.0]:
        g.add(line(pt(u, h) + LEFT * 0.12, pt(u, h) + RIGHT * 0.12, C_ADD, 3))
    return _b4_t(z(g, "axis"), "ruler")


def _b4_sheaf():
    g = VGroup()
    for k in range(7):
        s = 0.35 + 0.1 * k
        us = np.linspace(0, 10, 100)
        g.add(poly_line([pt(u, F(u) * s + 0.2 * np.sin(0.8 * u + k) * F(u) / 3) for u in us], C_PRICE, 3))
    return _b4_t(z(g, "graph"), "sheaf")


class A26(Film):
    def construct(self):
        base = lambda: (axis_(), ticks())
        self.show(*base(), _b4_layers(), hill(), c="как мерить слои")
        # 2: части и целое
        A = Square(side_length=1.0).set_stroke(WHITE, 2).set_fill(_B4_PINK[1], 1).move_to([-4.6, 0.6, 0])
        B = Circle(radius=0.5).set_stroke(WHITE, 2).set_fill(_B4_PINK[3], 1).move_to([-2.8, 0.6, 0])
        W = RoundedRectangle(width=2.6, height=1.5, corner_radius=0.2).set_stroke(WHITE, 2).set_fill(_B4_PINK[2], 1).move_to([1.8, 0.6, 0])
        fig = _b4_t(z(VGroup(A, B, W), "bar"), "figs")
        txt = (VGroup(label("+", [-3.7, 0.6, 0], WHITE, 56), label("≠", [-0.7, 0.6, 0], C_BAD, 64),
                           label("часть", [-4.6, -0.3, 0], WHITE, 22), label("часть", [-2.8, -0.3, 0], WHITE, 22), label("целое", [1.8, -0.3, 0], WHITE, 22)))
        self.show(_b4_t(VGroup(fig, txt), "pic2"), c="выбор по нескольким признакам")
        self.show(*base(), _b4_layers(), _b4_ruler(), hill(), c="интегралы для выбора (Шоке, Сугено)")
        # 4: куски минус дыры; цели и датчики
        pieces = VGroup(*[Rectangle(width=w, height=h).set_stroke(WHITE, 2).set_fill(_B4_PINK[i + 1], 1).move_to([x, y, 0])
                          for i, (x, y, w, h) in enumerate([(-5.0, 1.0, 1.6, 1.0), (-3.5, 0.6, 1.5, 1.2), (-2.2, 1.0, 1.0, 0.8)])])
        holes = VGroup(*[Circle(radius=0.2).set_stroke(WHITE, 2).set_fill(C_PLATE, 1).move_to([x, y, 0]) for x, y in [(-5.0, 1.0), (-3.5, 0.5), (-3.5, 0.95)]])
        fig4 = _b4_t(z(VGroup(pieces, holes), "bar"), "fig4")
        l4 = _b4_t(label("куски − дыры", [-3.6, -0.3, 0], WHITE, 24), "l4")
        tg = [(2.0, 1.2), (2.5, 0.7), (3.0, 1.4), (3.4, 0.6), (4.8, 1.3), (5.3, 0.8), (5.7, 1.5), (4.3, 0.4)]
        tgd = _b4_t(VGroup(*[dot([x, y, 0], C_BET, 0.1) for x, y in tg]), "tgd")
        sens = _b4_t(z(VGroup(*[Circle(radius=0.8).set_stroke(C_PRICE, 4).set_fill(opacity=0).move_to([x, y, 0]) for x, y in [(2.6, 1.0), (5.2, 1.0)]]), "graph"), "sens")
        l4b = _b4_t(VGroup(label("цели", [2.0, -0.3, 0], C_BET, 24), label("датчики", [4.6, -0.3, 0], C_PRICE, 24)), "l4b")
        self.show(fig4, l4, tgd, sens, l4b, c="цели, которые видят датчики")
        # 5: пучок кривых
        self.show(*base(), _b4_sheaf(), _b4_t(plaque("1995–98", "Концевич; Денеф и Лёзер", 0.0, 2.75), "plq"))


# =============================== A27: другие сложения ===============================
def _b4_card(x, title, kind):
    r = RoundedRectangle(width=3.5, height=2.6, corner_radius=0.15).set_stroke(C_ADD, 3).set_fill(C_PLATE, 1).move_to([x, 0.5, 0])
    g = VGroup(r)
    if kind == 0:
        for i in range(4):
            g.add(Rectangle(width=0.4, height=0.9).set_stroke(C_ADD, 2, opacity=0.3 + 0.23 * i).set_fill(C_ADD, 0.2 + 0.23 * i).move_to([x - 0.9 + 0.6 * i, 0.9, 0]))
    elif kind == 1:
        g.add(tx("×", 90, C_ADD).move_to([x, 0.95, 0]))
    else:
        g.add(line([x - 1.2, 0.9, 0], [x + 1.2, 0.9, 0], C_AXIS, 5), *[dot([x - 1.0 + 0.5 * i, 0.9, 0], C_AXIS, 0.08) for i in range(5)])
    g.add(tx(title, 28, WHITE).move_to([x, -0.2, 0]))
    return z(g, "label")


def _b4_fade(n, u0=0.5):
    g = VGroup()
    for i in range(n):
        op = 0.2 + 0.8 * i / (n - 1)
        r = Rectangle(width=1.0, height=1.6).set_stroke(C_ADD, 2, opacity=op).set_fill(C_ADD, op).move_to(pt(u0 + i * 1.2, 0.8))
        g.add(r)
    return _b4_t(z(g, "bar"), "bars")


class A27(Film):
    def construct(self):
        axis = lambda: axis_()
        cards = _b4_t(VGroup(_b4_card(-4.1, "память", 0), _b4_card(0, "произведение", 1), _b4_card(4.1, "шкала времени", 2)), "cards")
        self.show(cards)
        fade = _b4_fade(8, 0.8)
        old = _b4_t(VGroup(label("давно", pt(1.0, 0) + DOWN * 0.45, WHITE, 24), label("сейчас", pt(9.0, 0) + DOWN * 0.45, WHITE, 24)), "tt")
        self.show(axis(), fade, old, c="недавнее весит больше")
        hs = [1.0, 1.8, 1.3, 2.1, 1.5]
        b3 = _b4_t(z(VGroup(*[Rectangle(width=1.3, height=h).set_stroke(C_ADD, 2).set_fill(C_ADD, 0.85).move_to(pt(1 + 2 * i, h / 2)) for i, h in enumerate(hs)]), "bar"), "bars3")
        times = _b4_t(z(VGroup(*[tx("×", 56, WHITE).move_to(pt(2 + 2 * i, 0.8)) for i in range(4)]), "label"), "times")
        early = _b4_t(VGroup(pill("ещё раньше", WHITE, 24).move_to([-1.5, 2.75, 0]),
                             z(Arrow([-2.9, 2.75, 0], [-4.2, 2.75, 0], buff=0, stroke_width=5).set_color(WHITE), "ui")), "early")
        self.show(axis(), b3, times, early, _b4_t(plaque("1887", "Вольтерра", 4.2, 2.75), "plq"))
        base = -0.2
        seg = _b4_t(z(line(pt(0, 0, base), pt(4.6, 0, base), C_AXIS, 8), "axis"), "seg")
        dts = _b4_t(VGroup(*[dot(pt(5.6 + i, 0, -1.4), C_AXIS, 0.12) for i in range(5)]), "dots")
        lab4 = _b4_t(VGroup(label("плавное время", pt(2.3, 0, base) + UP * 0.45, WHITE, 24), label("время по шагам", pt(7.6, 0, -1.4) + UP * 0.45, WHITE, 24)), "lab4")
        self.show(seg, dts, lab4, _b4_t(plaque("1988", "Хильгер", 4.2, 2.75), "plq"))
        b5 = -0.8
        seg5 = _b4_t(z(line(pt(0, 0, b5), pt(4.6, 0, b5), C_AXIS, 8), "axis"), "seg")
        dts5 = _b4_t(VGroup(*[dot(pt(5.4 + 1.0 * i, 0, b5), C_AXIS, 0.12) for i in range(5)]), "dots")
        self.show(seg5, dts5, label("одна линия", pt(5, 0, b5) + UP * 0.6, WHITE, 28), _b4_t(plaque("1988", "Хильгер", 4.2, 2.75), "plq"))


# =============================== объёмные сцены (закон 26) ===============================
class A16(Film3D):
    """Лебег: горка режется поперёк на слои-этажи; под каждым этажом на оси — его часть оси."""
    END_K, END_CAP = 5, "сложим слои — снова площадь горки"

    def end2d(self):
        return [axis_(), ticks(), hill()]

    def construct(self):
        edge, back, ribs = ridge3()
        ax, grid = axis3()
        N = 6
        hs = np.linspace(0, 3, N + 1)
        half = lambda h: 5.0 * np.sqrt(max(0.0, 1 - h / 3.0))       # горка на высоте h: от 5 − half до 5 + half
        cols = [C_BET, C_AXIS, C_ADD, C_NOISE, C_PRICE, C_SUM]
        slabs = Group(*[slab(5 - half(hs[k]), 5 + half(hs[k]), hs[k], hs[k + 1], cols[k]) for k in range(N)])
        self.phrase(1, "Лебег: начнём с высоты")
        self.enter([edge, back, ax, grid])
        self.add(*self.flat(plaque("1902", "Лебег"), vscale()))
        self.phrase(2, "горку режем поперёк — на этажи")
        self.play(LaggedStart(*[FadeIn(s) for s in slabs], lag_ratio=0.15), self.frame.animate.reorient(-16, 66).move_to([0, 0.9, 1.4]).set_height(10.5), run_time=2.6)
        k = 2
        mark = Line([X(5 - half(hs[k])), -0.15, 0], [X(5 + half(hs[k])), -0.15, 0]).set_stroke(C_AXIS, 16)
        drop = VGroup(*[DashedLine([X(5 + sgn * half(hs[k])), 0, hs[k]], [X(5 + sgn * half(hs[k])), 0, 0]).set_stroke(C_AXIS, 3) for sgn in (-1, 1)])
        self.phrase(3, "под этажом — его часть оси")
        self.play(*[s.animate.set_color(C_NOTE) for i, s in enumerate(slabs) if i != k], ShowCreation(drop), ShowCreation(mark), self.frame.animate.reorient(-26, 62), run_time=2.4)
        w = 2 * half(hs[k])
        self.phrase(4, "площадь слоя: высота × длина части оси")
        self.play(self.frame.animate.reorient(0, 90).move_to(FRONT_CENTER).set_height(8), run_time=1.8)
        b0, b1 = AY + hs[k], AY + hs[k + 1]
        lab = self.flat(dim_h(X(5 - half(hs[k])), X(5 + half(hs[k])), AY, "длина части оси", C_AXIS, gap=0.35),
                        dim_v(X(5 + half(hs[k])), b0, b1, "высота слоя", cols[k], RIGHT, gap=0.5))
        self.play(*[FadeIn(m) for m in lab], run_time=0.8)
        self.phrase(5, "сложим слои — снова площадь горки")
        self.play(*[FadeOut(m) for m in lab], *[s.animate.set_color(cols[i]) for i, s in enumerate(slabs)], self.frame.animate.reorient(-22, 62).move_to([0, 0.9, 1.6]).set_height(10.5), run_time=1.6)
        self.play(*[s.animate.shift(OUT * 0.45 * i) for i, s in enumerate(slabs)], run_time=1.8)
        self.play(*[s.animate.shift(IN * 0.45 * i) for i, s in enumerate(slabs)], run_time=1.4)
        self.add(*self.flat(label("20", [5.4, 1.6, 0], C_SUM, 44)))
        self.leave([slabs, ax, grid, mark, drop, edge, back])


class A17(Film3D):
    """Два слоя прыгающего графика: дроби — на верхней плите, остальные — на нижней; общая длина дробей — ноль."""
    END_K, END_CAP = 6, "требование выполнено"

    def end2d(self):
        d, _, _ = jump()
        return [axis_(), ticks(), d, one_zero()]

    def construct(self):
        ax, grid = axis3()
        _, us, up = jump()
        spheres = Group(*[Sphere(radius=0.13).set_color(C_PRICE if b else WHITE).set_shading(0.1, 0.1, 0.0).move_to([X(u), 0.0, 2.0 if b else 0.0]) for u, b in zip(us, up)])
        self.phrase(1, "слои для прыгающего графика")
        self.enter([ax, grid, spheres])
        top = slab(0, 10, 1.75, 2.0 - 0.13, C_BET)
        bot = slab(0, 10, -0.25, -0.13 + 0.0, C_NOTE)
        self.phrase(2, "слоёв два: на высоте 1 и на высоте 0")
        self.play(FadeIn(top), FadeIn(bot), self.frame.animate.reorient(-18, 64).move_to([0, 0.9, 1.3]).set_height(8.8), run_time=2.4)
        self.phrase(3, "дроби — наверх, остальные — вниз")
        ones = [s for s, b in zip(spheres, up) if b]
        self.play(LaggedStart(*[Indicate(s, scale_factor=1.6, color=C_BET) for s in ones[:12]], lag_ratio=0.08), run_time=2.0)
        self.phrase(4, "дроби выписаны по порядку — общей длины нет")
        row = Group(*[s.copy() for s in ones])
        self.play(*[m.animate.move_to([X(0.5 + 0.38 * i), 0.0, 3.0]) for i, m in enumerate(row)], run_time=1.8)
        zero = self.flat(label("общая длина 0", [0, 2.75, 0], C_AXIS, 30))
        self.add(*zero)
        self.phrase(5, "сумма равна нулю")
        t = VGroup(tx("верхний: 1 × 0 = 0", 28, C_BET), tx("нижний: 0 × 10 = 0", 28, WHITE), tx("сумма 0", 34, C_SUM)).arrange(DOWN, buff=0.18).move_to([0, 2.3, 0])
        self.play(FadeOut(row), *[FadeOut(m) for m in zero], run_time=0.6)
        self.add(*self.flat(VGroup(plate(t), t)))
        self.phrase(6, "у обоих счётчиков ноль: требование выполнено")
        self.play(self.frame.animate.reorient(-8, 72), run_time=1.6)
        self.leave([ax, grid, spheres, top, bot])


class A28(Film3D):
    """Итог: из горки вырастает дерево из четырёх правил; камера разворачивает его в плоский вид."""
    END_K, END_CAP = 5, "какой способ взять, зависит от задачи"

    def end2d(self):
        return [pill("гладкая ширина — Риман", C_BET, 30).move_to([-3.2, 1.0, 0]), pill("случайная — Ито", C_NOISE, 30).move_to([3.2, 1.0, 0]),
                label("а дальше — смотря какая задача", [0, -0.3, 0], C_TEXT, 32)]

    def construct(self):
        edge, back, ribs = ridge3()
        ax, grid = axis3()
        tw = Group(*[tower(e, e + 1, F(e + 0.5)) for e in range(10)])
        q = VGroup(tx("Как найти площадь точно,", 32), tx("чтобы у всех вышло одно и то же число?", 32)).arrange(DOWN, buff=0.12).move_to([0, 2.45, 0])
        self.phrase(1, "вернёмся к вопросу")
        self.enter([edge, back, ax, grid, tw])
        qm = self.flat(VGroup(plate(q), q))
        self.add(*qm)
        self.play(self.frame.animate.reorient(-14, 66).move_to([0, 0.9, 1.4]).set_height(10.0), run_time=2.0)
        top = np.array([0.0, DEP / 2, 3.0])
        tips = [(-4.2, C_PRICE), (-1.4, C_AXIS), (1.4, C_BET), (4.2, C_ADD)]
        trunk = Line(top, top + OUT * 1.0).set_stroke(C_SUM, 18)
        base = top + OUT * 1.0
        branches = Group(*[Line(base, np.array([x, DEP / 2, 6.2])).set_stroke(c, 12) for x, c in tips])
        balls = Group(*[Sphere(radius=0.28).set_color(c).set_shading(0.1, 0.1, 0.0).move_to([x, DEP / 2, 6.2]) for x, c in tips])
        self.phrase(2, "правила меняли по одному — выросло дерево")
        self.play(FadeOut(tw), *[FadeOut(m) for m in qm], ShowCreation(trunk), self.frame.animate.reorient(-20, 70).move_to([0, 1.0, 3.4]).set_height(11), run_time=2.0)
        self.play(LaggedStart(*[ShowCreation(b) for b in branches], lag_ratio=0.2), run_time=1.6)
        self.play(LaggedStart(*[GrowFromCenter(b) for b in balls], lag_ratio=0.2), run_time=1.2)
        self.phrase(3, "график — слои; ширина — вес и шум")
        self.play(self.frame.animate.reorient(0, 90).move_to([0, 0, 3.4]).set_height(11), run_time=2.0)
        k = 8 / 11
        names = ["график: слои", "ширина: вес, шум", "высота: край, середина, подсказка", "сложение: новые меры"]
        ys = [2.85, 1.25, 2.85, 1.25]
        nodes = [node(n, x * k, y, col, 2.4, 20) for n, (x, col), y in zip(names, tips, ys)]
        self.add(*self.flat(*nodes[:2]))
        self.phrase(4, "высота — край, середина, подсказка; сложение — новые меры")
        self.add(*self.flat(*nodes[2:]))
        self.phrase(5, "какой способ взять, зависит от задачи")
        self.play(*[FadeOut(m) for m in nodes], FadeOut(trunk), FadeOut(branches), FadeOut(balls), FadeOut(edge), FadeOut(back), FadeOut(ax), FadeOut(grid), run_time=0.8)
        fin = [self._pin(m) for m in self.end2d()]
        self.play(*[FadeIn(m) for m in fin], run_time=0.8)


# =============================== таблица ===============================
ROWS = [("Риман", "площадь", "площадь, физика", C_BET), ("Стилтьес", "неровная ширина", "физика, вероятность", C_AXIS),
        ("Лебег", "рваный график", "вероятность, анализ", C_BET), ("Ито", "случайная ширина", "финансы, шум", C_NOISE),
        ("Стратонович", "школьные правила", "физика шума", C_NOISE), ("Лайонс", "грубый шум", "сигналы, данные", C_ADD)]


def _table(cols):
    g = VGroup()
    heads = {"name": ("способ", -4.8), "fix": ("что чинил", -0.6), "use": ("где применяют", 3.9)}
    for key in cols:
        h, x = heads[key]
        g.add(tx(h, 24, C_NOTE).move_to([x, 2.9, 0]))
    for i, (nm, fix, use, col) in enumerate(ROWS):
        y = 2.2 - 0.72 * i
        if "name" in cols:
            g.add(tx(nm, 30, col).move_to([-4.8, y, 0]))
        if "fix" in cols:
            g.add(tx(fix, 26, WHITE).move_to([-0.6, y, 0]))
        if "use" in cols:
            g.add(tx(use, 26, C_SUM).move_to([3.9, y, 0]))
    return z(g, "label")


class F01(Film):
    def construct(self):
        self.show(tagged(_table(["name"]), "table"), c="все способы в одной таблице")
        self.show(tagged(_table(["name", "fix"]), "table"), c="какую поломку чинил каждый")
        self.show(tagged(_table(["name", "fix", "use"]), "table"), c="где их применяют сегодня")
