import struct
def decomp(d, rle=True):
    t, cs, ds = struct.unpack('<BII', d[:9])
    buf = bytearray(4096); r = 0xFEF
    out = bytearray(); i = 9
    while len(out) < ds:
        flags = d[i]; i += 1
        for bit in range(8):
            if len(out) >= ds: break
            if flags & (1 << bit):
                c = d[i]; i += 1
                out.append(c); buf[r] = c; r = (r+1) & 0xFFF
            else:
                b1, b2 = d[i], d[i+1]; i += 2
                if t == 3 and rle and (b2 & 0x0F) == 0x0F:
                    h = b2 >> 4
                    if h == 0:
                        n = b1 + 19; c = d[i]; i += 1
                    else:
                        n = h + 3; c = b1
                    for _ in range(n):
                        out.append(c); buf[r] = c; r = (r+1) & 0xFFF
                    continue
                off = b1 | ((b2 & 0xF0) << 4); n = (b2 & 0x0F) + 3
                for k in range(n):
                    c = buf[(off + k) & 0xFFF]
                    out.append(c); buf[r] = c; r = (r+1) & 0xFFF
    return bytes(out[:ds])

def comp(data, LIM=4096, lazy=True):
    """Compressor tipo 3 (só literais e referências; sem RLE)."""
    n = len(data); out = bytearray(); i = 0
    tab = {}
    MAXD = 4096 - 18
    def add(p):
        if p + 3 <= n:
            tab.setdefault(data[p:p+3], []).append(p)
    while i < n:
        flagpos = len(out); out.append(0); flags = 0
        for bit in range(8):
            if i >= n: break
            best = 0; bq = 0
            if i + 3 <= n:
                cands = tab.get(data[i:i+3])
                if cands:
                    for q in reversed(cands[-LIM:]):
                        if i - q > MAXD: break
                        L = 3
                        while L < 17 and i + L < n and data[q+L] == data[i+L]: L += 1
                        if L > best: best, bq = L, q
                        if L == 17: break
            run = 1
            while run < 274 and i + run < n and data[i+run] == data[i]: run += 1
            if run >= 4 and run > best:
                if run <= 18:
                    out.append(data[i]); out.append(((run - 3) << 4) | 0x0F)
                else:
                    out.append(run - 19); out.append(0x0F); out.append(data[i])
                for k in range(run): add(i + k)
                i += run
                continue
            if best >= 3:
                off = (0xFEF + bq) & 0xFFF
                out.append(off & 0xFF); out.append(((off >> 4) & 0xF0) | (best - 3))
                for k in range(best): add(i + k)
                i += best
            else:
                flags |= 1 << bit; out.append(data[i]); add(i); i += 1
        out[flagpos] = flags
    return struct.pack('<BII', 3, len(out), n) + bytes(out)

def _best(data, i, n, tab, LIM):
    best=0; bq=0
    if i+3<=n:
        c=tab.get(data[i:i+3])
        if c:
            for q in reversed(c[-LIM:]):
                if i-q>4078: break
                L=3
                while L<17 and i+L<n and data[q+L]==data[i+L]: L+=1
                if L>best: best,bq=L,q
                if L==17: break
    run=1
    while run<274 and i+run<n and data[i+run]==data[i]: run+=1
    return best,bq,run

def comp2(data, LIM=1024):
    """Compressor tipo 3 com parsing por programação dinâmica (custo mínimo em bits)."""
    n=len(data); tab={}
    # pré-calcula melhores opções por posição
    opts=[None]*n
    for i in range(n):
        best,bq,run=_best(data,i,n,tab,LIM)
        opts[i]=(best,bq,run)
        if i+3<=n: tab.setdefault(data[i:i+3],[]).append(i)
    # custo em bits (1 bit de flag + payload)
    INF=10**18; cost=[INF]*(n+1); choice=[None]*(n+1); cost[n]=0
    for i in range(n-1,-1,-1):
        c=9+cost[i+1]; ch=('L',1)
        best,bq,run=opts[i]
        for L in range(3,best+1):
            v=17+cost[i+L]
            if v<c: c=v; ch=('R',L,bq)
        if run>=4:
            for L in ((min(run,18),) if run<19 else (18,min(run,274))):
                if L>=19: v=25+cost[i+L]
                else: v=17+cost[i+L]
                if v<c: c=v; ch=('S',L)
        cost[i]=c; choice[i]=ch
    out=bytearray(); i=0
    while i<n:
        fp=len(out); out.append(0); flags=0
        for bit in range(8):
            if i>=n: break
            ch=choice[i]
            if ch[0]=='L':
                flags|=1<<bit; out.append(data[i]); i+=1
            elif ch[0]=='R':
                L,q=ch[1],ch[2]; off=(0xFEF+q)&0xFFF
                out.append(off&0xFF); out.append(((off>>4)&0xF0)|(L-3)); i+=L
            else:
                L=ch[1]
                if L<=18: out.append(data[i]); out.append(((L-3)<<4)|0x0F)
                else: out.append(L-19); out.append(0x0F); out.append(data[i])
                i+=L
        out[fp]=flags
    return struct.pack('<BII',3,len(out),n)+bytes(out)
