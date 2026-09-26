"""
Pruebas de la interfaz web (adaptador de entrada HTML) — PMV Anemia Junín.

Cubren HIST-1.1 a HIST-1.5 desde los formularios: PRG (303), conservación de
datos ante error, mensajes por campo, semáforo con texto y protección CSRF.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

import pytest

from anemia_junin.bootstrap import crear_app

_HOY = date.today()
_NAC_2_ANIOS = (_HOY - timedelta(days=2 * 365 + 30)).isoformat()

_FORM_BASE = {
    "dni": "70000001",
    "nombres": "Rosa Elena",
    "apellidos": "Huanca Tapia",
    "fecha_nacimiento": _NAC_2_ANIOS,
    "sexo": "F",
    "tipo_nacimiento": "TERMINO",
    "peso_kg": "11.2",
    "distrito": "Huancayo",
    "altitud_msnm": "3271",
    "cuidador": "Carmen Tapia",
    "telefono": "987654321",
}


def _registrar(client, **extra):
    datos = {**_FORM_BASE, **extra}
    return client.post("/ninos/nuevo", data=datos)


class TestNavegacion:
    def test_raiz_redirige_a_lista(self, client):
        resp = client.get("/")
        assert resp.status_code == 303
        assert resp.headers["Location"].endswith("/ninos")

    def test_lista_vacia_muestra_aviso_academico(self, client):
        resp = client.get("/ninos")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "Demostración académica con datos sintéticos" in html
        assert "No hay niños registrados" in html

    def test_formulario_nuevo(self, client):
        resp = client.get("/ninos/nuevo")
        assert resp.status_code == 200
        assert 'name="dni"' in resp.get_data(as_text=True)

    def test_pagina_inexistente_404_html(self, client):
        resp = client.get("/no-existe")
        assert resp.status_code == 404
        assert "La página solicitada no existe" in resp.get_data(as_text=True)

    def test_api_inexistente_404_json(self, client):
        resp = client.get("/api/v1/no-existe")
        assert resp.status_code == 404
        assert resp.get_json()["error"]["code"] == "NOT_FOUND"


class TestRegistroWeb:
    """HIST-1.1 / HIST-1.3 desde el formulario."""

    def test_alta_valida_redirige_al_expediente(self, client):
        resp = _registrar(client)
        assert resp.status_code == 303
        assert resp.headers["Location"].endswith("/ninos/70000001")
        exp = client.get("/ninos/70000001").get_data(as_text=True)
        assert "Huanca Tapia, Rosa Elena" in exp
        assert "SIN DOSAJE" in exp

    def test_alta_con_dosaje_inicial_clasifica(self, client):
        resp = _registrar(
            client, tiene_dosaje_inicial="1",
            fecha_dosaje=_HOY.isoformat(), hb_observada="9.0",
        )
        assert resp.status_code == 303
        exp = client.get("/ninos/70000001").get_data(as_text=True)
        # 9.0 - 2.1 (3271 msnm) = 6.9 g/dL → SEVERA (texto además de color)
        assert "SEVERA" in exp
        assert "6.9" in exp

    def test_errores_conservan_datos_y_no_guardan(self, client):
        resp = _registrar(client, dni="1234567", telefono="12345", nombres="Lucía")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 422
        assert "Debe contener exactamente 8 dígitos" in html
        assert "Debe contener exactamente 9 dígitos" in html
        assert 'value="Lucía"' in html  # dato preservado
        assert client.get("/ninos/1234567").status_code == 404

    def test_campos_mal_formados_no_se_sustituyen(self, client):
        """Fecha, sexo y altitud inválidos no se reemplazan por valores por defecto."""
        resp = _registrar(client, fecha_nacimiento="", sexo="", altitud_msnm="abc")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 422
        assert "Ingrese una fecha válida" in html
        assert "Debe ser F o M" in html
        assert "Debe ser un número entero" in html
        assert client.get("/ninos/70000001").status_code == 404

    def test_hb_inicial_fuera_de_rango(self, client):
        resp = _registrar(
            client, tiene_dosaje_inicial="1",
            fecha_dosaje=_HOY.isoformat(), hb_observada="30",
        )
        assert resp.status_code == 422
        assert "como máximo 25.0" in resp.get_data(as_text=True)
        assert client.get("/ninos/70000001").status_code == 404

    def test_dni_duplicado_409(self, client):
        _registrar(client)
        resp = _registrar(client)
        assert resp.status_code == 409
        assert "Este DNI ya está registrado" in resp.get_data(as_text=True)


class TestExpedienteWeb:
    """HIST-1.2 desde la interfaz."""

    def test_expediente_inexistente(self, client):
        resp = client.get("/ninos/99999999")
        assert resp.status_code == 404
        assert "99999999" in resp.get_data(as_text=True)

    def test_editar_formulario_y_guardar(self, client):
        _registrar(client)
        assert client.get("/ninos/70000001/editar").status_code == 200
        resp = client.post("/ninos/70000001/editar", data={"peso_kg": "12.5", "distrito": "Chilca"})
        assert resp.status_code == 303
        html = client.get("/ninos/70000001").get_data(as_text=True)
        assert "12.5 kg" in html
        assert "Chilca" in html
        assert "Huanca Tapia" in html  # identidad intacta

    def test_editar_vacio(self, client):
        _registrar(client)
        resp = client.post("/ninos/70000001/editar", data={})
        assert resp.status_code == 422
        assert "Ingrese al menos un campo" in resp.get_data(as_text=True)

    def test_editar_peso_invalido(self, client):
        _registrar(client)
        resp = client.post("/ninos/70000001/editar", data={"peso_kg": "45"})
        assert resp.status_code == 422
        assert "como máximo 30.000 kg" in resp.get_data(as_text=True)

    def test_editar_telefono_invalido(self, client):
        _registrar(client)
        resp = client.post("/ninos/70000001/editar", data={"telefono": "123"})
        assert resp.status_code == 422

    @pytest.mark.parametrize("ruta", ["/ninos/99999999/editar", "/ninos/99999999/dosajes/nuevo"])
    def test_formularios_de_nino_inexistente(self, client, ruta):
        assert client.get(ruta).status_code == 404
        assert client.post(ruta, data={"peso_kg": "10", "hb_observada": "10"}).status_code == 404

    def test_nuevo_dosaje(self, client):
        _registrar(client)
        form = client.get("/ninos/70000001/dosajes/nuevo").get_data(as_text=True)
        assert "Precargada con la altitud del niño (3271 m)" in form
        resp = client.post("/ninos/70000001/dosajes/nuevo", data={
            "fecha_dosaje": _HOY.isoformat(), "hb_observada": "13.5", "altitud_msnm": "3271",
        })
        assert resp.status_code == 303
        assert "SIN ANEMIA" in client.get("/ninos/70000001").get_data(as_text=True)

    def test_nuevo_dosaje_invalido(self, client):
        _registrar(client)
        resp = client.post("/ninos/70000001/dosajes/nuevo", data={
            "fecha_dosaje": "", "hb_observada": "abc", "altitud_msnm": "x",
        })
        html = resp.get_data(as_text=True)
        assert resp.status_code == 422
        assert "Ingrese una fecha válida" in html
        assert "Debe ser un número válido" in html

    def test_nuevo_dosaje_fecha_futura(self, client):
        _registrar(client)
        resp = client.post("/ninos/70000001/dosajes/nuevo", data={
            "fecha_dosaje": (_HOY + timedelta(days=1)).isoformat(),
            "hb_observada": "11", "altitud_msnm": "3271",
        })
        assert resp.status_code == 422
        assert "No puede ser posterior a hoy" in resp.get_data(as_text=True)


class TestListaYReporteWeb:
    """HIST-1.4 y HIST-1.5 desde la interfaz."""

    def test_lista_ordenada_por_severidad_con_texto(self, client):
        _registrar(client, dni="70000001", apellidos="Alvarez Uno", tiene_dosaje_inicial="1",
                   fecha_dosaje=_HOY.isoformat(), hb_observada="14.0")
        _registrar(client, dni="70000002", apellidos="Zapata Dos", tiene_dosaje_inicial="1",
                   fecha_dosaje=_HOY.isoformat(), hb_observada="8.5")
        html = client.get("/ninos").get_data(as_text=True)
        assert html.index("70000002") < html.index("70000001")  # SEVERA antes que SIN ANEMIA
        assert re.search(r"badge--severa\">\s*SEVERA", html)

    def test_filtros(self, client):
        _registrar(client)
        html = client.get("/ninos?q=Huanca&clasificacion=SIN_DOSAJE&distrito=Huancayo")
        assert "70000001" in html.get_data(as_text=True)
        vacio = client.get("/ninos?clasificacion=SEVERA").get_data(as_text=True)
        assert "No se encontraron niños" in vacio

    def test_paginacion_parametros_invalidos(self, client):
        assert client.get("/ninos?pagina=x").status_code == 200

    def test_reporte_sin_parametros(self, client):
        resp = client.get("/reportes/registros")
        assert resp.status_code == 200
        assert "Generar reporte" in resp.get_data(as_text=True)

    def test_reporte_con_datos(self, client):
        _registrar(client)
        _registrar(client, dni="123")  # intento rechazado
        html = client.get(
            f"/reportes/registros?desde={_HOY.isoformat()}&hasta={_HOY.isoformat()}"
        ).get_data(as_text=True)
        assert "Calidad del registro" in html
        assert "50.0" in html  # 1 aceptado de 2 evaluados

    def test_reporte_fechas_invalidas(self, client):
        html = client.get("/reportes/registros?desde=x&hasta=y").get_data(as_text=True)
        assert "Fecha inválida" in html

    def test_reporte_rango_invertido(self, client):
        html = client.get("/reportes/registros?desde=2026-09-30&hasta=2026-09-01")
        assert "posterior o igual" in html.get_data(as_text=True)


class TestCsrf:
    """Los formularios HTML exigen token CSRF cuando la protección está activa."""

    @pytest.fixture
    def app_csrf(self, tmp_path: Path):
        normativa = Path(__file__).parents[2] / "config" / "normativa_v1.json"
        return crear_app(
            db_path=str(tmp_path / "csrf.db"), normativa_path=normativa,
            secret_key="clave-prueba", testing=False,
        )

    def test_post_sin_token_rechazado(self, app_csrf):
        resp = app_csrf.test_client().post("/ninos/nuevo", data=_FORM_BASE)
        assert resp.status_code == 400

    def test_post_con_token_aceptado(self, app_csrf):
        client = app_csrf.test_client()
        html = client.get("/ninos/nuevo").get_data(as_text=True)
        token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
        resp = client.post("/ninos/nuevo", data={**_FORM_BASE, "csrf_token": token})
        assert resp.status_code == 303

    def test_api_json_exenta_de_csrf(self, app_csrf):
        datos = {**_FORM_BASE, "peso_kg": 11.2, "altitud_msnm": 3271}
        resp = app_csrf.test_client().post("/api/v1/ninos", json=datos)
        assert resp.status_code == 201


class TestAdvertenciaAltitud:
    """DEV-100 (d): la UI muestra la advertencia de banda ≥ 4000 msnm no verificada."""

    def test_expediente_muestra_advertencia_solo_referencial(self, client):
        _registrar(client, altitud_msnm="4107", distrito="Junín", tiene_dosaje_inicial="1",
                   fecha_dosaje=_HOY.isoformat(), hb_observada="13.0")
        html = client.get("/ninos/70000001").get_data(as_text=True)
        assert "Advertencia sobre la clasificación actual (solo referencial)" in html
        assert "banda no verificada" in html

    def test_sin_advertencia_bajo_4000(self, client):
        _registrar(client, tiene_dosaje_inicial="1",
                   fecha_dosaje=_HOY.isoformat(), hb_observada="13.0")
        html = client.get("/ninos/70000001").get_data(as_text=True)
        assert "Advertencia sobre la clasificación actual" not in html


@pytest.mark.parametrize("valor", ["Infinity", "sNaN", "1e100"])
@pytest.mark.parametrize("campo", ["peso_kg", "hb_observada"])
def test_formulario_rechaza_numeros_especiales(client, campo, valor):
    extra = {campo: valor}
    if campo == "hb_observada":
        extra.update(tiene_dosaje_inicial="1", fecha_dosaje=_HOY.isoformat())
    respuesta = _registrar(client, **extra)
    assert respuesta.status_code == 422
    assert client.get("/api/v1/ninos/70000001").status_code == 404
