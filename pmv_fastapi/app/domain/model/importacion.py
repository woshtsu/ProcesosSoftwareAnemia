"""Objetos de valor de la importación de un dataset externo (ADR-009).

La lectura y limpieza del archivo (formatos, valores nulos, tabla de altitudes) es responsabilidad de quien invoca el
caso de uso; el dominio recibe registros ya normalizados y aplica sus propias reglas (rangos clínicos, edad).
"""

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class TipoEvaluacionImportada(StrEnum):
    DIAGNOSTICO = "DIAGNOSTICO"
    CONTROL_1_MES = "CONTROL_1_MES"
    CONTROL_3_MESES = "CONTROL_3_MESES"
    CONTROL_6_MESES = "CONTROL_6_MESES"


@dataclass(frozen=True)
class EvaluacionImportada:
    tipo: TipoEvaluacionImportada
    fecha: date
    hemoglobina_observada: float
    clasificacion_origen: str | None = None  # severidad registrada por el HIS (solo el diagnóstico)


@dataclass(frozen=True)
class RegistroImportado:
    """Un niño del dataset con sus evaluaciones, listo para persistir como origen DATASET_DIRESA_JUNIN."""

    codigo_origen: str  # seudónimo estable, p. ej. DJ-00001
    fecha_nacimiento: date
    establecimiento: str
    distrito: str
    comunidad: str
    altitud_m: float
    red: str | None = None
    microred: str | None = None
    provincia: str | None = None
    evaluaciones: tuple[EvaluacionImportada, ...] = ()
    descartes_lectura: tuple[str, ...] = ()  # motivos por los que se omitieron datos al leer la fila


@dataclass
class ResultadoImportacion:
    registros_recibidos: int = 0
    ninos_importados: int = 0
    ninos_omitidos: int = 0  # sin ninguna evaluación válida
    ninos_con_alta_por_edad: int = 0  # fuera de la población objetivo (60 meses o más) a la fecha de referencia
    evaluaciones_importadas: dict[str, int] = field(default_factory=dict)
    descartes: dict[str, int] = field(default_factory=dict)
    # Concordancia entre la severidad del HIS y la clasificación calculada por el sistema (evaluación de diagnóstico).
    matriz_concordancia: dict[str, dict[str, int]] = field(default_factory=dict)
    ninos_por_provincia: dict[str, int] = field(default_factory=dict)
