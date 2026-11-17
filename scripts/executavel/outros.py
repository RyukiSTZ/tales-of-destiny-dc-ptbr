import sys,struct,re
sys.path.insert(0,'/home/claude/slps'); sys.path.insert(0,'/home/claude/ferr')
import slps, checar
def montar_gen(itens, textos, dados, H, bancos):
    ent=[x for x in itens if x[0]=='ent']
    bi=0; pos,fim=bancos[0]; feitos={}
    for i,it in enumerate(ent):
        b=slps.codificar(textos.get(i,it[2]))
        if b in feitos: alvo=feitos[b]
        else:
            while pos+len(b)>fim+1:
                bi+=1
                if bi>=len(bancos): raise SystemExit('SEM ESPACO %d %r'%(i,textos.get(i,it[2])))
                pos,fim=bancos[bi]
            alvo=pos; dados[pos:pos+len(b)]=b; pos+=len(b); feitos[b]=alvo
        for p in it[1]: dados[p:p+4]=struct.pack('<I',alvo+H)
    return bi,pos,fim
def verificar(itens,textos,dados,H):
    ent=[x for x in itens if x[0]=='ent']; last={}
    for i,it in enumerate(ent):
        for p in it[1]: last[p]=i
    ruins=0
    for p,i in last.items():
        b=slps.codificar(textos.get(i,ent[i][2])); v=struct.unpack('<I',dados[p:p+4])[0]-H
        if dados[v:v+len(b)]!=b: ruins+=1
    return len(last),ruins
def carregar_pt(arq, en_arq, add_end=True, estrito=True):
    EN={}
    for l in open(en_arq,encoding='utf-8'):
        i,t=l.rstrip('\n').split('|',1); EN[int(i)]=t
    PT={}
    for l in open(arq,encoding='utf-8'):
        l=l.rstrip('\n')
        if not l: continue
        i,t=l.split('|',1); PT[int(i)]=t+('[END]' if add_end and not t.endswith('[END]') else '')
    mapa={EN[i]:PT[i] for i in PT}
    textos={}; erros=0
    for i,e in EN.items():
        if e in mapa:
            t=mapa[e]
            if estrito and sorted(checar.tags(e))!=sorted(checar.tags(t)): print('TAGS',i,e,t); erros+=1
            textos[i]=checar.jogo(t)
    return EN,textos,erros
