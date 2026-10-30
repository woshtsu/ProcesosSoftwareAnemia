"""Recordatorios de control y respuestas del tutor (HIST-4.1 y HIST-4.2, ADR-014). Servicio de dominio puro.

Selección (parámetros en ``REGLAS_RECORDATORIO_V1``): de la agenda del niño (ADR-007) se recuerdan
  * CITA_DEL_DIA: el control PENDIENTE programado para hoy;
  * PROXIMO: el control PENDIENTE cuya ventana de cumplimiento abre en 3 días o menos, o ya está abierta;
  * VENCIDO: el control VENCIDO.
Un recordatorio es único por (niño, control, tipo), donde el control es (código, fecha programada) como en ADR-010:
generar el lote dos veces el mismo día no repite mensajes (idempotencia). Un mismo control puede recibir uno de cada
tipo a lo largo del tiempo (primero PROXIMO, luego VENCIDO si el niño no acudió).

Contacto: solo los niños del sistema con celular. Los del dataset DIRESA no tienen celular ni tutor (ADR-009): se
cuentan como «sin contacto».

Mensaje: español sencillo y sin diagnóstico; solo el nombre del niño, el control, el establecimiento y la fecha
sugerida.

Respuesta del tutor: CONFIRMA, NO_PUEDE o REPROGRAMAR (con una fecha de hasta 90 días). El personal siempre indica la
fecha; en el webhook de WhatsApp es opcional porque el tutor puede no escribirla.

Webhook de WhatsApp: la firma ``X-Hub-Signature-256`` es HMAC-SHA256 del cuerpo con el secreto de la aplicación. Los
estados de entrega solo avanzan (ENVIADO, ENTREGADO, LEIDO); FALLIDO solo reemplaza a ENVIADO.
"""

import hashlib
import hmac
import re
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta

from app.domain.model.agenda import AgendaNino, ControlProgramado, EstadoControl, TipoControl
from app.domain.model.entidades import Nino
from app.domain.model.errores import ErrorCampo
from app.domain.model.notificacion import (
    CanalEnvio,
    EstadoRecordatorio,
    EventoEstado,
    EventosWebhook,
    MensajeEntrante,
    MetricasCanal,
    MetricasRecordatorios,
    Recordatorio,
    RespuestaTutor,
    TipoRecordatorio,
)

PATRON_CELULAR = re.compile(r"9[0-9]{8}")
DIAS_MAX_REPROGRAMACION = 90
PLANTILLA_WHATSAPP = "recordatorio_control"
TEXTO_PLANTILLA = (
    "Hola, le recordamos el {control} de {nino} en {establecimiento}. Fecha sugerida: {fecha}. "
    "Responda: 1 = Confirmo, 2 = No puedo, 3 = Reprogramar."
)


@dataclass(frozen=True)
class ReglasRecordatorio:
    """Parámetros de la selección de recordatorios (versionados)."""

    version: str
    dias_anticipacion: int = 3  # la ventana de cumplimiento abre en esta cantidad de días o menos


REGLAS_RECORDATORIO_V1 = ReglasRecordatorio(version="RECORDATORIO-V1")

_ETIQUETA_CONTROL = {
    TipoControl.TAMIZAJE_EDAD: "control de hemoglobina",
    TipoControl.CONTROL_TRATAMIENTO: "control de seguimiento",
}
_ESTADOS_ENTREGA = {
    "sent": EstadoRecordatorio.ENVIADO,
    "delivered": EstadoRecordatorio.ENTREGADO,
    "read": EstadoRecordatorio.LEIDO,
    "failed": EstadoRecordatorio.FALLIDO,
}
_RANGO = {EstadoRecordatorio.ENVIADO: 1, EstadoRecordatorio.ENTREGADO: 2, EstadoRecordatorio.LEIDO: 3}


# --- Selección -------------------------------------------------------------------------------------------------------


def tipo_de_recordatorio(control: ControlProgramado, hoy: date, reglas: ReglasRecordatorio) -> TipoRecordatorio | None:
    """Tipo de recordatorio que corresponde al control hoy, o ``None`` si no hay que recordarlo."""
    if control.estado == EstadoControl.VENCIDO:
        return TipoRecordatorio.VENCIDO
    if control.estado != EstadoControl.PENDIENTE:
        return None
    if control.fecha_programada == hoy:
        return TipoRecordatorio.CITA_DEL_DIA
    if control.fecha_inicio_ventana <= hoy + timedelta(days=reglas.dias_anticipacion):
        return TipoRecordatorio.PROXIMO
    return None


def seleccionar_controles(
    agenda: AgendaNino, hoy: date, reglas: ReglasRecordatorio = REGLAS_RECORDATORIO_V1
) -> list[tuple[ControlProgramado, TipoRecordatorio]]:
    """Controles de la agenda que hay que recordar hoy, con su tipo (en el orden de la agenda)."""
    elegidos = []
    for control in agenda.controles:
        tipo = tipo_de_recordatorio(control, hoy, reglas)
        if tipo is not None:
            elegidos.append((control, tipo))
    return elegidos


def tiene_contacto(nino: Nino) -> bool:
    """Se le puede escribir al tutor: registro del sistema con un celular válido."""
    return not nino.es_dataset and bool(nino.tutor_celular and PATRON_CELULAR.fullmatch(nino.tutor_celular))


def fecha_sugerida(control: ControlProgramado, tipo: TipoRecordatorio, hoy: date) -> str:
    if tipo == TipoRecordatorio.VENCIDO:
        return "lo antes posible"
    fecha = max(control.fecha_programada, hoy)
    return "hoy" if fecha == hoy else fecha.strftime("%d/%m/%Y")


def parametros_mensaje(
    nino: Nino, control: ControlProgramado, tipo: TipoRecordatorio, hoy: date
) -> tuple[str, str, str, str]:
    """Variables del mensaje, en el orden de la plantilla: niño, control, establecimiento y fecha sugerida."""
    return (
        (nino.nombres or "").strip(),
        _ETIQUETA_CONTROL[control.tipo],
        nino.establecimiento.strip(),
        fecha_sugerida(control, tipo, hoy),
    )


def redactar_mensaje(parametros: tuple[str, ...]) -> str:
    nino, control, establecimiento, fecha = parametros
    return TEXTO_PLANTILLA.format(nino=nino, control=control, establecimiento=establecimiento, fecha=fecha)


# --- Respuesta del tutor ---------------------------------------------------------------------------------------------


def validar_respuesta(datos: dict, hoy: date, exigir_fecha: bool = True) -> list[ErrorCampo]:
    errores: list[ErrorCampo] = []
    respuesta = datos.get("respuesta")
    if respuesta not in {r.value for r in RespuestaTutor}:
        errores.append(ErrorCampo("respuesta", "La respuesta debe ser CONFIRMA, NO_PUEDE o REPROGRAMAR."))
    fecha = datos.get("fecha_reprogramada")
    if respuesta == RespuestaTutor.REPROGRAMAR:
        if fecha is None:
            if exigir_fecha:
                errores.append(ErrorCampo("fecha_reprogramada", "Indique la nueva fecha."))
        elif not isinstance(fecha, date):
            errores.append(ErrorCampo("fecha_reprogramada", "Fecha inválida."))
        elif not (hoy <= fecha <= hoy + timedelta(days=DIAS_MAX_REPROGRAMACION)):
            errores.append(
                ErrorCampo(
                    "fecha_reprogramada",
                    f"La nueva fecha debe estar entre hoy y los próximos {DIAS_MAX_REPROGRAMACION} días.",
                )
            )
    elif fecha is not None:
        errores.append(ErrorCampo("fecha_reprogramada", "Solo se indica una fecha al reprogramar."))
    if datos.get("barrera") and respuesta != RespuestaTutor.NO_PUEDE:
        errores.append(ErrorCampo("barrera", "Solo se registra una barrera cuando el tutor responde NO_PUEDE."))
    return errores


def _normalizar(texto: str) -> str:
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.casefold().replace("_", " ").split())


_PATRON_FECHA = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b")
_CONFIRMA = {"1", "si", "confirmo", "confirma", "ok", "asistire", "confirmado"}
_NO_PUEDE = {"2", "no", "no puedo", "no puede", "no podre", "no podemos"}
_REPROGRAMA = {"3", "reprogramar", "reprogramo", "reprogramacion", "otra fecha", "cambiar fecha"}


def interpretar_respuesta(texto: str) -> tuple[RespuestaTutor | None, date | None]:
    """Respuesta que expresa el texto de un mensaje (botón, número o palabra) y la fecha que indique al reprogramar.

    Devuelve ``(None, None)`` si el texto no es una respuesta reconocible: se ignora y no se adivina.
    """
    limpio = _normalizar(texto)
    if limpio in _CONFIRMA:
        return RespuestaTutor.CONFIRMA, None
    if limpio in _NO_PUEDE:
        return RespuestaTutor.NO_PUEDE, None
    coincidencia = _PATRON_FECHA.search(limpio)
    resto = " ".join(_PATRON_FECHA.sub(" ", limpio).split())
    if resto in _REPROGRAMA or (coincidencia and resto in {"", "para"}):
        return RespuestaTutor.REPROGRAMAR, _fecha_o_none(coincidencia)
    return None, None


def _fecha_o_none(coincidencia: re.Match | None) -> date | None:
    if coincidencia is None:
        return None
    dia, mes, anio = (int(x) for x in coincidencia.groups())
    try:
        return date(anio, mes, dia)
    except ValueError:
        return None


# --- Webhook de WhatsApp ---------------------------------------------------------------------------------------------


def firma_valida(cuerpo: bytes, cabecera: str | None, secreto: str) -> bool:
    """``X-Hub-Signature-256`` = «sha256=» + HMAC-SHA256 del cuerpo exacto con el secreto de la aplicación."""
    if not cabecera or not cabecera.startswith("sha256="):
        return False
    esperada = hmac.new(secreto.encode(), cuerpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperada, cabecera.removeprefix("sha256="))


def verificacion_valida(modo: str | None, token: str | None, esperado: str) -> bool:
    """Verificación de la suscripción del webhook: ``hub.mode=subscribe`` y el token configurado (nunca uno vacío)."""
    return (
        modo == "subscribe"
        and bool(esperado)
        and bool(token)
        and hmac.compare_digest(token.encode(), esperado.encode())
    )


def firmar(cuerpo: bytes, secreto: str) -> str:
    """Valor de la cabecera de firma para un cuerpo (lo usan las pruebas y las herramientas de diagnóstico)."""
    return "sha256=" + hmac.new(secreto.encode(), cuerpo, hashlib.sha256).hexdigest()


def celular_de_whatsapp(numero: object) -> str | None:
    """Celular de 9 dígitos de un número de WhatsApp (51 + 9 dígitos), o ``None`` si no es un celular peruano."""
    digitos = re.sub(r"\D", "", numero) if isinstance(numero, str) else ""
    if len(digitos) == 11 and digitos.startswith("51"):
        digitos = digitos[2:]
    return digitos if PATRON_CELULAR.fullmatch(digitos) else None


def _texto_del_mensaje(mensaje: dict) -> str:
    texto = (mensaje.get("text") or {}).get("body")
    boton = mensaje.get("button") or {}
    interactivo = mensaje.get("interactive") or {}
    respuesta = interactivo.get("button_reply") or interactivo.get("list_reply") or {}
    for candidato in (texto, boton.get("payload"), boton.get("text"), respuesta.get("id"), respuesta.get("title")):
        if isinstance(candidato, str) and candidato.strip():
            return candidato
    return ""


def _dicts(valor: object) -> list[dict]:
    return [x for x in valor if isinstance(x, dict)] if isinstance(valor, list) else []


def extraer_eventos(payload: object) -> EventosWebhook:
    """Estados de entrega y mensajes entrantes de una notificación de WhatsApp (tolera estructuras incompletas)."""
    estados: list[EventoEstado] = []
    mensajes: list[MensajeEntrante] = []
    cambios = [
        cambio.get("value") or {}
        for entrada in _dicts(payload.get("entry") if isinstance(payload, dict) else None)
        for cambio in _dicts(entrada.get("changes"))
    ]
    for valor in (v for v in cambios if isinstance(v, dict)):
        for estado in _dicts(valor.get("statuses")):
            nuevo = _ESTADOS_ENTREGA.get(str(estado.get("status")))
            if nuevo is None or not isinstance(estado.get("id"), str):
                continue
            errores = _dicts(estado.get("errors"))
            titulo = (errores[0].get("title") or errores[0].get("message")) if errores else None
            estados.append(EventoEstado(estado["id"], nuevo, str(titulo)[:200] if titulo else None))
        for mensaje in _dicts(valor.get("messages")):
            contexto = mensaje.get("context") if isinstance(mensaje.get("context"), dict) else {}
            id_contexto = contexto.get("id") if isinstance(contexto.get("id"), str) else None
            mensajes.append(
                MensajeEntrante(_texto_del_mensaje(mensaje), celular_de_whatsapp(mensaje.get("from")), id_contexto)
            )
    return EventosWebhook(tuple(estados), tuple(mensajes))


def avanzar_estado(actual: EstadoRecordatorio, nuevo: EstadoRecordatorio) -> EstadoRecordatorio:
    """Estado resultante de aplicar un aviso de entrega: nunca retrocede y el simulado no cambia."""
    if actual not in _RANGO:
        return actual
    if nuevo == EstadoRecordatorio.FALLIDO:
        return nuevo if actual == EstadoRecordatorio.ENVIADO else actual
    return nuevo if _RANGO[nuevo] > _RANGO[actual] else actual


# --- Métricas --------------------------------------------------------------------------------------------------------


def _tasa(numerador: int, denominador: int) -> float | None:
    return round(numerador / denominador, 4) if denominador else None


def _contar(recordatorios: list[Recordatorio]) -> dict[str, int]:
    entregados = (EstadoRecordatorio.ENTREGADO, EstadoRecordatorio.LEIDO)
    return {
        "total": len(recordatorios),
        "fallidos": sum(1 for r in recordatorios if r.estado == EstadoRecordatorio.FALLIDO),
        "simulados": sum(1 for r in recordatorios if r.estado == EstadoRecordatorio.ENVIADO_SIMULADO),
        "entregados": sum(1 for r in recordatorios if r.estado in entregados),
        "leidos": sum(1 for r in recordatorios if r.estado == EstadoRecordatorio.LEIDO),
        "con_respuesta": sum(1 for r in recordatorios if r.respuesta is not None),
        "confirmados": sum(1 for r in recordatorios if r.respuesta == RespuestaTutor.CONFIRMA),
        "no_pueden": sum(1 for r in recordatorios if r.respuesta == RespuestaTutor.NO_PUEDE),
        "reprogramados": sum(1 for r in recordatorios if r.respuesta == RespuestaTutor.REPROGRAMAR),
    }


def calcular_metricas(recordatorios: list[Recordatorio]) -> MetricasRecordatorios:
    """Métricas de entrega y confirmación, en total y por canal (tasas como proporción de 0 a 1)."""
    n = _contar(recordatorios)
    enviados = n["total"] - n["fallidos"]
    reales = enviados - n["simulados"]
    por_canal = []
    for canal in CanalEnvio:
        propios = [r for r in recordatorios if r.canal == canal]
        if not propios:
            continue
        c = _contar(propios)
        enviados_canal = c["total"] - c["fallidos"]
        reales_canal = enviados_canal - c["simulados"]
        por_canal.append(
            MetricasCanal(
                canal=canal.value,
                total=c["total"],
                enviados=enviados_canal,
                fallidos=c["fallidos"],
                entregados=c["entregados"],
                leidos=c["leidos"],
                confirmados=c["confirmados"],
                tasa_entrega=_tasa(c["entregados"], reales_canal),
                tasa_confirmacion=_tasa(c["confirmados"], enviados_canal),
            )
        )
    return MetricasRecordatorios(
        total=n["total"],
        enviados=enviados,
        fallidos=n["fallidos"],
        simulados=n["simulados"],
        entregados=n["entregados"],
        leidos=n["leidos"],
        con_respuesta=n["con_respuesta"],
        confirmados=n["confirmados"],
        no_pueden=n["no_pueden"],
        reprogramados=n["reprogramados"],
        tasa_envio=_tasa(enviados, n["total"]),
        tasa_entrega=_tasa(n["entregados"], reales),
        tasa_respuesta=_tasa(n["con_respuesta"], enviados),
        tasa_confirmacion=_tasa(n["confirmados"], enviados),
        por_canal=tuple(por_canal),
    )
