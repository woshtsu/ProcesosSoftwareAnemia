"""Puerto de salida: envío de mensajes de recordatorio por un canal (HIST-4.1, ADR-014).

Los adaptadores (simulado, WhatsApp Cloud, SMS y la composición con respaldo) implementan este contrato. Un fallo del
canal no lanza excepciones: se informa en ``ResultadoEnvio`` para que el caso de uso lo registre.
"""

from typing import Protocol

from app.domain.model.notificacion import MensajeSaliente, ResultadoEnvio


class Notificador(Protocol):
    def enviar(self, mensaje: MensajeSaliente) -> ResultadoEnvio: ...
