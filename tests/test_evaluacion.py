from evaluacion import calcular_ficha, comparar, coincidencia_tema

def ejemplo(user='uno',likes=10):
    return {'usuario':user,'nombre':'Ciclismo MTB', 'biografia':'Bicicletas', 'seguidores':2000,
            'videos':[{'video_id':str(i),'descripcion':'Rutas en bicicleta', 'vistas':100,'likes':likes,'comentarios_cantidad':3} for i in range(4)]}

def test_comparacion_con_evidencia():
    rows=comparar([ejemplo(),ejemplo('dos',3)],'ciclismo')
    assert rows[0]['usuario']=='uno'
    assert rows[0]['estado']=='Evaluable'
    assert rows[0]['videos_comparables']==4

def test_sin_videos_no_se_recomienda():
    rows=comparar([{'usuario':'uno','seguidores':1_000_000,'biografia':'ciclismo','videos':[]}],'ciclismo')
    assert rows[0]['puntuacion'] is None
    assert rows[0]['estado']=='Datos insuficientes'

def test_no_deducir_afinidad_por_seguidores():
    r=coincidencia_tema('ciclismo',{'nombre':'Otro','seguidores':'3M','videos':[]})
    assert r['pct']==0

def test_sin_comentarios_en_uno_no_se_premia_el_otro():
    a=ejemplo('uno')
    b=ejemplo('dos')
    for v in b['videos']:
        v['comentarios_cantidad']=None
    rows=comparar([a,b],'ciclismo')
    assert rows[0]['puntuacion']==rows[1]['puntuacion']
