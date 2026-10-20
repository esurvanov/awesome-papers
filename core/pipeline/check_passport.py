"""Проверка ролика против паспорта (passport.py в папке статьи) — то, что проверяется программой:
  • ружьё Чехова: слово паспорта не звучит и не показывается раньше сцены, где его ввели, и потом используется ещё хотя бы раз;
  • не больше двух новых понятий на сцену (кроме завязки — первой сцены);
  • стыки: каждая сцена начинается со связки («но», «поэтому»…) или подхватывает слово паспорта из предыдущей сцены;
  • запрещённые слова и знаки — в тексте диктора и на экране (кроме справки);
  • палитра: в сценах только цвета паспорта (по смысловым именам C_STEP, C_LIFT…);
  • смена мира — только через переходник; порядок сцен в тексте диктора совпадает с паспортом, у каждой сцены есть класс.
Понятно ли с первых секунд, о чём ролик, цельность рассказа и голос программа не проверяет — это сверка с человеком.
Запуск (из корня): uv run python core/pipeline/check_passport.py papers/<папка-статьи>"""
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # корень репозитория
import importlib

PAPER = (ROOT / (sys.argv[1] if len(sys.argv) > 1 else "papers/2610.23637-relation-gap")).resolve()
sys.path.insert(0, str(PAPER))
P = importlib.import_module("passport")
N = importlib.import_module("narration")


def screen_texts(src):
    """Строки, выводимые на экран в каждой сцене: строковые константы внутри класса, кроме описания класса."""
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.ClassDef) and node.name in {c for c, *_ in P.SCENES}:
            doc = ast.get_docstring(node)
            out[node.name] = " ".join(c.value for c in ast.walk(node)
                                      if isinstance(c, ast.Constant) and isinstance(c.value, str) and c.value != doc)
    return out


def has(word, text):
    return re.search(r"(?<![а-яё])(" + P.STEMS[word] + ")", text.lower()) is not None


def main():
    src = (PAPER / getattr(N, "SCENE_FILE", "scenes.py")).read_text()
    shown = screen_texts(src)
    order = [c for c, *_ in P.SCENES]
    world = {c: w for c, _, w, *_ in P.SCENES}
    pos = {c: i for i, c in enumerate(order)}
    errs = []

    if N.ORDER != order:
        errs.append("порядок сцен в тексте диктора не совпадает с паспортом")
    for c in order:
        if c not in shown:
            errs.append(f"{c}: нет класса сцены")
    for a, b in zip(order, order[1:]):
        if world[a] != world[b] and (a, b) not in P.JUNCTIONS:
            errs.append(f"{a}→{b}: смена мира без переходника")

    for word, (_, intro) in P.WORDS.items():
        used_after = False
        for c in order:
            for where, text in (("диктор", N.TEXT.get(c, "")), ("экран", shown.get(c, ""))):
                if has(word, text):
                    if pos[c] < pos[intro] and world[c] != "ref":  # справка цитирует название статьи как есть
                        errs.append(f"{c} [{where}]: «{word}» звучит раньше, чем введено (в {intro})")
                    elif pos[c] > pos[intro]:
                        used_after = True
        if not used_after:
            errs.append(f"«{word}»: введено в {intro} и больше не используется")

    for c in order[1:]:
        new = [w for w, (_, intro) in P.WORDS.items() if intro == c]
        if len(new) > 2:
            errs.append(f"{c}: {len(new)} новых понятия ({', '.join(new)}) — больше двух")

    for prev, c in zip(order, order[1:]):
        first = re.split(r"(?<=[.?!])\s", N.TEXT[c].strip())[0]
        starts = re.sub(r"[^а-яё ]", "", first.lower()).split()[:1]
        linked = starts and starts[0] in P.CONNECTORS
        linked = linked or any(has(w, first) and has(w, N.TEXT[prev]) for w in P.WORDS)
        if not linked:
            errs.append(f"{prev}→{c}: начало сцены не подхватывает предыдущую («{first[:50]}…»)")

    for c in order:
        if world[c] in getattr(P, "FREE_WORLDS", {"ref"}):
            continue
        for where, text in (("диктор", N.TEXT.get(c, "")), ("экран", shown.get(c, ""))):
            for name, rx in P.BANNED.items():
                if re.search(rx, text, flags=re.I):
                    errs.append(f"{c} [{where}]: запрещено «{name}»")

    for name in re.findall(r"\bC_(BLUE|GREEN|RED|YEL|GREY)\b", src):
        errs.append(f"цвет C_{name}: в сценах только смысловые цвета паспорта")
    for hx in set(re.findall(r'"(#[0-9a-fA-F]{6})"', src)):
        if hx not in P.COLORS:
            errs.append(f"цвет {hx} не из палитры паспорта")

    print("\n".join(errs) if errs else "Паспорт: всё сходится")
    print(f"сцен {len(order)}, миров {len(set(world.values()))}, понятий {len(P.WORDS)}, цветов {len(P.COLORS)}, нарушений {len(errs)}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
