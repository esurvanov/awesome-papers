"""Build compact per-paper digests for scoring, split into N chunk files."""
import json, re, sys
from pathlib import Path

src, out, n_chunks = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
papers = json.loads((src / 'papers.json').read_text())

EVID = re.compile(r'(±|\\pm|std\b|standard deviation|standard error|confidence interval|\bseeds?\b|\bruns\b|ablat|contaminat|leak|GPU[- ]hours|compute budget|A100|H100|github\.com|huggingface\.co|limitation|we release|open-source|statistically significant|p\s*<)', re.I)
REF = re.compile(r'^## (References|Bibliography)\b', re.M)


def section(text, names, limit):
    m = re.search(r'^## [^\n]*(' + names + r')[^\n]*$', text, re.M | re.I)
    if not m:
        return ''
    rest = text[m.end():]
    nxt = re.search(r'^## ', rest, re.M)
    return rest[:nxt.start() if nxt else limit][:limit].strip()


digests = []
for p in papers:
    d = {k: p[k] for k in ('id', 'title', 'abstract', 'comment', 'categories')}
    d['authors'] = p['authors'][:12] + (['…+%d' % (len(p['authors']) - 12)] if len(p['authors']) > 12 else [])
    if p.get('fulltext'):
        t = Path(p['fulltext']).read_text()
        ab = t.find('Abstract')
        d['front_matter'] = t[:ab if 0 < ab < 3000 else 1200][:1500]
        r = REF.search(t)
        body = t[:r.start()] if r else t
        d['headings'] = re.findall(r'^## (.{0,90})', body, re.M)[:60]
        d['body_start'] = body[ab if ab > 0 else 0:][:18000]
        d['limitations'] = section(body, 'Limitation', 3000)
        d['conclusion'] = section(body, 'Conclusion|Discussion', 2500)
        snippets = []
        for m in EVID.finditer(body[18000:] if len(body) > 18000 else ''):
            s = body[max(0, m.start() - 150): m.end() + 150].replace('\n', ' ')
            if not snippets or s[:60] != snippets[-1][:60]:
                snippets.append(s)
            if len(snippets) >= 25:
                break
        d['evidence_snippets_after_body_start'] = snippets
        d['fulltext_chars'] = len(t)
    else:
        d['no_fulltext'] = True
    digests.append(d)

k = -(-len(digests) // n_chunks)
for i in range(n_chunks):
    part = digests[i * k:(i + 1) * k]
    if part:
        (out / f'chunk{i}.json').write_text(json.dumps(part, ensure_ascii=False))
        print(i, len(part), sum(len(json.dumps(x, ensure_ascii=False)) for x in part) // 1000, 'k chars')
