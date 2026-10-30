"""Adaptador de persistencia relacional (PostgreSQL en staging/producción, SQLite en desarrollo)."""

from collections import defaultdict
from datetime import UTC, date, datetime
from pathlib import Path

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    delete,
    func,
    insert,
    inspect,
    or_,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.domain.model.asistencia import AsistenciaControl, EstadoAsistencia
from app.domain.model.barrera import Barrera, FuenteBarrera, TipoBarrera
from app.domain.model.clasificacion import Clasificacion
from app.domain.model.entidades import Evaluacion, Nino
from app.domain.model.errores import (
    ConflictoAsistencia,
    ConflictoBarrera,
    ConflictoRecordatorio,
    ConflictoVisita,
    RegistroDuplicado,
)
from app.domain.model.notificacion import (
    CanalEnvio,
    EstadoRecordatorio,
    OrigenRespuesta,
    Recordatorio,
    RespuestaTutor,
    TipoRecordatorio,
)
from app.domain.model.origen import OrigenDatos
from app.domain.model.sincronizacion import (
    ConflictoSincronizacion,
    EstadoConflicto,
    OperacionSincronizada,
    ResolucionConflicto,
    ResultadoOperacion,
)
from app.domain.model.tiempo import limites_utc
from app.domain.model.visita import ConsumoSuplemento, ResultadoVisita, VisitaDomiciliaria
from app.ports.outbound.repositorio_barreras import RepositorioBarreras
from app.ports.outbound.repositorio_ninos import RepositorioNinos
from app.ports.outbound.repositorio_recordatorios import RepositorioRecordatorios
from app.ports.outbound.repositorio_sincronizacion import RepositorioSincronizacion
from app.ports.outbound.repositorio_visitas import RepositorioVisitas


class Base(DeclarativeBase):
    pass


class NinoORM(Base):
    __tablename__ = "nino"
    __table_args__ = (
        CheckConstraint("origen IN ('SISTEMA', 'DATASET_DIRESA_JUNIN')", name="ck_nino_origen"),
        # Solo los registros del sistema exigen los datos personales; los del dataset son seudónimos (ADR-009).
        CheckConstraint(
            "origen <> 'SISTEMA' OR (dni IS NOT NULL AND nombres IS NOT NULL AND apellidos IS NOT NULL "
            "AND sexo IS NOT NULL AND tutor_nombre IS NOT NULL)",
            name="ck_nino_sistema_completo",
        ),
        CheckConstraint("origen <> 'DATASET_DIRESA_JUNIN' OR codigo_origen IS NOT NULL", name="ck_nino_dataset_codigo"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dni: Mapped[str | None] = mapped_column(String(8), unique=True, index=True, nullable=True)
    nombres: Mapped[str | None] = mapped_column(String(80), nullable=True)
    apellidos: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sexo: Mapped[str | None] = mapped_column(String(1), nullable=True)
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    establecimiento: Mapped[str] = mapped_column(String(120))
    distrito: Mapped[str] = mapped_column(String(80))
    comunidad: Mapped[str] = mapped_column(String(80), index=True)
    altitud_m: Mapped[float] = mapped_column(Float)
    tutor_nombre: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tutor_celular: Mapped[str | None] = mapped_column(String(9), nullable=True)
    estado: Mapped[str] = mapped_column(String(10), default="ACTIVO", index=True)
    origen: Mapped[str] = mapped_column(String(24), default="SISTEMA", server_default="SISTEMA", index=True)
    codigo_origen: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    red: Mapped[str | None] = mapped_column(String(80), nullable=True)
    microred: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provincia: Mapped[str | None] = mapped_column(String(80), nullable=True)
    registrado_por: Mapped[str] = mapped_column(String(60))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    evaluaciones: Mapped[list["EvaluacionORM"]] = relationship(back_populates="nino", cascade="all, delete-orphan")
    asistencias: Mapped[list["AsistenciaORM"]] = relationship(back_populates="nino", cascade="all, delete-orphan")


class EvaluacionORM(Base):
    __tablename__ = "evaluacion_hemoglobina"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nino_id: Mapped[str] = mapped_column(ForeignKey("nino.id", ondelete="CASCADE"), index=True)
    fecha: Mapped[date] = mapped_column(Date, index=True)
    edad_meses: Mapped[int] = mapped_column(Integer)
    hemoglobina_observada: Mapped[float] = mapped_column(Float)
    altitud_m: Mapped[float] = mapped_column(Float)
    hemoglobina_ajustada: Mapped[float] = mapped_column(Float)
    clasificacion: Mapped[str] = mapped_column(String(12))
    clasificacion_origen: Mapped[str | None] = mapped_column(String(12), nullable=True)
    peso_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    talla_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    registrado_por: Mapped[str] = mapped_column(String(60))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    nino: Mapped[NinoORM] = relationship(back_populates="evaluaciones")


class AsistenciaORM(Base):
    __tablename__ = "asistencia_control"
    __table_args__ = (
        UniqueConstraint("nino_id", "codigo_control", "fecha_programada", name="uq_asistencia_control"),
        CheckConstraint("estado IN ('ASISTIO', 'NO_ASISTIO')", name="ck_asistencia_estado"),
        CheckConstraint("estado = 'ASISTIO' OR motivo IS NOT NULL", name="ck_asistencia_motivo"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nino_id: Mapped[str] = mapped_column(ForeignKey("nino.id", ondelete="CASCADE"), index=True)
    codigo_control: Mapped[str] = mapped_column(String(10))
    fecha_programada: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(12))
    motivo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    evaluacion_id: Mapped[str | None] = mapped_column(
        ForeignKey("evaluacion_hemoglobina.id", ondelete="SET NULL"), nullable=True
    )
    registrado_por: Mapped[str] = mapped_column(String(60))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    nino: Mapped[NinoORM] = relationship(back_populates="asistencias")


class VisitaORM(Base):
    """VIS-3.5 (ADR-013): a lo sumo una visita domiciliaria por niño y por día."""

    __tablename__ = "visita_domiciliaria"
    __table_args__ = (
        UniqueConstraint("nino_id", "fecha", name="uq_visita_nino_fecha"),
        CheckConstraint("resultado IN ('REALIZADA', 'NO_ENCONTRADO', 'RECHAZADA')", name="ck_visita_resultado"),
        CheckConstraint("consume_suplemento IN ('SI', 'NO', 'DESCONOCIDO')", name="ck_visita_consumo"),
        CheckConstraint("resultado = 'REALIZADA' OR consume_suplemento = 'DESCONOCIDO'", name="ck_visita_suplemento"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nino_id: Mapped[str] = mapped_column(ForeignKey("nino.id", ondelete="CASCADE"), index=True)
    fecha: Mapped[date] = mapped_column(Date)
    resultado: Mapped[str] = mapped_column(String(14))
    consume_suplemento: Mapped[str] = mapped_column(String(12))
    observaciones: Mapped[str | None] = mapped_column(String(500), nullable=True)
    registrado_por: Mapped[str] = mapped_column(String(60))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class OperacionSincronizadaORM(Base):
    """HIST-3.2 (ADR-012): bitácora de operaciones ya procesadas; su clave primaria da la idempotencia."""

    __tablename__ = "operacion_sincronizada"
    __table_args__ = (
        CheckConstraint(
            "resultado IN ('APLICADA', 'DUPLICADA', 'CONFLICTO', 'RESUELTA')", name="ck_operacion_resultado"
        ),
        Index("ix_operacion_cliente", "id_dispositivo", "id_cliente"),
    )
    id_operacion: Mapped[str] = mapped_column(String(36), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(24))
    id_dispositivo: Mapped[str] = mapped_column(String(60))
    resultado: Mapped[str] = mapped_column(String(12))
    id_recurso: Mapped[str | None] = mapped_column(String(36), nullable=True)
    id_cliente: Mapped[str | None] = mapped_column(String(60), nullable=True)
    fecha_local: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recibida_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ConflictoORM(Base):
    """HIST-3.3: operación que chocó con un dato distinto del servidor, a la espera de una decisión."""

    __tablename__ = "conflicto_sincronizacion"
    __table_args__ = (
        CheckConstraint("estado IN ('PENDIENTE', 'RESUELTO')", name="ck_conflicto_estado"),
        CheckConstraint(
            "resolucion IS NULL OR resolucion IN ('CONSERVAR_SERVIDOR', 'APLICAR_CLIENTE', 'DESCARTAR')",
            name="ck_conflicto_resolucion",
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id_operacion: Mapped[str] = mapped_column(
        ForeignKey("operacion_sincronizada.id_operacion", ondelete="CASCADE"), unique=True
    )
    tipo: Mapped[str] = mapped_column(String(24))
    motivo: Mapped[str] = mapped_column(String(400))
    nino_id: Mapped[str] = mapped_column(ForeignKey("nino.id", ondelete="CASCADE"), index=True)
    id_recurso: Mapped[str] = mapped_column(String(36))
    datos_cliente: Mapped[dict] = mapped_column(JSON)
    datos_servidor: Mapped[dict] = mapped_column(JSON)
    estado: Mapped[str] = mapped_column(String(10), default="PENDIENTE", index=True)
    resolucion: Mapped[str | None] = mapped_column(String(20), nullable=True)
    registrado_por: Mapped[str] = mapped_column(String(60))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resuelto_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resuelto_por: Mapped[str | None] = mapped_column(String(60), nullable=True)


class RecordatorioORM(Base):
    """HIST-4.1 y HIST-4.2 (ADR-014): un recordatorio por niño, control (código y fecha programada) y tipo."""

    __tablename__ = "recordatorio"
    __table_args__ = (
        UniqueConstraint("nino_id", "codigo_control", "fecha_programada", "tipo", name="uq_recordatorio_control_tipo"),
        CheckConstraint("tipo IN ('PROXIMO', 'CITA_DEL_DIA', 'VENCIDO')", name="ck_recordatorio_tipo"),
        CheckConstraint("canal IN ('SIMULADO', 'WHATSAPP', 'SMS')", name="ck_recordatorio_canal"),
        CheckConstraint(
            "estado IN ('ENVIADO_SIMULADO', 'ENVIADO', 'ENTREGADO', 'LEIDO', 'FALLIDO')", name="ck_recordatorio_estado"
        ),
        CheckConstraint(
            "respuesta IS NULL OR respuesta IN ('CONFIRMA', 'NO_PUEDE', 'REPROGRAMAR')",
            name="ck_recordatorio_respuesta",
        ),
        CheckConstraint(
            "origen_respuesta IS NULL OR origen_respuesta IN ('PERSONAL', 'WHATSAPP')", name="ck_recordatorio_origen"
        ),
        CheckConstraint("respuesta IS NULL OR respondido_en IS NOT NULL", name="ck_recordatorio_respondido"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nino_id: Mapped[str] = mapped_column(ForeignKey("nino.id", ondelete="CASCADE"), index=True)
    codigo_control: Mapped[str] = mapped_column(String(10))
    fecha_programada: Mapped[date] = mapped_column(Date)
    tipo: Mapped[str] = mapped_column(String(12))
    canal: Mapped[str] = mapped_column(String(10))
    estado: Mapped[str] = mapped_column(String(16), index=True)
    destino: Mapped[str] = mapped_column(String(9), index=True)
    mensaje: Mapped[str] = mapped_column(String(500))
    id_externo: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    detalle: Mapped[str | None] = mapped_column(String(300), nullable=True)
    intentos: Mapped[int] = mapped_column(Integer, default=1)
    generado_por: Mapped[str] = mapped_column(String(60))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    enviado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    respuesta: Mapped[str | None] = mapped_column(String(12), nullable=True)
    fecha_reprogramada: Mapped[date | None] = mapped_column(Date, nullable=True)
    respondido_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    respondido_por: Mapped[str | None] = mapped_column(String(60), nullable=True)
    origen_respuesta: Mapped[str | None] = mapped_column(String(10), nullable=True)


class BarreraORM(Base):
    """HIST-4.3 (ADR-014): obstáculo para cumplir el tratamiento; no se repite (niño, tipo, fecha, fuente)."""

    __tablename__ = "barrera"
    __table_args__ = (
        UniqueConstraint("nino_id", "tipo", "fecha", "fuente", name="uq_barrera_nino_tipo_fecha_fuente"),
        CheckConstraint(
            "tipo IN ('TRANSPORTE', 'ECONOMICA', 'OLVIDO', 'TRABAJO_CUIDADOR', 'DISTANCIA_CLIMA', "
            "'EFECTOS_ADVERSOS_SUPLEMENTO', 'RECHAZO_TRATAMIENTO', 'OTRA')",
            name="ck_barrera_tipo",
        ),
        CheckConstraint(
            "fuente IN ('PERSONAL', 'RESPUESTA_RECORDATORIO', 'INASISTENCIA', 'VISITA')", name="ck_barrera_fuente"
        ),
        CheckConstraint("tipo <> 'OTRA' OR detalle IS NOT NULL", name="ck_barrera_otra_detalle"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nino_id: Mapped[str] = mapped_column(ForeignKey("nino.id", ondelete="CASCADE"), index=True)
    tipo: Mapped[str] = mapped_column(String(30))
    detalle: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fuente: Mapped[str] = mapped_column(String(24))
    fecha: Mapped[date] = mapped_column(Date, index=True)
    recordatorio_id: Mapped[str | None] = mapped_column(
        ForeignKey("recordatorio.id", ondelete="SET NULL"), nullable=True
    )
    registrado_por: Mapped[str] = mapped_column(String(60))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))


_NINO = NinoORM.__table__
_EVAL = EvaluacionORM.__table__
_ASIST = AsistenciaORM.__table__
_VISITA = VisitaORM.__table__
_OPERACION = OperacionSincronizadaORM.__table__
_CONFLICTO = ConflictoORM.__table__
_RECORDATORIO = RecordatorioORM.__table__
_BARRERA = BarreraORM.__table__


def _patron_contiene(texto: str) -> str:
    """Patrón LIKE «contiene» con los comodines del usuario escapados: «%» y «_» se buscan como texto (DEF-07)."""
    literal = texto.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{literal}%"


def _utc(valor: datetime) -> datetime:
    return valor if valor.tzinfo else valor.replace(tzinfo=UTC)


def _a_evaluacion(r) -> Evaluacion:
    return Evaluacion(
        id=r.id,
        nino_id=r.nino_id,
        fecha=r.fecha,
        edad_meses=r.edad_meses,
        hemoglobina_observada=r.hemoglobina_observada,
        altitud_m=r.altitud_m,
        hemoglobina_ajustada=r.hemoglobina_ajustada,
        clasificacion=Clasificacion(r.clasificacion),
        clasificacion_origen=r.clasificacion_origen,
        peso_kg=r.peso_kg,
        talla_cm=r.talla_cm,
        registrado_por=r.registrado_por,
        creado_en=_utc(r.creado_en),
    )


def _a_asistencia(r) -> AsistenciaControl:
    return AsistenciaControl(
        id=r.id,
        nino_id=r.nino_id,
        codigo_control=r.codigo_control,
        fecha_programada=r.fecha_programada,
        estado=EstadoAsistencia(r.estado),
        motivo=r.motivo,
        evaluacion_id=r.evaluacion_id,
        registrado_por=r.registrado_por,
        creado_en=_utc(r.creado_en),
    )


def _a_visita(r) -> VisitaDomiciliaria:
    return VisitaDomiciliaria(
        id=r.id,
        nino_id=r.nino_id,
        fecha=r.fecha,
        resultado=ResultadoVisita(r.resultado),
        consume_suplemento=ConsumoSuplemento(r.consume_suplemento),
        observaciones=r.observaciones,
        registrado_por=r.registrado_por,
        creado_en=_utc(r.creado_en),
    )


def _a_operacion(r) -> OperacionSincronizada:
    return OperacionSincronizada(
        id_operacion=r.id_operacion,
        tipo=r.tipo,
        id_dispositivo=r.id_dispositivo,
        resultado=ResultadoOperacion(r.resultado),
        id_recurso=r.id_recurso,
        id_cliente=r.id_cliente,
        fecha_local=_utc(r.fecha_local) if r.fecha_local else None,
        recibida_en=_utc(r.recibida_en),
    )


def _a_conflicto(r) -> ConflictoSincronizacion:
    return ConflictoSincronizacion(
        id=r.id,
        id_operacion=r.id_operacion,
        tipo=r.tipo,
        motivo=r.motivo,
        nino_id=r.nino_id,
        id_recurso=r.id_recurso,
        datos_cliente=r.datos_cliente,
        datos_servidor=r.datos_servidor,
        estado=EstadoConflicto(r.estado),
        resolucion=ResolucionConflicto(r.resolucion) if r.resolucion else None,
        registrado_por=r.registrado_por,
        creado_en=_utc(r.creado_en),
        resuelto_en=_utc(r.resuelto_en) if r.resuelto_en else None,
        resuelto_por=r.resuelto_por,
    )


def _a_recordatorio(r) -> Recordatorio:
    return Recordatorio(
        id=r.id,
        nino_id=r.nino_id,
        codigo_control=r.codigo_control,
        fecha_programada=r.fecha_programada,
        tipo=TipoRecordatorio(r.tipo),
        canal=CanalEnvio(r.canal),
        estado=EstadoRecordatorio(r.estado),
        destino=r.destino,
        mensaje=r.mensaje,
        id_externo=r.id_externo,
        detalle=r.detalle,
        intentos=r.intentos,
        generado_por=r.generado_por,
        creado_en=_utc(r.creado_en),
        enviado_en=_utc(r.enviado_en) if r.enviado_en else None,
        actualizado_en=_utc(r.actualizado_en),
        respuesta=RespuestaTutor(r.respuesta) if r.respuesta else None,
        fecha_reprogramada=r.fecha_reprogramada,
        respondido_en=_utc(r.respondido_en) if r.respondido_en else None,
        respondido_por=r.respondido_por,
        origen_respuesta=OrigenRespuesta(r.origen_respuesta) if r.origen_respuesta else None,
    )


def _fila_recordatorio(r: Recordatorio) -> dict:
    return {
        "id": r.id,
        "nino_id": r.nino_id,
        "codigo_control": r.codigo_control,
        "fecha_programada": r.fecha_programada,
        "tipo": r.tipo.value,
        "canal": r.canal.value,
        "estado": r.estado.value,
        "destino": r.destino,
        "mensaje": r.mensaje,
        "id_externo": r.id_externo,
        "detalle": r.detalle[:300] if r.detalle else None,
        "intentos": r.intentos,
        "generado_por": r.generado_por,
        "creado_en": r.creado_en,
        "enviado_en": r.enviado_en,
        "actualizado_en": r.actualizado_en,
        "respuesta": r.respuesta.value if r.respuesta else None,
        "fecha_reprogramada": r.fecha_reprogramada,
        "respondido_en": r.respondido_en,
        "respondido_por": r.respondido_por,
        "origen_respuesta": r.origen_respuesta.value if r.origen_respuesta else None,
    }


def _a_barrera(r) -> Barrera:
    return Barrera(
        id=r.id,
        nino_id=r.nino_id,
        tipo=TipoBarrera(r.tipo),
        detalle=r.detalle,
        fuente=FuenteBarrera(r.fuente),
        fecha=r.fecha,
        recordatorio_id=r.recordatorio_id,
        registrado_por=r.registrado_por,
        creado_en=_utc(r.creado_en),
    )


def _a_nino(
    r, evaluaciones: list[Evaluacion] | None = None, asistencias: list[AsistenciaControl] | None = None
) -> Nino:
    return Nino(
        id=r.id,
        dni=r.dni,
        nombres=r.nombres,
        apellidos=r.apellidos,
        sexo=r.sexo,
        fecha_nacimiento=r.fecha_nacimiento,
        establecimiento=r.establecimiento,
        distrito=r.distrito,
        comunidad=r.comunidad,
        altitud_m=r.altitud_m,
        tutor_nombre=r.tutor_nombre,
        tutor_celular=r.tutor_celular,
        estado=r.estado,
        origen=OrigenDatos(r.origen),
        codigo_origen=r.codigo_origen,
        red=r.red,
        microred=r.microred,
        provincia=r.provincia,
        registrado_por=r.registrado_por,
        creado_en=_utc(r.creado_en),
        actualizado_en=_utc(r.actualizado_en),
        evaluaciones=evaluaciones or [],
        asistencias=asistencias or [],
    )


CAMPOS_NINO = (
    "dni",
    "nombres",
    "apellidos",
    "sexo",
    "fecha_nacimiento",
    "establecimiento",
    "distrito",
    "comunidad",
    "altitud_m",
    "tutor_nombre",
    "tutor_celular",
    "estado",
    "codigo_origen",
    "red",
    "microred",
    "provincia",
    "registrado_por",
    "creado_en",
    "actualizado_en",
)

CAMPOS_EVALUACION = (
    "id",
    "nino_id",
    "fecha",
    "edad_meses",
    "hemoglobina_observada",
    "altitud_m",
    "hemoglobina_ajustada",
    "clasificacion_origen",
    "peso_kg",
    "talla_cm",
    "registrado_por",
    "creado_en",
)


def _fila_nino(nino: Nino) -> dict:
    return {"id": nino.id, "origen": nino.origen.value, **{c: getattr(nino, c) for c in CAMPOS_NINO}}


def _fila_evaluacion(e: Evaluacion) -> dict:
    return {**{c: getattr(e, c) for c in CAMPOS_EVALUACION}, "clasificacion": e.clasificacion.value}


class RepositorioSQLAlchemy(
    RepositorioNinos, RepositorioVisitas, RepositorioSincronizacion, RepositorioRecordatorios, RepositorioBarreras
):
    def __init__(self, url: str):
        argumentos = {"check_same_thread": False} if url.startswith("sqlite") else {}
        if url.startswith("sqlite:///") and ":memory:" not in url:
            Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(url, connect_args=argumentos, pool_pre_ping=True)
        self.Sesion = sessionmaker(self.engine, expire_on_commit=False)

    def crear_esquema(self) -> None:
        inspector = inspect(self.engine)
        if inspector.has_table("nino") and "origen" not in {c["name"] for c in inspector.get_columns("nino")}:
            raise RuntimeError(
                "La base de datos tiene el esquema de la versión 1.x. En PostgreSQL aplique "
                "db/02_migracion_v2_0.sql; en una base SQLite de desarrollo, bórrela y vuelva a crearla."
            )
        Base.metadata.create_all(self.engine)

    def guardar(self, nino: Nino) -> Nino:
        try:
            with self.Sesion.begin() as s:
                s.execute(insert(_NINO).values(**_fila_nino(nino)))
        except IntegrityError:
            # Dos solicitudes simultáneas con el mismo DNI pasan la comprobación previa del caso de uso; la restricción
            # UNIQUE de la base rechaza la segunda y se traduce al error de dominio (409), no a un 500 (DEF-08).
            if nino.dni and self.obtener_por_dni(nino.dni):
                raise RegistroDuplicado(f"Ya existe un niño registrado con DNI {nino.dni}.") from None
            raise
        return nino

    def guardar_varios(self, ninos: list[Nino]) -> int:
        if not ninos:
            return 0
        with self.Sesion.begin() as s:
            s.execute(insert(_NINO), [_fila_nino(n) for n in ninos])
            evaluaciones = [_fila_evaluacion(e) for n in ninos for e in n.evaluaciones]
            if evaluaciones:
                s.execute(insert(_EVAL), evaluaciones)
        return len(ninos)

    def contar_por_origen(self, origen: str) -> int:
        with self.Sesion() as s:
            return s.scalar(select(func.count(_NINO.c.id)).where(_NINO.c.origen == str(origen)))

    def eliminar_por_origen(self, origen: str) -> int:
        ids = select(_NINO.c.id).where(_NINO.c.origen == str(origen))
        with self.Sesion.begin() as s:
            s.execute(delete(_BARRERA).where(_BARRERA.c.nino_id.in_(ids)))
            s.execute(delete(_RECORDATORIO).where(_RECORDATORIO.c.nino_id.in_(ids)))
            s.execute(delete(_CONFLICTO).where(_CONFLICTO.c.nino_id.in_(ids)))
            s.execute(delete(_VISITA).where(_VISITA.c.nino_id.in_(ids)))
            s.execute(delete(_ASIST).where(_ASIST.c.nino_id.in_(ids)))
            s.execute(delete(_EVAL).where(_EVAL.c.nino_id.in_(ids)))
            return s.execute(delete(_NINO).where(_NINO.c.origen == str(origen))).rowcount

    def actualizar(self, nino: Nino) -> Nino:
        with self.Sesion.begin() as s:
            o = s.get(NinoORM, nino.id)
            for c in CAMPOS_NINO:
                setattr(o, c, getattr(nino, c))
        return nino

    def agregar_evaluacion(self, e: Evaluacion) -> Evaluacion:
        with self.Sesion.begin() as s:
            s.execute(insert(_EVAL).values(**_fila_evaluacion(e)))
        return e

    def agregar_asistencia(self, a: AsistenciaControl) -> AsistenciaControl:
        fila = {
            "id": a.id,
            "nino_id": a.nino_id,
            "codigo_control": a.codigo_control,
            "fecha_programada": a.fecha_programada,
            "estado": a.estado.value,
            "motivo": a.motivo,
            "evaluacion_id": a.evaluacion_id,
            "registrado_por": a.registrado_por,
            "creado_en": a.creado_en,
        }
        try:
            with self.Sesion.begin() as s:
                s.execute(insert(_ASIST).values(**fila))
        except IntegrityError:
            # Dos solicitudes simultáneas pasan la comprobación previa; la restricción UNIQUE rechaza la segunda (409).
            with self.Sesion() as s:
                existe = s.scalar(
                    select(func.count(_ASIST.c.id)).where(
                        _ASIST.c.nino_id == a.nino_id,
                        _ASIST.c.codigo_control == a.codigo_control,
                        _ASIST.c.fecha_programada == a.fecha_programada,
                    )
                )
            if existe:
                raise ConflictoAsistencia(
                    f"El control {a.codigo_control} del {a.fecha_programada.isoformat()} ya tiene una asistencia."
                ) from None
            raise
        return a

    def actualizar_evaluacion(self, e: Evaluacion) -> Evaluacion:
        valores = {c: getattr(e, c) for c in CAMPOS_EVALUACION if c not in ("id", "nino_id", "creado_en")}
        with self.Sesion.begin() as s:
            s.execute(update(_EVAL).where(_EVAL.c.id == e.id).values(**valores, clasificacion=e.clasificacion.value))
        return e

    def actualizar_asistencia(self, a: AsistenciaControl) -> AsistenciaControl:
        with self.Sesion.begin() as s:
            s.execute(
                update(_ASIST)
                .where(_ASIST.c.id == a.id)
                .values(estado=a.estado.value, motivo=a.motivo, registrado_por=a.registrado_por)
            )
        return a

    # --- Visitas domiciliarias (VIS-3.5) ----------------------------------------------------------------------------
    def agregar_visita(self, v: VisitaDomiciliaria) -> VisitaDomiciliaria:
        fila = {
            "id": v.id,
            "nino_id": v.nino_id,
            "fecha": v.fecha,
            "resultado": v.resultado.value,
            "consume_suplemento": v.consume_suplemento.value,
            "observaciones": v.observaciones,
            "registrado_por": v.registrado_por,
            "creado_en": v.creado_en,
        }
        try:
            with self.Sesion.begin() as s:
                s.execute(insert(_VISITA).values(**fila))
        except IntegrityError:
            # Dos solicitudes simultáneas pasan la comprobación previa; la restricción UNIQUE rechaza la segunda (409).
            if self.obtener_visita_del_dia(v.nino_id, v.fecha):
                raise ConflictoVisita(f"El niño ya tiene una visita registrada el {v.fecha.isoformat()}.") from None
            raise
        return v

    def actualizar_visita(self, v: VisitaDomiciliaria) -> VisitaDomiciliaria:
        with self.Sesion.begin() as s:
            s.execute(
                update(_VISITA)
                .where(_VISITA.c.id == v.id)
                .values(
                    resultado=v.resultado.value,
                    consume_suplemento=v.consume_suplemento.value,
                    observaciones=v.observaciones,
                    registrado_por=v.registrado_por,
                )
            )
        return v

    def obtener_visita_del_dia(self, nino_id: str, fecha: date) -> VisitaDomiciliaria | None:
        with self.Sesion() as s:
            r = s.execute(select(_VISITA).where(_VISITA.c.nino_id == nino_id, _VISITA.c.fecha == fecha)).first()
        return _a_visita(r) if r else None

    def listar_visitas(self, nino_id: str) -> list[VisitaDomiciliaria]:
        q = select(_VISITA).where(_VISITA.c.nino_id == nino_id).order_by(_VISITA.c.fecha.desc(), _VISITA.c.creado_en)
        with self.Sesion() as s:
            return [_a_visita(r) for r in s.execute(q)]

    def ultimas_visitas(self, nino_ids: set[str]) -> dict[str, date]:
        # Una sola consulta agrupada: la tabla de visitas es pequeña frente a la de niños y evita listas IN enormes.
        q = select(_VISITA.c.nino_id, func.max(_VISITA.c.fecha)).group_by(_VISITA.c.nino_id)
        with self.Sesion() as s:
            return {nino_id: fecha for nino_id, fecha in s.execute(q) if nino_id in nino_ids}

    # --- Sincronización (HIST-3.2, HIST-3.3) -------------------------------------------------------------------------
    def obtener_operacion(self, id_operacion: str) -> OperacionSincronizada | None:
        with self.Sesion() as s:
            r = s.execute(select(_OPERACION).where(_OPERACION.c.id_operacion == id_operacion)).first()
        return _a_operacion(r) if r else None

    def registrar_operacion(self, o: OperacionSincronizada) -> bool:
        fila = {
            "id_operacion": o.id_operacion,
            "tipo": o.tipo,
            "id_dispositivo": o.id_dispositivo,
            "resultado": o.resultado.value,
            "id_recurso": o.id_recurso,
            "id_cliente": o.id_cliente,
            "fecha_local": o.fecha_local,
            "recibida_en": o.recibida_en,
        }
        try:
            with self.Sesion.begin() as s:
                s.execute(insert(_OPERACION).values(**fila))
        except IntegrityError:
            if self.obtener_operacion(o.id_operacion):
                return False  # la restricción de clave primaria detuvo a la segunda de dos solicitudes simultáneas
            raise
        return True

    def marcar_operacion_resuelta(self, id_operacion: str) -> None:
        with self.Sesion.begin() as s:
            s.execute(
                update(_OPERACION)
                .where(_OPERACION.c.id_operacion == id_operacion)
                .values(resultado=ResultadoOperacion.RESUELTA.value)
            )

    def id_nino_de_cliente(self, id_dispositivo: str, id_cliente: str) -> str | None:
        q = select(_OPERACION.c.id_recurso).where(
            _OPERACION.c.id_dispositivo == id_dispositivo,
            _OPERACION.c.id_cliente == id_cliente,
            _OPERACION.c.resultado.in_(["APLICADA", "DUPLICADA", "RESUELTA"]),
        )
        with self.Sesion() as s:
            return s.scalar(q)

    def contar_operaciones(self) -> int:
        with self.Sesion() as s:
            return s.scalar(select(func.count()).select_from(_OPERACION))

    def guardar_conflicto(self, c: ConflictoSincronizacion) -> ConflictoSincronizacion:
        with self.Sesion.begin() as s:
            s.execute(insert(_CONFLICTO).values(**self._fila_conflicto(c)))
        return c

    @staticmethod
    def _fila_conflicto(c: ConflictoSincronizacion) -> dict:
        return {
            "id": c.id,
            "id_operacion": c.id_operacion,
            "tipo": c.tipo,
            "motivo": c.motivo[:400],
            "nino_id": c.nino_id,
            "id_recurso": c.id_recurso,
            "datos_cliente": c.datos_cliente,
            "datos_servidor": c.datos_servidor,
            "estado": c.estado.value,
            "resolucion": c.resolucion.value if c.resolucion else None,
            "registrado_por": c.registrado_por,
            "creado_en": c.creado_en,
            "resuelto_en": c.resuelto_en,
            "resuelto_por": c.resuelto_por,
        }

    def _conflictos(self, *condiciones) -> list[ConflictoSincronizacion]:
        q = select(_CONFLICTO).where(*condiciones).order_by(_CONFLICTO.c.creado_en, _CONFLICTO.c.id)
        with self.Sesion() as s:
            return [_a_conflicto(r) for r in s.execute(q)]

    def obtener_conflicto(self, conflicto_id: str) -> ConflictoSincronizacion | None:
        encontrados = self._conflictos(_CONFLICTO.c.id == conflicto_id)
        return encontrados[0] if encontrados else None

    def obtener_conflicto_de_operacion(self, id_operacion: str) -> ConflictoSincronizacion | None:
        encontrados = self._conflictos(_CONFLICTO.c.id_operacion == id_operacion)
        return encontrados[0] if encontrados else None

    def listar_conflictos(self, estado: str | None = None) -> list[ConflictoSincronizacion]:
        return self._conflictos(*([_CONFLICTO.c.estado == estado] if estado else []))

    def actualizar_conflicto(self, c: ConflictoSincronizacion) -> ConflictoSincronizacion:
        valores = self._fila_conflicto(c)
        with self.Sesion.begin() as s:
            s.execute(update(_CONFLICTO).where(_CONFLICTO.c.id == c.id).values(**valores))
        return c

    # --- Recordatorios (HIST-4.1, HIST-4.2) ---------------------------------------------------------------------------
    def agregar_recordatorio(self, r: Recordatorio) -> Recordatorio:
        try:
            with self.Sesion.begin() as s:
                s.execute(insert(_RECORDATORIO).values(**_fila_recordatorio(r)))
        except IntegrityError:
            # Dos generaciones simultáneas pasan la comprobación previa; la restricción UNIQUE rechaza la segunda.
            with self.Sesion() as s:
                existe = s.scalar(
                    select(func.count(_RECORDATORIO.c.id)).where(
                        _RECORDATORIO.c.nino_id == r.nino_id,
                        _RECORDATORIO.c.codigo_control == r.codigo_control,
                        _RECORDATORIO.c.fecha_programada == r.fecha_programada,
                        _RECORDATORIO.c.tipo == r.tipo.value,
                    )
                )
            if existe:
                raise ConflictoRecordatorio("Ya existe un recordatorio para ese control y tipo.") from None
            raise
        return r

    def actualizar_recordatorio(self, r: Recordatorio) -> Recordatorio:
        valores = {c: v for c, v in _fila_recordatorio(r).items() if c not in ("id", "nino_id", "creado_en")}
        with self.Sesion.begin() as s:
            s.execute(update(_RECORDATORIO).where(_RECORDATORIO.c.id == r.id).values(**valores))
        return r

    def _recordatorios(self, *condiciones, orden=None, limite: int | None = None) -> list[Recordatorio]:
        q = (
            select(_RECORDATORIO)
            .where(*condiciones)
            .order_by(*(orden or (_RECORDATORIO.c.creado_en.desc(), _RECORDATORIO.c.id)))
        )
        if limite:
            q = q.limit(limite)
        with self.Sesion() as s:
            return [_a_recordatorio(r) for r in s.execute(q)]

    def obtener_recordatorio(self, recordatorio_id: str) -> Recordatorio | None:
        encontrados = self._recordatorios(_RECORDATORIO.c.id == recordatorio_id)
        return encontrados[0] if encontrados else None

    def obtener_por_id_externo(self, id_externo: str) -> Recordatorio | None:
        encontrados = self._recordatorios(_RECORDATORIO.c.id_externo == id_externo, limite=1)
        return encontrados[0] if encontrados else None

    def buscar_para_respuesta(self, id_externo: str | None, destino: str | None) -> Recordatorio | None:
        if id_externo and (r := self.obtener_por_id_externo(id_externo)):
            return r
        if not destino:
            return None
        encontrados = self._recordatorios(
            _RECORDATORIO.c.destino == destino,
            _RECORDATORIO.c.canal == CanalEnvio.WHATSAPP.value,
            _RECORDATORIO.c.respuesta.is_(None),
            _RECORDATORIO.c.estado != EstadoRecordatorio.FALLIDO.value,
            limite=1,
        )
        return encontrados[0] if encontrados else None

    def listar_recordatorios(
        self,
        estado: str | None = None,
        desde: date | None = None,
        hasta: date | None = None,
        nino_id: str | None = None,
        limite: int | None = None,
    ) -> list[Recordatorio]:
        condiciones = []
        if estado:
            condiciones.append(_RECORDATORIO.c.estado == estado)
        if nino_id:
            condiciones.append(_RECORDATORIO.c.nino_id == nino_id)
        if desde:
            condiciones.append(_RECORDATORIO.c.creado_en >= limites_utc(desde, desde)[0])
        if hasta:
            condiciones.append(_RECORDATORIO.c.creado_en <= limites_utc(hasta, hasta)[1])
        return self._recordatorios(*condiciones, limite=limite)

    # --- Barreras (HIST-4.3) ------------------------------------------------------------------------------------------
    def agregar_barrera(self, b: Barrera) -> Barrera:
        fila = {
            "id": b.id,
            "nino_id": b.nino_id,
            "tipo": b.tipo.value,
            "detalle": b.detalle,
            "fuente": b.fuente.value,
            "fecha": b.fecha,
            "recordatorio_id": b.recordatorio_id,
            "registrado_por": b.registrado_por,
            "creado_en": b.creado_en,
        }
        try:
            with self.Sesion.begin() as s:
                s.execute(insert(_BARRERA).values(**fila))
        except IntegrityError:
            # Dos solicitudes simultáneas pasan la comprobación previa; la restricción UNIQUE rechaza la segunda (409).
            if previa := self.obtener_equivalente(b.nino_id, b.tipo.value, b.fecha, b.fuente.value):
                raise ConflictoBarrera("El niño ya tiene registrada esa barrera.", previa.id) from None
            raise
        return b

    def _barreras(self, *condiciones) -> list[Barrera]:
        q = (
            select(_BARRERA)
            .where(*condiciones)
            .order_by(_BARRERA.c.fecha.desc(), _BARRERA.c.creado_en.desc(), _BARRERA.c.id)
        )
        with self.Sesion() as s:
            return [_a_barrera(r) for r in s.execute(q)]

    def obtener_equivalente(self, nino_id: str, tipo: str, fecha: date, fuente: str) -> Barrera | None:
        encontradas = self._barreras(
            _BARRERA.c.nino_id == nino_id,
            _BARRERA.c.tipo == str(tipo),
            _BARRERA.c.fecha == fecha,
            _BARRERA.c.fuente == str(fuente),
        )
        return encontradas[0] if encontradas else None

    def listar_barreras(self, nino_id: str) -> list[Barrera]:
        return self._barreras(_BARRERA.c.nino_id == nino_id)

    def barreras_desde(self, desde: date) -> dict[str, list[Barrera]]:
        agrupadas: dict[str, list[Barrera]] = defaultdict(list)
        for b in self._barreras(_BARRERA.c.fecha >= desde):
            agrupadas[b.nino_id].append(b)
        return dict(agrupadas)

    def _cargar(self, condiciones: list) -> list[Nino]:
        """Niños que cumplen las condiciones con sus evaluaciones y asistencias, en tres consultas por lotes.

        Las filas se convierten directamente en objetos de dominio (sin instancias ORM): es el camino caliente del
        listado de seguimiento y de las alertas, que recorren todos los niños activos.
        """
        with self.Sesion() as s:
            filas = s.execute(select(_NINO).where(*condiciones)).all()
            evaluaciones: dict[str, list[Evaluacion]] = defaultdict(list)
            q_eval = select(_EVAL).join(_NINO, _EVAL.c.nino_id == _NINO.c.id).where(*condiciones)
            for r in s.execute(q_eval):
                evaluaciones[r.nino_id].append(_a_evaluacion(r))
            asistencias: dict[str, list[AsistenciaControl]] = defaultdict(list)
            q_asist = select(_ASIST).join(_NINO, _ASIST.c.nino_id == _NINO.c.id).where(*condiciones)
            for r in s.execute(q_asist):
                asistencias[r.nino_id].append(_a_asistencia(r))
        return [_a_nino(r, evaluaciones.get(r.id), asistencias.get(r.id)) for r in filas]

    def obtener(self, nino_id: str) -> Nino | None:
        ninos = self._cargar([_NINO.c.id == nino_id])
        return ninos[0] if ninos else None

    def obtener_por_dni(self, dni: str) -> Nino | None:
        ninos = self._cargar([_NINO.c.dni == dni])
        return ninos[0] if ninos else None

    def listar(self, estado: str | None = None, texto: str | None = None) -> list[Nino]:
        condiciones = []
        if estado:
            condiciones.append(_NINO.c.estado == estado)
        if texto:
            patron = _patron_contiene(texto)
            condiciones.append(
                or_(
                    _NINO.c.nombres.ilike(patron, escape="\\"),
                    _NINO.c.apellidos.ilike(patron, escape="\\"),
                    _NINO.c.dni.like(patron, escape="\\"),
                    _NINO.c.codigo_origen.ilike(patron, escape="\\"),
                    _NINO.c.comunidad.ilike(patron, escape="\\"),
                )
            )
        ninos = self._cargar(condiciones)
        ninos.sort(key=lambda n: (n.apellidos or n.codigo_origen or "").casefold())
        return ninos

    def evaluaciones_en_periodo(self, desde: date, hasta: date) -> list[Evaluacion]:
        q = select(_EVAL).where(_EVAL.c.fecha.between(desde, hasta)).order_by(_EVAL.c.fecha)
        with self.Sesion() as s:
            return [_a_evaluacion(r) for r in s.execute(q)]

    def contar_registrados_en_periodo(self, desde: date, hasta: date) -> int:
        # Los días del periodo son días calendario de Perú, no de UTC (DEF-02).
        inicio, fin = limites_utc(desde, hasta)
        q = select(func.count(_NINO.c.id)).where(_NINO.c.creado_en.between(inicio, fin))
        with self.Sesion() as s:
            return s.scalar(q)

    def obtener_varios(self, ids: set[str]) -> dict[str, Nino]:
        # Una sola consulta sin cargar evaluaciones: evita el patrón N+1 del reporte (DEF-01).
        if not ids:
            return {}
        with self.Sesion() as s:
            return {r.id: _a_nino(r) for r in s.execute(select(_NINO).where(_NINO.c.id.in_(ids)))}
