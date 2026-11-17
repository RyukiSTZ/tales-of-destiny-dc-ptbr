import struct,sys,re,glob; sys.path.insert(0,'/home/claude/ferr'); import tales_lz
R='/home/claude/recebido_H/'
def entradas(d):
    n=struct.unpack('<I',d[:4])[0]
    if n>64 or n==0: return None
    E=[struct.unpack('<II',d[4+8*i:12+8*i]) for i in range(n)]
    if any(o+s>len(d) for o,s in E): return None
    return E
def acha(d):
    E=entradas(d)
    if not E: return None
    for k,(o,s) in enumerate(E):
        b=d[o:o+s]
        if s>9 and b[0] in (1,3):
            try: x=tales_lz.decomp(b)
            except Exception: continue
            if x[:4]==b'ENEM': return k,x,E
    return None
def nomes(x):
    out=[]
    for m in re.finditer(rb'[A-Za-z0-9\'"!?(][ -~]{1,}',x):
        p=m.start()
        if p<0x100 or x[p-1]!=0: continue
        t=m.group()
        e=p+len(t)
        if x[e]!=0 or not re.search(rb'[a-z]',t): continue
        out.append((p,t))
    # manter só os com passo de 56
    ps=set(p for p,_ in out)
    return [(p,t) for p,t in out if (p+56 in ps) or (p-56 in ps)]
if __name__=='__main__':
    import collections
    U=collections.Counter(); caps={}
    nf=0
    for f in sorted(glob.glob(R+'*')):
        b=f.split('/')[-1]
        try: num=int(b[:5])
        except: continue
        if not 1768<=num<=2610: continue
        r=acha(open(f,'rb').read())
        if not r: continue
        nf+=1; k,x,E=r
        for p,t in nomes(x):
            z=p+len(t)
            while z<len(x) and x[z]==0: z+=1
            U[t]+=1; caps[t]=min(caps.get(t,99),z-p)
    print(nf,len(U))
    mc=min(caps.values()); print('cap min',mc)
    import json; json.dump({k.decode('latin1'):[U[k],caps[k]] for k in U},open('/home/claude/md1/enem_nomes.json','w'),indent=0)
