"""Adaptador de salida: reloj real del sistema, en hora de Perú."""

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.model.tiempo import ZONA_PERU
from app.ports.outbound.reloj import Reloj


@dataclass
class RelojSistema(Reloj):
    """Fecha de hoy en Perú, independiente de la zona horaria del servidor (DEF-02)."""

    def hoy(self) -> date:
        return datetime.now(ZONA_PERU).date()
