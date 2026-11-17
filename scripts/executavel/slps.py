#!/usr/bin/env python3
"""Ferramenta de texto do SLPS (menus) do Tales of Destiny DC.

Usa o mesmo script Atlas da Life Bottle (TODDC_All_Dump.txt) como fonte de
ponteiros e textos, mas faz a inserção em Python, com layout próprio
(bancos de memória + textos repetidos compartilhados).

  slps.py verificar                 -> reconstrói o inglês e compara
  slps.py extrair saida.txt         -> lista de entradas (id|texto) em inglês
  slps.py montar pt.txt saida.42    -> monta o SLPS com a tradução
"""
import json, re, struct, sys, os

AQUI = os.path.dirname(os.path.abspath(__file__))
HDR = 0xFF000
LB = "/home/claude/lifebottle/tales-of-destiny-dc/patch/SLPS/scripts/code"


def carregar_tbl():
    m = {}
    for raw in open(os.path.join(AQUI, "toddc.tbl"), "rb").read().decode("utf-8", "replace").split("\n"):
        raw = raw.rstrip("\r")
        if "=" not in raw:
            continue
        h, t = raw.split("=", 1)
        if h.startswith("/"):
            h = h[1:]
        t = t.replace("\\n", "")
        if t == "" and raw.endswith("=="):
            t = "="
        if not re.fullmatch(r"[0-9A-Fa-f]+", h) or len(h) % 2 or t == "":
            continue
        if t not in m:
            m[t] = bytes.fromhex(h)
    return m


TBL = carregar_tbl()
CHAVES = sorted(TBL, key=len, reverse=True)
MAXK = max(len(k) for k in CHAVES)
RAW = re.compile(r"<\$([0-9A-Fa-f]{2})>")


def codificar(texto):
    out = bytearray()
    i = 0
    while i < len(texto):
        m = RAW.match(texto, i)
        if m:
            out.append(int(m.group(1), 16)); i = m.end(); continue
        for n in range(min(MAXK, len(texto) - i), 0, -1):
            b = TBL.get(texto[i:i + n])
            if b is not None:
                out += b; i += n; break
        else:
            raise ValueError("caractere sem tabela: %r em %r" % (texto[i], texto))
    return bytes(out)


def ler_dump(path):
    """Como o Atlas: cada linha de texto é anexada; #WRITE aponta para a posição atual.
    Entrada = ponteiros seguidos + todo o texto até o próximo #WRITE/#JMP."""
    itens, secao = [], ""
    atual = None
    def fecha():
        nonlocal atual
        if atual is not None:
            itens.append(("ent", atual[0], "".join(atual[1]), atual[2]))
        atual = None
    for linha in open(path, encoding="utf-8").read().split("\n"):
        linha = linha.rstrip("\r")
        if linha.lstrip().startswith("#") or linha.lstrip().startswith("//"):
            linha = linha.lstrip()
        if linha.startswith("#JMP("):
            fecha(); itens.append(("jmp", int(re.search(r"\$(\w+)", linha).group(1), 16)))
        elif linha.startswith("#WRITE("):
            p = int(re.search(r"\$(\w+)\)", linha).group(1), 16)
            if atual is not None and atual[1]:
                fecha()
            if atual is None:
                atual = [[], [], secao]
            atual[0].append(p)
        elif linha.startswith("//Section "):
            secao = linha[10:].strip()
        elif linha.startswith("#") or linha.startswith("//") or linha == "":
            continue
        else:
            if atual is None:
                atual = [[], [], secao]
            atual[1].append(linha)
    fecha()
    return itens


def aplicar_original(itens, dados):
    pos = None
    for it in itens:
        if it[0] == "jmp":
            pos = it[1]; continue
        b = codificar(it[2])
        for p in it[1]:
            dados[p:p + 4] = struct.pack("<I", pos + HDR)
        dados[pos:pos + len(b)] = b
        pos += len(b)


def bancos():
    secs = json.load(open(os.path.join(LB, "sectionsSLPS.json")))["items"]
    lista = []
    for b in secs:
        if "SLPS" in b["File"]:
            lista.append((int(b["Sections"][0]["TextStart"], 16), int(b["Sections"][-1]["TextEnd"], 16)))
    vistos = set(lista)
    for m in json.load(open(os.path.join(LB, "memoryBanks.json")))["memoryBanks"]:
        if "SLPS" in m["File"]:
            r = (int(m["TextStart"], 16), int(m["TextEnd"], 16))
            if r not in vistos:
                vistos.add(r); lista.append(r)
    return lista


def montar(itens, textos, dados, compartilhar=True):
    """textos: dict indice->texto traduzido (indice = ordem das entradas)."""
    bl = bancos()
    bi = 0
    pos, fim = bl[0]
    feitos = {}
    usado = []
    ent = [it for it in itens if it[0] == "ent"]
    for i, it in enumerate(ent):
        t = textos.get(i, it[2])
        b = codificar(t)
        if compartilhar and b in feitos:
            alvo = feitos[b]
        else:
            # o fim do banco é inclusivo na planilha da Life Bottle
            while pos + len(b) > fim + 1:
                usado.append((bl[bi][0], pos))
                bi += 1
                if bi >= len(bl):
                    raise SystemExit("SEM ESPACO: faltou lugar na entrada %d (%s)" % (i, t))
                pos, fim = bl[bi]
            alvo = pos
            dados[pos:pos + len(b)] = b
            pos += len(b)
            feitos[b] = alvo
        for p in it[1]:
            dados[p:p + 4] = struct.pack("<I", alvo + HDR)
    usado.append((bl[bi][0], pos))
    return usado, bl


if __name__ == "__main__":
    cmd = sys.argv[1]
    itens = ler_dump(os.path.join(AQUI, "all_en.txt"))
    if cmd == "verificar":
        d = bytearray(open(os.path.join(AQUI, "jp.42"), "rb").read())
        aplicar_original(itens, d)
        alvo = open(os.path.join(AQUI, "test.42"), "rb").read()
        dif = sum(1 for a, b in zip(d, alvo) if a != b)
        print("entradas:", sum(1 for i in itens if i[0] == "ent"), "bytes diferentes:", dif)
    elif cmd == "extrair":
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            for i, it in enumerate([x for x in itens if x[0] == "ent"]):
                f.write("%d|%s|%s\n" % (i, it[3], it[2]))
    elif cmd == "montar":
        textos = {}
        for linha in open(sys.argv[2], encoding="utf-8"):
            linha = linha.rstrip("\n")
            if not linha or linha.startswith(";"):
                continue
            i, _, t = linha.split("|", 2)
            textos[int(i)] = t
        d = bytearray(open(os.path.join(AQUI, "jp.42"), "rb").read())
        # parte do inglês final (mantém o que a Life Bottle mudou fora do texto)
        aplicar_original(itens, d)
        usado, bl = montar(itens, textos, d)
        for (ini, fimu), (a, z) in zip(usado, bl):
            print("banco %06X-%06X usado ate %06X (%d livres)" % (a, z, fimu, z + 1 - fimu))
        open(sys.argv[3], "wb").write(d)

def _dbg():
    itens = ler_dump(os.path.join(AQUI, "all_en.txt"))
    d = bytearray(open(os.path.join(AQUI, "jp.42"), "rb").read())
    aplicar_original(itens, d)
    alvo = open(os.path.join(AQUI, "test.42"), "rb").read()
    difs = [i for i, (a, b) in enumerate(zip(d, alvo)) if a != b]
    print(hex(difs[0]), hex(difs[-1]), len(difs))
    i = difs[0]
    print(d[i-16:i+32]); print(alvo[i-16:i+32])
