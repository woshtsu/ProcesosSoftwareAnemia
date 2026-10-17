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
