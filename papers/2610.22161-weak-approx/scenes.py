"""Ролик по статье arXiv 2610.22161 (Pat Lank, «Gluing weak approximability along recollements») простыми словами.
Образ «кирпичи и этажи» придуман для ролика, в статье строгие определения. Графики-схемы иллюстративные, расчётов в ролике нет.
Запуск (из корня репозитория): uv run manimgl papers/2610.22161-weak-approx/scenes.py D05 -w --hd"""
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
from manimkit import Base as _Base


class Base(_Base):
    SLOW = 1.6  # медленнее: текст успевают прочитать, а озвучка — прозвучать


def brick(label="G", color=C_YEL, w=0.9, h=0.5):
    r = RoundedRectangle(width=w, height=h, corner_radius=0.08).set_stroke(color, 2).set_fill(color, 0.55)
    t = tx(label, 22, WHITE).move_to(r)
    return VGroup(r, t)


class D01(Base):
    def construct(self):
        zin = Circle(radius=0.8).set_stroke(C_YEL, 5).set_fill(C_YEL, 0.45)
        zout = Annulus(inner_radius=0.8, outer_radius=1.8).set_stroke(C_BLUE, 5).set_fill(C_BLUE, 0.3)
        pic = VGroup(zout, zin).move_to(UP * 1.4)
        t1 = tx("Что сохраняется при склейке?", 52)
        sub = tx("Разбор статьи Пэта Ланка про категории", 28, C_GREY)
        g = VGroup(t1, sub).arrange(DOWN, buff=0.3).move_to(DOWN * 1.7)
        self.play(FadeIn(zout), FadeIn(zin), run_time=1.5)
        self.play(Write(t1), run_time=1.5)
        self.play(FadeIn(sub))
        self.wait(2)


class D03(Base):
    def construct(self):
        self.add(head("Кирпичи и этажи"))
        rng = np.random.default_rng(2)
        floors = list(range(-3, 4))
        for k, f in enumerate(floors):
            y = 1.9 - k * 0.8
            self.add(Line([-6, y - 0.4, 0], [1.5, y - 0.4, 0]).set_stroke(C_GREY, 1, opacity=0.5))
            self.add(tx(str(f), 22, C_GREY).move_to([-6.5, y, 0]))
        self.add(tx("этаж", 22, C_GREY).move_to([-6.5, 2.7, 0]))
        count = [1, 2, 3, 3, 2, 2, 1]
        bricks = VGroup()
        for k, c in enumerate(count):
            y = 1.9 - k * 0.8
            for i in range(c):
                b = brick("G", C_YEL, 0.9, 0.5).move_to([-5.3 + i * 1.05, y, 0])
                bricks.add(b)
        self.play(LaggedStartMap(FadeIn, bricks, lag_ratio=0.12), run_time=3)
        side = VGroup(
            tx("Один сорт кирпича G", 34, C_YEL),
            tx("копии на разных этажах", 30),
            tx("собирают любой объект", 30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(RIGHT * 3.7 + UP * 0.6)
        self.play(FadeIn(side))
        self.add(tx("образ для ролика: в статье строгие определения", 20, C_GREY).move_to(DOWN * 3.6))
        self.wait(3)


class D04(Base):
    def construct(self):
        self.add(head("«Слабая» точность"))
        x0 = -2.0
        sc = 0.62
        X = lambda f: x0 + f * sc
        axis = Line([X(-9), -2.2, 0], [X(4), -2.2, 0]).set_stroke(C_GREY, 3)
        self.play(ShowCreation(axis))
        for f in (-8, -6, -4, -2, 0, 2, 4):
            self.add(tx(str(f), 20, C_GREY).move_to([X(f), -2.6, 0]))
        self.add(tx("этажи", 22, C_GREY).move_to([X(4.2) + 0.5, -2.6, 0]))
        A = 2
        rows = [(1, C_GREEN), (2, C_YEL), (3, C_RED)]
        for k, (m, col) in enumerate(rows):
            y = 1.8 - k * 1.4
            lo, hi = 1 - m - A, A
            bar = Rectangle(width=(hi - lo) * sc, height=0.5).set_fill(col, 0.7).set_stroke(width=0).move_to([(X(lo) + X(hi)) / 2, y, 0])
            t = tx(f"точность «на {m} шаг(а)»", 26, col)
            t.move_to([-6.2 + t.get_width() / 2, y + 0.55, 0])
            rest = tx(f"остаток глубже {m}", 22, C_GREY).next_to(bar, RIGHT, buff=0.4) if False else tx(f"остаток глубже −{m}", 22, C_GREY)
            rest.move_to([X(5.4), y, 0])
            self.play(FadeIn(t), GrowFromEdge(bar, RIGHT), FadeIn(rest), run_time=1.2)
        self.add(tx("окно кирпичей", 22, C_GREY).move_to([-5.9, -1.35, 0]))
        self.play(FadeIn(cap("Хотим точнее — окно кирпичей шире, остаток уходит глубже", C_YEL)))
        self.wait(3)


class D05(Base):
    def construct(self):
        self.add(head("Что было известно до статьи"))
        z = VGroup(Circle(radius=0.6).set_stroke(C_YEL, 4).set_fill(C_YEL, 0.4), tx("Z", 36)).move_to(LEFT * 4.5 + UP * 1.2)
        u = VGroup(Circle(radius=0.6).set_stroke(C_BLUE, 4).set_fill(C_BLUE, 0.4), tx("U", 36)).move_to(LEFT * 1.5 + UP * 1.2)
        d = VGroup(Circle(radius=0.8).set_stroke(WHITE, 4).set_fill(WHITE, 0.1), tx("D", 40)).move_to(RIGHT * 3.5 + UP * 1.2)
        self.play(FadeIn(z), FadeIn(u), FadeIn(d))
        ck1 = check().scale(0.8).next_to(z, DOWN, buff=0.3)
        ck2 = check().scale(0.8).next_to(u, DOWN, buff=0.3)
        self.play(ShowCreation(ck1), ShowCreation(ck2))
        self.add(tx("части хороши", 24, C_GREEN).next_to(VGroup(z, u), DOWN, buff=0.9).shift(RIGHT * 0.1))
        ar = Arrow(LEFT * 0.4 + UP * 1.2, RIGHT * 2.4 + UP * 1.2, buff=0, stroke_width=6).set_color(C_GREY)
        self.play(ShowCreation(ar))
        q = tx("?", 90, C_YEL).move_to(RIGHT * 3.5 + UP * 1.2 + UP * 1.5)
        self.play(FadeIn(q))
        self.add(tx("хорошо ли целое?", 28, C_YEL).next_to(d, DOWN, buff=0.4))
        rows = VGroup(
            VGroup(tx("сильное свойство:", 28), tx("да (Берк, Нееман, Паувелс, 2023)", 28, C_GREEN)).arrange(RIGHT, buff=0.3),
            VGroup(tx("слабое свойство:", 28), tx("оставалось вопросом", 28, C_RED)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 2.4 + LEFT * 0.5)
        self.play(FadeIn(rows[0]))
        self.play(FadeIn(rows[1]))
        ans = pill("Ответ: да — при одном простом условии", C_YEL, 30).move_to(DOWN * 3.5)
        self.play(FadeIn(ans))
        self.wait(3)


class D06(Base):
    def construct(self):
        self.add(head("Условие: на высоких этажах пусто"))
        n0 = 4
        rng = np.random.default_rng(6)
        base_y = -2.0
        x0 = -6.0
        vals = list(range(-3, 10))
        bars = VGroup()
        for i, n in enumerate(vals):
            h = 0 if n >= n0 else float(rng.uniform(0.8, 2.6))
            x = x0 + i * 0.95
            if h > 0:
                r = Rectangle(width=0.7, height=h).set_fill(C_BLUE, 0.8).set_stroke(width=0).move_to([x, base_y + h / 2, 0])
                bars.add(r)
            self.add(tx(str(n), 20, C_GREY).move_to([x, base_y - 0.4, 0]))
        self.add(Line([x0 - 0.5, base_y, 0], [x0 + len(vals) * 0.95, base_y, 0]).set_stroke(C_GREY, 3))
        self.add(tx("этаж", 22, C_GREY).move_to([x0 - 0.8, base_y - 0.4, 0]))
        self.play(LaggedStartMap(GrowFromEdge, bars, edge=DOWN, lag_ratio=0.1), run_time=2.5)
        zone = Rectangle(width=(len(vals) - (n0 + 3)) * 0.95, height=3.3).set_fill(C_GREEN, 0.15).set_stroke(C_GREEN, 2)
        zone.move_to([x0 + (n0 + 3) * 0.95 + zone.get_width() / 2 - 0.47, base_y + 1.65, 0])
        self.play(FadeIn(zone))
        zl = tx("здесь связей нет", 28, C_GREEN).move_to(zone.get_center())
        self.play(FadeIn(zl))
        tl = tx("высота столбика: насколько кирпич связан сам с собой", 22, C_GREY).move_to([-1.5, 2.2, 0])
        self.add(tl)
        self.play(FadeIn(cap("Без этого условия целое не может быть хорошим — оно необходимо", C_YEL)))
        self.add(tx("схема для пояснения, не расчёт", 20, C_GREY).move_to([5.0, 2.2, 0]))
        self.wait(3)


class D07(Base):
    def construct(self):
        self.add(head("Почему старое доказательство ломается"))
        x0 = -5.2
        base_y = -2.2
        heights = [0.4 * (1.45 ** k) for k in range(7)]
        bars = VGroup()
        for k, h in enumerate(heights):
            r = Rectangle(width=0.8, height=h).set_fill(C_RED, 0.75).set_stroke(width=0).move_to([x0 + k * 1.05, base_y + h / 2, 0])
            bars.add(r)
            self.add(tx(str(k + 1), 22, C_GREY).move_to([x0 + k * 1.05, base_y - 0.4, 0]))
        self.add(Line([x0 - 0.6, base_y, 0], [x0 + 7 * 1.05, base_y, 0]).set_stroke(C_GREY, 3))
        self.add(tx("шаг", 22, C_GREY).move_to([x0 - 0.9, base_y - 0.4, 0]))
        self.play(LaggedStartMap(GrowFromEdge, bars, edge=DOWN, lag_ratio=0.35), run_time=3.5)
        self.add(tx("запас, который нужен на этом шаге", 22, C_GREY).move_to([-3.0, 2.3, 0]))
        dots = tx("…", 60, C_RED).move_to([x0 + 7.2 * 1.05 + 0.3, base_y + 1.0, 0])
        self.play(FadeIn(dots))
        side = VGroup(
            tx("Каждый шаг ухудшает запас", 30),
            tx("число шагов в «слабом» случае", 30),
            tx("ничем не ограничено", 30, C_RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(RIGHT * 4.0 + UP * 0.8)
        self.play(FadeIn(side))
        self.play(FadeIn(cap("Запас растёт с каждым шагом, а шагов может быть сколько угодно", C_YEL)))
        self.wait(3)


class D08(Base):
    def construct(self):
        self.add(head("Новая идея: поднять один кирпич"))
        left = VGroup(
            tx("Было", 30, C_RED),
            VGroup(*[brick("", C_RED, 0.6, 0.4) for _ in range(5)]).arrange(RIGHT, buff=0.15),
            tx("цепочка шагов, запас растёт", 24, C_GREY),
        ).arrange(DOWN, buff=0.35).move_to(LEFT * 3.8 + UP * 1.5)
        right = VGroup(
            tx("Стало", 30, C_GREEN),
            brick("G", C_GREEN, 1.0, 0.5),
            tx("один кирпич — сразу на нужный этаж", 24, C_GREY),
        ).arrange(DOWN, buff=0.35).move_to(RIGHT * 3.0 + UP * 1.5)
        self.play(FadeIn(left))
        self.play(FadeIn(right))
        self.wait(0.4)
        sc = 0.2
        base_y = -2.5
        vals = [("запас части Z", 5, C_YEL), ("запас части U", 5, C_BLUE), ("запас целого", 15, C_GREEN)]
        for k, (nm, v, col) in enumerate(vals):
            x = -3.6 + k * 3.6
            r = Rectangle(width=1.2, height=v * sc).set_fill(col, 0.8).set_stroke(width=0).move_to([x, base_y + v * sc / 2, 0])
            self.play(GrowFromEdge(r, DOWN), run_time=0.9)
            self.add(tx(nm, 22, col).move_to([x, base_y - 0.4, 0]))
            self.add(tx(f"A" if k < 2 else "3A", 36, WHITE).move_to(r))
        self.play(FadeIn(cap("Если части хороши с запасом A — целое хорошо с запасом 3A", C_YEL)))
        self.wait(3)


class D09(Base):
    def construct(self):
        self.add(head("Применение: алгебраические пространства"))
        boxes = [("схемы", "Нееман: свойство есть", C_BLUE), ("склейка", "новая теорема статьи", C_YEL), ("алгебраические\nпространства", "свойство есть у всех", C_GREEN)]
        xs = [-4.6, 0.0, 4.6]
        for k, ((a, b, col), x) in enumerate(zip(boxes, xs)):
            box = RoundedRectangle(width=3.6, height=1.5, corner_radius=0.2).set_stroke(col, 3).set_fill(col, 0.15).move_to([x, 1.4, 0])
            t = tx(a, 30, WHITE).move_to(box.get_center() + UP * 0.2)
            s = tx(b, 20, col).move_to(box.get_center() + DOWN * 0.45) if "\n" not in a else tx(b, 20, col).move_to(box.get_center() + DOWN * 0.6)
            if "\n" in a:
                t.move_to(box.get_center() + UP * 0.15)
            self.play(FadeIn(VGroup(box, t, s)), run_time=0.9)
            if k < 2:
                self.play(ShowCreation(Arrow([x + 1.9, 1.4, 0], [xs[k + 1] - 1.9, 1.4, 0], buff=0, stroke_width=6).set_color(C_GREY)), run_time=0.6)
        rows = VGroup(
            VGroup(check().scale(0.7), tx("для ноэтеровых пространств — ещё и «когерентность»", 28)).arrange(RIGHT, buff=0.3),
            VGroup(check().scale(0.7), tx("для схем сильного свойства может не быть — слабое необходимо", 28)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 1.5 + LEFT * 0.3)
        self.play(LaggedStartMap(FadeIn, rows, lag_ratio=0.5), run_time=2)
        self.play(FadeIn(cap("Пространства получают из схем склейкой — поэтому теорема сразу всё закрывает", C_YEL)))
        self.wait(3)


class D10(Base):
    def construct(self):
        self.add(head("Что осталось за кадром"))
        items = [
            "Для «стеков» нужна ещё одна лемма — автор её не доказывает",
            "Есть неопубликованное доказательство Паувелс, но с большими запасами",
            "Для пространств условие на кирпич автор проверяет отдельной леммой",
        ]
        for k, s in enumerate(items):
            row = VGroup(warn_icon(), tx(s, 30)).arrange(RIGHT, buff=0.4)
            row.move_to([-6.2 + row.get_width() / 2, 1.5 - k * 1.2, 0])
            self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.9)
            self.wait(0.4)
        self.wait(3)


class D11(Base):
    def construct(self):
        self.add(head("О самой статье"))
        items = [
            (check(), "Автор один: Пэт Ланк, Милан, препринт от 15 октября 2026", WHITE),
            (warn_icon(), "Независимой проверки ещё не было", C_YEL),
            (warn_icon(), "Автор пишет: ИИ помогал вычитывать и искать пробелы в доказательствах", C_YEL),
            (check(), "Доказательство пройдено, все границы пересчитаны: сходится", C_GREEN),
        ]
        for k, (ic, s, col) in enumerate(items):
            row = VGroup(ic, tx(s, 29, col)).arrange(RIGHT, buff=0.4)
            row.move_to([-6.4 + row.get_width() / 2, 1.7 - k * 1.2, 0])
            self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.9)
            self.wait(0.3)
        self.play(FadeIn(cap("Формальной компьютерной проверки не делали", C_GREY)))
        self.wait(3)


class D12(Base):
    def construct(self):
        self.add(head("Главное"))
        pts = [("Объект склеен из двух частей, обе «хороши»", WHITE),
               ("Хорошо ли целое — зависело от одного условия", C_YEL),
               ("Новый приём: поднимать один кирпич сразу на нужный этаж", C_GREEN),
               ("Итог: свойство есть у всех алгебраических пространств", C_BLUE)]
        for k, (s, col) in enumerate(pts):
            t = tx(s, 33, col)
            t.move_to([-6.2 + t.get_width() / 2, 1.7 - k * 1.2, 0])
            d = Dot(radius=0.12).set_color(col).next_to(t, LEFT, buff=0.3)
            self.play(FadeIn(VGroup(d, t), shift=RIGHT * 0.3), run_time=0.9)
            self.wait(0.5)
        self.wait(3)


# ---------------- Часть 1: идея, часть 2: склейка (по nLab, Stacks Project, Fiorenza–Loregián), разделители ----------------
def disc_pic(center, r=1.0, mode="all", n_rings=5):
    """Диск из точек-«данных». mode: all — все точки цветные, ring — только «остальное U», core — только ядро Z."""
    g = VGroup()
    core_r = r * 0.45
    for k in range(1, n_rings + 1):
        rr = r * k / n_rings
        m = max(6, int(8 * k))
        for i in range(m):
            ang = 2 * math.pi * i / m + 0.3 * k
            x, y = rr * math.cos(ang), rr * math.sin(ang)
            val = 0.5 + 0.5 * math.sin(2.2 * x + 1.3 * y)
            col = interpolate_color(Color(C_BLUE), Color(C_RED), val)
            in_core = rr <= core_r
            on = mode == "all" or (mode == "core" and in_core) or (mode == "ring" and not in_core)
            d = Dot(radius=0.055).set_color(col if on else C_GREY).set_opacity(1 if on else 0.18)
            d.move_to(center + np.array([x, y, 0]))
            g.add(d)
    return g


def divider(num, name, active):
    labels = ["Идея", "Азы", "Склейка", "Статья"]
    items = VGroup()
    for k, lb in enumerate(labels):
        col = C_YEL if k == active else C_GREY
        c = Circle(radius=0.38).set_stroke(col, 4).set_fill(col, 0.25 if k == active else 0.05)
        t = tx(str(k + 1), 30, col).move_to(c)
        l = tx(lb, 26, col).next_to(c, DOWN, buff=0.2)
        items.add(VGroup(c, t, l))
    items.arrange(RIGHT, buff=1.7).move_to(UP * 1.6)
    return items


class P1(Base):
    def construct(self):
        items = divider(1, "Идея статьи", 0)
        big = tx("Часть 1. Идея статьи", 52, C_YEL).move_to(DOWN * 0.8)
        self.play(FadeIn(items), Write(big), run_time=1.5)
        self.wait(1.2)


class P3(Base):
    def construct(self):
        items = divider(3, "Склейка", 2)
        big = tx("Часть 3. Что такое склейка", 52, C_YEL).move_to(DOWN * 0.8)
        sub = tx("по nLab, Stacks Project и работам Fiorenza–Loregián", 24, C_GREY).move_to(DOWN * 1.8)
        self.play(FadeIn(items), Write(big), run_time=1.5)
        self.play(FadeIn(sub))
        self.wait(1.2)


class P4(Base):
    def construct(self):
        items = divider(4, "Статья", 3)
        big = tx("Часть 4. Сама статья", 52, C_YEL).move_to(DOWN * 0.8)
        self.play(FadeIn(items), Write(big), run_time=1.5)
        self.wait(1.2)


class A1(Base):
    def construct(self):
        self.add(head("Идея в одной картинке"))
        zc, uc, dc = LEFT * 4.6 + UP * 0.8, LEFT * 1.3 + UP * 0.8, RIGHT * 3.8 + UP * 0.8
        z = VGroup(Circle(radius=0.7).set_stroke(C_YEL, 4).set_fill(C_YEL, 0.4), tx("Z", 38)).move_to(zc)
        u = VGroup(Annulus(inner_radius=0.35, outer_radius=0.9).set_stroke(C_BLUE, 4).set_fill(C_BLUE, 0.35), tx("U", 38)).move_to(uc)
        plus = tx("+", 56, C_GREY).move_to((zc + uc) / 2)
        eq = tx("=", 56, C_GREY).move_to((uc + dc) / 2 + LEFT * 0.2)
        dz = Circle(radius=0.55).set_stroke(C_YEL, 4).set_fill(C_YEL, 0.4)
        du = Annulus(inner_radius=0.55, outer_radius=1.15).set_stroke(C_BLUE, 4).set_fill(C_BLUE, 0.35)
        d = VGroup(du, dz).move_to(dc)
        self.play(FadeIn(z), FadeIn(u), FadeIn(plus))
        self.play(ShowCreation(Arrow(uc + RIGHT * 1.2, dc + LEFT * 1.5, buff=0, stroke_width=6).set_color(C_GREY)), FadeIn(d))
        c1, c2 = check().scale(0.8).next_to(z, DOWN, buff=0.4), check().scale(0.8).next_to(u, DOWN, buff=0.4)
        self.play(ShowCreation(c1), ShowCreation(c2))
        self.add(tx("у каждой части есть хорошее свойство", 28, C_GREEN).move_to(LEFT * 3.0 + DOWN * 1.5))
        q = tx("?", 90, C_YEL).next_to(d, UP, buff=0.3)
        self.play(FadeIn(q))
        self.add(tx("а у целого?", 30, C_YEL).next_to(d, DOWN, buff=0.4))
        self.play(FadeIn(cap("Вопрос статьи: передаётся ли хорошее свойство от частей к целому", WHITE)))
        self.wait(3)


class A2(Base):
    def construct(self):
        self.add(head("Само собой это не следует"))
        d = VGroup(Annulus(inner_radius=0.55, outer_radius=1.15).set_stroke(C_BLUE, 4).set_fill(C_BLUE, 0.35),
                   Circle(radius=0.55).set_stroke(C_YEL, 4).set_fill(C_YEL, 0.4)).move_to(UP * 1.0)
        self.play(FadeIn(d))
        left = VGroup(cross().scale(0.9), tx("в общем случае — нет", 32, C_RED)).arrange(RIGHT, buff=0.3).move_to(LEFT * 3.8 + DOWN * 1.0)
        right = VGroup(check().scale(0.9), tx("да, если выполнено одно условие", 32, C_GREEN)).arrange(RIGHT, buff=0.3).move_to(RIGHT * 2.8 + DOWN * 1.0)
        self.play(ShowCreation(Arrow(d.get_bottom(), LEFT * 3.8 + DOWN * 0.4, buff=0.1, stroke_width=5).set_color(C_RED)), FadeIn(left))
        self.play(ShowCreation(Arrow(d.get_bottom(), RIGHT * 2.8 + DOWN * 0.4, buff=0.1, stroke_width=5).set_color(C_GREEN)), FadeIn(right))
        self.play(FadeIn(cap("Это условие и найдено в статье (его разбор — в части 4)", C_YEL)))
        self.wait(3)


class G1(Base):
    def construct(self):
        self.add(head("Пространство и два куска"))
        c = LEFT * 3.2 + DOWN * 0.1
        x_ = Circle(radius=2.2).set_stroke(WHITE, 3).move_to(c)
        self.play(ShowCreation(x_))
        self.add(tx("X — всё пространство", 28).next_to(x_, UP, buff=0.25))
        z = Circle(radius=0.95).set_stroke(C_YEL, 6).set_fill(C_YEL, 0.35).move_to(c)
        self.play(FadeIn(z))
        u = Annulus(inner_radius=0.95, outer_radius=2.2).set_fill(C_BLUE, 0.25).set_stroke(width=0).move_to(c)
        u_edge = DashedLine(c + RIGHT * 0.95 + UP * 0.0, c + RIGHT * 0.95 + UP * 0.001)
        ring_edge = Circle(radius=0.95).set_stroke(C_BLUE, 3).move_to(c)
        ring_edge.set_stroke(C_BLUE, 3)
        self.play(FadeIn(u))
        side = VGroup(
            VGroup(tx("Z", 40, C_YEL), tx("замкнутая часть", 30)).arrange(RIGHT, buff=0.35),
            VGroup(tx("U", 40, C_BLUE), tx("«остальное»: X без Z", 30)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(RIGHT * 3.3 + UP * 0.8)
        self.play(FadeIn(side))
        self.add(tx("Z замкнута: граница ей принадлежит", 24, C_GREY).move_to(RIGHT * 3.3 + DOWN * 0.7))
        self.add(tx("U открыта: границы у неё нет", 24, C_GREY).move_to(RIGHT * 3.3 + DOWN * 1.2))
        self.add(tx("Картинка — аналогия: что значит «замкнутая» в статье, см. часть 2", 22, C_YEL).move_to(RIGHT * 3.0 + DOWN * 2.3))
        self.add(tx("по nLab: recollement", 20, C_GREY).move_to(DOWN * 3.85 + RIGHT * 5.2))
        self.play(FadeIn(cap("Пространство делят на замкнутую часть Z и всё остальное", C_YEL)))
        self.wait(3)


class G2(Base):
    def construct(self):
        self.add(head("Данные на пространстве раскладываются на куски"))
        self.add(tx("пример: температура в каждой точке пространства", 26, C_GREY).move_to(UP * 2.55))
        cs = [LEFT * 4.6, ORIGIN, RIGHT * 4.6]
        pics = [disc_pic(cs[0] + DOWN * 0.1, 1.3, "ring"), disc_pic(cs[1] + DOWN * 0.1, 1.3, "all"), disc_pic(cs[2] + DOWN * 0.1, 1.3, "core")]
        labs = ["кусок на U", "целое F", "кусок на Z"]
        cols = [C_BLUE, WHITE, C_YEL]
        self.play(FadeIn(pics[1]), FadeIn(tx(labs[1], 30, cols[1]).move_to(cs[1] + DOWN * 2.1)), run_time=1.2)
        self.play(FadeIn(pics[0]), FadeIn(tx(labs[0], 30, cols[0]).move_to(cs[0] + DOWN * 2.1)), run_time=1.2)
        self.play(ShowCreation(Arrow(cs[0] + RIGHT * 1.5, cs[1] + LEFT * 1.6, buff=0, stroke_width=6).set_color(C_GREY)))
        self.play(FadeIn(pics[2]), FadeIn(tx(labs[2], 30, cols[2]).move_to(cs[2] + DOWN * 2.1)), run_time=1.2)
        self.play(ShowCreation(Arrow(cs[1] + RIGHT * 1.5, cs[2] + LEFT * 1.6, buff=0, stroke_width=6).set_color(C_GREY)))
        self.add(tx("вложение", 22, C_GREY).move_to((cs[0] + cs[1]) / 2 + UP * 0.45), tx("сужение", 22, C_GREY).move_to((cs[1] + cs[2]) / 2 + UP * 0.45))
        self.play(FadeIn(cap("Точная цепочка: «кусок на U» → «целое» → «кусок на Z»", C_YEL)))
        self.add(tx("Stacks Project, лемма 17.7.1", 20, C_GREY).move_to(DOWN * 3.85 + RIGHT * 5.2))
        self.wait(3)


class G3(Base):
    def construct(self):
        self.add(head("Три категории и шесть функторов"))
        names = [("категория\nзамкнутой части Z", C_YEL, -5.0), ("категория\nцелого D", WHITE, 0.0), ("категория\n«остального» U", C_BLUE, 5.0)]
        for nm, col, x in names:
            b = RoundedRectangle(width=3.2, height=1.5, corner_radius=0.2).set_stroke(col, 3).set_fill(col, 0.12).move_to([x, 1.5, 0])
            t = tx(nm, 26, col).move_to(b)
            self.play(FadeIn(VGroup(b, t)), run_time=0.6)

        def arr(x0, x1, y, lab, col):
            a = Arrow([x0, y, 0], [x1, y, 0], buff=0, stroke_width=5).set_color(col)
            l = tx(lab, 22, col).move_to([(x0 + x1) / 2, y + 0.3, 0])
            return VGroup(a, l)

        # левая щель: между Z и D, x от -3.3 до -1.7
        L = [(-1.8, -3.2, 2.2, "i*", C_GREY), (-3.2, -1.8, 1.5, "i_*", C_YEL), (-1.8, -3.2, 0.8, "i!", C_GREY)]
        R = [(3.2, 1.8, 2.2, "j_!", C_GREY), (1.8, 3.2, 1.5, "j*", C_BLUE), (3.2, 1.8, 0.8, "j_*", C_GREY)]
        for x0, x1, y, lab, col in L + R:
            self.play(FadeIn(arr(x0, x1, y, lab, col)), run_time=0.5)
        notes = VGroup(
            VGroup(tx("i_*", 26, C_YEL), tx("положить Z в целое", 28)).arrange(RIGHT, buff=0.3),
            VGroup(tx("j*", 26, C_BLUE), tx("ограничить целое на «остальное»", 28)).arrange(RIGHT, buff=0.3),
            VGroup(tx("остальные четыре", 26, C_GREY), tx("— те же связи в обратную сторону", 28)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 1.2 + LEFT * 1.2)
        self.play(LaggedStartMap(FadeIn, notes, lag_ratio=0.5), run_time=2)
        key = pill("Z = в точности то, что исчезает на «остальном»", C_YEL, 28).move_to(DOWN * 3.0)
        self.play(FadeIn(key))
        self.add(tx("nLab: recollement", 20, C_GREY).move_to(DOWN * 3.85 + RIGHT * 5.2))
        self.wait(3)


class G4(Base):
    def construct(self):
        self.add(head("Объект восстанавливается из двух кусков"))
        r = 0.85
        row1 = [(-4.4, "ring"), (0.0, "all"), (4.4, "core")]
        row2 = [(-4.4, "core"), (0.0, "all"), (4.4, "ring")]
        names1 = ["кусок на U", "объект E", "кусок на Z"]
        names2 = ["кусок на Z", "объект E", "кусок на U"]
        for (row, y, names, lab) in ((row1, 1.2, names1, "первая цепочка"), (row2, -1.7, names2, "вторая цепочка")):
            self.add(tx(lab, 24, C_YEL).move_to([-6.0 + tx(lab, 24).get_width() / 2, y + 1.15, 0]))
            for (x, mode), nm in zip(row, names):
                self.play(FadeIn(disc_pic(np.array([x, y, 0]), r, mode, 4)), FadeIn(tx(nm, 22, C_GREY).move_to([x, y - 1.2, 0])), run_time=0.5)
            for x0, x1 in ((-4.4, 0.0), (0.0, 4.4)):
                self.add(Arrow([x0 + 1.15, y, 0], [x1 - 1.15, y, 0], buff=0, stroke_width=5).set_color(C_GREY))
        self.play(FadeIn(cap("Это «треугольники»: объект собирается из куска на U и куска на Z", C_YEL, -3.65)))
        self.wait(3)


class G5(Base):
    def construct(self):
        self.add(head("Зачем нужна склейка"))
        # дерево разбиений
        def node(x, y, r, col=WHITE):
            return Circle(radius=r).set_stroke(col, 3).set_fill(col, 0.15).move_to([x, y, 0])
        root = node(-3.2, 2.0, 0.6)
        self.play(FadeIn(root))
        lv1 = [node(-5.0, 0.4, 0.45, C_YEL), node(-1.4, 0.4, 0.45, C_BLUE)]
        lv2 = [node(-5.8, -1.3, 0.3, C_YEL), node(-4.2, -1.3, 0.3, C_BLUE), node(-2.2, -1.3, 0.3, C_YEL), node(-0.6, -1.3, 0.3, C_BLUE)]
        for n_, par in zip(lv1, [root, root]):
            self.play(FadeIn(n_), ShowCreation(Line(par.get_center(), n_.get_center()).set_stroke(C_GREY, 2)), run_time=0.6)
        for i, n_ in enumerate(lv2):
            par = lv1[i // 2]
            self.play(FadeIn(n_), ShowCreation(Line(par.get_center(), n_.get_center()).set_stroke(C_GREY, 2)), run_time=0.4)
        self.add(tx("…и так до простых кусков", 24, C_GREY).move_to([-3.2, -2.2, 0]))
        side = VGroup(
            tx("Сложное разбирают по индукции:", 30),
            tx("доказал для кусков —", 30),
            tx("получил для целого", 30, C_YEL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(RIGHT * 3.6 + UP * 1.0)
        self.play(FadeIn(side))
        self.add(tx("так же склейку применяет и статья", 24, C_GREEN).move_to(RIGHT * 3.6 + DOWN * 0.5))
        self.add(tx("Бейлинсон–Бернштейн–Делинь придумали это для «перверсных пучков»", 22, C_GREY).move_to(DOWN * 3.0))
        self.play(FadeIn(cap("Склейка позволяет сводить сложное к простому", C_YEL)))
        self.wait(3)


# ---------------- Часть 2: азы (источники: Wikipedia «Zariski topology», учебные конспекты по топологии, Stacks Project) ----------------
class P2(Base):
    def construct(self):
        items = divider(2, "Азы", 1)
        big = tx("Часть 2. Азы: пространство, открытое, замкнутое", 46, C_YEL).move_to(DOWN * 0.8)
        sub = tx("по учебным конспектам по топологии, Wikipedia и Stacks Project", 24, C_GREY).move_to(DOWN * 1.8)
        self.play(FadeIn(items), Write(big), run_time=1.5)
        self.play(FadeIn(sub))
        self.wait(1.2)


class B1(Base):
    def construct(self):
        self.add(head("Что такое пространство"))
        box = Rectangle(width=5.4, height=3.6).set_stroke(WHITE, 3).move_to(LEFT * 3.2 + DOWN * 0.1)
        self.play(ShowCreation(box))
        rng = np.random.default_rng(8)
        pts = VGroup(*[Dot(radius=0.05).set_color(C_GREY).move_to(LEFT * 3.2 + DOWN * 0.1 + np.array([rng.uniform(-2.5, 2.5), rng.uniform(-1.6, 1.6), 0])) for _ in range(90)])
        self.play(FadeIn(pts), run_time=1.2)
        p0 = Dot(radius=0.12).set_color(C_YEL).move_to(LEFT * 3.5 + UP * 0.2)
        self.play(FadeIn(p0, scale=1.6))
        for r in (1.2, 0.7, 0.35):
            c = Circle(radius=r).set_stroke(C_YEL, 3).move_to(p0)
            self.play(ShowCreation(c), run_time=0.8)
            self.play(FadeOut(c), run_time=0.3)
        side = VGroup(
            tx("Пространство", 38, C_YEL),
            tx("= множество точек", 30),
            tx("+ понятие «рядом»", 30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(RIGHT * 3.4 + UP * 1.2)
        self.play(FadeIn(side))
        ex = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.8).set_stroke(C_BLUE, 5), tx("прямая", 26)).arrange(RIGHT, buff=0.3),
            VGroup(Square(side_length=0.5).set_stroke(C_BLUE, 4).set_fill(C_BLUE, 0.2), tx("плоскость", 26)).arrange(RIGHT, buff=0.3),
            VGroup(Circle(radius=0.28).set_stroke(C_BLUE, 4), tx("окружность", 26)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(RIGHT * 3.4 + DOWN * 1.1)
        self.play(LaggedStartMap(FadeIn, ex, lag_ratio=0.4))
        self.play(FadeIn(cap("«Рядом» — это маленькая окрестность вокруг точки", C_YEL)))
        self.wait(3)


class B2(Base):
    def construct(self):
        self.add(head("Открытое и замкнутое: на диске"))
        cs = [LEFT * 4.6, ORIGIN, RIGHT * 4.6]
        r = 1.35
        # открытый диск: край пунктиром и не принадлежит
        op = VGroup(Circle(radius=r).set_stroke(width=0).set_fill(C_BLUE, 0.4), DashedVMobject(Circle(radius=r).set_stroke(C_BLUE, 4), num_dashes=24)).move_to(cs[0] + UP * 0.3)
        cl = Circle(radius=r).set_stroke(C_YEL, 6).set_fill(C_YEL, 0.35).move_to(cs[1] + UP * 0.3)
        hf = VGroup(Annulus(inner_radius=0.6, outer_radius=r).set_stroke(width=0).set_fill(C_GREEN, 0.35), Circle(radius=0.6).set_stroke(C_GREEN, 6), DashedVMobject(Circle(radius=r).set_stroke(C_GREEN, 4), num_dashes=24)).move_to(cs[2] + UP * 0.3)
        names = [("открытое", "края нет", C_BLUE), ("замкнутое", "край есть", C_YEL), ("ни то ни другое", "край только частично", C_GREEN)]
        for pic, c, (a, b, col) in zip([op, cl, hf], cs, names):
            self.play(FadeIn(pic), FadeIn(tx(a, 32, col).move_to(c + DOWN * 1.9)), FadeIn(tx(b, 24, C_GREY).move_to(c + DOWN * 2.4)), run_time=0.9)
        self.add(tx("граница — это край (окружность)", 28, WHITE).move_to(UP * 2.55))
        rule = VGroup(
            tx("замкнутое — содержит всю свою границу", 26, C_YEL),
            tx("открытое — не содержит ни одной точки границы", 26, C_BLUE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(DOWN * 3.3)
        self.play(FadeIn(rule))
        self.wait(3)


class B3(Base):
    def construct(self):
        self.add(head("Как найти границу на практике"))
        c = LEFT * 3.0 + DOWN * 0.2
        disc = Circle(radius=1.8).set_stroke(C_YEL, 6).set_fill(C_YEL, 0.3).move_to(c)
        self.play(FadeIn(disc))
        tests = [
            (c + LEFT * 0.4 + UP * 0.2, 0.55, C_GREEN, "внутри", "кружок целиком внутри множества"),
            (c + RIGHT * 1.8, 0.55, C_RED, "на границе", "кружок и в множестве, и вне его"),
            (c + RIGHT * 2.95 + DOWN * 0.2, 0.4, C_GREY, "снаружи", "кружка в множестве нет"),
        ]
        rows = VGroup()
        for k, (pt, rr, col, a, b) in enumerate(tests):
            d = Dot(radius=0.1).set_color(col).move_to(pt)
            circ = Circle(radius=rr).set_stroke(col, 4).move_to(pt)
            self.play(FadeIn(d), ShowCreation(circ), run_time=0.8)
            row = VGroup(Dot(radius=0.12).set_color(col), tx(a, 30, col), tx(b, 22, WHITE)).arrange(RIGHT, buff=0.25)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(RIGHT * 3.8 + DOWN * 1.3)
        for row in rows:
            self.play(FadeIn(row), run_time=0.6)
        self.add(tx("тест кружком:", 30, C_YEL).move_to(RIGHT * 3.2 + UP * 1.3))
        self.add(tx("встань в точку, нарисуй маленький кружок", 26).move_to(RIGHT * 4.3 + UP * 0.7))
        self.play(FadeIn(cap("Граница — те точки, где кружок любого размера задевает и «внутри», и «снаружи»", C_YEL)))
        self.wait(3)


class B4(Base):
    def construct(self):
        self.add(head("В статье «замкнутое» значит «заданное уравнением»"))
        # слева: прямая
        line = Line(LEFT * 6.3, LEFT * 1.7).shift(UP * 0.7).set_stroke(C_BLUE, 6)
        zero = Dot(radius=0.2).set_color(C_YEL).move_to(LEFT * 4.0 + UP * 0.7)
        self.play(ShowCreation(line), FadeIn(zero))
        self.add(tx("0", 24, C_GREY).move_to(LEFT * 4.0 + DOWN * 0.0))
        self.add(tx("прямая", 28, WHITE).move_to(LEFT * 4.0 + UP * 1.9))
        self.add(tx("Z: точка, где x = 0", 26, C_YEL).move_to(LEFT * 4.0 + DOWN * 0.7))
        self.add(tx("U: вся прямая без этой точки", 26, C_BLUE).move_to(LEFT * 4.0 + DOWN * 1.2))
        # справа: плоскость и окружность
        box = Rectangle(width=4.2, height=3.0).set_stroke(WHITE, 2).set_fill(C_BLUE, 0.22).move_to(RIGHT * 3.6 + UP * 0.5)
        circ = Circle(radius=1.0).set_stroke(C_YEL, 7).move_to(RIGHT * 3.6 + UP * 0.5)
        self.play(FadeIn(box), ShowCreation(circ))
        self.add(tx("плоскость", 28, WHITE).move_to(RIGHT * 3.6 + UP * 2.4))
        self.add(tx("Z: линия, где x² + y² = 1", 26, C_YEL).move_to(RIGHT * 3.6 + DOWN * 1.4))
        self.add(tx("U: вся плоскость вне линии", 26, C_BLUE).move_to(RIGHT * 3.6 + DOWN * 1.9))
        self.play(FadeIn(cap("Z — «тонкая» часть (точка, линия), U — почти всё пространство", C_YEL)))
        self.add(tx("по Wikipedia: Zariski topology", 20, C_GREY).move_to(DOWN * 3.85 + RIGHT * 5.2))
        self.wait(3)


class B5(Base):
    def construct(self):
        self.add(head("Какие требования к пространству"))
        # слева: конечно много карт
        self.add(tx("подходит", 30, C_GREEN).move_to(LEFT * 3.6 + UP * 2.3))
        cols = [C_BLUE, C_YEL, C_GREEN]
        charts = VGroup(*[Rectangle(width=2.4, height=1.8).set_stroke(c, 4).set_fill(c, 0.25).move_to(LEFT * (5.0 - 1.4 * k) + UP * (0.9 - 0.25 * k)) for k, c in enumerate(cols)])
        self.play(LaggedStartMap(FadeIn, charts, lag_ratio=0.4))
        self.add(tx("конечно много карт-кусков,", 24).move_to(LEFT * 3.6 + DOWN * 0.7), tx("их пересечения устроены просто", 24).move_to(LEFT * 3.6 + DOWN * 1.1))
        self.play(ShowCreation(check().scale(0.8).move_to(LEFT * 3.6 + DOWN * 1.7)))
        # справа: бесконечное дробление
        self.add(tx("не подходит", 30, C_RED).move_to(RIGHT * 3.6 + UP * 2.3))
        rng = np.random.default_rng(3)
        bits = VGroup(*[Square(side_length=rng.uniform(0.1, 0.28)).set_stroke(C_RED, 2).set_fill(C_RED, 0.25).move_to(RIGHT * 3.6 + UP * 0.5 + np.array([rng.uniform(-1.9, 1.9), rng.uniform(-1.0, 1.0), 0])) for _ in range(60)])
        self.play(FadeIn(bits, lag_ratio=0.02), run_time=1.5)
        self.add(tx("бесконечное дробление", 24).move_to(RIGHT * 3.6 + DOWN * 0.7), tx("на мелкие куски", 24).move_to(RIGHT * 3.6 + DOWN * 1.1))
        self.play(ShowCreation(cross().scale(0.8).move_to(RIGHT * 3.6 + DOWN * 1.7)))
        self.add(tx("в статье: «квазикомпактное, квазиотделимое алгебраическое пространство»", 22, C_YEL).move_to(DOWN * 2.3))
        self.add(tx("пояснение для ролика; определения — в Stacks Project", 20, C_GREY).move_to(DOWN * 2.8))
        self.play(FadeIn(cap("Это «обычные» пространства; странные — с бесконечным дроблением — не подходят", C_YEL, -3.65)))
        self.wait(3)


class B6(Base):
    def construct(self):
        self.add(head("На практике: подставь точку в уравнение"))
        c = LEFT * 3.4 + DOWN * 0.1
        box = Rectangle(width=4.6, height=3.6).set_stroke(WHITE, 2).set_fill(C_BLUE, 0.2).move_to(c)
        circ = Circle(radius=1.0).set_stroke(C_YEL, 6).move_to(c)
        self.play(FadeIn(box), ShowCreation(circ))
        self.add(tx("уравнение: x² + y² = 1", 30, C_YEL).move_to(RIGHT * 3.4 + UP * 2.4))
        pts = [((1, 0), "1 + 0 = 1", True), ((0, 0), "0 + 0 = 0", False), ((2, 1), "4 + 1 = 5", False)]
        rows = VGroup()
        for (x, y), calc, inz in pts:
            col = C_YEL if inz else C_BLUE
            d = Dot(radius=0.12).set_color(WHITE).move_to(c + np.array([x * 1.0, y * 1.0, 0]))
            self.play(FadeIn(d, scale=1.6), run_time=0.6)
            row = VGroup(tx(f"({x}, {y})", 28), tx(calc, 28, C_GREY), tx("→ в Z" if inz else "→ в U", 30, col)).arrange(RIGHT, buff=0.4)
            rows.add(row)
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(RIGHT * 3.4 + UP * 0.9)
            self.play(FadeIn(row), d.animate.set_color(col), run_time=0.7)
        self.play(FadeIn(cap("Равно 1 — точка в Z. Не равно — в U. Вот и вся проверка", C_YEL)))
        self.wait(3)
