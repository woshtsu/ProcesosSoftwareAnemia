"""Graba la demostración del PMV (video .webm) y genera capturas de evidencia.

Requiere el servidor en ejecución con datos de prueba:
    python -m scripts.cargar_datos_prueba
    uvicorn app.main:crear_app --factory --port 8000
    python -m scripts.grabar_demo --url http://127.0.0.1:8000 --salida docs/evidencias
"""

import argparse
import shutil
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

LEYENDA_JS = """(t) => {
  let d = document.getElementById('leyenda-demo');
  if (!d) {
    d = document.createElement('div'); d.id = 'leyenda-demo';
    d.style.cssText = 'position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:99;' +
      'background:rgba(20,45,75,.94);color:#fff;padding:10px 22px;border-radius:12px;font:600 17px Segoe UI,sans-serif;' +
      'box-shadow:0 6px 20px rgba(0,0,0,.25);max-width:88%;text-align:center';
    document.body.appendChild(d);
  }
  d.innerHTML = t;
}"""

PORTADA = """<html><body style="margin:0;height:100vh;display:flex;align-items:center;justify-content:center;
background:linear-gradient(135deg,#1F4E79,#2E5C8A);font-family:Segoe UI,sans-serif;color:#fff;text-align:center">
<div><div style="font-size:20px;opacity:.85;letter-spacing:.5px">Procesos de Software 2026-20 · Demo del PMV</div>
<h1 style="font-size:40px;margin:14px 0 8px">Sistema de Detección Temprana de Anemia Infantil</h1>
<div style="font-size:24px">Zonas rurales de Junín — Incremento 1: registro nominal y expediente digital</div>
<div style="margin-top:28px;font-size:17px;opacity:.9">{texto}</div></div></body></html>"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--salida", default="docs/evidencias")
    args = ap.parse_args()
    salida = Path(args.salida)
    capturas = salida / "capturas"
    capturas.mkdir(parents=True, exist_ok=True)
    tmp_video = salida / "_video_tmp"

    with sync_playwright() as p:
        nav = p.chromium.launch(args=["--lang=es-PE"], env={"LANG": "es_PE.UTF-8", "LANGUAGE": "es_PE:es"})
        ctx = nav.new_context(
            viewport={"width": 1280, "height": 720},
            locale="es-PE",
            timezone_id="America/Lima",
            record_video_dir=str(tmp_video),
            record_video_size={"width": 1280, "height": 720},
        )
        pg = ctx.new_page()

        def leyenda(texto: str, pausa: int = 0) -> None:
            pg.evaluate(LEYENDA_JS, texto)
            if pausa:
                pg.wait_for_timeout(pausa)

        def foto(nombre: str) -> None:
            pg.evaluate("() => { const d = document.getElementById('leyenda-demo'); if (d) d.style.display='none'; }")
            pg.screenshot(path=str(capturas / f"{nombre}.png"), full_page=True)
            pg.evaluate("() => { const d = document.getElementById('leyenda-demo'); if (d) d.style.display='block'; }")

        def escribir(selector: str, texto: str) -> None:
            pg.click(selector)
            pg.fill(selector, "")
            pg.type(selector, texto, delay=45)

        pg.set_content(PORTADA.format(texto="Entorno de staging local · API FastAPI + PostgreSQL 16 · PWA"))
        pg.wait_for_timeout(4500)

        # ---------------- HU-03: validación de datos inválidos ----------------
        pg.goto(args.url)
        pg.wait_for_timeout(800)
        leyenda("HU-03 · El sistema valida los datos antes de guardar", 2200)
        escribir("#dni", "7210001")
        escribir("#nombres", "Mía Valentina")
        escribir("#apellidos", "Poma Ccente")
        pg.select_option("#sexo", "F")
        pg.fill("#fecha_nacimiento", "2025-10-20")
        escribir("#comunidad", "Palmayoc")
        escribir("#altitud_m", "3720")
        escribir("#tutor_nombre", "Elena Ccente Rojas")
        escribir("#tutor_celular", "987123456")
        escribir("#hemoglobina_observada", "24")
        escribir("#peso_kg", "8.6")
        escribir("#talla_cm", "71.5")
        pg.wait_for_timeout(600)
        pg.get_by_test_id("guardar").click()
        pg.wait_for_selector(".campo.invalido")
        leyenda("Criterio de aceptación: rechaza datos fuera de rango con un mensaje comprensible", 3200)
        foto("02_validacion_datos_invalidos")

        # ---------------- HU-01: registro correcto con vista previa ----------------
        leyenda("HU-01 · Corrección y registro del niño con su evaluación inicial", 1500)
        escribir("#dni", "72100001")
        escribir("#hemoglobina_observada", "11.4")
        pg.get_by_test_id("clasificacion-previa").wait_for()
        leyenda("Vista previa: Hb ajustada por altitud (3 720 m) y clasificación automática", 3500)
        foto("01_registro_vista_previa")
        pg.get_by_test_id("guardar").click()
        pg.get_by_test_id("tabla-evaluaciones").wait_for()
        leyenda("HU-02 · Se crea el expediente digital único (sin triple registro)", 3500)
        foto("03_expediente_nuevo")

        # ---------------- HU-04: seguimiento ----------------
        pg.get_by_test_id("tab-seguimiento").click()
        pg.wait_for_timeout(700)
        leyenda("HU-04 · Niños en seguimiento, priorizados por gravedad y días sin control", 3500)
        foto("04_seguimiento")
        pg.select_option("#filtro-clasificacion", "MODERADA")
        pg.wait_for_timeout(1800)
        pg.select_option("#filtro-clasificacion", "")
        escribir("[data-testid=buscar]", "Quispe")
        pg.wait_for_timeout(1500)

        # ---------------- HU-02: expediente y nuevo control ----------------
        pg.locator("#cuerpo-seguimiento tr").first.click()
        pg.get_by_test_id("tabla-evaluaciones").wait_for()
        leyenda("HU-02 · Consulta del expediente y registro de un nuevo control", 2500)
        form = pg.locator("#form-control")
        form.locator("[name=fecha]").fill(date.today().isoformat())
        form.locator("[name=hemoglobina_observada]").type("12.8", delay=60)
        form.locator("[name=peso_kg]").type("8.3", delay=60)
        form.locator("[name=talla_cm]").type("70.2", delay=60)
        pg.get_by_test_id("guardar-control").click()
        pg.wait_for_timeout(1500)
        leyenda("La evolución de la hemoglobina ajustada queda visible para el personal", 3500)
        foto("05_expediente_evolucion")

        # ---------------- HU-05: reporte ----------------
        pg.get_by_test_id("tab-reporte").click()
        pg.get_by_test_id("generar-reporte").click()
        pg.get_by_test_id("kpi-registrados").wait_for()
        pg.wait_for_timeout(600)
        leyenda("HU-05 · Reporte del periodo por clasificación y comunidad (exportable a CSV)", 4000)
        foto("06_reporte_periodo")

        # ---------------- API documentada ----------------
        pg.goto(args.url + "/docs")
        pg.wait_for_timeout(1500)
        leyenda("Contrato de la API REST documentado con OpenAPI (Swagger UI)", 3500)
        foto("08_openapi_swagger")

        pg.set_content(PORTADA.format(texto="PMV entregado · tag v1.0-PMV · 77 pruebas automatizadas · cobertura 99 %"))
        pg.wait_for_timeout(4000)
        video = pg.video.path()
        ctx.close()

        # Captura en vista móvil (sin video)
        movil = nav.new_page(
            viewport={"width": 390, "height": 844}, locale="es-PE", timezone_id="America/Lima", device_scale_factor=2
        )
        movil.goto(args.url)
        movil.get_by_test_id("tab-seguimiento").click()
        movil.wait_for_timeout(800)
        movil.screenshot(path=str(capturas / "07_vista_movil.png"), full_page=False)
        nav.close()

    destino = salida / "demo_pmv.webm"
    shutil.move(video, destino)
    shutil.rmtree(tmp_video, ignore_errors=True)
    print("Video:", destino)


if __name__ == "__main__":
    main()
