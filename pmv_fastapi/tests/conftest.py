import os
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria
from app.application.servicio_expediente import ServicioExpediente
from app.main import crear_app

HOY = date(2026, 9, 28)


@pytest.fixture(autouse=True)
def modo_demo_explicito(monkeypatch):
    """Las pruebas históricas usan datos sintéticos; auth se prueba con supabase explícito."""
    monkeypatch.setenv("AUTH_MODE", "demo")


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

        with app.state.repositorio.engine.begin() as con:
            con.execute(
                text(
                    "TRUNCATE barrera, recordatorio, conflicto_sincronizacion, operacion_sincronizada, visita_domiciliaria, asistencia_control, evaluacion_hemoglobina, nino CASCADE"
                )
            )
    with TestClient(app) as c:
        yield c
    app.state.repositorio.engine.dispose()  # cierra las conexiones: evita ResourceWarning por bases SQLite abiertas


def cuerpo_registro(**cambios_nino):
    n = datos_nino(**cambios_nino)
    n["fecha_nacimiento"] = n["fecha_nacimiento"].isoformat()
    e = datos_eval()
    e["fecha"] = e["fecha"].isoformat()
    return {"nino": n, "evaluacion_inicial": e}


# --- Constructores de dominio para las pruebas de agenda y alertas (Incremento 2) -------------------------------------


def evaluacion_de(fecha: date, clasificacion: str = "SIN_ANEMIA", **cambios):
    """Evaluación de dominio con la clasificación fijada directamente (sin pasar por las reglas clínicas)."""
    from app.domain.model.clasificacion import Clasificacion
    from app.domain.model.entidades import Evaluacion

    base = dict(
        fecha=fecha,
        hemoglobina_observada=12.0,
        peso_kg=8.0,
        talla_cm=70.0,
        altitud_m=3000,
        edad_meses=12,
        registrado_por="prueba",
        clasificacion=Clasificacion(clasificacion),
    )
    base.update(cambios)
    return Evaluacion(**base)


def nino_de(nacimiento: date, evaluaciones: list | None = None, estado: str = "ACTIVO", **cambios):
    """Niño de dominio con las evaluaciones dadas: ``[(fecha, clasificación), ...]`` o ``Evaluacion``."""
    from app.domain.model.entidades import Evaluacion, Nino

    nino = Nino(**{**datos_nino(fecha_nacimiento=nacimiento, estado=estado), "registrado_por": "prueba", **cambios})
    for e in evaluaciones or []:
        nino.evaluaciones.append(e if isinstance(e, Evaluacion) else evaluacion_de(*e, nino_id=nino.id))
    return nino
