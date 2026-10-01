"""Adaptador en memoria: implementa el puerto para pruebas unitarias del núcleo."""

import copy
from datetime import date

from app.domain.entidades import Evaluacion, Nino


class RepositorioEnMemoria:
    def __init__(self) -> None:
        self._ninos: dict[str, Nino] = {}

    def guardar(self, nino: Nino) -> Nino:
        self._ninos[nino.id] = copy.deepcopy(nino)
        return nino

    def actualizar(self, nino: Nino) -> Nino:
        evaluaciones = self._ninos[nino.id].evaluaciones
        self._ninos[nino.id] = copy.deepcopy(nino)
        self._ninos[nino.id].evaluaciones = evaluaciones
        return nino

    def agregar_evaluacion(self, evaluacion: Evaluacion) -> Evaluacion:
        self._ninos[evaluacion.nino_id].evaluaciones.append(copy.deepcopy(evaluacion))
        return evaluacion

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
                if t not in nino.nombre_completo.lower() and t not in nino.dni and t not in nino.comunidad.lower():
                    continue
            resultado.append(copy.deepcopy(nino))
        return resultado

    def evaluaciones_en_periodo(self, desde: date, hasta: date) -> list[Evaluacion]:
        return [copy.deepcopy(e) for n in self._ninos.values() for e in n.evaluaciones if desde <= e.fecha <= hasta]

    def ninos_registrados_en_periodo(self, desde: date, hasta: date) -> list[Nino]:
        return [copy.deepcopy(n) for n in self._ninos.values() if desde <= n.creado_en.date() <= hasta]
