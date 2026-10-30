"""Puerto de entrada: contexto de ejecución (fecha de hoy y fecha de referencia fija, si la hay)."""

from typing import Protocol

from app.domain.model.contexto import ContextoSistema


class ConsultarContexto(Protocol):
    def contexto(self) -> ContextoSistema: ...
