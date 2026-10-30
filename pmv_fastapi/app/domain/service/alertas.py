"""Prioridad y resumen de las alertas internas de controles vencidos (HIST-2.2).

Prioridad (referencial, la confirma la microred):
  * ALTA: control de tratamiento vencido, o última clasificación MODERADA/SEVERA, o más de 30 días de atraso.
  * MEDIA: de 8 a 30 días de atraso.
  * BAJA: hasta 7 días de atraso.
Los días de atraso se cuentan desde la fecha límite del control (fin de su ventana de tolerancia).
Si el personal registró una inasistencia para el control (HIST-2.4), la prioridad sube un nivel (BAJA a MEDIA, MEDIA a
ALTA; ALTA se mantiene): la familia ya fue citada y no vino.
"""

from app.domain.model.agenda import AgendaNino, ControlProgramado, EstadoControl, TipoControl
from app.domain.model.alertas import AlertaControl, Prioridad, ResumenAlertas
from app.domain.model.clasificacion import Clasificacion
from app.domain.model.entidades import Nino

DIAS_ATRASO_ALTA = 30  # más de 30 días: prioridad ALTA
DIAS_ATRASO_BAJA = 7  # hasta 7 días: prioridad BAJA
_ORDEN = {Prioridad.ALTA: 0, Prioridad.MEDIA: 1, Prioridad.BAJA: 2}
_SUBE_UN_NIVEL = {Prioridad.BAJA: Prioridad.MEDIA, Prioridad.MEDIA: Prioridad.ALTA, Prioridad.ALTA: Prioridad.ALTA}


def calcular_prioridad(control: ControlProgramado, ultima: Clasificacion | None) -> Prioridad:
    dias = control.dias_vencido or 0
    if (
        control.tipo == TipoControl.CONTROL_TRATAMIENTO
        or ultima in (Clasificacion.MODERADA, Clasificacion.SEVERA)
        or dias > DIAS_ATRASO_ALTA
    ):
        prioridad = Prioridad.ALTA
    else:
        prioridad = Prioridad.BAJA if dias <= DIAS_ATRASO_BAJA else Prioridad.MEDIA
    return _SUBE_UN_NIVEL[prioridad] if control.inasistencia_registrada else prioridad


def alertas_de_nino(nino: Nino, agenda: AgendaNino) -> list[AlertaControl]:
    """Una alerta por cada control VENCIDO de la agenda del niño."""
    ultima = nino.ultima_evaluacion.clasificacion if nino.ultima_evaluacion else None
    return [
        AlertaControl(
            nino_id=nino.id,
            dni=nino.dni,
            codigo_origen=nino.codigo_origen,
            nombre_completo=nino.nombre_completo,
            comunidad=nino.comunidad,
            tutor_celular=nino.tutor_celular,
            control=c,
            ultima_clasificacion=ultima,
            prioridad=calcular_prioridad(c, ultima),
        )
        for c in agenda.controles
        if c.estado == EstadoControl.VENCIDO
    ]


def ordenar_alertas(alertas: list[AlertaControl]) -> list[AlertaControl]:
    """Prioridad, luego mayor atraso primero; el resto del orden solo garantiza resultados repetibles."""
    return sorted(
        alertas,
        key=lambda a: (
            _ORDEN[a.prioridad],
            -(a.control.dias_vencido or 0),
            a.nombre_completo,
            a.control.fecha_programada,
        ),
    )


def resumir_alertas(alertas: list[AlertaControl], proximos_7_dias: int) -> ResumenAlertas:
    return ResumenAlertas(
        total_vencidos=len(alertas),
        por_prioridad={p.value: sum(1 for a in alertas if a.prioridad == p) for p in Prioridad},
        ninos_con_vencidos=len({a.nino_id for a in alertas}),
        proximos_7_dias=proximos_7_dias,
    )
