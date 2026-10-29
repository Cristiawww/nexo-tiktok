"use strict";
// NEXO · consulta limitada y solicitada por el usuario, sin llamadas a APIs privadas.
// Se consulta una página pública a la vez, desde Chrome normal, respetando errores de acceso.
let running = null;
const MAX_VIDEOS = 10;
const MAX_PERFILES = 5;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

function updateVideo(oldValue = {}, fresh = {}) {
  const next = { ...oldValue };
  for (const [key, value] of Object.entries(fresh)) {
    if (value !== null && value !== undefined && value !== "") next[key] = value;
  }
  return next;
}
function mergeProfile(previous, incoming) {
  const combined = { ...(previous || {}) };
  for (const [key, value] of Object.entries(incoming || {})) {
    if (["videos", "comentarios_publicos"].includes(key)) continue;
    if (value !== null && value !== undefined && value !== "") combined[key] = value;
  }
  const previousById = new Map((previous?.videos || []).map(v=>[String(v.video_id),v]));
  const incomingRows = incoming?.videos?.length ? incoming.videos : (previous?.videos || []);
  const byId = new Map();
  for (const video of incomingRows) {
    if (!/^\d{6,25}$/.test(String(video?.video_id || ""))) continue;
    const key = String(video.video_id);
    byId.set(key, updateVideo(previousById.get(key), video));
  }
  combined.videos = [...byId.values()].slice(0, MAX_VIDEOS);
  const comments = new Map();
  for (const comment of [...(previous?.comentarios_publicos || []), ...(incoming?.comentarios_publicos || [])]) {
    if (typeof comment.comentario !== "string" || !comment.comentario.trim()) continue;
    const key = `${comment.video_id}|${comment.comentario.trim()}`;
    comments.set(key, comment);
  }
  combined.comentarios_publicos = [...comments.values()].slice(0, 100);
  combined.videos_detectados = combined.videos.length;
  combined.videos_con_metricas = combined.videos.filter(v => v.likes != null && v.vistas != null).length;
  return combined;
}

async function status(message, extra = {}) {
  await chrome.storage.local.set({
    progreso_nexo: { mensaje: message, ejecutando: Boolean(running && !running.cancelled), fecha: Date.now(), ...extra }
  });
}

async function readTab(tabId, detail = false) {
  await chrome.scripting.executeScript({target: {tabId}, files: ["reader.js"]});
  const result = await chrome.scripting.executeScript({
    target: {tabId}, func: async () => globalThis.nexoCaptureOpenPage()
  });
  const data = result?.[0]?.result;
  if (!data || data.error) throw new Error(data?.error || "No se pudo leer la página.");
  if (detail && !data.detalle) throw new Error("La publicación no se abrió correctamente.");
  return data.perfil;
}

async function waitUntilLoaded(tabId, timeoutMs = 16000) {
  const t = await chrome.tabs.get(tabId);
  if (t?.status === "complete") return;
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { chrome.tabs.onUpdated.removeListener(listener); reject(new Error("La publicación tardó demasiado en cargar.")); }, timeoutMs);
    function listener(id, changeInfo) {
      if (id === tabId && changeInfo.status === "complete") {
        clearTimeout(timer);
        chrome.tabs.onUpdated.removeListener(listener);
        resolve();
      }
    }
    chrome.tabs.onUpdated.addListener(listener);
  });
}

async function processProfile(tabId) {
  let done = 0, errors = 0;
  await status("Buscando publicaciones del perfil…", {completados: 0, total: MAX_VIDEOS});
  const tab = await chrome.tabs.get(tabId);
  const link = new URL(tab.url || "");
  const match = link.pathname.match(/^\/@([A-Za-z0-9._]{1,24})\/?$/);
  if (!(["www.tiktok.com", "tiktok.com", "m.tiktok.com"].includes(link.hostname) && match)) {
    throw new Error("Abre primero el perfil público @usuario en TikTok, no la página de inicio ni un video.");
  }
  let data = await readTab(tabId);
  if (data.cuenta_privada === true) throw new Error("La cuenta es privada y no se analizará.");
  if (data.usuario.toLowerCase() !== match[1].toLowerCase()) {
    throw new Error("El usuario leído no coincide con el perfil solicitado.");
  }
  const { perfiles = [] } = await chrome.storage.local.get("perfiles");
  const previous = perfiles.find(p => p.usuario.toLowerCase() === data.usuario.toLowerCase());
  if (!previous && perfiles.length >= MAX_PERFILES) {
    throw new Error("Solo se permiten cinco cuentas por comparación. Exporta o vacía la captura.");
  }
  const selected = (data.videos || []).filter(v => /^\d{6,25}$/.test(String(v.video_id || ""))).slice(0, MAX_VIDEOS);
  data.videos = selected;
  data.orden_videos = data.orden_videos || "primeras_publicaciones_visibles_no_necesariamente_cronologicas";
  if (!selected.length) {
    await storeProfile(data);
    await status("Perfil guardado, sin publicaciones accesibles en la página.", {completados:0,total:0});
    return;
  }
  await storeProfile(data);
  for (let index = 0; index < selected.length; index++) {
    if (!running || running.cancelled) break;
    const video = selected[index];
    await status(`Publicación ${index+1} de ${selected.length}`, {completados: index,total:selected.length,usuario:data.usuario});
    let detailTab = null;
    try {
      // Solo se abren URLs de publicaciones públicas que ya estaban en el perfil.
      detailTab = await chrome.tabs.create({url:`https://www.tiktok.com/@${data.usuario}/video/${video.video_id}`,active:false});
      await waitUntilLoaded(detailTab.id);
      await delay(950);
      const current = await chrome.tabs.get(detailTab.id);
      const currentPath = new URL(current.url || "https://www.tiktok.com/").pathname;
      if (!currentPath.includes(`/@${data.usuario}/video/${video.video_id}`)) throw new Error("La página redirigió a otro contenido.");
      const detail = await readTab(detailTab.id, true);
      const exact = (detail.videos || []).find(v=>String(v.video_id)===String(video.video_id));
      if (detail.usuario.toLowerCase() !== data.usuario.toLowerCase() || !exact) throw new Error("Los datos no corresponden a este video.");
      const baseIndex = data.videos.findIndex(v=>String(v.video_id)===String(video.video_id));
      data.videos[baseIndex] = updateVideo(data.videos[baseIndex], exact);
      for (const comment of detail.comentarios_publicos || []) {
        if (String(comment.video_id)===String(video.video_id)) data.comentarios_publicos.push(comment);
      }
    } catch (error) {
      errors++;
      // Mantener el video sin cifras en lugar de atribuir métricas ajenas.
      data.videos[index].error_captura = String(error?.message || error).slice(0, 150);
    } finally {
      if (detailTab?.id) try { await chrome.tabs.remove(detailTab.id); } catch (_) {}
      done++;
      await storeProfile(data);
    }
    await delay(900);
  }
  await status(running?.cancelled ? "Análisis detenido." : `Finalizado: ${done} publicaciones revisadas, ${errors} sin acceso completo.`,
    {completados:done,total:selected.length,usuario:data.usuario,fallos:errors});
}

async function storeProfile(data) {
  const { perfiles = [] } = await chrome.storage.local.get("perfiles");
  const i = perfiles.findIndex(p=>p.usuario?.toLowerCase()===data.usuario.toLowerCase());
  if (i < 0 && perfiles.length >= MAX_PERFILES) throw new Error("Límite de cinco perfiles.");
  const next = [...perfiles];
  if (i >= 0) next[i] = mergeProfile(perfiles[i], data);
  else next.push(mergeProfile(null,data));
  await chrome.storage.local.set({perfiles: next});
}

chrome.runtime.onMessage.addListener((message, sender, respond) => {
  if (message?.type === "START_NEXO") {
    if (running) {respond({ok:false,error:"Ya hay un análisis en curso."});return false;}
    running = {cancelled:false};
    respond({ok:true});
    (async () => {
      try {await processProfile(message.tabId);}
      catch (err) {await status(`Error: ${String(err?.message || err).slice(0,190)}`,{error:true});}
      finally {
        running = null;
        const {progreso_nexo:p={}} = await chrome.storage.local.get("progreso_nexo");
        await chrome.storage.local.set({progreso_nexo:{...p,ejecutando:false}});
      }
    })();
    return false;
  }
  if (message?.type === "STOP_NEXO") {
    if (running) running.cancelled = true;
    respond({ok:true});return false;
  }
  return false;
});
