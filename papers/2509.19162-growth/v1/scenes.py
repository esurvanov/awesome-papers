"""Ролик по статье arXiv 2509.19162 (Chervov, Fedoriaka, Konstantinova и др., «CayleyPy Growth: Efficient growth computations
and hundreds of new conjectures on Cayley graphs») простыми словами.

Единый источник правил — паспорт passport.py в этой папке: законы сценария, вопрос, станции полосы «мы здесь»,
словарь, палитра, план сцен. Весь рассказ идёт в одном мире: шарики, наборы ходов и башни их расстановок (единство места).

Основной мир (в статье это графы Кэли симметрической группы):
  • расстановка — перестановка; набор ходов — образующие; башня — граф, этаж — расстояние до порядка, потолок — диаметр;
  • ритм — квазимногочлен: свой многочлен для каждого остатка n; кольцо Глушкова — образующие L и X (без обратных);
  • качели — инволюция; квадрат с усами — рисунок рекордных образующих (§3.6); компас — как в прошлых роликах серии.
Башни, потолки и рекорды до 8 шариков посчитаны перебором (growth3d.floors); числа больших рядов — из статьи.
Приложение повторяет станции рассказа: у каждой карточки тот же значок, что в обзоре A03.
Запуск (из корня репозитория): uv run manimgl papers/2509.19162-growth/scenes.py A04 -w --hd
Весь ролик с озвучкой: uv run python core/pipeline/build.py papers/2509.19162-growth"""
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())  # корень репозитория, откуда бы ни лежал файл
sys.path.insert(0, str(ROOT / "core"))  # общая часть: manimkit
sys.path.insert(0, str(HERE))           # своя часть статьи: паспорт, шарики, башни
import numpy as np
from manimlib import *
from manimkit import *
import passport as P
import narration as N
from growth3d import (Row, Ring, ball, tower, tower_dots, profile, move_picture, floors, growth, apply, perm,
                      neighbours, star, glushkov, cycles4)

Base = story_base(P.STATIONS, P.SCENES)  # темп под речь + полоса «мы здесь»
STATION_OF = {code: st for code, st, *_ in P.SCENES}

# палитра паспорта: один цвет — один смысл
C_BALL = "#58a6ff"    # шарики, расстановки, ходы, башня
C_ORDER = "#3fb950"   # порядок и путь к нему
C_TOP = "#f778ba"     # потолок
C_RHYTHM = "#d2a8ff"  # ритм и формулы
C_SWING = "#f0883e"   # качели и квадрат с усами
C_COMP = "#e3b341"    # компас
C_NO = "#f85149"      # предел, «не справились»
C_NOTE = "#8b949e"    # подписи, справка
C_FORM = WHITE


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
        self.unsay()
        self._lab = note(s, color or C_NOTE).fix_in_frame()
        self.play(FadeIn(self._lab), run_time=0.5)

    def unsay(self):
        if self._lab is not None:
            self.play(FadeOut(self._lab), run_time=0.3)
            self._lab = None


SPEECH_WPS = 1.5   # слов в секунду у голоса verse — запас, если озвучки ещё нет (замер 22.10.2026: 52 слова — 35 с)
STRETCH = 2.4      # во сколько раз сборщик растянет анимацию под речь; выше ×3 «картинка стоит»
LEAD, TAIL = 0.4, 0.8  # тишина до и после речи — как в core/pipeline/build.py


def _speech(code):
    """Фразы сцены и длина её речи: по готовой озвучке (сборщик пишет её до рендера), иначе — оценка по числу слов."""
    import re
    import wave
    plain = N.TEXT[code].replace("\u0301", "")
    sents = [x for x in re.split(r"(?<=[.?!])\s+", plain.strip()) if x]
    wav = ROOT / "videos" / HERE.name / "audio" / f"{code}.realtime.wav"
    if wav.exists():
        with wave.open(str(wav)) as w:
            speech = w.getnframes() / w.getframerate()
    else:
        speech = len(re.findall(r"[а-яёa-z0-9]+", plain.lower())) / SPEECH_WPS
    return plain, sents, speech


def beat(scene, k):
    """Начало фразы k: дождаться точки «доля текста до фразы × длина речи» (так же считает лист сверки sync_sheet).
    Анимация до фразы идёт не дольше — тогда фраза и её картинка совпадают после растяжки сборщиком."""
    plain, sents, speech = _speech(type(scene).__name__)
    pos = sum(len(x) + 1 for x in sents[:k])
    target = (LEAD + pos / len(plain) * speech) / STRETCH
    now = scene.time / scene.SLOW
    if target > now + 0.05:
        scene.wait(target - now)


def pad(scene, items, color=WHITE):
    """Добрать движения до конца речи: подсвечивать пункты по порядку рассказа, пока анимация не дойдёт до (речь + тишина) / STRETCH.
    Так растяжка сборщика остаётся около STRETCH при любой длине текста."""
    _, _, speech = _speech(type(scene).__name__)
    target = (LEAD + speech + TAIL) / STRETCH
    k = 0
    while items and scene.time / scene.SLOW < target - 0.5:
        scene.play(Indicate(items[k % len(items)], color=color, scale_factor=1.06), run_time=1.0)
        scene.wait(0.4)
        k += 1


def lab(s, size=26, color=WHITE):
    return tx(s, size, color).fix_in_frame()


# ---------- значки станций: те же в обзоре (A03) и на карточках приложения ----------

def icon_build(s=1.0):
    ws = [0.25, 0.6, 0.95, 1.1, 0.8, 0.45, 0.2]
    g = VGroup()
    for k, w in enumerate(ws):
        col = C_ORDER if k == 0 else C_TOP if k == len(ws) - 1 else C_BALL
        g.add(Rectangle(width=w, height=0.11).set_stroke(width=0).set_fill(col, 0.9).move_to(UP * 0.15 * k))
    return g.move_to(ORIGIN).scale(s)


def icon_rhythm(s=1.0):
    hs = [3, 4, 6, 7, 9, 10]
    g = VGroup(*[Rectangle(width=0.16, height=0.09 * h).set_stroke(C_RHYTHM, 2)
                 .set_fill(C_RHYTHM, 0.9 if k % 2 == 0 else 0.3) for k, h in enumerate(hs)]).arrange(RIGHT, buff=0.05, aligned_edge=DOWN)
    return g.move_to(ORIGIN).scale(s)


def icon_ring(s=1.0, n=6, R=0.45):
    g = VGroup(Circle(radius=R).set_stroke(C_NOTE, 2))
    for k in range(n):
        a = PI / 2 + PI / n - TAU * k / n
        g.add(Dot(R * np.array([np.cos(a), np.sin(a), 0]), radius=R * 0.16).set_color(C_BALL))
    g.add(RoundedRectangle(width=R * 1.2, height=R * 0.45, corner_radius=0.05).set_stroke(WHITE, 1.5).move_to(UP * R))
    g.add(Arc(PI * 0.9, PI * 0.5, radius=R * 1.35).add_tip().set_color(C_BALL))
    return g.scale(s)


SQUARE_LAYOUT = {2: (-0.5, 0.5), 3: (0.5, 0.5), 5: (0.5, -0.5), 6: (-0.5, -0.5),  # квадрат
                 0: (-1.4, -1.0), 4: (1.4, -1.0), 1: (2.2, -0.4)}                 # усы: 6–0 и 5–4–1


def record7():
    """Рекорд для 7 шариков (табл. §3.4, Koltsov3 type 2): три хода-качели; потолок 30."""
    return [perm(7, [(2, 3), (5, 6)]), perm(7, [(1, 4), (2, 6), (3, 5)]), perm(7, [(0, 6), (2, 3), (4, 5)])]


def icon_records(s=1.0):
    pts = [np.array([*SQUARE_LAYOUT[k], 0]) * 0.33 for k in range(7)]
    pic = move_picture(7, record7(), [C_SWING] * 3, layout=pts, R=0.12)
    pic.remove(pic[2])  # без номеров мест
    return pic.move_to(ORIGIN).scale(s)


def compass(r=0.45, color=C_COMP):
    ring = Circle(radius=r).set_stroke(color, 4).set_fill(color, 0.1)
    a = rotate_vector(UP, -PI / 5)
    side = rotate_vector(a, PI / 2) * r * 0.22
    tip = Polygon(a * r * 0.85, side, -side).set_stroke(width=0).set_fill(color, 1)
    back = Polygon(-a * r * 0.85, side, -side).set_stroke(width=0).set_fill(C_NOTE, 1)
    return VGroup(ring, back, tip, Dot(radius=r * 0.08).set_color(BG))


def icon_compass(s=1.0):
    return compass(0.45).scale(s)


def icon_main(s=1.0):
    return VGroup(Circle(radius=0.45).set_stroke(C_ORDER, 3), check(C_ORDER, 0.22)).scale(s)


def icon_formal(s=1.0):
    box = RoundedRectangle(width=1.0, height=0.8, corner_radius=0.12).set_stroke(C_RHYTHM, 3)
    return VGroup(box, tx("f(n)", 26, C_RHYTHM).move_to(box)).scale(s)


STATION_ICON = {"Стройка": icon_build, "Ритм": icon_rhythm, "Глушков": icon_ring, "Рекорды": icon_records,
                "Компас": icon_compass, "Главное": icon_main, "Приложение": icon_formal}


def app_tag():
    return pill("приложение", C_NOTE, 20).to_corner(UL, buff=0.35)


def formal_card(scene, station, scenes, title, picture, formulas, fact, analogy=None, at=None):
    """Карточка приложения — пара к сцене рассказа: значок и имя станции, формулы, строки «по факту» и аналогия.
    at — номер фразы диктора для каждой формулы, каждой строки «по факту» и аналогии (по порядку): элемент появляется на своей фразе."""
    chip = VGroup(STATION_ICON[station](0.45), tx(f"пара к «{station}» · {'сцены' if '–' in scenes else 'сцена'} {scenes}", 20, C_NOTE)).arrange(RIGHT, buff=0.2)
    chip.next_to(app_tag(), RIGHT, buff=0.3)
    scene.add(head(title).shift(DOWN * 0.45), app_tag(), chip)
    pic = picture.move_to(LEFT * 5.0 + UP * 0.3)
    scene.play(FadeIn(pic), run_time=0.8)
    eqs = VGroup(*[f if isinstance(f, Mobject) else tx(f, 32, C_FORM) for f in formulas]).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
    eqs.move_to(RIGHT * 1.2 + UP * 0.75)
    gear = pill("по факту", C_COMP, 20)
    facts = VGroup(*[tx(f, 22, WHITE) for f in fact]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    VGroup(gear, facts).arrange(RIGHT, buff=0.3, aligned_edge=UP).next_to(eqs, DOWN, buff=0.45).align_to(eqs, LEFT)
    items = [(Write(e), e) for e in eqs] + [(FadeIn(VGroup(gear, f) if k == 0 else f, shift=UP * 0.1), f) for k, f in enumerate(facts)]
    if analogy:
        an = VGroup(tx("≈", 32, C_COMP), tx(analogy, 24, C_COMP)).arrange(RIGHT, buff=0.25).move_to(DOWN * 2.75)
        items.append((FadeIn(an), an))
    at = at or list(range(len(items)))
    for k, (anim, _) in sorted(zip(at, items), key=lambda x: x[0]):
        beat(scene, k)
        scene.play(anim, run_time=1.0)
    pad(scene, [m for _, m in items] + [pic])
    scene.wait(0.5)


def columns(values, x0, step, scale, colors, depth=0.4, width=0.42, y0=-1.8, opacity=0.85):
    """Объёмные столбики: высота — значение (потолок), цвет — по ритму."""
    g = Group()
    for k, (v, col) in enumerate(zip(values, colors)):
        h = max(0.02, v * scale)
        p = Prism(width, h, depth).set_color(col).set_opacity(opacity)
        p.move_to([x0 + k * step, y0 + h / 2, 0])
        g.add(p)
    return g


def ghost(values, x0, step, scale, color, width=0.42, y0=-1.8):
    """Контуры столбиков там, куда перебор не дотягивается: формула продолжена дальше."""
    return VGroup(*[DashedVMobject(Rectangle(width=width, height=v * scale), num_dashes=24).set_stroke(color, 2)
                    .move_to([x0 + k * step, y0 + v * scale / 2, 0]) for k, v in enumerate(values)])


def tower_group(n, gens, shift=ORIGIN, rise=0.5, spread=0.42, r=0.07, lines=True):
    pos, ls, d, by = tower(n, gens, rise=rise, spread=spread, lines=lines)
    dots = tower_dots(pos, d, r=r)
    grp = Group(ls, dots).shift(shift)
    dot_of = {s: dots[i] for i, s in enumerate(pos)}
    return pos, ls, dots, d, by, grp, dot_of


# ---------- акт 1 — вопрос и мир ----------

class A01(Base3D):
    """О чём ролик: ряд шариков и ходы; набор ходов — своя игра; все расстановки — башня;
    вопрос — насколько высока и можно ли узнать, не строя; ставка — в общем случае из самых трудных, Глушков 1968."""
    def construct(self):
        fr = self.frame
        fr.reorient(-8, 24)
        row = Row(range(5), gap=0.95, r=0.36, center=UP * 0.6)
        self.play(FadeIn(row.group, scale=0.9), run_time=1.2)
        sets = [("ход: поменять двух соседей", neighbours(5), [1, 3]),
                ("другой набор: первый шарик — с любым", star(5), [3, 1])]
        for text, gens, picks in sets:
            self.say(text, C_BALL)
            for i in picks:
                self.play(row.move(gens[i]), run_time=0.6)
        beat(self, 1)
        self.say("каждый набор ходов — своя игра", C_BALL)
        self.play(row.set_to(range(5)), row.paint(C_ORDER), fr.animate.reorient(10, 30), run_time=1.0)
        # все расстановки — в башню: внизу порядок, выше — дальше от порядка
        beat(self, 2)
        self.unsay()
        self.play(FadeOut(row.group), run_time=0.6)
        pos, ls, dots, d, by, grp, dot_of = tower_group(5, neighbours(5), shift=IN * 2.4 + LEFT * 1.2, rise=0.48)
        self.play(fr.animate.reorient(-20, 70).set_height(9), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(Group(*[dot_of[s] for s in by[f]]), scale=0.5) for f in sorted(by)], lag_ratio=0.3),
                  ShowCreation(ls), run_time=1.6)
        up = VGroup(Arrow(DOWN * 1.4, UP * 1.4).set_color(C_BALL), tx("дальше от порядка", 22, C_BALL)).arrange(RIGHT, buff=0.2)
        up.move_to(RIGHT * 3.4 + UP * 0.3).fix_in_frame()
        base = lab("внизу — порядок", 22, C_ORDER).move_to(RIGHT * 3.4 + DOWN * 1.7)
        self.play(FadeIn(up), FadeIn(base), run_time=0.8)
        beat(self, 3)
        q = lab("Насколько высокой бывает башня?", 34).to_edge(UP, buff=0.35)
        q2 = lab("и можно ли узнать высоту, не строя её?", 26, C_NOTE).next_to(q, DOWN, buff=0.15)
        self.play(Write(q), fr.animate.reorient(15, 72), run_time=1.0)
        self.play(FadeIn(q2), run_time=0.6)
        stake = VGroup(pill("в общем случае — из самых трудных задач", C_NO, 22),
                       pill("1968 · кибернетик Глушков", C_NOTE, 22),
                       pill("доказанного ответа нет", C_NO, 22)).arrange(RIGHT, buff=0.25).move_to(DOWN * 2.95).fix_in_frame()
        beat(self, 4)
        self.play(FadeOut(base), FadeIn(stake[0]), fr.animate.reorient(0, 72), run_time=1.2)
        beat(self, 5)
        self.play(FadeIn(stake[1]), run_time=0.8)
        self.play(FadeIn(stake[2]), fr.animate.reorient(-10, 72), run_time=1.2)
        pad(self, [q, q2, *stake])


class A02(Base):
    """Карточка статьи. Вход: башня уходит в угол. Выход: карточка уходит, значок башни возвращается в центр."""
    def construct(self):
        ic = icon_build(2.0).move_to(UP * 0.3)
        self.add(ic)
        self.play(ic.animate.scale(0.4).to_corner(UL, buff=0.5), run_time=1)
        card = RoundedRectangle(width=11.4, height=5.0, corner_radius=0.2).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.06).move_to(RIGHT * 0.6 + UP * 0.45)
        lines = VGroup(
            tx("arXiv 2509.19162 · 23 сентября 2025 · версия 2 — 1 апреля 2026", 20, C_NOTE),
            tx("CayleyPy Growth: Efficient growth computations", 26),
            tx("and hundreds of new conjectures on Cayley graphs", 26),
            tx("«Быстрый подсчёт роста и сотни новых гипотез о графах Кэли»", 21, C_NOTE),
            tx("А. Червов · Д. Федоряка · Е. Константинова · и ещё 46 авторов · проект CayleyPy", 21),
        ).arrange(DOWN, buff=0.16).move_to(card.get_center() + UP * 1.1)
        self.play(FadeIn(card), FadeIn(lines[0]), Write(lines[1]), Write(lines[2]), run_time=1.6)
        self.play(FadeIn(lines[3]), FadeIn(lines[4]))
        series = VGroup(
            VGroup(VGroup(*[Square(0.11).set_stroke(C_BALL, 1.5) for _ in range(9)]).arrange_in_grid(3, 3, buff=0.03), tx("кубики", 18, C_NOTE)).arrange(DOWN, buff=0.08),
            VGroup(icon_ring(0.55), tx("кольцо", 18, C_NOTE)).arrange(DOWN, buff=0.08),
            VGroup(icon_build(0.55), tx("башни · эта", 18, WHITE)).arrange(DOWN, buff=0.08)).arrange(RIGHT, buff=0.5)
        arrows = VGroup(*[Arrow(series[k].get_right(), series[k + 1].get_left(), buff=0.1).set_color(C_NOTE) for k in range(2)])
        sv = VGroup(tx("третья статья серии:", 20, C_NOTE), VGroup(series, arrows)).arrange(RIGHT, buff=0.35)
        sv.move_to(card.get_center() + DOWN * 0.45)
        self.play(FadeIn(sv[0]), LaggedStartMap(FadeIn, series, lag_ratio=0.4), FadeIn(arrows), run_time=1.5)
        beat(self, 1)
        self.play(Indicate(lines[0], color=WHITE), run_time=1.0)
        gist = VGroup(pill("башни — во много раз быстрее", C_BALL, 21), tx("→", 26, C_NOTE),
                      pill("высота = простые формулы", C_RHYTHM, 21), tx("→", 26, C_NOTE),
                      pill("≈ 200 гипотез", C_TOP, 21)).arrange(RIGHT, buff=0.2)
        gist.move_to(card.get_center() + DOWN * 1.65)
        beat(self, 2)
        self.play(FadeIn(gist[0]), run_time=0.8)
        self.play(FadeIn(gist[1:3]), run_time=0.8)
        beat(self, 3)
        self.play(FadeIn(gist[3:]), run_time=0.8)
        self.play(Indicate(gist[-1], color=C_TOP), run_time=0.8)
        pad(self, [lines[1], lines[4], series[2], gist[2], gist[4]])
        self.play(FadeOut(VGroup(card, lines, sv, gist)), ic.animate.scale(1 / 0.4).move_to(UP * 0.3), run_time=1.2)
        self.wait(0.3)


class A03(Base):
    """Обзор всей статьи: шесть остановок и приложение. Выход: значки уезжают в полосу «мы здесь»."""
    def construct(self):
        ic = icon_build(2.0).move_to(UP * 0.3)
        self.add(ic)
        self.add(head("Вся статья — шесть остановок"))
        stops = [("Стройка", "как строят башню"), ("Ритм", "формула высоты"), ("Глушков", "ответ на вопрос 1968"),
                 ("Рекорды", "самые высокие · предел"), ("Компас", "проверка дальше перебора"), ("Главное", "возврат к вопросу")]
        tiles = VGroup()
        for k, (name, cap_) in enumerate(stops):
            box = RoundedRectangle(width=3.6, height=1.75, corner_radius=0.15).set_stroke(C_NOTE, 1.5).set_fill(C_NOTE, 0.05)
            icon = STATION_ICON[name](0.8)
            txt = VGroup(tx(f"{k + 1} · {name}", 24), tx(cap_, 18, C_NOTE)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            VGroup(icon, txt).arrange(RIGHT, buff=0.3).move_to(box)
            tiles.add(VGroup(box, icon, txt))
        tiles.arrange_in_grid(2, 3, buff=0.3).move_to(UP * 0.55)
        app = VGroup(RoundedRectangle(width=11.4, height=0.95, corner_radius=0.15).set_stroke(C_RHYTHM, 1.5).set_fill(C_RHYTHM, 0.06))
        app.add(VGroup(icon_formal(0.6), tx("Приложение: те же остановки формулами · как это работает по факту", 22, C_RHYTHM))
                .arrange(RIGHT, buff=0.3).move_to(app[0]))
        app.next_to(tiles, DOWN, buff=0.3)
        beat(self, 1)
        self.play(ReplacementTransform(ic, tiles[0][1]), FadeIn(tiles[0][0]), FadeIn(tiles[0][2]), run_time=1.0)
        for k, t in enumerate(tiles[1:], 2):
            beat(self, k)
            self.play(FadeIn(t, shift=UP * 0.15), run_time=0.7)
            self.play(Indicate(t[1], color=WHITE), run_time=0.6)
        beat(self, 7)
        self.play(FadeIn(app, shift=UP * 0.15), run_time=0.8)
        pad(self, [app], C_RHYTHM)
        # переходник: значки уезжают на свои места в полосе «мы здесь»
        xs = np.linspace(-6.0, 6.0, len(P.STATIONS))
        moves = []
        for (name, _), t in zip(stops, tiles):
            x = xs[P.STATIONS.index(name)]
            moves.append(t[1].animate.scale(0.32).move_to([x, -3.15, 0]))
        moves.append(app[1][0].animate.scale(0.5).move_to([xs[-1], -3.15, 0]))
        self.play(*moves, FadeOut(VGroup(*[VGroup(t[0], t[2]) for t in tiles])), FadeOut(VGroup(app[0], app[1][1])), run_time=1.8)
        self.wait(0.6)
        first = tiles[0][1]
        self.play(first.animate.scale(1 / 0.32 * 2.2).move_to(UP * 0.3), FadeOut(VGroup(*[t[1] for t in tiles[1:]], app[1][0])), run_time=1.2)
        self.wait(0.3)


class A04(Base3D):
    """Маленькая башня: 4 шарика, ход — обмен соседей; 24 расстановки по этажам 1-3-5-6-5-3-1; потолок — 6-й этаж,
    на нём одна расстановка — задом наперёд (пересчитано перебором)."""
    def construct(self):
        fr = self.frame
        self.add(lab("Маленькая башня: четыре шарика", 34).to_edge(UP, buff=0.35))
        gens = neighbours(4)
        pos, ls, dots, d, by, grp, dot_of = tower_group(4, gens, shift=IN * 1.6 + LEFT * 2.0, rise=0.62, spread=0.55, r=0.09)
        fr.reorient(-20, 72)
        top = max(by)
        bars = VGroup()
        for f in range(top + 1):
            m = len(by[f])
            col = C_ORDER if f == 0 else C_TOP if f == top else C_BALL
            bars.add(VGroup(tx(str(f), 20, C_NOTE), Rectangle(width=0.4 * m, height=0.24).set_stroke(col, 2).set_fill(col, 0.55),
                            tx(str(m), 20, col)).arrange(RIGHT, buff=0.15))
        bars.arrange(UP, aligned_edge=LEFT, buff=0.1).move_to(RIGHT * 4.0 + DOWN * 0.2).fix_in_frame()
        hdr = lab("этаж · сколько расстановок", 18, C_NOTE).next_to(bars, UP, buff=0.2)
        row = Row(range(4), gap=0.7, r=0.26, center=LEFT * 2.0 + DOWN * 0.2 + IN * 1.6)
        self.say("ход — поменять местами двух соседей", C_BALL)
        self.play(FadeIn(row.group), run_time=0.6)
        self.play(row.move(gens[1]), run_time=0.8)
        self.play(row.move(gens[1]), run_time=0.6)
        self.play(FadeOut(row.group), run_time=0.4)
        beat(self, 2)
        self.say("этаж — сколько ходов до порядка самым коротким путём", C_BALL)
        self.play(FadeIn(hdr), run_time=0.4)
        for f in range(top + 1):
            layer = Group(*[dot_of[s] for s in by[f]])
            lf = VGroup(*[l for l in ls if abs(max(l.get_start()[2], l.get_end()[2]) - (f * 0.62 - 1.6)) < 1e-3])
            self.play(FadeIn(layer, scale=0.5), ShowCreation(lf), FadeIn(bars[f]), run_time=0.5)
            if f == 0:
                beat(self, 3)
                self.say("внизу — порядок · на первом этаже три соседки", C_ORDER)
        self.add(ls)
        self.play(fr.animate.reorient(20, 74), run_time=2.0)
        beat(self, 4)
        self.say("потолок — верхний этаж: за это число ходов распутается любая", C_TOP)
        tdot = dot_of[by[top][0]]
        self.play(Flash(tdot, color=C_TOP, flash_radius=0.4), tdot.animate.scale(1.5), run_time=1.0)
        rows = VGroup(VGroup(tx("потолок · 6", 22, C_TOP), tx("4 3 2 1", 24, C_TOP)).arrange(RIGHT, buff=0.3),
                      VGroup(tx("порядок · 0", 22, C_ORDER), tx("1 2 3 4", 24, C_ORDER)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(LEFT * 4.6 + UP * 2.0).fix_in_frame()
        beat(self, 5)
        self.play(FadeIn(rows), fr.animate.reorient(-15, 70), run_time=1.5)
        self.play(Indicate(rows[0][1], color=C_TOP), run_time=0.8)
        pad(self, [rows[0], bars[-1], rows[1], bars[0]])


class A05(Base3D):
    """Перебор этаж за этажом: от каждой расстановки этажа — все ходы; новые — на следующий этаж, виденные — в сторону.
    Скорость: на процессоре обычно в 10–100 раз, на видеокарте S₁₁ — 39 мин → 0,6 с (табл. 1–2); 15 шариков — 15! и дни (§3.1.3)."""
    def construct(self):
        fr = self.frame
        self.add(lab("Перебор: этаж за этажом", 34).to_edge(UP, buff=0.35))
        gens = neighbours(5)
        rise = 0.42
        pos, ls, dots, d, by, grp, dot_of = tower_group(5, gens, shift=IN * 2.2 + LEFT * 2.6, rise=rise)
        fr.reorient(-15, 72)
        top = max(by)
        self.add(dot_of[tuple(range(5))])
        beat(self, 1)
        self.say("от каждой расстановки этажа пробуем все ходы", C_BALL)
        cnt = VGroup()
        for f in range(top):
            src = by[f]
            tries = VGroup()
            for s in src:
                for g in gens:
                    t = apply(s, g)
                    col = C_BALL if d[t] == f + 1 else C_NOTE
                    tries.add(Line(pos[s] + IN * 2.2 + LEFT * 2.6, pos[t] + IN * 2.2 + LEFT * 2.6).set_stroke(col, 2 if col == C_BALL else 1,
                                                                                                         opacity=0.9 if col == C_BALL else 0.35))
            new = Group(*[dot_of[s] for s in by[f + 1]])
            self.play(ShowCreation(tries), FadeIn(new, scale=0.4), run_time=0.45)
            if f == 0:
                beat(self, 2)
                self.say("новые — на следующий этаж · уже виденные — в сторону", C_BALL)
            self.play(tries.animate.set_stroke(C_BALL, 1, opacity=0.18), run_time=0.15)
            cnt.add(tries)
        self.play(fr.animate.reorient(20, 74), run_time=1.6)
        beat(self, 3)
        self.unsay()
        # скорость: прежняя программа против новой
        sp = VGroup(
            tx("11 шариков · обмены соседей", 20, C_NOTE),
            VGroup(tx("прежняя", 20, C_NOTE), Rectangle(width=4.0, height=0.3).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.5), tx("39 мин", 20, C_NOTE)).arrange(RIGHT, buff=0.15),
            VGroup(tx("новая · видеокарта", 20, C_ORDER), Rectangle(width=0.04, height=0.3).set_stroke(C_ORDER, 2).set_fill(C_ORDER, 0.9), tx("0,6 с", 20, C_ORDER)).arrange(RIGHT, buff=0.15),
            tx("на процессоре — обычно в десятки раз", 20, WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(RIGHT * 3.4 + UP * 1.3).fix_in_frame()
        for r in sp:
            self.play(FadeIn(r, shift=LEFT * 0.15), run_time=0.6)
        self.play(Indicate(sp[2][2], color=C_ORDER, scale_factor=1.3), run_time=0.8)
        big = VGroup(tx("15 шариков", 24), tx("1 307 674 368 000", 30, C_BALL), tx("расстановок · несколько дней", 22, C_BALL)).arrange(DOWN, buff=0.08)
        big.move_to(RIGHT * 3.4 + DOWN * 1.5).fix_in_frame()
        beat(self, 4)
        self.play(FadeIn(big, scale=0.9), fr.animate.reorient(-10, 72), run_time=1.4)
        pad(self, [big[1], sp[2], sp[3]])


# ---------- акт 2 — ритм и Глушков ----------

STAR = {n: 3 * (n - 1) // 2 for n in range(3, 13)}  # «первый с любым»: потолок ⌊3(n−1)/2⌋ (известно; пересчитано до 9)


class A06(Base3D):
    """Много башен: полсотни наборов; потолки растут по простой формуле, часто две чередуются (чёт/нечёт),
    бывает по 4, 6, 8 — ритм. Пример — «первый с любым»: 3, 4, 6, 7, 9, 10… — ступеньки +1, +2."""
    def construct(self):
        fr = self.frame
        fr.reorient(0, 0)
        self.add(lab("Потолки многих башен", 34).to_edge(UP, buff=0.35))
        many = VGroup(*[profile(growth(4, g), width=0.5, step=0.05) for g in
                        [neighbours(4), star(4), glushkov(4), neighbours(4)[:2] + [star(4)[2]]]])
        grid = VGroup(*[many[k % len(many)].copy() for k in range(48)]).arrange_in_grid(4, 12, buff=0.25).move_to(UP * 0.5)
        self.play(LaggedStartMap(FadeIn, grid, lag_ratio=0.03), run_time=1.0)
        self.say("полсотни наборов ходов · у каждого — ряды до самых больших", C_BALL)
        beat(self, 1)
        self.play(FadeOut(grid), run_time=0.6)
        # пример: «первый шарик — с любым»
        row = Row(range(5), gap=0.8, r=0.3, center=UP * 2.0 + LEFT * 3.6)
        self.say("пример: первый шарик — с любым", C_BALL)
        self.play(FadeIn(row.group), run_time=0.5)
        for i in (2, 0):
            self.play(row.move(star(5)[i]), run_time=0.45)
        ns = list(STAR)
        vals = [STAR[n] for n in ns]
        cols = [C_RHYTHM if n % 2 else C_BALL for n in ns]
        bars = columns(vals, -4.6, 0.95, 0.24, cols, y0=-1.3)
        nlab = VGroup(*[tx(str(n), 20, C_NOTE).move_to([-4.6 + k * 0.95, -1.65, 0]) for k, n in enumerate(ns)])
        vlab = VGroup(*[tx(str(v), 20, c).move_to([-4.6 + k * 0.95, -1.3 + v * 0.24 + 0.28, 0]) for k, (v, c) in enumerate(zip(vals, cols))])
        beat(self, 2)
        self.say("подставляешь число шариков — получаешь потолок", C_BALL)
        self.play(FadeOut(row.group), fr.animate.reorient(-18, 22), run_time=0.8)
        self.play(FadeIn(nlab), run_time=0.4)
        self.play(LaggedStart(*[AnimationGroup(GrowFromEdge(b, DOWN), FadeIn(v)) for b, v in zip(bars, vlab)], lag_ratio=0.4), run_time=1.6)
        steps = VGroup(*[tx(f"+{vals[k + 1] - vals[k]}", 20, C_RHYTHM if (vals[k + 1] - vals[k]) == 2 else C_BALL)
                         .move_to([-4.6 + (k + 0.5) * 0.95, -1.3 + max(vals[k], vals[k + 1]) * 0.24 + 0.7, 0]) for k in range(len(vals) - 1)])
        beat(self, 3)
        self.say("формул две и они чередуются: для чётных и для нечётных", C_RHYTHM)
        self.play(LaggedStartMap(FadeIn, steps, lag_ratio=0.15), fr.animate.reorient(15, 24), run_time=2.0)
        leg = VGroup(VGroup(Square(0.25).set_fill(C_BALL, 0.85).set_stroke(width=0), tx("чётные", 20, C_BALL)).arrange(RIGHT, buff=0.15),
                     VGroup(Square(0.25).set_fill(C_RHYTHM, 0.85).set_stroke(width=0), tx("нечётные", 20, C_RHYTHM)).arrange(RIGHT, buff=0.15)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(LEFT * 5.2 + UP * 2.2).fix_in_frame()
        self.play(FadeIn(leg), run_time=0.5)
        self.unsay()
        more = VGroup(tx("бывает чередование", 22, C_NOTE), *[pill(f"по {k}", C_RHYTHM, 22) for k in (2, 4, 6, 8)],
                      tx("→", 26, C_NOTE), pill("ритм", C_RHYTHM, 26)).arrange(RIGHT, buff=0.2).move_to(DOWN * 2.95).fix_in_frame()
        beat(self, 4)
        self.play(LaggedStartMap(FadeIn, more[:-2], lag_ratio=0.25), fr.animate.reorient(-5, 20), run_time=2.0)
        beat(self, 5)
        self.play(FadeIn(more[-2:]), run_time=0.6)
        self.play(Indicate(more[-1], color=C_RHYTHM), run_time=0.8)
        pad(self, [*steps], C_RHYTHM)


class A07(Base3D):
    """Главная гипотеза: набор с простым правилом → потолок — формула с ритмом; в общем случае высоту заранее не узнать;
    путь: маленькие башни → ритм → формула дальше предела перебора (схема на том же примере)."""
    def construct(self):
        fr = self.frame
        fr.reorient(-15, 20)
        hyp = pill("гипотеза: простое правило → потолок — формула с ритмом", C_RHYTHM, 26).to_edge(UP, buff=0.35).fix_in_frame()
        self.play(FadeIn(hyp, scale=0.9), run_time=0.9)
        warn = VGroup(warn_icon(C_NO, 0.22), tx("в общем случае высоту заранее не узнать", 22, C_NO)).arrange(RIGHT, buff=0.2)
        warn.next_to(hyp, DOWN, buff=0.25).fix_in_frame()
        beat(self, 1)
        self.play(FadeIn(warn), run_time=0.7)
        ns = list(range(3, 19))
        vals = [3 * (n - 1) // 2 for n in ns]
        known, far = 8, len(ns) - 8
        sc, st, x0 = 0.17, 0.72, -5.6
        cols = [C_RHYTHM if n % 2 else C_BALL for n in ns[:known]]
        bars = columns(vals[:known], x0, st, sc, cols, width=0.36, depth=0.3)
        wall_x = x0 + (known - 0.5) * st
        wall = Rectangle(width=0.06, height=4.2).set_stroke(width=0).set_fill(C_NO, 0.8).move_to([wall_x, 0.1, 0])
        wl = tx("предел перебора", 20, C_NO).next_to(wall, UP, buff=0.1)
        far_g = ghost(vals[known:], x0 + known * st, st, sc, C_RHYTHM, width=0.36)
        chain = VGroup(pill("маленькие башни", C_BALL, 22), tx("→", 26, C_NOTE), pill("услышать ритм", C_RHYTHM, 22),
                       tx("→", 26, C_NOTE), pill("формула дальше", C_RHYTHM, 22)).arrange(RIGHT, buff=0.2).move_to(DOWN * 2.95).fix_in_frame()
        beat(self, 2)
        self.play(LaggedStartMap(GrowFromEdge, bars, edge=DOWN, lag_ratio=0.15), FadeIn(chain[0]), run_time=1.8)
        self.play(FadeIn(chain[1:3]), run_time=0.6)
        self.play(FadeIn(wall), FadeIn(wl), run_time=0.6)
        self.play(FadeIn(chain[3:]), LaggedStartMap(ShowCreation, far_g, lag_ratio=0.12), fr.animate.reorient(18, 24), run_time=2.4)
        self.add(lab("схема", 18, C_NOTE).to_corner(UR, buff=0.4).shift(DOWN * 1.2))
        self.play(fr.animate.reorient(0, 18), run_time=1.5)
        pad(self, [hyp, warn, chain[0], chain[2], chain[4], far_g])


GL = {5: 11, 6: 18, 7: 25, 8: 35, 9: 45, 10: 58, 11: 71, 12: 87}  # кольцо Глушкова: потолки — пересчитано перебором (наш и CayleyPy)


class A08(Base3D):
    """Кольцо Глушкова — кольцо прошлого ролика без поворота вправо: поворот влево и обмен двух верхних.
    Перебор: ритм два (формулы для чётных и нечётных); пересчитано нами до 12 шариков; первые этажи — числа Фибоначчи."""
    def construct(self):
        fr = self.frame
        fr.reorient(-8, 26)
        self.add(lab("Вопрос Глушкова", 34).to_edge(UP, buff=0.35))
        ring = Ring(range(6), R=1.7, r=0.34, center=LEFT * 3.4 + UP * 0.3)
        self.play(FadeIn(ring.group, scale=0.9), run_time=1.0)
        beat(self, 1)
        self.say("кольцо из прошлого ролика · ходов два", C_BALL)
        mv = VGroup(pill("↺ повернуть влево", C_BALL, 22), pill("⇄ поменять два верхних", C_BALL, 22)).arrange(DOWN, buff=0.15)
        mv.move_to(RIGHT * 2.2 + UP * 1.6).fix_in_frame()
        self.play(FadeIn(mv[0]), ring.left(), run_time=1.0)
        self.play(FadeIn(mv[1]), ring.swap(), run_time=1.0)
        noright = VGroup(tx("поворота вправо нет", 20, C_NOTE), cross(C_NO, 0.1)).arrange(RIGHT, buff=0.15).next_to(mv, DOWN, buff=0.2).fix_in_frame()
        self.play(FadeIn(noright), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(ring.group), FadeOut(mv), FadeOut(noright), fr.animate.reorient(-15, 20), run_time=0.6)
        ns = list(GL)
        vals = [GL[n] for n in ns]
        cols = [C_RHYTHM if n % 2 else C_BALL for n in ns]
        x0, st, sc = -4.2, 1.0, 0.043
        bars = columns(vals, x0, st, sc, cols, width=0.5)
        nlab = VGroup(*[tx(str(n), 20, C_NOTE).move_to([x0 + k * st, -2.15, 0]) for k, n in enumerate(ns)])
        vlab = VGroup(*[tx(str(v), 20, c).move_to([x0 + k * st, -1.8 + v * sc + 0.28, 0]) for k, (v, c) in enumerate(zip(vals, cols))])
        beat(self, 2)
        self.say("перебор дал ритм: одна формула для чётных, другая для нечётных", C_RHYTHM)
        self.play(FadeIn(nlab), run_time=0.4)
        self.play(LaggedStart(*[AnimationGroup(GrowFromEdge(b, DOWN), FadeIn(v)) for b, v in zip(bars, vlab)], lag_ratio=0.4), run_time=1.5)
        leg = VGroup(pill("чётные — формула 1", C_BALL, 20), pill("нечётные — формула 2", C_RHYTHM, 20)).arrange(DOWN, buff=0.12)
        leg.move_to(LEFT * 4.6 + UP * 2.1).fix_in_frame()
        self.play(FadeIn(leg), fr.animate.reorient(15, 24), run_time=0.8)
        chk = VGroup(check(C_ORDER, 0.14), tx("пересчитали сами: до 12 шариков — сходится", 22, C_ORDER)).arrange(RIGHT, buff=0.2)
        chk.move_to(LEFT * 3.4 + UP * 1.2).fix_in_frame()
        beat(self, 3)
        self.play(FadeIn(chk), LaggedStartMap(Indicate, vlab, color=C_ORDER, lag_ratio=0.1), run_time=1.6)
        self.unsay()
        fib = growth(7, glushkov(7))[:7]
        fr_row = VGroup(tx("первые этажи:", 22, C_NOTE), *[tx(str(v), 30, C_BALL) for v in fib]).arrange(RIGHT, buff=0.35)
        fr_row.move_to(DOWN * 0.3).fix_in_frame()
        beat(self, 4)
        self.play(FadeOut(Group(bars, nlab, vlab, leg, chk)), run_time=0.6)
        self.play(FadeIn(fr_row[0]), LaggedStartMap(FadeIn, fr_row[1:], lag_ratio=0.3), fr.animate.reorient(-5, 20), run_time=1.8)
        sums = VGroup(*[ArcBetweenPoints(fr_row[k].get_top() + UP * 0.05, fr_row[k + 2].get_top() + UP * 0.05, angle=-PI / 2)
                        .set_stroke(C_RHYTHM, 2) for k in range(1, 6)]).fix_in_frame()
        plus = tx("каждый = сумма двух предыдущих", 20, C_RHYTHM).next_to(fr_row, UP, buff=0.45).fix_in_frame()
        self.play(LaggedStartMap(ShowCreation, sums, lag_ratio=0.25), FadeIn(plus), run_time=1.6)
        pad(self, [*fr_row[1:]], C_RHYTHM)


class A09(Base3D):
    """Форма башни: обмены соседей — ровный колокол; кольцо Глушкова — широкая часть у потолка и резкий обрыв (6 шариков, перебор)."""
    def construct(self):
        fr = self.frame
        self.add(lab("Форма башни", 34).to_edge(UP, buff=0.35))
        n = 6
        L = tower_group(n, neighbours(n), shift=LEFT * 3.0 + IN * 2.4, rise=0.3, spread=0.2, r=0.045, lines=False)
        R = tower_group(n, glushkov(n), shift=RIGHT * 3.0 + IN * 2.4, rise=0.3, spread=0.2, r=0.045, lines=False)
        fr.reorient(0, 74).set_height(9.5)
        for k, grp_ in ((1, L), (2, R)):
            beat(self, k)
            self.say(["обмены соседей: ровный колокол", "кольцо Глушкова: широкая часть у потолка, сверху обрыв"][k - 1], [C_BALL, C_TOP][k - 1])
            by, dot_of = grp_[4], grp_[6]
            self.play(LaggedStart(*[FadeIn(Group(*[dot_of[s] for s in by[f]]), scale=0.5) for f in sorted(by)], lag_ratio=0.25), run_time=1.6)
        pl = profile(growth(n, neighbours(n)), width=2.0, step=0.2).move_to(LEFT * 3.0 + DOWN * 0.3).fix_in_frame()
        pr = profile(growth(n, glushkov(n)), width=2.0, step=0.2).move_to(RIGHT * 3.0 + DOWN * 0.1).fix_in_frame()
        self.play(fr.animate.reorient(25, 76), run_time=2.0)
        self.play(fr.animate.reorient(0, 0), FadeOut(Group(L[5], R[5])), FadeIn(pl), FadeIn(pr), run_time=1.6)
        names = VGroup(pill("колокол", C_BALL, 22).next_to(pl, DOWN, buff=0.2),
                       pill("перекос", C_TOP, 22).next_to(pr, DOWN, buff=0.2)).fix_in_frame()
        mid = DashedLine(pl.get_bottom() + DOWN * 0.05, pl.get_top() + UP * 0.05).set_stroke(C_NOTE, 2).fix_in_frame()
        peak = pr[int(np.argmax(growth(n, glushkov(n))))]
        arr = Arrow(pr.get_right() + RIGHT * 1.6 + UP * 0.6, peak.get_right() + RIGHT * 0.1, buff=0.05).set_color(C_TOP).fix_in_frame()
        cliff = tx("обрыв", 20, C_TOP).next_to(pr.get_top(), RIGHT, buff=0.5).fix_in_frame()
        self.play(FadeIn(names), ShowCreation(mid), run_time=1.0)
        self.play(GrowArrow(arr), FadeIn(cliff), run_time=1.0)
        self.unsay()
        keep = lab("авторы: перекос не исчезнет при любом числе шариков", 22, C_NOTE).move_to(DOWN * 3.0)
        beat(self, 3)
        self.play(FadeIn(keep), run_time=0.6)
        pad(self, [names[0], names[1], pr])


# ---------- рекорды ----------

class A10(Base3D):
    """Самые высокие башни: перебор наборов (до 9 шариков — все подряд, дальше выборочно); в рекордах — ход-качели;
    ходы линиями между местами складываются в квадрат с усами (рекорд 7 шариков из §3.4: потолок 30, пересчитано)."""
    def construct(self):
        fr = self.frame
        fr.reorient(-6, 22)
        self.add(lab("Самые высокие башни", 34).to_edge(UP, buff=0.35))
        gens = record7()
        row = Row(range(7), gap=0.82, r=0.3, center=UP * 1.6)
        self.play(FadeIn(row.group), run_time=0.7)
        how = lab("до 9 шариков — все наборы подряд · дальше выборочно", 22, C_NOTE).to_edge(UP, buff=1.0)
        beat(self, 1)
        self.play(FadeIn(how), run_time=0.6)
        beat(self, 2)
        self.say("ход-качели: сделаешь дважды — всё как было", C_SWING)
        for b in row.balls.values():
            b[0].set_color(C_SWING)
        self.play(row.move(gens[1]), run_time=0.6)
        self.play(row.move(gens[1]), run_time=0.6)
        back = VGroup(check(C_ORDER, 0.12), tx("как было", 20, C_ORDER)).arrange(RIGHT, buff=0.15).next_to(row.shelf, RIGHT, buff=0.3)
        self.play(FadeIn(back), run_time=0.4)
        self.wait(0.4)
        # рисунок ходов: место — точка, ход — линии своего цвета
        beat(self, 3)
        self.say("нарисуем каждый ход линиями между местами шариков", C_BALL)
        cols = [C_SWING, C_BALL, WHITE]
        pts = [np.array([0.82 * (k - 3), -0.6, 0]) for k in range(7)]
        pic = move_picture(7, gens, cols, layout=pts, R=0.16)
        self.play(FadeIn(pic[1]), FadeIn(pic[2]), run_time=0.6)
        self.play(LaggedStartMap(ShowCreation, pic[0], lag_ratio=0.5), run_time=1.2)
        self.play(FadeOut(row.group), FadeOut(back), run_time=0.5)
        sq = [np.array([*SQUARE_LAYOUT[k], 0]) * 1.1 + UP * 0.4 + LEFT * 2.6 for k in range(7)]
        target = move_picture(7, gens, cols, layout=sq, R=0.16)
        self.play(Transform(pic, target), fr.animate.reorient(10, 26), run_time=1.3)
        name = pill("квадрат с усами", C_SWING, 28).move_to(RIGHT * 3.8 + UP * 1.6).fix_in_frame()
        self.play(FadeIn(name, scale=0.9), run_time=0.7)
        self.unsay()
        rec = VGroup(tx("7 шариков", 22, C_NOTE),
                     VGroup(tx("рекорд", 20, C_SWING), Rectangle(width=3.0, height=0.28).set_fill(C_SWING, 0.8).set_stroke(width=0), tx("30", 22, C_SWING)).arrange(RIGHT, buff=0.15),
                     VGroup(tx("соседи", 20, C_BALL), Rectangle(width=2.1, height=0.28).set_fill(C_BALL, 0.8).set_stroke(width=0), tx("21", 22, C_BALL)).arrange(RIGHT, buff=0.15)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(RIGHT * 3.8 + DOWN * 0.6).fix_in_frame()
        self.play(FadeIn(rec), run_time=0.8)
        self.play(fr.animate.reorient(-8, 24), run_time=1.4)
        pad(self, [name, rec[1], pic])


class A11(Base3D):
    """Предел для любых ходов (гипотеза 7): потолок не выше числа пар + 4,5 хода на шарик (= n²/2 + 4n);
    выведен по рядам до 14 шариков; для 15 — 150, рекорд 148; прежде — ≈ n², и даже он не доказан (§3.8)."""
    def construct(self):
        fr = self.frame
        fr.reorient(0, 20)
        self.add(lab("Предел для любых ходов", 34).to_edge(UP, buff=0.35))
        n = 6
        c = LEFT * 3.6 + UP * 0.2
        pts = [c + 1.6 * np.array([np.cos(PI / 2 - TAU * k / n), np.sin(PI / 2 - TAU * k / n), 0]) for k in range(n)]
        balls = Group(*[ball(k, 0.3).move_to(p) for k, p in enumerate(pts)])
        self.play(FadeIn(balls), run_time=0.6)
        beat(self, 1)
        self.say("пары: линии от каждого шарика к каждому", C_ORDER)
        chords = VGroup(*[Line(pts[i], pts[j]).set_stroke(C_ORDER, 2.5, opacity=0.8) for i in range(n) for j in range(i + 1, n)])
        cnt = Integer(0, font_size=40).set_color(C_ORDER).fix_in_frame().move_to(LEFT * 6.2 + UP * 0.2)
        self.add(cnt, lab("пар", 22, C_ORDER).next_to(cnt, DOWN, buff=0.1))
        for k, l in enumerate(chords):
            self.play(ShowCreation(l), cnt.animate.set_value(k + 1), run_time=0.18)
        self.play(fr.animate.reorient(-15, 30), run_time=1.0)
        rule = VGroup(tx("гипотеза: потолок любой башни не выше", 24),
                      VGroup(pill("число пар", C_ORDER, 24), tx("+", 28), pill("4,5 хода на шарик", C_TOP, 24)).arrange(RIGHT, buff=0.2)
                      ).arrange(DOWN, buff=0.15).move_to(RIGHT * 2.8 + UP * 1.9).fix_in_frame()
        beat(self, 2)
        self.play(FadeIn(rule), run_time=1.0)
        beat(self, 3)
        self.say("предел выведен по рядам до 14 шариков", C_TOP)
        # проверка на 15 шариках: предел 150, рекорд 148
        x, y0, sc = 2.8, -2.4, 0.016
        limit = DashedLine([x - 1.6, y0 + 150 * sc, 0], [x + 1.6, y0 + 150 * sc, 0]).set_stroke(C_TOP, 4).fix_in_frame()
        ll = tx("предел · 150", 20, C_TOP).next_to(limit, RIGHT, buff=0.15).fix_in_frame()
        recb = Rectangle(width=1.0, height=148 * sc).set_fill(C_SWING, 0.8).set_stroke(width=0).move_to([x, y0 + 148 * sc / 2, 0]).fix_in_frame()
        rl = tx("рекорд 15 шариков · 148", 20, C_SWING).next_to(recb, LEFT, buff=0.2).fix_in_frame()
        self.play(ShowCreation(limit), FadeIn(ll), run_time=0.8)
        self.play(GrowFromEdge(recb, DOWN), FadeIn(rl), run_time=1.2)
        gap = tx("не хватило двух", 22, C_TOP).next_to(limit, UP, buff=0.1).fix_in_frame()
        self.play(FadeIn(gap), Indicate(recb, color=C_SWING), run_time=0.8)
        beat(self, 4)
        self.unsay()
        before = VGroup(pill("прежде: предел ≈ вдвое выше", C_NOTE, 20), tx("и даже он не доказан", 20, C_NO)).arrange(RIGHT, buff=0.2)
        before.move_to(DOWN * 3.0).fix_in_frame()
        self.play(FadeIn(before), fr.animate.reorient(10, 26), run_time=1.2)
        pad(self, [chords, rule, limit, recb, before])


# ---------- компас ----------

def c4_top(n):
    """Круги по четыре: потолок по формуле (с поправкой «+1», см. NOTES.md)."""
    return n * (n - 1) // 6 + 1 if n % 3 != 2 else (n * (n - 1) + 4) // 6


class A12(Base3D):
    """За пределом перебора — компас: ходы «круги по четыре соседа»; по маленьким башням угадали формулу и дальнюю
    расстановку; на больших рядах компас распутал её ровно за длину по формуле (§6; высоты — схема по формуле)."""
    def construct(self):
        fr = self.frame
        fr.reorient(-15, 18)
        self.add(lab("Дальше перебора — компас", 34).to_edge(UP, buff=0.35))
        ns = list(range(6, 21))
        vals = [c4_top(n) for n in ns]
        known = 8  # перебор: до 13 шариков
        x0, st, sc = -5.6, 0.74, 0.05
        bars = columns(vals[:known], x0, st, sc, [C_BALL] * known, width=0.36, depth=0.3)
        wall_x = x0 + (known - 0.5) * st
        wall = Rectangle(width=0.06, height=4.0).set_stroke(width=0).set_fill(C_NO, 0.8).move_to([wall_x, 0.1, 0])
        wl = tx("перебор упирается в память", 18, C_NO).next_to(wall, UP, buff=0.1)
        self.play(LaggedStartMap(GrowFromEdge, bars, edge=DOWN, lag_ratio=0.12), run_time=1.4)
        self.play(FadeIn(wall), FadeIn(wl), run_time=0.6)
        comp = compass(0.45).fix_in_frame().move_to(RIGHT * 5.4 + UP * 1.7)
        beat(self, 1)
        self.say("компас из прошлых роликов: угадывает этаж и ведёт вниз", C_COMP)
        self.play(FadeIn(comp, scale=0.6), run_time=0.6)
        self.play(Rotate(comp[2], TAU, about_point=comp[3].get_center()), run_time=1.0)
        row = Row(range(6), gap=0.7, r=0.26, center=UP * 1.9 + LEFT * 1.2)
        beat(self, 2)
        self.say("ход: покрутить по кругу четыре соседних шарика", C_BALL)
        self.play(FadeIn(row.group), run_time=0.5)
        g = cycles4(6)
        for k in (0, 2):
            self.play(row.move(g[k], lift=0.5), run_time=0.8)
        far = ghost(vals[known:], x0 + known * st, st, sc, C_RHYTHM, width=0.36)
        beat(self, 3)
        self.play(FadeOut(row.group), run_time=0.4)
        self.say("по маленьким башням — формула потолка и самая дальняя расстановка", C_RHYTHM)
        self.play(LaggedStartMap(ShowCreation, far, lag_ratio=0.1), fr.animate.reorient(10, 22), run_time=1.6)
        cb = columns(vals[known:], x0 + known * st, st, sc, [C_COMP] * (len(ns) - known), width=0.3, depth=0.25)
        beat(self, 4)
        self.say("компас распутывает её на больших рядах", C_COMP)
        self.play(LaggedStartMap(GrowFromEdge, cb, edge=DOWN, lag_ratio=0.15), Rotate(comp[2], TAU, about_point=comp[3].get_center()),
                  fr.animate.reorient(15, 22), run_time=2.4)
        self.unsay()
        res = VGroup(check(C_ORDER, 0.14), tx("путь компаса — ровно той длины, что дала формула", 24, C_ORDER)).arrange(RIGHT, buff=0.2)
        res.move_to(DOWN * 2.95).fix_in_frame()
        self.play(FadeIn(res), run_time=0.8)
        self.add(lab("высоты — схема по формуле", 18, C_NOTE).to_corner(UR, buff=0.4).shift(DOWN * 0.6))
        self.play(fr.animate.reorient(-5, 20), run_time=1.4)
        pad(self, [res, far, comp], C_COMP)


class A13(Base):
    """Чат-боты: задача — программа распутывания только данными ходами; проверить легко; для известных наборов пишут,
    для новых не дали даже правильной (§3.12); экзамен для ИИ и открытые соревнования (больше десятка, §3.11)."""
    def construct(self):
        self.add(head("А чат-боты?"))
        bub = RoundedRectangle(width=7.6, height=1.5, corner_radius=0.3).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.08).move_to(UP * 1.6 + LEFT * 1.4)
        tail = Polygon(bub.get_corner(DL) + RIGHT * 0.8, bub.get_corner(DL) + RIGHT * 1.4, bub.get_corner(DL) + RIGHT * 0.5 + DOWN * 0.5)
        tail.set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.08)
        task = VGroup(tx("напиши программу:", 24, C_NOTE), tx("распутай любую расстановку только этими ходами", 24)).arrange(DOWN, buff=0.1).move_to(bub)
        pic = move_picture(5, star(5)[:2] + [neighbours(5)[3]], [C_BALL, WHITE, C_SWING]).scale(0.8).next_to(bub, RIGHT, buff=0.5)
        beat(self, 1)
        self.play(FadeIn(bub), FadeIn(tail), Write(task), run_time=1.4)
        self.play(FadeIn(pic), run_time=0.6)
        ver = VGroup(tx("проверка ответа:", 22, C_NOTE), pill("запустить", C_ORDER, 22), check(C_ORDER, 0.14)).arrange(RIGHT, buff=0.25)
        ver.move_to(UP * 0.0)
        beat(self, 2)
        self.play(FadeIn(ver), run_time=0.8)
        rows = VGroup(
            VGroup(check(C_ORDER, 0.12), tx("известные наборы — программу пишут", 24, C_ORDER)).arrange(RIGHT, buff=0.25),
            VGroup(cross(C_NO, 0.12), tx("новые наборы — не дали даже правильной", 24, C_NO)).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(DOWN * 1.1)
        beat(self, 3)
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.15), run_time=0.8)
        self.play(Indicate(rows[1], color=C_NO), run_time=0.8)
        beat(self, 4)
        crowd = VGroup(*[Dot(radius=0.04).set_color(C_NOTE) for _ in range(60)]).arrange_in_grid(3, 20, buff=0.08)
        out = VGroup(pill("экзамен для ИИ", C_COMP, 22), VGroup(crowd, tx("открытые соревнования · больше десятка", 20, C_NOTE)).arrange(DOWN, buff=0.1)
                     ).arrange(RIGHT, buff=0.6).move_to(DOWN * 2.6)
        self.play(FadeIn(out[0]), LaggedStartMap(FadeIn, out[1], lag_ratio=0.02), run_time=1.4)
        pad(self, [task, pic, ver, rows[0], rows[1], out[0], out[1]])


# ---------- акт 3 — главное ----------

class A14(Base3D):
    """Возврат к вопросу: у наборов с простым правилом потолок — формула с ритмом; у кольца Глушкова формула есть;
    предел — пары + 4,5 хода на шарик; всё — гипотезы, проверенные перебором и компасом."""
    def construct(self):
        fr = self.frame
        q = lab("Насколько высокой бывает башня — и можно ли узнать, не строя?", 28).to_edge(UP, buff=0.35)
        self.add(q)
        pos, ls, dots, d, by, grp, dot_of = tower_group(6, glushkov(6), shift=LEFT * 3.6 + IN * 2.6, rise=0.3, spread=0.2, r=0.05, lines=False)
        fr.reorient(-20, 72).set_height(9.5)
        self.play(FadeIn(grp), run_time=1.0)
        ans = pill("похоже, да", C_ORDER, 28).move_to(RIGHT * 2.6 + UP * 2.2).fix_in_frame()
        beat(self, 1)
        self.play(FadeIn(ans), fr.animate.reorient(10, 72), run_time=1.2)
        rows = [(icon_rhythm(0.45), "простое правило → потолок — формула с ритмом", C_RHYTHM),
                (icon_ring(0.4), "кольцо Глушкова: формула есть", C_BALL),
                (icon_records(0.35), "предел: пары + 4,5 хода на шарик", C_TOP)]
        tbl = VGroup(*[VGroup(i, tx(t, 22, col)).arrange(RIGHT, buff=0.25) for i, t, col in rows])
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(RIGHT * 2.6 + UP * 0.4).fix_in_frame()
        for k, r in enumerate(tbl, 1):
            beat(self, k)
            self.play(FadeIn(r, shift=RIGHT * 0.15), run_time=0.8)
        self.play(fr.animate.reorient(-15, 74), run_time=1.6)
        beat(self, 4)
        hyp = VGroup(warn_icon(C_COMP, 0.22), VGroup(tx("всё это гипотезы:", 22, C_COMP), tx("проверены перебором и компасом, не доказаны", 22, C_COMP)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)).arrange(RIGHT, buff=0.2)
        hyp.move_to(RIGHT * 2.6 + DOWN * 1.2).fix_in_frame()
        self.play(FadeIn(hyp), run_time=0.8)
        top = dot_of[by[max(by)][0]]
        self.play(Flash(top, color=C_TOP, flash_radius=0.4), fr.animate.reorient(-30, 74), run_time=2.0)
        pad(self, [ans, *tbl, hyp])


# ---------- приложение: те же станции формулами ----------

class F01(Base):
    """Переход в приложение: башня со всеми ходами = граф Кэли; расстановка = перестановка; набор ходов = образующие."""
    def construct(self):
        ic = icon_build(2.0)
        self.add(ic)
        self.play(ic.animate.scale(0.5).to_corner(UL, buff=0.6), run_time=1)
        self.add(head("Образ → формула"), app_tag().to_corner(UR, buff=0.35))
        rows = [("башня со всеми ходами", "граф Кэли  Γ(Sn, S)"),
                ("расстановка", "перестановка  σ ∈ Sn :  (2 0 3 1)"),
                ("набор ходов", "образующие  S = {g1, g2, …}"),
                ("ход", "σ → σ·g")]
        tbl = VGroup(*[VGroup(tx(a, 24, C_BALL), tx("→", 24, C_NOTE), tx(b, 24, C_FORM)).arrange(RIGHT, buff=0.3) for a, b in rows])
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(UP * 0.4)
        icons = VGroup(*[STATION_ICON[s](0.4) for s in ("Стройка", "Ритм", "Глушков", "Рекорды", "Компас")]).arrange(RIGHT, buff=0.5)
        pair = VGroup(tx("у каждой карточки — значок её сцены:", 22, C_NOTE), icons).arrange(RIGHT, buff=0.35).move_to(DOWN * 2.2)
        beat(self, 1)
        self.play(FadeIn(pair[0]), LaggedStartMap(FadeIn, icons, lag_ratio=0.25), run_time=1.4)
        beat(self, 2)
        for r in tbl:
            self.play(FadeIn(r, shift=RIGHT * 0.15), run_time=0.6)
        self.add(tx("в формулах шарики нумеруются с нуля, как в статье", 18, C_NOTE).move_to(DOWN * 2.85))
        pad(self, [*tbl, *icons])


class F02(Base):
    """∥ Стройка: этаж = расстояние, потолок = диаметр, рост γ; поиск в ширину; по факту — 3 бита на расстановку
    (bfs bitmask), ход — сразу для всего этажа на видеокарте; S₁₁: 2352 с → 0,6 с (табл. 1–2)."""
    def construct(self):
        formal_card(self, "Стройка", "4–5", "Этаж, потолок, рост", icon_build(1.6),
                    ["этаж(σ) = d(e, σ) — кратчайший путь",
                     "рост: γ(k) = сколько σ на этаже k",
                     tx("4 шарика: γ = 1 3 5 6 5 3 1 → диаметр = 6", 28, C_TOP),
                     "E(k+1) = S·E(k) − всё виденное"],
                    ["3 бита на расстановку · ход — сразу для всего этажа",
                     "11 шариков: GAP 2352 с → видеокарта 0,6 с"],
                    "волна от камня в пруду: круг за кругом", at=[0, 1, 1, 2, 3, 4, 4])


class F03(Base):
    """∥ Ритм: потолок D(n) = pᵢ(n), i — остаток n от деления на s (квазимногочлен); как находят; високосный год."""
    def construct(self):
        formal_card(self, "Ритм", "6–7", "Ритм = квазимногочлен", icon_rhythm(1.8),
                    ["D(n) = p_i(n),   i = остаток n при делении на s",
                     tx("первый с любым:  D = ⌊3(n − 1)/2⌋ → 3 4 6 7 9 10", 28, C_RHYTHM),
                     "s = 2, 4, 6, 8 · многочлены 1-й или 2-й степени"],
                    ["перебор: D для n ≤ 15 (смежные классы — до 42)",
                     "по нескольку точек на остаток → парабола → остальные — проверка"],
                    "високосный год: правило с ритмом 4", at=[1, 2, 2, 3, 3, 4])


class F04(Base):
    """∥ Глушков: (3n² − 8n + 9)/4 для нечётных, (3n² − 8n + 12)/4 для чётных, от n = 5 (гипотеза 11, OEIS A039745);
    первые этажи — Фибоначчи; пересчитано нами для n = 5…12."""
    def construct(self):
        formal_card(self, "Глушков", "8", "Формула Глушкова", icon_ring(1.6),
                    [tx("нечётные:  D = (3n^2 − 8n + 9) / 4", 32, C_RHYTHM),
                     tx("чётные:      D = (3n^2 − 8n + 12) / 4", 32, C_BALL),
                     "от n = 5 · ходы: L = сдвиг влево, X = (0 1)",
                     "первые этажи: γ(k) = γ(k − 1) + γ(k − 2)"],
                    ["пересчитали: n = 5…12 · для 12 перебор 87 = формула 87",
                     "3n^2/4 — известно давно; новое — точная формула"], at=[1, 2, 3, 6, 5, 4])


class F05(Base):
    """∥ колокол: рост как распределение; обмены соседей → нормальный закон (Диаконис), середина D/2;
    Глушков — перекос < −0,5 (гипотеза 12), похоже на Гумбеля (§4.2)."""
    def construct(self):
        pics = VGroup(profile(growth(6, neighbours(6)), width=1.3, step=0.12), profile(growth(6, glushkov(6)), width=1.3, step=0.12)).arrange(RIGHT, buff=0.4, aligned_edge=DOWN)
        formal_card(self, "Глушков", "9", "Колокол = распределение", pics,
                    ["рост γ(k) / n!  — доля расстановок на этаже k",
                     tx("соседи → нормальный закон · середина = D/2", 30, C_BALL),
                     tx("Глушков → перекос < −0,5 · похоже на Гумбеля", 30, C_TOP)],
                    ["нормальный закон для соседей доказал Диаконис",
                     "Гумбель — подгонка по n ≤ 15, не доказано"],
                    "Гумбель описывает самые сильные паводки года", at=[0, 1, 2, 1, 2, 2])


class F06(Base):
    """∥ Рекорды: качели g·g = e; квадрат с усами — один 4-цикл и два хвоста; предел n²/2 + 4n (гипотеза 7);
    подгонка по n ≤ 14: n²/2 + 4n − 22,5; n = 15: 150 и 148; доказано пока exp(O((log n)⁴ log log n)) (Хелфготт, Шереш)."""
    def construct(self):
        formal_card(self, "Рекорды", "10–11", "Рекорды формулами", icon_records(1.5),
                    ["качели:  g·g = e   (инволюция)",
                     "квадрат с усами: один цикл из 4 мест + два хвоста",
                     tx("предел:  D ≤ n^2/2 + 4n  =  n(n − 1)/2 + 4,5n", 32, C_TOP)],
                    ["подгонка по n ≤ 14: n^2/2 + 4n − 22,5 · n = 15: 150, рекорд 148",
                     "доказано пока только exp(O((log n)^4 log log n))"], at=[1, 2, 3, 4, 4])


class F07(Base):
    """∥ Компас: нейросеть оценивает d(e, σ), поиск лучом; круги по четыре — n(n − 1)/6 + 1 (n = 3k, 3k + 1),
    n(n − 1)/6 + 2/3 (n = 3k + 2); в статье «− 1» — перебор n = 6…12 даёт «+ 1»."""
    def construct(self):
        formal_card(self, "Компас", "12", "Компас и круги по четыре", icon_compass(1.6),
                    ["компас: нейросеть(σ) ≈ d(e, σ) · поиск лучом",
                     tx("D = n(n − 1)/6 + 1     при n = 3k, 3k + 1", 30, C_RHYTHM),
                     tx("D = n(n − 1)/6 + 2/3  при n = 3k + 2", 30, C_RHYTHM),
                     tx("в статье напечатано «− 1»: перебор n = 6…12 даёт «+ 1»", 24, C_NO)],
                    ["перебор до 13 шариков · дальше компас: путь = формула",
                     "довод, не доказательство: путь компаса может быть не кратчайшим"], at=[0, 1, 1, 2, 2, 2])


class F08(Base):
    """По факту в коде: три строки на CayleyPy (проверено, версия с PyPI) и тот же перебор этажами в шесть строк."""
    def construct(self):
        self.add(head("Как это выглядит в коде").shift(DOWN * 0.1), app_tag())
        lines = [("from cayleypy import CayleyGraph, PermutationGroups", WHITE),
                 ("graph = CayleyGraph(PermutationGroups.lx(7))   # кольцо Глушкова", C_BALL),
                 ("graph.bfs().layer_sizes   # [1, 2, 3, 5, 8, 13, 21, 33, …, 21, 2]", C_ORDER),
                 ("", WHITE),
                 ("def growth(start, moves):          # под капотом: перебор этажами", C_NOTE),
                 ("    seen, layer, sizes = {start}, {start}, []", WHITE),
                 ("    while layer:", WHITE),
                 ("        sizes.append(len(layer))", C_BALL),
                 ("        layer = {m(s) for s in layer for m in moves} - seen", C_BALL),
                 ("        seen |= layer", WHITE),
                 ("    return sizes                   # рост: этаж за этажом", C_ORDER)]
        code = VGroup(*[Text(l or " ", font="Menlo", font_size=21).set_color(c) for l, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        cw = Text("m" * 10, font="Menlo", font_size=21).get_width() / 10  # ширина символа: отступы Python не теряются
        for l, (s, _) in zip(code, lines):
            l.shift(RIGHT * cw * (len(s) - len(s.lstrip(" "))))
        box = SurroundingRectangle(code, buff=0.3).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.06)
        VGroup(box, code).move_to(DOWN * 0.15)
        self.play(FadeIn(box))
        beat(self, 1)
        for l in code[:3]:
            self.play(Write(l), run_time=0.5)
        beat(self, 2)
        self.play(Indicate(code[2], color=C_ORDER), run_time=1)
        beat(self, 3)
        for l in code[3:]:
            self.play(Write(l), run_time=0.4)
        self.play(Indicate(code[8], color=C_BALL), run_time=1)
        self.add(tx("библиотека: pip install cayleypy · вывод проверен", 20, C_NOTE).next_to(box, DOWN, buff=0.2))
        pad(self, [code[1], code[2], code[4], code[8], code[10]])


class F09(Base):
    """Где встречается: прямо — сети процессоров (потолок = худшая задержка), перевороты участков ДНК (§5), головоломки;
    по аналогии — планирование мелкими шагами."""
    def construct(self):
        self.add(head("Где это встречается"), app_tag())
        rows = [("прямо", "сети процессоров: потолок = самая долгая задержка сообщения", WHITE),
                ("прямо", "биология: переворот участка ДНК = ход, расстояние между геномами = этаж", WHITE),
                ("прямо", "головоломки: кубики, кольца, шарики", WHITE),
                ("аналогия", "планирование: от одного состояния к другому мелкими шагами", C_NOTE)]
        tbl = VGroup()
        for a, b, col in rows:
            tbl.add(VGroup(pill(a, C_ORDER if a == "прямо" else C_NOTE, 20), tx(b, 23, col)).arrange(RIGHT, buff=0.35))
        tbl.arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(UP * 0.6)
        for k, r in enumerate(tbl, 1):
            beat(self, k)
            self.play(FadeIn(r), run_time=0.6)
        chain = VGroup(pill("быстрый перебор", C_BALL, 22), tx("→", 26, C_NOTE), pill("ритм", C_RHYTHM, 22), tx("→", 26, C_NOTE),
                       pill("гипотеза", C_TOP, 22), tx("→", 26, C_NOTE), pill("компас проверяет дальше", C_COMP, 22)).arrange(RIGHT, buff=0.2)
        chain.move_to(DOWN * 2.3)
        beat(self, 5)
        self.play(LaggedStartMap(FadeIn, chain, lag_ratio=0.3), run_time=1.8)
        pad(self, [*tbl, chain[0], chain[2], chain[4], chain[6]])


class A15(Base):
    """Кто и когда: Глушков 1968; Диаконис — колокол; Бабаи — гипотеза о малом диаметре; Хелфготт–Шереш 2014;
    CayleyPy: кубики и кольцо — февраль 2025, эта статья — сентябрь 2025, v2 — апрель 2026; что проверено, что гипотеза."""
    def construct(self):
        self.add(head("Кто и когда"))
        y = 1.5
        line = Line(LEFT * 6, RIGHT * 6).shift(UP * y).set_stroke(C_NOTE, 2)
        self.play(ShowCreation(line), run_time=0.6)
        events = [("1968", "Глушков: кольцо с двумя ходами", C_NOTE),
                  ("2014", "Хелфготт, Шереш: лучшая доказанная граница", C_NOTE),
                  ("02.2025", "CayleyPy: кубики и кольцо", C_NOTE),
                  ("09.2025", "эта статья · 49 авторов", WHITE),
                  ("04.2026", "вторая версия статьи", WHITE)]
        xs = np.linspace(-4.9, 4.9, len(events))  # равные шаги: важен порядок, а не масштаб лет
        names = VGroup(pill("Перси Диаконис: колокол для соседей", C_BALL, 20),
                       pill("Ласло Бабаи: потолок мал по сравнению с башней", C_TOP, 20)).arrange(RIGHT, buff=0.3).move_to(UP * 0.15)
        for k, ((yr, a, col), x) in enumerate(zip(events, xs)):
            if k == 0:
                beat(self, 1)
            if k == 2:
                beat(self, 2)
                self.play(FadeIn(names[0]), run_time=0.7)
                beat(self, 3)
                self.play(FadeIn(names[1]), run_time=0.7)
                beat(self, 4)
            up = k % 2 == 0
            label = VGroup(tx(yr, 24, col), tx(a, 17, col)).arrange(DOWN, buff=0.05).move_to([x, y + (0.6 if up else -0.6), 0])
            self.play(FadeIn(Dot([x, y, 0], radius=0.09).set_color(col)), FadeIn(label), run_time=0.6)
        rows = [("Проверено", "перебор до 15 шариков (смежные классы — до 42) · компас дальше", WHITE),
                ("Гипотезы", "ритм, формула Глушкова, предел n²/2 + 4n, рекорды — около 200 гипотез", C_RHYTHM),
                ("Неточность", "круги по четыре: в статье «− 1», перебор даёт «+ 1»", C_NO),
                ("Образ", "башня = граф Кэли, этаж = расстояние — точно; высоты в сцене 12 — схема", C_NOTE)]
        tbl = VGroup()
        for k, (a, b, col) in enumerate(rows):
            r = VGroup(tx(a, 20, C_NOTE), tx(b, 19, col))
            r[0].move_to([-6.2 + r[0].get_width() / 2, 0, 0])
            r[1].move_to([-4.4 + r[1].get_width() / 2, 0, 0])
            r.shift(DOWN * (0.85 + k * 0.45))
            tbl.add(r)
        beat(self, 5)
        for r in tbl:
            self.play(FadeIn(r, shift=RIGHT * 0.15), run_time=0.7)
        pad(self, [*names, *tbl])
