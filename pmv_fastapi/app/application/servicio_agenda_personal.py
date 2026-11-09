"""Caso de uso HIST-2.3: agenda del personal de un establecimiento en un rango de fechas.

Una sola consulta por lotes (``listar`` trae niños y evaluaciones juntos) y cálculo en memoria: sin consultas por
niño (ADR-006). Los filtros por establecimiento y comunidad se aplican antes de calcular las agendas.
"""

from datetime import date

from app.domain.model.agenda_personal import AgendaPersonal
from app.domain.service.agenda import generar_agenda
from app.domain.service.agenda_personal import construir_agenda_personal, resolver_rango
from app.domain.service.validaciones import exigir, validar_rango_agenda
from app.ports.inbound.agenda_personal import ConsultarAgendaPersonal
from app.ports.outbound.cache_agendas import ProveedorAgendasActivos
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_ninos import RepositorioNinos


def _igual(a: str, b: str) -> bool:
    return a.strip().casefold() == b.strip().casefold()


class ServicioAgendaPersonal(ConsultarAgendaPersonal):
    def __init__(
        self,
        repo: RepositorioNinos,
        reloj: Reloj,
        cache_agendas: ProveedorAgendasActivos | None = None,
    ):
        self.repo = repo
        self.reloj = reloj
        self.cache_agendas = cache_agendas

    def agenda_personal(
        self,
        desde: date | None = None,
        hasta: date | None = None,
        establecimiento: str | None = None,
        comunidad: str | None = None,
    ) -> AgendaPersonal:
        hoy = self.reloj.hoy()
        desde, hasta = resolver_rango(desde, hasta, hoy)
        exigir(validar_rango_agenda(desde, hasta))
        activos_con_agenda = (
            self.cache_agendas.obtener_agendas()
            if self.cache_agendas is not None
            else [(n, generar_agenda(n, hoy)) for n in self.repo.listar(estado="ACTIVO")]
        )
        establecimientos = sorted({n.establecimiento for n, _ in activos_con_agenda}, key=str.casefold)
        del_establecimiento = [
            (n, ag) for n, ag in activos_con_agenda if not establecimiento or _igual(n.establecimiento, establecimiento)
        ]
        comunidades = sorted({n.comunidad for n, _ in del_establecimiento}, key=str.casefold)
        seleccion = [(n, ag) for n, ag in del_establecimiento if not comunidad or _igual(n.comunidad, comunidad)]
        return construir_agenda_personal(
            seleccion,
            desde,
            hasta,
            hoy,
            establecimiento=establecimiento or None,
            comunidad=comunidad or None,
            establecimientos_disponibles=establecimientos,
            comunidades_disponibles=comunidades,
        )
