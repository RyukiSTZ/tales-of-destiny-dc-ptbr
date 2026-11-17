import sys; sys.path.insert(0,'/home/claude/img'); import tim2, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from lado import pack4
S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
def unpack4(d,i):
    o=i['img']; raw=np.frombuffer(d[o:o+i['img_size']],np.uint8)
    idx=np.empty(raw.size*2,np.uint8); idx[0::2]=raw&15; idx[1::2]=raw>>4; return idx.reshape(i['h'],i['w'])
jobs=[('00053',0x68e0,['Personalizar']),('00057',0x76c0,['Loja']),('00058',0x2290,['Tática']),('00062',0x79d0,['Itens']),
      ('00072',0x21b0,['Saco de','Comida']),('00073',0x2090,['Novo','Jogo+'])]
prev=[]
for f,off,lines in jobs:
    d=bytearray(open('/home/claude/md1/saida/%s.md1'%f,'rb').read()); info=next(tim2.pics(bytes(d),off))
    old=unpack4(bytes(d),info); H,W=old.shape
    core=old>=8; ys,xs=np.where(core); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    n=len(lines); lh=(y1-y0+1)/n
    # rótulo: altura de cada linha de texto (núcleo) ~ lh-4
    m=np.zeros((H,W),np.uint8); maxw=max(x1-x0+1,W-20) if n==1 else max(x1-x0+1,W-24)
    maxw=min(maxw,W-18)
    fs=60
    while True:
        fnt=ImageFont.truetype(FONT,fs); bbs=[fnt.getbbox(t) for t in lines]
        if max(b[2]-b[0] for b in bbs)<=maxw and max(b[3]-b[1] for b in bbs)<=lh-2: break
        fs-=1
    im=Image.new('L',(W,H)); dr=ImageDraw.Draw(im)
    for k,(t,b) in enumerate(zip(lines,bbs)):
        cy=y0+lh*(k+.5); dr.text((W/2-(b[0]+b[2])/2, cy-(b[1]+b[3])/2),t,font=fnt,fill=255)
    m=(np.array(im)>100).astype(np.uint8)
    out=np.zeros((H,W),np.uint8)
    for k in range(n):
        a=int(y0+lh*k); b=int(y0+lh*(k+1))
        sub=m[a:b]; r=np.where(sub.any(1))[0]
        if len(r)==0: continue
        ra,rb=r.min(),r.max(); grad=[15,15,14,14,14,13,13]
        for y in range(ra,rb+1):
            g=grad[int((y-ra)/max(1,rb-ra)*(len(grad)-1)+.5)]; out[a+y][sub[y]>0]=g
    prevm=m.copy(); K=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    for r in [9,5,5,4,3,2,1,1,1]:
        dm=cv2.dilate(prevm,K); out[(dm>0)&(prevm==0)]=r; prevm=dm
    print(f,lines,'fs',fs,'orig box',x0,x1,y0,y1)
    nb=pack4(out); d[info['img']:info['img']+len(nb)]=nb
    open('saida/%s.md1'%f,'wb').write(d)
    prev.append((tim2.para_png(bytes(d),info),tim2.para_png(open('/home/claude/recebido_3/flat/%s.md1'%f,'rb').read(),info)))
sh=Image.new('RGBA',(128*6,160),(40,40,120,255))
for k,(p,q) in enumerate(prev): sh.alpha_composite(q,(128*k,0)); sh.alpha_composite(p,(128*k,80))
sh.resize((1280,320),Image.NEAREST).save(S+'hdrn.png')
