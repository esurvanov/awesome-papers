"""Сценарий ролика в Markdown — собирается из паспорта и текста диктора (единый источник, руками не править).
Запуск (из корня): uv run python core/pipeline/make_scenario.py papers/<папка-статьи>  →  scenario.md в папке статьи"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # корень репозитория
import importlib

PAPER = (ROOT / (sys.argv[1] if len(sys.argv) > 1 else "papers/2610.23637-relation-gap")).resolve()
NAME = PAPER.name
sys.path.insert(0, str(PAPER))
P = importlib.import_module("passport")
N = importlib.import_module("narration")

ICON = {"map": "🗺", "ref": "📜", "formal": "📐", "practice": "🛠"}

out = [f"# Ролик «{getattr(P, 'TITLE', NAME)}» — сценарий", "",
       f"Статья: {getattr(P, 'PAPER', '—')}.",
       "Собрано из паспорта `passport.py` и текста диктора `narration.py` этой папки — руками не править.", "",
       f"**Главный вопрос:** {P.QUESTION}", ""]
if getattr(P, "PITCH", ""):
    out += [f"**Задача мира (20 с, без терминов):** {P.PITCH}", ""]
if getattr(P, "RETELL", []):
    out += ["**Пересказ зрителя после ролика:**", ""] + [f"{i}. {x}" for i, x in enumerate(P.RETELL, 1)] + [""]
if getattr(P, "IDEA", ""):
    out += [f"**Общая идея:** {P.IDEA}", ""]
if getattr(P, "LEVERS", {}):
    out += ["**Пункты договора (рычаги):**", ""] + [f"- **{k}** — {v}" for k, v in P.LEVERS.items()] + [""]
if getattr(P, "ENTITIES", {}):
    out += ["## Сквозные сущности", "", "| Сущность | Как выглядит | Видна в сценах |", "|---|---|---|"]
    out += [f"| {k} | {d} | {', '.join(sc)} |" for k, (d, sc) in P.ENTITIES.items()] + [""]
out += [
       "**Полоса «мы здесь»:** " + " → ".join(P.STATIONS), "",
       "## Законы сценария", ""] + [f"{i}. {x}" for i, x in enumerate(P.STORY_LAWS, 1)]
out += ["", "## Миры", ""] + [f"- {v}" for v in P.WORLDS.values()]
out += ["", "## Словарь — одно слово, один смысл", "", "| Слово | Смысл | Вводится |", "|---|---|---|"]
out += [f"| {w} | {m} | {intro} |" for w, (m, intro, *_) in P.WORDS.items()]
out += ["", "**Не произносим и не выводим:** " + ", ".join(f"«{k}»" for k in P.BANNED), "",
        "## Палитра — один цвет, один смысл", ""] + [f"- `{k}` {v}" for k, v in P.COLORS.items()]
out += ["", "**Старшинство при конфликте правил:** " + " → ".join(P.PRIORITY), "",
        "## Карта ролика", "", "| # | Сцена | Акт / станция | Мысль | Новые понятия |", "|---|---|---|---|---|"]
for i, (c, st, w, th, _) in enumerate(P.SCENES, 1):
    new = ", ".join(x for x, (_, intro, *_) in P.WORDS.items() if intro == c) or "—"
    out.append(f"| {i} | {c} | {ICON[w]} {st} | {th} | {new} |")
out += ["", "## Сцены", ""]
for i, (c, st, w, th, _) in enumerate(P.SCENES, 1):
    out += [f"### {i}. {c} · {ICON[w]} {st}", "", f"- **Мысль:** {th}"]
    for (a, b), (host, what) in P.JUNCTIONS.items():
        if host == c:
            out.append(f"- **Переходник:** {what}")
    board = getattr(P, "STORYBOARD", {}).get(c)
    if board:
        import re
        sents = [x for x in re.split(r"(?<=[.?!])\s+", N.TEXT[c].replace("\u0301", "").strip()) if x]
        out += ["", "| # | Фраза диктора | Что в кадре |", "|---|---|---|"]
        out += [f"| {k} | {t} | {board[k - 1] if k <= len(board) else '⚠ нет'} |" for k, t in enumerate(sents, 1)]
        out.append("")
    else:
        out += [f"- **Диктор:** {N.TEXT[c]}", ""]
if getattr(P, "LINKS", {}):
    out += ["## Стыки", "", "| Стык | Связка в тексте | Что сломалось → что чиним | В кадре: остаётся и меняется |", "|---|---|---|---|"]
    out += [f"| {a} → {b} | {x} | {y} | {z} |" for (a, b), (x, y, z) in P.LINKS.items()] + [""]
out += ["## Проверки", "", "**Программа** (`core/pipeline/check_passport.py`, обратное распознавание речи в `core/pipeline/build.py`):"]
out += [f"- {x}" for x in P.CHECKS_AUTO] + ["", "**Человек:**"] + [f"- {x}" for x in P.CHECKS_HUMAN]
out += ["", f"**Голос:** {P.VOICE['status']}; кандидаты — {', '.join(P.VOICE['candidates'])}; подача — {P.VOICE['style']}."]
(PAPER / "scenario.md").write_text("\n".join(out) + "\n")
print(f"сцен {len(P.SCENES)}, строк {len(out)}")
