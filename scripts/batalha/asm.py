import re,struct
SRC='/home/claude/lifebottle/tales-of-destiny-dc/patch/ASM/Battle_Subs_Text.asm'
def parse_args(s):
    out=[];i=0;cur=''
    while i<len(s):
        c=s[i]
        if c=='"':
            j=i+1; buf=''
            while s[j]!='"':
                buf+=s[j]; j+=1
            out.append(('s',buf)); i=j+1; continue
        if c==',':
            if cur.strip(): out.append(('t',cur.strip()))
            cur=''
        else: cur+=c
        i+=1
    if cur.strip(): out.append(('t',cur.strip()))
    return out
def strip_comment(l):
    q=False
    for i,c in enumerate(l):
        if c=='"': q=not q
        if c==';' and not q: return l[:i]
    return l
def ler(src=SRC):
    eq={}; items=[]
    for raw in open(src,encoding='utf-8',errors='replace'):
        l=strip_comment(raw.rstrip('\n')).strip()
        if not l: continue
        m=re.match(r'^(\w+)\s+equ\s+(.*)$',l,re.I)
        if m: eq[m.group(1)]=[x.strip() for x in m.group(2).split(',')]; continue
        m=re.match(r'^(\w+):$',l)
        if m: items.append(('label',m.group(1))); continue
        m=re.match(r'^\.(\w+)\s*(.*)$',l)
        if m: items.append((m.group(1).lower(),m.group(2))); continue
        raise Exception('?? '+l)
    return eq,items
def num(t,eq):
    if t in eq:
        assert len(eq[t])==1,t; return num(eq[t][0],eq)
    return int(t,0)
def montar(eq,items,base,textos=None,enc=None):
    """textos: dict indice_asciiz->bytes novo"""
    # passo 1 tamanhos e labels
    labels={}
    def emit(pass2):
        out=bytearray(); k=0
        for op,arg in items:
            if op=='label': labels[arg.lower()]=base+len(out); continue
            if op=='align':
                a=int(arg,0)
                while len(out)%a: out.append(0)
            elif op in('word','halfword','byte'):
                sz={'word':4,'halfword':2,'byte':1}[op]
                for _,t in parse_args(arg):
                    tl=t.lower()
                    if t in eq or re.match(r'^(0x[0-9a-f]+|\d+)$',t,re.I): v=num(t,eq)
                    else:
                        if pass2 and tl not in labels: raise Exception('label? '+t)
                        v=labels.get(tl,0)
                    out+=v.to_bytes(sz,'little')
            elif op=='asciiz':
                if textos is not None and k in textos: b=textos[k]
                else:
                    b=bytearray()
                    for kind,v in parse_args(arg):
                        if kind=='s': b+=v.encode('latin-1')
                        else: b+=bytes(num(x,eq) for x in eq[v]) if v in eq else bytes([num(v,eq)])
                out+=b+b'\0'; k+=1
            else: raise Exception(op)
        return out
    emit(False); return emit(True),labels
def strings(eq,items):
    r=[]
    for op,arg in items:
        if op=='asciiz': r.append(parse_args(arg))
    return r
