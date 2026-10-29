"""Estadística y research que se apoyan en datos observables, sin suposiciones."""
from __future__ import annotations
import math
from collections import Counter
from typing import Any

from analisis_negocio import numero_compacto, calidad, limpiar_texto, oportunidades

OCEAN_LABELS = {
    "O": "Apertura a la experiencia",
    "C": "Responsabilidad",
    "E": "Extraversión",
    "A": "Amabilidad",
    "N": "Neuroticismo",
}


def benford(values: list[Any]) -> dict:
    """First significant digit reference; never asserts authenticity or fraud."""
    parsed = [numero_compacto(x) for x in values]
    positives = [v for v in parsed if v is not None and math.isfinite(v) and v > 0]
    observed_counts = Counter(int(v / (10 ** math.floor(math.log10(v)))) if int(v / (10 ** math.floor(math.log10(v)))) < 10 else 9 for v in positives)
    total = len(positives)
    expected = {d: math.log10(1 + 1 / d) for d in range(1, 10)}
    observed = {d: observed_counts.get(d, 0) / total if total else None for d in expected}
    span = max(positives) / min(positives) if positives else None
    # 100 and 100x are heuristics for initial exploration, not validation.
    min_sample = total >= 100
    spread_ok = span is not None and span >= 100
    ready = min_sample and spread_ok
    mad = (sum(abs(observed[d] - expected[d]) for d in expected) / 9) if total else None
    return {"n": total, "span": span, "ready": ready, "mad": mad,
            "expected": expected, "observed": observed,
            "reason": ("Solo exploratorio: comprobar el mecanismo generador de datos y el redondeo" if ready
                       else "Muestra o escala insuficiente para una lectura estadística de Benford")}


def research_patterns(records: list[dict]) -> dict:
    """Descriptive patterns within THIS sample, not global trends."""
    n = len(records)
    followers = [numero_compacto(p.get("seguidores")) for p in records]
    followers = [x for x in followers if x is not None]
    video_counts = [len(p.get("videos") or []) for p in records]
    video_views = sum(1 for p in records for v in p.get("videos", []) if numero_compacto(v.get("vistas")) is not None)
    comments = [c for p in records for c in p.get("comentarios_publicos", [])]
    ranking_fields = [calidad(p) for p in records]
    content = oportunidades(comments)
    missing = Counter()
    for p in records:
        for k in ("seguidores", "biografia", "publicaciones", "verificada"):
            if p.get(k) is None:
                missing[k] += 1
    return {
        "perfiles": n,
        "seguidores_min": min(followers) if followers else None,
        "seguidores_max": max(followers) if followers else None,
        "calidad_promedio": round(sum(ranking_fields) / n, 1) if n else None,
        "videos_detectados": sum(video_counts),
        "videos_con_vistas": video_views,
        "comentarios_recogidos": len(comments),
        "campos_faltantes": dict(missing),
        "necesidades": content["prioridades"],
        "comentarios_repetidos": content["duplicados_textuales"],
    }


def ocean_aggregate(records: list[dict], instrument: str) -> dict:
    """Aggregate ONLY voluntarily supplied validated scores, no IDs.

    Expected score columns O,C,E,A,N (same scale across respondents).
    We intentionally do not accept a TikTok username or map to profiles.
    """
    if not instrument or not instrument.strip():
        raise ValueError("Indica el instrumento empleado; no se deducen rasgos de TikTok")
    rows = []
    for row in records:
        out = {}
        for letter in OCEAN_LABELS:
            val = row.get(letter)
            if val is None or val == "":
                raise ValueError(f"Falta un valor {letter}")
            try:
                x = float(val)
            except (ValueError, TypeError):
                raise ValueError(f"El valor de {letter} no es numérico") from None
            if not math.isfinite(x):
                raise ValueError("Valor no finito")
            out[letter] = x
        rows.append(out)
    if len(rows) < 5:
        raise ValueError("Para mostrar resultados agregados se requieren al menos cinco respuestas voluntarias")
    return {"n": len(rows), "instrumento": instrument.strip(),
            "promedios": {letter: round(sum(r[letter] for r in rows) / len(rows), 2) for letter in OCEAN_LABELS}}
