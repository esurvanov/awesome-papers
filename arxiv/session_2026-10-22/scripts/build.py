import json, sys, html
W, PAPERS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
meta = {p['id']: p for p in json.load(open(PAPERS))}
rows = []
for i in range(5):
    for r in json.load(open(f'{W}/out{i}.json')):
        p = meta[r['id']]
        rows.append({'id': r['id'], 't': p['title'], 'c': r['cat'], 'k': r['type'], 's': r['summary']})
assert len(rows) == len(meta), (len(rows), len(meta))
data = json.dumps(rows, ensure_ascii=False).replace('</', '<\\/')

page = r'''<title>arXiv cs.AI · 21 октября</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* layout: summary bars on top, filters, then one dense table */
:root{
  --bg:#f6f7f9; --panel:#ffffff; --fg:#1b2230; --muted:#5f6b7d; --line:#e1e5ec;
  --accent:#2457c5; --accent-soft:#e6edfb;
  --sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#12161d; --panel:#1a2029; --fg:#e4e8ef; --muted:#97a2b3; --line:#2a323e;
  --accent:#7ea4ff; --accent-soft:#223152; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#12161d; --panel:#1a2029; --fg:#e4e8ef; --muted:#97a2b3; --line:#2a323e;
  --accent:#7ea4ff; --accent-soft:#223152; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:14px;line-height:1.45}
.wrap{max-width:1180px;margin:0 auto;padding-block:20px 40px;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
  display:grid;gap:16px}
h1{font-size:20px;font-weight:600;margin:0;text-wrap:balance}
.sub{color:var(--muted);font-size:13px;margin-top:2px}
.top{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:16px}
@media (max-width:760px){.top{grid-template-columns:minmax(0,1fr)}}
.box{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px;min-width:0}
.lbl{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:8px}
.bars{display:grid;gap:4px}
.bar{display:grid;grid-template-columns:22px minmax(0,190px) minmax(0,1fr) 34px;align-items:center;gap:8px;
  background:none;border:0;padding:3px 4px;border-radius:5px;color:inherit;font:inherit;text-align:left;cursor:pointer}
.bar:hover{background:var(--accent-soft)}
.bar[aria-pressed="true"]{background:var(--accent-soft);outline:1px solid var(--accent)}
.bar .n{font-family:var(--mono);font-size:12px;text-align:right;font-variant-numeric:tabular-nums}
.bar .nm{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.track{height:10px;border-radius:3px;background:var(--line);overflow:hidden}
.fill{height:100%;background:var(--accent);border-radius:3px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line);background:var(--panel);color:inherit;font:inherit;font-size:13px;
  padding:5px 10px;border-radius:999px;cursor:pointer;display:inline-flex;gap:6px;align-items:center}
.chip b{font-family:var(--mono);font-weight:500;font-size:12px;color:var(--muted)}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--panel)}
.chip[aria-pressed="true"] b{color:var(--panel)}
.tools{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
#q{flex:1 1 240px;min-width:0;font:inherit;padding:8px 12px;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--fg)}
#q:focus-visible,.chip:focus-visible,.bar:focus-visible,#reset:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
#reset{font:inherit;font-size:13px;background:none;border:0;color:var(--accent);cursor:pointer;padding:6px}
#count{font-family:var(--mono);font-size:12px;color:var(--muted)}
.tbl{overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:8px}
table{width:100%;border-collapse:collapse;min-width:760px}
th{position:sticky;top:0;background:var(--panel);text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:500;padding:10px 12px;border-bottom:1px solid var(--line)}
td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:0}
td.num{font-family:var(--mono);font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums;width:36px}
td.ttl{width:32%}
td.ttl a{color:var(--fg);text-decoration:none;font-weight:500}
td.ttl a:hover{color:var(--accent);text-decoration:underline}
td.ttl .id{display:block;font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:2px}
.tag{display:inline-flex;gap:5px;align-items:center;white-space:nowrap;font-size:12px;padding:2px 8px;border-radius:4px;background:var(--accent-soft)}
.kind{font-size:12px;color:var(--muted);white-space:nowrap}
td.sum{color:var(--fg)}
.empty{padding:30px;text-align:center;color:var(--muted)}
</style>

<div class="wrap">
  <header>
    <h1>📚 arXiv cs.AI · 21 октября 2026</h1>
    <div class="sub">__N__ статей · кликните тему или тип для фильтра</div>
  </header>
  <div class="top">
    <div class="box"><div class="lbl">🗂️ Темы</div><div class="bars" id="bars"></div></div>
    <div class="box"><div class="lbl">🏷️ Тип работы</div><div class="chips" id="kinds"></div></div>
  </div>
  <div class="tools">
    <input id="q" type="search" placeholder="🔍 Поиск по названию и саммари">
    <button id="reset" type="button">↺ Сбросить</button>
    <span id="count"></span>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>#</th><th>Статья</th><th>Тема</th><th>Тип</th><th>Саммари</th></tr></thead>
    <tbody id="rows"></tbody>
  </table></div>
</div>

<script>
const D = __DATA__;
const ICON = {"Агенты":"🤖","Безопасность и приватность":"🛡️","Мультимодальность":"🎬","Роботы и модели мира":"🦾",
  "Обучение и дообучение":"🎓","Эффективность моделей":"⚡","Устройство моделей и теория":"🔬","Наука и инженерия":"🧪",
  "Медицина":"🩺","Поиск, данные и RAG":"🔎","Прочее":"📦"};
const KICON = {"Метод":"🛠️","Бенчмарк":"📏","Анализ":"📊","Обзор":"📖","Система":"⚙️"};
const st = {cat:null, kind:null, q:""};
const esc = s => s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const count = key => D.reduce((m,r)=>(m[r[key]]=(m[r[key]]||0)+1,m),{});
const cats = Object.entries(count("c")).sort((a,b)=>b[1]-a[1]);
const kinds = Object.entries(count("k")).sort((a,b)=>b[1]-a[1]);
const max = cats[0][1];
bars.innerHTML = cats.map(([c,n]) => `<button class="bar" type="button" data-c="${esc(c)}" aria-pressed="false">
  <span>${ICON[c]||"•"}</span><span class="nm">${esc(c)}</span>
  <span class="track"><span class="fill" style="display:block;width:${(n/max*100).toFixed(1)}%"></span></span><span class="n">${n}</span></button>`).join("");
document.getElementById("kinds").innerHTML = kinds.map(([k,n]) => `<button class="chip" type="button" data-k="${esc(k)}" aria-pressed="false">${KICON[k]||""} ${esc(k)} <b>${n}</b></button>`).join("");
function render(){
  const q = st.q.toLowerCase();
  const f = D.filter(r => (!st.cat||r.c===st.cat) && (!st.kind||r.k===st.kind) && (!q || (r.t+" "+r.s).toLowerCase().includes(q)));
  rows.innerHTML = f.length ? f.map((r,i) => `<tr><td class="num">${i+1}</td>
    <td class="ttl"><a href="https://arxiv.org/abs/${r.id}" target="_blank" rel="noopener">${esc(r.t)}</a><span class="id">${r.id}</span></td>
    <td><span class="tag">${ICON[r.c]||""} ${esc(r.c)}</span></td><td class="kind">${KICON[r.k]||""} ${esc(r.k)}</td>
    <td class="sum">${esc(r.s)}</td></tr>`).join("") : `<tr><td colspan="5" class="empty">Ничего не найдено</td></tr>`;
  document.getElementById("count").textContent = `${f.length} / ${D.length}`;
  document.querySelectorAll(".bar").forEach(b => b.setAttribute("aria-pressed", b.dataset.c===st.cat));
  document.querySelectorAll(".chip").forEach(b => b.setAttribute("aria-pressed", b.dataset.k===st.kind));
}
bars.addEventListener("click", e => { const b=e.target.closest(".bar"); if(!b) return; st.cat = st.cat===b.dataset.c?null:b.dataset.c; render(); });
document.getElementById("kinds").addEventListener("click", e => { const b=e.target.closest(".chip"); if(!b) return; st.kind = st.kind===b.dataset.k?null:b.dataset.k; render(); });
q.addEventListener("input", () => { st.q=q.value; render(); });
reset.addEventListener("click", () => { st.cat=st.kind=null; st.q=""; q.value=""; render(); });
render();
</script>
'''
open(OUT, 'w').write(page.replace('__DATA__', data).replace('__N__', str(len(rows))))
with open(OUT.replace('.html', '.csv'), 'w') as f:
    import csv; w = csv.writer(f)
    w.writerow(['id', 'title', 'url', 'category', 'type', 'summary'])
    for r in rows: w.writerow([r['id'], r['t'], f"https://arxiv.org/abs/{r['id']}", r['c'], r['k'], r['s']])
print(len(rows))
