"""Adaptador en memoria: implementa el puerto para pruebas unitarias del núcleo."""

import copy
from datetime import date

from app.domain.model.asistencia import AsistenciaControl
from app.domain.model.entidades import Evaluacion, Nino
from app.domain.model.errores import ConflictoAsistencia
from app.domain.model.tiempo import fecha_local
from app.ports.outbound.repositorio_ninos import RepositorioNinos


class RepositorioEnMemoria(RepositorioNinos):
    def __init__(self) -> None:
        self._ninos: dict[str, Nino] = {}

    def guardar(self, nino: Nino) -> Nino:
        self._ninos[nino.id] = copy.deepcopy(nino)
        return nino

    def guardar_varios(self, ninos: list[Nino]) -> int:
        for nino in ninos:
            self.guardar(nino)
        return len(ninos)

    def contar_por_origen(self, origen: str) -> int:
        return sum(1 for n in self._ninos.values() if n.origen == origen)

    def eliminar_por_origen(self, origen: str) -> int:
        ids = [i for i, n in self._ninos.items() if n.origen == origen]
        for i in ids:
            del self._ninos[i]
        return len(ids)

    def actualizar(self, nino: Nino) -> Nino:
        evaluaciones, asistencias = self._ninos[nino.id].evaluaciones, self._ninos[nino.id].asistencias
        self._ninos[nino.id] = copy.deepcopy(nino)
        self._ninos[nino.id].evaluaciones = evaluaciones
        self._ninos[nino.id].asistencias = asistencias
        return nino

    def agregar_evaluacion(self, evaluacion: Evaluacion) -> Evaluacion:
        self._ninos[evaluacion.nino_id].evaluaciones.append(copy.deepcopy(evaluacion))
        return evaluacion

    def agregar_asistencia(self, asistencia: AsistenciaControl) -> AsistenciaControl:
        existentes = self._ninos[asistencia.nino_id].asistencias
        if any(
            a.codigo_control == asistencia.codigo_control and a.fecha_programada == asistencia.fecha_programada
            for a in existentes
        ):
            raise ConflictoAsistencia(
                f"El control {asistencia.codigo_control} del {asistencia.fecha_programada.isoformat()} "
                "ya tiene una asistencia."
            )
        existentes.append(copy.deepcopy(asistencia))
        return asistencia

    def obtener(self, nino_id: str) -> Nino | None:
        nino = self._ninos.get(nino_id)
        return copy.deepcopy(nino) if nino else None

    def obtener_por_dni(self, dni: str) -> Nino | None:
        for nino in self._ninos.values():
            if nino.dni == dni:
                return copy.deepcopy(nino)
        return None

    def listar(self, estado: str | None = None, texto: str | None = None) -> list[Nino]:
        resultado = []
        for nino in self._ninos.values():
            if estado and nino.estado != estado:
                continue
            if texto:
                t = texto.lower()
                campos = (
                    f"{nino.nombres or ''} {nino.apellidos or ''}",
                    nino.dni or "",
                    nino.codigo_origen or "",
                    nino.comunidad,
                )
                if not any(t in campo.lower() for campo in campos):
                    continue
            resultado.append(copy.deepcopy(nino))
        return resultado

    def evaluaciones_en_periodo(self, desde: date, hasta: date) -> list[Evaluacion]:
        return [copy.deepcopy(e) for n in self._ninos.values() for e in n.evaluaciones if desde <= e.fecha <= hasta]

    def contar_registrados_en_periodo(self, desde: date, hasta: date) -> int:
        return sum(1 for n in self._ninos.values() if desde <= fecha_local(n.creado_en) <= hasta)

    def obtener_varios(self, ids: set[str]) -> dict[str, Nino]:
        return {i: copy.deepcopy(self._ninos[i]) for i in ids if i in self._ninos}
