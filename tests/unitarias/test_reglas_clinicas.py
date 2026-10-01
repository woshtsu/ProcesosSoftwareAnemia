"""CP-01 a CP-06: reglas clínicas del dominio (HU-03)."""

import pytest

from app.domain.reglas_clinicas import Clasificacion, ajuste_por_altitud, clasificar_anemia, hemoglobina_ajustada


@pytest.mark.parametrize(
    "altitud, esperado", [(0, 0.0), (-10, 0.0), (1000, 0.6), (3000, 2.0), (3550, 2.4), (4000, 2.7)]
)
def test_ajuste_por_altitud_segun_ecuacion(altitud, esperado):
    assert ajuste_por_altitud(altitud) == esperado


def test_hemoglobina_ajustada_resta_el_ajuste():
    assert hemoglobina_ajustada(12.4, 3720) == 9.9


@pytest.mark.parametrize(
    "edad, hb, esperado",
    [
        (8, 10.5, Clasificacion.SIN_ANEMIA),
        (8, 10.4, Clasificacion.LEVE),
        (8, 9.5, Clasificacion.LEVE),
        (8, 9.4, Clasificacion.MODERADA),
        (8, 7.0, Clasificacion.MODERADA),
        (8, 6.9, Clasificacion.SEVERA),
        (30, 11.0, Clasificacion.SIN_ANEMIA),
        (30, 10.9, Clasificacion.LEVE),
        (30, 10.0, Clasificacion.LEVE),
        (30, 9.9, Clasificacion.MODERADA),
        (30, 6.5, Clasificacion.SEVERA),
        (23, 10.5, Clasificacion.SIN_ANEMIA),
        (24, 10.5, Clasificacion.LEVE),
    ],
)
def test_clasificacion_en_limites_de_los_puntos_de_corte(edad, hb, esperado):
    assert clasificar_anemia(edad, hb) == esperado


@pytest.mark.parametrize("edad", [0, 3, 5, 60])
def test_fuera_de_rango_de_edad_no_aplica(edad):
    assert clasificar_anemia(edad, 9.0) == Clasificacion.NO_APLICA
