"""Contexto de ejecución del sistema: fecha de hoy y, si está fijada, la fecha de referencia (ADR-009)."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ContextoSistema:
    fecha_hoy: date  # «hoy» según el reloj del sistema
    fecha_referencia: date | None  # fecha fija configurada (p. ej. el corte de un dataset); None con el reloj real
