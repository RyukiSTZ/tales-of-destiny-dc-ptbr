import sys; sys.path.insert(0,'/home/claude/backup_tod/fonte'); import acentos
from PIL import Image
src,dst,prev=sys.argv[1:4]
d=bytearray(open(src,'rb').read())
ims=[]
for P,w in [(512,1.9),(1024,2.6)]:
    acentos.FONTE=0xE68C0+P*288; acentos.LARG=0xD88B0+P*8
    orig=acentos.nucleo
    def nuc(a,cx,t,orig=orig,w=w):
        return orig(a,cx,t) if w<2 else _bold(a,cx,t)
    p=acentos.montar(d)
    ims.append(acentos.imagem(d,"aeiocE"+"".join(p)))
open(dst,'wb').write(d)
W=max(i.width for i in ims); out=Image.new('L',(W,sum(i.height for i in ims)))
y=0
for i in ims: out.paste(i,(0,y)); y+=i.height
out.save(prev)
