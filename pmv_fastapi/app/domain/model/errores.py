"""Errores del dominio. No dependen de ningún framework."""

from dataclasses import dataclass, field


@dataclass
class ErrorCampo:
    campo: str
    mensaje: str


@dataclass
class ErrorValidacion(Exception):
    """Uno o más datos no cumplen las reglas del dominio."""

    errores: list[ErrorCampo] = field(default_factory=list)

    def __str__(self) -> str:
        return "; ".join(f"{e.campo}: {e.mensaje}" for e in self.errores)


class RegistroDuplicado(Exception):
    """Ya existe un niño registrado con el mismo DNI."""


class NoEncontrado(Exception):
    """El recurso solicitado no existe."""


class ConflictoAsistencia(Exception):
    """El control ya tiene una asistencia registrada o ya está cumplido (HIST-2.4)."""


class ConflictoVisita(Exception):
    """El niño ya tiene una visita domiciliaria registrada en esa fecha (VIS-3.5)."""


class ConflictoYaResuelto(Exception):
    """El conflicto de sincronización ya fue resuelto y no admite otra resolución (HIST-3.3)."""


class ConflictoBarrera(Exception):
    """El niño ya tiene registrada esa barrera (mismo tipo, fecha y fuente) (HIST-4.3)."""

    def __init__(self, mensaje: str, id_existente: str):
        super().__init__(mensaje)
        self.id_existente = id_existente


class ConflictoRecordatorio(Exception):
    """Ya existe un recordatorio para ese niño, control y tipo (HIST-4.1)."""


class ConflictoRespuesta(Exception):
    """El recordatorio ya tiene una respuesta del tutor registrada (HIST-4.2)."""


class FirmaInvalida(Exception):
    """La notificación del webhook no trae una firma válida (HIST-4.2)."""


class WebhookNoConfigurado(Exception):
    """El webhook no puede recibir eventos porque no se configuró el secreto con que se valida su firma (ADR-014)."""
