"""
Validaciones del dominio — PMV Anemia Junín (INC-1).

Sin dependencias externas. Cada función de validación devuelve una lista de
mensajes de error (vacía si es válida). Los mensajes son para uso interno;
las rutas y formularios los mapean a sus propios mensajes de usuario.
"""

from __future__ import annotations

import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

# ─── Constantes ───────────────────────────────────────────────────────────────

_RE_DNI = re.compile(r"^\d{8}$")
_RE_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s\-]+$")
_RE_TELEFONO = re.compile(r"^\d{9}$")

_PESO_MIN_KG = Decimal("1.000")
_PESO_MAX_KG = Decimal("30.000")
_HB_MIN_GDL = Decimal("2.0")
_HB_MAX_GDL = Decimal("25.0")
_ALT_MIN = 0
_ALT_MAX = 4999
_NOMBRE_MIN = 2
_NOMBRE_MAX = 80
_DISTRITO_MIN = 2
_DISTRITO_MAX = 80


# ─── Errores ──────────────────────────────────────────────────────────────────

class ErrorValidacion(Exception):
    """Error de validación con mapa de campos → lista de mensajes."""

    def __init__(self, errores: dict[str, list[str]]) -> None:
        self.errores = errores
        super().__init__(str(errores))

    @classmethod
    def si_hay_errores(cls, errores: dict[str, list[str]]) -> None:
        """Lanza ErrorValidacion si el mapa de errores no está vacío."""
        errores_reales = {k: v for k, v in errores.items() if v}
        if errores_reales:
            raise cls(errores_reales)


# ─── Validaciones individuales ────────────────────────────────────────────────

def validar_dni(dni: object) -> list[str]:
    if not isinstance(dni, str):
        return ["Debe ser texto"]
    if not _RE_DNI.match(dni):
        return ["Debe contener exactamente 8 dígitos"]
    return []


def validar_nombre(valor: object, campo: str = "nombre") -> list[str]:
    if not isinstance(valor, str):
        return [f"{campo}: Debe ser texto"]
    limpio = valor.strip()
    if len(limpio) < _NOMBRE_MIN:
        return [f"Debe tener al menos {_NOMBRE_MIN} caracteres"]
    if len(limpio) > _NOMBRE_MAX:
        return [f"Debe tener como máximo {_NOMBRE_MAX} caracteres"]
    if not _RE_NOMBRE.match(limpio):
        return ["Solo se permiten letras, espacios y guiones"]
    return []


def normalizar_nombre(valor: str) -> str:
    """Quita espacios exteriores y colapsa espacios internos."""
    return " ".join(valor.split())


def validar_fecha_nacimiento(fecha: object, fecha_referencia: date) -> list[str]:
    if not isinstance(fecha, date):
        return ["Debe ser una fecha válida"]
    if fecha > fecha_referencia:
        return ["No puede ser posterior a hoy"]
    # Edad máxima al registro: antes de cumplir 5 años (60 meses completos)
    meses = meses_completos(fecha, fecha_referencia)
    if meses >= 60:
        return ["El niño debe tener menos de 5 años al momento del registro"]
    return []


def validar_sexo(sexo: object) -> list[str]:
    if sexo not in ("F", "M"):
        return ["Debe ser F o M"]
    return []


def validar_tipo_nacimiento(tipo: object) -> list[str]:
    if tipo not in ("TERMINO", "PREMATURO"):
        return ["Debe ser TERMINO o PREMATURO"]
    return []


def validar_peso_kg(peso_raw: object) -> tuple[list[str], int]:
    """
    Valida el peso en kg y devuelve (errores, peso_en_gramos).
    Acepta str, int, float o Decimal con máximo 3 decimales.
    Rechaza precisión excesiva (más de 3 decimales) sin redondear silenciosamente.
    """
    try:
        peso = Decimal(str(peso_raw))
    except (InvalidOperation, TypeError, ValueError):
        return ["Debe ser un número válido"], 0

    # Verificar precisión excesiva
    if peso != peso.quantize(Decimal("0.001")):
        return ["Máximo 3 decimales permitidos"], 0

    if peso < _PESO_MIN_KG:
        return [f"Debe ser al menos {_PESO_MIN_KG} kg"], 0
    if peso > _PESO_MAX_KG:
        return [f"Debe ser como máximo {_PESO_MAX_KG} kg"], 0

    peso_g = int((peso * 1000).to_integral_value(rounding=ROUND_HALF_UP))
    return [], peso_g


def validar_distrito(distrito: object) -> list[str]:
    if not isinstance(distrito, str):
        return ["Debe ser texto"]
    limpio = distrito.strip()
    if len(limpio) < _DISTRITO_MIN:
        return [f"Debe tener al menos {_DISTRITO_MIN} caracteres"]
    if len(limpio) > _DISTRITO_MAX:
        return [f"Debe tener como máximo {_DISTRITO_MAX} caracteres"]
    return []


def normalizar_distrito(valor: str) -> str:
    return " ".join(valor.split())


def validar_altitud(altitud: object) -> list[str]:
    if not isinstance(altitud, int):
        try:
            altitud = int(altitud)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return ["Debe ser un número entero"]
    if altitud < _ALT_MIN or altitud > _ALT_MAX:
        return [f"Debe estar entre {_ALT_MIN} y {_ALT_MAX} metros"]
    return []


def validar_telefono(telefono: object) -> list[str]:
    if telefono is None or telefono == "":
        return []
    if not isinstance(telefono, str):
        return ["Debe ser texto"]
    if not _RE_TELEFONO.match(telefono):
        return ["Debe contener exactamente 9 dígitos"]
    return []


def validar_hb_gdl(hb_raw: object) -> tuple[list[str], int]:
    """
    Valida Hb en g/dL y devuelve (errores, hb_en_decimas).
    Acepta máximo 1 decimal. Rechaza precisión excesiva sin redondear.
    """
    try:
        hb = Decimal(str(hb_raw))
    except (InvalidOperation, TypeError, ValueError):
        return ["Debe ser un número válido"], 0

    # Verificar precisión excesiva (máximo 1 decimal)
    if hb != hb.quantize(Decimal("0.1")):
        return ["Máximo 1 decimal permitido"], 0

    if hb < _HB_MIN_GDL:
        return [f"Debe ser al menos {_HB_MIN_GDL} g/dL"], 0
    if hb > _HB_MAX_GDL:
        return [f"Debe ser como máximo {_HB_MAX_GDL} g/dL"], 0

    hb_ddl = int((hb * 10).to_integral_value(rounding=ROUND_HALF_UP))
    return [], hb_ddl


def validar_fecha_dosaje(
    fecha_dosaje: object,
    fecha_nacimiento: date,
    fecha_referencia: date,
) -> tuple[list[str], int]:
    """
    Valida la fecha del dosaje y devuelve (errores, edad_en_meses_completos).
    """
    if not isinstance(fecha_dosaje, date):
        return ["Debe ser una fecha válida"], 0
    if fecha_dosaje < fecha_nacimiento:
        return ["No puede ser anterior a la fecha de nacimiento"], 0
    if fecha_dosaje > fecha_referencia:
        return ["No puede ser posterior a hoy"], 0

    edad = meses_completos(fecha_nacimiento, fecha_dosaje)
    if edad >= 60:
        return ["La edad al dosaje debe ser menor de 60 meses"], 0

    return [], edad


# ─── Utilidades de fecha ──────────────────────────────────────────────────────

def meses_completos(fecha_inicio: date, fecha_fin: date) -> int:
    """
    Calcula meses completos entre dos fechas.
    Un mes es completo cuando el día del mes fin >= día del mes inicio
    (maneja años bisiestos: nacimiento 29-feb cuenta cumpleaños el 28-feb en años normales).
    """
    if fecha_fin < fecha_inicio:
        return 0

    meses = (fecha_fin.year - fecha_inicio.year) * 12 + (fecha_fin.month - fecha_inicio.month)

    # Ajuste: si el día fin es anterior al día inicio, no se completó el mes
    try:
        aniversario = fecha_inicio.replace(year=fecha_fin.year, month=fecha_fin.month)
    except ValueError:
        # El día no existe en ese mes (ej: 31 de febrero). Usamos último día del mes.
        import calendar
        ultimo_dia = calendar.monthrange(fecha_fin.year, fecha_fin.month)[1]
        aniversario = fecha_inicio.replace(
            year=fecha_fin.year, month=fecha_fin.month, day=ultimo_dia
        )

    if fecha_fin < aniversario:
        meses -= 1

    return max(0, meses)
