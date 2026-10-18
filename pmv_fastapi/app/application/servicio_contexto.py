"""Caso de uso: contexto de ejecución (fecha de hoy y fecha de referencia fija) para la interfaz y la API."""

from datetime import date

from app.domain.model.contexto import ContextoSistema
from app.ports.inbound.contexto import ConsultarContexto
from app.ports.outbound.reloj import Reloj


class ServicioContexto(ConsultarContexto):
    def __init__(self, reloj: Reloj, fecha_referencia: date | None = None):
        self.reloj = reloj
        self.fecha_referencia = fecha_referencia

    def contexto(self) -> ContextoSistema:
        return ContextoSistema(fecha_hoy=self.reloj.hoy(), fecha_referencia=self.fecha_referencia)
