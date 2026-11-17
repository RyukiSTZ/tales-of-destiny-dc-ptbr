import sys,json,re,os
sys.path.insert(0,'/home/claude/slps'); sys.path.insert(0,'/home/claude/md1')
import slps, checar, scan
R='/home/claude/recebido_H/'
pt={}
for l in open('ui_pt.txt',encoding='utf-8'):
    l=l.rstrip('\n')
    if not l: continue
    f,o,t=l.split('|',2); pt[(f,int(o,16))]=t
# texto EN por (f,o)
arqs=sorted(set(f for f,o in pt))+['02991.md1']
ens={}; slots={}
for f in arqs:
    for s,L,n,t in scan.scan(R+f): ens[(f,s)]=t; slots[(f,s)]=n
mapa={}
for k,t in pt.items():
    if k not in ens: print('NAO ACHEI',k); continue
    mapa.setdefault(ens[k],t)
os.makedirs('saida',exist_ok=True)
tot=0; prob=0
for f in arqs:
    d=bytearray(open(R+f,'rb').read()); o=bytes(d)
    for (ff,s),e in ens.items():
        if ff!=f: continue
        t=pt.get((f,s)) or mapa.get(e)
        if not t: continue
        def semline(x): return sorted(y for y in checar.tags(x) if y!='[LINE]')
        if semline(e)!=semline(t): print('TAGS',f,hex(s),e,'=>',t); prob+=1; continue
        b=slps.codificar(checar.jogo(t)); cap=slots[(f,s)]-1
        if len(b)>cap: print('GRANDE',f,hex(s),len(b),cap,t); prob+=1; continue
        d[s:s+cap+1]=b+b'\0'*(cap+1-len(b)); tot+=1
    open('saida/'+f,'wb').write(d)
print('aplicados',tot,'problemas',prob)
# curtos fora do scan
ex=0
for l in open('extra_pt.txt',encoding='utf-8'):
    l=l.rstrip('\n')
    if not l: continue
    f,o,t=l.split('|',2); s=int(o,16)
    d=bytearray(open('saida/'+f,'rb').read()); e=s
    while d[e]: e+=1
    n=e
    while n<len(d) and d[n]==0: n+=1
    cap=n-s-1
    b=slps.codificar(checar.jogo(t))
    if len(b)>cap: print('GRANDE extra',f,o,t,cap); continue
    d[s:s+len(b)+1]=b+b'\0'; d[s+len(b)+1:n]=b'\0'*(n-s-len(b)-1)
    open('saida/'+f,'wb').write(d); ex+=1
print('extras',ex)
