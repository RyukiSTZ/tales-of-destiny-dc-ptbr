import sys; sys.path.insert(0,'/home/claude/img'); sys.path.insert(0,'/home/claude/ferr')
import tim2, tales_lz, numpy as np, cv2, struct
from PIL import Image, ImageDraw, ImageFont
from lado import pack4
S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-BoldOblique.ttf'
d=open('/home/claude/recebido_H/00039.pak1','rb').read()
n=struct.unpack('<I',d[:4])[0]; p=list(struct.unpack('<%dI'%(2*n),d[4:4+8*n]))
ents=[d[p[2*k]:p[2*k]+p[2*k+1]] for k in range(n)]
u=bytearray(tales_lz.decomp(ents[0])); info=next(tim2.pics(bytes(u),0)); o=info['img']
raw=np.frombuffer(bytes(u[o:o+info['img_size']]),np.uint8); idx=np.empty(raw.size*2,np.uint8); idx[0::2]=raw&15; idx[1::2]=raw>>4; idx=idx.reshape(512,256)
jobs=[((6,225,106,246),'Mapa-Múndi'),((0,251,95,273),'Descobertas'),((12,275,94,295),'Monstros'),
      ((5,298,94,318),'Coleção'),((12,320,61,340),'Comida'),((20,341,77,363),'História'),((6,364,57,384),''),((89,202,129,221),'')]
K=np.ones((3,3),np.uint8)
for (x0,y0,x1,y1),t in jobs:
    reg=idx[y0:y1+1,x0:x1+1]; reg[:]=0
    if not t: continue
    W,H=x1-x0+1,y1-y0+1
    fs=24
    while True:
        f=ImageFont.truetype(FONT,fs); b=f.getbbox(t)
        if b[2]-b[0]<=W-3 and b[3]-b[1]<=H-4: break
        fs-=1
    sc=1.0
    im=Image.new('L',(W,H)); ImageDraw.Draw(im).text((1-b[0],(H-(b[1]+b[3]))/2),t,font=f,fill=255)
    m=(np.array(im)>70).astype(np.uint8)
    out=np.zeros((H,W),np.uint8); r=np.where(m.any(1))[0]; ra,rb=r.min(),r.max(); g=[12,12,11,11,10,9,9]
    for y in range(ra,rb+1): out[y][m[y]>0]=g[int((y-ra)/max(1,rb-ra)*(len(g)-1)+.5)]
    ring=(cv2.dilate(m,K)>0)&(m==0); out[ring]=7
    reg[:]=out
    print(t,fs,W,H)
nb=pack4(idx); u[o:o+len(nb)]=nb
c=tales_lz.comp2(bytes(u)); assert tales_lz.decomp(c)==bytes(u)
ents[0]=c
hdr=4+8*n; out=bytearray(struct.pack('<I',n)+b'\0'*8*n); pos=hdr
for k,e in enumerate(ents):
    struct.pack_into('<II',out,4+8*k,pos,len(e)); out+=e; pos+=len(e)
open('saida/00039.pak1','wb').write(out); print('tam',len(d),len(out))
# verificação: reabre
im=tim2.para_png(bytes(u),info).crop((0,195,160,395)); bg=Image.new('RGBA',im.size,(40,40,120,255)); bg.alpha_composite(im)
bg.resize((640,800),Image.NEAREST).save(S+'atln.png')
