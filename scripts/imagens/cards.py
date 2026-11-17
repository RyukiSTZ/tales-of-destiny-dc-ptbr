import sys; sys.path.insert(0,'/home/claude/img'); import tim2, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
R='/home/claude/recebido_H/'; S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
FONT='/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-regular.otf'
def segs_smallcaps(txt):
    out=[]
    for ch in txt:
        out.append((ch.upper(), ch.isupper()))
    return out
def render(W,H,segs,big,small,track,x0,base,maxw):
    while True:
        fb=ImageFont.truetype(FONT,big); fs=ImageFont.truetype(FONT,small)
        w=sum((fb if b else fs).getlength(c)+track for c,b in segs)-track
        if w<=maxw: break
        big-=1; small=round(small*(big)/(big+1)); 
    im=Image.new('L',(W,H)); dr=ImageDraw.Draw(im); x=x0
    for c,b in segs:
        f=fb if b else fs; dr.text((x,base),c,font=f,fill=255,anchor='ls'); x+=f.getlength(c)+track
    return np.array(im),w,big
jobs=[
 (0x20,   (125,204,20,455), None, 'Lado do Leon',  'sc'),
 (0x2d060,(125,176,160,480), 160,'Lado do Lion',  'lc'),
 (0x5a0a0,(125,204,20,465), None, 'Lado da Lilith','sc'),
]
d=bytearray(open(R+'00036.pak1','rb').read()); prev=[]
for off,(y0,y1,xa,xb),sil,txt,mode in jobs:
    info=next(tim2.pics(bytes(d),off)); im=tim2.para_png(bytes(d),info); a=np.array(im).astype(int)
    rgb=a[...,:3]; sat=rgb.max(2)-rgb.min(2)
    reg=np.zeros(rgb.shape[:2],bool); reg[y0:y1,xa:xb]=True
    gray=(sat<40)&(rgb.max(2)>8)&reg
    if sil:
        n,lab=cv2.connectedComponents(((rgb.max(2)>8)&(sat<40)).astype(np.uint8),connectivity=8)
        keep=set(np.unique(lab[:, :sil][lab[:, :sil]>0]))
        for k in keep: gray&=(lab!=k)
    # bbox original
    ys,xs=np.where(gray); print(hex(off),'orig bbox',xs.min(),xs.max(),ys.min(),ys.max())
    ox0,ox1,oy1=xs.min(),xs.max(),ys.max()
    a[gray,:3]=0
    if mode=='sc':
        segs=segs_smallcaps(txt); m,w,bg=render(512,358,segs,84,56,4,0,191,ox1-ox0)
        sh=int((ox0+ox1-w)/2); m=np.roll(m,sh,axis=1)
    else:
        segs=[(c,False) for c in txt]
        f=56
        while ImageFont.truetype(FONT,f).getlength(txt)>xb-12-178: f-=1
        img=Image.new('L',(512,358)); ImageDraw.Draw(img).text((178,172),txt,font=ImageFont.truetype(FONT,f),fill=255,anchor='ls'); m=np.array(img); bg=f
    print(txt,'size',bg)
    v=m.astype(int); sel=v>0
    for c in range(3): a[...,c][sel]=np.maximum(a[...,c][sel],v[sel])
    o=Image.fromarray(a.astype(np.uint8),'RGBA')
    nb=tim2.codificar_8bpp(bytes(d),info,o); d[info['img']:info['img']+len(nb)]=nb
    prev.append(tim2.para_png(bytes(d),info))
open('saida/00036.pak1','wb').write(d)
sh=Image.new('RGBA',(512,358*3))
for k,p in enumerate(prev): sh.paste(p,(0,358*k))
sh.save(S+'c36n.png')
