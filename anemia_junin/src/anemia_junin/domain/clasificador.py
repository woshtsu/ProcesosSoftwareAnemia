"""
Clasificador de hemoglobina — PMV Anemia Junín.

Implementa reglas versionadas basadas en la NTS 213-MINSA/DGIESP-2024 (aprobada por
RM 251-2024-MINSA, modificada por RM 429-2024-MINSA). Datos en config/normativa_v1.json.
Sin dependencias externas.

Fuente de referencia (no certifica uso clínico):
  https://www.gob.pe/institucion/minsa/normas-legales/5670414-429-2024-minsa

Representación interna:
  - Hb en décimas de g/dL (enteros); ej: 10.5 g/dL → 105
  - Ajuste en décimas de g/dL; ej: 1.8 → 18
"""

from __future__ import annotations

from dataclasses import dataclass

from anemia_junin.domain.entities import Clasificacion
from anemia_junin.domain.ports import ProveedorNormativo


@dataclass
class ResultadoClasificacion:
    clasificacion: Clasificacion
    ajuste_ddl: int          # décimas de g/dL
    hb_ajustada_ddl: int     # décimas de g/dL
    version_normativa: str
    advertencias: list[str]


class ClasificadorHemoglobina:
    """
    Clasifica Hb usando ajuste tabulado por altitud y umbrales por edad.

    Reglas:
    - < 6 meses → NO_EVALUABLE
    - Hb ajustada negativa → NO_EVALUABLE + advertencia
    - Sin normativa para el grupo de edad → NO_EVALUABLE + advertencia
    """

    def __init__(self, proveedor: ProveedorNormativo) -> None:
        self._proveedor = proveedor
        self._tabla_ajuste = self._cargar_tabla_ajuste()
        self._grupos_edad = self._cargar_grupos_edad()

    # ─── API pública ──────────────────────────────────────────────────────────

    def clasificar(
        self,
        *,
        hb_observada_ddl: int,
        altitud_msnm: int,
        edad_meses: int,
    ) -> ResultadoClasificacion:
        version = self._proveedor.version()
        advertencias: list[str] = []

        # Menores de 6 meses: no se evalúan
        if edad_meses < 6:
            return ResultadoClasificacion(
                clasificacion=Clasificacion.NO_EVALUABLE,
                ajuste_ddl=0,
                hb_ajustada_ddl=hb_observada_ddl,
                version_normativa=version,
                advertencias=["Menor de 6 meses: clasificación no aplicable"],
            )

        # Ajuste tabulado
        ajuste_ddl, verificada = self._ajuste_para_altitud(altitud_msnm)
        hb_ajustada_ddl = hb_observada_ddl - ajuste_ddl
        if not verificada:
            advertencias.append(
                f"Ajuste por altitud ({altitud_msnm} msnm) de una banda no verificada contra "
                "la fuente oficial: la clasificación es solo referencial"
            )

        # Hb ajustada negativa
        if hb_ajustada_ddl < 0:
            advertencias.append(
                f"Hb ajustada negativa ({hb_ajustada_ddl / 10:.1f} g/dL): revisar valores"
            )
            return ResultadoClasificacion(
                clasificacion=Clasificacion.NO_EVALUABLE,
                ajuste_ddl=ajuste_ddl,
                hb_ajustada_ddl=hb_ajustada_ddl,
                version_normativa=version,
                advertencias=advertencias,
            )

        # Buscar grupo de edad
        grupo = self._grupo_para_edad(edad_meses)
        if grupo is None:
            advertencias.append(f"Edad {edad_meses} meses fuera de los grupos normados")
            return ResultadoClasificacion(
                clasificacion=Clasificacion.NO_EVALUABLE,
                ajuste_ddl=ajuste_ddl,
                hb_ajustada_ddl=hb_ajustada_ddl,
                version_normativa=version,
                advertencias=advertencias,
            )

        clasificacion = self._aplicar_umbrales(hb_ajustada_ddl, grupo)

        return ResultadoClasificacion(
            clasificacion=clasificacion,
            ajuste_ddl=ajuste_ddl,
            hb_ajustada_ddl=hb_ajustada_ddl,
            version_normativa=version,
            advertencias=advertencias,
        )

    # ─── Internos ─────────────────────────────────────────────────────────────

    def _cargar_tabla_ajuste(self) -> list[tuple[int, int, int, bool]]:
        """Devuelve lista de (altitud_desde, altitud_hasta, ajuste_ddl, verificada)."""
        tabla = []
        for fila in self._proveedor.tabla_ajuste():
            desde = int(fila["altitud_desde_msnm"])
            hasta = int(fila["altitud_hasta_msnm"])
            # Convertir g/dL a décimas
            ajuste_ddl = round(float(fila["ajuste_gdl"]) * 10)
            verificada = bool(fila.get("verificada", True))
            tabla.append((desde, hasta, ajuste_ddl, verificada))
        return tabla

    def _cargar_grupos_edad(self) -> list[dict]:
        """Devuelve lista de grupos con umbrales en décimas de g/dL."""
        grupos = []
        for g in self._proveedor.grupos_edad():
            umbrales = g["umbrales_hb_ajustada_gdl"]
            def _ddl(clave: str, u: dict = umbrales) -> int:
                return round(float(u[clave]) * 10)

            grupos.append({
                "desde": int(g["desde_meses_inclusive"]),
                "hasta": int(g["hasta_meses_inclusive"]),
                "severa_hasta_exclusive_ddl": _ddl("severa_hasta_exclusive"),
                "moderada_hasta_exclusive_ddl": _ddl("moderada_hasta_exclusive"),
                "leve_hasta_exclusive_ddl": _ddl("leve_hasta_exclusive"),
            })
        return grupos

    def _ajuste_para_altitud(self, altitud_msnm: int) -> tuple[int, bool]:
        """Devuelve (ajuste_ddl, banda_verificada)."""
        for desde, hasta, ajuste, verificada in self._tabla_ajuste:
            if desde <= altitud_msnm <= hasta:
                return ajuste, verificada
        # Fuera de rango — no debería ocurrir si el validador funciona
        return 0, True

    def _grupo_para_edad(self, edad_meses: int) -> dict | None:
        for grupo in self._grupos_edad:
            if grupo["desde"] <= edad_meses <= grupo["hasta"]:
                return grupo
        return None

    def _aplicar_umbrales(self, hb_ajustada_ddl: int, grupo: dict) -> Clasificacion:
        """
        Clasifica según umbrales del grupo.

        Intervalos (para grupo 6-23 meses, en décimas):
          SEVERA:    hb < 70  (< 7.0 g/dL)
          MODERADA:  70 ≤ hb < 95  (7.0–9.4 g/dL)
          LEVE:      95 ≤ hb < 105  (9.5–10.4 g/dL)
          SIN_ANEMIA: hb ≥ 105  (≥ 10.5 g/dL)
        """
        if hb_ajustada_ddl < grupo["severa_hasta_exclusive_ddl"]:
            return Clasificacion.SEVERA
        if hb_ajustada_ddl < grupo["moderada_hasta_exclusive_ddl"]:
            return Clasificacion.MODERADA
        if hb_ajustada_ddl < grupo["leve_hasta_exclusive_ddl"]:
            return Clasificacion.LEVE
        return Clasificacion.SIN_ANEMIA
