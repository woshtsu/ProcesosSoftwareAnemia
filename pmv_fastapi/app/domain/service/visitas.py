"""Visita domiciliaria priorizada (VIS-3.5, brecha B4, ADR-013). Servicio de dominio puro.

Reglas de la visita:
  * La fecha no puede ser futura ni anterior al nacimiento; hay a lo sumo una visita por niño y por día.
  * El resultado es REALIZADA, NO_ENCONTRADO o RECHAZADA.
  * El consumo del suplemento es SI, NO o DESCONOCIDO (valor por defecto); solo una visita REALIZADA puede decir
    SI o NO, pues si no hubo encuentro con la familia no se pudo preguntar.
  * Las observaciones son opcionales y no superan 500 caracteres.

Puntaje de prioridad (propuesta del equipo, NO es una norma del MINSA; los pesos están en ``PESOS_V1`` y deben
validarse con la microred). Es determinista y la suma de sus cuatro componentes va de 0 a 100:
  * SEVERIDAD de la última evaluación: SEVERA 40, MODERADA 25, LEVE 10.
  * CONTROL_VENCIDO: hasta 30 puntos, proporcionales a los días de atraso del control más vencido de la agenda
    (tope de 60 días).
  * INASISTENCIAS registradas (RF-09) cuya fecha programada cae en los últimos 90 días: 5 puntos cada una, hasta 15.
  * ULTIMA_VISITA: hasta 15 puntos, proporcionales a los días desde la última visita (tope de 90 días); un niño sin
    ninguna visita recibe el máximo.
Desde la versión 4.0 (VISITA-V2, ADR-013) se suma un quinto componente solo a los niños con barreras críticas
(HIST-4.4, ``domain/service/barreras.py``):
  * BARRERA_CRITICA: 15 puntos si su alerta de barreras es de prioridad ALTA y 8 si es MEDIA. Un niño sin barreras
    críticas no lleva este componente, de modo que su puntaje no cambia (sigue de 0 a 100) y el máximo con barreras
    es 115.
Solo se priorizan los niños en tratamiento: activos cuya última evaluación tiene anemia.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta

from app.domain.model.agenda import AgendaNino, EstadoControl
from app.domain.model.alertas import Prioridad
from app.domain.model.asistencia import EstadoAsistencia
from app.domain.model.barrera import AlertaBarrera
from app.domain.model.clasificacion import Clasificacion
from app.domain.model.entidades import Nino
from app.domain.model.errores import ErrorCampo
from app.domain.model.visita import (
    LIMITE_MAXIMO,
    ComponentePuntaje,
    ConsumoSuplemento,
    NinoPriorizado,
    ResultadoVisita,
    VisitaDomiciliaria,
)

OBSERVACIONES_MAX = 500


@dataclass(frozen=True)
class PesosPrioridadVisita:
    """Pesos del puntaje de prioridad (versionados, como las reglas clínicas y el esquema de la agenda)."""

    version: str
    por_severidad: dict[Clasificacion, float] = field(default_factory=dict)
    maximo_control_vencido: float = 30.0
    dias_tope_control_vencido: int = 60
    puntos_por_inasistencia: float = 5.0
    maximo_inasistencias: float = 15.0
    dias_ventana_inasistencias: int = 90
    maximo_ultima_visita: float = 15.0
    dias_tope_ultima_visita: int = 90
    puntos_barrera_critica: dict[Prioridad, float] = field(default_factory=dict)  # por prioridad de la alerta (V2)


PESOS_V1 = PesosPrioridadVisita(
    version="VISITA-V1",
    por_severidad={Clasificacion.SEVERA: 40.0, Clasificacion.MODERADA: 25.0, Clasificacion.LEVE: 10.0},
)

# V2 (INC-4): mismos pesos que V1 más el componente de barreras críticas. Propuesta del equipo, no norma del MINSA.
PESOS_V2 = PesosPrioridadVisita(
    version="VISITA-V2",
    por_severidad=PESOS_V1.por_severidad,
    puntos_barrera_critica={Prioridad.ALTA: 15.0, Prioridad.MEDIA: 8.0},
)


def _enum_valido(valor, enum) -> bool:
    return isinstance(valor, str) and valor in {e.value for e in enum}


def validar_datos_visita(datos: dict, fecha_nacimiento: date, hoy: date) -> list[ErrorCampo]:
    errores: list[ErrorCampo] = []
    fecha = datos.get("fecha")
    if not isinstance(fecha, date):
        errores.append(ErrorCampo("fecha", "Fecha de visita inválida."))
    elif fecha > hoy:
        errores.append(ErrorCampo("fecha", "La fecha de la visita no puede ser futura."))
    elif fecha < fecha_nacimiento:
        errores.append(ErrorCampo("fecha", "La visita no puede ser anterior al nacimiento."))
    resultado = datos.get("resultado")
    resultado_valido = _enum_valido(resultado, ResultadoVisita)
    if not resultado_valido:
        errores.append(ErrorCampo("resultado", "El resultado debe ser REALIZADA, NO_ENCONTRADO o RECHAZADA."))
    consumo = datos.get("consume_suplemento") or ConsumoSuplemento.DESCONOCIDO.value
    if not _enum_valido(consumo, ConsumoSuplemento):
        errores.append(ErrorCampo("consume_suplemento", "Indique SI, NO o DESCONOCIDO."))
    elif consumo != ConsumoSuplemento.DESCONOCIDO and resultado_valido and resultado != ResultadoVisita.REALIZADA:
        errores.append(
            ErrorCampo(
                "consume_suplemento", "Solo una visita realizada puede indicar si el niño consume el suplemento."
            )
        )
    observaciones = datos.get("observaciones")
    if observaciones is not None and not isinstance(observaciones, str):
        errores.append(ErrorCampo("observaciones", "Debe ser texto."))
    elif observaciones and len(observaciones.strip()) > OBSERVACIONES_MAX:
        errores.append(ErrorCampo("observaciones", f"No puede superar {OBSERVACIONES_MAX} caracteres."))
    return errores


def crear_visita(nino_id: str, datos: dict, usuario: str) -> VisitaDomiciliaria:
    """Visita de dominio a partir de datos ya validados."""
    return VisitaDomiciliaria(
        nino_id=nino_id,
        fecha=datos["fecha"],
        resultado=ResultadoVisita(datos["resultado"]),
        consume_suplemento=ConsumoSuplemento(datos.get("consume_suplemento") or ConsumoSuplemento.DESCONOCIDO),
        observaciones=(datos.get("observaciones") or "").strip() or None,
        registrado_por=usuario,
    )


def validar_limite(limite: int) -> list[ErrorCampo]:
    if not (1 <= limite <= LIMITE_MAXIMO):
        return [ErrorCampo("limite", f"El límite debe estar entre 1 y {LIMITE_MAXIMO}.")]
    return []


def en_tratamiento(nino: Nino) -> bool:
    """Niño activo cuya última evaluación tiene anemia (LEVE, MODERADA o SEVERA)."""
    ultima = nino.ultima_evaluacion
    return nino.estado == "ACTIVO" and ultima is not None and ultima.tiene_anemia


def _proporcional(valor: int, tope: int, maximo: float) -> float:
    return round(min(valor, tope) / tope * maximo, 1)


def priorizar_nino(
    nino: Nino,
    agenda: AgendaNino,
    ultima_visita: date | None,
    hoy: date,
    pesos: PesosPrioridadVisita = PESOS_V2,
    alerta_barrera: AlertaBarrera | None = None,
) -> NinoPriorizado:
    """Puntaje y componentes de un niño en tratamiento (quien llama filtra antes con ``en_tratamiento``).

    ``alerta_barrera`` es la alerta de barreras críticas del niño, si la tiene (HIST-4.4): suma el componente
    BARRERA_CRITICA."""
    clasificacion = nino.ultima_evaluacion.clasificacion
    atrasos = [c.dias_vencido or 0 for c in agenda.controles if c.estado == EstadoControl.VENCIDO]
    dias_vencido = max(atrasos, default=0)
    desde = hoy - timedelta(days=pesos.dias_ventana_inasistencias)
    inasistencias = sum(
        1 for a in nino.asistencias if a.estado == EstadoAsistencia.NO_ASISTIO and desde <= a.fecha_programada <= hoy
    )
    dias_visita = (hoy - ultima_visita).days if ultima_visita else None
    componentes = (
        ComponentePuntaje(
            "SEVERIDAD",
            "Severidad de la última evaluación",
            clasificacion.value,
            pesos.por_severidad.get(clasificacion, 0.0),
            max(pesos.por_severidad.values()),
        ),
        ComponentePuntaje(
            "CONTROL_VENCIDO",
            "Días del control más vencido",
            f"{dias_vencido} días",
            _proporcional(dias_vencido, pesos.dias_tope_control_vencido, pesos.maximo_control_vencido),
            pesos.maximo_control_vencido,
        ),
        ComponentePuntaje(
            "INASISTENCIAS",
            f"Inasistencias en los últimos {pesos.dias_ventana_inasistencias} días",
            str(inasistencias),
            min(inasistencias * pesos.puntos_por_inasistencia, pesos.maximo_inasistencias),
            pesos.maximo_inasistencias,
        ),
        ComponentePuntaje(
            "ULTIMA_VISITA",
            "Tiempo desde la última visita",
            "sin visitas" if dias_visita is None else f"{dias_visita} días",
            pesos.maximo_ultima_visita
            if dias_visita is None
            else _proporcional(dias_visita, pesos.dias_tope_ultima_visita, pesos.maximo_ultima_visita),
            pesos.maximo_ultima_visita,
        ),
    )
    if alerta_barrera is not None:
        componentes += (
            ComponentePuntaje(
                "BARRERA_CRITICA",
                "Barreras críticas",
                "; ".join(r.descripcion for r in alerta_barrera.razones),
                pesos.puntos_barrera_critica[alerta_barrera.prioridad],
                max(pesos.puntos_barrera_critica.values()),
            ),
        )
    return NinoPriorizado(
        nino_id=nino.id,
        dni=nino.dni,
        codigo_origen=nino.codigo_origen,
        nombre_completo=nino.nombre_completo,
        establecimiento=nino.establecimiento,
        comunidad=nino.comunidad,
        ultima_clasificacion=clasificacion,
        dias_control_vencido=dias_vencido,
        inasistencias_recientes=inasistencias,
        ultima_visita=ultima_visita,
        dias_desde_ultima_visita=dias_visita,
        puntaje=round(sum(c.puntos for c in componentes), 1),
        componentes=componentes,
    )


def ordenar_priorizados(items: list[NinoPriorizado]) -> list[NinoPriorizado]:
    """Mayor puntaje primero; a igual puntaje, más días de atraso, luego nombre e id (resultado repetible)."""
    return sorted(items, key=lambda i: (-i.puntaje, -i.dias_control_vencido, i.nombre_completo, i.nino_id))
