"""Notificador simulado: no envía nada; registra el mensaje como ENVIADO_SIMULADO (demo y pruebas, ADR-014)."""

import uuid

from app.domain.model.notificacion import CanalEnvio, EstadoRecordatorio, MensajeSaliente, ResultadoEnvio


class NotificadorSimulado:
    def enviar(self, mensaje: MensajeSaliente) -> ResultadoEnvio:
        return ResultadoEnvio(
            exito=True,
            canal=CanalEnvio.SIMULADO,
            estado=EstadoRecordatorio.ENVIADO_SIMULADO,
            id_externo=f"sim-{uuid.uuid4()}",
        )
