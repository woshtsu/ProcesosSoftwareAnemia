"""Composición con respaldo: si el canal principal (WhatsApp) falla, el mismo mensaje se reintenta por el respaldo."""

from dataclasses import replace

from app.domain.model.notificacion import MensajeSaliente, ResultadoEnvio
from app.ports.outbound.notificador import Notificador


class NotificadorConRespaldo:
    def __init__(self, principal: Notificador, respaldo: Notificador):
        self.principal = principal
        self.respaldo = respaldo

    def enviar(self, mensaje: MensajeSaliente) -> ResultadoEnvio:
        resultado = self.principal.enviar(mensaje)
        if resultado.exito:
            return resultado
        reintento = self.respaldo.enviar(mensaje)
        aviso = f"{resultado.error} Se reintentó por {reintento.canal.value}."
        # Si también falla el respaldo se conserva el motivo de ambos; si funciona, el motivo queda como aviso.
        error = aviso if reintento.exito else f"{aviso} {reintento.error}"
        return replace(reintento, error=error)
