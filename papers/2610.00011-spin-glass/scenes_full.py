"""Подробная версия по статье arXiv 2610.00011 (Tierz): дисперсия свободной энергии модели SK. Сцены S01–S13.
Запуск (из корня репозитория): uv run manimgl papers/2610.00011-spin-glass/scenes_full.py S05 -w --hd"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                  # корень репозитория
sys.path.insert(0, str(ROOT / "core"))  # общая часть: manimkit
sys.path.insert(0, str(HERE))           # своя часть статьи: паспорт, текст, модели
import numpy as np
from manimlib import *
from manimkit import *
from spinglass import *  # модель спинового стекла — своя часть статьи

D = json.load(open(HERE / "data" / "sk_data.json"))


class S01(Base):
    def construct(self):
        t = tx("Дисперсия свободной энергии", 52)
        t2 = tx("в критической точке модели Шеррингтона–Киркпатрика", 30, C_GREY)
        t3 = tx("arXiv 2610.00011 · Tierz", 24, C_BLUE)
        g = VGroup(t, t2, t3).arrange(DOWN, buff=0.35)
        n, pairs = 9, [(i, j) for i in range(9) for j in range(i + 1, 9)]
        rng = np.random.default_rng(3)
        lines, dots = network(rng.standard_normal(len(pairs)), n, pairs, 1.3)
        net = VGroup(lines, dots).next_to(g, UP, buff=0.4)
        VGroup(net, g).move_to(ORIGIN)
        self.play(ShowCreation(lines, lag_ratio=0.02), FadeIn(dots), run_time=2)
        self.play(Write(t), run_time=1.2)
        self.play(FadeIn(t2), FadeIn(t3))
        self.wait(1.5)


class S02(Base):
    def construct(self):
        self.add(title("Модель"))
        n = 8
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        rng = np.random.default_rng(5)
        J = rng.standard_normal(len(pairs))
        lines, dots = network(J, n, pairs, 2.2, LEFT * 3.2 + DOWN * 0.3)
        spins = VGroup()
        for k, p in enumerate(ring(n, 2.2, LEFT * 3.2 + DOWN * 0.3)):
            up = rng.random() > 0.5
            a = Arrow(p + (DOWN if up else UP) * 0.0, p + (UP if up else DOWN) * 0.45, buff=0, stroke_width=4)
            a.set_color(C_BLUE if up else C_YEL)
            a.shift((UP if up else DOWN) * 0.15 + (UP if up else DOWN) * 0.2)
            spins.add(a)
        self.play(FadeIn(dots), run_time=0.6)
        self.play(ShowCreation(lines, lag_ratio=0.03), run_time=2)
        self.play(FadeIn(spins))
        leg = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.6).set_stroke(C_GREEN, 5), tx("тянет к одному", 24)).arrange(RIGHT),
            VGroup(Line(ORIGIN, RIGHT * 0.6).set_stroke(C_RED, 5), tx("тянет к разному", 24)).arrange(RIGHT),
            VGroup(Line(ORIGIN, RIGHT * 0.6).set_stroke(WHITE, 2), tx("толще = сильнее", 24)).arrange(RIGHT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(RIGHT * 3.6 + UP * 1.4)
        self.play(FadeIn(leg))
        S = all_states(n)
        F = free_energy(J, n, S, pairs)
        lab = VGroup(tx("F =", 40), DecimalNumber(F, num_decimal_places=3, font_size=44).set_color(C_YEL)).arrange(RIGHT)
        box = pill("одно число на всю систему", C_BLUE)
        VGroup(lab, box).arrange(DOWN, buff=0.35).move_to(RIGHT * 3.6 + DOWN * 1.6)
        self.play(FadeIn(lab), FadeIn(box))
        self.wait(2)


class S03(Base):
    def construct(self):
        self.add(title("Разброс F"))
        n = 8
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        S = all_states(n)
        rng = np.random.default_rng(9)
        shown = []
        for k in range(3):
            J = rng.standard_normal(len(pairs))
            lines, dots = network(J, n, pairs, 0.8, LEFT * 5.0 + UP * (2.0 - 2.2 * k), 0.8)
            F = free_energy(J, n, S, pairs)
            lab = VGroup(tx("F =", 26), DecimalNumber(F, num_decimal_places=3, font_size=30).set_color(C_YEL)).arrange(RIGHT)
            lab.next_to(dots, RIGHT, buff=0.7)
            shown.append(VGroup(lines, dots, lab))
        for s in shown:
            self.play(FadeIn(s), run_time=0.9)
        note = pill("силы выбраны заново → F другое", C_GREEN, 24).move_to(LEFT * 3.0 + DOWN * 3.65)
        self.play(FadeIn(note))
        self.wait(0.5)
        # гистограмма по реальным 4000 выборкам
        F = np.array(D["F"])
        x0, x1, ybase, hmax = 0.5, 6.5, -2.4, 3.2   # экран: x от 0.5 до 6.5
        base = Line([x0, ybase, 0], [x1, ybase, 0]).set_stroke(C_GREY, 3)
        self.play(ShowCreation(base))
        lo, hi = 0.7, 1.1
        sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
        bins = np.linspace(lo, hi, 31)
        h, _ = np.histogram(F, bins=bins)
        h = h / h.max()
        bars = VGroup()
        for i in range(30):
            if h[i] > 0:
                w = sx(bins[i + 1]) - sx(bins[i]) - 0.03
                r = Rectangle(width=w, height=h[i] * hmax).set_stroke(width=0).set_fill(C_BLUE, 0.85)
                r.move_to([(sx(bins[i]) + sx(bins[i + 1])) / 2, ybase + h[i] * hmax / 2, 0])
                bars.add(r)
        self.play(LaggedStart(*[GrowFromPoint(b, b.get_bottom()) for b in bars], lag_ratio=0.03), run_time=2.2)
        m, s = F.mean(), F.std()
        brace = Line([sx(m - s), ybase + hmax + 0.35, 0], [sx(m + s), ybase + hmax + 0.35, 0]).set_stroke(C_YEL, 5)
        lab = tx("разброс", 28, C_YEL).next_to(brace, UP, buff=0.12)
        self.play(ShowCreation(brace), FadeIn(lab))
        cnt = tx("4000 наборов сил", 22, C_GREY).next_to(base, DOWN, buff=0.25)
        self.play(FadeIn(cnt))
        self.wait(2)


class S04(Base):
    def construct(self):
        self.add(title("Три режима по температуре"))
        line = Line(LEFT * 5.5, RIGHT * 5.5).shift(UP * 0.4).set_stroke(C_GREY, 3)
        cx = 1.2
        zones = VGroup(
            Rectangle(width=5.5 - 0.15, height=1.0).set_fill(C_GREEN, 0.25).set_stroke(width=0).move_to(LEFT * (5.5 - 2.675) + UP * 0.4),
            Rectangle(width=0.3, height=1.0).set_fill(C_YEL, 0.8).set_stroke(width=0).move_to(UP * 0.4),
            Rectangle(width=5.5 - 0.15, height=1.0).set_fill(C_BLUE, 0.25).set_stroke(width=0).move_to(RIGHT * (5.5 - 2.675) + UP * 0.4),
        )
        zones.shift(RIGHT * 0)
        self.play(ShowCreation(line), FadeIn(zones))
        names = VGroup(tx("спокойно", 28, C_GREEN).move_to(LEFT * 2.9 + UP * 1.4),
                       tx("критично", 28, C_YEL).move_to(UP * 1.4),
                       tx("застыло", 28, C_BLUE).move_to(RIGHT * 2.9 + UP * 1.4))
        beta = VGroup(tx("β < 1", 26).move_to(LEFT * 2.9 + DOWN * 0.4), tx("β = 1", 26).move_to(DOWN * 0.4),
                      tx("β > 1", 26).move_to(RIGHT * 2.9 + DOWN * 0.4))
        self.play(FadeIn(names), FadeIn(beta))
        v = VGroup(
            VGroup(tx("разброс ≈", 24), tx("1 / N²", 34, C_GREEN)).arrange(RIGHT),
            VGroup(tx("разброс ≈", 24), tx("log N / N²", 34, C_YEL)).arrange(RIGHT),
            VGroup(tx("слишком сложно", 26, C_GREY)),
        )
        for g, x in zip(v, (-2.9, 0, 2.9)):
            g.arrange(DOWN, buff=0.15) if False else None
            g.move_to(RIGHT * x + DOWN * 1.8)
        self.play(FadeIn(v[0]))
        self.play(FadeIn(v[1]))
        self.play(FadeIn(v[2]))
        goal = pill("Вопрос: чему равен коэффициент при log N / N² ?", C_YEL, 28).move_to(DOWN * 3.2)
        self.play(FadeIn(goal))
        self.play(Indicate(v[1][1], color=C_YEL))
        self.wait(2)


class S05(Base):
    def construct(self):
        self.add(title("Коэффициент: кто что доказал"))
        rows = [
            ("Чен, Лам · 2019", "порядок (log N)²", None, C_GREY, "грубо"),
            ("Простая оценка (эта статья)", "1/2", 0.5, C_RED, "сверху"),
            ("Талагран / Шерцер", "1/4", 0.25, C_YEL, "сверху"),
            ("Ду, Хуан · июль 2026", "1/6", 1 / 6, C_GREEN, "точно"),
        ]
        ox = LEFT * 1.2
        scale = 7.5
        y0 = 1.9
        objs = []
        for k, (who, val, v, col, tag) in enumerate(rows):
            y = y0 - k * 1.25
            name = tx(who, 24).move_to([-6.7 + tx(who, 24).get_width() / 2, y, 0])
            if v is None:
                bar = Line([-1.0, y, 0], [4.8, y, 0]).set_stroke(col, 6)
                bar.add_tip() if hasattr(bar, "add_tip") else None
                lab = tx(val, 26, col).next_to(bar, RIGHT, buff=0.2).shift(LEFT * 1.9)
                lab.move_to([2, y + 0.4, 0])
            else:
                bar = Rectangle(width=v * scale, height=0.55).set_fill(col, 0.85).set_stroke(width=0)
                bar.move_to([-1.0 + v * scale / 2, y, 0])
                lab = tx(val, 30, col).next_to(bar, RIGHT, buff=0.2)
            tg = pill(tag, col, 20).move_to([5.9, y, 0])
            objs.append((name, bar, lab, tg))
        for name, bar, lab, tg in objs:
            self.play(FadeIn(name), GrowFromEdge(bar, LEFT) if isinstance(bar, Rectangle) else ShowCreation(bar), FadeIn(lab), FadeIn(tg), run_time=0.9)
        fin = pill("Эта статья: всё из одной формулы", C_BLUE, 28).move_to(DOWN * 3.1)
        self.play(FadeIn(fin))
        self.wait(2)


class S06(Base):
    def construct(self):
        self.add(title("Идея: расцепить силы"))
        n = 8
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        rng = np.random.default_rng(21)
        a = rng.standard_normal(len(pairs))
        c = rng.standard_normal(len(pairs))
        rho = ValueTracker(1.0)
        l1, d1 = network(a, n, pairs, 1.25, LEFT * 4.4 + UP * 1.2, 0.8)
        left = VGroup(l1, d1)

        def right_net():
            r = rho.get_value()
            J = math.sqrt(r) * a + math.sqrt(1 - r) * c
            l, d = network(J, n, pairs, 1.25, LEFT * 1.4 + UP * 1.2, 0.8)
            return VGroup(l, d)

        right = always_redraw(right_net)
        t1, t2 = tx("система 1", 24, C_BLUE).next_to(left, DOWN), tx("система 2", 24, C_YEL).move_to(LEFT * 1.4 + DOWN * 0.4)
        self.play(FadeIn(left), FadeIn(right), FadeIn(t1), FadeIn(t2))
        rl = VGroup(tx("общность сил  ρ =", 26), DecimalNumber(1.0, num_decimal_places=2, font_size=32).set_color(C_YEL)).arrange(RIGHT)
        rl[1].add_updater(lambda m: m.set_value(rho.get_value()))
        rl.move_to(LEFT * 3 + DOWN * 1.3)
        self.add(rl)
        self.wait(0.8)
        # график chi(rho) по реальным данным
        xs, ys = D["rho"], D["chi8"]
        ax = Axes(x_range=(0, 1, 0.25), y_range=(0, 2.4, 0.5), width=4.6, height=3.0,
                  axis_config={"stroke_color": C_GREY, "include_ticks": False}).move_to(RIGHT * 4.2 + UP * 0.6)
        xl, yl = tx("ρ", 24, C_GREY).next_to(ax, DOWN, buff=0.1), tx("согласованность χ", 22, C_GREY).next_to(ax, UP, buff=0.12)
        self.play(ShowCreation(ax), FadeIn(xl), FadeIn(yl))
        cur = curve(ax, xs, ys, C_GREEN)
        self.play(ShowCreation(cur), rho.animate.set_value(0.0), run_time=5, rate_func=linear)
        self.wait(0.4)
        pts = [ax.c2p(x, y) for x, y in zip(xs, ys)] + [ax.c2p(1, 0), ax.c2p(0, 0)]
        area = poly(pts, C_GREEN, 0.3)
        self.play(FadeIn(area))
        trap = float(np.sum((np.array(ys[1:]) + np.array(ys[:-1])) / 2 * np.diff(xs)))
        s = D["F_var"] * 2 * D["N"] ** 2
        r1 = VGroup(tx("площадь − 1 =", 26), DecimalNumber(trap - 1, num_decimal_places=3, font_size=30).set_color(C_GREEN)).arrange(RIGHT)
        r2 = VGroup(tx("2N² · разброс F =", 26), DecimalNumber(s, num_decimal_places=3, font_size=30).set_color(C_YEL)).arrange(RIGHT)
        VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(RIGHT * 3.9 + DOWN * 2.7)
        self.play(FadeIn(r1)); self.play(FadeIn(r2))
        eq = pill("разброс = площадь под кривой", C_BLUE, 24).move_to(LEFT * 3 + DOWN * 2.6)
        self.play(FadeIn(eq))
        self.wait(2.5)


class S07(Base):
    def construct(self):
        self.add(title("Точное равенство → верхняя граница"))
        xs, ys, bs = D["rho"], D["chi8"], D["bound8"]
        ax = Axes(x_range=(0, 1, 0.25), y_range=(0, 5, 1), width=7.4, height=4.2,
                  axis_config={"stroke_color": C_GREY, "include_ticks": False}).move_to(LEFT * 1.8 + DOWN * 0.3)
        self.play(ShowCreation(ax), FadeIn(tx("ρ", 24, C_GREY).next_to(ax, DOWN, buff=0.1)))
        c1 = curve(ax, xs, ys, C_GREEN)
        self.play(ShowCreation(c1));
        l1 = tx("реальная согласованность", 24, C_GREEN).move_to(ax.c2p(0.45, 1.0) + DOWN * 0.45)
        self.play(FadeIn(l1))
        c2 = curve(ax, xs[:-1], bs[:-1], C_YEL)
        self.play(ShowCreation(c2))
        l2 = tx("граница из формулы", 24, C_YEL).move_to(ax.c2p(0.3, 3.4))
        self.play(FadeIn(l2))
        pts = [ax.c2p(x, y) for x, y in zip(xs[:-1], bs[:-1])] + [ax.c2p(x, y) for x, y in zip(xs[-2::-1], ys[-2::-1])]
        gap = poly(pts, C_RED, 0.28)
        self.play(FadeIn(gap))
        g = tx("поправка ≤ 0", 22, C_RED).move_to(ax.c2p(0.86, 2.9)); self.play(FadeIn(g))
        # формула словами-блоками справа
        blk = VGroup(
            pill("(1 − ρ + 2ρ/N) · χ", C_GREEN, 26),
            tx("=", 30),
            pill("1 + ρ/N", C_YEL, 26),
            tx("+", 30),
            pill("поправки ≤ 0", C_RED, 26),
        ).arrange(DOWN, buff=0.25).move_to(RIGHT * 4.6 + UP * 0.4)
        self.play(LaggedStartMap(FadeIn, blk, lag_ratio=0.3), run_time=2)
        sub = tx("N = 8 · точное при любом N", 22, C_GREY).next_to(blk, DOWN, buff=0.4)
        self.play(FadeIn(sub))
        self.wait(2.5)


class S08(Base):
    def construct(self):
        self.add(title("Из дроби получается логарифм"))
        ax = Axes(x_range=(0, 1.02, 0.25), y_range=(0, 12, 4), width=7.2, height=4.4,
                  axis_config={"stroke_color": C_GREY, "include_ticks": False}).move_to(LEFT * 2.6 + DOWN * 0.2)
        self.play(ShowCreation(ax), FadeIn(tx("ρ", 24, C_GREY).next_to(ax, DOWN, buff=0.1)))
        f = lambda r: 1 / (1 - r)
        xs = np.linspace(0, 0.915, 60)
        cur = curve(ax, xs, [f(x) for x in xs], C_YEL)
        lab = tx("1 / (1 − ρ)", 28, C_YEL).move_to(ax.c2p(0.3, 6.8))
        self.play(ShowCreation(cur), FadeIn(lab))
        r0 = ValueTracker(0.1)

        def area():
            r = r0.get_value()
            grid = np.linspace(0, r, 40)
            pts = [ax.c2p(x, 0) for x in grid] + [ax.c2p(x, f(x)) for x in grid[::-1]]
            return poly(pts, C_YEL, 0.35)

        a = always_redraw(area)
        cut = always_redraw(lambda: DashedLine(ax.c2p(r0.get_value(), 0), ax.c2p(r0.get_value(), f(r0.get_value()))).set_stroke(C_RED, 3))
        self.add(a, cut)
        num = VGroup(tx("площадь =", 28), DecimalNumber(0, num_decimal_places=2, font_size=36).set_color(C_YEL)).arrange(RIGHT)
        num[1].add_updater(lambda m: m.set_value(-math.log(1 - r0.get_value())))
        num.move_to(RIGHT * 4.2 + UP * 1.5)
        self.add(num)
        self.play(r0.animate.set_value(0.9), run_time=5, rate_func=linear)
        cutlab = pill("обрезка при 1 − ρ ≈ 1/χ", C_RED, 24).move_to(RIGHT * 4.2 + UP * 0.2)
        res = VGroup(tx("растёт как", 26), tx("ln χ", 42, C_YEL)).arrange(RIGHT).move_to(RIGHT * 4.2 + DOWN * 1.0)
        self.play(FadeIn(cutlab)); self.play(FadeIn(res))
        why = tx("χ не бывает больше своего максимума", 22, C_GREY).move_to(RIGHT * 4.2 + DOWN * 2.3)
        self.play(FadeIn(why))
        self.wait(2.5)


class S09(Base):
    def construct(self):
        self.add(title("Словарь: рост χ → коэффициент"))
        ax = NumberLine(x_range=(0, 1.05, 0.25), width=9.5, include_numbers=False).shift(DOWN * 0.1).set_stroke(C_GREY, 3)
        self.play(ShowCreation(ax))
        pos = lambda g: ax.n2p(g)
        ticks = VGroup(*[VGroup(Line(pos(g) + DOWN * 0.15, pos(g) + UP * 0.15).set_stroke(WHITE, 3), tx(s, 22, C_GREY).next_to(pos(g), DOWN, buff=0.25)) for g, s in ((0, "0"), (1 / 3, "1/3"), (1 / 2, "1/2"), (1, "1"))])
        self.play(FadeIn(ticks))
        tag = tx("χ растёт как N в степени γ", 26, C_GREY).move_to(UP * 2.5)
        self.play(FadeIn(tag))
        g = ValueTracker(1.0)
        dot = always_redraw(lambda: Dot(pos(g.get_value()), radius=0.16).set_color(C_YEL))
        big = VGroup(tx("коэффициент  γ/2 =", 32), DecimalNumber(0.5, num_decimal_places=3, font_size=48).set_color(C_YEL)).arrange(RIGHT).move_to(DOWN * 2.2)
        big[1].add_updater(lambda m: m.set_value(g.get_value() / 2))
        self.add(dot, big)
        marks = [(1.0, "тривиально", C_RED), (0.5, "Талагран", C_YEL), (1 / 3, "Ду, Хуан", C_GREEN)]
        for val, name, col in marks:
            self.play(g.animate.set_value(val), run_time=2.2)
            lab = pill(name, col, 24).next_to(pos(val), UP, buff=0.5 + 0.9 * (val < 0.4))
            self.play(FadeIn(lab))
            self.wait(0.4)
        self.wait(1.5)


class S10(Base):
    def construct(self):
        self.add(title("Равенство и «потеря»"))
        L = 4.4
        y = 1.2
        full = Rectangle(width=L, height=0.7).set_fill(C_YEL, 0.85).set_stroke(width=0).move_to([-1.5 + L / 2 - L / 2 + 0, y, 0])
        full.move_to([-4.0 + L / 2, y, 0])
        lb = tx("ln χ", 30, C_YEL).next_to(full, LEFT, buff=0.3)
        self.play(GrowFromEdge(full, LEFT), FadeIn(lb))
        d = 1.2
        loss = Rectangle(width=d, height=0.7).set_fill(C_RED, 0.9).set_stroke(width=0).move_to([-4.0 + L - d / 2, y - 1.4, 0])
        ll = tx("потеря D ≥ 0", 28, C_RED).next_to(loss, DOWN, buff=0.15)
        self.play(FadeIn(loss), FadeIn(ll))
        var = Rectangle(width=L - d, height=0.7).set_fill(C_GREEN, 0.85).set_stroke(width=0).move_to([-4.0 + (L - d) / 2, y - 2.8, 0])
        vl = tx("2N² · разброс", 28, C_GREEN).next_to(var, LEFT, buff=0.3)
        self.play(GrowFromEdge(var, LEFT), FadeIn(vl))
        self.wait(0.5)
        up = pill("D ≥ 0  ⇒  разброс ≤ ½·ln χ", C_YEL, 24).move_to(RIGHT * 3.4 + UP * 1.2)
        self.play(FadeIn(up));
        ck = check().scale(0.8).next_to(up, RIGHT, buff=0.15); lbl = tx("доказано в статье", 20, C_GREEN).next_to(up, DOWN, buff=0.15)
        self.play(ShowCreation(ck), FadeIn(lbl))
        self.play(loss.animate.stretch_to_fit_width(0.12).move_to([-4.0 + L - 0.06, y - 1.4, 0]), var.animate.stretch_to_fit_width(L - 0.12).move_to([-4.0 + (L - 0.12) / 2, y - 2.8, 0]), FadeOut(ll), run_time=2)
        eq = pill("D ограничено  ⇒  равенство", C_GREEN, 24).move_to(RIGHT * 3.4 + DOWN * 1.2)
        self.play(FadeIn(eq))
        who = tx("держится на работе Ду–Хуана", 22, C_RED).next_to(eq, DOWN, buff=0.2)
        self.play(FadeIn(who))
        self.wait(2.5)


class S11(Base):
    def construct(self):
        self.add(title("Проверка при высоких температурах"))
        ax = Axes(x_range=(0, 1.0, 0.25), y_range=(0, 1.8, 0.5), width=7.6, height=4.2,
                  axis_config={"stroke_color": C_GREY, "include_ticks": False}).move_to(LEFT * 1.5 + DOWN * 0.3)
        self.play(ShowCreation(ax), FadeIn(tx("β", 24, C_GREY).next_to(ax, DOWN, buff=0.1)))
        bs = np.linspace(0.05, 0.93, 60)
        cur = curve(ax, bs, [math.log(1 / (1 - b * b)) for b in bs], C_BLUE)
        lb = tx("формула  ln 1/(1−β²)", 26, C_BLUE).move_to(ax.c2p(0.38, 1.35))
        self.play(ShowCreation(cur), FadeIn(lb))
        dots = VGroup(*[Dot(ax.c2p(b, v), radius=0.11).set_color(C_YEL) for b, v in zip(D["betas"], D["var_beta"])])
        self.play(LaggedStartMap(FadeIn, dots, lag_ratio=0.25), run_time=2.5)
        lb2 = tx("реальные расчёты, N = 8", 24, C_YEL).move_to(ax.c2p(0.3, 0.75))
        self.play(FadeIn(lb2))
        ck = VGroup(check(), tx("точки под кривой — верхняя граница держится", 24, C_GREEN)).arrange(RIGHT, buff=0.2).move_to(RIGHT * 4.3 + UP * 1.4)
        ck[1].scale(0.85)
        ck.move_to(DOWN * 3.3)
        self.play(FadeIn(ck))
        self.wait(2.5)


class S12(Base):
    def construct(self):
        self.add(title("Что я проверил на компьютере"))
        rows = [("Главное равенство, N=4", "0,9507", "0,9511"), ("Главное равенство, N=4 (ρ=0,9)", "0,8464", "0,8463"),
                ("Главное равенство, N=5", "0,8495", "0,8501"), ("Формула разброса, N=6", "0,3721", "0,3729")]
        hdr = VGroup(tx("слева", 22, C_BLUE), tx("справа", 22, C_YEL))
        hdr[0].move_to(RIGHT * 1.5 + UP * 2.2); hdr[1].move_to(RIGHT * 3.6 + UP * 2.2)
        self.play(FadeIn(hdr))
        for k, (nm, a, b) in enumerate(rows):
            y = 1.7 - k * 0.75
            row = VGroup(tx(nm, 24).move_to([-3.0, y, 0]), tx(a, 28, C_BLUE).move_to([1.5, y, 0]), tx(b, 28, C_YEL).move_to([3.6, y, 0]), check().scale(0.8).move_to([5.3, y, 0]))
            row[0].move_to([-6.5 + row[0].get_width() / 2, y, 0])
            self.play(FadeIn(row), run_time=0.7)
        others = VGroup(
            VGroup(check().scale(0.7), tx("обе поправки отрицательные", 24)).arrange(RIGHT),
            VGroup(check().scale(0.7), tx("граница выполнена в 15 из 15 случаев", 24)).arrange(RIGHT),
            VGroup(check().scale(0.7), tx("ссылки: 4 из 4 существуют и совпадают", 24)).arrange(RIGHT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(DOWN * 2.6 + LEFT * 1.8)
        self.play(LaggedStartMap(FadeIn, others, lag_ratio=0.4), run_time=2)
        self.wait(2)


class S13(Base):
    def construct(self):
        self.add(title("Итог"))
        items = [
            (check(), "Математика верна", C_GREEN),
            (check(C_YEL), "Новое: простое точное равенство", C_YEL),
            (cross(), "Число 1/6 получили Ду и Хуан раньше", C_RED),
            (cross(C_GREY), "Открыто: ограничить «потерю» самим методом", C_GREY),
        ]
        for k, (ic, s, col) in enumerate(items):
            row = VGroup(ic, tx(s, 32, col)).arrange(RIGHT, buff=0.4)
            row.move_to(UP * (1.7 - k * 1.1))
            row.move_to([-4.2 + row.get_width() / 2, row.get_center()[1], 0])
            self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.9)
        self.wait(0.5)
        end = pill("Препринт · рецензирования ещё не было", C_GREY, 24).move_to(DOWN * 3.0)
        self.play(FadeIn(end))
        self.wait(2.5)
