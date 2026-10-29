"""Auditoría reproducible de una cuenta pública: observación != recomendación != resultado."""
from __future__ import annotations
from analisis_negocio import indicadores, indicadores_videos, oportunidades


def auditar_perfil(perfil: dict, sector: str = "") -> dict:
    """Describe observaciones reales, diferenciando perfil, videos y comentarios."""
    datos=indicadores(perfil)
    videos=indicadores_videos(perfil.get("videos") or [])
    texts=oportunidades(perfil.get("comentarios_publicos") or [])
    with_both=[v for v in videos if v.get("tasa_like_vistas_pct") is not None]
    with_views=[v for v in videos if v.get("vistas") is not None]
    observaciones,faltantes,acciones=[],[],[]
    if with_both:
        # Media de ratios por publicación, no tasa global ni indicador de ventas.
        media=sum(v["tasa_like_vistas_pct"] for v in with_both)/len(with_both)
        observaciones.append(f"{len(with_both)} videos con likes y vistas; relación media likes/vistas: {media:.2f}%")
        mejor=max(with_both,key=lambda v:v["tasa_like_vistas_pct"])
        observaciones.append(f"Mayor relación observada: {mejor['tasa_like_vistas_pct']:.2f}% (video {mejor.get('video_id','sin ID')})")
        if len(with_both)<3:
            faltantes.append("Menos de tres videos con datos comparables")
    else:
        faltantes.append("Vistas y Me gusta de publicaciones recientes (no se calcula engagement)")
    if with_views:
        observaciones.append(f"{len(with_views)} videos con cifras de vistas recuperadas")
    if texts['comentarios_analizados']:
        observaciones.append(f"{texts['comentarios_analizados']} comentarios públicos leídos")
        if texts['prioridades']:
            first=texts['prioridades'][0]
            observaciones.append(f"Pregunta frecuente detectada: {first['necesidad']} ({first['menciones']} menciones)")
    else:
        faltantes.append("Comentarios públicos de las publicaciones")
    if datos['seguidores'] is not None:
        observaciones.append(f"Audiencia declarada: {datos['seguidores']:,.0f} seguidores a la fecha registrada")
    if sector and not (perfil.get('biografia') or '').strip():
        faltantes.append('Biografía para revisar la relación con el sector')
    if not videos:
        acciones.append("Consultar enlaces de publicaciones públicas y repetir la extracción")
    if len(with_both)<3:
        acciones.append("Revisar al menos tres publicaciones con métricas comparables")
    if not texts['comentarios_analizados']:
        acciones.append("Revisar preguntas en comentarios públicos antes de proponer contenido")
    acciones.append("Comprobar cualquier colaboración mediante visitas o ventas atribuidas a un enlace de campaña")
    if len(with_both)>=3 and texts['comentarios_analizados']>0:
        evaluacion='Análisis exploratorio'
    else:
        evaluacion='Evidencia insuficiente'
    return {"usuario":perfil.get('usuario'),"fecha":perfil.get('fecha_consulta'),
            "calidad":datos['calidad_porcentaje'],"observaciones":observaciones,
            "faltantes":faltantes,"acciones":acciones,"videos_muestra":len(videos),
            "videos_con_metricas":len(with_both),"comentarios_muestra":texts['comentarios_analizados'],
            "evaluacion":evaluacion}
