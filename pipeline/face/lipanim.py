"""lipanim.py - audio-driven mouth animation on a single still (tier1 jaw / tier2 acoustic visemes) + body fuzz. Test tool, 2026-11-13."""
import numpy as np, cv2, subprocess, math, sys
SR=16000; FPS=25
CX,Y0=276.0,212.6; DMAX=10.5
def load(path):
    raw=subprocess.run(["ffmpeg","-v","error","-i",path,"-ac","1","-ar",str(SR),"-f","s16le","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.int16).astype(np.float32)/32768
def lpc_formants(x):
    x=x*np.hamming(len(x)); x=np.append(x[0],x[1:]-0.97*x[:-1]); p=14
    r=np.correlate(x,x,"full")[len(x)-1:len(x)+p]
    if r[0]<1e-9: return None
    R=np.array([[r[abs(i-j)] for j in range(p)] for i in range(p)])+np.eye(p)*r[0]*1e-4
    try: a=np.linalg.solve(R,r[1:p+1])
    except Exception: return None
    roots=np.roots(np.concatenate(([1],-a))); roots=roots[np.imag(roots)>0.01]
    f=[(math.atan2(z.imag,z.real)*SR/(2*math.pi), -math.log(abs(z))*SR/math.pi) for z in roots]
    f=sorted([fr for fr,bw in f if 200<fr<3800 and bw<450])
    return f[:2] if len(f)>=2 else (f if f else None)
def features(audio,n):
    out=[]
    for i in range(n):
        c=int((i+0.5)/FPS*SR); w=audio[max(0,c-256):c+256]
        if len(w)<512: w=np.pad(w,(0,512-len(w)))
        rms=math.sqrt(float(np.mean(w**2)))+1e-7; db=20*math.log10(rms)
        zcr=float(np.mean(np.abs(np.diff(np.sign(w)))>0))
        sp=np.abs(np.fft.rfft(w*np.hanning(512)))**2; hf=float(sp[int(3500/SR*512):].sum()/(sp.sum()+1e-12))
        fm=lpc_formants(w) if db>-55 else None
        out.append((db,zcr,hf,fm))
    return out
def gs(x,sig):
    k=np.exp(-0.5*(np.arange(-int(4*sig),int(4*sig)+1)/sig)**2); k/=k.sum()
    return np.convolve(np.pad(x,(len(k)//2,len(k)//2),mode='edge'),k,'valid')
def smooth(x,att,rel):
    y=np.zeros_like(x); v=0
    for i,t in enumerate(x): v+=(t-v)*(att if t>v else rel); y[i]=v
    return y
def params(audio,n,tier):
    F=features(audio,n); db=np.array([f[0] for f in F]); ref=np.percentile(db[db>-60],95)
    e=np.clip((db-(ref-35))/35,0,1); o=np.zeros(n); s=np.ones(n); teeth=np.zeros(n,bool)
    for i,(d,zcr,hf,fm) in enumerate(F):
        if tier==1: o[i]=e[i]**1.4; continue
        voiced=(zcr<0.16 and e[i]>0.2)
        f1=fm[0] if fm else None; f2=fm[1] if (fm and len(fm)>1) else None
        vo=np.clip((f1-280)/(750-280),0.2,1.0) if (voiced and f1) else 0.5
        o[i]=0.85*e[i]**0.95*(0.4+0.6*vo)
        if hf>0.45 and not voiced and e[i]>0.12: o[i]=min(o[i],0.18); s[i]=1.05; teeth[i]=True
        if voiced and f2:
            if f2<1150: s[i]=0.82
            elif f2>1900: s[i]=1.08
        if e[i]<0.10: o[i]=0
    o=gs(smooth(o,0.5,0.35),1.4); o=np.roll(o,-1); o[-1]=0; s=gs(1+(s-1)*0.5,2.0)
    teeth=gs((teeth|(o>0.5)).astype(float),2.0)>0.5
    return o,s,teeth
H=W=512
Y,X=np.mgrid[0:H,0:W].astype(np.float32)
def sstep(t): t=np.clip(t,0,1); return t*t*(3-2*t)
WG=np.exp(-((X-CX)/42)**2)
TAPER=1-sstep((Y-258)/47)
BAND=np.exp(-((Y-Y0-5)/16)**2)*np.exp(-((X-CX)/55)**2)
def mouth(img,o,s,teeth):
    d=float(o*DMAX); L=max(d,1.0)
    ramp=np.clip((Y-Y0)/L,0,1)
    my=(Y-d*WG*ramp*TAPER).astype(np.float32)
    se=1+(s-1)*BAND
    mx=(CX+(X-CX)/se).astype(np.float32)
    out=cv2.remap(img,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    if d>1.2:
        a=22*s*0.92; b=d*0.5+1.2
        m=np.zeros((H,W),np.float32); cv2.ellipse(m,(int(round(CX)),int(round(Y0+d*0.5+1))),(int(a),int(b)),0,0,360,1,-1,cv2.LINE_AA)
        m=cv2.GaussianBlur(m,(0,0),1.1)
        col=np.array([34,40,52],np.float32)
        out=out*(1-m[...,None]*0.93)+col*(m[...,None]*0.93)
        if teeth and d>5:
            t=np.zeros((H,W),np.float32); th=min(0.42*d,7.5)
            cv2.rectangle(t,(int(CX-a*0.72),int(Y0+1)),(int(CX+a*0.72),int(Y0+1+th)),1,-1)
            t=cv2.GaussianBlur(t,(0,0),0.9)*m
            tc=np.array([172,196,212],np.float32); out=out*(1-t[...,None]*0.85)+tc*(t[...,None]*0.85)
    return out.astype(np.uint8)
HM=np.zeros((H,W),np.float32); cv2.ellipse(HM,(272,150),(120,150),0,0,360,1,-1); HM=cv2.GaussianBlur(HM,(0,0),14)
rng0=np.random.RandomState(7); PH=rng0.rand(12)*6.28

# ---- eyes: blinks + tiny gaze drift (added 2026-11-14)
EYES=[(246.0,136.0),(307.0,136.0)]; YC=137.0
def _blink_curve(n,seed=3):
    r=np.random.RandomState(seed); c=np.zeros(n+20); prof=[0.009,0.058,0.154,0.28,0.406,0.502,0.551,0.56,0.40,0.21,0.08,0.02]; t=1.4
    while t*FPS<n:
        i0=int(t*FPS)
        for j,v in enumerate(prof): c[i0+j]=max(c[i0+j],v)
        if r.rand()<0.15:
            i1=i0+16
            for j,v in enumerate(prof): c[i1+j]=max(c[i1+j],v*0.9)
        t+=r.uniform(2.4,5.5)
    return gs(c[:n],0.5)
def _gaze(n,seed=5):
    r=np.random.RandomState(seed); gx=np.zeros(n); gy=np.zeros(n); i=0; cx_=cy_=0.0
    while i<n:
        cx_=r.uniform(-1.1,1.1); cy_=r.uniform(-0.5,0.5); L=int(r.uniform(1.6,3.2)*FPS); gx[i:i+L]=cx_; gy[i:i+L]=cy_; i+=L
    return gs(gx,3.0),gs(gy,3.0)
_NB=_blink_curve(3000); _GX,_GY=_gaze(3000)
def eyes(img,i):
    k=float(_NB[i]); gx=float(_GX[i]); gy=float(_GY[i])
    mx=X.copy(); my=Y.copy(); dark=np.zeros((H,W),np.float32)
    for ex,ey in EYES:
        Wx=np.exp(-((X-ex)/27)**2); u=Y-YC
        if k>0.001:
            Wy=np.exp(-(u/9)**2); my=my+u*(k/(1-k))*Wy*Wx
            dark=np.maximum(dark,Wx*np.exp(-((Y-YC-1)/2.3)**2)*min(1.0,k/0.6))
        Wg=np.exp(-((X-ex)/30)**2)*np.exp(-((Y-ey)/9)**2); mx=mx-gx*Wg; my=my-gy*Wg
    out=cv2.remap(img,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    out*=(1-0.38*dark[...,None])
    bl=0.85 if k>0.001 else 1.0
    out=out*bl+img.astype(np.float32)*(1-bl)
    return np.clip(out,0,255).astype(np.uint8)
def affine(img,tx,ty,rot,sc,piv):
    M=cv2.getRotationMatrix2D(piv,rot,sc); M[0,2]+=tx; M[1,2]+=ty
    return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def noisefield(seed,amp):
    r=np.random.RandomState(seed); f=r.randn(2,7,7).astype(np.float32)*amp
    return [cv2.resize(f[k],(W,H),interpolation=cv2.INTER_CUBIC) for k in range(2)]
SHIM=[noisefield(100+k,0.5) for k in range(40)]
def frame(src,i,o,s,teeth,fuzz):
    t=i/FPS; head=eyes(mouth(src,o,s,teeth),i)
    if not fuzz: return head
    htx=0.7*math.sin(t*2*math.pi/53+PH[0])+0.3*math.sin(t*2*math.pi/29+PH[1]); hty=0.5*math.sin(t*2*math.pi/61+PH[2])
    hrot=0.15*math.sin(t*2*math.pi/70+PH[3])
    head=affine(head,htx,hty,hrot,1.0,(272.0,300.0))
    btx=0.8*math.sin(t*2*math.pi/66+PH[4]); bty=0.5*math.sin(t*2*math.pi/43+PH[5])  # ~14 breaths/min
    br=1+0.0012*math.sin(t*2*math.pi/12)
    body=affine(src,btx,bty,0.06*math.sin(t*2*math.pi/90+PH[6]),br,(256.0,420.0))
    k=int(t*0.5)%39; w=(t*0.5)-int(t*0.5); fx=SHIM[k][0]*(1-w)+SHIM[k+1][0]*w; fy=SHIM[k][1]*(1-w)+SHIM[k+1][1]*w
    body=cv2.remap(body,(X+fx).astype(np.float32),(Y+fy).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    sig=0.35+0.55*(0.5+0.5*math.sin(t*2*math.pi/23+PH[7])); body=cv2.GaussianBlur(body,(0,0),sig)
    m=HM[...,None]; out=body.astype(np.float32)*(1-m)+head.astype(np.float32)*m
    r=np.random.RandomState(1000+i); g=r.normal(0,1,(H,W,1)).astype(np.float32)
    out+=g*(1.2*m+2.6*(1-m)); out*=1+0.012*math.sin(t*2*math.pi/3.7+PH[8])
    return np.clip(out,0,255).astype(np.uint8)
def oval_crop(fr,oh=300):
    c=fr[14:414,96:448]; ow=int(round(oh*352/400)); c=cv2.resize(c,(ow,oh),interpolation=cv2.INTER_AREA)
    a=np.zeros((oh,ow),np.float32); cv2.ellipse(a,(ow//2,oh//2),(ow//2-6,oh//2-6),0,0,360,1,-1,cv2.LINE_AA); a=cv2.GaussianBlur(a,(0,0),oh*0.045)
    return c,a
def paste(bg,fr,x,y,oh=300):
    c,a=oval_crop(fr,oh); h,w=c.shape[:2]; roi=bg[y:y+h,x:x+w].astype(np.float32)
    bg[y:y+h,x:x+w]=(roi*(1-a[...,None])+c.astype(np.float32)*a[...,None]).astype(np.uint8)
