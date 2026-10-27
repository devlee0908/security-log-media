import numpy as np,wave
SR=44100;D=33.5;N=int(SR*D);x=np.zeros((N,2));bpm=112;b=60/bpm
def add(sig,t0,pan=0.5,g=1.0):
    i=int(t0*SR);j=min(N,i+len(sig))
    if j<=i:return
    s=sig[:j-i]*g;x[i:j,0]+=s*(1-pan)*2**.5*.7;x[i:j,1]+=s*pan*2**.5*.7
def env(n,a=0.005,r=0.2):
    t=np.arange(n)/SR;return np.minimum(1,t/a)*np.exp(-t/r)
hz=lambda m:440*2**((m-69)/12)
prog=[(57,[57,60,64]),(53,[53,57,60]),(60,[60,64,67]),(55,[55,59,62])]  # Am F C G
TWIST=11.26
for bar in range(int(D/(4*b))+1):
    t0=bar*4*b;root,ch=prog[bar%4]
    if t0>=D:break
    n=int(4*b*SR);tt=np.arange(n)/SR
    pad=sum(np.sin(2*np.pi*hz(m+12)*tt)+0.3*np.sin(2*np.pi*hz(m+24)*tt*1.003) for m in ch)/len(ch)
    add(pad*np.minimum(1,tt/0.4)*np.minimum(1,(4*b-tt)/0.3),t0,0.5,0.10)
    for k in range(8):  # pluck arpeggio 8ths
        m=ch[[0,1,2,1,0,2,1,2][k]]+24;n2=int(0.4*SR);t2=np.arange(n2)/SR
        add((np.sin(2*np.pi*hz(m)*t2)+0.4*np.sin(4*np.pi*hz(m)*t2))*env(n2,0.003,0.12),t0+k*b/2,0.3+0.4*(k%2),0.16)
    for k in range(4):  # bass + kick + hats
        n3=int(b*0.9*SR);t3=np.arange(n3)/SR
        add(np.sin(2*np.pi*hz(root-12)*t3)*env(n3,0.01,0.35),t0+k*b,0.5,0.22)
        kk=int(0.25*SR);tk=np.arange(kk)/SR;add(np.sin(2*np.pi*(50+90*np.exp(-tk*30))*tk)*np.exp(-tk*12),t0+k*b,0.5,0.45)
        for hh in (0.5,):
            nh=int(0.05*SR);add(np.random.randn(nh)*np.exp(-np.arange(nh)/SR*80),t0+(k+hh)*b,0.65,0.06)
# riser into twist + hit
rn=int(1.8*SR);tr=np.arange(rn)/SR;add(np.random.randn(rn)*(tr/1.8)**2*0.5+np.sin(2*np.pi*(200+600*tr/1.8)*tr)*(tr/1.8)**2,TWIST-1.8,0.5,0.18)
hn=int(1.5*SR);th=np.arange(hn)/SR;add((np.sin(2*np.pi*45*th)+0.5*np.random.randn(hn)*np.exp(-th*8))*np.exp(-th*2.5),TWIST,0.5,0.6)
# duck music briefly right after hit (breath), fade out
t=np.arange(N)/SR;g=np.ones(N);m=(t>TWIST+0.1)&(t<TWIST+1.2);g[m]=0.35;g*=np.minimum(1,(D-t)/1.5);x*=g[:,None]
x/=np.abs(x).max()*1.12
with wave.open('bgm.wav','wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype('<i2').tobytes())
