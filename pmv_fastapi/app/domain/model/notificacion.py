"""Recordatorios de control por mensajería y respuesta del tutor (HIST-4.1 y HIST-4.2, ADR-014)."""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum

from app.domain.model.tiempo import ahora


class TipoRecordatorio(StrEnum):
    PROXIMO = "PROXIMO"  # control pendiente cuya ventana abre en 3 días o menos (o ya está abierta)
    CITA_DEL_DIA = "CITA_DEL_DIA"  # control pendiente programado para hoy
    VENCIDO = "VENCIDO"  # control vencido


class CanalEnvio(StrEnum):
    SIMULADO = "SIMULADO"
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"


class EstadoRecordatorio(StrEnum):
    ENVIADO_SIMULADO = "ENVIADO_SIMULADO"  # el notificador simulado lo registró; no salió ningún mensaje real
    ENVIADO = "ENVIADO"  # el proveedor aceptó el mensaje
    ENTREGADO = "ENTREGADO"  # llegó al teléfono del tutor
    LEIDO = "LEIDO"  # el tutor lo abrió
    FALLIDO = "FALLIDO"  # el envío falló o el proveedor lo devolvió


class RespuestaTutor(StrEnum):
    CONFIRMA = "CONFIRMA"
    NO_PUEDE = "NO_PUEDE"
    REPROGRAMAR = "REPROGRAMAR"  # con una nueva fecha


class OrigenRespuesta(StrEnum):
    PERSONAL = "PERSONAL"  # la registró el personal (llamada, visita)
    WHATSAPP = "WHATSAPP"  # llegó por el webhook de WhatsApp


@dataclass(frozen=True)
class MensajeSaliente:
    """Mensaje que el puerto ``Notificador`` entrega a un canal. Sin diagnóstico: solo el aviso del control."""

    destino: str  # celular de 9 dígitos
    texto: str  # texto completo (SMS y simulado)
    plantilla: str  # nombre de la plantilla aprobada (WhatsApp)
    parametros: tuple[str, ...]  # variables de la plantilla: niño, control, establecimiento, fecha
    referencia: str  # id del recordatorio


@dataclass(frozen=True)
class ResultadoEnvio:
    exito: bool
    canal: CanalEnvio
    estado: EstadoRecordatorio
    id_externo: str | None = None
    error: str | None = None  # motivo de la falla; también el aviso de que el respaldo reemplazó a WhatsApp


@dataclass
class Recordatorio:
    """Recordatorio de un control; único por (niño, control, tipo). El control es (código, fecha programada)."""

    nino_id: str
    codigo_control: str
    fecha_programada: date
    tipo: TipoRecordatorio
    canal: CanalEnvio
    estado: EstadoRecordatorio
    destino: str
    mensaje: str
    generado_por: str
    id_externo: str | None = None
    detalle: str | None = None
    intentos: int = 1
    enviado_en: datetime | None = None
    respuesta: RespuestaTutor | None = None
    fecha_reprogramada: date | None = None
    respondido_en: datetime | None = None
    respondido_por: str | None = None
    origen_respuesta: OrigenRespuesta | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creado_en: datetime = field(default_factory=ahora)
    actualizado_en: datetime = field(default_factory=ahora)

    @property
    def clave(self) -> tuple[str, str, date, str]:
        return (self.nino_id, self.codigo_control, self.fecha_programada, self.tipo.value)

    @property
    def simulado(self) -> bool:
        return self.canal == CanalEnvio.SIMULADO


@dataclass(frozen=True)
class VistaRecordatorio:
    """Recordatorio con los datos del niño para mostrarlo (sin consultar niño por niño)."""

    recordatorio: Recordatorio
    nombre_nino: str
    codigo_origen: str | None
    comunidad: str
    establecimiento: str


@dataclass(frozen=True)
class ResultadoGeneracion:
    fecha: date
    candidatos: int
    enviados: int
    fallidos: int
    omitidos_sin_contacto: int
    omitidos_ya_enviado: int
    recordatorios: tuple[VistaRecordatorio, ...] = ()


@dataclass(frozen=True)
class EventoEstado:
    """Cambio de estado de entrega que informa el webhook de WhatsApp."""

    id_externo: str
    estado: EstadoRecordatorio
    error: str | None = None


@dataclass(frozen=True)
class MensajeEntrante:
    """Respuesta del tutor recibida por el webhook de WhatsApp."""

    texto: str
    telefono: str | None = None  # celular de 9 dígitos del remitente
    id_contexto: str | None = None  # id del mensaje al que responde, si lo indica WhatsApp


@dataclass(frozen=True)
class EventosWebhook:
    estados: tuple[EventoEstado, ...] = ()
    mensajes: tuple[MensajeEntrante, ...] = ()


@dataclass(frozen=True)
class ResumenWebhook:
    estados_aplicados: int = 0
    respuestas_registradas: int = 0
    ignorados: int = 0


@dataclass(frozen=True)
class ConfiguracionWebhook:
    """Secretos del webhook de WhatsApp (vacíos si no se configuraron)."""

    verify_token: str = ""
    app_secret: str = ""


@dataclass(frozen=True)
class ResultadoRespuesta:
    recordatorio: VistaRecordatorio
    barrera_id: str | None = None  # barrera registrada junto con la respuesta NO_PUEDE
    barrera_sugerida: bool = False  # NO_PUEDE sin barrera: conviene registrar el motivo


@dataclass(frozen=True)
class MetricasCanal:
    canal: str
    total: int
    enviados: int
    fallidos: int
    entregados: int
    leidos: int
    confirmados: int
    tasa_entrega: float | None
    tasa_confirmacion: float | None


@dataclass(frozen=True)
class MetricasRecordatorios:
    """Métricas de entrega de mensajes (hito H4). Las tasas son proporciones de 0 a 1 o ``None`` si no hay base."""

    total: int
    enviados: int  # el canal aceptó el mensaje (todo menos FALLIDO, incluidos los simulados)
    fallidos: int
    simulados: int
    entregados: int  # ENTREGADO o LEIDO
    leidos: int
    con_respuesta: int
    confirmados: int
    no_pueden: int
    reprogramados: int
    tasa_envio: float | None
    tasa_entrega: float | None  # entregados / enviados reales (sin los simulados)
    tasa_respuesta: float | None
    tasa_confirmacion: float | None  # confirmados / enviados
    por_canal: tuple[MetricasCanal, ...] = ()
