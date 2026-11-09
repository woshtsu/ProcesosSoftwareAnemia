"""Pruebas unitarias para la caché en memoria de verificación de sesión (ServicioSesion)."""

import asyncio
import base64
import hashlib
import json
import time

import pytest

from app.application.servicio_sesion import ServicioSesion
from app.domain.model.autenticacion import Sesion, UsuarioAutenticado


class ProveedorIdentidadFalso:
    def __init__(self, usuario_fijo=None):
        self.usuario_fijo = usuario_fijo or UsuarioAutenticado("7cf4a660", "enfermeria@example.test")
        self.llamadas_usuario = 0
        self.llamadas_salir = 0
        self.cerrado = False

    async def iniciar(self, email: str, password: str) -> Sesion:
        return Sesion(self.usuario_fijo, "access-iniciar", "refresh-iniciar", 3600)

    async def renovar(self, refresh_token: str) -> Sesion:
        return Sesion(self.usuario_fijo, "access-renovar", "refresh-renovar", 3600)

    async def usuario(self, access_token: str) -> UsuarioAutenticado:
        self.llamadas_usuario += 1
        return self.usuario_fijo

    async def salir(self, access_token: str) -> None:
        self.llamadas_salir += 1

    async def aclose(self) -> None:
        self.cerrado = True


def crear_jwt(exp_timestamp: int) -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = (
        base64.urlsafe_b64encode(json.dumps({"sub": "7cf4a660", "exp": exp_timestamp}).encode()).decode().rstrip("=")
    )
    return f"{header}.{payload}.fakesignature"


@pytest.mark.anyio
async def test_acierto_de_cache_evita_segunda_llamada_al_proveedor():
    proveedor = ProveedorIdentidadFalso()
    servicio = ServicioSesion(proveedor, ttl_segundos=60.0)

    u1 = await servicio.usuario("token-prueba")
    u2 = await servicio.usuario("token-prueba")

    assert u1 == u2
    assert proveedor.llamadas_usuario == 1


@pytest.mark.anyio
async def test_expiracion_por_ttl_vuelve_a_consultar_al_proveedor():
    proveedor = ProveedorIdentidadFalso()
    servicio = ServicioSesion(proveedor, ttl_segundos=0.05)

    await servicio.usuario("token-expira")
    assert proveedor.llamadas_usuario == 1

    await asyncio.sleep(0.06)
    await servicio.usuario("token-expira")
    assert proveedor.llamadas_usuario == 2


@pytest.mark.anyio
async def test_expiracion_por_jwt_exp_se_respeta_si_es_menor_que_ttl():
    proveedor = ProveedorIdentidadFalso()
    servicio = ServicioSesion(proveedor, ttl_segundos=3600.0)

    # JWT expira en 0.05 s a partir de ahora
    jwt_corto = crear_jwt(int(time.time() + 1))
    await servicio.usuario(jwt_corto)
    assert proveedor.llamadas_usuario == 1

    # La entrada debe existir en caché
    clave = hashlib.sha256(jwt_corto.encode()).hexdigest()
    assert clave in servicio._cache
    # expira_en debe ser acotado por la expiración real del token, no por las 3600 s
    assert servicio._cache[clave].expira_en <= time.monotonic() + 1.1


@pytest.mark.anyio
async def test_token_jwt_ya_vencido_no_se_guarda_en_cache():
    proveedor = ProveedorIdentidadFalso()
    servicio = ServicioSesion(proveedor, ttl_segundos=60.0)

    jwt_vencido = crear_jwt(int(time.time() - 30))
    await servicio.usuario(jwt_vencido)
    assert proveedor.llamadas_usuario == 1
    assert len(servicio._cache) == 0


@pytest.mark.anyio
async def test_logout_invalida_la_entrada_en_cache():
    proveedor = ProveedorIdentidadFalso()
    servicio = ServicioSesion(proveedor, ttl_segundos=60.0)

    await servicio.usuario("token-logout")
    assert proveedor.llamadas_usuario == 1
    clave = hashlib.sha256(b"token-logout").hexdigest()
    assert clave in servicio._cache

    await servicio.salir("token-logout")
    assert proveedor.llamadas_salir == 1
    assert clave not in servicio._cache

    # Al volver a pedir usuario con ese token, consulta al proveedor
    await servicio.usuario("token-logout")
    assert proveedor.llamadas_usuario == 2


@pytest.mark.anyio
async def test_ttl_cero_desactiva_la_cache():
    proveedor = ProveedorIdentidadFalso()
    servicio = ServicioSesion(proveedor, ttl_segundos=0.0)

    await servicio.usuario("token-directo")
    await servicio.usuario("token-directo")
    await servicio.usuario("token-directo")

    assert proveedor.llamadas_usuario == 3
    assert len(servicio._cache) == 0


@pytest.mark.anyio
async def test_tamano_maximo_acotado_descarta_entradas_antiguas():
    proveedor = ProveedorIdentidadFalso()
    servicio = ServicioSesion(proveedor, ttl_segundos=60.0, max_size=2)

    await servicio.usuario("token-1")
    await servicio.usuario("token-2")
    assert len(servicio._cache) == 2

    await servicio.usuario("token-3")
    assert len(servicio._cache) == 2

    # El token 1 (más antiguo) debe haber sido descartado
    clave1 = hashlib.sha256(b"token-1").hexdigest()
    clave3 = hashlib.sha256(b"token-3").hexdigest()
    assert clave1 not in servicio._cache
    assert clave3 in servicio._cache


@pytest.mark.anyio
async def test_token_nunca_se_almacena_en_claro_solo_sha256():
    proveedor = ProveedorIdentidadFalso()
    servicio = ServicioSesion(proveedor, ttl_segundos=60.0)
    token_secreto = "este-es-un-access-token-muy-secreto-123456789"

    await servicio.usuario(token_secreto)

    for k in servicio._cache:
        assert token_secreto not in k
        assert len(k) == 64
        assert k == hashlib.sha256(token_secreto.encode()).hexdigest()


def test_configuracion_por_variable_de_entorno(monkeypatch):
    proveedor = ProveedorIdentidadFalso()

    monkeypatch.setenv("AUTH_CACHE_TTL_SEGUNDOS", "120")
    s1 = ServicioSesion(proveedor)
    assert s1.ttl_segundos == 120.0

    monkeypatch.setenv("AUTH_CACHE_TTL_SEGUNDOS", "0")
    s2 = ServicioSesion(proveedor)
    assert s2.ttl_segundos == 0.0

    monkeypatch.delenv("AUTH_CACHE_TTL_SEGUNDOS", raising=False)
    s3 = ServicioSesion(proveedor)
    assert s3.ttl_segundos == 60.0


@pytest.mark.anyio
async def test_aclose_cierra_proveedor():
    proveedor = ProveedorIdentidadFalso()
    servicio = ServicioSesion(proveedor)
    assert not proveedor.cerrado
    await servicio.aclose()
    assert proveedor.cerrado
