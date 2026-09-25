"""
DTOs de entrada y salida — PMV Anemia Junín.

Los DTOs desacoplan la capa de aplicación de los adaptadores.
No contienen lógica de negocio.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from anemia_junin.domain.entities import Clasificacion, Sexo, TipoNacimiento

# ─── Entrada ─────────────────────────────────────────────────────────────────

@dataclass
class DosajeInicialDTO:
    fecha_dosaje: date
    hb_observada_ddl: int   # ya convertido a décimas


@dataclass
class CrearNinoDTO:
    dni: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    sexo: Sexo
    tipo_nacimiento: TipoNacimiento
    peso_g: int
    distrito: str
    altitud_msnm: int
    cuidador: str
    telefono: str | None
    dosaje_inicial: DosajeInicialDTO | None = None


@dataclass
class ActualizarNinoDTO:
    peso_g: int | None = None
    distrito: str | None = None
    altitud_msnm: int | None = None
    cuidador: str | None = None
    telefono: str | None = None   # "" o None para borrar


@dataclass
class CrearDosajeDTO:
    fecha_dosaje: date
    hb_observada_ddl: int
    altitud_msnm: int


@dataclass
class FiltroListaDTO:
    q: str | None = None
    distrito: str | None = None
    clasificacion: str | None = None
    pagina: int = 1
    tamano: int = 20


@dataclass
class PeriodoReporteDTO:
    desde: date
    hasta: date


# ─── Salida ───────────────────────────────────────────────────────────────────

@dataclass
class NinoSalidaDTO:
    id: UUID
    dni: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    sexo: Sexo
    tipo_nacimiento: TipoNacimiento
    peso_kg: float
    distrito: str
    altitud_msnm: int
    cuidador: str
    telefono: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class DosajeSalidaDTO:
    id: UUID
    nino_id: UUID
    fecha_dosaje: date
    hb_observada: float
    altitud_msnm: int
    ajuste_gdl: float
    hb_ajustada: float
    edad_meses: int
    clasificacion: Clasificacion
    version_normativa: str
    advertencias: list[str]
    created_at: datetime


@dataclass
class NinoResumenDTO:
    dni: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    sexo: Sexo
    distrito: str
    clasificacion_ultimo_dosaje: Clasificacion


@dataclass
class ExpedienteDTO:
    nino: NinoSalidaDTO
    clasificacion_actual: Clasificacion
    historial_dosajes: list[DosajeSalidaDTO]


@dataclass
class PaginaDTO:
    items: list
    total: int
    pagina: int
    tamano: int


@dataclass
class CalidadRegistroDTO:
    intentos_aceptados: int
    intentos_rechazados: int
    tasa_aceptacion_pct: float | None   # None si no hay intentos


@dataclass
class ReporteRegistrosDTO:
    periodo_desde: date
    periodo_hasta: date
    ninos_registrados: int
    dosajes_registrados: int
    distribucion_clasificacion: dict[str, int]
    distribucion_distrito: dict[str, int]
    calidad_registro: CalidadRegistroDTO
