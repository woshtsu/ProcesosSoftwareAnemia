/* Service worker (HIST-3.1). Precachea el shell de la aplicación y sirve las lecturas (GET de la API) con la estrategia
   «red primero, caché de respaldo»: sin conexión la aplicación abre y muestra los últimos datos consultados, con la
   cabecera X-Desde-Cache para que la interfaz lo avise. Las escrituras no pasan por aquí: se guardan en la cola del
   dispositivo (IndexedDB) y las envía Sync. El caché de datos se borra al cerrar sesión (auth.js). */
const VERSION = "v4";
const CACHE_SHELL = `anemia-junin-shell-${VERSION}`;
const CACHE_DATOS = `anemia-junin-datos-${VERSION}`;
const SHELL = [
  "/", "/static/estilos.css", "/static/auth.js", "/static/cola.js", "/static/sync.js", "/static/app.js",
  "/static/icono.svg", "/static/manifest.json",
];
const VENDOR = ["/static/vendor/swagger-ui.css", "/static/vendor/swagger-ui-bundle.js"];
const PRECARGA_API = ["/api/auth/config", "/api/salud"]; // para que la aplicación abra sin conexión desde la primera visita
const SIN_CACHE = ["/api/sincronizacion", "/api/auth/login", "/api/auth/logout"];

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE_SHELL);
    await c.addAll(SHELL);
    await Promise.allSettled(VENDOR.map((u) => c.add(u))); // la documentación de la API: si falla, no impide instalar
    const datos = await caches.open(CACHE_DATOS);
    await Promise.allSettled(PRECARGA_API.map((u) => datos.add(u)));
    await self.skipWaiting();
  })());
});
self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    const vigentes = [CACHE_SHELL, CACHE_DATOS];
    await Promise.all((await caches.keys()).filter((k) => !vigentes.includes(k)).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

async function redPrimero(peticion, nombreCache, marcar) {
  const cache = await caches.open(nombreCache);
  try {
    const r = await fetch(peticion);
    if (r.ok) cache.put(peticion, r.clone());
    return r;
  } catch (error) {
    const guardada = await cache.match(peticion);
    if (!guardada) throw error;
    if (!marcar) return guardada;
    const cabeceras = new Headers(guardada.headers);
    cabeceras.set("X-Desde-Cache", "1");
    return new Response(guardada.body, { status: guardada.status, statusText: guardada.statusText, headers: cabeceras });
  }
}

self.addEventListener("fetch", (e) => {
  const { request } = e;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || request.method !== "GET") return;
  if (url.pathname.startsWith("/api/")) {
    if (SIN_CACHE.some((p) => url.pathname.startsWith(p)) || url.searchParams.has("formato")) return;
    e.respondWith(redPrimero(request, CACHE_DATOS, true));
  } else if (request.mode === "navigate" && url.pathname === "/") {
    e.respondWith(redPrimero(new Request("/"), CACHE_SHELL, false));
  } else if (url.pathname === "/" || url.pathname.startsWith("/static/")) {
    e.respondWith(redPrimero(request, CACHE_SHELL, false));
  }
});
