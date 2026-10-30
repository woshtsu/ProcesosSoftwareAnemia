"""Puerto de salida: persistencia de las barreras de acceso al tratamiento (HIST-4.3)."""

from datetime import date
from typing import Protocol

from app.domain.model.barrera import Barrera


class RepositorioBarreras(Protocol):
    def agregar_barrera(self, barrera: Barrera) -> Barrera:
        """Guarda la barrera; lanza ConflictoBarrera si el niño ya la tiene (restricción UNIQUE tipo, fecha, fuente)."""
        ...

    def obtener_equivalente(self, nino_id: str, tipo: str, fecha: date, fuente: str) -> Barrera | None: ...

    def listar_barreras(self, nino_id: str) -> list[Barrera]:
        """Barreras del niño, la más reciente primero."""
        ...

    def barreras_desde(self, desde: date) -> dict[str, list[Barrera]]:
        """Barreras con fecha desde ``desde`` de todos los niños, agrupadas por niño (una sola consulta por lotes)."""
        ...
