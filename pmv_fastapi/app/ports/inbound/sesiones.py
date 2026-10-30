"""Casos de uso de autenticación de la aplicación."""

from typing import Protocol

from app.domain.model.autenticacion import Sesion, UsuarioAutenticado


class GestionarSesiones(Protocol):
    async def iniciar(self, email: str, password: str) -> Sesion: ...

    async def renovar(self, refresh_token: str) -> Sesion: ...

    async def usuario(self, access_token: str) -> UsuarioAutenticado: ...

    async def salir(self, access_token: str) -> None: ...
