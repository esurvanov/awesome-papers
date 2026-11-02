"""Проверка README: два языка, без эмодзи, ссылки и картинки на месте, все статьи названы.

Запуск: uv run python core/pipeline/check_readme.py
Правила (замечание автора 02.11.2026, PLAYBOOK № 52):
  1. README.md — на английском, README.ru.md — на русском, каждый ссылается на другой в первой строке после заголовка.
  2. Эмодзи и значки-картинки в тексте запрещены.
  3. Каждая локальная ссылка и картинка указывает на существующий файл.
  4. Каждая папка papers/* названа в обоих файлах; у каждой статьи с номером arXiv есть ссылка на arxiv.org.
  5. В каждом файле есть картинки и схемы (docs/img), русский текст — в README.ru.md, не в README.md.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EMOJI = re.compile("[\U0001F000-\U0001FFFF☀-➿⬀-⯿️‍]")
CYR = re.compile("[А-Яа-яЁё]")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")


def main():
    errors = []
    en, ru = ROOT / "README.md", ROOT / "README.ru.md"
    for f in (en, ru):
        if not f.exists():
            errors.append(f"нет файла {f.name}")
    if errors:
        return report(errors)
    text = {f.name: f.read_text(encoding="utf-8") for f in (en, ru)}

    if "(README.ru.md)" not in text["README.md"].split("\n## ")[0]:
        errors.append("README.md: в начале нет ссылки на README.ru.md")
    if "(README.md)" not in text["README.ru.md"].split("\n## ")[0]:
        errors.append("README.ru.md: в начале нет ссылки на README.md")

    for name, t in text.items():
        for n, line in enumerate(t.splitlines(), 1):
            m = EMOJI.search(line)
            if m:
                errors.append(f"{name}:{n}: эмодзи {m.group()!r}")
        for target in LINK.findall(t):
            if re.match(r"(https?:|#|mailto:)", target):
                continue
            if not (ROOT / target.split("#")[0]).exists():
                errors.append(f"{name}: ссылка на несуществующий файл {target}")
        if not re.search(r"!\[[^\]]+\]\(docs/img/", t):
            errors.append(f"{name}: нет картинок из docs/img")
        if not re.search(r"!\[[^\]]+\]\(docs/img/\S+\.svg\)", t):
            errors.append(f"{name}: нет схемы (svg)")

    if CYR.search(re.sub(r"`[^`]*`|\([^)]*\)|\[[^\]]*\]", "", text["README.md"])):
        errors.append("README.md: русский текст в английской странице")
    if not CYR.search(text["README.ru.md"]):
        errors.append("README.ru.md: нет русского текста")

    for d in sorted((ROOT / "papers").iterdir()):
        if not d.is_dir():
            continue
        for name, t in text.items():
            if f"papers/{d.name}" not in t:
                errors.append(f"{name}: нет папки papers/{d.name}")
        m = re.match(r"(\d{4}\.\d{5})-", d.name)
        if m:
            for name, t in text.items():
                if f"arxiv.org/abs/{m.group(1)}" not in t:
                    errors.append(f"{name}: нет ссылки на arxiv.org/abs/{m.group(1)}")
    return report(errors)


def report(errors):
    for e in errors:
        print("НАРУШЕНИЕ:", e)
    print(f"README: {len(errors)} нарушений")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
