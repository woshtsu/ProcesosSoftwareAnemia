"""Puerto de entrada: agenda de controles de un niño (HIST-2.1)."""

from typing import Protocol

from app.domain.model.agenda import AgendaNino


class GenerarAgenda(Protocol):
    def generar_agenda(self, nino_id: str) -> AgendaNino: ...
