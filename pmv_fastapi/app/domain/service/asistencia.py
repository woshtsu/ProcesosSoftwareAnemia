"""Reglas del registro de asistencia a un control (HIST-2.4, ADR-010). Servicio de dominio puro.

Un control se identifica por (código, fecha programada) dentro de la agenda del niño. Reglas:
  * El estado es ASISTIO o NO_ASISTIO; la inasistencia exige un motivo (3 a 200 caracteres).
  * No se registra la asistencia de un control con fecha programada futura.
  * El control debe existir en la agenda del niño (404) y no tener ya una asistencia registrada (409).
  * Un control ya CUMPLIDO o CERRADO_RECUPERADO no admite asistencia (409): ya no hay nada que registrar.
  * La evaluación vinculada (opcional, solo con ASISTIO) debe pertenecer al niño y no cumplir ya otro control.
"""

from datetime import date

from app.domain.model.agenda import AgendaNino, ControlProgramado, EstadoControl
from app.domain.model.asistencia import EstadoAsistencia
from app.domain.model.entidades import Nino
from app.domain.model.errores import ConflictoAsistencia, ErrorCampo, ErrorValidacion, NoEncontrado

MOTIVO_MIN = 3
MOTIVO_MAX = 200


def validar_datos_asistencia(datos: dict, hoy: date) -> list[ErrorCampo]:
    errores: list[ErrorCampo] = []
    estado = datos.get("estado")
    if estado not in {e.value for e in EstadoAsistencia}:
        errores.append(ErrorCampo("estado", "El estado debe ser ASISTIO o NO_ASISTIO."))
    programada = datos.get("fecha_programada")
    if not isinstance(programada, date):
        errores.append(ErrorCampo("fecha_programada", "Fecha programada inválida."))
    elif programada > hoy:
        errores.append(
            ErrorCampo("fecha_programada", "No se puede registrar la asistencia a un control con fecha futura.")
        )
    motivo = (datos.get("motivo") or "").strip()
    if len(motivo) > MOTIVO_MAX:
        errores.append(ErrorCampo("motivo", f"No puede superar {MOTIVO_MAX} caracteres."))
    elif estado == EstadoAsistencia.NO_ASISTIO and len(motivo) < MOTIVO_MIN:
        errores.append(ErrorCampo("motivo", "Indique el motivo de la inasistencia."))
    if datos.get("evaluacion_id") and estado == EstadoAsistencia.NO_ASISTIO:
        errores.append(ErrorCampo("evaluacion_id", "Solo se vincula una evaluación cuando el niño asistió."))
    return errores


def localizar_control_registrable(nino: Nino, agenda: AgendaNino, datos: dict) -> ControlProgramado:
    """Control de la agenda sobre el que se registrará la asistencia; lanza el error de dominio que corresponda."""
    codigo, programada = datos["codigo"], datos["fecha_programada"]
    control = next((c for c in agenda.controles if c.codigo == codigo and c.fecha_programada == programada), None)
    if control is None:
        raise NoEncontrado(f"El niño no tiene programado el control {codigo} con fecha {programada.isoformat()}.")
    if any(a.codigo_control == codigo and a.fecha_programada == programada for a in nino.asistencias):
        raise ConflictoAsistencia(
            f"El control {codigo} del {programada.isoformat()} ya tiene una asistencia registrada."
        )
    if control.estado == EstadoControl.CUMPLIDO:
        raise ConflictoAsistencia(f"El control {codigo} del {programada.isoformat()} ya está cumplido.")
    if control.estado == EstadoControl.CERRADO_RECUPERADO:
        raise ConflictoAsistencia(f"El control {codigo} del {programada.isoformat()} fue cerrado por recuperación.")
    evaluacion_id = datos.get("evaluacion_id")
    if evaluacion_id:
        if evaluacion_id not in {e.id for e in nino.evaluaciones}:
            raise ErrorValidacion([ErrorCampo("evaluacion_id", "La evaluación no pertenece al expediente del niño.")])
        if any(c.evaluacion_id == evaluacion_id for c in agenda.controles):
            raise ErrorValidacion([ErrorCampo("evaluacion_id", "Esa evaluación ya cumple otro control de la agenda.")])
    return control
