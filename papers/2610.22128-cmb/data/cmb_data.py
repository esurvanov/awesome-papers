# Упрощённая модель рекомбинации (трёхуровневая, как в разделе 4 статьи) — НЕ данные статьи, а мой расчёт для иллюстрации.
import numpy as np, json
from pathlib import Path
from scipy.integrate import solve_ivp
kB=1.380649e-23; hbar=1.054571817e-34; c=2.99792458e8; me=9.1093837e-31; mp=1.67262192e-27
B1=13.605693*1.602176634e-19; B2=B1/4; G=6.6743e-11; a=1/137.035999
T0=2.7255; h=0.674; Ob=0.0224/h**2; Om=0.143/h**2; Y=0.245
H0=100*h*1e3/3.0857e22
rho_c=3*H0**2/(8*np.pi*G)
nH0=(1-Y)*Ob*rho_c/mp
Orh2=2.473e-5*(1+0.2271*3.046)
L2s=8.22
lam_a=(16*np.pi/3)*(hbar/(me*c))/a**2
def Hstd(z): return H0*np.sqrt(Om*(1+z)**3+Orh2/h**2*(1+z)**4)
def alphaB(T):
    t=T/1e4; return 1e-19*1.14*4.309*t**-0.6166/(1+0.6703*t**0.5300)
def saha(z):
    T=T0*(1+z); nH=nH0*(1+z)**3
    S=(me*kB*T/(2*np.pi*hbar**2))**1.5*np.exp(-B1/(kB*T))/nH
    return (-S+np.sqrt(S*S+4*S))/2
def rhs(z,x,lam):
    T=T0*(1+z); nH=nH0*(1+z)**3; H=lam*Hstd(z); x=x[0]
    al=alphaB(T); be=al*(me*kB*T/(2*np.pi*hbar**2))**1.5*np.exp(-B2/(kB*T))
    La=8*np.pi*H/(lam_a**3*max(1-x,1e-12)*nH)
    C=(L2s+La)/(L2s+La+be)
    S=(me*kB*T/(2*np.pi*hbar**2))**1.5*np.exp(-B1/(kB*T))/nH
    return [C*al*nH*(x*x-(1-x)*S)/((1+z)*H)]
zs=np.linspace(1700,600,111)
out={'z':zs.tolist(),'saha':[float(saha(z)) for z in zs]}
for lam in (0.5,1.0,1.5,2.0):
    s=solve_ivp(rhs,[1700,600],[saha(1700)],args=(lam,),t_eval=zs,method='Radau',rtol=1e-8,atol=1e-12)
    out[f'x{lam}']=s.y[0].tolist()
    x=np.array(s.y[0]); zr=np.interp(0.5,x[::-1],zs[::-1]); print(lam,'z(x=0.5)=%.0f'%zr,'x(z=1000)=%.3f'%np.interp(1000,zs[::-1],x[::-1]),'x(z=800)=%.4f'%np.interp(800,zs[::-1],x[::-1]))
zr=np.interp(0.5,np.array(out['saha'])[::-1],zs[::-1]); print('saha z(x=.5)=%.0f'%zr)
json.dump(out,open(Path(__file__).parent/'cmb_data.json','w'))
