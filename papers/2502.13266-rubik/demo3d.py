"""Демо стыка 3D и доски (не входит в ролик, паспорт его не проверяет).

Demo3D — объёмный кубик: облёт камерой, два хода (поворот грани), кубик сжимается в комнату-старт, под ним — рельефный
лабиринт (высота комнаты = расстояние до выхода), рельеф сплющивается в карту, камера встаёт сверху. Последний кадр совпадает
с плоской картой пиксель в пиксель — на него ложится рисунок «от руки».
DemoPath — только путь к выходу и подписи на тёмном фоне в тех же координатах: его рисует Animator (demo3d_build.py).
Запуск: uv run python papers/2502.13266-rubik/demo3d_build.py"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(HERE))
import numpy as np
from manimlib import *
from manimkit import tx, note, BG
import maze as M

from cube3d import C_POS, C_EXIT, C_NOTE, RISE, rubik, turn, p3, relief, flat_room  # общие 3D-детали ролика

# озвучка по кускам демо (ударения — знаками); длина куска подстраивается под речь (DEMO_SEG от demo3d_build.py)
NARRATION = [
    "Вот ку́бик Ру́бика. Ход — э́то поворо́т одно́й гра́ни на че́тверть оборо́та. "
    "Поверну́ли ве́рхнюю грань, пото́м пра́вую — и ку́бик уже́ переме́шан.",
    "Ка́ждая така́я пози́ция — ко́мната в огро́мном лабири́нте, а ка́ждый ход — дверь в сосе́днюю ко́мнату. "
    "Вы́ход — со́бранный ку́бик. Чем да́льше ко́мната от вы́хода, тем вы́ше она́ стои́т.",
    "Е́сли посмотре́ть све́рху, релье́ф превраща́ется в ка́рту.",
    "А зада́ча сбо́рщика — найти́ на э́той ка́рте са́мый коро́ткий путь от ста́рта к вы́ходу. Здесь э́то шесть ходо́в.",
]
SEG_BASE = [9.5, 8.5, 5.0]  # длина 3D-кусков при темпе 1 (сумма run_time в куске)



class Demo3D(ThreeDScene):
    def setup(self):
        super().setup()
        self.camera.background_rgba = [0.059, 0.067, 0.082, 1]
        want = [float(x) for x in os.environ.get("DEMO_SEG", "").split(",") if x]
        self.k = [w / b for w, b in zip(want, SEG_BASE)] if want else [1.0] * len(SEG_BASE)
        self.seg = 0

    def play(self, *args, run_time=1.0, **kwargs):
        super().play(*args, run_time=run_time * self.k[self.seg], **kwargs)

    def wait(self, duration=1.0, *args, **kwargs):
        super().wait(duration * self.k[self.seg], *args, **kwargs)

    def construct(self):
        frame = self.frame
        frame.reorient(-35, 68)
        cube = rubik()
        cap = tx("Кубик Рубика", 36).to_edge(UP, buff=0.4).fix_in_frame()
        self.play(FadeIn(cube, scale=0.8), FadeIn(cap), run_time=1.5)
        self.play(frame.animate.reorient(30, 62), run_time=3)
        hod = note("ход — поворот одной грани", C_POS).fix_in_frame()
        self.play(FadeIn(hod))
        self.play(turn(cube, 2, 1, PI / 2), run_time=1.4)
        self.play(turn(cube, 0, 1, -PI / 2), frame.animate.reorient(55, 70), run_time=1.6)
        self.play(FadeOut(hod), FadeOut(cap))

        self.seg = 1
        # кубик сжимается в комнату-старт, под ним вырастает рельеф лабиринта
        doors, rooms = relief()
        start = p3(M.START)
        self.play(frame.animate.reorient(-35, 62).move_to(np.array([-1.2, 0.2, 1.4])).set_height(9.5), cube.animate.scale(0.09).move_to(start),
                  FadeIn(rooms, lag_ratio=0.03), ShowCreation(doors, lag_ratio=0.02), run_time=3.5)
        self.play(FadeOut(cube), run_time=0.5)
        lab = VGroup(tx("выход — внизу", 26, C_EXIT), tx("чем дальше от выхода, тем выше комната", 22, C_NOTE)).arrange(DOWN, buff=0.12)
        lab.to_edge(UP, buff=0.4).fix_in_frame()
        self.play(FadeIn(lab), frame.animate.reorient(20, 66).move_to(np.array([-1.2, 0.2, 1.4])), run_time=3.5)
        self.play(FadeOut(lab))

        self.seg = 2
        # рельеф сплющивается в карту, камера встаёт сверху — кадр совпадает с плоской картой
        self.play(rooms.animate.stretch(0.001, 2, about_point=ORIGIN), doors.animate.stretch(0.001, 2, about_point=ORIGIN),
                  frame.animate.reorient(0, 0).move_to(ORIGIN).set_height(FRAME_HEIGHT), run_time=3)
        flat = VGroup(*[flat_room(k) for k in range(len(M.POS))])
        self.play(FadeOut(rooms), FadeIn(flat), run_time=1.5)
        self.wait(0.5)


class DemoPath(Scene):
    """Только то, что дорисует рука: путь к выходу и подписи, в координатах карты."""
    def setup(self):
        self.camera.background_rgba = [0.059, 0.067, 0.082, 1]

    def construct(self):
        _, path = M.beam(M.START, M.DIST, width=1)
        line = VMobject().set_points_as_corners([p3(k, rise=False) for k in path]).set_stroke(C_EXIT, 7)
        parts = {  # имя части → объект; слово озвучки, под которое часть рисуется, — в DRAW_CUES (demo3d_build.py)
            "path": line,
            "start": tx("старт", 22).next_to(p3(M.START, False), DOWN, buff=0.25),
            "exit": tx("выход", 22, C_EXIT).next_to(p3(M.EXIT, False), LEFT, buff=0.25),
            "count": VGroup(tx(f"{len(path) - 1} ходов", 26, C_EXIT), tx("самый короткий путь", 22, C_EXIT)).arrange(DOWN, buff=0.1)
            .move_to(RIGHT * 5.4 + UP * 0.6),
        }
        self.add(*parts.values())
        if os.environ.get("DEMO_BOXES"):  # рамки частей в долях 0–1000 кадра — для разметки Animator
            fw, fh = FRAME_WIDTH, FRAME_HEIGHT
            boxes = {}
            for name, m in parts.items():
                (x0, y1, _), (x1, y0, _) = m.get_corner(UL) + np.array([-0.1, 0.1, 0]), m.get_corner(DR) + np.array([0.1, -0.1, 0])
                boxes[name] = {"xmin": round((x0 + fw / 2) / fw * 1000), "xmax": round((x1 + fw / 2) / fw * 1000),
                               "ymin": round((fh / 2 - y1) / fh * 1000), "ymax": round((fh / 2 - y0) / fh * 1000)}
            Path(os.environ["DEMO_BOXES"]).write_text(json.dumps(boxes))
