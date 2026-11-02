"""Сцены ролика «Как сложить бесконечно много столбиков» (версия 5): история по датам, непрерывные превращения героя-холма.
Запуск одной сцены: uv run manimgl papers/integrals-film/scenes.py A04 -w --hd  ·  весь ролик: uv run python core/pipeline/build.py papers/integrals-film
Правила переходов (закон 24): превращаются только объекты с одной меткой .tag; всё остальное гаснет и появляется заново; подпись сначала
гаснет, потом появляется новая; сквозные сущности меняются по частям (меняется только то, у чего изменилось значение).
Каждая сцена начинается с последнего кадра предыдущей (мгновенно, без склейки). Кадр = фраза диктора (self.beat)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(HERE))
import numpy as np
from manimlib import *
from manimkit import *
import passport as P
import narration as N
from kit import *
from icons import ICONS
from world import *

Base = story_base(P.STATIONS, P.SCENES, ICONS, N.TEXT, HERE)
ORDER = [c for c, *_ in P.SCENES]


def _is_line(m):
    leaves = [x for x in m.get_family() if x.has_points()]
    return bool(leaves) and all(isinstance(x, VMobject) and x.get_fill_opacity() < 0.01 for x in leaves)


def _same(a, b):
    """Один и тот же вид: превращать не нужно, объект просто заменяется."""
    try:
        if len(a.get_family()) != len(b.get_family()):
            return False
        if not (np.allclose(a.get_center(), b.get_center(), atol=0.02) and abs(a.get_width() - b.get_width()) < 0.02
                and abs(a.get_height() - b.get_height()) < 0.02):
            return False
        la = [x for x in a.get_family() if x.has_points()]
        lb = [x for x in b.get_family() if x.has_points()]
        return not la or (la[0].get_stroke_color() == lb[0].get_stroke_color() and abs(la[0].get_fill_opacity() - lb[0].get_fill_opacity()) < 0.02
                          and abs(la[0].get_stroke_opacity() - lb[0].get_stroke_opacity()) < 0.02)
    except Exception:
        return False


def _compatible(a, b):
    """Превращать можно только однотипное: то же число частей и тот же вид (линия — в линию, заливка — в заливку)."""
    return len(a.get_family()) == len(b.get_family()) and _is_line(a) == _is_line(b) and type(a).__name__ == type(b).__name__


def _bright(m):
    """Плотные яркие заливки: полупрозрачное делаем почти сплошным."""
    for x in m.get_family():
        if x.has_points() and isinstance(x, VMobject):
            f = x.get_fill_opacity()
            if 0.28 < f < 0.9:
                x.set_fill(opacity=min(0.95, f * 2.0))
    return m


def _dry(code):
    """«Сухой прогон» сцены: только собрать её последний кадр (для начала следующей сцены)."""
    cls = globals()[code]
    o = object.__new__(cls)
    if hasattr(cls, "end2d"):                      # объёмная сцена: её последний кадр — плоский вид спереди
        o._k, o._cur, o._dry = cls.END_K, [_bright(m) for m in o.end2d()], True
        o._capm = cap(cls.END_CAP)
        return o
    o._init()
    o._dry = True
    o.construct()
    return o


def _ov_key(st):
    return {"lamps": (tuple(st["lit"]) if isinstance(st.get("lit"), (list, tuple)) else st.get("lit")) if st.get("lit") is not None else None,
            "twins": st.get("twins") or None, "tablo": st.get("tablo") or None, "sprout": st.get("sprout") or None}


def ov_parts(code, k):
    """Сквозные сущности кадра k: {имя: (ключ, объект)}; у только что введённой сущности под ней стоит имя до конца сцены."""
    st = state_for(code, k)
    if not st:
        return {}
    keys = _ov_key(st)
    out = {}
    build = {"lamps": lambda: lamps(st["lit"]), "twins": lambda: twins(st["twins"]), "tablo": lambda: tablo(st["tablo"]), "sprout": lambda: sprout(st["sprout"])}
    for name, key in keys.items():
        if key is None:
            continue
        m = build[name]().move_to([*POS[name], 0])
        out[name] = (key, m)
        first = LABELS.get(code, {}).get(name)
        if first is not None and k >= first:
            out[name + "_lab"] = ("lab", tx(NAME[name], 18, C_NOTE).move_to([POS[name][0], POS[name][1] - 0.62, 0]))
    return out


class OverlayMixin:
    def _ov_anims(self, code, k, pin=False):
        new = ov_parts(code, k)
        old = getattr(self, "_ovp", {}) or {}
        anims = []
        for name, (key, m) in new.items():
            if pin:
                m.fix_in_frame()
            if name in old and old[name][0] == key:
                new[name] = old[name]
            elif name in old and not name.endswith("_lab") and len(old[name][1].get_family()) == len(m.get_family()):
                anims.append(ReplacementTransform(old[name][1], m))
            else:
                if name in old:
                    anims.append(FadeOut(old[name][1]))
                anims.append(FadeIn(m))
        for name, (key, m) in old.items():
            if name not in new:
                anims.append(FadeOut(m))
        self._ovp = new
        return anims


class Film(OverlayMixin, Base):
    def _init(self):
        self._k, self._cur, self._capm, self._ovp, self._dry = 0, [], None, {}, False

    def setup(self):
        super().setup()
        self.camera.background_rgba = [0, 0, 0, 1]
        self._init()
        i = ORDER.index(type(self).__name__)
        if i > 0:                                  # начало = последний кадр предыдущей сцены, без анимации
            prev = ORDER[i - 1]
            p = _dry(prev)
            self._cur = list(p._cur)
            self.add(*self._cur)
            if p._capm is not None:
                self._capm = p._capm
                self.add(self._capm)
            self._ovp = ov_parts(prev, p._k)
            for _, m in self._ovp.values():
                self.add(m)

    # ---- кадр фразы ----
    def _enter(self, m, tag, how):
        mode = how.get(tag) if tag else None
        if mode == "create" or (mode is None and _is_line(m)):
            return ShowCreation(m)
        if tag == "bars" or mode == "grow":
            return LaggedStart(*[GrowFromEdge(b, DOWN) for b in m], lag_ratio=0.08)
        if len(m.submobjects) >= 8:
            return LaggedStart(*[FadeIn(x) for x in m], lag_ratio=0.03)
        return FadeIn(m)

    def show(self, *mobs, c=None, how=None, morph=None, rt=1.0):
        self._k += 1
        items = [_bright(m) for m in mobs]
        capm = cap(c) if c else None
        if self._dry:
            self._cur, self._capm = items, capm
            self._caps = getattr(self, '_caps', []) + [c or 'кадр']
            return
        code = type(self).__name__
        self.beat(self._k - 1)
        how, morph = how or {}, morph or {}
        if self._capm is not None:                 # подпись: старая гаснет полностью, потом появляется новая
            self.play(FadeOut(self._capm), run_time=0.25)
            self._capm = None
        anims, old, used = [], list(self._cur), set()
        for m in items:
            t = getattr(m, "tag", None)
            match = None
            if t is not None:                      # метка есть только у объектов, которые правда продолжаются в следующем кадре
                for j, o in enumerate(old):
                    ot = getattr(o, "tag", None)
                    if j not in used and ot is not None and (ot == t or morph.get(ot) == t):
                        match = j
                        break
            if match is not None:
                used.add(match)
                o = old[match]
                if _same(o, m):
                    self.remove(o)
                    self.add(m)
                elif _compatible(o, m) or morph.get(getattr(o, "tag", None)) == t:
                    anims.append(ReplacementTransform(o, m))
                else:                              # разнородное не превращаем: старое гаснет, новое появляется
                    anims.append(FadeOut(o))
                    anims.append(self._enter(m, t, how))
            else:
                anims.append(self._enter(m, t, how))
        for j, o in enumerate(old):
            if j not in used:
                anims.append(FadeOut(o))
        anims += self._ov_anims(code, self._k)
        if anims:
            self.play(*anims, run_time=rt)
        if capm is not None:
            self.play(FadeIn(capm), run_time=0.3)
        self._cur, self._capm = items, capm

    def do(self, fn):
        """Своя анимация между кадрами (в сухом прогоне не выполняется)."""
        if not self._dry:
            fn()

    def track(self, *ms):
        if not self._dry:
            self._cur = list(self._cur) + list(ms)


# ============================== плоские сцены ==============================
class A02(Film):
    def construct(self):
        self.show(hill(), axis_(False, C_NOTE), c="как читать график")
        sl = Dot(pt(-2.5), radius=0.14).set_color(C_AXIS)
        self.show(hill(), axis_(), sl, tx("точка", 22, C_AXIS).move_to(pt(-2.5, -0.6)), c="по оси выбираем точку")
        x = -2.5
        self.show(hill(), axis_(), sl, line(pt(x), pt(x, F(x)), C_BET, 4), Dot(pt(x, F(x)), radius=0.11).set_color(C_BET),
                  dim_v(x - 1.0, AY, AY + F(x), "высота", C_BET, 22, side=-1), c="над точкой стоит число — высота")
        self.show(axis_(), c="двигаем точку — высота меняется, кривая вычерчивается")
        self.do(self.trace)
        self.show(hill(), axis_(), line(pt(-2.0), pt(-2.0, F(-2.0)), C_BET, 4), tx("высота — жёлтая", 24, C_BET).move_to(pt(-0.7, 1.3)),
                  tx("график — синий", 26, C_PRICE).move_to(pt(0.0, 3.5)), tx("ось — оранжевая", 24, C_AXIS).move_to(pt(3.2, -0.6)), c="цвета ролика")

    def trace(self):
        t = ValueTracker(-5.0)
        X = lambda: t.get_value()
        dot = always_redraw(lambda: Dot(pt(X()), radius=0.14).set_color(C_AXIS))
        vl = always_redraw(lambda: line(pt(X()), pt(X(), F(X())), C_BET, 4))
        tip = always_redraw(lambda: Dot(pt(X(), F(X())), radius=0.11).set_color(C_BET))
        trail = always_redraw(lambda: poly_line([pt(x, F(x)) for x in np.linspace(XL, max(X(), XL + 0.05), 40)], C_PRICE, 5))
        self.add(trail, vl, dot, tip)
        self.play(t.animate.set_value(5.0), run_time=4.0, rate_func=linear)
        for m in (trail, vl, dot, tip):
            m.clear_updaters()
        self.remove(vl, dot, tip)
        self.remove(trail)
        full = hill()
        self.add(full)
        self.track(full)


def msum(n):
    """Сумма площадей n столбиков с высотой в середине куска — считается из того же рисунка, что и на экране."""
    w = (XR - XL) / n
    return sum(F(XL + (i + 0.5) * w) * w for i in range(n))


def num(v, d=2):
    return f"{v:.{d}f}".replace(".", ",")


def panel_hill(cx, cy, n, pick="mid", s=0.38):
    """Уменьшенный холм со столбиками: число стоит под картинкой и считается из неё."""
    w = (XR - XL) / n
    off = {"left": 0.0, "mid": 0.5, "right": 1.0}[pick]
    g = VGroup()
    for i in range(n):
        xm = XL + (i + off) * w
        h = F(XL + (i + off) * w)
        g.add(Rectangle(width=w * 0.96, height=max(h, 0.03)).set_stroke(C_BET, 1.5).set_fill(C_BET, 0.5).move_to([XL + (i + 0.5) * w, AY + max(h, 0.03) / 2, 0]))
    g.add(hill(C_PRICE, 5), axis_(False, C_AXIS))
    g.scale(s, about_point=pt(0)).shift(np.array([cx, cy, 0.0]) - pt(0))
    return g


def psum(n, pick="mid"):
    w = (XR - XL) / n
    off = {"left": 0.0, "mid": 0.5, "right": 1.0}[pick]
    return sum(F(XL + (i + off) * w) * w for i in range(n))


class A04(Film):
    def construct(self):
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), dim_v(2.55, -1.4, 0.6, "высота", C_BET, 24), dim_h(-1.7, 1.7, -1.95, "ширина = длина куска", C_AXIS, 22),
                  c="у столбика есть высота и ширина")
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), tx("площадь = ширина × высота", 34, WHITE).move_to([0, 2.3, 0]),
                  dim_v(2.55, -1.4, 0.6, "высота", C_BET, 24), dim_h(-1.7, 1.7, -1.95, "ширина", C_AXIS, 22), c="площадь столбика")
        self.show(hill(), axis_(), bars(10, 0.5), tx("складываем площади всех столбиков", 28, C_SUM).move_to([0, 2.5, 0]), c="получается сумма")
        pans = [(cx, n) for cx, n in ((-4.4, 6), (0.0, 12), (4.4, 24))]
        self.show(*[panel_hill(cx, 0.4, n) for cx, n in pans], *[tx(num(psum(n)), 30, C_SUM).move_to([cx, -1.4, 0]) for cx, n in pans],
                  *[tx(f"столбиков {n}", 22, C_NOTE).move_to([cx, -0.95, 0]) for cx, n in pans], tx("площадь фигуры равна 20", 28, WHITE).move_to([0, 2.5, 0]),
                  c="тоньше столбики — сумма ближе к площади")
        self.show(hill(), axis_(), bars(40, 0.5), c="без конца тоньше — сумма совпадает с площадью")


class A07(Film):
    def construct(self):
        self.show(hill(), axis_(), bars(10, 0.5), plaque("1854", "Риман", WHITE, 0, 2.8), c="Риман: что значит посчитать площадь точно")
        pa, pb = panel_hill(-3.4, 0.2, 7, "mid", 0.5), panel_hill(3.4, 0.2, 11, "mid", 0.5)
        self.show(pa, pb, tx("режем так", 26, WHITE).move_to([-3.2, 2.1, 0]), tx("режем иначе", 26, WHITE).move_to([3.2, 2.1, 0]),
                  tx(num(psum(7)), 30, C_SUM).move_to([-3.2, -1.7, 0]), tx(num(psum(11)), 30, C_SUM).move_to([3.2, -1.7, 0]), c="ось можно резать на куски как угодно")
        pl, pm = panel_hill(-3.4, 0.2, 10, "left", 0.5), panel_hill(3.4, 0.2, 10, "mid", 0.5)
        self.show(pl, pm, tx("высота слева", 26, C_BET).move_to([-3.2, 2.1, 0]), tx("высота посередине", 26, C_BET).move_to([3.2, 2.1, 0]),
                  tx(num(psum(10, "left")), 30, C_SUM).move_to([-3.2, -1.7, 0]), tx(num(psum(10, "mid")), 30, C_SUM).move_to([3.2, -1.7, 0]),
                  c="высоту можно брать в любой точке куска")
        self.show(hill(), axis_(), bars(40, 0.5), tx("при утончении сумма приближается к 20: это и есть площадь", 28, WHITE).move_to([0, 2.5, 0]), c="предел суммы и есть площадь")


class A08(Film):
    def construct(self):
        bb = lambda **k: big_bar(0, -1.5, 3.4, 1.9, 0.6, 0.0, **k)
        self.show(bb(), c="у счёта есть договор из четырёх пунктов")
        self.show(bb(bar=False, curve=False, pieceline=False), bb().set_opacity(0.25), poly_line([[t * 1.7, -1.5 + 1.9 + 0.6 * t, 0] for t in np.linspace(-1.3, 1.3, 30)], C_PRICE, 10),
                  tx("какой график", 28, C_PRICE).move_to([0.2, 2.0, 0]), c="первый пункт — что складываем")
        self.show(bb(), line([-1.7, -1.5, 0], [1.7, -1.5, 0], C_AXIS, 16), tx("ширина куска — его длина", 26, C_AXIS).move_to([0, -2.2, 0]), c="второй — чем меряем ширину куска")
        self.show(bb(), Dot([0.0, -1.5 + 1.9, 0], radius=0.18).set_color(C_BET), tx("любая точка куска", 26, C_BET).move_to([0.0, 1.25, 0]).shift(UP * 1.4), c="третий — где в куске берём высоту")
        self.show(bb(), tx("+", 70, C_ADD).move_to([2.9, -0.3, 0]), tx("сумма", 30, C_ADD).move_to([4.3, -0.3, 0]), c="четвёртый — как складываем")
        pa, pb = panel_hill(-3.4, 0.1, 8, "mid", 0.45), panel_hill(3.4, 0.1, 13, "mid", 0.45)
        self.show(pa, pb, tx(num(psum(8)), 30, C_SUM).move_to([-3.2, -1.7, 0]), tx(num(psum(13)), 30, C_SUM).move_to([3.2, -1.7, 0]),
                  tx("счётчик А", 24, WHITE).move_to([-3.2, 2.2, 0]), tx("счётчик Б", 24, WHITE).move_to([3.2, 2.2, 0]),
                  tx("оба стремятся к 20", 26, WHITE).move_to([0, -2.3, 0]), c="разные нарезки — совпадающая сумма")


ROWS = [("Риман", "площадь", "сумма: значение × ширина куска", "площадь, физика", C_BET),
        ("Стилтьес", "неровная ширина", "сумма: значение × прирост веса", "физика, вероятность", C_AXIS),
        ("Лебег", "рваный график, пределы", "сумма: высота слоя × мера слоя", "ряды Фурье, вероятность", C_BET),
        ("Ито", "случайная ширина", "значение в левой точке куска", "финансы, шум", C_NOISE),
        ("Стратонович", "привычные правила", "среднее по краям куска", "физика шума", C_NOISE)]


def _pic(i, x, y):
    if i == 0:
        g = VGroup(*[Rectangle(width=0.2, height=h).set_stroke(C_BET, 1).set_fill(C_BET, 0.9) for h in (0.3, 0.5, 0.55, 0.45)]).arrange(RIGHT, buff=0.02, aligned_edge=DOWN)
    elif i == 1:
        g = poly_line([[-0.4, 0, 0], [-0.1, 0, 0], [-0.1, 0.3, 0], [0.2, 0.3, 0], [0.2, 0.55, 0], [0.4, 0.55, 0]], C_AXIS, 4)
    elif i == 2:
        g = VGroup(*[Rectangle(width=0.8 - 0.18 * k, height=0.16).set_stroke(C_BET, 1).set_fill(C_BET, 0.9) for k in range(4)]).arrange(UP, buff=0.02)
    elif i == 3:
        g = VGroup(poly_line([[-0.4, 0, 0], [-0.25, 0.2, 0], [-0.1, -0.05, 0], [0.05, 0.25, 0], [0.2, 0.1, 0], [0.4, 0.3, 0]], C_NOISE, 3), Triangle().scale(0.08).rotate(PI).set_fill(C_BAD, 1).set_stroke(width=0).move_to([-0.25, 0.4, 0]))
    else:
        g = VGroup(poly_line([[-0.4, 0, 0], [-0.25, 0.2, 0], [-0.1, -0.05, 0], [0.05, 0.25, 0], [0.2, 0.1, 0], [0.4, 0.3, 0]], C_NOISE, 3), Triangle().scale(0.08).rotate(PI).set_fill(C_SUM, 1).set_stroke(width=0).move_to([0.0, 0.4, 0]))
    return g.move_to([x, y, 0])


def _table(cols):
    g = VGroup()
    ys = [1.9 - 0.85 * i for i in range(len(ROWS))]
    heads = {"name": ("способ", -5.2), "pic": ("картинка", -3.3), "fix": ("что чинил", -1.0), "formula": ("формула", 2.0), "use": ("где применяют", 5.2)}
    for key in cols:
        h, x = heads[key]
        g.add(tx(h, 22, C_NOTE).move_to([x, 2.65, 0]))
    for i, (nm, fix, formula, use, col) in enumerate(ROWS):
        y = ys[i]
        if "name" in cols:
            g.add(tx(nm, 28, col).move_to([-5.2, y, 0]))
        if "pic" in cols:
            g.add(_pic(i, -3.3, y))
        if "fix" in cols:
            g.add(tx(fix, 22, WHITE).move_to([-1.0, y, 0]))
        if "formula" in cols:
            g.add(tx(formula, 22, WHITE).move_to([2.0, y, 0]))
        if "use" in cols:
            g.add(tx(use, 22, C_SUM).move_to([5.2, y, 0]))
    return g


class F01(Film):
    def construct(self):
        self.show(_table(["name", "pic"]), c="у каждого способа своя картинка")
        self.show(_table(["name", "pic", "fix"]), c="и своя поломка, которую он чинил")
        self.show(_table(["name", "pic", "fix", "use"]), c="и свои применения")


def lowsum(n):
    """Сумма «лесенки снизу» из n ступеней под холмом: ступень берёт высоту у дальнего от середины края куска."""
    w = (XR - XL) / n
    return sum(F(max(abs(XL + i * w), abs(XL + (i + 1) * w))) * w for i in range(n))


def stair_pts(n):
    w = (XR - XL) / n
    pts = []
    for i in range(n):
        x0, x1 = XL + i * w, XL + (i + 1) * w
        h = F(max(abs(x0), abs(x1)))
        pts += [pt(x0, h), pt(x1, h)]
    return pts


def panel_stair(cx, cy, n, s=0.42):
    g = VGroup(area_of(lambda x: 0.0, XL, XR, AY, C_BET, 0.0), poly_line(stair_pts(n), C_PRICE, 6), hill(C_NOTE, 3), axis_(False, C_AXIS))
    g.scale(s, about_point=pt(0)).shift(np.array([cx, cy, 0.0]) - pt(0))
    return g


class A14(Film):
    def construct(self):
        self.show(hill(C_NOTE, 3), axis_(), tx("второй козырь Лебега", 32, WHITE).move_to([0, 2.6, 0]), c="пределы", morph={"dots": "hill"}, rt=1.6)
        self.show(hill(C_NOTE, 3), axis_(), poly_line(stair_pts(3), C_PRICE, 4).set_stroke(opacity=0.45), poly_line(stair_pts(6), C_PRICE, 4).set_stroke(opacity=0.7),
                  poly_line(stair_pts(12), C_PRICE, 5), tx("приближения", 28, C_PRICE).move_to([0, 2.5, 0]), c="графики всё ближе к предельному — приближения")
        pans = [(-4.2, 3), (0.0, 6), (4.2, 12)]
        self.show(*[panel_stair(cx, 0.4, n) for cx, n in pans], *[tx(num(lowsum(n)), 30, C_SUM).move_to([cx, -1.4, 0]) for cx, n in pans],
                  tx("площади тоже растут к 20", 28, WHITE).move_to([0, 2.5, 0]), c="площади подходят к площади предельного графика")
        self.show(VGroup(tx("слои Лебега", 32, C_BET), tx("всегда работают", 26, C_SUM)).arrange(DOWN, buff=0.4).move_to([-3.2, 0.5, 0]),
                  VGroup(tx("столбики Римана", 32, C_BET), tx("иногда застревают", 26, C_BAD)).arrange(DOWN, buff=0.4).move_to([3.2, 0.5, 0]), c="со слоями работает всегда")
        self.show(VGroup(curve_of(lambda x: 0.7 * np.sin(2.5 * x), -1.2, 1.2, 0, C_PRICE, 5, 40), tx("ряды Фурье", 28, WHITE)).arrange(DOWN, buff=0.4).move_to([-3.0, 0.4, 0]),
                  VGroup(bell(0, 0), tx("вероятность", 28, WHITE)).arrange(DOWN, buff=0.4).move_to([3.0, 0.4, 0]), c="на такой основе стоят Фурье и вероятность")


class A01(Film):
    def construct(self):
        self.show(hill(), axis_(False, C_NOTE), c="график")
        self.show(hill(), axis_(False, C_NOTE), area(C_PRICE, 0.22), tx("площадь", 34, WHITE).move_to([0, -0.2, 0]), c="сколько места в этой фигуре")
        rect = Rectangle(width=2.4, height=1.6).set_stroke(C_BET, 3).set_fill(C_BET, 0.25).move_to([-3.6, 0.2, 0])
        arch = poly_line([[x, 0.1 + 1.6 * (1 - (x / 2.0) ** 2), 0] for x in np.linspace(-2, 2, 40)], C_PRICE, 5).move_to([3.4, 0.4, 0])
        base = line([1.4, -0.7, 0], [5.4, -0.7, 0], C_NOTE, 3)
        self.show(rect, tx("у прямоугольника всё просто", 22, C_BET).move_to([-3.6, -1.3, 0]), arch, base,
                  tx("кривая сверху: простой формулы нет", 22, C_PRICE).move_to([3.4, -1.3, 0]), c="прямоугольник считается просто")
        self.show(hill(), axis_(False, C_NOTE), area(C_PRICE, 0.15), tx("как считали и почему способ менялся", 30, WHITE).move_to([0, 2.4, 0]),
                  c="способ счёта переделывали много раз")
        self.show(tx("Как посчитать площадь так, чтобы ответ", 38).move_to([0, 1.5, 0]), tx("не зависел от способа счёта?", 38).move_to([0, 0.7, 0]),
                  hill(C_PRICE, 4, -2.6, 2.6).scale(0.5).move_to([0, -1.3, 0]), c="вопрос ролика")


class A03(Film):
    def construct(self):
        self.show(hill(), axis_(), cuts(8), VGroup(*[piece(XL + i * 1.25, XL + (i + 1) * 1.25, C_AXIS, AY - 0.12, 8) for i in range(8)]), c="ось делится на куски")
        self.show(hill(), axis_(), bars(8), c="на каждом куске — столбик")
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), tx("кусок оси", 24, C_AXIS).move_to([0, -1.95, 0]),
                  tx("верх на графике", 24, C_PRICE).move_to([2.4, 1.6, 0]), tx("столбик", 26, C_BET).move_to([0, 0.0, 0]),
                  c="столбик стоит на куске оси, верх касается графика")
        self.show(hill(), axis_(), bars(16), c="вся фигура — из столбиков")


class A05(Film):
    def construct(self):
        T = lambda a, b, c, col, op: Polygon(pt(*a), pt(*b), pt(*c)).set_stroke(col, 3).set_fill(col, op)
        base = [hill(), axis_(False, C_NOTE)]
        self.show(*base, plaque("III в. до н. э.", "Архимед", WHITE, 0, 2.65), tx("кусок параболы", 26, C_PRICE).move_to([0, -0.4, 0]), c="Архимед искал площадь куска параболы")
        t1 = T((-5, 0), (5, 0), (0, H), C_BET, 0.3)
        t2 = [T((0, H), (5, 0), (2.5, F(2.5)), C_AXIS, 0.4), T((-5, 0), (0, H), (-2.5, F(2.5)), C_AXIS, 0.4)]
        self.show(*base, t1, *t2, tx("вписанный треугольник", 22, C_BET).move_to([0, -0.2, 0]), tx("поменьше", 20, C_AXIS).move_to([-3.2, 0.0, 0]), tx("поменьше", 20, C_AXIS).move_to([3.2, 0.0, 0]), c="в кусок вписан треугольник, в промежутки — поменьше")
        t3 = [T((0, H), (2.5, F(2.5)), (1.25, F(1.25)), C_ADD, 0.5) for _ in range(0)]
        sq = lambda s, col: Square(side_length=s).set_stroke(col, 3).set_fill(col, 0.4)
        row = VGroup(sq(1.6, C_BET), sq(0.8, C_AXIS), sq(0.4, C_ADD), sq(0.2, C_SUM), tx("…", 30, WHITE)).arrange(RIGHT, buff=0.35, aligned_edge=DOWN).move_to([0, 0.6, 0])
        self.show(row, tx("1", 22, WHITE).next_to(row[0], DOWN, buff=0.1), tx("¼", 22, WHITE).next_to(row[1], DOWN, buff=0.1), tx("1/16", 20, WHITE).next_to(row[2], DOWN, buff=0.1),
                  c="каждый следующий ряд — четверть предыдущего")
        self.show(row.copy().move_to([0, 1.6, 0]), tx("вместе: треугольник и ещё его треть", 30, WHITE).move_to([0, -0.2, 0]),
                  tx("сумма подходит к одному числу", 26, C_SUM).move_to([0, -1.2, 0]), c="ряды не кончаются, сумма подходит к числу")
        # пятая фраза: та же идея — части, число которых растёт без конца
        self.show(VGroup(bars_of(lambda x: 1.3 * (1 - (x / 2.5) ** 2), 10, -2.5, 2.5, 0.0, C_BET, 0.4), curve_of(lambda x: 1.3 * (1 - (x / 2.5) ** 2), -2.5, 2.5, 0.0, C_PRICE, 3, 40)).move_to([3.2, 0.2, 0]),
                  VGroup(Polygon(np.array([-1.5, -0.7, 0]), np.array([1.5, -0.7, 0]), np.array([0, 0.9, 0])).set_stroke(C_BET, 3).set_fill(C_BET, 0.3)).move_to([-3.2, 0.1, 0]),
                  tx("=", 40, WHITE).move_to([0, 0.2, 0]), tx("части, которых без конца больше", 26, C_NOTE).move_to([0, -1.8, 0]), c="та же идея, что у столбиков")


class A06(Film):
    def _acc(self, x1):
        return [tagged(area_of(F, XL, x1, AY, C_SUM, 0.35), 'fill'), tagged(line(pt(x1), pt(x1, F(x1)), C_BET, 3), 'vl'), tagged(Dot(pt(x1), radius=0.14).set_color(C_AXIS), 'sl')]

    def accumulate(self):
        t = ValueTracker(-5.0)
        X = lambda: t.get_value()
        fill = always_redraw(lambda: area_of(F, XL, max(X(), XL + 0.05), AY, C_SUM, 0.35))
        vl = always_redraw(lambda: line(pt(X()), pt(X(), F(X())), C_BET, 3))
        dot = always_redraw(lambda: Dot(pt(X()), radius=0.14).set_color(C_AXIS))
        lab = always_redraw(lambda: tx('площадь слева от точки', 22, C_SUM).move_to([X() - 2.2, 0.3, 0]))
        self.add(fill, vl, dot, lab)
        self.play(t.animate.set_value(1.0), run_time=3.0, rate_func=smooth)
        for m in (fill, vl, dot, lab):
            m.clear_updaters()
        self.remove(fill, vl, dot, lab)
        fin = self._acc(1.0)
        self.add(*fin)
        self.track(*fin)

    def construct(self):
        x1 = 1.0
        left = lambda: [*self._acc(x1), hill(), axis_(False, C_NOTE)]
        self.show(hill(), axis_(False, C_NOTE), c="нашли короткий путь")
        self.do(self.accumulate)
        self.show(*left(), portrait("Ньютон", "", WHITE, 0.9).move_to([-5.4, 2.35, 0]), portrait("Лейбниц", "", WHITE, 0.9).move_to([-3.6, 2.35, 0]),
                  plaque("XVII в.", "независимо", WHITE, 3.5, 2.65), c="Ньютон и Лейбниц, XVII век")
        def panel(g, cx, cy, sc):
            g.scale(sc, about_point=pt(0)).shift(np.array([cx, cy, 0.0]) - pt(0))
            return g
        Gf = lambda x: 2.4 * (((x + 5) - (x ** 3 + 125) / 75.0) * H / 20.0 * 20.0 / 20.0) / (H * 10 * 2 / 3) * 1.0
        grow = lambda x: 2.4 * ((x + 5) - (x ** 3 + 125) / 75.0) / (10 - 250 / 75.0)     # площадь слева от точки, 0…2,4
        xs0 = 1.0
        L = lambda extra=(): panel(VGroup(hill(C_PRICE, 4), axis_(False, C_NOTE), *extra), -3.2, -0.6, 0.5)
        R = lambda extra=(): VGroup(line([0.4, -1.8, 0], [6.0, -1.8, 0], C_NOTE, 2), poly_line([[0.4 + 5.6 * (x + 5) / 10, -1.8 + grow(x), 0] for x in np.linspace(-5, 5, 60)], C_SUM, 5), *extra)
        dotL = lambda x: Dot(pt(x), radius=0.14).set_color(C_AXIS)
        self.show(L([line(pt(xs0), pt(xs0, F(xs0)), C_BET, 4), dotL(xs0)]), R([Dot([0.4 + 5.6 * (xs0 + 5) / 10, -1.8 + grow(xs0), 0], radius=0.12).set_color(C_SUM)]),
                  tx("высота графика", 22, C_BET).move_to([-3.2, 1.4, 0]), tx("площадь слева от точки", 22, C_SUM).move_to([3.2, 0.9, 0]),
                  c="где график выше, там площадь растёт быстрее")
        xa, xb = -2.0, 2.0
        ga, gb = [0.4 + 5.6 * (x + 5) / 10 for x in (xa, xb)], [-1.8 + grow(x) for x in (xa, xb)]
        self.show(L([area_of(F, xa, xb, AY, C_SUM, 0.45), line(pt(xa), pt(xa, F(xa)), C_BET, 3), line(pt(xb), pt(xb, F(xb)), C_BET, 3)]),
                  R([Dot([ga[0], gb[0], 0], radius=0.12).set_color(C_SUM), Dot([ga[1], gb[1], 0], radius=0.12).set_color(C_SUM), line([ga[1] + 0.35, gb[0], 0], [ga[1] + 0.35, gb[1], 0], C_SUM, 4)]),
                  tx("площадь между двумя точками", 22, C_SUM).move_to([-3.2, 1.4, 0]), tx("разность двух значений", 22, C_SUM).move_to([3.2, 1.0, 0]),
                  c="площадь между точками — разность двух значений")
        s = VMobject().set_points_smoothly([np.array(p, dtype=float) for p in
                                            [(-0.45, -1.0, 0), (-0.25, -1.25, 0), (-0.05, -1.05, 0), (0.0, -0.6, 0), (0.0, 0.7, 0), (0.05, 1.05, 0), (0.25, 1.25, 0), (0.45, 1.05, 0)]]).set_stroke(WHITE, 8).set_fill(opacity=0)
        self.show(s.scale(1.2).move_to([-2.0, 0.2, 0]), tx("вытянутая S от слова summa", 28, WHITE).move_to([2.2, 0.4, 0]), portrait("Лейбниц", "", WHITE, 1.0).move_to([2.2, -1.4, 0]),
                  c="знак интеграла придумал Лейбниц")


class A09(Film):
    def construct(self):
        self.show(hill(), axis_(), bars(8), c="поменяем ширину столбика — пункт про ось")
        edges = [-5.0, -3.6, -2.4, -1.5, -0.2, 1.5, 2.4, 3.6, 5.0]
        ub = bars_of(F, 8, -5.0, 5.0, AY, C_BET, 0.35)
        ubs = VGroup(*[Rectangle(width=edges[i + 1] - edges[i], height=F((edges[i] + edges[i + 1]) / 2)).set_stroke(C_BET, 2).set_fill(C_BET, 0.4).move_to([(edges[i] + edges[i + 1]) / 2, AY + F((edges[i] + edges[i + 1]) / 2) / 2, 0]) for i in range(8)])
        self.show(hill(), axis_(), ubs, dim_h(edges[1], edges[2], AY - 0.5, "прирост веса", C_AXIS, 20), c="ширина куска — прирост другой величины, веса")
        wpts = [(-5.0, 0.0), (-3.0, 0.5), (-1.2, 0.8), (0.4, 0.85), (1.2, 0.9), (2.0, 1.9), (3.2, 2.2), (5.0, 2.4)]
        wl = poly_line([[x, -2.55 + 0.5 * y, 0] for x, y in wpts], C_AXIS, 5)
        self.show(hill().scale(0.5, about_point=pt(0)).shift(UP * 2.0), line([-5.8, -0.55, 0], [5.8, -0.55, 0], C_AXIS, 4), tx("ось", 20, C_AXIS).move_to([5.4, -0.85, 0]), wl,
                  line([-5.0, -2.6, 0], [5.0, -2.6, 0], C_NOTE, 2), tx("вес", 28, C_AXIS).move_to([-5.5, -1.7, 0]), tx("почти стоит", 20, C_AXIS).move_to([0.4, -1.55, 0]),
                  tx("быстро растёт", 20, C_AXIS).move_to([3.6, -1.1, 0]), c="вес растёт неровно")
        wide = Rectangle(width=2.0, height=2.0).set_stroke(C_BET, 3).set_fill(C_BET, 0.45).move_to([0, -0.4, 0])
        step = poly_line([[-3.0, -1.5, 0], [-1.0, -1.5, 0], [-1.0, -0.5, 0], [1.0, -0.5, 0], [1.0, 0.8, 0], [3.0, 0.8, 0]], C_AXIS, 5)
        self.show(wide, dim_h(-1.0, 1.0, -1.75, "скачок веса = широкий столбик", C_AXIS, 22), step.shift(DOWN * 0.0), tx("скачок", 24, C_AXIS).move_to([1.5, 0.0, 0]), c="скачок веса — широкий столбик")
        self.show(big_bar(0, -1.4, 3.4, 2.0, 0.6, 0.0), tx("площадь = высота × прирост веса", 30, WHITE).move_to([0, 2.2, 0]), dim_h(-1.7, 1.7, -1.95, "прирост веса", C_AXIS, 22), c="сумма считается так же")
        self.show(hill(), axis_(), bars(8), plaque("1894", "Стилтьес", WHITE, 0, 2.65), c="так предложил Стилтьес")


class A10(Film):
    def construct(self):
        stairs = poly_line([pt(-5, 1.0), pt(-3, 1.0), pt(-3, 2.2), pt(-1, 2.2), pt(-1, 0.6), pt(1.5, 0.6), pt(1.5, 2.6), pt(3.4, 2.6), pt(3.4, 1.4), pt(5, 1.4)], C_PRICE, 5)
        self.show(stairs, axis_(), hill(C_NOTE, 2).set_opacity(0.3), c="график не обязан быть гладким")
        d, xs, up = jump()
        self.show(d, axis_(), vaxis().scale(0.001), one_zero_marks(), tx("единица в дробях, во всех остальных точках ноль", 24, WHITE).move_to([0, 2.4, 0]), c="в каждой точке оси — единица или ноль", morph={"hill": "dots"}, rt=1.6)
        # увеличение куска: кусок оси и его крупный план в рамке; в крупном плане снова и единицы, и нули
        dd, _, _ = jump(-4.8, 4.8, AY, 1.2, 60, 7)
        sel = Rectangle(width=0.8, height=1.6).set_stroke(C_AXIS, 2).move_to([0.0, AY + 0.6, 0])

        def panel(cx, cy, w, h, n, seed):
            fr = Rectangle(width=w, height=h).set_stroke(C_AXIS, 2)
            pd, _, _ = jump(-w / 2 + 0.3, w / 2 - 0.3, -h / 2 + 0.3, h - 0.6, n, seed, 0.09)
            return VGroup(fr, pd).move_to([cx, cy, 0])
        p1 = panel(0.0, 1.4, 7.0, 1.8, 26, 21)
        self.show(dd.set_opacity(0.7), axis_(), one_zero_marks(hi=1.2), sel, p1,
                  line([-0.4, AY + 1.4, 0], [-3.5, 0.5, 0], C_AXIS, 2, True), line([0.4, AY + 1.4, 0], [3.5, 0.5, 0], C_AXIS, 2, True),
                  tx("тот же кусок крупно", 22, C_AXIS).move_to([5.0, 1.4, 0]), c="в любом куске есть и те, и другие")
        pa = panel(-3.3, 0.6, 4.4, 1.8, 20, 21)
        pb = panel(2.8, 0.6, 5.8, 1.8, 16, 33)
        self.show(pa, pb, Rectangle(width=0.7, height=1.4).set_stroke(C_AXIS, 2).move_to([-3.0, 0.6, 0]), Arrow([-0.8, 0.6, 0], [-0.1, 0.6, 0], buff=0).set_color(C_AXIS),
                  tx("ещё крупнее", 22, C_AXIS).move_to([2.8, -0.7, 0]), tx("и снова единицы и нули вперемешку", 24, WHITE).move_to([0, 2.3, 0]), c="увеличиваем — снова и то, и другое")
        self.show(d, axis_(), one_zero_marks(), tx("?", 90, C_BAD).move_to([0, 2.6, 0]), tx("выдержит ли договор такой график", 26, WHITE).move_to([0, -2.2, 0]))


class A11(Film):
    def construct(self):
        d, xs, up = jump()
        self.show(d, axis_(), one_zero_marks(), piece(-0.6, 0.6), tx("проверим договор", 28, WHITE).move_to([0, 2.5, 0]), c="возьмём кусок оси")
        row, _, upv = jump(-1.7, 1.7, -1.0, 1.9, 14, 5, 0.11)
        base = VGroup(line([-1.9, -1.0, 0], [1.9, -1.0, 0], C_AXIS, 9), Rectangle(width=3.8, height=1.9).set_stroke(C_BET, 2).move_to([0, -0.05, 0]).set_stroke(opacity=0.5))
        self.show(row, base, tx("кусок оси", 22, C_AXIS).move_to([0, -1.55, 0]), c="поставим на нём столбик")
        i_hi = int(np.argmax(upv)); i_lo = int(np.argmin(upv))
        lz = lens(row[i_hi].get_center()[0] - 0.05, row[i_hi].get_center()[1] + 0.05)
        self.show(row, base, lz, tx("замер", 30, C_BET).move_to([0, 2.0, 0]), c="высота берётся в одной точке куска")

        def hop():
            for k in (i_lo, i_hi, i_lo):
                p = row[k].get_center()
                self.play(lz.animate.move_to([p[0] + 0.2, p[1] - 0.2, 0]), run_time=0.7)
                self.wait(0.2)
        self.do(hop)
        hi_bar = Rectangle(width=3.0, height=1.9).set_stroke(C_BET, 3).set_fill(C_BET, 0.45).move_to([-3.4, -0.05, 0])
        lo_bar = line([2.0, -1.0, 0], [5.0, -1.0, 0], C_BET, 8)
        self.show(hi_bar, line([-4.9, -1.0, 0], [-1.9, -1.0, 0], C_AXIS, 9), Dot([-3.4, 0.9, 0], radius=0.13).set_color(C_BET), tx("точка с единицей: столбик высокий", 22, C_BET).move_to([-3.4, 1.6, 0]),
                  lo_bar, line([2.0, -1.0, 0], [5.0, -1.0, 0], C_AXIS, 9).shift(DOWN * 0.1), Dot([3.5, -1.0, 0], radius=0.13).set_color(WHITE), tx("точка с нулём: столбик плоский", 22, WHITE).move_to([3.5, -0.2, 0]),
                  c="единица — высокий, ноль — плоский")
        self.show(hi_bar.copy().move_to([-3.4, -0.05, 0]), line([-4.9, -1.0, 0], [-1.9, -1.0, 0], C_AXIS, 9), line([2.0, -1.0, 0], [5.0, -1.0, 0], C_BET, 8),
                  tx("≠", 100, C_BAD).move_to([0, -0.3, 0]), tx("один и тот же кусок", 22, C_AXIS).move_to([0, -2.2, 0]), c="кусок тот же, а столбики разные")
        self.show(d, axis_(), one_zero_marks(), cross(C_BAD, 0.9).move_to([0, 0.8, 0]), plaque("1854", "Риман", C_BAD, 0, 2.6), c="способ Римана здесь не работает")


class A15(Film):
    def construct(self):
        j, _, _ = noise(-5, 5, -1.7, 0.1, 70, 4, C_NOISE, 3)
        self.show(hill().scale(0.55, about_point=pt(0)).shift(UP * 2.1), line([-5.8, -0.5, 0], [5.8, -0.5, 0], C_AXIS, 4), tx("ось", 20, C_AXIS).move_to([5.4, -0.8, 0]), j, tx("вес", 24, C_AXIS).move_to([-5.5, -1.7, 0]), c="а если вес случаен")
        j1, _, _ = noise(-5.5, 5.5, 0.2, 0.3, 90, 11, C_NOISE, 4)
        self.show(j1, tx("шум", 44, C_NOISE).move_to([0, 2.0, 0]), c="шум — линия дрожит вверх и вниз наугад")
        j2, _, _ = noise(-3.2, 3.2, -0.9, 0.22, 90, 17, C_NOISE, 4)
        j1s, _, _ = noise(-5.5, 5.5, 2.0, 0.12, 90, 11, C_NOISE, 3)
        fr = Rectangle(width=0.9, height=1.0).set_stroke(C_AXIS, 2).move_to([0.8, 2.0, 0])
        self.show(j1s, fr, j2, line([0.3, 1.5, 0], [-3.2, 0.2, 0], C_AXIS, 2, True), line([1.3, 1.5, 0], [3.2, 0.2, 0], C_AXIS, 2, True), tx("увеличим", 22, C_AXIS).move_to([4.5, 1.1, 0]), c="сколько ни увеличивай — снова дрожь")
        jh, _, _ = noise(-4.6, 4.6, 1.5, 0.15, 70, 5, C_NOISE, 3)
        jw, _, _ = noise(-4.6, 4.6, -1.7, 0.15, 70, 7, C_NOISE, 3)
        self.show(jh, jw, line([-5.6, -0.1, 0], [5.6, -0.1, 0], C_AXIS, 3), tx("высота — от шума", 24, C_BET).move_to([0, 2.8, 0]),
                  tx("вес — от такого же шума", 24, C_AXIS).move_to([0, -0.65, 0]), c="и высоту, и вес даёт такая линия")


class A16(Film):
    def construct(self):
        j, xs, ys = noise(-4.0, 4.0, 0.4, 0.25, 40, 13, C_NOISE, 4)
        self.show(j, line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4), piece(-0.6, 0.6, C_AXIS, -1.3), tx("где в куске делать замер?", 30, WHITE).move_to([0, 2.5, 0]), c="в какой точке куска брать высоту")
        self.show(j, line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4), piece(-0.6, 0.6, C_AXIS, -1.3), marker(-0.6, 0.0, C_BAD), marker(0.6, 0.0, C_SUM), tx("левый край", 22, C_BAD).move_to([-1.6, -1.75, 0]), tx("правый край", 22, C_SUM).move_to([1.7, -1.75, 0]),
                  line([-0.6, -1.3, 0], [-0.6, 0.0, 0], C_BAD, 2, True), line([0.6, -1.3, 0], [0.6, 0.0, 0], C_SUM, 2, True), c="у куска два края: левый и правый")
        bl = Rectangle(width=2.0, height=1.9).set_stroke(C_BAD, 3).set_fill(C_BAD, 0.3).move_to([-2.5, -0.35, 0])
        br = Rectangle(width=2.0, height=2.0).set_stroke(C_SUM, 3).set_fill(C_SUM, 0.3).move_to([2.5, -0.3, 0])
        self.show(bl, br, tx("слева", 24, C_BAD).move_to([-2.5, 1.0, 0]), tx("справа", 24, C_SUM).move_to([2.5, 1.0, 0]), tx("=", 90, C_SUM).move_to([0, -0.3, 0]), tx("гладкий график: почти одно и то же", 24, WHITE).move_to([0, 2.4, 0]), c="гладкий график: суммы совпадают")
        bl2 = Rectangle(width=2.0, height=0.9).set_stroke(C_BAD, 3).set_fill(C_BAD, 0.3).move_to([-2.5, -0.85, 0])
        br2 = Rectangle(width=2.0, height=2.1).set_stroke(C_SUM, 3).set_fill(C_SUM, 0.3).move_to([2.5, -0.25, 0])
        self.show(bl2, br2, tx("≠", 90, C_BAD).move_to([0, -0.3, 0]), tx("4,5", 30, C_BAD).move_to([-2.5, 0.3, 0]), tx("5,5", 30, C_SUM).move_to([2.5, 1.1, 0]), tx("шум: суммы расходятся, тоньше — не помогает", 24, WHITE).move_to([0, 2.4, 0]),
                  c="шум: суммы расходятся и при тонких столбиках")
        self.show(pill("пункт про высоту", C_BET, 40).move_to([0, 0.6, 0]), cross(C_BAD, 0.6).move_to([0, -0.9, 0]), tx("придётся переписать", 28, WHITE).move_to([0, -1.9, 0]), c="договор нарушен")


class A17(Film):
    def construct(self):
        j, xs, ys = noise(-4.0, 4.0, 0.4, 0.25, 40, 13, C_NOISE, 4)
        ax = line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4)
        self.show(j, ax, piece(-0.6, 0.6, C_AXIS, -1.3), marker(-0.6, 0.0, C_BAD), tx("левый край", 22, C_BAD).move_to([-1.6, -1.75, 0]), plaque("1944", "Ито", WHITE, 0, 2.65), c="Ито: высоту берём на левом краю")
        fut = Rectangle(width=4.0, height=3.2).set_stroke(C_NOTE, 2).set_fill(C_NOTE, 0.12).move_to([2.6, 0.2, 0])
        self.show(poly_line([[x, y, 0] for x, y in zip(xs[xs < -0.5], ys[xs < -0.5])], C_NOISE, 5), ax, fut, lock(0.9, 1.9, C_BAD), tx("будущее", 24, C_NOTE).move_to([2.6, 0.2, 0]), tx("прошлое известно", 24, C_NOISE).move_to([-2.4, 1.8, 0]),
                  c="высота известна заранее: в будущее не подглядываем")
        self.show(scales(C_SUM).scale(1.4).move_to([-1.4, 0.2, 0]), pill("в среднем 0", C_SUM, 34).move_to([2.8, 0.2, 0]), tx("если шум случаен, в среднем ноль", 26, WHITE).move_to([0, 2.2, 0]), c="сумма честная — в среднем ноль")
        self.show(tx("шум", 30, C_NOISE).move_to([-4.6, 1.0, 0]), tx("→", 40, WHITE).move_to([-3.4, 1.0, 0]), tx("квадрат шума", 30, WHITE).move_to([-0.8, 1.0, 0]),
                  pill("обычное правило: только часть ответа", C_BET, 24).move_to([0, -0.4, 0]), c="возьмём от шума квадрат")
        self.show(pill("обычное правило", C_BET, 28).move_to([-3.2, 0.5, 0]), tx("+", 50, WHITE).move_to([-0.8, 0.5, 0]), pill("добавка", C_ADD, 28).move_to([1.6, 0.5, 0]),
                  tx("добавка — от дрожи шума", 24, C_NOISE).move_to([1.6, -0.4, 0]), c="остальное — добавка")


class A18(Film):
    def construct(self):
        self.show(hill(), axis_(), bars(8), tx("куски равны", 24, C_NOTE).move_to([0, 2.5, 0]), c="куски были одинаковые")
        edges = [-5.0, -3.0, -1.2, 0.4, 1.8, 2.9, 3.8, 4.5, 5.0]
        ubs = VGroup(*[Rectangle(width=edges[i + 1] - edges[i], height=F((edges[i] + edges[i + 1]) / 2)).set_stroke(C_BET, 2).set_fill(C_BET, 0.4).move_to([(edges[i] + edges[i + 1]) / 2, AY + F((edges[i] + edges[i + 1]) / 2) / 2, 0]) for i in range(8)])
        self.show(hill(), axis_(), ubs, plaque("1957–61", "Курцвейль и Хенсток", WHITE, 0, 2.65), c="куски могут быть разной ширины")
        self.show(hill(), axis_(), ubs, tx("круто — куски уже", 22, C_AXIS).move_to([-4.0, 0.6, 0]), tx("полого — шире", 22, C_AXIS).move_to([0.6, 2.2, 0]), c="где график круто меняется — куски уже")


class A19(Film):
    def construct(self):
        j, xs, ys = noise(-4.0, 4.0, 0.4, 0.25, 40, 13, C_NOISE, 4)
        ax = line([-4.0, -1.3, 0], [4.0, -1.3, 0], C_AXIS, 4)
        self.show(j, ax, piece(-0.6, 0.6, C_AXIS, -1.3), marker(-0.6, 0.0, C_BAD), tx("левый край", 22, C_BAD).move_to([-1.6, -1.75, 0]), tx("физикам нужны школьные правила пересчёта", 26, WHITE).move_to([0, 2.5, 0]), c="физикам левый край неудобен")
        self.show(j, ax, piece(-0.6, 0.6, C_AXIS, -1.3), marker(0.0, 0.0, C_SUM), tx("середина", 22, C_SUM).move_to([0.0, -1.75, 0]), plaque("1963–66", "Фиск и Стратонович", WHITE, 0, 2.65), c="Фиск и Стратонович взяли середину куска")
        self.show(pill("обычное правило", C_BET, 30).move_to([0, 0.6, 0]), tx("✓", 80, C_SUM).move_to([0, -0.8, 0]), tx("добавки нет", 28, WHITE).move_to([0, -1.9, 0]), c="с серединой добавки нет")
        a, b = pill("сумма Ито", C_NOISE, 28).move_to([-3.2, 0.5, 0]), pill("сумма Стратоновича", C_NOISE, 28).move_to([3.2, 0.5, 0])
        self.show(a, b, darrow(a.get_right() + RIGHT * 0.15, b.get_left() + LEFT * 0.15, C_BET), pill("+ добавка", C_ADD, 24).move_to([0, 1.3, 0]), c="одну сумму можно перевести в другую")
        jj, _, _ = noise(-5.5, 5.5, 0.4, 0.3, 90, 11, C_NOISE, 4)
        self.show(jj, pill("запись Ито", C_NOISE, 24).move_to([-3.2, -1.4, 0]), pill("запись Стратоновича", C_NOISE, 24).move_to([3.2, -1.4, 0]), Arrow([-3.2, -1.0, 0], [-1.5, 0.0, 0], buff=0).set_color(C_NOTE),
                  Arrow([3.2, -1.0, 0], [1.5, 0.0, 0], buff=0).set_color(C_NOTE), c="обе записи описывают одну линию шума")


class A20(Film):
    def construct(self):
        jr, _, _ = noise(-5.5, 5.5, 0.4, 0.28, 240, 29, C_NOISE, 3)
        self.show(jr, tx("шум грубее", 36, C_NOISE).move_to([0, 2.4, 0]), c="бывает шум ещё грубее")
        self.show(jr, marker(-1.0, -0.8, C_BAD), marker(0.2, -0.8, C_SUM), tx("левый край", 20, C_BAD).move_to([-1.6, -1.6, 0]), tx("середина", 20, C_SUM).move_to([0.9, -1.6, 0]), cross(C_BAD, 0.35).move_to([-1.0, -0.4, 0]), cross(C_BAD, 0.35).move_to([0.2, -0.4, 0]),
                  tx("надёжной суммы нет", 28, C_BAD).move_to([0, 2.4, 0]), c="ни край, ни середина не дают надёжной суммы")
        sp = VMobject().set_points_smoothly([np.array([0.6 * np.cos(t) * (1 - t / 14), 0.6 * np.sin(t) * (1 - t / 14), 0.0]) for t in np.linspace(0, 12, 60)]).set_stroke(C_ADD, 4).set_fill(opacity=0)
        self.show(jr.copy().scale(0.6).move_to([0, -0.8, 0]), sp.move_to([0, 1.2, 0]), portrait("Лайонс", "1998", WHITE, 1.0).move_to([-3.8, 1.8, 0]), tx("подсказка: как шум закручивается", 24, C_ADD).move_to([2.6, 1.6, 0]),
                  c="Лайонс: добавим к шуму подсказку")
        self.show(jr.copy().scale(0.6).move_to([-3.0, 0.3, 0]), sp.copy().scale(0.7).move_to([-3.0, 1.5, 0]), tx("→", 50, WHITE).move_to([0, 0.4, 0]), tablo("число").scale(1.8).move_to([3.4, 0.4, 0]),
                  c="с подсказкой сумма определена для каждой линии")
        self.show(portrait("Хайрер", "2014", WHITE, 1.4).move_to([-2.6, 0.4, 0]), VGroup(Circle(radius=0.7).set_stroke(C_BET, 5).set_fill(C_BET, 0.2), tx("★", 50, C_BET)).move_to([2.6, 0.7, 0]),
                  tx("Филдсовская премия", 26, C_BET).move_to([2.6, -0.5, 0]), c="Хайрер получил Филдсовскую премию")


class A21(Film):
    def construct(self):
        self.show(portrait("Ито", "1944", WHITE, 1.3).move_to([0, -1.2, 0]), *[Arrow([0.0, -0.4, 0], [x, 1.5, 0], buff=0.05).set_stroke(C_NOTE, 3) for x in (-4.2, -1.4, 1.4, 4.2)],
                  *[tx(t, 22, col).move_to([x, 1.95, 0]) for t, col, x in (("скачки", C_SUM, -4.2), ("будущее", C_SUM, -1.4), ("вся история", C_BET, 1.4), ("граница", C_BAD, 4.2))],
                  c="от Ито пути расходятся")
        jj, xs, ys = noise(-5, -0.6, 0.2, 0.25, 30, 41, C_NOISE, 4)
        self.show(jj, poly_line([[-0.6, ys[-1], 0], [-0.6, ys[-1] + 1.3, 0]], C_BAD, 5), tx("скачок", 24, C_BAD).move_to([0.5, 1.0, 0]), Arrow([1.0, 0.4, 0], [2.2, 0.4, 0], buff=0).set_color(WHITE),
                  curve_of(lambda x: 1.3 / (1 + np.exp(-9 * x)), -0.6, 0.6, -0.3, C_SUM, 5, 30).move_to([3.4, 0.4, 0]), tx("быстрое непрерывное движение (Маркус)", 22, C_SUM).move_to([1.8, -1.3, 0]), c="скачок как быстрое непрерывное движение")
        self.show(big_bar(0, -1.5, 2.6, 1.6, 0.4, 0.0), lock(1.9, 0.5, C_SUM), tx("открыт", 22, C_SUM).move_to([1.9, -0.1, 0]), pill("в среднем 0 — как раньше", C_SUM, 24).move_to([0, 2.2, 0]),
                  tx("Скороход, Маллявэн", 22, WHITE).move_to([0, -2.2, 0]), c="столбик знает будущее, сумма остаётся честной")
        j2, xs2, ys2 = noise(-5, 1.0, 0.0, 0.25, 40, 43, C_NOISE, 4)
        self.show(j2, line([-5, -0.9, 0], [1.0, -0.9, 0], C_PRICE, 6), bar_w(1.0, 0.7, 1.4, -1.6, C_BET), tx("высота зависит от всей истории (Конт, Фурнье)", 24, C_BET).move_to([0, 2.2, 0]), c="высота — от всей истории линии")
        fam = RoundedRectangle(width=7.0, height=2.6, corner_radius=0.3).set_stroke(C_NOISE, 3).move_to([-1.0, 0.5, 0])
        self.show(fam, tx("шумы, по которым можно считать", 24, C_NOISE).move_to([-1.0, 0.5, 0]), cross(C_BAD, 0.45).move_to([4.6, 0.5, 0]), tx("шире нельзя (Бихтелер, Деллашери)", 24, C_BAD).move_to([0, -1.5, 0]), c="граница: шире шумы — счёта нет")


class A22(Film):
    def construct(self):
        N = 5
        hs = np.linspace(0, H, N + 1)
        xk = lambda h: 5.0 * np.sqrt(max(0.0, 1 - h / H))
        layers = lambda col, op: VGroup(*[Rectangle(width=2 * xk(hs[k]), height=hs[k + 1] - hs[k]).set_stroke(col, 2).set_fill(col, op).move_to([0, AY + (hs[k] + hs[k + 1]) / 2, 0]) for k in range(N)])
        self.show(axis_(), hill(C_PRICE, 3), layers(C_BET, 0.35), tx("сложить слои — как?", 30, C_ADD).move_to([0, 2.6, 0]), c="пункт про сложение")
        a = Square(side_length=1.2).set_stroke(C_BET, 3).set_fill(C_BET, 0.3).move_to([-3.0, 0.4, 0]); b = Square(side_length=1.2).set_stroke(C_AXIS, 3).set_fill(C_AXIS, 0.3).move_to([-1.2, 0.4, 0])
        u = Rectangle(width=3.0, height=1.2).set_stroke(C_ADD, 3).move_to([3.0, 0.4, 0])
        self.show(a, b, tx("+", 40, WHITE).move_to([-2.1, 0.4, 0]), tx("≠", 60, C_BAD).move_to([0.9, 0.4, 0]), u, tx("целое", 24, C_ADD).move_to([3.0, 0.4, 0]), tx("выбор по нескольким критериям", 24, WHITE).move_to([0, 2.2, 0]),
                  c="целое бывает не равно сумме частей")
        self.show(axis_(), hill(C_PRICE, 3), layers(C_ADD, 0.3), tx("особая мера слоя: интегралы Шоке и Сугено", 26, C_ADD).move_to([0, 2.6, 0]), c="слои измеряют особой мерой")
        shape = VGroup(Rectangle(width=4.0, height=2.0).set_stroke(C_ADD, 3).set_fill(C_ADD, 0.2), Circle(radius=0.4).set_stroke(C_BAD, 3).set_fill("#0f1115", 1).shift(LEFT * 0.9), Circle(radius=0.4).set_stroke(C_BAD, 3).set_fill("#0f1115", 1).shift(RIGHT * 0.9))
        self.show(shape.move_to([-2.4, 0.4, 0]), tx("куски − дыры", 28, C_ADD).move_to([-2.4, -1.2, 0]), tx("эйлерова характеристика", 24, WHITE).move_to([-2.4, 2.0, 0]),
                  *[Dot([x, y, 0], radius=0.12).set_color(C_SUM) for x, y in ((2.2, 1.0), (3.6, 0.2), (4.8, 1.2))], tx("считаем цели, которые видят датчики", 22, C_SUM).move_to([3.6, -0.8, 0]), c="эйлерова характеристика считает куски минус дыры")
        self.show(*[portrait(n, "", WHITE, 0.9).move_to([x, 1.2, 0]) for n, x in (("Концевич", -4.0), ("Денеф", -1.3), ("Лёзер", 1.4))], plaque("1995–98", "мера на пространстве кривых", WHITE, 0, -1.0), c="мера на пространстве кривых")


class A23(Film):
    def construct(self):
        self.show(*[pill(t, col, 26).move_to([x, 0.6, 0]) for t, col, x in (("память", C_ADD, -4.2), ("произведение", C_ADD, 0.0), ("шкала времени", C_ADD, 4.2))], tx("другие сложения", 34, WHITE).move_to([0, 2.4, 0]), c="совсем другие сложения")
        bs = VGroup(*[Rectangle(width=0.8, height=1.4).set_stroke(C_ADD, 2).set_fill(C_ADD, 0.15 + 0.1 * i).move_to([-3.5 + i * 1.0, -0.8, 0]) for i in range(8)])
        self.show(bs, tx("недавнее прошлое весит больше далёкого", 24, WHITE).move_to([0, 1.4, 0]), tx("дробный интеграл", 26, C_ADD).move_to([0, 2.4, 0]), c="дробный интеграл — сумма с памятью")
        self.show(*[Rectangle(width=1.0, height=1.2).set_stroke(C_BET, 2).set_fill(C_BET, 0.3).move_to([-4.0 + i * 2.0, 0.2, 0]) for i in range(5)],
                  *[tx("×", 40, C_ADD).move_to([-3.0 + i * 2.0, 0.2, 0]) for i in range(4)], plaque("1887", "Вольтерра", WHITE, 0, 2.5), c="Вольтерра перемножал столбики")
        tl = VGroup(line([-5.0, 0.0, 0], [-0.5, 0.0, 0], C_ADD, 6), *[Dot([x, 0.0, 0], radius=0.1).set_color(C_ADD) for x in (1.0, 2.0, 3.2, 4.0, 5.0)])
        self.show(tl, tx("сплошная ось", 22, C_ADD).move_to([-2.7, -0.6, 0]), tx("отдельные точки", 22, C_ADD).move_to([3.0, -0.6, 0]), plaque("1988", "Хильгер", WHITE, 0, 2.5), c="шкала времени — и сплошная, и из точек")


# ============================== объёмные сцены (закон 26): только слои-этажи и дерево ==============================
Base3D = story_base3d(P.STATIONS, P.SCENES, ICONS, N.TEXT, HERE)
DEP = 2.2                      # глубина холма (ось y)


def ridge():
    """Холм как объём без полупрозрачной поверхности: светящаяся передняя и задняя кромки и рёбра между ними. Вид спереди совпадает с плоским холмом."""
    edge = ParametricCurve(lambda t: np.array([t, 0.0, F(t)]), t_range=(XL, XR, 0.05)).set_stroke(C_PRICE, 9)
    back = ParametricCurve(lambda t: np.array([t, DEP, F(t)]), t_range=(XL, XR, 0.05)).set_stroke(C_PRICE, 4)
    ribs = VGroup(*[Line([x, 0, F(x)], [x, DEP, F(x)]).set_stroke(C_PRICE, 3) for x in np.linspace(XL, XR, 9)])
    return ribs, edge, back


def axis3():
    ax = Line([-5.8, 0, 0], [5.8, 0, 0]).set_stroke(C_AXIS, 10)
    grid = VGroup(*[Line([x, 0, 0], [x, DEP, 0]).set_stroke(C_NOTE, 1.5) for x in np.linspace(XL, XR, 11)],
                  *[Line([XL, y, 0], [XR, y, 0]).set_stroke(C_NOTE, 1.5) for y in np.linspace(0, DEP, 4)])
    return ax, grid


def tower(x0, x1, h, color=C_BET):
    p = Prism(width=x1 - x0 - 0.08, height=DEP, depth=h - 0.04)
    p.set_color(color).set_opacity(1).set_shading(0.2, 0.2, 0.15)
    p.move_to([(x0 + x1) / 2, DEP / 2, h / 2])
    return p


def towers(n, color=C_BET):
    xs = np.linspace(XL, XR, n + 1)
    return Group(*[tower(xs[i], xs[i + 1], F((xs[i] + xs[i + 1]) / 2), color) for i in range(n)])


def plate(w, h0, h1, color):
    p = Prism(width=w, height=DEP, depth=h1 - h0 - 0.08)
    p.set_color(color).set_opacity(1).set_shading(0.2, 0.2, 0.15)
    p.move_to([0, DEP / 2, (h0 + h1) / 2])
    return p


class Film3D(OverlayMixin, Base3D):
    """Объёмная сцена: вид спереди (theta=0, phi=90, центр z=1,5, высота 8) совпадает с плоской сценой. Вход и выход без провала яркости:
    объёмные объекты добавляются мгновенно под плоскими такого же вида, и плоские гаснут; на выходе наоборот."""
    def setup(self):
        super().setup()
        self.camera.background_rgba = [0, 0, 0, 1]
        self.camera.light_source.move_to([-6, -8, 12])
        self._k, self._capm, self._ovp = 0, None, {}
        self.frame.reorient(0, 90).move_to([0, 0, 1.5]).set_height(8)
        i = ORDER.index(type(self).__name__)
        prev = ORDER[i - 1]
        p = _dry(prev)
        self._old = []
        for m in p._cur:
            self._pin(m)
            self._old.append(m)
        if p._capm is not None:
            self._capm = self._pin(p._capm)
        self._ovp = ov_parts(prev, p._k)
        for _, m in self._ovp.values():
            self._pin(m)

    def _pin(self, m):
        m.fix_in_frame()
        m.set_z_index(100)
        self.add(m, set_depth_test=False)
        return m

    def phrase(self, k, c=None, rt=0.6):
        """Начало кадра фразы k: старая подпись гаснет, сквозные сущности меняются по частям, потом появляется новая подпись."""
        self._k = k
        self.beat(k - 1)
        code = type(self).__name__
        if self._capm is not None:
            self.play(FadeOut(self._capm), run_time=0.25)
            self._capm = None
        anims = self._ov_anims(code, k, pin=True)
        if anims:
            self.play(*anims, run_time=rt)
        if c:
            new = cap(c).fix_in_frame().set_z_index(100)
            self.play(FadeIn(new), run_time=0.3)
            self._capm = new

    def enter(self, objs3d, rt=0.9):
        self.add(*objs3d)
        self.play(*[FadeOut(m) for m in self._old], run_time=rt)
        self._old = []

    def leave(self, objs3d, rt=0.9):
        flat = [_bright(m).fix_in_frame().set_z_index(100) for m in self.end2d()]
        self.play(self.frame.animate.reorient(0, 90).move_to([0, 0, 1.5]).set_height(8), run_time=1.6)
        self.add(*flat, set_depth_test=False)
        self.play(*[FadeOut(o) for o in objs3d], run_time=rt)

    def cam(self, theta, phi, rt=3.0, center=(0, 0.8, 1.6), height=10.5):
        self.play(self.frame.animate.reorient(theta, phi).move_to(list(center)).set_height(height), run_time=rt, rate_func=smooth)


class A12(Film3D):
    """Лебег: холм режется на этажи; под этажом на оси остаётся след."""
    END_K, END_CAP = 5, "сложим слои — снова площадь холма"

    def end2d(self):
        return [hill(), axis_()]

    def construct(self):
        ribs, edge, back = ridge()
        ax, grid = axis3()
        N = 6
        hs = np.linspace(0, H, N + 1)
        xk = lambda h: 5.0 * np.sqrt(max(0.0, 1 - h / H))
        cols = [C_BET, C_AXIS, C_ADD, C_NOISE, C_PRICE, C_SUM]
        plates = Group(*[plate(2 * xk(hs[k]), hs[k], hs[k + 1], cols[k]) for k in range(N)])
        tick = VGroup(vaxis(), *[line([-5.8, AY + h, 0], [-5.5, AY + h, 0], C_BET, 3) for h in hs], plaque("1902", "Лебег", WHITE, 3.0, 2.65).scale(0.9)).fix_in_frame()
        self.phrase(1, "начнём с высоты")
        self.enter([edge, back, ribs, ax, grid])
        self.play(FadeIn(tick), run_time=0.6)
        self.phrase(2, "горизонтальные слои, как этажи")
        self.play(FadeOut(tick), FadeOut(ribs), LaggedStart(*[FadeIn(p) for p in plates], lag_ratio=0.15), self.frame.animate.reorient(-14, 66).move_to([0, 1.0, 1.4]).set_height(10.5), run_time=2.5)
        k = 2
        mark = Line([-xk(hs[k]), -0.2, 0], [xk(hs[k]), -0.2, 0]).set_stroke(C_AXIS, 14)
        self.phrase(3, "часть оси под слоем — где график достаёт до этой высоты")
        self.play(ShowCreation(mark), Indicate(plates[k], scale_factor=1.04), self.frame.animate.reorient(-26, 60), run_time=2.5)
        w = 2 * xk(hs[k])
        self.phrase(4, "площадь слоя")
        lab = VGroup(dim_h(-w / 2, w / 2, AY - 0.55, "длина части оси", C_AXIS, 22), dim_v(w / 2 + 0.3, AY + hs[k], AY + hs[k + 1], "высота слоя", C_BET, 22),
                     tx("площадь слоя = высота слоя × длина части оси", 28, WHITE).move_to([0, 2.6, 0])).fix_in_frame().set_z_index(100)
        self.play(self.frame.animate.reorient(0, 90).move_to([0, 0, 1.5]).set_height(8), FadeIn(lab), run_time=2.0)
        self.phrase(5, "сложим слои — снова площадь холма")
        shadows = VGroup(*[Line([-xk(hs[j]), -0.2, 0], [xk(hs[j]), -0.2, 0]).set_stroke(cols[j], 14) for j in range(N)])
        self.play(FadeOut(lab), self.frame.animate.reorient(-24, 60).move_to([0, 1.0, 1.8]).set_height(10.5), run_time=1.5)
        self.play(*[p.animate.shift(OUT * 0.5 * j) for j, p in enumerate(plates)], FadeOut(mark), ShowCreation(shadows), run_time=2.5)
        self.play(*[p.animate.shift(IN * 0.5 * j) for j, p in enumerate(plates)], run_time=1.5)
        self.leave([plates, ax, grid, shadows, edge, back])


class A13(Film3D):
    """Два слоя на прыгающем графике: единицы на верхней плите, нули на нижней; сверху пыль точек без длины."""
    END_K, END_CAP = 6, "договор выполнен: счётчики сходятся"

    def end2d(self):
        d, _, _ = jump()
        return [d, axis_(), one_zero_marks()]

    def construct(self):
        ax, grid = axis3()
        d2, xs, up = jump()
        dots = Group(*[Sphere(radius=0.15).set_color(C_PRICE if u else WHITE).set_shading(0.1, 0.1, 0.0).move_to([x, 0.6, 2.0 if u else 0.0]) for x, u in zip(xs, up)])
        s1 = Prism(width=11.6, height=DEP, depth=0.4).set_color(C_BET).set_opacity(1).set_shading(0.2, 0.2, 0.1).move_to([0, DEP / 2, 1.55])
        s0 = Prism(width=11.6, height=DEP, depth=0.4).set_color(C_NOTE).set_opacity(1).set_shading(0.2, 0.2, 0.1).move_to([0, DEP / 2, -0.45])
        self.phrase(1, "применим слои к прыгающему графику")
        self.enter([ax, grid, dots])
        self.phrase(2, "слоёв всего два")
        self.play(FadeIn(s1), FadeIn(s0), self.frame.animate.reorient(-18, 64).move_to([0, 1.0, 1.4]).set_height(8.6), run_time=2.5)
        self.phrase(3, "каждая точка — в свой слой")
        ones = [d for d, u in zip(dots, up) if u]
        self.play(*[Indicate(d, scale_factor=1.5, color=C_BET) for d in ones[:10]], run_time=2.0)
        self.phrase(4, "такие точки можно выписать списком — длины у них нет")
        proj = VGroup(*[Line([x, 0.6, 2.0], [x, 0.6, 0.0]).set_stroke(C_BET, 2) for x, u in zip(xs, up) if u])
        self.play(ShowCreation(proj), self.frame.animate.reorient(-6, 78).move_to([0, 1.0, 1.0]).set_height(8.0), run_time=2.0)
        lab = tx("длина такой россыпи = 0", 30, C_AXIS).move_to([0, 2.4, 0]).fix_in_frame().set_z_index(100)
        self.play(FadeIn(lab), run_time=0.8)
        self.phrase(5, "сумма равна нулю при любом счёте")
        t = VGroup(tx("слой единицы: 1 × 0 = 0", 28, C_BET), tx("слой нуля: 0 × вся ось = 0", 28, WHITE), tx("сумма = 0", 36, C_SUM)).arrange(DOWN, buff=0.2).move_to([0, 2.3, 0]).fix_in_frame().set_z_index(100)
        self.play(FadeOut(lab), FadeIn(t), run_time=1.2)
        self.phrase(6, "договор выполнен: счётчики сходятся")
        self.play(FadeOut(t), FadeOut(proj), self.frame.animate.reorient(-10, 70), run_time=2.0)
        self.leave([ax, grid, dots, s1, s0])


class A24(Film3D):
    """Итог: холм и башни превращаются в дерево; камера разворачивает его в плоский вид."""
    END_K, END_CAP = 4, "какой способ взять, зависит от задачи"

    def end2d(self):
        return [pill("гладкая ширина — Риман", C_BET, 28).move_to([-3.4, 0.9, 0]), pill("случайная — Ито", C_NOISE, 28).move_to([3.4, 0.9, 0]),
                tx("а дальше — смотря какая задача", 34, WHITE).move_to([0, -0.7, 0])]

    def construct(self):
        ribs, edge, back = ridge()
        ax, grid = axis3()
        t12 = towers(12)
        q = VGroup(tx("Как посчитать площадь так, чтобы ответ", 32), tx("не зависел от способа счёта?", 32)).arrange(DOWN, buff=0.15).move_to([0, 2.7, 0]).fix_in_frame().set_z_index(100)
        self.phrase(1, "возвращаемся к вопросу")
        self.enter([edge, back, ax, grid, t12])
        self.play(FadeIn(q), self.frame.animate.reorient(-14, 66).move_to([0, 1.0, 1.4]).set_height(10.0), run_time=2.0)
        top = np.array([0.0, DEP / 2, F(0.0)])
        tips = [(-4.2, C_PRICE), (-1.4, C_AXIS), (1.4, C_BET), (4.2, C_ADD)]
        trunk = Line(top, top + OUT * 1.0).set_stroke(C_SUM, 18)
        base = top + OUT * 1.0
        branches = Group(*[Line(base, np.array([x, DEP / 2, F(0.0) + 3.4])).set_stroke(c, 12) for x, c in tips])
        balls = Group(*[Sphere(radius=0.28).set_color(c).set_shading(0.1, 0.1, 0.0).move_to([x, DEP / 2, F(0.0) + 3.4]) for x, c in tips])
        self.phrase(2, "единого способа нет — договор переписывали по пунктам")
        self.play(FadeOut(q), FadeOut(t12), ShowCreation(trunk), self.frame.animate.reorient(-20, 70).move_to([0, 1.0, 3.2]).set_height(10.5), run_time=2.0)
        self.play(LaggedStart(*[ShowCreation(b) for b in branches], lag_ratio=0.2), run_time=1.6)
        self.play(LaggedStart(*[GrowFromCenter(b) for b in balls], lag_ratio=0.2), run_time=1.2)
        names = ["график: слои, приближения", "ось: вес, шум, подсказка", "высота: левый край, середина", "сложение: другие меры"]
        self.phrase(3, "четыре пункта — четыре ветви")
        self.play(self.frame.animate.reorient(0, 90).move_to([0, 0, 3.2]).set_height(8), run_time=2.0)
        labs = VGroup(*[node(n, x, 2.55, c, 3.1).scale(0.8) for n, (x, c) in zip(names, tips)]).fix_in_frame().set_z_index(100)
        self.play(FadeIn(labs), run_time=1.0)
        fin = [_bright(m).fix_in_frame().set_z_index(100) for m in self.end2d()]
        self.phrase(4, "какой способ взять, зависит от задачи")
        self.add(*fin, set_depth_test=False)
        self.play(*[FadeIn(m) for m in fin], run_time=1.0)
