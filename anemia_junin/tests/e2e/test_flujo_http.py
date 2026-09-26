"""
Prueba extremo a extremo (E2E) sin navegador — PMV Anemia Junín.

Levanta la aplicación real en un servidor HTTP (Werkzeug, puerto libre aleatorio),
con CSRF ACTIVO, y recorre el flujo completo del personal de salud mediante
peticiones HTTP reales (urllib + cookies), igual que lo haría un navegador:

    lista vacía → formulario de alta (token CSRF) → alta con dosaje inicial
    → redirección 303 al expediente → nuevo dosaje → lista ordenada → reporte
    → misma información vía API JSON.

Se eligió este enfoque porque Playwright requiere descargar navegadores
(`playwright install`), lo que no siempre es posible en el ambiente del curso.
Si están instalados, el mismo flujo puede automatizarse con pytest-playwright.
"""

from __future__ import annotations

import http.cookiejar
import json
import re
import threading
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import pytest
from werkzeug.serving import make_server

from anemia_junin.bootstrap import crear_app

pytestmark = pytest.mark.e2e


class _SinRedireccion(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # noqa: D401 — devuelve None para no seguir
        return None


@pytest.fixture
def servidor(tmp_path: Path):
    app = crear_app(
        db_path=str(tmp_path / "e2e.db"),
        normativa_path=Path(__file__).parents[2] / "config" / "normativa_v1.json",
        secret_key="clave-e2e",
        testing=False,  # CSRF activo, como en producción
    )
    srv = make_server("127.0.0.1", 0, app, threaded=True)
    hilo = threading.Thread(target=srv.serve_forever, daemon=True)
    hilo.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()
    hilo.join(timeout=5)


class _Navegador:
    """Cliente HTTP mínimo con cookies y sin seguir redirecciones."""

    def __init__(self, base: str) -> None:
        self.base = base
        cookies = urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        self._opener = urllib.request.build_opener(cookies, _SinRedireccion)

    def _abrir(self, req):
        try:
            with self._opener.open(req, timeout=10) as r:
                return r.status, dict(r.headers), r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            with e:  # cierra la respuesta de error (evita ResourceWarning)
                return e.code, dict(e.headers), e.read().decode("utf-8")

    def get(self, ruta: str):
        return self._abrir(urllib.request.Request(self.base + ruta))

    def post_form(self, ruta: str, datos: dict):
        cuerpo = urllib.parse.urlencode(datos).encode()
        return self._abrir(urllib.request.Request(self.base + ruta, data=cuerpo, method="POST"))

    def token(self, ruta: str) -> str:
        _, _, html = self.get(ruta)
        return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def test_flujo_completo_personal_de_salud(servidor):
    nav = _Navegador(servidor)
    hoy = date.today()

    # 1. Lista vacía con aviso académico
    status, _, html = nav.get("/ninos")
    assert status == 200
    assert "Demostración académica con datos sintéticos" in html

    # 2. Alta sin token CSRF → rechazada
    status, _, _ = nav.post_form("/ninos/nuevo", {"dni": "80000001"})
    assert status == 400

    # 3. Alta válida con dosaje inicial (token CSRF real)
    formulario = {
        "csrf_token": nav.token("/ninos/nuevo"),
        "dni": "80000001", "nombres": "Diego", "apellidos": "Condori Ccama",
        "fecha_nacimiento": (hoy - timedelta(days=400)).isoformat(),
        "sexo": "M", "tipo_nacimiento": "TERMINO", "peso_kg": "9.8",
        "distrito": "Chupaca", "altitud_msnm": "3263", "cuidador": "Isabel Ccama",
        "telefono": "912345678", "tiene_dosaje_inicial": "1",
        "fecha_dosaje": hoy.isoformat(), "hb_observada": "11.0",
    }
    status, cabeceras, _ = nav.post_form("/ninos/nuevo", formulario)
    assert status == 303
    assert cabeceras["Location"].endswith("/ninos/80000001")

    # 4. Expediente: 11.0 - 2.1 = 8.9 g/dL en 13 meses → MODERADA
    status, _, html = nav.get("/ninos/80000001")
    assert status == 200
    assert "Condori Ccama, Diego" in html
    assert "MODERADA" in html

    # 5. Alta inválida conserva datos y muestra errores
    status, _, html = nav.post_form(
        "/ninos/nuevo", {**formulario, "csrf_token": nav.token("/ninos/nuevo"), "dni": "8000"}
    )
    assert status == 422
    assert "Debe contener exactamente 8 dígitos" in html

    # 6. Nuevo dosaje → pasa a SIN ANEMIA
    status, _, _ = nav.post_form("/ninos/80000001/dosajes/nuevo", {
        "csrf_token": nav.token("/ninos/80000001/dosajes/nuevo"),
        "fecha_dosaje": hoy.isoformat(), "hb_observada": "13.9", "altitud_msnm": "3263",
    })
    assert status == 303
    _, _, html = nav.get("/ninos/80000001")
    assert "SIN ANEMIA" in html

    # 7. Reporte del periodo con indicador de calidad (1 aceptado, 1 rechazado)
    _, _, html = nav.get(f"/reportes/registros?desde={hoy}&hasta={hoy}")
    assert "50.0%" in html

    # 8. La API JSON expone la misma información
    status, _, cuerpo = nav.get("/api/v1/ninos/80000001")
    datos = json.loads(cuerpo)["data"]
    assert status == 200
    assert datos["clasificacion_actual"] == "SIN_ANEMIA"
    assert len(datos["historial_dosajes"]) == 2


def test_smoke_test_contra_servidor_real(servidor, capsys):
    """El script scripts/smoke_test.py aprueba contra el servidor levantado."""
    import importlib.util

    ruta = Path(__file__).parents[2] / "scripts" / "smoke_test.py"
    spec = importlib.util.spec_from_file_location("smoke_test", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    assert modulo.main(["--url", servidor]) == 0
    assert "RESULTADO: APROBADO" in capsys.readouterr().out
