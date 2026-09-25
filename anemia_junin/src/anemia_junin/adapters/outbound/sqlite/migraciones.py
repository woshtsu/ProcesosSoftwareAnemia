"""
Gestión de migraciones SQLite — PMV Anemia Junín.

Aplica migraciones SQL numeradas sin borrar datos existentes.
Mantiene la tabla `schema_version` como registro de versiones aplicadas.
"""

from __future__ import annotations

import logging
import re
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

# El directorio de migraciones está en la raíz del proyecto
# src/anemia_junin/adapters/outbound/sqlite/migraciones.py → 5 niveles arriba = raíz
_MIGRATIONS_DIR = Path(__file__).parents[5] / "migrations"


def _conexion_base(db_path: str) -> sqlite3.Connection:
    """Abre una conexión con configuración estándar del proyecto."""
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.row_factory = sqlite3.Row
    return conn


def migrar(db_path: str, migrations_dir: Path | None = None) -> None:
    """
    Aplica todas las migraciones pendientes en orden ascendente.
    Es idempotente: nunca re-aplica una migración ya registrada.
    """
    if migrations_dir is None:
        migrations_dir = _MIGRATIONS_DIR

    conn = _conexion_base(db_path)
    try:
        # Asegurar que la tabla de control exista antes de consultar
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version     INTEGER PRIMARY KEY,
                aplicada_en TEXT    NOT NULL,
                descripcion TEXT    NOT NULL
            )
        """)
        conn.commit()

        aplicadas = {
            row[0]
            for row in conn.execute("SELECT version FROM schema_version")
        }

        archivos = sorted(
            f for f in migrations_dir.glob("*.sql")
            if re.match(r"^\d+_", f.name)
        )

        for archivo in archivos:
            numero = int(archivo.name.split("_")[0])
            if numero in aplicadas:
                logger.debug("Migración %d ya aplicada, omitiendo.", numero)
                continue

            logger.info("Aplicando migración %d: %s", numero, archivo.name)
            sql = archivo.read_text(encoding="utf-8")
            conn.executescript(sql)
            conn.commit()
            logger.info("Migración %d aplicada correctamente.", numero)

    finally:
        conn.close()
