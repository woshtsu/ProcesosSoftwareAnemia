"""Barreras de acceso al tratamiento y su alerta cuando son críticas (HIST-4.3 y HIST-4.4, ADR-014)."""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum

from app.domain.model.alertas import Prioridad
from app.domain.model.clasificacion import Clasificacion
from app.domain.model.tiempo import ahora


class TipoBarrera(StrEnum):
    TRANSPORTE = "TRANSPORTE"
    ECONOMICA = "ECONOMICA"
    OLVIDO = "OLVIDO"
    TRABAJO_CUIDADOR = "TRABAJO_CUIDADOR"
    DISTANCIA_CLIMA = "DISTANCIA_CLIMA"
    EFECTOS_ADVERSOS_SUPLEMENTO = "EFECTOS_ADVERSOS_SUPLEMENTO"
    RECHAZO_TRATAMIENTO = "RECHAZO_TRATAMIENTO"
    OTRA = "OTRA"  # el detalle es obligatorio


class FuenteBarrera(StrEnum):
    PERSONAL = "PERSONAL"  # la registra el personal por iniciativa propia
    RESPUESTA_RECORDATORIO = "RESPUESTA_RECORDATORIO"  # el tutor respondió NO_PUEDE a un recordatorio
    INASISTENCIA = "INASISTENCIA"  # motivo de una inasistencia a control (RF-09)
    VISITA = "VISITA"  # visita domiciliaria RECHAZADA o NO_ENCONTRADO


class CodigoRazonBarrera(StrEnum):
    BARRERA_GRAVE = "BARRERA_GRAVE"  # rechazo del tratamiento o efectos adversos del suplemento
    BARRERAS_RECURRENTES = "BARRERAS_RECURRENTES"  # dos o más barreras distintas en la ventana
    ANEMIA_CONTROL_VENCIDO = "ANEMIA_CONTROL_VENCIDO"  # barrera con anemia moderada o severa y control vencido


@dataclass
class Barrera:
    """Obstáculo que declaró la familia o que halló el personal para cumplir el tratamiento o los controles."""

    nino_id: str
    tipo: TipoBarrera
    fuente: FuenteBarrera
    fecha: date
    registrado_por: str
    detalle: str | None = None
    recordatorio_id: str | None = None  # recordatorio cuya respuesta NO_PUEDE originó la barrera
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creado_en: datetime = field(default_factory=ahora)


@dataclass(frozen=True)
class RazonAlertaBarrera:
    codigo: CodigoRazonBarrera
    descripcion: str


@dataclass(frozen=True)
class AlertaBarrera:
    """Niño con barreras críticas, la razón (o razones) por las que lo es y las barreras vigentes que la sustentan."""

    nino_id: str
    dni: str | None
    codigo_origen: str | None
    nombre_completo: str
    comunidad: str
    establecimiento: str
    tutor_celular: str | None
    ultima_clasificacion: Clasificacion | None
    dias_control_vencido: int
    prioridad: Prioridad
    razones: tuple[RazonAlertaBarrera, ...]
    barreras: tuple[Barrera, ...]
