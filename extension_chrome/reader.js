"use strict";
// Captura contenido renderizado en TikTok público; no accede a cookies ni endpoints privados.
async function captureOpenPage() {
  // Esta función se ejecuta dentro de la pestaña abierta de TikTok.
  const hostname = location.hostname.toLowerCase();
  if (!["www.tiktok.com", "tiktok.com", "m.tiktok.com"].includes(hostname)) {
    return { error: "Abre un perfil o video de TikTok antes de guardar." };
  }
  const match = location.pathname.match(/^\/@([\w.]{1,24})(?:\/video\/(\d+))?/);
  if (!match) return { error: "Abre una dirección del tipo tiktok.com/@usuario." };
  const username = match[1];
  const detailId = match[2] || null;
  const safeText = (txt, max = 600) => String(txt || "").replace(/\s+/g, " ").trim().slice(0, max);
  const text = (selectors) => {
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) {
        const val = safeText(el.textContent, 400);
        if (val) return val;
      }
    }
    return null;
  };
  const stateList = [];
  for (const id of ["__UNIVERSAL_DATA_FOR_REHYDRATION__", "SIGI_STATE"]) {
    const tag = document.getElementById(id);
    if (!tag?.textContent) continue;
    try { const obj = JSON.parse(tag.textContent); if (obj && typeof obj === "object") stateList.push(obj); } catch (_) {}
  }
  const result = {
    usuario: username, nombre: text(['[data-e2e="user-title"]']),
    biografia: text(['[data-e2e="user-bio"]']),
    seguidores: text(['[data-e2e="followers-count"]']),
    seguidos: text(['[data-e2e="following-count"]']),
    me_gusta: text(['[data-e2e="likes-count"]']),
    publicaciones: null, verificada: null, cuenta_privada: null,
    url: `https://www.tiktok.com/@${username}`,
    fecha_consulta: new Date().toISOString(),
    origen: "Chrome · captura local de página pública",
    videos: [], comentarios_publicos: []
  };
  const videos = new Map();
  const makeVideo = (vid) => ({ usuario: username, video_id: String(vid),
    url: `https://www.tiktok.com/@${username}/video/${vid}`,
    descripcion: null, vistas: null, likes: null, comentarios_cantidad: null,
    compartidos: null, fecha_publicacion: null, origen: "Enlace visible en Chrome" });
  const put = (id, item, source) => {
    const vid = String(id || "");
    if (!/^\d{6,25}$/.test(vid)) return;
    if (item && typeof item === "object") {
      const author = item.author;
      const authorName = typeof author === "object" && author ? author.uniqueId : author;
      if (authorName && String(authorName).toLowerCase() !== username.toLowerCase()) return;
    }
    const base = videos.get(vid) || makeVideo(vid);
    const stats = item?.stats || item?.statsV2 || {};
    const values = { descripcion: item?.desc, vistas: stats.playCount,
      likes: stats.diggCount, comentarios_cantidad: stats.commentCount,
      compartidos: stats.shareCount, fecha_publicacion: item?.createTime };
    for (const [key, val] of Object.entries(values)) {
      if (val !== undefined && val !== null && val !== "") base[key] = val;
    }
    if (item) base.origen = source;
    videos.set(vid, base);
  };
  // Se lee solo información ya incluida en la página pública abierta.
  for (const state of stateList) {
    const scope = state?.__DEFAULT_SCOPE__ || {};
    const detail = scope?.["webapp.user-detail"]?.userInfo || {};
    const olderUsers = state?.UserModule?.users || {};
    let user = detail.user || null;
    let stats = detail.stats || detail.statsV2 || {};
    if (!user || String(user.uniqueId || "").toLowerCase() !== username.toLowerCase()) {
      user = null;
      for (const [id, candidate] of Object.entries(olderUsers)) {
        if (String(candidate?.uniqueId || "").toLowerCase() === username.toLowerCase()) {
          user = candidate;
          stats = state.UserModule?.stats?.[id] || {};
          break;
        }
      }
    }
    if (user) {
      result.nombre = user.nickname || result.nombre;
      result.biografia = user.signature ?? result.biografia;
      for (const [field, key] of [["seguidores", "followerCount"], ["seguidos", "followingCount"], ["me_gusta", "heartCount"], ["publicaciones", "videoCount"]]) {
        if (stats[key] !== undefined && stats[key] !== null) result[field] = stats[key];
      }
      result.verificada = typeof user.verified === "boolean" ? user.verified : null;
      result.cuenta_privada = typeof user.privateAccount === "boolean" ? user.privateAccount : null;
    }
    for (const item of Object.values(state?.ItemModule || {})) {
      if (!item || typeof item !== "object") continue;
      const author = typeof item.author === "object" ? item.author?.uniqueId : item.author;
      // Un objeto sin autor comprobable no se atribuye a esta cuenta.
      if (!author || String(author).toLowerCase() !== username.toLowerCase()) continue;
      put(item.id, item, "Datos incrustados en página");
    }
    const post = scope?.["webapp.user-post"] || {};
    const pools = user ? [post, post?.data || {}] : [];
    for (const pool of pools) {
      const list = pool?.itemList || pool?.item_list || [];
      if (!Array.isArray(list)) continue;
      for (const entry of list) {
        if (typeof entry === "string") put(entry, null, "Lista pública");
        else if (entry?.id) put(entry.id, entry, "Lista pública");
      }
    }
    const struct = scope?.["webapp.video-detail"]?.itemInfo?.itemStruct;
    if (detailId && struct?.id && String(struct.id) === detailId) put(detailId, struct, "Detalle del video");
  }
  // El desplazamiento carga únicamente la cuadrícula de la página que el usuario ya abrió.
  if (!detailId) {
    for (let attempt = 0; attempt < 8; attempt++) {
      const count = [...document.querySelectorAll('a[href*="/video/"]')]
        .filter(a => a.href.includes(`/@${username}/video/`)).length;
      if (count >= 10) break;
      window.scrollBy({top: 720, behavior: "instant"});
      await new Promise(resolve => setTimeout(resolve, 750));
    }
  }
  const domOrder = [];
  for (const a of document.querySelectorAll('a[href*="/video/"]')) {
    let u;
    try { u = new URL(a.href); } catch (_) { continue; }
    if (!['www.tiktok.com', 'tiktok.com', 'm.tiktok.com'].includes(u.hostname)) continue;
    const m = u.pathname.match(/^\/@([\w.]{1,24})\/video\/(\d+)/);
    if (!m || m[1].toLowerCase() !== username.toLowerCase()) continue;
    if (!domOrder.includes(m[2])) domOrder.push(m[2]);
    put(m[2], null, "Enlace visible");
    const views = a.querySelector('[data-e2e="video-views"],strong[data-e2e="video-views"],strong');
    if (views && views.textContent?.trim()) {
      const item = videos.get(m[2]);
      if (item && item.vistas == null) item.vistas = safeText(views.textContent, 30);
    }
  }
  if (detailId) {
    put(detailId, null, "Página del video");
    const current = videos.get(detailId);
    const counters = [
      ["likes", ['[data-e2e="like-count"]','[data-e2e="browse-like-count"]']],
      ["comentarios_cantidad", ['[data-e2e="comment-count"]','[data-e2e="browse-comment-count"]']],
      ["compartidos", ['[data-e2e="share-count"]','[data-e2e="browse-share-count"]']],
      ["vistas", ['[data-e2e="video-views"]','[data-e2e="play-count"]']]
    ];
    for (const [field, selectors] of counters) {
      if (current[field] == null) current[field] = text(selectors);
    }
    if (!current.descripcion) current.descripcion = text(['[data-e2e="browse-video-desc"]','[data-e2e="video-desc"]']);
    const selector = '[data-e2e="comment-level-1"] [data-e2e="comment-content"], [data-e2e="comment-content"]';
    const distinct = new Set();
    for (const el of document.querySelectorAll(selector)) {
      const comment = safeText(el.textContent, 350);
      if (!comment || distinct.has(comment)) continue;
      distinct.add(comment);
      result.comentarios_publicos.push({usuario:username,video_id:detailId,comentario:comment,origen:"Comentario visible en Chrome"});
      if (result.comentarios_publicos.length >= 20) break;
    }
  }
  if (result.cuenta_privada === true) return { error: "Esta cuenta está marcada como privada; no se importarán sus publicaciones." };
  const collected = [...videos.values()];
  // Solo llamamos "más recientes" a los videos si se recuperaron fechas suficientes.
  const dated = collected.length >= 10 && collected.every(v => Number(v.fecha_publicacion) > 0);
  if (!detailId && dated) {
    collected.sort((a,b)=>Number(b.fecha_publicacion)-Number(a.fecha_publicacion));
  } else if (!detailId) {
    const idx=id=>domOrder.indexOf(String(id));
    collected.sort((a,b)=>{
      const ai=idx(a.video_id),bi=idx(b.video_id);
      if(ai>=0 && bi>=0) return ai-bi;
      if(ai>=0) return -1;
      if(bi>=0) return 1;
      return 0;
    });
  }
  result.videos = collected.slice(0, 10);
  result.videos_detectados = result.videos.length;
  result.orden_videos = dated ? "fecha_publicacion_descendente" : "primeras_publicaciones_visibles_orden_no_confirmado";
  return { perfil: result, detalle: Boolean(detailId) };
}


globalThis.nexoCaptureOpenPage = captureOpenPage;
