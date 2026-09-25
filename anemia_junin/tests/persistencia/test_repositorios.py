"""
Pruebas de persistencia — PMV Anemia Junín.

Verifican integridad, rollback y la restricción UNIQUE en el DNI.
Usan base de datos en memoria para aislamiento.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import date, datetime
from pathlib import Path

import pytest

from anemia_junin.adapters.outbound.sqlite.migraciones import migrar
from anemia_junin.adapters.outbound.sqlite.repositorios import (
    RepositorioDosajesSQLite,
)
from anemia_junin.adapters.outbound.sqlite.unidad_de_trabajo import UnidadDeTrabajo
from anemia_junin.domain.entities import (
    Clasificacion,
    Dosaje,
    IntentoRegistro,
    Nino,
    Sexo,
    TipoNacimiento,
)

# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def db_path(tmp_path: Path) -> str:
    ruta = str(tmp_path / "test.db")
    migrar(ruta)
    return ruta


def _nino_base(dni: str = "12345678") -> Nino:
    ahora = datetime(2026, 9, 25, 8, 0, 0)
    return Nino(
        id=uuid.uuid4(),
        dni=dni,
        nombres="Ana María",
        apellidos="Quispe López",
        fecha_nacimiento=date(2023, 3, 15),
        sexo=Sexo.F,
        tipo_nacimiento=TipoNacimiento.TERMINO,
        peso_g=8500,
        distrito="Huancayo",
        altitud_msnm=3271,
        cuidador="María López",
        telefono="987654321",
        created_at=ahora,
        updated_at=ahora,
    )


def _dosaje_base(nino_id: uuid.UUID) -> Dosaje:
    return Dosaje(
        id=uuid.uuid4(),
        nino_id=nino_id,
        fecha_dosaje=date(2026, 9, 25),
        hb_observada_ddl=105,
        altitud_msnm=3271,
        ajuste_ddl=21,
        hb_ajustada_ddl=84,
        edad_meses=42,
        clasificacion=Clasificacion.MODERADA,
        version_normativa="v1",
        advertencias=[],
        created_at=datetime(2026, 9, 25, 8, 0, 0),
    )


# ─── Migraciones ─────────────────────────────────────────────────────────────

class TestMigraciones:
    def test_crea_tablas(self, db_path):
        conn = sqlite3.connect(db_path)
        tablas = {
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "ninos" in tablas
        assert "dosajes" in tablas
        assert "intentos_registro" in tablas
        assert "schema_version" in tablas
        conn.close()

    def test_idempotente(self, db_path):
        # Aplicar dos veces no falla ni duplica la versión
        migrar(db_path)
        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0]
        assert count == 1
        conn.close()


# ─── Repositorio de Niños ────────────────────────────────────────────────────

class TestRepositorioNinos:
    def test_guardar_y_obtener_por_dni(self, db_path):
        nino = _nino_base()
        with UnidadDeTrabajo(db_path) as uow:
            uow.ninos.guardar(nino)

        with UnidadDeTrabajo(db_path) as uow:
            encontrado = uow.ninos.obtener_por_dni("12345678")

        assert encontrado is not None
        assert encontrado.dni == "12345678"
        assert encontrado.nombres == "Ana María"

    def test_dni_con_cero_inicial(self, db_path):
        nino = _nino_base(dni="01234567")
        with UnidadDeTrabajo(db_path) as uow:
            uow.ninos.guardar(nino)

        with UnidadDeTrabajo(db_path) as uow:
            encontrado = uow.ninos.obtener_por_dni("01234567")

        assert encontrado is not None
        assert encontrado.dni == "01234567"  # cero preservado

    def test_dni_duplicado_falla(self, db_path):
        nino1 = _nino_base()
        nino2 = _nino_base()  # mismo DNI, distinto UUID

        with UnidadDeTrabajo(db_path) as uow:
            uow.ninos.guardar(nino1)

        with pytest.raises(sqlite3.IntegrityError):
            with UnidadDeTrabajo(db_path) as uow:
                uow.ninos.guardar(nino2)

    def test_rollback_no_persiste(self, db_path):
        nino = _nino_base()
        try:
            with UnidadDeTrabajo(db_path) as uow:
                uow.ninos.guardar(nino)
                raise RuntimeError("Fallo simulado")
        except RuntimeError:
            pass

        with UnidadDeTrabajo(db_path) as uow:
            encontrado = uow.ninos.obtener_por_dni("12345678")
        assert encontrado is None

    def test_actualizar_campos_permitidos(self, db_path):
        nino = _nino_base()
        with UnidadDeTrabajo(db_path) as uow:
            uow.ninos.guardar(nino)

        nino.peso_g = 9000
        nino.distrito = "Junín"
        nino.altitud_msnm = 3800
        nino.cuidador = "Pedro Quispe"
        nino.telefono = "912345678"
        nino.updated_at = datetime(2026, 9, 25, 10, 0, 0)

        with UnidadDeTrabajo(db_path) as uow:
            uow.ninos.actualizar(nino)

        with UnidadDeTrabajo(db_path) as uow:
            actualizado = uow.ninos.obtener_por_dni("12345678")

        assert actualizado is not None
        assert actualizado.peso_g == 9000
        assert actualizado.distrito == "Junín"
        assert actualizado.cuidador == "Pedro Quispe"
        # DNI e identidad no cambian
        assert actualizado.dni == "12345678"
        assert actualizado.nombres == "Ana María"

    def test_obtener_inexistente_devuelve_none(self, db_path):
        with UnidadDeTrabajo(db_path) as uow:
            resultado = uow.ninos.obtener_por_dni("99999999")
        assert resultado is None

    def test_persistencia_tras_reinicio(self, db_path):
        """Los datos sobreviven al cierre y reapertura de la conexión."""
        nino = _nino_base()
        with UnidadDeTrabajo(db_path) as uow:
            uow.ninos.guardar(nino)
        # Simular reinicio: nueva instancia de UoW
        with UnidadDeTrabajo(db_path) as uow:
            encontrado = uow.ninos.obtener_por_dni("12345678")
        assert encontrado is not None


# ─── Repositorio de Dosajes ───────────────────────────────────────────────────

class TestRepositorioDosajes:
    def test_guardar_y_listar(self, db_path):
        nino = _nino_base()
        dosaje = _dosaje_base(nino.id)

        with UnidadDeTrabajo(db_path) as uow:
            uow.ninos.guardar(nino)
            uow.dosajes.guardar(dosaje)

        with UnidadDeTrabajo(db_path) as uow:
            historial = uow.dosajes.listar_por_nino(nino.id)

        assert len(historial) == 1
        assert historial[0].clasificacion == Clasificacion.MODERADA

    def test_ultimo_dosaje_por_fecha_clinica(self, db_path):
        """El último dosaje se determina por fecha clínica, no por inserción."""
        nino = _nino_base()
        ahora = datetime(2026, 9, 25, 8, 0, 0)

        dosaje_antiguo = Dosaje(
            id=uuid.uuid4(), nino_id=nino.id,
            fecha_dosaje=date(2026, 6, 1),
            hb_observada_ddl=80, altitud_msnm=0, ajuste_ddl=0,
            hb_ajustada_ddl=80, edad_meses=39,
            clasificacion=Clasificacion.MODERADA, version_normativa="v1",
            advertencias=[], created_at=ahora,
        )
        dosaje_reciente = Dosaje(
            id=uuid.uuid4(), nino_id=nino.id,
            fecha_dosaje=date(2026, 9, 20),
            hb_observada_ddl=110, altitud_msnm=0, ajuste_ddl=0,
            hb_ajustada_ddl=110, edad_meses=42,
            clasificacion=Clasificacion.SIN_ANEMIA, version_normativa="v1",
            advertencias=[], created_at=ahora,
        )

        with UnidadDeTrabajo(db_path) as uow:
            uow.ninos.guardar(nino)
            # Insertar el reciente primero, luego el antiguo
            uow.dosajes.guardar(dosaje_reciente)
            uow.dosajes.guardar(dosaje_antiguo)

        with UnidadDeTrabajo(db_path) as uow:
            ultimo = uow.dosajes.ultimo_por_nino(nino.id)

        # El reciente (sept) debe ser el último aunque se insertó primero
        assert ultimo is not None
        assert ultimo.clasificacion == Clasificacion.SIN_ANEMIA
        assert ultimo.fecha_dosaje == date(2026, 9, 20)

    def test_dosaje_inmutable_no_se_actualiza(self, db_path):
        """No existe método de actualización de dosajes."""
        assert not hasattr(RepositorioDosajesSQLite, "actualizar")

    def test_advertencias_se_persisten(self, db_path):
        nino = _nino_base()
        dosaje = _dosaje_base(nino.id)
        dosaje.advertencias = ["Hb ajustada negativa: revisar valores"]

        with UnidadDeTrabajo(db_path) as uow:
            uow.ninos.guardar(nino)
            uow.dosajes.guardar(dosaje)

        with UnidadDeTrabajo(db_path) as uow:
            historial = uow.dosajes.listar_por_nino(nino.id)

        assert len(historial[0].advertencias) == 1


# ─── Transacción atómica niño + dosaje inicial ───────────────────────────────

class TestTransaccionAtomica:
    def test_nino_y_dosaje_en_una_transaccion(self, db_path):
        nino = _nino_base()
        dosaje = _dosaje_base(nino.id)

        with UnidadDeTrabajo(db_path) as uow:
            uow.ninos.guardar(nino)
            uow.dosajes.guardar(dosaje)

        with UnidadDeTrabajo(db_path) as uow:
            n = uow.ninos.obtener_por_dni("12345678")
            h = uow.dosajes.listar_por_nino(nino.id)

        assert n is not None
        assert len(h) == 1

    def test_rollback_atomico_nino_y_dosaje(self, db_path):
        """Si falla cualquier parte, no se guarda ninguna."""
        nino = _nino_base()
        dosaje = _dosaje_base(nino.id)

        try:
            with UnidadDeTrabajo(db_path) as uow:
                uow.ninos.guardar(nino)
                uow.dosajes.guardar(dosaje)
                raise sqlite3.Error("Fallo simulado después de guardar")
        except sqlite3.Error:
            pass

        with UnidadDeTrabajo(db_path) as uow:
            n = uow.ninos.obtener_por_dni("12345678")
        assert n is None


# ─── Intento de registro ──────────────────────────────────────────────────────

class TestRepositorioIntentos:
    def test_guardar_intento_aceptado(self, db_path):
        intento = IntentoRegistro.nuevo(
            operacion="CREAR_NINO",
            resultado="ACEPTADO",
            codigos_error=[],
            ahora=datetime(2026, 9, 25, 8, 0, 0),
        )
        with UnidadDeTrabajo(db_path) as uow:
            uow.intentos.guardar(intento)

        with UnidadDeTrabajo(db_path) as uow:
            conteos = uow.intentos.contar_en_periodo(
                datetime(2026, 9, 25, 0, 0, 0),
                datetime(2026, 9, 25, 23, 59, 59),
            )
        assert conteos["ACEPTADO"] == 1
        assert conteos["RECHAZADO"] == 0

    def test_guardar_intento_rechazado_con_codigos(self, db_path):
        intento = IntentoRegistro.nuevo(
            operacion="CREAR_NINO",
            resultado="RECHAZADO",
            codigos_error=["DNI_INVALIDO", "PESO_FUERA_RANGO"],
            ahora=datetime(2026, 9, 25, 8, 0, 0),
        )
        with UnidadDeTrabajo(db_path) as uow:
            uow.intentos.guardar(intento)

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        fila = conn.execute(
            "SELECT codigos_error FROM intentos_registro WHERE resultado='RECHAZADO'"
        ).fetchone()
        conn.close()
        import json
        assert json.loads(fila["codigos_error"]) == ["DNI_INVALIDO", "PESO_FUERA_RANGO"]
