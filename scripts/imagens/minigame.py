import sys; sys.path.insert(0,'/home/claude/img'); sys.path.insert(0,'/home/claude/ferr')
import tim2, tales_lz, numpy as np, cv2, struct
from PIL import Image, ImageDraw, ImageFont
S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
d=open('/home/claude/recebido_H/01430.pak1','rb').read()
n,o,s=struct.unpack('<III',d[:12]); u=bytearray(tales_lz.decomp(d[o:o+s])); info=next(tim2.pics(bytes(u),0))
a=np.array(tim2.para_png(bytes(u),info)).astype(int)
st=a[226:252,216:295]; rgb=st[...,:3]; op=st[...,3]>200
G=rgb[op&(rgb[...,1]>rgb[...,0]+60)&(rgb[...,1]>rgb[...,2]+30)]; fill=tuple(np.median(G,0).astype(int))
P=rgb[op&(rgb[...,2]>rgb[...,1]+60)]; purp=tuple(np.median(P,0).astype(int))
print('fill',fill,'purple',purp)
jobs=[((216,225,79,27),'Iniciar'),((74,226,114,26),'Recordes'),((92,257,68,27),'Sair'),((186,257,136,29),'Como Jogar')]
for (x,y,w,h),t in jobs:
    a[y:y+h,x:x+w]=0
    fs=30
    while True:
        f=ImageFont.truetype(FONT,fs); b=f.getbbox(t)
        if b[2]-b[0]<=w-12 and b[3]-b[1]<=h-12: break
        fs-=1
    im=Image.new('L',(w,h)); ImageDraw.Draw(im).text((w/2-(b[0]+b[2])/2,h/2-(b[1]+b[3])/2),t,font=f,fill=255)
    m=(np.array(im)>100).astype(np.uint8); K=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    w1=cv2.dilate(m,K); p1=cv2.dilate(w1,K); p2=cv2.dilate(p1,K)
    reg=a[y:y+h,x:x+w]
    reg[p2>0]=purp+(255,); reg[w1>0]=(255,255,255,255); reg[m>0]=fill+(255,)
    print(t,fs)
o2=Image.fromarray(a.astype(np.uint8),'RGBA')
nb=tim2.codificar_8bpp(bytes(u),info,o2); u[info['img']:info['img']+len(nb)]=nb
c=tales_lz.comp2(bytes(u)); assert tales_lz.decomp(c)==bytes(u)
out=struct.pack('<III',1,12,len(c))+c
open('saida/01430.pak1','wb').write(out); print('tam',len(d),len(out))
im=tim2.para_png(bytes(u),info).crop((70,222,330,290)); bg=Image.new('RGBA',im.size,(30,30,30,255)); bg.alpha_composite(im)
bg.resize((1040,272),Image.NEAREST).save(S+'mgn.png')
