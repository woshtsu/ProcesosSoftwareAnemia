"""CP-297 a CP-302: pruebas de extremo a extremo de INC-3 (registro sin conexión, sincronización, visitas priorizadas).

Playwright + servidor real sobre una base SQLite temporal con el conjunto sintético de scripts/cargar_datos_prueba.py.
La pérdida de conexión se simula con ``context.set_offline(True)``: el navegador no alcanza al servidor y la aplicación
debe guardar en el dispositivo (IndexedDB), mostrar el indicador de pendientes y sincronizar al reconectar.
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


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _levantar(carpeta: Path):
    """Servidor uvicorn real sobre una base SQLite temporal con el conjunto sintético; devuelve (proceso, url)."""
    entorno = {**os.environ, "DATABASE_URL": f"sqlite:///{carpeta / 'inc3.db'}", "AUTH_MODE": "demo"}
    entorno.pop("FECHA_REFERENCIA", None)
    subprocess.run(
        [sys.executable, "-m", "scripts.cargar_datos_prueba"],
        cwd=RAIZ,
        env=entorno,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    puerto = _puerto_libre()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:crear_app", "--factory", "--port", str(puerto)],
        cwd=RAIZ,
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
    return proc, url


@pytest.fixture(scope="module")
def url_base(tmp_path_factory):
    proc, url = _levantar(tmp_path_factory.mktemp("e2e_inc3"))
    yield url
    proc.terminate()
    proc.wait()


@pytest.fixture
def servidor_propio(tmp_path):
    """Servidor que la prueba puede apagar para simular una posta sin ninguna conexión."""
    proc, url = _levantar(tmp_path)
    yield proc, url
    if proc.poll() is None:
        proc.terminate()
    proc.wait()


@pytest.fixture
def contexto(url_base):
    with playwright.sync_playwright() as p:
        navegador = p.chromium.launch()
        ctx = navegador.new_context(viewport={"width": 1280, "height": 900}, locale="es-PE", timezone_id="America/Lima")
        yield ctx
        ctx.close()
        navegador.close()


def abrir_controlada(ctx, url):
    """Abre la aplicación y espera a que el service worker la controle (así sus lecturas quedan en caché)."""
    pg = ctx.new_page()
    pg.goto(url)
    pg.evaluate("navigator.serviceWorker.ready.then(() => true)")
    pg.reload()
    pg.wait_for_function("navigator.serviceWorker.controller !== null")
    expect(pg.get_by_test_id("tab-registro")).to_be_visible()
    return pg


def llenar_registro(pg, dni, nombres="Mía Alejandra", apellidos="Huamán Zevallos", fecha_control=None):
    if fecha_control:
        pg.fill("#fecha", fecha_control)
    pg.fill("#dni", dni)
    pg.fill("#nombres", nombres)
    pg.fill("#apellidos", apellidos)
    pg.select_option("#sexo", "F")
    pg.fill("#fecha_nacimiento", "2025-09-10")
    pg.fill("#comunidad", "Palmayoc")
    pg.fill("#altitud_m", "3720")
    pg.fill("#tutor_nombre", "Elena Zevallos Rojas")
    pg.fill("#hemoglobina_observada", "9.4")
    pg.fill("#peso_kg", "8.4")
    pg.fill("#talla_cm", "71")


def pendientes(pg, n):
    expect(pg.get_by_test_id("indicador-sync")).to_have_attribute("data-pendientes", str(n))


def test_cp297_registrar_nino_y_control_sin_conexion_sincroniza_al_reconectar(contexto, url_base):
    pg = abrir_controlada(contexto, url_base)
    pendientes(pg, 0)
    expect(pg.get_by_test_id("indicador-sync")).to_have_text("Al día")

    contexto.set_offline(True)
    llenar_registro(pg, "72300001", fecha_control=(date.today() - timedelta(days=20)).isoformat())
    pg.get_by_test_id("guardar").click()
    expect(pg.get_by_test_id("expediente-pendiente")).to_be_visible()
    pendientes(pg, 1)
    pg.locator("#form-control input[name=hemoglobina_observada]").fill("10.1")
    pg.locator("#form-control input[name=peso_kg]").fill("8.6")
    pg.locator("#form-control input[name=talla_cm]").fill("72")
    pg.get_by_test_id("guardar-control").click()
    pendientes(pg, 2)
    expect(pg.get_by_test_id("indicador-sync")).to_have_text("2 pendientes")
    assert pg.get_by_test_id("evaluacion-pendiente").count() == 2

    # El niño pendiente aparece en Seguimiento, marcado, y el panel lista las dos operaciones.
    pg.get_by_test_id("tab-seguimiento").click()
    expect(pg.get_by_test_id("fila-pendiente")).to_have_count(1)
    pg.get_by_test_id("tab-sincronizacion").click()
    expect(pg.get_by_test_id("pendiente")).to_have_count(2)
    assert httpx.get(f"{url_base}/api/ninos/dni/72300001").status_code == 404

    contexto.set_offline(False)
    pendientes(pg, 0)
    expect(pg.get_by_test_id("indicador-sync")).to_have_text("Al día")
    expect(pg.get_by_test_id("sync-vacio")).to_be_visible()
    cuerpo = httpx.get(f"{url_base}/api/ninos/dni/72300001").json()
    assert len(cuerpo["evaluaciones"]) == 2

    pg.get_by_test_id("tab-seguimiento").click()
    pg.get_by_test_id("buscar").fill("72300001")
    expect(pg.locator("#cuerpo-seguimiento tr")).to_have_count(1)
    expect(pg.get_by_test_id("fila-pendiente")).to_have_count(0)
    assert len(httpx.get(f"{url_base}/api/ninos", params={"q": "72300001"}).json()) == 1


def test_cp298_recargar_sin_conexion_abre_desde_cache(contexto, servidor_propio):
    proceso, url = servidor_propio
    pg = abrir_controlada(contexto, url)
    pg.get_by_test_id("tab-seguimiento").click()
    expect(pg.locator("#cuerpo-seguimiento tr").first).to_be_visible()

    # Sin conexión de verdad: el navegador queda desconectado y el servidor deja de responder.
    proceso.terminate()
    proceso.wait()
    contexto.set_offline(True)
    pg.reload()
    expect(pg.get_by_test_id("tab-registro")).to_be_visible()
    expect(pg.locator("#red.fuera")).to_have_count(1)
    pg.get_by_test_id("tab-seguimiento").click()
    expect(pg.locator("#cuerpo-seguimiento tr").first).to_be_visible()
    expect(pg.get_by_test_id("aviso-cache")).to_be_visible()


def test_cp299_registro_sin_conexion_con_datos_incompletos_no_se_guarda(contexto, url_base):
    pg = abrir_controlada(contexto, url_base)
    contexto.set_offline(True)
    pg.fill("#nombres", "Solo Nombre")
    pg.get_by_test_id("guardar").click()
    expect(pg.locator(".campo.invalido").first).to_be_visible()
    pendientes(pg, 0)


def test_cp300_asistencia_sin_conexion_queda_pendiente_y_se_sincroniza(contexto, url_base):
    vencida = next(
        f
        for f in httpx.get(url_base + "/api/alertas/controles-vencidos").json()
        if not f["control"]["inasistencia_registrada"]
    )
    nino_id, codigo = vencida["nino"]["id"], vencida["control"]["codigo"]
    pg = abrir_controlada(contexto, url_base)
    pg.evaluate("id => abrirExpediente(id)", nino_id)
    fila = pg.locator(
        f"[data-testid=agenda-tabla] tr[data-codigo='{codigo}'][data-programada='{vencida['control']['fecha_programada']}']"
    )
    expect(fila).to_be_visible()

    contexto.set_offline(True)
    fila.get_by_test_id("btn-no-asistio").click()
    pg.get_by_test_id("asistencia-motivo").select_option("Olvido de la cita")
    pg.get_by_test_id("asistencia-confirmar").click()
    pendientes(pg, 1)
    expect(fila.get_by_test_id("asistencia-pendiente")).to_be_visible()

    contexto.set_offline(False)
    pendientes(pg, 0)
    agenda = httpx.get(f"{url_base}/api/ninos/{nino_id}/agenda").json()
    control = next(
        c
        for c in agenda["controles"]
        if c["codigo"] == codigo and c["fecha_programada"] == vencida["control"]["fecha_programada"]
    )
    assert control["inasistencia_registrada"] is True


def test_cp301_visita_priorizada_en_linea_con_desglose_del_puntaje(contexto, url_base):
    pg = abrir_controlada(contexto, url_base)
    pg.get_by_test_id("tab-visitas").click()
    filas = pg.get_by_test_id("visita-priorizada")
    expect(filas.first).to_be_visible()
    primero = filas.first
    nino_id = primero.get_attribute("data-nino")
    assert primero.locator("td").first.inner_text() == "1"
    primero.get_by_test_id("puntaje").click()
    expect(pg.get_by_test_id("desglose").first).to_be_visible()
    primero.get_by_test_id("btn-visitar").click()
    pg.get_by_test_id("visita-resultado").select_option("REALIZADA")
    pg.get_by_test_id("visita-suplemento").select_option("SI")
    pg.get_by_test_id("visita-observaciones").fill("Familia receptiva")
    pg.get_by_test_id("visita-confirmar").click()
    expect(pg.get_by_test_id("modal-visita")).to_be_hidden()
    visitas = httpx.get(f"{url_base}/api/ninos/{nino_id}/visitas").json()
    assert [(v["resultado"], v["consume_suplemento"]) for v in visitas] == [("REALIZADA", "SI")]
    # La visita registrada hace bajar al niño en la lista (ya no es el más atrasado en visitas).
    pg.get_by_test_id("visitas-consultar").click()
    expect(pg.get_by_test_id("visita-priorizada").first).not_to_have_attribute("data-nino", nino_id)


def test_cp302_visita_sin_conexion_desde_la_lista_se_sincroniza(contexto, url_base):
    pg = abrir_controlada(contexto, url_base)
    pg.get_by_test_id("tab-visitas").click()
    filas = pg.get_by_test_id("visita-priorizada")
    expect(filas.first).to_be_visible()
    nino_id = filas.first.get_attribute("data-nino")

    contexto.set_offline(True)
    filas.first.get_by_test_id("btn-visitar").click()
    pg.get_by_test_id("visita-resultado").select_option("NO_ENCONTRADO")
    pg.get_by_test_id("visita-confirmar").click()
    pendientes(pg, 1)
    expect(pg.get_by_test_id("visita-pendiente-fila")).to_be_visible()

    contexto.set_offline(False)
    pendientes(pg, 0)
    visitas = httpx.get(f"{url_base}/api/ninos/{nino_id}/visitas").json()
    assert [v["resultado"] for v in visitas] == ["NO_ENCONTRADO"]


def test_cp303_conflicto_de_evaluacion_se_resuelve_desde_el_panel(contexto, url_base):
    hoy = httpx.get(url_base + "/api/salud").json()[
        "fecha_hoy"
    ]  # «hoy» del servidor (Perú), no del equipo que ejecuta la prueba
    hoy = date.today().isoformat()
    cuerpo = {
        "nino": {
            "dni": "72300003",
            "nombres": "Ana Lucía",
            "apellidos": "Ccora Ñaupa",
            "sexo": "F",
            "fecha_nacimiento": "2025-09-10",
            "establecimiento": "P. S. Chongos Alto",
            "distrito": "Chongos Alto",
            "comunidad": "Palmayoc",
            "altitud_m": 3720,
            "tutor_nombre": "Rosa Ñaupa",
            "tutor_celular": None,
        },
        "evaluacion_inicial": {"fecha": hoy, "hemoglobina_observada": 9.8, "peso_kg": 8.4, "talla_cm": 71},
    }
    r = httpx.post(url_base + "/api/ninos", json=cuerpo, headers={"X-Usuario": "enf.rosa.quispe"})
    assert r.status_code == 201
    nino_id = r.json()["id"]
    pg = abrir_controlada(contexto, url_base)
    pg.evaluate("id => abrirExpediente(id)", nino_id)
    pg.locator("#form-control input[name=hemoglobina_observada]").wait_for()

    contexto.set_offline(True)
    pg.locator("#form-control input[name=hemoglobina_observada]").fill("11.2")
    pg.locator("#form-control input[name=peso_kg]").fill("8.4")
    pg.locator("#form-control input[name=talla_cm]").fill("71")
    pg.get_by_test_id("guardar-control").click()
    pendientes(pg, 1)

    contexto.set_offline(False)
    pendientes(pg, 0)
    pg.get_by_test_id("tab-sincronizacion").click()
    conflicto = pg.get_by_test_id("conflicto")
    expect(conflicto).to_have_count(1)
    expect(pg.get_by_test_id("indicador-sync")).to_contain_text("1 conflicto")
    conflicto.get_by_test_id("conflicto-conservar").click()
    expect(pg.get_by_test_id("sin-conflictos")).to_be_visible()
    expect(pg.get_by_test_id("indicador-sync")).to_have_text("Al día")
    assert len(httpx.get(f"{url_base}/api/ninos/{nino_id}").json()["evaluaciones"]) == 1
