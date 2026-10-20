"""Та же статья простыми словами: образ «компания людей». Сцены L01–L11.
Запуск (из корня репозитория): uv run manimgl papers/2610.00011-spin-glass/scenes_simple.py L05 -w --hd"""
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


class L01(Base):
    def construct(self):
        n, pairs = 9, [(i, j) for i in range(9) for j in range(i + 1, 9)]
        rng = np.random.default_rng(3)
        lines, dots = network(rng.standard_normal(len(pairs)), n, pairs, 1.4, UP * 1.3)
        t = tx("Насколько шумит случайная система", 48)
        t2 = tx("на границе порядка и хаоса?", 48)
        sub = tx("Разбор научной статьи простыми словами", 28, C_GREY)
        g = VGroup(t, t2, sub).arrange(DOWN, buff=0.25).move_to(DOWN * 1.5)
        self.play(ShowCreation(lines, lag_ratio=0.02), FadeIn(dots), run_time=2)
        self.play(Write(t), Write(t2), run_time=1.5)
        self.play(FadeIn(sub))
        self.wait(2)


class L02(Base):
    def construct(self):
        self.add(head("Представьте компанию"))
        n = 8
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        rng = np.random.default_rng(5)
        J = rng.standard_normal(len(pairs))
        c = LEFT * 3.4 + DOWN * 0.2
        lines, dots = network(J, n, pairs, 2.2, c)
        self.play(FadeIn(dots), run_time=0.6)
        self.play(ShowCreation(lines, lag_ratio=0.03), run_time=2)
        who = cap("8 человек. Каждая пара — друзья или враги", WHITE, -3.55)
        self.play(FadeIn(who))
        leg = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.7).set_stroke(C_GREEN, 6), tx("дружба", 30)).arrange(RIGHT, buff=0.3),
            VGroup(Line(ORIGIN, RIGHT * 0.7).set_stroke(C_RED, 6), tx("вражда", 30)).arrange(RIGHT, buff=0.3),
            VGroup(Line(ORIGIN, RIGHT * 0.7).set_stroke(WHITE, 2), tx("толще — сильнее", 30)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(RIGHT * 4.0 + UP * 1.5)
        self.play(FadeIn(leg))
        spins = VGroup()
        for p in ring(n, 2.2, c):
            up = rng.random() > 0.5
            a = Arrow(p, p + (UP if up else DOWN) * 0.5, buff=0, stroke_width=5).set_color(C_BLUE if up else C_YEL)
            a.shift((UP if up else DOWN) * 0.3)
            spins.add(a)
        self.play(FadeIn(spins))
        dec = pill("каждый выбирает «за» или «против»", C_BLUE, 28).move_to(RIGHT * 4.0 + DOWN * 0.2)
        self.play(FadeIn(dec))
        S = all_states(n)
        F = free_energy(J, n, S, pairs)
        sc = VGroup(tx("общий балл компании", 28), DecimalNumber(F, num_decimal_places=2, font_size=60).set_color(C_YEL)).arrange(DOWN, buff=0.15).move_to(RIGHT * 4.0 + DOWN * 1.9)
        self.play(FadeIn(sc))
        self.wait(2.5)


class L03(Base):
    def construct(self):
        self.add(head("Каждая компания случайна"))
        n = 8
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        S = all_states(n)
        rng = np.random.default_rng(9)
        for k in range(3):
            J = rng.standard_normal(len(pairs))
            lines, dots = network(J, n, pairs, 0.8, LEFT * 5.0 + UP * (2.0 - 2.2 * k), 0.8)
            F = free_energy(J, n, S, pairs)
            lab = VGroup(tx("балл", 28), DecimalNumber(F, num_decimal_places=2, font_size=40).set_color(C_YEL)).arrange(RIGHT).next_to(dots, RIGHT, buff=0.7)
            self.play(FadeIn(VGroup(lines, dots, lab)), run_time=1)
        c1 = cap("Новая компания — немного другой балл", WHITE)
        self.play(FadeIn(c1))
        self.wait(0.5)
        F = np.array(D["F"])
        x0, x1, ybase, hmax = 0.5, 6.5, -2.4, 3.2
        base = Line([x0, ybase, 0], [x1, ybase, 0]).set_stroke(C_GREY, 3)
        lo, hi = 0.7, 1.1
        sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
        bins = np.linspace(lo, hi, 31)
        h, _ = np.histogram(F, bins=bins)
        h = h / h.max()
        bars = VGroup()
        for i in range(30):
            if h[i] > 0:
                r = Rectangle(width=sx(bins[i + 1]) - sx(bins[i]) - 0.03, height=h[i] * hmax).set_stroke(width=0).set_fill(C_BLUE, 0.85)
                r.move_to([(sx(bins[i]) + sx(bins[i + 1])) / 2, ybase + h[i] * hmax / 2, 0])
                bars.add(r)
        self.play(ShowCreation(base), FadeOut(c1))
        sub = cap("Составили 4000 случайных компаний", C_GREY)
        self.play(FadeIn(sub))
        self.play(LaggedStart(*[GrowFromPoint(b, b.get_bottom()) for b in bars], lag_ratio=0.03), run_time=2.5)
        m, s = F.mean(), F.std()
        br = Line([sx(m - s), ybase + hmax + 0.35, 0], [sx(m + s), ybase + hmax + 0.35, 0]).set_stroke(C_YEL, 6)
        lb = tx("разброс баллов", 30, C_YEL).next_to(br, UP, buff=0.12)
        self.play(ShowCreation(br), FadeIn(lb))
        self.play(FadeOut(sub))
        q = cap("Вопрос статьи: как точно измерить этот разброс?", C_YEL)
        self.play(FadeIn(q))
        self.wait(2.5)


class L04(Base):
    def construct(self):
        self.add(head("Где измерять сложнее всего"))
        y0 = 0.6
        left = Rectangle(width=5.0, height=1.1).set_fill(C_GREEN, 0.3).set_stroke(width=0).move_to(LEFT * 3.0 + UP * y0)
        mid = Rectangle(width=0.5, height=1.1).set_fill(C_YEL, 0.9).set_stroke(width=0).move_to(UP * y0)
        right = Rectangle(width=5.0, height=1.1).set_fill(C_BLUE, 0.3).set_stroke(width=0).move_to(RIGHT * 3.0 + UP * y0)
        self.play(FadeIn(left), FadeIn(mid), FadeIn(right))
        names = [("всё спокойно", C_GREEN, -3.0), ("на грани", C_YEL, 0), ("всё застыло", C_BLUE, 3.0)]
        for s, col, x in names:
            self.play(FadeIn(tx(s, 34, col).move_to(RIGHT * x + UP * (y0 + 1.1))), run_time=0.6)
        ex = [("как вода: жидкая", -3.0), ("лёд вот-вот появится", 0), ("как лёд: твёрдая", 3.0)]
        for s, x in ex:
            self.add(tx(s, 24, C_GREY).move_to(RIGHT * x + UP * (y0 - 1.0)))
        arr = Arrow(LEFT * 5.2 + DOWN * 1.4, RIGHT * 5.2 + DOWN * 1.4, buff=0, stroke_width=4).set_color(C_GREY)
        self.play(ShowCreation(arr))
        self.add(tx("слабее связи", 24, C_GREY).move_to(LEFT * 4.0 + DOWN * 1.8), tx("сильнее связи", 24, C_GREY).move_to(RIGHT * 4.0 + DOWN * 1.8))
        self.play(Indicate(mid, color=C_YEL, scale_factor=1.3))
        c = cap("Именно на грани разброс труднее всего посчитать точно", C_YEL)
        self.play(FadeIn(c))
        self.wait(3)


class L05(Base):
    def construct(self):
        self.add(head("Хитрость: две почти одинаковые компании"))
        n = 8
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        rng = np.random.default_rng(21)
        a = rng.standard_normal(len(pairs))
        c = rng.standard_normal(len(pairs))
        share = ValueTracker(1.0)
        l1, d1 = network(a, n, pairs, 1.25, LEFT * 4.6 + UP * 1.0, 0.8)
        left = VGroup(l1, d1)

        def right_net():
            r = share.get_value()
            J = math.sqrt(r) * a + math.sqrt(1 - r) * c
            l, d = network(J, n, pairs, 1.25, LEFT * 1.6 + UP * 1.0, 0.8)
            return VGroup(l, d)

        right = always_redraw(right_net)
        t1 = tx("компания 1", 26, C_BLUE).move_to(LEFT * 4.6 + DOWN * 0.7)
        t2 = tx("компания 2", 26, C_YEL).move_to(LEFT * 1.6 + DOWN * 0.7)
        self.play(FadeIn(left), FadeIn(right), FadeIn(t1), FadeIn(t2))
        pct = VGroup(tx("общих отношений:", 30), DecimalNumber(100, num_decimal_places=0, font_size=44).set_color(C_YEL), tx("%", 36, C_YEL)).arrange(RIGHT, buff=0.15)
        pct[1].add_updater(lambda m: m.set_value(share.get_value() * 100))
        pct.move_to(LEFT * 3.1 + DOWN * 1.7)
        self.add(pct)
        sub = cap("Сначала связи одинаковые, потом их постепенно меняем", WHITE)
        self.play(FadeIn(sub))
        xs, ys = D["rho"], D["chi8"]
        ax = Axes(x_range=(0, 1, 0.25), y_range=(0, 2.4, 0.5), width=4.8, height=3.0,
                  axis_config={"stroke_color": C_GREY, "include_ticks": False}).move_to(RIGHT * 4.3 + UP * 0.5)
        ylab = tx("насколько похожи решения", 24, C_GREY).next_to(ax, UP, buff=0.12)
        xl = VGroup(tx("0%", 22, C_GREY).next_to(ax.c2p(0, 0), DOWN, buff=0.1), tx("100%", 22, C_GREY).next_to(ax.c2p(1, 0), DOWN, buff=0.1))
        self.play(ShowCreation(ax), FadeIn(ylab), FadeIn(xl))
        xl2 = VGroup(tx("100% общих", 20, C_GREY).next_to(ax.c2p(0, 0), DOWN, buff=0.1), tx("0%", 20, C_GREY).next_to(ax.c2p(1, 0), DOWN, buff=0.1))
        self.remove(xl)
        self.add(xl2)
        cur = curve(ax, [1 - x for x in xs[::-1]], ys[::-1], C_GREEN)
        self.play(ShowCreation(cur), share.animate.set_value(0.0), run_time=6, rate_func=linear)
        self.play(FadeOut(sub))
        pts = [ax.c2p(1 - x, y) for x, y in zip(xs, ys)] + [ax.c2p(0, 0), ax.c2p(1, 0)]
        area = poly(pts, C_GREEN, 0.3)
        self.play(FadeIn(area))
        key = cap("Чем дольше компании остаются похожими — тем сильнее шум", C_YEL)
        self.play(FadeIn(key))
        trap = float(np.sum((np.array(ys[1:]) + np.array(ys[:-1])) / 2 * np.diff(xs))) - 1
        s = D["F_var"] * 2 * D["N"] ** 2
        r1 = VGroup(tx("по площади", 26), DecimalNumber(trap, num_decimal_places=2, font_size=36).set_color(C_GREEN)).arrange(RIGHT)
        r2 = VGroup(tx("прямой подсчёт", 26), DecimalNumber(s, num_decimal_places=2, font_size=36).set_color(C_YEL)).arrange(RIGHT)
        VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(RIGHT * 4.3 + DOWN * 2.1)
        self.play(FadeIn(r1)); self.play(FadeIn(r2))
        ok = check().scale(0.8).next_to(VGroup(r1, r2), RIGHT, buff=0.3)
        self.play(ShowCreation(ok))
        self.wait(3)


class L06(Base):
    def construct(self):
        self.add(head("Потолок для похожести"))
        xs, ys, bs = D["rho"], D["chi8"], D["bound8"]
        ax = Axes(x_range=(0, 1, 0.25), y_range=(0, 5, 1), width=7.6, height=4.2,
                  axis_config={"stroke_color": C_GREY, "include_ticks": False}).move_to(LEFT * 1.6 + DOWN * 0.2)
        X = lambda x: 1 - x
        self.play(ShowCreation(ax))
        self.add(tx("100% общих", 22, C_GREY).next_to(ax.c2p(0, 0), DOWN, buff=0.1), tx("0%", 22, C_GREY).next_to(ax.c2p(1, 0), DOWN, buff=0.1))
        c1 = curve(ax, [1 - x for x in xs], ys, C_GREEN)
        self.play(ShowCreation(c1))
        l1 = pill("реальная похожесть", C_GREEN, 26).move_to(ax.c2p(0.6, 0.55))
        self.play(FadeIn(l1))
        c2 = curve(ax, [1 - x for x in xs], bs, C_YEL)
        self.play(ShowCreation(c2))
        l2 = pill("потолок из формулы", C_YEL, 26).move_to(ax.c2p(0.62, 4.1))
        self.play(FadeIn(l2))
        pts = [ax.c2p(1 - x, y) for x, y in zip(xs, bs)] + [ax.c2p(1 - x, y) for x, y in zip(xs[::-1], ys[::-1])]
        gap = poly(pts, C_RED, 0.28)
        self.play(FadeIn(gap))
        self.add(tx("запас", 26, C_RED).move_to(ax.c2p(0.1, 3.3)))
        side = VGroup(
            VGroup(check().scale(0.7), tx("точная формула", 30)).arrange(RIGHT, buff=0.25),
            VGroup(check().scale(0.7), tx("верна для любого размера", 30)).arrange(RIGHT, buff=0.25),
            VGroup(check().scale(0.7), tx("реальная кривая ниже", 30)).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(RIGHT * 4.6 + UP * 0.6)
        self.play(LaggedStartMap(FadeIn, side, lag_ratio=0.5), run_time=2.5)
        self.play(FadeIn(cap("Это главная формула статьи", WHITE)))
        self.wait(3)


class L07(Base):
    def construct(self):
        self.add(head("Потолок шума растёт очень медленно"))
        labels = ["10", "100", "1 тыс.", "10 тыс.", "100 тыс."]
        base_y = -2.3
        x0 = -5.0
        step = 2.0
        bars = VGroup()
        for k, s in enumerate(labels):
            h = 0.75 * (k + 1)
            r = Rectangle(width=1.2, height=h).set_fill(C_YEL, 0.85).set_stroke(width=0)
            r.move_to([x0 + k * step, base_y + h / 2, 0])
            bars.add(r)
            self.add(tx(s, 26, C_GREY).move_to([x0 + k * step, base_y - 0.35, 0]))
        self.add(tx("число частиц в системе", 26, C_GREY).move_to(DOWN * 3.0))
        for k, r in enumerate(bars):
            self.play(GrowFromEdge(r, DOWN), run_time=0.7)
            if k > 0:
                self.play(FadeIn(tx("+1 шаг", 24, C_RED).next_to(r, UP, buff=0.12)), run_time=0.3)
        side = VGroup(tx("в 10 раз больше частиц", 32), tx("потолок вырос на один шаг", 32, C_YEL)).arrange(DOWN, buff=0.3).move_to(LEFT * 3.0 + UP * 1.7)
        self.play(FadeIn(side))
        self.play(FadeIn(cap("Так растёт число цифр в числе — это и есть логарифм", C_YEL)))
        self.wait(3)


class L08(Base):
    def construct(self):
        self.add(head("Лесенка точности"))
        x0 = -6.0
        scale = 12.0
        truth = x0 + (1 / 6) * scale
        rows = [("Простая оценка", "из этой статьи", 0.5, C_RED), ("Оценка Талаграна", "классическая", 0.25, C_YEL), ("Ду и Хуан", "точный ответ, июль 2026", 1 / 6, C_GREEN)]
        for k, (a, b, v, col) in enumerate(rows):
            y = 1.6 - k * 1.5
            bar = Rectangle(width=v * scale, height=0.8).set_fill(col, 0.85).set_stroke(width=0).move_to([x0 + v * scale / 2, y, 0])
            n1 = tx(a, 32).next_to(bar, RIGHT, buff=0.3).shift(UP * 0.18)
            n2 = tx(b, 22, C_GREY).next_to(n1, DOWN, buff=0.08, aligned_edge=LEFT)
            self.play(GrowFromEdge(bar, LEFT), FadeIn(n1), FadeIn(n2), run_time=1.1)
        line = DashedLine([truth, 2.4, 0], [truth, -2.4, 0]).set_stroke(C_GREEN, 3)
        self.play(ShowCreation(line))
        self.add(tx("истина", 26, C_GREEN).move_to([truth, -2.75, 0]))
        self.play(FadeIn(cap("Чем короче полоска — тем точнее мы знаем шум", WHITE)))
        self.wait(3)


class L09(Base):
    def construct(self):
        self.add(head("Что здесь новое"))
        items = [
            (check(), "Математика статьи верна", C_GREEN),
            (check(C_YEL), "Новое: простая точная формула", C_YEL),
            (cross(), "Ответ «1/6» уже нашли Ду и Хуан", C_RED),
            (cross(C_GREY), "Не удалось: обойтись без их помощи", C_GREY),
        ]
        for k, (ic, s, col) in enumerate(items):
            row = VGroup(ic, tx(s, 36, col)).arrange(RIGHT, buff=0.45)
            row.move_to([-4.6 + row.get_width() / 2, 1.7 - k * 1.15, 0])
            self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=1)
            self.wait(0.6)
        self.play(FadeIn(cap("Автор сам честно об этом пишет", C_GREY)))
        self.wait(2.5)


class L10(Base):
    def construct(self):
        self.add(head("Я проверил расчётом на компьютере"))
        self.add(tx("по формуле", 26, C_BLUE).move_to(RIGHT * 1.0 + UP * 2.4), tx("прямой счёт", 26, C_YEL).move_to(RIGHT * 3.4 + UP * 2.4))
        rows = [("Главная формула, 4 человека", "0,951", "0,951"), ("Главная формула, 5 человек", "0,850", "0,850"), ("Шум компании, 6 человек", "0,373", "0,372")]
        for k, (nm, a, b) in enumerate(rows):
            y = 1.5 - k * 1.0
            t = tx(nm, 30)
            t.move_to([-6.8 + t.get_width() / 2, y, 0])
            row = VGroup(t, tx(a, 38, C_BLUE).move_to([1.0, y, 0]), tx(b, 38, C_YEL).move_to([3.4, y, 0]), check().scale(0.9).move_to([5.3, y, 0]))
            self.play(FadeIn(row), run_time=0.9)
        more = VGroup(
            VGroup(check().scale(0.7), tx("потолок выполнен во всех 15 случаях", 30)).arrange(RIGHT, buff=0.25),
            VGroup(check().scale(0.7), tx("ссылки на другие работы настоящие", 30)).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 2.2 + LEFT * 1.2)
        self.play(LaggedStartMap(FadeIn, more, lag_ratio=0.5))
        self.wait(2.5)


class L11(Base):
    def construct(self):
        self.add(head("Главное"))
        pts = [("Шум случайной системы можно оценить простой точной формулой", WHITE),
               ("Точный ответ на грани хаоса уже знали другие", C_YEL),
               ("Статья даёт новый, более простой путь к нему", C_GREEN)]
        for k, (s, col) in enumerate(pts):
            t = tx(s, 34, col)
            t.move_to([-6.0 + t.get_width() / 2, 1.5 - k * 1.3, 0])
            dot = Dot(radius=0.12).set_color(col).next_to(t, LEFT, buff=0.3)
            self.play(FadeIn(VGroup(dot, t), shift=RIGHT * 0.3), run_time=1)
            self.wait(0.8)
        self.play(FadeIn(pill("Это препринт: независимой проверки ещё не было", C_GREY, 26).move_to(DOWN * 2.8)))
        self.wait(3)
