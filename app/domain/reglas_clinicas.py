"""Reglas clínicas del Incremento 1 (HU-03).

Puntos de corte y ecuación de ajuste por altitud tomados de la guía de la OMS
(2024) sobre niveles de hemoglobina para definir anemia. Los parámetros están
centralizados en este módulo porque deben ser confirmados por la microred
frente a la norma técnica vigente (dependencia F del plan del Incremento 1);
si la norma cambia, se actualizan en un solo lugar.
"""

from dataclasses import dataclass
from enum import StrEnum

# Rangos de plausibilidad de captura (evitan errores de digitación).
HB_MIN_CAPTURA = 3.0  # g/dL
HB_MAX_CAPTURA = 20.0  # g/dL
PESO_MIN_KG = 1.5
PESO_MAX_KG = 30.0
TALLA_MIN_CM = 40.0
TALLA_MAX_CM = 125.0
ALTITUD_MIN_M = 0
ALTITUD_MAX_M = 5000
EDAD_MAX_MESES = 59  # población objetivo: menores de 5 años


class Clasificacion(StrEnum):
    SIN_ANEMIA = "SIN_ANEMIA"
    LEVE = "LEVE"
    MODERADA = "MODERADA"
    SEVERA = "SEVERA"
    NO_APLICA = "NO_APLICA"  # menores de 6 meses: evaluación clínica, sin punto de corte en el PMV


@dataclass(frozen=True)
class PuntoDeCorte:
    edad_min_meses: int
    edad_max_meses: int
    umbral_anemia: float  # Hb ajustada < umbral  => anemia
    umbral_leve: float  # umbral_leve <= Hb < umbral_anemia => leve
    umbral_severa: float  # Hb < umbral_severa => severa ; resto => moderada


PUNTOS_DE_CORTE = (
    PuntoDeCorte(6, 23, umbral_anemia=10.5, umbral_leve=9.5, umbral_severa=7.0),
    PuntoDeCorte(24, 59, umbral_anemia=11.0, umbral_leve=10.0, umbral_severa=7.0),
)


def ajuste_por_altitud(altitud_m: float) -> float:
    """Ajuste de hemoglobina (g/dL) que se resta al valor observado.

    Ecuación OMS 2024 en g/L: 0.0056384 * altitud + 0.0000003 * altitud^2.
    Se convierte a g/dL dividiendo entre 10 y se redondea a 1 decimal.
    """
    if altitud_m <= 0:
        return 0.0
    ajuste_g_l = 0.0056384 * altitud_m + 0.0000003 * altitud_m**2
    return round(ajuste_g_l / 10, 1)


def hemoglobina_ajustada(hb_observada: float, altitud_m: float) -> float:
    return round(hb_observada - ajuste_por_altitud(altitud_m), 1)


def clasificar_anemia(edad_meses: int, hb_ajustada: float) -> Clasificacion:
    for corte in PUNTOS_DE_CORTE:
        if corte.edad_min_meses <= edad_meses <= corte.edad_max_meses:
            if hb_ajustada >= corte.umbral_anemia:
                return Clasificacion.SIN_ANEMIA
            if hb_ajustada >= corte.umbral_leve:
                return Clasificacion.LEVE
            if hb_ajustada >= corte.umbral_severa:
                return Clasificacion.MODERADA
            return Clasificacion.SEVERA
    return Clasificacion.NO_APLICA
