"""Notificador SMS de respaldo: simulado o mediante un proveedor HTTP configurable (ADR-014).

Sin ``url`` es simulado (ENVIADO_SIMULADO). Con ``url`` envía un POST JSON ``{"to", "from", "message"}`` con
``Authorization: Bearer`` (contrato genérico: se adapta al proveedor elegido); cualquier respuesta 2xx cuenta como
aceptada y el identificador sale de ``id`` o ``message_id`` si el proveedor lo devuelve.
"""

import uuid

import httpx

from app.domain.model.notificacion import CanalEnvio, EstadoRecordatorio, MensajeSaliente, ResultadoEnvio


class NotificadorSMS:
    def __init__(
        self,
        url: str = "",
        token: str = "",
        remitente: str = "",
        cliente: httpx.Client | None = None,
    ):
        self.url = url
        self.token = token
        self.remitente = remitente
        self.cliente = cliente or httpx.Client(timeout=10.0)

    @property
    def simulado(self) -> bool:
        return not self.url

    def enviar(self, mensaje: MensajeSaliente) -> ResultadoEnvio:
        if self.simulado:
            return ResultadoEnvio(True, CanalEnvio.SMS, EstadoRecordatorio.ENVIADO_SIMULADO, f"sim-sms-{uuid.uuid4()}")
        cuerpo = {"to": f"+51{mensaje.destino}", "from": self.remitente, "message": mensaje.texto}
        cabeceras = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        try:
            r = self.cliente.post(self.url, json=cuerpo, headers=cabeceras)
        except httpx.HTTPError as e:
            return self._fallo(f"SMS: sin respuesta del proveedor ({type(e).__name__}).")
        if not r.is_success:
            return self._fallo(f"SMS: error {r.status_code}.")
        try:
            datos = r.json()
        except ValueError:
            datos = {}
        identificador = (datos.get("id") or datos.get("message_id")) if isinstance(datos, dict) else None
        return ResultadoEnvio(
            True, CanalEnvio.SMS, EstadoRecordatorio.ENVIADO, str(identificador) if identificador else None
        )

    @staticmethod
    def _fallo(error: str) -> ResultadoEnvio:
        return ResultadoEnvio(False, CanalEnvio.SMS, EstadoRecordatorio.FALLIDO, error=error)
