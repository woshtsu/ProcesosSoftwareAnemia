"""Login completo en navegador con Supabase simulado; no utiliza cuentas reales."""

import socket
import threading
import time
from pathlib import Path

import httpx
import pytest
import uvicorn

from app.adapters.outbound.supabase_auth import SupabaseAuth
from app.application.servicio_sesion import ServicioSesion
from app.main import crear_app

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect
pytestmark = pytest.mark.e2e


@pytest.fixture
def servidor_auth(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "false")
    user = {"id": "usuario-prueba", "email": "enfermeria@example.test", "email_confirmed_at": "2026-10-23"}

    def responder(req):
        if req.url.path.endswith("/token"):
            import json

            if json.loads(req.content).get("password") != "correcta":
                return httpx.Response(400)
            return httpx.Response(
                200,
                json={"access_token": "access-e2e", "refresh_token": "refresh-e2e", "expires_in": 3600, "user": user},
            )
        if req.url.path.endswith("/logout"):
            return httpx.Response(204)
        return httpx.Response(200, json=user)

    app = crear_app(f"sqlite:///{tmp_path}/login.db", auth_mode="supabase")
    app.state.auth_configurado = True
    app.state.sesiones = ServicioSesion(
        SupabaseAuth("https://example.test", "publica", transport=httpx.MockTransport(responder))
    )
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    server = uvicorn.Server(uvicorn.Config(app, log_level="error"))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    assert server.started
    try:
        yield f"http://127.0.0.1:{sock.getsockname()[1]}"
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        sock.close()
        app.state.repositorio.engine.dispose()


@pytest.mark.parametrize("viewport", [{"width": 1366, "height": 900}, {"width": 390, "height": 844}])
def test_login_error_acceso_recarga_y_cierre(servidor_auth, viewport):
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport=viewport, locale="es-PE")
        page = context.new_page()
        try:
            page.goto(servidor_auth)
            expect(page.locator("#login-enviar")).to_be_enabled()
            expect(page.locator("#aplicacion")).to_be_hidden()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            destino = Path(__file__).resolve().parents[3] / "diagramas/_build/auth"
            destino.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(destino / f"login-{viewport['width']}.png"), full_page=True)
            page.fill("#login-email", "enfermeria@example.test")
            page.fill("#login-password", "incorrecta")
            page.click("#login-enviar")
            expect(page.locator("#login-error")).to_contain_text("Correo o contraseña")
            page.fill("#login-password", "correcta")
            page.click("#login-enviar")
            expect(page.locator("#aplicacion")).to_be_visible()
            expect(page.locator("#usuario-autenticado")).to_have_text("enfermeria@example.test")
            expect(page.locator("#usuario")).to_be_hidden()
            assert "aj_access" not in page.evaluate("document.cookie")
            assert not page.evaluate("Object.values(localStorage).some(v => v.includes('access-e2e'))")
            page.reload()
            expect(page.locator("#aplicacion")).to_be_visible()
            page.click("#cerrar-sesion")
            expect(page.locator("#form-login")).to_be_visible()
            expect(page.locator("#aplicacion")).to_be_hidden()
            assert not any(c["name"] in {"aj_access", "aj_refresh"} for c in context.cookies())
        finally:
            browser.close()
