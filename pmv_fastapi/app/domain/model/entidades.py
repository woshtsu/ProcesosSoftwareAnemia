"""Entidades del dominio (HU-01, HU-02). Puras: sin frameworks ni reglas clínicas."""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

from app.domain.model.asistencia import AsistenciaControl
from app.domain.model.clasificacion import Clasificacion
from app.domain.model.origen import OrigenDatos
from app.domain.model.tiempo import ahora


@dataclass
class Evaluacion:
    """Dosaje de hemoglobina y antropometría de un control.

    ``peso_kg`` y ``talla_cm`` son ``None`` solo en las evaluaciones importadas de un dataset que no las registra
    (ADR-009); las evaluaciones registradas desde el sistema siempre los traen.
    """

    fecha: date
    hemoglobina_observada: float
    peso_kg: float | None
    talla_cm: float | None
    altitud_m: float
    edad_meses: int
    registrado_por: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nino_id: str = ""
    hemoglobina_ajustada: float = 0.0
    clasificacion: Clasificacion = Clasificacion.NO_APLICA
    creado_en: datetime = field(default_factory=ahora)
    clasificacion_origen: str | None = (
        None  # severidad que registró el HIS (LEV, MOD, SEV): solo en la evaluación importada
    )

    @property
    def tiene_anemia(self) -> bool:
        return self.clasificacion in (Clasificacion.LEVE, Clasificacion.MODERADA, Clasificacion.SEVERA)


@dataclass
class Nino:
    """Niño en seguimiento.

    Con origen ``SISTEMA`` dni, nombres, apellidos, sexo y tutor son obligatorios (lo exigen las validaciones y las
    restricciones de la base). Con origen ``DATASET_DIRESA_JUNIN`` pueden ser ``None``: el registro es un seudónimo
    (``codigo_origen``) sin datos personales (ADR-009).
    """

    dni: str | None
    nombres: str | None
    apellidos: str | None
    sexo: str | None
    fecha_nacimiento: date
    establecimiento: str
    distrito: str
    comunidad: str
    altitud_m: float
    tutor_nombre: str | None
    registrado_por: str
    tutor_celular: str | None = None
    estado: str = "ACTIVO"
    origen: OrigenDatos = OrigenDatos.SISTEMA
    codigo_origen: str | None = None
    red: str | None = None
    microred: str | None = None
    provincia: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creado_en: datetime = field(default_factory=ahora)
    actualizado_en: datetime = field(default_factory=ahora)
    evaluaciones: list[Evaluacion] = field(default_factory=list)
    asistencias: list[AsistenciaControl] = field(default_factory=list)

    @property
    def es_dataset(self) -> bool:
        return self.origen != OrigenDatos.SISTEMA

    @property
    def nombre_completo(self) -> str:
        """Nombre legible: sin nombres (registro del dataset) se muestra el código seudónimo."""
        nombre = " ".join(p for p in (self.nombres, self.apellidos) if p)
        if nombre:
            return nombre
        return f"Registro {self.codigo_origen} (dataset anonimizado)" if self.codigo_origen else "Registro sin nombre"

    @property
    def ultima_evaluacion(self) -> Evaluacion | None:
        if not self.evaluaciones:
            return None
        return max(self.evaluaciones, key=lambda e: (e.fecha, e.creado_en))
