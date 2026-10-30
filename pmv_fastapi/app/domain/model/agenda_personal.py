"""Objetos de valor de la agenda del personal de un establecimiento (HIST-2.3)."""

from dataclasses import dataclass, field
from datetime import date

from app.domain.model.agenda import ControlProgramado
from app.domain.model.alertas import Prioridad


@dataclass(frozen=True)
class ItemAgendaPersonal:
    """Un control programado de un niño, con los datos para ubicarlo en el establecimiento."""

    nino_id: str
    codigo_origen: str | None
    dni: str | None
    nombre_completo: str
    establecimiento: str
    comunidad: str
    control: ControlProgramado
    prioridad: Prioridad | None  # solo si el control está vencido


@dataclass(frozen=True)
class DiaAgendaPersonal:
    fecha: date
    total: int = 0
    cumplidos: int = 0
    pendientes: int = 0
    vencidos: int = 0
    con_inasistencia: int = 0
    items: list[ItemAgendaPersonal] = field(default_factory=list)


@dataclass(frozen=True)
class ResumenAgendaPersonal:
    total: int = 0
    cumplidos: int = 0
    pendientes: int = 0
    vencidos: int = 0
    con_inasistencia: int = 0
    ninos: int = 0


@dataclass(frozen=True)
class AgendaPersonal:
    desde: date
    hasta: date
    fecha_referencia: date
    establecimiento: str | None
    comunidad: str | None
    resumen: ResumenAgendaPersonal
    dias: list[DiaAgendaPersonal] = field(default_factory=list)
    establecimientos_disponibles: list[str] = field(default_factory=list)
    comunidades_disponibles: list[str] = field(default_factory=list)
