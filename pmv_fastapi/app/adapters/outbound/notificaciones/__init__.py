"""Notificadores de recordatorios (puerto ``Notificador``) y su selección según la configuración (ADR-014)."""

from collections.abc import Mapping

import httpx

from app.adapters.outbound.notificaciones.respaldo import NotificadorConRespaldo
from app.adapters.outbound.notificaciones.simulado import NotificadorSimulado
from app.adapters.outbound.notificaciones.sms import NotificadorSMS
from app.adapters.outbound.notificaciones.whatsapp_cloud import NotificadorWhatsAppCloud
from app.ports.outbound.notificador import Notificador

__all__ = [
    "NotificadorConRespaldo",
    "NotificadorSMS",
    "NotificadorSimulado",
    "NotificadorWhatsAppCloud",
    "crear_notificador",
]


def crear_notificador(entorno: Mapping[str, str], cliente: httpx.Client | None = None) -> Notificador:
    """Notificador según las variables de entorno.

    * Sin ``WHATSAPP_TOKEN`` y ``WHATSAPP_PHONE_NUMBER_ID`` (por defecto): simulado, no sale ningún mensaje.
    * Con ambas: WhatsApp Cloud API; si además hay ``SMS_API_URL``, un fallo de WhatsApp se reintenta por SMS.
    ``cliente`` permite inyectar un ``httpx.Client`` con ``MockTransport`` en las pruebas.
    """
    token = entorno.get("WHATSAPP_TOKEN", "").strip()
    telefono = entorno.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    if not (token and telefono):
        return NotificadorSimulado()
    whatsapp = NotificadorWhatsAppCloud(
        token,
        telefono,
        plantilla=entorno.get("WHATSAPP_PLANTILLA", "").strip() or "recordatorio_control",
        idioma=entorno.get("WHATSAPP_IDIOMA", "").strip() or "es",
        version_api=entorno.get("WHATSAPP_API_VERSION", "").strip() or "v21.0",
        cliente=cliente,
    )
    url_sms = entorno.get("SMS_API_URL", "").strip()
    if not url_sms:
        return whatsapp
    sms = NotificadorSMS(
        url_sms, entorno.get("SMS_API_TOKEN", "").strip(), entorno.get("SMS_REMITENTE", "").strip(), cliente=cliente
    )
    return NotificadorConRespaldo(whatsapp, sms)
