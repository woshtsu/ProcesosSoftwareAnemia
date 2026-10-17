"""Puerto de salida: reloj del sistema (permite fijar «hoy» en las pruebas)."""

from datetime import date
from typing import Protocol


class Reloj(Protocol):
    def hoy(self) -> date:
        """Fecha de hoy en Perú."""
        ...
