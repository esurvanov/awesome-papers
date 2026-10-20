"""Сцены нового ролика — ШАБЛОН (папка core/templates/paper копируется в papers/<arxiv-id>-<слово>/).
Паспорт — passport.py рядом; порядок работы — PLAYBOOK.md в корне.
Кадр сцены: uv run manimgl papers/<папка>/scenes.py A01 -s -w   ·   весь ролик: uv run python core/pipeline/build.py papers/<папка>"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())  # корень репозитория, откуда бы ни лежал файл
sys.path.insert(0, str(ROOT / "core"))  # общая часть: manimkit
sys.path.insert(0, str(HERE))           # своя часть статьи: паспорт, текст, модели
from manimlib import *
from manimkit import *
import passport as P

Base = story_base(P.STATIONS, P.SCENES)  # темп под речь + полоса «мы здесь»

C_A = "#58a6ff"     # смысловые имена цветов — как в паспорте COLORS
C_NOTE = "#8b949e"


class A01(Base):
    """О чём ролик, вопрос и ставка."""
    def construct(self):
        q = tx("Вопрос ролика", 44).to_edge(UP, buff=0.5)
        self.play(Write(q), run_time=1.5)
        self.play(FadeIn(pill("ставка: почему это интересно", C_A, 26).move_to(DOWN * 2.6)))
        self.wait(2)


class A02(Base):
    """Карточка статьи."""
    def construct(self):
        card = VGroup(tx("arXiv XXXX.XXXXX · дата", 22, C_NOTE), tx("Название статьи", 30), tx("Авторы", 24)).arrange(DOWN, buff=0.3)
        self.play(FadeIn(card))
        self.wait(2)


class A03(Base):
    """…"""
    def construct(self):
        self.add(head("Мир"))
        self.play(FadeIn(note("одна мысль сцены")))
        self.wait(2)
