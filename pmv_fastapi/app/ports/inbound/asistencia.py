"""Puerto de entrada: asistencia a los controles programados (HIST-2.4)."""

from typing import Protocol

from app.domain.model.asistencia import AsistenciaControl


class RegistrarAsistencia(Protocol):
    def registrar_asistencia(self, nino_id: str, codigo: str, datos: dict, usuario: str) -> AsistenciaControl:
        """``datos``: fecha_programada, estado (ASISTIO o NO_ASISTIO), motivo y evaluacion_id (opcionales)."""
        ...

    def listar_asistencias(self, nino_id: str) -> list[AsistenciaControl]: ...
