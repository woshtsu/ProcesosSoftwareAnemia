"""Adaptador en memoria: implementa el puerto para pruebas unitarias del núcleo."""

import copy
from datetime import date

from app.domain.model.asistencia import AsistenciaControl
from app.domain.model.barrera import Barrera
from app.domain.model.entidades import Evaluacion, Nino
from app.domain.model.errores import ConflictoAsistencia, ConflictoBarrera, ConflictoRecordatorio, ConflictoVisita
from app.domain.model.notificacion import CanalEnvio, EstadoRecordatorio, Recordatorio
from app.domain.model.sincronizacion import (
    ConflictoSincronizacion,
    OperacionSincronizada,
    ResultadoOperacion,
)
from app.domain.model.tiempo import fecha_local
from app.domain.model.visita import VisitaDomiciliaria
from app.ports.outbound.repositorio_barreras import RepositorioBarreras
from app.ports.outbound.repositorio_ninos import RepositorioNinos
from app.ports.outbound.repositorio_recordatorios import RepositorioRecordatorios
from app.ports.outbound.repositorio_sincronizacion import RepositorioSincronizacion
from app.ports.outbound.repositorio_visitas import RepositorioVisitas


class RepositorioEnMemoria(
    RepositorioNinos, RepositorioVisitas, RepositorioSincronizacion, RepositorioRecordatorios, RepositorioBarreras
):
    def __init__(self) -> None:
        self._ninos: dict[str, Nino] = {}
        self._visitas: dict[str, VisitaDomiciliaria] = {}
        self._operaciones: dict[str, OperacionSincronizada] = {}
        self._conflictos: dict[str, ConflictoSincronizacion] = {}
        self._recordatorios: dict[str, Recordatorio] = {}
        self._barreras: dict[str, Barrera] = {}

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
        self._barreras = {k: b for k, b in self._barreras.items() if b.nino_id not in ids}
        self._recordatorios = {k: r for k, r in self._recordatorios.items() if r.nino_id not in ids}
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

    def actualizar_evaluacion(self, evaluacion: Evaluacion) -> Evaluacion:
        existentes = self._ninos[evaluacion.nino_id].evaluaciones
        existentes[:] = [copy.deepcopy(evaluacion) if e.id == evaluacion.id else e for e in existentes]
        return evaluacion

    def actualizar_asistencia(self, asistencia: AsistenciaControl) -> AsistenciaControl:
        existentes = self._ninos[asistencia.nino_id].asistencias
        existentes[:] = [copy.deepcopy(asistencia) if a.id == asistencia.id else a for a in existentes]
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

    # --- Visitas domiciliarias -----------------------------------------------------------------------------------
    def agregar_visita(self, visita: VisitaDomiciliaria) -> VisitaDomiciliaria:
        if self.obtener_visita_del_dia(visita.nino_id, visita.fecha):
            raise ConflictoVisita(f"El niño ya tiene una visita registrada el {visita.fecha.isoformat()}.")
        self._visitas[visita.id] = copy.deepcopy(visita)
        return visita

    def actualizar_visita(self, visita: VisitaDomiciliaria) -> VisitaDomiciliaria:
        self._visitas[visita.id] = copy.deepcopy(visita)
        return visita

    def obtener_visita_del_dia(self, nino_id: str, fecha: date) -> VisitaDomiciliaria | None:
        for v in self._visitas.values():
            if v.nino_id == nino_id and v.fecha == fecha:
                return copy.deepcopy(v)
        return None

    def listar_visitas(self, nino_id: str) -> list[VisitaDomiciliaria]:
        propias = [copy.deepcopy(v) for v in self._visitas.values() if v.nino_id == nino_id]
        return sorted(propias, key=lambda v: (-v.fecha.toordinal(), v.creado_en))

    def ultimas_visitas(self, nino_ids: set[str]) -> dict[str, date]:
        ultimas: dict[str, date] = {}
        for v in self._visitas.values():
            if v.nino_id in nino_ids and v.fecha > ultimas.get(v.nino_id, date.min):
                ultimas[v.nino_id] = v.fecha
        return ultimas

    # --- Sincronización --------------------------------------------------------------------------------------------
    def obtener_operacion(self, id_operacion: str) -> OperacionSincronizada | None:
        return copy.deepcopy(self._operaciones.get(id_operacion))

    def registrar_operacion(self, operacion: OperacionSincronizada) -> bool:
        if operacion.id_operacion in self._operaciones:
            return False
        self._operaciones[operacion.id_operacion] = copy.deepcopy(operacion)
        return True

    def marcar_operacion_resuelta(self, id_operacion: str) -> None:
        self._operaciones[id_operacion].resultado = ResultadoOperacion.RESUELTA

    def id_nino_de_cliente(self, id_dispositivo: str, id_cliente: str) -> str | None:
        mapean = (ResultadoOperacion.APLICADA, ResultadoOperacion.DUPLICADA, ResultadoOperacion.RESUELTA)
        for o in self._operaciones.values():
            if o.id_dispositivo == id_dispositivo and o.id_cliente == id_cliente and o.resultado in mapean:
                return o.id_recurso
        return None

    def contar_operaciones(self) -> int:
        return len(self._operaciones)

    def guardar_conflicto(self, conflicto: ConflictoSincronizacion) -> ConflictoSincronizacion:
        self._conflictos[conflicto.id] = copy.deepcopy(conflicto)
        return conflicto

    def obtener_conflicto(self, conflicto_id: str) -> ConflictoSincronizacion | None:
        return copy.deepcopy(self._conflictos.get(conflicto_id))

    def obtener_conflicto_de_operacion(self, id_operacion: str) -> ConflictoSincronizacion | None:
        for c in self._conflictos.values():
            if c.id_operacion == id_operacion:
                return copy.deepcopy(c)
        return None

    def listar_conflictos(self, estado: str | None = None) -> list[ConflictoSincronizacion]:
        elegidos = [c for c in self._conflictos.values() if not estado or c.estado == estado]
        return [copy.deepcopy(c) for c in sorted(elegidos, key=lambda c: (c.creado_en, c.id))]

    def actualizar_conflicto(self, conflicto: ConflictoSincronizacion) -> ConflictoSincronizacion:
        self._conflictos[conflicto.id] = copy.deepcopy(conflicto)
        return conflicto

    # --- Recordatorios ---------------------------------------------------------------------------------------------
    def agregar_recordatorio(self, recordatorio: Recordatorio) -> Recordatorio:
        if any(r.clave == recordatorio.clave for r in self._recordatorios.values()):
            raise ConflictoRecordatorio("Ya existe un recordatorio para ese control y tipo.")
        self._recordatorios[recordatorio.id] = copy.deepcopy(recordatorio)
        return recordatorio

    def actualizar_recordatorio(self, recordatorio: Recordatorio) -> Recordatorio:
        self._recordatorios[recordatorio.id] = copy.deepcopy(recordatorio)
        return recordatorio

    def obtener_recordatorio(self, recordatorio_id: str) -> Recordatorio | None:
        return copy.deepcopy(self._recordatorios.get(recordatorio_id))

    def obtener_por_id_externo(self, id_externo: str) -> Recordatorio | None:
        for r in self._recordatorios.values():
            if r.id_externo == id_externo:
                return copy.deepcopy(r)
        return None

    def buscar_para_respuesta(self, id_externo: str | None, destino: str | None) -> Recordatorio | None:
        if id_externo and (r := self.obtener_por_id_externo(id_externo)):
            return r
        if not destino:
            return None
        candidatos = [
            r
            for r in self._recordatorios.values()
            if r.destino == destino
            and r.canal == CanalEnvio.WHATSAPP
            and r.respuesta is None
            and r.estado != EstadoRecordatorio.FALLIDO
        ]
        return copy.deepcopy(max(candidatos, key=lambda r: r.creado_en)) if candidatos else None

    def listar_recordatorios(
        self,
        estado: str | None = None,
        desde: date | None = None,
        hasta: date | None = None,
        nino_id: str | None = None,
        limite: int | None = None,
    ) -> list[Recordatorio]:
        elegidos = [
            r
            for r in self._recordatorios.values()
            if (not estado or r.estado == estado)
            and (not nino_id or r.nino_id == nino_id)
            and (not desde or fecha_local(r.creado_en) >= desde)
            and (not hasta or fecha_local(r.creado_en) <= hasta)
        ]
        elegidos.sort(key=lambda r: r.creado_en, reverse=True)
        return [copy.deepcopy(r) for r in (elegidos[:limite] if limite else elegidos)]

    # --- Barreras --------------------------------------------------------------------------------------------------
    def agregar_barrera(self, barrera: Barrera) -> Barrera:
        previa = self.obtener_equivalente(barrera.nino_id, barrera.tipo, barrera.fecha, barrera.fuente)
        if previa:
            raise ConflictoBarrera("El niño ya tiene registrada esa barrera.", previa.id)
        self._barreras[barrera.id] = copy.deepcopy(barrera)
        return barrera

    def obtener_equivalente(self, nino_id: str, tipo: str, fecha: date, fuente: str) -> Barrera | None:
        for b in self._barreras.values():
            if (b.nino_id, b.tipo, b.fecha, b.fuente) == (nino_id, tipo, fecha, fuente):
                return copy.deepcopy(b)
        return None

    def listar_barreras(self, nino_id: str) -> list[Barrera]:
        propias = [copy.deepcopy(b) for b in self._barreras.values() if b.nino_id == nino_id]
        return sorted(propias, key=lambda b: (b.fecha, b.creado_en), reverse=True)

    def barreras_desde(self, desde: date) -> dict[str, list[Barrera]]:
        agrupadas: dict[str, list[Barrera]] = {}
        for b in self._barreras.values():
            if b.fecha >= desde:
                agrupadas.setdefault(b.nino_id, []).append(copy.deepcopy(b))
        return agrupadas
