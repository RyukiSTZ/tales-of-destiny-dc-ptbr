import struct,sys; sys.path.insert(0,'/home/claude/ferr'); sys.path.insert(0,'/home/claude/img'); import tales_lz,tim2
import numpy as np
from PIL import Image
from lado import glyph_mask, estilo, pack4
S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Bold.ttf'
def dec1(d,r0=0xFEE):
    t,cs,ds=struct.unpack('<BII',d[:9]); buf=bytearray(4096); r=r0; out=bytearray(); i=9
    while len(out)<ds:
        fl=d[i]; i+=1
        for b in range(8):
            if len(out)>=ds: break
            if fl&(1<<b):
                c=d[i]; i+=1; out.append(c); buf[r]=c; r=(r+1)&0xFFF
            else:
                b1,b2=d[i],d[i+1]; i+=2; off=b1|((b2&0xF0)<<4); n=(b2&0xF)+3
                for k in range(n):
                    c=buf[(off+k)&0xFFF]; out.append(c); buf[r]=c; r=(r+1)&0xFFF
    return bytes(out)
linhas=['Novo Jogo','Continuar','Carregar Dados Originais','Personalizar','Modo de Som']
prev=None
for f in ['13451','13452','13453']:
    P='/home/claude/TOD_PTBR_TESTE/textos/prontos/%s.pak0'%f
    d=open(P,'rb').read(); n=struct.unpack('<I',d[:4])[0]; v=struct.unpack('<%dI'%n,d[4:4+4*n])
    p=4+4*n; ents=[]
    for s in v: ents.append(d[p:p+s]); p+=s
    alvo=None
    for k,e in enumerate(ents):
        if e[:1]==b'\x01':
            u=bytearray(dec1(e)); j=u.find(b'TIM2',0x40000)
            if j>0:
                pi=next(tim2.pics(bytes(u),j))
                if (pi['w'],pi['h'])==(512,160): alvo=k; break
    print(f,'entrada',alvo)
    o=pi['img']; idx=np.zeros((160,512),np.uint8)
    for k,t in enumerate(linhas):
        m,fs=glyph_mask(t,FONT,310,22,512,32,fs=23,thr=70)
        idx[k*32:(k+1)*32]=estilo(m,[1,1,2,2,3,4,5,6,6],[11,15,14,13]); print(t,fs)
    nb=pack4(idx); u[o:o+len(nb)]=nb
    c=tales_lz.comp2(bytes(u)); assert tales_lz.decomp(c)==bytes(u)
    ents[alvo]=c
    out=struct.pack('<I',n)+b''.join(struct.pack('<I',len(e)) for e in ents)+b''.join(ents)
    open(P,'wb').write(out); print('tam',len(d),len(out))
    if prev is None:
        im=tim2.para_png(bytes(u),pi); bg=Image.new('RGBA',im.size,(40,60,40,255)); bg.alpha_composite(im); bg.save(S+'titulo.png'); prev=1
