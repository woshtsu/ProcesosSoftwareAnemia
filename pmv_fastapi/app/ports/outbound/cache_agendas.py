"""Puerto de salida: proveedor de la instantánea de agendas de niños activos."""

from typing import Protocol

from app.domain.model.agenda import AgendaNino
from app.domain.model.entidades import Nino


class ProveedorAgendasActivos(Protocol):
    def obtener_agendas(self) -> list[tuple[Nino, AgendaNino]]: ...
