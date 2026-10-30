"""CP-180 a CP-186: pruebas de extremo a extremo de la agenda del personal (RF-08), el registro de asistencia (RF-09) y
el registro del dataset DIRESA Junín sin nombre (ADR-009 y ADR-010). Playwright + servidor real.

Hay dos servidores, cada uno con su base SQLite temporal:
- ``url_base``: el conjunto sintético de scripts/cargar_datos_prueba.py (escenarios definidos respecto de hoy);
- ``url_dataset``: la muestra de tests/fixtures/dataset_muestra.csv importada y servida con FECHA_REFERENCIA=2024-06-30.
"""

import os
import socket
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import httpx
import pytest

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect
pytestmark = pytest.mark.e2e

RAIZ = Path(__file__).resolve().parents[2]
FIXTURE = RAIZ / "tests" / "fixtures" / "dataset_muestra.csv"


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _servidor(entorno):
    """Arranca uvicorn con el entorno dado y devuelve (proceso, url) cuando /api/salud responde."""
    puerto = _puerto_libre()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:crear_app", "--factory", "--port", str(puerto)],
        cwd=RAIZ,
        env={**entorno, "AUTH_MODE": "demo"},
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
    return proc, url


@pytest.fixture(scope="module")
def url_base(tmp_path_factory):
    db = tmp_path_factory.mktemp("e2e_inc2") / "sintetico.db"
    entorno = {**os.environ, "DATABASE_URL": f"sqlite:///{db}"}
    entorno.pop("FECHA_REFERENCIA", None)
    subprocess.run([sys.executable, "-m", "scripts.cargar_datos_prueba"], cwd=RAIZ, env=entorno, check=True)
    proc, url = _servidor(entorno)
    yield url
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="module")
def url_dataset(tmp_path_factory):
    db = tmp_path_factory.mktemp("e2e_dataset") / "dataset.db"
    entorno = {**os.environ, "DATABASE_URL": f"sqlite:///{db}", "FECHA_REFERENCIA": "2024-06-30"}
    subprocess.run(
        [sys.executable, "-m", "scripts.importar_dataset_diresa", "--csv", str(FIXTURE), "--completo", "--reiniciar"],
        cwd=RAIZ,
        env=entorno,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    proc, url = _servidor(entorno)
    yield url
    proc.terminate()
    proc.wait()


def _abrir(url, ancho=1280):
    p = playwright.sync_playwright().start()
    navegador = p.chromium.launch()
    pg = navegador.new_page(viewport={"width": ancho, "height": 900}, locale="es-PE", timezone_id="America/Lima")
    pg.goto(url)
    return p, navegador, pg


@pytest.fixture
def pagina(url_base):
    p, navegador, pg = _abrir(url_base)
    yield pg
    navegador.close()
    p.stop()


@pytest.fixture
def pagina_dataset(url_dataset):
    p, navegador, pg = _abrir(url_dataset)
    yield pg
    navegador.close()
    p.stop()


def hoy_del_servidor(url) -> date:
    return date.fromisoformat(httpx.get(url + "/api/salud").json()["fecha_hoy"])


def consultar_agenda(pg, desde, hasta, comunidad=None):
    pg.get_by_test_id("tab-agenda").click()
    pg.get_by_test_id("agenda-desde").fill(desde.isoformat())
    pg.get_by_test_id("agenda-hasta").fill(hasta.isoformat())
    pg.get_by_test_id("agenda-consultar").click()
    if comunidad:
        pg.get_by_test_id("filtro-agenda-comunidad").select_option(comunidad)
    pg.wait_for_function(
        "([d, h]) => document.querySelector('[data-testid=agenda-personal-resumen]').textContent.includes('fecha de referencia')"
        " && document.querySelector('#agenda-hasta').value === h && document.querySelector('#agenda-desde').value === d",
        arg=[desde.isoformat(), hasta.isoformat()],
    )


def id_de(url, dni) -> str:
    return httpx.get(f"{url}/api/ninos/dni/{dni}").json()["id"]


def prioridad_de_alerta(url, dni, codigo):
    for f in httpx.get(url + "/api/alertas/controles-vencidos").json():
        if f["nino"]["dni"] == dni and f["control"]["codigo"] == codigo:
            return f["prioridad"]
    return None


def test_cp180_rf08_pestana_agenda_semana_de_la_fecha_de_referencia_resumen_y_filtros(pagina, url_base):
    hoy = hoy_del_servidor(url_base)
    pagina.get_by_test_id("tab-agenda").click()
    tabla = pagina.get_by_test_id("agenda-personal-tabla")
    tabla.wait_for()
    lunes = hoy - timedelta(days=hoy.weekday())
    expect(pagina.get_by_test_id("agenda-desde")).to_have_value(lunes.isoformat())
    expect(pagina.get_by_test_id("agenda-hasta")).to_have_value((lunes + timedelta(days=6)).isoformat())
    assert pagina.get_by_test_id("agenda-personal-dia").count() == 7
    semana = httpx.get(url_base + "/api/agenda").json()
    assert semana["resumen"]["total"] >= 1
    assert pagina.get_by_test_id("agenda-personal-total").inner_text() == f"{semana['resumen']['total']} programados"
    # Un rango con vencidos y cumplidos: los totales de la pantalla coinciden con los de la API.
    desde, hasta = hoy - timedelta(days=30), hoy
    consultar_agenda(pagina, desde, hasta)
    api = httpx.get(url_base + "/api/agenda", params={"desde": desde.isoformat(), "hasta": hasta.isoformat()}).json()
    r = api["resumen"]
    assert r["cumplidos"] >= 1
    assert pagina.get_by_test_id("agenda-personal-cumplidos").inner_text() == f"{r['cumplidos']} cumplidos"
    assert pagina.get_by_test_id("agenda-personal-pendientes").inner_text() == f"{r['pendientes']} pendientes"
    assert tabla.locator("tr[data-codigo]").count() == r["total"]
    totales = pagina.get_by_test_id("agenda-personal-dia-total").all_inner_texts()
    assert totales == [
        f"{d['total']} control(es)"
        + (
            f" · {d['cumplidos']} cumplidos · {d['pendientes']} pendientes · {d['vencidos']} vencidos"
            if d["total"]
            else ""
        )
        for d in api["dias"]
    ]
    # Los controles cumplidos se muestran atenuados.
    atenuadas = tabla.locator("tr.atenuado")
    assert atenuadas.count() == r["cumplidos"]
    assert float(atenuadas.first.evaluate("e => getComputedStyle(e.cells[0]).opacity")) < 1
    # Filtro por comunidad.
    comunidad = next(i["nino"]["comunidad"] for d in api["dias"] for i in d["items"])
    pagina.get_by_test_id("filtro-agenda-comunidad").select_option(comunidad)
    pagina.wait_for_function(
        "c => { const f = [...document.querySelectorAll('[data-testid=agenda-personal-tabla] tr[data-codigo]')];"
        " return f.length > 0 && f.every((x) => x.cells[3].textContent.includes(c)); }",
        arg=comunidad,
    )
    filtrada = httpx.get(
        url_base + "/api/agenda",
        params={"desde": desde.isoformat(), "hasta": hasta.isoformat(), "comunidad": comunidad},
    ).json()
    assert tabla.locator("tr[data-codigo]").count() == filtrada["resumen"]["total"] < r["total"]


def test_cp181_rf08_rango_invalido_navegacion_por_semanas_y_fecha_de_hoy(pagina, url_base):
    hoy = hoy_del_servidor(url_base)
    pagina.get_by_test_id("tab-agenda").click()
    pagina.get_by_test_id("agenda-personal-tabla").wait_for()
    pagina.get_by_test_id("agenda-desde").fill((hoy - timedelta(days=40)).isoformat())
    pagina.get_by_test_id("agenda-hasta").fill(hoy.isoformat())
    pagina.get_by_test_id("agenda-consultar").click()
    error = pagina.get_by_test_id("agenda-error")
    expect(error).to_be_visible()
    assert "31 días" in error.inner_text()
    pagina.get_by_test_id("agenda-desde").fill(hoy.isoformat())
    pagina.get_by_test_id("agenda-hasta").fill((hoy - timedelta(days=3)).isoformat())
    pagina.get_by_test_id("agenda-consultar").click()
    expect(error).to_be_visible()
    # Navegación: el rango se corre el mismo número de días.
    lunes = hoy - timedelta(days=hoy.weekday())
    pagina.get_by_test_id("agenda-desde").fill(lunes.isoformat())
    pagina.get_by_test_id("agenda-hasta").fill((lunes + timedelta(days=6)).isoformat())
    pagina.get_by_test_id("agenda-siguiente").click()
    expect(pagina.get_by_test_id("agenda-desde")).to_have_value((lunes + timedelta(days=7)).isoformat())
    expect(error).to_be_hidden()
    pagina.get_by_test_id("agenda-anterior").click()
    pagina.get_by_test_id("agenda-anterior").click()
    expect(pagina.get_by_test_id("agenda-desde")).to_have_value((lunes - timedelta(days=7)).isoformat())
    # Sin fecha de referencia fijada no se muestra el aviso.
    expect(pagina.get_by_test_id("aviso-fecha-referencia")).to_be_hidden()


def test_cp182_rf09_no_asistio_desde_el_expediente_marca_el_control_y_sube_la_prioridad(pagina, url_base):
    # 71000018: DHc1 vencido hace pocos días, prioridad BAJA.
    assert prioridad_de_alerta(url_base, "71000018", "DHc1") == "BAJA"
    pagina.get_by_test_id("tab-expediente").click()
    pagina.get_by_test_id("buscar-dni").fill("71000018")
    pagina.get_by_role("button", name="Abrir").click()
    fila = pagina.locator('[data-testid="agenda-tabla"] tr[data-codigo="DHc1"][data-estado="VENCIDO"]').first
    fila.wait_for()
    assert fila.get_by_test_id("marca-inasistencia").count() == 0
    fila.get_by_test_id("btn-no-asistio").click()
    modal = pagina.get_by_test_id("modal-asistencia")
    expect(modal).to_be_visible()
    # Sin motivo no se registra.
    pagina.get_by_test_id("asistencia-confirmar").click()
    assert "motivo" in pagina.get_by_test_id("asistencia-error").inner_text().lower()
    pagina.get_by_test_id("asistencia-motivo").select_option("Enfermedad del niño")
    pagina.get_by_test_id("asistencia-detalle").fill("Fiebre")
    pagina.get_by_test_id("asistencia-confirmar").click()
    expect(modal).to_be_hidden()
    fila = pagina.locator('[data-testid="agenda-tabla"] tr[data-codigo="DHc1"][data-estado="VENCIDO"]').first
    expect(fila.get_by_test_id("marca-inasistencia")).to_have_text("Inasistencia registrada")
    expect(fila.get_by_test_id("btn-no-asistio")).to_have_count(0)
    assert fila.get_by_test_id("estado-control").get_attribute("data-estado") == "VENCIDO"  # sigue vencido
    assert fila.get_by_test_id("marca-inasistencia").get_attribute("title") == "Enfermedad del niño: Fiebre"
    assert pagina.get_by_test_id("agenda-inasistencias").inner_text() == "1 con inasistencia"
    # La alerta sube un nivel y muestra la marca; un segundo registro del mismo control es 409.
    assert prioridad_de_alerta(url_base, "71000018", "DHc1") == "MEDIA"
    pagina.get_by_test_id("tab-alertas").click()
    pagina.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0")
    celda = pagina.locator("[data-testid=alertas-tabla] tbody tr", has_text="71000018").first
    expect(celda.get_by_test_id("marca-inasistencia")).to_be_visible()
    expect(celda.get_by_test_id("prioridad")).to_have_text("MEDIA")
    nino = id_de(url_base, "71000018")
    duplicado = httpx.post(
        f"{url_base}/api/ninos/{nino}/controles/DHc1/asistencia",
        json={"fecha_programada": fila.get_attribute("data-programada"), "estado": "NO_ASISTIO", "motivo": "Otra vez"},
    )
    assert duplicado.status_code == 409


def test_cp183_rf09_asistio_desde_la_agenda_del_personal_cumple_el_control_y_lo_quita_de_las_alertas(pagina, url_base):
    # 71000019 (Palmayoc): DHc2 vencido con prioridad MEDIA.
    assert prioridad_de_alerta(url_base, "71000019", "DHc2") == "MEDIA"
    hoy = hoy_del_servidor(url_base)
    consultar_agenda(pagina, hoy - timedelta(days=60), hoy - timedelta(days=30), comunidad="Palmayoc")
    fila = pagina.locator('[data-testid="agenda-personal-tabla"] tr[data-codigo="DHc2"][data-estado="VENCIDO"]').first
    fila.wait_for()
    assert "71000019" in fila.inner_text()
    fila.get_by_test_id("btn-asistio").click()
    expect(pagina.get_by_test_id("modal-asistencia")).to_be_visible()
    pagina.get_by_test_id("asistencia-confirmar").click()
    expect(pagina.get_by_test_id("modal-asistencia")).to_be_hidden()
    cumplida = pagina.locator(
        '[data-testid="agenda-personal-tabla"] tr[data-codigo="DHc2"][data-estado="CUMPLIDO"]'
    ).first
    cumplida.wait_for()
    assert "(asistió)" in cumplida.inner_text()
    assert "atenuado" in cumplida.get_attribute("class")
    expect(cumplida.get_by_test_id("btn-asistio")).to_have_count(0)
    assert prioridad_de_alerta(url_base, "71000019", "DHc2") is None  # ya no genera alerta
    asistencias = httpx.get(f"{url_base}/api/ninos/{id_de(url_base, '71000019')}/asistencias").json()
    assert [(a["codigo_control"], a["estado"]) for a in asistencias] == [("DHc2", "ASISTIO")]


def test_cp184_rf08_vista_movil_de_la_agenda_sin_desborde_horizontal(url_base):
    p, navegador, pg = _abrir(url_base, ancho=375)
    try:
        hoy = hoy_del_servidor(url_base)
        consultar_agenda(pg, hoy - timedelta(days=30), hoy)
        assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        pg.locator("[data-testid=agenda-personal-tabla] tr[data-codigo]").first.get_by_test_id(
            "agenda-personal-nino"
        ).click()
        pg.get_by_test_id("agenda-tabla").wait_for()
        assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    finally:
        navegador.close()
        p.stop()


def test_cp185_dataset_aviso_de_fecha_de_referencia_y_registro_sin_nombre(pagina_dataset, url_dataset):
    pg = pagina_dataset
    aviso = pg.get_by_test_id("aviso-fecha-referencia")
    expect(aviso).to_be_visible()
    assert aviso.inner_text().strip() == "Fecha de referencia: 30/06/2024 (corte del dataset)"
    assert httpx.get(url_dataset + "/api/salud").json()["fecha_referencia"] == "2024-06-30"
    expect(pg.locator("#fecha")).to_have_value("2024-06-30")  # la fecha por defecto sale del servidor, no del navegador
    pg.get_by_test_id("tab-seguimiento").click()
    pg.get_by_test_id("buscar").fill("DJ-00002")  # la búsqueda encuentra por código
    pg.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length === 1")
    fila = pg.locator("#cuerpo-seguimiento tr").first
    assert "Registro DJ-00002 (dataset anonimizado)" in fila.inner_text()
    fila.click()
    pg.get_by_test_id("tabla-evaluaciones").wait_for()
    expect(pg.get_by_test_id("expediente-nombre")).to_have_text("Registro DJ-00002 (dataset anonimizado)")
    expect(pg.get_by_test_id("expediente-codigo")).to_have_text("DJ-00002")
    assert "Dataset DIRESA Junín" in pg.get_by_test_id("expediente-origen").inner_text()
    expect(pg.get_by_test_id("sin-antropometria")).to_have_count(1)  # el dataset no trae peso ni talla
    assert pg.get_by_test_id("clasificacion-his").inner_text().startswith("HIS: ")
    assert (
        "undefined" not in pg.get_by_test_id("expediente").inner_text()
        and "null" not in pg.get_by_test_id("expediente").inner_text()
    )
    # También se abre por código desde la pestaña Expediente.
    pg.get_by_test_id("tab-expediente").click()
    pg.get_by_test_id("buscar-dni").fill("dj-00003")
    pg.get_by_role("button", name="Abrir").click()
    expect(pg.get_by_test_id("expediente-codigo")).to_have_text("DJ-00003")


def test_cp186_dataset_agenda_y_alertas_usan_la_fecha_de_referencia(pagina_dataset, url_dataset):
    pg = pagina_dataset
    pg.get_by_test_id("tab-agenda").click()
    pg.get_by_test_id("agenda-personal-tabla").wait_for()
    expect(pg.get_by_test_id("agenda-desde")).to_have_value("2024-06-24")
    expect(pg.get_by_test_id("agenda-hasta")).to_have_value("2024-06-30")
    consultar_agenda(pg, date(2024, 6, 1), date(2024, 6, 30))
    assert "fecha de referencia 30/06/2024" in pg.get_by_test_id("agenda-personal-resumen").inner_text()
    api = httpx.get(url_dataset + "/api/agenda", params={"desde": "2024-06-01", "hasta": "2024-06-30"}).json()
    assert api["resumen"]["total"] >= 1
    assert pg.locator("tr[data-codigo]").count() == api["resumen"]["total"]
    nombres = pg.get_by_test_id("agenda-personal-nino").all_inner_texts()
    assert nombres and all(n.startswith("Registro DJ-") for n in nombres)  # nadie sin nombre legible
    pg.get_by_test_id("tab-alertas").click()
    pg.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0")
    assert "Registro DJ-" in pg.get_by_test_id("alertas-tabla").inner_text()
