"""Adaptador de salida: reloj con una fecha fija, para demostraciones y análisis con un dataset (ADR-009)."""

from dataclasses import dataclass
from datetime import date

from app.ports.outbound.reloj import Reloj


@dataclass
class RelojFijo(Reloj):
    """«Hoy» es siempre ``fecha``: permite usar el corte de un dataset (p. ej. 30/06/2024) como fecha de referencia."""

    fecha: date

    def hoy(self) -> date:
        return self.fecha

    @classmethod
    def desde_texto(cls, texto: str) -> "RelojFijo":
        """Crea el reloj desde ``AAAA-MM-DD`` (valor de la variable de entorno FECHA_REFERENCIA)."""
        try:
            return cls(date.fromisoformat(texto.strip()))
        except ValueError:
            raise ValueError(
                f"FECHA_REFERENCIA inválida: '{texto}'. Use el formato AAAA-MM-DD (p. ej. 2024-06-30)."
            ) from None
