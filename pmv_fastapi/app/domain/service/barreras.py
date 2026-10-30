"""Barreras de acceso y alerta de barreras críticas (HIST-4.3 y HIST-4.4, ADR-014). Servicio de dominio puro.

Registro de una barrera:
  * Tipos del catálogo (``TipoBarrera``); con ``OTRA`` el detalle es obligatorio. El detalle no supera 200 caracteres.
  * La fuente es PERSONAL, RESPUESTA_RECORDATORIO, INASISTENCIA o VISITA (por defecto PERSONAL).
  * La fecha no puede ser futura ni anterior al nacimiento (por defecto, hoy).
  * Un niño no repite la misma barrera (tipo, fecha y fuente).

Una barrera es crítica (reglas parametrizadas y versionadas en ``REGLAS_BARRERAS_V1``, propuesta del equipo que debe
confirmar la microred, igual que las reglas clínicas, ADR-004). Un niño activo entra en la alerta si cumple alguna:
  1. BARRERA_GRAVE: tiene una barrera vigente de tipo RECHAZO_TRATAMIENTO o EFECTOS_ADVERSOS_SUPLEMENTO.
  2. BARRERAS_RECURRENTES: tiene dos o más barreras distintas (tipo y fecha) en los últimos 60 días.
  3. ANEMIA_CONTROL_VENCIDO: tiene cualquier barrera vigente, su última evaluación es MODERADA o SEVERA y su agenda
     tiene un control vencido.
«Vigente» es una barrera de los últimos 90 días: sin esa vigencia (decisión del equipo; la especificación no la fija)
una barrera antigua alertaría para siempre. Prioridad: ALTA si cumple la regla 1 o dos o más reglas; MEDIA en el resto.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta

from app.domain.model.agenda import AgendaNino, EstadoControl
from app.domain.model.alertas import Prioridad
from app.domain.model.barrera import (
    AlertaBarrera,
    Barrera,
    CodigoRazonBarrera,
    FuenteBarrera,
    RazonAlertaBarrera,
    TipoBarrera,
)
from app.domain.model.clasificacion import Clasificacion
from app.domain.model.entidades import Nino
from app.domain.model.errores import ErrorCampo

DETALLE_MAX = 200
DETALLE_MIN_OTRA = 3
_ORDEN_PRIORIDAD = {Prioridad.ALTA: 0, Prioridad.MEDIA: 1}


@dataclass(frozen=True)
class ReglasBarrerasCriticas:
    """Parámetros de la alerta de barreras críticas (versionados)."""

    version: str
    tipos_graves: frozenset[TipoBarrera] = field(default_factory=frozenset)
    minimo_recurrentes: int = 2
    dias_ventana_recurrentes: int = 60
    dias_vigencia: int = 90
    clasificaciones_con_vencido: frozenset[Clasificacion] = field(default_factory=frozenset)

    @property
    def dias_consulta(self) -> int:
        """Antigüedad máxima de las barreras que intervienen en la regla."""
        return max(self.dias_vigencia, self.dias_ventana_recurrentes)


REGLAS_BARRERAS_V1 = ReglasBarrerasCriticas(
    version="BARRERAS-V1",
    tipos_graves=frozenset({TipoBarrera.RECHAZO_TRATAMIENTO, TipoBarrera.EFECTOS_ADVERSOS_SUPLEMENTO}),
    clasificaciones_con_vencido=frozenset({Clasificacion.MODERADA, Clasificacion.SEVERA}),
)

_DESCRIPCION = {
    CodigoRazonBarrera.BARRERA_GRAVE: "Rechazo del tratamiento o efectos adversos del suplemento",
    CodigoRazonBarrera.BARRERAS_RECURRENTES: "Dos o más barreras distintas en los últimos {dias} días",
    CodigoRazonBarrera.ANEMIA_CONTROL_VENCIDO: "Barrera con anemia {clasificacion} y un control vencido",
}


def validar_datos_barrera(datos: dict, fecha_nacimiento: date, hoy: date) -> list[ErrorCampo]:
    errores: list[ErrorCampo] = []
    tipo = datos.get("tipo")
    if tipo not in {t.value for t in TipoBarrera}:
        errores.append(ErrorCampo("tipo", "Seleccione una barrera del catálogo."))
    fuente = datos.get("fuente") or FuenteBarrera.PERSONAL.value
    if fuente not in {f.value for f in FuenteBarrera}:
        errores.append(
            ErrorCampo("fuente", "La fuente debe ser PERSONAL, RESPUESTA_RECORDATORIO, INASISTENCIA o VISITA.")
        )
    detalle = datos.get("detalle")
    if detalle is not None and not isinstance(detalle, str):
        errores.append(ErrorCampo("detalle", "Debe ser texto."))
    else:
        texto = (detalle or "").strip()
        if len(texto) > DETALLE_MAX:
            errores.append(ErrorCampo("detalle", f"No puede superar {DETALLE_MAX} caracteres."))
        elif tipo == TipoBarrera.OTRA and len(texto) < DETALLE_MIN_OTRA:
            errores.append(ErrorCampo("detalle", "Describa la barrera: con «Otra» el detalle es obligatorio."))
    fecha = datos.get("fecha") or hoy
    if not isinstance(fecha, date):
        errores.append(ErrorCampo("fecha", "Fecha inválida."))
    elif fecha > hoy:
        errores.append(ErrorCampo("fecha", "La fecha de la barrera no puede ser futura."))
    elif fecha < fecha_nacimiento:
        errores.append(ErrorCampo("fecha", "La barrera no puede ser anterior al nacimiento."))
    return errores


def crear_barrera(nino_id: str, datos: dict, usuario: str, hoy: date) -> Barrera:
    """Barrera de dominio a partir de datos ya validados."""
    return Barrera(
        nino_id=nino_id,
        tipo=TipoBarrera(datos["tipo"]),
        fuente=FuenteBarrera(datos.get("fuente") or FuenteBarrera.PERSONAL),
        fecha=datos.get("fecha") or hoy,
        detalle=(datos.get("detalle") or "").strip() or None,
        recordatorio_id=datos.get("recordatorio_id") or None,
        registrado_por=usuario,
    )


def _dias_desde(barrera: Barrera, hoy: date) -> int:
    return (hoy - barrera.fecha).days


def _razones(
    nino: Nino, agenda: AgendaNino, barreras: list[Barrera], hoy: date, reglas: ReglasBarrerasCriticas
) -> list[RazonAlertaBarrera]:
    vigentes = [b for b in barreras if _dias_desde(b, hoy) <= reglas.dias_vigencia]
    razones: list[RazonAlertaBarrera] = []
    if any(b.tipo in reglas.tipos_graves for b in vigentes):
        razones.append(
            RazonAlertaBarrera(CodigoRazonBarrera.BARRERA_GRAVE, _DESCRIPCION[CodigoRazonBarrera.BARRERA_GRAVE])
        )
    recientes = {(b.tipo, b.fecha) for b in barreras if _dias_desde(b, hoy) <= reglas.dias_ventana_recurrentes}
    if len(recientes) >= reglas.minimo_recurrentes:
        texto = _DESCRIPCION[CodigoRazonBarrera.BARRERAS_RECURRENTES].format(dias=reglas.dias_ventana_recurrentes)
        razones.append(RazonAlertaBarrera(CodigoRazonBarrera.BARRERAS_RECURRENTES, texto))
    ultima = nino.ultima_evaluacion
    tiene_vencido = any(c.estado == EstadoControl.VENCIDO for c in agenda.controles)
    if vigentes and tiene_vencido and ultima and ultima.clasificacion in reglas.clasificaciones_con_vencido:
        texto = _DESCRIPCION[CodigoRazonBarrera.ANEMIA_CONTROL_VENCIDO].format(
            clasificacion=ultima.clasificacion.value.lower()
        )
        razones.append(RazonAlertaBarrera(CodigoRazonBarrera.ANEMIA_CONTROL_VENCIDO, texto))
    return razones


def evaluar_barreras_nino(
    nino: Nino,
    agenda: AgendaNino,
    barreras: list[Barrera],
    hoy: date,
    reglas: ReglasBarrerasCriticas = REGLAS_BARRERAS_V1,
) -> AlertaBarrera | None:
    """Alerta del niño si sus barreras son críticas; ``None`` si no lo son o si el niño tiene alta (no hay agenda)."""
    if not agenda.aplica:
        return None
    razones = _razones(nino, agenda, barreras, hoy, reglas)
    if not razones:
        return None
    graves = any(r.codigo == CodigoRazonBarrera.BARRERA_GRAVE for r in razones)
    atrasos = [c.dias_vencido or 0 for c in agenda.controles if c.estado == EstadoControl.VENCIDO]
    ultima = nino.ultima_evaluacion
    sustento = sorted(
        (b for b in barreras if _dias_desde(b, hoy) <= reglas.dias_consulta),
        key=lambda b: (b.fecha, b.creado_en),
        reverse=True,
    )
    return AlertaBarrera(
        nino_id=nino.id,
        dni=nino.dni,
        codigo_origen=nino.codigo_origen,
        nombre_completo=nino.nombre_completo,
        comunidad=nino.comunidad,
        establecimiento=nino.establecimiento,
        tutor_celular=nino.tutor_celular,
        ultima_clasificacion=ultima.clasificacion if ultima else None,
        dias_control_vencido=max(atrasos, default=0),
        prioridad=Prioridad.ALTA if graves or len(razones) >= 2 else Prioridad.MEDIA,
        razones=tuple(razones),
        barreras=tuple(sustento),
    )


def ordenar_alertas_barrera(alertas: list[AlertaBarrera]) -> list[AlertaBarrera]:
    """Prioridad, más razones, más días de control vencido y barrera más reciente primero; luego nombre e id."""
    return sorted(
        alertas,
        key=lambda a: (
            _ORDEN_PRIORIDAD[a.prioridad],
            -len(a.razones),
            -a.dias_control_vencido,
            -max(b.fecha for b in a.barreras).toordinal(),
            a.nombre_completo,
            a.nino_id,
        ),
    )


def fecha_limite_consulta(hoy: date, reglas: ReglasBarrerasCriticas = REGLAS_BARRERAS_V1) -> date:
    """Fecha desde la cual se consultan las barreras que intervienen en la alerta."""
    return hoy - timedelta(days=reglas.dias_consulta)
