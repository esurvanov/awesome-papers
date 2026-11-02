"""Общее для роликов по паспорту: полоса «мы здесь», подпись над ней, базовые сцены (2D и 3D) со станцией и привязкой к фразам диктора.

Привязка к фразам: сцена знает свой текст (narration.TEXT) и готовую озвучку (videos/<папка>/audio/<сцена>.<движок>.wav,
сборщик пишет её до рендера). beat(k) ждёт начала фразы k — по паузам настоящей записи (core/pipeline/timing.py);
pad(пункты) добирает движения до конца речи. Тогда фраза и её кадр совпадают по построению, а растяжка сборщиком — около STRETCH."""

__all__ = ["story_bar", "note", "story_base", "story_base3d", "storyboard_base", "layout_problems", "STRETCH"]  # не отдавать наружу имена manimlib — они перекрывают значки из style (cross)
import os
import sys
from pathlib import Path

import numpy as np
from manimlib import *
from .style import tx, Base, C_GREY

STRETCH = 2.4      # во сколько раз сборщик растянет анимацию под речь; выше ×3 «картинка стоит»
LEAD, TAIL = 0.4, 0.8  # тишина до и после речи — как в core/pipeline/build.py
BAR_Y = -3.45      # полоса «мы здесь»: подписи целиком в кадре (кадр — от −4 до 4)


def story_bar(stations, active, color_note=C_GREY, icons=None):
    """Полоса «мы здесь»: пройденные станции — серые, текущая — белая, будущие — тусклые.
    icons — {станция: функция(масштаб) → значок}: значок стоит над точкой станции во всех сценах (тот же, что в обзоре)."""
    xs = np.linspace(-6.0, 6.0, len(stations))
    y = BAR_Y
    g = VGroup(Line([xs[0], y, 0], [xs[-1], y, 0]).set_stroke(color_note, 1, opacity=0.4))
    for i, (x, name) in enumerate(zip(xs, stations)):
        col, op = (WHITE, 1.0) if i == active else (color_note, 0.9 if i < active else 0.35)
        g.add(Dot([x, y, 0], radius=0.07 if i != active else 0.1).set_color(col).set_opacity(op))
        g.add(tx(name, 16, col).set_opacity(op).move_to([x, y - 0.24, 0]))
        if icons and name in icons:
            ic = icons[name](0.28).move_to([x, y + 0.28, 0])
            g.add(ic.set_opacity(1.0 if i == active else 0.45))
    return g


def note(s, color=C_GREY, y=-2.85):
    """Подпись внизу кадра — над полосой «мы здесь» и её значками."""
    return tx(s, 26, color).move_to(DOWN * (-y))


def _speech(scene):
    """Фразы сцены, их начала и длина речи — по готовой озвучке; без неё — оценка по числу слов (1,5 слова в секунду)."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
    from timing import sentences, phrase_starts
    code, text = type(scene).__name__, scene.TEXT[type(scene).__name__]
    wav = scene.PAPER_ROOT / "videos" / scene.PAPER_DIR.name / "audio" / f"{code}.{os.environ.get('VOICE_ENGINE', 'realtime')}.wav"
    sents = sentences(text)
    if wav.exists():
        return phrase_starts(wav, text)
    words = len(" ".join(sents).split())
    length = words / 1.5
    plain, pos, out = " ".join(sents), 0, []
    for s in sents:
        out.append(pos / len(plain) * length)
        pos += len(s) + 1
    return out, length


SYNC_LEAD_IN = 0.15  # точный синхрон: кадр фразы начинается чуть раньше её первого слова (окно −0,2…+0,5 с, PLAYBOOK, закон 30)


def _sync_abs(scene):
    return os.environ.get("SYNC") == "abs" or getattr(scene, "SYNC", None) == "abs"


def _beat(scene, k):
    """Ждать начала фразы k. Точный синхрон (SYNC="abs" в narration.py статьи): время сцены = время записи, анимации идут в своём темпе,
    кадр начинается за SYNC_LEAD_IN до первого слова фразы; если прошлый кадр не успел — предупреждение с перерасходом.
    Старый режим (без SYNC): ожидание в «сжатом» времени с постоянной растяжкой STRETCH — даёт сдвиг, растущий к концу сцены."""
    starts, _ = _speech(scene)
    if _sync_abs(scene):
        target = LEAD + starts[min(k, len(starts) - 1)] - SYNC_LEAD_IN
        now = scene.time
        if target > now + 0.02:
            scene.wait((target - now) / scene.SLOW)
        elif now - target > 0.5:
            print(f"  ⚠ синхрон {type(scene).__name__}: кадр фразы {k + 1} опоздал на {now - target:.1f} с — сократите анимации прошлого кадра", flush=True)
        scene._sync_log = getattr(scene, "_sync_log", []) + [(k + 1, round(max(now, target), 2), round(LEAD + starts[min(k, len(starts) - 1)], 2))]
        return
    target = (LEAD + starts[min(k, len(starts) - 1)]) / STRETCH
    now = scene.time / scene.SLOW
    if target > now + 0.05:
        scene.wait(target - now)


def _pad(scene, items, color=WHITE):
    _, length = _speech(scene)
    target = (LEAD + length + TAIL) / (1.0 if _sync_abs(scene) else STRETCH)
    k = 0
    while items and scene.time / scene.SLOW < target - 0.5:
        scene.play(Indicate(items[k % len(items)], color=color, scale_factor=1.06), run_time=1.0)
        scene.wait(0.4)
        k += 1


def _bind(cls, stations, scenes, icons, text, paper_dir):
    cls.STATION_OF = {code: st for code, st, *_ in scenes}
    cls.STATIONS, cls.ICONS, cls.TEXT = stations, icons, text or {}
    cls.PAPER_DIR = Path(paper_dir) if paper_dir else Path(".")
    cls.PAPER_ROOT = next((d for d in cls.PAPER_DIR.resolve().parents if (d / "pyproject.toml").exists()), Path("."))
    cls.beat = _beat
    cls.pad = _pad
    return cls


def story_base(stations, scenes, icons=None, text=None, paper_dir=None):
    """Базовая 2D-сцена ролика: темп из SLOW (сборщик подгоняет под речь), полоса «мы здесь» со значками, self.beat(k), self.pad(…).
    Использование: Base = story_base(P.STATIONS, P.SCENES, ICONS, N.TEXT, HERE)."""

    class StoryBase(Base):
        SLOW = float(os.environ.get("SLOW", 1.6))

        def setup(self):
            self._seen = {}  # объект → [время появления, время конца анимации появления]; для доски (BOARD_PLAN)
            super().setup()
            code = type(self).__name__
            if code in self.STATION_OF:
                self.add(story_bar(self.STATIONS, self.STATIONS.index(self.STATION_OF[code]), icons=self.ICONS))

        def play(self, *args, **kwargs):
            t0 = self.time
            super().play(*args, **kwargs)
            self._note_new(t0)

        def wait(self, *args, **kwargs):
            t0 = self.time
            super().wait(*args, **kwargs)
            self._note_new(t0)

        def _note_new(self, t0):
            for m in self.mobjects:
                if id(m) not in self._seen:
                    self._seen[id(m)] = (m, t0, self.time)

        def tear_down(self):
            """BOARD_PLAN=путь.json: записать, где на последнем кадре лежит каждый объект и когда он появился, —
            точная разметка для рисования «от руки» (core/pipeline/board.py), угадывать её не нужно."""
            super().tear_down()
            path = os.environ.get("BOARD_PLAN")
            if not path:
                return
            import json
            self._note_new(self.time)
            fw, fh = FRAME_WIDTH, FRAME_HEIGHT
            items = []
            for m in self.mobjects:
                if m is getattr(self, "frame", None):  # камера тоже среди объектов сцены — это не часть рисунка
                    continue
                if id(m) not in self._seen or not m.has_points() and not m.get_family()[1:]:
                    continue
                _, t0, t1 = self._seen[id(m)]
                (x0, y1, _), (x1, y0, _) = m.get_corner(UL), m.get_corner(DR)
                box = {"xmin": (x0 + fw / 2) / fw * 1000, "xmax": (x1 + fw / 2) / fw * 1000,
                       "ymin": (fh / 2 - y1) / fh * 1000, "ymax": (fh / 2 - y0) / fh * 1000}
                items.append({"start": t0, "end": t1, "box": {k: int(round(min(1000, max(0, v)))) for k, v in box.items()}})
            with open(path, "w") as f:
                json.dump({"duration": self.time, "items": items}, f, ensure_ascii=False, indent=1)

    return _bind(StoryBase, stations, scenes, icons, text, paper_dir)


def story_base3d(stations, scenes, icons=None, text=None, paper_dir=None):
    """Базовая 3D-сцена ролика: тот же темп, та же полоса (закреплена в кадре), self.say(подпись), self.beat(k), self.pad(…)."""

    class StoryBase3D(ThreeDScene):
        SLOW = float(os.environ.get("SLOW", 1.6))

        def setup(self):
            super().setup()
            self.camera.background_rgba = [0.059, 0.067, 0.082, 1]
            code = type(self).__name__
            if code in self.STATION_OF:
                self.add(story_bar(self.STATIONS, self.STATIONS.index(self.STATION_OF[code]), icons=self.ICONS).fix_in_frame())
            self._lab = None

        def play(self, *args, run_time=1.0, **kwargs):
            super().play(*args, run_time=run_time * self.SLOW, **kwargs)

        def wait(self, duration=1.0, *args, **kwargs):
            super().wait(duration * self.SLOW, *args, **kwargs)

        def say(self, s, color=None):
            """Подпись внизу: сначала убрать старую, потом показать новую."""
            self.unsay()
            self._lab = note(s, color or C_GREY).fix_in_frame()
            self.play(FadeIn(self._lab), run_time=0.5)

        def unsay(self):
            if self._lab is not None:
                self.play(FadeOut(self._lab), run_time=0.3)
                self._lab = None

    return _bind(StoryBase3D, stations, scenes, icons, text, paper_dir)


SAFE = (-7.0, 7.0, -2.95, 3.85)  # область кадра для содержимого: выше полосы «мы здесь» и её значков, внутри краёв


def _leaves(m):
    return [x for x in m.get_family() if x.has_points()]


def _box(m):
    (x0, y0, _), (x1, y1, _) = m.get_corner(DL), m.get_corner(UR)
    return x0, y0, x1, y1


def layout_problems(scene, exclude=()):
    """Конечная проверка расстановки кадра (PLAYBOOK, закон 16): всё внутри SAFE; текст не налезает на текст;
    текст не пересекает рамку плитки (либо внутри, либо снаружи). Возвращает список проблем словами."""
    skip = {id(x) for e in exclude if e is not None for x in e.get_family()}
    mobs = [m for m in scene.mobjects if id(m) not in skip and m is not getattr(scene, "frame", None)]
    texts, frames, problems = [], [], []
    for m in mobs:
        for x in m.get_family():
            if id(x) in skip:
                continue
            if isinstance(x, (Text, MarkupText)):
                texts.append(x)
            elif isinstance(x, (RoundedRectangle,)) and x.get_width() > 1.0 and x.get_height() > 0.6:
                frames.append(x)
    x0, x1, y0, y1 = SAFE
    for m in mobs:
        for leaf in _leaves(m):
            if id(leaf) in skip or leaf.get_width() < 1e-3 and leaf.get_height() < 1e-3:
                continue
            a, b, c, d = _box(leaf)
            if a < x0 - 0.02 or c > x1 + 0.02 or b < y0 - 0.02 or d > y1 + 0.02:
                label = getattr(leaf, "text", None) or type(leaf).__name__
                problems.append(f"за краем: «{label}»")
                break
    for i, t in enumerate(texts):
        a = _box(t)
        for u in texts[i + 1:]:
            b = _box(u)
            ix = min(a[2], b[2]) - max(a[0], b[0])
            iy = min(a[3], b[3]) - max(a[1], b[1])
            if ix > 0.03 and iy > 0.03 and t not in u.get_family() and u not in t.get_family():
                problems.append(f"текст на тексте: «{t.text}» и «{u.text}»")
        for f in frames:
            fb = _box(f)
            inside = a[0] >= fb[0] and a[2] <= fb[2] and a[1] >= fb[1] and a[3] <= fb[3]
            apart = a[2] <= fb[0] or a[0] >= fb[2] or a[3] <= fb[1] or a[1] >= fb[3]
            if not inside and not apart:
                problems.append(f"текст через рамку: «{t.text}»")
    # пометки поверх содержимого (стрелки, рамки подсветки, контуры, линии, фон вроде рельсов) — наложение для них задумано
    overlay = (Arrow, Arc, ArcBetweenPoints, SurroundingRectangle, DashedLine, Line, DashedVMobject)
    tops = [m for m in mobs if (m.has_points() or m.get_family()[1:]) and not isinstance(m, overlay) and not getattr(m, "overlay", False)]
    for i, m in enumerate(tops):  # частичное наложение отдельных элементов кадра (целиком внутри — можно)
        a = _box(m)
        for u in tops[i + 1:]:
            b = _box(u)
            ix = min(a[2], b[2]) - max(a[0], b[0])
            iy = min(a[3], b[3]) - max(a[1], b[1])
            if ix <= 0.05 or iy <= 0.05:
                continue
            small = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
            inside = (a[0] >= b[0] and a[2] <= b[2] and a[1] >= b[1] and a[3] <= b[3]) or \
                     (b[0] >= a[0] and b[2] <= a[2] and b[1] >= a[1] and b[3] <= a[3])
            if not inside and small > 0 and ix * iy > 0.15 * small:
                name = lambda x: getattr(x, "text", None) or next((y.text for y in x.get_family() if hasattr(y, "text")), type(x).__name__)
                problems.append(f"наложение: «{name(m)}» и «{name(u)}»")
    return sorted(set(problems))


def storyboard_base(stations, scenes, icons=None, paper_dir=None):
    """Основа раскадровки: схематичные кадры, по одному на фразу диктора, без анимации (PLAYBOOK, «Флоу», шаг 7).
    В construct: нарисовать кадр фразы → self.snap() → следующий кадр → self.snap() …
    Кадры пишутся в videos/<папка>/storyboard/<сцена>-<N>.png; их берёт core/pipeline/animatic.py вместо текста.
    Запуск: uv run manimgl papers/<папка>/storyboard.py A01 -s -w (для всех сцен — animatic.py --draw)."""

    class StoryboardBase(Scene):
        def setup(self):
            super().setup()
            self.camera.background_rgba = [0.059, 0.067, 0.082, 1]
            self._k = 0
            code = type(self).__name__
            self._bar = None
            if code in self.STATION_OF:
                self._bar = story_bar(self.STATIONS, self.STATIONS.index(self.STATION_OF[code]), icons=self.ICONS)
                self.add(self._bar)

        def snap(self, allow=()):
            """Сохранить текущий кадр как кадр следующей фразы. allow — объекты, которым можно быть вне области содержимого
            (например, подсветка значков в самой полосе «мы здесь»)."""
            self._k += 1
            out = self.PAPER_ROOT / "videos" / self.PAPER_DIR.name / "storyboard"
            out.mkdir(parents=True, exist_ok=True)
            self.update_frame(force_draw=True)
            name = f"{type(self).__name__}-{self._k}"
            self.get_image().convert("RGB").save(out / f"{name}.png")
            import json
            probs = layout_problems(self, exclude=[self._bar, *allow])
            (out / f"{name}.layout.json").write_text(json.dumps(probs, ensure_ascii=False))
            for pr in probs:
                print(f"  ⚠ {name}: {pr}", flush=True)

        def clear_keep_bar(self):
            self.remove(*[m for m in self.mobjects if m is not self._bar])

    return _bind(StoryboardBase, stations, scenes, icons, None, paper_dir)
