"""Caso de uso HIST-2.1: agenda de controles de un niño, calculada en línea desde su expediente (ADR-007)."""

from app.domain.model.agenda import AgendaNino
from app.domain.model.errores import NoEncontrado
from app.domain.service.agenda import generar_agenda
from app.ports.inbound.agenda import GenerarAgenda
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_ninos import RepositorioNinos


class ServicioAgenda(GenerarAgenda):
    def __init__(self, repo: RepositorioNinos, reloj: Reloj):
        self.repo = repo
        self.reloj = reloj

    def generar_agenda(self, nino_id: str) -> AgendaNino:
        nino = self.repo.obtener(nino_id)
        if not nino:
            raise NoEncontrado("No existe el expediente solicitado.")
        return generar_agenda(nino, self.reloj.hoy())
