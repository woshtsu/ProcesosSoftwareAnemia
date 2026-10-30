"""Puertos de entrada: recordatorios de control, respuesta del tutor y webhook de WhatsApp (HIST-4.1 y HIST-4.2)."""

from datetime import date
from typing import Protocol

from app.domain.model.notificacion import (
    EventosWebhook,
    MetricasRecordatorios,
    ResultadoGeneracion,
    ResultadoRespuesta,
    ResumenWebhook,
    VistaRecordatorio,
)


class GenerarRecordatorios(Protocol):
    def generar_recordatorios(self, usuario: str, establecimiento: str | None = None) -> ResultadoGeneracion:
        """Lote del día: recuerda los controles próximos, de hoy y vencidos que aún no tienen recordatorio."""
        ...


class ConsultarRecordatorios(Protocol):
    def listar_recordatorios(
        self, estado: str | None = None, desde: date | None = None, nino_id: str | None = None, limite: int = 200
    ) -> list[VistaRecordatorio]: ...

    def metricas_recordatorios(self, desde: date | None = None, hasta: date | None = None) -> MetricasRecordatorios: ...


class RegistrarRespuestaRecordatorio(Protocol):
    def registrar_respuesta(self, recordatorio_id: str, datos: dict, usuario: str) -> ResultadoRespuesta:
        """``datos``: respuesta (CONFIRMA, NO_PUEDE o REPROGRAMAR), fecha_reprogramada y, con NO_PUEDE, barrera."""
        ...


class ProcesarNotificacionesWhatsApp(Protocol):
    def verificar_suscripcion(self, modo: str | None, token: str | None) -> bool:
        """Verificación (GET) que hace Meta al registrar el webhook con ``WHATSAPP_VERIFY_TOKEN``."""
        ...

    def procesar_webhook(self, cuerpo: bytes, firma: str | None) -> ResumenWebhook:
        """Aplica los estados de entrega y las respuestas de una notificación de WhatsApp. Siempre exige la firma
        ``X-Hub-Signature-256`` (FirmaInvalida si no es válida) y falla cerrado: sin ``WHATSAPP_APP_SECRET``
        configurado lanza WebhookNoConfigurado y no procesa nada; ErrorValidacion si el cuerpo no es un JSON."""
        ...

    def procesar_eventos(self, eventos: EventosWebhook) -> ResumenWebhook:
        """Aplica los estados de entrega y las respuestas ya extraídos de la notificación."""
        ...
