"""Identidad y sesión independientes del proveedor de autenticación."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class UsuarioAutenticado:
    id: str
    email: str


@dataclass(frozen=True)
class Sesion:
    usuario: UsuarioAutenticado
    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    expires_in: int = 3600


class SesionInvalida(Exception):
    """Credenciales o sesión rechazadas por el proveedor."""


class AutenticacionNoDisponible(Exception):
    """Proveedor sin configurar, respuesta inválida o fallo temporal."""
