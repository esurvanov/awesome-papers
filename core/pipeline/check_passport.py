"""Проверка ролика против паспорта (passport.py в папке статьи) — то, что проверяется программой:
  • ружьё Чехова: слово паспорта не звучит и не показывается раньше сцены, где его ввели, и потом используется ещё хотя бы раз;
  • не больше двух новых понятий на сцену (кроме завязки — первой сцены);
  • стыки: каждая сцена начинается со связки («но», «поэтому»…) или подхватывает слово паспорта из предыдущей сцены;
  • запрещённые слова и знаки — в тексте диктора и на экране (кроме справки);
  • палитра: в сценах только цвета паспорта (по смысловым именам C_STEP, C_LIFT…);
  • скука считается: не больше LIMITS["numerals"] чисел в речи сцены рассказа и LIMITS["words"] слов на сцену (паспорт может задать свои);
  • смена мира — только через переходник; порядок сцен в тексте диктора совпадает с паспортом, у каждой сцены есть класс;
  • статус после статьи (STATUS): у каждого утверждения — ступень шкалы, источник и дата проверки;
    обойдены все места поиска SOURCES (PLAYBOOK, «Статус после статьи»).
Паспорт версии 2 (PASSPORT_VERSION = 2; PLAYBOOK, «Флоу»), до отрисовки:
  • пересказ зрителя RETELL — три фразы; задача мира PITCH — не длиннее 45 слов (≈ 20 с) и без запрещённых слов;
  • у каждого слова паспорта — как оно показано на экране (третье поле WORDS);
  • у каждого числа в речи сцены рассказа — как оно показано (NUMBERS[сцена]: {слово числа: как показано});
  • раскадровка STORYBOARD: у каждой фразы каждой сцены — описание кадра;
  • проба на новом зрителе VIEWER_TEST: вопросы по каждому слову рассказа и «зачем это всё», все ответы верные.
Понятно ли на самом деле, цельность и голос программа не проверяет — это проба на новом зрителе и сверка с автором.
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
N.TEXT = {k: v.replace("\u0301", "") for k, v in N.TEXT.items()}  # знаки ударения в тексте диктора не мешают сверке слов


def screen_texts(src):
    """Строки, выводимые на экран в каждой сцене: строковые константы внутри класса, кроме описания класса."""
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.ClassDef) and node.name in {c for c, *_ in P.SCENES}:
            first = node.body[0] if node.body else None  # описание класса как есть: get_docstring чистит отступы и с ним не совпадает
            doc = first.value.value if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant) else None
            out[node.name] = " ".join(c.value for c in ast.walk(node)
                                      if isinstance(c, ast.Constant) and isinstance(c.value, str) and c.value != doc)
    return out


# число — слово целиком: числительное или цифра («столько», «сторону», «семья» числами не считаются)
NUMERAL = re.compile(r"^(?:\d[\d,.]*|нол[ьяю]|нул[ьяю]|один|одн(?:а|о|у|ой|ого|ому|им|ом|и|их|им|ими)|"
                     r"два|две|двух|двум|двумя|три|тр[её]х|трем|тремя|четыре|четыр[её]х|четырем|четырьмя|"
                     r"пят[ьи]|пятью|шест[ьи]|шестью|сем[ьи]|семью|восем[ьи]|восьми|восемью|девят[ьи]|девятью|десят[ьи]|десятью|"
                     r"\w*надцат[ьи]\w*|\w*дцат[ьи]\w*|сорок\w*|(?:пять|шесть|семь|восемь|пяти|шести|семи|восьми)десят\w*|девяност\w*|сто|ста|триста|четыреста|сотн\w*|(?:три|четыре|пять|шесть|семь|восемь|девять|тр[её]х|четыр[её]х|пяти|шести|семи|восьми|девяти)с[оа]т\w*|двест\w*|тысяч\w*|"
                     r"миллион\w*|миллиард\w*|триллион\w*|квинтиллион\w*|половин\w*|четверт\w*|процент\w*|десятк\w*)$")


# статус после статьи: шкала и места поиска (PLAYBOOK, «Статус после статьи»)
STATUS_SCALE = ["гипотеза", "проверено перебором", "проверено иначе", "доказано (препринт)", "доказано (рецензировано)", "формализовано"]
SOURCES = ["новые версии статьи", "цитирующие работы", "OEIS и справочники", "репозиторий авторов", "формализация",
           "новые препринты авторов"]


def status_errors(st):
    """Карточка статусов: что утверждает ролик и насколько это верно на сегодня. None — ролик выпущен до правила."""
    import datetime
    if st is None:
        return []
    errs = []
    for c in st.get("claims", []):
        name = c.get("claim", "?")[:50]
        if c.get("status") not in STATUS_SCALE:
            errs.append(f"статус «{name}»: «{c.get('status')}» не из шкалы {STATUS_SCALE}")
        if not c.get("source"):
            errs.append(f"статус «{name}»: нет источника")
        try:
            datetime.date.fromisoformat(c.get("checked", ""))
        except ValueError:
            errs.append(f"статус «{name}»: нет даты проверки (ГГГГ-ММ-ДД)")
    if not st.get("claims"):
        errs.append("статус: нет ни одного утверждения в карточке")
    for src in SOURCES:
        if not st.get("searched", {}).get(src):
            errs.append(f"статус: не обойдено место поиска «{src}»")
    return errs


def _sents(text):
    return [x for x in re.split(r"(?<=[.?!])\s+", text.strip()) if x]


def v2_errors(order, world):
    """Паспорт версии 2: пересказ, задача мира, показ слов и чисел, раскадровка, проба на новом зрителе."""
    errs = []
    free = getattr(P, "FREE_WORLDS", {"ref"})
    retell = getattr(P, "RETELL", [])
    if len(retell) != 3 or not all(x.strip() for x in retell):
        errs.append("RETELL: нужны три фразы — что зритель расскажет другу после ролика")
    pitch = getattr(P, "PITCH", "")
    if not pitch:
        errs.append("PITCH: нет задачи мира — кто, что делает и зачем ему худший случай, за 20 секунд без терминов")
    elif len(pitch.split()) > 45:
        errs.append(f"PITCH: {len(pitch.split())} слов — больше 45 (≈ 20 с)")
    for name, rx in P.BANNED.items():
        if pitch and re.search(rx, pitch, flags=re.I):
            errs.append(f"PITCH: запрещено «{name}» — задача мира объясняется без терминов")
    for w, v in P.WORDS.items():
        if len(v) < 3 or not str(v[2]).strip():
            errs.append(f"«{w}»: не сказано, как слово показано на экране (третье поле WORDS)")
    nums = getattr(P, "NUMBERS", {})
    for c in order:
        if world[c] in free:
            continue
        t = re.sub(r"(?<![а-яё])(\w+) на \1(?![а-яё])", " ", N.TEXT[c].lower())
        keys = [k.lower() for k in nums.get(c, {})]
        for word in re.findall(r"[а-яё\d][а-яё\d,.]*", t):
            if NUMERAL.match(word) and not any(word[:4] in k or k[:4] in word for k in keys):
                errs.append(f"{c}: число «{word}» в речи — не сказано, как оно показано (NUMBERS[\"{c}\"])")
        for k, how in nums.get(c, {}).items():
            if not str(how).strip():
                errs.append(f"{c}: число «{k}» — пустое «как показано»")
    # общая идея и сквозные сущности (закон 21): конечные свойства — что идея есть, сущности названы и сцены существуют,
    # каждый стык описан, а связка стыка — действительно начало сцены; «держит ли это ролик вместе» — вопрос к автору
    if hasattr(P, "IDEA"):
        if not P.IDEA.strip():
            errs.append("IDEA: пустая общая идея")
        ents = getattr(P, "ENTITIES", {})
        if len(ents) < 3:
            errs.append("ENTITIES: нужно не меньше трёх сквозных сущностей")
        for k, (_, scs) in ents.items():
            for c in scs:
                if c not in order:
                    errs.append(f"ENTITIES[{k}]: сцены «{c}» нет в SCENES")
        links = getattr(P, "LINKS", {})
        norm = lambda t: re.sub(r"[^а-яё ]", "", t.lower().replace("ё", "е").replace("\u0301", "")).split()
        for a_, b_ in zip(order, order[1:]):
            if (a_, b_) not in links:
                errs.append(f"{a_}→{b_}: нет описания стыка (LINKS)")
                continue
            want = norm(links[(a_, b_)][0])
            first = norm(_sents(N.TEXT[b_])[0])
            if first[:len(want)] != want:
                errs.append(f"{a_}→{b_}: связка стыка «{links[(a_, b_)][0]}» не совпадает с началом сцены")
    board = getattr(P, "STORYBOARD", {})
    for c in order:
        n, got = len(_sents(N.TEXT[c])), len(board.get(c, []))
        if got != n:
            errs.append(f"{c}: раскадровка — {got} кадров на {n} фраз (STORYBOARD)")
    test = getattr(P, "VIEWER_TEST", None)
    if not test:
        errs.append("VIEWER_TEST: нет пробы на новом зрителе — показать раскадровку тому, кто тему не знает (core/pipeline/animatic.py)")
    else:
        qs = " ".join(a.get("q", "") for a in test.get("answers", [])).lower()
        for w, (_, intro, *_) in P.WORDS.items():
            if world.get(intro) not in free and not has(w, qs):
                errs.append(f"VIEWER_TEST: нет вопроса про «{w}»")
        if "зачем" not in qs:
            errs.append("VIEWER_TEST: нет вопроса «зачем это всё»")
        for a in test.get("answers", []):
            if not a.get("ok"):
                errs.append(f"VIEWER_TEST: зритель не понял — «{a.get('q', '')}» → «{a.get('a', '')}»")
        for k in ("who", "date", "saw"):
            if not test.get(k):
                errs.append(f"VIEWER_TEST: нет поля «{k}»")
    return errs


def has(word, text):
    return re.search(r"(?<![а-яё])(" + P.STEMS[word] + ")", text.lower()) is not None


def main():
    src = (PAPER / getattr(N, "SCENE_FILE", "scenes.py")).read_text()
    shown = screen_texts(src)
    drawn = set(shown)  # сцены, у которых есть класс в файле сцен
    board = PAPER / "storyboard.py"  # надписи раскадровки — тоже экран: проверяются до отрисовки сцен
    if board.exists():
        for c, t in screen_texts(board.read_text()).items():
            shown[c] = (shown.get(c, "") + " " + t).strip()
    order = [c for c, *_ in P.SCENES]
    world = {c: w for c, _, w, *_ in P.SCENES}
    pos = {c: i for i, c in enumerate(order)}
    errs = []

    if N.ORDER != order:
        errs.append("порядок сцен в тексте диктора не совпадает с паспортом")
    for c in order:
        if c not in drawn:
            errs.append(f"{c}: нет класса сцены")
    for a, b in zip(order, order[1:]):
        if world[a] != world[b] and (a, b) not in P.JUNCTIONS:
            errs.append(f"{a}→{b}: смена мира без переходника")

    for word, (_, intro, *_) in P.WORDS.items():
        used_after = False
        for c in order:
            for where, text in (("диктор", N.TEXT.get(c, "")), ("экран", shown.get(c, ""))):
                if has(word, text):
                    exempt = c in getattr(P, "REF_EXEMPT", set()) if getattr(P, "PASSPORT_VERSION", 1) >= 2 else world[c] == "ref"
                    if pos[c] < pos[intro] and not exempt:  # карточка статьи цитирует название как есть (REF_EXEMPT)
                        errs.append(f"{c} [{where}]: «{word}» звучит раньше, чем введено (в {intro})")
                    elif pos[c] > pos[intro]:
                        used_after = True
        if not used_after:
            errs.append(f"«{word}»: введено в {intro} и больше не используется")

    for c in order[1:]:
        new = [w for w, (_, intro, *_) in P.WORDS.items() if intro == c]
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

    # голые числа и затянутые сцены — то, что делает ролик скучным, считается: не больше LIMITS["numerals"] чисел на сцену
    # рассказа (размеры вида «пять на пять» не в счёт; справка и приложение свободны) и не больше LIMITS["words"] слов на сцену
    lim = {"numerals": 8, "words": 80, **getattr(P, "LIMITS", {})}
    for c in order:
        t = re.sub(r"(?<![а-яё])(\w+) на \1(?![а-яё])", " ", N.TEXT[c].lower())
        words = len(re.findall(r"[а-яёa-z0-9]+", N.TEXT[c].lower()))
        if words > lim["words"]:
            errs.append(f"{c}: {words} слов — больше {lim['words']} (≈ {lim['words'] // 1.8:.0f} с речи): сцену делить или сокращать")
        if world[c] not in getattr(P, "FREE_WORLDS", {"ref"}):
            nums = sum(1 for w in re.findall(r"[а-яё\d][а-яё\d,.]*", t) if NUMERAL.match(w))
            if nums > lim["numerals"]:
                errs.append(f"{c}: {nums} чисел в речи — больше {lim['numerals']}: числа показывать картинкой, а не перечислять")

    released = hasattr(P, "STATUS") and P.STATUS is None  # ролик выпущен до правил 40–43
    for c in ([] if released else order):  # закон 15 «ролик сам по себе»: о прошлых роликах не говорим нигде, ни в справке, ни в приложении
        for where, text in (("диктор", N.TEXT.get(c, "")), ("экран", shown.get(c, ""))):
            if re.search(r"прошл\w*\s+ролик", text, flags=re.I):
                errs.append(f"{c} [{where}]: отсылка к прошлым роликам — ролик рассказывается сам по себе (закон 15)")

    if getattr(P, "PASSPORT_VERSION", 1) >= 2:
        errs += v2_errors(order, world)
        first = order[0]
        for st in P.STATIONS:  # полоса «мы здесь» видна с первого кадра: её подписи — только словами, известными с завязки
            for w, (_, intro, *_) in P.WORDS.items():
                if intro != first and has(w, st):
                    errs.append(f"полоса «мы здесь»: станция «{st}» — слово «{w}» вводится только в {intro}")

    if not hasattr(P, "STATUS"):
        errs.append("нет STATUS — карточки статусов после статьи (шаблон: core/templates/paper/passport.py)")
    else:
        errs += status_errors(P.STATUS)

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
