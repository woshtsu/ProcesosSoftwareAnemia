"""Puerto de entrada: reporte del periodo (HU-05)."""

from datetime import date
from typing import Protocol


class GenerarReporte(Protocol):
    def reporte_periodo(self, desde: date, hasta: date) -> dict: ...
