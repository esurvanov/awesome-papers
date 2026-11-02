"""Проверка текста диктора на «признаки ИИ-текста» по правилам Humanizer (core/skills/humanizer, MIT, https://github.com/blader/humanizer).

Запуск (из корня):
    uv run python core/pipeline/humanize.py papers/<папка>          # быстро и локально: русские аналоги сильных признаков
    uv run python core/pipeline/humanize.py papers/<папка> --llm    # плюс разбор моделью OpenAI по всем 26 правилам + предложенная правка
Результат — papers/<папка>/humanize.md: по сцене — найденные признаки (цитатой) и, с --llm, вариант правки.
Текст диктора не переписывается сам: правку переносит человек или Claude — так сохраняются знаки ударения, слова паспорта
(ружьё Чехова) и числа. С --llm текст сцен (без знаков ударения) уходит в OpenAI (модель LM)."""
import argparse
import importlib
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "core" / "skills" / "humanizer" / "SKILL.md"
LM = "gpt-4.1"

# локальные проверки: русские формы сильнейших признаков Humanizer (§ — номер правила в SKILL.md); правило автора из CLAUDE.md —
# фигура «не X, а Y» запрещена как рефлекс, рубленые фразы подряд — тоже
LOCAL = [
    ("§1 «не X, а Y»", r"(?<![а-яё])(?:дело|суть|речь|вопрос)\s+не\s+в\s+[^.?!]{1,60}?,\s*а\s"),
    ("§1 «не X, а Y»", r"(?<![а-яё])это\s+не\s+[^.?!,]{1,40},\s*а\s"),
    ("§1 «не только …, но и»", r"(?<![а-яё])не\s+(?:только|просто|столько)\s+[^.?!]{1,80}?,?\s*но\s+и\s"),
    ("§1 «не X. Это Y»", r"(?<![а-яё])(?:это|он|она|оно)\s+не\s+[^.?!]{1,50}\.\s+(?:Это|Он|Она|Оно)\s"),
    ("§3 фраза «на глубину»", r"(?<![а-яё])(?:на самом деле|по сути|в сущности|главный вопрос|настоящий вопрос|суть в том)"),
    ("§4 разгон перед мыслью", r"(?<![а-яё])(?:давайте разберёмся|давайте посмотрим|давайте разберем|погрузимся|итак, давайте|вот что важно)"),
    ("§12 слова-штампы", r"(?<![а-яё])(?:ключев(?:ой|ая|ое|ые)|уникальн\w+|революционн\w+|важно отметить|стоит отметить|играет важную роль)"),
    ("§13 раздувание", r"(?<![а-яё])(?:прорыв\w*|переворот\w*|меняет вс[её]|невероятн\w+|поразительн\w+)"),
]


def plain(s):
    return s.replace("́", "")


def sentences(s):
    return [x for x in re.split(r"(?<=[.?!])\s+", s.strip()) if x]


def local_scan(text):
    """Сильные признаки, которые ловятся без модели: шаблоны выше + §2 ряд рубленых фраз и §8 тире через слово."""
    hits = []
    for name, rx in LOCAL:
        for m in re.finditer(rx, text, flags=re.I):
            hits.append((name, m.group(0).strip()))
    sents = sentences(text)
    run = []
    for s in sents + [""]:
        if s and len(re.findall(r"[а-яёa-z0-9]+", s.lower())) <= 3:
            run.append(s)
            continue
        if len(run) >= 3:
            hits.append(("§2 рубленые фразы подряд", " ".join(run)))
        run = []
    for s in sents:
        if s.count("—") >= 3:
            hits.append(("§8 тире как связка везде", s))
    return hits


def openai_key():
    for line in (ROOT / ".env.local").read_text().splitlines():
        if line.startswith("OPENAI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("В .env.local нет OPENAI_API_KEY")


def llm_review(text, keep_words):
    """Разбор по SKILL.md (встроенный режим): признаки цитатами + правка; слова паспорта и числа — без изменений."""
    system = SKILL.read_text() + f"""

## Режим для этого вызова
Встроенный режим. Текст — реплика диктора научно-популярного ролика на русском, её произносят вслух: разговорный регистр,
короткие предложения, числа словами. Применяй правила к русскому тексту (у каждого шаблона есть русские формы).
Не меняй и не склоняй по-другому эти слова-понятия ролика: {", ".join(keep_words)}. Не меняй числа и названия.
Не добавляй фактов. Тире «—» между подлежащим и сказуемым («Ход — это поворот») в русском — норма, это не признак §8.
Ответь только JSON: {{"tells": [{{"rule": "§N название", "quote": "точная цитата"}}], "rewrite": "текст целиком"}}.
Если признаков нет — "tells": [] и "rewrite" равен исходному тексту."""
    body = {"model": LM, "temperature": 0.2, "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}]}
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {openai_key()}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(json.loads(r.read())["choices"][0]["message"]["content"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paper")
    ap.add_argument("--llm", action="store_true", help="разбор моделью по всем правилам Humanizer (текст уходит в OpenAI)")
    ap.add_argument("--only", nargs="*", help="только эти сцены")
    a = ap.parse_args()
    paper = (ROOT / a.paper).resolve()
    sys.path.insert(0, str(paper))
    nar = importlib.import_module("narration")
    try:
        keep = list(importlib.import_module("passport").WORDS)
    except Exception:  # noqa: BLE001
        keep = []

    out = [f"# Humanizer: признаки ИИ-текста в тексте диктора", "",
           f"Правила — `core/skills/humanizer/SKILL.md` (MIT, blader/humanizer). "
           f"Проверка: локальная{' + модель ' + LM if a.llm else ''}. Правка не применяется сама — переносить вручную, сохраняя ударения.", ""]
    total = 0
    for code in nar.ORDER:
        if a.only and code not in a.only:
            continue
        text = plain(nar.TEXT[code])
        hits = local_scan(text)
        review = llm_review(text, keep) if a.llm else None
        tells = [(t["rule"], t["quote"]) for t in (review or {}).get("tells", [])]
        found = hits + [t for t in tells if t not in hits]
        total += len(found)
        if not found:
            continue
        out += [f"## {code}", ""] + [f"- **{r}**: «{q}»" for r, q in found]
        if review and review.get("rewrite") and review["rewrite"].strip() != text.strip():
            out += ["", "Было:", f"> {text}", "", "Предлагается:", f"> {review['rewrite']}"]
        out.append("")
        print(f"{code}: {len(found)}", flush=True)
    if total == 0:
        out.append("Признаков не найдено.")
    (paper / "humanize.md").write_text("\n".join(out) + "\n")
    print(f"признаков {total} → {paper / 'humanize.md'}")


if __name__ == "__main__":
    main()
