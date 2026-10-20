# Реальные данные для ролика: модель SK на малых системах (перебор всех состояний + Монте-Карло по силам)
import numpy as np, json
from pathlib import Path
import mc
from mc import setup, gibbs_G
rng=np.random.default_rng(11); mc.rng=rng
out={}
def pair(B,E,rho):
    a=rng.standard_normal((B,E)); b=rng.standard_normal((B,E)); c=rng.standard_normal((B,E))
    return np.sqrt(rho)*a+np.sqrt(1-rho)*b, np.sqrt(rho)*a+np.sqrt(1-rho)*c
def chi(N,rho,B=120000):
    S,pairs,P=setup(N);E=len(pairs);tot=0;n=0
    for _ in range(B//20000):
        J1,J2=pair(20000,E,rho);G1,_=gibbs_G(J1,S,P);G2,_=gibbs_G(J2,S,P)
        tot+=((G1*G2).sum((1,2))/N).sum();n+=20000
    return tot/n
# 1) гистограмма свободной энергии, N=8, beta=1 (силы пересэмплируются)
N=8;S,pairs,P=setup(N);E=len(pairs)
F=[]
for _ in range(10):
    J=rng.standard_normal((20000,E));F.append(gibbs_G(J,S,P)[1]/N)
F=np.concatenate(F);out['F']=F[:4000].tolist();out['F_mean']=float(F.mean());out['F_var']=float(F.var())
# 2) кривая согласованности chi(rho), N=8, и граница
rhos=np.linspace(0,1,21);out['rho']=rhos.tolist()
for N in (8,):
    out[f'chi{N}']=[chi(N,r) for r in rhos]
    out[f'bound{N}']=[(1+r/N)/(1-r+2*r/N) for r in rhos]
out['N']=8
# 3) высокие температуры: 2 N^2 Var F_GOE против log(1/(1-beta^2)), N=8
N=8;S,pairs,P=setup(N);E=len(pairs)
betas=[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9];vv=[]
for b in betas:
    Fs=[]
    for _ in range(10):
        J=rng.standard_normal((20000,E));H=gibbs_G(J*b,S,P)[1]/N;Fs.append(H)
    v=np.concatenate(Fs).var()+b*b/(2*N*N)   # поправка на диагональ (GOE)
    vv.append(2*N*N*v)
out['betas']=betas;out['var_beta']=vv;out['log_beta']=[float(np.log(1/(1-b*b))) for b in betas]
json.dump(out,open(Path(__file__).parent/'sk_data.json','w'))
print({k:(v if not isinstance(v,list) else len(v)) for k,v in out.items()})
print(out['chi8'][::4],out['var_beta'],out['log_beta'])
