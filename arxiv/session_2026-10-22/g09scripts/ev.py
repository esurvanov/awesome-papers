import re,sys
f=sys.argv[1]; skip=sys.argv[2] if len(sys.argv)>2 else None
lines=open(f,encoding='utf-8',errors='replace').read().split('\n')
pat=re.compile(r'(±|\bstd\b|standard deviation|confidence interval|\bseeds?\b|\bruns\b|ablat|contaminat|leak|GPU|\bhours\b|compute|github\.com|huggingface\.co|limitation|significan|p\s*<|bootstrap)',re.I)
lo,hi=(map(int,skip.split('-')) if skip else (0,0))
for i,l in enumerate(lines,1):
    if lo<=i<=hi: continue
    for m in pat.finditer(l):
        s=max(0,m.start()-110); print(f"{i}: ...{l[s:m.end()+110]}"); break
