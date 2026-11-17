import sys; sys.path.insert(0,'/home/claude/img'); import tim2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from lado import pack4
S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
d=bytearray(open('/home/claude/recebido_3/flat/00000.tm2','rb').read()); i=next(tim2.pics(bytes(d),0)); o=i['img']
raw=np.frombuffer(bytes(d[o:o+i['img_size']]),np.uint8); idx=np.empty(raw.size*2,np.uint8); idx[0::2]=raw&15; idx[1::2]=raw>>4; idx=idx.reshape(512,256).copy()
x0,y0,x1,y1=154,330,183,344
# fundo: copiar linha de fundo limpa (só 5) mantendo a borda
for y in range(y0,y1+1):
    for x in range(x0,x1+1):
        if idx[y,x] not in (0,1): idx[y,x]=5
F='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
t='Próx'
fs=16
while True:
    f=ImageFont.truetype(F,fs); b=f.getbbox(t)
    if b[2]-b[0]<=x1-x0-1 and b[3]-b[1]<=y1-y0: break
    fs-=1
W,H=x1-x0+1,y1-y0+1
im=Image.new('L',(W,H)); ImageDraw.Draw(im).text(((W-1)/2-(b[0]+b[2])/2,(H-1)/2-(b[1]+b[3])/2),t,font=f,fill=255)
m=np.array(im)>90
sh=np.zeros_like(m); sh[1:,1:]=m[:-1,:-1]
reg=idx[y0:y1+1,x0:x1+1]
reg[sh & (reg!=1)]=7
reg[m]=9
print(fs)
nb=pack4(idx); d[o:o+len(nb)]=nb
open('saida/00000.tm2','wb').write(d)
im=tim2.para_png(bytes(d),i).crop((130,320,210,356)); bg=Image.new('RGBA',im.size,(40,40,120,255)); bg.alpha_composite(im); bg.resize((640,288),Image.NEAREST).save(S+'nx.png')
