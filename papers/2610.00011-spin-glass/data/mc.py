import numpy as np, itertools, sys
rng=np.random.default_rng(1)
def setup(N):
    S=np.array(list(itertools.product([-1,1],repeat=N)),dtype=float)  # 2^N x N
    pairs=[(i,j) for i in range(N) for j in range(i+1,N)]
    P=np.stack([S[:,i]*S[:,j] for i,j in pairs],1)  # 2^N x E
    return S,pairs,P
def gibbs_G(Jb,S,P):  # Jb: B x E  -> G: B x N x N, logZ
    H=Jb@P.T/np.sqrt(S.shape[1])     # B x 2^N
    m=H.max(1,keepdims=True); w=np.exp(H-m); Z=w.sum(1,keepdims=True); p=w/Z
    G=np.einsum('bs,si,sj->bij',p,S,S)
    return G,(np.log(Z[:,0])+m[:,0])
def pair(B,E,rho):  # two edge vectors with correlation rho
    a=rng.standard_normal((B,E)); b=rng.standard_normal((B,E)); c=rng.standard_normal((B,E))
    return np.sqrt(rho)*a+np.sqrt(1-rho)*b, np.sqrt(rho)*a+np.sqrt(1-rho)*c
def chi(N,rho,B=200000):
    S,pairs,P=setup(N); E=len(pairs); tot=0;n=0;tot2=0
    for _ in range(B//20000):
        J1,J2=pair(20000,E,rho); G1,_=gibbs_G(J1,S,P); G2,_=gibbs_G(J2,S,P)
        v=(G1*G2).sum((1,2))/N; tot+=v.sum(); tot2+=(v**2).sum(); n+=len(v)
    m=tot/n; return m, np.sqrt((tot2/n-m*m)/n)
