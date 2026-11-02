import re, sys, json, time, urllib.request, xml.etree.ElementTree as ET
html = open(sys.argv[1], encoding='utf-8').read()
out = sys.argv[2]
start = html.index('<h3>Wed, 21 Oct 2026')
end = html.index('<h3>Tue, 20 Oct 2026')
sec = html[start:end]
ids = list(dict.fromkeys(re.findall(r'href\s*=\s*"/abs/([0-9]+\.[0-9]+)', sec)))
print('ids', len(ids))
ns = {'a': 'http://www.w3.org/2005/Atom'}
res = {}
for i in range(0, len(ids), 100):
    chunk = ids[i:i+100]
    url = 'https://export.arxiv.org/api/query?max_results=200&id_list=' + ','.join(chunk)
    for attempt in range(5):
        try:
            data = urllib.request.urlopen(url, timeout=60).read(); break
        except Exception as e:
            print('retry', e); time.sleep(5)
    root = ET.fromstring(data)
    for e in root.findall('a:entry', ns):
        aid = re.sub(r'v\d+$', '', e.find('a:id', ns).text.rsplit('/abs/', 1)[1])
        norm = lambda s: ' '.join(s.split())
        res[aid] = {'id': aid, 'title': norm(e.find('a:title', ns).text),
                    'authors': [norm(a.find('a:name', ns).text) for a in e.findall('a:author', ns)],
                    'abstract': norm(e.find('a:summary', ns).text),
                    'url': f'https://arxiv.org/abs/{aid}'}
    time.sleep(3)
rows = [res[i] for i in ids if i in res]
print('got', len(rows), 'missing', [i for i in ids if i not in res])
json.dump(rows, open(f'{out}/papers.json', 'w'), ensure_ascii=False, indent=1)
with open(f'{out}/titles.txt', 'w') as f:
    f.writelines(f"{r['id']}\t{r['title']}\n" for r in rows)
with open(f'{out}/abstracts.md', 'w') as f:
    for n, r in enumerate(rows, 1):
        f.write(f"## {n}. {r['title']}\n{r['url']} · {', '.join(r['authors'])}\n\n{r['abstract']}\n\n")
