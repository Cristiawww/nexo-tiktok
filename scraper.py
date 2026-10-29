"""Extracción limitada a páginas públicas de TikTok mediante Playwright.

Sin API privada, autenticación, proxies, evasión de bloqueos ni datos inventados.
Los selectores y la estructura del HTML pueden cambiar.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout, Error as PWError
from sesion import RUTA_SESION, abrir_contexto

USER_RE = re.compile(r"^[A-Za-z0-9._]{1,24}$")
VIDEO_RE = re.compile(r"^https://(?:www\.)?tiktok\.com/@([A-Za-z0-9._]{1,24})/video/(\d+)(?:[/?#]|$)")
def validar_urls_videos(texto: str, maximo: int = 50) -> list[dict]:
    """Acepta exclusivamente enlaces públicos de videos de tiktok.com."""
    result,seen=[],set()
    for part in re.split(r"[,;\s]+", texto or ""):
        part=part.strip()
        if not part:
            continue
        match=VIDEO_RE.match(part)
        if not match:
            raise ValueError(f"Enlace de video no válido: {part[:55]}")
        user,vid=match.groups()
        if (user.casefold(),vid) not in seen:
            result.append({"usuario":user,"video_id":vid,
                           "url":f"https://www.tiktok.com/@{user}/video/{vid}"})
            seen.add((user.casefold(),vid))
        if len(result)>=maximo: break
    return result


def _empty_video(user: str, vid: str, origin: str) -> dict:
    return {"usuario":user,"video_id":vid,
            "url":f"https://www.tiktok.com/@{user}/video/{vid}",
            "descripcion":None,"vistas":None,"likes":None,
            "comentarios_cantidad":None,"compartidos":None,
            "fecha_publicacion":None,"origen":origin}


def _feed_videos(feed: object, username: str, profile_user_id: str | None = None) -> dict[str,dict]:
    """Lee únicamente respuestas de lista de publicaciones de un perfil público.
    Un item solo se atribuye si su autor coincide con el usuario o ID de perfil.
    """
    if not isinstance(feed,dict): return {}
    nested=feed.get("data") if isinstance(feed.get("data"),dict) else feed
    rows=nested.get("itemList") or nested.get("item_list") or nested.get("items") or []
    if isinstance(rows,dict): rows=list(rows.values())
    if not isinstance(rows,list): return {}
    found={}
    for item in rows:
        if not isinstance(item,dict): continue
        author=item.get("author")
        author_id=item.get("authorId") or item.get("author_id")
        unique=(author.get("uniqueId") if isinstance(author,dict) else author)
        if not ((isinstance(unique,str) and unique.casefold()==username.casefold())
                or (profile_user_id and str(author_id or (author.get("id") if isinstance(author,dict) else ""))==str(profile_user_id))):
            continue
        vid=str(item.get("id", ""))
        if not vid.isdigit(): continue
        video=_video_from_item(item,vid,username,"Lista pública de videos")
        if video: found[vid]=video
    return found


def _public_video_metadata(page, user: str, vid: str) -> dict:
    """Recupera contadores DOM visibles si el JSON incrustado no los incluye."""
    output=_empty_video(user,vid,"Contadores visibles")
    for field, selectors in {
        "likes": ('[data-e2e="like-count"]','[data-e2e="browse-like-count"]'),
        "comentarios_cantidad": ('[data-e2e="comment-count"]','[data-e2e="browse-comment-count"]'),
        "compartidos": ('[data-e2e="share-count"]','[data-e2e="browse-share-count"]'),
        "vistas": ('[data-e2e="video-views"]','[data-e2e="play-count"]'),
    }.items():
        for selector in selectors:
            val=_texto(page,selector)
            if val is not None:
                output[field]=val
                break
    return output


def _append_video_metrics(current:dict, new:dict) -> None:
    for field in ("vistas","likes","comentarios_cantidad","compartidos","descripcion","fecha_publicacion"):
        if new.get(field) is not None:
            current[field]=new[field]
    if any(new.get(k) is not None for k in ("vistas","likes","comentarios_cantidad")):
        current["origen"]=new.get("origen") or current.get("origen")


SELECTORS = {
    "nombre": '[data-e2e="user-title"]',
    "biografia": '[data-e2e="user-bio"]',
    "seguidores": '[data-e2e="followers-count"]',
    "seguidos": '[data-e2e="following-count"]',
    "me_gusta": '[data-e2e="likes-count"]',
}


def limpiar_usuario(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Usuario incorrecto")
    value = value.strip()
    if value.startswith("https://"):
        parsed = urlparse(value)
        if parsed.hostname not in ("www.tiktok.com", "tiktok.com", "m.tiktok.com"):
            raise ValueError("El enlace debe ser de TikTok")
        found = re.match(r"^/@([^/?#]+)", parsed.path)
        value = found.group(1) if found else ""
    value = value.lstrip("@").strip()
    if not USER_RE.fullmatch(value):
        raise ValueError(f"Usuario de TikTok no válido: {value[:35]}")
    return value


def usuarios_unicos(texto: str, maximo: int = 5) -> list[str]:
    resultado, vistos = [], set()
    for valor in re.split(r"[,;\n]+", texto or ""):
        if not valor.strip():
            continue
        u = limpiar_usuario(valor)
        if u.casefold() not in vistos:
            resultado.append(u)
            vistos.add(u.casefold())
        if len(resultado) >= maximo:
            break
    return resultado


def _texto(page, selector: str, attr: str | None = None):
    try:
        node = page.locator(selector).first
        value = node.get_attribute(attr, timeout=900) if attr else node.inner_text(timeout=900)
        return value.strip() if value and value.strip() else None
    except (PWTimeout, PWError, AttributeError):
        return None


def _states(page) -> list[dict]:
    result = []
    for script_id in ("__UNIVERSAL_DATA_FOR_REHYDRATION__", "SIGI_STATE"):
        try:
            content = page.locator(f'script[id="{script_id}"]').first.text_content(timeout=1000)
            obj = json.loads(content or "null")
            if isinstance(obj, dict):
                result.append(obj)
        except (PWTimeout, PWError, TypeError, ValueError):
            pass
    return result


def user_from_state(state: dict, username: str) -> tuple[dict, dict]:
    """Return matching user only. Never attribute other profile's stats."""
    scope = state.get("__DEFAULT_SCOPE__", {})
    detail = scope.get("webapp.user-detail", {}) if isinstance(scope, dict) else {}
    info = detail.get("userInfo", {}) if isinstance(detail, dict) else {}
    user = info.get("user", {}) if isinstance(info, dict) else {}
    if isinstance(user, dict) and str(user.get("uniqueId", "")).casefold() == username.casefold():
        return user, info.get("stats") or info.get("statsV2") or {}
    module = state.get("UserModule", {})
    users = module.get("users", {}) if isinstance(module, dict) else {}
    stats = module.get("stats", {}) if isinstance(module, dict) else {}
    if isinstance(users, dict):
        for key, user in users.items():
            if isinstance(user, dict) and str(user.get("uniqueId", "")).casefold() == username.casefold():
                return user, stats.get(key, {}) if isinstance(stats, dict) else {}
    return {}, {}


def _video_from_item(item: dict, video_id: str, username: str, origin: str) -> dict:
    stats = item.get("stats") or item.get("statsV2") or {}
    if not isinstance(stats, dict):
        stats = {}
    author = item.get("author")
    if isinstance(author, dict):
        author = author.get("uniqueId")
    if isinstance(author, str) and author and author.casefold() != username.casefold():
        return {}
    return {
        "usuario": username, "video_id": video_id,
        "url": f"https://www.tiktok.com/@{username}/video/{video_id}",
        "descripcion": item.get("desc"),
        "vistas": stats.get("playCount"), "likes": stats.get("diggCount"),
        "comentarios_cantidad": stats.get("commentCount"),
        "compartidos": stats.get("shareCount"),
        "fecha_publicacion": item.get("createTime"), "origen": origin,
    }


def videos_from_states(states: list[dict], username: str) -> dict[str, dict]:
    """Capture only valid video records from embedded public page data."""
    found = {}
    for state in states:
        module = state.get("ItemModule")
        if isinstance(module, dict):
            for vid, item in module.items():
                if isinstance(item, dict) and str(item.get("id", vid)).isdigit():
                    v = _video_from_item(item, str(item.get("id", vid)), username, "HTML incrustado")
                    if v:
                        found[v["video_id"]] = v
        scope = state.get("__DEFAULT_SCOPE__", {})
        detail = scope.get("webapp.video-detail", {}) if isinstance(scope, dict) else {}
        iteminfo = detail.get("itemInfo", {}) if isinstance(detail, dict) else {}
        item = iteminfo.get("itemStruct", {}) if isinstance(iteminfo, dict) else {}
        if isinstance(item, dict) and str(item.get("id", "")).isdigit():
            vid = str(item["id"])
            v = _video_from_item(item, vid, username, "Página pública del video")
            if v:
                found[vid] = v
    return found


def videos_del_feed_incrustado(states: list[dict], username: str,
                                 profile_user_id: str | None = None) -> dict[str, dict]:
    """Recoge publicaciones del feed específico del perfil visitado.

    Algunas versiones de TikTok muestran IDs en `webapp.user-post`, otras
    incluyen objetos completos. No atribuye autores diferentes.
    """
    result = {}
    for state in states:
        scope = state.get("__DEFAULT_SCOPE__", {})
        if not isinstance(scope,dict):
            continue
        post=scope.get("webapp.user-post", {})
        if not isinstance(post,dict):
            continue
        # Exigir que el perfil leído en el mismo estado coincida con el solicitado.
        user, _ = user_from_state(state, username)
        if not user:
            continue
        pid=str(user.get("id") or profile_user_id or "")
        pools=[post]
        if isinstance(post.get("data"),dict):pools.append(post["data"])
        for pool in pools:
            items=pool.get("itemList") or pool.get("item_list") or []
            if not isinstance(items,list):continue
            for obj in items:
                if isinstance(obj,str) and obj.isdigit():
                    result.setdefault(obj,_empty_video(username,obj,"Lista del perfil"))
                elif isinstance(obj,dict):
                    vid=str(obj.get("id", ""))
                    if not vid.isdigit():continue
                    author=obj.get("author")
                    unique=(author.get("uniqueId") if isinstance(author,dict) else author)
                    authorid=obj.get("authorId") or (author.get("id") if isinstance(author,dict) else None)
                    if (unique and str(unique).casefold()!=username.casefold()):continue
                    if (authorid and pid and str(authorid)!=pid):continue
                    result[vid]=_video_from_item(obj,vid,username,"Lista del perfil") or _empty_video(username,vid,"Lista del perfil")
    return result


def _video_links(page, username: str) -> list[str]:
    try:
        links = page.locator('a[href*="/video/"]').evaluate_all("els => els.map(e => e.href)")
    except (PWError, PWTimeout):
        return []
    ids = []
    for url in links:
        match = VIDEO_RE.match(str(url))
        if match and match.group(1).casefold() == username.casefold() and match.group(2) not in ids:
            ids.append(match.group(2))
    return ids


def _comments_public(page, username: str, vid: str, max_comments: int) -> list[dict]:
    """Read visible comment bodies only; usernames are intentionally discarded."""
    if max_comments <= 0:
        return []
    texts = []
    for selector in ('[data-e2e="comment-level-1"] [data-e2e="comment-content"]',
                     '[data-e2e="comment-content"]',
                     '[data-e2e="comment-item"] [data-e2e="comment-content"]'):
        try:
            texts = page.locator(selector).all_inner_texts(timeout=1800)
            if texts:
                break
        except (PWError, PWTimeout):
            pass
    seen, rows = set(), []
    for text in texts:
        text = re.sub(r"\s+", " ", str(text)).strip()[:350]
        if not text or text in seen:
            continue
        rows.append({"usuario": username, "video_id": vid, "comentario": text,
                     "origen": "Comentario visible en página pública"})
        seen.add(text)
        if len(rows) >= max_comments:
            break
    return rows


def extract_profile(page, username: str, video_limit: int = 10) -> dict:
    """Parse the page already opened by browser; facilitates offline unit tests."""
    states = _states(page)
    record = {"usuario": username, "nombre": _texto(page, SELECTORS["nombre"]),
              "biografia": _texto(page, SELECTORS["biografia"]),
              "seguidores": _texto(page, SELECTORS["seguidores"]),
              "seguidos": _texto(page, SELECTORS["seguidos"]),
              "me_gusta": _texto(page, SELECTORS["me_gusta"]),
              "publicaciones": None, "verificada": None, "cuenta_privada": None,
              "url": f"https://www.tiktok.com/@{username}",
              "fecha_consulta": datetime.now().astimezone().isoformat(timespec="seconds"),
              "origen": "TikTok público · Playwright"}
    found_verified = False
    for state in states:
        user, stats = user_from_state(state, username)
        if not user:
            continue
        found_verified = True
        record["nombre"] = user.get("nickname") or record["nombre"]
        record["biografia"] = user.get("signature") if user.get("signature") is not None else record["biografia"]
        for field, key in (("seguidores", "followerCount"), ("seguidos", "followingCount"),
                           ("me_gusta", "heartCount"), ("publicaciones", "videoCount")):
            if stats.get(key) is not None:
                record[field] = stats[key]  # prefer exact values from embedded JSON
        record["verificada"] = user.get("verified") if isinstance(user.get("verified"), bool) else None
        record["cuenta_privada"] = user.get("privateAccount") if isinstance(user.get("privateAccount"), bool) else None
    if not found_verified and not any(record.get(k) for k in ("seguidores", "seguidos", "me_gusta")):
        raise RuntimeError("La página no proporcionó estadísticas públicas verificables para esta cuenta")
    # Bio/name are descriptive text from TikTok and not proof of identity.
    found = videos_from_states(states, username)
    profile_id = None
    for state in states:
        user, _ = user_from_state(state, username)
        if user.get("id"):
            profile_id = str(user["id"])
            break
    for vid,v in videos_del_feed_incrustado(states,username,profile_id).items():
        if vid in found:
            _append_video_metrics(found[vid],v)
        else:
            found[vid]=v
    ids = _video_links(page, username)
    for vid in ids:
        found.setdefault(vid, {"usuario": username, "video_id": vid,
            "url": f"https://www.tiktok.com/@{username}/video/{vid}",
            "descripcion": None, "vistas": None, "likes": None, "comentarios_cantidad": None,
            "compartidos": None, "fecha_publicacion": None, "origen": "Enlace público"})
    # El HTML puede incorporar publicaciones aunque la cuadrícula no renderice enlaces.
    # Sin vínculo visible, exigir autor explícitamente coincidente en ItemModule.
    confirmed_state_ids=set()
    for state in states:
        module=state.get("ItemModule") or {}
        if not isinstance(module,dict): continue
        for vid,item in module.items():
            if not isinstance(item,dict): continue
            author=item.get("author")
            unique=author.get("uniqueId") if isinstance(author,dict) else author
            if isinstance(unique,str) and unique.casefold()==username.casefold():
                confirmed_state_ids.add(str(item.get("id",vid)))
    feed_ids=set(videos_del_feed_incrustado(states,username,profile_id))
    accepted=ids+[vid for vid in found if vid not in ids and (vid in confirmed_state_ids or vid in feed_ids)]
    videos = [found[vid] for vid in accepted if vid in found]
    has_dates = bool(videos) and all(str(v.get("fecha_publicacion") or "").isdigit() for v in videos)
    if has_dates:
        videos.sort(key=lambda v: int(v["fecha_publicacion"]), reverse=True)
    record["videos"] = videos[:video_limit]
    record["orden_videos"] = "fecha_publicacion" if has_dates else "orden_visible_no_confirmado"
    record["videos_detectados"] = len(record["videos"])
    return record


def scrape_batch(usernames: list[str], video_limit: int = 10, detail_limit: int = 10,
                 comments_per_video: int = 5, headless: bool = False,
                 on_progress=None, video_urls: list[dict] | None = None,
                 usar_sesion: bool = True) -> tuple[list[dict], list[dict]]:
    """Actual browser navigation, sequential and bounded. Returns successes + failures."""
    users, uniq = [], set()
    for raw in usernames[:5]:
        try:
            u = limpiar_usuario(raw)
            if u.casefold() not in uniq:
                users.append(u); uniq.add(u.casefold())
        except ValueError:
            continue
    if not users:
        return [], [{"usuario": "-", "error": "Sin usuarios válidos"}]
    records, failures = [], []
    video_urls=video_urls or []
    with sync_playwright() as p:
        browser = None
        if usar_sesion:
            # Contexto persistente exclusivo. No se copia ninguna cookie al repositorio.
            ctx = abrir_contexto(p)
        else:
            browser = p.chromium.launch(headless=headless)
            ctx = browser.new_context(locale="es-ES", viewport={"width": 1380, "height": 960})
        try:
            for index, user in enumerate(users):
                if on_progress:
                    on_progress(index, len(users), user)
                page = ctx.new_page()
                feed_responses=[]
                def _capture_response(res):
                    # Observar únicamente las respuestas públicas cargadas por el propio perfil.
                    # No se invocan endpoints internos ni se reutilizan sesiones privadas.
                    path=urlparse(res.url).path.lower()
                    if "item_list" in path or "user-post" in path:
                        feed_responses.append(res)
                page.on("response",_capture_response)
                try:
                    response = page.goto(f"https://www.tiktok.com/@{user}",
                                         wait_until="domcontentloaded", timeout=25000)
                    if response and response.status in (403, 429):
                        raise RuntimeError(f"TikTok respondió HTTP {response.status}; consulta detenida para esta cuenta")
                    try:
                        page.locator('[data-e2e="followers-count"], script#__UNIVERSAL_DATA_FOR_REHYDRATION__, script#SIGI_STATE').first.wait_for(timeout=5500)
                    except PWTimeout:
                        pass
                    page.wait_for_timeout(1100)
                    # Algunas cuentas muestran la cuadrícula solo al hacer scroll.
                    if video_limit:
                        # Scroll limitado: algunas listas se muestran progresivamente.
                        for _ in range(4):
                            if len(_video_links(page, user)) >= video_limit:
                                break
                            page.mouse.wheel(0, 920)
                            page.wait_for_timeout(900)
                    record = extract_profile(page, user, video_limit=video_limit)
                    profile_id=None
                    for state in _states(page):
                        u,_=user_from_state(state,user)
                        if u.get("id"):
                            profile_id=str(u["id"])
                            break
                    by_id={v["video_id"]:v for v in record["videos"]}
                    for res in feed_responses:
                        try:
                            if res.status!=200: continue
                            data=res.json()
                        except (ValueError,PWError,PWTimeout):
                            continue
                        for vid,video in _feed_videos(data,user,profile_id).items():
                            if vid in by_id:
                                _append_video_metrics(by_id[vid],video)
                            else: by_id[vid]=video
                    ordered=list(by_id.values())
                    if ordered and all(str(v.get("fecha_publicacion") or "").isdigit() for v in ordered):
                        ordered.sort(key=lambda v:int(v["fecha_publicacion"]),reverse=True)
                        record["orden_videos"]="fecha_publicacion"
                    record["videos"]=ordered[:video_limit]
                    record["videos_detectados"]=len(record["videos"])
                    record["fuente_lista_videos"]="HTML / datos incrustados / respuestas observadas"
                    # Consultar páginas de publicación públicas, si se solicita.
                    comments = []
                    detail_failures = 0
                    for v in record["videos"][:max(0, min(detail_limit, video_limit))]:
                        detailpage = ctx.new_page()
                        try:
                            resp = detailpage.goto(v["url"], wait_until="domcontentloaded", timeout=18000)
                            if resp and resp.status in (403, 429):
                                detail_failures += 1
                                break
                            detailpage.wait_for_timeout(800)
                            from_page = videos_from_states(_states(detailpage), user).get(v["video_id"])
                            if from_page:
                                _append_video_metrics(v,from_page)
                            _append_video_metrics(v,_public_video_metadata(detailpage,user,v["video_id"]))
                            if comments_per_video:
                                # Scroll limitado para cargar comentarios visibles; sin inicio de sesión.
                                detailpage.mouse.wheel(0,650)
                                detailpage.wait_for_timeout(500)
                                comments.extend(_comments_public(detailpage, user, v["video_id"], min(comments_per_video, 15)))
                        except (PWTimeout, PWError):
                            detail_failures += 1
                        finally:
                            detailpage.close()
                        time.sleep(0.5)
                    record["comentarios_publicos"] = comments
                    record["detalle_videos_fallidos"] = detail_failures
                    record["videos_con_vistas"] = sum(1 for v in record["videos"] if v.get("vistas") is not None)
                    record["videos_con_likes"] = sum(1 for v in record["videos"] if v.get("likes") is not None)
                    record["sesion_local"] = bool(usar_sesion)
                    records.append(record)
                except (PWTimeout, PWError, RuntimeError) as exc:
                    mensaje = str(exc)[:260]
                    failures.append({"usuario": user, "error": mensaje})
                    if "HTTP 403" in mensaje or "HTTP 429" in mensaje:
                        break  # respetar la negativa del servidor, no insistir con otras cuentas
                finally:
                    page.close()
                if index + 1 < len(users):
                    time.sleep(1.2)
        finally:
            ctx.close()
            if browser is not None:
                browser.close()
    return records, failures
