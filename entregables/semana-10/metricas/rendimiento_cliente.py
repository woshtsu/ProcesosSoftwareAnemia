"""Factor P (cliente PWA): FCP, LCP, carga y transferencia de la aplicacion con CPU 4x mas lenta y red 4G lenta emulada.

Uso (raiz del repositorio): PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python entregables/semana-10/metricas/rendimiento_cliente.py
Servidor demo 127.0.0.1:8765. Perfil movil (390x844), CDP: CPU throttling x4 y red 1.6 Mbps / 150 ms (perfil «Slow 4G» de Lighthouse).
Se mide la primera carga (sin service worker) y la segunda (con shell en cache), 5 repeticiones cada una (mediana).
Salida: metricas/salidas/P_cliente_pwa.json
"""

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capturar_software as cs  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

JS = """() => new Promise(res => {
  const out = {fcp: null, lcp: null};
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (e.name === 'first-contentful-paint') out.fcp = e.startTime; }).observe({type: 'paint', buffered: true});
  new PerformanceObserver(l => { const es = l.getEntries(); out.lcp = es[es.length - 1].startTime; }).observe({type: 'largest-contentful-paint', buffered: true});
  setTimeout(() => { const n = performance.getEntriesByType('navigation')[0]; const rs = performance.getEntriesByType('resource');
    out.dcl = n.domContentLoadedEventEnd; out.load = n.loadEventEnd; out.bytes = n.transferSize + rs.reduce((a, r) => a + r.transferSize, 0); out.recursos = rs.length + 1; res(out); }, 1500);
})"""


def medir(nav, repeticiones, controlada):
    filas = []
    for _ in range(repeticiones):
        ctx = nav.new_context(viewport=cs.MOV, device_scale_factor=2, is_mobile=True, has_touch=True, locale="es-PE", service_workers="allow")
        pg = ctx.new_page()
        cdp = ctx.new_cdp_session(pg)
        if controlada:
            pg.goto(cs.URL)
            pg.evaluate("navigator.serviceWorker.ready.then(() => true)")
            pg.wait_for_timeout(1500)
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
        cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
        pg.goto(cs.URL, wait_until="load")
        filas.append(pg.evaluate(JS))
        ctx.close()
    return {k: round(statistics.median(f[k] for f in filas if f[k] is not None), 1) for k in ("fcp", "lcp", "dcl", "load", "bytes", "recursos")}


def main():
    proc = cs.levantar({})
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch()
            primera = medir(nav, 5, False)
            segunda = medir(nav, 5, True)
            nav.close()
    finally:
        proc.terminate()
        proc.wait()
    res = {"perfil": "movil 390x844, CPU x4, 1.6 Mbps, 150 ms", "repeticiones": 5, "primera_carga": primera, "segunda_carga_con_service_worker": segunda, "umbral_lcp_ms": 2500}
    (cs.BASE / "metricas" / "salidas" / "P_cliente_pwa.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
