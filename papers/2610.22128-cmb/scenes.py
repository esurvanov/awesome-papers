"""Ролик по статье arXiv 2610.22128 (гравитационная постоянная и реликтовое излучение) простыми словами. Сцены C01–C12.
Данные: cmb_data.json — мой упрощённый расчёт рекомбинации (не данные статьи); числа графика C07 — из таблиц статьи.
Запуск (из корня репозитория): uv run manimgl papers/2610.22128-cmb/scenes.py C05 -w --hd"""
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

CD = json.load(open(HERE / "data" / "cmb_data.json"))


class C01(Base):
    def construct(self):
        rng = np.random.default_rng(4)
        nx, ny = 64, 34
        noise = rng.standard_normal((ny, nx))
        fx = np.fft.fftfreq(nx)[None, :]
        fy = np.fft.fftfreq(ny)[:, None]
        filt = np.exp(-(fx ** 2 + fy ** 2) * 900)
        sm = np.real(np.fft.ifft2(np.fft.fft2(noise) * filt))
        sm = (sm - sm.mean()) / sm.std()
        sq = VGroup()
        for j in range(ny):
            for i in range(nx):
                u, v = (i / (nx - 1) - 0.5) * 2, (j / (ny - 1) - 0.5) * 2
                if u * u + v * v < 1:
                    t = max(-1, min(1, sm[j, i] / 2))
                    col = interpolate_color(Color(C_BLUE), Color("#ffffff"), t + 1 if t < 0 else 1) if False else (
                        interpolate_color(Color(C_BLUE), Color("#e6edf3"), (t + 1) / 1) if t < 0 else interpolate_color(Color("#e6edf3"), Color(C_RED), t))
                    s = Square(side_length=0.16).set_stroke(width=0).set_fill(col, 1).move_to([u * 5.1 * 0.62 * 1.0, v * 1.55 + 1.35, 0])
                    sq.add(s)
        t1 = tx("Менялась ли гравитация", 48)
        t2 = tx("в молодой Вселенной?", 48)
        sub = tx("Разбор статьи про реликтовое излучение", 28, C_GREY)
        g = VGroup(t1, t2, sub).arrange(DOWN, buff=0.25).move_to(DOWN * 1.9)
        self.play(FadeIn(sq, lag_ratio=0.0005), run_time=2.5)
        self.play(Write(t1), Write(t2), run_time=1.5)
        self.play(FadeIn(sub))
        self.wait(2)


class C02(Base):
    def construct(self):
        self.add(head("Реликтовое излучение — первый свет"))
        line = Line(LEFT * 6, RIGHT * 6).shift(UP * 0.2).set_stroke(C_GREY, 4)
        self.play(ShowCreation(line))
        pts = [(-6, "Большой взрыв", C_RED), (-3.0, "горячая плазма:\nсвет не проходит", C_YEL), (0.5, "380 тыс. лет:\nатомы собрались", C_GREEN), (6, "сегодня,\n13,8 млрд лет", C_BLUE)]
        for x, s, col in pts:
            d = Dot(radius=0.2).set_color(col).move_to([x, 0.2, 0])
            lab = tx(s, 26, col).next_to(d, DOWN, buff=0.35)
            if x > 5:
                lab.shift(LEFT * 0.6)
            if x < -5:
                lab = tx(s, 26, col).next_to(d, UP, buff=0.35).shift(RIGHT * 0.5)
            self.play(FadeIn(d, scale=1.6), FadeIn(lab), run_time=0.9)
        fog = Rectangle(width=3.0, height=0.7).set_fill(C_YEL, 0.25).set_stroke(width=0).move_to([-3.0, 0.2, 0])
        self.play(FadeIn(fog))
        rays = VGroup(*[Arrow([0.9, 0.2 + k * 0.18, 0], [5.0, 0.2 + k * 0.18, 0], buff=0, stroke_width=3).set_color(C_GREEN) for k in (-2, -1, 0, 1, 2)])
        self.play(ShowCreation(rays, lag_ratio=0.2), run_time=1.5)
        self.play(FadeIn(cap("С тех пор этот свет летит к нам — это и есть реликтовое излучение", C_YEL)))
        self.wait(3)


class C03(Base):
    def construct(self):
        self.add(head("Вопрос: одинакова ли гравитация?"))
        a1, a2 = Circle(radius=0.5).set_fill(C_BLUE, 0.7).set_stroke(width=0).move_to(LEFT * 5.2 + UP * 0.5), Circle(radius=0.5).set_fill(C_BLUE, 0.7).set_stroke(width=0).move_to(LEFT * 2.6 + UP * 0.5)
        ar1 = Arrow(a1.get_right(), a2.get_left(), buff=0.1).set_color(C_GREEN)
        ar2 = Arrow(a2.get_left(), a1.get_right(), buff=0.1).set_color(C_GREEN)
        now = tx("сегодня", 32, C_GREEN).next_to(VGroup(a1, a2), UP, buff=0.9)
        lab = tx("силу измеряют в лаборатории", 26).next_to(VGroup(a1, a2), DOWN, buff=0.6)
        self.play(FadeIn(a1), FadeIn(a2), ShowCreation(ar1), ShowCreation(ar2), FadeIn(now), FadeIn(lab))
        self.play(FadeIn(check().next_to(lab, DOWN, buff=0.3)))
        b1, b2 = Circle(radius=0.5).set_fill(C_YEL, 0.7).set_stroke(width=0).move_to(RIGHT * 2.6 + UP * 0.5), Circle(radius=0.5).set_fill(C_YEL, 0.7).set_stroke(width=0).move_to(RIGHT * 5.2 + UP * 0.5)
        dar = DashedLine(b1.get_right(), b2.get_left(), buff=0.1).set_stroke(C_YEL, 4)
        q = tx("?", 80, C_YEL).move_to(RIGHT * 3.9 + UP * 1.15)
        then = tx("380 тысяч лет после взрыва", 32, C_YEL).next_to(VGroup(b1, b2), UP, buff=1.2)
        self.play(FadeIn(b1), FadeIn(b2), ShowCreation(dar), FadeIn(then), FadeIn(q))
        self.play(FadeIn(tx("тогда — неизвестно", 26).next_to(VGroup(b1, b2), DOWN, buff=0.6)))
        self.play(FadeIn(cap("Реликтовое излучение — свидетель того времени", WHITE)))
        self.wait(3)


class C04(Base):
    def construct(self):
        self.add(head("Гравитация задаёт скорость расширения"))
        t = ValueTracker(0)
        for cx, rate, col, name in ((-3.4, 1.0, C_BLUE, "G как сегодня"), (3.4, 1.7, C_YEL, "G больше")):
            c = Circle(radius=0.1).move_to([cx, 0.2, 0])
            c.add_updater(lambda m, r=rate, x=cx, co=col: m.become(Circle(radius=0.15 + 2.0 * min(1, t.get_value()) * r / 1.7).set_stroke(co, 6).set_fill(co, 0.15).move_to([x, 0.2, 0])))
            self.add(c)
            self.add(tx(name, 32, col).move_to([cx, -2.3, 0]))
            dots = VGroup()
            for k in range(12):
                ang = 2 * math.pi * k / 12
                d = Dot(radius=0.06).set_color(col)
                d.add_updater(lambda m, a=ang, r=rate, x=cx: m.move_to([x + (0.15 + 2.0 * min(1, t.get_value()) * r / 1.7) * math.cos(a), 0.2 + (0.15 + 2.0 * min(1, t.get_value()) * r / 1.7) * math.sin(a), 0]))
                dots.add(d)
            self.add(dots)
        clock = VGroup(tx("прошло одно и то же время", 26, C_GREY)).move_to(UP * 2.4)
        self.add(clock)
        self.play(t.animate.set_value(1), run_time=4, rate_func=linear)
        self.play(FadeIn(cap("Больше G — быстрее расширение", C_YEL)))
        self.wait(3)


class C05(Base):
    def construct(self):
        self.add(head("Атомы не успевают собраться"))
        zs = np.array(CD["z"])
        ax = Axes(x_range=(0, 1000, 250), y_range=(-3.1, 0.1, 1), width=7.4, height=4.0,
                  axis_config={"stroke_color": C_GREY, "include_ticks": False}).move_to(LEFT * 1.7 + DOWN * 0.2)
        self.play(ShowCreation(ax))
        for yv, s in ((0, "100%"), (-1, "10%"), (-2, "1%"), (-3, "0,1%")):
            self.add(tx(s, 22, C_GREY).next_to(ax.c2p(0, yv), LEFT, buff=0.15))
        self.add(tx("раньше", 22, C_GREY).next_to(ax.c2p(0, -3.1), DOWN, buff=0.12), tx("позже", 22, C_GREY).next_to(ax.c2p(1000, -3.1), DOWN, buff=0.12))
        yl = tx("доля свободных электронов", 24, C_GREY).next_to(ax, UP, buff=0.15)
        self.add(yl)

        def cv(key, color, width=4):
            xs = [1700 - z for z in zs]
            ys = [math.log10(max(v, 1e-3)) for v in CD[key]]
            return curve(ax, xs, ys, color, width)

        saha = cv("saha", C_GREY, 4)
        saha.set_stroke(C_GREY, 4, opacity=0.9)
        self.play(ShowCreation(saha))
        self.add(tx("идеальная сборка", 22, C_GREY).move_to(ax.c2p(250, -2.5)))
        cols = [C_GREEN, C_BLUE, C_YEL, C_RED]
        names = ["G в 4 раза меньше", "G как сегодня", "G в 2,25 раза больше", "G в 4 раза больше"]
        lams = ["0.5", "1.0", "1.5", "2.0"]
        leg = VGroup()
        for lam, col, nm in zip(lams, cols, names):
            c = cv(f"x{lam}", col)
            self.play(ShowCreation(c), run_time=1.3)
            leg.add(VGroup(Line(ORIGIN, RIGHT * 0.5).set_stroke(col, 6), tx(nm, 24)).arrange(RIGHT, buff=0.2))
        leg.arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(RIGHT * 4.9 + UP * 0.9)
        self.play(FadeIn(leg))
        self.play(FadeIn(cap("Чем больше G, тем больше электронов остаётся свободными", C_YEL)))
        self.add(tx("мой упрощённый расчёт", 20, C_GREY).move_to(RIGHT * 4.9 + DOWN * 1.5))
        self.wait(3)


class C06(Base):
    def construct(self):
        self.add(head("Свободные электроны — как туман"))

        def walk(step, total, seed):
            rng = np.random.default_rng(seed)
            n = int(total / step)
            ang = rng.uniform(0, 2 * math.pi, n)
            p = np.cumsum(np.stack([np.cos(ang), np.sin(ang)], 1) * step, 0)
            p = np.vstack([[0, 0], p])
            return p

        best = None
        for seed in range(200):
            a = walk(0.14, 9.0, seed)
            b = walk(0.45, 9.0, seed + 1000)
            if np.linalg.norm(a[-1]) < 1.0 and np.linalg.norm(b[-1]) > 2.0 and np.abs(a).max() < 1.8 and np.abs(b).max() < 2.2:
                best = (a, b)
                break
        a, b = best
        for (cx, p, col, name, dens) in ((-3.5, a, C_YEL, "много электронов", 140), (3.5, b, C_GREEN, "мало электронов", 25)):
            rng = np.random.default_rng(7)
            box = Rectangle(width=5.2, height=4.4).set_stroke(C_GREY, 2).move_to([cx, 0.2, 0])
            fog = VGroup(*[Dot(radius=0.04).set_color(C_GREY).set_opacity(0.55).move_to([cx + rng.uniform(-2.5, 2.5), 0.2 + rng.uniform(-2.1, 2.1), 0]) for _ in range(dens)])
            self.add(box, fog, tx(name, 28, col).move_to([cx, -2.4, 0]))
        pa = VMobject().set_points_as_corners([[-3.5 + x, 0.2 + y, 0] for x, y in a]).set_stroke(C_YEL, 3)
        pb = VMobject().set_points_as_corners([[3.5 + x, 0.2 + y, 0] for x, y in b]).set_stroke(C_GREEN, 3)
        sa, sb = Dot(radius=0.1).move_to([-3.5, 0.2, 0]), Dot(radius=0.1).move_to([3.5, 0.2, 0])
        self.play(FadeIn(sa), FadeIn(sb))
        self.play(ShowCreation(pa), ShowCreation(pb), run_time=5, rate_func=linear)
        ea = Dot(radius=0.12).set_color(WHITE).move_to([-3.5 + a[-1][0], 0.2 + a[-1][1], 0])
        eb = Dot(radius=0.12).set_color(WHITE).move_to([3.5 + b[-1][0], 0.2 + b[-1][1], 0])
        ar_a = Arrow(sa.get_center(), ea.get_center(), buff=0.12, stroke_width=6).set_color(WHITE)
        ar_b = Arrow(sb.get_center(), eb.get_center(), buff=0.12, stroke_width=6).set_color(WHITE)
        self.play(FadeIn(ea), FadeIn(eb), ShowCreation(ar_a), ShowCreation(ar_b))
        self.play(FadeIn(cap("Свет прошёл одинаковый путь, но в тумане ушёл недалеко", C_YEL)))
        self.wait(3)


class C07(Base):
    def construct(self):
        self.add(head("Три линейки реликтового излучения"))
        lam = np.array([0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0])
        G = lam ** 2
        damp = np.array([2471, 2213, 2015, 1860, 1731, 1625, 1535, 1460]) / 1860.0
        ax = Axes(x_range=(0, 4.2, 1), y_range=(0, 0.7, 0.1), width=7.4, height=4.2,
                  axis_config={"stroke_color": C_GREY, "include_ticks": False}).move_to(LEFT * 1.8 + DOWN * 0.2)
        base_line = Line(ax.c2p(0, 0.3), ax.c2p(4.2, 0.3)).set_stroke(C_GREY, 1, opacity=0.5)
        self.play(ShowCreation(ax), ShowCreation(base_line))
        for gx in (1, 2, 3, 4):
            self.add(tx(str(gx), 22, C_GREY).next_to(ax.c2p(gx, 0), DOWN, buff=0.12))
        self.add(tx("сила гравитации (1 = сегодня)", 24, C_GREY).next_to(ax, DOWN, buff=0.5))
        self.add(tx("изменение, 1 = как сегодня", 22, C_GREY).next_to(ax, UP, buff=0.12))
        eq = Line(ax.c2p(0.06, 0.3), ax.c2p(4.0, 0.3)).set_stroke(C_GREY, 7)
        la = curve(ax, [0.0625, 1.0, 4.0], [296.1 / 299.6 - 0.7, 0.3, 304.4 / 299.6 - 0.7], C_BLUE, 6)
        ld = curve(ax, list(G), list(damp - 0.7), C_YEL, 7)
        self.play(ShowCreation(eq))
        l1 = pill("масштаб равенства: не меняется", C_GREY, 22).move_to(RIGHT * 4.7 + UP * 1.6)
        self.play(FadeIn(l1))
        self.play(ShowCreation(la))
        l2 = pill("расстояние между пиками: чуть-чуть", C_BLUE, 22).move_to(RIGHT * 4.7 + UP * 0.6)
        self.play(FadeIn(l2))
        self.play(ShowCreation(ld), run_time=2)
        l3 = pill("масштаб затухания: заметно", C_YEL, 22).move_to(RIGHT * 4.7 + DOWN * 0.4)
        self.play(FadeIn(l3))
        self.play(FadeIn(cap("G в 4 раза больше — масштаб затухания меньше на 21%", C_YEL)))
        self.wait(3)


class C08(Base):
    def construct(self):
        self.add(head("Откуда берётся итог"))
        s = 8.0
        zero = Line([0, 1.9, 0], [0, -1.6, 0]).set_stroke(C_GREY, 3)
        self.play(ShowCreation(zero))
        self.add(tx("0", 24, C_GREY).move_to([0, 2.2, 0]))
        # геометрия: влево на 0.5
        g_bar = Rectangle(width=0.5 * s, height=0.7).set_fill(C_RED, 0.85).set_stroke(width=0).move_to([-0.25 * s, 1.0, 0])
        g_lab = tx("геометрия: расстояние сжимается", 28, C_RED).next_to(g_bar, UP, buff=0.15).shift(RIGHT * 0.2)
        self.play(GrowFromEdge(g_bar, RIGHT), FadeIn(g_lab))
        self.add(tx("−0,5", 34, C_RED).move_to([-0.25 * s, 1.0, 0]))
        k_bar = Rectangle(width=0.196 * s, height=0.7).set_fill(C_GREEN, 0.85).set_stroke(width=0).move_to([-0.5 * s + 0.098 * s, -0.2, 0])
        k_lab = tx("задержка рекомбинации: возвращает назад", 28, C_GREEN)
        k_lab.move_to([-6.6 + k_lab.get_width() / 2, -0.95, 0])
        self.play(GrowFromEdge(k_bar, LEFT), FadeIn(k_lab))
        self.add(tx("+0,2", 28, C_GREEN).move_to(k_bar.get_center()))
        res = Dot(radius=0.18).set_color(C_YEL).move_to([-0.304 * s, -1.9, 0])
        rl = tx("итог: −0,3", 36, C_YEL).next_to(res, RIGHT, buff=0.3)
        self.play(FadeIn(res, scale=1.6), FadeIn(rl))
        box = pill("G на 10% больше → масштаб затухания на 1,4% меньше", C_YEL, 28).move_to(DOWN * 3.2)
        self.play(FadeIn(box))
        self.wait(3)


class C09(Base):
    def construct(self):
        self.add(head("Граница: когда эффект пропадает"))
        lo, hi = -2.2, 1.0
        x0, x1 = -6.0, 6.0
        sx = lambda g: x0 + (math.log10(g) - lo) / (hi - lo) * (x1 - x0)
        bar = Rectangle(width=x1 - x0, height=0.9).set_fill(C_BLUE, 0.2).set_stroke(width=0).move_to([0, 0.4, 0])
        eqz = Rectangle(width=sx(1 / 49) - x0, height=0.9).set_fill(C_GREEN, 0.35).set_stroke(width=0).move_to([(x0 + sx(1 / 49)) / 2, 0.4, 0])
        self.play(FadeIn(bar), FadeIn(eqz))
        for g, s in ((0.01, "1/100"), (0.1, "1/10"), (1, "1"), (10, "10")):
            self.add(tx(s, 22, C_GREY).move_to([sx(g), -0.4, 0]))
        self.add(tx("сила гравитации относительно сегодняшней", 24, C_GREY).move_to(DOWN * 1.0))
        self.add(tx("равновесие:\nэффекта нет", 26, C_GREEN).move_to([(x0 + sx(1 / 49)) / 2 + 0.5, 1.6, 0]))
        self.add(tx("эффект есть", 26, C_BLUE).move_to([sx(5), 1.6, 0]))
        bl = DashedLine([sx(1 / 49), 1.0, 0], [sx(1 / 49), -0.2, 0]).set_stroke(C_RED, 4)
        self.play(ShowCreation(bl))
        self.add(tx("граница ≈ 1/49", 26, C_RED).move_to([sx(1 / 49) + 1.0, -1.7, 0]))
        us = Dot(radius=0.2).set_color(C_YEL).move_to([sx(1), 0.4, 0])
        self.play(FadeIn(us, scale=1.6))
        self.add(tx("наша Вселенная", 26, C_YEL).next_to(us, UP, buff=0.9))
        br = Line([sx(0.0625), -2.3, 0], [sx(4), -2.3, 0]).set_stroke(C_GREY, 6)
        self.play(ShowCreation(br))
        self.add(tx("здесь авторы считали на компьютере", 24, C_GREY).move_to([sx(0.6), -2.7, 0]))
        self.play(FadeIn(cap("Граница лежит за пределами расчётов — это оценка", C_YEL, -3.6)))
        self.wait(3)


class C10(Base):
    def construct(self):
        self.add(head("Что именно «слышит» G"))
        rows = [("высота пиков", 0.025, C_GREY), ("положение «равенства»", 0.017, C_BLUE), ("затухание", 0.32, C_YEL)]
        s = 11.0
        for k, (nm, v, col) in enumerate(rows):
            y = 1.5 - k * 1.5
            t = tx(nm, 30)
            t.move_to([-6.3 + t.get_width() / 2, y + 0.6, 0])
            bar = Rectangle(width=max(v * s, 0.06), height=0.6).set_fill(col, 0.85).set_stroke(width=0).move_to([-6.3 + max(v * s, 0.06) / 2, y, 0])
            self.play(FadeIn(t), GrowFromEdge(bar, LEFT), run_time=1)
            lab = tx({0.025: "почти нет", 0.017: "почти нет", 0.32: "заметно"}[v], 28, col).next_to(bar, RIGHT, buff=0.3)
            self.play(FadeIn(lab), run_time=0.5)
        self.play(FadeIn(cap("Из таких измерений без догадок о поздней Вселенной получается G", C_YEL)))
        self.wait(3)


class C11(Base):
    def construct(self):
        self.add(head("Оговорки"))
        items = [
            "Число зависит от определения: −0,30 или −0,25",
            "Граница 1/49 — оценка за пределами расчётов",
            "Остальные константы считаются неизменными",
            "Препринт: независимой проверки ещё не было",
        ]
        for k, s in enumerate(items):
            row = VGroup(warn_icon(), tx(s, 32)).arrange(RIGHT, buff=0.4)
            row.move_to([-5.9 + row.get_width() / 2, 1.7 - k * 1.1, 0])
            self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.9)
            self.wait(0.4)
        self.play(FadeIn(cap("Авторы сообщают, что ИИ помогал с проверкой выкладок", C_GREY)))
        self.wait(3)


class C12(Base):
    def construct(self):
        self.add(head("Главное"))
        pts = [("Гравитация меняет скорость расширения Вселенной", WHITE),
               ("От этого меняется, сколько атомов успело собраться", C_YEL),
               ("Меняется «туман», и затухание на мелких масштабах", C_GREEN),
               ("Так можно сравнить G тогда и сегодня", C_BLUE)]
        for k, (s, col) in enumerate(pts):
            t = tx(s, 34, col)
            t.move_to([-6.0 + t.get_width() / 2, 1.7 - k * 1.2, 0])
            d = Dot(radius=0.12).set_color(col).next_to(t, LEFT, buff=0.3)
            self.play(FadeIn(VGroup(d, t), shift=RIGHT * 0.3), run_time=0.9)
            self.wait(0.5)
        self.wait(3)
