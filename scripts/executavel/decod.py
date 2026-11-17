import slps
REV={}
for k,v in slps.TBL.items():
    if v not in REV or len(k)<len(REV[v]) and not k.startswith('['):
        REV.setdefault(v,k)
# prefer bracket names for control codes; prefer plain chars for 1-2 byte
def dec(b):
    out=[];i=0
    while i<len(b):
        for L in (6,5,4,3,2,1):
            if b[i:i+L] in REV and (L>1 or True):
                t=REV[b[i:i+L]]; out.append(t); i+=L; break
        else:
            out.append('<$%02X>'%b[i]); i+=1
    return ''.join(out)
def ler(d,v):
    e=d.find(b'\0',v)
    # control codes contain zeros: walk properly
    i=v; 
    while True:
        c=d[i]
        if c==0: break
        if c in (4,5,6,7,0xb,0xc,0xd,0xe,0x13,0x14): i+=5
        elif c>=0x80 and c not in (0xb7,): i+=2
        else: i+=1
    return d[v:i]
