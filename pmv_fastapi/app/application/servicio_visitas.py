"""Caso de uso VIS-3.5: registrar visitas domiciliarias y priorizar a los niños en tratamiento (ADR-013).

Una sola carga por lotes de niños y de últimas visitas, con el cálculo en memoria (sin consultas por niño, ADR-006).
"""

from app.domain.model.errores import ConflictoVisita, NoEncontrado
from app.domain.model.visita import NinoPriorizado, VisitaDomiciliaria
from app.domain.service.agenda import generar_agenda
from app.domain.service.validaciones import exigir
from app.domain.service.visitas import (
    crear_visita,
    en_tratamiento,
    ordenar_priorizados,
    priorizar_nino,
    validar_datos_visita,
    validar_limite,
)
from app.ports.inbound.visitas import ConsultarVisitasPriorizadas, GestionarVisitas
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_ninos import RepositorioNinos
from app.ports.outbound.repositorio_visitas import RepositorioVisitas


class ServicioVisitas(GestionarVisitas, ConsultarVisitasPriorizadas):
    def __init__(self, repo: RepositorioNinos, visitas: RepositorioVisitas, reloj: Reloj):
        self.repo = repo
        self.visitas = visitas
        self.reloj = reloj

    def _nino(self, nino_id: str):
        nino = self.repo.obtener(nino_id)
        if not nino:
            raise NoEncontrado("No existe el expediente solicitado.")
        return nino

    def registrar_visita(self, nino_id: str, datos: dict, usuario: str) -> VisitaDomiciliaria:
        nino = self._nino(nino_id)
        exigir(validar_datos_visita(datos, nino.fecha_nacimiento, self.reloj.hoy()))
        if self.visitas.obtener_visita_del_dia(nino.id, datos["fecha"]):
            raise ConflictoVisita(f"El niño ya tiene una visita registrada el {datos['fecha'].isoformat()}.")
        return self.visitas.agregar_visita(crear_visita(nino.id, datos, usuario))

    def listar_visitas(self, nino_id: str) -> list[VisitaDomiciliaria]:
        return self.visitas.listar_visitas(self._nino(nino_id).id)

    def visitas_priorizadas(self, establecimiento: str | None, limite: int) -> list[NinoPriorizado]:
        exigir(validar_limite(limite))
        hoy = self.reloj.hoy()
        filtro = (establecimiento or "").strip().casefold()
        candidatos = [
            n
            for n in self.repo.listar(estado="ACTIVO")
            if en_tratamiento(n) and (not filtro or n.establecimiento.casefold() == filtro)
        ]
        ultimas = self.visitas.ultimas_visitas({n.id for n in candidatos})
        items = [priorizar_nino(n, generar_agenda(n, hoy), ultimas.get(n.id), hoy) for n in candidatos]
        return ordenar_priorizados(items)[:limite]
