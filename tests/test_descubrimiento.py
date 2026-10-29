from descubrimiento import usuario_desde_enlace, variantes, candidatos_desde_resultados


def test_only_tiktok_links():
    assert usuario_desde_enlace('https://www.tiktok.com/@bicis.ejemplo/video/123')=='bicis.ejemplo'
    assert usuario_desde_enlace('https://fake-tiktok.com/@bicis.ejemplo') is None
    assert usuario_desde_enlace('javascript:alert(1)') is None


def test_expand_topics():
    assert 'bicicleta' in variantes('ciclismo')


def test_candidate_deduplication():
    data=[{'url':'https://www.tiktok.com/@A','titulo':'A'},
          {'url':'https://www.tiktok.com/@A/video/123','titulo':'A video'},
          {'url':'https://www.tiktok.com/@B','titulo':'B'}]
    assert [x['usuario'] for x in candidatos_desde_resultados(data)]==['A','B']


def test_search_redirect_and_explicit_url_in_result():
    from urllib.parse import quote
    url='https://duckduckgo.com/l/?uddg='+quote('https://www.tiktok.com/@ciclismo.real')
    assert usuario_desde_enlace(url)=='ciclismo.real'
    data=[{'url':'https://www.google.com/search?q=ciclismo',
           'titulo':'TikTok · https://www.tiktok.com/@cuenta_ciclista',
           'resumen':'Un resultado público'}]
    assert candidatos_desde_resultados(data)[0]['usuario']=='cuenta_ciclista'
