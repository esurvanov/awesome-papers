"""Исследование статьи для сценария: STORM (Stanford OVAL, MIT, https://github.com/stanford-oval/storm) — вопросы с разных
точек зрения → поиск → план → текст со ссылками на источники. Опора для паспорта ролика: факты, контекст, «что известно до статьи».

Запуск (из корня):
    uv run python core/pipeline/research.py papers/2502.13266-rubik
    uv run python core/pipeline/research.py papers/<папка> --topic "Своя формулировка темы" --no-web
Источники поиска: сама статья (её текст, поиск локально, без отправки куда-либо) + веб через DuckDuckGo (запросы уходят в DuckDuckGo).
Модели: OpenAI gpt-4.1-mini (вопросы и ответы в диалогах) и gpt-4.1 (план, текст, полировка); ключ — OPENAI_API_KEY в .env.local.
Результат:
    papers/<папка>/research/outline.md, article.md, sources.md — план, текст со ссылками [n], список источников (в git);
    videos/<папка>/storm/ — сырые диалоги и результаты поиска (тексты чужих страниц — в git не попадают).
STORM живёт в своём окружении .venvs/storm (закреплённые старые зависимости); скрипт сам перезапускается в нём.
Окружение (один раз): uv venv --python 3.11 .venvs/storm && uv pip install --python .venvs/storm/bin/python
    knowledge-storm ddgs "huggingface_hub<0.26\""""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENV_PY = ROOT / ".venvs" / "storm" / "bin" / "python"
LM_FAST, LM_STRONG = "gpt-4.1-mini", "gpt-4.1"

try:
    import dspy
    from knowledge_storm import STORMWikiLMConfigs, STORMWikiRunner, STORMWikiRunnerArguments
    from knowledge_storm.lm import OpenAIModel
except ImportError:
    if Path(sys.executable).resolve() == VENV_PY.resolve() or not VENV_PY.exists():
        raise SystemExit("нет окружения STORM — команда в описании модуля")
    os.execv(str(VENV_PY), [str(VENV_PY), *sys.argv])


def sh(*cmd):
    return subprocess.run([str(c) for c in cmd], check=True, capture_output=True, text=True).stdout


def openai_key():
    for line in (ROOT / ".env.local").read_text().splitlines():
        if line.startswith("OPENAI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("В .env.local нет OPENAI_API_KEY")


def paper_text(arxiv_id, cache):
    """Текст статьи с arXiv (pdftotext); кэш — в videos/, в git не попадает."""
    txt = cache / "paper.txt"
    if not txt.exists():
        pdf = cache / "paper.pdf"
        urllib.request.urlretrieve(f"https://arxiv.org/pdf/{arxiv_id}", pdf)
        sh("pdftotext", "-layout", pdf, txt)
    return txt.read_text(errors="ignore")


def arxiv_title(arxiv_id):
    with urllib.request.urlopen(f"https://export.arxiv.org/api/query?id_list={arxiv_id}", timeout=60) as r:
        feed = r.read().decode()
    titles = re.findall(r"<title>(.*?)</title>", feed, flags=re.S)
    return " ".join(titles[-1].split()) if len(titles) > 1 else arxiv_id


def _words(s):
    return re.findall(r"[a-zа-яё0-9]{3,}", s.lower())


class PaperRM(dspy.Retrieve):
    """Поиск по тексту самой статьи: куски по ~1000 знаков, ранжирование TF-IDF. Всё локально, ничего не отправляется."""

    def __init__(self, text, url, title, k=3, size=1000):
        super().__init__(k=k)
        flat = " ".join(text.split())
        self.chunks = [flat[i:i + size] for i in range(0, len(flat), size - 150)]
        self.tf = [Counter(_words(c)) for c in self.chunks]
        df = Counter(w for tf in self.tf for w in tf)
        self.idf = {w: math.log(len(self.chunks) / n) for w, n in df.items()}
        self.url, self.title, self.k, self.usage = url, title, k, 0

    def get_usage_and_reset(self):
        u, self.usage = self.usage, 0
        return {"PaperRM": u}

    def forward(self, query_or_queries, exclude_urls=()):
        queries = [query_or_queries] if isinstance(query_or_queries, str) else query_or_queries
        self.usage += len(queries)
        out = []
        for q in queries:
            qw = set(_words(q))
            scores = [sum(tf[w] * self.idf.get(w, 0) for w in qw) / math.sqrt(sum(tf.values()) or 1) for tf in self.tf]
            for i in sorted(range(len(scores)), key=lambda i: -scores[i])[:self.k]:
                url = f"{self.url}#part-{i + 1}"
                if scores[i] > 0 and url not in exclude_urls:
                    out.append({"url": url, "title": f"{self.title} (часть {i + 1})", "description": self.title,
                                "snippets": [self.chunks[i]]})
        return out


class WebRM(dspy.Retrieve):
    """Веб через DuckDuckGo (пакет ddgs; старый duckduckgo_search, на котором встроенный поисковик STORM, молча отдаёт пусто)."""

    def __init__(self, k=3):
        super().__init__(k=k)
        from ddgs import DDGS
        self.ddgs, self.k, self.usage = DDGS(), k, 0

    def get_usage_and_reset(self):
        u, self.usage = self.usage, 0
        return {"WebRM": u}

    def forward(self, query_or_queries, exclude_urls=()):
        queries = [query_or_queries] if isinstance(query_or_queries, str) else query_or_queries
        self.usage += len(queries)
        out = []
        for q in queries:
            for d in self.ddgs.text(q, max_results=self.k) or []:
                url, body = d.get("href"), d.get("body")
                if url and body and url not in exclude_urls:
                    out.append({"url": url, "title": d.get("title") or url, "description": d.get("title") or url, "snippets": [body]})
        return out


class BothRM(dspy.Retrieve):
    """Сначала статья, потом веб; сбой веб-поиска не останавливает исследование."""

    def __init__(self, paper, web, k):
        super().__init__(k=k)
        self.paper, self.web = paper, web

    def get_usage_and_reset(self):
        return {**self.paper.get_usage_and_reset(), **(self.web.get_usage_and_reset() if self.web else {})}

    def forward(self, query_or_queries, exclude_urls=()):
        res = self.paper.forward(query_or_queries, list(exclude_urls))
        if self.web:
            try:
                res += self.web.forward(query_or_queries, list(exclude_urls))
            except Exception as e:  # noqa: BLE001
                print(f"  веб-поиск не ответил ({type(e).__name__}) — только статья", flush=True)
        return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paper", help="папка статьи, например papers/2502.13266-rubik (номер arXiv — в начале имени)")
    ap.add_argument("--topic", default=None, help="тема для STORM; по умолчанию — название статьи с arXiv")
    ap.add_argument("--no-web", action="store_true", help="искать только в тексте статьи")
    ap.add_argument("--perspectives", type=int, default=3, help="сколько точек зрения (собеседников) задают вопросы")
    ap.add_argument("--turns", type=int, default=3, help="сколько вопросов в каждом диалоге")
    a = ap.parse_args()

    paper = (ROOT / a.paper).resolve()
    arxiv_id = paper.name.split("-")[0]
    raw = ROOT / "videos" / paper.name / "storm"
    raw.mkdir(parents=True, exist_ok=True)
    title = arxiv_title(arxiv_id)
    topic = a.topic or title
    text = paper_text(arxiv_id, raw)

    kw = {"api_key": openai_key(), "temperature": 1.0, "top_p": 0.9}
    lm = STORMWikiLMConfigs()
    lm.set_conv_simulator_lm(OpenAIModel(model=LM_FAST, max_tokens=500, **kw))
    lm.set_question_asker_lm(OpenAIModel(model=LM_FAST, max_tokens=500, **kw))
    lm.set_outline_gen_lm(OpenAIModel(model=LM_STRONG, max_tokens=600, **kw))
    lm.set_article_gen_lm(OpenAIModel(model=LM_STRONG, max_tokens=900, **kw))
    lm.set_article_polish_lm(OpenAIModel(model=LM_STRONG, max_tokens=4000, **kw))

    rm = BothRM(PaperRM(text, f"https://arxiv.org/abs/{arxiv_id}", title, k=3),
                None if a.no_web else WebRM(k=3), k=6)
    args = STORMWikiRunnerArguments(output_dir=str(raw), max_conv_turn=a.turns, max_perspective=a.perspectives,
                                    search_top_k=6, max_thread_num=3)
    runner = STORMWikiRunner(args, lm, rm)
    runner.run(topic=topic, do_research=True, do_generate_outline=True, do_generate_article=True, do_polish_article=True)
    runner.post_run()
    runner.summary()

    # итог — в папку статьи: план, текст со ссылками, список источников
    run_dir = max((d for d in raw.iterdir() if d.is_dir()), key=lambda d: d.stat().st_mtime)
    out = paper / "research"
    out.mkdir(exist_ok=True)
    head = f"<!-- STORM ({LM_FAST} + {LM_STRONG}), тема: {topic}; источники: статья{'' if a.no_web else ' + веб (DuckDuckGo)'} -->\n\n"
    (out / "outline.md").write_text(head + (run_dir / "storm_gen_outline.txt").read_text())
    art = run_dir / "storm_gen_article_polished.txt"
    (out / "article.md").write_text(head + (art if art.exists() else run_dir / "storm_gen_article.txt").read_text())
    info = json.loads((run_dir / "url_to_info.json").read_text())
    idx = sorted(info["url_to_unified_index"].items(), key=lambda kv: kv[1])
    (out / "sources.md").write_text(head + "\n".join(f"[{i}] {info['url_to_info'][u]['title']} — {u}" for u, i in idx) + "\n")
    shutil.copy(run_dir / "url_to_info.json", raw / "last_url_to_info.json")
    print("Готово:", out)


if __name__ == "__main__":
    main()
