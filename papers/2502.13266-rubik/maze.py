"""Модель лабиринта для сцен: небольшой граф «комнат» по слоям расстояния до выхода, без manimlib.
Всё детерминировано (фиксированное зерно), чтобы каждая сцена рисовала один и тот же лабиринт.
Лабиринт — иллюстрация: настоящий граф кубика огромен, здесь важны только его свойства — двери, выход, расстояние."""
import random
from collections import deque

LAYERS = [1, 3, 4, 5, 5, 5, 4]   # сколько комнат на каждом расстоянии от выхода
X0, DX = -5.6, 1.45              # выход слева, дальше слои вправо
Y_SPAN = 4.4                     # высота, по которой разложен слой
Y_MID = 0.15


def build(seed=7):
    rnd = random.Random(seed)
    pos, layer = [], []
    for d, n in enumerate(LAYERS):
        for i in range(n):
            y = Y_MID if n == 1 else Y_MID + Y_SPAN / 2 - i * Y_SPAN / (n - 1)
            jx = 0 if d == 0 else rnd.uniform(-0.22, 0.22)
            jy = 0 if n == 1 else rnd.uniform(-0.18, 0.18)
            pos.append((X0 + d * DX + jx, y + jy))
            layer.append(d)
    ids = {d: [k for k, l in enumerate(layer) if l == d] for d in range(len(LAYERS))}
    edges = set()
    for d in range(1, len(LAYERS)):
        for k in ids[d]:
            prev = sorted(ids[d - 1], key=lambda j: abs(pos[j][1] - pos[k][1]))
            edges.add(tuple(sorted((k, prev[0]))))
            if len(prev) > 1 and rnd.random() < 0.45:
                edges.add(tuple(sorted((k, prev[1]))))
        same = ids[d]
        for a, b in zip(same, same[1:]):
            if rnd.random() < 0.5:
                edges.add(tuple(sorted((a, b))))
    return pos, layer, sorted(edges)


POS, LAYER, EDGES = build()
EXIT = 0
NB = {k: set() for k in range(len(POS))}
for a, b in EDGES:
    NB[a].add(b)
    NB[b].add(a)


def dist_from(src):
    d = {src: 0}
    q = deque([src])
    while q:
        v = q.popleft()
        for w in NB[v]:
            if w not in d:
                d[w] = d[v] + 1
                q.append(w)
    return d


DIST = dist_from(EXIT)  # настоящее расстояние до выхода


def estimate(seed=1, errors=(0, 0, 1, 1, 2)):
    """Оценка компаса: настоящее расстояние плюс ошибка в большую сторону — как в статье: прогулка петляет,
    и ходов в ней не меньше, чем на кратчайшем пути."""
    rnd = random.Random(seed)
    return {k: (0 if k == EXIT else max(1, DIST[k] + rnd.choice(errors))) for k in range(len(POS))}


ROUGH = (0, 1, 2, 3, 4)        # ошибки компасов отряда — грубее, чтобы пути разошлись
SQUAD = [21, 8, 0]             # зёрна трёх компасов отряда: пути 8, 7 и 6 ходов
WIDTH_DEMO = 124               # компас для сцены «ширина фронта»: ширина 1 — тупик, 2 — путь 7, 3 — путь 6 ходов


def walk(seed=3, steps=7):
    """Случайная прогулка от выхода без шага назад."""
    rnd = random.Random(seed)
    path = [EXIT]
    while len(path) <= steps:
        opts = [w for w in NB[path[-1]] if len(path) < 2 or w != path[-2]]
        path.append(rnd.choice(sorted(opts)))
    return path


def beam(start, est, width=3, max_steps=20):
    """Поиск фронтом: шаги — список (соседи, оставленные); в конце — путь к выходу по родителям."""
    parent = {start: None}
    front = [start]
    steps = []
    for _ in range(max_steps):
        nbrs = []
        for v in front:
            for w in sorted(NB[v]):
                if w not in parent:
                    parent[w] = v
                    nbrs.append(w)
        if not nbrs:
            break
        if EXIT in nbrs:
            steps.append((nbrs, [EXIT]))
            break
        keep = sorted(nbrs, key=lambda w: (est[w], w))[:width]
        steps.append((nbrs, keep))
        front = keep
    path = [EXIT]
    while parent.get(path[-1]) is not None:
        path.append(parent[path[-1]])
    return steps, path[::-1] if path[-1] == start else None


START = max(range(len(POS)), key=lambda k: (DIST[k], -abs(POS[k][1] - Y_MID)))


if __name__ == "__main__":
    print("комнат", len(POS), "дверей", len(EDGES), "старт", START, "расстояние", DIST[START])
    for s in (1, 2, 4):
        st, p = beam(START, estimate(s))
        print("компас", s, "шагов фронта", len(st), "путь", p, "длина", len(p) - 1 if p else None)
    for s in SQUAD:
        st, p = beam(START, estimate(s, ROUGH), width=2)
        print("отряд", s, len(p) - 1)
    print("прогулка", walk(), [DIST[k] for k in walk()])
