import struct
from PIL import Image
def pics(d, base=0):
    """yield (offset_header, info dict) para cada imagem num TIM2 em d[base:]"""
    assert d[base:base+4]==b'TIM2'
    n=struct.unpack('<H',d[base+6:base+8])[0]
    p=base+16 if d[base+5]==0 else base+128
    for i in range(n):
        tot,cs,isz,hs,cc,pf,mm,ct,it,w,h=struct.unpack('<IIIHHBBBBHH',d[p:p+24])
        yield dict(hdr=p,total=tot,clut_size=cs,img_size=isz,hsize=hs,colors=cc,clut_type=ct,img_type=it,w=w,h=h,
                   img=p+hs, clut=p+hs+isz)
        p+=tot
def clut_rgba(d,info):
    ct=info['clut_type']&0x1f; n=info['colors']; o=info['clut']; cols=[]
    for i in range(n):
        if ct==3: r,g,b,a=d[o+4*i:o+4*i+4]
        elif ct==2: r,g,b=d[o+3*i:o+3*i+3]; a=0x80
        else:
            v=struct.unpack('<H',d[o+2*i:o+2*i+2])[0]; r=(v&31)<<3; g=((v>>5)&31)<<3; b=((v>>10)&31)<<3; a=0x80 if v&0x8000 else 0
        cols.append((r,g,b,min(255,a*2)))
    if info['img_type']==5 and not (info['clut_type']&0x80) and n==256:
        # CSM1 swizzle
        out=list(cols)
        for i in range(256):
            j=(i&0xE7)|((i&0x08)<<1)|((i&0x10)>>1)
            out[i]=cols[j]
        cols=out
    return cols
def para_png(d,info):
    w,h=info['w'],info['h']; it=info['img_type']; o=info['img']
    im=Image.new('RGBA',(w,h)); px=im.load()
    if it in (4,5):
        cl=clut_rgba(d,info)
        for y in range(h):
            for x in range(w):
                if it==5: v=d[o+y*w+x]
                else:
                    b=d[o+(y*w+x)//2]; v=(b>>4) if (x&1) else (b&15)
                px[x,y]=cl[v]
    elif it==3:
        for y in range(h):
            for x in range(w):
                r,g,b,a=d[o+4*(y*w+x):o+4*(y*w+x)+4]; px[x,y]=(r,g,b,min(255,a*2))
    elif it==1:
        for y in range(h):
            for x in range(w):
                v=struct.unpack('<H',d[o+2*(y*w+x):o+2*(y*w+x)+2])[0]
                px[x,y]=((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3,255 if v&0x8000 else 0)
    return im

def codificar_8bpp(d,info,im):
    """devolve bytes novos dos pixels (8bpp ou 4bpp) mapeando im para a CLUT existente"""
    import numpy as np
    cl=np.array(clut_rgba(d,info),dtype=int)
    a=np.array(im.convert('RGBA')).astype(int)
    H,W=a.shape[:2]
    flat=a.reshape(-1,4)
    # distância com peso no alfa
    uniq,inv=np.unique(flat,axis=0,return_inverse=True)
    dist=((uniq[:,None,:3]-cl[None,:,:3])**2).sum(axis=2)+ 4*(uniq[:,None,3]-cl[None,:,3])**2
    idx=dist.argmin(axis=1)[inv.reshape(-1)].astype(np.uint8)
    if info['img_type']==5: return idx.tobytes()
    out=bytearray(W*H//2)
    for i in range(0,len(idx),2): out[i//2]=(idx[i]&15)|((idx[i+1]&15)<<4)
    return bytes(out)
