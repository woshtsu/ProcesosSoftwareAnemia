"""Entidades del dominio (HU-01, HU-02). Puras: sin frameworks ni reglas clínicas."""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

from app.domain.model.clasificacion import Clasificacion
from app.domain.model.tiempo import ahora


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
    clasificacion: Clasificacion = Clasificacion.NO_APLICA
    creado_en: datetime = field(default_factory=ahora)

    @property
    def tiene_anemia(self) -> bool:
        return self.clasificacion in (Clasificacion.LEVE, Clasificacion.MODERADA, Clasificacion.SEVERA)


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
