"""Validaciones de los datos de entrada (HU-01, HU-03). Servicio de dominio puro."""

import re
from datetime import date

from app.domain.model.errores import ErrorCampo, ErrorValidacion
from app.domain.model.origen import OrigenDatos
from app.domain.model.tiempo import edad_en_meses
from app.domain.service import reglas_clinicas as rc

# Solo dígitos ASCII y coincidencia completa (DEF-04): ``\d`` acepta dígitos Unicode y ``$`` un salto de línea final.
PATRON_DNI = re.compile(r"[0-9]{8}")
PATRON_CELULAR = re.compile(r"9[0-9]{8}")

PERIODO_MIN = date(2000, 1, 1)
PERIODO_MAX = date(2100, 12, 31)
DIAS_MAX_AGENDA_PERSONAL = 31  # rango máximo de la agenda del personal (HIST-2.3), ambos extremos incluidos

# Largo máximo de los textos: coincide con las columnas VARCHAR del esquema (DEF-06).
LONGITUD_MAXIMA = {
    "nombres": 80,
    "apellidos": 80,
    "establecimiento": 120,
    "distrito": 80,
    "comunidad": 80,
    "tutor_nombre": 120,
}


def _texto(valor: str | None, campo: str, errores: list[ErrorCampo], minimo: int = 2, obligatorio: bool = True) -> None:
    if not obligatorio and (valor is None or not valor.strip()):
        return  # campo opcional vacío (solo registros de un dataset, ADR-009)
    if valor is None or len(valor.strip()) < minimo:
        errores.append(ErrorCampo(campo, "Es obligatorio."))
    elif len(valor.strip()) > LONGITUD_MAXIMA[campo]:
        errores.append(ErrorCampo(campo, f"No puede superar {LONGITUD_MAXIMA[campo]} caracteres."))


def validar_altitud(altitud: float | None) -> list[ErrorCampo]:
    """Altitud plausible; también rechaza NaN e infinitos (DEF-05)."""
    if altitud is None or not (rc.ALTITUD_MIN_M <= altitud <= rc.ALTITUD_MAX_M):
        return [
            ErrorCampo("altitud_m", f"La altitud debe estar entre {rc.ALTITUD_MIN_M} y {rc.ALTITUD_MAX_M} m s. n. m.")
        ]
    return []


def validar_fecha_nacimiento(fecha: date | None, hoy: date) -> list[ErrorCampo]:
    if not isinstance(fecha, date):
        return [ErrorCampo("fecha_nacimiento", "Fecha de nacimiento inválida.")]
    if fecha > hoy:
        return [ErrorCampo("fecha_nacimiento", "No puede ser una fecha futura.")]
    if edad_en_meses(fecha, hoy) > rc.EDAD_MAX_MESES:
        return [ErrorCampo("fecha_nacimiento", "El sistema atiende a menores de 5 años (0 a 59 meses).")]
    return []


def validar_datos_nino(datos: dict, hoy: date, origen: OrigenDatos = OrigenDatos.SISTEMA) -> list[ErrorCampo]:
    """Valida los datos de un niño. Con origen SISTEMA todo es obligatorio; con origen DATASET los datos personales
    (DNI, nombres, apellidos, sexo, tutor) pueden faltar, pero si vienen deben cumplir el mismo formato (ADR-009)."""
    errores: list[ErrorCampo] = []
    obligatorio = origen == OrigenDatos.SISTEMA
    dni = (datos.get("dni") or "").strip()
    if (obligatorio or dni) and not PATRON_DNI.fullmatch(dni):
        errores.append(ErrorCampo("dni", "El DNI debe tener exactamente 8 dígitos."))
    _texto(datos.get("nombres"), "nombres", errores, obligatorio=obligatorio)
    _texto(datos.get("apellidos"), "apellidos", errores, obligatorio=obligatorio)
    if datos.get("sexo") not in ("F", "M") and (obligatorio or datos.get("sexo")):
        errores.append(ErrorCampo("sexo", "Seleccione F o M."))
    errores += validar_fecha_nacimiento(datos.get("fecha_nacimiento"), hoy)
    _texto(datos.get("establecimiento"), "establecimiento", errores)
    _texto(datos.get("distrito"), "distrito", errores)
    _texto(datos.get("comunidad"), "comunidad", errores)
    errores += validar_altitud(datos.get("altitud_m"))
    _texto(datos.get("tutor_nombre"), "tutor_nombre", errores, obligatorio=obligatorio)
    celular = datos.get("tutor_celular")
    if celular and not PATRON_CELULAR.fullmatch(celular):
        errores.append(ErrorCampo("tutor_celular", "El celular debe tener 9 dígitos y empezar con 9."))
    return errores


def _fuera_de_rango(valor: float | None, minimo: float, maximo: float, obligatorio: bool) -> bool:
    """True si falta un valor obligatorio o está fuera de rango (NaN e infinitos también cuentan como fuera)."""
    if valor is None:
        return obligatorio
    return not (minimo <= valor <= maximo)


def validar_datos_evaluacion(
    datos: dict, fecha_nacimiento: date | None, hoy: date, antropometria_obligatoria: bool = True
) -> list[ErrorCampo]:
    """Valida una evaluación. Peso y talla son obligatorios salvo en la importación de un dataset que no los trae
    (``antropometria_obligatoria=False``); si vienen, siempre se validan sus rangos."""
    errores: list[ErrorCampo] = []
    fecha = datos.get("fecha")
    if not isinstance(fecha, date):
        errores.append(ErrorCampo("fecha", "Fecha de evaluación inválida."))
    else:
        if fecha > hoy:
            errores.append(ErrorCampo("fecha", "La fecha de evaluación no puede ser futura."))
        if fecha_nacimiento and fecha < fecha_nacimiento:
            errores.append(ErrorCampo("fecha", "La evaluación no puede ser anterior al nacimiento."))
    hb = datos.get("hemoglobina_observada")
    if hb is None or not (rc.HB_MIN_CAPTURA <= hb <= rc.HB_MAX_CAPTURA):
        errores.append(
            ErrorCampo(
                "hemoglobina_observada",
                f"Hemoglobina fuera del rango clínico válido ({rc.HB_MIN_CAPTURA} a {rc.HB_MAX_CAPTURA} g/dL). "
                "Verifique la lectura.",
            )
        )
    if _fuera_de_rango(datos.get("peso_kg"), rc.PESO_MIN_KG, rc.PESO_MAX_KG, antropometria_obligatoria):
        errores.append(ErrorCampo("peso_kg", f"El peso debe estar entre {rc.PESO_MIN_KG} y {rc.PESO_MAX_KG} kg."))
    if _fuera_de_rango(datos.get("talla_cm"), rc.TALLA_MIN_CM, rc.TALLA_MAX_CM, antropometria_obligatoria):
        errores.append(ErrorCampo("talla_cm", f"La talla debe estar entre {rc.TALLA_MIN_CM} y {rc.TALLA_MAX_CM} cm."))
    return errores


def validar_periodo(desde: date, hasta: date) -> list[ErrorCampo]:
    """Periodo de un reporte: ordenado y dentro de un rango razonable (DEF-03: fechas extremas provocaban un 500)."""
    errores = []
    if desde > hasta:
        errores.append(ErrorCampo("desde", "La fecha inicial debe ser anterior o igual a la final."))
    for campo, valor in (("desde", desde), ("hasta", hasta)):
        if not (PERIODO_MIN <= valor <= PERIODO_MAX):
            errores.append(ErrorCampo(campo, f"La fecha debe estar entre {PERIODO_MIN.year} y {PERIODO_MAX.year}."))
    return errores


def validar_rango_agenda(desde: date, hasta: date) -> list[ErrorCampo]:
    """Rango de la agenda del personal (HIST-2.3): ordenado, entre 2000 y 2100 y de 31 días como máximo."""
    errores = validar_periodo(desde, hasta)
    if not errores and (hasta - desde).days + 1 > DIAS_MAX_AGENDA_PERSONAL:
        errores.append(ErrorCampo("hasta", f"El rango no puede superar {DIAS_MAX_AGENDA_PERSONAL} días."))
    return errores


def exigir(errores: list[ErrorCampo]) -> None:
    if errores:
        raise ErrorValidacion(errores)
