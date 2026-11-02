"""Download one day of an arXiv listing: title, authors, abstract and full text (HTML version).

Usage:
    python3 -I fetch_arxiv.py --date 2026-10-21 --category cs.AI --out <dir>

Output in <dir>:
    papers.json     metadata for every paper + whether full text was found
    html/<id>.html  full paper as published by arXiv (only papers that have an HTML version)
    text/<id>.txt   plain text extracted from the HTML
Re-running skips papers that are already downloaded.
"""
import argparse
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

UA = {'User-Agent': 'arxiv-daily-fetch/1.0 (personal reading list)'}
ATOM = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}


def get(url, timeout=60, tries=4):
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if attempt == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == tries - 1:
                raise
        time.sleep(5 * (attempt + 1))


def list_ids(category, date):
    page = get(f'https://arxiv.org/list/{category}/recent?skip=0&show=2000')
    header = date.strftime('<h3>%a, %d %b %Y')
    if header not in page:
        days = re.findall(r'<h3>([^<(]+)', page)
        raise SystemExit(f'{date} not in recent listing; available: {[d.strip() for d in days]}')
    section = page[page.index(header):]
    nxt = section.find('<h3>', 4)
    section = section[:nxt] if nxt > 0 else section
    return list(dict.fromkeys(re.findall(r'href\s*=\s*"/abs/([0-9]+\.[0-9]+)', section)))


def fetch_meta(ids):
    norm = lambda s: ' '.join((s or '').split())
    meta = {}
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        root = ET.fromstring(get('https://export.arxiv.org/api/query?max_results=200&id_list=' + ','.join(chunk)))
        for e in root.findall('a:entry', ATOM):
            aid = re.sub(r'v\d+$', '', e.find('a:id', ATOM).text.rsplit('/abs/', 1)[1])
            comment = e.find('arxiv:comment', ATOM)
            meta[aid] = {
                'id': aid,
                'url': f'https://arxiv.org/abs/{aid}',
                'title': norm(e.find('a:title', ATOM).text),
                'authors': [norm(a.find('a:name', ATOM).text) for a in e.findall('a:author', ATOM)],
                'abstract': norm(e.find('a:summary', ATOM).text),
                'comment': norm(comment.text) if comment is not None else '',
                'categories': [c.get('term') for c in e.findall('a:category', ATOM)],
            }
        time.sleep(3)  # arXiv API asks for one request every 3 seconds
    return [meta[i] for i in ids if i in meta]


class TextExtractor(HTMLParser):
    """Turns an arXiv (LaTeXML) paper page into readable plain text."""
    SKIP = {'script', 'style', 'nav', 'header', 'footer', 'annotation', 'annotation-xml', 'button'}
    BLOCK = {'p', 'div', 'section', 'li', 'tr', 'figcaption', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'table'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.in_article = [], 0, False

    def handle_starttag(self, tag, attrs):
        if tag == 'article':
            self.in_article = True
        if tag in self.SKIP:
            self.skip += 1
        elif tag == 'math' and not self.skip:
            alt = dict(attrs).get('alttext')
            if alt:
                self.out.append(f' ${alt}$ ')
            self.skip += 1  # alttext already carries the formula
        elif tag in self.BLOCK:
            self.out.append('\n')
        if tag in ('h1', 'h2', 'h3', 'h4') and not self.skip:
            self.out.append('## ')

    def handle_endtag(self, tag):
        if tag in self.SKIP or tag == 'math':
            self.skip = max(0, self.skip - 1)
        elif tag in self.BLOCK:
            self.out.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)

    def text(self):
        t = ''.join(self.out)
        t = re.sub(r'[ \t\xa0]+', ' ', t)
        return re.sub(r'\n\s*\n+', '\n\n', t).strip()


def html_to_text(page):
    m = re.search(r'<article.*?</article>', page, re.S)
    p = TextExtractor()
    p.feed(m.group(0) if m else page)
    return p.text()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', required=True, help='YYYY-MM-DD as shown in the arXiv listing')
    ap.add_argument('--category', default='cs.AI')
    ap.add_argument('--out', required=True)
    ap.add_argument('--no-fulltext', action='store_true')
    ap.add_argument('--delay', type=float, default=1.0, help='pause between full-text downloads, seconds')
    a = ap.parse_args()

    out = Path(a.out)
    (out / 'html').mkdir(parents=True, exist_ok=True)
    (out / 'text').mkdir(exist_ok=True)

    ids = list_ids(a.category, dt.date.fromisoformat(a.date))
    print(f'{len(ids)} papers on {a.date}', flush=True)
    papers = fetch_meta(ids)
    print(f'metadata: {len(papers)}', flush=True)

    for n, p in enumerate(papers, 1):
        html_path, text_path = out / 'html' / f"{p['id']}.html", out / 'text' / f"{p['id']}.txt"
        if not a.no_fulltext and not text_path.exists():
            page = get(f"https://arxiv.org/html/{p['id']}")
            # papers without an HTML build return 404 or a "conversion failed" stub
            if page and '<article' in page:
                html_path.write_text(page)
                text_path.write_text(html_to_text(page))
            time.sleep(a.delay)
        p['fulltext'] = str(text_path) if text_path.exists() else None
        p['fulltext_chars'] = text_path.stat().st_size if text_path.exists() else 0
        if n % 25 == 0:
            print(f'full text: {n}/{len(papers)}', flush=True)

    (out / 'papers.json').write_text(json.dumps(papers, ensure_ascii=False, indent=1))
    have = sum(1 for p in papers if p['fulltext'])
    print(f'done: {len(papers)} papers, full text for {have}', flush=True)


if __name__ == '__main__':
    main()
