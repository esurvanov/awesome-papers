"""Модель Шеррингтона–Киркпатрика на малых системах: перебор состояний и рисование сети связей."""
import math
import numpy as np
from manimlib import *
from manimkit.style import *


def all_states(n):
    return np.array([[1 if (k >> i) & 1 else -1 for i in range(n)] for k in range(2 ** n)], dtype=float)


def free_energy(J, n, S, pairs):
    H = np.zeros(len(S))
    for (i, j), w in zip(pairs, J):
        H += w * S[:, i] * S[:, j] / math.sqrt(n)
    m = H.max()
    return (math.log(np.exp(H - m).sum()) + m) / n


def ring(n, r, center=ORIGIN):
    return [center + r * np.array([math.cos(2 * math.pi * k / n + math.pi / 2),
                                   math.sin(2 * math.pi * k / n + math.pi / 2), 0]) for k in range(n)]


def network(J, n, pairs, r, center=ORIGIN, scale=1.0):
    pts = ring(n, r, center)
    lines = VGroup()
    for (i, j), w in zip(pairs, J):
        l = Line(pts[i], pts[j])
        l.set_stroke(C_GREEN if w > 0 else C_RED, min(1 + 3.2 * abs(w) * scale, 7), opacity=0.75)
        lines.add(l)
    dots = VGroup(*[Dot(p, radius=0.09, color=WHITE) for p in pts])
    return lines, dots
