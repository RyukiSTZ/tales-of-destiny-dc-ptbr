import sys,re,glob,json
sys.path.insert(0,'/home/claude/slps'); import slps
rev={}
for k,v in slps.TBL.items():
    if len(v)>=3: rev.setdefault(v,k)
CODES=(4,5,6,7,0xb,0xc,0xd,0xe,0x13,0x14)
def tenta(d,i):
    """tenta decodificar string a partir de i; retorna (fim, texto) ou None"""
    txt=''; j=i; letras=0
    while j<len(d) and d[j]!=0:
        c=d[j]
        if c in CODES:
            k=d[j:j+5]
            if k in rev: txt+=rev[k]; j+=5; continue
            return None
        if c==1: txt+='[LINE]'; j+=1; continue
        if 0x20<=c<0x7f: txt+=chr(c); j+=1; letras+=c>=0x41; continue
        if c in (0x81,0x99,0x9a,0x9b) and j+1<len(d) and d[j+1:j+2]!=b'\0':
            t=slps.TBL and None
            txt+='<$%02X><$%02X>'%(c,d[j+1]); j+=2; continue
        return None
    return j,txt
def scan(f):
    d=open(f,'rb').read(); out=[]; i=0
    while i<len(d):
        if d[i]==0 or (i>0 and d[i-1]!=0): i+=1; continue
        r=tenta(d,i)
        if not r: i+=1; continue
        j,t=r
        plain=re.sub(r'\[[^\]]*\]|<\$..>','',t)
        if j-i>=3 and re.search(r'[A-Za-z]{2}',plain) and re.fullmatch(r"[ -~]*",plain) and not re.search(r'%|\\|sce|lib|TIM2|_|\.[ch]\b|^[A-Z0-9]+$',plain) and sum(ch.isalpha() for ch in plain)>=max(2,len(plain)*0.5):
            n=j
            lim=(j+1+7)//8*8
            while n<len(d) and d[n]==0 and n<lim: n+=1
            out.append((i,j-i,n-i,t))
        i=j+1
    return out
if __name__=='__main__':
    tot={}
    for f in sys.argv[1:]:
        r=scan(f); tot[f]=r
        for s,L,cap,t in r: print('%s|%x|%d|%d|%s'%(f.split('/')[-1],s,L,cap-1,t))
    json.dump(tot,open('scan.json','w'))
