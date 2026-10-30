"""CP-370 a CP-397: integración API + SQLAlchemy (SQLite) del Incremento 4: recordatorios por WhatsApp (HIST-4.1),
respuesta del tutor y webhook (HIST-4.2), barreras (HIST-4.3) y alerta de barreras críticas (HIST-4.4). Hoy = 28-sep-2026.

Ninguna prueba hace una llamada de red real: el notificador es el simulado o un cliente con ``httpx.MockTransport``.
"""

import json
import uuid
from datetime import date

import httpx
import pytest
from fastapi.testclient import TestClient

from app.adapters.outbound.notificaciones import crear_notificador
from app.domain.model.notificacion import ConfiguracionWebhook
from app.domain.model.origen import OrigenDatos
from app.domain.service.notificaciones import firmar
from app.main import crear_app
from tests.conftest import RelojFijo, cuerpo_registro, nino_de
from tests.integracion.test_api_inc2 import ESCENARIO, registrar
from tests.integracion.test_autenticacion import CSRF, USER, auth_cliente, ingresar  # noqa: F401

ESCENARIO_NACIMIENTO = date(2025, 9, 1)
ESCENARIO_EVALUACION = date(2026, 7, 1)
USUARIO = {"X-Usuario": "enf.rosa"}
RUTA_WEBHOOK = "/api/notificaciones/whatsapp/webhook"
SECRETO = "secreto-de-prueba"
TOKEN_VERIFICACION = "token-de-verificacion"


def barrera(**cambios):
    return {"tipo": "TRANSPORTE", "fuente": "PERSONAL", "fecha": "2026-09-20"} | cambios


def generar(cliente, **cuerpo):
    r = cliente.post("/api/recordatorios/generar", json=cuerpo or None, headers=USUARIO)
    assert r.status_code == 200, r.text
    return r.json()


# --- HIST-4.3: barreras -----------------------------------------------------------------------------------------------


def test_cp370_registrar_y_listar_barreras_del_nino(cliente):
    nino = registrar(cliente, **ESCENARIO["T"])
    r = cliente.post(f"/api/ninos/{nino}/barreras", json=barrera(fecha="2026-09-10"), headers=USUARIO)
    assert r.status_code == 201, r.text
    primera = r.json()
    assert (primera["tipo"], primera["fuente"], primera["fecha"], primera["detalle"]) == (
        "TRANSPORTE",
        "PERSONAL",
        "2026-09-10",
        None,
    )
    assert primera["registrado_por"] == "enf.rosa" and primera["nino_id"] == nino and primera["recordatorio_id"] is None
    otra = cliente.post(
        f"/api/ninos/{nino}/barreras",
        json=barrera(tipo="OTRA", detalle="Río crecido", fecha="2026-09-25"),
        headers=USUARIO,
    ).json()
    lista = cliente.get(f"/api/ninos/{nino}/barreras").json()
    assert [b["id"] for b in lista] == [otra["id"], primera["id"]] and lista[0]["detalle"] == "Río crecido"


def test_cp371_la_barrera_repetida_es_409_y_los_datos_invalidos_422_y_el_nino_inexistente_404(cliente):
    nino = registrar(cliente, **ESCENARIO["T"])
    assert cliente.post(f"/api/ninos/{nino}/barreras", json=barrera(), headers=USUARIO).status_code == 201
    repetida = cliente.post(f"/api/ninos/{nino}/barreras", json=barrera(), headers=USUARIO)
    assert repetida.status_code == 409 and "ya tiene registrada" in repetida.json()["mensaje"]
    assert (
        cliente.post(f"/api/ninos/{nino}/barreras", json=barrera(fuente="VISITA"), headers=USUARIO).status_code == 201
    )
    for malo, campo in (
        (barrera(tipo="NADA"), "tipo"),
        (barrera(tipo="OTRA"), "detalle"),
        (barrera(fecha="2026-12-01"), "fecha"),
        (barrera(fuente="OTRA_FUENTE"), "fuente"),
    ):
        r = cliente.post(f"/api/ninos/{nino}/barreras", json=malo, headers=USUARIO)
        assert r.status_code == 422 and campo in [e["campo"] for e in r.json()["errores"]]
    assert cliente.post("/api/ninos/no-existe/barreras", json=barrera(), headers=USUARIO).status_code == 404
    assert cliente.get("/api/ninos/no-existe/barreras").status_code == 404
    assert cliente.post(f"/api/ninos/{nino}/barreras", json={}, headers=USUARIO).status_code == 422


# --- HIST-4.4: alertas de barreras críticas ---------------------------------------------------------------------------


def test_cp372_la_alerta_de_barreras_criticas_trae_razones_prioridad_y_filtros(cliente):
    grave = registrar(cliente, **ESCENARIO["T"])
    media = registrar(cliente, **{**ESCENARIO["T"], "dni": "70000099", "comunidad": "Quilcas"})
    sana = registrar(cliente, **ESCENARIO["M"])
    assert cliente.get("/api/alertas/barreras").json() == []
    cliente.post(f"/api/ninos/{grave}/barreras", json=barrera(tipo="RECHAZO_TRATAMIENTO"), headers=USUARIO)
    cliente.post(f"/api/ninos/{media}/barreras", json=barrera(), headers=USUARIO)
    cliente.post(f"/api/ninos/{sana}/barreras", json=barrera(), headers=USUARIO)
    alertas = cliente.get("/api/alertas/barreras").json()
    assert [a["nino"]["id"] for a in alertas][0] == grave
    por_id = {a["nino"]["id"]: a for a in alertas}
    assert por_id[grave]["prioridad"] == "ALTA" and "BARRERA_GRAVE" in [r["codigo"] for r in por_id[grave]["razones"]]
    assert por_id[media]["prioridad"] == "MEDIA" and por_id[media]["razones"][0]["codigo"] == "ANEMIA_CONTROL_VENCIDO"
    assert por_id[grave]["barreras"][0]["tipo"] == "RECHAZO_TRATAMIENTO" and por_id[grave]["dias_control_vencido"] > 0
    assert por_id[grave]["nino"]["comunidad"] == "Llacuas" and por_id[grave]["ultima_clasificacion"] in {
        "MODERADA",
        "SEVERA",
    }
    assert sana not in por_id  # sin anemia moderada o severa una sola barrera no es crítica
    assert [a["nino"]["id"] for a in cliente.get("/api/alertas/barreras?comunidad=quilcas").json()] == [media]
    assert [a["nino"]["id"] for a in cliente.get("/api/alertas/barreras?prioridad=ALTA").json()] == [grave]
    r = cliente.get("/api/alertas/barreras?prioridad=BAJA")
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "prioridad"


def test_cp373_las_visitas_priorizadas_suman_el_componente_de_barreras_criticas(cliente):
    con = registrar(cliente, **ESCENARIO["T"])
    sin = registrar(cliente, **{**ESCENARIO["T"], "dni": "70000098", "comunidad": "Quilcas"})
    antes = {i["nino"]["id"]: i for i in cliente.get("/api/visitas/priorizadas").json()}
    assert len(antes[con]["componentes"]) == 4 and antes[con]["puntaje"] == antes[sin]["puntaje"]
    cliente.post(f"/api/ninos/{con}/barreras", json=barrera(tipo="EFECTOS_ADVERSOS_SUPLEMENTO"), headers=USUARIO)
    despues = {i["nino"]["id"]: i for i in cliente.get("/api/visitas/priorizadas").json()}
    assert [c["codigo"] for c in despues[con]["componentes"]][-1] == "BARRERA_CRITICA"
    assert (
        despues[con]["puntaje"] == pytest.approx(antes[con]["puntaje"] + 15.0)
        and despues[sin]["puntaje"] == antes[sin]["puntaje"]
    )
    assert cliente.get("/api/visitas/priorizadas").json()[0]["nino"]["id"] == con


# --- HIST-4.1: generar, listar y métricas -----------------------------------------------------------------------------


def test_cp374_generar_recordatorios_simulados_es_idempotente_y_enmascara_el_celular(cliente):
    registrar(cliente, **ESCENARIO["T"])
    primera = generar(cliente)
    assert (primera["fecha"], primera["enviados"], primera["fallidos"]) == ("2026-09-28", 3, 0)
    assert primera["candidatos"] == 3 and primera["omitidos_sin_contacto"] == 0 and primera["omitidos_ya_enviado"] == 0
    r = primera["recordatorios"][0]
    assert (r["canal"], r["estado"], r["simulado"], r["tipo"]) == ("SIMULADO", "ENVIADO_SIMULADO", True, "VENCIDO")
    assert (
        r["destino"] == "*****4321" and "987654321" not in json.dumps(primera) and "anemia" not in r["mensaje"].lower()
    )
    assert r["nino"]["nombre_completo"] == "Luz Mery Quispe Rojas" and r["respuesta"] is None
    segunda = generar(cliente)
    assert (segunda["enviados"], segunda["omitidos_ya_enviado"], segunda["recordatorios"]) == (0, 3, [])
    assert len(cliente.get("/api/recordatorios").json()) == 3


def guardar_con_evaluaciones(repo, nino):
    repo.guardar(nino)
    for evaluacion in nino.evaluaciones:
        repo.agregar_evaluacion(evaluacion)


def test_cp375_los_ninos_sin_celular_y_los_del_dataset_se_cuentan_como_sin_contacto(cliente):
    registrar(cliente, **ESCENARIO["T"])
    repo = cliente.app.state.repositorio
    dataset = nino_de(
        ESCENARIO_NACIMIENTO,
        [(ESCENARIO_EVALUACION, "MODERADA")],
        origen=OrigenDatos.DATASET_DIRESA_JUNIN,
        codigo_origen="DJ-00001",
        dni=None,
        nombres=None,
        apellidos=None,
        sexo=None,
        tutor_nombre=None,
        tutor_celular=None,
    )
    guardar_con_evaluaciones(repo, dataset)
    sin_celular = nino_de(
        ESCENARIO_NACIMIENTO, [(ESCENARIO_EVALUACION, "MODERADA")], dni="70000097", tutor_celular=None
    )
    guardar_con_evaluaciones(repo, sin_celular)
    r = generar(cliente)
    assert (r["enviados"], r["omitidos_sin_contacto"], r["candidatos"]) == (3, 6, 9)
    assert dataset.id not in {x["nino"]["id"] for x in r["recordatorios"]}


def test_cp376_generar_por_establecimiento(cliente):
    registrar(cliente, **ESCENARIO["T"])
    otro = cliente.post("/api/recordatorios/generar", json={"establecimiento": "Otro Puesto"}, headers=USUARIO).json()
    assert (otro["candidatos"], otro["enviados"]) == (0, 0)
    propio = cliente.post(
        "/api/recordatorios/generar", json={"establecimiento": "p. s. chongos alto"}, headers=USUARIO
    ).json()
    assert propio["enviados"] == 3


def test_cp377_listar_recordatorios_con_filtros_y_errores(cliente):
    nino = registrar(cliente, **ESCENARIO["T"])
    generar(cliente)
    todos = cliente.get("/api/recordatorios").json()
    assert len(todos) == 3 and {r["nino"]["id"] for r in todos} == {nino}
    assert len(cliente.get("/api/recordatorios?limite=2").json()) == 2
    assert len(cliente.get(f"/api/recordatorios?nino_id={nino}&estado=ENVIADO_SIMULADO&desde=2020-01-01").json()) == 3
    assert cliente.get("/api/recordatorios?estado=FALLIDO").json() == []
    assert cliente.get("/api/recordatorios?desde=2100-01-01").json() == []
    for consulta, campo in (("estado=RARO", "estado"), ("limite=0", "limite"), ("limite=1001", "limite")):
        r = cliente.get(f"/api/recordatorios?{consulta}")
        assert r.status_code == 422 and r.json()["errores"][0]["campo"] == campo


def test_cp378_metricas_de_recordatorios(cliente):
    registrar(cliente, **ESCENARIO["T"])
    vacias = cliente.get("/api/recordatorios/metricas").json()
    assert (vacias["total"], vacias["tasa_envio"], vacias["tasa_entrega"], vacias["por_canal"]) == (0, None, None, [])
    generar(cliente)
    m = cliente.get("/api/recordatorios/metricas").json()
    assert (m["total"], m["enviados"], m["simulados"], m["fallidos"]) == (3, 3, 3, 0)
    assert (m["tasa_envio"], m["tasa_entrega"], m["tasa_respuesta"]) == (1.0, None, 0.0)
    assert m["por_canal"][0]["canal"] == "SIMULADO" and m["por_canal"][0]["total"] == 3
    assert cliente.get("/api/recordatorios/metricas?desde=2100-01-01").json()["total"] == 0
    r = cliente.get("/api/recordatorios/metricas?desde=2026-10-01&hasta=2026-09-01")
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "desde"


# --- HIST-4.2: respuesta del tutor registrada por el personal ---------------------------------------------------------


def test_cp379_el_personal_registra_la_respuesta_del_tutor(cliente):
    registrar(cliente, **ESCENARIO["T"])
    uno, dos, tres = generar(cliente)["recordatorios"]
    r = cliente.post(f"/api/recordatorios/{uno['id']}/respuesta", json={"respuesta": "CONFIRMA"}, headers=USUARIO)
    assert r.status_code == 200, r.text
    cuerpo = r.json()
    recordatorio = cuerpo["recordatorio"]
    assert (recordatorio["respuesta"], recordatorio["origen_respuesta"], recordatorio["respondido_por"]) == (
        "CONFIRMA",
        "PERSONAL",
        "enf.rosa",
    )
    assert (
        cuerpo["barrera_id"] is None
        and cuerpo["barrera_sugerida"] is False
        and recordatorio["respondido_en"] is not None
    )
    r = cliente.post(
        f"/api/recordatorios/{dos['id']}/respuesta",
        json={"respuesta": "REPROGRAMAR", "fecha_reprogramada": "2026-10-10"},
        headers=USUARIO,
    )
    assert r.json()["recordatorio"]["fecha_reprogramada"] == "2026-10-10"
    m = cliente.get("/api/recordatorios/metricas").json()
    assert (m["con_respuesta"], m["confirmados"], m["reprogramados"], m["tasa_confirmacion"]) == (2, 1, 1, 0.3333)
    sugerida = cliente.post(
        f"/api/recordatorios/{tres['id']}/respuesta", json={"respuesta": "NO_PUEDE"}, headers=USUARIO
    ).json()
    assert sugerida["barrera_sugerida"] is True and sugerida["barrera_id"] is None


def test_cp380_no_puede_con_barrera_registra_la_barrera_con_la_fuente_respuesta_y_genera_alerta(cliente):
    nino = registrar(cliente, **ESCENARIO["T"])
    uno = generar(cliente)["recordatorios"][0]
    r = cliente.post(
        f"/api/recordatorios/{uno['id']}/respuesta",
        json={
            "respuesta": "NO_PUEDE",
            "barrera": {"tipo": "RECHAZO_TRATAMIENTO", "detalle": "No quiere darle el sulfato"},
        },
        headers=USUARIO,
    )
    assert r.status_code == 200 and r.json()["barrera_sugerida"] is False
    (b,) = cliente.get(f"/api/ninos/{nino}/barreras").json()
    assert (b["id"], b["fuente"], b["recordatorio_id"], b["fecha"]) == (
        r.json()["barrera_id"],
        "RESPUESTA_RECORDATORIO",
        uno["id"],
        "2026-09-28",
    )
    (alerta,) = cliente.get("/api/alertas/barreras").json()
    assert alerta["nino"]["id"] == nino and alerta["prioridad"] == "ALTA"


@pytest.mark.parametrize(
    "cuerpo, estado",
    [
        ({"respuesta": "TAL VEZ"}, 422),
        ({"respuesta": "REPROGRAMAR"}, 422),
        ({"respuesta": "REPROGRAMAR", "fecha_reprogramada": "2026-01-01"}, 422),
        ({"respuesta": "CONFIRMA", "barrera": {"tipo": "OLVIDO"}}, 422),
        ({"respuesta": "NO_PUEDE", "barrera": {"tipo": "OTRA"}}, 422),
        ({}, 422),
    ],
)
def test_cp381_respuestas_invalidas(cliente, cuerpo, estado):
    registrar(cliente, **ESCENARIO["T"])
    uno = generar(cliente)["recordatorios"][0]
    assert cliente.post(f"/api/recordatorios/{uno['id']}/respuesta", json=cuerpo, headers=USUARIO).status_code == estado
    assert all(r["respuesta"] is None for r in cliente.get("/api/recordatorios").json())


def test_cp382_respuesta_duplicada_409_e_inexistente_404(cliente):
    registrar(cliente, **ESCENARIO["T"])
    uno = generar(cliente)["recordatorios"][0]
    ruta = f"/api/recordatorios/{uno['id']}/respuesta"
    assert cliente.post(ruta, json={"respuesta": "CONFIRMA"}, headers=USUARIO).status_code == 200
    repetida = cliente.post(ruta, json={"respuesta": "NO_PUEDE"}, headers=USUARIO)
    assert repetida.status_code == 409 and "ya tiene una respuesta" in repetida.json()["mensaje"]
    assert (
        cliente.post(
            "/api/recordatorios/no-existe/respuesta", json={"respuesta": "CONFIRMA"}, headers=USUARIO
        ).status_code
        == 404
    )


# --- Webhook de WhatsApp ----------------------------------------------------------------------------------------------


def respuesta_de_meta(manejador=None):
    peticiones: list[httpx.Request] = []

    def transporte(peticion: httpx.Request) -> httpx.Response:
        peticiones.append(peticion)
        if manejador:
            return manejador(peticion)
        n = len(peticiones)
        return httpx.Response(200, json={"messages": [{"id": f"wamid.{n}"}]})

    return httpx.Client(transport=httpx.MockTransport(transporte)), peticiones


@pytest.fixture
def whatsapp(tmp_path, monkeypatch):
    """Aplicación con WhatsApp simulado por HTTP (MockTransport), secretos del webhook y respaldo por SMS."""
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", TOKEN_VERIFICACION)
    monkeypatch.setenv("WHATSAPP_APP_SECRET", SECRETO)

    def manejar(peticion):
        if "graph.facebook.com" in str(peticion.url):
            n = len([p for p in meta if "graph.facebook.com" in str(p.url)])
            return httpx.Response(200, json={"messages": [{"id": f"wamid.{n}"}]})
        return httpx.Response(200, json={"id": "sms-1"})

    http, meta = respuesta_de_meta(manejar)
    entorno = {"WHATSAPP_TOKEN": "tk", "WHATSAPP_PHONE_NUMBER_ID": "55", "SMS_API_URL": "https://sms.local/enviar"}
    app = crear_app(f"sqlite:///{tmp_path}/wa.db", reloj=RelojFijo(), notificador=crear_notificador(entorno, http))
    with TestClient(app) as c:
        yield c, meta
    app.state.repositorio.engine.dispose()


def firmado(cuerpo: dict, secreto=SECRETO):
    crudo = json.dumps(cuerpo).encode()
    return {
        "content": crudo,
        "headers": {"X-Hub-Signature-256": firmar(crudo, secreto), "Content-Type": "application/json"},
    }


def evento(estados=None, mensajes=None):
    return {"entry": [{"changes": [{"value": {"statuses": estados or [], "messages": mensajes or []}}]}]}


def test_cp383_con_whatsapp_configurado_los_mensajes_salen_por_la_api_simulada_y_quedan_enviados(whatsapp):
    c, meta = whatsapp
    registrar(c, **ESCENARIO["T"])
    r = generar(c)
    assert (r["enviados"], r["fallidos"]) == (3, 0) and len(meta) == 3
    uno = r["recordatorios"][0]
    assert (uno["canal"], uno["estado"], uno["simulado"]) == ("WHATSAPP", "ENVIADO", False)
    cuerpo = json.loads(meta[0].content)
    assert cuerpo["to"] == "51987654321" and cuerpo["template"]["name"] == "recordatorio_control"
    assert meta[0].headers["Authorization"] == "Bearer tk"
    m = c.get("/api/recordatorios/metricas").json()
    assert (m["simulados"], m["enviados"], m["tasa_entrega"]) == (0, 3, 0.0)


def test_cp384_si_whatsapp_falla_el_mensaje_se_reintenta_por_sms(tmp_path):
    def manejar(peticion):
        if "graph.facebook.com" in str(peticion.url):
            return httpx.Response(500, json={"error": {"code": 2, "message": "Servicio no disponible"}})
        return httpx.Response(200, json={"id": "sms-9"})

    http, peticiones = respuesta_de_meta(manejar)
    entorno = {"WHATSAPP_TOKEN": "tk", "WHATSAPP_PHONE_NUMBER_ID": "55", "SMS_API_URL": "https://sms.local/enviar"}
    app = crear_app(f"sqlite:///{tmp_path}/sms.db", reloj=RelojFijo(), notificador=crear_notificador(entorno, http))
    with TestClient(app) as c:
        registrar(c, **ESCENARIO["T"])
        r = generar(c)
        uno = r["recordatorios"][0]
        assert (r["enviados"], r["fallidos"]) == (3, 0) and (uno["canal"], uno["estado"]) == ("SMS", "ENVIADO")
        assert "WhatsApp: error 500" in uno["detalle"] and uno["detalle"].endswith("Se reintentó por SMS.")
        assert len(peticiones) == 6
        por_canal = {x["canal"]: x for x in c.get("/api/recordatorios/metricas").json()["por_canal"]}
        assert por_canal["SMS"]["total"] == 3
    app.state.repositorio.engine.dispose()


def test_cp385_si_fallan_ambos_canales_queda_fallido_y_se_reintenta_despues(tmp_path):
    estado = {"cae": True}

    def manejar(peticion):
        if estado["cae"]:
            return httpx.Response(503)
        return httpx.Response(200, json={"messages": [{"id": "wamid.ok"}]})

    http, _ = respuesta_de_meta(manejar)
    app = crear_app(
        f"sqlite:///{tmp_path}/f.db",
        reloj=RelojFijo(),
        notificador=crear_notificador({"WHATSAPP_TOKEN": "tk", "WHATSAPP_PHONE_NUMBER_ID": "55"}, http),
    )
    with TestClient(app) as c:
        registrar(c, **ESCENARIO["T"])
        r = generar(c)
        assert (r["enviados"], r["fallidos"]) == (0, 3)
        assert r["recordatorios"][0]["estado"] == "FALLIDO" and "503" in r["recordatorios"][0]["detalle"]
        estado["cae"] = False
        otra = generar(c)
        assert (otra["enviados"], otra["fallidos"], otra["omitidos_ya_enviado"]) == (3, 0, 0)
        assert {x["intentos"] for x in otra["recordatorios"]} == {2}
        assert len(c.get("/api/recordatorios").json()) == 3
    app.state.repositorio.engine.dispose()


def test_cp386_verificacion_del_webhook(whatsapp):
    c, _ = whatsapp
    ok = c.get(
        RUTA_WEBHOOK, params={"hub.mode": "subscribe", "hub.verify_token": TOKEN_VERIFICACION, "hub.challenge": "12345"}
    )
    assert ok.status_code == 200 and ok.text == "12345" and ok.headers["content-type"].startswith("text/plain")
    for params in (
        {"hub.mode": "subscribe", "hub.verify_token": "otro", "hub.challenge": "1"},
        {"hub.mode": "unsubscribe", "hub.verify_token": TOKEN_VERIFICACION, "hub.challenge": "1"},
        {"hub.mode": "subscribe", "hub.verify_token": TOKEN_VERIFICACION},
        {},
    ):
        assert c.get(RUTA_WEBHOOK, params=params).status_code == 403


def test_cp387_sin_token_configurado_la_verificacion_se_rechaza(cliente):
    r = cliente.get(RUTA_WEBHOOK, params={"hub.mode": "subscribe", "hub.verify_token": "", "hub.challenge": "1"})
    assert r.status_code == 403 and r.json()["mensaje"] == "Verificación rechazada."


def test_cp388_el_webhook_firmado_actualiza_estados_y_registra_respuestas(whatsapp):
    c, _ = whatsapp
    registrar(c, **ESCENARIO["T"])
    uno, dos, tres = generar(c)["recordatorios"]
    estados = evento(
        estados=[
            {"id": "wamid.1", "status": "delivered"},
            {"id": "wamid.1", "status": "read"},
            {"id": "wamid.2", "status": "failed", "errors": [{"title": "Número no válido"}]},
            {"id": "wamid.inexistente", "status": "read"},
        ]
    )
    r = c.post(RUTA_WEBHOOK, **firmado(estados))
    assert r.status_code == 200 and r.json() == {"estados_aplicados": 3, "respuestas_registradas": 0, "ignorados": 1}
    por_id = {x["id"]: x for x in c.get("/api/recordatorios").json()}
    assert por_id[uno["id"]]["estado"] == "LEIDO" and por_id[dos["id"]]["estado"] == "FALLIDO"
    assert por_id[dos["id"]]["detalle"] == "Número no válido" and por_id[tres["id"]]["estado"] == "ENVIADO"
    respuestas = evento(
        mensajes=[
            {"from": "51987654321", "text": {"body": "1"}, "context": {"id": "wamid.3"}},
            {"from": "51987654321", "type": "button", "button": {"payload": "No puedo"}},
            {"from": "51999999999", "text": {"body": "1"}},
            {"from": "51987654321", "text": {"body": "hola"}},
        ]
    )
    r = c.post(RUTA_WEBHOOK, **firmado(respuestas))
    assert r.json() == {"estados_aplicados": 0, "respuestas_registradas": 2, "ignorados": 2}
    por_id = {x["id"]: x for x in c.get("/api/recordatorios").json()}
    assert (
        por_id[tres["id"]]["respuesta"],
        por_id[tres["id"]]["origen_respuesta"],
        por_id[tres["id"]]["respondido_por"],
    ) == ("CONFIRMA", "WHATSAPP", "whatsapp")
    sin_contexto = [x for x in por_id.values() if x["respuesta"] == "NO_PUEDE"]
    assert len(sin_contexto) == 1 and sin_contexto[0]["id"] != tres["id"]
    m = c.get("/api/recordatorios/metricas").json()
    assert (m["con_respuesta"], m["confirmados"], m["no_pueden"], m["entregados"], m["leidos"]) == (2, 1, 1, 1, 1)


def test_cp389_la_firma_invalida_o_ausente_se_rechaza_sin_cambiar_nada(whatsapp):
    c, _ = whatsapp
    registrar(c, **ESCENARIO["T"])
    generar(c)
    cuerpo = evento(estados=[{"id": "wamid.1", "status": "read"}])
    crudo = json.dumps(cuerpo).encode()
    for cabeceras in ({}, {"X-Hub-Signature-256": "sha256=00"}, {"X-Hub-Signature-256": firmar(crudo, "otro")}):
        r = c.post(RUTA_WEBHOOK, content=crudo, headers=cabeceras)
        assert r.status_code == 403 and r.json()["mensaje"] == "La firma de la notificación no es válida."
    assert c.get("/api/recordatorios/metricas").json()["leidos"] == 0


def test_cp390_un_cuerpo_que_no_es_json_firmado_es_422(whatsapp):
    c, _ = whatsapp
    crudo = b"esto no es json"
    r = c.post(RUTA_WEBHOOK, content=crudo, headers={"X-Hub-Signature-256": firmar(crudo, SECRETO)})
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "cuerpo"


def test_cp391_sin_secreto_configurado_se_acepta_sin_firma_y_se_ignora_lo_irreconocible(cliente):
    registrar(cliente, **ESCENARIO["T"])
    uno = generar(cliente)["recordatorios"][0]
    r = cliente.post(RUTA_WEBHOOK, json=evento(estados=[{"id": uno["id"], "status": "read"}]))
    assert r.status_code == 200 and r.json() == {"estados_aplicados": 0, "respuestas_registradas": 0, "ignorados": 1}
    assert cliente.post(RUTA_WEBHOOK, json={"object": "whatsapp_business_account"}).json()["ignorados"] == 0
    assert cliente.post(RUTA_WEBHOOK, json=[1, 2]).status_code == 200


# --- Sincronización de barreras ---------------------------------------------------------------------------------------


def uid():
    return str(uuid.uuid4())


def op_barrera(datos, nino_ref, minuto=0):
    return {
        "id_operacion": uid(),
        "tipo": "REGISTRAR_BARRERA",
        "id_dispositivo": "tableta-posta-1",
        "fecha_local": f"2026-09-27T08:{minuto:02d}:00-05:00",
        "datos": datos,
        "nino_ref": nino_ref,
    }


def sincronizar(cliente, *operaciones):
    r = cliente.post("/api/sincronizacion", json={"operaciones": list(operaciones)}, headers=USUARIO)
    assert r.status_code == 200, r.text
    return r.json()["resultados"]


def test_cp392_una_barrera_registrada_sin_conexion_se_sincroniza_una_sola_vez(cliente):
    nino = registrar(cliente, **ESCENARIO["T"])
    operacion = op_barrera(
        {"tipo": "OLVIDO", "detalle": None, "fuente": "PERSONAL", "fecha": "2026-09-26"}, {"id": nino}
    )
    (r,) = sincronizar(cliente, operacion)
    assert r["resultado"] == "APLICADA"
    (b,) = cliente.get(f"/api/ninos/{nino}/barreras").json()
    assert (r["id_recurso"], b["tipo"], b["registrado_por"]) == (b["id"], "OLVIDO", "enf.rosa")
    (reenvio,) = sincronizar(cliente, operacion)
    assert reenvio["resultado"] == "DUPLICADA" and reenvio["id_recurso"] == b["id"]
    # otra operación con el mismo hecho (mismo tipo, fecha y fuente) se mapea a la barrera existente
    (igual,) = sincronizar(cliente, op_barrera(operacion["datos"], {"id": nino}, 5))
    assert igual["resultado"] == "DUPLICADA" and igual["id_recurso"] == b["id"]
    assert len(cliente.get(f"/api/ninos/{nino}/barreras").json()) == 1


def test_cp393_una_barrera_invalida_se_rechaza_y_la_de_un_nino_inexistente_tambien(cliente):
    nino = registrar(cliente, **ESCENARIO["T"])
    mala = op_barrera({"tipo": "OTRA", "fuente": "PERSONAL", "fecha": "2026-09-26"}, {"id": nino})
    futura = op_barrera({"tipo": "OLVIDO", "fecha": "2026-12-01"}, {"id": nino}, 1)
    sin_nino = op_barrera({"tipo": "OLVIDO"}, {"id": "no-existe"}, 2)
    sin_tipo = op_barrera({"detalle": "x"}, {"id": nino}, 3)
    resultados = sincronizar(cliente, mala, futura, sin_nino, sin_tipo)
    assert [x["resultado"] for x in resultados] == ["RECHAZADA"] * 4
    assert cliente.get(f"/api/ninos/{nino}/barreras").json() == []


def test_cp394_la_barrera_de_un_nino_nuevo_del_mismo_lote_usa_su_id_cliente(cliente):
    from tests.integracion.test_api_inc3 import datos_registro

    registro = {
        "id_operacion": uid(),
        "tipo": "REGISTRAR_NINO",
        "id_dispositivo": "tableta-posta-1",
        "fecha_local": "2026-09-27T08:00:00-05:00",
        "id_cliente": "tmp-9",
        "datos": datos_registro(dni="72000009"),
    }
    barrera_op = op_barrera({"tipo": "TRANSPORTE", "fecha": "2026-09-27"}, {"id_cliente": "tmp-9"}, 1)
    resultados = sincronizar(cliente, registro, barrera_op)
    assert [x["resultado"] for x in resultados] == ["APLICADA", "APLICADA"]
    nino = cliente.get("/api/ninos/dni/72000009").json()["id"]
    assert len(cliente.get(f"/api/ninos/{nino}/barreras").json()) == 1


# --- Autenticación en modo Supabase -----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "metodo, ruta, cuerpo",
    [
        ("get", "/api/alertas/barreras", None),
        ("get", "/api/ninos/x/barreras", None),
        ("post", "/api/ninos/x/barreras", barrera()),
        ("post", "/api/recordatorios/generar", None),
        ("get", "/api/recordatorios", None),
        ("get", "/api/recordatorios/metricas", None),
        ("post", "/api/recordatorios/x/respuesta", {"respuesta": "CONFIRMA"}),
    ],
)
def test_cp395_los_endpoints_del_incremento_4_exigen_sesion(auth_cliente, metodo, ruta, cuerpo):  # noqa: F811
    c, _, _ = auth_cliente
    r = getattr(c, metodo)(ruta, **({"json": cuerpo} if cuerpo is not None else {}), headers=CSRF)
    assert r.status_code == 401 and r.headers["Cache-Control"] == "no-store"


def test_cp396_el_webhook_es_publico_sin_sesion_ni_csrf_pero_exige_la_firma(auth_cliente, monkeypatch):  # noqa: F811
    c, _, _ = auth_cliente
    cuerpo = evento()
    assert c.post(RUTA_WEBHOOK, json=cuerpo).status_code == 200  # sin secreto configurado, sin sesión y sin CSRF
    c.app.state.recordatorios.webhook = ConfiguracionWebhook(TOKEN_VERIFICACION, SECRETO)
    crudo = json.dumps(cuerpo).encode()
    assert c.post(RUTA_WEBHOOK, content=crudo).status_code == 403
    assert (
        c.post(RUTA_WEBHOOK, content=crudo, headers={"X-Hub-Signature-256": firmar(crudo, SECRETO)}).status_code == 200
    )
    ok = c.get(
        RUTA_WEBHOOK, params={"hub.mode": "subscribe", "hub.verify_token": TOKEN_VERIFICACION, "hub.challenge": "7"}
    )
    assert ok.status_code == 200 and ok.text == "7"


def test_cp397_con_sesion_las_acciones_usan_el_usuario_verificado_y_exigen_csrf(auth_cliente):  # noqa: F811
    c, _, _ = auth_cliente
    ingresar(c)
    nino = c.post("/api/ninos", json=cuerpo_registro(), headers=CSRF)
    assert nino.status_code == 201
    nino_id = nino.json()["id"]
    assert c.post(f"/api/ninos/{nino_id}/barreras", json=barrera()).status_code == 403  # sin X-CSRF-Protection
    r = c.post(f"/api/ninos/{nino_id}/barreras", json=barrera(), headers={**CSRF, "X-Usuario": "suplantado"})
    assert r.status_code == 201 and r.json()["registrado_por"] == USER["id"]
    assert c.post("/api/recordatorios/generar", headers=CSRF).status_code == 200
    assert c.get("/api/recordatorios").json()[0]["nino"]["id"] == nino_id
