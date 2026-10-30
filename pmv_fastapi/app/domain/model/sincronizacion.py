"""Sincronización de operaciones registradas sin conexión (HIST-3.2, HIST-3.3, ADR-012)."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.domain.model.errores import ErrorCampo
from app.domain.model.tiempo import ahora

LOTE_MAXIMO = 200


class TipoOperacion(StrEnum):
    REGISTRAR_NINO = "REGISTRAR_NINO"
    REGISTRAR_EVALUACION = "REGISTRAR_EVALUACION"
    REGISTRAR_ASISTENCIA = "REGISTRAR_ASISTENCIA"
    REGISTRAR_VISITA = "REGISTRAR_VISITA"
    REGISTRAR_BARRERA = "REGISTRAR_BARRERA"  # INC-4: barrera de acceso registrada sin conexión (ADR-014)


class ResultadoOperacion(StrEnum):
    APLICADA = "APLICADA"  # se creó el registro en el servidor
    DUPLICADA = "DUPLICADA"  # ya estaba aplicada (mismo id_operacion) o el servidor ya tiene el mismo dato
    CONFLICTO = "CONFLICTO"  # el servidor tiene un dato distinto: queda a la espera de una decisión humana
    RECHAZADA = "RECHAZADA"  # no cumple las reglas del dominio; no se guarda nada
    RESUELTA = "RESUELTA"  # solo en la bitácora: conflicto de un niño resuelto conservando al niño del servidor


class EstadoConflicto(StrEnum):
    PENDIENTE = "PENDIENTE"
    RESUELTO = "RESUELTO"


class ResolucionConflicto(StrEnum):
    CONSERVAR_SERVIDOR = "CONSERVAR_SERVIDOR"  # el dato del servidor gana; solo se agrega lo que no existía
    APLICAR_CLIENTE = "APLICAR_CLIENTE"  # el dato del dispositivo reemplaza al del servidor donde el dominio lo permite
    DESCARTAR = "DESCARTAR"  # se ignora la operación del dispositivo


@dataclass(frozen=True)
class OperacionEntrante:
    """Una operación tal como la envía el dispositivo (``datos`` en JSON, fechas como texto ISO)."""

    id_operacion: str
    tipo: str
    id_dispositivo: str
    fecha_local: datetime
    datos: dict
    id_cliente: str | None = None  # solo REGISTRAR_NINO: identificador temporal del niño en el dispositivo
    nino_id: str | None = None  # referencia al niño por su id del servidor…
    nino_id_cliente: str | None = None  # …o por el id temporal de un niño registrado sin conexión


@dataclass
class OperacionSincronizada:
    """Bitácora de una operación ya procesada: es lo que hace idempotente la sincronización."""

    id_operacion: str
    tipo: str
    id_dispositivo: str
    resultado: ResultadoOperacion
    id_recurso: str | None = None
    id_cliente: str | None = None
    fecha_local: datetime | None = None
    recibida_en: datetime = field(default_factory=ahora)


@dataclass
class ConflictoSincronizacion:
    """Operación que choca con un dato distinto del servidor; nunca se sobrescribe a ciegas."""

    id_operacion: str
    tipo: str
    motivo: str
    nino_id: str
    id_recurso: str
    datos_cliente: dict
    datos_servidor: dict
    registrado_por: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    estado: EstadoConflicto = EstadoConflicto.PENDIENTE
    resolucion: ResolucionConflicto | None = None
    creado_en: datetime = field(default_factory=ahora)
    resuelto_en: datetime | None = None
    resuelto_por: str | None = None


@dataclass(frozen=True)
class ResultadoSincronizacion:
    """Resultado de una operación del lote."""

    id_operacion: str
    tipo: str
    resultado: ResultadoOperacion
    id_recurso: str | None = None  # id del servidor del recurso aplicado, existente o en conflicto
    id_cliente: str | None = None  # mapeo id_cliente -> id_recurso de un niño
    id_conflicto: str | None = None
    mensaje: str | None = None
    errores: tuple[ErrorCampo, ...] = ()
    resultado_original: ResultadoOperacion | None = None  # solo en DUPLICADA por reenvío del id_operacion


@dataclass(frozen=True)
class ResumenSincronizacion:
    aplicadas: int = 0
    duplicadas: int = 0
    conflictos: int = 0
    rechazadas: int = 0
