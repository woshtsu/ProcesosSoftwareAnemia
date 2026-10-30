"""Casos de uso HIST-4.3 y HIST-4.4: registrar barreras y alertar las críticas (ADR-014).

La alerta carga una sola vez los niños activos y las barreras vigentes (consultas por lotes, ADR-006) y calcula en
memoria con las reglas de ``domain/service/barreras.py``.
"""

from app.domain.model.alertas import Prioridad
from app.domain.model.barrera import AlertaBarrera, Barrera
from app.domain.model.errores import ConflictoBarrera, ErrorCampo, ErrorValidacion, NoEncontrado
from app.domain.service.agenda import generar_agenda
from app.domain.service.barreras import (
    crear_barrera,
    evaluar_barreras_nino,
    fecha_limite_consulta,
    ordenar_alertas_barrera,
    validar_datos_barrera,
)
from app.domain.service.validaciones import exigir
from app.ports.inbound.barreras import ConsultarAlertasBarreras, GestionarBarreras
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_barreras import RepositorioBarreras
from app.ports.outbound.repositorio_ninos import RepositorioNinos


class ServicioBarreras(GestionarBarreras, ConsultarAlertasBarreras):
    def __init__(self, repo: RepositorioNinos, barreras: RepositorioBarreras, reloj: Reloj):
        self.repo = repo
        self.barreras = barreras
        self.reloj = reloj

    def _nino(self, nino_id: str):
        nino = self.repo.obtener(nino_id)
        if not nino:
            raise NoEncontrado("No existe el expediente solicitado.")
        return nino

    def registrar_barrera(self, nino_id: str, datos: dict, usuario: str) -> Barrera:
        nino = self._nino(nino_id)
        hoy = self.reloj.hoy()
        exigir(validar_datos_barrera(datos, nino.fecha_nacimiento, hoy))
        barrera = crear_barrera(nino.id, datos, usuario, hoy)
        previa = self.barreras.obtener_equivalente(nino.id, barrera.tipo, barrera.fecha, barrera.fuente)
        if previa:
            raise ConflictoBarrera(
                f"El niño ya tiene registrada esa barrera el {barrera.fecha.isoformat()} con la misma fuente.",
                previa.id,
            )
        return self.barreras.agregar_barrera(barrera)

    def listar_barreras(self, nino_id: str) -> list[Barrera]:
        return self.barreras.listar_barreras(self._nino(nino_id).id)

    def alertas_barreras(self, comunidad: str | None = None, prioridad: str | None = None) -> list[AlertaBarrera]:
        if prioridad and prioridad not in {Prioridad.ALTA.value, Prioridad.MEDIA.value}:
            raise ErrorValidacion([ErrorCampo("prioridad", "La prioridad debe ser ALTA o MEDIA.")])
        hoy = self.reloj.hoy()
        por_nino = self.barreras.barreras_desde(fecha_limite_consulta(hoy))
        filtro = (comunidad or "").strip().casefold()
        alertas = []
        for nino in self.repo.listar(estado="ACTIVO"):
            if nino.id not in por_nino or (filtro and nino.comunidad.casefold() != filtro):
                continue
            alerta = evaluar_barreras_nino(nino, generar_agenda(nino, hoy), por_nino[nino.id], hoy)
            if alerta and (not prioridad or alerta.prioridad == prioridad):
                alertas.append(alerta)
        return ordenar_alertas_barrera(alertas)
