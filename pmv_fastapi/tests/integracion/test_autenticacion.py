"""Supabase Auth simulado por HTTP: acceso, cookies, renovación, CSRF y auditoría."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.adapters.outbound.supabase_auth import SupabaseAuth
from app.application.servicio_sesion import ServicioSesion
from app.domain.model.autenticacion import AutenticacionNoDisponible, SesionInvalida
from app.main import crear_app
from tests.conftest import RelojFijo, cuerpo_registro

CSRF = {"X-CSRF-Protection": "1"}
USER = {
    "id": "7cf4a660-bb6f-4c6d-a6cb-b1bfb1092380",
    "email": "enfermeria@example.test",
    "email_confirmed_at": "2026-10-23T10:00:00Z",
    "is_anonymous": False,
}
TOKEN = {"access_token": "access-valido", "refresh_token": "refresh-valido", "expires_in": 3600, "user": USER}


@pytest.fixture
def auth_cliente(tmp_path, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://proyecto.example.test")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_prueba")
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "false")
    calls, estado = [], {"fallo": False}

    def responder(req):
        calls.append(req)
        assert req.headers["apikey"] == "sb_publishable_prueba"
        if estado["fallo"]:
            return httpx.Response(503)
        if req.url.path.endswith("/token"):
            import json

            data = json.loads(req.content)
            if data.get("password") == "correcta" or data.get("refresh_token") == "refresh-valido":
                return httpx.Response(200, json=TOKEN)
            return httpx.Response(400, json={"msg": "invalid credentials"})
        if req.headers.get("Authorization") != "Bearer access-valido":
            return httpx.Response(401)
        if req.url.path.endswith("/logout"):
            return httpx.Response(204)
        return httpx.Response(200, json=USER)

    app = crear_app(f"sqlite:///{tmp_path}/auth.db", reloj=RelojFijo(), auth_mode="supabase")
    app.state.sesiones = ServicioSesion(
        SupabaseAuth("https://proyecto.example.test", "sb_publishable_prueba", transport=httpx.MockTransport(responder))
    )
    with TestClient(app) as cliente:
        yield cliente, calls, estado
    app.state.repositorio.engine.dispose()


def ingresar(c):
    return c.post("/api/auth/login", json={"email": USER["email"], "password": "correcta"}, headers=CSRF)


def test_sin_configuracion_falla_cerrado_por_defecto(tmp_path, monkeypatch):
    monkeypatch.delenv("AUTH_MODE")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    app = crear_app(f"sqlite:///{tmp_path}/sin-config.db")
    with TestClient(app) as c:
        assert c.get("/api/auth/config").json() == {"modo": "supabase", "configurado": False}
        assert c.get("/").status_code == 200
        assert c.get("/api/ninos").status_code == 401
        assert ingresar(c).status_code == 503
    app.state.repositorio.engine.dispose()


@pytest.mark.parametrize(
    "path",
    [
        "/api/ninos",
        "/api/agenda",
        "/api/alertas/resumen",
        "/api/alertas/controles-vencidos",
        "/api/reportes/periodo?formato=csv",
    ],
)
def test_lecturas_clinicas_exigen_sesion(auth_cliente, path):
    c, calls, _ = auth_cliente
    r = c.get(path, headers={"X-Usuario": "administrador"})
    assert r.status_code == 401 and not calls
    assert r.headers["Cache-Control"] == "no-store"


def test_login_cookies_sin_tokens_en_respuesta(auth_cliente):
    c, _, _ = auth_cliente
    r = ingresar(c)
    assert r.status_code == 200
    assert r.json() == {"usuario": {"id": USER["id"], "email": USER["email"]}}
    assert "access-valido" not in r.text and "refresh-valido" not in r.text
    for cookie in r.headers.get_list("set-cookie"):
        assert "HttpOnly" in cookie and "SameSite=strict" in cookie and "Path=/api" in cookie
    assert c.get("/api/ninos").status_code == 200
    assert c.get("/api/auth/session").json()["usuario"]["id"] == USER["id"]


def test_credenciales_incorrectas_y_campos_vacios(auth_cliente):
    c, _, _ = auth_cliente
    r = c.post("/api/auth/login", json={"email": USER["email"], "password": "incorrecta"}, headers=CSRF)
    assert r.status_code == 401 and not c.cookies
    r = c.post("/api/auth/login", json={"email": "", "password": ""}, headers=CSRF)
    assert r.status_code == 422 and "incorrecta" not in r.text


def test_csrf_y_origen_ajeno_se_rechazan(auth_cliente):
    c, _, _ = auth_cliente
    assert c.post("/api/auth/login", json={"email": USER["email"], "password": "correcta"}).status_code == 403
    assert ingresar(c).status_code == 200
    r = c.post("/api/ninos", json=cuerpo_registro(), headers={**CSRF, "Origin": "https://ajeno.example"})
    assert r.status_code == 403
    assert c.post("/api/auth/logout").status_code == 403


def test_auditoria_usa_uuid_verificado_ignora_usuario_cliente(auth_cliente):
    c, _, _ = auth_cliente
    ingresar(c)
    r = c.post("/api/ninos", json=cuerpo_registro(), headers={**CSRF, "X-Usuario": "suplantado"})
    assert r.status_code == 201
    assert r.json()["registrado_por"] == USER["id"]


def test_sesion_renueva_access_vencido(auth_cliente):
    c, calls, _ = auth_cliente
    c.cookies.set("aj_access", "vencido", path="/api")
    c.cookies.set("aj_refresh", "refresh-valido", path="/api")
    assert c.get("/api/ninos").status_code == 401
    r = c.get("/api/auth/session")
    assert r.status_code == 200
    assert any(req.url.params.get("grant_type") == "refresh_token" for req in calls)
    assert "aj_access=access-valido" in r.headers["set-cookie"]


def test_refresh_rechazado_borra_cookies(auth_cliente):
    c, _, _ = auth_cliente
    c.cookies.set("aj_refresh", "falso", path="/api")
    r = c.get("/api/auth/session")
    assert r.status_code == 401
    assert "Max-Age=0" in r.headers["set-cookie"]


def test_logout_revoca_y_borra_cookies(auth_cliente):
    c, calls, _ = auth_cliente
    ingresar(c)
    r = c.post("/api/auth/logout", headers=CSRF)
    assert r.status_code == 200 and not c.cookies
    assert calls[-1].url.params.get("scope") == "local"
    assert c.get("/api/ninos").status_code == 401


def test_fallo_proveedor_no_se_convierte_en_acceso_anonimo(auth_cliente):
    c, _, estado = auth_cliente
    ingresar(c)
    estado["fallo"] = True
    assert c.get("/api/ninos").status_code == 503
    assert c.get("/api/auth/session").status_code == 503
    r = c.post("/api/auth/logout", headers=CSRF)
    assert r.status_code == 503 and not c.cookies


def test_cookies_secure_en_https(auth_cliente):
    c, _, _ = auth_cliente
    c.app.state.cookie_secure = True
    r = ingresar(c)
    assert all("Secure" in cookie for cookie in r.headers.get_list("set-cookie"))


@pytest.mark.anyio
@pytest.mark.parametrize("usuario", [{**USER, "email_confirmed_at": None}, {**USER, "is_anonymous": True}, {}])
async def test_rechaza_usuario_sin_confirmar_o_anonimo(usuario):
    adapter = SupabaseAuth(
        "https://example.test", "publica", transport=httpx.MockTransport(lambda r: httpx.Response(200, json=usuario))
    )
    with pytest.raises(SesionInvalida):
        await adapter.usuario("token")


@pytest.mark.anyio
async def test_timeout_y_respuesta_malformada():
    def timeout(req):
        raise httpx.ConnectTimeout("no disponible")

    for transport in [httpx.MockTransport(timeout), httpx.MockTransport(lambda r: httpx.Response(200, text="no-json"))]:
        adapter = SupabaseAuth("https://example.test", "publica", transport=transport)
        with pytest.raises(AutenticacionNoDisponible):
            await adapter.iniciar("correo@example.test", "clave")


@pytest.mark.anyio
async def test_respuesta_token_incompleta_y_sin_configurar():
    adapter = SupabaseAuth(
        "https://example.test", "publica", transport=httpx.MockTransport(lambda r: httpx.Response(200, json={}))
    )
    with pytest.raises(AutenticacionNoDisponible):
        await adapter.iniciar("correo@example.test", "clave")
    with pytest.raises(AutenticacionNoDisponible):
        await SupabaseAuth("", "").usuario("token")


def test_modo_invalido_no_arranca(tmp_path):
    with pytest.raises(ValueError, match="AUTH_MODE"):
        crear_app(f"sqlite:///{tmp_path}/invalida.db", auth_mode="invalido")
