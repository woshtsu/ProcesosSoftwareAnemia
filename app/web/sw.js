/* Service worker del PMV: guarda en caché la interfaz para que abra con conectividad intermitente.
   La cola de sincronización de registros se implementa en el Incremento 3. */
const CACHE = "anemia-junin-pmv-v1";
const RECURSOS = ["/", "/static/estilos.css", "/static/app.js", "/static/icono.svg", "/static/manifest.json"];
self.addEventListener("install", (e) => e.waitUntil(caches.open(CACHE).then((c) => c.addAll(RECURSOS))));
self.addEventListener("activate", (e) => e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))));
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.pathname.startsWith("/api/")) return;
  e.respondWith(fetch(e.request).then((r) => { const copia = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, copia)); return r; }).catch(() => caches.match(e.request)));
});
