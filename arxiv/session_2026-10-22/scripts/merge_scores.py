"""Merge agent scores, recompute totals per scoring_criteria.md v1, emit JSON/CSV/markdown."""
import csv, json, sys
from pathlib import Path

score_dir, papers_json = Path(sys.argv[1]), Path(sys.argv[2])
meta = {p['id']: p for p in json.loads(papers_json.read_text())}
rows, problems = [], []
for f in sorted(score_dir.glob('out*.json')):
    for r in json.loads(f.read_text()):
        clamp = lambda v, hi: max(0, min(hi, int(v)))
        for k, hi in (('imp', 2), ('nov', 2), ('rel', 2), ('br', 2), ('ready', 2), ('sig', 1)):
            if r.get(k) != clamp(r.get(k, 0), hi):
                problems.append((r['id'], k, r.get(k)))
            r[k] = clamp(r.get(k, 0), hi)
        r['checks_n'] = sum(bool(x) for x in r.get('checks', []))
        r['total'] = r['imp'] + r['nov'] + r['rel'] + r['br'] + r['ready'] + r['sig']
        r['verdict'] = 'read' if r['total'] >= 8 else 'abstract' if r['total'] >= 5 else 'skip'
        p = meta[r['id']]
        r['title'], r['url'] = p['title'], p['url']
        r['abstract_only'] = r.get('abstract_only', False) or not p.get('fulltext')
        rows.append(r)

missing = set(meta) - {r['id'] for r in rows}
print('rows', len(rows), 'missing', sorted(missing), 'clamped', problems)
rows.sort(key=lambda r: (-r['total'], -r['rel'], -r['nov']))
(score_dir / 'scored.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1))

with open(score_dir / 'scored.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(['total', 'verdict', 'explore', 'imp', 'nov', 'rel', 'checks_of_9', 'br', 'ready', 'sig', 'abstract_only', 'id', 'title', 'url', 'why', 'pro', 'con', 'adjustments'])
    for r in rows:
        w.writerow([r['total'], r['verdict'], r.get('explore', False), r['imp'], r['nov'], r['rel'], r['checks_n'], r['br'], r['ready'], r['sig'],
                    r['abstract_only'], r['id'], r['title'], r['url'], r['why'], r['pro'], r['con'], '; '.join(r.get('adj', []))])

from collections import Counter
print(Counter(r['verdict'] for r in rows), 'explore', sum(bool(r.get('explore')) for r in rows))
