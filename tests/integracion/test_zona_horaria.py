"""DEF-02: el periodo del reporte se interpreta en días calendario de Perú también en la base de datos."""

import os
from datetime import UTC, date, datetime

from app.adapters.salida.persistencia.sqlalchemy_repo import RepositorioSQLAlchemy
from app.domain.entidades import Evaluacion, Nino
from tests.conftest import datos_nino


def test_registro_nocturno_cuenta_en_el_dia_local(tmp_path):
    url = os.getenv("TEST_DATABASE_URL") or f"sqlite:///{tmp_path}/tz.db"
    repo = RepositorioSQLAlchemy(url)
    repo.crear_esquema()
    nino = Nino(**datos_nino(dni="79990001"), registrado_por="a")
    nino.creado_en = datetime(2026, 9, 29, 1, 30, tzinfo=UTC)  # 20:30 del 28-sep en Perú
    ev = Evaluacion(date(2026, 9, 28), 12.0, 8.0, 70.0, 3720, 11, "a", nino_id=nino.id)
    ev.calcular()
    nino.evaluaciones.append(ev)
    repo.guardar(nino)
    try:
        assert repo.contar_registrados_en_periodo(date(2026, 9, 28), date(2026, 9, 28)) == 1
        assert repo.contar_registrados_en_periodo(date(2026, 9, 29), date(2026, 9, 29)) == 0
    finally:
        if os.getenv("TEST_DATABASE_URL"):
            from sqlalchemy import text

            with repo.engine.begin() as c:
                c.execute(text("DELETE FROM evaluacion_hemoglobina WHERE nino_id = :i"), {"i": nino.id})
                c.execute(text("DELETE FROM nino WHERE id = :i"), {"i": nino.id})
