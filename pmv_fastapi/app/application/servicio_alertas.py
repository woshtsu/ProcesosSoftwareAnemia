"""Caso de uso HIST-2.2: controles vencidos y alertas internas de los niños activos.

Una sola consulta por lotes (``listar`` trae niños y evaluaciones juntos) y cálculo en memoria: sin consultas por
niño (ADR-006).
"""

from collections.abc import Iterator

from app.domain.model.agenda import AgendaNino
from app.domain.model.alertas import AlertaControl, Prioridad, ResumenAlertas
from app.domain.model.entidades import Nino
from app.domain.model.errores import ErrorCampo, ErrorValidacion
from app.domain.service.agenda import generar_agenda
from app.domain.service.alertas import alertas_de_nino, ordenar_alertas, resumir_alertas
from app.ports.inbound.alertas import ConsultarControlesVencidos
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_ninos import RepositorioNinos


class ServicioAlertas(ConsultarControlesVencidos):
    def __init__(self, repo: RepositorioNinos, reloj: Reloj):
        self.repo = repo
        self.reloj = reloj

    def _agendas_activos(self) -> Iterator[tuple[Nino, AgendaNino]]:
        hoy = self.reloj.hoy()
        for nino in self.repo.listar(estado="ACTIVO"):
            yield nino, generar_agenda(nino, hoy)

    def listar_controles_vencidos(
        self, comunidad: str | None = None, prioridad: str | None = None
    ) -> list[AlertaControl]:
        if prioridad and prioridad not in {p.value for p in Prioridad}:
            raise ErrorValidacion([ErrorCampo("prioridad", "La prioridad debe ser ALTA, MEDIA o BAJA.")])
        alertas: list[AlertaControl] = []
        for nino, agenda in self._agendas_activos():
            if comunidad and nino.comunidad.casefold() != comunidad.strip().casefold():
                continue
            alertas += alertas_de_nino(nino, agenda)
        if prioridad:
            alertas = [a for a in alertas if a.prioridad == prioridad]
        return ordenar_alertas(alertas)

    def resumen_alertas(self) -> ResumenAlertas:
        alertas: list[AlertaControl] = []
        proximos = 0
        for nino, agenda in self._agendas_activos():
            alertas += alertas_de_nino(nino, agenda)
            proximos += agenda.resumen.proximos
        return resumir_alertas(alertas, proximos)
