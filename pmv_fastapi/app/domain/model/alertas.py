"""Objetos de valor de las alertas internas de controles vencidos (HIST-2.2)."""

from dataclasses import dataclass, field
from enum import StrEnum

from app.domain.model.agenda import ControlProgramado
from app.domain.model.clasificacion import Clasificacion


class Prioridad(StrEnum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"


@dataclass(frozen=True)
class AlertaControl:
    """Un control vencido de un niño activo, con los datos para contactar a la familia."""

    nino_id: str
    dni: str | None
    nombre_completo: str
    comunidad: str
    tutor_celular: str | None
    control: ControlProgramado
    ultima_clasificacion: Clasificacion | None
    prioridad: Prioridad
    codigo_origen: str | None = None  # seudónimo del registro del dataset (p. ej. DJ-00001)


@dataclass(frozen=True)
class ResumenAlertas:
    total_vencidos: int = 0
    por_prioridad: dict[str, int] = field(default_factory=dict)
    ninos_con_vencidos: int = 0
    proximos_7_dias: int = 0
