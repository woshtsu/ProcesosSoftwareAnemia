"""Clasificación de la anemia (objeto de valor del dominio)."""

from enum import StrEnum


class Clasificacion(StrEnum):
    SIN_ANEMIA = "SIN_ANEMIA"
    LEVE = "LEVE"
    MODERADA = "MODERADA"
    SEVERA = "SEVERA"
    NO_APLICA = "NO_APLICA"  # menores de 6 meses: evaluación clínica, sin punto de corte en el PMV
