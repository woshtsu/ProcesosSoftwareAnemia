"""CP-07 a CP-12: validación de datos de entrada (HU-01, HU-03)."""

from datetime import date

import pytest

from app.domain.entidades import Evaluacion, edad_en_meses, validar_datos_evaluacion, validar_datos_nino
from app.domain.errores import ErrorCampo, ErrorValidacion
from app.domain.reglas_clinicas import Clasificacion
from tests.conftest import HOY, datos_eval, datos_nino


def campos(errores):
    return {e.campo for e in errores}


def test_datos_validos_no_generan_errores():
    assert validar_datos_nino(datos_nino(), HOY) == []
    assert validar_datos_evaluacion(datos_eval(), date(2025, 10, 15), HOY) == []


@pytest.mark.parametrize("dni", ["1234567", "123456789", "7123456A", ""])
def test_dni_debe_tener_8_digitos(dni):
    assert "dni" in campos(validar_datos_nino(datos_nino(dni=dni), HOY))


def test_campos_obligatorios_vacios():
    errores = validar_datos_nino(datos_nino(nombres=" ", apellidos=None, comunidad="", tutor_nombre="", sexo="X"), HOY)
    assert {"nombres", "apellidos", "comunidad", "tutor_nombre", "sexo"} <= campos(errores)


def test_fecha_nacimiento_futura_o_mayor_de_5_anos():
    assert "fecha_nacimiento" in campos(validar_datos_nino(datos_nino(fecha_nacimiento=date(2026, 12, 1)), HOY))
    assert "fecha_nacimiento" in campos(validar_datos_nino(datos_nino(fecha_nacimiento=date(2021, 8, 1)), HOY))
    assert "fecha_nacimiento" in campos(validar_datos_nino(datos_nino(fecha_nacimiento="2025-01-01"), HOY))


def test_altitud_y_celular_invalidos():
    errores = validar_datos_nino(datos_nino(altitud_m=6000, tutor_celular="812345678"), HOY)
    assert {"altitud_m", "tutor_celular"} <= campos(errores)
    assert "tutor_celular" not in campos(validar_datos_nino(datos_nino(tutor_celular=None), HOY))


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("hemoglobina_observada", 2.9),
        ("hemoglobina_observada", 20.1),
        ("hemoglobina_observada", None),
        ("peso_kg", 45),
        ("talla_cm", 20),
        ("fecha", date(2026, 10, 1)),
        ("fecha", date(2025, 1, 1)),
        ("fecha", None),
    ],
)
def test_evaluacion_fuera_de_rango(campo, valor):
    errores = validar_datos_evaluacion(datos_eval(**{campo: valor}), date(2025, 10, 15), HOY)
    assert campo in campos(errores)


def test_mensaje_de_hemoglobina_es_comprensible():
    errores = validar_datos_evaluacion(datos_eval(hemoglobina_observada=25), None, HOY)
    assert "rango clínico válido" in errores[0].mensaje


@pytest.mark.parametrize(
    "nac, ref, meses",
    [
        (date(2025, 10, 15), date(2026, 9, 28), 11),
        (date(2025, 10, 28), date(2026, 9, 28), 11),
        (date(2025, 10, 29), date(2026, 9, 28), 10),
        (date(2024, 9, 28), date(2026, 9, 28), 24),
    ],
)
def test_edad_en_meses(nac, ref, meses):
    assert edad_en_meses(nac, ref) == meses


def test_evaluacion_calcula_ajuste_y_clasificacion():
    e = Evaluacion(
        fecha=HOY, hemoglobina_observada=11.0, peso_kg=8, talla_cm=70, altitud_m=3550, edad_meses=10, registrado_por="x"
    )
    e.calcular()
    assert e.hemoglobina_ajustada == 8.6
    assert e.clasificacion == Clasificacion.MODERADA
    assert e.tiene_anemia


def test_error_validacion_se_representa_como_texto():
    assert str(ErrorValidacion([ErrorCampo("dni", "mal")])) == "dni: mal"


def test_fecha_local_usa_hora_de_peru():
    # DEF-02: 01:30 UTC del 29-sep son las 20:30 del 28-sep en Perú.
    from datetime import UTC, datetime

    from app.domain.entidades import fecha_local, limites_utc

    assert fecha_local(datetime(2026, 9, 29, 1, 30, tzinfo=UTC)) == date(2026, 9, 28)
    assert fecha_local(datetime(2026, 9, 29, 1, 30)) == date(2026, 9, 28)  # sin zona: se asume UTC
    inicio, fin = limites_utc(date(2026, 9, 28), date(2026, 9, 28))
    assert inicio == datetime(2026, 9, 28, 5, 0, tzinfo=UTC)
    assert fin.date() == date(2026, 9, 29) and fin.hour == 4
