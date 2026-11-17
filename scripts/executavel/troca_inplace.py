import sys; sys.path.insert(0,'/home/claude/slps'); import slps, checar
P='/home/claude/fonte2/SLPS_258.42'
d=bytearray(open(P,'rb').read())
pares=[l.rstrip('\n').split('=>') for l in open(sys.argv[1],encoding='utf-8') if '=>' in l]
for a,b in pares:
    A=slps.codificar(checar.jogo(a.strip())); B=slps.codificar(checar.jogo(b[1:] if b.startswith(" ") else b))
    assert len(B)<=len(A),(a,b)
    n=0; i=0
    while True:
        i=d.find(b'\0'+A+b'\0',i)
        if i<0: break
        d[i+1:i+1+len(A)]=B+b'\0'*(len(A)-len(B)); n+=1; i+=1
    print(n,a,'->',b)
open(P,'wb').write(d)
