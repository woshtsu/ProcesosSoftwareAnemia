"""Raíz de composición: conecta adaptadores con el núcleo (arquitectura hexagonal)."""

import os
import threading
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.types import Scope

from app.adapters.inbound.http.api import registrar_manejadores, router
from app.adapters.inbound.http.autenticacion import registrar_seguridad
from app.adapters.inbound.http.autenticacion import router as auth_router
from app.adapters.outbound.notificaciones import crear_notificador
from app.adapters.outbound.persistence.sqlalchemy_repo import RepositorioSQLAlchemy
from app.adapters.outbound.reloj_fijo import RelojFijo
from app.adapters.outbound.reloj_sistema import RelojSistema
from app.adapters.outbound.supabase_auth import SupabaseAuth
from app.application.cache_agendas import CacheAgendas
from app.application.servicio_agenda import ServicioAgenda
from app.application.servicio_agenda_personal import ServicioAgendaPersonal
from app.application.servicio_alertas import ServicioAlertas
from app.application.servicio_asistencia import ServicioAsistencia
from app.application.servicio_barreras import ServicioBarreras
from app.application.servicio_contexto import ServicioContexto
from app.application.servicio_expediente import ServicioExpediente
from app.application.servicio_recordatorios import ServicioRecordatorios
from app.application.servicio_sesion import ServicioSesion
from app.application.servicio_sincronizacion import ServicioSincronizacion
from app.application.servicio_visitas import ServicioVisitas
from app.domain.model.notificacion import ConfiguracionWebhook
from app.ports.outbound.notificador import Notificador

VERSION = "4.0.0-inc4"
WEB = Path(__file__).parent / "web"


CACHE_LARGO = "public, max-age=86400"
ESTATICOS_INMUTABLES = {"icono.svg", "manifest.json"}


class StaticFilesConCache(StaticFiles):
    """Las librerías de terceros e iconos se cachean un día; el código propio usa ``no-cache``:
    el navegador revalida con ETag (304 sin cuerpo), de modo que tras un despliegue nunca
    mezcla versiones de app.js, auth.js, cola.js y sync.js."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        if response.status_code < 400:
            ruta = path.replace("\\", "/")
            largo = ruta.startswith("vendor/") or ruta in ESTATICOS_INMUTABLES
            response.headers["Cache-Control"] = CACHE_LARGO if largo else "no-cache"
        return response


def crear_app(
    database_url: str | None = None,
    reloj=None,
    fecha_referencia: date | None = None,
    auth_mode: str | None = None,
    notificador: Notificador | None = None,
) -> FastAPI:
    """Compone la aplicación. Con ``fecha_referencia`` (o la variable de entorno FECHA_REFERENCIA=AAAA-MM-DD) el
    «hoy» del sistema es esa fecha fija, p. ej. el corte de un dataset (ADR-009); sin ella se usa el reloj real.

    ``notificador`` fija el canal de los recordatorios (pruebas); por defecto sale de las variables de entorno
    WHATSAPP_* y SMS_*: sin ellas es el notificador simulado y nunca se envía un mensaje real (ADR-014)."""
    modo = auth_mode or os.getenv("AUTH_MODE", "supabase")
    if modo not in {"supabase", "demo"}:
        raise ValueError("AUTH_MODE debe ser supabase o demo.")
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./datos/anemia.db")
    if reloj is None and fecha_referencia is None and os.getenv("FECHA_REFERENCIA"):
        fecha_referencia = RelojFijo.desde_texto(os.environ["FECHA_REFERENCIA"]).fecha
    repo = RepositorioSQLAlchemy(url)
    repo.crear_esquema()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if os.getenv("PRECALCULAR_AGENDAS") == "1" and hasattr(app.state, "cache_agendas"):
            threading.Thread(target=app.state.cache_agendas.obtener_agendas, daemon=True).start()
        yield
        if hasattr(app.state, "proveedor_auth") and hasattr(app.state.proveedor_auth, "aclose"):
            await app.state.proveedor_auth.aclose()
        if hasattr(app.state, "sesiones") and hasattr(app.state.sesiones, "aclose"):
            await app.state.sesiones.aclose()

    app = FastAPI(
        title="Sistema de Detección Temprana de Anemia Infantil — Junín",
        version=VERSION,
        description="API del Incremento 1 (registro nominal, expediente digital, validación clínica, seguimiento "
        "y reporte del periodo), del Incremento 2 (agenda automática de controles, alertas de controles vencidos, "
        "agenda del personal y registro de asistencia a control) y del Incremento 3 (sincronización de lo registrado "
        "sin conexión, resolución de conflictos y visita domiciliaria priorizada) y del Incremento 4 (recordatorios de "
        "control por WhatsApp con respaldo por SMS, respuesta del tutor, barreras de acceso y su alerta crítica).",
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )
    if reloj is None:
        reloj = RelojFijo(fecha_referencia) if fecha_referencia else RelojSistema()
    cache_agendas = CacheAgendas(repo, reloj)
    app.state.cache_agendas = cache_agendas
    expediente = ServicioExpediente(repo, reloj, cache_agendas=cache_agendas)
    app.state.repositorio = repo
    app.state.expediente = app.state.seguimiento = app.state.reporte = expediente
    app.state.agenda = ServicioAgenda(repo, reloj)
    app.state.alertas = ServicioAlertas(repo, reloj, cache_agendas=cache_agendas)
    app.state.agenda_personal = ServicioAgendaPersonal(repo, reloj, cache_agendas=cache_agendas)
    app.state.asistencia = ServicioAsistencia(repo, reloj)
    app.state.barreras = ServicioBarreras(repo, repo, reloj, cache_agendas=cache_agendas)
    app.state.visitas = ServicioVisitas(repo, repo, reloj, repo, cache_agendas=cache_agendas)
    app.state.sincronizacion = ServicioSincronizacion(
        repo, repo, repo, expediente, app.state.asistencia, app.state.visitas, reloj, app.state.barreras
    )
    app.state.recordatorios = ServicioRecordatorios(
        repo,
        repo,
        notificador or crear_notificador(os.environ),
        reloj,
        app.state.barreras,
        ConfiguracionWebhook(os.getenv("WHATSAPP_VERIFY_TOKEN", ""), os.getenv("WHATSAPP_APP_SECRET", "")),
        cache_agendas=cache_agendas,
    )
    app.state.contexto = ServicioContexto(reloj, fecha_referencia)
    proveedor = SupabaseAuth(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_PUBLISHABLE_KEY", ""))
    app.state.proveedor_auth = proveedor
    app.state.sesiones = ServicioSesion(proveedor)
    app.state.auth_mode = modo
    app.state.auth_configurado = proveedor.configurado
    app.state.cookie_secure = os.getenv("AUTH_COOKIE_SECURE", "true").lower() != "false"
    registrar_seguridad(app)
    registrar_manejadores(app)
    app.include_router(router)
    app.include_router(auth_router)
    app.mount("/static", StaticFilesConCache(directory=WEB), name="static")

    @app.get("/", include_in_schema=False)
    def inicio():
        return FileResponse(WEB / "index.html", headers={"Cache-Control": "no-cache"})

    @app.get("/docs", include_in_schema=False)
    def documentacion():
        # Recursos servidos localmente: la documentación funciona sin acceso a CDN (entorno rural).
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="API — Anemia Junín (Incremento 4)",
            swagger_js_url="/static/vendor/swagger-ui-bundle.js",
            swagger_css_url="/static/vendor/swagger-ui.css",
        )

    @app.get("/sw.js", include_in_schema=False)
    def service_worker():
        return FileResponse(
            WEB / "sw.js",
            media_type="application/javascript",
            headers={"Cache-Control": "no-cache"},
        )

    return app
