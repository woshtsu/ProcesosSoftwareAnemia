"""Puerto de salida: persistencia de las visitas domiciliarias (VIS-3.5)."""

from datetime import date
from typing import Protocol

from app.domain.model.visita import VisitaDomiciliaria


class RepositorioVisitas(Protocol):
    def agregar_visita(self, visita: VisitaDomiciliaria) -> VisitaDomiciliaria:
        """Guarda la visita; lanza ConflictoVisita si el niño ya tiene una en esa fecha (restricción UNIQUE)."""
        ...

    def actualizar_visita(self, visita: VisitaDomiciliaria) -> VisitaDomiciliaria:
        """Reemplaza resultado, consumo y observaciones de una visita existente (al resolver un conflicto)."""
        ...

    def obtener_visita_del_dia(self, nino_id: str, fecha: date) -> VisitaDomiciliaria | None: ...

    def listar_visitas(self, nino_id: str) -> list[VisitaDomiciliaria]:
        """Visitas del niño, la más reciente primero."""
        ...

    def ultimas_visitas(self, nino_ids: set[str]) -> dict[str, date]:
        """Fecha de la visita más reciente de cada niño que tiene alguna (una sola consulta por lotes)."""
        ...
