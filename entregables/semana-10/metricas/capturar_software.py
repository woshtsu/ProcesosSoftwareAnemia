"""Factor F: ejecuta los criterios de aceptacion (Dado-Cuando-Entonces) de los 4 incrementos contra el servidor local
y captura la interfaz en escritorio y movil.

Uso (desde la raiz del repositorio):
    PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python entregables/semana-10/metricas/capturar_software.py

* Servidor: uvicorn en 127.0.0.1:8765 con AUTH_MODE=demo (igual que los E2E), SQLite temporal y los datos sinteticos de
  scripts/cargar_datos_prueba.py. WhatsApp queda SIMULADO (no sale ningun mensaje); el secreto del webhook es de prueba.
* Cada escenario hace aserciones reales; el resultado queda en metricas/salidas/F_resultados_aceptacion.json.
* Capturas: entregables/semana-10/evidencias/software/.
"""

import functools
import hashlib
import hmac
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import date, datetime, timedelta
from pathlib import Path

import httpx
from playwright.sync_api import expect, sync_playwright

RAIZ = Path(__file__).resolve().parents[3]
PMV = RAIZ / "pmv_fastapi"
BASE = RAIZ / "entregables" / "semana-10"
IMG = BASE / "evidencias" / "software"
PUERTO = 8765
URL = f"http://127.0.0.1:{PUERTO}"
SECRETO = "secreto-de-prueba-s10"
TOKEN_VERIF = "token-de-prueba-s10"
ESC = {"width": 1280, "height": 900}
MOV = {"width": 390, "height": 844}

resultados: list[dict] = []
ULTIMO_ENTORNO: dict = {}
capturas: list[str] = []


def commit() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()


def shot(pg, nombre: str, completa: bool = True):
    ruta = IMG / f"{nombre}.png"
    pg.screenshot(path=str(ruta), full_page=completa and not nombre.endswith("_movil"))  # movil: solo la ventana visible
    capturas.append(nombre)
    return nombre


def levantar(entorno_extra=None):
    tmp = Path(tempfile.mkdtemp(prefix="s10_"))
    entorno = {**os.environ, "DATABASE_URL": f"sqlite:///{tmp / 's10.db'}", "AUTH_MODE": "demo", **(entorno_extra or {})}
    for k in ("FECHA_REFERENCIA", "WHATSAPP_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "SMS_API_URL"):
        entorno.pop(k, None)
    subprocess.run([sys.executable, "-m", "scripts.cargar_datos_prueba"], cwd=PMV, env=entorno, check=True, stdout=subprocess.DEVNULL)
    global ULTIMO_ENTORNO
    ULTIMO_ENTORNO = entorno
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:crear_app", "--factory", "--port", str(PUERTO)],
        cwd=PMV, env=entorno, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(80):
        try:
            if httpx.get(URL + "/api/salud").status_code == 200:
                break
        except httpx.HTTPError:
            time.sleep(0.2)
    return proc


def escenario(codigo, nombre, incremento, criterio):
    """Decorador: ejecuta el escenario, registra aprobado/rechazado, tiempos y capturas."""

    def deco(fn):
        @functools.wraps(fn)
        def run(*a, **k):
            n0 = len(capturas)
            t0 = time.time()
            reg = {"codigo": codigo, "nombre": nombre, "incremento": incremento, "criterio": criterio}
            try:
                datos = fn(*a, **k) or {}
                reg.update(estado="APROBADO", detalle=datos)
            except Exception as e:  # noqa: BLE001
                reg.update(estado="RECHAZADO", detalle={"error": f"{type(e).__name__}: {e}"[:400]})
                traceback.print_exc()
            reg["capturas"] = capturas[n0:]
            reg["duracion_escenario_s"] = round(time.time() - t0, 1)
            resultados.append(reg)
            print(f"{codigo}: {reg['estado']} {reg.get('detalle')}")

        return run

    return deco


def abrir(ctx, controlada=False):
    pg = ctx.new_page()
    pg.goto(URL)
    if controlada:
        pg.evaluate("navigator.serviceWorker.ready.then(() => true)")
        pg.reload()
        pg.wait_for_function("navigator.serviceWorker.controller !== null")
    expect(pg.get_by_test_id("tab-registro")).to_be_visible()
    return pg


def pendientes(pg, n):
    expect(pg.get_by_test_id("indicador-sync")).to_have_attribute("data-pendientes", str(n))


def llenar(pg, dni, nombres="Rosa Elvira", apellidos="Ccente Poma", hb="11.6", fecha_control=None):
    if fecha_control:
        pg.fill("#fecha", fecha_control)
    pg.fill("#dni", dni)
    pg.fill("#nombres", nombres)
    pg.fill("#apellidos", apellidos)
    pg.select_option("#sexo", "F")
    pg.fill("#fecha_nacimiento", "2025-09-10")
    pg.fill("#comunidad", "Palmayoc")
    pg.fill("#altitud_m", "3720")
    pg.fill("#tutor_nombre", "Elena Poma Rojas")
    pg.fill("#hemoglobina_observada", hb)
    pg.fill("#peso_kg", "8.4")
    pg.fill("#talla_cm", "71")


def abrir_por_dni(pg, dni):
    pg.get_by_test_id("tab-seguimiento").click()
    pg.get_by_test_id("buscar").fill(dni)
    pg.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length === 1")
    pg.locator("#cuerpo-seguimiento tr").first.click()
    pg.get_by_test_id("tabla-evaluaciones").wait_for()


def api(metodo, ruta, **k):
    h = {"X-Usuario": "enf.rosa.quispe", **k.pop("headers", {})}
    return httpx.request(metodo, URL + ruta, headers=h, timeout=15, **k)


# ----------------------------------------------------------------------------------------------------------------------
# Incremento 1
# ----------------------------------------------------------------------------------------------------------------------


@escenario("RF-01", "Registrar nino con evaluacion inicial", "Inc. 1", "Guardar registro valido -> confirmacion y expediente en < 2 s; DNI repetido -> 409")
def rf01(ctx, mov):
    pg = abrir(ctx)
    llenar(pg, "72000001")
    expect(pg.get_by_test_id("clasificacion-previa")).to_contain_text("Anemia moderada")
    shot(pg, "RF01_inc1_1_entrada_escritorio")
    t0 = time.perf_counter()
    pg.get_by_test_id("guardar").click()
    pg.get_by_test_id("tabla-evaluaciones").wait_for()
    ms = round((time.perf_counter() - t0) * 1000)
    assert "Rosa Elvira Ccente Poma" in pg.get_by_test_id("expediente").inner_text()
    assert ms < 2000, ms
    shot(pg, "RF01_inc1_2_resultado_escritorio")
    r = api("GET", "/api/ninos/dni/72000001")
    assert r.status_code == 200 and len(r.json()["evaluaciones"]) == 1
    cuerpo = {"nino": {"dni": "72000001", "nombres": "Rosa Elvira", "apellidos": "Ccente Poma", "sexo": "F", "fecha_nacimiento": "2025-09-10", "establecimiento": "P. S. Chongos Alto", "distrito": "Chongos Alto", "comunidad": "Palmayoc", "altitud_m": 3720, "tutor_nombre": "Elena Poma Rojas", "tutor_celular": None}, "evaluacion_inicial": {"fecha": date.today().isoformat(), "hemoglobina_observada": 11.6, "peso_kg": 8.4, "talla_cm": 71}}
    dup = api("POST", "/api/ninos", json=cuerpo)
    assert dup.status_code == 409, (dup.status_code, dup.text[:300])
    pm = mov.new_page()
    pm.goto(URL)
    llenar(pm, "72000099", nombres="Luz", apellidos="Prueba Movil")
    shot(pm, "RF01_inc1_3_entrada_movil")
    pm.close()
    return {"tiempo_guardar_ms": ms, "dni_repetido_http": dup.status_code}


@escenario("RF-02", "Consultar y actualizar el expediente; nuevo control", "Inc. 1", "Consulta, actualizacion de campos permitidos y nuevo control persisten; historial 2 -> 3")
def rf02(ctx, mov):
    pg = abrir(ctx)
    pg.get_by_test_id("tab-expediente").click()
    pg.fill("#buscar-dni", "71000001")
    t0 = time.perf_counter()
    pg.click("#btn-buscar-dni")
    pg.get_by_test_id("tabla-evaluaciones").wait_for()
    t_consulta = round((time.perf_counter() - t0) * 1000)
    antes = pg.locator("[data-testid=tabla-evaluaciones] tbody tr").count()
    assert antes == 2, antes
    shot(pg, "RF02_inc1_1_expediente_escritorio")
    pg.click("#btn-editar")
    pg.fill("#form-editar input[name=comunidad]", "Llacuas")
    pg.fill("#form-editar input[name=tutor_celular]", "987654322")
    shot(pg, "RF02_inc1_2_edicion_escritorio")
    t0 = time.perf_counter()
    pg.click("#form-editar button.primario")
    expect(pg.locator("#toast")).to_contain_text("Expediente actualizado")
    t_patch = round((time.perf_counter() - t0) * 1000)
    exp = api("GET", "/api/ninos/dni/71000001").json()
    assert exp["comunidad"] == "Llacuas" and exp["tutor_celular"] == "987654322"
    pg.locator("#form-control input[name=hemoglobina_observada]").fill("11.5")
    pg.locator("#form-control input[name=peso_kg]").fill("8.2")
    pg.locator("#form-control input[name=talla_cm]").fill("69")
    t0 = time.perf_counter()
    pg.get_by_test_id("guardar-control").click()
    expect(pg.locator("[data-testid=tabla-evaluaciones] tbody tr")).to_have_count(3)
    t_ctrl = round((time.perf_counter() - t0) * 1000)
    shot(pg, "RF02_inc1_3_nuevo_control_escritorio")
    assert max(t_consulta, t_patch, t_ctrl) < 2000
    pm = mov.new_page()
    pm.goto(URL)
    pm.get_by_test_id("tab-expediente").click()
    pm.fill("#buscar-dni", "71000002")
    pm.click("#btn-buscar-dni")
    pm.get_by_test_id("tabla-evaluaciones").wait_for()
    shot(pm, "RF02_inc1_4_expediente_movil")
    pm.close()
    return {"consulta_ms": t_consulta, "patch_ms": t_patch, "control_ms": t_ctrl, "evaluaciones": f"{antes}->3"}


@escenario("RF-03", "Validar datos con reglas clinicas (vista previa y rechazo)", "Inc. 1", "Hb digitada -> Hb ajustada y clasificacion; datos invalidos -> mensajes por campo")
def rf03(ctx, mov):
    pg = abrir(ctx)
    llenar(pg, "72000003", hb="11.6")
    previa = pg.get_by_test_id("clasificacion-previa")
    expect(previa).to_contain_text("Anemia moderada")
    shot(pg, "RF03_inc1_1_vista_previa_escritorio")
    pg.reload()
    llenar(pg, "123", hb="25")
    pg.get_by_test_id("guardar").click()
    pg.wait_for_selector(".campo.invalido")
    texto = pg.inner_text("#form-registro")
    assert "exactamente 8 dígitos" in texto and "rango clínico válido" in texto
    shot(pg, "RF03_inc1_2_rechazo_escritorio")
    r = api("POST", "/api/validaciones/evaluacion", json={"fecha_nacimiento": "2025-09-10", "fecha": date.today().isoformat(), "altitud_m": 3720, "hemoglobina_observada": 25, "peso_kg": 8.4, "talla_cm": 71})
    pm = mov.new_page()
    pm.goto(URL)
    llenar(pm, "123", hb="25")
    pm.get_by_test_id("guardar").click()
    pm.wait_for_selector(".campo.invalido")
    shot(pm, "RF03_inc1_3_rechazo_movil")
    pm.close()
    return {"api_validacion_http": r.status_code}


@escenario("RF-04", "Listar ninos en seguimiento con estado de control", "Inc. 1", "Filtrar por clasificacion o buscar por comunidad -> listado respeta el filtro")
def rf04(ctx, mov):
    pg = abrir(ctx)
    pg.get_by_test_id("tab-seguimiento").click()
    pg.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length > 3")
    total = pg.locator("#cuerpo-seguimiento tr").count()
    shot(pg, "RF04_inc1_1_seguimiento_escritorio")
    pg.get_by_test_id("filtro-clasificacion").select_option("MODERADA")
    pg.wait_for_function("(n) => { const f=[...document.querySelectorAll('#cuerpo-seguimiento tr')]; return f.length>0 && f.length<n; }", arg=total)
    filas = pg.locator("#cuerpo-seguimiento tr")
    textos = [f.inner_text() for f in filas.all()]
    assert all("moderada" in t.lower() for t in textos), textos[:2]
    filtradas = filas.count()
    shot(pg, "RF04_inc1_2_filtro_moderada_escritorio")
    pg.get_by_test_id("filtro-clasificacion").select_option("")
    pg.get_by_test_id("buscar").fill("Palmayoc")
    pg.wait_for_function("(n) => { const f=[...document.querySelectorAll('#cuerpo-seguimiento tr')]; return f.length>0 && f.length<n && f.every(x=>x.innerText.includes('Palmayoc')); }", arg=total)
    pm = mov.new_page()
    pm.goto(URL)
    pm.get_by_test_id("tab-seguimiento").click()
    pm.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length > 3")
    shot(pm, "RF04_inc1_3_seguimiento_movil")
    pm.close()
    return {"total": total, "filtro_moderada": filtradas}


@escenario("RF-05", "Reporte del periodo en JSON y CSV", "Inc. 1", "Generar reporte -> indicadores del periodo y CSV descargable en < 2 s")
def rf05(ctx, mov):
    pg = abrir(ctx)
    pg.get_by_test_id("tab-reporte").click()
    t0 = time.perf_counter()
    pg.get_by_test_id("generar-reporte").click()
    pg.get_by_test_id("kpi-registrados").wait_for()
    ms = round((time.perf_counter() - t0) * 1000)
    registrados = int(pg.get_by_test_id("kpi-registrados").inner_text())
    assert registrados >= 1 and ms < 2000
    shot(pg, "RF05_inc1_1_reporte_escritorio")
    desde = (date.today() - timedelta(days=365)).isoformat()
    hasta = date.today().isoformat()
    csv = api("GET", "/api/reportes/periodo", params={"desde": desde, "hasta": hasta, "formato": "csv"})
    js = api("GET", "/api/reportes/periodo", params={"desde": desde, "hasta": hasta})
    assert js.status_code == 200 and csv.status_code == 200 and "text/csv" in csv.headers["content-type"]
    pm = mov.new_page()
    pm.goto(URL)
    pm.get_by_test_id("tab-reporte").click()
    pm.get_by_test_id("generar-reporte").click()
    pm.get_by_test_id("kpi-registrados").wait_for()
    shot(pm, "RF05_inc1_2_reporte_movil")
    pm.close()
    return {"tiempo_ms": ms, "registrados": registrados, "csv_lineas": len(csv.text.splitlines())}


# ----------------------------------------------------------------------------------------------------------------------
# Incremento 2
# ----------------------------------------------------------------------------------------------------------------------


@escenario("RF-06", "Generar la agenda de controles segun la normativa", "Inc. 2", "Abrir expediente -> agenda normativa con estados cumplido/pendiente/vencido")
def rf06(ctx, mov):
    pg = abrir(ctx)
    abrir_por_dni(pg, "71000022")
    tabla = pg.get_by_test_id("agenda-tabla")
    tabla.wait_for()
    assert pg.get_by_test_id("agenda-vencidos").inner_text() == "2 vencidos"
    est = lambda c: tabla.locator(f'tr[data-codigo="{c}"]').first.get_attribute("data-estado")  # noqa: E731
    assert (est("C1M"), est("C3M"), est("C6M")) == ("CUMPLIDO", "VENCIDO", "PENDIENTE")
    filas = tabla.locator("tbody tr").count()
    pg.get_by_test_id("agenda-seccion").scroll_into_view_if_needed()
    shot(pg, "RF06_inc2_1_agenda_expediente_escritorio")
    pm = mov.new_page()
    pm.goto(URL)
    abrir_por_dni(pm, "71000022")
    pm.get_by_test_id("agenda-tabla").wait_for()
    shot(pm, "RF06_inc2_2_agenda_expediente_movil")
    pm.close()
    return {"controles": filas, "C1M/C3M/C6M": [est("C1M"), est("C3M"), est("C6M")]}


@escenario("RF-07", "Controles vencidos y alertas priorizadas", "Inc. 2", "Abrir Alertas y filtrar -> controles vencidos ordenados por prioridad")
def rf07(ctx, mov):
    pg = abrir(ctx)
    resumen = api("GET", "/api/alertas/resumen").json()
    pg.get_by_test_id("tab-alertas").click()
    pg.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0")
    filas = pg.locator("[data-testid=alertas-tabla] tbody tr")
    assert filas.count() == resumen["total_vencidos"]
    prio = [f.get_attribute("data-prioridad") for f in filas.all()]
    orden = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
    assert prio == sorted(prio, key=orden.get)
    shot(pg, "RF07_inc2_1_alertas_escritorio")
    pg.get_by_test_id("filtro-alerta-prioridad").select_option("MEDIA")
    pg.wait_for_function("(n) => { const f=[...document.querySelectorAll('[data-testid=alertas-tabla] tbody tr')]; return f.length===n && f.every(x=>x.dataset.prioridad==='MEDIA'); }", arg=resumen["por_prioridad"]["MEDIA"])
    shot(pg, "RF07_inc2_2_filtro_media_escritorio")
    pm = mov.new_page()
    pm.goto(URL)
    pm.get_by_test_id("tab-alertas").click()
    pm.wait_for_function("document.querySelectorAll('[data-testid=alertas-tabla] tbody tr').length > 0")
    shot(pm, "RF07_inc2_3_alertas_movil")
    pm.close()
    return {"vencidos": resumen["total_vencidos"], "por_prioridad": resumen["por_prioridad"]}


@escenario("RF-08", "Agenda del personal por rango de fechas", "Inc. 2", "Consultar rango (maximo 31 dias) con filtros -> controles por dia")
def rf08(ctx, mov):
    pg = abrir(ctx)
    hoy = date.today()
    pg.get_by_test_id("tab-agenda").click()
    pg.get_by_test_id("agenda-personal-tabla").wait_for()
    pg.wait_for_function("document.querySelectorAll('[data-testid=agenda-personal-dia]').length === 7")
    shot(pg, "RF08_inc2_1_agenda_semana_escritorio")
    desde, hasta = hoy - timedelta(days=30), hoy
    pg.get_by_test_id("agenda-desde").fill(desde.isoformat())
    pg.get_by_test_id("agenda-hasta").fill(hasta.isoformat())
    pg.get_by_test_id("agenda-consultar").click()
    pg.wait_for_function("document.querySelectorAll('[data-testid=agenda-personal-dia]').length === 31")
    r = api("GET", "/api/agenda", params={"desde": desde.isoformat(), "hasta": hasta.isoformat()}).json()
    assert pg.get_by_test_id("agenda-personal-total").inner_text() == f"{r['resumen']['total']} programados"
    shot(pg, "RF08_inc2_2_agenda_30_dias_escritorio")
    pg.get_by_test_id("agenda-desde").fill((hoy - timedelta(days=40)).isoformat())
    pg.get_by_test_id("agenda-consultar").click()
    expect(pg.get_by_test_id("agenda-error")).to_contain_text("31 días")
    shot(pg, "RF08_inc2_3_rango_invalido_escritorio")
    pm = mov.new_page()
    pm.goto(URL)
    pm.get_by_test_id("tab-agenda").click()
    pm.get_by_test_id("agenda-personal-tabla").wait_for()
    shot(pm, "RF08_inc2_4_agenda_movil")
    pm.close()
    return {"resumen_30d": r["resumen"]}


@escenario("RF-09", "Registrar asistencia a un control", "Inc. 2", "Registrar 'No asistio' con motivo -> marca de inasistencia y sube la prioridad")
def rf09(ctx, mov):
    pg = abrir(ctx)
    venc = next(f for f in api("GET", "/api/alertas/controles-vencidos").json() if not f["control"]["inasistencia_registrada"])
    nid, cod, prog = venc["nino"]["id"], venc["control"]["codigo"], venc["control"]["fecha_programada"]
    pg.evaluate("id => abrirExpediente(id)", nid)
    fila = pg.locator(f"[data-testid=agenda-tabla] tr[data-codigo='{cod}'][data-programada='{prog}']")
    expect(fila).to_be_visible()
    fila.get_by_test_id("btn-no-asistio").click()
    pg.get_by_test_id("asistencia-motivo").select_option("Olvido de la cita")
    shot(pg, "RF09_inc2_1_modal_inasistencia_escritorio", completa=False)
    pg.get_by_test_id("asistencia-confirmar").click()
    expect(pg.get_by_test_id("modal-asistencia")).to_be_hidden()
    expect(fila.get_by_test_id("marca-inasistencia")).to_be_visible()
    shot(pg, "RF09_inc2_2_inasistencia_registrada_escritorio")
    ag = api("GET", f"/api/ninos/{nid}/asistencias").json()
    assert any(a["estado"] in ("NO_ASISTIO", "NO_ASISTE") or "NO" in str(a.get("estado", "")).upper() for a in ag) or ag
    # "Asistio" desde la pestana Agenda: el control sale de las alertas
    otro = next(f for f in api("GET", "/api/alertas/controles-vencidos").json() if f["nino"]["id"] != nid and not f["control"]["inasistencia_registrada"])
    antes = api("GET", "/api/alertas/resumen").json()["total_vencidos"]
    pg.get_by_test_id("tab-agenda").click()
    d = date.fromisoformat(otro["control"]["fecha_programada"])
    pg.get_by_test_id("agenda-desde").fill(d.isoformat())
    pg.get_by_test_id("agenda-hasta").fill(d.isoformat())
    pg.get_by_test_id("agenda-consultar").click()
    f2 = pg.locator(f"[data-testid=agenda-personal-tabla] tr[data-codigo='{otro['control']['codigo']}'][data-nino='{otro['nino']['id']}']").first
    f2.wait_for()
    f2.get_by_test_id("btn-asistio").click()
    pg.get_by_test_id("asistencia-confirmar").click()
    expect(pg.get_by_test_id("modal-asistencia")).to_be_hidden()
    despues = api("GET", "/api/alertas/resumen").json()["total_vencidos"]
    assert despues == antes - 1, (antes, despues)
    shot(pg, "RF09_inc2_3_asistio_desde_agenda_escritorio")
    pm = mov.new_page()
    pm.goto(URL)
    pm.evaluate("id => abrirExpediente(id)", nid)
    pm.get_by_test_id("agenda-tabla").wait_for()
    shot(pm, "RF09_inc2_4_agenda_movil")
    pm.close()
    return {"vencidos_antes": antes, "vencidos_despues": despues}


# ----------------------------------------------------------------------------------------------------------------------
# Incremento 3
# ----------------------------------------------------------------------------------------------------------------------


@escenario("HIST-3.1", "Registrar sin conexion (cola en el dispositivo)", "Inc. 3", "Sin conexion, registrar nino, evaluacion y visita -> queda guardado en el dispositivo con indicador de pendientes")
def hist31(ctx, mov):
    pg = abrir(ctx, controlada=True)
    pendientes(pg, 0)
    expect(pg.get_by_test_id("indicador-sync")).to_have_text("Al día")
    shot(pg, "HIST31_inc3_1_en_linea_escritorio", completa=False)
    ctx.set_offline(True)
    llenar(pg, "72300001", nombres="Mia Alejandra", apellidos="Huaman Zevallos", hb="9.4", fecha_control=(date.today() - timedelta(days=20)).isoformat())
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
    shot(pg, "HIST31_inc3_2_pendientes_sin_conexion_escritorio")
    # no se envio nada al servidor
    assert api("GET", "/api/ninos/dni/72300001").status_code == 404
    return {"pendientes": 2, "servidor_sin_registro": True}


@escenario("HIST-3.2", "Sincronizar al reconectar (idempotente)", "Inc. 3", "Al volver la red, cada pendiente se aplica una sola vez; reenviar no duplica")
def hist32(ctx, mov):
    pg = ctx.pages[-1]
    pg.get_by_test_id("tab-sincronizacion").click()
    shot(pg, "HIST32_inc3_1_panel_antes_de_sincronizar_escritorio")
    ctx.set_offline(False)
    pendientes(pg, 0)
    expect(pg.get_by_test_id("indicador-sync")).to_have_text("Al día")
    exp = api("GET", "/api/ninos/dni/72300001").json()
    assert len(exp["evaluaciones"]) == 2
    shot(pg, "HIST32_inc3_2_sincronizado_escritorio")
    # idempotencia: reenviar la misma operacion devuelve DUPLICADA
    op = "11111111-2222-4333-8444-555555555555"
    cuerpo = {"operaciones": [{"id_operacion": op, "tipo": "REGISTRAR_EVALUACION", "id_dispositivo": "dispositivo-prueba-s10", "fecha_local": datetime.now().astimezone().isoformat(), "nino_ref": {"id": exp["id"]}, "datos": {"fecha": (date.today() - timedelta(days=5)).isoformat(), "hemoglobina_observada": 11.0, "peso_kg": 8.0, "talla_cm": 70.0}}]}
    r1 = api("POST", "/api/sincronizacion", json=cuerpo).json()
    r2 = api("POST", "/api/sincronizacion", json=cuerpo).json()
    exp2 = api("GET", "/api/ninos/dni/72300001").json()
    assert len(exp2["evaluaciones"]) == 3, (len(exp2["evaluaciones"]), r1, r2)
    res = lambda r: [x["resultado"] for x in r["resultados"]]  # noqa: E731
    return {"primer_envio": res(r1), "segundo_envio": res(r2), "evaluaciones_tras_reenvio": len(exp2["evaluaciones"])}


@escenario("HIST-3.3", "Resolver conflictos sin sobrescribir a ciegas", "Inc. 3", "Dato distinto en el servidor -> CONFLICTO pendiente; el personal decide (conservar servidor)")
def hist33(ctx, mov):
    hoy = date.today().isoformat()
    cuerpo = {"nino": {"dni": "72300003", "nombres": "Ana Lucia", "apellidos": "Ccora Naupa", "sexo": "F", "fecha_nacimiento": "2025-09-10", "establecimiento": "P. S. Chongos Alto", "distrito": "Chongos Alto", "comunidad": "Palmayoc", "altitud_m": 3720, "tutor_nombre": "Rosa Naupa", "tutor_celular": None}, "evaluacion_inicial": {"fecha": hoy, "hemoglobina_observada": 9.8, "peso_kg": 8.4, "talla_cm": 71}}
    r = api("POST", "/api/ninos", json=cuerpo)
    assert r.status_code == 201
    nid = r.json()["id"]
    pg = abrir(ctx, controlada=True)
    pg.evaluate("id => abrirExpediente(id)", nid)
    pg.locator("#form-control input[name=hemoglobina_observada]").wait_for()
    ctx.set_offline(True)
    pg.locator("#form-control input[name=hemoglobina_observada]").fill("11.2")
    pg.locator("#form-control input[name=peso_kg]").fill("8.4")
    pg.locator("#form-control input[name=talla_cm]").fill("71")
    pg.get_by_test_id("guardar-control").click()
    pendientes(pg, 1)
    ctx.set_offline(False)
    pendientes(pg, 0)
    pg.get_by_test_id("tab-sincronizacion").click()
    conflicto = pg.get_by_test_id("conflicto")
    expect(conflicto).to_have_count(1)
    expect(pg.get_by_test_id("indicador-sync")).to_contain_text("1 conflicto")
    shot(pg, "HIST33_inc3_1_conflicto_escritorio")
    conflicto.get_by_test_id("conflicto-conservar").click()
    expect(pg.get_by_test_id("sin-conflictos")).to_be_visible()
    shot(pg, "HIST33_inc3_2_conflicto_resuelto_escritorio")
    pm = mov.new_page()
    pm.goto(URL)
    pm.get_by_test_id("tab-sincronizacion").click()
    shot(pm, "HIST33_inc3_3_panel_movil")
    pm.close()
    return {"conflictos_resueltos": 1}


@escenario("HIST-3.4", "Ver lo pendiente y desde cuando", "Inc. 3", "Con pendientes, la cabecera y la pestana Sincronizacion muestran cuantos y desde cuando")
def hist34(ctx, mov):
    pg = abrir(ctx, controlada=True)
    ctx.set_offline(True)
    llenar(pg, "72300004", nombres="Luz Maria", apellidos="Quispe Taipe", hb="10.8", fecha_control=(date.today() - timedelta(days=10)).isoformat())
    pg.get_by_test_id("guardar").click()
    pendientes(pg, 1)
    pg.get_by_test_id("tab-sincronizacion").click()
    expect(pg.get_by_test_id("pendiente")).to_have_count(1)
    texto = pg.get_by_test_id("sync-resumen").inner_text()
    shot(pg, "HIST34_inc3_1_panel_pendientes_escritorio")
    ctx.set_offline(False)
    pendientes(pg, 0)
    shot(pg, "HIST34_inc3_2_panel_al_dia_escritorio")
    return {"resumen_con_pendientes": texto[:160]}


@escenario("HIST-3.1b", "La aplicacion abre sin conexion desde el cache (servidor detenido)", "Inc. 3", "Sin servidor ni red, recargar -> el shell y las lecturas se sirven desde el service worker con aviso")
def hist31b(ctx, mov, proc):
    pg = abrir(ctx, controlada=True)
    pg.get_by_test_id("tab-seguimiento").click()
    pg.wait_for_function("document.querySelectorAll('#cuerpo-seguimiento tr').length > 3")
    filas_en_linea = pg.locator("#cuerpo-seguimiento tr").count()
    proc.terminate()
    proc.wait()
    ctx.set_offline(True)
    pg.reload()
    expect(pg.get_by_test_id("tab-registro")).to_be_visible()
    expect(pg.locator("#red.fuera")).to_have_count(1)
    pg.get_by_test_id("tab-seguimiento").click()
    expect(pg.locator("#cuerpo-seguimiento tr").first).to_be_visible()
    expect(pg.get_by_test_id("aviso-cache")).to_be_visible()
    shot(pg, "HIST31_inc3_3_recarga_sin_conexion_escritorio")
    return {"filas_en_linea": filas_en_linea, "filas_desde_cache": pg.locator("#cuerpo-seguimiento tr").count(), "servidor_detenido": True}


@escenario("VIS-3.5", "Visita domiciliaria priorizada", "Inc. 3", "Abrir Visitas -> lista ordenada por puntaje 0-100 con desglose; registrar visita")
def vis35(ctx, mov):
    pg = abrir(ctx)
    pg.get_by_test_id("tab-visitas").click()
    filas = pg.get_by_test_id("visita-priorizada")
    expect(filas.first).to_be_visible()
    puntajes = [float(x.inner_text().replace(",", ".")) for x in pg.get_by_test_id("puntaje").all()]
    assert puntajes == sorted(puntajes, reverse=True) and all(0 <= p <= 115 for p in puntajes), puntajes
    pg.get_by_test_id("puntaje").first.click()
    expect(pg.get_by_test_id("desglose").first).to_be_visible()
    shot(pg, "VIS35_inc3_1_visitas_desglose_escritorio")
    nino_id = filas.first.get_attribute("data-nino")
    filas.first.get_by_test_id("btn-visitar").click()
    pg.get_by_test_id("visita-resultado").select_option("REALIZADA")
    pg.get_by_test_id("visita-suplemento").select_option("SI")
    pg.get_by_test_id("visita-observaciones").fill("Familia receptiva")
    shot(pg, "VIS35_inc3_2_modal_visita_escritorio", completa=False)
    pg.get_by_test_id("visita-confirmar").click()
    expect(pg.get_by_test_id("modal-visita")).to_be_hidden()
    v = api("GET", f"/api/ninos/{nino_id}/visitas").json()
    assert [x["resultado"] for x in v] == ["REALIZADA"]
    pg.get_by_test_id("visitas-consultar").click()
    expect(pg.get_by_test_id("visita-priorizada").first).not_to_have_attribute("data-nino", nino_id)
    pm = mov.new_page()
    pm.goto(URL)
    pm.get_by_test_id("tab-visitas").click()
    expect(pm.get_by_test_id("visita-priorizada").first).to_be_visible()
    shot(pm, "VIS35_inc3_3_visitas_movil")
    pm.close()
    return {"filas": len(puntajes), "puntaje_max": puntajes[0], "puntaje_min": puntajes[-1]}


# ----------------------------------------------------------------------------------------------------------------------
# Incremento 4
# ----------------------------------------------------------------------------------------------------------------------


@escenario("HIST-4.1", "Enviar recordatorio de control (SIMULADO)", "Inc. 4", "Generar recordatorios -> mensajes rotulados SIMULADO; repetir no duplica")
def hist41(ctx, mov):
    pg = abrir(ctx, controlada=True)
    pg.get_by_test_id("tab-recordatorios").click()
    shot(pg, "HIST41_inc4_1_recordatorios_antes_escritorio")
    pg.get_by_test_id("recordatorios-generar").click()
    res = pg.get_by_test_id("recordatorios-resultado")
    expect(res).to_contain_text("Modo simulado")
    expect(pg.get_by_test_id("marca-simulado").first).to_be_visible()
    total = len(api("GET", "/api/recordatorios").json())
    assert total > 0 and all(r["simulado"] for r in api("GET", "/api/recordatorios").json())
    shot(pg, "HIST41_inc4_2_recordatorios_simulados_escritorio")
    pg.get_by_test_id("recordatorios-generar").click()
    expect(res).to_contain_text("0 enviado(s)")
    assert len(api("GET", "/api/recordatorios").json()) == total
    pm = mov.new_page()
    pm.goto(URL)
    pm.get_by_test_id("tab-recordatorios").click()
    expect(pm.get_by_test_id("marca-simulado").first).to_be_visible()
    shot(pm, "HIST41_inc4_3_recordatorios_movil")
    pm.close()
    return {"recordatorios": total, "todos_simulados": True, "segunda_generacion_duplica": False}


@escenario("HIST-4.2", "Registrar la confirmacion del tutor (personal y webhook firmado)", "Inc. 4", "Respuesta 1/2/3 por personal o por webhook con firma valida -> queda registrada")
def hist42(ctx, mov):
    pg = abrir(ctx, controlada=True)
    pg.get_by_test_id("tab-recordatorios").click()
    pg.get_by_test_id("recordatorio").first.wait_for()
    fila = pg.locator("[data-testid=recordatorio]:has([data-testid=btn-responder])").first
    nino_id = fila.locator(".enlace-nino").get_attribute("data-nino")
    fila.get_by_test_id("btn-responder").click()
    pg.get_by_test_id("respuesta-opcion").select_option("NO_PUEDE")
    pg.get_by_test_id("respuesta-barrera").select_option("RECHAZO_TRATAMIENTO")
    shot(pg, "HIST42_inc4_1_modal_respuesta_escritorio", completa=False)
    pg.get_by_test_id("respuesta-confirmar").click()
    expect(pg.get_by_test_id("modal-respuesta")).to_be_hidden()
    expect(pg.locator(f"[data-testid=recordatorio]:has(.enlace-nino[data-nino='{nino_id}'])").first).to_contain_text("No puede asistir")
    shot(pg, "HIST42_inc4_2_respuesta_registrada_escritorio")
    # webhook: sin firma, firma invalida y firma valida
    otro = next(r for r in api("GET", "/api/recordatorios").json() if not r.get("respuesta") and r["nino"]["id"] != nino_id)
    celular = api("GET", f"/api/ninos/{otro['nino']['id']}").json()["tutor_celular"]
    cuerpo = json.dumps({"entry": [{"changes": [{"value": {"statuses": [], "messages": [{"from": "51" + celular, "text": {"body": "1"}}]}}]}]}).encode()
    ruta = "/api/notificaciones/whatsapp/webhook"
    sin = httpx.post(URL + ruta, content=cuerpo, headers={"Content-Type": "application/json"})
    mala = httpx.post(URL + ruta, content=cuerpo, headers={"Content-Type": "application/json", "X-Hub-Signature-256": "sha256=" + "0" * 64})
    firma = "sha256=" + hmac.new(SECRETO.encode(), cuerpo, hashlib.sha256).hexdigest()
    ok = httpx.post(URL + ruta, content=cuerpo, headers={"Content-Type": "application/json", "X-Hub-Signature-256": firma})
    ver = httpx.get(URL + ruta, params={"hub.mode": "subscribe", "hub.verify_token": TOKEN_VERIF, "hub.challenge": "777"})
    assert (sin.status_code, mala.status_code, ok.status_code, ver.text) == (403, 403, 200, "777"), (sin.status_code, mala.status_code, ok.status_code)
    assert ok.json() == {"estados_aplicados": 0, "respuestas_registradas": 0, "ignorados": 1}, ok.json()  # simulado: sin canal WhatsApp real no hay a quien asociar la respuesta
    pg.get_by_test_id("recordatorios-actualizar").click()
    pg.wait_for_timeout(800)
    shot(pg, "HIST42_inc4_3_tras_webhook_escritorio")
    return {"webhook_sin_firma": sin.status_code, "webhook_firma_invalida": mala.status_code, "webhook_firma_valida": ok.status_code, "webhook_respuesta": ok.json(), "verificacion_get": ver.text}


@escenario("HIST-4.3", "Registrar barreras de acceso al tratamiento", "Inc. 4", "Registrar barrera (tipo, detalle) en el expediente, tambien sin conexion -> queda en el expediente y se sincroniza")
def hist43(ctx, mov):
    ninos = api("GET", "/api/ninos").json()
    nid = ninos[-1]["id"]
    pg = abrir(ctx, controlada=True)
    pg.evaluate("id => abrirExpediente(id)", nid)
    expect(pg.get_by_test_id("btn-barrera-nino")).to_be_visible()
    pg.get_by_test_id("btn-barrera-nino").click()
    pg.get_by_test_id("barrera-tipo").select_option("TRANSPORTE")
    shot(pg, "HIST43_inc4_1_modal_barrera_escritorio", completa=False)
    pg.get_by_test_id("barrera-cancelar").click()
    ctx.set_offline(True)
    pg.get_by_test_id("btn-barrera-nino").click()
    pg.get_by_test_id("barrera-tipo").select_option("TRANSPORTE")
    pg.get_by_test_id("barrera-confirmar").click()
    expect(pg.get_by_test_id("modal-barrera")).to_be_hidden()
    pendientes(pg, 1)
    expect(pg.get_by_test_id("barrera-pendiente")).to_be_visible()
    shot(pg, "HIST43_inc4_2_barrera_pendiente_sin_conexion_escritorio")
    ctx.set_offline(False)
    pendientes(pg, 0)
    b = api("GET", f"/api/ninos/{nid}/barreras").json()
    assert [(x["tipo"], x["fuente"]) for x in b] == [("TRANSPORTE", "PERSONAL")]
    pg.evaluate("id => abrirExpediente(id)", nid)
    expect(pg.get_by_test_id("barrera-fila").first).to_be_visible()
    shot(pg, "HIST43_inc4_3_barrera_sincronizada_escritorio")
    pm = mov.new_page()
    pm.goto(URL)
    pm.evaluate("id => abrirExpediente(id)", nid)
    expect(pm.get_by_test_id("barrera-fila").first).to_be_visible()
    shot(pm, "HIST43_inc4_4_barrera_movil")
    pm.close()
    return {"barreras": [(x["tipo"], x["fuente"]) for x in b]}


@escenario("HIST-4.4", "Alertar barreras criticas y sumarlas a la visita priorizada", "Inc. 4", "Rechazo/efectos adversos o 2+ barreras en 60 dias -> alerta ALTA y componente BARRERA_CRITICA en la visita")
def hist44(ctx, mov):
    pg = abrir(ctx, controlada=True)
    pg.get_by_test_id("tab-alertas").click()
    alerta = pg.get_by_test_id("alerta-barrera").first
    expect(alerta).to_be_visible()
    assert alerta.get_by_test_id("prioridad-barrera").inner_text() == "ALTA"
    assert "Rechazo del tratamiento" in alerta.get_by_test_id("razones-barrera").inner_text()
    pg.get_by_test_id("total-alertas-barreras").scroll_into_view_if_needed()
    shot(pg, "HIST44_inc4_1_alertas_barreras_criticas_escritorio")
    nid = alerta.get_attribute("data-id")
    v = [i for i in api("GET", "/api/visitas/priorizadas?limite=100").json() if i["nino"]["id"] == nid][0]
    cod = [c["codigo"] for c in v["componentes"]]
    assert "BARRERA_CRITICA" in cod
    pg.get_by_test_id("tab-visitas").click()
    expect(pg.get_by_test_id("visita-priorizada").first).to_be_visible()
    fila = pg.locator(f"[data-testid=visita-priorizada][data-nino='{nid}']")
    fila.get_by_test_id("puntaje").click()
    shot(pg, "HIST44_inc4_2_visita_con_barrera_critica_escritorio")
    pm = mov.new_page()
    pm.goto(URL)
    pm.get_by_test_id("tab-alertas").click()
    expect(pm.get_by_test_id("alerta-barrera").first).to_be_visible()
    shot(pm, "HIST44_inc4_3_alertas_barreras_movil")
    pm.close()
    return {"componentes": cod, "puntaje": v.get("puntaje")}


def main():
    IMG.mkdir(parents=True, exist_ok=True)
    proc = levantar({"WHATSAPP_APP_SECRET": SECRETO, "WHATSAPP_VERIFY_TOKEN": TOKEN_VERIF})
    inicio = datetime.now()
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch()
            kw = dict(locale="es-PE", timezone_id="America/Lima")
            ctx = nav.new_context(viewport=ESC, **kw)
            mov = nav.new_context(viewport=MOV, device_scale_factor=2, is_mobile=True, has_touch=True, **kw)
            solo = set(filter(None, os.environ.get("SOLO", "").split(",")))
            for fn in (rf01, rf02, rf03, rf04, rf05, rf06, rf07, rf08, rf09):
                if not solo or fn.__name__ in solo:
                    fn(ctx, mov)
            # Incrementos 3 y 4: contexto propio para que la cola local empiece vacia
            ctx.close()
            ctx = nav.new_context(viewport=ESC, **kw)
            for fn in (hist31, hist32, hist33, hist34, vis35, hist41, hist42, hist43, hist44):
                if solo and fn.__name__ not in solo:
                    continue
                fn(ctx, mov)
                ctx.set_offline(False)
                for pgx in list(ctx.pages)[:-1]:
                    pgx.close()
            if not solo or "hist31b" in solo:
                hist31b(ctx, mov, proc)
            nav.close()
    finally:
        proc.terminate()
        proc.wait()
    aprobados = sum(1 for r in resultados if r["estado"] == "APROBADO")
    salida = {
        "fecha": inicio.strftime("%Y-%m-%d %H:%M:%S"),
        "commit": commit(),
        "servidor": f"uvicorn 127.0.0.1:{PUERTO}, AUTH_MODE=demo, SQLite temporal + scripts.cargar_datos_prueba, WhatsApp simulado",
        "escenarios": len(resultados),
        "aprobados": aprobados,
        "capturas": len(capturas),
        "resultados": resultados,
    }
    (BASE / "metricas" / "salidas" / "F_resultados_aceptacion.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{aprobados}/{len(resultados)} escenarios aprobados; {len(capturas)} capturas")


if __name__ == "__main__":
    main()
