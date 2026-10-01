import os
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.adapters.salida.persistencia.memoria import RepositorioEnMemoria
from app.application.casos_uso import ServicioExpediente
from app.main import crear_app

HOY = date(2026, 9, 28)


class RelojFijo:
    def __init__(self, dia: date = HOY):
        self.dia = dia

    def hoy(self) -> date:
        return self.dia


@pytest.fixture
def reloj():
    return RelojFijo()


@pytest.fixture
def servicio(reloj):
    return ServicioExpediente(RepositorioEnMemoria(), reloj)


def datos_nino(**cambios):
    base = dict(
        dni="71234567",
        nombres="Luz Mery",
        apellidos="Quispe Rojas",
        sexo="F",
        fecha_nacimiento=date(2025, 10, 15),
        establecimiento="P. S. Chongos Alto",
        distrito="Chongos Alto",
        comunidad="Palmayoc",
        altitud_m=3720,
        tutor_nombre="Rosa Rojas Pérez",
        tutor_celular="987654321",
    )
    base.update(cambios)
    return base


def datos_eval(**cambios):
    base = dict(fecha=date(2026, 9, 20), hemoglobina_observada=12.4, peso_kg=8.1, talla_cm=69.5)
    base.update(cambios)
    return base


@pytest.fixture
def cliente(tmp_path):
    # Por defecto SQLite temporal; en CI se valida también contra PostgreSQL con TEST_DATABASE_URL.
    url = os.getenv("TEST_DATABASE_URL") or f"sqlite:///{tmp_path}/prueba.db"
    app = crear_app(url, reloj=RelojFijo())
    if url.startswith("postgresql"):
        from sqlalchemy import text

        with app.state.servicio.repo.engine.begin() as con:
            con.execute(text("TRUNCATE evaluacion_hemoglobina, nino CASCADE"))
    with TestClient(app) as c:
        yield c


def cuerpo_registro(**cambios_nino):
    n = datos_nino(**cambios_nino)
    n["fecha_nacimiento"] = n["fecha_nacimiento"].isoformat()
    e = datos_eval()
    e["fecha"] = e["fecha"].isoformat()
    return {"nino": n, "evaluacion_inicial": e}
