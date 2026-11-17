import struct,sys,glob,json,os
sys.path.insert(0,'/home/claude/ferr'); sys.path.insert(0,'/home/claude/slps'); sys.path.insert(0,'/home/claude/md1')
import tales_lz, slps, checar, enem
R='/home/claude/recebido_H/'
m=json.load(open('enem_reuso.json'))
for l in open('enem_pt.txt',encoding='utf-8'):
    l=l.rstrip('\n')
    if l: a,b=l.split('|',1); m[a]=b
def montar(d,E,novo_k,novo_b):
    n=len(E); hdr=d[:E[0][0]]
    partes=[]; 
    for k,(o,s) in enumerate(E): partes.append(novo_b if k==novo_k else d[o:o+s])
    out=bytearray(hdr); pos=len(hdr); ent=[]
    for p in partes: ent.append((pos,len(p))); out+=p; pos+=len(p)
    for k,(o,s) in enumerate(ent): out[4+8*k:12+8*k]=struct.pack('<II',o,s)
    return bytes(out)
os.makedirs('saida',exist_ok=True)
ok=skip=nomes=0; cache={}
for f in sorted(glob.glob(R+'*')):
    b=f.split('/')[-1]
    try: num=int(b[:5])
    except: continue
    if not 1768<=num<=2610: continue
    d=open(f,'rb').read(); r=enem.acha(d)
    if not r: continue
    k,x,E=r
    # modelo contiguo?
    if montar(d,E,-1,b'')!=d: skip+=1; print('PULEI',b); continue
    x=bytearray(x); mud=0
    for p,t in enem.nomes(bytes(x)):
        e=t.decode('latin1')
        if e not in m: continue
        z=p+len(t)
        while z<len(x) and x[z]==0: z+=1
        cap=min(z-p,25)-1
        bb=slps.codificar(checar.jogo(m[e]))
        if len(bb)>cap: print('GRANDE',b,e,m[e],len(bb),cap); continue
        x[p:p+cap+1]=bb+b'\0'*(cap+1-len(bb)); mud+=1
    if not mud: continue
    key=bytes(x)
    if key not in cache: cache[key]=tales_lz.comp2(key)
    c=cache[key]; assert tales_lz.decomp(c)==key
    novo=montar(d,E,k,c)
    open('saida/'+b,'wb').write(novo); ok+=1; nomes+=mud
print('arquivos',ok,'pulados',skip,'nomes',nomes)
