import sys; sys.path.insert(0,'/home/claude/img'); import tim2, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S='/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/'
def glyph_mask(txt,font,maxw,maxh,W,H,fs=40,thr=110):
    while True:
        f=ImageFont.truetype(font,fs); bb=f.getbbox(txt)
        if bb[2]-bb[0]<=maxw and bb[3]-bb[1]<=maxh: break
        fs-=1
    im=Image.new('L',(W,H)); dr=ImageDraw.Draw(im)
    dr.text(((W-(bb[2]+bb[0]))/2,(H-(bb[3]+bb[1]))/2),txt,font=f,fill=255)
    return (np.array(im)>thr).astype(np.uint8),fs
def estilo(m,fill_rows,rings):
    """m: mask; fill_rows: lista de índices de cima p/ baixo; rings: índices do contorno de dentro p/ fora"""
    H,W=m.shape; out=np.zeros((H,W),np.uint8)
    ys=np.where(m.any(1))[0]; y0,y1=ys.min(),ys.max()
    for y in range(H):
        if m[y].any():
            k=int((y-y0)/(max(1,y1-y0))*(len(fill_rows)-1)+.5); out[y][m[y]>0]=fill_rows[k]
    prev=m.copy()
    for r in rings:
        dm=cv2.dilate(prev,np.ones((3,3),np.uint8)); out[(dm>0)&(prev==0)]=r; prev=dm
    return out
def pack4(idx):
    f=idx.ravel(); return bytes((f[0::2]&15)|((f[1::2]&15)<<4))
if __name__=='__main__':
    R='/home/claude/recebido_H/'
    d=bytearray(open(R+'00021.pak1','rb').read()); info=next(tim2.pics(bytes(d),0x30))
    FONT='/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Bold.ttf'
    idx=np.zeros((64,512),np.uint8)
    for k,t in enumerate(['Lado do Stahn','Lado do Leon']):
        m,fs=glyph_mask(t,FONT,172,22,512,32,fs=23,thr=70); print(t,fs)
        idx[k*32:(k+1)*32]=estilo(m,[1,1,2,2,3,4,5,6,6],[11,15,14,13])
    nb=pack4(idx); d[info['img']:info['img']+len(nb)]=nb
    open('saida/00021.pak1','wb').write(d)
    im=tim2.para_png(bytes(d),info); bg=Image.new('RGBA',im.size,(40,40,120,255)); bg.alpha_composite(im)
    bg.resize((1024,128),Image.NEAREST).save(S+'s21n.png')
