"""Puerto de entrada: listado de niños en seguimiento (HU-04)."""

from typing import Protocol


class ConsultarSeguimiento(Protocol):
    def listar_seguimiento(
        self,
        estado: str | None = "ACTIVO",
        texto: str | None = None,
        clasificacion: str | None = None,
        limite: int | None = None,
    ) -> list[dict]:
        """Filas con: nino, ultima_evaluacion, dias_desde_ultimo_control, control_atrasado, controles_vencidos,
        edad_meses."""
        ...
