"""Raíz de composición: conecta adaptadores con el núcleo (arquitectura hexagonal)."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.adapters.inbound.http.api import registrar_manejadores, router
from app.adapters.outbound.persistence.sqlalchemy_repo import RepositorioSQLAlchemy
from app.adapters.outbound.reloj_sistema import RelojSistema
from app.application.servicio_agenda import ServicioAgenda
from app.application.servicio_alertas import ServicioAlertas
from app.application.servicio_expediente import ServicioExpediente

VERSION = "1.5.0-inc2-avance"
WEB = Path(__file__).parent / "web"


def crear_app(database_url: str | None = None, reloj=None) -> FastAPI:
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./datos/anemia.db")
    repo = RepositorioSQLAlchemy(url)
    repo.crear_esquema()

    app = FastAPI(
        title="Sistema de Detección Temprana de Anemia Infantil — Junín",
        version=VERSION,
        description="API del Incremento 1 (registro nominal, expediente digital, validación clínica, seguimiento "
        "y reporte del periodo) y del avance del Incremento 2 (agenda automática de controles y alertas de "
        "controles vencidos).",
        docs_url=None,
        redoc_url=None,
    )
    reloj = reloj or RelojSistema()
    expediente = ServicioExpediente(repo, reloj)
    app.state.repositorio = repo
    app.state.expediente = app.state.seguimiento = app.state.reporte = expediente
    app.state.agenda = ServicioAgenda(repo, reloj)
    app.state.alertas = ServicioAlertas(repo, reloj)
    registrar_manejadores(app)
    app.include_router(router)
    app.mount("/static", StaticFiles(directory=WEB), name="static")

    @app.get("/", include_in_schema=False)
    def inicio():
        return FileResponse(WEB / "index.html")

    @app.get("/docs", include_in_schema=False)
    def documentacion():
        # Recursos servidos localmente: la documentación funciona sin acceso a CDN (entorno rural).
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="API — Anemia Junín (Incremento 2, avance)",
            swagger_js_url="/static/vendor/swagger-ui-bundle.js",
            swagger_css_url="/static/vendor/swagger-ui.css",
        )

    @app.get("/sw.js", include_in_schema=False)
    def service_worker():
        return FileResponse(WEB / "sw.js", media_type="application/javascript")

    return app
