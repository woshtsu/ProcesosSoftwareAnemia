"""Autenticación delegada al puerto de identidad, sin conocer Supabase ni HTTP."""

import base64
import hashlib
import json
import os
import time
from typing import NamedTuple

from app.domain.model.autenticacion import Sesion, UsuarioAutenticado
from app.ports.inbound.sesiones import GestionarSesiones
from app.ports.outbound.proveedor_identidad import ProveedorIdentidad

MAX_CACHE_SIZE_DEFAULT = 1000
TTL_CACHE_DEFAULT = 60.0


def _obtener_ttl_configurado(ttl: float | None = None) -> float:
    if ttl is not None:
        return float(ttl)
    env_ttl = os.getenv("AUTH_CACHE_TTL_SEGUNDOS")
    if env_ttl is not None and env_ttl.strip():
        try:
            return float(env_ttl)
        except ValueError:
            return TTL_CACHE_DEFAULT
    return TTL_CACHE_DEFAULT


def _expiracion_jwt(token: str) -> float | None:
    partes = token.split(".")
    if len(partes) != 3:
        return None
    try:
        payload_b64 = partes[1]
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload_b64.encode("ascii")))
        exp = claims.get("exp")
        if isinstance(exp, (int, float)):
            return float(exp)
    except Exception:
        return None
    return None


class _EntradaCache(NamedTuple):
    usuario: UsuarioAutenticado
    expira_en: float  # time.monotonic()


class ServicioSesion(GestionarSesiones):
    def __init__(
        self,
        proveedor: ProveedorIdentidad,
        ttl_segundos: float | None = None,
        max_size: int = MAX_CACHE_SIZE_DEFAULT,
    ):
        self.proveedor = proveedor
        self.ttl_segundos = _obtener_ttl_configurado(ttl_segundos)
        self.max_size = max(1, max_size)
        self._cache: dict[str, _EntradaCache] = {}

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def aclose(self) -> None:
        if hasattr(self.proveedor, "aclose"):
            await self.proveedor.aclose()

    async def iniciar(self, email: str, password: str) -> Sesion:
        return await self.proveedor.iniciar(email.strip(), password)

    async def renovar(self, refresh_token: str) -> Sesion:
        return await self.proveedor.renovar(refresh_token)

    async def usuario(self, access_token: str) -> UsuarioAutenticado:
        if self.ttl_segundos <= 0:
            return await self.proveedor.usuario(access_token)

        clave = self._hash_token(access_token)
        ahora = time.monotonic()
        entrada = self._cache.get(clave)
        if entrada is not None:
            if ahora < entrada.expira_en:
                return entrada.usuario
            self._cache.pop(clave, None)

        usuario = await self.proveedor.usuario(access_token)

        ttl_efectivo = self.ttl_segundos
        jwt_exp = _expiracion_jwt(access_token)
        if jwt_exp is not None:
            restante_real = jwt_exp - time.time()
            if restante_real <= 0:
                return usuario
            ttl_efectivo = min(self.ttl_segundos, restante_real)

        if ttl_efectivo > 0:
            if len(self._cache) >= self.max_size:
                expiradas = [k for k, v in self._cache.items() if ahora >= v.expira_en]
                for k in expiradas:
                    self._cache.pop(k, None)
                while len(self._cache) >= self.max_size:
                    self._cache.pop(next(iter(self._cache)))

            self._cache[clave] = _EntradaCache(usuario=usuario, expira_en=ahora + ttl_efectivo)

        return usuario

    async def salir(self, access_token: str) -> None:
        clave = self._hash_token(access_token)
        self._cache.pop(clave, None)
        await self.proveedor.salir(access_token)
