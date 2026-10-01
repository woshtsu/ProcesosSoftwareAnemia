"""Contratos de la API REST (DTO). La validación clínica vive en el dominio;
aquí solo se define la forma de los mensajes JSON."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class EvaluacionEntrada(BaseModel):
    fecha: date = Field(description="Fecha del control (AAAA-MM-DD)")
    hemoglobina_observada: float = Field(description="Hemoglobina medida con hemoglobinómetro (g/dL)")
    peso_kg: float
    talla_cm: float


class NinoEntrada(BaseModel):
    dni: str = Field(examples=["71234567"])
    nombres: str
    apellidos: str
    sexo: str = Field(description="F o M")
    fecha_nacimiento: date
    establecimiento: str
    distrito: str
    comunidad: str
    altitud_m: float
    tutor_nombre: str
    tutor_celular: str | None = None


class RegistroNinoEntrada(BaseModel):
    nino: NinoEntrada
    evaluacion_inicial: EvaluacionEntrada


class VistaPreviaEntrada(BaseModel):
    fecha_nacimiento: date
    altitud_m: float
    evaluacion: EvaluacionEntrada


class ActualizacionNino(BaseModel):
    establecimiento: str | None = None
    distrito: str | None = None
    comunidad: str | None = None
    altitud_m: float | None = None
    tutor_nombre: str | None = None
    tutor_celular: str | None = None
    estado: str | None = None


class EvaluacionSalida(BaseModel):
    id: str
    fecha: date
    edad_meses: int
    hemoglobina_observada: float
    altitud_m: float
    hemoglobina_ajustada: float
    clasificacion: str
    peso_kg: float
    talla_cm: float
    registrado_por: str


class NinoSalida(BaseModel):
    id: str
    dni: str
    nombres: str
    apellidos: str
    sexo: str
    fecha_nacimiento: date
    edad_meses: int
    establecimiento: str
    distrito: str
    comunidad: str
    altitud_m: float
    tutor_nombre: str
    tutor_celular: str | None
    estado: str
    registrado_por: str
    creado_en: datetime
    actualizado_en: datetime


class ExpedienteSalida(NinoSalida):
    evaluaciones: list[EvaluacionSalida]


class FilaSeguimiento(BaseModel):
    id: str
    dni: str
    nombre_completo: str
    edad_meses: int
    comunidad: str
    estado: str
    ultima_fecha_control: date | None
    ultima_hb_ajustada: float | None
    ultima_clasificacion: str | None
    dias_desde_ultimo_control: int | None
    control_atrasado: bool


class ReporteComunidad(BaseModel):
    comunidad: str
    evaluaciones: int
    con_anemia: int


class ReportePeriodo(BaseModel):
    desde: date
    hasta: date
    ninos_registrados: int
    evaluaciones_realizadas: int
    ninos_evaluados: int
    ninos_con_anemia: int
    por_clasificacion: dict[str, int]
    por_comunidad: list[ReporteComunidad]


class ErrorDetalle(BaseModel):
    campo: str
    mensaje: str


class RespuestaError(BaseModel):
    mensaje: str
    errores: list[ErrorDetalle] = []
