"""Puerto de entrada: controles vencidos y alertas internas (HIST-2.2)."""

from typing import Protocol

from app.domain.model.alertas import AlertaControl, ResumenAlertas


class ConsultarControlesVencidos(Protocol):
    def listar_controles_vencidos(
        self, comunidad: str | None = None, prioridad: str | None = None
    ) -> list[AlertaControl]: ...

    def resumen_alertas(self) -> ResumenAlertas: ...
