"""Caso de uso HIST-2.2: controles vencidos y alertas internas de los niños activos.

Una sola consulta por lotes (``listar`` trae niños y evaluaciones juntos) y cálculo en memoria: sin consultas por
niño (ADR-006).
"""

from collections.abc import Iterable

from app.domain.model.agenda import AgendaNino
from app.domain.model.alertas import AlertaControl, Prioridad, ResumenAlertas
from app.domain.model.entidades import Nino
from app.domain.model.errores import ErrorCampo, ErrorValidacion
from app.domain.service.agenda import generar_agenda
from app.domain.service.alertas import alertas_de_nino, ordenar_alertas, resumir_alertas
from app.ports.inbound.alertas import ConsultarControlesVencidos
from app.ports.outbound.cache_agendas import ProveedorAgendasActivos
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_ninos import RepositorioNinos


class ServicioAlertas(ConsultarControlesVencidos):
    def __init__(
        self,
        repo: RepositorioNinos,
        reloj: Reloj,
        cache_agendas: ProveedorAgendasActivos | None = None,
    ):
        self.repo = repo
        self.reloj = reloj
        self.cache_agendas = cache_agendas

    def _agendas_activos(self) -> Iterable[tuple[Nino, AgendaNino]]:
        if self.cache_agendas is not None:
            return self.cache_agendas.obtener_agendas()
        hoy = self.reloj.hoy()
        return [(nino, generar_agenda(nino, hoy)) for nino in self.repo.listar(estado="ACTIVO")]

    def listar_controles_vencidos(
        self, comunidad: str | None = None, prioridad: str | None = None, limite: int | None = None
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
        ordenadas = ordenar_alertas(alertas)
        return ordenadas[:limite] if limite is not None else ordenadas

    def resumen_alertas(self) -> ResumenAlertas:
        alertas: list[AlertaControl] = []
        proximos = 0
        for nino, agenda in self._agendas_activos():
            alertas += alertas_de_nino(nino, agenda)
            proximos += agenda.resumen.proximos
        return resumir_alertas(alertas, proximos)
