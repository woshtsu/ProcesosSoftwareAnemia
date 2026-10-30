"""CP-402 a CP-405: pruebas de extremo a extremo de INC-4 (recordatorios simulados, respuesta del tutor y barreras).

Playwright + servidor real sobre una base SQLite temporal con el conjunto sintético de scripts/cargar_datos_prueba.py.
El notificador es el simulado (sin WHATSAPP_TOKEN): no sale ningún mensaje. La pérdida de conexión se simula con
``context.set_offline(True)``.
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

RAIZ = Path(__file__).resolve().parents[2]


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _levantar(carpeta: Path):
    """Servidor uvicorn real sobre una base SQLite temporal con el conjunto sintético; devuelve (proceso, url)."""
    entorno = {**os.environ, "DATABASE_URL": f"sqlite:///{carpeta / 'inc4.db'}", "AUTH_MODE": "demo"}
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
    proc, url = _levantar(tmp_path_factory.mktemp("e2e_inc4"))
    yield url
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


def pendientes(pg, n):
    expect(pg.get_by_test_id("indicador-sync")).to_have_attribute("data-pendientes", str(n))


def test_cp402_generar_recordatorios_simulados_y_registrar_no_puede_con_barrera_genera_alerta(contexto, url_base):
    pg = abrir_controlada(contexto, url_base)
    pg.get_by_test_id("tab-recordatorios").click()
    pg.get_by_test_id("recordatorios-generar").click()
    resultado = pg.get_by_test_id("recordatorios-resultado")
    expect(resultado).to_contain_text("Modo simulado")
    expect(pg.get_by_test_id("marca-simulado").first).to_be_visible()
    expect(pg.get_by_test_id("kpi-rec-total")).not_to_have_text("0")
    total = len(httpx.get(url_base + "/api/recordatorios").json())
    assert total > 0 and all(r["simulado"] for r in httpx.get(url_base + "/api/recordatorios").json())

    # repetir la generación no duplica mensajes
    pg.get_by_test_id("recordatorios-generar").click()
    expect(resultado).to_contain_text("0 enviado(s)")
    assert len(httpx.get(url_base + "/api/recordatorios").json()) == total

    fila = pg.locator("[data-testid=recordatorio]:has([data-testid=btn-responder])").first
    nino_id = fila.locator(".enlace-nino").get_attribute("data-nino")
    fila.get_by_test_id("btn-responder").click()
    pg.get_by_test_id("respuesta-opcion").select_option("NO_PUEDE")
    pg.get_by_test_id("respuesta-barrera").select_option("RECHAZO_TRATAMIENTO")
    pg.get_by_test_id("respuesta-confirmar").click()
    expect(pg.get_by_test_id("modal-respuesta")).to_be_hidden()
    expect(pg.locator(f"[data-testid=recordatorio]:has(.enlace-nino[data-nino='{nino_id}'])").first).to_contain_text(
        "No puede asistir"
    )
    barreras = httpx.get(f"{url_base}/api/ninos/{nino_id}/barreras").json()
    assert [(b["tipo"], b["fuente"]) for b in barreras] == [("RECHAZO_TRATAMIENTO", "RESPUESTA_RECORDATORIO")]

    pg.get_by_test_id("tab-alertas").click()
    alerta = pg.locator(f"[data-testid=alerta-barrera][data-id='{nino_id}']")
    expect(alerta).to_be_visible()
    expect(alerta.get_by_test_id("prioridad-barrera")).to_have_text("ALTA")
    expect(alerta.get_by_test_id("razones-barrera")).to_contain_text("Rechazo del tratamiento")


def test_cp403_registrar_barrera_sin_conexion_se_sincroniza_al_reconectar(contexto, url_base):
    ninos = httpx.get(url_base + "/api/ninos").json()
    nino_id = ninos[-1]["id"]
    pg = abrir_controlada(contexto, url_base)
    pg.evaluate("id => abrirExpediente(id)", nino_id)
    expect(pg.get_by_test_id("btn-barrera-nino")).to_be_visible()
    expect(pg.get_by_test_id("barreras-nino-vacio")).to_be_visible()

    contexto.set_offline(True)
    pg.get_by_test_id("btn-barrera-nino").click()
    pg.get_by_test_id("barrera-tipo").select_option("TRANSPORTE")
    pg.get_by_test_id("barrera-confirmar").click()
    expect(pg.get_by_test_id("modal-barrera")).to_be_hidden()
    pendientes(pg, 1)
    expect(pg.get_by_test_id("barrera-pendiente")).to_be_visible()

    contexto.set_offline(False)
    pendientes(pg, 0)
    barreras = httpx.get(f"{url_base}/api/ninos/{nino_id}/barreras").json()
    assert [(b["tipo"], b["fuente"]) for b in barreras] == [("TRANSPORTE", "PERSONAL")]


def test_cp404_la_barrera_asociada_a_una_inasistencia_se_registra_con_su_fuente(contexto, url_base):
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
    fila.get_by_test_id("btn-no-asistio").click()
    pg.get_by_test_id("asistencia-motivo").select_option("Distancia o falta de transporte")
    pg.get_by_test_id("asistencia-barrera").select_option("DISTANCIA_CLIMA")
    pg.get_by_test_id("asistencia-confirmar").click()
    expect(pg.get_by_test_id("modal-asistencia")).to_be_hidden()
    expect(pg.get_by_test_id("barrera-fila").first).to_be_visible()
    barreras = httpx.get(f"{url_base}/api/ninos/{nino_id}/barreras").json()
    assert [(b["tipo"], b["fuente"]) for b in barreras] == [("DISTANCIA_CLIMA", "INASISTENCIA")]


def test_cp405_la_barrera_de_una_visita_no_lograda_se_registra_y_suma_al_puntaje(contexto, url_base):
    pg = abrir_controlada(contexto, url_base)
    pg.get_by_test_id("tab-visitas").click()
    primero = pg.get_by_test_id("visita-priorizada").first
    expect(primero).to_be_visible()
    nino_id = primero.get_attribute("data-nino")
    antes = next(
        i for i in httpx.get(url_base + "/api/visitas/priorizadas?limite=100").json() if i["nino"]["id"] == nino_id
    )
    primero.get_by_test_id("btn-visitar").click()
    pg.get_by_test_id("visita-resultado").select_option("RECHAZADA")
    pg.get_by_test_id("visita-barrera").select_option("EFECTOS_ADVERSOS_SUPLEMENTO")
    pg.get_by_test_id("visita-confirmar").click()
    expect(pg.get_by_test_id("modal-visita")).to_be_hidden()
    barreras = httpx.get(f"{url_base}/api/ninos/{nino_id}/barreras").json()
    assert [(b["tipo"], b["fuente"]) for b in barreras] == [("EFECTOS_ADVERSOS_SUPLEMENTO", "VISITA")]
    despues = next(
        i for i in httpx.get(url_base + "/api/visitas/priorizadas?limite=100").json() if i["nino"]["id"] == nino_id
    )
    assert despues["componentes"][-1]["codigo"] == "BARRERA_CRITICA"
    assert despues["componentes"][-1]["puntos"] == 15.0 and len(antes["componentes"]) == 4
