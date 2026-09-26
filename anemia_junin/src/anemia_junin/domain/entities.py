"""
Entidades del dominio — PMV Anemia Junín (INC-1).

Sin dependencias externas (sin Flask, sin SQLite, sin adaptadores).
Los valores monetarios y de hemoglobina se almacenan como enteros en unidades mínimas
para evitar errores de punto flotante:
  - Hb en décimas de g/dL (ej: 10.5 g/dL → 105)
  - Peso en gramos (ej: 8.500 kg → 8500)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum


class Sexo(StrEnum):
    F = "F"
    M = "M"


class TipoNacimiento(StrEnum):
    TERMINO = "TERMINO"
    PREMATURO = "PREMATURO"


class Clasificacion(StrEnum):
    SEVERA = "SEVERA"
    MODERADA = "MODERADA"
    LEVE = "LEVE"
    SIN_ANEMIA = "SIN_ANEMIA"
    NO_EVALUABLE = "NO_EVALUABLE"
    SIN_DOSAJE = "SIN_DOSAJE"


@dataclass
class Nino:
    """Representa a un niño en seguimiento de anemia."""

    id: uuid.UUID
    dni: str                        # texto; preserva ceros iniciales
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    sexo: Sexo
    tipo_nacimiento: TipoNacimiento
    peso_g: int                     # gramos; 1 kg → 1000
    distrito: str
    altitud_msnm: int               # 0–4999
    cuidador: str
    telefono: str | None         # None o 9 dígitos
    created_at: datetime
    updated_at: datetime

    @classmethod
    def nuevo(
        cls,
        *,
        dni: str,
        nombres: str,
        apellidos: str,
        fecha_nacimiento: date,
        sexo: Sexo,
        tipo_nacimiento: TipoNacimiento,
        peso_g: int,
        distrito: str,
        altitud_msnm: int,
        cuidador: str,
        telefono: str | None,
        ahora: datetime,
    ) -> Nino:
        return cls(
            id=uuid.uuid4(),
            dni=dni,
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            tipo_nacimiento=tipo_nacimiento,
            peso_g=peso_g,
            distrito=distrito,
            altitud_msnm=altitud_msnm,
            cuidador=cuidador,
            telefono=telefono,
            created_at=ahora,
            updated_at=ahora,
        )


@dataclass
class Dosaje:
    """Dosaje de hemoglobina — registro histórico inmutable."""

    id: uuid.UUID
    nino_id: uuid.UUID
    fecha_dosaje: date
    hb_observada_ddl: int           # décimas de g/dL; ej: 10.5 → 105
    altitud_msnm: int               # altitud en el momento del dosaje
    ajuste_ddl: int                 # décimas de g/dL; ej: 1.8 → 18
    hb_ajustada_ddl: int            # = hb_observada_ddl - ajuste_ddl
    edad_meses: int                 # edad completa al momento del dosaje
    clasificacion: Clasificacion
    version_normativa: str
    advertencias: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))

    @classmethod
    def nuevo(
        cls,
        *,
        nino_id: uuid.UUID,
        fecha_dosaje: date,
        hb_observada_ddl: int,
        altitud_msnm: int,
        ajuste_ddl: int,
        hb_ajustada_ddl: int,
        edad_meses: int,
        clasificacion: Clasificacion,
        version_normativa: str,
        advertencias: list[str],
        ahora: datetime,
    ) -> Dosaje:
        return cls(
            id=uuid.uuid4(),
            nino_id=nino_id,
            fecha_dosaje=fecha_dosaje,
            hb_observada_ddl=hb_observada_ddl,
            altitud_msnm=altitud_msnm,
            ajuste_ddl=ajuste_ddl,
            hb_ajustada_ddl=hb_ajustada_ddl,
            edad_meses=edad_meses,
            clasificacion=clasificacion,
            version_normativa=version_normativa,
            advertencias=advertencias,
            created_at=ahora,
        )


@dataclass
class IntentoRegistro:
    """Registro de auditoría de intentos de alta de niño (sin PII rechazada)."""

    id: uuid.UUID
    momento: datetime
    operacion: str          # "CREAR_NINO"
    resultado: str          # "ACEPTADO" | "RECHAZADO"
    codigos_error: list[str] = field(default_factory=list)

    @classmethod
    def nuevo(
        cls,
        *,
        operacion: str,
        resultado: str,
        codigos_error: list[str],
        ahora: datetime,
    ) -> IntentoRegistro:
        return cls(
            id=uuid.uuid4(),
            momento=ahora,
            operacion=operacion,
            resultado=resultado,
            codigos_error=codigos_error,
        )
