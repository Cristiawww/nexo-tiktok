"""Genera láminas SVG para importar dentro de un archivo Figma Design.
Los cuadros de métricas vacíos son deliberados: no se inventan datos.
"""
from pathlib import Path
import svgwrite

ROOT=Path(__file__).resolve().parent
W,H=1440,900
NAVY='#102E34'; INK='#152E33'; TEAL='#006F63'; MINT='#CBF3DE'; PAPER='#FAF9F5'; WHITE='#FFFFFF'; LINE='#DCE6DE'; QUIET='#657A72'; OCHRE='#DF8A51'; SAGE='#E8F6EB'; BEIGE='#F3EFE6'

def new(name):
    dw=svgwrite.Drawing(str(ROOT/name),size=(W,H),viewBox=f'0 0 {W} {H}')
    dw.add(dw.rect(insert=(0,0),size=(W,H),fill=PAPER))
    return dw

def rect(d,x,y,w,h,fill=WHITE,stroke=None,r=8,sw=1):
    kw=dict(insert=(x,y),size=(w,h),rx=r,ry=r,fill=fill)
    if stroke:kw.update(stroke=stroke,stroke_width=sw)
    return d.add(d.rect(**kw))

def line(d,x1,y1,x2,y2,color=LINE,width=1):
    return d.add(d.line((x1,y1),(x2,y2),stroke=color,stroke_width=width))

def txt(d,x,y,s,size=20,color=INK,bold=False,space=None,anchor=None,family='Arial, sans-serif'):
    opts=dict(insert=(x,y),fill=color,font_size=size,font_family=family)
    if bold:opts['font_weight']=700
    if space:opts['letter_spacing']=space
    if anchor:opts['text_anchor']=anchor
    d.add(d.text(s,**opts))

def lines(d,x,y,arr,size=18,color=INK,gap=None,bold=False):
    gap=gap or size*1.45
    for i,s in enumerate(arr):txt(d,x,y+i*gap,s,size,color,bold)

def circle(d,x,y,r,fill):d.add(d.circle(center=(x,y),r=r,fill=fill))

def pill(d,x,y,label,fill=MINT,color=INK,width=None):
    w=width or max(74,16+len(label)*8)
    rect(d,x,y,w,31,fill,None,15)
    txt(d,x+14,y+21,label,13,color,True)
    return w

def frame(d,index,title,sub):
    txt(d,72,65,'NEXO',22,INK,True,space='3px')
    txt(d,1368,65,index,13,QUIET,True,anchor='end',space='2px')
    line(d,72,84,1368,84)
    txt(d,72,149,title,48,INK,True)
    txt(d,72,186,sub,19,QUIET)

def footer(d,index):
    line(d,72,847,1368,847)
    txt(d,72,873,'NEXO  /  INVESTIGACIÓN + PRODUCTO',12,QUIET,True,space='1.2px')
    txt(d,1368,873,index,12,QUIET,anchor='end')

def sidebar(d,current):
    rect(d,0,0,278,H,NAVY,r=0)
    txt(d,38,74,'nexo.',50,WHITE,True,space='-3px')
    txt(d,40,101,'COLABORACIONES',12,'#A7DBCA',True,space='2px')
    for i,(lab,tag) in enumerate([('Cuentas','01'),('Ranking','02'),('Videos','03'),('Campaña','04')]):
        y=184+73*i
        if tag==current:
            rect(d,22,y-34,232,55,'#2A615E',r=5)
            rect(d,22,y-34,5,55,MINT,r=1)
        txt(d,45,y,tag,15,'#9DDBCB',True)
        txt(d,93,y,lab,20,WHITE,tag==current)
    txt(d,40,810,'5 CUENTAS / 10 VIDEOS',14,'#A7DBCA',True)
    txt(d,40,841,'PLAYWRIGHT · LOCAL',12,'#A7DBCA')

def uiheader(d,step,title,sub):
    sidebar(d,step)
    x=330
    txt(d,x,54,'NEXO  /  COMPARADOR DE CREADORES',13,TEAL,True,space='1.4px')
    txt(d,1360,54,f'{step} / 04',13,QUIET,True,anchor='end')
    line(d,x,76,1360,76)
    txt(d,x,144,title,49,INK,True)
    txt(d,x,181,sub,19,QUIET)

# 01 Research
D=new('01_RESEARCH.svg');frame(D,'INVESTIGACIÓN / 01','Elegir a quién contratar','La pregunta correcta no es quién tiene más seguidores, sino quién encaja mejor con el producto.')
rect(D,72,225,615,260,NAVY)
txt(D,100,265,'PROBLEMA',14,'#91DCC4',True,space='2px')
lines(D,100,317,['Un negocio local quiere anunciar','accesorios de ciclismo, pero','no sabe qué creador elegir.'],28,WHITE,40,True)
txt(D,100,453,'DECISIÓN: COLABORAR / NO COLABORAR',13,'#A4DCC8',True,space='1px')
rect(D,712,225,656,260,WHITE,LINE)
txt(D,742,265,'HIPÓTESIS DE PRODUCTO',14,TEAL,True,space='1.5px')
lines(D,742,314,['Revisar publicaciones recientes y','comentarios permite una selección','más defendible que contar seguidores.'],25,INK,41)
pill(D,742,429,'HIPÓTESIS PENDIENTE DE VALIDAR',SAGE,TEAL,300)
for i,(n,title,desc) in enumerate([
    ('01','Captura','Hasta cinco perfiles públicos'),('02','Comparación','Diez videos visibles por cuenta'),
    ('03','Patrones','Vistas, interacción, preguntas'),('04','Resultado','Candidata y evidencia disponible')]):
    x=72+i*327
    rect(D,x,523,302,248,WHITE,LINE)
    txt(D,x+22,561,n,28,TEAL,True)
    txt(D,x+22,607,title,24,INK,True)
    txt(D,x+22,642,desc,16,QUIET)
    line(D,x+22,683,x+278,683)
    txt(D,x+22,716,'PROCESO DE RESEARCH',12,QUIET,True,space='.7px')
footer(D,'01 / 08');D.save()

# 02 Methods
D=new('02_METODO_Y_PATRONES.svg');frame(D,'INVESTIGACIÓN / 02','Cómo se toma la decisión','Métricas comparables sobre publicaciones, no popularidad histórica del perfil.')
col=[('Afinidad','35 %','Tema en biografía y descripciones'),('Alcance','25 %','Mediana de vistas por video'),('Interacción','20 %','Likes / vistas por publicación'),('Conversación','10 %','Comentarios / vistas disponibles'),('Cobertura','10 %','Videos con cifras comparables')]
for i,(a,b,c) in enumerate(col):
    x=72+i*261
    rect(D,x,229,242,195,WHITE,LINE)
    txt(D,x+19,271,a,21,INK,True)
    txt(D,x+19,320,b,38,TEAL,True)
    txt(D,x+19,357,c.split(' por ')[0],14,QUIET)
    if ' por ' in c:txt(D,x+19,377,'por '+c.split(' por ',1)[1],14,QUIET)
rect(D,72,456,632,301,NAVY)
txt(D,102,501,'PATRONES A MEDIR',15,'#9DDFC4',True,space='1.6px')
lines(D,102,555,['•  ¿Qué temas aparecen en cada publicación?', '•  ¿Las vistas son constantes o irregulares?',
                '•  ¿La audiencia comenta o solo visualiza?', '•  ¿Qué preguntas se repiten?'],21,WHITE,46)
rect(D,731,456,637,301,WHITE,LINE)
txt(D,763,501,'REGLA DE EVIDENCIA',15,TEAL,True,space='1.5px')
lines(D,763,559,['Sin vistas y likes de al menos tres videos,', 'una cuenta no recibe puntuación comercial.',
                '', 'El ranking nunca predice ventas.', 'Las cuentas sin datos siguen visibles.'],20,INK,36)
footer(D,'02 / 08');D.save()

# 03 capture UI
D=new('03_CUENTAS.svg');uiheader(D,'01','Empieza por el producto.','Consulta hasta cinco cuentas desde una sesión propia de Playwright.')
rect(D,330,227,596,496,WHITE,LINE)
txt(D,358,266,'PRODUCTO',15,TEAL,True,space='1.2px')
rect(D,358,285,538,61,BEIGE,LINE,5)
txt(D,378,323,'Accesorios de ciclismo',20,INK)
txt(D,358,397,'CUENTAS DE TIKTOK',15,TEAL,True,space='1.2px')
rect(D,358,413,538,188,PAPER,LINE,5)
lines(D,378,454,['@creador_1','@creador_2','@creador_3','@creador_4','@creador_5'],20,QUIET,30)
rect(D,358,639,538,59,TEAL,r=5)
txt(D,627,675,'Analizar cuentas',20,WHITE,True,anchor='middle')
rect(D,955,227,407,228,NAVY)
txt(D,988,269,'SESIÓN LOCAL',15,'#A7E2CF',True,space='1px')
txt(D,988,327,'Playwright + Chrome',25,WHITE,True)
lines(D,988,370,['Inicio de sesión manual','Perfil aislado de NEXO'],16,'#CBE6DB',25)
rect(D,955,475,407,248,WHITE,LINE)
txt(D,986,515,'CUENTAS EN ESTUDIO',15,TEAL,True)
txt(D,986,601,'0',66,INK,True)
txt(D,1078,602,'perfiles',22,QUIET)
txt(D,986,676,'Estado: sin consulta',16,QUIET)
footer(D,'03 / 08');D.save()

# 04 compare UI
D=new('04_RANKING.svg');uiheader(D,'02','Comparación','Cinco cuentas en la misma escala de observación.')
rect(D,330,221,1033,92,WHITE,LINE)
for i,(lab,val) in enumerate([('CUENTAS','—'),('VIDEOS MEDIDOS','—'),('SECTOR','Ciclismo')]):
    x=358+i*331
    txt(D,x,255,lab,14,QUIET,True)
    txt(D,x,291,val,25,TEAL,True)
rect(D,330,340,1033,385,WHITE,LINE)
labels=[('CUENTA',365),('TEMA',613),('VISTAS',746),('INTERACCIÓN',893),('VIDEOS',1075),('ESTADO',1220)]
rect(D,347,357,999,53,NAVY,r=3)
for label,x in labels:txt(D,x,390,label,13,WHITE,True)
for i in range(5):
    y=446+i*53
    if i%2==0:rect(D,347,y-27,998,49,SAGE,r=2)
    txt(D,365,y,'@usuario_'+str(i+1),18,INK,True)
    for x in [613,746,893,1075]:txt(D,x,y,'—',22,QUIET)
    txt(D,1220,y,'SIN DATOS',13,QUIET,True)
txt(D,349,771,'SIN MÉTRICAS, NO HAY CANDIDATO GANADOR.',16,TEAL,True,space='.3px')
footer(D,'04 / 08');D.save()

# 05 videos UI
D=new('05_VIDEOS.svg');uiheader(D,'03','Dentro de cada video.','Mismas métricas, una publicación a la vez.')
rect(D,330,227,1033,79,WHITE,LINE)
txt(D,354,261,'CUENTA',13,TEAL,True)
txt(D,355,293,'@usuario',20,INK,True)
pill(D,1130,249,'10 VIDEOS MÁX.',SAGE,TEAL,180)
for i in range(3):
    y=329+150*i
    rect(D,330,y,1033,130,WHITE,LINE)
    rect(D,349,y+17,92,97,NAVY,r=4)
    txt(D,395,y+75,f'{i+1:02}',30,MINT,True,anchor='middle')
    txt(D,468,y+57,'Publicación '+f'{i+1:02}',23,INK,True)
    txt(D,468,y+91,'Contenido por verificar',15,QUIET)
    for j,(key,x) in enumerate([('VISTAS',819),('ME GUSTA',996),('COMENTARIOS',1169)]):
        txt(D,x,y+43,key,13,QUIET,True)
        txt(D,x,y+85,'—',32,INK,True)
txt(D,343,824,'La extracción registra datos visibles. No descarga videos MP4.',14,QUIET)
footer(D,'05 / 08');D.save()

# 06 campaign UI
D=new('06_CAMPANA.svg');uiheader(D,'04','La elección, con pruebas.','Un perfil gana por evidencia comparable, no por seguidores.')
rect(D,330,229,615,400,MINT)
txt(D,359,273,'CANDIDATA PRINCIPAL',15,TEAL,True,space='1px')
txt(D,359,368,'Por determinar',52,INK,True)
line(D,359,392,907,392,'#A8D1BC')
lines(D,359,442,['El sistema espera publicaciones con', 'vistas y likes para calcular el ranking.'],20,INK,33)
rect(D,359,529,243,49,TEAL,r=4)
txt(D,481,560,'Revisar ranking',17,WHITE,True,anchor='middle')
rect(D,966,229,397,400,WHITE,LINE)
txt(D,994,274,'CRITERIOS',15,TEAL,True)
for i,c in enumerate(['01  Afinidad','02  Alcance','03  Interacción','04  Conversación','05  Cobertura']):
    y=317+i*56
    txt(D,995,y,c,20,INK,True)
    line(D,992,y+16,1338,y+16)
rect(D,330,659,1033,112,NAVY)
txt(D,357,698,'SIGUIENTE PASO COMERCIAL',14,'#9BE2BF',True,space='1.3px')
txt(D,357,735,'Un enlace o código de campaña permite medir visitas y ventas reales.',21,WHITE)
footer(D,'06 / 08');D.save()

# 07 brand+atomic
D=new('07_LINEA_GRAFICA_ATOMIC.svg');frame(D,'DISEÑO / 07','Un sistema, no pantallas sueltas','Identidad visual y componentes para Figma Design.')
for i,(c,n,code) in enumerate([(NAVY,'PETRÓLEO',NAVY),(TEAL,'VERDE TINTA',TEAL),(MINT,'MENTA',MINT),(PAPER,'MARFIL',PAPER),(OCHRE,'COBRE',OCHRE)]):
    x=72+i*260
    rect(D,x,221,239,135,c,None,8)
    txt(D,x,384,n,14,INK,True)
    txt(D,x,408,code,14,QUIET)
rect(D,72,462,620,322,WHITE,LINE)
txt(D,98,505,'JERARQUÍA',14,TEAL,True,space='1px')
txt(D,98,560,'Elegir bien.',47,INK,True)
txt(D,98,607,'Space Grotesk / titulares',18,QUIET)
txt(D,98,649,'La investigación decide.',22,INK)
txt(D,98,686,'DM Sans / lectura y formularios',17,QUIET)
rect(D,98,715,202,48,TEAL,r=5);txt(D,199,745,'Analizar',17,WHITE,True,anchor='middle')
rect(D,729,462,639,322,WHITE,LINE)
txt(D,754,504,'ATOMIC DESIGN',14,TEAL,True,space='1px')
for i,(lab,what) in enumerate([('ÁTOMO','Botón / etiqueta'),('MOLÉCULA','Campo + acción'),('ORGANISMO','Tarjeta de cuenta'),('PLANTILLA','Menú + panel'),('PÁGINA','Ranking completo')]):
    y=545+i*44
    pill(D,753,y-23,lab,SAGE,TEAL,127)
    txt(D,914,y-3,what,18,INK)
footer(D,'07 / 08');D.save()

# 08 Scientific frameworks
D=new('08_BIGFIVE_BENFORD.svg');frame(D,'ANÁLISIS / 08','Qué se puede afirmar','El dato observado y el dato inferido no son lo mismo.')
rect(D,72,230,625,555,WHITE,LINE)
txt(D,103,274,'BIG FIVE / OCEAN',16,TEAL,True,space='1.4px')
for i,(l,n) in enumerate([('O','Apertura'),('C','Responsabilidad'),('E','Extraversión'),('A','Amabilidad'),('N','Neuroticismo')]):
    y=324+i*69
    circle(D,137,y,22,MINT);txt(D,137,y+7,l,21,TEAL,True,anchor='middle')
    txt(D,176,y+7,n,23,INK,True)
line(D,100,687,666,687)
lines(D,104,719,['No inferir personalidad por seguidores, likes o', 'comentarios. Solo cuestionarios voluntarios válidos.'],17,QUIET,28)
rect(D,721,230,647,555,NAVY)
txt(D,751,273,'LEY DE BENFORD',16,'#A9E4CB',True,space='1.5px')
txt(D,751,321,'Frecuencia teórica de primeros dígitos',19,WHITE)
vals=[30.1,17.6,12.5,9.7,7.9,6.7,5.8,5.1,4.6]
for i,v in enumerate(vals):
    x=771+i*64
    h=v*8.3
    rect(D,x,634-h,38,h,MINT,r=1)
    txt(D,x+19,659,str(i+1),15,WHITE,True,anchor='middle')
    txt(D,x+19,622-h,f'{v:.1f}',11,WHITE,anchor='middle')
line(D,750,686,1327,686,'#71938B')
lines(D,752,719,['Con 5 perfiles no hay muestra adecuada.', 'Un desajuste no demuestra fraude.'],17,'#C5E6DB',28)
footer(D,'08 / 08');D.save()
print('SVGs creados:',len(list(ROOT.glob('*.svg'))))

# 09 conclusions (conditional; cannot invent the winning account)
D=new('09_CONCLUSIONES.svg');frame(D,'RESULTADOS / 09','De la comparación a la acción','Conclusiones sujetas a la información recuperada en cada consulta.')
rect(D,72,222,603,479,NAVY)
txt(D,100,268,'CRITERIO PARA ELEGIR',14,'#A5E2C7',True,space='1.5px')
lines(D,100,326,['¿La cuenta publica sobre el tema?', '¿Tiene 3 o más videos medibles?',
             '¿Se conocen vistas y likes?', '¿Hay conversación comparable?'],23,WHITE,60)
rect(D,99,619,535,51,'#256359',r=4)
txt(D,120,652,'SI FALTAN DATOS → SIN RECOMENDACIÓN',16,WHITE,True)
rect(D,700,222,668,479,WHITE,LINE)
txt(D,733,267,'CONCLUSIONES DEL ESTUDIO',14,TEAL,True,space='1.5px')
for i,(a,b) in enumerate([('Observación','Publicaciones, cifras y fecha de consulta.'),
             ('Comparación','Mediana de vistas e interacción por video.'),
             ('Decisión','Preselección basada en datos comparables.'),
             ('Evaluación','Un código de campaña para medir resultados.')]):
    y=318+i*91
    txt(D,733,y,a,22,INK,True)
    txt(D,733,y+29,b,16,QUIET)
    line(D,733,y+49,1332,y+49)
txt(D,72,754,'RESULTADO ACTUAL: AÚN NO HAY DATOS NUEVOS PARA DECLARAR UNA CUENTA GANADORA.',16,TEAL,True)
footer(D,'09 / 09');D.save()
