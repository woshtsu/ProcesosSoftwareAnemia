"""
Bootstrap — Construcción e inyección de dependencias — PMV Anemia Junín.

Conecta repositorios, proveedor normativo, clasificador, reloj y crea la app Flask.
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, date, datetime
from functools import partial
from pathlib import Path

from flask import Flask

logger = logging.getLogger(__name__)


class RelojReal:
    def ahora_utc(self) -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def hoy(self) -> date:
        return date.today()


def crear_app(
    db_path: str | None = None,
    normativa_path: Path | None = None,
    secret_key: str | None = None,
    testing: bool = False,
) -> Flask:
    """
    Fábrica de la aplicación Flask.

    Args:
        db_path: Ruta a la base de datos SQLite. Por defecto: instance/anemia.db
        normativa_path: Ruta al JSON normativo. Por defecto: config/normativa_v1.json
        secret_key: Clave secreta para sesiones y CSRF. Usar variable de entorno en producción.
        testing: Si True, deshabilita el manejo de errores de Flask.
    """
    from anemia_junin.adapters.outbound.normativa.proveedor import ProveedorNormativoJSON
    from anemia_junin.adapters.outbound.sqlite.migraciones import migrar
    from anemia_junin.adapters.outbound.sqlite.unidad_de_trabajo import (
        UnidadDeTrabajo,
        verificar_conexion,
    )
    from anemia_junin.application.casos_de_uso.actualizar_nino import ActualizarNino
    from anemia_junin.application.casos_de_uso.agregar_dosaje import AgregarDosaje
    from anemia_junin.application.casos_de_uso.consultar_expediente import ConsultarExpediente
    from anemia_junin.application.casos_de_uso.consultar_reporte import ConsultarReporte
    from anemia_junin.application.casos_de_uso.listar_ninos import ListarNinos
    from anemia_junin.application.casos_de_uso.registrar_nino import RegistrarNino
    from anemia_junin.domain.clasificador import ClasificadorHemoglobina

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # ─── Configuración ────────────────────────────────────────────────────────
    _raiz = Path(__file__).parents[2]  # src/anemia_junin/ → raíz del proyecto

    # Prioridad: argumento explícito > variable de entorno > valor por defecto
    if db_path is None:
        db_path = os.environ.get("ANEMIA_DB_PATH") or str(_raiz / "instance" / "anemia.db")
    if normativa_path is None:
        normativa_env = os.environ.get("ANEMIA_NORMATIVA_PATH")
        normativa_path = (
            Path(normativa_env) if normativa_env else _raiz / "config" / "normativa_v1.json"
        )
    if secret_key is None:
        secret_key = os.environ.get("ANEMIA_SECRET_KEY") or "dev-secret-key-cambiar-en-produccion"

    app.config["SECRET_KEY"] = secret_key
    app.config["DB_PATH"] = db_path
    app.config["TESTING"] = testing
    app.config["WTF_CSRF_ENABLED"] = not testing

    # ─── Normativa ────────────────────────────────────────────────────────────
    # Lanza NormativaInvalidaError si el JSON es inválido → impide el inicio
    proveedor_normativo = ProveedorNormativoJSON(normativa_path)

    # ─── Migraciones ──────────────────────────────────────────────────────────
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    migrar(db_path)

    # ─── Servicios ────────────────────────────────────────────────────────────
    clasificador = ClasificadorHemoglobina(proveedor_normativo)
    reloj = RelojReal()
    uow_factory = partial(UnidadDeTrabajo, db_path)  # solo lectura (BEGIN diferido)
    uow_escritura = partial(UnidadDeTrabajo, db_path, inmediata=True)  # BEGIN IMMEDIATE

    # ─── Casos de uso ─────────────────────────────────────────────────────────
    casos_de_uso = {
        "registrar_nino": RegistrarNino(uow_escritura, clasificador, reloj),
        "consultar_expediente": ConsultarExpediente(uow_factory),
        "actualizar_nino": ActualizarNino(uow_escritura, reloj),
        "agregar_dosaje": AgregarDosaje(uow_escritura, clasificador, reloj),
        "listar_ninos": ListarNinos(uow_factory, reloj),
        "consultar_reporte": ConsultarReporte(uow_factory),
    }

    app.config["CASOS_DE_USO"] = casos_de_uso
    app.config["VERIFICAR_BD"] = partial(verificar_conexion, db_path)

    # ─── Blueprints ───────────────────────────────────────────────────────────
    from anemia_junin.adapters.inbound.rest_api.blueprints import api_bp
    from anemia_junin.adapters.inbound.web_ui.blueprints import web_bp

    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(web_bp)

    # ─── CSRF ─────────────────────────────────────────────────────────────────
    # Protege los formularios HTML. La API JSON queda exenta: no usa cookies de
    # sesión ni CORS, por lo que no es vulnerable a CSRF desde otro origen.
    from flask_wtf.csrf import CSRFProtect

    csrf = CSRFProtect(app)
    csrf.exempt(api_bp)

    @app.errorhandler(404)
    def _no_encontrado(_error):
        from flask import jsonify, render_template, request

        if request.path.startswith("/api/"):
            cuerpo = {"error": {"code": "NOT_FOUND", "message": "Recurso no encontrado"}}
            return jsonify(cuerpo), 404
        return render_template("errors/404.html", dni=None), 404

    @app.errorhandler(500)
    def _error_interno(_error):
        from flask import jsonify, request

        # Sin trazas internas en la respuesta (se registran en el log del servidor)
        cuerpo = {"error": {"code": "INTERNAL_ERROR", "message": "Error interno del servidor"}}
        if request.path.startswith("/api/"):
            return jsonify(cuerpo), 500
        return "Error interno del servidor", 500

    logger.info("Aplicación iniciada. BD: %s", db_path)
    return app
