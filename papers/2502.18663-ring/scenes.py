"""Ролик по статье arXiv 2502.18663 (Chervov, Obozov и др., «CayleyPy RL: Pathfinding and Reinforcement Learning on Cayley Graphs»)
простыми словами.

Единый источник правил — паспорт passport.py в этой папке: законы сценария, вопрос, станции полосы «мы здесь»,
словарь, палитра, план сцен. Весь рассказ идёт на одном кольце с шариками и башне его расстановок (единство места).

Основной мир — кольцо (в статье это граф Кэли LRX симметрической группы):
  • расстановка — перестановка; ходы — L (влево), R (вправо), X (обмен в окошке — первые два места);
  • этаж — расстояние до порядка, потолок — диаметр графа, зеркало — предполагаемый самый дальний элемент ℓn;
  • компас и фронт — как в ролике про кубики (нейросеть по диффузионному расстоянию и лучевой поиск).
Башня этажей посчитана перебором (ring3d.floors) для 5 шариков; числа результатов — из таблиц 2–6 статьи.
Запуск (из корня репозитория): uv run manimgl papers/2502.18663-ring/scenes.py A03 -w --hd
Весь ролик с озвучкой: uv run python core/pipeline/build.py papers/2502.18663-ring"""
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())  # корень репозитория, откуда бы ни лежал файл
sys.path.insert(0, str(ROOT / "core"))  # общая часть: manimkit
sys.path.insert(0, str(HERE))           # своя часть статьи: паспорт, кольцо, башня
import numpy as np
from manimlib import *
from manimkit import *
import passport as P
from ring3d import Ring, ball, tower, tower_dots, floors, mirror, pairs, left, right, swap

Base = story_base(P.STATIONS, P.SCENES)  # темп под речь + полоса «мы здесь»
STATION_OF = {code: st for code, st, *_ in P.SCENES}


class Base3D(ThreeDScene):
    """3D-сцена ролика: тот же темп под речь (SLOW) и та же полоса «мы здесь», закреплённая в кадре."""
    SLOW = float(os.environ.get("SLOW", 1.6))

    def setup(self):
        super().setup()
        self.camera.background_rgba = [0.059, 0.067, 0.082, 1]
        st = STATION_OF.get(type(self).__name__)
        if st:
            self.add(story_bar(P.STATIONS, P.STATIONS.index(st)).fix_in_frame())
        self._lab = None

    def play(self, *args, run_time=1.0, **kwargs):
        super().play(*args, run_time=run_time * self.SLOW, **kwargs)

    def wait(self, duration=1.0, *args, **kwargs):
        super().wait(duration * self.SLOW, *args, **kwargs)

    def say(self, s, color=None):
        """Подпись внизу: сначала убрать старую, потом показать новую."""
        if self._lab is not None:
            self.play(FadeOut(self._lab), run_time=0.3)
        self._lab = note(s, color or C_NOTE).fix_in_frame()
        self.play(FadeIn(self._lab), run_time=0.5)


# палитра паспорта: один цвет — один смысл
C_RING = "#58a6ff"    # кольцо, шарики, расстановки, ходы
C_ORDER = "#3fb950"   # порядок и найденный путь
C_MIRROR = "#f778ba"  # зеркало и потолок
C_WALK = "#f0883e"    # прогулки
C_COMP = "#e3b341"    # компас
C_FRONT = "#d2a8ff"   # фронт и подсказка
C_NO = "#f85149"      # длинные пути, ошибка
C_NOTE = "#8b949e"    # подписи, справка
C_FORM = WHITE


def lab(s, size=26, color=WHITE):
    return tx(s, size, color).fix_in_frame()


def ring_icon(n=6, R=0.45, color=C_RING, s=None):
    """Плоский значок кольца: обод, окошко, шарики-точки (без номеров)."""
    g = VGroup(Circle(radius=R).set_stroke(C_NOTE, 2))
    for k in range(n):
        a = PI / 2 + PI / n - TAU * k / n
        g.add(Dot(R * np.array([np.cos(a), np.sin(a), 0]), radius=R * 0.16).set_color(color))
    w = RoundedRectangle(width=R * 1.2, height=R * 0.45, corner_radius=0.05).set_stroke(WHITE, 1.5).move_to(UP * R)
    return g.add(w)


def compass(r=0.45, color=C_COMP):
    ring = Circle(radius=r).set_stroke(color, 4).set_fill(color, 0.1)
    a = rotate_vector(UP, -PI / 5)
    side = rotate_vector(a, PI / 2) * r * 0.22
    tip = Polygon(a * r * 0.85, side, -side).set_stroke(width=0).set_fill(color, 1)
    back = Polygon(-a * r * 0.85, side, -side).set_stroke(width=0).set_fill(C_NOTE, 1)
    return VGroup(ring, back, tip, Dot(radius=r * 0.08).set_color(BG))


def front_icon(s=1.0):
    g = VGroup(*[Dot(radius=0.11 * s).set_color(C_FRONT) for _ in range(5)]).arrange(RIGHT, buff=0.1 * s)
    return VGroup(g, Arrow(UP * 0.5 * s, DOWN * 0.3 * s, buff=0).set_color(C_FRONT).next_to(g, DOWN, buff=0.05))


def hbar(value, vmax, length, color, thick=0.36):
    w = max(0.03, length * value / vmax)
    return Rectangle(width=w, height=thick).set_stroke(color, 2).set_fill(color, 0.55)


def app_tag():
    return pill("приложение", C_NOTE, 20).to_corner(UL, buff=0.35)


def formal_card(scene, title, picture, formula, explain, analogy, extra=None):
    """Карточка приложения: слева значок из рассказа, справа формула, под ней пояснение и аналогия."""
    scene.add(head(title), app_tag())
    pic = picture.move_to(LEFT * 4.9 + UP * 0.5)
    scene.play(FadeIn(pic), run_time=0.8)
    eq = (formula if isinstance(formula, Mobject) else tx(formula, 38, C_FORM)).move_to(RIGHT * 1.4 + UP * 1.0)
    scene.play(Write(eq), run_time=1.2)
    ex = tx(explain, 25).move_to(RIGHT * 1.4 + DOWN * 0.3)
    scene.play(FadeIn(ex))
    if extra is not None:
        scene.play(FadeIn(extra.move_to(RIGHT * 1.4 + DOWN * 1.15)))
    an = VGroup(tx("≈", 34, C_COMP), tx(analogy, 25, C_COMP)).arrange(RIGHT, buff=0.25).move_to(DOWN * 2.2)
    scene.play(FadeIn(an))
    scene.wait(2)


def shown(s):
    """Номера на шариках — с единицы (в статье — с нуля)."""
    return tuple(v + 1 for v in s)


TOWER_SHIFT = LEFT * 2.2 + IN * 2.5  # башня 5 шариков: этажи 0…10 по высоте


def tower_scene(scene, phi=72, theta=-20, height=None):
    """Башня 5 шариков: точки-расстановки, линии-ходы. Камера сбоку."""
    pos, lines, d, by = tower(5, rise=0.5)
    dots = tower_dots(pos, d)
    grp = Group(lines, dots).shift(TOWER_SHIFT)
    scene.frame.reorient(theta, phi)
    if height:
        scene.frame.set_height(height)
    return pos, lines, dots, d, by, grp


def P3(pos, s):
    return pos[s] + TOWER_SHIFT


# ---------- акт 1 — вопрос и мир ----------

class A01(Base3D):
    """О чём ролик: кольцо с шариками, три хода, окошко; какую расстановку распутывать дольше всех; ставка — задача 1968 года."""
    def construct(self):
        fr = self.frame
        fr.reorient(-10, 28)
        q = lab("Какую расстановку распутывать дольше всех?", 34).to_edge(UP, buff=0.4)
        ring = Ring(range(6), R=2.0, r=0.38, center=UP * 0.2)
        self.play(Write(q), FadeIn(ring.group, scale=0.85), run_time=1.5)
        self.play(fr.animate.reorient(8, 30), run_time=1.5)
        for name, sign in (("влево", "↺ влево"), ("вправо", "↻ вправо"), ("обмен", "⇄ обмен в окошке")):
            self.say(f"ход: {sign}", C_RING)
            self.play(ring.move(name), run_time=1.0)
        self.play(ShowPassingFlash(ring.window.copy().set_stroke(WHITE, 8)), run_time=0.8)
        self.say("расстановка — как шарики стоят по кругу", C_RING)
        rnd = random.Random(3)
        for _ in range(7):
            self.play(ring.move(rnd.choice(["влево", "вправо", "обмен"])), run_time=0.35)
        self.say("как ни перемешай — по порядку можно вернуть", C_ORDER)
        self.play(ring.set_to(range(6)), ring.paint(C_ORDER), run_time=1.4)
        self.play(ring.paint(C_RING), fr.animate.reorient(-6, 26), run_time=0.8)
        self.play(FadeOut(self._lab), run_time=0.3)
        self._lab = None
        stake = VGroup(pill("1968", C_NOTE, 24), tx("кибернетик Глушков: родственная задача", 24),
                       pill("до сих пор открыта", C_NO, 22)).arrange(RIGHT, buff=0.3).move_to(DOWN * 3.0).fix_in_frame()
        self.play(LaggedStartMap(FadeIn, stake, lag_ratio=0.35), run_time=1.5)
        self.wait(2)


class A02(Base):
    """Карточка статьи. Вход: кольцо уходит в угол. Выход: кольцо возвращается в центр."""
    def construct(self):
        ic = ring_icon(6, 1.2).move_to(UP * 0.3)
        self.add(ic)
        self.play(ic.animate.scale(0.45).to_corner(UL, buff=0.5), run_time=1)
        card = RoundedRectangle(width=10.6, height=4.7, corner_radius=0.2).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.06).move_to(RIGHT * 0.9 + UP * 0.5)
        lines = VGroup(
            tx("arXiv 2502.18663 · 25 февраля 2025 · журнал ATMP, 2026", 22, C_NOTE),
            tx("CayleyPy RL: Pathfinding and Reinforcement Learning on Cayley Graphs", 26),
            tx("«Поиск путей и обучение с подкреплением на графах Кэли»", 22, C_NOTE),
            tx("А. Червов · М. Обозов · и ещё 32 автора · проект CayleyPy", 24),
            tx("та же команда, что и в ролике про кубики Рубика", 20, C_NOTE),
        ).arrange(DOWN, buff=0.22).move_to(card.get_center() + UP * 0.8)
        self.play(FadeIn(card), FadeIn(lines[0]), Write(lines[1]), run_time=1.5)
        self.play(FadeIn(lines[2]), FadeIn(lines[3]), FadeIn(lines[4]))
        icons = [(VGroup(*[Square(0.12).set_stroke(C_RING, 1.5) for _ in range(9)]).arrange_in_grid(3, 3, buff=0.04), "перебор"),
                 (compass(0.25), "обученная программа"),
                 (VGroup(*[Dot(radius=0.04).set_color(C_NOTE) for _ in range(15)]).arrange_in_grid(3, 5, buff=0.06), "соревнование"),
                 (tx("∎", 34, WHITE), "доказательства")]
        row = VGroup(*[VGroup(i, tx(t, 18, C_NOTE)).arrange(DOWN, buff=0.1) for i, t in icons]).arrange(RIGHT, buff=0.55)
        goal = pill("одна простая формула", C_ORDER, 22)
        gist = VGroup(row, Arrow(LEFT * 0.4, RIGHT * 0.4).set_color(WHITE), goal).arrange(RIGHT, buff=0.3)
        gist.move_to(card.get_center() + DOWN * 1.45)
        self.play(Indicate(lines[4], color=WHITE), run_time=0.8)
        for item in row:
            self.play(FadeIn(item, shift=UP * 0.15), run_time=0.5)
        self.play(GrowArrow(gist[1]), FadeIn(goal), run_time=0.8)
        self.play(Indicate(goal, color=C_ORDER), run_time=0.8)
        self.wait(0.5)
        # переходник обратно в мир: карточка уходит, кольцо возвращается в центр
        self.play(FadeOut(VGroup(card, lines, gist)), ic.animate.scale(1 / 0.45).move_to(UP * 0.3), run_time=1.2)
        self.wait(0.5)


class A03(Base3D):
    """Башня: все 120 расстановок пяти шариков по этажам (этаж = ходов до порядка); потолок — 10-й этаж, на нём одна расстановка."""
    def construct(self):
        fr = self.frame
        self.add(lab("Все расстановки пяти шариков", 36).to_edge(UP, buff=0.35))
        pos, lines, dots, d, by, grp = tower_scene(self, phi=70, theta=-25)
        fr.move_to(LEFT * 0.6 + OUT * 0.2)
        top = max(by)
        # справа — столбик «этаж: сколько расстановок», растёт вместе с башней
        bars = VGroup()
        for f in range(top + 1):
            m = len(by[f])
            col = C_ORDER if f == 0 else C_MIRROR if f == top else C_RING
            row = VGroup(tx(str(f), 18, C_NOTE), hbar(m, 29, 2.6, col, 0.2), tx(str(m), 18, col)).arrange(RIGHT, buff=0.15)
            bars.add(row)
        bars.arrange(UP, aligned_edge=LEFT, buff=0.08).move_to(RIGHT * 4.3 + DOWN * 0.1).fix_in_frame()
        hdr = lab("этаж · сколько расстановок", 18, C_NOTE).next_to(bars, UP, buff=0.2)
        self.say("этаж — сколько ходов до порядка", C_RING)
        self.play(FadeIn(hdr), run_time=0.5)
        dot_of = {s: dots[i] for i, s in enumerate(pos)}
        for f in range(top + 1):
            layer = Group(*[dot_of[s] for s in by[f]])
            ls = VGroup(*[l for l in lines if abs(l.get_start()[2] - (f * 0.5)) < 1e-6 and l.get_end()[2] <= f * 0.5 + 1e-6
                          or abs(l.get_end()[2] - f * 0.5) < 1e-6 and l.get_start()[2] <= f * 0.5 + 1e-6])
            self.play(FadeIn(layer, scale=0.5), ShowCreation(ls), FadeIn(bars[f]), run_time=0.45)
            if f == 0:
                self.say("внизу — сам порядок · три соседки на первом этаже", C_ORDER)
        self.add(lines)
        self.play(fr.animate.reorient(25, 72), run_time=2.5)
        cnt = lab("120 расстановок", 26, C_RING).next_to(bars, DOWN, buff=0.25)
        self.play(FadeIn(cnt), run_time=0.5)
        self.say("потолок — верхний этаж: столько ходов хватает на любую расстановку", C_MIRROR)
        topdot = dot_of[[s for s in by[top]][0]]
        self.play(Flash(topdot, color=C_MIRROR, flash_radius=0.4), topdot.animate.scale(1.6), run_time=1.0)
        cap10 = lab("потолок: 10 ходов · на нём ровно одна", 26, C_MIRROR).to_edge(UP, buff=1.15)
        self.play(FadeIn(cap10), fr.animate.reorient(-15, 66), run_time=2)
        self.wait(1.5)


class A04(Base3D):
    """Перебор до 15 шариков: на потолке всегда одна расстановка — зеркало (отражение через окошко); задом наперёд — на два этажа ниже."""
    def construct(self):
        fr = self.frame
        fr.reorient(0, 24)
        self.add(lab("Кто стоит на потолке?", 36).to_edge(UP, buff=0.35))
        # перебор: счётчик расстановок растёт с числом шариков
        rows = VGroup()
        import math
        for n in range(4, 16):
            rows.add(VGroup(tx(f"{n} шариков", 18, C_NOTE), tx(f"{math.factorial(n):,}".replace(",", " "), 18, C_RING)).arrange(RIGHT, buff=0.25))
        rows.arrange(DOWN, aligned_edge=RIGHT, buff=0.05).move_to(RIGHT * 3.6 + UP * 0.6).fix_in_frame()
        self.say("перебор: обойти все расстановки", C_RING)
        self.play(LaggedStartMap(FadeIn, rows, lag_ratio=0.25), run_time=2.5)
        big = lab("больше триллиона · несколько дней счёта", 22, C_RING).next_to(rows, DOWN, buff=0.2)
        self.play(Indicate(rows[-1], color=C_RING), FadeIn(big), run_time=1)
        # каждый раз наверху одна — зеркало: кольцо из шести шариков отражается через окошко
        ring = Ring(range(6), R=1.8, r=0.34, center=LEFT * 2.4 + UP * 0.1)
        axis = DashedLine(ring.c + UP * 2.5, ring.c + DOWN * 2.0).set_stroke(C_MIRROR, 3)
        self.play(FadeIn(ring.group), run_time=1)
        self.say("зеркало: кольцо, отражённое через окошко", C_MIRROR)
        self.play(ShowCreation(axis), run_time=0.8)
        balls = Group(*ring.balls.values())
        self.play(Rotate(balls, PI, axis=UP, about_point=ring.c), fr.animate.reorient(-25, 40), run_time=2.2)
        for b in ring.balls.values():  # после отражения номер снова спереди шарика и читается слева направо
            b[1].rotate(PI, axis=UP).move_to(b[0].get_center() + OUT * (ring.r + 0.02))
        ring.s = mirror(6)
        self.play(ring.paint(C_MIRROR), fr.animate.reorient(0, 24), run_time=1.0)
        top = lab("на потолке всегда одна-единственная", 24, C_MIRROR).next_to(rows, DOWN, buff=0.75)
        self.play(FadeIn(top), run_time=0.6)
        self.wait(0.6)
        # задом наперёд — на два этажа ниже
        d6 = floors(6)
        cmp = VGroup(
            VGroup(tx("зеркало", 22, C_MIRROR), tx(" ".join(map(str, shown(mirror(6)))), 24, C_MIRROR),
                   pill(f"этаж {d6[mirror(6)]}", C_MIRROR, 20)).arrange(RIGHT, buff=0.3),
            VGroup(tx("задом наперёд", 22, C_RING), tx(" ".join(map(str, shown(tuple(range(5, -1, -1))))), 24, C_RING),
                   pill(f"этаж {d6[tuple(range(5, -1, -1))]}", C_RING, 20)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, aligned_edge=RIGHT, buff=0.25).move_to(RIGHT * 3.4 + DOWN * 2.3).fix_in_frame()
        self.play(FadeOut(self._lab), run_time=0.3)
        self._lab = None
        self.play(FadeIn(cmp[0]), run_time=0.6)
        self.play(FadeIn(cmp[1]), run_time=0.6)
        self.play(Indicate(cmp[1][2], color=C_RING), run_time=0.8)
        self.wait(1.5)


class A05(Base3D):
    """Пары: 5 шариков — 10 линий, потолок тоже 10; 6 — 15 и 15; совпадает везде, где был перебор (от 4 шариков) → гипотеза."""
    def construct(self):
        fr = self.frame
        fr.reorient(0, 20)
        self.add(lab("Посчитаем пары", 36).to_edge(UP, buff=0.35))

        def chords(ring, n):
            ls = VGroup()
            for i in range(n):
                for j in range(i + 1, n):
                    ls.add(Line(ring.pos(i), ring.pos(j)).set_stroke(C_ORDER, 2.5, opacity=0.8))
            return ls

        r5 = Ring(range(5), R=1.5, r=0.3, center=LEFT * 3.4 + UP * 0.3, window=False, labels=False)
        self.play(FadeIn(r5.group), run_time=0.8)
        c5 = chords(r5, 5)
        cnt = Integer(0, font_size=40).set_color(C_ORDER).fix_in_frame().move_to(LEFT * 5.9 + UP * 0.3)
        self.add(cnt)
        self.say("пять шариков — десять пар", C_ORDER)
        for k, l in enumerate(c5):
            self.play(ShowCreation(l), cnt.animate.set_value(k + 1), run_time=0.25)
        eq5 = lab("пар 10 = потолок 10", 26).move_to(LEFT * 3.4 + DOWN * 2.35)
        self.play(FadeIn(eq5), run_time=0.6)
        r6 = Ring(range(6), R=1.5, r=0.3, center=RIGHT * 0.4 + UP * 0.3, window=False, labels=False)
        c6 = chords(r6, 6)
        self.play(FadeIn(r6.group), run_time=0.6)
        self.play(LaggedStartMap(ShowCreation, c6, lag_ratio=0.15), run_time=2)
        eq6 = lab("пар 15 = потолок 15", 26).move_to(RIGHT * 0.4 + DOWN * 2.35)
        self.play(FadeIn(eq6), run_time=0.6)
        self.play(fr.animate.reorient(-12, 32), run_time=1.5)
        # совпадает на всех кольцах перебора
        d = {4: 6, 5: 10, 6: 15, 7: 21, 8: 28, 9: 36, 10: 45, 11: 55, 12: 66, 13: 78, 14: 91, 15: 105}  # потолок по перебору (OEIS A186783)
        tbl = VGroup(*[VGroup(tx(str(n), 20, C_NOTE), tx(str(pairs(n)), 20, C_ORDER), tx(str(v), 20, C_MIRROR),
                              check(C_ORDER, 0.09)).arrange(RIGHT, buff=0.22) for n, v in d.items()])
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.06).to_edge(RIGHT, buff=0.5).shift(UP * 0.1).fix_in_frame()
        th = lab("шариков · пар · потолок", 16, C_NOTE).next_to(tbl, UP, buff=0.15)
        self.say("совпадает везде, где был перебор — с четырёх шариков", C_ORDER)
        self.play(FadeIn(th), LaggedStartMap(FadeIn, tbl, lag_ratio=0.15), run_time=2.2)
        self.play(FadeOut(self._lab), run_time=0.3)
        self._lab = None
        hyp = pill("гипотеза: потолок = число пар шариков", C_MIRROR, 26).move_to(DOWN * 3.0).fix_in_frame()
        self.play(FadeIn(hyp, scale=0.9), run_time=0.8)
        self.wait(2)


# ---------- акт 2 — поиск, ответ ----------

class A06(Base3D):
    """Дальше перебор невозможен (20 шариков — 2,4·10^18 расстановок); проверка — распутать зеркало;
    классическая программа: 20 шариков → 217 944 хода за 41 мин, а пар 190 (таблица 2 статьи)."""
    def construct(self):
        fr = self.frame
        fr.reorient(0, 22)
        self.add(lab("Двадцать шариков", 36).to_edge(UP, buff=0.35))
        ring = Ring(mirror(20), R=1.6, r=0.15, center=LEFT * 4.3 + UP * 0.2, color=C_MIRROR, labels=False)
        self.play(FadeIn(ring.rim), run_time=0.4)
        self.play(LaggedStartMap(FadeIn, Group(*ring.balls.values()), lag_ratio=0.1), FadeIn(ring.window), run_time=1.6)
        self.play(fr.animate.reorient(15, 30), run_time=1.2)
        big = VGroup(tx("2 432 902 008 176 640 000", 28, C_RING), tx("расстановок", 22, C_RING)).arrange(DOWN, buff=0.08)
        nob = VGroup(tx("перебор", 24, C_NOTE), cross(C_NO, 0.15)).arrange(RIGHT, buff=0.2)
        head_r = VGroup(big, nob).arrange(DOWN, buff=0.2).move_to(RIGHT * 2.0 + UP * 2.2).fix_in_frame()
        self.play(FadeIn(big), run_time=0.8)
        self.play(FadeIn(nob), run_time=0.5)
        self.say("проверка: распутать зеркало — путь не короче числа пар?", C_MIRROR)
        # столбики пути: зелёный — пар, красный — путь классической программы; красный растёт вверх до края кадра
        base_y = -2.1
        g = Prism(0.7, 0.04, 0.5).set_color(C_ORDER).move_to([-0.6, base_y, 0])
        rb = Prism(0.7, 0.04, 0.5).set_color(C_NO).move_to([1.0, base_y, 0])
        gl = lab("пар: 190", 24, C_ORDER).move_to([-0.6, base_y - 0.45, 0])
        rl = lab("классическая программа", 22, C_NO).move_to([1.0 + 0.6, base_y - 0.45, 0])
        self.play(fr.animate.reorient(0, 22), run_time=1)
        self.play(FadeIn(g), FadeIn(gl), run_time=0.8)
        self.play(Indicate(gl, color=C_ORDER), run_time=0.6)
        self.play(FadeIn(rb), FadeIn(rl), run_time=0.8)
        clock = VGroup(Circle(radius=0.35).set_stroke(C_NOTE, 3), Line(ORIGIN, UP * 0.28).set_stroke(C_NOTE, 3))
        clock.move_to(RIGHT * 2.6 + DOWN * 1.2).fix_in_frame()
        self.play(FadeOut(head_r), FadeIn(clock), run_time=0.6)
        self.play(rb.animate.stretch(110, 1, about_edge=DOWN), Rotate(clock[1], -TAU * 2, about_point=clock[0].get_center()),
                  fr.animate.reorient(-12, 24), run_time=4)
        self.play(FadeOut(clock), run_time=0.4)
        res = VGroup(tx("217 944 хода", 34, C_NO), tx("41 минута", 26, C_NOTE), tx("в 1147 раз длиннее пар", 22, C_NO),
                     tx("не в масштабе: столбик выше кадра", 18, C_NOTE)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        res.move_to(RIGHT * 4.4 + UP * 0.6).fix_in_frame()
        for r in res:
            self.play(FadeIn(r, shift=LEFT * 0.15), run_time=0.6)
        self.play(Indicate(gl, color=C_ORDER), fr.animate.reorient(8, 26), run_time=1.2)
        self.wait(1)


class A07(Base3D):
    """Компас из прошлого ролика: прогулки от порядка (случайные ходы с записью «расстановка → шаг»), компас угадывает этаж; ошибается, но даёт направление."""
    def construct(self):
        fr = self.frame
        self.add(lab("Компас из прошлого ролика", 36).to_edge(UP, buff=0.35))
        pos, lines, dots, d, by, grp = tower_scene(self, phi=70, theta=-20)
        fr.move_to(LEFT * 0.4 + OUT * 0.2)
        self.play(FadeIn(grp), run_time=1.2)
        # прогулка: случайные ходы от порядка, без шага назад
        rnd = random.Random(11)
        s, prev, path = tuple(range(5)), None, [tuple(range(5))]
        for _ in range(12):
            opts = [f(s) for f in (left, right, swap) if f(s) != prev]
            prev, s = s, rnd.choice(opts)
            path.append(s)
        self.say("прогулка: от порядка — случайные ходы, записываем шаг", C_WALK)
        log = VGroup()
        for k, (a, b) in enumerate(zip(path, path[1:]), 1):
            seg = Line(P3(pos, a), P3(pos, b)).set_stroke(C_WALK, 5)
            dot = Sphere(radius=0.09, resolution=(12, 6)).set_color(C_WALK).move_to(P3(pos, b))
            row = VGroup(tx(" ".join(map(str, shown(b))), 17, C_RING), tx(f"→ шаг {k}", 17, C_WALK)).arrange(RIGHT, buff=0.2)
            log.add(row)
            self.play(ShowCreation(seg), FadeIn(dot), run_time=0.3)
        log.arrange(DOWN, aligned_edge=LEFT, buff=0.05).to_edge(RIGHT, buff=0.4).shift(UP * 0.1).fix_in_frame()
        self.play(LaggedStartMap(FadeIn, log, lag_ratio=0.1), fr.animate.reorient(15, 72), run_time=1.6)
        end = path[-1]
        comp = compass(0.4).fix_in_frame().move_to(LEFT * 5.4 + UP * 1.6)
        self.say("компас: смотрит на расстановку и угадывает этаж", C_COMP)
        self.play(FadeIn(comp, scale=0.6), run_time=0.6)
        guess = VGroup(tx(f"прогулка: шаг {len(path) - 1}", 22, C_WALK), tx(f"на деле: этаж {d[end]}", 22, C_ORDER)).arrange(DOWN, buff=0.1)
        guess.next_to(comp, DOWN, buff=0.2).fix_in_frame()
        self.play(FadeIn(guess[0]), Indicate(log[-1], color=C_WALK), run_time=0.8)
        self.play(FadeIn(guess[1]), run_time=0.6)
        self.say("прогулка петляет — компас ошибается, но направление показывает", C_COMP)
        arrow = Arrow(P3(pos, end), P3(pos, tuple(range(5))) + OUT * 0.3, buff=0.2).set_color(C_COMP)
        self.play(GrowArrow(arrow), fr.animate.reorient(-10, 68), run_time=1.6)
        self.wait(1.5)


class A08(Base3D):
    """Фронт: держим много многообещающих расстановок; 20 шариков → ровно 190 ходов за ~4 мин; до 28 — ровно число пар; до 44 — длиннее (таблицы 2–3)."""
    def construct(self):
        fr = self.frame
        self.add(lab("Поиск фронтом", 36).to_edge(UP, buff=0.35))
        pos, lines, dots, d, by, grp = tower_scene(self, phi=70, theta=20)
        fr.move_to(LEFT * 0.4 + OUT * 0.2)
        self.add(grp)
        top = max(by)
        start = by[top][0]
        # одиночный путь по компасу упирается в тупик (схема)
        rnd = random.Random(5)
        s, lone = start, [start]
        for _ in range(4):
            s = rnd.choice([f(s) for f in (left, right, swap) if d[f(s)] <= d[s]])
            lone.append(s)
        self.say("один путь: ошибка компаса — и тупик", C_NO)
        segs = VGroup(*[Line(P3(pos, a), P3(pos, b)).set_stroke(C_NO, 5) for a, b in zip(lone, lone[1:])])
        self.play(ShowCreation(segs), run_time=1.4)
        x = cross(C_NO, 0.15).fix_in_frame().move_to(LEFT * 4.8 + UP * 1.4)
        self.play(FadeIn(x), run_time=0.4)
        self.play(FadeOut(segs), FadeOut(x), run_time=0.5)
        # фронт: этаж за этажом держим несколько лучших и спускаемся
        self.say("фронт: держим много многообещающих сразу и пробуем все ходы", C_FRONT)
        cur = [start]
        fronts = []
        while True:
            nb = sorted({f(s) for s in cur for f in (left, right, swap)}, key=lambda t: (d[t], t))
            cur = nb[:6]
            mark = Group(*[Sphere(radius=0.13, resolution=(12, 6)).set_color(C_FRONT).move_to(P3(pos, t)) for t in cur])
            fronts.append(mark)
            self.play(FadeIn(mark, scale=0.5), *([FadeOut(fronts[-2])] if len(fronts) > 1 else []), run_time=0.35)
            if tuple(range(5)) in cur:
                break
        self.play(FadeOut(fronts[-1]), run_time=0.3)
        # найденный путь — кратчайший: спуск на один этаж за ход
        s, best = start, [start]
        while d[s] > 0:
            s = min((f(s) for f in (left, right, swap)), key=lambda t: d[t])
            best.append(s)
        path = VGroup(*[Line(P3(pos, a), P3(pos, b)).set_stroke(C_ORDER, 7) for a, b in zip(best, best[1:])])
        self.play(ShowCreation(path), fr.animate.reorient(-15, 70), run_time=1.8)
        # итог на двадцати шариках
        self.play(FadeOut(self._lab), run_time=0.3)
        self._lab = None
        res = VGroup(tx("20 шариков", 24, WHITE), tx("190 ходов = числу пар", 26, C_ORDER),
                     tx("≈ 4 минуты (было 41)", 22, C_NOTE)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        res.move_to(RIGHT * 3.6 + UP * 1.4).fix_in_frame()
        self.play(LaggedStartMap(FadeIn, res, lag_ratio=0.4), run_time=1.3)
        # полоса шариков: до 28 — ровно, до 44 — длиннее
        ns = [9, 12, 16, 20, 24, 28, 31, 34, 38, 44]
        exact = {n: n <= 28 for n in ns}
        strip = VGroup()
        for n in ns:
            col = C_ORDER if exact[n] else C_NO
            strip.add(VGroup(Dot(radius=0.11).set_color(col), tx(str(n), 16, col)).arrange(DOWN, buff=0.06))
        strip.arrange(RIGHT, buff=0.22).move_to(RIGHT * 3.6 + DOWN * 0.9).fix_in_frame()
        sl = VGroup(tx("ровно число пар", 18, C_ORDER).next_to(strip[:6], DOWN, buff=0.15),
                    tx("длиннее", 18, C_NO).next_to(strip[6:], DOWN, buff=0.15),
                    tx("шариков:", 18, C_NOTE).next_to(strip, UP, buff=0.15)).fix_in_frame()
        self.play(LaggedStartMap(FadeIn, strip, lag_ratio=0.15), FadeIn(sl), run_time=1.8)
        self.wait(1.5)


class A09(Base3D):
    """Подсказка в одну строчку: не менять шарики в окошке, если они уже по порядку; предел — с 40 до 100 шариков;
    для 100 — 9 часов, путь 16 632 при 4 950 парах (таблица 4); подсказка — только для этого кольца."""
    def construct(self):
        fr = self.frame
        fr.reorient(0, 26)
        self.add(lab("Подсказка в одну строчку", 36).to_edge(UP, buff=0.35))
        ring = Ring((2, 3, 0, 5, 1, 4), R=1.7, r=0.34, center=LEFT * 3.0 + UP * 0.2)
        self.play(FadeIn(ring.group), run_time=0.8)
        rule = pill("в окошке уже по порядку → не меняем", C_FRONT, 24).move_to(UP * 2.3 + RIGHT * 2.3).fix_in_frame()
        self.say("подсказка: не менять шарики в окошке, если они уже по порядку", C_FRONT)
        self.play(FadeIn(rule), ring.window.animate.set_stroke(C_FRONT, 6), run_time=0.8)
        x = cross(C_FRONT, 0.2).move_to(ring.window.get_center() + UP * 0.75)
        self.play(FadeIn(x, scale=1.5), run_time=0.6)
        self.play(FadeOut(x), FadeOut(ring.group), FadeOut(ring.window), run_time=0.5)
        # предел: кольцо растёт с 40 до 100 шариков
        r40 = Ring(range(40), R=1.9, r=0.1, center=LEFT * 3.0 + UP * 0.2, labels=False, window=False)
        r100 = Ring(range(100), R=2.1, r=0.06, center=LEFT * 3.0 + UP * 0.2, labels=False, window=False)
        n_lab = Integer(40, font_size=48).set_color(C_RING).fix_in_frame().move_to(LEFT * 3.0 + UP * 0.2)
        self.say("предел: с 40 шариков до 100", C_RING)
        self.play(FadeIn(r40.group), FadeIn(n_lab), run_time=0.8)
        self.play(FadeOut(r40.group), FadeIn(r100.group), n_lab.animate.set_value(100), fr.animate.reorient(-15, 34), run_time=2.2)
        res = VGroup(
            VGroup(tx("путь", 22, C_NOTE), hbar(16632, 16632, 4.2, C_NO), tx("16 632", 22, C_NO)).arrange(RIGHT, buff=0.2),
            VGroup(tx("пар ", 22, C_NOTE), hbar(4950, 16632, 4.2, C_ORDER), tx("4 950", 22, C_ORDER)).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(RIGHT * 2.6 + UP * 0.3).fix_in_frame()
        t9 = lab("100 шариков · 9 часов · путь пока в 3,4 раза длиннее", 22, WHITE).next_to(res, DOWN, buff=0.3)
        self.play(FadeIn(res[0]), FadeIn(res[1]), run_time=1)
        self.play(FadeIn(t9), run_time=0.6)
        self.play(FadeOut(self._lab), run_time=0.3)
        self._lab = None
        only = VGroup(warn_icon(C_COMP, 0.22), tx("подсказка знает про это кольцо · для других задач её пока нет", 22, C_COMP)).arrange(RIGHT, buff=0.2)
        self.play(FadeIn(only.move_to(DOWN * 2.9).fix_in_frame()), run_time=0.8)
        self.wait(2)


class A10(Base):
    """Открытое соревнование: кольца от 2 до 200 шариков; дошли ровно до числа пар; короче не нашёл никто (раздел 5)."""
    def construct(self):
        self.add(head("Открытое соревнование"))
        crowd = VGroup(*[Dot(radius=0.05).set_color(C_NOTE) for _ in range(120)]).arrange_in_grid(6, 20, buff=0.1).move_to(UP * 1.6)
        self.play(LaggedStartMap(FadeIn, crowd, lag_ratio=0.01), run_time=1.2)
        task = VGroup(ring_icon(8, 0.35, C_MIRROR), tx("распутать зеркало · кольца от 2 до 200 шариков", 26)).arrange(RIGHT, buff=0.3)
        task.move_to(UP * 0.4)
        self.play(FadeIn(task), run_time=0.8)
        rings = VGroup(*[ring_icon(min(n, 24), 0.12 + 0.002 * n, C_MIRROR) for n in (2, 5, 10, 20, 40, 80, 120, 160, 200)]).arrange(RIGHT, buff=0.35)
        rings.move_to(DOWN * 0.7)
        marks = VGroup(*[check(C_ORDER, 0.1).next_to(r, DOWN, buff=0.12) for r in rings])
        self.play(LaggedStartMap(Indicate, crowd, lag_ratio=0.005, color=WHITE), run_time=1.2)
        for r, m in zip(rings, marks):
            self.play(FadeIn(r, scale=0.6), run_time=0.3)
            self.play(FadeIn(m), run_time=0.25)
        self.play(FadeIn(tx("дошли до пути = числу пар", 24, C_ORDER).move_to(DOWN * 1.85)), run_time=0.8)
        none = VGroup(tx("короче", 30, C_NOTE), tx("0", 48, C_NO), tx("решений", 30, C_NOTE)).arrange(RIGHT, buff=0.3).move_to(DOWN * 2.7)
        self.play(FadeIn(none, scale=0.9), run_time=0.8)
        self.play(Indicate(none[1], color=C_NO, scale_factor=1.4), run_time=1)
        self.wait(1)


# ---------- почему ----------

class A11(Base3D):
    """Тройка шариков идёт по кругу по часовой или против; поворот кольца её не переворачивает, обмен в окошке — да;
    зеркало переворачивает все тройки → ходов не меньше: пары − половина шариков − 1 (утверждение 4.2)."""
    def construct(self):
        fr = self.frame
        fr.reorient(0, 22)
        self.add(lab("Почему короче не выходит", 36).to_edge(UP, buff=0.35))
        ring = Ring(range(6), R=1.8, r=0.34, center=LEFT * 2.6 + UP * 0.2)
        trio = (0, 1, 3)  # шарики 1, 2, 4
        for v in trio:
            ring.balls[v][0].set_color(C_COMP)
        self.play(FadeIn(ring.group), run_time=0.8)

        def orient():
            a, b, c = [ring.balls[v].get_center() for v in trio]
            return np.sign(np.cross(b - a, c - a)[2])

        tri = VMobject().set_stroke(C_COMP, 4)
        tri.add_updater(lambda m: m.set_points_as_corners([ring.balls[v].get_center() + OUT * 0.4 for v in trio + trio[:1]]))
        sign_lab = VGroup()

        def sign_mob():
            cw = orient() < 0
            col = C_COMP if cw else C_NO
            arc = Arc(PI / 2 if cw else PI / 2, -1.6 * PI if cw else 1.6 * PI, radius=0.45).add_tip().set_color(col)
            t = tx("по часовой" if cw else "против часовой", 24, col)
            return VGroup(arc, t).arrange(RIGHT, buff=0.25).move_to(RIGHT * 3.2 + UP * 1.4).fix_in_frame()

        self.add(tri)
        sign_lab = sign_mob()
        self.say("тройка шариков: по кругу — по часовой или против", C_COMP)
        self.play(FadeIn(sign_lab), run_time=0.6)
        self.say("поворот кольца тройку не переворачивает", C_RING)
        for name in ("влево", "влево", "вправо", "вправо"):
            self.play(ring.move(name), run_time=0.7)
        ok = check(C_ORDER, 0.2).fix_in_frame().next_to(sign_lab, DOWN, buff=0.2)
        self.play(FadeIn(ok), run_time=0.4)
        self.say("переворачивает её только обмен в окошке", C_NO)
        self.play(FadeOut(ok), ring.move("обмен"), run_time=1.0)
        new = sign_mob()
        self.play(ReplacementTransform(sign_lab, new), run_time=0.6)
        sign_lab = new
        self.wait(0.6)
        # зеркало переворачивает все 20 троек сразу
        self.say("зеркало переворачивает все тройки сразу", C_MIRROR)
        all_t = lab("троек у 6 шариков: 20 · перевернуть все → много обменов", 22, C_MIRROR).move_to(RIGHT * 3.2 + UP * 0.2)
        self.play(FadeIn(all_t), run_time=0.6)
        self.play(FadeOut(self._lab), run_time=0.3)
        self._lab = None
        bound = VGroup(tx("ходов на зеркало не меньше, чем", 26), tx("пары − половина шариков − 1", 26, C_MIRROR)).arrange(DOWN, buff=0.12)
        bound.move_to(RIGHT * 3.2 + DOWN * 1.0).fix_in_frame()
        ex = lab("20 шариков: не меньше 179", 24, C_NOTE).next_to(bound, DOWN, buff=0.2)
        self.play(FadeIn(bound), fr.animate.reorient(-15, 30), run_time=1.2)
        self.play(FadeIn(ex), run_time=0.6)
        self.wait(1.5)


class A12(Base3D):
    """Сверху — способ распутывания авторов: число пар + 3 хода на шарик; вилка; для 20 шариков 179…250 при гипотезе 190;
    чем больше шариков, тем уже вилка относительно потолка (утверждения 4.2–4.3)."""
    def construct(self):
        fr = self.frame
        self.add(lab("Вилка", 36).to_edge(UP, buff=0.35))
        pos, lines, dots, d, by, grp = tower_scene(self, phi=70, theta=-30)
        grp.scale(0.7, about_point=ORIGIN).shift(LEFT * 3.2)
        self.play(FadeIn(grp), run_time=1)
        self.play(fr.animate.reorient(30, 70), run_time=2)
        self.say("сверху: способ авторов — не дольше, чем пары + 3 хода на шарик", C_RING)
        rows = []
        y0 = 1.7
        for i, n in enumerate((10, 20, 100)):
            lo, mid, hi = pairs(n) - n // 2 - 1, pairs(n), pairs(n) + 3 * n
            XC, SC = 1.6, 4.5  # гипотеза — в точке XC; SC — масштаб «доля потолка → экран»
            yy = y0 - i * 1.25
            bar = Rectangle(width=SC * (hi - lo) / mid, height=0.34).set_stroke(C_FRONT, 2).set_fill(C_FRONT, 0.35)
            bar.move_to([XC + SC * ((lo + hi) / 2 / mid - 1), yy, 0])
            tick = Line(UP * 0.3, DOWN * 0.3).set_stroke(C_MIRROR, 5).move_to([XC, yy, 0])
            labs = VGroup(tx(f"{n} шариков", 20, C_NOTE).move_to([XC - 2.6, yy + 0.4, 0]),
                          tx(str(lo), 18, C_FRONT).next_to(bar, LEFT, buff=0.12),
                          tx(str(hi), 18, C_FRONT).next_to(bar, RIGHT, buff=0.12),
                          tx(str(mid), 18, C_MIRROR).next_to(tick, UP, buff=0.05))
            g = VGroup(bar, tick, labs).fix_in_frame()
            rows.append(g)
        self.play(FadeIn(rows[1][1]), FadeIn(rows[1][2][0]), FadeIn(rows[1][2][3]), run_time=0.8)
        self.play(GrowFromPoint(rows[1][0], rows[1][1].get_center()), run_time=1.2)
        self.play(FadeIn(rows[1][2][1]), FadeIn(rows[1][2][2]), run_time=0.6)
        self.say("вилка для 20 шариков: от 179 до 250 · гипотеза 190", C_FRONT)
        self.wait(0.8)
        self.say("больше шариков — вилка уже по сравнению с потолком", C_FRONT)
        for k in (0, 2):
            self.play(FadeIn(rows[k][1]), FadeIn(rows[k][2]), run_time=0.6)
            self.play(GrowFromPoint(rows[k][0], rows[k][1].get_center()), run_time=1.0)
        self.play(Indicate(rows[2][0], color=C_FRONT), fr.animate.reorient(-10, 68), run_time=1.5)
        self.play(fr.animate.reorient(10, 70), run_time=1.5)
        self.wait(0.5)


# ---------- акт 3 — развязка ----------

class A13(Base3D):
    """Возврат к вопросу: скорее всего — зеркало и число пар; подтверждения; после статьи доказано «не быстрее числа пар»
    (Антюфеев, 2026); открыто — нет ли расстановки ещё дальше."""
    def construct(self):
        fr = self.frame
        q = lab("Какую расстановку распутывать дольше всех?", 32).to_edge(UP, buff=0.35)
        self.add(q)
        pos, lines, dots, d, by, grp = tower_scene(self, phi=70, theta=-20)
        grp.scale(0.8, about_point=ORIGIN).shift(LEFT * 3.4)
        self.play(FadeIn(grp), run_time=1)
        ans = VGroup(pill("скорее всего — зеркало", C_MIRROR, 26), tx("ходов = числу пар", 26, C_MIRROR)).arrange(DOWN, buff=0.15)
        ans.move_to(RIGHT * 2.6 + UP * 2.0).fix_in_frame()
        self.play(FadeIn(ans), fr.animate.reorient(20, 70), run_time=1.5)
        rows = [("перебор", "до 15 шариков", C_RING), ("компас и фронт", "до 28 точно · до 100 с подсказкой", C_FRONT),
                ("соревнование", "до 200 шариков · короче нет", C_NOTE), ("доказательство", "вилка", C_FRONT)]
        tbl = VGroup(*[VGroup(check(C_ORDER, 0.1), tx(a, 22, col), tx(b, 18, C_NOTE)).arrange(RIGHT, buff=0.2) for a, b, col in rows])
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to(RIGHT * 2.6 + UP * 0.1).fix_in_frame()
        for r in tbl:
            self.play(FadeIn(r, shift=RIGHT * 0.15), run_time=0.6)
            self.play(Indicate(r[0], color=C_ORDER), run_time=0.4)
        self.play(fr.animate.reorient(-5, 70), run_time=1.5)
        new = VGroup(pill("2026", C_ORDER, 20), tx("Антюфеев: быстрее числа пар зеркало не распутать", 22, C_ORDER)).arrange(RIGHT, buff=0.2)
        new.move_to(RIGHT * 1.6 + DOWN * 1.6).fix_in_frame()
        self.play(FadeIn(new, shift=UP * 0.2), run_time=0.8)
        self.play(Indicate(new[1], color=C_ORDER), fr.animate.reorient(10, 72), run_time=1.5)
        top_dot = [dots[i] for i, s in enumerate(pos) if d[s] == max(by)][0]
        qm = tx("?", 44, C_MIRROR).fix_in_frame()
        open_q = VGroup(tx("открыто:", 22, C_NOTE), tx("нет ли расстановки ещё дальше", 22, C_MIRROR)).arrange(RIGHT, buff=0.2)
        open_q.move_to(RIGHT * 1.6 + DOWN * 2.4).fix_in_frame()
        qm.next_to(open_q, LEFT, buff=0.25)
        self.play(FadeIn(qm), FadeIn(open_q), Flash(top_dot, color=C_MIRROR, flash_radius=0.4), fr.animate.reorient(-15, 72), run_time=1.5)
        self.play(Flash(top_dot, color=C_MIRROR, flash_radius=0.5), fr.animate.reorient(-30, 74), run_time=2)
        self.wait(1)


# ---------- приложение ----------

class F01(Base):
    """Переход в приложение: кольцо со всеми расстановками и ходами = граф Кэли; расстановка = перестановка; ходы L, R, X."""
    def construct(self):
        ic = ring_icon(6, 1.1).move_to(ORIGIN)
        self.add(ic)
        self.play(ic.animate.scale(0.5).to_corner(UL, buff=0.6), run_time=1)
        self.add(head("Образ → формула"), app_tag().to_corner(UR, buff=0.35))
        rows = [("кольцо со всеми расстановками", "граф Кэли группы перестановок Sn"),
                ("расстановка", "перестановка: (1 0 4 3 2)"),
                ("↺ влево", "L = (1 2 … n−1 0)"), ("↻ вправо", "R = L⁻¹"), ("⇄ обмен в окошке", "X = (0, 1)")]
        tbl = VGroup(*[VGroup(tx(a, 24, C_RING), tx("→", 24, C_NOTE), tx(b, 24, C_FORM)).arrange(RIGHT, buff=0.3) for a, b in rows])
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.1)
        for r in tbl:
            self.play(FadeIn(r, shift=RIGHT * 0.15), run_time=0.6)
        self.add(tx("в формулах шарики нумеруются с нуля, как в статье", 20, C_NOTE).move_to(DOWN * 2.6))
        self.wait(2)


class F02(Base):
    """Потолок = диаметр; гипотеза OEIS A186783: diam = n(n−1)/2 (n ≥ 4); зеркало ℓn = R²·e← (формула (1) статьи)."""
    def construct(self):
        formal_card(self, "Потолок = диаметр графа", ring_icon(6, 0.9, C_MIRROR),
                    "diam = n(n − 1) / 2", "гипотеза OEIS A186783 · проверена перебором до n = 15",
                    "отражение циферблата: цифры меняются парами через ось",
                    extra=tx("зеркало = (1 0 n−1 … 3 2) = R²·(n−1 … 1 0)", 24, C_MIRROR))


class F03(Base):
    """Новинка статьи: компас дообучают уравнением Беллмана d(s) = 1 + min d(соседей); 28 шариков: медиана 650 → 402 (таблица 6)."""
    def construct(self):
        formal_card(self, "Компас + уравнение Беллмана", compass(0.8),
                    "d(s) = 1 + min d(t),  t — соседи s", "прогулки дают первую прикидку, потом сверка с соседями",
                    "дорога домой: соседу 5 минут → тебе не больше 6",
                    extra=tx("28 шариков: обычный путь 650 → 402 хода (пар 378)", 24, C_ORDER))


class F04(Base):
    """Вилка формулами: n(n−1)/2 − n/2 − 1 ≤ diam ≤ n(n−1)/2 + 3n (утверждения 4.2 и 4.3)."""
    def construct(self):
        formal_card(self, "Вилка — границы диаметра", VGroup(*[Line(UP, DOWN).set_stroke(C_FRONT, 6).shift(RIGHT * x) for x in (-0.4, 0.4)]),
                    "n(n−1)/2 − n/2 − 1  ≤  diam  ≤  n(n−1)/2 + 3n", "снизу — тройки и обмены · сверху — распутывание по циклам",
                    "весы без точной шкалы: вес зажат между двумя гирями",
                    extra=tx("2026, Антюфеев (препринт): diam ≥ n(n−1)/2", 24, C_ORDER))


class F05(Base):
    """Как это закодировать: лучевой поиск в несколько строк на Python и подсказка одной строкой (X-trick)."""
    def construct(self):
        self.add(head("Как это закодировать"), app_tag())
        code = VGroup(*[Text(l, font="Menlo", font_size=23).set_color(c) for l, c in [
            ("def beam_search(start, model, W, steps=1000):", WHITE),
            ("    front = [start]", C_FRONT),
            ("    for _ in range(steps):", WHITE),
            ("        nbrs = {m(s) for s in front for m in (L, R, X)", C_RING),
            ("                if not (m is X and s[0] < s[1])}   # подсказка", C_FRONT),
            ("        if SORTED in nbrs: return True", C_ORDER),
            ("        front = sorted(nbrs, key=model)[:W]   # W лучших по компасу", C_COMP),
            ("    return False", WHITE)]]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        cw = Text("m" * 10, font="Menlo", font_size=23).get_width() / 10  # ширина символа: отступы Python не теряются
        for l in code:
            l.shift(RIGHT * cw * (len(l.text) - len(l.text.lstrip(" "))))
        box = SurroundingRectangle(code, buff=0.35).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.06)
        VGroup(box, code).move_to(UP * 0.35)
        self.play(FadeIn(box))
        for l in code:
            self.play(Write(l), run_time=0.5)
        self.play(Indicate(code[4], color=C_FRONT), run_time=1)
        self.add(tx("схема; полный код (PyTorch) — в открытом доступе на Kaggle", 22, C_NOTE).next_to(box, DOWN, buff=0.3))
        self.wait(2)


class F06(Base):
    """Где это встречается: прямо — головоломки-кольца, сети процессоров; по аналогии — планирование."""
    def construct(self):
        self.add(head("Где это встречается"), app_tag())
        rows = [("прямо", "головоломки «Овальная трасса» (TopSpin) и «Венгерские кольца»", WHITE),
                ("прямо", "сети процессоров: диаметр = самая долгая задержка сообщения", WHITE),
                ("аналогия", "планирование: от одного состояния к другому мелкими шагами", C_NOTE)]
        tbl = VGroup()
        for a, b, col in rows:
            tbl.add(VGroup(pill(a, C_ORDER if a == "прямо" else C_NOTE, 20), tx(b, 24, col)).arrange(RIGHT, buff=0.35))
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(UP * 0.5)
        for r in tbl:
            self.play(FadeIn(r), run_time=0.6)
        chain = VGroup(pill("перебор → гипотеза", C_RING, 22), pill("программа → проверка далеко", C_COMP, 22),
                       pill("доказательство → вилка", C_FRONT, 22)).arrange(RIGHT, buff=0.25).move_to(DOWN * 2.3)
        self.play(LaggedStartMap(FadeIn, chain, lag_ratio=0.4), run_time=1.5)
        self.wait(2)


class A14(Base):
    """Кто и когда: Глушков 1968 → OEIS 2011 / гипотеза 2020 → статья 2025 / журнал 2026 → препринт Антюфеева 2026; что доказано, что гипотеза."""
    def construct(self):
        self.add(head("Кто и когда"))
        y = 1.3
        line = Line(LEFT * 6, RIGHT * 6).shift(UP * y).set_stroke(C_NOTE, 2)
        self.play(ShowCreation(line), run_time=0.6)
        events = [("1968", "Глушков: кольцо с двумя ходами", C_NOTE),
                  ("2011", "последовательность в OEIS (A186783)", C_NOTE),
                  ("2020", "гипотеза: diam = n(n−1)/2", C_NOTE),
                  ("2025", "эта статья · 34 автора · CayleyPy", WHITE),
                  ("2026", "журнал ATMP · Антюфеев: diam ≥ n(n−1)/2", C_ORDER)]
        xs = np.linspace(-4.9, 4.9, len(events))  # равные шаги: важен порядок, а не масштаб лет
        for k, ((yr, a, col), x) in enumerate(zip(events, xs)):
            up = k % 2 == 0
            label = VGroup(tx(yr, 24, col), tx(a, 17, col)).arrange(DOWN, buff=0.05)
            label.move_to([x, y + (0.6 if up else -0.6), 0])
            self.play(FadeIn(Dot([x, y, 0], radius=0.09).set_color(col)), FadeIn(label), run_time=0.7)
        rows = [("Доказано", "n(n−1)/2 − n/2 − 1 ≤ diam ≤ n(n−1)/2 + 3n (статья); diam ≥ n(n−1)/2 (препринт 2026)", WHITE),
                ("Гипотеза", "diam = n(n−1)/2 и зеркало (1 0 n−1 … 2) — единственная дальняя расстановка", C_MIRROR),
                ("Неточности", "аннотация arXiv: «− n/2», текст: «− n/2 − 1» · ссылка на «табл. 8» вместо 6", C_NO),
                ("Образ", "кольцо и башня — точная картина графа; башня нарисована для 5 шариков", C_NOTE)]
        tbl = VGroup()
        for k, (a, b, col) in enumerate(rows):
            r = VGroup(tx(a, 20, C_NOTE), tx(b, 19, col))
            r[0].move_to([-6.2 + r[0].get_width() / 2, 0, 0])
            r[1].move_to([-4.2 + r[1].get_width() / 2, 0, 0])
            r.shift(DOWN * (0.9 + k * 0.45))
            tbl.add(r)
        for r in tbl:
            self.play(FadeIn(r, shift=RIGHT * 0.15), run_time=0.8)
        self.wait(1.5)
