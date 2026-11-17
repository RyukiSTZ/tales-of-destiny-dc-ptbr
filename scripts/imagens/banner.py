import sys; sys.path.insert(0,'/home/claude/img'); import tim2, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
R='/home/claude/recebido_H/'; S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-BoldOblique.ttf'
prev=[]
for f,txt in [('00032.tm2','1 ano depois...'),('00033.tm2','3 meses depois...')]:
    d=bytearray(open(R+f,'rb').read()); info=next(tim2.pics(bytes(d),0))
    im=tim2.para_png(bytes(d),info); a=np.array(im).astype(int)
    L=a[...,:3].mean(2); al=a[...,3]
    txtm=(al>200)&(L<170)
    ys,xs=np.where(txtm); print(f,xs.min(),xs.max(),ys.min(),ys.max())
    col=tuple(int(v) for v in np.median(a[txtm][:,:3],axis=0))
    m=cv2.dilate(txtm.astype(np.uint8),np.ones((3,3)),iterations=1)
    rgb=cv2.inpaint(a[...,:3].astype(np.uint8),m,4,cv2.INPAINT_TELEA)
    out=np.dstack([rgb,a[...,3]]).astype(np.uint8); o=Image.fromarray(out,'RGBA')
    h=ys.max()-ys.min()+1; cy=(ys.min()+ys.max())/2; cx=(xs.min()+xs.max())/2
    fs=h+1; fnt=ImageFont.truetype(FONT,fs)
    while True:
        bb=fnt.getbbox(txt)
        if bb[2]-bb[0]<=230: break
        fs-=1; fnt=ImageFont.truetype(FONT,fs)
    dr=ImageDraw.Draw(o); bb=fnt.getbbox(txt)
    x=cx-(bb[2]+bb[0])/2; y=cy-(bb[3]+bb[1])/2
    dr.text((x,y),txt,font=fnt,fill=col+(255,))
    nb=tim2.codificar_8bpp(bytes(d),info,o); d[info['img']:info['img']+len(nb)]=nb
    open('saida/'+f,'wb').write(d); prev.append(tim2.para_png(bytes(d),info)); prev.append(im)
sh=Image.new('RGBA',(576,256),(40,40,120,255))
for i,p in enumerate(prev): sh.alpha_composite(p,((i%2)*288,(i//2)*64))
sh.resize((1152,512),Image.NEAREST).save(S+'ban.png')
