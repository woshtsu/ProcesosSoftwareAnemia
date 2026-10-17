"""CP-83 a CP-88: pruebas de regresión de los defectos DEF-03 a DEF-06 hallados en el Incremento 2
(ver docs/evidencias/registro_defectos_inc2.md). DEF-07 se verifica en las pruebas de integración (SQLAlchemy)."""

from datetime import date

import pytest

from app.domain.model.errores import ErrorValidacion
from app.domain.service.validaciones import validar_datos_nino, validar_periodo
from tests.conftest import HOY, datos_eval, datos_nino


def campos(errores):
    return {e.campo for e in errores}


@pytest.mark.parametrize(
    "desde, hasta, campos_con_error",
    [
        (date(2026, 1, 1), date(9999, 12, 31), {"hasta"}),  # DEF-03: antes producía OverflowError -> HTTP 500
        (date(9999, 12, 30), date(9999, 12, 31), {"desde", "hasta"}),
        (date(1999, 12, 31), date(2026, 1, 1), {"desde"}),
        (date(2100, 12, 31), date(2101, 1, 1), {"hasta"}),
        (date(2026, 2, 1), date(2026, 1, 1), {"desde"}),
        (date(2000, 1, 1), date(2100, 12, 31), set()),  # límites inclusivos
        (date(2026, 1, 1), date(2026, 1, 1), set()),
    ],
)
def test_cp83_def03_periodo_del_reporte_con_fechas_extremas(desde, hasta, campos_con_error):
    assert campos(validar_periodo(desde, hasta)) == campos_con_error


def test_cp84_def03_el_servicio_rechaza_el_periodo_extremo(servicio):
    with pytest.raises(ErrorValidacion) as e:
        servicio.reporte_periodo(date(2026, 1, 1), date(9999, 12, 31))
    assert e.value.errores[0].campo == "hasta"
    assert servicio.reporte_periodo(date(2026, 9, 1), date(2026, 9, 30))["evaluaciones_realizadas"] == 0


@pytest.mark.parametrize("dni", ["7123456٤", "７１２３４５６７", "71234567\n8", "7123 567", "71234567​"])
def test_cp85_def04_dni_solo_acepta_digitos_ascii(dni):
    assert "dni" in campos(validar_datos_nino(datos_nino(dni=dni), HOY))


def test_cp85_def04_dni_con_espacios_en_los_extremos_se_recorta(servicio):
    nino = servicio.registrar_nino(datos_nino(dni=" 71234567 "), datos_eval(), "a")
    assert nino.dni == "71234567"


@pytest.mark.parametrize("celular", ["987654321\n", "\n987654321", "٩87654321", "98765432", " 987654321"])
def test_cp86_def04_celular_exige_coincidencia_completa_y_digitos_ascii(celular):
    assert "tutor_celular" in campos(validar_datos_nino(datos_nino(tutor_celular=celular), HOY))


@pytest.mark.parametrize("altitud", [float("nan"), float("inf"), float("-inf"), 99999, -1, 5000.1])
def test_cp87_def05_la_vista_previa_valida_la_altitud(servicio, altitud):
    with pytest.raises(ErrorValidacion) as e:
        servicio.previsualizar_evaluacion(date(2025, 1, 1), altitud, datos_eval())
    assert campos(e.value.errores) == {"altitud_m"}


@pytest.mark.parametrize("nacimiento", [date(2027, 1, 1), date(2021, 1, 1), date(1, 1, 1)])
def test_cp87_def05_la_vista_previa_valida_la_fecha_de_nacimiento(servicio, nacimiento):
    with pytest.raises(ErrorValidacion) as e:
        servicio.previsualizar_evaluacion(nacimiento, 3000, datos_eval())
    assert "fecha_nacimiento" in campos(e.value.errores)


def test_cp87_def05_vista_previa_valida_acepta_limites_de_altitud(servicio):
    for altitud in (0, 5000):
        assert servicio.previsualizar_evaluacion(date(2025, 1, 1), altitud, datos_eval()).clasificacion


@pytest.mark.parametrize(
    "campo, maximo",
    [
        ("nombres", 80),
        ("apellidos", 80),
        ("comunidad", 80),
        ("distrito", 80),
        ("establecimiento", 120),
        ("tutor_nombre", 120),
    ],
)
def test_cp88_def06_largo_maximo_de_los_textos(campo, maximo):
    assert campo not in campos(validar_datos_nino(datos_nino(**{campo: "x" * maximo}), HOY))
    errores = validar_datos_nino(datos_nino(**{campo: "x" * (maximo + 1)}), HOY)
    assert [e.mensaje for e in errores if e.campo == campo] == [f"No puede superar {maximo} caracteres."]
    # El largo se mide sobre el texto sin espacios laterales, que es el que se guarda.
    assert campo not in campos(validar_datos_nino(datos_nino(**{campo: "  " + "x" * maximo + "  "}), HOY))
