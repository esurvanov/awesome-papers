"""Сцены нового ролика — ШАБЛОН (папка core/templates/paper копируется в papers/<arxiv-id>-<слово>/).
Основа — core/manimkit/film.py (кадр = фраза, превращения по меткам, точный синхрон, начало с последнего кадра прошлой сцены, проверка
наложений), помощники кадра — core/manimkit/annot.py (стрелки на выносных, подпись с плашкой, порядок слоёв, связка панелей).
Мир этого ролика (свои фигуры, числа из рисунка) — в world.py рядом. Правила кадра — PLAYBOOK, законы 22–35.
Кадр сцены: uv run manimgl papers/<папка>/scenes.py A01 -w -l  ·  весь ролик: uv run python core/pipeline/build.py papers/<папка>"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(HERE))
from manimlib import *
from manimkit import *
from manimkit.annot import *
from manimkit.film import film_base
import passport as P
import narration as N

ICONS = {}  # {"Станция": функция(масштаб) → VGroup} — значки полосы «мы здесь»
Film, Film3D = film_base(P.STATIONS, P.SCENES, ICONS, N.TEXT, HERE)


class A01(Film):
    """Один вызов self.show на каждую фразу TEXT["A01"]; объект, который продолжается в следующем кадре, — с одной меткой tagged(m, "имя")."""
    def construct(self):
        q = label("Вопрос ролика", [0, 1.5, 0], size=40)
        self.show(tagged(q, "question"), c="о чём ролик")


class A02(Film):
    def construct(self):
        self.show(tagged(label("Вопрос ролика", [0, 2.6, 0], size=30), "question"), pill("ставка: почему это интересно").move_to([0, 0.5, 0]), c="ставка")


class A03(Film):
    def construct(self):
        self.show(label("Мир", [0, 1.0, 0], size=36), c="одна мысль сцены")
