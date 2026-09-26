"""
Prueba de contrato OpenAPI — PMV Anemia Junín.

1. Cada ruta/método de openapi.yaml existe en Flask y viceversa (bajo /api/v1).
2. Las respuestas reales validan contra los esquemas publicados (jsonschema).
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import jsonschema
import pytest
import yaml

_SPEC = yaml.safe_load(
    (Path(__file__).parents[2] / "openapi.yaml").read_text(encoding="utf-8")
)
_PREFIJO = "/api/v1"


def _validar(cuerpo: dict, esquema: str) -> None:
    schema = {"$ref": f"#/components/schemas/{esquema}", "components": _SPEC["components"]}
    jsonschema.Draft202012Validator(schema).validate(cuerpo)


def _rutas_flask(app) -> set[tuple[str, str]]:
    rutas = set()
    for regla in app.url_map.iter_rules():
        if not regla.rule.startswith(_PREFIJO):
            continue
        ruta = re.sub(r"<(?:[a-z]+:)?([a-z_]+)>", r"{\1}", regla.rule[len(_PREFIJO):])
        for metodo in regla.methods - {"HEAD", "OPTIONS"}:
            rutas.add((ruta, metodo.lower()))
    return rutas


def _rutas_spec() -> set[tuple[str, str]]:
    return {(ruta, metodo) for ruta, ops in _SPEC["paths"].items() for metodo in ops}


def test_rutas_coinciden_con_el_contrato(app):
    assert _rutas_flask(app) == _rutas_spec()


@pytest.fixture
def poblado(client):
    nino = {
        "dni": "01234567", "nombres": "Ana María", "apellidos": "Quispe López",
        "fecha_nacimiento": "2023-03-15", "sexo": "F", "tipo_nacimiento": "TERMINO",
        "peso_kg": 8.5, "distrito": "Huancayo", "altitud_msnm": 3271,
        "cuidador": "María López", "telefono": None,
        "dosaje_inicial": {"fecha_dosaje": date.today().isoformat(), "hb_observada": 10.5},
    }
    resp = client.post("/api/v1/ninos", json=nino)
    assert resp.status_code == 201
    _validar(resp.get_json(), "NinoResponse")
    return client


def test_respuestas_cumplen_esquemas(poblado):
    c = poblado
    hoy = date.today().isoformat()
    _validar(c.get("/api/v1/salud").get_json(), "SaludResponse")
    _validar(c.get("/api/v1/ninos").get_json(), "ListaNinosResponse")
    _validar(c.get("/api/v1/ninos/01234567").get_json(), "ExpedienteResponse")
    _validar(c.patch("/api/v1/ninos/01234567", json={"peso_kg": 9}).get_json(), "NinoResponse")
    dos = c.post("/api/v1/ninos/01234567/dosajes",
                 json={"fecha_dosaje": hoy, "hb_observada": 11.0, "altitud_msnm": 3271})
    _validar(dos.get_json(), "DosajeResponse")
    rep = c.get(f"/api/v1/reportes/registros?desde={hoy}&hasta={hoy}")
    _validar(rep.get_json(), "ReporteResponse")


def test_errores_cumplen_esquema(poblado):
    c = poblado
    for resp in (
        c.post("/api/v1/ninos", json={"dni": "1"}),
        c.get("/api/v1/ninos/99999999"),
        c.post("/api/v1/ninos", data="x", content_type="text/plain"),
    ):
        _validar(resp.get_json(), "ErrorResponse")
