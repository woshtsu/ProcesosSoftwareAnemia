"""Visita domiciliaria y su priorización (VIS-3.5, brecha B4)."""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum

from app.domain.model.clasificacion import Clasificacion
from app.domain.model.tiempo import ahora

LIMITE_PREDETERMINADO = 20  # niños que devuelve la lista priorizada si no se indica otro límite
LIMITE_MAXIMO = 200


class ResultadoVisita(StrEnum):
    REALIZADA = "REALIZADA"
    NO_ENCONTRADO = "NO_ENCONTRADO"
    RECHAZADA = "RECHAZADA"


class ConsumoSuplemento(StrEnum):
    SI = "SI"
    NO = "NO"
    DESCONOCIDO = "DESCONOCIDO"


@dataclass
class VisitaDomiciliaria:
    """Visita del personal al domicilio de un niño en tratamiento. Una visita por niño y por día."""

    nino_id: str
    fecha: date
    resultado: ResultadoVisita
    registrado_por: str
    consume_suplemento: ConsumoSuplemento = ConsumoSuplemento.DESCONOCIDO
    observaciones: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creado_en: datetime = field(default_factory=ahora)


@dataclass(frozen=True)
class ComponentePuntaje:
    """Una parte explicable del puntaje de prioridad: qué se midió, cuánto vale y cuánto podría valer como máximo."""

    codigo: str  # SEVERIDAD, CONTROL_VENCIDO, INASISTENCIAS o ULTIMA_VISITA
    descripcion: str
    valor: str  # lo observado, p. ej. «MODERADA», «45 días», «sin visitas»
    puntos: float
    maximo: float


@dataclass(frozen=True)
class NinoPriorizado:
    """Niño en tratamiento con su puntaje de prioridad de visita domiciliaria y los componentes que lo explican."""

    nino_id: str
    dni: str | None
    codigo_origen: str | None
    nombre_completo: str
    establecimiento: str
    comunidad: str
    ultima_clasificacion: Clasificacion
    dias_control_vencido: int
    inasistencias_recientes: int
    ultima_visita: date | None
    dias_desde_ultima_visita: int | None
    puntaje: float
    componentes: tuple[ComponentePuntaje, ...] = ()
