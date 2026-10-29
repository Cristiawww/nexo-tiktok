"use strict";
const $ = id => document.getElementById(id);
let timer = null;
function say(message) {$("status").textContent=message;}
async function refresh() {
  const {perfiles=[], progreso_nexo:p={}}=await chrome.storage.local.get(["perfiles","progreso_nexo"]);
  $("count").textContent=`${perfiles.length} / 5`;
  $("export").disabled=!perfiles.length;
  const active=Boolean(p.ejecutando && (Date.now()-(p.fecha||0)<240000));
  $("start").disabled=active;
  $("stop").disabled=!active;
  if(p.mensaje) say(p.mensaje);
  $("progress").value=p.completados || 0;
  $("progress").max=Math.max(1,p.total || 1);
  $("progress-label").textContent=p.total ? `${p.completados || 0} / ${p.total}` : "";
  const totalVideos=perfiles.reduce((total,p)=>total+(p.videos?.length || 0),0);
  const metricas=perfiles.reduce((total,p)=>total+(p.videos || []).filter(v=>v.vistas!=null&&v.likes!=null).length,0);
  $("summary").textContent=`${totalVideos} publicaciones · ${metricas} con vistas y likes`;
}
$("start").addEventListener("click",async()=>{
  try {
    const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
    if(!tab?.id)throw new Error("No hay una pestaña activa.");
    const url=new URL(tab.url || "");
    if(!["www.tiktok.com","tiktok.com","m.tiktok.com"].includes(url.hostname) || !/^\/@[A-Za-z0-9._]{1,24}\/?$/.test(url.pathname)){
      throw new Error("Abre un perfil público, por ejemplo tiktok.com/@usuario.");
    }
    const response=await chrome.runtime.sendMessage({type:"START_NEXO",tabId:tab.id});
    if(!response?.ok) throw new Error(response?.error || "No pudo comenzar.");
    say("Iniciando análisis…");
    await refresh();
  }catch(err){say(String(err?.message || err));}
});
$("stop").addEventListener("click",async()=>{
  await chrome.runtime.sendMessage({type:"STOP_NEXO"});say("Deteniendo después de la publicación actual…");
});
$("export").addEventListener("click",async()=>{
  const {perfiles=[]}=await chrome.storage.local.get("perfiles");
  if(!perfiles.length)return say("Todavía no hay cuentas guardadas.");
  const obj={origen:"NEXO - captura local en Chrome",version:2,fecha_exportacion:new Date().toISOString(),perfiles};
  const url=URL.createObjectURL(new Blob([JSON.stringify(obj,null,2)],{type:"application/json"}));
  const a=document.createElement("a");a.href=url;a.download="nexo_captura_chrome.json";
  document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),3000);
  say(`Archivo generado: ${perfiles.length} perfiles.`);
});
$("clear").addEventListener("click",async()=>{
  const {progreso_nexo:p={}}=await chrome.storage.local.get("progreso_nexo");
  if(p.ejecutando){say("Detén primero el análisis.");return;}
  await chrome.storage.local.remove(["perfiles","progreso_nexo"]);
  say("Capturas borradas.");await refresh();
});
chrome.storage.onChanged.addListener((changes,area)=>{
  if(area==="local"&&(changes.progreso_nexo||changes.perfiles))refresh();
});
refresh(); timer=setInterval(refresh,1200);
