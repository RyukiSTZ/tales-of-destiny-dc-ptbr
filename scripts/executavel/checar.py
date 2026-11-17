import re,sys,glob,unicodedata
sys.path.insert(0,'/home/claude/slps')
import slps
MAPA = {"á":"#","à":"$","â":"&","ã":";","é":"=","ê":"@","í":"\\","ó":"^","ô":"_","õ":"`","ú":"{","ç":"|","É":"}",
 "Á":"A","À":"A","Â":"A","Ã":"A","Ê":"E","Í":"I","Ó":"O","Ô":"O","Õ":"O","Ú":"U","Ç":"C","ü":"u","Ü":"U","è":"e","º":"o","ª":"a"}
TAG=re.compile(r'\[(?:[A-Za-z_]+[0-9a-z_]*|/color|S\d\d|TAG_\d+[a-z]?)\]')
def tags(t):
    return [x for x in re.findall(r'\[[^\]]*\]',t) if x in slps.TBL]
def jogo(t):
    return ''.join(MAPA.get(c,c) for c in t)
GRUPO={x:'Item' for x in ['Consumable','Jewel','Weapon','Armor','Unique','Food','Key']}
GRUPO.update({'Hidden Artes':'Artes'})
def carrega_en():
    L={}
    for l in open('/home/claude/slps/en.txt',encoding='utf-8'):
        i,s,t=l.rstrip('\n').split('|',2); L[int(i)]=(GRUPO.get(s,s),t)
    return L
def carrega_pt(arqs):
    P={}
    for a in arqs:
        for n,l in enumerate(open(a,encoding='utf-8'),1):
            l=l.rstrip('\n')
            if not l: continue
            i,t=l.split('|',1); P[int(i)]=(t,a,n)
    return P
if __name__=='__main__':
    EN=carrega_en(); arqs=sys.argv[1:] or sorted(glob.glob('/home/claude/slps/lotes/pt_*.txt'))
    P=carrega_pt(arqs); erros=0
    SECMAX={}
    for i,(s_,e_) in EN.items():
        k=(s_,'[LINE]' in e_)
        for x in e_.replace('[END]','').split('[LINE]'):
            SECMAX[k]=max(SECMAX.get(k,0),len(re.sub(r'\[[^\]]*\]','',x)))
    for i,(t,a,n) in P.items():
        if i not in EN: print('ID inexistente',i,a); erros+=1; continue
        s,e=EN[i]
        if sorted(tags(e))!=sorted(tags(t)): print('TAGS',i,tags(e),tags(t)); erros+=1
        try: slps.codificar(jogo(t))
        except Exception as x: print('COD',i,x); erros+=1
        tl=t.replace('[END]','').split('[LINE]')
        multi = '[LINE]' in e
        lim = SECMAX[(s, multi)]
        for x in tl:
            L=len(re.sub(r'\[[^\]]*\]','',x))
            if L>lim: print('LONGO',i,s,L,'>',lim,'|',x)
        # also check vs section max line
    # tamanho
    b_en=sum(len(slps.codificar(EN[i][1])) for i in P); b_pt=sum(len(slps.codificar(jogo(P[i][0]))) for i in P)
    print('entradas',len(P),'bytes en',b_en,'pt',b_pt,'%+.1f%%'%(100*(b_pt-b_en)/b_en),'erros',erros)
