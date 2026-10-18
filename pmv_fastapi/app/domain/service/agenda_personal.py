"""Agenda del personal de un establecimiento (HIST-2.3, RF-08). Servicio de dominio puro.

Reúne, para un rango de fechas, los controles programados de los niños activos y los agrupa por día. Cada control
conserva el estado de la agenda normativa (ADR-007) y la asistencia registrada (ADR-010):
  * Se muestran los controles CUMPLIDO, PENDIENTE y VENCIDO cuya fecha programada cae en el rango; los
    CERRADO_RECUPERADO ya no se exigen y no se listan.
  * Los vencidos llevan la prioridad de la alerta (HIST-2.2).
  * Cada día trae sus totales (total, cumplidos, pendientes, vencidos, con inasistencia registrada); los días sin
    controles figuran con totales en cero.
  * Dentro de un día el orden es: vencidos (por prioridad), pendientes y cumplidos; luego nombre y código del control.
"""

from collections import Counter
from collections.abc import Iterable
from datetime import date, timedelta

from app.domain.model.agenda import AgendaNino, EstadoControl
from app.domain.model.agenda_personal import (
    AgendaPersonal,
    DiaAgendaPersonal,
    ItemAgendaPersonal,
    ResumenAgendaPersonal,
)
from app.domain.model.alertas import Prioridad
from app.domain.model.entidades import Nino
from app.domain.service.alertas import calcular_prioridad

_ORDEN_ESTADO = {EstadoControl.VENCIDO: 0, EstadoControl.PENDIENTE: 1, EstadoControl.CUMPLIDO: 2}
_ORDEN_PRIORIDAD = {Prioridad.ALTA: 0, Prioridad.MEDIA: 1, Prioridad.BAJA: 2, None: 3}


def semana_de(fecha: date) -> tuple[date, date]:
    """Lunes y domingo de la semana que contiene ``fecha`` (rango por defecto de la agenda del personal)."""
    lunes = fecha - timedelta(days=fecha.weekday())
    return lunes, lunes + timedelta(days=6)


def resolver_rango(desde: date | None, hasta: date | None, hoy: date) -> tuple[date, date]:
    """Completa el rango: sin fechas, la semana de ``hoy``; con una sola, siete días a partir de ella."""
    if desde is None and hasta is None:
        return semana_de(hoy)
    if hasta is None:
        return desde, desde + timedelta(days=6)
    if desde is None:
        return hasta - timedelta(days=6), hasta
    return desde, hasta


def _items_de_nino(nino: Nino, agenda: AgendaNino, desde: date, hasta: date) -> list[ItemAgendaPersonal]:
    ultima = nino.ultima_evaluacion.clasificacion if nino.ultima_evaluacion else None
    return [
        ItemAgendaPersonal(
            nino_id=nino.id,
            codigo_origen=nino.codigo_origen,
            dni=nino.dni,
            nombre_completo=nino.nombre_completo,
            establecimiento=nino.establecimiento,
            comunidad=nino.comunidad,
            control=c,
            prioridad=calcular_prioridad(c, ultima) if c.estado == EstadoControl.VENCIDO else None,
        )
        for c in agenda.controles
        if c.estado in _ORDEN_ESTADO and desde <= c.fecha_programada <= hasta
    ]


def _orden_item(item: ItemAgendaPersonal) -> tuple:
    return (
        _ORDEN_ESTADO[item.control.estado],
        _ORDEN_PRIORIDAD[item.prioridad],
        item.nombre_completo,
        item.control.codigo,
    )


def _dia(fecha: date, items: list[ItemAgendaPersonal]) -> DiaAgendaPersonal:
    items = sorted(items, key=_orden_item)
    estados = Counter(i.control.estado for i in items)
    return DiaAgendaPersonal(
        fecha=fecha,
        total=len(items),
        cumplidos=estados[EstadoControl.CUMPLIDO],
        pendientes=estados[EstadoControl.PENDIENTE],
        vencidos=estados[EstadoControl.VENCIDO],
        con_inasistencia=sum(1 for i in items if i.control.inasistencia_registrada),
        items=items,
    )


def construir_agenda_personal(
    agendas: Iterable[tuple[Nino, AgendaNino]],
    desde: date,
    hasta: date,
    hoy: date,
    establecimiento: str | None = None,
    comunidad: str | None = None,
    establecimientos_disponibles: list[str] | None = None,
    comunidades_disponibles: list[str] | None = None,
) -> AgendaPersonal:
    """Agrupa por día los controles del rango. ``agendas`` ya viene filtrada por establecimiento y comunidad."""
    por_dia: dict[date, list[ItemAgendaPersonal]] = {}
    for nino, agenda in agendas:
        for item in _items_de_nino(nino, agenda, desde, hasta):
            por_dia.setdefault(item.control.fecha_programada, []).append(item)
    dias = [
        _dia(desde + timedelta(days=i), por_dia.get(desde + timedelta(days=i), []))
        for i in range((hasta - desde).days + 1)
    ]
    resumen = ResumenAgendaPersonal(
        total=sum(d.total for d in dias),
        cumplidos=sum(d.cumplidos for d in dias),
        pendientes=sum(d.pendientes for d in dias),
        vencidos=sum(d.vencidos for d in dias),
        con_inasistencia=sum(d.con_inasistencia for d in dias),
        ninos=len({i.nino_id for d in dias for i in d.items}),
    )
    return AgendaPersonal(
        desde=desde,
        hasta=hasta,
        fecha_referencia=hoy,
        establecimiento=establecimiento,
        comunidad=comunidad,
        resumen=resumen,
        dias=dias,
        establecimientos_disponibles=establecimientos_disponibles or [],
        comunidades_disponibles=comunidades_disponibles or [],
    )
