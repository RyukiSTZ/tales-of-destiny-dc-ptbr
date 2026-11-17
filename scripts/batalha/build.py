import sys,re; sys.path.insert(0,'/home/claude/slps'); import asm, checar
eq,it=asm.ler()
S=asm.strings(eq,it)
def longo(t):
    m=re.match(r'^([A-Z]+)> (.*)$',t)
    if m: return '{COLOR_START}{%s}{COLOR_END}: %s'%(m.group(1),m.group(2))
    return t
textos={}
for l in open('pt_curto.txt',encoding='utf-8'):
    k,t=l.rstrip('\n').split('|',1); k=int(k); t=longo(t)
    # checar mesmos códigos
    en=''.join('{'+v+'}' if kind=='t' else '' for kind,v in S[k])
    pc=''.join(re.findall(r'\{\w+\}',t))
    assert en==pc,(k,en,pc)
    b=bytearray()
    for tok in re.split(r'(\{\w+\})',t):
        if not tok: continue
        if tok.startswith('{'): b+=bytes(asm.num(x,eq) for x in eq[tok[1:-1]])
        else:
            j=checar.jogo(tok); assert all(32<=ord(c)<127 for c in j),(k,j); b+=j.encode('latin-1')
    textos[k]=bytes(b)
assert len(textos)==len(S)
BASE=0x4b88b4; FO=0x151f4; LIM=0x1d8f8
out,lab=asm.montar(eq,it,BASE,textos)
print('tam',len(out),'limite',LIM-FO, 'sobra',LIM-FO-len(out))
if len(out)<=LIM-FO:
    d=bytearray(open('/home/claude/lifebottle/tales-of-destiny-dc/patch/DAT_FILES_PATCHED/00013.bin','rb').read())
    d[FO:LIM]=out+b'\0'*(LIM-FO-len(out))
    open('00013.bin','wb').write(d); print('ok')
