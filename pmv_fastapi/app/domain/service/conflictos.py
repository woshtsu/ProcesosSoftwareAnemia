"""Reglas de conflicto de la sincronización (HIST-3.3, ADR-012). Servicio de dominio puro y determinista.

Cada operación del dispositivo se compara con lo que el servidor ya tiene; el servidor es la fuente de verdad y
nunca se sobrescribe a ciegas:

  (a) Niño: si el DNI ya existe y los datos son distintos -> CONFLICTO; si coinciden se toma el niño existente y se
      mapea (no es conflicto). Con el niño idéntico, la evaluación inicial sigue la regla (b).
  (b) Evaluación del mismo niño y la misma fecha: hemoglobina igual -> DUPLICADA lógica (se mapea a la existente);
      hemoglobina distinta -> CONFLICTO; si no hay evaluación esa fecha se crea.
  (c) Asistencia del mismo control (código y fecha programada): mismo estado -> se mapea; estado distinto -> CONFLICTO.
  (d) Visita del mismo niño y fecha: igual -> se mapea; distinta -> CONFLICTO.

Al resolver un conflicto con APLICAR_CLIENTE solo se reemplaza el valor del servidor donde el dominio lo permite
(``motivo_no_aplicable``): los datos de identidad de un niño (nombres, apellidos, sexo, fecha de nacimiento) nunca se
sobrescriben, y una asistencia respaldada por una evaluación no se cambia.
"""

from dataclasses import dataclass, field
from enum import StrEnum

from app.domain.model.asistencia import AsistenciaControl
from app.domain.model.entidades import Evaluacion, Nino
from app.domain.model.sincronizacion import TipoOperacion
from app.domain.model.visita import ConsumoSuplemento, VisitaDomiciliaria

TOLERANCIA_HB = 0.05  # g/dL: la hemoglobina se captura con un decimal
CAMPOS_IDENTIDAD = ("nombres", "apellidos", "sexo", "fecha_nacimiento")
CAMPOS_EDITABLES = ("establecimiento", "distrito", "comunidad", "altitud_m", "tutor_nombre", "tutor_celular")
PREFIJO_EVALUACION = "evaluacion."


class AccionSync(StrEnum):
    CREAR = "CREAR"  # no existe nada equivalente en el servidor
    MAPEAR = "MAPEAR"  # el servidor ya tiene el mismo dato: se usa el existente
    AGREGAR_EVALUACION = "AGREGAR_EVALUACION"  # el niño ya existe idéntico, pero le falta la evaluación del dispositivo
    CONFLICTO = "CONFLICTO"  # el servidor tiene un dato distinto


@dataclass(frozen=True)
class Decision:
    accion: AccionSync
    id_recurso: str | None = None
    motivo: str | None = None
    datos_servidor: dict = field(default_factory=dict)
    diferencias: tuple[str, ...] = ()


def _texto(valor) -> str:
    return " ".join(str(valor).split()).casefold() if valor else ""


def _distinto(campo: str, servidor, cliente) -> bool:
    if campo == "altitud_m":
        return cliente is None or abs(servidor - cliente) > 1e-6
    if campo == "fecha_nacimiento":
        return servidor != cliente
    return _texto(servidor) != _texto(cliente)


def hemoglobina_igual(a: float, b: float) -> bool:
    return abs(a - b) < TOLERANCIA_HB


# --- Instantáneas en JSON (lo que se guarda en el conflicto y se muestra a la persona) -----------------------------


def instantanea_nino(n: Nino) -> dict:
    return {
        "id": n.id,
        "dni": n.dni,
        "nombres": n.nombres,
        "apellidos": n.apellidos,
        "sexo": n.sexo,
        "fecha_nacimiento": n.fecha_nacimiento.isoformat(),
        "establecimiento": n.establecimiento,
        "distrito": n.distrito,
        "comunidad": n.comunidad,
        "altitud_m": n.altitud_m,
        "tutor_nombre": n.tutor_nombre,
        "tutor_celular": n.tutor_celular,
    }


def instantanea_evaluacion(e: Evaluacion) -> dict:
    return {
        "id": e.id,
        "fecha": e.fecha.isoformat(),
        "hemoglobina_observada": e.hemoglobina_observada,
        "hemoglobina_ajustada": e.hemoglobina_ajustada,
        "clasificacion": e.clasificacion.value,
        "peso_kg": e.peso_kg,
        "talla_cm": e.talla_cm,
        "registrado_por": e.registrado_por,
    }


def instantanea_asistencia(a: AsistenciaControl) -> dict:
    return {
        "id": a.id,
        "codigo": a.codigo_control,
        "fecha_programada": a.fecha_programada.isoformat(),
        "estado": a.estado.value,
        "motivo": a.motivo,
        "evaluacion_id": a.evaluacion_id,
        "registrado_por": a.registrado_por,
    }


def instantanea_visita(v: VisitaDomiciliaria) -> dict:
    return {
        "id": v.id,
        "fecha": v.fecha.isoformat(),
        "resultado": v.resultado.value,
        "consume_suplemento": v.consume_suplemento.value,
        "observaciones": v.observaciones,
        "registrado_por": v.registrado_por,
    }


# --- Decisiones ----------------------------------------------------------------------------------------------------


def diferencias_nino(existente: Nino, datos: dict) -> tuple[str, ...]:
    """Campos en que los datos del dispositivo difieren del niño que ya está en el servidor."""
    return tuple(c for c in (*CAMPOS_IDENTIDAD, *CAMPOS_EDITABLES) if _distinto(c, getattr(existente, c), datos.get(c)))


def decidir_evaluacion(nino: Nino, datos: dict) -> Decision:
    del_dia = sorted((e for e in nino.evaluaciones if e.fecha == datos["fecha"]), key=lambda e: e.creado_en)
    if not del_dia:
        return Decision(AccionSync.CREAR)
    igual = next(
        (e for e in del_dia if hemoglobina_igual(e.hemoglobina_observada, datos["hemoglobina_observada"])), None
    )
    if igual:
        return Decision(AccionSync.MAPEAR, igual.id)
    previa = del_dia[0]
    return Decision(
        AccionSync.CONFLICTO,
        previa.id,
        f"El niño ya tiene una evaluación del {datos['fecha'].isoformat()} con hemoglobina "
        f"{previa.hemoglobina_observada} g/dL; el dispositivo registró {datos['hemoglobina_observada']} g/dL.",
        instantanea_evaluacion(previa),
        ("hemoglobina_observada",),
    )


def decidir_nino(existente: Nino | None, datos_nino: dict, datos_evaluacion: dict) -> Decision:
    if existente is None:
        return Decision(AccionSync.CREAR)
    diferencias = diferencias_nino(existente, datos_nino)
    if diferencias:
        return Decision(
            AccionSync.CONFLICTO,
            existente.id,
            f"Ya existe un niño con el DNI {existente.dni} y datos distintos ({', '.join(diferencias)}).",
            instantanea_nino(existente),
            diferencias,
        )
    evaluacion = decidir_evaluacion(existente, datos_evaluacion)
    if evaluacion.accion == AccionSync.CREAR:
        return Decision(AccionSync.AGREGAR_EVALUACION, existente.id)
    if evaluacion.accion == AccionSync.MAPEAR:
        return Decision(AccionSync.MAPEAR, existente.id)
    return Decision(
        AccionSync.CONFLICTO,
        existente.id,
        evaluacion.motivo,
        {**instantanea_nino(existente), "evaluacion": evaluacion.datos_servidor},
        (PREFIJO_EVALUACION + evaluacion.diferencias[0],),
    )


def decidir_asistencia(nino: Nino, datos: dict) -> Decision:
    previa = next(
        (
            a
            for a in nino.asistencias
            if a.codigo_control == datos["codigo"] and a.fecha_programada == datos["fecha_programada"]
        ),
        None,
    )
    if previa is None:
        return Decision(AccionSync.CREAR)
    if previa.estado.value == datos["estado"]:
        return Decision(AccionSync.MAPEAR, previa.id)
    return Decision(
        AccionSync.CONFLICTO,
        previa.id,
        f"El control {previa.codigo_control} del {previa.fecha_programada.isoformat()} ya tiene registrado "
        f"«{previa.estado.value}»; el dispositivo registró «{datos['estado']}».",
        instantanea_asistencia(previa),
        ("estado",),
    )


def decidir_visita(visita_del_dia: VisitaDomiciliaria | None, datos: dict) -> Decision:
    if visita_del_dia is None:
        return Decision(AccionSync.CREAR)
    propuesta = {
        "resultado": datos["resultado"],
        "consume_suplemento": datos.get("consume_suplemento") or ConsumoSuplemento.DESCONOCIDO.value,
        "observaciones": (datos.get("observaciones") or "").strip() or None,
    }
    actual = {
        "resultado": visita_del_dia.resultado.value,
        "consume_suplemento": visita_del_dia.consume_suplemento.value,
        "observaciones": visita_del_dia.observaciones,
    }
    diferencias = tuple(c for c, valor in propuesta.items() if _texto(actual[c]) != _texto(valor))
    if not diferencias:
        return Decision(AccionSync.MAPEAR, visita_del_dia.id)
    return Decision(
        AccionSync.CONFLICTO,
        visita_del_dia.id,
        f"El niño ya tiene una visita registrada el {visita_del_dia.fecha.isoformat()} con datos distintos "
        f"({', '.join(diferencias)}).",
        instantanea_visita(visita_del_dia),
        diferencias,
    )


def motivo_no_aplicable(tipo: str, diferencias: tuple[str, ...], datos_servidor: dict) -> str | None:
    """Por qué APLICAR_CLIENTE no se puede ejecutar (``None`` si se puede)."""
    if tipo == TipoOperacion.REGISTRAR_NINO:
        permitidos = {*CAMPOS_EDITABLES}
        bloqueados = [d for d in diferencias if d not in permitidos and not d.startswith(PREFIJO_EVALUACION)]
        if bloqueados:
            return (
                "Los datos de identidad del niño (nombres, apellidos, sexo y fecha de nacimiento) no se sobrescriben: "
                f"{', '.join(bloqueados)}. Conserve el dato del servidor o descarte la operación."
            )
    if tipo == TipoOperacion.REGISTRAR_ASISTENCIA and datos_servidor.get("evaluacion_id"):
        return "La asistencia del servidor está respaldada por una evaluación y no se puede cambiar."
    return None
