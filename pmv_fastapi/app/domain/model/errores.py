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
