import json, re, sys, collections
P = json.load(open(sys.argv[1]))
cats = [
 ('safety', r'safety|attack|sabotage|jailbreak|red-team|privacy|adversar|guardrail|authoriz|injection|unlearning|watermark|fraud|secur|manipulat|backdoor|byzantine|obfuscat|differential privacy|fingerprint'),
 ('agents', r'agent|harness|computer-use|tool use|tool market|multi-agent|subagent|claw'),
 ('robot', r'robot|world model|world-action|embodied|humanoid|vla|jepa|navigation|driving|uas|motion|tactile|grasp|umi'),
 ('effic', r'quantiz|sparse attention|compression|moe|mixture-of-experts|expert|prun|kv|cache|multi-token|ptq|qat|bit|latency|efficient|router'),
 ('train', r'reinforcement|rlvr|\brl\b|distillation|dpo|preference|reward|alignment|fine-tun|post-train|self-improv|self-evol'),
 ('med', r'clinical|medical|ecg|radiolog|health|dementia|brain|mri|depression|patient|ehr|drug|respiratory|counsel'),
 ('sci', r'scien|chemi|crystal|material|pde|physics|vasp|molecul|aptamer|grain boundary|transcriptom|optimization laws|rtl|kernel|silicon|6g|industrial|manufactur|telecom|lean|theorem|proof'),
 ('mm', r'vision|visual|image|video|multimodal|3d|vlm|diffusion|gaussian|scene|chart|geometry|speech|audio|asr|duplex|sound|omni'),
 ('interp', r'interpretab|mechanis|emergence|causal|probabilit|information|representation|attribution|hallucinat|sycophan|confidence|calibrat|theory|bounds|impossib|scaffold|organize'),
]
names = {'safety':'Безопасность и приватность','agents':'Агенты','robot':'Роботы и world models','effic':'Эффективность моделей','train':'Обучение, RL, дистилляция','med':'Медицина','sci':'Наука и инженерия','mm':'Мультимодальность (видео/3D/речь)','interp':'Понимание моделей и теория','other':'Прочее'}
c = collections.Counter(); ex = collections.defaultdict(list)
bench = 0
for p in P:
    t = p['title'].lower()
    if re.search(r'bench|benchmark|evaluat|auditing|measur', t): bench += 1
    k = next((k for k, r in cats if re.search(r, t)), 'other')
    c[k] += 1; ex[k].append(p['title'])
for k, n in c.most_common(): print(f'{n:4d} {names[k]}')
print('bench', bench, 'agent-any', sum(bool(re.search(cats[1][1], p['title'].lower()+p['abstract'].lower()[:300])) for p in P))
for k in ['other']: print('\n'.join(ex[k]))
