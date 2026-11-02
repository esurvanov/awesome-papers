import sys
lines=open(sys.argv[1]).read().split('\n')[int(sys.argv[2])-1:int(sys.argv[3])]
buf=[]
out=[]
for l in lines:
    s=l.strip()
    if not s: continue
    if len(s)<40:
        buf.append(s)
    else:
        if buf: out.append(' | '.join(buf)); buf=[]
        out.append(s)
if buf: out.append(' | '.join(buf))
print('\n'.join(out))
