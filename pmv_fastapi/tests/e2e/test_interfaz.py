"""CP-33 a CP-36 y CP-109 a CP-112: pruebas de extremo a extremo de la interfaz (Playwright + servidor real).

El servidor arranca sobre una base SQLite temporal con el conjunto sintético de scripts/cargar_datos_prueba.py, cuyos
escenarios de agenda (cumplidos, pendientes, próximos y vencidos) están definidos respecto de la fecha de hoy.
"""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect
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
    subprocess.run([sys.executable, "-m", "scripts.cargar_datos_prueba"], cwd=raiz, env=entorno, check=True)
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
        pg = navegador.new_page(viewport={"width": 1280, "height": 900}, locale="es-PE", timezone_id="America/Lima")
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


# --- Incremento 2 (avance): agenda en el expediente y pestaña de alertas ------------------------------------------------


def esperar_filas_de_prioridad(pg, prioridad, cantidad):
    """Espera a que la tabla de alertas muestre exactamente ``cantidad`` filas y todas de la prioridad dada."""
    pg.wait_for_function(
        "([p, n]) => { const f = [...document.querySelectorAll('[data-testid=alertas-tabla] tbody tr')];"
        " return f.length === n && f.every((x) => x.dataset.prioridad === p); }",
        arg=[prioridad, cantidad],
    )


def abrir_expediente_por_dni(pg, dni):
    pg.get_by_test_id("tab-seguimiento").click()
    pg.get_by_test_id("buscar").fill(dni)
    pg.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length === 1")
    pg.locator("#cuerpo-seguimiento tr").first.click()
    pg.get_by_test_id("tabla-evaluaciones").wait_for()


def test_cp109_hist21_agenda_de_controles_en_el_expediente(pagina):
    # 71000022: dos evaluaciones con anemia leve; C1M cumplido, C3M y DHx vencidos, C6M pendiente.
    abrir_expediente_por_dni(pagina, "71000022")
    tabla = pagina.get_by_test_id("agenda-tabla")
    tabla.wait_for()
    resumen = pagina.get_by_test_id("agenda-resumen")
    assert pagina.get_by_test_id("agenda-vencidos").inner_text() == "2 vencidos"
    assert "2 cumplidos" in resumen.inner_text() and "Próximo control" in resumen.inner_text()
    filas = tabla.locator("tbody tr")
    assert filas.count() == 13
    estado = lambda codigo: tabla.locator(f'tr[data-codigo="{codigo}"]').first.get_attribute("data-estado")  # noqa: E731
    assert estado("C1M") == "CUMPLIDO" and estado("C3M") == "VENCIDO" and estado("C6M") == "PENDIENTE"
    chip = tabla.locator('tr[data-codigo="C3M"] [data-testid="estado-control"]')
    assert chip.inner_text().startswith("Vencido · ")
    assert "Agenda referencial" in pagina.get_by_test_id("agenda-seccion").inner_text()


def test_cp110_hist21_agenda_casos_especiales(pagina):
    abrir_expediente_por_dni(pagina, "71000023")  # recuperada: controles cerrados por recuperación
    # expect() reintenta hasta que la agenda del NUEVO expediente reemplaza a la anterior (evita la carrera con la tabla previa)
    expect(pagina.locator('[data-testid="agenda-tabla"] tr[data-estado="CERRADO_RECUPERADO"]')).to_have_count(2)
    abrir_expediente_por_dni(pagina, "71000017")  # un control por vencer en 3 días
    expect(pagina.locator('[data-testid="agenda-tabla"] tr[data-estado="PROXIMO"]')).to_have_count(1)
    assert pagina.get_by_test_id("agenda-proximos").inner_text() == "1 por vencer"
    # Con alta: sin agenda (el listado de seguimiento solo muestra activos hasta cambiar el filtro).
    pagina.get_by_test_id("tab-seguimiento").click()
    pagina.select_option("#filtro-estado", "ALTA")
    pagina.get_by_test_id("buscar").fill("71000024")
    pagina.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length === 1")
    pagina.locator("#cuerpo-seguimiento tr").first.click()
    pagina.get_by_test_id("agenda-sin-agenda").wait_for()
    assert "alta" in pagina.get_by_test_id("agenda-sin-agenda").inner_text()
    assert pagina.get_by_test_id("agenda-tabla").count() == 0


def test_cp111_hist22_pestana_de_alertas_resumen_filtros_y_navegacion(pagina, url_base):
    resumen = httpx.get(url_base + "/api/alertas/resumen").json()
    assert resumen["total_vencidos"] >= 8
    # La insignia de la cabecera muestra el total de controles vencidos.
    pagina.wait_for_function(
        f"document.querySelector('[data-testid=insignia-alertas]').textContent === '{resumen['total_vencidos']}'"
    )
    pagina.get_by_test_id("tab-alertas").click()
    tabla = pagina.get_by_test_id("alertas-tabla")
    pagina.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0")
    assert tabla.locator("tbody tr").count() == resumen["total_vencidos"]
    assert pagina.get_by_test_id("kpi-vencidos").inner_text() == str(resumen["total_vencidos"])
    assert pagina.get_by_test_id("kpi-ninos-vencidos").inner_text() == str(resumen["ninos_con_vencidos"])
    assert pagina.get_by_test_id("kpi-alta").inner_text() == str(resumen["por_prioridad"]["ALTA"])
    assert pagina.get_by_test_id("kpi-proximos").inner_text() == str(resumen["proximos_7_dias"])
    prioridades = [f.get_attribute("data-prioridad") for f in tabla.locator("tbody tr").all()]
    orden = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
    assert prioridades == sorted(prioridades, key=orden.get)  # primero las prioridades altas
    # Filtro por prioridad.
    pagina.get_by_test_id("filtro-alerta-prioridad").select_option("MEDIA")
    esperar_filas_de_prioridad(pagina, "MEDIA", resumen["por_prioridad"]["MEDIA"])
    assert {f.get_attribute("data-prioridad") for f in tabla.locator("tbody tr").all()} == {"MEDIA"}
    # Filtro por comunidad (combinado).
    pagina.get_by_test_id("filtro-alerta-prioridad").select_option("")
    pagina.get_by_test_id("filtro-alerta-comunidad").select_option("Huaycha")
    pagina.wait_for_function(
        "[...document.querySelectorAll('[data-testid=alertas-tabla] tbody tr')].every(f => f.cells[5].textContent === 'Huaycha')"
        " && document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0"
    )
    pagina.get_by_test_id("filtro-alerta-comunidad").select_option("")
    pagina.get_by_test_id("filtro-alerta-prioridad").select_option("BAJA")
    esperar_filas_de_prioridad(pagina, "BAJA", resumen["por_prioridad"]["BAJA"])
    # Clic en un niño: abre su expediente con la agenda.
    fila = tabla.locator("tbody tr").first
    nombre = fila.locator("strong").inner_text()
    fila.click()
    pagina.get_by_test_id("agenda-tabla").wait_for()
    assert nombre in pagina.get_by_test_id("expediente").inner_text()


def test_cp112_hist22_vista_movil_sin_desborde_horizontal(url_base):
    with playwright.sync_playwright() as p:
        navegador = p.chromium.launch()
        pg = navegador.new_page(viewport={"width": 375, "height": 800}, locale="es-PE", timezone_id="America/Lima")
        pg.goto(url_base)
        pg.get_by_test_id("tab-alertas").click()
        pg.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0")
        assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        pg.locator("[data-testid=alertas-tabla] tbody tr").first.click()
        pg.get_by_test_id("agenda-tabla").wait_for()
        assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        navegador.close()
