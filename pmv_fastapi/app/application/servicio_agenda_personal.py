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
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_ninos import RepositorioNinos


def _igual(a: str, b: str) -> bool:
    return a.strip().casefold() == b.strip().casefold()


class ServicioAgendaPersonal(ConsultarAgendaPersonal):
    def __init__(self, repo: RepositorioNinos, reloj: Reloj):
        self.repo = repo
        self.reloj = reloj

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
        activos = self.repo.listar(estado="ACTIVO")
        establecimientos = sorted({n.establecimiento for n in activos}, key=str.casefold)
        del_establecimiento = [n for n in activos if not establecimiento or _igual(n.establecimiento, establecimiento)]
        comunidades = sorted({n.comunidad for n in del_establecimiento}, key=str.casefold)
        seleccion = [n for n in del_establecimiento if not comunidad or _igual(n.comunidad, comunidad)]
        return construir_agenda_personal(
            ((n, generar_agenda(n, hoy)) for n in seleccion),
            desde,
            hasta,
            hoy,
            establecimiento=establecimiento or None,
            comunidad=comunidad or None,
            establecimientos_disponibles=establecimientos,
            comunidades_disponibles=comunidades,
        )
