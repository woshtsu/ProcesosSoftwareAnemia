"""Puertos de salida (interfaces) que el núcleo necesita.

Los adaptadores de persistencia implementan este contrato; el dominio y los
casos de uso nunca importan SQLAlchemy ni FastAPI.
"""

from datetime import date
from typing import Protocol

from app.domain.entidades import Evaluacion, Nino


class RepositorioNinos(Protocol):
    def guardar(self, nino: Nino) -> Nino: ...

    def actualizar(self, nino: Nino) -> Nino: ...

    def agregar_evaluacion(self, evaluacion: Evaluacion) -> Evaluacion: ...

    def obtener(self, nino_id: str) -> Nino | None: ...

    def obtener_por_dni(self, dni: str) -> Nino | None: ...

    def listar(self, estado: str | None = None, texto: str | None = None) -> list[Nino]: ...

    def evaluaciones_en_periodo(self, desde: date, hasta: date) -> list[Evaluacion]: ...

    def ninos_registrados_en_periodo(self, desde: date, hasta: date) -> list[Nino]: ...


class Reloj(Protocol):
    def hoy(self) -> date: ...
