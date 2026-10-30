"""Asistencia a un control programado (HIST-2.4)."""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum

from app.domain.model.tiempo import ahora


class EstadoAsistencia(StrEnum):
    ASISTIO = "ASISTIO"
    NO_ASISTIO = "NO_ASISTIO"


@dataclass
class AsistenciaControl:
    """Registro de que el niño asistió (o no) a un control de su agenda.

    El control se identifica por ``(codigo_control, fecha_programada)``: la fecha programada distingue, por ejemplo,
    los distintos dosajes DHx (6, 15, 24 meses…) o los controles C1M de episodios de anemia distintos.
    """

    nino_id: str
    codigo_control: str
    fecha_programada: date
    estado: EstadoAsistencia
    registrado_por: str
    motivo: str | None = None  # obligatorio cuando no asistió
    evaluacion_id: str | None = None  # evaluación del día que acredita la asistencia (opcional)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creado_en: datetime = field(default_factory=ahora)
