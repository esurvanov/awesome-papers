"""Образцы новой версии (3D, ярко): сцены 3, 10, 11 — до массового рендера (закон 20).
uv run manimgl papers/integrals-film/proto3d.py P03 -w --hd   ·   неподвижные кадры: ... -s"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(HERE))
import numpy as np
from manimlib import *
from manimkit import tx

# яркая палитра: роли те же, цвета насыщеннее
BLUE, YEL, ORG, GRN, PUR, RED, PNK = "#3aa6ff", "#ffd23f", "#ff8c1a", "#2ee66b", "#c88bff", "#ff4d5e", "#ff5fb0"
BG = "#000000"
D = 2.2                      # глубина холма (ось y)
HL, HH = 5.0, 3.0            # полуширина и высота холма
F = lambda x: HH * (1 - (x / HL) ** 2)


def hill_ridge(opacity=0.35):
    """Холм как объём: профиль-парабола, вытянутый в глубину; передняя кромка светится."""
    surf = ParametricSurface(lambda u, v: np.array([u, v, F(u)]), u_range=(-HL, HL), v_range=(0, D), resolution=(90, 4))
    surf.set_color(BLUE).set_opacity(opacity).set_shading(0.4, 0.3, 0.2)
    edge = ParametricCurve(lambda t: np.array([t, 0.0, F(t)]), t_range=(-HL, HL, 0.05)).set_stroke(BLUE, 9)
    back = ParametricCurve(lambda t: np.array([t, D, F(t)]), t_range=(-HL, HL, 0.05)).set_stroke(BLUE, 3).set_opacity(0.6)
    return surf, edge, back


def floor_axis():
    ax = Line([-6.2, 0, 0], [6.2, 0, 0]).set_stroke(ORG, 10)
    grid = VGroup(*[Line([x, 0, 0], [x, D, 0]).set_stroke("#334", 1) for x in np.linspace(-HL, HL, 11)],
                  *[Line([-HL, y, 0], [HL, y, 0]).set_stroke("#334", 1) for y in np.linspace(0, D, 4)])
    return ax, grid


def tower(x0, x1, h, color=YEL, op=0.95):
    p = Prism(width=x1 - x0 - 0.04, height=D, depth=h)
    p.set_color(color).set_opacity(op).set_shading(0.5, 0.35, 0.3)
    p.move_to([(x0 + x1) / 2, D / 2, h / 2])
    return p


class P03(ThreeDScene):
    """Сцена 3: на куски делится ось, на каждом куске вырастает башня; камера облетает."""
    def construct(self):
        self.camera.background_rgba = [0, 0, 0, 1]
        self.camera.light_source.move_to([-6, -8, 12])
        self.frame.reorient(-12, 66).set_height(10.5).move_to([0, 1.0, 1.4])
        surf, edge, back = hill_ridge()
        ax, grid = floor_axis()
        self.add(grid, surf, edge, back, ax)
        cap = tx("на каждом куске — столбик", 34, WHITE).to_edge(DOWN, buff=0.5).fix_in_frame()
        self.play(FadeIn(cap))
        n = 8
        xs = np.linspace(-HL, HL, n + 1)
        cuts = VGroup(*[Line([x, 0, 0], [x, 0, F(x)]).set_stroke(WHITE, 2) for x in xs])
        self.play(ShowCreation(cuts), run_time=1.2)
        towers = Group(*[tower(xs[i], xs[i + 1], F((xs[i] + xs[i + 1]) / 2)) for i in range(n)])
        self.play(LaggedStart(*[GrowFromEdge(t, IN) for t in towers], lag_ratio=0.12), run_time=3.0)
        self.play(self.frame.animate.reorient(-38, 60).move_to([0, 0.8, 1.6]), run_time=4.5, rate_func=smooth)
        self.play(self.frame.animate.reorient(-8, 72), run_time=4.0, rate_func=smooth)
        self.wait(0.5)


class P10(ThreeDScene):
    """Сцена 10: холм режется на этажи; этажи раздвигаются, под каждым подсвечивается часть оси."""
    def construct(self):
        self.camera.background_rgba = [0, 0, 0, 1]
        self.camera.light_source.move_to([-6, -8, 12])
        self.frame.reorient(-14, 68).set_height(10.5).move_to([0, 1.0, 1.4])
        surf, edge, back = hill_ridge(0.5)
        ax, grid = floor_axis()
        self.add(grid, surf, edge, back, ax)
        cap = tx("слои — как этажи", 34, WHITE).to_edge(DOWN, buff=0.5).fix_in_frame()
        self.play(FadeIn(cap))
        N = 6
        hs = np.linspace(0, HH, N + 1)
        xk = lambda h: HL * np.sqrt(max(0.0, 1 - h / HH))
        cols = [YEL, "#ffb347", ORG, "#ff7043", PNK, PUR]
        floors = []
        for k in range(N):
            w = 2 * xk(hs[k])
            p = Prism(width=w, height=D, depth=hs[k + 1] - hs[k] - 0.03)
            p.set_color(cols[k]).set_opacity(0.95).set_shading(0.5, 0.35, 0.3)
            p.move_to([0, D / 2, (hs[k] + hs[k + 1]) / 2])
            floors.append(p)
        self.play(FadeOut(surf), LaggedStart(*[FadeIn(f) for f in floors], lag_ratio=0.15), run_time=2.0)
        self.play(self.frame.animate.reorient(-30, 58), run_time=2.5)
        # этажи раздвигаются вверх, на оси остаются их «следы»
        k = 2
        shadows = VGroup(*[Line([-xk(hs[j]), -0.15, 0], [xk(hs[j]), -0.15, 0]).set_stroke(cols[j], 10) for j in range(N)])
        lift = [f.animate.shift(OUT * 0.5 * j) for j, f in enumerate(floors)]
        self.play(*lift, run_time=2.5)
        self.play(ShowCreation(shadows[k]), run_time=1.0)
        self.play(*[ShowCreation(shadows[j]) for j in range(N) if j != k], run_time=2.0)
        self.play(self.frame.animate.reorient(-10, 70), run_time=3.5)
        self.wait(0.5)


class P11(ThreeDScene):
    """Сцена 11: два этажа — единиц и нулей; точки оседают на свои этажи, этаж единицы почти пустой."""
    def construct(self):
        self.camera.background_rgba = [0, 0, 0, 1]
        self.camera.light_source.move_to([-6, -8, 12])
        self.frame.reorient(-14, 66).set_height(8.2).move_to([0, 1.0, 1.7])
        ax, grid = floor_axis()
        self.add(grid, ax)
        rng = np.random.default_rng(7)
        xs = np.linspace(-4.8, 4.8, 54) + rng.uniform(-0.08, 0.08, 54)
        up = rng.random(54) < 0.5
        dots = Group(*[Sphere(radius=0.15).set_color(BLUE if u else "#f2f6ff").move_to([x, 0.6, 0.15]) for x, u in zip(xs, up)])
        dots.set_shading(0.15, 0.2, 0.0)
        cap = tx("слоёв всего два", 34, WHITE).to_edge(DOWN, buff=0.5).fix_in_frame()
        self.play(FadeIn(cap), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.02), run_time=2.0)
        slab1 = Prism(width=11, height=D, depth=0.5).set_color(YEL).set_opacity(0.55).set_shading(0.3, 0.2, 0.1).move_to([0, D / 2, 3.0])
        slab0 = Prism(width=11, height=D, depth=0.5).set_color("#8fa3c4").set_opacity(0.55).set_shading(0.3, 0.2, 0.1).move_to([0, D / 2, 1.0])
        lab1 = tx("слой единицы", 30, YEL).move_to([-4.6, 0, 3.9]).fix_in_frame()
        self.play(FadeIn(slab1), FadeIn(slab0), self.frame.animate.reorient(-24, 60), run_time=2.0)
        moves = [d.animate.move_to([d.get_center()[0], 1.1, 3.0 if u else 1.0]) for d, u in zip(dots, up)]
        self.play(LaggedStart(*moves, lag_ratio=0.02), run_time=3.5)
        self.play(self.frame.animate.reorient(-6, 72), run_time=3.0)
        self.wait(0.5)
