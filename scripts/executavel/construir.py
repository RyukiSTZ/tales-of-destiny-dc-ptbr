import sys,glob,re
sys.path.insert(0,'/home/claude/slps')
import slps, checar
EN={}
for l in open('/home/claude/slps/en.txt',encoding='utf-8'):
    i,s,t=l.rstrip('\n').split('|',2); EN[int(i)]=(s,t)
P=checar.carrega_pt(sorted(glob.glob('/home/claude/slps/lotes/pt_*.txt')))
mapa={EN[i][1]:t for i,(t,a,n) in P.items()}
textos={}; falta=[]
for i,(s,e) in EN.items():
    if e in mapa: textos[i]=checar.jogo(mapa[e])
    elif s not in ('Locations','Character Name') and re.search(r'[A-Za-z]{3}',re.sub(r'\[[^\]]*\]','',e)): falta.append((i,s,e))
with open('/home/claude/slps/pt_final.txt','w',encoding='utf-8') as f:
    for i in sorted(textos): f.write('%d|x|%s\n'%(i,textos[i]))
print('traduzidas',len(textos),'faltando',len(falta))
for x in falta[:80]: print(x)
