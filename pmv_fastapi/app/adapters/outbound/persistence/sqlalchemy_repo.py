"""Adaptador de persistencia relacional (PostgreSQL en staging/producción, SQLite en desarrollo)."""

from collections import defaultdict
from datetime import UTC, date, datetime
from pathlib import Path

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
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
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.domain.model.asistencia import AsistenciaControl, EstadoAsistencia
from app.domain.model.clasificacion import Clasificacion
from app.domain.model.entidades import Evaluacion, Nino
from app.domain.model.errores import ConflictoAsistencia, RegistroDuplicado
from app.domain.model.origen import OrigenDatos
from app.domain.model.tiempo import limites_utc
from app.ports.outbound.repositorio_ninos import RepositorioNinos


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


_NINO = NinoORM.__table__
_EVAL = EvaluacionORM.__table__
_ASIST = AsistenciaORM.__table__


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


class RepositorioSQLAlchemy(RepositorioNinos):
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
