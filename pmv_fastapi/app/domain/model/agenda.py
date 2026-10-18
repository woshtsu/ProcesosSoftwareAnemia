"""Objetos de valor de la agenda de controles (HIST-2.1)."""

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class TipoControl(StrEnum):
    TAMIZAJE_EDAD = "TAMIZAJE_EDAD"  # dosajes DHx/DHc por edad
    CONTROL_TRATAMIENTO = "CONTROL_TRATAMIENTO"  # hemoglobina de seguimiento del tratamiento (C1M, C3M, C6M)


class EstadoControl(StrEnum):
    CUMPLIDO = "CUMPLIDO"
    PENDIENTE = "PENDIENTE"
    VENCIDO = "VENCIDO"
    CERRADO_RECUPERADO = "CERRADO_RECUPERADO"  # control de tratamiento no realizado y ya innecesario por recuperación


@dataclass(frozen=True)
class ControlProgramado:
    """Un control de la agenda de un niño y su estado normativo a una fecha de referencia."""

    codigo: str  # DHx, DHc1, DHc2, C1M, C3M, C6M
    tipo: TipoControl
    fecha_programada: date
    fecha_limite: date  # último día en que el control aún se considera oportuno
    estado: EstadoControl
    dias_vencido: int | None  # días transcurridos desde fecha_limite (solo VENCIDO)
    evaluacion_id: str | None  # evaluación que cumplió el control (solo CUMPLIDO)
    descripcion: str
    fecha_inicio_ventana: date  # primer día en que el control se considera cumplido
    edad_meses_programada: int | None = None  # solo controles por edad
    proximo: bool = False  # PENDIENTE que vence en 7 días o menos
    inasistencia_registrada: bool = False  # el personal registró que el niño no asistió (HIST-2.4); control sin cumplir
    motivo_inasistencia: str | None = None
    cumplido_por_asistencia: bool = False  # CUMPLIDO porque el personal registró que el niño asistió (HIST-2.4)
    asistencia_id: str | None = None


@dataclass(frozen=True)
class ResumenAgenda:
    total: int = 0
    cumplidos: int = 0
    pendientes: int = 0
    vencidos: int = 0
    cerrados: int = 0
    proximos: int = 0  # subconjunto de pendientes que vencen en 7 días o menos
    inasistencias: int = 0  # controles sin cumplir con una inasistencia registrada
    proximo_control: ControlProgramado | None = None  # primer control PENDIENTE por fecha programada


@dataclass(frozen=True)
class AgendaNino:
    nino_id: str
    version_esquema: str
    fecha_referencia: date
    aplica: bool  # False cuando el niño tiene alta: no se programa agenda
    motivo: str | None = None
    controles: list[ControlProgramado] = field(default_factory=list)
    resumen: ResumenAgenda = field(default_factory=ResumenAgenda)
