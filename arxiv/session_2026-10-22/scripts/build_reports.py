"""Collect per-paper full-text reports, validate, recompute totals, build page + markdown."""
import json, sys
from collections import Counter
from pathlib import Path

S = Path(sys.argv[1])
rep_dir, out_html, out_md = S / 'score22/reports', Path(sys.argv[2]), Path(sys.argv[3])
meta = {p['id']: p for p in json.loads((S / 'arxiv_2026-10-22_full/papers.json').read_text())}
prior = {r['id']: r for r in json.loads((S / 'score22/scored.json').read_text())}
expected = {i for i, r in prior.items() if not r['abstract_only']}

K = [('imp', 'Важность', 2), ('nov', 'Новизна', 2), ('rel', 'Надёжность', 2), ('br', 'Широта', 2), ('ready', 'Готовность', 2), ('sig', 'Сигналы', 1)]
rows, issues = [], []
for f in sorted(rep_dir.glob('*.json')):
    try:
        r = json.loads(f.read_text())
    except Exception as e:
        issues.append((f.name, 'bad json', str(e)[:60])); continue
    c = r.get('criteria', {})
    for k, _, hi in K:
        v = int(c.get(k, {}).get('score', 0))
        if not 0 <= v <= hi:
            issues.append((r['id'], k, v))
        c.setdefault(k, {})['score'] = max(0, min(hi, v))
    total = sum(c[k]['score'] for k, _, _ in K)
    if total != r.get('total'):
        issues.append((r['id'], 'total', r.get('total'), total))
    r['total'] = total
    r['verdict'] = 'read' if total >= 8 else 'abstract' if total >= 5 else 'skip'
    r['checks_n'] = sum(bool(x.get('ok')) for x in r.get('checks', []))
    r['title'] = meta[r['id']]['title']
    r['prior_total'] = prior[r['id']]['total']
    rows.append(r)

got = {r['id'] for r in rows}
print('reports', len(rows), 'missing', sorted(expected - got), 'issues', issues)
rows.sort(key=lambda r: (-r['total'], -r['criteria']['rel']['score'], -r['checks_n']))
print(Counter(r['verdict'] for r in rows), 'explore', sum(bool(r.get('explore')) for r in rows))
d = [r['total'] - r['prior_total'] for r in rows]
print('changed', sum(x != 0 for x in d), 'up', sum(x > 0 for x in d), 'down', sum(x < 0 for x in d))
(S / 'score22/reports_all.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1))

V = {'read': '🟢 Читать', 'abstract': '🟡 Аннотация', 'skip': '⚪ Пропуск'}
with open(out_md, 'w') as f:
    f.write('# Отчёты по скорингу · arXiv cs.AI · 22 октября 2026\n\nКритерии v1, оценка по полному тексту.\n\n')
    for n, r in enumerate(rows, 1):
        c = r['criteria']
        f.write(f"## {n}. {r['title']}\n{V[r['verdict']]} · **{r['total']}/11** · https://arxiv.org/abs/{r['id']}\n\n{r.get('summary','')}\n\n")
        for x in r.get('key_results', []):
            f.write(f'- {x}\n')
        f.write('\n| Критерий | Балл | Почему |\n|---|---|---|\n')
        for k, name, hi in K:
            f.write(f"| {name} | {c[k]['score']}/{hi} | {c[k].get('why','')} |\n")
        f.write(f"\n**Надёжность: {r['checks_n']}/9**\n\n")
        for ch in r.get('checks', []):
            f.write(f"- {'✅' if ch.get('ok') else '❌'} {ch.get('name','')}: {ch.get('where','')}\n")
        if r.get('adj'):
            f.write('\n**Поправки:** ' + '; '.join(r['adj']) + '\n')
        f.write(f"\n➕ {r.get('pro','')}  \n➖ {r.get('con','')}  \n📖 {r.get('what_to_read','')}\n")
        if r.get('code'):
            f.write(f"💻 {r['code']}\n")
        if r.get('changed_from_prior'):
            f.write(f"🔄 Было {r['prior_total']}: {r['changed_from_prior']}\n")
        f.write('\n')

data = json.dumps(rows, ensure_ascii=False).replace('</', '<\\/')
tpl = (S / 'scripts/reports_template.html').read_text()
out_html.write_text(tpl.replace('__DATA__', data).replace('__N__', str(len(rows))))
print('written', out_html, out_md)
