"""Общее для роликов по паспорту: полоса «мы здесь», подпись над ней, базовая сцена со станцией."""

__all__ = ["story_bar", "note", "story_base"]  # не отдавать наружу имена manimlib — они перекрывают значки из style (cross)
import os
import numpy as np
from manimlib import *
from .style import tx, Base, C_GREY


def story_bar(stations, active, color_note=C_GREY):
    """Полоса «мы здесь»: пройденные станции — серые, текущая — белая, будущие — тусклые."""
    xs = np.linspace(-6.0, 6.0, len(stations))
    y = -3.62
    g = VGroup(Line([xs[0], y, 0], [xs[-1], y, 0]).set_stroke(color_note, 1, opacity=0.4))
    for i, (x, name) in enumerate(zip(xs, stations)):
        col, op = (WHITE, 1.0) if i == active else (color_note, 0.9 if i < active else 0.35)
        g.add(Dot([x, y, 0], radius=0.07 if i != active else 0.1).set_color(col).set_opacity(op))
        g.add(tx(name, 16, col).set_opacity(op).move_to([x, y - 0.24, 0]))
    return g


def note(s, color=C_GREY, y=-3.05):
    """Подпись внизу кадра — над полосой «мы здесь»."""
    return tx(s, 26, color).move_to(DOWN * (-y))


def story_base(stations, scenes):
    """Базовая сцена ролика по паспорту: темп из переменной SLOW (сборщик подгоняет под речь) и полоса «мы здесь».
    Использование: Base = story_base(P.STATIONS, P.SCENES)."""
    station_of = {code: st for code, st, *_ in scenes}

    class StoryBase(Base):
        SLOW = float(os.environ.get("SLOW", 1.6))

        def setup(self):
            super().setup()
            code = type(self).__name__
            if code in station_of:
                self.add(story_bar(stations, stations.index(station_of[code])))

    return StoryBase
