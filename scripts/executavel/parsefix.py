import sys,json; sys.path.insert(0,'/home/claude/slps'); import slps
d=open('/home/claude/backup_tod/fonte/SLPS_258.42_ingles_original','rb').read()
rev={}
for k,v in slps.TBL.items():
    if len(v)>=3: rev.setdefault(v,k)
def parse(a,z):
    i=a; out=[]
    while i<z:
        if d[i]==0: i+=1; continue
        s=i; txt=''
        while d[i]!=0:
            c=d[i]
            if c in (4,5,6,7,0xb,0xc,0xd,0xe,0x13,0x14): txt+=rev.get(d[i:i+5],''.join('<$%02X>'%x for x in d[i:i+5])); i+=5
            elif c>=0x80: txt+='<$%02X><$%02X>'%(d[i],d[i+1]); i+=2
            elif c==1: txt+='[LINE]'; i+=1
            else: txt+=chr(c); i+=1
        n=i
        while d[n]==0: n+=1
        out.append((s,i-s,n-s,txt))
    return out
if __name__=='__main__':
    allv=[]
    for a,z in [(0x19a000,0x19a120),(0x19a800,0x19a860),(0x19b0c0,0x19b2a0),(0x1aa9f0,0x1aaa40),(0x1ab5f0,0x1ab830),(0x1bf4c0,0x1bf4d8)]:
        for x in parse(a,z): print(hex(x[0]),x[1],x[2],x[3]); allv.append(x)
    json.dump(allv,open('fixos3_en.json','w'))
