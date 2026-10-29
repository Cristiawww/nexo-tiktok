"""Cinco criterios COMERCIALES medibles (no equivalen al Big Five psicológico)."""
from __future__ import annotations
import math
import statistics
import re
import unicodedata
from analisis_negocio import numero_compacto

SINONIMOS = {
    "ciclismo": ("ciclismo", "bicicleta", "bicicletas", "ciclista", "mtb", "bici", "bike"),
    "tecnologia": ("tecnologia", "tecnologico", "gadgets", "smartphone", "celular", "computadora", "software", "tecnologia"),
    "ropa": ("ropa", "moda", "outfit", "vestuario", "prenda", "fashion", "estilo"),
    "maquillaje": ("maquillaje", "cosmeticos", "belleza", "makeup", "skincare"),
    "comida": ("comida", "receta", "cocina", "gastronomia", "alimentos"),
}


def normalizar(s):
    s = unicodedata.normalize("NFKD", str(s or "")).casefold()
    return "".join(c for c in s if not unicodedata.combining(c))


def tokens(s):
    return set(re.findall(r"[a-z0-9]+", normalizar(s)))


def coincidencia_tema(tema: str, perfil: dict) -> dict:
    words=tokens(tema)
    alternatives=set(words)
    for key, synonyms in SINONIMOS.items():
        if key in words:
            alternatives |= set(synonyms)
    base=tokens(" ".join(str(perfil.get(k) or "") for k in ("nombre","biografia")))
    videos=perfil.get("videos") or []
    hits_bio=len(alternatives & base)
    hits_video=sum(bool(alternatives & tokens(v.get("descripcion"))) for v in videos)
    videos_con_texto=sum(bool(str(v.get("descripcion") or "").strip()) for v in videos)
    ratio=hits_video/videos_con_texto if videos_con_texto else 0
    # Afinidad sobre evidencia textual, no representa compatibilidad psicológica.
    pct=round(100*min(1.0, (0.35 if hits_bio else 0.0)+0.65*ratio), 1)
    return {"pct":pct,"coincidencias_bio":hits_bio,"videos_relacionados":hits_video,
            "videos_con_texto":videos_con_texto}


def calcular_ficha(perfil:dict, tema:str) -> dict:
    vids=perfil.get("videos") or []
    comparables=[]
    para_vistas=[]
    para_comentarios=[]
    for v in vids:
        views=numero_compacto(v.get("vistas"))
        likes=numero_compacto(v.get("likes"))
        comments=numero_compacto(v.get("comentarios_cantidad"))
        if views is not None and views > 0:
            para_vistas.append(views)
            if likes is not None and likes>=0:
                comparables.append(min(1.0,likes/views))
            if comments is not None and comments>=0:
                para_comentarios.append(min(1.0,comments/views))
    afin=coincidencia_tema(tema,perfil)
    cobertura=round(100*len(comparables)/len(vids),1) if vids else 0
    comentario_texto=len(perfil.get("comentarios_publicos") or [])
    return {
        "usuario":str(perfil.get("usuario") or ""),
        "nombre":str(perfil.get("nombre") or perfil.get("usuario") or ""),
        "seguidores":numero_compacto(perfil.get("seguidores")),
        "videos":len(vids),
        "videos_comparables":len(comparables),
        "videos_con_vistas":len(para_vistas),
        "comentarios_texto":comentario_texto,
        "afinidad_pct":afin["pct"],
        "relacionados":afin["videos_relacionados"],
        "vistas_median":round(statistics.median(para_vistas)) if para_vistas else None,
        "likes_vistas_pct":round(100*statistics.median(comparables),2) if comparables else None,
        "comentarios_vistas_pct":round(100*statistics.median(para_comentarios),2) if para_comentarios else None,
        "cobertura_pct":cobertura,
        "apto_para_comparar":len(comparables)>=3 and afin["pct"]>0,
        "fecha":perfil.get("fecha_consulta"),
    }


def _relative(val, maximum, log=False):
    if val is None or maximum is None or maximum<=0:
        return None
    if log:
        return round(100*math.log1p(val)/math.log1p(maximum),1)
    return round(100*val/maximum,1)


def comparar(perfiles:list[dict],tema:str) -> list[dict]:
    rows=[calcular_ficha(p,tema) for p in perfiles]
    valid=[r for r in rows if r["apto_para_comparar"]]
    max_views=max((r["vistas_median"] or 0 for r in valid),default=0)
    max_likes=max((r["likes_vistas_pct"] or 0 for r in valid),default=0)
    max_comments=max((r["comentarios_vistas_pct"] or 0 for r in valid),default=0)
    comentarios_comparables=bool(valid) and all(r["comentarios_vistas_pct"] is not None for r in valid)
    for r in rows:
        if not r["apto_para_comparar"]:
            r["puntuacion"]=None
            r["estado"]="Datos insuficientes" if r["videos_comparables"]<3 else "Afinidad sin confirmar"
            continue
        # Si no existen recuentos de comentarios en el lote, no se asigna puntuación.
        weights={"afinidad_pct":.35, "visibilidad":.25, "interaccion":.20, "cobertura_pct":.10}
        scores={"afinidad_pct":r["afinidad_pct"],
                "visibilidad":_relative(r["vistas_median"],max_views,log=True),
                "interaccion":_relative(r["likes_vistas_pct"],max_likes),
                "cobertura_pct":r["cobertura_pct"]}
        if comentarios_comparables and max_comments>0:
            weights["conversacion"]=.10
            scores["conversacion"]=_relative(r["comentarios_vistas_pct"],max_comments)
        available=[k for k in weights if scores.get(k) is not None]
        r["puntuacion"]=round(sum(weights[k]*scores[k] for k in available)/sum(weights[k] for k in available),1)
        r["estado"]="Evaluable"
    return sorted(rows,key=lambda r:(r["puntuacion"] is None, -(r["puntuacion"] or 0),r["usuario"].casefold()))
