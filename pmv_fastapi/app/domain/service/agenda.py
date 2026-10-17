"""Agenda automática de controles (HIST-2.1, Incremento 2).

Servicio de dominio puro: a partir del expediente de un niño y de la fecha de hoy calcula qué controles le
corresponden y en qué estado normativo está cada uno. No diagnostica ni prescribe; solo programa y vigila
fechas. Los parámetros están centralizados y versionados en ``ESQUEMA_AGENDA_V1`` porque deben ser
confirmados por la microred (igual que las reglas clínicas, ADR-004).

Fuentes del esquema V1 (referenciales, pendientes de confirmación por la microred):
  * Dosajes por edad: esquema operativo del establecimiento, Sesión 1 (S1) Anexo A, Tablas A.3 y A.4,
    compatible con la NTS N.° 213-MINSA/DGIESP-2024 (DHx = dosaje de tamizaje; DHc1/DHc2 = dosajes de control).
  * Controles de hemoglobina del tratamiento a +1, +3 y +6 meses del diagnóstico: seguimiento del
    tratamiento según la NTS N.° 213-MINSA/DGIESP-2024.

Reglas (ver ADR-007):
  1. Dosajes por edad: fecha programada = nacimiento + N meses calendario (el día 31 pasa al último día del mes).
  2. Control de tratamiento: cada episodio de anemia (LEVE, MODERADA o SEVERA) programa C1M, C3M y C6M a partir de
     la fecha de la evaluación de diagnóstico. Un episodio empieza con la primera evaluación con anemia y sigue
     abierto mientras las evaluaciones posteriores mantengan la anemia; las evaluaciones con anemia dentro del
     episodio NO reinician el calendario. Se abre un episodio nuevo cuando hay anemia otra vez después de una
     evaluación SIN_ANEMIA o después de vencida la ventana del último control (C6M) del episodio anterior.
  3. Cumplimiento: un control se cumple con una evaluación fechada en [programada - 15 días, programada + 30 días].
     Una evaluación cumple como máximo un control: se asignan primero los pares más cercanos; en empate gana el
     control más antiguo y, a igual fecha, el de tratamiento.
  4. Estados: CUMPLIDO; PENDIENTE (hoy <= fecha límite; ``proximo`` si vence en 7 días o menos); VENCIDO (hoy >
     fecha límite; ``dias_vencido`` cuenta desde la fecha límite); CERRADO_RECUPERADO (control de tratamiento sin
     cumplir cuya ventana aún no había vencido cuando una evaluación posterior al diagnóstico resultó SIN_ANEMIA).
     Los controles que ya estaban vencidos antes de la recuperación siguen figurando como VENCIDO (historial
     fiel) salvo que ``cerrar_vencidos_al_recuperar`` se active en el esquema.
  5. La agenda empieza cuando el niño entra al sistema: solo se generan dosajes por edad con fecha programada >=
     fecha de la primera evaluación - 15 días. Así un niño registrado a los 14 meses no nace con controles
     «vencidos» de los 6, 9 y 12 meses.
  6. Solo niños en estado ACTIVO (los de ALTA no tienen agenda) y solo controles con el niño menor de 60 meses en
     la fecha programada.
"""

import calendar
from dataclasses import dataclass
from datetime import date, timedelta

from app.domain.model.agenda import (
    AgendaNino,
    ControlProgramado,
    EstadoControl,
    ResumenAgenda,
    TipoControl,
)
from app.domain.model.clasificacion import Clasificacion
from app.domain.model.entidades import Evaluacion, Nino
from app.domain.model.tiempo import edad_en_meses, fecha_local
from app.domain.service.reglas_clinicas import EDAD_MAX_MESES


@dataclass(frozen=True)
class EsquemaAgenda:
    """Parámetros normativos de la agenda (versionados)."""

    version: str
    fuente: str
    dosajes_por_edad: tuple[tuple[int, str], ...]  # (meses de edad, código)
    controles_tratamiento: tuple[tuple[int, str], ...]  # (meses desde el diagnóstico, código)
    tolerancia_previa_dias: int = 15
    tolerancia_posterior_dias: int = 30
    dias_proximo_a_vencer: int = 7
    cerrar_vencidos_al_recuperar: bool = False


ESQUEMA_AGENDA_V1 = EsquemaAgenda(
    version="AGENDA-V1",
    fuente="S1 Anexo A, Tablas A.3 y A.4 (esquema operativo del establecimiento); NTS N.° 213-MINSA/DGIESP-2024",
    dosajes_por_edad=(
        (6, "DHx"),
        (9, "DHc1"),
        (12, "DHc2"),
        (15, "DHx"),
        (18, "DHc1"),
        (21, "DHc2"),
        (24, "DHx"),
        (30, "DHc1"),
        (36, "DHx"),
        (39, "DHc1"),
        (48, "DHx"),
        (51, "DHc1"),
    ),
    controles_tratamiento=((1, "C1M"), (3, "C3M"), (6, "C6M")),
)

MOTIVO_ALTA = "El niño tiene alta: no se programan controles."
_ORDEN_TIPO = {TipoControl.CONTROL_TRATAMIENTO: 0, TipoControl.TAMIZAJE_EDAD: 1}


def agregar_meses(fecha: date, meses: int) -> date:
    """Suma meses calendario; si el día no existe en el mes destino se usa su último día (31-ene + 1 = 28/29-feb)."""
    indice = fecha.year * 12 + (fecha.month - 1) + meses
    anio, mes0 = divmod(indice, 12)
    mes = mes0 + 1
    return date(anio, mes, min(fecha.day, calendar.monthrange(anio, mes)[1]))


@dataclass
class _Episodio:
    fecha_diagnostico: date
    recuperado_en: date | None = None


@dataclass
class _Previsto:
    codigo: str
    tipo: TipoControl
    programada: date
    descripcion: str
    edad_meses: int | None = None
    episodio: _Episodio | None = None


def _previstos_por_edad(nino: Nino, evaluaciones: list[Evaluacion], esq: EsquemaAgenda) -> list[_Previsto]:
    # La agenda arranca con el niño en el sistema (regla 5).
    inicio = evaluaciones[0].fecha if evaluaciones else fecha_local(nino.creado_en)
    minimo = inicio - timedelta(days=esq.tolerancia_previa_dias)
    previstos = []
    for meses, codigo in esq.dosajes_por_edad:
        programada = agregar_meses(nino.fecha_nacimiento, meses)
        if programada < minimo or meses > EDAD_MAX_MESES:
            continue
        tipo_dosaje = "tamizaje" if codigo == "DHx" else "control"
        previstos.append(
            _Previsto(
                codigo,
                TipoControl.TAMIZAJE_EDAD,
                programada,
                f"Dosaje de {tipo_dosaje} {codigo} ({meses} meses)",
                edad_meses=meses,
            )
        )
    return previstos


def _episodios_de_anemia(evaluaciones: list[Evaluacion], esq: EsquemaAgenda) -> list[_Episodio]:
    meses_final = max(m for m, _ in esq.controles_tratamiento)
    episodios: list[_Episodio] = []
    abierto: _Episodio | None = None
    for ev in evaluaciones:
        if ev.tiene_anemia:
            vigente = abierto is not None and ev.fecha <= agregar_meses(
                abierto.fecha_diagnostico, meses_final
            ) + timedelta(days=esq.tolerancia_posterior_dias)
            if not vigente:
                abierto = _Episodio(ev.fecha)
                episodios.append(abierto)
        elif (
            ev.clasificacion == Clasificacion.SIN_ANEMIA
            and abierto is not None
            and ev.fecha > abierto.fecha_diagnostico
        ):
            abierto.recuperado_en = ev.fecha
            abierto = None
    return episodios


def _previstos_tratamiento(nino: Nino, episodios: list[_Episodio], esq: EsquemaAgenda) -> list[_Previsto]:
    previstos = []
    for episodio in episodios:
        for meses, codigo in esq.controles_tratamiento:
            programada = agregar_meses(episodio.fecha_diagnostico, meses)
            if edad_en_meses(nino.fecha_nacimiento, programada) > EDAD_MAX_MESES:
                continue
            plural = "mes" if meses == 1 else "meses"
            previstos.append(
                _Previsto(
                    codigo,
                    TipoControl.CONTROL_TRATAMIENTO,
                    programada,
                    f"Control de hemoglobina del tratamiento a {meses} {plural} ({codigo})",
                    episodio=episodio,
                )
            )
    return previstos


def _asignar_evaluaciones(
    previstos: list[_Previsto], evaluaciones: list[Evaluacion], esq: EsquemaAgenda
) -> dict[int, Evaluacion]:
    """Asigna a cada control, como máximo, una evaluación dentro de su ventana; cada evaluación sirve a un control."""
    pares = []
    for i, previsto in enumerate(previstos):
        for ev in evaluaciones:
            desfase = (ev.fecha - previsto.programada).days
            if -esq.tolerancia_previa_dias <= desfase <= esq.tolerancia_posterior_dias:
                clave = (abs(desfase), previsto.programada, _ORDEN_TIPO[previsto.tipo], ev.fecha, ev.creado_en)
                pares.append((clave, i, ev))
    pares.sort(key=lambda p: p[0])
    asignadas: dict[int, Evaluacion] = {}
    usadas: set[str] = set()
    for _, i, ev in pares:
        if i not in asignadas and ev.id not in usadas:
            asignadas[i] = ev
            usadas.add(ev.id)
    return asignadas


def _resolver(previsto: _Previsto, evaluacion: Evaluacion | None, hoy: date, esq: EsquemaAgenda) -> ControlProgramado:
    limite = previsto.programada + timedelta(days=esq.tolerancia_posterior_dias)
    campos = {
        "codigo": previsto.codigo,
        "tipo": previsto.tipo,
        "fecha_programada": previsto.programada,
        "fecha_limite": limite,
        "descripcion": previsto.descripcion,
        "fecha_inicio_ventana": previsto.programada - timedelta(days=esq.tolerancia_previa_dias),
        "edad_meses_programada": previsto.edad_meses,
    }
    if evaluacion is not None:
        return ControlProgramado(
            estado=EstadoControl.CUMPLIDO, dias_vencido=None, evaluacion_id=evaluacion.id, **campos
        )
    recuperado = previsto.episodio.recuperado_en if previsto.episodio else None
    if recuperado is not None and (esq.cerrar_vencidos_al_recuperar or limite >= recuperado):
        return ControlProgramado(
            estado=EstadoControl.CERRADO_RECUPERADO, dias_vencido=None, evaluacion_id=None, **campos
        )
    if hoy > limite:
        return ControlProgramado(
            estado=EstadoControl.VENCIDO, dias_vencido=(hoy - limite).days, evaluacion_id=None, **campos
        )
    proximo = (limite - hoy).days <= esq.dias_proximo_a_vencer
    return ControlProgramado(
        estado=EstadoControl.PENDIENTE, dias_vencido=None, evaluacion_id=None, proximo=proximo, **campos
    )


def _resumir(controles: list[ControlProgramado]) -> ResumenAgenda:
    pendientes = [c for c in controles if c.estado == EstadoControl.PENDIENTE]
    return ResumenAgenda(
        total=len(controles),
        cumplidos=sum(1 for c in controles if c.estado == EstadoControl.CUMPLIDO),
        pendientes=len(pendientes),
        vencidos=sum(1 for c in controles if c.estado == EstadoControl.VENCIDO),
        cerrados=sum(1 for c in controles if c.estado == EstadoControl.CERRADO_RECUPERADO),
        proximos=sum(1 for c in pendientes if c.proximo),
        proximo_control=pendientes[0] if pendientes else None,
    )


def generar_agenda(nino: Nino, hoy: date, esquema: EsquemaAgenda = ESQUEMA_AGENDA_V1) -> AgendaNino:
    """Calcula la agenda de controles de un niño a la fecha ``hoy`` (ordenada por fecha programada)."""
    if nino.estado != "ACTIVO":
        return AgendaNino(nino.id, esquema.version, hoy, aplica=False, motivo=MOTIVO_ALTA)
    evaluaciones = sorted(nino.evaluaciones, key=lambda e: (e.fecha, e.creado_en))
    previstos = _previstos_por_edad(nino, evaluaciones, esquema)
    previstos += _previstos_tratamiento(nino, _episodios_de_anemia(evaluaciones, esquema), esquema)
    previstos.sort(key=lambda p: (p.programada, _ORDEN_TIPO[p.tipo], p.codigo))
    asignadas = _asignar_evaluaciones(previstos, evaluaciones, esquema)
    controles = [_resolver(p, asignadas.get(i), hoy, esquema) for i, p in enumerate(previstos)]
    return AgendaNino(nino.id, esquema.version, hoy, aplica=True, controles=controles, resumen=_resumir(controles))
