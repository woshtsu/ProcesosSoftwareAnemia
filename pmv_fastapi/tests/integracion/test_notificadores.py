"""CP-358 a CP-369: notificadores de WhatsApp Cloud y SMS, respaldo y selección por configuración (ADR-014).

Todas las pruebas usan ``httpx.MockTransport``: no se hace ninguna llamada de red real a Meta ni a proveedores SMS.
"""

import json

import httpx
import pytest

from app.adapters.outbound.notificaciones import (
    NotificadorConRespaldo,
    NotificadorSimulado,
    NotificadorSMS,
    NotificadorWhatsAppCloud,
    crear_notificador,
)
from app.domain.model.notificacion import CanalEnvio, EstadoRecordatorio, MensajeSaliente

MENSAJE = MensajeSaliente(
    destino="987654321",
    texto="Hola, le recordamos el control",
    plantilla="recordatorio_control",
    parametros=("Luz", "control de hemoglobina", "P. S. Chongos Alto", "hoy"),
    referencia="rec-1",
)


def cliente(manejador):
    """Cliente httpx cuyo transporte es un simulacro: registra las peticiones y responde con ``manejador``."""
    peticiones: list[httpx.Request] = []

    def transporte(peticion: httpx.Request) -> httpx.Response:
        peticiones.append(peticion)
        return manejador(peticion)

    return httpx.Client(transport=httpx.MockTransport(transporte)), peticiones


def responde(codigo, cuerpo=None):
    return lambda _: (
        httpx.Response(codigo, json=cuerpo) if cuerpo is not None else httpx.Response(codigo, text="no json")
    )


def cae(_):
    raise httpx.ConnectError("sin red")


OK_WHATSAPP = {"messaging_product": "whatsapp", "messages": [{"id": "wamid.ABC"}]}


# --- WhatsApp Cloud API -----------------------------------------------------------------------------------------------


def test_cp358_whatsapp_envia_una_plantilla_con_los_parametros_y_devuelve_el_id():
    http, peticiones = cliente(responde(200, OK_WHATSAPP))
    n = NotificadorWhatsAppCloud("token-de-prueba", "1234567890", cliente=http)
    r = n.enviar(MENSAJE)
    assert (r.exito, r.canal, r.estado, r.id_externo, r.error) == (
        True,
        CanalEnvio.WHATSAPP,
        EstadoRecordatorio.ENVIADO,
        "wamid.ABC",
        None,
    )
    (peticion,) = peticiones
    assert peticion.method == "POST" and str(peticion.url) == "https://graph.facebook.com/v21.0/1234567890/messages"
    assert peticion.headers["Authorization"] == "Bearer token-de-prueba"
    cuerpo = json.loads(peticion.content)
    assert cuerpo["to"] == "51987654321" and cuerpo["type"] == "template" and cuerpo["messaging_product"] == "whatsapp"
    plantilla = cuerpo["template"]
    assert (plantilla["name"], plantilla["language"]["code"]) == ("recordatorio_control", "es")
    assert [p["text"] for p in plantilla["components"][0]["parameters"]] == list(MENSAJE.parametros)


def test_cp359_la_plantilla_el_idioma_la_version_y_la_url_son_configurables():
    http, peticiones = cliente(responde(200, OK_WHATSAPP))
    n = NotificadorWhatsAppCloud(
        "t",
        "55",
        plantilla="mi_plantilla",
        idioma="es_PE",
        version_api="v22.0",
        cliente=http,
        url_base="https://prueba.local/",
    )
    n.enviar(MENSAJE)
    assert str(peticiones[0].url) == "https://prueba.local/v22.0/55/messages"
    cuerpo = json.loads(peticiones[0].content)["template"]
    assert (cuerpo["name"], cuerpo["language"]["code"]) == ("mi_plantilla", "es_PE")
    sin_plantilla = NotificadorWhatsAppCloud("t", "55", plantilla="", cliente=http)
    sin_plantilla.enviar(MENSAJE)
    assert json.loads(peticiones[1].content)["template"]["name"] == "recordatorio_control"


def test_cp360_whatsapp_rechazado_informa_el_codigo_y_el_motivo_sin_exponer_el_token():
    error = {"error": {"code": 131030, "message": "Recipient phone number not in allowed list"}}
    http, _ = cliente(responde(400, error))
    r = NotificadorWhatsAppCloud("token-secreto", "55", cliente=http).enviar(MENSAJE)
    assert (r.exito, r.estado, r.canal, r.id_externo) == (False, EstadoRecordatorio.FALLIDO, CanalEnvio.WHATSAPP, None)
    assert "400" in r.error and "131030" in r.error and "token-secreto" not in r.error
    sin_json, _ = cliente(responde(500))
    assert NotificadorWhatsAppCloud("t", "55", cliente=sin_json).enviar(MENSAJE).error == "WhatsApp: error 500."
    otro_json, _ = cliente(responde(502, ["raro"]))
    assert NotificadorWhatsAppCloud("t", "55", cliente=otro_json).enviar(MENSAJE).error == "WhatsApp: error 502."


@pytest.mark.parametrize(
    "cuerpo", [{"messages": []}, {}, {"messages": [{"sin_id": 1}]}, {"messages": ["x"]}, ["lista"]]
)
def test_cp361_whatsapp_con_respuesta_2xx_sin_identificador_es_una_falla(cuerpo):
    http, _ = cliente(responde(200, cuerpo))
    r = NotificadorWhatsAppCloud("t", "55", cliente=http).enviar(MENSAJE)
    assert r.exito is False and "identificador" in r.error


def test_cp361_whatsapp_sin_conexion_o_con_cuerpo_no_json_es_una_falla():
    http, _ = cliente(cae)
    r = NotificadorWhatsAppCloud("t", "55", cliente=http).enviar(MENSAJE)
    assert (r.exito, r.estado) == (False, EstadoRecordatorio.FALLIDO) and "ConnectError" in r.error
    sin_json, _ = cliente(responde(200))
    assert NotificadorWhatsAppCloud("t", "55", cliente=sin_json).enviar(MENSAJE).exito is False


# --- SMS ---------------------------------------------------------------------------------------------------------------


def test_cp362_sms_sin_url_es_simulado_y_no_hace_peticiones():
    http, peticiones = cliente(cae)
    n = NotificadorSMS(cliente=http)
    r = n.enviar(MENSAJE)
    assert n.simulado is True and peticiones == []
    assert (r.exito, r.canal, r.estado) == (True, CanalEnvio.SMS, EstadoRecordatorio.ENVIADO_SIMULADO)
    assert r.id_externo.startswith("sim-sms-")


def test_cp363_sms_con_proveedor_envia_el_texto_y_toma_el_id_de_la_respuesta():
    http, peticiones = cliente(responde(201, {"message_id": 77}))
    n = NotificadorSMS("https://sms.local/enviar", "tok-sms", "ANEMIA", cliente=http)
    r = n.enviar(MENSAJE)
    assert (r.exito, r.canal, r.estado, r.id_externo) == (True, CanalEnvio.SMS, EstadoRecordatorio.ENVIADO, "77")
    assert n.simulado is False
    assert json.loads(peticiones[0].content) == {"to": "+51987654321", "from": "ANEMIA", "message": MENSAJE.texto}
    assert peticiones[0].headers["Authorization"] == "Bearer tok-sms"
    sin_id, _ = cliente(responde(200, {"ok": True}))
    assert NotificadorSMS("https://sms.local", cliente=sin_id).enviar(MENSAJE).id_externo is None
    lista, _ = cliente(responde(200, ["x"]))
    assert NotificadorSMS("https://sms.local", cliente=lista).enviar(MENSAJE).exito is True
    sin_json, _ = cliente(responde(200))
    assert NotificadorSMS("https://sms.local", cliente=sin_json).enviar(MENSAJE).exito is True


def test_cp364_sms_sin_token_no_envia_cabecera_de_autorizacion():
    http, peticiones = cliente(responde(200, {"id": "a"}))
    NotificadorSMS("https://sms.local", cliente=http).enviar(MENSAJE)
    assert "Authorization" not in peticiones[0].headers


def test_cp365_sms_rechazado_o_sin_conexion_es_una_falla():
    http, _ = cliente(responde(503, {"error": "x"}))
    r = NotificadorSMS("https://sms.local", cliente=http).enviar(MENSAJE)
    assert (r.exito, r.estado, r.error) == (False, EstadoRecordatorio.FALLIDO, "SMS: error 503.")
    caido, _ = cliente(cae)
    assert "ConnectError" in NotificadorSMS("https://sms.local", cliente=caido).enviar(MENSAJE).error


# --- Respaldo y selección ---------------------------------------------------------------------------------------------


def test_cp366_el_respaldo_solo_se_usa_si_el_principal_falla_y_conserva_el_motivo():
    ok_http, ok_peticiones = cliente(responde(200, OK_WHATSAPP))
    sms_http, sms_peticiones = cliente(responde(200, {"id": "s1"}))
    combinado = NotificadorConRespaldo(
        NotificadorWhatsAppCloud("t", "55", cliente=ok_http), NotificadorSMS("https://sms.local", cliente=sms_http)
    )
    r = combinado.enviar(MENSAJE)
    assert (r.canal, r.id_externo, r.error) == (CanalEnvio.WHATSAPP, "wamid.ABC", None) and sms_peticiones == []
    caido_http, _ = cliente(responde(500, {"error": {"code": 1, "message": "interno"}}))
    cae_whatsapp = NotificadorConRespaldo(
        NotificadorWhatsAppCloud("t", "55", cliente=caido_http), NotificadorSMS("https://sms.local", cliente=sms_http)
    )
    r = cae_whatsapp.enviar(MENSAJE)
    assert (r.exito, r.canal, r.estado, r.id_externo) == (True, CanalEnvio.SMS, EstadoRecordatorio.ENVIADO, "s1")
    assert (
        "WhatsApp: error 500" in r.error
        and r.error.endswith("Se reintentó por SMS.")
        and len(sms_peticiones) == 1
        and len(ok_peticiones) == 1
    )
    sms_caido, _ = cliente(responde(500, {}))
    ambos = NotificadorConRespaldo(
        NotificadorWhatsAppCloud("t", "55", cliente=caido_http), NotificadorSMS("https://sms.local", cliente=sms_caido)
    ).enviar(MENSAJE)
    assert ambos.exito is False and ambos.canal == CanalEnvio.SMS
    assert "WhatsApp: error 500" in ambos.error and "SMS: error 500." in ambos.error


def test_cp367_sin_configuracion_el_notificador_es_simulado_y_envia_sin_red():
    for entorno in (
        {},
        {"WHATSAPP_TOKEN": "t"},
        {"WHATSAPP_PHONE_NUMBER_ID": "55"},
        {"WHATSAPP_TOKEN": " ", "WHATSAPP_PHONE_NUMBER_ID": " "},
    ):
        n = crear_notificador(entorno)
        assert isinstance(n, NotificadorSimulado)
    r = NotificadorSimulado().enviar(MENSAJE)
    assert (r.exito, r.canal, r.estado) == (True, CanalEnvio.SIMULADO, EstadoRecordatorio.ENVIADO_SIMULADO)
    assert r.id_externo.startswith("sim-") and r.id_externo != NotificadorSimulado().enviar(MENSAJE).id_externo


def test_cp368_con_credenciales_se_usa_whatsapp_y_con_url_sms_se_agrega_el_respaldo():
    http, peticiones = cliente(responde(200, OK_WHATSAPP))
    solo = crear_notificador({"WHATSAPP_TOKEN": "t", "WHATSAPP_PHONE_NUMBER_ID": "55"}, http)
    assert (
        isinstance(solo, NotificadorWhatsAppCloud) and solo.plantilla == "recordatorio_control" and solo.idioma == "es"
    )
    solo.enviar(MENSAJE)
    assert str(peticiones[0].url) == "https://graph.facebook.com/v21.0/55/messages"
    entorno = {
        "WHATSAPP_TOKEN": "t",
        "WHATSAPP_PHONE_NUMBER_ID": "55",
        "WHATSAPP_PLANTILLA": "otra",
        "WHATSAPP_IDIOMA": "es_PE",
        "WHATSAPP_API_VERSION": "v22.0",
        "SMS_API_URL": "https://sms.local/x",
        "SMS_API_TOKEN": "ts",
        "SMS_REMITENTE": "DIRESA",
    }
    combinado = crear_notificador(entorno, http)
    assert isinstance(combinado, NotificadorConRespaldo)
    assert (combinado.principal.plantilla, combinado.principal.idioma) == ("otra", "es_PE")
    assert "v22.0" in combinado.principal.url
    assert (combinado.respaldo.url, combinado.respaldo.token, combinado.respaldo.remitente) == (
        "https://sms.local/x",
        "ts",
        "DIRESA",
    )


def test_cp369_los_notificadores_sin_cliente_propio_crean_uno_pero_no_envian_nada_al_construirse():
    assert isinstance(NotificadorWhatsAppCloud("t", "55").cliente, httpx.Client)
    assert isinstance(NotificadorSMS("https://sms.local").cliente, httpx.Client)
