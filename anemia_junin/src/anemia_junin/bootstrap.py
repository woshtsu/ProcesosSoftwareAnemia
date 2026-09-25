"""
Bootstrap — Construcción e inyección de dependencias — PMV Anemia Junín.

Conecta repositorios, proveedor normativo, clasificador, reloj y crea la app Flask.
"""

from __future__ import annotations

import logging
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
    from anemia_junin.adapters.outbound.sqlite.unidad_de_trabajo import UnidadDeTrabajo
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

    if db_path is None:
        db_path = str(_raiz / "instance" / "anemia.db")
    if normativa_path is None:
        normativa_path = _raiz / "config" / "normativa_v1.json"
    if secret_key is None:
        secret_key = "dev-secret-key-cambiar-en-produccion"

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
    uow_factory = partial(UnidadDeTrabajo, db_path)

    # ─── Casos de uso ─────────────────────────────────────────────────────────
    casos_de_uso = {
        "registrar_nino": RegistrarNino(uow_factory, clasificador, reloj),
        "consultar_expediente": ConsultarExpediente(uow_factory),
        "actualizar_nino": ActualizarNino(uow_factory, reloj),
        "agregar_dosaje": AgregarDosaje(uow_factory, clasificador, reloj),
        "listar_ninos": ListarNinos(uow_factory),
        "consultar_reporte": ConsultarReporte(uow_factory),
    }

    app.config["CASOS_DE_USO"] = casos_de_uso

    # ─── Blueprints ───────────────────────────────────────────────────────────
    from anemia_junin.adapters.inbound.rest_api.blueprints import api_bp
    from anemia_junin.adapters.inbound.web_ui.blueprints import web_bp

    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(web_bp)

    logger.info("Aplicación iniciada. BD: %s", db_path)
    return app
