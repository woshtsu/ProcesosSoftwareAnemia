"""CP-327 a CP-357: recordatorios de control y respuesta del tutor (HIST-4.1 y HIST-4.2, ADR-014). Reglas de dominio puro
y casos de uso con el repositorio en memoria y un notificador de prueba (nunca hay red)."""

import json
from datetime import date, timedelta

import pytest

from app.adapters.outbound.notificaciones.simulado import NotificadorSimulado
from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria
from app.application.servicio_barreras import ServicioBarreras
from app.application.servicio_recordatorios import ServicioRecordatorios
from app.domain.model.agenda import ControlProgramado, EstadoControl, TipoControl
from app.domain.model.errores import (
    ConflictoRecordatorio,
    ConflictoRespuesta,
    ErrorValidacion,
    FirmaInvalida,
    NoEncontrado,
    WebhookNoConfigurado,
)
from app.domain.model.notificacion import (
    CanalEnvio,
    ConfiguracionWebhook,
    EstadoRecordatorio,
    EventoEstado,
    EventosWebhook,
    MensajeEntrante,
    MensajeSaliente,
    OrigenRespuesta,
    Recordatorio,
    RespuestaTutor,
    ResultadoEnvio,
    TipoRecordatorio,
)
from app.domain.model.origen import OrigenDatos
from app.domain.service.agenda import generar_agenda
from app.domain.service.notificaciones import (
    PLANTILLA_WHATSAPP,
    REGLAS_RECORDATORIO_V1,
    ReglasRecordatorio,
    avanzar_estado,
    calcular_metricas,
    celular_de_whatsapp,
    extraer_eventos,
    fecha_sugerida,
    firma_valida,
    firmar,
    interpretar_respuesta,
    parametros_mensaje,
    redactar_mensaje,
    seleccionar_controles,
    tiene_contacto,
    tipo_de_recordatorio,
    validar_respuesta,
    verificacion_valida,
)
from tests.conftest import HOY, RelojFijo, nino_de

NACIMIENTO = date(2025, 9, 1)
DIAGNOSTICO = (date(2026, 7, 1), "MODERADA")
E = EstadoRecordatorio


def control(estado=EstadoControl.PENDIENTE, programada=HOY + timedelta(days=10), tipo=TipoControl.TAMIZAJE_EDAD, **kw):
    base = dict(
        codigo="DHx",
        tipo=tipo,
        fecha_programada=programada,
        fecha_limite=programada + timedelta(days=30),
        estado=estado,
        dias_vencido=None,
        evaluacion_id=None,
        descripcion="Dosaje",
        fecha_inicio_ventana=programada - timedelta(days=15),
    )
    return ControlProgramado(**{**base, **kw})


# --- Selección --------------------------------------------------------------------------------------------------------


def test_cp327_el_tipo_de_recordatorio_depende_del_estado_y_de_la_fecha_del_control():
    r = REGLAS_RECORDATORIO_V1
    assert (
        tipo_de_recordatorio(control(EstadoControl.VENCIDO, HOY - timedelta(days=40)), HOY, r)
        == TipoRecordatorio.VENCIDO
    )
    assert tipo_de_recordatorio(control(programada=HOY), HOY, r) == TipoRecordatorio.CITA_DEL_DIA
    for estado in (EstadoControl.CUMPLIDO, EstadoControl.CERRADO_RECUPERADO):
        assert tipo_de_recordatorio(control(estado, HOY), HOY, r) is None


def test_cp328_la_ventana_abre_a_los_3_dias_pero_no_a_los_4():
    r = REGLAS_RECORDATORIO_V1
    tres = control(programada=HOY + timedelta(days=18), fecha_inicio_ventana=HOY + timedelta(days=3))
    cuatro = control(programada=HOY + timedelta(days=19), fecha_inicio_ventana=HOY + timedelta(days=4))
    abierta = control(programada=HOY + timedelta(days=1), fecha_inicio_ventana=HOY - timedelta(days=14))
    assert tipo_de_recordatorio(tres, HOY, r) == TipoRecordatorio.PROXIMO
    assert tipo_de_recordatorio(cuatro, HOY, r) is None
    assert tipo_de_recordatorio(abierta, HOY, r) == TipoRecordatorio.PROXIMO
    assert tipo_de_recordatorio(cuatro, HOY, ReglasRecordatorio("X", dias_anticipacion=4)) == TipoRecordatorio.PROXIMO


def test_cp329_se_seleccionan_los_controles_de_la_agenda_en_su_orden():
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    elegidos = seleccionar_controles(generar_agenda(nino, HOY), HOY)
    assert [(c.codigo, t) for c, t in elegidos] == [
        ("C1M", TipoRecordatorio.VENCIDO),
        ("DHc2", TipoRecordatorio.PROXIMO),
        ("C3M", TipoRecordatorio.PROXIMO),
    ]
    con_alta = nino_de(NACIMIENTO, [DIAGNOSTICO], estado="ALTA")
    assert seleccionar_controles(generar_agenda(con_alta, HOY), HOY) == []


def test_cp330_solo_los_ninos_del_sistema_con_celular_valido_tienen_contacto():
    assert tiene_contacto(nino_de(NACIMIENTO)) is True
    assert tiene_contacto(nino_de(NACIMIENTO, tutor_celular=None)) is False
    assert tiene_contacto(nino_de(NACIMIENTO, tutor_celular="12345")) is False
    assert tiene_contacto(nino_de(NACIMIENTO, tutor_celular="887654321")) is False
    dataset = nino_de(
        NACIMIENTO, origen=OrigenDatos.DATASET_DIRESA_JUNIN, codigo_origen="DJ-1", tutor_celular="987654321"
    )
    assert tiene_contacto(dataset) is False  # el dataset nunca tiene contacto aunque la fila lo trajera


def test_cp331_el_mensaje_no_incluye_diagnostico_y_usa_la_fecha_sugerida():
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO], nombres=" Luz Mery ")
    proximo = control(programada=HOY + timedelta(days=2), tipo=TipoControl.CONTROL_TRATAMIENTO)
    parametros = parametros_mensaje(nino, proximo, TipoRecordatorio.PROXIMO, HOY)
    assert parametros == ("Luz Mery", "control de seguimiento", "P. S. Chongos Alto", "30/09/2026")
    texto = redactar_mensaje(parametros)
    assert "Luz Mery" in texto and "30/09/2026" in texto and "1 = Confirmo" in texto
    for prohibida in ("anemia", "MODERADA", "hemoglobina", "tratamiento"):
        assert prohibida not in texto
    assert parametros_mensaje(nino, control(), TipoRecordatorio.PROXIMO, HOY)[1] == "control de hemoglobina"
    assert PLANTILLA_WHATSAPP == "recordatorio_control"


def test_cp332_fecha_sugerida_hoy_futura_o_lo_antes_posible():
    assert fecha_sugerida(control(programada=HOY), TipoRecordatorio.CITA_DEL_DIA, HOY) == "hoy"
    assert fecha_sugerida(control(programada=HOY - timedelta(days=3)), TipoRecordatorio.PROXIMO, HOY) == "hoy"
    assert fecha_sugerida(control(programada=HOY + timedelta(days=5)), TipoRecordatorio.PROXIMO, HOY) == "03/10/2026"
    assert (
        fecha_sugerida(control(programada=HOY - timedelta(days=60)), TipoRecordatorio.VENCIDO, HOY)
        == "lo antes posible"
    )


# --- Respuesta del tutor ----------------------------------------------------------------------------------------------


def test_cp333_validacion_de_la_respuesta():
    assert validar_respuesta({"respuesta": "CONFIRMA"}, HOY) == []
    assert validar_respuesta({"respuesta": "NO_PUEDE", "barrera": {"tipo": "OLVIDO"}}, HOY) == []
    assert validar_respuesta({"respuesta": "REPROGRAMAR", "fecha_reprogramada": HOY}, HOY) == []
    assert validar_respuesta({"respuesta": "REPROGRAMAR", "fecha_reprogramada": HOY + timedelta(days=90)}, HOY) == []
    assert validar_respuesta({"respuesta": "REPROGRAMAR"}, HOY, exigir_fecha=False) == []


@pytest.mark.parametrize(
    "datos, campo",
    [
        ({"respuesta": "TAL VEZ"}, "respuesta"),
        ({}, "respuesta"),
        ({"respuesta": "REPROGRAMAR"}, "fecha_reprogramada"),
        ({"respuesta": "REPROGRAMAR", "fecha_reprogramada": "2026-10-01"}, "fecha_reprogramada"),
        ({"respuesta": "REPROGRAMAR", "fecha_reprogramada": HOY - timedelta(days=1)}, "fecha_reprogramada"),
        ({"respuesta": "REPROGRAMAR", "fecha_reprogramada": HOY + timedelta(days=91)}, "fecha_reprogramada"),
        ({"respuesta": "CONFIRMA", "fecha_reprogramada": HOY}, "fecha_reprogramada"),
        ({"respuesta": "CONFIRMA", "barrera": {"tipo": "OLVIDO"}}, "barrera"),
    ],
)
def test_cp334_respuestas_invalidas(datos, campo):
    assert campo in [e.campo for e in validar_respuesta(datos, HOY)]


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("1", (RespuestaTutor.CONFIRMA, None)),
        (" Sí ", (RespuestaTutor.CONFIRMA, None)),
        ("CONFIRMO", (RespuestaTutor.CONFIRMA, None)),
        ("asistiré", (RespuestaTutor.CONFIRMA, None)),
        ("2", (RespuestaTutor.NO_PUEDE, None)),
        ("No puedo", (RespuestaTutor.NO_PUEDE, None)),
        ("NO_PUEDE", (RespuestaTutor.NO_PUEDE, None)),
        ("3", (RespuestaTutor.REPROGRAMAR, None)),
        ("Reprogramar", (RespuestaTutor.REPROGRAMAR, None)),
        ("reprogramar 05/10/2026", (RespuestaTutor.REPROGRAMAR, date(2026, 10, 5))),
        ("5-10-2026", (RespuestaTutor.REPROGRAMAR, date(2026, 10, 5))),
        ("para 5/10/2026", (RespuestaTutor.REPROGRAMAR, date(2026, 10, 5))),
        ("REPROGRAMAR_31/02/2026", (RespuestaTutor.REPROGRAMAR, None)),
        ("hola, buenos días", (None, None)),
        ("", (None, None)),
        ("31/02/2026 gracias", (None, None)),
    ],
)
def test_cp335_se_interpreta_el_texto_de_la_respuesta(texto, esperado):
    assert interpretar_respuesta(texto) == esperado


# --- Webhook ----------------------------------------------------------------------------------------------------------


def test_cp336_firma_y_verificacion_del_webhook():
    cuerpo = b'{"entry": []}'
    firma = firmar(cuerpo, "secreto")
    assert firma.startswith("sha256=") and firma_valida(cuerpo, firma, "secreto") is True
    assert firma_valida(cuerpo, firma, "otro") is False and firma_valida(cuerpo + b" ", firma, "secreto") is False
    assert firma_valida(cuerpo, None, "secreto") is False and firma_valida(cuerpo, "md5=abc", "secreto") is False
    assert verificacion_valida("subscribe", "tok", "tok") is True
    assert (
        verificacion_valida("subscribe", "mal", "tok") is False and verificacion_valida("otro", "tok", "tok") is False
    )
    assert verificacion_valida("subscribe", None, "tok") is False
    assert verificacion_valida("subscribe", "", "") is False  # sin token configurado nunca se verifica


def test_cp337_celular_de_whatsapp():
    assert celular_de_whatsapp("51987654321") == "987654321"
    assert celular_de_whatsapp("+51 987 654 321") == "987654321"
    assert celular_de_whatsapp("987654321") == "987654321"
    for malo in ("5198765", "51887654321", "34612345678", None, 987654321, ""):
        assert celular_de_whatsapp(malo) is None


def payload(estados=None, mensajes=None):
    return {"entry": [{"changes": [{"value": {"statuses": estados or [], "messages": mensajes or []}}]}]}


def test_cp338_extraer_eventos_de_estados_y_mensajes():
    eventos = extraer_eventos(
        payload(
            estados=[
                {"id": "w1", "status": "delivered"},
                {"id": "w2", "status": "read"},
                {"id": "w3", "status": "failed", "errors": [{"title": "Número no válido"}]},
                {"id": "w4", "status": "failed", "errors": [{"message": "x" * 300}]},
                {"id": "w5", "status": "sent", "errors": []},
                {"id": "w6", "status": "deleted"},  # estado desconocido
                {"status": "sent"},  # sin id
                "basura",
            ],
            mensajes=[
                {"from": "51987654321", "text": {"body": "1"}, "context": {"id": "w1"}},
                {"from": "51987654321", "type": "button", "button": {"payload": "NO_PUEDE", "text": "No puedo"}},
                {"from": "51987654321", "interactive": {"button_reply": {"id": "3", "title": "Reprogramar"}}},
                {"from": "51987654321", "interactive": {"list_reply": {"title": "Confirmo"}}},
                {"from": "34600000000", "text": {"body": " "}, "context": "raro"},
            ],
        )
    )
    assert [(e.id_externo, e.estado) for e in eventos.estados] == [
        ("w1", E.ENTREGADO),
        ("w2", E.LEIDO),
        ("w3", E.FALLIDO),
        ("w4", E.FALLIDO),
        ("w5", E.ENVIADO),
    ]
    assert eventos.estados[2].error == "Número no válido" and len(eventos.estados[3].error) == 200
    assert eventos.estados[4].error is None
    assert [(m.texto, m.telefono, m.id_contexto) for m in eventos.mensajes] == [
        ("1", "987654321", "w1"),
        ("NO_PUEDE", "987654321", None),
        ("3", "987654321", None),
        ("Confirmo", "987654321", None),
        ("", None, None),
    ]


@pytest.mark.parametrize(
    "raro", [None, [], "texto", {}, {"entry": "x"}, {"entry": [1]}, {"entry": [{"changes": [1, {"value": 3}]}]}]
)
def test_cp339_extraer_eventos_tolera_estructuras_incompletas(raro):
    assert extraer_eventos(raro) == EventosWebhook()


def test_cp340_los_estados_de_entrega_solo_avanzan_y_el_simulado_no_cambia():
    assert avanzar_estado(E.ENVIADO, E.ENTREGADO) == E.ENTREGADO
    assert avanzar_estado(E.ENTREGADO, E.LEIDO) == E.LEIDO
    assert avanzar_estado(E.LEIDO, E.ENTREGADO) == E.LEIDO
    assert avanzar_estado(E.ENTREGADO, E.ENVIADO) == E.ENTREGADO
    assert avanzar_estado(E.ENVIADO, E.FALLIDO) == E.FALLIDO
    assert avanzar_estado(E.ENTREGADO, E.FALLIDO) == E.ENTREGADO
    assert avanzar_estado(E.FALLIDO, E.ENTREGADO) == E.FALLIDO
    assert avanzar_estado(E.ENVIADO_SIMULADO, E.LEIDO) == E.ENVIADO_SIMULADO


# --- Métricas ---------------------------------------------------------------------------------------------------------


def rec(estado=E.ENVIADO, canal=CanalEnvio.WHATSAPP, respuesta=None, codigo="DHx", **kw):
    return Recordatorio(
        "n1", codigo, HOY, TipoRecordatorio.PROXIMO, canal, estado, "987654321", "m", "enf", respuesta=respuesta, **kw
    )


def test_cp341_metricas_de_entrega_y_confirmacion_en_total_y_por_canal():
    vacias = calcular_metricas([])
    assert (vacias.total, vacias.tasa_envio, vacias.tasa_entrega, vacias.tasa_respuesta, vacias.por_canal) == (
        0,
        None,
        None,
        None,
        (),
    )
    lote = [
        rec(E.ENTREGADO, respuesta=RespuestaTutor.CONFIRMA),
        rec(E.LEIDO, respuesta=RespuestaTutor.NO_PUEDE),
        rec(E.ENVIADO, respuesta=RespuestaTutor.REPROGRAMAR),
        rec(E.FALLIDO),
        rec(E.ENVIADO, CanalEnvio.SMS),
        rec(E.ENVIADO_SIMULADO, CanalEnvio.SIMULADO),
    ]
    m = calcular_metricas(lote)
    assert (m.total, m.enviados, m.fallidos, m.simulados, m.entregados, m.leidos) == (6, 5, 1, 1, 2, 1)
    assert (m.con_respuesta, m.confirmados, m.no_pueden, m.reprogramados) == (3, 1, 1, 1)
    assert (m.tasa_envio, m.tasa_entrega, m.tasa_respuesta, m.tasa_confirmacion) == (0.8333, 0.5, 0.6, 0.2)
    por = {c.canal: c for c in m.por_canal}
    assert set(por) == {"SIMULADO", "WHATSAPP", "SMS"}
    assert (
        por["WHATSAPP"].total,
        por["WHATSAPP"].enviados,
        por["WHATSAPP"].fallidos,
        por["WHATSAPP"].tasa_entrega,
    ) == (4, 3, 1, 0.6667)
    assert por["SIMULADO"].tasa_entrega is None and por["SIMULADO"].enviados == 1
    solo_simulados = calcular_metricas([rec(E.ENVIADO_SIMULADO, CanalEnvio.SIMULADO)])
    assert solo_simulados.tasa_envio == 1.0 and solo_simulados.tasa_entrega is None
    assert rec(E.ENVIADO_SIMULADO, CanalEnvio.SIMULADO).simulado is True and rec().simulado is False
    assert rec().clave == ("n1", "DHx", HOY, "PROXIMO")


# --- Casos de uso -----------------------------------------------------------------------------------------------------


class NotificadorDePrueba:
    """Registra los mensajes y responde con los resultados programados (por defecto, envío exitoso por WhatsApp)."""

    def __init__(self, *resultados):
        self.resultados = list(resultados)
        self.enviados: list[MensajeSaliente] = []

    def enviar(self, mensaje):
        self.enviados.append(mensaje)
        if self.resultados:
            return self.resultados.pop(0)
        return ResultadoEnvio(True, CanalEnvio.WHATSAPP, E.ENVIADO, f"wamid.{len(self.enviados)}")


def falla(error="WhatsApp: error 500."):
    return ResultadoEnvio(False, CanalEnvio.WHATSAPP, E.FALLIDO, error=error)


@pytest.fixture
def repo():
    return RepositorioEnMemoria()


@pytest.fixture
def notificador():
    return NotificadorDePrueba()


def crear_servicio(repo, notificador, webhook=ConfiguracionWebhook(), reloj=None):
    reloj = reloj or RelojFijo()
    return ServicioRecordatorios(repo, repo, notificador, reloj, ServicioBarreras(repo, repo, reloj), webhook)


@pytest.fixture
def servicio(repo, notificador):
    return crear_servicio(repo, notificador)


def guardar(repo, **cambios):
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO], **cambios)
    repo.guardar(nino)
    return nino


def test_cp342_se_envia_un_recordatorio_por_control_a_los_ninos_con_contacto_y_se_cuenta_el_resto(
    repo, servicio, notificador
):
    con = guardar(repo, dni="70000001", nombres="Ana")
    guardar(
        repo,
        dni=None,
        nombres=None,
        apellidos=None,
        sexo=None,
        tutor_nombre=None,
        tutor_celular=None,
        origen=OrigenDatos.DATASET_DIRESA_JUNIN,
        codigo_origen="DJ-1",
    )
    guardar(repo, dni="70000003", tutor_celular=None)
    guardar(repo, dni="70000004", estado="ALTA")
    r = servicio.generar_recordatorios("enf.rosa")
    assert (r.fecha, r.candidatos, r.enviados, r.fallidos, r.omitidos_sin_contacto, r.omitidos_ya_enviado) == (
        HOY,
        9,
        3,
        0,
        6,
        0,
    )
    assert [v.recordatorio.codigo_control for v in r.recordatorios] == ["C1M", "DHc2", "C3M"]
    assert {v.recordatorio.nino_id for v in r.recordatorios} == {con.id} and r.recordatorios[
        0
    ].nombre_nino == con.nombre_completo
    primero = r.recordatorios[0].recordatorio
    assert (primero.tipo, primero.canal, primero.estado, primero.destino) == (
        TipoRecordatorio.VENCIDO,
        CanalEnvio.WHATSAPP,
        E.ENVIADO,
        "987654321",
    )
    assert (primero.generado_por, primero.id_externo, primero.enviado_en is not None) == ("enf.rosa", "wamid.1", True)
    assert len(notificador.enviados) == 3 and notificador.enviados[0].referencia == primero.id
    assert notificador.enviados[0].parametros[0] == "Ana" and notificador.enviados[0].plantilla == PLANTILLA_WHATSAPP


def test_cp343_generar_dos_veces_el_mismo_dia_no_repite_mensajes(repo, servicio, notificador):
    guardar(repo)
    servicio.generar_recordatorios("enf")
    segunda = servicio.generar_recordatorios("enf")
    assert (segunda.enviados, segunda.omitidos_ya_enviado, segunda.recordatorios) == (0, 3, ())
    assert len(notificador.enviados) == 3 and len(repo.listar_recordatorios()) == 3


def test_cp344_un_envio_fallido_se_reintenta_en_la_siguiente_generacion_sobre_el_mismo_registro(repo):
    guardar(repo)
    notificador = NotificadorDePrueba(falla(), falla("WhatsApp: sin respuesta."))
    servicio = crear_servicio(repo, notificador)
    primera = servicio.generar_recordatorios("enf")
    assert (primera.enviados, primera.fallidos) == (1, 2)  # los dos primeros fallan, el tercero se envía
    fallido = primera.recordatorios[0].recordatorio
    assert (fallido.estado, fallido.detalle, fallido.enviado_en, fallido.id_externo, fallido.intentos) == (
        E.FALLIDO,
        "WhatsApp: error 500.",
        None,
        None,
        1,
    )
    segunda = servicio.generar_recordatorios("otra")
    assert (segunda.enviados, segunda.fallidos, segunda.omitidos_ya_enviado) == (2, 0, 1)
    reintentado = repo.obtener_recordatorio(fallido.id)
    assert (reintentado.estado, reintentado.intentos, reintentado.generado_por, reintentado.detalle) == (
        E.ENVIADO,
        2,
        "otra",
        None,
    )
    assert reintentado.enviado_en is not None and len(repo.listar_recordatorios()) == 3
    assert notificador.enviados[3].referencia == fallido.id  # el reintento conserva la referencia


def test_cp345_el_aviso_del_respaldo_se_guarda_como_detalle(repo):
    guardar(repo)
    sms = ResultadoEnvio(True, CanalEnvio.SMS, E.ENVIADO, "sms-1", "WhatsApp: error 500. Se reintentó por SMS.")
    servicio = crear_servicio(repo, NotificadorDePrueba(sms))
    primero = servicio.generar_recordatorios("enf").recordatorios[0].recordatorio
    assert (primero.canal, primero.estado, primero.detalle) == (CanalEnvio.SMS, E.ENVIADO, sms.error)


def test_cp346_filtro_por_establecimiento_y_notificador_simulado(repo):
    guardar(repo, dni="70000001", establecimiento="P. S. Chongos Alto")
    guardar(repo, dni="70000002", establecimiento="C. S. Otro")
    servicio = crear_servicio(repo, NotificadorSimulado())
    r = servicio.generar_recordatorios("enf", " p. s. chongos ALTO ")
    assert (r.candidatos, r.enviados) == (3, 3)
    recordatorio = r.recordatorios[0].recordatorio
    assert (recordatorio.canal, recordatorio.estado, recordatorio.simulado) == (
        CanalEnvio.SIMULADO,
        E.ENVIADO_SIMULADO,
        True,
    )
    assert recordatorio.id_externo.startswith("sim-") and recordatorio.enviado_en is not None


def test_cp347_una_generacion_simultanea_ya_creada_cuenta_como_ya_enviado(repo, notificador):
    guardar(repo)
    servicio = crear_servicio(repo, notificador)

    original = repo.agregar_recordatorio

    def agregar(r):
        if r.codigo_control == "DHc2":
            raise ConflictoRecordatorio("ya existe")
        return original(r)

    repo.agregar_recordatorio = agregar
    r = servicio.generar_recordatorios("enf")
    assert (r.enviados, r.omitidos_ya_enviado, len(r.recordatorios)) == (2, 1, 2)


def test_cp348_listar_recordatorios_con_filtros_y_validacion(repo, servicio):
    a = guardar(repo, dni="70000001")
    servicio.generar_recordatorios("enf")
    lista = servicio.listar_recordatorios()
    assert len(lista) == 3 and {v.nombre_nino for v in lista} == {a.nombre_completo}
    assert servicio.listar_recordatorios(estado="FALLIDO") == []
    assert (
        len(servicio.listar_recordatorios(estado="ENVIADO", nino_id=a.id, desde=HOY - timedelta(days=1), limite=2)) == 2
    )
    for kwargs, campo in (({"estado": "RARO"}, "estado"), ({"limite": 0}, "limite"), ({"limite": 1001}, "limite")):
        with pytest.raises(ErrorValidacion) as e:
            servicio.listar_recordatorios(**kwargs)
        assert e.value.errores[0].campo == campo


def test_cp349_metricas_del_servicio_y_rango_de_fechas_invalido(repo, servicio):
    guardar(repo)
    servicio.generar_recordatorios("enf")
    m = servicio.metricas_recordatorios()
    assert (m.total, m.enviados, m.tasa_envio) == (3, 3, 1.0)
    assert servicio.metricas_recordatorios(desde=date(2100, 1, 1)).total == 0
    with pytest.raises(ErrorValidacion) as e:
        servicio.metricas_recordatorios(desde=HOY, hasta=HOY - timedelta(days=1))
    assert e.value.errores[0].campo == "desde"


def primero(servicio):
    return servicio.generar_recordatorios("enf").recordatorios[0].recordatorio


def test_cp350_el_personal_registra_confirma_y_reprograma(repo, servicio):
    guardar(repo)
    r1 = primero(servicio)
    res = servicio.registrar_respuesta(r1.id, {"respuesta": "CONFIRMA"}, "enf.rosa")
    guardado = repo.obtener_recordatorio(r1.id)
    assert (guardado.respuesta, guardado.origen_respuesta, guardado.respondido_por) == (
        RespuestaTutor.CONFIRMA,
        OrigenRespuesta.PERSONAL,
        "enf.rosa",
    )
    assert guardado.respondido_en is not None and res.barrera_id is None and res.barrera_sugerida is False
    r2 = repo.listar_recordatorios()[1]
    nueva = HOY + timedelta(days=7)
    servicio.registrar_respuesta(r2.id, {"respuesta": "REPROGRAMAR", "fecha_reprogramada": nueva}, "enf")
    assert repo.obtener_recordatorio(r2.id).fecha_reprogramada == nueva


def test_cp351_no_puede_con_barrera_la_registra_con_la_fuente_respuesta_y_sin_barrera_la_sugiere(repo, servicio):
    nino = guardar(repo)
    recordatorios = servicio.generar_recordatorios("enf").recordatorios
    con = servicio.registrar_respuesta(
        recordatorios[0].recordatorio.id,
        {"respuesta": "NO_PUEDE", "barrera": {"tipo": "OTRA", "detalle": "Sin dinero"}},
        "enf",
    )
    barrera = repo.listar_barreras(nino.id)[0]
    assert con.barrera_id == barrera.id and con.barrera_sugerida is False
    assert (barrera.fuente.value, barrera.recordatorio_id, barrera.fecha, barrera.detalle) == (
        "RESPUESTA_RECORDATORIO",
        recordatorios[0].recordatorio.id,
        HOY,
        "Sin dinero",
    )
    sin = servicio.registrar_respuesta(recordatorios[1].recordatorio.id, {"respuesta": "NO_PUEDE"}, "enf")
    assert sin.barrera_id is None and sin.barrera_sugerida is True
    # la misma barrera del mismo día con la misma fuente no se duplica: se devuelve la existente
    igual = servicio.registrar_respuesta(
        recordatorios[2].recordatorio.id,
        {"respuesta": "NO_PUEDE", "barrera": {"tipo": "OTRA", "detalle": "Sin dinero"}},
        "enf",
    )
    assert igual.barrera_id == con.barrera_id and len(repo.listar_barreras(nino.id)) == 1


def test_cp352_respuesta_invalida_duplicada_o_a_un_recordatorio_inexistente(repo, servicio):
    guardar(repo)
    r1 = primero(servicio)
    with pytest.raises(NoEncontrado):
        servicio.registrar_respuesta("no-existe", {"respuesta": "CONFIRMA"}, "enf")
    with pytest.raises(ErrorValidacion):
        servicio.registrar_respuesta(r1.id, {"respuesta": "REPROGRAMAR"}, "enf")
    with pytest.raises(ErrorValidacion) as e:  # barrera inválida: no se guarda la respuesta
        servicio.registrar_respuesta(r1.id, {"respuesta": "NO_PUEDE", "barrera": {"tipo": "OTRA"}}, "enf")
    assert e.value.errores[0].campo == "detalle" and repo.obtener_recordatorio(r1.id).respuesta is None
    servicio.registrar_respuesta(r1.id, {"respuesta": "CONFIRMA"}, "enf")
    with pytest.raises(ConflictoRespuesta):
        servicio.registrar_respuesta(r1.id, {"respuesta": "NO_PUEDE"}, "enf")


# --- Webhook: casos de uso --------------------------------------------------------------------------------------------


def evento_estado(id_externo, estado, error=None):
    return EventoEstado(id_externo, estado, error)


def test_cp353_los_estados_del_webhook_actualizan_el_recordatorio_y_se_ignoran_los_desconocidos_o_atrasados(
    repo, servicio
):
    guardar(repo)
    r1 = primero(servicio)
    resumen = servicio.procesar_eventos(
        EventosWebhook(
            estados=(
                evento_estado(r1.id_externo, E.ENTREGADO),
                evento_estado(r1.id_externo, E.ENVIADO),  # retroceso: se ignora
                evento_estado("wamid.desconocido", E.LEIDO),
                evento_estado(r1.id_externo, E.LEIDO),
            )
        )
    )
    assert (resumen.estados_aplicados, resumen.respuestas_registradas, resumen.ignorados) == (2, 0, 2)
    assert repo.obtener_recordatorio(r1.id).estado == E.LEIDO
    r2 = repo.listar_recordatorios()[1]
    servicio.procesar_eventos(EventosWebhook(estados=(evento_estado(r2.id_externo, E.FALLIDO, "Número no válido"),)))
    r2 = repo.obtener_recordatorio(r2.id)
    assert (r2.estado, r2.detalle) == (E.FALLIDO, "Número no válido")


def test_cp354_las_respuestas_del_webhook_se_asocian_por_contexto_o_por_celular_y_solo_una_vez(repo, servicio):
    guardar(repo)
    r1 = primero(servicio)
    resumen = servicio.procesar_eventos(
        EventosWebhook(
            mensajes=(
                MensajeEntrante("2", "987654321", r1.id_externo),
                MensajeEntrante("1", "987654321", r1.id_externo),  # ya respondido: sin otro pendiente con ese contexto
                MensajeEntrante("gracias", "987654321", None),  # no es una respuesta
                MensajeEntrante("1", "900000000", None),  # celular desconocido
            )
        )
    )
    assert (resumen.respuestas_registradas, resumen.ignorados) == (1, 3)
    r1 = repo.obtener_recordatorio(r1.id)
    assert (r1.respuesta, r1.origen_respuesta, r1.respondido_por) == (
        RespuestaTutor.NO_PUEDE,
        OrigenRespuesta.WHATSAPP,
        "whatsapp",
    )


def test_cp355_reprogramar_por_whatsapp_acepta_la_fecha_en_rango_y_descarta_la_que_no_lo_esta(repo, servicio):
    guardar(repo)
    servicio.generar_recordatorios("enf")
    uno, dos, _ = repo.listar_recordatorios()
    servicio.procesar_eventos(
        EventosWebhook(mensajes=(MensajeEntrante("reprogramar 05/10/2026", None, uno.id_externo),))
    )
    servicio.procesar_eventos(
        EventosWebhook(mensajes=(MensajeEntrante("reprogramar 05/10/2027", None, dos.id_externo),))
    )
    assert repo.obtener_recordatorio(uno.id).fecha_reprogramada == date(2026, 10, 5)
    sin_fecha = repo.obtener_recordatorio(dos.id)
    assert (sin_fecha.respuesta, sin_fecha.fecha_reprogramada) == (RespuestaTutor.REPROGRAMAR, None)


def test_cp356_el_webhook_firmado_se_procesa_y_el_invalido_se_rechaza(repo, notificador):
    guardar(repo)
    servicio = crear_servicio(repo, notificador, ConfiguracionWebhook("tok", "secreto"))
    r1 = primero(servicio)
    cuerpo = json.dumps(payload(estados=[{"id": r1.id_externo, "status": "delivered"}])).encode()
    assert servicio.procesar_webhook(cuerpo, firmar(cuerpo, "secreto")).estados_aplicados == 1
    for firma in (None, "sha256=00", firmar(cuerpo, "otro")):
        with pytest.raises(FirmaInvalida):
            servicio.procesar_webhook(cuerpo, firma)
    malo = b"no es json"
    with pytest.raises(ErrorValidacion) as e:
        servicio.procesar_webhook(malo, firmar(malo, "secreto"))
    assert e.value.errores[0].campo == "cuerpo"
    assert (
        servicio.verificar_suscripcion("subscribe", "tok") is True
        and servicio.verificar_suscripcion("subscribe", "x") is False
    )


def test_cp357_sin_secreto_configurado_el_webhook_falla_cerrado_y_no_procesa_nada(repo, servicio):
    guardar(repo)
    r1 = primero(servicio)
    cuerpo = json.dumps(payload(estados=[{"id": r1.id_externo, "status": "read"}])).encode()
    for firma in (None, "sha256=00", firmar(cuerpo, ""), firmar(cuerpo, "cualquiera")):
        with pytest.raises(WebhookNoConfigurado):
            servicio.procesar_webhook(cuerpo, firma)
    assert repo.obtener_recordatorio(r1.id).estado == r1.estado  # ni el estado de entrega ni nada cambió
    assert servicio.verificar_suscripcion("subscribe", "") is False
