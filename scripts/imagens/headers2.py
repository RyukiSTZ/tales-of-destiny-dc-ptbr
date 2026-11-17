import sys,struct; sys.path.insert(0,'/home/claude/img'); sys.path.insert(0,'/home/claude/ferr')
import tim2,tales_lz,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
from lado import pack4
S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
def render(lines,W,H,core):
    """core: máscara bool do núcleo original (>=8) para achar a área"""
    ys,xs=np.where(core); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    n=len(lines); lh=(y1-y0+1)/n; maxw=W-18
    fs=60
    while True:
        f=ImageFont.truetype(FONT,fs); bbs=[f.getbbox(t) for t in lines]
        if max(b[2]-b[0] for b in bbs)<=maxw and max(b[3]-b[1] for b in bbs)<=lh-2: break
        fs-=1
    im=Image.new('L',(W,H)); dr=ImageDraw.Draw(im)
    for k,(t,b) in enumerate(zip(lines,bbs)):
        cy=y0+lh*(k+.5); dr.text((W/2-(b[0]+b[2])/2, cy-(b[1]+b[3])/2),t,font=f,fill=255)
    m=(np.array(im)>100).astype(np.uint8); out=np.zeros((H,W),np.uint8)
    for k in range(n):
        a=int(y0+lh*k); bb=int(y0+lh*(k+1)); sub=m[a:bb]; r=np.where(sub.any(1))[0]
        if len(r)==0: continue
        ra,rb=r.min(),r.max(); grad=[15,15,14,14,14,13,13]
        for y in range(ra,rb+1): out[a+y][sub[y]>0]=grad[int((y-ra)/max(1,rb-ra)*(len(grad)-1)+.5)]
    prev=m.copy(); K=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    for r in [9,5,5,4,3,2,1,1,1]:
        dm=cv2.dilate(prev,K); out[(dm>0)&(prev==0)]=r; prev=dm
    return out,fs
ref=open('/home/claude/recebido_H/00055.md1','rb').read(); RI=next(tim2.pics(ref,0x4360)); REFCL=tim2.clut_rgba(ref,RI)
jobs=[('/home/claude/bsub/00013.bin',0xced80,['Salvar']),('/home/claude/bsub/00013.bin',0xcf2b0,['Carregar']),
      ('/home/claude/bsub/00013.bin',0xcf7f0,['Carregar','Dados','Originais']),
      ('/home/claude/md1/saida/00054.md1',0x9fe0,['Teste de','Som']),('/home/claude/md1/saida/00059.md1',0x5bd0,['Equipar']),
      ('/home/claude/md1/saida/00060.md1',0x5490,['Dispositivo','Swordian']),('/home/claude/fonte2/SLPS_258.42',0x1aad00,['Menu','Principal'])]
prev=[]
for f,s,lines in jobs:
    d=bytearray(open(f,'rb').read()); t,cs,ds=struct.unpack('<BII',d[s:s+9]); u=bytearray(tales_lz.decomp(bytes(d[s:s+9+cs])))
    p=next(tim2.pics(bytes(u),0)); W,H=p['w'],p['h']; o=p['img']
    if p['img_type']==4:
        raw=np.frombuffer(bytes(u[o:o+p['img_size']]),np.uint8); old=np.empty(raw.size*2,np.uint8); old[0::2]=raw&15; old[1::2]=raw>>4; old=old.reshape(H,W)
        core=old>=8
    else:
        a=np.array(tim2.para_png(bytes(u),p)).astype(int); core=(a[...,3]>200)&(a[...,:3].mean(2)<170)
    idx,fs=render(lines,W,H,core)
    if p['img_type']==4: nb=pack4(idx)
    else:
        rgba=np.array([REFCL[v] for v in idx.ravel()],np.uint8).reshape(H,W,4)
        nb=tim2.codificar_8bpp(bytes(u),p,Image.fromarray(rgba,'RGBA'))
    u[o:o+len(nb)]=nb
    c=tales_lz.comp2(bytes(u)); assert tales_lz.decomp(c)==bytes(u)
    e=s+9+cs; z=0
    while e+z<len(d) and d[e+z]==0: z+=1
    ok=len(c)<=9+cs+z
    print(f.split('/')[-1],hex(s),lines,'fs',fs,'novo',len(c),'antigo',9+cs,'+zeros',z,'OK' if ok else 'NAO CABE')
    if ok:
        d[s:s+9+cs+z]=c+b'\0'*(9+cs+z-len(c)); open(f,'wb').write(d)
    prev.append(tim2.para_png(bytes(u),p))
sh=Image.new('RGBA',(128*len(prev),80),(40,40,120,255))
for k,im in enumerate(prev): sh.alpha_composite(im.convert('RGBA'),(128*k,0))
sh.resize((sh.width*2,160),Image.NEAREST).save(S+'hdr2.png')
