import pytest
from investigacion import benford, ocean_aggregate, research_patterns
from analisis_negocio import oportunidades, numero_compacto
from seleccion_comercial import elegir_cuenta


def test_compact_count():
    assert numero_compacto('302.3K') == 302300
    assert numero_compacto('1.7M') == 1_700_000


def test_benford_small_sample_not_validated():
    result=benford([12,13,14,20,25])
    assert result['ready'] is False
    assert result['n']==5
    assert abs(result['expected'][1] - .30102999566) < .000001


def test_benford_first_digits_include_fraction():
    result=benford([.0021, 12, 345])
    assert result['observed'][2] == pytest.approx(1/3)
    assert result['observed'][1] == pytest.approx(1/3)
    assert result['observed'][3] == pytest.approx(1/3)


def test_ocean_requires_valid_instrument_and_real_responses():
    rows=[dict(O=3,C=4,E=2,A=5,N=1) for i in range(5)]
    assert ocean_aggregate(rows,'Instrumento con autorización')['promedios']['C']==4
    with pytest.raises(ValueError):
        ocean_aggregate(rows[:4],'Test')
    with pytest.raises(ValueError):
        ocean_aggregate(rows,'')


def test_ranking_commercial_not_personality():
    candidates=[{'usuario':'bici','nombre':'Rutas MTB','biografia':'Ciclismo y bicicletas',
        'seguidores':5000,'seguidos':120,'me_gusta':12000,'publicaciones':25,'fecha_consulta':'2026-10-29'},
        {'usuario':'tech','nombre':'Tech','biografia':'Tecnología',
        'seguidores':100000,'seguidos':100,'me_gusta':100000,'publicaciones':50,'fecha_consulta':'2026-10-29'}]
    order=elegir_cuenta('ciclismo',candidates)
    assert order[0]['usuario']=='bici'
    assert order[0]['afinidad_pct']>0
    assert order[1]['afinidad_pct']==0


def test_research_patterns_never_infers_traits():
    sample=[{'usuario':'a','seguidores':1000,'videos':[], 'comentarios_publicos':[]}]
    info=research_patterns(sample)
    assert info['perfiles']==1
    assert not any(k.lower() in ['extraversión','neuroticismo'] for k in info)


def test_comment_classification_not_ai_detection():
    result=oportunidades([{'comentario':'¿Cuál es el precio?'},{'comentario':'¿Cuál es el precio?'}])
    assert result['duplicados_textuales'] == 1
    assert any(x['necesidad']=='Precio y promociones' for x in result['prioridades'])
