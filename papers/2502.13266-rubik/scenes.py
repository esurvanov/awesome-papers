"""Ролик по статье arXiv 2502.13266 (Chervov, Khoruzhii и др., «A Machine Learning Approach That Beats Large Rubik's Cubes») простыми словами.

Единый источник правил — паспорт passport.py в этой папке: законы сценария, вопрос, станции полосы «мы здесь»,
словарь, палитра, план сцен. Весь рассказ идёт в одном лабиринте позиций кубика (единство места).

Основной мир — лабиринт (в статье это граф Кэли / Шрайера группы кубика):
  • комната — позиция, дверь — ход (поворот грани на четверть оборота), выход — собранный кубик;
  • прогулка — случайное блуждание от выхода без шага назад; число ходов — подсказка для компаса;
  • компас — нейросеть ResMLP, угадывает «сколько ходов до выхода» (диффузионное расстояние), ошибается;
  • фронт — beam search ширины W; отряд — несколько агентов, берётся самый короткий путь.
Нарисованный лабиринт — маленькая иллюстрация (maze.py рядом); числа на графиках — из таблиц I и III статьи.
Запуск (из корня репозитория): uv run manimgl papers/2502.13266-rubik/scenes.py A06 -w --hd
Весь ролик с озвучкой: uv run python core/pipeline/build.py papers/2502.13266-rubik"""
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())  # корень репозитория, откуда бы ни лежал файл
sys.path.insert(0, str(ROOT / "core"))  # общая часть: manimkit
sys.path.insert(0, str(HERE))           # своя часть статьи: паспорт, текст, лабиринт
import numpy as np
from manimlib import *
from manimkit import *
import passport as P
import maze as M
from cube3d import rubik, turn, p3, relief, flat_room, neighbours

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

    def play(self, *args, run_time=1.0, **kwargs):
        super().play(*args, run_time=run_time * self.SLOW, **kwargs)

    def wait(self, duration=1.0, *args, **kwargs):
        super().wait(duration * self.SLOW, *args, **kwargs)

# палитра паспорта: один цвет — один смысл
C_POS = "#58a6ff"    # позиции, комнаты, ходы-двери
C_EXIT = "#3fb950"   # выход и найденный путь
C_WALK = "#f0883e"   # прогулки и их следы
C_COMP = "#e3b341"   # компас и его оценки
C_FRONT = "#d2a8ff"  # фронт
C_NO = "#f85149"     # ошибка, тупик
C_NOTE = "#8b949e"   # подписи, справка, чужие результаты
C_FORM = WHITE

ROOM = 0.34          # сторона комнаты


# ---------- кубик ----------

def cube_icon(L=1.0, n=3, scrambled=False, seed=0):
    """Кубик в изометрии: верх, левая и правая грани по n×n наклеек. Собранный — у каждой грани свой цвет."""
    u = np.array([np.cos(PI / 6), np.sin(PI / 6), 0]) * L
    v = np.array([-np.cos(PI / 6), np.sin(PI / 6), 0]) * L
    w = np.array([0, -1, 0]) * L
    faces = [(u, v, WHITE), (v, w, C_POS), (u, w, C_NOTE)]
    rnd = random.Random(seed)
    g = VGroup()
    for a, b, col in faces:
        for i in range(n):
            for j in range(n):
                c = (i + 0.5) / n * a + (j + 0.5) / n * b
                pts = [c + s * (x * a / n + y * b / n) for x, y in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)) for s in (0.86,)]
                fill = rnd.choice([WHITE, C_POS, C_NOTE]) if scrambled else col
                g.add(Polygon(*pts).set_stroke(BG, 1).set_fill(fill, 0.9))
    return g.move_to(ORIGIN)


# ---------- лабиринт ----------

def p(k):
    return np.array([*M.POS[k], 0.0])


def room(k, color=C_POS, op=1.0, fill=0.15):
    s = Square(ROOM).move_to(p(k)).set_stroke(color, 2.5, opacity=op).set_fill(color, fill * op)
    return s


def maze(op=1.0, exit_label=True):
    """Весь лабиринт: двери, комнаты, выход."""
    doors = VGroup(*[Line(p(a), p(b)).set_stroke(C_POS, 2, opacity=0.4 * op) for a, b in M.EDGES])
    rooms = VGroup(*[room(k, op=op) for k in range(len(M.POS)) if k != M.EXIT])
    ex = room(M.EXIT, C_EXIT, op, 0.5).scale(1.25)
    g = VGroup(doors, rooms, ex)
    if exit_label:
        g.add(tx("выход", 22, C_EXIT).set_opacity(op).next_to(ex, LEFT, buff=0.12))
    return g


def path_line(ks, color=C_EXIT, width=7, dashed=False):
    pts = [p(k) for k in ks]
    if dashed:
        return VGroup(*[DashedLine(a, b, dash_length=0.1).set_stroke(color, width) for a, b in zip(pts, pts[1:])])
    m = VMobject().set_points_as_corners(pts)
    return m.set_stroke(color, width).set_fill(opacity=0)


def start_mark(k=None):
    k = M.START if k is None else k
    return VGroup(room(k, WHITE, 1, 0.35), tx("старт", 20).next_to(p(k), DOWN, buff=0.22))


# ---------- значки ----------

def compass(r=0.45, color=C_COMP):
    ring = Circle(radius=r).set_stroke(color, 4).set_fill(color, 0.1)
    a = rotate_vector(UP, -PI / 5)
    side = rotate_vector(a, PI / 2) * r * 0.22
    tip = Polygon(a * r * 0.85, side, -side).set_stroke(width=0).set_fill(color, 1)
    back = Polygon(-a * r * 0.85, side, -side).set_stroke(width=0).set_fill(C_NOTE, 1)
    return VGroup(ring, back, tip, Dot(radius=r * 0.08).set_color(BG))


def walk_thumb(s=1.0):
    pts = [np.array([x, y, 0]) * s for x, y in ((-0.8, -0.3), (-0.4, 0.3), (0, -0.1), (0.3, 0.4), (0.8, 0.1))]
    m = VMobject().set_points_as_corners(pts).set_stroke(C_WALK, 5)
    return VGroup(m, Square(0.22 * s).move_to(pts[0]).set_stroke(C_EXIT, 3).set_fill(C_EXIT, 0.5),
                  *[Dot(q, radius=0.05 * s).set_color(C_WALK) for q in pts[1:]])


def front_thumb(s=1.0):
    g = VGroup(*[Square(0.24 * s).set_stroke(C_FRONT, 3).set_fill(C_FRONT, 0.45) for _ in range(4)]).arrange(DOWN, buff=0.12 * s)
    arr = Arrow(RIGHT * 0.6 * s, LEFT * 0.4 * s, buff=0).set_color(C_FRONT).next_to(g, LEFT, buff=0.1)
    return VGroup(g, arr)


def squad_thumb(s=1.0):
    return VGroup(*[compass(0.28 * s) for _ in range(3)]).arrange(RIGHT, buff=0.15 * s)


def bar(value, vmax, length, color, thick=0.42, vertical=False):
    size = max(0.02, length * value / vmax)
    r = Rectangle(width=thick if vertical else size, height=size if vertical else thick)
    return r.set_stroke(color, 2).set_fill(color, 0.55)


def scheme_tag():
    """Пометка на нарисованном лабиринте: это схема, настоящий — 10^19+ комнат, у каждой 12 дверей."""
    t = VGroup(tx("схема", 18, WHITE), tx("в настоящем: 10^19+ комнат,", 15, C_NOTE), tx("у каждой 12 дверей", 15, C_NOTE)).arrange(DOWN, buff=0.06)
    box = RoundedRectangle(width=t.get_width() + 0.35, height=t.get_height() + 0.25, corner_radius=0.12).set_stroke(C_NOTE, 1.5).set_fill(C_NOTE, 0.12)
    return VGroup(box, t.move_to(box)).to_corner(UL, buff=0.3)


def app_tag():
    return pill("приложение", C_NOTE, 20).to_corner(UL, buff=0.35)


def formal_card(scene, title, picture, formula, explain, analogy):
    """Карточка приложения: слева значок из рассказа, справа формула, под ней пояснение и аналогия."""
    scene.add(head(title), app_tag())
    pic = picture.move_to(LEFT * 4.9 + UP * 0.5)
    scene.play(FadeIn(pic), run_time=0.8)
    eq = (formula if isinstance(formula, Mobject) else tx(formula, 40, C_FORM)).move_to(RIGHT * 1.4 + UP * 0.9)
    scene.play(Write(eq), run_time=1.2)
    ex = tx(explain, 26).move_to(RIGHT * 1.4 + DOWN * 0.6)
    scene.play(FadeIn(ex))
    an = VGroup(tx("≈", 34, C_COMP), tx(analogy, 26, C_COMP)).arrange(RIGHT, buff=0.25).move_to(DOWN * 2.1)
    scene.play(FadeIn(an))
    scene.wait(2)


# ---------- акт 1 — вопрос и мир ----------

class A01(Base3D):
    """О чём ролик: собрать кубик легко, за минимум ходов — трудно; ход и позиция на объёмном кубике; позиций больше, чем атомов на Земле."""
    def construct(self):
        fr = self.frame
        fr.reorient(-35, 68)
        q = tx("Как собрать кубик за самое маленькое число ходов?", 34).to_edge(UP, buff=0.4).fix_in_frame()
        cube = rubik()
        self.play(Write(q), FadeIn(cube, scale=0.8), run_time=1.5)
        self.play(fr.animate.reorient(25, 64), run_time=2)
        ok = VGroup(tx("собрать", 26), check(C_EXIT, 0.2)).arrange(RIGHT, buff=0.2)
        hard = tx("за минимум ходов — трудно", 26, C_NO)
        VGroup(ok, hard).arrange(RIGHT, buff=0.9).move_to(DOWN * 2.5).fix_in_frame()
        self.play(FadeIn(ok))
        self.play(FadeIn(hard))
        hod = note("ход — поворот одной грани", C_POS).fix_in_frame()
        self.play(FadeOut(ok), FadeOut(hard), run_time=0.4)
        self.play(FadeIn(hod), run_time=0.6)
        self.play(turn(cube, 2, 1, PI / 2), run_time=1.4)
        poz = note("позиция — как сейчас раскрашены грани", C_POS).fix_in_frame()
        self.play(FadeOut(hod), run_time=0.3)
        self.play(turn(cube, 0, 1, -PI / 2), fr.animate.reorient(50, 70), FadeIn(poz), run_time=1.6)
        self.wait(0.5)
        # откуда позиции: уголки и рёбра разлетаются, меняются местами и поворачиваются (8!·3^7 × 12!·2^11 ÷ 2 = 4,3·10^19)
        corners = [c for c in cube if np.count_nonzero(np.round(c.grid_pos)) == 3]
        edges = [c for c in cube if np.count_nonzero(np.round(c.grid_pos)) == 2]
        ctr = cube.get_center()
        lbl = VGroup(tx("8 уголков", 28, C_COMP), tx("12 рёбер", 28, C_WALK)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        lbl.to_corner(UR, buff=0.5).shift(DOWN * 0.7).fix_in_frame()
        self.play(FadeOut(poz), run_time=0.3)
        self.play(*[c.animate.shift((c.get_center() - ctr) * 0.7) for c in corners], FadeIn(lbl[0]), run_time=1.0)
        self.play(*[c.animate.shift((c.get_center() - ctr) * 0.35) for c in edges], FadeIn(lbl[1]), run_time=1.0)
        cpos = [c.get_center() for c in corners]
        self.play(*[c.animate.move_to(cpos[(i + 1) % 4 + 4 * (i // 4)]).rotate(TAU / 3, axis=cpos[i] - ctr)
                    for i, c in enumerate(corners)], run_time=1.4)
        epos = [c.get_center() for c in edges]
        self.play(*[c.animate.move_to(epos[(i + 3) % len(edges)]).rotate(PI, axis=epos[i] - ctr) for i, c in enumerate(edges)],
                  run_time=1.4)
        # счётчик сочетаний крутится до 43 252 003 274 489 856 000
        val = ValueTracker(0)
        num = always_redraw(lambda: tx(f"{int(10 ** (19.636 * val.get_value())) if val.get_value() > 0 else 0:,}".replace(",", " "),
                                       28, C_POS).to_corner(DR, buff=0.5).shift(UP * 0.9).fix_in_frame())
        self.add(num)
        self.play(val.animate.set_value(1), run_time=3, rate_func=rush_into)
        self.remove(num)
        total = VGroup(tx("43 252 003 274 489 856 000", 28, C_POS), tx("≈ 43 миллиарда миллиардов позиций", 20, C_NOTE)).arrange(DOWN, aligned_edge=RIGHT, buff=0.1)
        self.add(total.to_corner(DR, buff=0.5).shift(UP * 0.8).fix_in_frame())
        self.wait(0.8)
        # перебор: миллиард позиций в секунду — с 2025 до 3395 года
        self.play(FadeOut(cube), FadeOut(lbl), FadeOut(total), fr.animate.reorient(0, 0), run_time=1)
        yr = ValueTracker(2025)
        track = Line(LEFT * 4.5, RIGHT * 4.5).set_stroke(C_NOTE, 6).move_to(UP * 0.3)
        fill = always_redraw(lambda: Line(track.get_start(), track.point_from_proportion(max(1e-3, (yr.get_value() - 2025) / 1370)))
                             .set_stroke(C_NO, 10).fix_in_frame())
        year = always_redraw(lambda: tx(str(int(yr.get_value())), 48, C_NO).next_to(track, UP, buff=0.35).fix_in_frame())
        cap = tx("перебор со скоростью миллиард позиций в секунду", 24, C_NOTE).next_to(track, DOWN, buff=0.4)
        ends = VGroup(tx("2025 — старт", 20, C_NOTE).next_to(track.get_start(), DOWN, buff=0.15),
                      tx("3395 — финиш", 20, C_NO).next_to(track.get_end(), DOWN, buff=0.15))
        self.add(track.fix_in_frame(), fill, year)
        self.play(FadeIn(cap.fix_in_frame()), FadeIn(ends.fix_in_frame()), run_time=0.6)
        self.play(yr.animate.set_value(3395), run_time=3, rate_func=linear)
        self.wait(0.6)
        self.remove(fill, year)
        self.play(FadeOut(VGroup(track, cap, ends)), run_time=0.5)
        # а у 5×5×5 позиций больше, чем атомов на Земле
        earth = VGroup(Circle(radius=1.1).set_stroke(C_POS, 4).set_fill(C_POS, 0.25),
                       Circle(radius=1.1).set_stroke(C_EXIT, 0).set_fill(C_EXIT, 0.35).stretch(0.45, 0).shift(LEFT * 0.3 + UP * 0.2).scale(0.7))
        cmp5 = VGroup(VGroup(cube_icon(1.0, n=5, scrambled=True, seed=5), tx("позиций 5×5×5", 22, C_POS)).arrange(DOWN, buff=0.25),
                      tx(">", 120, WHITE),
                      VGroup(earth, tx("атомов на Земле", 22, C_POS)).arrange(DOWN, buff=0.25)).arrange(RIGHT, buff=1.0).move_to(UP * 0.4)
        self.play(FadeIn(cmp5[0], shift=RIGHT * 0.3), FadeIn(cmp5[2], shift=LEFT * 0.3), run_time=1.0)
        self.play(GrowFromCenter(cmp5[1].fix_in_frame()), run_time=0.6)
        ask = pill("можно ли найти короткую сборку, не перебирая все позиции?", C_COMP, 26)
        self.play(FadeIn(ask.move_to(DOWN * 2.3).fix_in_frame()), run_time=0.8)
        self.wait(1.5)


class A02(Base):
    """Карточка статьи. Вход: кубик уходит в угол. Выход: кубик возвращается в центр."""
    def construct(self):
        cb = cube_icon(0.9, n=4, scrambled=True, seed=4).move_to(UP * 0.4)
        self.add(cb)
        self.play(cb.animate.scale(0.5).to_corner(UL, buff=0.5), run_time=1)
        card = RoundedRectangle(width=10.4, height=4.6, corner_radius=0.2).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.06).move_to(RIGHT * 0.9 + UP * 0.5)
        lines = VGroup(
            tx("arXiv 2502.13266 · 18 февраля 2025", 22, C_NOTE),
            tx("A Machine Learning Approach That Beats Large Rubik's Cubes", 28),
            tx("«Машинное обучение, которое обыгрывает большие кубики Рубика»", 22, C_NOTE),
            tx("А. Червов · К. Хоружий · и ещё 10 авторов · Москва, Париж, Мюнхен", 24),
        ).arrange(DOWN, buff=0.28).move_to(card.get_center() + UP * 0.75)
        self.play(FadeIn(card), FadeIn(lines[0]), Write(lines[1]), run_time=1.5)
        self.play(FadeIn(lines[2]), FadeIn(lines[3]))
        # соревнование: толпа команд, одна точка — программа авторов — выходит вперёд
        crowd = VGroup(*[Dot(radius=0.045).set_color(C_NOTE) for _ in range(200)]).arrange_in_grid(8, 25, buff=0.1)
        crowd.move_to(card.get_center() + LEFT * 2.3 + DOWN * 1.35)
        ccap = tx("2023: 1000+ команд программистов", 20, C_NOTE).next_to(crowd, UP, buff=0.12)
        self.play(LaggedStartMap(FadeIn, crowd, lag_ratio=0.01), FadeIn(ccap), run_time=1.5)
        star = Dot(radius=0.11).set_color(C_EXIT).move_to(crowd.get_center())
        win = VGroup(tx("программа авторов — короче всех", 24, C_EXIT),
                     tx("первая нейросеть для кубиков больше 3×3×3", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        win.move_to(card.get_center() + RIGHT * 2.5 + DOWN * 1.35)
        self.play(FadeIn(star, scale=2), run_time=0.5)
        self.play(star.animate.next_to(win, LEFT, buff=0.25), FadeIn(win[0]), run_time=1.0)
        self.play(FadeIn(win[1]), run_time=0.6)
        gist = VGroup(crowd, ccap, star, win)
        self.wait(1.5)
        # переходник обратно в мир: карточка уходит, кубик возвращается в центр
        self.play(FadeOut(VGroup(card, lines, gist)), cb.animate.scale(2).move_to(UP * 0.4), run_time=1.2)
        self.wait(1)


class A03(Base3D):
    """Позиция — комната, ход — дверь, собранный кубик — выход: кубик сжимается в комнату, вырастает рельеф лабиринта
    (выше — дальше от выхода), рельеф сплющивается в карту; путь к выходу рисует рука (narration.BOARD → A03Hand)."""
    def construct(self):
        fr = self.frame
        self.add(head("Лабиринт позиций").fix_in_frame())
        fr.reorient(-30, 62)
        cube = rubik(step=0.45)
        FLOOR = IN * 0.75  # пол комнаты — под кубиком
        room = Square(2.2).set_stroke(C_POS, 3).set_fill(C_POS, 0.08).shift(FLOOR)  # комната вокруг кубика, на «полу»
        self.play(FadeIn(cube, scale=0.8), run_time=1.2)
        lab = note("позиция = комната", C_POS).fix_in_frame()
        self.play(ShowCreation(room), FadeIn(lab))
        # что такое комната: одна раскраска кубика; поворот грани — переход через дверь в соседнюю комнату
        room_b = Square(2.2).set_stroke(C_POS, 3).set_fill(C_POS, 0.08).move_to(RIGHT * 4.2 + FLOOR)
        door_ab = Line(RIGHT * 1.1 + FLOOR, RIGHT * 3.1 + FLOOR).set_stroke(C_POS, 5)
        self.play(fr.animate.move_to(RIGHT * 2.1), ShowCreation(room_b), ShowCreation(door_ab), run_time=1.2)
        lab_r = note("комната = одна раскраска кубика · поворот грани = дверь в соседнюю комнату", C_POS).fix_in_frame()
        self.play(FadeOut(lab), run_time=0.3)
        self.play(FadeIn(lab_r), run_time=0.6)
        self.play(turn(cube, 2, 1, PI / 2), run_time=1.2)
        self.play(cube.animate.move_to(RIGHT * 4.2), run_time=1.2)
        self.wait(0.6)
        moved, cube = cube, rubik(step=0.45)  # в комнате слева снова собранная раскраска — это другая комната
        self.play(FadeOut(moved), FadeOut(room_b), FadeOut(door_ab), FadeIn(cube), fr.animate.move_to(ORIGIN), run_time=1.0)
        lab = lab_r
        # 12 настоящих соседей: тот же кубик после одного поворота грани (6 граней × 2 стороны)
        nbs = neighbours(step=0.16)
        ring = Group()
        doors12 = VGroup()
        for i, (_, c) in enumerate(nbs):
            ang = i * TAU / len(nbs)
            pos = np.array([3.4 * np.cos(ang), 3.4 * np.sin(ang), 0])
            ring.add(c.move_to(pos))
            doors12.add(Line(pos * 0.38, pos * 0.82).set_stroke(C_POS, 3))
        lab2 = note("ход = дверь · 6 граней × 2 стороны = 12 дверей из каждой комнаты", C_POS).fix_in_frame()
        self.play(FadeOut(lab), run_time=0.3)
        self.play(fr.animate.reorient(-15, 40).set_height(10), FadeIn(lab2), run_time=1.2)
        self.play(LaggedStart(*[AnimationGroup(ShowCreation(d), FadeIn(c, scale=0.6)) for d, c in zip(doors12, ring)], lag_ratio=0.25),
                  run_time=3.5)
        self.add(tx("12", 40, C_POS).move_to(UP * 2.6 + RIGHT * 4.6).fix_in_frame())
        self.wait(1)
        # этот кубик собран — его комната и есть выход; дальше лабиринт рисуем схемой (комнат и дверей меньше)
        doors, rooms = relief()
        tag = scheme_tag().fix_in_frame()
        lab3 = note("собранный кубик — выход · чем дальше от выхода, тем выше комната", C_EXIT).fix_in_frame()
        self.play(FadeOut(lab2), FadeOut(ring), FadeOut(doors12), FadeOut(room), *[FadeOut(m) for m in self.mobjects
                  if isinstance(m, Text) and m.text == "12"], run_time=0.6)
        self.play(fr.animate.reorient(-35, 62).move_to(np.array([-1.2, 0.2, 1.4])).set_height(9.5),
                  cube.animate.scale(0.16).move_to(p3(M.EXIT)), FadeIn(rooms, lag_ratio=0.03), FadeIn(tag), FadeIn(lab3), run_time=3)
        self.play(FadeOut(cube), ShowCreation(doors, lag_ratio=0.02), run_time=2)
        self.play(fr.animate.reorient(20, 66).move_to(np.array([-1.2, 0.2, 1.4])), run_time=3)
        self.play(FadeOut(lab3), rooms.animate.stretch(0.001, 2, about_point=ORIGIN), doors.animate.stretch(0.001, 2, about_point=ORIGIN),
                  fr.animate.reorient(0, 0).move_to(ORIGIN).set_height(FRAME_HEIGHT), run_time=3)
        flat = VGroup(*[flat_room(k) for k in range(len(M.POS))])
        self.play(FadeOut(rooms), FadeIn(flat), run_time=1.2)
        self.play(FadeIn(tx("выход", 22, C_EXIT).next_to(p3(M.EXIT, False), LEFT, buff=0.25)),
                  FadeIn(tx("старт", 20).next_to(p3(M.START, False), DOWN, buff=0.22)))
        self.play(FadeIn(note("собрать за минимум ходов = найти самый короткий путь к выходу").fix_in_frame()))
        self.wait(3)  # тут рука дорисовывает подпись и путь (слой A03Hand)


class A03Hand(Base):
    """Слой рисунка «от руки» для A03 (narration.BOARD): части по порядку — подпись «6 ходов», путь к выходу.
    Координаты — те же, что у плоской карты в конце A03."""
    def construct(self):
        _, path = M.beam(M.START, M.DIST, width=1)
        self.add(VGroup(tx(f"{len(path) - 1} ходов", 26, C_EXIT), tx("самый короткий путь", 22, C_EXIT)).arrange(DOWN, buff=0.1)
                 .move_to(RIGHT * 5.4 + UP * 0.6))
        self.add(path_line(path))


class A04(Base):
    """Карты лабиринта нет; поэтому гуляем от выхода случайно и записываем, сколько ходов сделали."""
    def construct(self):
        self.add(head("Прогулка от выхода"), scheme_tag())
        mz = maze(op=0.45)
        self.add(mz)
        nomap = VGroup(tx("карты нет:", 24, C_NO), tx("комнат 10^74", 24, C_NO)).arrange(DOWN, buff=0.1).move_to(RIGHT * 5.4 + UP * 2.0)
        self.play(FadeIn(nomap))
        path = M.walk()
        tok = Dot(p(path[0]), radius=0.13).set_color(C_WALK)
        self.play(FadeIn(tok))
        marks = VGroup()
        for i, (a, b) in enumerate(zip(path, path[1:]), 1):
            seg = Line(p(a), p(b)).set_stroke(C_WALK, 6)
            num = tx(str(i), 22, C_WALK).next_to(p(b), UR, buff=0.05)
            self.play(ShowCreation(seg), tok.animate.move_to(p(b)), FadeIn(num), run_time=0.45)
            marks.add(seg, num)
        rec = VGroup(tx("запись:", 22, C_NOTE),
                     VGroup(cube_icon(0.22, scrambled=True, seed=9), tx("→", 24, C_NOTE), tx(f"{len(path) - 1} ходов", 24, C_WALK)).arrange(RIGHT, buff=0.15)
                     ).arrange(DOWN, buff=0.15).move_to(RIGHT * 5.4 + UP * 0.3)
        self.play(FadeIn(rec))
        others = VGroup()
        for s in range(4, 14):
            w = M.walk(seed=s, steps=6)
            others.add(VMobject().set_points_as_corners([p(k) for k in w]).set_stroke(C_WALK, 3, opacity=0.35))
        self.play(LaggedStartMap(ShowCreation, others, lag_ratio=0.15), run_time=2)
        self.play(FadeIn(VGroup(tx("прогулки дешёвые:", 22, C_WALK), tx("миллиарды на лету", 22, C_WALK)).arrange(DOWN, buff=0.1).move_to(RIGHT * 5.4 + DOWN * 1.2)))
        self.wait(2)


class A05(Base):
    """На миллиардах прогулок учится компас: угадывает, сколько ходов до выхода; честно — ошибается."""
    def construct(self):
        self.add(head("Компас"), scheme_tag())
        mz = maze(op=0.7)
        self.add(mz)
        cp = compass(0.6).move_to(RIGHT * 5.4 + UP * 1.6)
        trails = VGroup(*[VMobject().set_points_as_corners([p(k) for k in M.walk(seed=sd, steps=6)]).set_stroke(C_WALK, 3, opacity=0.6)
                          for sd in range(4, 10)])
        self.play(LaggedStartMap(ShowCreation, trails, lag_ratio=0.15), run_time=1.6)
        self.play(*[t.animate.scale(0.05).move_to(cp).set_opacity(0) for t in trails], FadeIn(cp, scale=0.5), run_time=1.2)
        self.remove(trails)
        self.play(FadeIn(tx("сколько ходов до выхода?", 22, C_COMP).next_to(cp, DOWN, buff=0.2)))
        est = M.estimate(1)
        nums = VGroup(*[tx(str(est[k]), 20, C_COMP).next_to(p(k), UP, buff=0.04) for k in range(len(M.POS)) if k != M.EXIT])
        self.play(LaggedStartMap(FadeIn, nums, lag_ratio=0.05), run_time=1.6)
        # почему ошибается: прогулка петляет — ходов в ней больше, чем на кратчайшем пути до той же комнаты
        wpath = next(w for w in (M.walk(seed=sd, steps=7) for sd in range(200)) if M.DIST[w[-1]] <= 3)
        _, short = M.beam(wpath[-1], M.DIST, width=1)
        loop, sline = path_line(wpath, C_WALK, 5), path_line(short, C_EXIT, 5)
        why = VGroup(tx(f"прогулка: {len(wpath) - 1} ходов", 20, C_WALK), tx(f"на самом деле: {len(short) - 1}", 20, C_EXIT)).arrange(DOWN, buff=0.1)
        why.move_to(RIGHT * 5.4 + DOWN * 0.3)
        self.play(ShowCreation(loop), FadeIn(why[0]), run_time=1.6)
        self.play(ShowCreation(sline), FadeIn(why[1]), run_time=1.0)
        self.wait(0.6)
        self.play(FadeOut(loop), FadeOut(sline), FadeOut(why), run_time=0.5)
        wrong = [k for k in range(len(M.POS)) if k != M.EXIT and est[k] != M.DIST[k]]
        rings = VGroup(*[Square(ROOM * 1.6).move_to(p(k)).set_stroke(C_NO, 3) for k in wrong])
        self.play(ShowCreation(rings), run_time=1.0)
        self.add(VGroup(tx("ошибается:", 22, C_NO), tx("оценка больше настоящей", 20, C_NO)).arrange(DOWN, buff=0.08).move_to(RIGHT * 5.4 + DOWN * 0.3))
        self.play(FadeIn(note("но направление показывает: дальше от выхода — число больше")))
        self.play(FadeIn(pill("учится на 8 млрд позиций", C_COMP, 22).move_to(RIGHT * 5.3 + DOWN * 1.4)))
        self.play(FadeIn(tx("компас — первая часть сборщика", 18, C_NOTE).move_to(RIGHT * 5.3 + DOWN * 2.1)))
        self.wait(2)


# ---------- акт 2 — сборщик ----------

class A06(Base):
    """Компас ошибается, поэтому идём фронтом: держим самые многообещающие комнаты, ширина до 16 млн."""
    def construct(self):
        self.add(head("Фронт"), scheme_tag())
        mz = maze(op=0.55)
        self.add(mz)
        est = M.estimate(M.WIDTH_DEMO, M.ROUGH)  # тот же компас, что в сцене «ширина фронта»
        st = start_mark()
        self.play(FadeIn(st))
        lone_steps, _ = M.beam(M.START, est, width=1)
        chain = [M.START] + [keep[0] for _, keep in lone_steps if keep]
        lone = path_line(chain, C_NO, 5, dashed=True)
        dead = VGroup(cross(C_NO, 0.18).move_to(p(chain[-1])), tx("тупик", 20, C_NO).next_to(p(chain[-1]), DOWN, buff=0.25))
        self.play(ShowCreation(lone), run_time=1.6)
        self.play(FadeIn(dead, scale=1.4), FadeIn(pill("одним путём — тупик", C_NO, 18).move_to(RIGHT * 5.3 + DOWN * 0.4)), run_time=0.7)
        self.wait(0.5)
        self.play(FadeOut(lone), FadeOut(dead), run_time=0.5)
        side = VGroup(tx("ширина фронта:", 22, C_FRONT), tx("здесь 3", 26, C_FRONT), tx("у авторов до 16 млн", 22, C_FRONT)).arrange(DOWN, buff=0.12)
        side.move_to(RIGHT * 5.5 + UP * 1.7)
        self.play(FadeIn(side))
        steps, path = M.beam(M.START, est, width=3)
        prev = VGroup()
        for nbrs, keep in steps:
            cand = VGroup(*[room(k, C_FRONT, 1, 0.0) for k in nbrs])
            ev = VGroup(*[tx(str(est[k]), 20, C_COMP).next_to(p(k), UP, buff=0.04) for k in nbrs])
            self.play(FadeIn(cand), FadeIn(ev), run_time=0.5)
            kept = VGroup(*[room(k, C_EXIT if k == M.EXIT else C_FRONT, 1, 0.6) for k in keep])
            drop = VGroup(*[c for c, k in zip(cand, nbrs) if k not in keep])
            self.play(FadeIn(kept), drop.animate.set_stroke(C_NOTE, opacity=0.4), prev.animate.set_fill(C_FRONT, 0.15), FadeOut(ev), run_time=0.5)
            prev = kept
        self.play(ShowCreation(path_line(path)), run_time=1.2)
        self.play(FadeIn(note("одна ошибка компаса не губит весь поиск")))
        self.wait(2)


class A07(Base):
    """Разные прогулки — разные компасы; отряд: каждый ищет сам, берём самый короткий путь."""
    def construct(self):
        self.add(head("Отряд"), scheme_tag())
        mz = maze(op=0.5)
        self.add(mz, start_mark())
        rows = VGroup()
        lines = []
        for i, s in enumerate(M.SQUAD):
            _, path = M.beam(M.START, M.estimate(s, M.ROUGH), width=2)
            lines.append((path_line(path, C_FRONT, 5, dashed=True), len(path) - 1))
        for i, (ln, n) in enumerate(lines):
            r = VGroup(walk_thumb(0.32).rotate(i * 0.7), compass(0.25), tx(f"{n} ходов", 24, C_FRONT)).arrange(RIGHT, buff=0.2)
            rows.add(r)
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(RIGHT * 5.5 + UP * 1.0)
        for (ln, n), r in zip(lines, rows):
            self.play(FadeIn(r), ShowCreation(ln), run_time=1.0)
            self.play(FadeOut(ln), run_time=0.4)
        best = min(range(len(lines)), key=lambda i: lines[i][1])
        _, path = M.beam(M.START, M.estimate(M.SQUAD[best], M.ROUGH), width=2)
        self.play(ShowCreation(path_line(path)), rows[best][2].animate.set_color(C_EXIT), run_time=1.2)
        self.add(check(C_EXIT, 0.18).next_to(rows[best], RIGHT, buff=0.15))
        self.play(FadeIn(note("компасы ошибаются по-разному — в ответ идёт самый короткий путь")))
        self.wait(2)


# ---------- ответ и почему ----------

class A08(Base):
    """Итоги историями: 98 из 100 загораются зелёным; гонка к выходу — на 7 ходов короче; 19 задач — 19 галочек."""
    def construct(self):
        self.add(head("Что получилось"))
        # 1) обычный кубик: из 100 задач кратчайший путь — в 98
        grid = VGroup(*[Square(0.26).set_stroke(C_NOTE, 1.5).set_fill(C_NOTE, 0.15) for _ in range(100)]).arrange_in_grid(10, 10, buff=0.08)
        grid.move_to(LEFT * 3.0 + DOWN * 0.1)
        cap1 = VGroup(cube_icon(0.35), tx("обычный кубик: 100 задач", 24)).arrange(RIGHT, buff=0.2).next_to(grid, UP, buff=0.3)
        self.play(FadeIn(cap1), LaggedStartMap(FadeIn, grid, lag_ratio=0.01), run_time=1.2)
        self.play(LaggedStart(*[sq.animate.set_fill(C_EXIT, 0.8).set_stroke(C_EXIT) for sq in grid[:98]], lag_ratio=0.02), run_time=2.2)
        res1 = VGroup(tx("98", 72, C_EXIT), tx("раз из 100 —", 22, C_EXIT), tx("самый короткий путь", 22, C_EXIT)).arrange(DOWN, buff=0.08)
        res1.move_to(RIGHT * 2.6 + DOWN * 0.1)
        self.play(FadeIn(res1, shift=LEFT * 0.2), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(VGroup(grid, cap1, res1)), run_time=0.5)
        # 2) 4×4×4: гонка двух фишек — по ходу за шаг; путь сборщика короче на 7 ходов
        L_old, L_new, unit = 53.5, 46.5, 0.19
        y_old, y_new = 0.9, -0.5
        x0 = -5.0
        tr_old = Line([x0, y_old, 0], [x0 + L_old * unit, y_old, 0]).set_stroke(C_NOTE, 5)
        tr_new = Line([x0, y_new, 0], [x0 + L_new * unit, y_new, 0]).set_stroke(C_EXIT, 5)
        flag_old = VGroup(Line([x0 + L_old * unit, y_old - 0.3, 0], [x0 + L_old * unit, y_old + 0.3, 0]).set_stroke(WHITE, 3))
        flag_new = VGroup(Line([x0 + L_new * unit, y_new - 0.3, 0], [x0 + L_new * unit, y_new + 0.3, 0]).set_stroke(WHITE, 3))
        lab_old = tx("лучшие из 1000+ команд", 20, C_NOTE).next_to(tr_old, UP, buff=0.15).align_to(tr_old, LEFT)
        lab_new = tx("сборщик", 20, C_EXIT).next_to(tr_new, UP, buff=0.15).align_to(tr_new, LEFT)
        cap2 = VGroup(cube_icon(0.35, n=4), tx("кубик 4×4×4: путь к выходу", 24)).arrange(RIGHT, buff=0.2).move_to(UP * 2.2)
        tok_old = Dot([x0, y_old, 0], radius=0.14).set_color(C_NOTE)
        tok_new = Dot([x0, y_new, 0], radius=0.14).set_color(C_EXIT)
        self.play(FadeIn(cap2), ShowCreation(tr_old), ShowCreation(tr_new), FadeIn(lab_old), FadeIn(lab_new),
                  FadeIn(flag_old), FadeIn(flag_new), FadeIn(tok_old), FadeIn(tok_new), run_time=1.0)
        T = 3.0  # одинаковая скорость: время пропорционально длине пути
        self.play(tok_new.animate.move_to(tr_new.get_end()), tok_old.animate.move_to(tr_old.point_from_proportion(L_new / L_old)),
                  run_time=T * L_new / L_old, rate_func=linear)
        win = VGroup(check(C_EXIT, 0.22), tx("финиш", 22, C_EXIT)).arrange(RIGHT, buff=0.15).next_to(tr_new.get_end(), RIGHT, buff=0.3)
        self.play(FadeIn(win), tok_old.animate.move_to(tr_old.get_end()), run_time=T * (L_old - L_new) / L_old, rate_func=linear)
        gap = VGroup(Line([x0 + L_new * unit, y_new - 0.55, 0], [x0 + L_old * unit, y_new - 0.55, 0]).set_stroke(C_EXIT, 4),
                     tx("на 7 ходов короче", 24, C_EXIT))
        gap[1].next_to(gap[0], DOWN, buff=0.12)
        self.play(ShowCreation(gap[0]), FadeIn(gap[1]), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(VGroup(cap2, tr_old, tr_new, flag_old, flag_new, lab_old, lab_new, tok_old, tok_new, win, gap)), run_time=0.5)
        # 3) 5×5×5: 19 задач — короче в каждой
        cubes = VGroup(*[cube_icon(0.32, n=5, scrambled=True, seed=i) for i in range(19)]).arrange_in_grid(2, 10, buff=0.35).move_to(UP * 0.1)
        cap3 = tx("кубик 5×5×5: 19 задач соревнования", 24).next_to(cubes, UP, buff=0.4)
        self.play(FadeIn(cap3), LaggedStartMap(FadeIn, cubes, lag_ratio=0.05), run_time=1.2)
        marks = VGroup(*[check(C_EXIT, 0.14).next_to(c, DOWN, buff=0.08) for c in cubes])
        self.play(LaggedStartMap(FadeIn, marks, lag_ratio=0.12, scale=1.6), run_time=2.4)
        self.play(FadeIn(note("короче лучших команд в каждой задаче", C_EXIT)), run_time=0.6)
        self.wait(1)


class A09(Base):
    """Ширина фронта на схеме: тот же компас; ширина 1 — тупик, 2 — путь 7 ходов, 3 — кратчайший, 6 ходов;
    у авторов на 4×4×4: шире в 256 раз — путь с 60 до 50 ходов."""
    def construct(self):
        self.add(head("Почему: ширина фронта"), scheme_tag())
        mz = maze(op=0.5)
        self.add(mz, start_mark())
        est = M.estimate(M.WIDTH_DEMO, M.ROUGH)
        side = VGroup()
        prev = VGroup()
        for w in (1, 2, 3):
            steps, path = M.beam(M.START, est, width=w)
            visited = VGroup(*[room(k, C_FRONT, 1, 0.45) for _, keep in steps for k in keep if k != M.EXIT])
            self.play(FadeOut(prev), run_time=0.3)
            self.play(LaggedStartMap(FadeIn, visited, lag_ratio=0.08), run_time=1.6)
            if path:
                ln = path_line(path, C_EXIT if w == 3 else C_FRONT, 6)
                self.play(ShowCreation(ln), run_time=0.9)
                res = tx(f"ширина {w}: путь {len(path) - 1} ходов", 22, C_EXIT if w == 3 else C_FRONT)
            else:
                last = steps[-1][1][-1] if steps and steps[-1][1] else M.START
                ln = VGroup(cross(C_NO, 0.2).move_to(p(last)))
                self.play(FadeIn(ln, scale=1.5), run_time=0.6)
                res = tx(f"ширина {w}: тупик", 22, C_NO)
            side.add(res)
            side.arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(RIGHT * 5.3 + UP * 1.0)
            self.play(FadeIn(res), run_time=0.5)
            prev = VGroup(visited, ln)
        self.wait(0.6)
        fact = VGroup(tx("у авторов, 4×4×4:", 20, C_FRONT), tx("фронт шире в 256 раз —", 20, C_FRONT),
                      tx("путь 60 → 50 ходов", 24, C_EXIT)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to(RIGHT * 5.3 + DOWN * 1.0)
        self.play(FadeIn(fact), run_time=0.8)
        self.play(FadeIn(note("ширина влияет сильнее всего: чем шире фронт, тем больше ошибок компаса он прощает")))
        self.wait(1.2)


class A10(Base):
    """Отряд: 69 компасов решают 19 задач; на каждой побеждает самый короткий путь; пригодились 10, даже слабые.
    Кто какую задачу выиграл — схема (в статье — рис. 3)."""
    def construct(self):
        self.add(head("Почему: отряд"))
        team = VGroup(*[compass(0.17, C_COMP) for _ in range(69)]).arrange_in_grid(7, 10, buff=0.16).move_to(LEFT * 3.2 + DOWN * 0.5)
        tcap = tx("69 компасов", 22, C_COMP).next_to(team, UP, buff=0.2)
        tasks = VGroup(*[cube_icon(0.22, n=5, scrambled=True, seed=i) for i in range(19)]).arrange_in_grid(4, 5, buff=0.25)
        tasks.move_to(RIGHT * 3.6 + UP * 0.4)
        kcap = tx("19 задач", 22).next_to(tasks, UP, buff=0.2)
        self.play(LaggedStartMap(FadeIn, team, lag_ratio=0.01), FadeIn(tcap), run_time=1.2)
        self.play(LaggedStartMap(FadeIn, tasks, lag_ratio=0.04), FadeIn(kcap), run_time=1.0)
        rnd = random.Random(3)
        winners = rnd.sample(range(69), 10)
        assign = [winners[i % 10] for i in rnd.sample(range(19), 19)]  # каждый из 10 выиграл 1–2 задачи
        beams = []
        for t, wi in zip(tasks, assign):
            beams.append(AnimationGroup(ShowCreationThenFadeOut(Line(team[wi].get_center(), t.get_center()).set_stroke(C_EXIT, 3)),
                                        Indicate(team[wi], color=C_EXIT, scale_factor=1.6)))
        self.play(LaggedStart(*beams, lag_ratio=0.25), run_time=4.5)
        marks = VGroup(*[check(C_EXIT, 0.1).next_to(t, DOWN, buff=0.03) for t in tasks])
        self.play(FadeIn(marks), run_time=0.5)
        # в команде остаются 10 победителей, остальные гаснут
        box = RoundedRectangle(width=4.2, height=1.1, corner_radius=0.15).set_stroke(C_EXIT, 2).move_to(RIGHT * 3.6 + DOWN * 2.0)
        bcap = tx("в итоге пригодились 10 — даже слабые", 20, C_EXIT).next_to(box, UP, buff=0.1)
        self.play(*[team[i].animate.set_opacity(0.15) for i in range(69) if i not in winners], ShowCreation(box), FadeIn(bcap), run_time=1.0)
        self.play(*[team[w].animate.move_to(box.get_left() + RIGHT * (0.3 + 0.4 * k)) for k, w in enumerate(winners)], run_time=1.2)
        self.play(FadeIn(note("вместе — до 8 ходов короче, чем лучший компас в одиночку", C_EXIT)), run_time=0.6)
        self.wait(1)


class A11(Base):
    """Неожиданное тремя историями: прогулок больше — компас не лучше; маленький компас точнее большого; часы обучения."""
    def construct(self):
        self.add(head("Почему: неожиданное"))
        # 1) ведро прогулок наполняется, стрелка качества стоит
        bucket = VGroup(Line([-1, 1, 0], [-0.8, -1, 0]), Line([-0.8, -1, 0], [0.8, -1, 0]), Line([0.8, -1, 0], [1, 1, 0])).set_stroke(C_WALK, 4)
        bucket.move_to(LEFT * 5.3 + DOWN * 0.2)
        level = ValueTracker(0.05)
        water = always_redraw(lambda: Rectangle(width=1.55, height=1.95 * level.get_value()).set_stroke(width=0).set_fill(C_WALK, 0.6)
                              .move_to(bucket.get_bottom() + UP * 0.975 * level.get_value()))
        amount = always_redraw(lambda: tx(f"{4 * 2 ** round(2 * level.get_value()):.0f} млрд", 22, C_WALK).next_to(bucket, UP, buff=0.2))
        gauge = VGroup(Arc(radius=0.9, start_angle=PI, angle=-PI).set_stroke(C_NOTE, 4),
                       tx("точность", 18, C_NOTE)).arrange(DOWN, buff=0.1).move_to(LEFT * 3.1 + DOWN * 0.1)
        needle = Line(ORIGIN, UP * 0.75).set_stroke(C_COMP, 5).rotate(-PI / 5, about_point=ORIGIN).shift(gauge[0].get_center() + DOWN * 0.45)
        c1 = tx("больше прогулок — точнее не становится", 20, C_NOTE).move_to(LEFT * 4.2 + DOWN * 2.0)
        self.add(water)
        self.play(ShowCreation(bucket), FadeIn(gauge), FadeIn(needle), run_time=0.8)
        self.add(amount)
        self.play(level.animate.set_value(1.0), WiggleOutThenIn(needle, scale_value=1.0, rotation_angle=0.03 * TAU, n_wiggles=8), run_time=3.0)
        self.play(FadeIn(c1), run_time=0.5)
        # 2) большой и маленький компас: маленький точнее
        big, small = compass(0.85, C_NOTE), compass(0.42)
        duel = VGroup(VGroup(big, tx("прошлые: 14,7 млн настроек", 18, C_NOTE)).arrange(DOWN, buff=0.15),
                      VGroup(small, tx("сборщик: 4 млн", 18, C_COMP)).arrange(DOWN, buff=0.15)).arrange(RIGHT, buff=0.6, aligned_edge=DOWN)
        duel.move_to(RIGHT * 0.3 + UP * 0.2)
        self.play(FadeIn(duel[0]), run_time=0.6)
        self.play(TransformFromCopy(big, small), FadeIn(duel[1][1]), run_time=1.0)
        crown = VGroup(check(C_EXIT, 0.18), tx("точнее", 20, C_EXIT)).arrange(RIGHT, buff=0.1).next_to(small, UP, buff=0.15)
        self.play(FadeIn(crown, shift=DOWN * 0.1), run_time=0.6)
        # 3) часы обучения: наши останавливаются почти сразу
        def clock(col):
            return VGroup(Circle(radius=0.55).set_stroke(col, 4), Dot(radius=0.05).set_color(col))
        cl_old, cl_new = clock(C_NOTE), clock(C_EXIT)
        clocks = VGroup(VGroup(cl_old, tx("3,5 суток", 20, C_NOTE)).arrange(DOWN, buff=0.12),
                        VGroup(cl_new, tx("5 часов", 20, C_EXIT)).arrange(DOWN, buff=0.12)).arrange(RIGHT, buff=0.5).move_to(RIGHT * 4.7 + UP * 0.2)
        hand_old = Line(ORIGIN, UP * 0.45).set_stroke(C_NOTE, 4).shift(cl_old.get_center())
        hand_new = Line(ORIGIN, UP * 0.45).set_stroke(C_EXIT, 4).shift(cl_new.get_center())
        self.play(FadeIn(clocks), FadeIn(hand_old), FadeIn(hand_new), run_time=0.6)
        self.play(Rotate(hand_old, -TAU * 17, about_point=cl_old.get_center()),
                  Rotate(hand_new, -TAU * 1, about_point=cl_new.get_center(), run_time=0.6), run_time=3.0)
        c3 = tx("обучение — в 18 раз быстрее · сборка — в 26 раз", 20, C_EXIT).move_to(RIGHT * 3.4 + DOWN * 2.0)
        self.play(FadeIn(c3), run_time=0.5)
        self.play(FadeIn(note("время — на том же компьютере и с той же шириной фронта")))
        self.wait(1)


class A12(Base):
    """Возврат к вопросу: можно — компас из прогулок, широкий фронт, отряд; про кубик сборщик ничего не знает; 48 — гипотеза."""
    def construct(self):
        self.add(head("Главное"))
        q = tx("Можно ли найти короткую сборку, если позиции не перебрать?", 28, C_NOTE).move_to(UP * 2.5)
        self.play(FadeIn(q))
        ans = VGroup(tx("Можно", 40, C_EXIT), check(C_EXIT, 0.3)).arrange(RIGHT, buff=0.25).move_to(UP * 1.6)
        self.play(FadeIn(ans))
        chain = VGroup(
            VGroup(walk_thumb(0.7), tx("прогулки", 20, C_WALK)).arrange(DOWN, buff=0.15),
            VGroup(compass(0.35), tx("компас", 20, C_COMP)).arrange(DOWN, buff=0.15),
            VGroup(front_thumb(0.7), tx("широкий фронт", 20, C_FRONT)).arrange(DOWN, buff=0.15),
            VGroup(squad_thumb(0.9), tx("отряд", 20, C_COMP)).arrange(DOWN, buff=0.15),
            VGroup(room(M.EXIT, C_EXIT, 1, 0.5).scale(1.6).move_to(ORIGIN), tx("короткий путь", 20, C_EXIT)).arrange(DOWN, buff=0.15),
        )
        items = []
        for k, c in enumerate(chain):
            items.append(c)
            if k < len(chain) - 1:
                items.append(tx("→", 30, C_NOTE))
        row = VGroup(*items).arrange(RIGHT, buff=0.35).move_to(DOWN * 0.1)
        for m in row:
            self.play(FadeIn(m), run_time=0.45)
        self.play(FadeIn(tx("про кубик сборщик ничего не знает — только комнаты и двери", 22, C_POS).move_to(DOWN * 1.5)))
        self.play(FadeIn(pill("кратчайшие пути больших кубиков неизвестны — сравнение с лучшими известными сборками", C_NOTE, 20).move_to(DOWN * 2.45)))
        self.wait(2)


# ---------- приложение ----------

class F01(Base):
    """Переход в приложение: лабиринт = граф, компас = нейросеть."""
    def construct(self):
        self.add(app_tag())
        mz = maze()
        self.add(mz)
        self.play(mz.animate.scale(0.42).move_to(RIGHT * 4.6 + DOWN * 0.2), run_time=1.2)
        self.add(head("Приложение: то же самое формулами"))
        rows = [("лабиринт", "граф", C_POS), ("комната", "вершина графа", C_POS), ("дверь", "ребро графа (ход)", C_POS),
                ("компас", "нейросеть", C_COMP)]
        tbl = VGroup()
        for a, b, col in rows:
            r = VGroup(tx(a, 32, col), tx("→", 32, C_NOTE), tx(b, 32, C_FORM)).arrange(RIGHT, buff=0.45)
            tbl.add(r)
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(LEFT * 1.2 + DOWN * 0.2)
        for r in tbl:
            self.play(FadeIn(r), run_time=0.6)
        self.play(FadeIn(note("на каждом шаге: картинка из рассказа → формула → аналогия")))
        self.wait(2)


class F02(Base):
    """Позиция = перестановка наклеек; ход = перестановка (как тасовка карт)."""
    def construct(self):
        eq = VGroup(tx("позиция = (p(0), p(1), …, p(53))", 36), tx("ход — тоже перестановка: двигает 20 наклеек из 54", 26, C_POS)).arrange(DOWN, buff=0.3)
        formal_card(self, "Позиция — это перестановка", cube_icon(0.9, scrambled=True, seed=3), eq,
                    "p(i) — куда переехала наклейка номер i", "тасовка колоды: карты те же, порядок другой")


class F03(Base):
    """Прогулка → пары (позиция, k); компас учится угадывать k."""
    def construct(self):
        eq = VGroup(tx("прогулка → (позиция, k)", 38, C_WALK), tx("нейросеть: позиция ↦ k", 34, C_COMP)).arrange(DOWN, buff=0.3)
        formal_card(self, "Прогулка — обучающие пары", walk_thumb(1.6), eq,
                    "среднее k — «диффузионное расстояние»; оно больше кратчайшего", "капля чернил: дальше точка — позже доходит краска")


class F04(Base):
    """Нейросеть: 10 слоёв, 4 млн чисел, учится уменьшать квадрат ошибки."""
    def construct(self):
        eq = VGroup(tx("позиция → 10 слоёв → оценка", 36, C_COMP), tx("(оценка − k)^2 → меньше", 36)).arrange(DOWN, buff=0.3)
        formal_card(self, "Компас — нейросеть", compass(0.8), eq,
                    "4 млн чисел-настроек · 1 млн свежих позиций на каждый круг", "ученик сверяет ответ с ключом и поправляется")


class F05(Base):
    """Фронт = лучевой поиск: соседи → оценка → оставить W лучших → повтор."""
    def construct(self):
        eq = VGroup(tx("фронт → соседи → без повторов", 32, C_FRONT), tx("→ оценка нейросетью → W лучших", 32, C_FRONT),
                    tx("W до 2^24 ≈ 16,8 млн · не больше 200 шагов", 26)).arrange(DOWN, buff=0.25)
        formal_card(self, "Фронт — лучевой поиск (beam search)", front_thumb(1.6), eq,
                    "поиск по графу: шаг за шагом, пока не встретится выход", "отбор в турнире: дальше проходят лучшие, а не все")


class F06(Base):
    """Отряд = агенты: длина = минимум по агентам."""
    def construct(self):
        eq = VGroup(tx("агент = нейросеть + лучевой поиск", 32), tx("длина = min(L1, L2, …, LA)", 38, C_EXIT)).arrange(DOWN, buff=0.3)
        formal_card(self, "Отряд — несколько агентов", squad_thumb(1.6), eq,
                    "каждый агент учится на своих случайных прогулках", "такси разными дорогами: засчитывается первое")


class F07(Base):
    """Итоговая таблица: 3×3×3, 4×4×4, 5×5×5 против прошлых лучших."""
    def construct(self):
        self.add(head("Итог: таблица I статьи"), app_tag())
        hdr = ["кубик", "набор", "раньше", "статья", "агентов"]
        rows = [["3×3×3", "1000 позиций", "60,3 % · 69,6 %", "98,4 %", "26"],
                ["4×4×4", "43 позиции", "53,49 хода", "46,51", "29"],
                ["5×5×5", "19 позиций", "96,58 хода", "92,16", "69"]]
        xs = [-5.2, -2.7, 0.4, 3.3, 5.4]
        y0 = 1.5
        for x, h in zip(xs, hdr):
            self.add(tx(h, 22, C_NOTE).move_to([x, y0, 0]))
        self.add(Line([-6.2, y0 - 0.35, 0], [6.2, y0 - 0.35, 0]).set_stroke(C_NOTE, 1))
        for i, r in enumerate(rows):
            cells = VGroup(*[tx(c, 26, [WHITE, C_NOTE, C_NOTE, C_EXIT, C_COMP][j]).move_to([xs[j], y0 - 0.9 - i * 0.8, 0]) for j, c in enumerate(r)])
            self.play(LaggedStartMap(FadeIn, cells[:3], lag_ratio=0.3), run_time=1.0)
            self.play(FadeIn(cells[3], scale=1.2), FadeIn(cells[4]), run_time=0.7)
            self.play(ShowCreationThenFadeOut(SurroundingRectangle(cells[3], buff=0.12).set_stroke(C_EXIT, 3)), run_time=0.9)
        self.play(FadeIn(note("3×3×3 — доля кратчайших путей; 4×4×4 и 5×5×5 — средняя длина, раньше = лучшие ответы соревнования")))
        self.wait(2)


class F08(Base):
    """Как это закодировать: лучевой поиск в несколько строк на Python."""
    def construct(self):
        self.add(head("Как это закодировать"), app_tag())
        code = VGroup(*[Text(l, font="Menlo", font_size=24, color=c) for l, c in [
            ("def beam_search(start, model, W, steps=200):", WHITE),
            ("    front = [start]", C_FRONT),
            ("    for _ in range(steps):", WHITE),
            ("        nbrs = unique(move(v) for v in front for move in MOVES)", C_POS),
            ("        if SOLVED in nbrs: return True", C_EXIT),
            ("        front = sorted(nbrs, key=model)[:W]   # W лучших по компасу", C_COMP),
            ("    return False", WHITE)]]).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        cw = Text("m" * 10, font="Menlo", font_size=24).get_width() / 10  # ширина символа: отступы Python не теряются
        for l in code:
            l.shift(RIGHT * cw * (len(l.text) - len(l.text.lstrip(" "))))
        box = SurroundingRectangle(code, buff=0.4).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.06)
        VGroup(box, code).move_to(UP * 0.35)
        self.play(FadeIn(box))
        for l in code:
            self.play(Write(l), run_time=0.6)
        self.add(tx("схема; полный код на PyTorch авторы выложили вместе со статьёй", 22, C_NOTE).next_to(box, DOWN, buff=0.3))
        self.wait(2)


class F09(Base):
    """Где это встречается: прямо — головоломки и графы перестановок; по аналогии — планирование действий."""
    def construct(self):
        self.add(head("Где это встречается"), app_tag())
        rows = [
            ("прямо", "головоломки: кубики, соревнование программистов 2023 (Kaggle Santa)", WHITE),
            ("прямо", "пути в огромных графах перестановок, где перебор невозможен", WHITE),
            ("в планах", "задачи из биологии и программирования (по словам авторов)", C_NOTE),
            ("аналогия", "планирование: робот или игра — от одного состояния к другому", C_NOTE),
        ]
        tbl = VGroup()
        for a, b, col in rows:
            tag = pill(a, C_EXIT if a == "прямо" else C_NOTE, 20)
            tbl.add(VGroup(tag, tx(b, 24, col)).arrange(RIGHT, buff=0.35))
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(UP * 0.4)
        for r in tbl:
            self.play(FadeIn(r), run_time=0.6)
        self.play(FadeIn(pill("урок: карты нет — учи компас на случайных прогулках и иди широким фронтом", C_COMP, 24).move_to(DOWN * 2.5)))
        self.wait(2)


class A13(Base):
    """Кто и когда: шкала событий с картинками (1974 → 2025), авторы, что измерено, что неточно."""
    def construct(self):
        self.add(head("Кто и когда"))
        y = 1.2
        line = Line(LEFT * 6, RIGHT * 6).shift(UP * y).set_stroke(C_NOTE, 2)
        self.play(ShowCreation(line), run_time=0.6)
        crowd = VGroup(*[Dot(radius=0.03).set_color(C_NOTE) for _ in range(24)]).arrange_in_grid(4, 6, buff=0.06)
        badge = VGroup(Circle(radius=0.32).set_stroke(C_EXIT, 3), tx("26", 24, C_EXIT))
        events = [(1974, "Эрнё Рубик придумал кубик", cube_icon(0.38)),
                  (2014, "3×3×3: хватает 26 поворотов", badge),
                  (2019, "первая нейросеть собрала 3×3×3", compass(0.3, C_NOTE)),
                  (2023, "соревнование: 1000+ команд", crowd),
                  (2025, "эта статья: 4×4×4 и 5×5×5", cube_icon(0.38, n=5, scrambled=True, seed=1))]
        xs = np.linspace(-5.3, 5.3, len(events))  # равные шаги: важен порядок, а не масштаб лет
        for k, ((yr, a, icon), x) in enumerate(zip(events, xs)):
            col = WHITE if yr == 2025 else C_NOTE
            up = k % 2 == 0
            icon.move_to([x, y + (0.75 if up else -0.75), 0])
            label = VGroup(tx(str(yr), 22, col), tx(a, 16, col)).arrange(DOWN, buff=0.04)
            label.next_to(icon, UP if up else DOWN, buff=0.12)
            self.play(FadeIn(Dot([x, y, 0], radius=0.09).set_color(col)), FadeIn(icon, scale=0.6), FadeIn(label), run_time=0.8)
        rows = [
            ("Авторы", "Червов, Хоружий и ещё 10 · Москва, Париж, Мюнхен · библиотека CayleyPy", WHITE),
            ("Тип", "эксперимент, не доказательство: кратчайшие пути для больших кубиков неизвестны", WHITE),
            ("Неточности", "98,4 % или 97,6 % · агентов 29 или 6", C_NO),
            ("Образ", "лабиринт — точная картина графа; нарисованный — маленькая схема", C_NOTE),
        ]
        tbl = VGroup()
        for k, (a, b, col) in enumerate(rows):
            r = VGroup(tx(a, 20, C_NOTE), tx(b, 22, col))
            r[0].move_to([-6.2 + r[0].get_width() / 2, 0, 0])
            r[1].move_to([-4.0 + r[1].get_width() / 2, 0, 0])
            r.shift(DOWN * (1.2 + k * 0.45))
            tbl.add(r)
        for r in tbl:
            self.play(FadeIn(r, shift=RIGHT * 0.15), run_time=0.8)
        self.wait(1.5)
