"""Validaciones de los datos de entrada (HU-01, HU-03). Servicio de dominio puro."""

import re
from datetime import date

from app.domain.model.errores import ErrorCampo, ErrorValidacion
from app.domain.model.tiempo import edad_en_meses
from app.domain.service import reglas_clinicas as rc

# Solo dígitos ASCII y coincidencia completa (DEF-04): ``\d`` acepta dígitos Unicode y ``$`` un salto de línea final.
PATRON_DNI = re.compile(r"[0-9]{8}")
PATRON_CELULAR = re.compile(r"9[0-9]{8}")

PERIODO_MIN = date(2000, 1, 1)
PERIODO_MAX = date(2100, 12, 31)

# Largo máximo de los textos: coincide con las columnas VARCHAR del esquema (DEF-06).
LONGITUD_MAXIMA = {
    "nombres": 80,
    "apellidos": 80,
    "establecimiento": 120,
    "distrito": 80,
    "comunidad": 80,
    "tutor_nombre": 120,
}


def _texto(valor: str | None, campo: str, errores: list[ErrorCampo], minimo: int = 2) -> None:
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


def validar_datos_nino(datos: dict, hoy: date) -> list[ErrorCampo]:
    errores: list[ErrorCampo] = []
    dni = (datos.get("dni") or "").strip()
    if not PATRON_DNI.fullmatch(dni):
        errores.append(ErrorCampo("dni", "El DNI debe tener exactamente 8 dígitos."))
    _texto(datos.get("nombres"), "nombres", errores)
    _texto(datos.get("apellidos"), "apellidos", errores)
    if datos.get("sexo") not in ("F", "M"):
        errores.append(ErrorCampo("sexo", "Seleccione F o M."))
    errores += validar_fecha_nacimiento(datos.get("fecha_nacimiento"), hoy)
    _texto(datos.get("establecimiento"), "establecimiento", errores)
    _texto(datos.get("distrito"), "distrito", errores)
    _texto(datos.get("comunidad"), "comunidad", errores)
    errores += validar_altitud(datos.get("altitud_m"))
    _texto(datos.get("tutor_nombre"), "tutor_nombre", errores)
    celular = datos.get("tutor_celular")
    if celular and not PATRON_CELULAR.fullmatch(celular):
        errores.append(ErrorCampo("tutor_celular", "El celular debe tener 9 dígitos y empezar con 9."))
    return errores


def validar_datos_evaluacion(datos: dict, fecha_nacimiento: date | None, hoy: date) -> list[ErrorCampo]:
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
    peso = datos.get("peso_kg")
    if peso is None or not (rc.PESO_MIN_KG <= peso <= rc.PESO_MAX_KG):
        errores.append(ErrorCampo("peso_kg", f"El peso debe estar entre {rc.PESO_MIN_KG} y {rc.PESO_MAX_KG} kg."))
    talla = datos.get("talla_cm")
    if talla is None or not (rc.TALLA_MIN_CM <= talla <= rc.TALLA_MAX_CM):
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


def exigir(errores: list[ErrorCampo]) -> None:
    if errores:
        raise ErrorValidacion(errores)
