"""Contratos de la API REST (DTO). La validación clínica vive en el dominio;
aquí solo se define la forma de los mensajes JSON."""

from datetime import date, datetime
from typing import Any

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
    clasificacion_origen: str | None = Field(
        default=None, description="Severidad registrada por el HIS (LEV, MOD, SEV); solo en evaluaciones importadas"
    )
    peso_kg: float | None = Field(description="None en las evaluaciones importadas de un dataset (no las registra)")
    talla_cm: float | None
    registrado_por: str


class NinoSalida(BaseModel):
    id: str
    dni: str | None = Field(description="None en los registros del dataset anonimizado")
    nombres: str | None
    apellidos: str | None
    nombre_completo: str = Field(description="Nombre legible; sin nombres: «Registro DJ-00001 (dataset anonimizado)»")
    sexo: str | None
    fecha_nacimiento: date
    edad_meses: int
    establecimiento: str
    distrito: str
    comunidad: str
    altitud_m: float
    tutor_nombre: str | None
    tutor_celular: str | None
    estado: str
    origen: str = Field(description="SISTEMA o DATASET_DIRESA_JUNIN")
    codigo_origen: str | None = Field(description="Código seudónimo del dataset (p. ej. DJ-00001)")
    red: str | None
    microred: str | None
    provincia: str | None
    registrado_por: str
    creado_en: datetime
    actualizado_en: datetime


class ExpedienteSalida(NinoSalida):
    evaluaciones: list[EvaluacionSalida]


class FilaSeguimiento(BaseModel):
    id: str
    dni: str | None
    codigo_origen: str | None
    origen: str
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
    inasistencia_registrada: bool = Field(description="El personal registró que el niño no asistió a este control")
    motivo_inasistencia: str | None = None
    cumplido_por_asistencia: bool = Field(description="CUMPLIDO porque el personal registró que el niño asistió")


class ResumenAgendaSalida(BaseModel):
    total: int
    cumplidos: int
    pendientes: int
    vencidos: int
    cerrados: int
    proximos: int
    inasistencias: int = Field(description="Controles sin cumplir con una inasistencia registrada")
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
    dni: str | None
    codigo_origen: str | None
    nombre_completo: str
    comunidad: str
    tutor_celular: str | None


class AlertaSalida(BaseModel):
    nino: AlertaNino
    control: ControlSalida
    ultima_clasificacion: str | None
    prioridad: str = Field(description="ALTA, MEDIA o BAJA (sube un nivel si hay una inasistencia registrada)")


class ResumenAlertasSalida(BaseModel):
    total_vencidos: int
    por_prioridad: dict[str, int]
    ninos_con_vencidos: int
    proximos_7_dias: int


class AsistenciaEntrada(BaseModel):
    fecha_programada: date = Field(
        description="Fecha programada del control (AAAA-MM-DD), tal como figura en la agenda"
    )
    estado: str = Field(description="ASISTIO o NO_ASISTIO")
    motivo: str | None = Field(default=None, description="Obligatorio si no asistió (3 a 200 caracteres)")
    evaluacion_id: str | None = Field(
        default=None, description="Evaluación del día que acredita la asistencia (opcional)"
    )


class AsistenciaSalida(BaseModel):
    id: str
    nino_id: str
    codigo_control: str
    fecha_programada: date
    estado: str
    motivo: str | None
    evaluacion_id: str | None
    registrado_por: str
    creado_en: datetime


class ItemAgendaNino(BaseModel):
    id: str
    codigo_origen: str | None
    dni: str | None
    nombre_completo: str
    establecimiento: str
    comunidad: str


class ItemAgendaPersonalSalida(BaseModel):
    nino: ItemAgendaNino
    control: ControlSalida
    prioridad: str | None = Field(description="ALTA, MEDIA o BAJA; solo si el control está vencido")


class DiaAgendaSalida(BaseModel):
    fecha: date
    total: int
    cumplidos: int
    pendientes: int
    vencidos: int
    con_inasistencia: int
    items: list[ItemAgendaPersonalSalida]


class ResumenAgendaPersonalSalida(BaseModel):
    total: int
    cumplidos: int
    pendientes: int
    vencidos: int
    con_inasistencia: int
    ninos: int


class AgendaPersonalSalida(BaseModel):
    desde: date
    hasta: date
    fecha_referencia: date = Field(description="«Hoy» según el reloj del sistema")
    establecimiento: str | None
    comunidad: str | None
    resumen: ResumenAgendaPersonalSalida
    dias: list[DiaAgendaSalida]
    establecimientos_disponibles: list[str]
    comunidades_disponibles: list[str]


class SaludSalida(BaseModel):
    estado: str
    fecha_hoy: date = Field(description="«Hoy» según el reloj del sistema")
    fecha_referencia: date | None = Field(
        description="Fecha fija configurada con FECHA_REFERENCIA (p. ej. el corte del dataset); None con el reloj real"
    )


class ErrorDetalle(BaseModel):
    campo: str
    mensaje: str


class RespuestaError(BaseModel):
    mensaje: str
    errores: list[ErrorDetalle] = []


class VisitaEntrada(BaseModel):
    fecha: date = Field(description="Fecha de la visita (AAAA-MM-DD); no puede ser futura")
    resultado: str = Field(description="REALIZADA, NO_ENCONTRADO o RECHAZADA")
    consume_suplemento: str = Field(
        default="DESCONOCIDO",
        description="SI, NO o DESCONOCIDO; solo una visita REALIZADA puede indicar SI o NO",
    )
    observaciones: str | None = Field(default=None, description="Hasta 500 caracteres")


class VisitaSalida(BaseModel):
    id: str
    nino_id: str
    fecha: date
    resultado: str
    consume_suplemento: str
    observaciones: str | None
    registrado_por: str
    creado_en: datetime


class ComponentePuntajeSalida(BaseModel):
    codigo: str = Field(
        description="SEVERIDAD, CONTROL_VENCIDO, INASISTENCIAS, ULTIMA_VISITA o BARRERA_CRITICA (con barreras críticas)"
    )
    descripcion: str
    valor: str = Field(description="Lo observado: «MODERADA», «45 días», «sin visitas»…")
    puntos: float
    maximo: float


class NinoVisitaSalida(BaseModel):
    id: str
    dni: str | None
    codigo_origen: str | None
    nombre_completo: str
    comunidad: str


class VisitaPriorizadaSalida(BaseModel):
    posicion: int = Field(description="Lugar en la lista priorizada (1 = visitar primero)")
    nino: NinoVisitaSalida
    establecimiento: str
    ultima_clasificacion: str
    dias_control_vencido: int
    inasistencias_recientes: int = Field(description="Inasistencias (RF-09) de los últimos 90 días")
    ultima_visita: date | None
    dias_desde_ultima_visita: int | None
    puntaje: float = Field(
        description="0 a 100 (hasta 115 con barreras críticas): propuesta del equipo (ADR-013), no una norma del MINSA"
    )
    componentes: list[ComponentePuntajeSalida]


class NinoRefEntrada(BaseModel):
    id: str | None = Field(default=None, description="Id del niño en el servidor")
    id_cliente: str | None = Field(
        default=None, max_length=60, description="Id temporal de un niño registrado sin conexión en el dispositivo"
    )


class OperacionEntrada(BaseModel):
    id_operacion: str = Field(
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        description="UUID generado en el dispositivo; hace idempotente el reenvío",
    )
    tipo: str = Field(
        description="REGISTRAR_NINO, REGISTRAR_EVALUACION, REGISTRAR_ASISTENCIA, REGISTRAR_VISITA o REGISTRAR_BARRERA"
    )
    id_dispositivo: str = Field(min_length=1, max_length=60)
    fecha_local: datetime = Field(description="Fecha y hora local en que se registró (ISO 8601)")
    id_cliente: str | None = Field(default=None, max_length=60, description="Solo REGISTRAR_NINO: id temporal del niño")
    nino_ref: NinoRefEntrada | None = Field(default=None, description="Niño al que se refiere (no es REGISTRAR_NINO)")
    datos: dict[str, Any] = Field(
        description="REGISTRAR_NINO: {nino, evaluacion_inicial} como en POST /api/ninos; REGISTRAR_EVALUACION: "
        "{fecha, hemoglobina_observada, peso_kg, talla_cm}; REGISTRAR_ASISTENCIA: {codigo, fecha_programada, estado, "
        "motivo?}; REGISTRAR_VISITA: {fecha, resultado, consume_suplemento?, observaciones?}; REGISTRAR_BARRERA: "
        "{tipo, detalle?, fuente?, fecha?}"
    )


class LoteSincronizacionEntrada(BaseModel):
    operaciones: list[OperacionEntrada] = Field(min_length=1, max_length=200, description="De 1 a 200 operaciones")


class ResultadoOperacionSalida(BaseModel):
    id_operacion: str
    tipo: str
    resultado: str = Field(description="APLICADA, DUPLICADA, CONFLICTO o RECHAZADA")
    id_recurso: str | None = Field(description="Id del servidor del recurso aplicado, existente o en conflicto")
    id_cliente: str | None = Field(description="Mapeo id_cliente -> id_recurso de un niño aplicado o ya existente")
    id_conflicto: str | None
    mensaje: str | None
    errores: list[ErrorDetalle] = Field(description="Errores de validación por campo (solo RECHAZADA)")
    resultado_original: str | None = Field(
        description="Solo en DUPLICADA por reenvío: resultado de la primera vez que se procesó"
    )


class ResumenSincronizacionSalida(BaseModel):
    aplicadas: int
    duplicadas: int
    conflictos: int
    rechazadas: int


class SincronizacionSalida(BaseModel):
    resumen: ResumenSincronizacionSalida
    resultados: list[ResultadoOperacionSalida]


class ConflictoSalida(BaseModel):
    id: str
    id_operacion: str
    tipo: str
    motivo: str
    nino_id: str
    id_recurso: str
    datos_cliente: dict[str, Any]
    datos_servidor: dict[str, Any]
    estado: str = Field(description="PENDIENTE o RESUELTO")
    resolucion: str | None = Field(description="CONSERVAR_SERVIDOR, APLICAR_CLIENTE o DESCARTAR")
    registrado_por: str
    creado_en: datetime
    resuelto_en: datetime | None
    resuelto_por: str | None


class ResolucionEntrada(BaseModel):
    resolucion: str = Field(description="CONSERVAR_SERVIDOR, APLICAR_CLIENTE o DESCARTAR")


# --- INC-4: barreras (HIST-4.3 y HIST-4.4) --------------------------------------------------------------------------


class BarreraEntrada(BaseModel):
    tipo: str = Field(
        description="TRANSPORTE, ECONOMICA, OLVIDO, TRABAJO_CUIDADOR, DISTANCIA_CLIMA, EFECTOS_ADVERSOS_SUPLEMENTO, "
        "RECHAZO_TRATAMIENTO u OTRA (con OTRA el detalle es obligatorio)"
    )
    detalle: str | None = Field(default=None, description="Hasta 200 caracteres")
    fuente: str = Field(default="PERSONAL", description="PERSONAL, RESPUESTA_RECORDATORIO, INASISTENCIA o VISITA")
    fecha: date | None = Field(default=None, description="Por defecto hoy; no puede ser futura")


class BarreraSalida(BaseModel):
    id: str
    nino_id: str
    tipo: str
    detalle: str | None
    fuente: str
    fecha: date
    recordatorio_id: str | None
    registrado_por: str
    creado_en: datetime


class RazonBarreraSalida(BaseModel):
    codigo: str = Field(description="BARRERA_GRAVE, BARRERAS_RECURRENTES o ANEMIA_CONTROL_VENCIDO")
    descripcion: str


class AlertaBarreraNino(BaseModel):
    id: str
    dni: str | None
    codigo_origen: str | None
    nombre_completo: str
    comunidad: str
    establecimiento: str
    tutor_celular: str | None


class AlertaBarreraSalida(BaseModel):
    nino: AlertaBarreraNino
    prioridad: str = Field(description="ALTA (barrera grave o dos o más razones) o MEDIA")
    razones: list[RazonBarreraSalida]
    ultima_clasificacion: str | None
    dias_control_vencido: int
    barreras: list[BarreraSalida] = Field(
        description="Barreras vigentes que sustentan la alerta, la más reciente primero"
    )


# --- INC-4: recordatorios y respuesta del tutor (HIST-4.1 y HIST-4.2) ------------------------------------------------


class GenerarRecordatoriosEntrada(BaseModel):
    establecimiento: str | None = Field(default=None, description="Limita el lote a un establecimiento")


class RecordatorioNino(BaseModel):
    id: str
    nombre_completo: str
    codigo_origen: str | None
    comunidad: str
    establecimiento: str


class RecordatorioSalida(BaseModel):
    id: str
    nino: RecordatorioNino
    codigo_control: str
    fecha_programada: date
    tipo: str = Field(description="PROXIMO, CITA_DEL_DIA o VENCIDO")
    canal: str = Field(description="SIMULADO, WHATSAPP o SMS")
    simulado: bool = Field(description="True si no salió ningún mensaje real (notificador simulado)")
    estado: str = Field(description="ENVIADO_SIMULADO, ENVIADO, ENTREGADO, LEIDO o FALLIDO")
    destino: str = Field(description="Celular del tutor enmascarado")
    mensaje: str
    detalle: str | None = Field(description="Motivo de la falla o aviso de que el respaldo SMS reemplazó a WhatsApp")
    intentos: int
    creado_en: datetime
    enviado_en: datetime | None
    respuesta: str | None = Field(description="CONFIRMA, NO_PUEDE o REPROGRAMAR")
    fecha_reprogramada: date | None
    respondido_en: datetime | None
    respondido_por: str | None
    origen_respuesta: str | None = Field(description="PERSONAL o WHATSAPP")


class GeneracionSalida(BaseModel):
    fecha: date
    candidatos: int = Field(description="Controles que correspondía recordar hoy")
    enviados: int
    fallidos: int
    omitidos_sin_contacto: int = Field(description="Sin celular del tutor (incluye los niños del dataset)")
    omitidos_ya_enviado: int = Field(description="Ya tenían un recordatorio del mismo tipo para ese control")
    recordatorios: list[RecordatorioSalida] = Field(description="Los recordatorios enviados o fallidos en este lote")


class BarreraDeRespuestaEntrada(BaseModel):
    tipo: str
    detalle: str | None = None


class RespuestaEntrada(BaseModel):
    respuesta: str = Field(description="CONFIRMA, NO_PUEDE o REPROGRAMAR")
    fecha_reprogramada: date | None = Field(default=None, description="Obligatoria con REPROGRAMAR; hasta 90 días")
    barrera: BarreraDeRespuestaEntrada | None = Field(
        default=None, description="Solo con NO_PUEDE: registra la barrera junto con la respuesta"
    )


class RespuestaSalida(BaseModel):
    recordatorio: RecordatorioSalida
    barrera_id: str | None = Field(description="Barrera registrada junto con la respuesta NO_PUEDE")
    barrera_sugerida: bool = Field(description="NO_PUEDE sin barrera: conviene registrar el motivo")


class MetricasCanalSalida(BaseModel):
    canal: str
    total: int
    enviados: int
    fallidos: int
    entregados: int
    leidos: int
    confirmados: int
    tasa_entrega: float | None
    tasa_confirmacion: float | None


class MetricasRecordatoriosSalida(BaseModel):
    total: int
    enviados: int = Field(description="El canal aceptó el mensaje (todo menos FALLIDO, con los simulados)")
    fallidos: int
    simulados: int
    entregados: int = Field(description="ENTREGADO o LEIDO")
    leidos: int
    con_respuesta: int
    confirmados: int
    no_pueden: int
    reprogramados: int
    tasa_envio: float | None = Field(description="enviados / total (proporción de 0 a 1)")
    tasa_entrega: float | None = Field(description="entregados / enviados reales, sin los simulados")
    tasa_respuesta: float | None
    tasa_confirmacion: float | None = Field(description="confirmados / enviados")
    por_canal: list[MetricasCanalSalida]


class ResumenWebhookSalida(BaseModel):
    estados_aplicados: int
    respuestas_registradas: int
    ignorados: int
