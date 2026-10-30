"""Puertos de entrada: visita domiciliaria y su priorización (VIS-3.5)."""

from typing import Protocol

from app.domain.model.visita import NinoPriorizado, VisitaDomiciliaria


class GestionarVisitas(Protocol):
    def registrar_visita(self, nino_id: str, datos: dict, usuario: str) -> VisitaDomiciliaria:
        """``datos``: fecha, resultado, consume_suplemento y observaciones."""
        ...

    def listar_visitas(self, nino_id: str) -> list[VisitaDomiciliaria]: ...


class ConsultarVisitasPriorizadas(Protocol):
    def visitas_priorizadas(self, establecimiento: str | None, limite: int) -> list[NinoPriorizado]: ...
