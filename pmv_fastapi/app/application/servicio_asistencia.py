"""Caso de uso HIST-2.4: registrar la asistencia (o inasistencia) a un control programado (ADR-010)."""

from app.domain.model.asistencia import AsistenciaControl, EstadoAsistencia
from app.domain.model.errores import NoEncontrado
from app.domain.service.agenda import generar_agenda
from app.domain.service.asistencia import localizar_control_registrable, validar_datos_asistencia
from app.domain.service.validaciones import exigir
from app.ports.inbound.asistencia import RegistrarAsistencia
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_ninos import RepositorioNinos


class ServicioAsistencia(RegistrarAsistencia):
    def __init__(self, repo: RepositorioNinos, reloj: Reloj):
        self.repo = repo
        self.reloj = reloj

    def _nino(self, nino_id: str):
        nino = self.repo.obtener(nino_id)
        if not nino:
            raise NoEncontrado("No existe el expediente solicitado.")
        return nino

    def registrar_asistencia(self, nino_id: str, codigo: str, datos: dict, usuario: str) -> AsistenciaControl:
        nino = self._nino(nino_id)
        hoy = self.reloj.hoy()
        exigir(validar_datos_asistencia(datos, hoy))
        agenda = generar_agenda(nino, hoy)
        control = localizar_control_registrable(nino, agenda, {**datos, "codigo": codigo})
        estado = EstadoAsistencia(datos["estado"])
        motivo = (datos.get("motivo") or "").strip() or None
        asistencia = AsistenciaControl(
            nino_id=nino.id,
            codigo_control=control.codigo,
            fecha_programada=control.fecha_programada,
            estado=estado,
            motivo=motivo,
            evaluacion_id=datos.get("evaluacion_id") or None,
            registrado_por=usuario,
        )
        return self.repo.agregar_asistencia(asistencia)

    def listar_asistencias(self, nino_id: str) -> list[AsistenciaControl]:
        nino = self._nino(nino_id)
        return sorted(nino.asistencias, key=lambda a: (a.fecha_programada, a.creado_en))
