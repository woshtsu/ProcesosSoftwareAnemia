"""CP-33 a CP-36: pruebas de extremo a extremo de la interfaz (Playwright + servidor real)."""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

playwright = pytest.importorskip("playwright.sync_api")
pytestmark = pytest.mark.e2e


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def url_base(tmp_path_factory):
    puerto = _puerto_libre()
    db = tmp_path_factory.mktemp("e2e") / "e2e.db"
    entorno = {**os.environ, "DATABASE_URL": f"sqlite:///{db}"}
    raiz = Path(__file__).resolve().parents[2]
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:crear_app", "--factory", "--port", str(puerto)],
        cwd=raiz,
        env=entorno,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{puerto}"
    for _ in range(50):
        try:
            if httpx.get(url + "/api/salud").status_code == 200:
                break
        except httpx.HTTPError:
            time.sleep(0.2)
    yield url
    proc.terminate()
    proc.wait()


@pytest.fixture
def pagina(url_base):
    with playwright.sync_playwright() as p:
        navegador = p.chromium.launch()
        pg = navegador.new_page(viewport={"width": 1280, "height": 900}, locale="es-PE")
        pg.goto(url_base)
        yield pg
        navegador.close()


def llenar_registro(pg, dni, hb="11.6"):
    pg.fill("#dni", dni)
    pg.fill("#nombres", "Rosa Elvira")
    pg.fill("#apellidos", "Ccente Poma")
    pg.select_option("#sexo", "F")
    pg.fill("#fecha_nacimiento", "2025-09-10")
    pg.fill("#comunidad", "Palmayoc")
    pg.fill("#altitud_m", "3720")
    pg.fill("#tutor_nombre", "Elena Poma Rojas")
    pg.fill("#hemoglobina_observada", hb)
    pg.fill("#peso_kg", "8.4")
    pg.fill("#talla_cm", "71")


def test_hu01_hu03_registro_con_vista_previa_y_expediente(pagina):
    llenar_registro(pagina, "72000001")
    previa = pagina.get_by_test_id("clasificacion-previa")
    previa.wait_for()
    assert "Anemia moderada" in previa.inner_text()
    assert pagina.get_by_test_id("borrador").is_visible()
    pagina.get_by_test_id("guardar").click()
    pagina.get_by_test_id("tabla-evaluaciones").wait_for()
    assert "Rosa Elvira Ccente Poma" in pagina.get_by_test_id("expediente").inner_text()


def test_hu03_datos_invalidos_muestran_mensaje_comprensible(pagina):
    llenar_registro(pagina, "123", hb="25")
    pagina.get_by_test_id("guardar").click()
    pagina.wait_for_selector(".campo.invalido")
    texto = pagina.inner_text("#form-registro")
    assert "exactamente 8 dígitos" in texto and "rango clínico válido" in texto


def test_hu04_seguimiento_y_busqueda(pagina):
    pagina.get_by_test_id("tab-seguimiento").click()
    pagina.get_by_test_id("buscar").fill("72000001")
    pagina.wait_for_timeout(600)
    filas = pagina.locator("#cuerpo-seguimiento tr")
    assert filas.count() == 1 and "Palmayoc" in filas.first.inner_text()
    filas.first.click()
    pagina.get_by_test_id("tabla-evaluaciones").wait_for()


def test_hu05_reporte_del_periodo(pagina):
    pagina.get_by_test_id("tab-reporte").click()
    pagina.get_by_test_id("generar-reporte").click()
    pagina.get_by_test_id("kpi-registrados").wait_for()
    assert int(pagina.get_by_test_id("kpi-registrados").inner_text()) >= 1
