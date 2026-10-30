"""Autenticación delegada al puerto de identidad, sin conocer Supabase ni HTTP."""

from app.domain.model.autenticacion import Sesion, UsuarioAutenticado
from app.ports.inbound.sesiones import GestionarSesiones
from app.ports.outbound.proveedor_identidad import ProveedorIdentidad


class ServicioSesion(GestionarSesiones):
    def __init__(self, proveedor: ProveedorIdentidad):
        self.proveedor = proveedor

    async def iniciar(self, email: str, password: str) -> Sesion:
        return await self.proveedor.iniciar(email.strip(), password)

    async def renovar(self, refresh_token: str) -> Sesion:
        return await self.proveedor.renovar(refresh_token)

    async def usuario(self, access_token: str) -> UsuarioAutenticado:
        return await self.proveedor.usuario(access_token)

    async def salir(self, access_token: str) -> None:
        await self.proveedor.salir(access_token)
