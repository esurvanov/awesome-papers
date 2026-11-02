"""Основа сцен любого ролика (PLAYBOOK, законы 24, 29–31, 35). Подключение в scenes.py статьи:
    Film, Film3D = film_base(P.STATIONS, P.SCENES, ICONS, N.TEXT, HERE)
Что даёт:
  • self.show(*объекты, c="подпись") — кадр фразы: ждёт её начала (точный синхрон — SYNC = "abs" в narration.py), подпись старого кадра
    гаснет, объекты с одной меткой .tag превращаются (только однотипные), остальное гаснет и появляется, новая подпись — после;
  • self.do(fn) — своя анимация внутри кадра (движение — на словах о движении); self.keep(*ms) — оставить её объекты в кадре;
  • каждая сцена начинается с последнего кадра предыдущей (мгновенно) — склеек нет;
  • после каждого кадра — проверка наложений; замечания и журнал синхрона пишутся в videos/<папка>/frame_check/<сцена>.json
    (их читает сборка: опоздание кадра > 0,5 с или наложение — ошибка);
  • overlay(code, k) — сквозная строка ролика (например, «правила счёта»): переопределить в своём классе, вернуть объект или None;
  • Film3D — объёмная сцена: вид спереди совпадает с плоским кадром (AXIS_Y — где ось в плоском кадре), вход и выход без провала яркости;
    end2d() — плоский последний кадр (с него начнётся следующая сцена), phrase(k, c) — начало кадра фразы, enter/leave/cam/flat."""
import json
import sys
from pathlib import Path

import numpy as np
from manimlib import (FadeIn, FadeOut, ShowCreation, LaggedStart, GrowFromEdge, ReplacementTransform, VGroup, VMobject, ThreeDScene, DOWN, smooth)
from .story import story_base, story_base3d, layout_problems
from .annot import cap

__all__ = ["film_base"]


def _is_line(m):
    leaves = [x for x in m.get_family() if x.has_points()]
    return bool(leaves) and all(isinstance(x, VMobject) and x.get_fill_opacity() < 0.01 for x in leaves)


def _same(a, b):
    try:
        if len(a.get_family()) != len(b.get_family()):
            return False
        if not (np.allclose(a.get_center(), b.get_center(), atol=0.01) and abs(a.get_width() - b.get_width()) < 0.01
                and abs(a.get_height() - b.get_height()) < 0.01):
            return False
        la = [x for x in a.get_family() if x.has_points()]
        lb = [x for x in b.get_family() if x.has_points()]
        return not la or all(x.get_stroke_color() == y.get_stroke_color() and abs(x.get_fill_opacity() - y.get_fill_opacity()) < 0.02
                             for x, y in zip(la, lb))
    except Exception:
        return False


def _compatible(a, b):
    return len(a.get_family()) == len(b.get_family()) and _is_line(a) == _is_line(b)


class _Empty:
    _k, _cur, _capm, _dry = 0, [], None, True


def film_base(stations, scenes, icons=None, text=None, paper_dir=None):
    order = [c for c, *_ in scenes]
    Base2D = story_base(stations, scenes, icons, text, paper_dir)
    Base3D = story_base3d(stations, scenes, icons, text, paper_dir)
    holder = {}

    def find(code):
        for mod in list(sys.modules.values()):
            c = getattr(mod, code, None)
            if isinstance(c, type) and issubclass(c, (holder["Film"], holder["Film3D"])):
                return c
        return None

    def dry(code):
        """Последний кадр сцены без отрисовки — начало следующей (если сцены нет — пустое начало)."""
        cls = find(code)
        if cls is None:
            return _Empty()
        o = object.__new__(cls)
        if hasattr(cls, "end2d"):
            o._k, o._cur, o._dry = cls.END_K, list(o.end2d()), True
            o._capm = cap(cls.END_CAP) if getattr(cls, "END_CAP", None) else None
            return o
        o._init()
        o._dry = True
        o.construct()
        return o

    def write_log(scene, probs):
        out = Path(scene.PAPER_ROOT) / "videos" / Path(scene.PAPER_DIR).name / "frame_check"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{type(scene).__name__}.json").write_text(json.dumps({"problems": probs, "sync": getattr(scene, "_sync_log", [])},
                                                                     ensure_ascii=False, indent=1))

    class Film(Base2D):
        def overlay(self, code, k):
            return None

        def _init(self):
            self._k, self._cur, self._capm, self._ov, self._ovkey, self._dry, self._probs = 0, [], None, None, None, False, []

        def setup(self):
            super().setup()
            self._bar = self.mobjects[-1] if self.mobjects else None      # полоса «мы здесь» — её не проверяем
            self.camera.background_rgba = [0, 0, 0, 1]
            self._init()
            i = order.index(type(self).__name__)
            if i > 0:
                p = dry(order[i - 1])
                self._cur = list(p._cur)
                self.add(*self._cur)
                if p._capm is not None:
                    self._capm = p._capm
                    self.add(self._capm)
                ov = self.overlay(order[i - 1], p._k)
                if ov is not None:
                    self._ov = ov
                    self.add(ov)

        def _enter(self, m, how):
            t = getattr(m, "tag", None)
            mode = how.get(t) if t else None
            if mode == "grow" or t == "bars":
                return LaggedStart(*[GrowFromEdge(b, DOWN) for b in m], lag_ratio=0.1)
            if mode == "create" or (mode is None and _is_line(m)):
                return ShowCreation(m)
            if mode == "fade" or len(m.submobjects) < 8:
                return FadeIn(m)
            return LaggedStart(*[FadeIn(x) for x in m], lag_ratio=0.04)

        def show(self, *mobs, c=None, how=None, morph=None, rt=1.0):
            self._k += 1
            items = list(mobs)
            capm = cap(c) if c else None
            if self._dry:
                self._cur, self._capm = items, capm
                return
            code = type(self).__name__
            self.beat(self._k - 1)
            how, morph = how or {}, morph or {}
            if self._capm is not None:
                self.play(FadeOut(self._capm), run_time=0.2)
                self._capm = None
            anims, old, used = [], list(self._cur), set()
            for m in items:
                t = getattr(m, "tag", None)
                jm = None
                if t is not None:
                    for j, o in enumerate(old):
                        ot = getattr(o, "tag", None)
                        if j not in used and ot is not None and (ot == t or morph.get(ot) == t):
                            jm = j
                            break
                if jm is not None:
                    used.add(jm)
                    o = old[jm]
                    if _same(o, m):
                        self.remove(o)
                        self.add(m)
                    elif _compatible(o, m) or morph.get(getattr(o, "tag", None)) == t:
                        anims.append(ReplacementTransform(o, m))
                    else:
                        anims += [FadeOut(o), self._enter(m, how)]
                else:
                    anims.append(self._enter(m, how))
            for j, o in enumerate(old):
                if j not in used:
                    anims.append(FadeOut(o))
            ov = self.overlay(code, self._k)
            if ov is not None:
                anims.append(ReplacementTransform(self._ov, ov) if self._ov is not None else FadeIn(ov))
                self._ov = ov
            elif self._ov is not None:
                anims.append(FadeOut(self._ov))
                self._ov = None
            if anims:
                self.play(*anims, run_time=rt)
            if capm is not None:
                self.play(FadeIn(capm), run_time=0.25)
            self._cur, self._capm = items, capm
            try:
                probs = layout_problems(self, exclude=[self._bar])
            except Exception:
                probs = []
            for pr in probs:
                msg = f"{code}-{self._k}: {pr}"
                self._probs.append(msg)
                print(f"  ⚠ кадр {msg}", flush=True)

        def do(self, fn):
            if not self._dry:
                fn()

        def keep(self, *ms):
            if not self._dry:
                self._cur = list(self._cur) + list(ms)

        def tear_down(self):
            super().tear_down()
            write_log(self, self._probs)

    class Film3D(Base3D):
        AXIS_Y = -1.6
        END_CAP = None

        def overlay(self, code, k):
            return None

        @property
        def front(self):
            return np.array([0.0, 0.0, -self.AXIS_Y])

        def setup(self):
            super().setup()
            self.camera.background_rgba = [0, 0, 0, 1]
            self.camera.light_source.move_to([-6, -8, 12])
            self._k, self._capm, self._ov = 0, None, None
            self.frame.reorient(0, 90).move_to(self.front).set_height(8)
            i = order.index(type(self).__name__)
            p = dry(order[i - 1])
            self._old = [self._pin(m) for m in p._cur]
            if p._capm is not None:
                self._capm = self._pin(p._capm)
            ov = self.overlay(order[i - 1], p._k)
            if ov is not None:
                self._ov = self._pin(ov)

        def _pin(self, m):
            m.fix_in_frame()
            m.set_z_index(100)
            self.add(m, set_depth_test=False)
            return m

        def flat(self, *ms):
            return [self._pin(m) for m in ms]

        def phrase(self, k, c=None):
            self._k = k
            self.beat(k - 1)
            if self._capm is not None:
                self.play(FadeOut(self._capm), run_time=0.2)
                self._capm = None
            ov = self.overlay(type(self).__name__, k)
            if ov is not None:
                new = self._pin(ov)
                self.play(ReplacementTransform(self._ov, new) if self._ov is not None else FadeIn(new), run_time=0.4)
                self._ov = new
            if c:
                self._capm = self._pin(cap(c))
                self.play(FadeIn(self._capm), run_time=0.25)

        def enter(self, objs3d, rt=0.8):
            self.add(*objs3d)
            self.play(*[FadeOut(m) for m in self._old], run_time=rt)
            self._old = []

        def leave(self, objs3d, rt=0.8):
            fin = [self._pin(m) for m in self.end2d()]
            self.play(self.frame.animate.reorient(0, 90).move_to(self.front).set_height(8), run_time=1.6)
            self.add(*fin, set_depth_test=False)
            self.play(*[FadeOut(o) for o in objs3d], run_time=rt)

        def cam(self, theta, phi, rt=3.0, center=(0, 0.9, 1.4), height=10.0):
            self.play(self.frame.animate.reorient(theta, phi).move_to(list(center)).set_height(height), run_time=rt, rate_func=smooth)

        def tear_down(self):
            super().tear_down()
            write_log(self, [])

    holder["Film"], holder["Film3D"] = Film, Film3D
    return Film, Film3D
