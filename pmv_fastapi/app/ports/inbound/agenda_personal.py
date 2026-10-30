"""Puerto de entrada: agenda del personal de un establecimiento (HIST-2.3)."""

from datetime import date
from typing import Protocol

from app.domain.model.agenda_personal import AgendaPersonal


class ConsultarAgendaPersonal(Protocol):
    def agenda_personal(
        self,
        desde: date | None = None,
        hasta: date | None = None,
        establecimiento: str | None = None,
        comunidad: str | None = None,
    ) -> AgendaPersonal:
        """Controles programados por día en el rango (por defecto, la semana de la fecha de referencia)."""
        ...
