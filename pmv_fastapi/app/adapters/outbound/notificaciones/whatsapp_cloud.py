"""Notificador de WhatsApp Cloud API (Graph API de Meta), con mensaje de plantilla aprobada (ADR-014).

Solo se activa si existen ``WHATSAPP_TOKEN`` y ``WHATSAPP_PHONE_NUMBER_ID`` (ver ``crear_notificador``). Los mensajes
de iniciativa de la empresa fuera de la ventana de 24 horas deben usar una plantilla aprobada por Meta; la aprobación
puede tardar y es un riesgo documentado del plan (S3-4). Nunca se registra el token ni el cuerpo de la respuesta.
"""

import httpx

from app.domain.model.notificacion import CanalEnvio, EstadoRecordatorio, MensajeSaliente, ResultadoEnvio

URL_GRAPH = "https://graph.facebook.com"


class NotificadorWhatsAppCloud:
    def __init__(
        self,
        token: str,
        phone_number_id: str,
        plantilla: str = "recordatorio_control",
        idioma: str = "es",
        version_api: str = "v21.0",
        cliente: httpx.Client | None = None,
        url_base: str = URL_GRAPH,
    ):
        self.token = token
        self.url = f"{url_base.rstrip('/')}/{version_api}/{phone_number_id}/messages"
        self.plantilla = plantilla
        self.idioma = idioma
        self.cliente = cliente or httpx.Client(timeout=10.0)

    def _cuerpo(self, mensaje: MensajeSaliente) -> dict:
        return {
            "messaging_product": "whatsapp",
            "to": f"51{mensaje.destino}",
            "type": "template",
            "template": {
                "name": self.plantilla or mensaje.plantilla,
                "language": {"code": self.idioma},
                "components": [
                    {"type": "body", "parameters": [{"type": "text", "text": p} for p in mensaje.parametros]}
                ],
            },
        }

    def enviar(self, mensaje: MensajeSaliente) -> ResultadoEnvio:
        try:
            r = self.cliente.post(
                self.url, json=self._cuerpo(mensaje), headers={"Authorization": f"Bearer {self.token}"}
            )
        except httpx.HTTPError as e:
            return self._fallo(f"WhatsApp: sin respuesta del servicio ({type(e).__name__}).")
        try:
            cuerpo = r.json()
        except ValueError:
            cuerpo = {}
        if r.is_success:
            mensajes = cuerpo.get("messages") if isinstance(cuerpo, dict) else None
            id_externo = mensajes[0].get("id") if mensajes and isinstance(mensajes[0], dict) else None
            if id_externo:
                return ResultadoEnvio(True, CanalEnvio.WHATSAPP, EstadoRecordatorio.ENVIADO, id_externo)
            return self._fallo("WhatsApp: la respuesta no trae el identificador del mensaje.")
        error = cuerpo.get("error") if isinstance(cuerpo, dict) else None
        detalle = f" {error.get('code')}: {error.get('message')}" if isinstance(error, dict) else ""
        return self._fallo(f"WhatsApp: error {r.status_code}.{detalle}"[:300])

    @staticmethod
    def _fallo(error: str) -> ResultadoEnvio:
        return ResultadoEnvio(False, CanalEnvio.WHATSAPP, EstadoRecordatorio.FALLIDO, error=error)
