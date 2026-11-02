"""Схемы для README (SVG, два языка): docs/img/pipeline.{en,ru}.svg и docs/img/repo.{en,ru}.svg.

Запуск: python3 docs/make_diagrams.py
Подписи — в словаре T; цвета и размеры — общие, чтобы английская и русская схемы не расходились.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent / "img"

C = {"bg": "#0f172a", "text": "#e2e8f0", "sub": "#94a3b8", "step": "#1e3a5f", "step_line": "#60a5fa",
     "gate": "#5b3a0a", "gate_line": "#fbbf24", "end": "#14532d", "end_line": "#4ade80", "arrow": "#64748b"}

T = {
    "en": {
        "pipeline_title": "From a paper to a film",
        "gate": "gate",
        "steps": [
            ("Paper", "pick, read, passport"),
            ("Retelling", "three sentences a friend can repeat"),
            ("Narration", "plain words, stress marks"),
            ("Text check", "stress, plain words, read aloud"),
            ("Voice", "speech model reads the text"),
            ("Voice check", "pitch falls at phrase ends"),
            ("Storyboard", "rough film, test viewer"),
            ("Scenes", "one phrase = one frame"),
            ("Build check", "late frames, overlaps"),
            ("Film", "MP4 with voice"),
        ],
        "gates": [3, 5, 8],
        "repo_title": "What is in the repository",
        "repo_root": "awesome-papers",
        "repo": [
            ("core/", "shared by every film", "scene base, checks, build, word lists, film template"),
            ("papers/", "one folder per paper", "passport, narration, scenes, scenario, notes"),
            ("arxiv/", "paper texts", "extracted texts, scores, reports (no PDFs or pages)"),
            ("vendor/", "forks of other code", "ManimGL (copied), Animator (linked)"),
            ("not in git", "built on your machine", "videos, frames, voice files, keys, 3D models"),
        ],
    },
    "ru": {
        "pipeline_title": "От статьи к ролику",
        "gate": "ворота",
        "steps": [
            ("Статья", "выбрать, прочитать, паспорт"),
            ("Пересказ", "три фразы, которые зритель повторит"),
            ("Текст диктора", "простые слова, ударения"),
            ("Проверка текста", "ударения, слова, чтение вслух"),
            ("Голос", "речевая модель читает текст"),
            ("Проверка голоса", "тон не падает на концах фраз"),
            ("Раскадровка", "черновой ролик, новый зритель"),
            ("Сцены", "одна фраза = один кадр"),
            ("Проверка сборки", "опоздания кадров, наложения"),
            ("Ролик", "MP4 с голосом"),
        ],
        "gates": [3, 5, 8],
        "repo_title": "Что лежит в репозитории",
        "repo_root": "awesome-papers",
        "repo": [
            ("core/", "общее для всех роликов", "основа сцен, проверки, сборка, словари, шаблон ролика"),
            ("papers/", "папка на каждую статью", "паспорт, текст диктора, сцены, сценарий, заметки"),
            ("arxiv/", "тексты статей", "тексты, оценки, отчёты (без PDF и страниц)"),
            ("vendor/", "форки чужого кода", "ManimGL (копия), Animator (ссылка)"),
            ("не в git", "собирается у вас", "видео, кадры, озвучка, ключи, 3D-модели"),
        ],
    },
}


def box(x, y, w, h, fill, line, title, sub, num=None, tag=None):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{line}" stroke-width="2"/>']
    if num:
        s.append(f'<text x="{x + 12}" y="{y + 20}" font-size="13" fill="{line}" font-weight="700">{num}</text>')
    if tag:
        s.append(f'<text x="{x + w - 12}" y="{y + 20}" font-size="12" fill="{line}" text-anchor="end">{escape(tag)}</text>')
    s.append(f'<text x="{x + w / 2}" y="{y + 46}" font-size="17" fill="{C["text"]}" text-anchor="middle" font-weight="700">{escape(title)}</text>')
    for i, ln in enumerate(wrap(sub, 24)):
        s.append(f'<text x="{x + w / 2}" y="{y + 70 + 16 * i}" font-size="13" fill="{C["sub"]}" text-anchor="middle">{escape(ln)}</text>')
    return "\n".join(s)


def wrap(text, n):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]


def arrow(x1, y1, x2, y2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C["arrow"]}" stroke-width="2.5" marker-end="url(#a)"/>')


def svg(w, h, body, lang, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{escape(title)}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif" lang="{lang}">\n'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{C["arrow"]}"/></marker></defs>\n'
            f'<rect width="{w}" height="{h}" rx="14" fill="{C["bg"]}"/>\n'
            f'<text x="{w / 2}" y="36" font-size="22" fill="{C["text"]}" text-anchor="middle" font-weight="700">{escape(title)}</text>\n'
            f'{body}\n</svg>\n')


def pipeline(lang):
    t = T[lang]
    bw, bh, gx, x0 = 184, 96, 28, 24
    parts = []
    pos = []
    for i, (title, sub) in enumerate(t["steps"]):
        r, c = divmod(i, 5)
        x, y = x0 + c * (bw + gx), 64 + r * (bh + 56)
        pos.append((x, y))
        if i in t["gates"]:
            parts.append(box(x, y, bw, bh, C["gate"], C["gate_line"], title, sub, i + 1, t["gate"]))
        elif i == len(t["steps"]) - 1:
            parts.append(box(x, y, bw, bh, C["end"], C["end_line"], title, sub, i + 1))
        else:
            parts.append(box(x, y, bw, bh, C["step"], C["step_line"], title, sub, i + 1))
    for i in range(len(pos) - 1):
        (xa, ya), (xb, yb) = pos[i], pos[i + 1]
        if ya == yb:
            parts.append(arrow(xa + bw + 2, ya + bh / 2, xb - 2, yb + bh / 2))
        else:
            ym = ya + bh + 28
            parts.append(f'<polyline points="{xa + bw / 2},{ya + bh + 2} {xa + bw / 2},{ym} {xb + bw / 2},{ym} {xb + bw / 2},{yb - 2}" '
                         f'fill="none" stroke="{C["arrow"]}" stroke-width="2.5" marker-end="url(#a)"/>')
    w = x0 * 2 + 5 * bw + 4 * gx
    return svg(w, 64 + 2 * bh + 56 + 24, "\n".join(parts), lang, t["pipeline_title"])


def repo(lang):
    t = T[lang]
    n, bw, gx, x0 = len(t["repo"]), 184, 28, 24
    w = x0 * 2 + n * bw + (n - 1) * gx
    parts = [box(w / 2 - 110, 56, 220, 56, C["end"], C["end_line"], t["repo_root"], "").replace('y="102"', 'y="90"')]
    for i, (name, what, sub) in enumerate(t["repo"]):
        x, y = x0 + i * (bw + gx), 160
        line, fill = (C["gate_line"], C["gate"]) if i == n - 1 else (C["step_line"], C["step"])
        parts.append(f'<polyline points="{w / 2},114 {w / 2},138 {x + bw / 2},138 {x + bw / 2},{y - 2}" fill="none" '
                     f'stroke="{C["arrow"]}" stroke-width="2" marker-end="url(#a)"/>')
        parts.append(f'<rect x="{x}" y="{y}" width="{bw}" height="150" rx="10" fill="{fill}" stroke="{line}" stroke-width="2"/>')
        parts.append(f'<text x="{x + bw / 2}" y="{y + 34}" font-size="19" fill="{C["text"]}" text-anchor="middle" font-weight="700" '
                     f'font-family="Menlo,Consolas,monospace">{escape(name)}</text>')
        for j, ln in enumerate(wrap(what, 22)):
            parts.append(f'<text x="{x + bw / 2}" y="{y + 62 + 16 * j}" font-size="14" fill="{line}" text-anchor="middle" font-weight="700">{escape(ln)}</text>')
        for j, ln in enumerate(wrap(sub, 24)):
            parts.append(f'<text x="{x + bw / 2}" y="{y + 100 + 16 * j}" font-size="13" fill="{C["sub"]}" text-anchor="middle">{escape(ln)}</text>')
    return svg(w, 340, "\n".join(parts), lang, t["repo_title"])


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in T:
        (OUT / f"pipeline.{lang}.svg").write_text(pipeline(lang), encoding="utf-8")
        (OUT / f"repo.{lang}.svg").write_text(repo(lang), encoding="utf-8")
        print("ok", lang)
