import sys,struct; sys.path.insert(0,'/home/claude/img'); sys.path.insert(0,'/home/claude/ferr')
import tim2,tales_lz,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
d=open('/home/claude/recebido_3/flat/01741.bin','rb').read()
u=bytearray(tales_lz.decomp(d[12:])); info=next(tim2.pics(bytes(u),0)); o=info['img']
idx=np.frombuffer(bytes(u[o:o+info['img_size']]),np.uint8).reshape(512,256).copy()
K=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
jobs=[((179,217,72,32),'Itens'),((178,264,73,35),'Equipar'),((179,312,72,32),'Tática')]
for (x,y,w,h),t in jobs:
    fs=30
    while True:
        f=ImageFont.truetype(FONT,fs); b=f.getbbox(t)
        if b[2]-b[0]<=w-18 and b[3]-b[1]<=h-14: break
        fs-=1
    im=Image.new('L',(w,h)); ImageDraw.Draw(im).text((w/2-(b[0]+b[2])/2,h/2-(b[1]+b[3])/2),t,font=f,fill=255)
    m=(np.array(im)>100).astype(np.uint8)
    out=np.zeros((h,w),np.uint8)
    ys=np.where(m.any(1))[0]; a,bb=ys.min(),ys.max()
    for yy in range(h):
        g=[0xbc,0xbd,0xbe][min(2,int((yy-a)/max(1,bb-a)*3))]
        out[yy][m[yy]>0]=g
    r1=cv2.dilate(m,K); r2=cv2.dilate(r1,K); out[(r2>0)&(m==0)]=0x80
    prev=r2
    for c in [0xaf,0xae,0xad,0xab,0xa9,0xa6,0xa3]:
        dm=cv2.dilate(prev,K); out[(dm>0)&(prev==0)]=c; prev=dm
    idx[y:y+h,x:x+w]=out; print(t,fs)
u[o:o+idx.size]=idx.tobytes()
c=tales_lz.comp2(bytes(u)); assert tales_lz.decomp(c)==bytes(u)
out=struct.pack('<III',1,12,len(c))+c
open('saida/01741.bin','wb').write(out); print(len(d),len(out))
im=tim2.para_png(bytes(u),info).crop((170,200,256,400)); bg=Image.new('RGBA',im.size,(40,40,120,255)); bg.alpha_composite(im); bg.resize((344,800),Image.NEAREST).save(S+'anel.png')
