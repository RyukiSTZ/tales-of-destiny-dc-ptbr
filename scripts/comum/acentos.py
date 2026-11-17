#!/usr/bin/env python3
"""Desenha as letras acentuadas na fonte do Tales of Destiny DC (SLPS_258.42).

A fonte de diálogo/menu fica no executável: 24x24 pixels, 4 bits por pixel,
um glifo por caractere ASCII (glifo = código - 0x20), a partir do offset
0xE68C0 do arquivo. A tabela de larguras (8 bytes por caractere, ver
patch/ASM/font_tables.asm da Life Bottle) fica no offset 0xD88B0.

Os símbolos abaixo não aparecem em nenhum texto visível do jogo em inglês
(só em linhas de depuração), então viram as letras acentuadas.

Uso: python acentos.py SLPS_258.42_original SLPS_258.42_saida [previa.png]
"""
import sys
from PIL import Image, ImageDraw

FONTE = 0xE68C0
LARG = 0xD88B0
TAM = 24 * 24 // 2

# símbolo -> (letra base, acento)
MAPA = {
    "#": ("a", "agudo"), "$": ("a", "grave"), "&": ("a", "circ"), ";": ("a", "til"),
    "=": ("e", "agudo"), "@": ("e", "circ"),
    "\\": ("i", "agudo"),
    "^": ("o", "agudo"), "_": ("o", "circ"), "`": ("o", "til"),
    "{": ("u", "agudo"),
    "|": ("c", "cedilha"),
    "}": ("E", "agudo"),
}
LETRA = {"#": "á", "$": "à", "&": "â", ";": "ã", "=": "é", "@": "ê", "\\": "í",
         "^": "ó", "_": "ô", "`": "õ", "{": "ú", "|": "ç", "}": "É"}


def ler(d, ch):
    o = FONTE + (ord(ch) - 0x20) * TAM
    return [[(d[o + (y * 24 + x) // 2] >> (4 * (x % 2))) & 0xF for x in range(24)] for y in range(24)]


def gravar(d, ch, g):
    o = FONTE + (ord(ch) - 0x20) * TAM
    for y in range(24):
        for x in range(0, 24, 2):
            d[o + (y * 24 + x) // 2] = (g[y][x] & 0xF) | ((g[y][x + 1] & 0xF) << 4)


def centro(g):
    xs = [x for y in range(24) for x in range(24) if g[y][x] >= 8]
    return sum(xs) / len(xs)


def nucleo(acento, cx, topo):
    """Desenha o traço do acento em 4x e reduz para 24x24 (tons 0-15)."""
    E = 4
    im = Image.new("L", (24 * E, 24 * E), 0)
    dr = ImageDraw.Draw(im)
    w = int(1.9 * E)
    c = cx * E + E / 2
    t = topo * E
    if acento == "agudo":
        dr.line([(c + 2.2 * E, t + 0.3 * E), (c - 1.2 * E, t + 3.0 * E)], fill=255, width=w)
    elif acento == "grave":
        dr.line([(c - 2.2 * E, t + 0.3 * E), (c + 1.2 * E, t + 3.0 * E)], fill=255, width=w)
    elif acento == "circ":
        dr.line([(c - 2.8 * E, t + 3.0 * E), (c, t + 0.3 * E), (c + 2.8 * E, t + 3.0 * E)], fill=255, width=w, joint="curve")
    elif acento == "til":
        pts = [(c - 3.4 * E, t + 2.8 * E), (c - 2.0 * E, t + 1.0 * E), (c - 0.6 * E, t + 1.2 * E),
               (c + 0.6 * E, t + 2.4 * E), (c + 2.0 * E, t + 2.6 * E), (c + 3.4 * E, t + 0.8 * E)]
        dr.line(pts, fill=255, width=w, joint="curve")
    elif acento == "cedilha":
        dr.line([(c, t), (c, t + 1.2 * E), (c + 1.4 * E, t + 1.6 * E), (c + 1.0 * E, t + 2.6 * E),
                 (c - 1.4 * E, t + 3.0 * E)], fill=255, width=int(1.6 * E), joint="curve")
    im = im.resize((24, 24), Image.LANCZOS)
    return [[min(15, round(im.getpixel((x, y)) / 255 * 15)) if im.getpixel((x, y)) > 50 else 0
             for x in range(24)] for y in range(24)]


def contorno(n):
    """Contorno escuro no estilo da fonte: 3 colado no traço, 1 no anel de fora."""
    out = [[0] * 24 for _ in range(24)]
    for y in range(24):
        for x in range(24):
            if n[y][x]:
                out[y][x] = max(n[y][x], 4)
                continue
            perto = lambda r: any(0 <= y + j < 24 and 0 <= x + i < 24 and n[y + j][x + i]
                                  for j in range(-r, r + 1) for i in range(-r, r + 1))
            out[y][x] = 3 if perto(1) else (1 if perto(2) else 0)
    return out


def encolher(g, de, ate, novo_de):
    """Encolhe as linhas de..ate (inclusive) para novo_de..ate (para o É caber)."""
    src = Image.new("L", (24, ate - de + 1))
    for y in range(de, ate + 1):
        for x in range(24):
            src.putpixel((x, y - de), g[y][x] * 17)
    dst = src.resize((24, ate - novo_de + 1), Image.LANCZOS)
    novo = [[0] * 24 for _ in range(24)]
    for y in range(novo_de, ate + 1):
        for x in range(24):
            novo[y][x] = min(15, round(dst.getpixel((x, y - novo_de)) / 17))
    for y in range(ate + 1, 24):
        novo[y] = list(g[y])
    return novo


def montar(d):
    previa = []
    for simb, (base, acento) in MAPA.items():
        g = [list(r) for r in ler(d, base)]
        if base == "E":
            g = encolher(g, 1, 20, 3)
        if base == "i":
            for y in range(0, 7):  # tira o pingo do i; o acento entra no lugar
                g[y] = [0] * 24
        cx = round(centro(g))
        if acento == "cedilha":
            n = nucleo(acento, cx, 19.9)
        else:
            n = nucleo(acento, cx + (0.6 if acento in ("agudo", "grave") and base == "i" else 0), 1.6 if base == "i" else (-0.9 if base == "E" else 0.6))
        a = contorno(n)
        g = [[max(g[y][x], a[y][x]) if a[y][x] >= 4 or g[y][x] < 4 else g[y][x] for x in range(24)] for y in range(24)]
        gravar(d, simb, g)
        # larguras: iguais às da letra base
        ob, os_ = LARG + (ord(base) - 0x20) * 8, LARG + (ord(simb) - 0x20) * 8
        d[os_:os_ + 8] = d[ob:ob + 8]
        previa.append(simb)
    return previa


def imagem(d, chars, escala=4):
    W = 26
    im = Image.new("L", (len(chars) * W, 26), 30)
    for i, ch in enumerate(chars):
        g = ler(d, ch)
        for y in range(24):
            for x in range(24):
                im.putpixel((i * W + x, y), g[y][x] * 17)
    return im.resize((im.width * escala, im.height * escala), Image.NEAREST)


if __name__ == "__main__":
    d = bytearray(open(sys.argv[1], "rb").read())
    assert d[:4] == b"\x7fELF", "não é o executável do jogo"
    assert d[LARG:LARG + 8] == bytes([2, 3, 1, 3, 3, 3, 2, 2]), "tabela de larguras não está onde esperado"
    p = montar(d)
    open(sys.argv[2], "wb").write(d)
    if len(sys.argv) > 3:
        imagem(d, "aeiocE" + "".join(p)).save(sys.argv[3])
    print("ok:", " ".join(f"{s}={LETRA[s]}" for s in p))
