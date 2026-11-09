"""Puerto de salida: persistencia de niños y evaluaciones.

Los adaptadores de persistencia (SQLAlchemy, memoria) implementan este contrato; el dominio y los casos de uso
nunca importan SQLAlchemy ni FastAPI.
"""

from datetime import date
from typing import Protocol

from app.domain.model.asistencia import AsistenciaControl
from app.domain.model.entidades import Evaluacion, Nino


class RepositorioNinos(Protocol):
    def version_datos(self) -> int:
        """Versión monótona de los datos (se incrementa en cada escritura de niños, evaluaciones o asistencias)."""
        ...

    def guardar(self, nino: Nino) -> Nino: ...

    def guardar_varios(self, ninos: list[Nino]) -> int:
        """Guarda niños con sus evaluaciones en una sola transacción (importaciones); devuelve cuántos guardó."""
        ...

    def eliminar_por_origen(self, origen: str) -> int:
        """Elimina los niños de un origen (con sus evaluaciones y asistencias); devuelve cuántos eliminó."""
        ...

    def contar_por_origen(self, origen: str) -> int: ...

    def actualizar(self, nino: Nino) -> Nino: ...

    def agregar_evaluacion(self, evaluacion: Evaluacion) -> Evaluacion: ...

    def agregar_asistencia(self, asistencia: AsistenciaControl) -> AsistenciaControl:
        """Guarda la asistencia; lanza ConflictoAsistencia si el control ya tiene una (restricción UNIQUE)."""
        ...

    def actualizar_evaluacion(self, evaluacion: Evaluacion) -> Evaluacion:
        """Reemplaza los valores de una evaluación existente (solo al resolver un conflicto de sincronización)."""
        ...

    def actualizar_asistencia(self, asistencia: AsistenciaControl) -> AsistenciaControl:
        """Reemplaza el estado y el motivo de una asistencia existente (solo al resolver un conflicto)."""
        ...

    def obtener(self, nino_id: str) -> Nino | None: ...

    def obtener_por_dni(self, dni: str) -> Nino | None: ...

    def listar(self, estado: str | None = None, texto: str | None = None) -> list[Nino]:
        """Niños con sus evaluaciones, cargados por lotes (sin consultas por niño)."""
        ...

    def evaluaciones_en_periodo(self, desde: date, hasta: date) -> list[Evaluacion]: ...

    def contar_registrados_en_periodo(self, desde: date, hasta: date) -> int: ...

    def obtener_varios(self, ids: set[str]) -> dict[str, Nino]: ...
