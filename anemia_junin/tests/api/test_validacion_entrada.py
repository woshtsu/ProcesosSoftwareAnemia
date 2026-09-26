"""
Pruebas de endurecimiento de la API (HIST-1.3) — PMV Anemia Junín.

Ningún campo mal formado o ausente se sustituye por un valor por defecto: se
rechaza con 400, no se guarda nada y el intento queda en la traza de calidad.
"""

from __future__ import annotations

from datetime import date

import pytest

_BASE = {
    "dni": "20000001",
    "nombres": "Carlos",
    "apellidos": "Mamani Flores",
    "fecha_nacimiento": "2024-01-10",
    "sexo": "M",
    "tipo_nacimiento": "PREMATURO",
    "peso_kg": 9.25,
    "distrito": "Tarma",
    "altitud_msnm": 3053,
    "cuidador": "Rosa Flores",
    "telefono": None,
}


def _hoy() -> str:
    return date.today().isoformat()


def _reporte(client):
    return client.get(f"/api/v1/reportes/registros?desde={_hoy()}&hasta={_hoy()}").get_json()


@pytest.mark.parametrize(
    ("campo", "valor", "mensaje"),
    [
        ("sexo", None, "'F' o 'M'"),
        ("sexo", "X", "'F' o 'M'"),
        ("tipo_nacimiento", None, "TERMINO"),
        ("fecha_nacimiento", None, "YYYY-MM-DD"),
        ("fecha_nacimiento", "15/03/2024", "fecha válida"),
        ("altitud_msnm", None, "número entero"),
        ("altitud_msnm", "abc", "número entero"),
        ("altitud_msnm", 3200.5, "número entero"),
        ("altitud_msnm", True, "número entero"),
        ("peso_kg", "pesado", "número válido"),
        ("peso_kg", 8.1234, "3 decimales"),
    ],
)
def test_campo_invalido_no_se_sustituye(client, campo, valor, mensaje):
    resp = client.post("/api/v1/ninos", json={**_BASE, campo: valor})
    assert resp.status_code == 400
    campos = resp.get_json()["error"]["fields"]
    assert mensaje in " ".join(campos[campo])
    assert client.get("/api/v1/ninos/20000001").status_code == 404


def test_intento_rechazado_por_conversion_queda_en_traza(client):
    client.post("/api/v1/ninos", json={**_BASE, "sexo": None})
    calidad = _reporte(client)["data"]["calidad_registro"]
    assert calidad["intentos_rechazados"] == 1
    assert calidad["intentos_aceptados"] == 0


@pytest.mark.parametrize(
    ("dosaje", "campo"),
    [
        ({"fecha_dosaje": "2026-13-01", "hb_observada": 10.0}, "dosaje_inicial.fecha_dosaje"),
        ({"fecha_dosaje": "2026-01-01", "hb_observada": 30.0}, "dosaje_inicial.hb_observada"),
        ({"fecha_dosaje": "2026-01-01", "hb_observada": 10.55}, "dosaje_inicial.hb_observada"),
        ({"fecha_dosaje": "2026-01-01"}, "dosaje_inicial.hb_observada"),
    ],
)
def test_dosaje_inicial_invalido_rechaza_todo(client, dosaje, campo):
    resp = client.post("/api/v1/ninos", json={**_BASE, "dosaje_inicial": dosaje})
    assert resp.status_code == 400
    assert campo in resp.get_json()["error"]["fields"]
    assert client.get("/api/v1/ninos/20000001").status_code == 404


def test_dosaje_inicial_no_objeto(client):
    resp = client.post("/api/v1/ninos", json={**_BASE, "dosaje_inicial": [1, 2]})
    assert resp.status_code == 400


def test_altitud_como_texto_numerico_se_normaliza(client):
    resp = client.post("/api/v1/ninos", json={**_BASE, "altitud_msnm": "3053"})
    assert resp.status_code == 201
    assert resp.get_json()["data"]["altitud_msnm"] == 3053


def test_cuerpo_json_no_objeto(client):
    resp = client.post("/api/v1/ninos", json=[1, 2, 3])
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "INVALID_JSON"


def test_json_mal_formado(client):
    resp = client.post("/api/v1/ninos", data="{no-json", content_type="application/json")
    assert resp.status_code == 400


def test_patch_altitud_texto_y_telefono_borrado(client):
    client.post("/api/v1/ninos", json={**_BASE, "telefono": "912345678"})
    resp = client.patch("/api/v1/ninos/20000001", json={"altitud_msnm": "4107", "telefono": ""})
    data = resp.get_json()["data"]
    assert resp.status_code == 200
    assert data["altitud_msnm"] == 4107
    assert data["telefono"] is None


def test_patch_errores(client):
    client.post("/api/v1/ninos", json=_BASE)
    assert client.patch("/api/v1/ninos/20000001", data="x").status_code == 415
    resp = client.patch("/api/v1/ninos/20000001", json={
        "peso_kg": 50, "distrito": "X", "altitud_msnm": 6000, "cuidador": "1", "telefono": "1",
    })
    campos = resp.get_json()["error"]["fields"]
    assert resp.status_code == 400
    assert set(campos) == {"peso_kg", "distrito", "altitud_msnm", "cuidador", "telefono"}


def test_dosaje_con_banda_no_verificada_advierte(client):
    client.post("/api/v1/ninos", json=_BASE)
    resp = client.post("/api/v1/ninos/20000001/dosajes", json={
        "fecha_dosaje": _hoy(), "hb_observada": 12.0, "altitud_msnm": 4107,
    })
    assert resp.status_code == 201
    assert any("no verificada" in a for a in resp.get_json()["data"]["advertencias"])


def test_dosaje_errores(client):
    client.post("/api/v1/ninos", json=_BASE)
    url = "/api/v1/ninos/20000001/dosajes"
    assert client.post(url, data="x").status_code == 415
    resp = client.post(url, json={"fecha_dosaje": "x", "hb_observada": "y"})
    campos = set(resp.get_json()["error"]["fields"])
    assert campos >= {"fecha_dosaje", "hb_observada", "altitud_msnm"}
    resp = client.post(
        url, json={"fecha_dosaje": "2000-01-01", "hb_observada": 10, "altitud_msnm": 3053}
    )
    assert resp.status_code == 400  # anterior al nacimiento


def test_listar_parametros_invalidos(client):
    assert client.get("/api/v1/ninos?pagina=a").status_code == 400


def test_reporte_fechas(client):
    assert client.get("/api/v1/reportes/registros?desde=x&hasta=y").status_code == 400
    resp = client.get("/api/v1/reportes/registros?desde=2026-09-30&hasta=2026-09-01")
    assert resp.status_code == 400


def test_salud_reporta_error_de_bd(app):
    app.config["VERIFICAR_BD"] = lambda: False
    resp = app.test_client().get("/api/v1/salud")
    assert resp.get_json()["data"]["base_datos"] == "error"


def test_verificar_conexion_bd_inexistente(tmp_path):
    from anemia_junin.adapters.outbound.sqlite.unidad_de_trabajo import verificar_conexion

    assert verificar_conexion(str(tmp_path / "vacia.db")) is False


def test_verificar_conexion_no_crea_archivo(tmp_path):
    from anemia_junin.adapters.outbound.sqlite.unidad_de_trabajo import verificar_conexion

    ruta = tmp_path / "no_existe.db"
    assert verificar_conexion(str(ruta)) is False
    assert not ruta.exists()


def test_verificar_conexion_bd_sin_esquema(tmp_path):
    import sqlite3
    from contextlib import closing

    from anemia_junin.adapters.outbound.sqlite.unidad_de_trabajo import verificar_conexion

    ruta = tmp_path / "sin_esquema.db"
    with closing(sqlite3.connect(ruta)) as conn:
        conn.execute("CREATE TABLE x (a)")
    assert verificar_conexion(str(ruta)) is False


@pytest.mark.parametrize("valor", ["Infinity", "sNaN", "1e100"])
@pytest.mark.parametrize("campo", ["peso_kg", "hb_observada"])
def test_numeros_especiales_devuelven_400_y_registran_rechazo(client, campo, valor):
    datos = dict(_BASE)
    if campo == "peso_kg":
        datos[campo] = valor
    else:
        datos["dosaje_inicial"] = {"fecha_dosaje": _hoy(), "hb_observada": valor}
    respuesta = client.post("/api/v1/ninos", json=datos)
    assert respuesta.status_code == 400
    assert respuesta.get_json()["error"]["fields"]
    assert client.get("/api/v1/ninos/20000001").status_code == 404
    calidad = _reporte(client)["data"]["calidad_registro"]
    assert calidad["intentos_rechazados"] == 1
    assert calidad["intentos_aceptados"] == 0
