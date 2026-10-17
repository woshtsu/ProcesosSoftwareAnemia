"""Puerto de salida: persistencia de niños y evaluaciones.

Los adaptadores de persistencia (SQLAlchemy, memoria) implementan este contrato; el dominio y los casos de uso
nunca importan SQLAlchemy ni FastAPI.
"""

from datetime import date
from typing import Protocol

from app.domain.model.entidades import Evaluacion, Nino


class RepositorioNinos(Protocol):
    def guardar(self, nino: Nino) -> Nino: ...

    def actualizar(self, nino: Nino) -> Nino: ...

    def agregar_evaluacion(self, evaluacion: Evaluacion) -> Evaluacion: ...

    def obtener(self, nino_id: str) -> Nino | None: ...

    def obtener_por_dni(self, dni: str) -> Nino | None: ...

    def listar(self, estado: str | None = None, texto: str | None = None) -> list[Nino]:
        """Niños con sus evaluaciones, cargados por lotes (sin consultas por niño)."""
        ...

    def evaluaciones_en_periodo(self, desde: date, hasta: date) -> list[Evaluacion]: ...

    def contar_registrados_en_periodo(self, desde: date, hasta: date) -> int: ...

    def obtener_varios(self, ids: set[str]) -> dict[str, Nino]: ...
