"""Raíz de composición: conecta adaptadores con el núcleo (arquitectura hexagonal)."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.adapters.entrada.http.api import registrar_manejadores, router
from app.adapters.salida.persistencia.sqlalchemy_repo import RepositorioSQLAlchemy
from app.application.casos_uso import RelojSistema, ServicioExpediente

VERSION = "1.0.0-pmv"
WEB = Path(__file__).parent / "web"


def crear_app(database_url: str | None = None, reloj=None) -> FastAPI:
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./datos/anemia.db")
    repo = RepositorioSQLAlchemy(url)
    repo.crear_esquema()

    app = FastAPI(
        title="Sistema de Detección Temprana de Anemia Infantil — Junín",
        version=VERSION,
        description="API del Incremento 1 (PMV): registro nominal, expediente digital, "
        "validación clínica, seguimiento y reporte del periodo.",
        docs_url=None,
        redoc_url=None,
    )
    app.state.servicio = ServicioExpediente(repo, reloj or RelojSistema())
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
            title="API — Anemia Junín (PMV)",
            swagger_js_url="/static/vendor/swagger-ui-bundle.js",
            swagger_css_url="/static/vendor/swagger-ui.css",
        )

    @app.get("/sw.js", include_in_schema=False)
    def service_worker():
        return FileResponse(WEB / "sw.js", media_type="application/javascript")

    return app
