"""Adaptador de persistencia relacional (PostgreSQL en staging/producción, SQLite en desarrollo)."""

from datetime import UTC, date, datetime, time
from pathlib import Path

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
    or_,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload, sessionmaker

from app.domain.entidades import Evaluacion, Nino
from app.domain.reglas_clinicas import Clasificacion


class Base(DeclarativeBase):
    pass


class NinoORM(Base):
    __tablename__ = "nino"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dni: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    nombres: Mapped[str] = mapped_column(String(80))
    apellidos: Mapped[str] = mapped_column(String(80))
    sexo: Mapped[str] = mapped_column(String(1))
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    establecimiento: Mapped[str] = mapped_column(String(120))
    distrito: Mapped[str] = mapped_column(String(80))
    comunidad: Mapped[str] = mapped_column(String(80), index=True)
    altitud_m: Mapped[float] = mapped_column(Float)
    tutor_nombre: Mapped[str] = mapped_column(String(120))
    tutor_celular: Mapped[str | None] = mapped_column(String(9), nullable=True)
    estado: Mapped[str] = mapped_column(String(10), default="ACTIVO", index=True)
    registrado_por: Mapped[str] = mapped_column(String(60))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    evaluaciones: Mapped[list["EvaluacionORM"]] = relationship(back_populates="nino", cascade="all, delete-orphan")


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
    peso_kg: Mapped[float] = mapped_column(Float)
    talla_cm: Mapped[float] = mapped_column(Float)
    registrado_por: Mapped[str] = mapped_column(String(60))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    nino: Mapped[NinoORM] = relationship(back_populates="evaluaciones")


def _utc(valor: datetime) -> datetime:
    return valor if valor.tzinfo else valor.replace(tzinfo=UTC)


def _a_evaluacion(o: EvaluacionORM) -> Evaluacion:
    return Evaluacion(
        id=o.id,
        nino_id=o.nino_id,
        fecha=o.fecha,
        edad_meses=o.edad_meses,
        hemoglobina_observada=o.hemoglobina_observada,
        altitud_m=o.altitud_m,
        hemoglobina_ajustada=o.hemoglobina_ajustada,
        clasificacion=Clasificacion(o.clasificacion),
        peso_kg=o.peso_kg,
        talla_cm=o.talla_cm,
        registrado_por=o.registrado_por,
        creado_en=_utc(o.creado_en),
    )


def _a_nino(o: NinoORM) -> Nino:
    return Nino(
        id=o.id,
        dni=o.dni,
        nombres=o.nombres,
        apellidos=o.apellidos,
        sexo=o.sexo,
        fecha_nacimiento=o.fecha_nacimiento,
        establecimiento=o.establecimiento,
        distrito=o.distrito,
        comunidad=o.comunidad,
        altitud_m=o.altitud_m,
        tutor_nombre=o.tutor_nombre,
        tutor_celular=o.tutor_celular,
        estado=o.estado,
        registrado_por=o.registrado_por,
        creado_en=_utc(o.creado_en),
        actualizado_en=_utc(o.actualizado_en),
        evaluaciones=[_a_evaluacion(e) for e in o.evaluaciones],
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
    "registrado_por",
    "creado_en",
    "actualizado_en",
)


class RepositorioSQLAlchemy:
    def __init__(self, url: str):
        argumentos = {"check_same_thread": False} if url.startswith("sqlite") else {}
        if url.startswith("sqlite:///") and ":memory:" not in url:
            Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(url, connect_args=argumentos, pool_pre_ping=True)
        self.Sesion = sessionmaker(self.engine, expire_on_commit=False)

    def crear_esquema(self) -> None:
        Base.metadata.create_all(self.engine)

    def guardar(self, nino: Nino) -> Nino:
        with self.Sesion.begin() as s:
            s.add(NinoORM(id=nino.id, **{c: getattr(nino, c) for c in CAMPOS_NINO}))
        return nino

    def actualizar(self, nino: Nino) -> Nino:
        with self.Sesion.begin() as s:
            o = s.get(NinoORM, nino.id)
            for c in CAMPOS_NINO:
                setattr(o, c, getattr(nino, c))
        return nino

    def agregar_evaluacion(self, e: Evaluacion) -> Evaluacion:
        with self.Sesion.begin() as s:
            s.add(
                EvaluacionORM(
                    id=e.id,
                    nino_id=e.nino_id,
                    fecha=e.fecha,
                    edad_meses=e.edad_meses,
                    hemoglobina_observada=e.hemoglobina_observada,
                    altitud_m=e.altitud_m,
                    hemoglobina_ajustada=e.hemoglobina_ajustada,
                    clasificacion=e.clasificacion.value,
                    peso_kg=e.peso_kg,
                    talla_cm=e.talla_cm,
                    registrado_por=e.registrado_por,
                    creado_en=e.creado_en,
                )
            )
        return e

    def _consulta(self):
        return select(NinoORM).options(selectinload(NinoORM.evaluaciones))

    def obtener(self, nino_id: str) -> Nino | None:
        with self.Sesion() as s:
            o = s.scalars(self._consulta().where(NinoORM.id == nino_id)).first()
            return _a_nino(o) if o else None

    def obtener_por_dni(self, dni: str) -> Nino | None:
        with self.Sesion() as s:
            o = s.scalars(self._consulta().where(NinoORM.dni == dni)).first()
            return _a_nino(o) if o else None

    def listar(self, estado: str | None = None, texto: str | None = None) -> list[Nino]:
        q = self._consulta()
        if estado:
            q = q.where(NinoORM.estado == estado)
        if texto:
            patron = f"%{texto.lower()}%"
            q = q.where(
                or_(
                    NinoORM.nombres.ilike(patron),
                    NinoORM.apellidos.ilike(patron),
                    NinoORM.dni.like(patron),
                    NinoORM.comunidad.ilike(patron),
                )
            )
        with self.Sesion() as s:
            return [_a_nino(o) for o in s.scalars(q.order_by(NinoORM.apellidos))]

    def evaluaciones_en_periodo(self, desde: date, hasta: date) -> list[Evaluacion]:
        q = select(EvaluacionORM).where(EvaluacionORM.fecha.between(desde, hasta)).order_by(EvaluacionORM.fecha)
        with self.Sesion() as s:
            return [_a_evaluacion(o) for o in s.scalars(q)]

    def ninos_registrados_en_periodo(self, desde: date, hasta: date) -> list[Nino]:
        inicio = datetime.combine(desde, time.min, tzinfo=UTC)
        fin = datetime.combine(hasta, time.max, tzinfo=UTC)
        q = self._consulta().where(NinoORM.creado_en.between(inicio, fin))
        with self.Sesion() as s:
            return [_a_nino(o) for o in s.scalars(q)]
