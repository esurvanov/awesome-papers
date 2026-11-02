"""Проверка текста диктора до озвучки (PLAYBOOK, законы 27, 28, 32, 34): ударения по реестру, обыденная лексика, текст на слух.

Все проверки конечные: при нарушении озвучка не запускается (build.py вызывает check() перед синтезом).
Реестры — общие для всех роликов (core/lang/) и свои у ролика (papers/<папка>/), свои дополняют и перекрывают общие:
  • stress_registry.tsv — форма, форма с ударением, источники, статус (V2 — два словаря совпали, V1+rule, V1-frequent, YO, HOMOGRAPH —
    все чтения через «|»); новые формы проверяются по двум словарям и добавляются в общий реестр, чтобы второй раз не проверять;
  • lexicon.tsv — основа слова, статус (banned — книжное, запрещено; term:A07 — термин не раньше этой сцены), замена.
Запуск: uv run python core/pipeline/text_check.py papers/<папка>"""
import csv
import importlib
import re
import sys
from pathlib import Path

ACC = "́"
VOW = "аеёиоуыэюяАЕЁИОУЫЭЮЯ"
OK_STATUS = {"V2", "V1+rule", "V1-frequent", "YO", "HOMOGRAPH"}  # омограф: в реестре все чтения через «|», в тексте — нужное по контексту
LIMITS = {"phrase_words": 18, "scene_words": 80, "same_start_share": 0.6}


def words(text):
    return re.findall(r"[А-Яа-яЁё́]+(?:-[А-Яа-яЁё́]+)*", text)


def sentences(text):
    return [s for s in re.split(r"(?<=[.?!])\s+", text.replace(ACC, "").strip()) if s]


def load_registry(path):
    reg = {}
    if not path.exists():
        return reg
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            reg[row["form"].strip().lower()] = (row["stressed"].strip().lower(), row["status"].strip())
    return reg


def stress_errors(text_by_scene, reg):
    """Каждая форма с 2+ гласными: есть в реестре со статусом из OK_STATUS и знак в тексте совпадает с реестром."""
    errs = []
    for code, text in text_by_scene.items():
        for w in words(text):
            plain = w.replace(ACC, "").lower()
            nv = sum(ch in VOW for ch in plain)
            if nv < 2 or "ё" in plain:
                continue
            if plain not in reg:
                errs.append(f"{code}: «{plain}» нет в реестре ударений")
                continue
            want, status = reg[plain]
            if status not in OK_STATUS:
                errs.append(f"{code}: «{plain}» в реестре со статусом {status} — нужна проверка")
            elif w.lower() not in want.split("|"):
                errs.append(f"{code}: «{w.lower()}» — в реестре «{want}»")
    return errs


def load_lexicon(path):
    lex = []
    if not path.exists():
        return lex
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            lex.append((row["stem"].strip().lower(), row["status"].strip(), row.get("replace", "").strip()))
    return lex


def lexicon_errors(text_by_scene, lex, order):
    errs = []
    pos = {c: i for i, c in enumerate(order)}
    for code, text in text_by_scene.items():
        plain = text.replace(ACC, "").lower()
        for stem, status, rep in lex:
            rx = r"(?<![а-яё])" + stem
            if not re.search(rx, plain):
                continue
            if status == "banned":
                errs.append(f"{code}: необыденное «{stem}…» — замена: {rep}")
            elif status.startswith("term:"):
                intro = status.split(":", 1)[1]
                if intro in pos and pos[code] < pos[intro]:
                    errs.append(f"{code}: термин «{stem}…» раньше введения ({intro})")
    return errs


def hearing_errors(text_by_scene):
    """Текст на слух: длина фразы и сцены, двоеточий нет, нет «не X, а Y», начала сцен не однообразны."""
    errs, starts = [], []
    for code, text in text_by_scene.items():
        plain = text.replace(ACC, "")
        if ":" in plain:
            errs.append(f"{code}: двоеточие в тексте диктора (на слух его нет)")
        if re.search(r"(?<![а-яё])не\s+[а-яё]+[^.?!]{0,30},\s*а\s", plain.lower()):
            errs.append(f"{code}: похоже на фигуру «не X, а Y»")
        n = len(re.findall(r"[а-яё]+", plain.lower()))
        if n > LIMITS["scene_words"]:
            errs.append(f"{code}: {n} слов — больше {LIMITS['scene_words']}")
        for s in sentences(plain):
            k = len(re.findall(r"[а-яё]+", s.lower()))
            if k > LIMITS["phrase_words"]:
                errs.append(f"{code}: фраза из {k} слов — больше {LIMITS['phrase_words']}: «{s[:50]}…»")
        first = re.findall(r"[а-яё]+", plain.lower())[:1]
        starts.append(first[0] if first else "")
    if starts:
        top = max(set(starts), key=starts.count)
        if starts.count(top) / len(starts) > LIMITS["same_start_share"] / 2:
            errs.append(f"начало сцен: «{top}» в {starts.count(top)} из {len(starts)} сцен — разнообразить")
    return errs


CORE_LANG = Path(__file__).resolve().parents[1] / "lang"


def check(paper):
    paper = Path(paper).resolve()
    sys.path.insert(0, str(paper))
    nar = importlib.import_module("narration")
    text = {c: nar.TEXT[c] for c in nar.ORDER}
    reg = {**load_registry(CORE_LANG / "stress_registry.tsv"), **load_registry(paper / "stress_registry.tsv")}
    lex = load_lexicon(CORE_LANG / "lexicon.tsv") + load_lexicon(paper / "lexicon.tsv")
    errs = stress_errors(text, reg)
    errs += lexicon_errors(text, lex, nar.ORDER)
    errs += hearing_errors(text)
    return errs


if __name__ == "__main__":
    e = check(sys.argv[1])
    for x in e:
        print(x)
    print(f"нарушений {len(e)}")
    sys.exit(1 if e else 0)
