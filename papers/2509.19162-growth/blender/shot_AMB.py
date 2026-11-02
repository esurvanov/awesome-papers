"""Фон сцен с инфографикой (A07–A16, приложение): та же станция живёт своей жизнью — длинный состав идёт по главному пути,
второй навстречу по пути 2, камера медленно облетает станцию по кругу. Один ролик на 120 с; compose.py --ambient берёт из него
куски с разных мест, размывает и кладёт под кадры раскадровки."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import film as F
import station as S

args = sys.argv[sys.argv.index("--") + 1:]
out, draft = args[0], "--draft" in args
L = 120.0
SP = S.TRACK_SPACING

S.setup(samples=24)
S.ground()
S.yard()
S.scenery()
S.nature()
kinds = ["серый", "рок", "синий", "цистерна", "хром", "платформа"]


def train(n, x0, y, dx, name):
    cars = [S.place(S.model(S.LOCO, 20.0, name=f"{name}_loco"), x0 + 18.0 * (1 if dx > 0 else -1), y)]
    for k in range(n):
        kind = kinds[(k + len(name)) % len(kinds)]
        size = 15.0 if kind in ("цистерна", "хром", "платформа") else 14.0
        cars.append(S.place(S.model(S.WAGONS[kind], size, name=f"{name}{k}"), x0 - k * 15.5 * (1 if dx > 0 else -1), y))
    for c in cars:
        x = c.location.x
        S.drive(c, S.path((x, y), (x + dx, y)), 0.0, L)
    return cars


a = train(10, -160.0, 0.0, 260.0, "a")
b = train(7, 170.0, -2 * SP, -220.0, "b")
bad = S.collisions(a + b, L, step=24)
if bad:
    print("СТОЛКНОВЕНИЯ:\n  " + "\n  ".join(bad[:20]))
    raise SystemExit(1)
cam = S.camera((0, -120, 40), (0, -6, 0), lens=30, dof=60)
for k in range(13):  # облёт по кругу: ключ каждые 10 с
    t = L * k / 12
    ang = -math.pi / 2 + 2 * math.pi * k / 12
    F.cam_at(cam, t, (130 * math.cos(ang), 100 * math.sin(ang) - 6, 38 + 8 * math.sin(2 * ang)), (0, -6, 2), lens=30)
F.finish(out, L, draft)
print(f"СЦЕНА AMB готова: {out}")
