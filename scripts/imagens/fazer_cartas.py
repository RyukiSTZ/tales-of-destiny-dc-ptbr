import sys,os; sys.path.insert(0,'/home/claude/img'); import carta, tim2
from PIL import Image
R='/home/claude/recebido_H/'
jobs=[
('00024.pak1',0x1a870,['Desde então, o mundo','vem se recuperando aos poucos.']),
('00024.pak1',0x30,['E assim...']),
('00024.pak1',0x350b0,['A formação da Aetherosfera','cobrou seu preço, e vai demorar','um tempo até tudo voltar','totalmente ao normal...']),
('00024.pak1',0x4f8f0,['Até hoje,','nós, humanos, ainda erramos,','e às vezes ainda nos perdemos.']),
('00025.pak1',0x1a870,['Mas nessas horas,','só precisamos','manter a cabeça erguida','e seguir em frente.']),
('00025.pak1',0x30,['Acho que ainda haverá momentos','de tristeza ou desânimo.']),
('00025.pak1',0x350b0,['Confiaram a nós um','futuro feliz, e acho que','estamos à altura.']),
('00025.pak1',0x4f8f0,['Sei que não sou a pessoa mais confiável,','mas, mesmo assim, continuem cuidando','de nós de onde estiverem.']),
('00027.pak1',0x350b0,['E você também,','Dymlos.']),
('00027.pak1',0x4f8f0,['Aos meus amigos insubstituíveis,','lá de baixo do céu.','Assinado,','Stahn Aileron']),
]
os.makedirs('saida',exist_ok=True); prev=[]
dados={}
for f,off,lines in jobs:
    d=dados.setdefault(f,bytearray(open(R+f,'rb').read()))
    info=next(tim2.pics(bytes(d),off)); im=tim2.para_png(bytes(d),info)
    bg,m=carta.limpar(im); g=carta.linhas_texto(m); c=carta.cor_texto(im,m)
    tops=[a for a,b in g]
    if len(tops)!=len(lines): print('LINHAS',f,hex(off),tops,len(lines)); 
    if len(tops)<len(lines): continue
    # assinatura: manter alinhamentos originais? centralizado ok
    out=carta.escrever(bg,lines,tops[:len(lines)] if len(tops)==len(lines) else tops,c)
    nb=tim2.codificar_8bpp(bytes(d),info,out); o=info['img']; d[o:o+len(nb)]=nb
    prev.append(tim2.para_png(bytes(d),info))
for f,d in dados.items(): open('saida/'+f,'wb').write(d)
W=480; sheet=Image.new('RGBA',(960,224*((len(prev)+1)//2)))
for i,p in enumerate(prev): sheet.paste(p,((i%2)*480,(i//2)*224))
sheet.save('/tmp/claude-0/-home-claude/5bd5e35d-ae6d-5749-b2fa-83e1bda3ea92/scratchpad/cartas.png')
