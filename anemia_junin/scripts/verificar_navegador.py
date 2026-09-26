"""Aceptación técnica reproducible en Chromium, con datos sintéticos y SQLite temporal."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright

RAIZ = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromium", help="Ejecutable Chromium existente; omitir usa Playwright")
    args = parser.parse_args()
    salida = RAIZ / "docs/evidencias/cierre"
    salida.mkdir(parents=True, exist_ok=True)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        puerto = sock.getsockname()[1]
    with TemporaryDirectory(prefix="anemia_browser_") as temporal:
        db = str(Path(temporal) / "browser.db")
        subprocess.run(
            [sys.executable, "scripts/cargar_datos_sinteticos.py", "--db", db],
            cwd=RAIZ,
            check=True,
            capture_output=True,
        )
        proceso = subprocess.Popen(
            [sys.executable, "-m", "anemia_junin", "--port", str(puerto), "--db", db],
            cwd=RAIZ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        url = f"http://127.0.0.1:{puerto}"
        try:
            for _ in range(100):
                try:
                    with urlopen(url + "/api/v1/salud", timeout=1) as respuesta:
                        assert respuesta.status == 200
                    break
                except OSError:
                    time.sleep(0.1)
            else:
                raise RuntimeError("El servidor no inició")
            with sync_playwright() as pw:
                navegador = pw.chromium.launch(headless=True, executable_path=args.chromium)
                pagina = navegador.new_page(viewport={"width": 1360, "height": 1000})
                pagina.goto(url + "/ninos")
                pagina.screenshot(path=str(salida / "01_listado.png"), full_page=True)
                pagina.goto(url + "/ninos/nuevo")
                inicio = time.perf_counter()
                datos = {
                    "dni": "89000001",
                    "nombres": "Elena",
                    "apellidos": "Demo Sintetica",
                    "fecha_nacimiento": (date.today() - timedelta(days=800)).isoformat(),
                    "peso_kg": "11.5",
                    "distrito": "Huancayo",
                    "altitud_msnm": "3271",
                    "cuidador": "Rosa Demo",
                    "telefono": "900000001",
                }
                for nombre, valor in datos.items():
                    pagina.locator(f"[name='{nombre}']").fill(valor)
                pagina.locator("[name='sexo']").select_option("F")
                pagina.locator("[name='tipo_nacimiento']").select_option("TERMINO")
                pagina.get_by_role("button", name="Registrar niño").click()
                expect(pagina).to_have_url(url + "/ninos/89000001")
                segundos = time.perf_counter() - inicio
                expect(pagina.locator("body")).to_contain_text("Demo Sintetica")
                pagina.screenshot(path=str(salida / "02_expediente.png"), full_page=True)
                pagina.goto(url + "/ninos/89000001/editar")
                pagina.locator("[name='distrito']").fill("El Tambo")
                pagina.get_by_role("button", name="Guardar cambios").click()
                pagina.reload()
                expect(pagina.locator("body")).to_contain_text("El Tambo")
                pagina.goto(url + "/ninos/89000001/dosajes/nuevo")
                pagina.locator("[name='fecha_dosaje']").fill(date.today().isoformat())
                pagina.locator("[name='hb_observada']").fill("12.0")
                pagina.locator("[name='altitud_msnm']").fill("3271")
                pagina.locator("button[type='submit']").click()
                expect(pagina).to_have_url(url + "/ninos/89000001")
                expect(pagina.locator("body")).to_contain_text("12.0")
                pagina.screenshot(path=str(salida / "03_dosaje.png"), full_page=True)
                pagina.goto(url + "/ninos/nuevo")
                pagina.get_by_role("button", name="Registrar niño").click()
                expect(pagina.get_by_role("alert")).to_contain_text("Revise los datos")
                pagina.screenshot(path=str(salida / "04_validacion.png"), full_page=True)
                hoy = date.today().isoformat()
                pagina.goto(url + f"/reportes/registros?desde={hoy}&hasta={hoy}")
                pagina.screenshot(path=str(salida / "05_reporte.png"), full_page=True)
                pagina.set_viewport_size({"width": 420, "height": 900})
                pagina.goto(url + "/ninos/nuevo")
                pagina.screenshot(path=str(salida / "06_movil.png"), full_page=True)
                with urlopen(url + f"/api/v1/reportes/registros?desde={hoy}&hasta={hoy}") as r:
                    reporte = json.load(r)
                evidencia = {
                    "fecha": hoy,
                    "python": sys.version.split()[0],
                    "navegador": navegador.version,
                    "resultado": "APROBADO",
                    "flujos": [
                        "listado",
                        "alta con CSRF",
                        "consulta",
                        "edición persistida",
                        "dosaje",
                        "rechazo de formulario",
                        "reporte",
                        "vista móvil",
                    ],
                    "segundos_alta_automatizada": round(segundos, 3),
                    "nota": ("Tiempo automatizado, no prueba de usabilidad humana "
                             "ni aceptación clínica"),
                    "reporte": reporte,
                }
                (salida / "navegador.json").write_text(
                    json.dumps(evidencia, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                print(json.dumps(evidencia, ensure_ascii=False))
                navegador.close()
        finally:
            proceso.terminate()
            proceso.wait(timeout=15)


if __name__ == "__main__":
    main()
