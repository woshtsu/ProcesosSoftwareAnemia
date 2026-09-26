"""
Ports (interfaces) del dominio — PMV Anemia Junín.

Se expresan con typing.Protocol para no imponer herencia y mantener el dominio
libre de dependencias externas.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Protocol, runtime_checkable
from uuid import UUID

from anemia_junin.domain.entities import Dosaje, IntentoRegistro, Nino

# ─── Filtros de lista ─────────────────────────────────────────────────────────

class FiltroNinos:
    """Parámetros de búsqueda/filtrado para la lista de niños."""

    def __init__(
        self,
        *,
        q: str | None = None,
        distrito: str | None = None,
        clasificacion: str | None = None,
        pagina: int = 1,
        tamano: int = 20,
        fecha_referencia: date | None = None,
    ) -> None:
        # fecha_referencia = "hoy" según el puerto Reloj (ADR-001: tiempo testeable);
        # define la ventana de seguimiento activo de 6 a 59 meses.
        self.fecha_referencia = fecha_referencia
        self.q = q
        self.distrito = distrito
        self.clasificacion = clasificacion
        self.pagina = max(1, pagina)
        self.tamano = min(max(1, tamano), 100)

    @property
    def offset(self) -> int:
        return (self.pagina - 1) * self.tamano


# ─── Resultado paginado ───────────────────────────────────────────────────────

class PaginaNinos:
    def __init__(self, items: list, total: int, pagina: int, tamano: int) -> None:
        self.items = items
        self.total = total
        self.pagina = pagina
        self.tamano = tamano


# ─── Interfaces (Protocols) ───────────────────────────────────────────────────

@runtime_checkable
class RepositorioNinos(Protocol):
    def guardar(self, nino: Nino) -> None: ...
    def obtener_por_dni(self, dni: str) -> Nino | None: ...
    def obtener_por_id(self, nino_id: UUID) -> Nino | None: ...
    def actualizar(self, nino: Nino) -> None: ...
    def listar(self, filtro: FiltroNinos) -> PaginaNinos: ...
    def consultar_reporte(
        self,
        *,
        desde_utc: datetime,
        hasta_utc: datetime,
        desde_iso: str,
        hasta_iso: str,
    ) -> dict: ...


@runtime_checkable
class RepositorioDosajes(Protocol):
    def guardar(self, dosaje: Dosaje) -> None: ...
    def listar_por_nino(self, nino_id: UUID) -> list[Dosaje]: ...
    def ultimo_por_nino(self, nino_id: UUID) -> Dosaje | None: ...


@runtime_checkable
class RepositorioIntentos(Protocol):
    def guardar(self, intento: IntentoRegistro) -> None: ...
    def contar_en_periodo(self, desde: datetime, hasta: datetime) -> dict[str, int]: ...


@runtime_checkable
class UnidadDeTrabajo(Protocol):
    """Context manager para transacciones atómicas."""

    def __enter__(self) -> UnidadDeTrabajo: ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool: ...

    @property
    def ninos(self) -> RepositorioNinos: ...

    @property
    def dosajes(self) -> RepositorioDosajes: ...

    @property
    def intentos(self) -> RepositorioIntentos: ...


@runtime_checkable
class ProveedorNormativo(Protocol):
    """Accede a la configuración normativa (NTS 213)."""

    def version(self) -> str: ...
    def grupos_edad(self) -> list[dict]: ...
    def tabla_ajuste(self) -> list[dict]: ...


@runtime_checkable
class Reloj(Protocol):
    """Fuente de tiempo — testeable."""

    def ahora_utc(self) -> datetime: ...
    def hoy(self) -> date: ...
