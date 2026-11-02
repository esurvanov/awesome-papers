"""Слой подписей поверх 3D-фильма (прозрачный фон): плашки, вопросы, счётчики и полоса «мы здесь» со значками.
Время — настоящие секунды по началам фраз озвучки (как у 3D-сцены, blender/film.py), поэтому слой совпадает с картинкой и голосом.
Рендер: uv run manimgl papers/2509.19162-growth/overlays.py A01 -w -t --video_dir videos/2509.19162-growth/film"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(ROOT / "core" / "pipeline"))
sys.path.insert(0, str(HERE))
from manimlib import *
from manimkit import *
import narration as N
import passport as P
from timing import phrase_starts
from station import C_BALL, C_ORDER, C_TOP, C_RHYTHM, C_SWING, C_COMP, C_NO, C_NOTE, mini_train
from icons import film_bar

LEAD, TAIL = 0.4, 0.8


def plate(mob, pad=0.22, opacity=0.62):
    """Тёмная подложка под подпись — читается на любом фоне 3D."""
    bg = RoundedRectangle(width=mob.get_width() + 2 * pad, height=mob.get_height() + 2 * pad, corner_radius=0.12)
    bg.set_stroke(width=0).set_fill(BLACK, opacity).move_to(mob)
    return VGroup(bg, mob)


class Overlay(Scene):
    def setup(self):
        super().setup()
        self.camera.background_rgba = [0, 0, 0, 0]
        code = type(self).__name__
        st = {c: s for c, s, *_ in P.SCENES}[code]
        self.add(film_bar(P.STATIONS, P.STATIONS.index(st)))
        wav = ROOT / "videos" / HERE.name / "audio" / f"{code}.realtime.wav"
        starts, length = phrase_starts(wav, N.TEXT[code])
        self.P = [LEAD + t for t in starts]
        self.L = LEAD + length + TAIL

    def at(self, k, offset=0.0):
        """Дождаться начала фразы k (+ сдвиг), в настоящих секундах."""
        target = self.P[k] + offset
        if target > self.time + 0.02:
            self.wait(target - self.time)

    def finish(self):
        if self.L > self.time:
            self.wait(self.L - self.time)


class A01(Overlay):
    def construct(self):
        t1 = plate(tx("Сортировочная станция", 34)).to_corner(UL, buff=0.4)
        self.play(FadeIn(t1), run_time=0.8)
        self.at(1)
        lab = plate(tx("состав · вагоны с номерами вперемешку", 28, C_BALL)).to_edge(UP, buff=0.4)
        self.play(FadeOut(t1), FadeIn(lab), run_time=0.6)
        self.at(2)
        goal = VGroup(tx("цель — по порядку:", 26, C_ORDER), mini_train((0, 1, 2, 3, 4), C_ORDER, 0.42)).arrange(RIGHT, buff=0.3)
        goal = plate(goal).to_edge(UP, buff=0.4)
        self.play(FadeOut(lab), FadeIn(goal), run_time=0.6)
        self.at(3)
        rule = plate(VGroup(tx("манёвры этой станции:", 24, C_NOTE), tx("⇄ поменять двух соседей", 28, WHITE)).arrange(DOWN, buff=0.1))
        rule.to_corner(UR, buff=0.4)
        self.play(FadeIn(rule), run_time=0.6)
        self.at(4)
        cnt = plate(tx("меняем соседей 2 и 4 — через съезд на соседний путь", 26, C_SWING)).to_edge(DOWN, buff=1.5)
        self.play(FadeIn(cnt), run_time=0.5)
        self.at(5)
        q = plate(VGroup(tx("Сколько манёвров нужно", 40), tx("на самый запутанный состав?", 40)).arrange(DOWN, buff=0.1), pad=0.3)
        q.to_edge(UP, buff=0.5)
        self.play(FadeOut(goal), FadeOut(rule), FadeOut(cnt), FadeIn(q), run_time=0.8)
        self.at(6)
        q2 = plate(tx("…и можно ли узнать это, не пробуя все составы?", 28, C_NOTE)).next_to(q, DOWN, buff=0.25)
        self.play(FadeIn(q2), run_time=0.6)
        self.at(7)
        hard = plate(tx("для компьютера — из самых трудных задач", 28, C_NO)).to_edge(DOWN, buff=1.5)
        self.play(FadeIn(hard), run_time=0.6)
        self.at(8)
        gl = plate(VGroup(tx("1968", 34, WHITE), tx("кибернетик Глушков задал похожий вопрос", 26, C_NOTE)).arrange(RIGHT, buff=0.3))
        gl.to_edge(DOWN, buff=1.5)
        self.play(FadeOut(hard), FadeOut(q2), FadeIn(gl), run_time=0.7)
        self.finish()


class A04(Overlay):
    def construct(self):
        t = plate(tx("Маленькая станция · 4 вагона", 32)).to_corner(UL, buff=0.4)
        self.play(FadeIn(t), run_time=0.6)
        self.at(1)
        rule = plate(VGroup(tx("манёвр станции:", 24, C_NOTE), tx("⇄ поменять двух соседей", 28, WHITE)).arrange(DOWN, buff=0.1)).to_corner(UR, buff=0.4)
        how = plate(tx("соседи 3 и 4 меняются через съезд", 26, C_SWING)).to_edge(DOWN, buff=1.5)
        self.play(FadeIn(rule), FadeIn(how), run_time=0.6)
        self.at(2)
        tower = plate(tx("вышка: все 24 состава — по этажам", 30, C_BALL)).to_edge(UP, buff=0.4)
        self.play(FadeOut(t), FadeOut(how), FadeIn(tower), run_time=0.6)
        self.at(3)
        steps = VGroup(mini_train((1, 0, 3, 2), C_BALL, 0.3), tx("→", 26), mini_train((0, 1, 3, 2), C_BALL, 0.3), tx("→", 26),
                       mini_train((0, 1, 2, 3), C_ORDER, 0.3)).arrange(RIGHT, buff=0.2)
        defn = plate(VGroup(tx("этаж = сколько манёвров до порядка", 28, WHITE), VGroup(steps, tx("2 манёвра → этаж 2", 24, C_SWING)).arrange(RIGHT, buff=0.4)
                            ).arrange(DOWN, buff=0.18), pad=0.3).to_edge(DOWN, buff=1.5)
        self.play(FadeOut(tower), FadeIn(defn), run_time=0.7)
        self.at(4)
        low = plate(VGroup(tx("этаж 0 · порядок", 28, C_ORDER), mini_train((0, 1, 2, 3), C_ORDER, 0.34)).arrange(RIGHT, buff=0.3)).to_edge(UP, buff=0.4)
        self.play(FadeOut(defn), FadeIn(low), run_time=0.6)
        self.at(5)
        one = plate(VGroup(tx("этаж 1 · 3 состава", 28, C_BALL), tx("в каждом перепутаны два соседа", 24, C_NOTE)).arrange(DOWN, buff=0.08)).to_edge(UP, buff=0.4)
        self.play(FadeOut(low), FadeIn(one), run_time=0.6)
        self.at(6)
        counts = [1, 3, 5, 6, 5, 3, 1]
        bars = VGroup()
        for f, c in enumerate(counts):
            col = C_ORDER if f == 0 else C_TOP if f == 6 else C_BALL
            bars.add(VGroup(tx(str(f), 20, C_NOTE), Rectangle(width=0.35 * c, height=0.26).set_stroke(col, 2).set_fill(col, 0.7), tx(str(c), 20, col)).arrange(RIGHT, buff=0.12))
        bars.arrange(UP, aligned_edge=LEFT, buff=0.08)
        chart = plate(VGroup(tx("этаж · составов", 20, C_NOTE), bars).arrange(DOWN, aligned_edge=LEFT, buff=0.15), pad=0.25).to_corner(UR, buff=0.4).shift(DOWN * 0.3)
        self.play(FadeOut(one), FadeOut(rule), FadeIn(chart), run_time=0.7)
        self.finish()


class A05(Overlay):
    def construct(self):
        t = plate(VGroup(tx("потолок", 34, C_TOP), tx("верхний этаж вышки", 24, C_NOTE)).arrange(DOWN, buff=0.08)).to_corner(UL, buff=0.4)
        self.play(FadeIn(t), run_time=0.6)
        self.at(1)
        hard = plate(VGroup(tx("самый запутанный — задом наперёд", 26, C_TOP), mini_train((3, 2, 1, 0), C_TOP, 0.42)).arrange(RIGHT, buff=0.3)).to_edge(UP, buff=0.4)
        self.play(FadeIn(hard), run_time=0.6)
        self.at(2)
        seq = [(3, 2, 1, 0), (2, 3, 1, 0), (2, 1, 3, 0), (1, 2, 3, 0), (1, 2, 0, 3), (1, 0, 2, 3), (0, 1, 2, 3)]
        col = VGroup(*[VGroup(tx(str(k), 20, C_NOTE), mini_train(p, C_ORDER if k == 6 else C_BALL, 0.26)).arrange(RIGHT, buff=0.2) for k, p in enumerate(seq)])
        col.arrange(DOWN, aligned_edge=LEFT, buff=0.07)
        panel = plate(VGroup(col, tx("6 манёвров", 26, C_TOP)).arrange(DOWN, buff=0.15), pad=0.25).to_edge(LEFT, buff=0.4).shift(DOWN * 0.3)
        self.play(FadeIn(panel), run_time=0.6)
        self.at(3)
        q = plate(tx("как диспетчер строит вышку?", 30)).to_edge(UP, buff=0.4)
        self.play(FadeOut(hard), FadeOut(panel), FadeOut(t), FadeIn(q), run_time=0.6)
        self.at(4)
        rows = VGroup(VGroup(tx("этаж 0:", 20, C_NOTE), mini_train((0, 1, 2, 3), C_ORDER, 0.2)).arrange(RIGHT, buff=0.2),
                      VGroup(tx("этаж 1:", 20, C_NOTE), *[mini_train(p, C_BALL, 0.2) for p in ((1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2))]).arrange(RIGHT, buff=0.15))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        jr_head = tx("журнал", 26, C_COMP)
        jr = VGroup(jr_head, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        jbox = RoundedRectangle(width=jr.get_width() + 0.7, height=3.6, corner_radius=0.15).set_stroke(C_COMP, 3).set_fill(BLACK, 0.7)
        jr.move_to(jbox).align_to(jbox, UP).shift(DOWN * 0.3)
        journal = VGroup(jbox, jr).to_corner(UR, buff=0.4).shift(DOWN * 0.6)
        self.play(FadeIn(journal), run_time=0.7)
        self.at(5)
        h = plate(tx("от каждого состава этажа — все манёвры", 26, WHITE)).to_edge(DOWN, buff=1.5)
        self.play(FadeOut(q), FadeIn(h), run_time=0.5)
        self.at(6)
        new = VGroup(tx("этаж 2:", 20, C_NOTE), mini_train((1, 0, 3, 2), C_BALL, 0.2)).arrange(RIGHT, buff=0.2).next_to(rows, DOWN, buff=0.15, aligned_edge=LEFT)
        h2 = plate(tx("новый состав → на следующий этаж", 26, C_ORDER)).to_edge(DOWN, buff=1.5)
        self.play(FadeIn(new), FadeOut(h), FadeIn(h2), run_time=0.6)
        self.at(7)
        dup = VGroup(tx("повтор:", 20, C_NOTE), mini_train((1, 0, 2, 3), C_NOTE, 0.2)).arrange(RIGHT, buff=0.2).next_to(new, DOWN, buff=0.15, aligned_edge=LEFT)
        strike = Line(dup.get_left(), dup.get_right()).set_stroke(C_NO, 4)
        h3 = plate(tx("уже есть в журнале → пропускаем", 26, C_NO)).to_edge(DOWN, buff=1.5)
        self.play(FadeIn(dup), ShowCreation(strike), FadeOut(h2), FadeIn(h3), run_time=0.7)
        self.finish()


class A06(Overlay):
    def construct(self):
        t = plate(tx("Станции бывают больше", 32)).to_corner(UL, buff=0.4)
        self.play(FadeIn(t), run_time=0.6)
        self.at(1)
        n = plate(tx("15 вагонов", 34, C_BALL)).to_corner(UL, buff=0.4)
        cnt = Integer(0, font_size=64, group_with_commas=False).set_color(C_BALL)
        lab = tx("разных составов", 26, C_NOTE)
        box_ = plate(VGroup(cnt, lab).arrange(DOWN, buff=0.1), pad=0.3).to_edge(UP, buff=0.5)
        self.play(FadeOut(t), FadeIn(n), FadeIn(box_), run_time=0.5)
        self.play(ChangeDecimalToValue(cnt, 1307674368000), run_time=3.0)
        big = plate(VGroup(tx("1 307 674 368 000 — больше триллиона", 30, C_BALL), tx("разных составов", 26, C_NOTE)).arrange(DOWN, buff=0.1),
                    pad=0.3).to_edge(UP, buff=0.5)  # подложка — по новой, более широкой строке
        self.play(FadeOut(box_), FadeIn(big), run_time=0.4)
        self.at(2)
        years = plate(VGroup(tx("по составу в секунду", 24, C_NOTE), tx("> 40 000 лет", 44, WHITE)).arrange(DOWN, buff=0.1), pad=0.3).to_edge(DOWN, buff=1.5)
        self.play(FadeIn(years), run_time=0.6)
        self.at(3)
        days = plate(VGroup(tx("программа авторов", 24, C_NOTE), tx("несколько дней", 40, C_ORDER)).arrange(DOWN, buff=0.1), pad=0.3).to_edge(DOWN, buff=1.5)
        self.play(FadeOut(years), FadeIn(days), run_time=0.6)
        self.at(4)
        sw = plate(VGroup(tx("11 вагонов, одна и та же работа:", 24, C_NOTE),
                          VGroup(tx("прежняя — 39 мин", 34, C_NOTE), tx("новая — 0,6 с", 34, C_ORDER)).arrange(RIGHT, buff=0.8),
                          tx("прежние — медленнее до тысячи раз", 26, C_NO)).arrange(DOWN, buff=0.15), pad=0.3).to_edge(DOWN, buff=1.5)
        self.play(FadeOut(days), FadeIn(sw), run_time=0.6)
        self.finish()


from icons import badge, COLOR


class A02(Overlay):
    def construct(self):
        card = VGroup(tx("arXiv 2509.19162 · проект CayleyPy · 49 авторов", 22, C_NOTE),
                      tx("CayleyPy Growth", 46, WHITE), tx("быстрый подсчёт роста и сотни новых гипотез о графах Кэли", 26, C_NOTE)).arrange(DOWN, buff=0.15)
        c = plate(card, pad=0.45, opacity=0.75).move_to(UP * 1.6)
        self.play(FadeIn(c, shift=UP * 0.2), run_time=0.8)
        self.at(1)
        series = VGroup(*[VGroup(badge(n, "done" if n != "Все составы" else "active", 0.7), tx(t, 20, C_NOTE)).arrange(DOWN, buff=0.1)
                          for n, t in (("Обзор", "кубики Рубика"), ("Глушков", "кольцо"), ("Все составы", "станции · эта"))]).arrange(RIGHT, buff=1.2)
        s = plate(VGroup(tx("третья статья серии", 22, WHITE), series).arrange(DOWN, buff=0.2), pad=0.3).move_to(DOWN * 0.6)
        self.play(FadeIn(s), run_time=0.7)
        self.at(2)
        d = plate(tx("23 сентября 2025 · версия 2 — 1 апреля 2026", 24, C_NOTE)).next_to(c, DOWN, buff=0.2)
        self.play(FadeIn(d), run_time=0.5)
        self.at(3)
        gist = VGroup(tx("составы — во много раз быстрее", 26, C_BALL), tx("→", 28), tx("ответ — простые формулы", 26, C_RHYTHM)).arrange(RIGHT, buff=0.25)
        g = plate(gist, pad=0.3).to_edge(DOWN, buff=1.6)
        self.play(FadeOut(s), FadeIn(g), run_time=0.6)
        self.at(4)
        h = plate(tx("≈ 200 гипотез", 34, C_TOP)).next_to(g, UP, buff=0.25)
        self.play(FadeIn(h), run_time=0.5)
        self.finish()


class A03(Overlay):
    def construct(self):
        head = plate(tx("Шесть вопросов", 36)).to_edge(UP, buff=0.4)
        self.play(FadeIn(head), run_time=0.6)
        qs = [("Все составы", "как записать все составы,", "даже если их триллионы?"), ("Формула", "можно ли посчитать ответ", "формулой, не записывая?"),
              ("Глушков", "что нашли на вопрос", "Глушкова 1968 года?"), ("Худшая станция", "какая станция хуже всех?", "есть ли общий предел?"),
              ("Проверка", "как проверить там,", "где записать всё нельзя?"), ("Итог", "что из этого", "следует")]
        tiles = VGroup()
        for k, (name, a, b) in enumerate(qs):
            body = VGroup(tx(f"{k + 1}", 30, COLOR[name]), VGroup(tx(a, 22), tx(b, 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.06)).arrange(RIGHT, buff=0.25)
            row = VGroup(badge(name, "active", 0.85), body).arrange(RIGHT, buff=0.3)
            bg = RoundedRectangle(width=4.2, height=1.6, corner_radius=0.15).set_stroke(COLOR[name], 2).set_fill(BLACK, 0.68)
            row.set_width(min(row.get_width(), 3.9)).move_to(bg)
            tiles.add(VGroup(bg, row))
        tiles.arrange_in_grid(2, 3, buff=0.25).move_to(UP * 0.3)
        for k, tile in enumerate(tiles, 1):
            self.at(k)
            self.play(FadeIn(tile, shift=UP * 0.15), run_time=0.6)
        self.at(7)
        app = plate(VGroup(badge("Как устроено", "active", 0.6), tx("в конце: те же вопросы формулами и как это устроено", 24, COLOR["Как устроено"])).arrange(RIGHT, buff=0.3)).next_to(tiles, DOWN, buff=0.25)
        self.play(FadeIn(app), run_time=0.6)
        self.wait(1.0)
        self.play(FadeOut(VGroup(tiles, app, head)), run_time=0.8)
        self.finish()


# ---------- сцены из раскадровки: те же кадры-инфографика, по фразам, поверх станции ----------

import storyboard as SB


class BoardOverlay(Overlay):
    """Кадры раскадровки (storyboard.py) как слой фильма: всё, что construct добавляет до snap(), появляется к началу
    очередной фразы; clear_keep_bar() убирает прошлый кадр. Под инфографикой — тёмная подложка, станция видна по краям."""
    PANEL = 0.66

    def setup(self):
        super().setup()
        panel = RoundedRectangle(width=14.2, height=6.75, corner_radius=0.25).set_stroke(width=0).set_fill(BLACK, self.PANEL)
        Scene.add(self, panel.move_to(UP * 0.5))
        self._fixed = list(self.mobjects)
        self._k, self._new, self._gone, self._buffer = 0, [], [], True

    def add(self, *mobs):
        if getattr(self, "_buffer", False):
            self._new.extend(m for m in mobs if m not in self._new)
            return self
        return super().add(*mobs)

    def remove(self, *mobs):
        if getattr(self, "_buffer", False):
            for m in mobs:
                if m in self._new:
                    self._new.remove(m)
                elif m in self.mobjects and m not in self._fixed:
                    self._gone.append(m)
            return self
        return super().remove(*mobs)

    def clear_keep_bar(self):
        self._new.clear()
        self._gone = [m for m in self.mobjects if m not in self._fixed]

    def snap(self, allow=()):
        self.at(min(self._k, len(self.P) - 1), 0.15 if self._k else 0.0)
        self._k += 1
        anims = [FadeOut(m) for m in self._gone] + [FadeIn(m) for m in self._new]
        new, self._new, self._gone = self._new, [], []
        self._buffer = False
        if anims:
            self.play(*anims, run_time=0.5)
        self._buffer = True


def _board_scene(code):
    def construct(self):
        getattr(SB, code).construct(self)
        self._buffer = False
        self.finish()
    return type(code, (BoardOverlay,), {"construct": construct})


for _c in ["A07", "A08", "A09", "A10", "A11", "A12", "A13", "A14", "A15", "F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "A16"]:
    globals()[_c] = _board_scene(_c)
