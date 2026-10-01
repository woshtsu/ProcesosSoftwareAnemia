"""Entidades del dominio y sus validaciones (HU-01, HU-03)."""

import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime

from app.domain import reglas_clinicas as rc
from app.domain.errores import ErrorCampo, ErrorValidacion

PATRON_DNI = re.compile(r"^\d{8}$")
PATRON_CELULAR = re.compile(r"^9\d{8}$")


def edad_en_meses(fecha_nacimiento: date, fecha_referencia: date) -> int:
    meses = (fecha_referencia.year - fecha_nacimiento.year) * 12 + (fecha_referencia.month - fecha_nacimiento.month)
    if fecha_referencia.day < fecha_nacimiento.day:
        meses -= 1
    return meses


def ahora() -> datetime:
    return datetime.now(UTC)


@dataclass
class Evaluacion:
    """Dosaje de hemoglobina y antropometría de un control."""

    fecha: date
    hemoglobina_observada: float
    peso_kg: float
    talla_cm: float
    altitud_m: float
    edad_meses: int
    registrado_por: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nino_id: str = ""
    hemoglobina_ajustada: float = 0.0
    clasificacion: rc.Clasificacion = rc.Clasificacion.NO_APLICA
    creado_en: datetime = field(default_factory=ahora)

    def calcular(self) -> None:
        self.hemoglobina_ajustada = rc.hemoglobina_ajustada(self.hemoglobina_observada, self.altitud_m)
        self.clasificacion = rc.clasificar_anemia(self.edad_meses, self.hemoglobina_ajustada)

    @property
    def tiene_anemia(self) -> bool:
        return self.clasificacion in (
            rc.Clasificacion.LEVE,
            rc.Clasificacion.MODERADA,
            rc.Clasificacion.SEVERA,
        )


@dataclass
class Nino:
    dni: str
    nombres: str
    apellidos: str
    sexo: str
    fecha_nacimiento: date
    establecimiento: str
    distrito: str
    comunidad: str
    altitud_m: float
    tutor_nombre: str
    registrado_por: str
    tutor_celular: str | None = None
    estado: str = "ACTIVO"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creado_en: datetime = field(default_factory=ahora)
    actualizado_en: datetime = field(default_factory=ahora)
    evaluaciones: list[Evaluacion] = field(default_factory=list)

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"

    @property
    def ultima_evaluacion(self) -> Evaluacion | None:
        if not self.evaluaciones:
            return None
        return max(self.evaluaciones, key=lambda e: (e.fecha, e.creado_en))


def _texto(valor: str | None, campo: str, errores: list[ErrorCampo], minimo: int = 2) -> None:
    if valor is None or len(valor.strip()) < minimo:
        errores.append(ErrorCampo(campo, "Es obligatorio."))


def validar_datos_nino(datos: dict, hoy: date) -> list[ErrorCampo]:
    errores: list[ErrorCampo] = []
    dni = (datos.get("dni") or "").strip()
    if not PATRON_DNI.match(dni):
        errores.append(ErrorCampo("dni", "El DNI debe tener exactamente 8 dígitos."))
    _texto(datos.get("nombres"), "nombres", errores)
    _texto(datos.get("apellidos"), "apellidos", errores)
    if datos.get("sexo") not in ("F", "M"):
        errores.append(ErrorCampo("sexo", "Seleccione F o M."))
    fn = datos.get("fecha_nacimiento")
    if not isinstance(fn, date):
        errores.append(ErrorCampo("fecha_nacimiento", "Fecha de nacimiento inválida."))
    elif fn > hoy:
        errores.append(ErrorCampo("fecha_nacimiento", "No puede ser una fecha futura."))
    elif edad_en_meses(fn, hoy) > rc.EDAD_MAX_MESES:
        errores.append(ErrorCampo("fecha_nacimiento", "El sistema atiende a menores de 5 años (0 a 59 meses)."))
    _texto(datos.get("establecimiento"), "establecimiento", errores)
    _texto(datos.get("distrito"), "distrito", errores)
    _texto(datos.get("comunidad"), "comunidad", errores)
    altitud = datos.get("altitud_m")
    if altitud is None or not (rc.ALTITUD_MIN_M <= altitud <= rc.ALTITUD_MAX_M):
        errores.append(
            ErrorCampo("altitud_m", f"La altitud debe estar entre {rc.ALTITUD_MIN_M} y {rc.ALTITUD_MAX_M} m s. n. m.")
        )
    _texto(datos.get("tutor_nombre"), "tutor_nombre", errores)
    celular = datos.get("tutor_celular")
    if celular and not PATRON_CELULAR.match(celular):
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


def exigir(errores: list[ErrorCampo]) -> None:
    if errores:
        raise ErrorValidacion(errores)
