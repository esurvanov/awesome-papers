"""Инфографика по статье Agent4Sci (arXiv 2610.28763): шесть объёмных кадров, без озвучки.

I1 проблема · I2 стенд · I3 защита от обмана · I4 прирост · I5 электросети · I6 вывод и что дальше.
Подписи у 3D-объектов развёрнуты к камере (bill) и рисуются поверх объёмов; заголовок, пояснение и вывод закреплены в кадре.
Значки (эмодзи) Pango не рисует — их нет в кадрах, они на странице вокруг картинок.
Запуск (последний кадр каждой сцены в PNG):
    for s in I1 I2 I3 I4 I5 I6; do uv run manimgl papers/2610.28763-agent4sci/infographic3d.py $s -s -w --hd --video_dir videos/2610.28763-agent4sci; done"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
import numpy as np
from manimlib import *
from manimkit import tx, C_BLUE, C_GREEN, C_RED, C_YEL, C_GREY

C_PURP, C_ORNG = "#d2a8ff", "#f0883e"
STEPS = ["проблема", "стенд", "честность", "прирост", "пример", "вывод"]


def bill(m, frame, at):
    """Плоскую подпись развернуть лицом к камере и поставить в точку at."""
    m.apply_matrix(frame.get_inverse_camera_rotation_matrix().T)
    return m.move_to(at)


def box(w, d, h, color, at, op=0.9):
    """Брусок: основание w×d, высота h, стоит на плоскости z = at[2]."""
    b = Prism(w, d, h).set_color(color).set_opacity(op).set_shading(0.4, 0.4, 0.3)
    return b.move_to(np.array(at) + OUT * h / 2)


def ground(w=11, d=6, color=C_GREY):
    g = Square3D().set_color(color).set_opacity(0.12)
    return g.stretch(w / 2, 0).stretch(d / 2, 1)


class Info(ThreeDScene):
    STEP = 0
    TITLE = SUB = BOTTOM = ""
    THETA, PHI = -25, 62
    ZOOM, CENTER = 9.0, ORIGIN  # высота кадра камеры и точка, куда она смотрит

    def setup(self):
        super().setup()
        self.camera.background_rgba = [0.059, 0.067, 0.082, 1]
        self.frame.reorient(self.THETA, self.PHI).set_height(self.ZOOM).move_to(self.CENTER)

    def chrome(self):
        """Шапка (номер шага, заголовок, пояснение), вывод кадра и полоса шагов внизу."""
        top = VGroup(tx(f"{self.STEP + 1}/6", 26, C_GREY), tx(self.TITLE, 40)).arrange(RIGHT, buff=0.35)
        top.to_edge(UP, buff=0.3)
        parts = [top]
        if self.SUB:
            parts.append(tx(self.SUB, 24, C_GREY).next_to(top, DOWN, buff=0.15))
        bar = VGroup(*[tx(s, 20, WHITE if i == self.STEP else C_GREY).set_opacity(1 if i == self.STEP else 0.45)
                       for i, s in enumerate(STEPS)]).arrange(RIGHT, buff=0.55).to_edge(DOWN, buff=0.22)
        line = Line(LEFT * 7, RIGHT * 7).set_stroke(C_GREY, 1, opacity=0.3).next_to(bar, UP, buff=0.14)
        bot = tx(self.BOTTOM, 30, C_YEL).next_to(line, UP, buff=0.2)
        for m in parts + [bar, line, bot]:
            self.add(m.fix_in_frame(), set_depth_test=False)

    def lab(self, s, at, size=26, color=WHITE):
        m = bill(tx(s, size, color), self.frame, at)
        self.labels.append(m)
        return m

    def construct(self):
        self.labels = []
        self.draw()
        self.add(*self.labels, set_depth_test=False)  # подписи — поверх объёмов
        self.chrome()


# ---------- 1. проблема: гора, флаг людей наверху, агент у подножия ----------

class I1(Info):
    STEP, TITLE = 0, "Может ли ИИ-агент сам двигать науку?"
    BOTTOM = "«ИИ-учёный» — громкое имя, но честно его никто не проверял"
    THETA, PHI, ZOOM, CENTER = -20, 64, 9.4, np.array([0, 0, 0.9])

    def draw(self):
        hill = ParametricSurface(lambda u, v: np.array([u, v, 1.9 * np.exp(-((u + 0.4) ** 2 + v ** 2) / 2.6)]),
                                 u_range=(-4.6, 3.0), v_range=(-2.2, 2.2), resolution=(60, 30))
        hill.set_color(C_BLUE).set_opacity(0.6).set_shading(0.5, 0.4, 0.3)
        self.add(hill)
        top = np.array([-0.4, 0, 1.9])
        pole = Line3D(top, top + OUT * 0.9, width=0.04, color=WHITE)
        flag = Polygon(top + OUT * 0.9, top + OUT * 0.58, top + OUT * 0.74 + RIGHT * 0.5).set_fill(C_GREEN, 1).set_stroke(width=0)
        self.add(pole, flag)
        self.lab("лучшая модель людей", top + OUT * 1.25 + LEFT * 0.2, 26, C_GREEN)
        bot = np.array([-4.0, -1.0, 0.0])
        self.add(Sphere(radius=0.3).set_color(C_YEL).move_to(bot + OUT * 0.3))
        self.lab("ИИ-агент", bot + OUT * 0.95, 26, C_YEL)
        self.lab("сможет выше?", np.array([-2.6, -0.4, 2.2]), 30, C_YEL)
        # проба: 12 задач, в 5 агенты жульничали — отдельная площадка справа
        for i in range(12):
            bad = i < 5
            self.add(box(0.36, 0.36, 0.7 if bad else 0.36, C_RED if bad else C_GREY,
                         [3.9 + (i % 6) * 0.5, -1.9 + (i // 6) * 0.55, 0], 0.95 if bad else 0.55))
        self.lab("проба: в 5 задачах из 12", np.array([5.2, -1.6, 1.55]), 24, C_RED)
        self.lab("агенты жульничали", np.array([5.2, -1.6, 1.15]), 24, C_RED)


# ---------- 2. стенд: задача → агент → измеритель → проверяющий ----------

class I2(Info):
    STEP, TITLE = 1, "Стенд: 20 настоящих научных задач"
    SUB = "11 наук · 12 часов на задачу · 8 видеокарт · 0 участия людей · 4 агента"
    BOTTOM = "агент работает один · измеряет и проверяет его другой ИИ"
    THETA, PHI, ZOOM, CENTER = -12, 60, 8.0, np.array([0, -0.6, 0.9])

    def draw(self):
        self.add(ground(12.5, 3.4))
        xs = [-4.5, -1.5, 1.5, 4.5]
        cols = [C_GREY, C_YEL, C_GREEN, C_PURP]
        hs = [0.9, 1.5, 1.2, 1.2]
        names = ["статья + код + данные", "агент улучшает", "второй ИИ измеряет", "третий ищет обман"]
        for x, c, h, n in zip(xs, cols, hs, names):
            self.add(box(1.5, 1.5, h, c, [x, 0, 0], 0.85))
            self.lab(n, np.array([x, 0, h + 0.5]), 24, c)
        for a, b in zip(xs, xs[1:]):
            self.add(Arrow(np.array([a + 0.8, 0, 0.5]), np.array([b - 0.8, 0, 0.5]), buff=0).set_color(WHITE))


# ---------- 3. честность: стена, скрытый тест в сейфе, три проверяющих + люди ----------

class I3(Info):
    STEP, TITLE = 2, "Почему цифрам можно верить"
    BOTTOM = "агент не видит тест и не может подыграть себе · 0 нарушений"
    THETA, PHI, ZOOM, CENTER = -20, 60, 8.6, np.array([0, -0.3, 0.7])

    def draw(self):
        self.add(ground(12, 5.4))
        self.add(Prism(0.15, 3.4, 2.2).set_color(C_RED).set_opacity(0.4).move_to(np.array([-1.3, 0.6, 1.1])))
        self.lab("стена", np.array([-1.3, 0.6, 3.0]), 26, C_RED)
        self.add(Sphere(radius=0.4).set_color(C_YEL).move_to(np.array([-4.0, 0.6, 0.4])))
        self.lab("ИИ-агент", np.array([-4.0, 0.6, 1.25]), 26, C_YEL)
        self.lab("старт — лучшая модель людей,", np.array([-4.2, -1.5, 0.35]), 22, C_GREY)
        self.lab("заново перепроверенная", np.array([-4.2, -1.5, 0.0]), 22, C_GREY)
        self.add(box(1.4, 1.4, 1.4, C_GREEN, [1.3, 1.2, 0], 0.85))
        self.lab("скрытый тест", np.array([1.3, 1.2, 2.0]), 26, C_GREEN)
        for i, (c, n) in enumerate([(C_ORNG, "Claude"), (C_BLUE, "Codex"), (C_PURP, "Gemini"), (WHITE, "люди")]):
            p = np.array([2.2 + i * 1.15, -1.3, 0])
            self.add(Sphere(radius=0.26).set_color(c).move_to(p + OUT * 0.26))
            self.lab(n, p + OUT * 0.85, 22, c)
        self.lab("обман ищут ИИ трёх компаний и люди", np.array([3.9, -2.4, 0.0]), 22, WHITE)


# ---------- 4. прирост: столбцы по агентам, надстройка от подсказок ----------

class I4(Info):
    STEP, TITLE = 3, "20 из 20 задач улучшено"
    SUB = "средний прирост качества сверх лучшей модели людей"
    BOTTOM = "сам: до +10% · с тремя подсказками: +20% · 56% приёмов — подбор настроек"
    THETA, PHI, ZOOM, CENTER = -18, 70, 9.0, np.array([0.2, 0, 1.2])

    def draw(self):
        self.add(ground(11, 3.2))
        k = 0.11  # высота столбца на процент
        data = [("Claude Opus", 10.4, 20.1, C_ORNG), ("Claude Sonnet", 9.6, None, C_ORNG),
                ("Gemini", 6.8, None, C_PURP), ("Codex", 4.4, 8.1, C_BLUE)]
        for i, (n, v, hint, c) in enumerate(data):
            x = -3.9 + i * 2.6
            self.add(box(1.2, 1.2, v * k, c, [x, 0, 0], 0.9))
            self.lab(f"+{v:.1f}%".replace(".", ","), np.array([x, -0.65, v * k / 2]), 26, WHITE)
            if hint:
                self.add(box(1.2, 1.2, (hint - v) * k, C_YEL, [x, 0, v * k], 0.35))
                self.lab(f"с подсказками +{hint:.1f}%".replace(".", ","), np.array([x, 0, hint * k + 0.35]), 22, C_YEL)
            self.lab(n, np.array([x, -1.4, -0.3]), 24, c)


# ---------- 5. электросети: лестница вклада ----------

class I5(Info):
    STEP, TITLE = 4, "Пример: прогноз электросетей"
    SUB = "качество прогноза после каждого шага агента"
    BOTTOM = "прорыв дала идея из физики — агент нашёл её в 2 из 4 запусков"
    THETA, PHI, ZOOM, CENTER = -18, 70, 9.0, np.array([0.2, 0, 1.3])

    def draw(self):
        self.add(ground(11.5, 3.2))
        k = 0.026
        steps = [("перебор настроек", 4.6, C_GREY), ("инженерия", 64.4, C_BLUE),
                 ("законы Кирхгофа", 91, C_GREEN), ("3 дня работы", 99.5, C_YEL)]
        for i, (n, v, c) in enumerate(steps):
            x = -4.0 + i * 2.65
            self.add(box(1.6, 1.4, max(v * k, 0.08), c, [x, 0, 0], 0.9))
            self.lab(f"{v:g}%".replace(".", ","), np.array([x, 0, v * k + 0.55]), 32, WHITE if c == C_GREY else c)
            self.lab(n, np.array([x, -1.4, -0.3]), 24, c)


# ---------- 6. вывод: три уступа и что дальше ----------

class I6(Info):
    STEP, TITLE = 5, "Сегодня агент — сильный инженер, ещё не учёный"
    BOTTOM = "дальше: сравнить с людьми · команды агентов · исследование с нуля"
    THETA, PHI, ZOOM, CENTER = -24, 64, 8.0, np.array([0.8, 0, 0.6])

    def draw(self):
        tiers = [("инженер: уже умеет", C_GREEN, 0.9), ("с подсказками: выше", C_YEL, 0.8),
                 ("учёный: пока редко", C_PURP, 0.3)]
        for i, (n, c, op) in enumerate(tiers):
            w = 4.6 - i * 1.4
            self.add(box(w, w * 0.6, 0.8, c, [0, 0, i * 0.8], op))
            self.lab(n, np.array([w / 2 + 1.9, 0, i * 0.8 + 0.4]), 26, c)
        self.add(Sphere(radius=0.28).set_color(C_YEL).move_to(np.array([-1.8, -0.9, 1.08])))
        self.lab("агент сейчас", np.array([-3.5, -0.9, 1.1]), 24, C_YEL)
        self.lab("?", np.array([0, 0, 2.95]), 44, C_PURP)
