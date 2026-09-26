"""
Unidad de Trabajo SQLite — PMV Anemia Junín.

Context manager que agrupa repositorios bajo una misma transacción.
Commit en __exit__ si no hubo excepción; rollback si hubo.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from types import TracebackType

from anemia_junin.adapters.outbound.sqlite.repositorios import (
    RepositorioDosajesSQLite,
    RepositorioIntentosSQLite,
    RepositorioNinosSQLite,
)


def _abrir_conexion(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.row_factory = sqlite3.Row
    return conn


def verificar_conexion(db_path: str) -> bool:
    """Comprueba que la base de datos responde (usado por GET /api/v1/salud)."""
    # mode=rw: no crea un archivo vacío si la BD no existe
    uri = Path(db_path).resolve().as_uri() + "?mode=rw"
    try:
        conn = sqlite3.connect(uri, uri=True, timeout=2.0)
    except sqlite3.Error:
        return False
    try:
        conn.execute("SELECT 1 FROM schema_version LIMIT 1")
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()


class UnidadDeTrabajo:
    """
    Gestiona una conexión y transacción SQLite.

    Uso:
        with UnidadDeTrabajo(db_path) as uow:
            uow.ninos.guardar(nino)
            uow.dosajes.guardar(dosaje)
        # commit automático al salir sin excepción
    """

    def __init__(self, db_path: str, inmediata: bool = False) -> None:
        """
        Args:
            db_path: ruta de la BD SQLite.
            inmediata: si True abre la transacción con ``BEGIN IMMEDIATE`` (reserva el
                bloqueo de escritura desde el inicio). Se usa en los casos de uso que
                leen y luego escriben: con ``BEGIN`` diferido, dos transacciones
                concurrentes que intentan pasar de lectura a escritura provocan
                ``database is locked`` inmediato en modo WAL (detectado en la prueba
                de carga con Locust).
        """
        self._db_path = db_path
        self._inmediata = inmediata
        self._conn: sqlite3.Connection | None = None
        self._ninos: RepositorioNinosSQLite | None = None
        self._dosajes: RepositorioDosajesSQLite | None = None
        self._intentos: RepositorioIntentosSQLite | None = None

    def __enter__(self) -> UnidadDeTrabajo:
        self._conn = _abrir_conexion(self._db_path)
        self._conn.execute("BEGIN IMMEDIATE" if self._inmediata else "BEGIN")
        self._ninos = RepositorioNinosSQLite(self._conn)
        self._dosajes = RepositorioDosajesSQLite(self._conn)
        self._intentos = RepositorioIntentosSQLite(self._conn)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if self._conn is None:
            return False
        try:
            if exc_type is None:
                self._conn.commit()
            else:
                self._conn.rollback()
        finally:
            self._conn.close()
            self._conn = None
        return False  # no suprimir excepciones

    @property
    def ninos(self) -> RepositorioNinosSQLite:
        assert self._ninos is not None, "Usar dentro de un bloque 'with'"
        return self._ninos

    @property
    def dosajes(self) -> RepositorioDosajesSQLite:
        assert self._dosajes is not None, "Usar dentro de un bloque 'with'"
        return self._dosajes

    @property
    def intentos(self) -> RepositorioIntentosSQLite:
        assert self._intentos is not None, "Usar dentro de un bloque 'with'"
        return self._intentos
