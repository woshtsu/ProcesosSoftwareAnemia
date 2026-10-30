"""Puertos de entrada: barreras de acceso al tratamiento y alerta de barreras críticas (HIST-4.3 y HIST-4.4)."""

from typing import Protocol

from app.domain.model.barrera import AlertaBarrera, Barrera


class GestionarBarreras(Protocol):
    def registrar_barrera(self, nino_id: str, datos: dict, usuario: str) -> Barrera:
        """``datos``: tipo, detalle, fuente, fecha y recordatorio_id (todos opcionales salvo el tipo)."""
        ...

    def listar_barreras(self, nino_id: str) -> list[Barrera]: ...


class ConsultarAlertasBarreras(Protocol):
    def alertas_barreras(self, comunidad: str | None = None, prioridad: str | None = None) -> list[AlertaBarrera]: ...
