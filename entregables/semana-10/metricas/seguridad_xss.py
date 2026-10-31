"""A05:2025 Injection (XSS): datos con HTML/JS en nombres, comunidad y tutor no deben ejecutarse en ninguna pantalla.

Uso (raiz del repositorio): PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python entregables/semana-10/metricas/seguridad_xss.py
Servidor demo en 127.0.0.1:8765 con datos sinteticos. Se registra por la API un nino con cargas `<img onerror>`, `<script>` y
`<svg onload>`; luego se recorren Seguimiento, Expediente, Alertas, Visitas, Recordatorios y Sincronizacion, y tambien se registra
uno mas desde el formulario (toast). Resultado: metricas/salidas/OWASP_xss.json y capturas en evidencias/seguridad/.
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capturar_software as cs  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

OUT = cs.BASE / "evidencias" / "seguridad"
CARGAS = {
    "nombres": '<img src=x onerror="window.__xss=1">',
    "apellidos": "<script>window.__xss=2</script>",
    "comunidad": "<b>Palm</b>",
    "tutor_nombre": "<svg onload=window.__xss=3>",
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    proc = cs.levantar({})
    res = {"cargas": CARGAS, "pantallas": []}
    try:
        hoy = date.today()
        cuerpo = {
            "nino": {"dni": "72999999", "nombres": CARGAS["nombres"], "apellidos": CARGAS["apellidos"], "sexo": "F", "fecha_nacimiento": "2025-03-01", "establecimiento": "P. S. Chongos Alto", "distrito": "Chongos Alto", "comunidad": CARGAS["comunidad"], "altitud_m": 3720, "tutor_nombre": CARGAS["tutor_nombre"], "tutor_celular": "955111222"},
            "evaluacion_inicial": {"fecha": (hoy - timedelta(days=100)).isoformat(), "hemoglobina_observada": 9.0, "peso_kg": 8.4, "talla_cm": 71},
        }
        r = cs.api("POST", "/api/ninos", json=cuerpo)
        assert r.status_code == 201, r.text
        res["registro_api_http"] = r.status_code
        cs.api("POST", "/api/recordatorios/generar")
        with sync_playwright() as p:
            nav = p.chromium.launch()
            ctx = nav.new_context(viewport=cs.ESC, locale="es-PE", timezone_id="America/Lima")
            pg = ctx.new_page()
            dialogos = []
            pg.on("dialog", lambda d: (dialogos.append(d.message), d.dismiss()))
            pg.goto(cs.URL)
            pg.get_by_test_id("tab-registro").wait_for()

            def revisar(nombre, captura):
                pg.wait_for_timeout(500)
                x = pg.evaluate("typeof window.__xss === 'undefined' ? null : window.__xss")
                inyectados = pg.evaluate("document.querySelectorAll('#aplicacion img[src=x], #aplicacion script:not([src]), #aplicacion svg[onload], #aplicacion b').length")
                texto = pg.evaluate("document.body.innerText")
                visible_literal = "<img src=x" in texto or "<script>" in texto or "<svg onload" in texto
                res["pantallas"].append({"pantalla": nombre, "window___xss": x, "elementos_inyectados_en_dom": inyectados, "texto_literal_visible": visible_literal})
                cs.shot(pg, captura, completa=False)
                pg.screenshot(path=str(OUT / f"{captura}.png"), full_page=False)
                (cs.IMG / f"{captura}.png").unlink(missing_ok=True)

            pg.get_by_test_id("tab-seguimiento").click()
            pg.get_by_test_id("buscar").fill("72999999")
            pg.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length === 1")
            revisar("Seguimiento", "XSS1_seguimiento")
            pg.locator("#cuerpo-seguimiento tr").first.click()
            pg.get_by_test_id("tabla-evaluaciones").wait_for()
            revisar("Expediente", "XSS2_expediente")
            pg.get_by_test_id("tab-alertas").click()
            pg.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0")
            revisar("Alertas", "XSS3_alertas")
            pg.get_by_test_id("tab-visitas").click()
            pg.get_by_test_id("visita-priorizada").first.wait_for()
            revisar("Visitas", "XSS4_visitas")
            pg.get_by_test_id("tab-recordatorios").click()
            pg.get_by_test_id("recordatorios-generar").click()
            pg.wait_for_timeout(800)
            revisar("Recordatorios", "XSS5_recordatorios")
            pg.get_by_test_id("tab-registro").click()
            pg.reload()
            cs.llenar(pg, "72999998", nombres=CARGAS["nombres"], apellidos=CARGAS["apellidos"])
            pg.fill("#comunidad", CARGAS["comunidad"])
            pg.get_by_test_id("guardar").click()
            pg.get_by_test_id("tabla-evaluaciones").wait_for()
            revisar("Registro (toast y expediente)", "XSS6_registro_ui")
            res["dialogos_javascript"] = dialogos
            nav.close()
    finally:
        proc.terminate()
        proc.wait()
    res["ejecucion_de_codigo"] = any(x["window___xss"] is not None for x in res["pantallas"]) or bool(res["dialogos_javascript"])
    res["estado"] = "CUMPLE" if not res["ejecucion_de_codigo"] and all(x["elementos_inyectados_en_dom"] == 0 for x in res["pantallas"]) else "HALLAZGO"
    (cs.BASE / "metricas" / "salidas" / "OWASP_xss.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    for x in res["pantallas"]:
        print(f"{x['pantalla']:<32} window.__xss={x['window___xss']}  nodos inyectados={x['elementos_inyectados_en_dom']}  texto literal visible={x['texto_literal_visible']}")
    print("Dialogos JavaScript:", res["dialogos_javascript"], "| estado:", res["estado"])


if __name__ == "__main__":
    main()
