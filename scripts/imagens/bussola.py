import struct,sys; sys.path.insert(0,'/home/claude/ferr'); import tales_lz
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
def ler(f):
    d=open(f,'rb').read(); n=struct.unpack('<I',d[:4])[0]; v=struct.unpack('<%dI'%n,d[4:4+4*n])
    p=4+4*n; ents=[]
    for s in v: ents.append(d[p:p+s]); p+=s
    return n,ents
def clut(c):
    cols=[(c[4*i],c[4*i+1],c[4*i+2],min(255,c[4*i+3]*2)) for i in range(256)]
    return np.array([cols[(i&0xE7)|((i&8)<<1)|((i&0x10)>>1)] for i in range(256)],np.uint8)
ref=None
for f in ['13451','13452','13453']:
    n,ents=ler('/home/claude/recebido_5/Nova pasta/%s.pak0'%f)
    alvo=None
    for k,e in enumerate(ents):
        if e[:1]!=b'\x03': continue
        try: u=bytearray(tales_lz.decomp(e))
        except Exception: continue
        if len(u)==67648 and u[:4]==b'TIM2':
            idx=np.frombuffer(bytes(u[0x40:0x40+65536]),np.uint8).reshape(256,256)
            if (idx[232:249,40:64]==0x44).sum()>30: alvo=k; break
    print(f,'entrada',alvo)
    if alvo is None: continue
    idx=idx.copy()
    reg=(idx[226:254,0:128]>0).astype(np.uint8)
    nn,lab,st,c=cv2.connectedComponentsWithStats(cv2.dilate(reg,np.ones((3,3),np.uint8)))
    boxes=sorted([tuple(s[:4]) for s in st[1:] if s[4]>40])
    print(boxes)
    for (x,y,w,h),t in zip(boxes[1:3],['L','O']):
        y+=226
        idx[y:y+h,x:x+w]=0
        fs=30
        while True:
            fo=ImageFont.truetype(FONT,fs); b=fo.getbbox(t)
            if b[3]-b[1]<=h-6 and b[2]-b[0]<=w-6: break
            fs-=1
        im=Image.new('L',(w,h)); ImageDraw.Draw(im).text((w/2-(b[0]+b[2])/2,h/2-(b[1]+b[3])/2),t,font=fo,fill=255)
        m=(np.array(im)>100).astype(np.uint8); K=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        r1=cv2.dilate(m,K); r2=cv2.dilate(r1,K)
        out=np.zeros((h,w),np.uint8); out[r2>0]=0x33; out[r1>0]=0x37; out[m>0]=0x44
        idx[y:y+h,x:x+w]=out
    u[0x40:0x40+65536]=idx.tobytes()
    c=tales_lz.comp2(bytes(u)); assert tales_lz.decomp(c)==bytes(u)
    ents[alvo]=c
    out=struct.pack('<I',n)+b''.join(struct.pack('<I',len(e)) for e in ents)+b''.join(ents)
    open('/home/claude/TOD_PTBR_TESTE/textos/prontos/%s.pak0'%f,'wb').write(out)
    if ref is None:
        cl=clut(bytes(u[0x40+65536:0x40+65536+1024])); im=Image.fromarray(cl[idx[200:256,0:128]],'RGBA'); bg=Image.new('RGBA',im.size,(40,40,120,255)); bg.alpha_composite(im); bg.resize((512,224),Image.NEAREST).save(S+'bussola.png'); ref=1
