from diagnostico import auditar_perfil


def test_reporte_sin_videos_no_inventa_engagement():
    row={"usuario":"ejemplo","seguidores":"302.3K","seguidos":"15","me_gusta":"1.7M",
         "publicaciones":"16","fecha_consulta":"2026-10-22T17:37:26-05:00","videos":[]}
    out=auditar_perfil(row,"ciclismo")
    assert out["videos_muestra"] == 0
    assert any("no se calcula engagement" in x for x in out["faltantes"])
    assert not any("likes/vistas promedio" in x for x in out["observaciones"])


def test_reporte_con_videos_muestra_tasa_real():
    row={"usuario":"ejemplo","videos":[{"likes":100,"vistas":1000}],
          "comentarios_publicos":[{"comentario":"¿Cuánto cuesta?"}]}
    out=auditar_perfil(row,"ropa")
    assert out["videos_muestra"] == 1
    assert out["comentarios_muestra"] == 1
    assert any("10.00%" in x for x in out["observaciones"])
