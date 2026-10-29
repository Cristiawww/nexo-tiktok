"""Búsqueda de cuentas públicas por sector. Solo devuelve enlaces sustentados
por resultados web visibles o enlaces de búsqueda pública TikTok.
No valida contenido ni seguidores; eso ocurre al ejecutar scraper.py.
"""
from __future__ import annotations

import base64
import re
import unicodedata
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

from playwright.sync_api import sync_playwright, Error as PWError, TimeoutError as PWTimeout

USERNAME = re.compile(r"^/@([A-Za-z0-9._]{1,24})(?:/|$)")
SEARCH_TEXT = re.compile(r"(?:https?://)?(?:www\.)?tiktok\.com/@([A-Za-z0-9._]{1,24})",re.I)
TERMS = {
    "ropa": ["moda", "outfit", "fashion", "estilo"],
    "moda": ["ropa", "outfits", "fashion", "estilo"],
    "ciclismo": ["bicicleta", "mtb", "ciclista", "cycling", "bike"],
    "bicicleta": ["ciclismo", "mtb", "bike"],
    "bicicletas": ["ciclismo", "mtb", "bike"],
    "tecnologia": ["gadgets", "tech", "celulares", "computadoras"],
    "celular": ["tecnologia", "smartphone", "review"],
    "reposteria": ["pasteles", "postres", "pasteleria"],
    "maquillaje": ["makeup", "beauty", "belleza"],
    "comida": ["recetas", "gastronomia", "cocina"],
    "deportes": ["entrenamiento", "fitness", "run"],
}
TEMAS_RELACIONADOS = TERMS  # used by selection logic


def normalizar(value):
    s=unicodedata.normalize('NFKD',str(value or '')).casefold()
    return ''.join(c for c in s if not unicodedata.combining(c))


def variantes(tema):
    words = normalizar(tema).split()
    found=[]
    for word in words:
        found += TERMS.get(word,[])
    return list(dict.fromkeys(found))[:5]


def _unwrap(url):
    """Handle standard search-engine redirects; do not follow arbitrary sites."""
    parsed=urlparse(url)
    host=(parsed.hostname or '').casefold()
    args=parse_qs(parsed.query)
    if host.endswith('duckduckgo.com') and args.get('uddg'):
        return unquote(args['uddg'][0])
    if host in ('www.google.com','google.com') and args.get('q'):
        return unquote(args['q'][0])
    if host in ('www.bing.com','bing.com') and args.get('u'):
        val=args['u'][0]
        if val.startswith('a1'):
            try:
                return base64.urlsafe_b64decode(val[2:] + '='*((-len(val[2:]))%4)).decode('utf8')
            except (ValueError,UnicodeDecodeError):
                pass
    return url


def usuario_desde_enlace(url):
    if not isinstance(url,str):
        return None
    parsed=urlparse(_unwrap(url))
    if parsed.scheme not in ('http','https') or parsed.hostname not in ('tiktok.com','www.tiktok.com','m.tiktok.com'):
        return None
    match=USERNAME.match(parsed.path)
    return match.group(1) if match else None


def candidatos_desde_resultados(results, limite=5):
    candidates, seen=[],set()
    for item in results:
        url=str(item.get('url') or '')
        name=usuario_desde_enlace(url)
        source='Enlace de resultado público'
        if not name:
            # If indexed result includes the explicit platform profile URL in its
            # title/summary, it can be a candidate, but must be verified by scraper.
            summary=str(item.get('titulo') or '')+' '+str(item.get('resumen') or '')
            match=SEARCH_TEXT.search(summary)
            name=match.group(1) if match else None
            source='Texto de resultado público'
        if not name or name.casefold() in seen:
            continue
        candidates.append({'usuario':name,
            'url':f'https://www.tiktok.com/@{name}',
            'titulo_resultado':str(item.get('titulo') or '')[:130],
            'resumen_resultado':str(item.get('resumen') or '')[:280],
            'fuente':source})
        seen.add(name.casefold())
        if len(candidates)>=limite:
            break
    return candidates


def _links(page):
    try:
        return page.locator('a[href]').evaluate_all('''els=>els.map(a=>({
            url:a.href||'',
            titulo:(a.innerText||a.getAttribute('aria-label')||'').trim().slice(0,130),
            resumen:(a.closest('article,li,.result,.b_algo,.MjjYud')?.innerText||
                a.parentElement?.innerText||'').trim().slice(0,280)
        }))''')
    except (PWError,PWTimeout):
        return []


def buscar_cuentas_por_tema(tema, limite=5):
    tema=str(tema or '').strip()
    if not 2<=len(tema)<=80:
        raise ValueError('El sector debe tener entre 2 y 80 caracteres')
    limite=max(1,min(5,int(limite)))
    alternatives=variantes(tema)
    companion=' OR '.join(alternatives[:3]) if alternatives else tema
    queries=[
        ('Bing',f'https://www.bing.com/search?q={quote_plus("site:tiktok.com/@ "+tema)}'),
        ('DuckDuckGo',f'https://html.duckduckgo.com/html/?q={quote_plus("TikTok "+tema+" "+companion)}'),
        ('TikTok',f'https://www.tiktok.com/search/user?q={quote_plus(tema)}'),
        ('Bing relacionado',f'https://www.bing.com/search?q={quote_plus("site:tiktok.com/@ "+companion)}'),
    ]
    found,seen=[],set()
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            ctx=browser.new_context(locale='es-ES',viewport={'width':1350,'height':900})
            page=ctx.new_page()
            for source,url in queries:
                if len(found)>=limite:
                    break
                try:
                    response=page.goto(url,wait_until='domcontentloaded',timeout=13000)
                    if response and response.status in (403,429):
                        continue
                    page.wait_for_timeout(800)
                    for candidate in candidatos_desde_resultados(_links(page),limite=30):
                        u=candidate['usuario']
                        if u.casefold() not in seen:
                            seen.add(u.casefold())
                            candidate['fuente']+=' · '+source
                            found.append(candidate)
                        if len(found)>=limite:
                            break
                except (PWTimeout,PWError):
                    continue
            ctx.close()
        finally:
            browser.close()
    return found[:limite]
