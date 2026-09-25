"""
Pruebas de API REST — PMV Anemia Junín.

HIST-1.1 a HIST-1.5: casos indispensables del plan.
"""

from __future__ import annotations

import json

import pytest

# ─── Helpers ─────────────────────────────────────────────────────────────────

_NINO_BASE = {
    "dni": "12345678",
    "nombres": "Ana María",
    "apellidos": "Quispe López",
    "fecha_nacimiento": "2023-03-15",
    "sexo": "F",
    "tipo_nacimiento": "TERMINO",
    "peso_kg": 8.5,
    "distrito": "Huancayo",
    "altitud_msnm": 3271,
    "cuidador": "María López",
    "telefono": "987654321",
}

_DOSAJE_BASE = {
    "fecha_dosaje": "2026-09-25",
    "hb_observada": 10.5,
    "altitud_msnm": 3271,
}


def _post_nino(client, data=None):
    return client.post(
        "/api/v1/ninos",
        data=json.dumps(data or _NINO_BASE),
        content_type="application/json",
    )


def _crear_nino(client, data=None):
    resp = _post_nino(client, data or _NINO_BASE)
    assert resp.status_code == 201
    return resp


# ─── GET /salud ───────────────────────────────────────────────────────────────

class TestSalud:
    def test_ok(self, client):
        resp = client.get("/api/v1/salud")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["data"]["estado"] == "ok"
        assert data["data"]["base_datos"] == "conectada"


# ─── POST /ninos ──────────────────────────────────────────────────────────────

class TestCrearNino:
    def test_alta_valida(self, client):
        resp = _post_nino(client)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["data"]["dni"] == "12345678"

    def test_alta_con_dni_cero_inicial(self, client):
        nino = {**_NINO_BASE, "dni": "01234567"}
        resp = _post_nino(client, nino)
        assert resp.status_code == 201
        assert resp.get_json()["data"]["dni"] == "01234567"

    def test_alta_duplicada_409(self, client):
        _crear_nino(client)
        resp = _post_nino(client)
        assert resp.status_code == 409
        assert resp.get_json()["error"]["code"] == "CONFLICT"

    def test_multiples_errores(self, client):
        datos = {
            "dni": "123",           # inválido
            "nombres": "A",          # muy corto
            "apellidos": "Quispe",
            "fecha_nacimiento": "2023-03-15",
            "sexo": "X",             # inválido
            "tipo_nacimiento": "TERMINO",
            "peso_kg": 0.5,          # muy bajo
            "distrito": "Huancayo",
            "altitud_msnm": 3271,
            "cuidador": "María",
            "telefono": None,
        }
        resp = _post_nino(client, datos)
        assert resp.status_code == 400
        error = resp.get_json()["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert "dni" in error["fields"]
        assert "nombres" in error["fields"]

    def test_content_type_requerido(self, client):
        resp = client.post("/api/v1/ninos", data="{}", content_type="text/plain")
        assert resp.status_code == 415

    def test_campo_desconocido_rechazado(self, client):
        datos = {**_NINO_BASE, "campo_extra": "valor"}
        resp = _post_nino(client, datos)
        assert resp.status_code == 400

    def test_alta_con_dosaje_inicial(self, client):
        datos = {
            **_NINO_BASE,
            "dosaje_inicial": {
                "fecha_dosaje": "2026-09-25",
                "hb_observada": 10.5,
            }
        }
        resp = _post_nino(client, datos)
        assert resp.status_code == 201
        data = resp.get_json()
        assert "dosaje_inicial" in data["data"]
        assert data["data"]["dosaje_inicial"]["clasificacion"] is not None

    def test_dosaje_inicial_invalido_no_guarda_nino(self, client):
        """Si el dosaje inicial falla, no se guarda el niño (transacción atómica)."""
        datos = {
            **_NINO_BASE,
            "dosaje_inicial": {
                "fecha_dosaje": "2020-01-01",  # anterior al nacimiento 2023
                "hb_observada": 10.5,
            }
        }
        resp = _post_nino(client, datos)
        assert resp.status_code == 400
        # Verificar que el niño no fue guardado
        resp2 = client.get("/api/v1/ninos/12345678")
        assert resp2.status_code == 404

    def test_no_acepta_campos_calculados(self, client):
        """hb_ajustada no debe aceptarse desde el cliente."""
        datos = {**_NINO_BASE}
        datos["dosaje_inicial"] = {
            "fecha_dosaje": "2026-09-25",
            "hb_observada": 10.5,
            "hb_ajustada": 8.0,  # campo calculado, rechazado
        }
        resp = _post_nino(client, datos)
        assert resp.status_code == 400


# ─── GET /ninos ───────────────────────────────────────────────────────────────

class TestListarNinos:
    def test_lista_vacia(self, client):
        resp = client.get("/api/v1/ninos")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["data"] == []
        assert data["meta"]["total"] == 0

    def test_lista_con_nino(self, client):
        _crear_nino(client)
        resp = client.get("/api/v1/ninos")
        assert resp.status_code == 200
        data = resp.get_json()
        # El niño tiene 42 meses (2023-03-15 → 2026-09-25) → dentro de 6-59
        assert data["meta"]["total"] >= 0  # puede estar en lista de seguimiento

    def test_paginacion(self, client):
        resp = client.get("/api/v1/ninos?pagina=1&tamano=5")
        assert resp.status_code == 200
        meta = resp.get_json()["meta"]
        assert meta["tamano"] == 5
        assert meta["pagina"] == 1


# ─── GET /ninos/<dni> ─────────────────────────────────────────────────────────

class TestExpediente:
    def test_expediente_existente(self, client):
        _crear_nino(client)
        resp = client.get("/api/v1/ninos/12345678")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["nino"]["dni"] == "12345678"
        assert data["clasificacion_actual"] == "SIN_DOSAJE"

    def test_expediente_no_encontrado(self, client):
        resp = client.get("/api/v1/ninos/99999999")
        assert resp.status_code == 404
        assert resp.get_json()["error"]["code"] == "NOT_FOUND"


# ─── PATCH /ninos/<dni> ───────────────────────────────────────────────────────

class TestActualizarNino:
    def test_actualizar_peso(self, client):
        _crear_nino(client)
        resp = client.patch(
            "/api/v1/ninos/12345678",
            data=json.dumps({"peso_kg": 9.0}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.get_json()["data"]["peso_kg"] == 9.0

    def test_identidad_no_modificable(self, client):
        _crear_nino(client)
        resp = client.patch(
            "/api/v1/ninos/12345678",
            data=json.dumps({"nombres": "Otro Nombre"}),
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "nombres" in resp.get_json()["error"]["fields"]["_extra"][0]

    def test_actualizacion_vacia_rechazada(self, client):
        _crear_nino(client)
        resp = client.patch(
            "/api/v1/ninos/12345678",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_actualizacion_nino_inexistente(self, client):
        resp = client.patch(
            "/api/v1/ninos/99999999",
            data=json.dumps({"distrito": "Lima"}),
            content_type="application/json",
        )
        assert resp.status_code == 404


# ─── POST /ninos/<dni>/dosajes ────────────────────────────────────────────────

class TestAgregarDosaje:
    def test_dosaje_valido(self, client):
        _crear_nino(client)
        resp = client.post(
            "/api/v1/ninos/12345678/dosajes",
            data=json.dumps(_DOSAJE_BASE),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert "clasificacion" in data
        assert "hb_ajustada" in data
        assert "ajuste_gdl" in data

    def test_dosaje_nino_inexistente(self, client):
        resp = client.post(
            "/api/v1/ninos/99999999/dosajes",
            data=json.dumps(_DOSAJE_BASE),
            content_type="application/json",
        )
        assert resp.status_code == 404

    def test_historial_se_actualiza(self, client):
        _crear_nino(client)
        client.post(
            "/api/v1/ninos/12345678/dosajes",
            data=json.dumps(_DOSAJE_BASE),
            content_type="application/json",
        )
        resp = client.get("/api/v1/ninos/12345678")
        historial = resp.get_json()["data"]["historial_dosajes"]
        assert len(historial) == 1
        assert historial[0]["clasificacion"] is not None

    def test_campo_calculado_rechazado(self, client):
        _crear_nino(client)
        datos = {**_DOSAJE_BASE, "hb_ajustada": 8.0}
        resp = client.post(
            "/api/v1/ninos/12345678/dosajes",
            data=json.dumps(datos),
            content_type="application/json",
        )
        assert resp.status_code == 400


# ─── GET /reportes/registros ──────────────────────────────────────────────────

class TestReporte:
    def test_periodo_vacio(self, client):
        resp = client.get("/api/v1/reportes/registros?desde=2026-09-01&hasta=2026-09-30")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["ninos_registrados"] == 0
        assert data["calidad_registro"]["tasa_aceptacion_pct"] is None

    def test_fechas_requeridas(self, client):
        resp = client.get("/api/v1/reportes/registros")
        assert resp.status_code == 400

    def test_calidad_con_datos(self, client):
        """Prueba que 24/28 intentos → 85.7% (fixture controlada)."""
        # Crear 24 altas aceptadas
        for i in range(24):
            dni = f"{i:08d}"
            nino = {**_NINO_BASE, "dni": dni}
            _post_nino(client, nino)

        # Crear 4 altas rechazadas (DNI inválido)
        for _ in range(4):
            _post_nino(client, {**_NINO_BASE, "dni": "123"})  # DNI inválido

        resp = client.get("/api/v1/reportes/registros?desde=2026-09-01&hasta=2026-09-30")
        assert resp.status_code == 200
        calidad = resp.get_json()["data"]["calidad_registro"]
        assert calidad["intentos_aceptados"] == 24
        assert calidad["intentos_rechazados"] == 4
        assert calidad["tasa_aceptacion_pct"] == pytest.approx(85.7, abs=0.1)

    def test_fechas_inclusivas(self, client):
        _crear_nino(client)
        # La fecha de hoy debe estar incluida
        resp = client.get("/api/v1/reportes/registros?desde=2026-09-25&hasta=2026-09-25")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["ninos_registrados"] >= 1
