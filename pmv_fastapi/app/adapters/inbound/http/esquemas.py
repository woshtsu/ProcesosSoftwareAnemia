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
    control_atrasado: bool = Field(description="True si la agenda normativa tiene al menos un control VENCIDO")
    controles_vencidos: int = Field(description="Cantidad de controles VENCIDOS en la agenda del niño")


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


class ControlSalida(BaseModel):
    codigo: str = Field(description="DHx, DHc1, DHc2 (por edad) o C1M, C3M, C6M (tratamiento)")
    tipo: str = Field(description="TAMIZAJE_EDAD o CONTROL_TRATAMIENTO")
    descripcion: str
    fecha_programada: date
    fecha_inicio_ventana: date = Field(description="Primer día en que una evaluación cumple el control")
    fecha_limite: date = Field(description="Último día en que una evaluación cumple el control")
    estado: str = Field(description="CUMPLIDO, PENDIENTE, VENCIDO o CERRADO_RECUPERADO")
    proximo: bool = Field(description="PENDIENTE que vence en 7 días o menos")
    dias_vencido: int | None = Field(description="Días desde la fecha límite (solo VENCIDO)")
    evaluacion_id: str | None = Field(description="Evaluación que cumplió el control (solo CUMPLIDO)")
    edad_meses_programada: int | None = Field(description="Edad objetivo en meses (solo controles por edad)")


class ResumenAgendaSalida(BaseModel):
    total: int
    cumplidos: int
    pendientes: int
    vencidos: int
    cerrados: int
    proximos: int
    proximo_control: ControlSalida | None


class AgendaSalida(BaseModel):
    nino_id: str
    version_esquema: str
    fecha_referencia: date
    aplica: bool = Field(description="False si el niño tiene alta: no se programan controles")
    motivo: str | None
    resumen: ResumenAgendaSalida
    controles: list[ControlSalida]


class AlertaNino(BaseModel):
    id: str
    dni: str
    nombre_completo: str
    comunidad: str
    tutor_celular: str | None


class AlertaSalida(BaseModel):
    nino: AlertaNino
    control: ControlSalida
    ultima_clasificacion: str | None
    prioridad: str = Field(description="ALTA, MEDIA o BAJA")


class ResumenAlertasSalida(BaseModel):
    total_vencidos: int
    por_prioridad: dict[str, int]
    ninos_con_vencidos: int
    proximos_7_dias: int


class ErrorDetalle(BaseModel):
    campo: str
    mensaje: str


class RespuestaError(BaseModel):
    mensaje: str
    errores: list[ErrorDetalle] = []
