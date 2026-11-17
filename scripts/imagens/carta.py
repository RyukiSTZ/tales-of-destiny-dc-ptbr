from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf'
def limpar(im):
    a=np.array(im.convert('RGBA')).astype(float)
    L=a[...,:3].mean(axis=2)
    mask=(L<170)&(a[...,0]>a[...,2]+12)&(a[...,3]>100)
    # dilatar
    m=mask.copy()
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            m|=np.roll(np.roll(mask,dy,0),dx,1)
    b=a.copy(); H,W=L.shape
    for y in range(H):
        row=m[y]
        if not row.any(): continue
        x=0
        while x<W:
            if row[x]:
                s=x
                while x<W and row[x]: x+=1
                e=x
                l=b[y,s-1] if s>0 else b[y,e] if e<W else b[y,s]
                r=b[y,e] if e<W else l
                for k in range(s,e):
                    t=(k-s+1)/(e-s+1); b[y,k]=l*(1-t)+r*t
            else: x+=1
    return Image.fromarray(b.clip(0,255).astype(np.uint8),'RGBA'), m
def linhas_texto(m):
    ys=np.where(m.any(axis=1))[0]; grp=[]
    for y in ys:
        if grp and y-grp[-1][1]<=3: grp[-1][1]=y
        else: grp.append([y,y])
    return [g for g in grp if g[1]-g[0]>=6]
def cor_texto(im,m):
    a=np.array(im.convert('RGBA'))
    L=a[...,:3].mean(axis=2)
    sel=a[(L<120)&(a[...,0]>a[...,2]+12)][:, :3]
    return tuple(int(v) for v in np.median(sel,axis=0)) if len(sel) else (95,75,55)
def escrever(bg,linhas,tops,cor,size=14,cx=240):
    im=bg.copy(); d=ImageDraw.Draw(im); f=ImageFont.truetype(FONT,size)
    for t,top in zip(linhas,tops):
        w=d.textlength(t,font=f)
        d.text((cx-w/2,top-3),t,font=f,fill=cor+(255,)); d.text((cx-w/2+1,top-3),t,font=f,fill=cor+(255,))
    return im
