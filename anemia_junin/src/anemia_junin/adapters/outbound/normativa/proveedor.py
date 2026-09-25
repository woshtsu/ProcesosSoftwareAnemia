"""
Proveedor normativo JSON — PMV Anemia Junín.

Lee config/normativa_v1.json y valida su estructura al inicio.
Si el archivo es inválido o está ausente, lanza NormativaInvalidaError
para impedir el inicio de la aplicación.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class NormativaInvalidaError(RuntimeError):
    """Se lanza cuando la configuración normativa está ausente o inválida."""


class ProveedorNormativoJSON:
    """
    Carga la configuración normativa desde un archivo JSON.
    Valida la estructura mínima requerida al instanciarse.
    """

    def __init__(self, ruta: Path) -> None:
        if not ruta.exists():
            raise NormativaInvalidaError(
                f"Archivo normativo no encontrado: {ruta}"
            )
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise NormativaInvalidaError(
                f"Archivo normativo con JSON inválido: {ruta} — {exc}"
            ) from exc

        self._validar(datos, ruta)
        self._datos = datos
        self._version = datos["_meta"]["version"]
        logger.info(
            "Normativa cargada: versión %s desde %s", self._version, ruta
        )

    def version(self) -> str:
        return self._version

    def grupos_edad(self) -> list[dict]:
        return self._datos["clasificacion"]["grupos_edad_meses"]

    def tabla_ajuste(self) -> list[dict]:
        return self._datos["ajuste_altitud"]["tabla"]

    # ─── Validación mínima ────────────────────────────────────────────────────

    def _validar(self, datos: dict, ruta: Path) -> None:
        errores: list[str] = []

        if "_meta" not in datos or "version" not in datos.get("_meta", {}):
            errores.append("Falta '_meta.version'")

        grupos = datos.get("clasificacion", {}).get("grupos_edad_meses", [])
        if not grupos:
            errores.append("Falta 'clasificacion.grupos_edad_meses' o está vacío")
        for i, g in enumerate(grupos):
            for campo in ("desde_meses_inclusive", "hasta_meses_inclusive", "umbrales_hb_ajustada_gdl"):
                if campo not in g:
                    errores.append(f"Grupo {i}: falta '{campo}'")

        tabla = datos.get("ajuste_altitud", {}).get("tabla", [])
        if not tabla:
            errores.append("Falta 'ajuste_altitud.tabla' o está vacía")
        for i, fila in enumerate(tabla):
            for campo in ("altitud_desde_msnm", "altitud_hasta_msnm", "ajuste_gdl"):
                if campo not in fila:
                    errores.append(f"Tabla ajuste fila {i}: falta '{campo}'")

        if errores:
            raise NormativaInvalidaError(
                f"Normativa inválida en {ruta}:\n" + "\n".join(f"  - {e}" for e in errores)
            )
