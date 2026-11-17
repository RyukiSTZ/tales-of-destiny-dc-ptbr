import sys; sys.path.insert(0,'/home/claude/img'); import tim2,numpy as np
from PIL import Image,ImageDraw,ImageFont
S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
d=bytearray(open('/home/claude/recebido_3/flat/00015.md1','rb').read()); p=next(tim2.pics(bytes(d),0x71600))
im=tim2.para_png(bytes(d),p).convert('RGB'); a=np.array(im).astype(int)
ys,xs=np.where(a.mean(2)<200); print('logo',xs.min(),xs.max(),ys.min(),ys.max())
strip=im.crop((0,ys.min()-6,640,ys.max()+7)); im.paste((255,255,255),(0,ys.min()-6,640,ys.max()+7)); ys=np.array([0])
dr=ImageDraw.Draw(im)
FB='/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-bold.otf'
FR='/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-regular.otf'
FI='/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-italic.otf'
linhas=[('Tradução PT-BR feita por Ryuki',FB,32,(55,53,53)),
        (None,None,10,None),
        ('Agradecimentos à equipe Life Bottle',FR,25,(88,86,86)),
        ('pela tradução em inglês.',FR,25,(88,86,86)),
        (None,None,14,None),
        ('Dedicado ao meu amigo e irmão',FI,28,(62,60,61)),
        ('Marcosuke!',FB,32,(55,53,53))]
y=None
tot=sum((s if t is None else s+8) for t,f,s,c in linhas)
y=(480-tot)//2
for t,f,s,c in linhas:
    if t is None: y+=s; continue
    fo=ImageFont.truetype(f,s); b=fo.getbbox(t); w=b[2]-b[0]
    dr.text(((640-w)/2-b[0],y),t,font=fo,fill=c); y+=s+8
print('fim y',y)
nb=tim2.codificar_8bpp(bytes(d),p,im.convert('RGBA')); d[p['img']:p['img']+len(nb)]=nb
open('saida/00015.md1','wb').write(d)
out=tim2.para_png(bytes(d),p); out.save(S+'dedic.png')
