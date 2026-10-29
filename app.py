"""NEXO · Selección de creadores con datos de TikTok realmente observados.
No incorpora perfiles, videos ni resultados ficticios.
"""
from __future__ import annotations
import html
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from analisis_negocio import numero_compacto, oportunidades
from evaluacion import comparar
from scraper import scrape_batch, usuarios_unicos
from sesion import RUTA_SESION

st.set_page_config(page_title='NEXO / Colaboraciones',page_icon='◉',layout='wide',initial_sidebar_state='expanded')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--ink:#152E33;--dark:#102E34;--teal:#006F63;--mint:#CBF3DE;--paper:#FAF9F5;--line:#DFE5E1;--quiet:#647874;--orange:#DF8A51}
html,body,.stApp,button,input,textarea{font-family:'DM Sans',sans-serif!important}
.stApp{background:#FAF9F5!important;color:#152E33!important}
.main .block-container{max-width:1320px;padding:2rem 2.8rem 4rem}
header[data-testid='stHeader']{background:transparent}
#MainMenu,footer{visibility:hidden}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;color:#152E33!important;letter-spacing:-.052em!important}
h1{font-size:3.05rem!important;line-height:1.06!important;font-weight:700!important}
h2{font-size:1.45rem!important}
[data-testid='stSidebar']{background:#102E34!important}
[data-testid='stSidebar'] *{color:#ECF5EF!important}
[data-testid='stSidebar'] [data-baseweb='radio'] label{padding:13px 12px!important;border-radius:5px!important;margin:3px 0!important}
[data-testid='stSidebar'] [data-baseweb='radio'] label:hover{background:#244449!important}
[data-testid='stSidebar'] [data-baseweb='radio'] label:has(input:checked){background:#2D615F!important;border-left:3px solid #C8F5D4!important}
[data-testid='stSidebar'] hr{border-color:#406066!important}
[data-testid='stWidgetLabel'] p{color:#152E33!important;font-weight:700!important}
[data-testid='stTextInput'] input,[data-testid='stTextArea'] textarea,[data-baseweb='select']>div{background:white!important;color:#152E33!important;border:1px solid #B6C6C1!important;border-radius:6px!important}
[data-testid='stTextInput'] input::placeholder,[data-testid='stTextArea'] textarea::placeholder{color:#71837D!important}
.stButton>button[kind='primary']{background:#006F63!important;color:white!important;border-radius:6px!important;border:0!important;font-weight:700!important;min-height:48px}
.stButton>button[kind='secondary'],[data-testid='stDownloadButton'] button{background:white!important;color:#152E33!important;border:1px solid #B4C7C0!important;border-radius:6px!important;min-height:45px}
[data-testid='stMetric']{border-left:3px solid #006F63!important;background:white!important;border-radius:4px!important;border-top:1px solid #DFE5E1!important;border-right:1px solid #DFE5E1!important;border-bottom:1px solid #DFE5E1!important;padding:17px!important}
[data-testid='stMetricLabel'] p{font-size:.80rem!important;color:#57716B!important}
[data-testid='stMetricValue']{font-family:'Space Grotesk',sans-serif!important;color:#152E33!important}
[data-testid='stFileUploader']{background:white!important;border-radius:5px!important;border:1px solid #DFE5E1!important;padding:7px!important}
[data-testid='stDataFrame']{border-radius:5px;border:1px solid #DFE5E1}
[data-testid='stAlert']{border-radius:5px}
.nexo-top{display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid #D7E0DB;padding-bottom:12px;margin-bottom:26px;color:#4B6963;font-size:.76rem;letter-spacing:.1em;font-weight:700}
.nexo-heading{font-size:3.1rem;font-weight:700;letter-spacing:-.065em;line-height:1.04;font-family:'Space Grotesk',sans-serif;color:#132D32;margin:0 0 14px}
.nexo-sub{color:#5C746E;font-size:1.05rem;margin:0 0 29px;max-width:680px}
.nexo-cover{background:#12363B;color:#E4F4EB;border-radius:6px;padding:25px 31px;min-height:206px;position:relative;overflow:hidden}
.nexo-cover:after{content:'';position:absolute;right:-80px;top:-75px;width:270px;height:270px;border-radius:50%;border:45px solid #417D74;opacity:.33}
.nexo-cover .index{color:#9DE3BB;font-size:.75rem;letter-spacing:.16em;font-weight:700}
.nexo-cover h2{color:#F6FBF6!important;font-size:2.0rem!important;line-height:1.1!important;margin:9px 0!important;max-width:370px}
.nexo-cover p{color:#D0E6DC;font-size:.93rem;max-width:350px}
.nexo-profile{border:1px solid #DCE6DF;background:#fff;border-radius:6px;padding:22px;margin-bottom:9px;min-height:177px}
.nexo-profile .handle{color:#00796C;font-size:.84rem;font-weight:700;margin:0 0 11px}
.nexo-profile h3{font-size:1.21rem!important;min-height:33px;margin:0 0 6px!important;overflow-wrap:anywhere}
.nexo-profile .number{font-size:1.75rem;color:#173A3D;font-family:'Space Grotesk',sans-serif;font-weight:700;letter-spacing:-.06em}
.nexo-profile .meta{font-size:.75rem;color:#667973;margin-top:10px}
.nexo-rule{height:1px;background:#D8E2DC;margin:22px 0}
.nexo-brand{font-size:2.75rem;font-family:'Space Grotesk',sans-serif;font-weight:700;letter-spacing:-.11em;color:#E8FFF0!important;margin:0}
.nexo-mini{color:#A7D5C7!important;letter-spacing:.19em;font-size:.7rem;font-weight:700}
.nexo-tag{color:#007F6A!important;font-size:.74rem;letter-spacing:.13em;font-weight:700}
.nexo-flag{display:inline-block;border-radius:3px;background:#E0F5EA;color:#23634E!important;padding:6px 9px;font-size:.75rem;font-weight:700}
.nexo-winner{padding:26px;background:#C9F0DA;border-left:6px solid #006F63;border-radius:4px}
.nexo-winner .username{color:#17463E!important;font-family:'Space Grotesk',sans-serif;font-size:2.3rem;font-weight:700;letter-spacing:-.05em}
.nexo-foot{font-size:.78rem;color:#677C73;margin-top:22px}
@media(max-width:800px){.main .block-container{padding:1.25rem 1rem 4rem}.nexo-heading{font-size:2.2rem}}
</style>''',unsafe_allow_html=True)


def e(value):
    return html.escape(str(value if value is not None else ''),quote=True)


def fmt(value):
    n=numero_compacto(value)
    if n is None:return '—'
    if n>=1_000_000:return f'{n/1_000_000:.1f} M'
    if n>=10_000:return f'{n/1000:.1f} mil'
    return f'{n:,.0f}'.replace(',','.')


def section_head(n,title,short=''):
    st.markdown(f'<div class="nexo-top"><span>NEXO / {e(n)}</span><span>ESTUDIO DE CREADORES</span></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="nexo-heading">{e(title)}</div>',unsafe_allow_html=True)
    if short:st.markdown(f'<p class="nexo-sub">{e(short)}</p>',unsafe_allow_html=True)


def open_json(content):
    obj=json.loads(content)
    records=obj if isinstance(obj,list) else obj.get('perfiles',obj) if isinstance(obj,dict) else []
    if isinstance(records,dict):records=[records]
    return [r for r in records if isinstance(r,dict) and r.get('usuario')]


def profile_card(p):
    vs=p.get('videos') or []
    st.markdown(f'''<div class="nexo-profile"><div class="handle">@{e(p.get('usuario'))}</div>
    <h3>{e(p.get('nombre') or p.get('usuario'))}</h3>
    <div class="number">{fmt(p.get('seguidores'))}</div>
    <div class="meta">SEGUIDORES · {len(vs)} VIDEOS RECUPERADOS</div></div>''',unsafe_allow_html=True)

if 'cuentas' not in st.session_state: st.session_state.cuentas=[]
if 'errores' not in st.session_state: st.session_state.errores=[]
if 'producto' not in st.session_state: st.session_state.producto=''

with st.sidebar:
    st.markdown('<div class="nexo-brand">nexo<span style="color:#A5ECBD">.</span></div><div class="nexo-mini">COLABORACIONES</div>',unsafe_allow_html=True)
    st.markdown('<div style="height:28px"></div>',unsafe_allow_html=True)
    vista=st.radio('MENÚ',['01  Cuentas','02  Ranking','03  Videos','04  Campaña'],label_visibility='collapsed')
    st.divider()
    st.markdown(f'<span style="color:#BCE7D5;font-size:.82rem">{len(st.session_state.cuentas)} perfiles · {sum(len(x.get("videos") or []) for x in st.session_state.cuentas)} videos</span>',unsafe_allow_html=True)

cuentas=st.session_state.cuentas
producto=st.session_state.producto

if vista.startswith('01'):
    section_head('01','Primero, el producto.','Compara creadores a partir de publicaciones reales.')
    left,right=st.columns([1.18,.82],gap='large')
    with left:
        producto=st.text_input('Producto',value=producto,placeholder='Ej. accesorios para ciclismo')
        st.session_state.producto=producto.strip()
        raw=st.text_area('Cuentas',height=155,placeholder='@usuario_1\n@usuario_2\n@usuario_3')
        if st.button('Analizar cuentas',type='primary',use_container_width=True):
            try:
                usuarios=usuarios_unicos(raw,5)
                if not usuarios: st.warning('Escribe una cuenta de TikTok.')
                else:
                    progress=st.progress(0)
                    def update(i,n,u): progress.progress(min(1,i/max(n,1)),text=f'@{u} · {i+1}/{n}')
                    with st.spinner('Leyendo perfiles y publicaciones...'):
                        datos,fallos=scrape_batch(usuarios,video_limit=10,detail_limit=10,comments_per_video=5,usar_sesion=True,on_progress=update)
                    progress.empty()
                    st.session_state.cuentas=datos
                    st.session_state.errores=fallos
                    if datos:st.success(f'{len(datos)} perfiles procesados.')
                    if fallos:
                        with st.expander(f'{len(fallos)} consultas sin completar'):
                            for x in fallos: st.write(f"@{x['usuario']}: {x['error']}")
            except Exception as ex:
                st.error(f'No se pudo completar la consulta: {str(ex)[:230]}')
        if st.session_state.errores and not cuentas:
            st.info('Si TikTok rechaza Playwright, conserva la información real que obtengas desde Chrome normal y cárgala en el campo Archivo JSON.')
    with right:
        st.markdown('''<div class="nexo-cover"><div class="index">01 / ENTRADA</div><h2>Una elección.<br/>Cinco cuentas.</h2><p>Datos de perfiles, rendimiento reciente y conversación pública.</p></div>''',unsafe_allow_html=True)
        st.markdown('<div class="nexo-rule"></div>',unsafe_allow_html=True)
        st.markdown('**Sesión de TikTok**')
        st.caption('Abre tu sesión desde la terminal con `python sesion.py` antes de consultar. Cierra ese navegador para liberar el perfil.')
        if RUTA_SESION.is_dir():st.markdown('<span class="nexo-flag">PERFIL LOCAL CREADO</span>',unsafe_allow_html=True)
        else:st.caption('Sin perfil local. Todavía no has abierto el navegador de NEXO.')
        with st.expander('Archivo JSON'):
            file=st.file_uploader('Captura previa',type=['json'],label_visibility='collapsed')
            if file and st.button('Importar archivo',use_container_width=True):
                try:
                    filas=open_json(file.getvalue().decode('utf-8-sig'))[:5]
                    if not filas:st.warning('El archivo no contiene perfiles reconocibles.')
                    else:
                        st.session_state.cuentas=filas
                        st.session_state.errores=[]
                        st.success(f'{len(filas)} perfiles importados.')
                        st.rerun()
                except (ValueError,UnicodeDecodeError) as exc:st.error(f'No se pudo importar: {exc}')
    if cuentas:
        st.markdown('### Cuentas en estudio')
        cols=st.columns(min(3,len(cuentas)))
        for i,p in enumerate(cuentas):
            with cols[i%len(cols)]:profile_card(p)

elif vista.startswith('02'):
    section_head('02','Comparación','Publicaciones recientes frente a tamaño de audiencia.')
    if not cuentas: st.info('Sin datos. Primero carga cuentas en la sección 01.')
    else:
        scores=comparar(cuentas,producto)
        m=st.columns(3)
        m[0].metric('Cuentas',len(cuentas))
        m[1].metric('Videos disponibles',sum(x['videos'] for x in scores))
        m[2].metric('Videos con vistas y likes',sum(x['videos_comparables'] for x in scores))
        data=pd.DataFrame([{
            'Cuenta':'@'+x['usuario'], 'Tema (%)':x['afinidad_pct'],
            'Vistas (mediana)':x['vistas_median'], 'Likes / vistas (%)':x['likes_vistas_pct'],
            'Comentarios / vistas (%)':x['comentarios_vistas_pct'],
            'Videos medidos':x['videos_comparables'], 'Puntaje':x['puntuacion'], 'Estado':x['estado']
        } for x in scores])
        st.dataframe(data,hide_index=True,use_container_width=True)
        chart=pd.DataFrame([{'Cuenta':'@'+x['usuario'],'Vistas':x['vistas_median']} for x in scores if x['vistas_median'] is not None])
        if not chart.empty:
            st.markdown('### Vistas por creador')
            st.bar_chart(chart.set_index('Cuenta'),color='#007F6A')
        st.download_button('Exportar comparación',data.to_csv(index=False).encode('utf-8-sig'),
                           file_name='nexo_ranking.csv',mime='text/csv')

elif vista.startswith('03'):
    section_head('03','Videos recientes')
    if not cuentas: st.info('Sin datos. Primero carga cuentas en la sección 01.')
    else:
        cuenta=st.selectbox('Cuenta',['@'+x['usuario'] for x in cuentas])
        p=next(x for x in cuentas if '@'+x['usuario']==cuenta)
        vids=p.get('videos') or []
        comments=p.get('comentarios_publicos') or []
        c=st.columns(3)
        c[0].metric('Publicaciones',len(vids))
        c[1].metric('Con vistas',sum(numero_compacto(x.get('vistas')) is not None for x in vids))
        c[2].metric('Comentarios leídos',len(comments))
        if not vids:st.warning('TikTok no entregó publicaciones de esta cuenta.')
        else:
            for i,v in enumerate(vids[:10],1):
                with st.container(border=True):
                    head=st.columns([3.2,1,1,1])
                    head[0].markdown(f'**{i:02d} · {e((v.get("descripcion") or "Video")[:100])}**')
                    if v.get('url'):head[0].link_button('Ver publicación',v['url'])
                    head[1].metric('Vistas',fmt(v.get('vistas')))
                    head[2].metric('Me gusta',fmt(v.get('likes')))
                    head[3].metric('Comentarios',fmt(v.get('comentarios_cantidad')))
            st.caption('Si existen videos fijados y faltan fechas, el orden visible no garantiza que sean los diez más recientes.')
        if comments:
            st.markdown('### En los comentarios')
            topics=oportunidades(comments)
            if topics.get('prioridades'):
                st.dataframe(pd.DataFrame([{'Tema':x['necesidad'],'Menciones':x['menciones']} for x in topics['prioridades']]),hide_index=True,use_container_width=True)
            with st.expander('Leer comentarios'):
                for item in comments[:30]:st.write('•',item.get('comentario',''))
        if vids:
            st.download_button('Exportar videos',pd.DataFrame(vids[:10]).to_csv(index=False).encode('utf-8-sig'),
                               file_name=f"videos_{p['usuario']}.csv",mime='text/csv')

else:
    section_head('04','Elección de campaña','Qué cuenta merece la primera conversación comercial.')
    if not cuentas:st.info('Sin datos. Primero carga cuentas en la sección 01.')
    else:
        results=comparar(cuentas,producto)
        eligible=[x for x in results if x.get('puntuacion') is not None]
        st.markdown('### Cinco señales')
        labs=['Afinidad','Vistas','Me gusta','Comentarios','Cobertura']
        blocks=st.columns(5)
        for col,label in zip(blocks,labs):
            with col:st.markdown(f'<div style="border-top:3px solid #00786B;border-bottom:1px solid #D5E2DB;padding:14px 3px;font-weight:700;color:#244540">{e(label)}</div>',unsafe_allow_html=True)
        st.markdown('<div style="height:16px"></div>',unsafe_allow_html=True)
        if not eligible:
            st.warning('No hay suficientes publicaciones comparables para seleccionar una cuenta todavía.')
            st.dataframe(pd.DataFrame([{'Cuenta':'@'+x['usuario'],'Videos medidos':x['videos_comparables'],
                                      'Afinidad (%)':x['afinidad_pct'],'Estado':x['estado']} for x in results]),hide_index=True,use_container_width=True)
        else:
            top=eligible[0]
            st.markdown(f'<div class="nexo-winner"><div class="nexo-tag">PRIMERA CANDIDATA EN ESTA MUESTRA</div><div class="username">@{e(top["usuario"])}</div><span style="font-size:1.3rem;color:#31584D">{top["puntuacion"]} / 100</span></div>',unsafe_allow_html=True)
            c1,c2,c3=st.columns(3)
            c1.metric('Afinidad temática',f'{top["afinidad_pct"]} %')
            c2.metric('Mediana de vistas',fmt(top['vistas_median']))
            c3.metric('Videos comparables',top['videos_comparables'])
            st.markdown('### Otras opciones')
            for x in results:
                if x['usuario']!=top['usuario']:
                    st.markdown(f'**@{e(x["usuario"])}**  ·  {e(str(x["puntuacion"]) + " / 100" if x["puntuacion"] is not None else x["estado"])}')
            st.caption('Ranking interno de esta muestra; no representa ventas esperadas.')
        with st.expander('Descargar captura original'):
            st.download_button('JSON',json.dumps(cuentas,ensure_ascii=False,indent=2).encode('utf-8'),
                               file_name='nexo_captura.json',mime='application/json')
