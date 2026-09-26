"""
Pruebas del dominio: clasificador de Hb — PMV Anemia Junín.

Casos indispensables:
- Cada umbral de Hb y cada frontera de altitud
- Menores de 6 meses y ausencia de dosaje
- Hb ajustada negativa
"""

from __future__ import annotations

import pytest

from anemia_junin.domain.clasificador import ClasificadorHemoglobina
from anemia_junin.domain.entities import Clasificacion

# ─── Fixture: proveedor normativo en memoria ──────────────────────────────────

class ProveedorNormativoFake:
    """Implementa ProveedorNormativo con los datos del plan."""

    def version(self) -> str:
        return "v1"

    def grupos_edad(self) -> list[dict]:
        return [
            {
                "id": "6_23",
                "desde_meses_inclusive": 6,
                "hasta_meses_inclusive": 23,
                "umbrales_hb_ajustada_gdl": {
                    "severa_hasta_exclusive": 7.0,
                    "moderada_hasta_exclusive": 9.5,
                    "leve_hasta_exclusive": 10.5,
                    "sin_anemia_desde_inclusive": 10.5,
                },
            },
            {
                "id": "24_59",
                "desde_meses_inclusive": 24,
                "hasta_meses_inclusive": 59,
                "umbrales_hb_ajustada_gdl": {
                    "severa_hasta_exclusive": 7.0,
                    "moderada_hasta_exclusive": 10.0,
                    "leve_hasta_exclusive": 11.0,
                    "sin_anemia_desde_inclusive": 11.0,
                },
            },
        ]

    def tabla_ajuste(self) -> list[dict]:
        return [
            {"altitud_desde_msnm": 0,    "altitud_hasta_msnm": 499,  "ajuste_gdl": 0.0},
            {"altitud_desde_msnm": 500,  "altitud_hasta_msnm": 999,  "ajuste_gdl": 0.4},
            {"altitud_desde_msnm": 1000, "altitud_hasta_msnm": 1499, "ajuste_gdl": 0.8},
            {"altitud_desde_msnm": 1500, "altitud_hasta_msnm": 1999, "ajuste_gdl": 1.1},
            {"altitud_desde_msnm": 2000, "altitud_hasta_msnm": 2499, "ajuste_gdl": 1.4},
            {"altitud_desde_msnm": 2500, "altitud_hasta_msnm": 2999, "ajuste_gdl": 1.8},
            {"altitud_desde_msnm": 3000, "altitud_hasta_msnm": 3499, "ajuste_gdl": 2.1},
            {"altitud_desde_msnm": 3500, "altitud_hasta_msnm": 3999, "ajuste_gdl": 2.5},
            {"altitud_desde_msnm": 4000, "altitud_hasta_msnm": 4499, "ajuste_gdl": 2.9},
            {"altitud_desde_msnm": 4500, "altitud_hasta_msnm": 4999, "ajuste_gdl": 3.3},
        ]


@pytest.fixture
def clasificador() -> ClasificadorHemoglobina:
    return ClasificadorHemoglobina(ProveedorNormativoFake())


# ─── Menores de 6 meses ───────────────────────────────────────────────────────

class TestMenoresDeSeisMeses:
    def test_cinco_meses_no_evaluable(self, clasificador):
        r = clasificador.clasificar(hb_observada_ddl=120, altitud_msnm=0, edad_meses=5)
        assert r.clasificacion == Clasificacion.NO_EVALUABLE

    def test_cero_meses_no_evaluable(self, clasificador):
        r = clasificador.clasificar(hb_observada_ddl=150, altitud_msnm=0, edad_meses=0)
        assert r.clasificacion == Clasificacion.NO_EVALUABLE

    def test_advertencia_menor_seis_meses(self, clasificador):
        r = clasificador.clasificar(hb_observada_ddl=120, altitud_msnm=0, edad_meses=3)
        assert len(r.advertencias) > 0


# ─── Ajuste de altitud — todas las fronteras ──────────────────────────────────

class TestAjusteAltitud:
    """Verifica cada rango de ajuste tabulado con una Hb base que no cambia la clasificación."""

    def _ajuste(self, clasificador, altitud: int) -> int:
        r = clasificador.clasificar(hb_observada_ddl=150, altitud_msnm=altitud, edad_meses=12)
        return r.ajuste_ddl

    def test_0_msnm(self, clasificador):
        assert self._ajuste(clasificador, 0) == 0

    def test_499_msnm(self, clasificador):
        assert self._ajuste(clasificador, 499) == 0

    def test_500_msnm(self, clasificador):
        assert self._ajuste(clasificador, 500) == 4   # 0.4 g/dL → 4 ddl

    def test_999_msnm(self, clasificador):
        assert self._ajuste(clasificador, 999) == 4

    def test_1000_msnm(self, clasificador):
        assert self._ajuste(clasificador, 1000) == 8

    def test_1500_msnm(self, clasificador):
        assert self._ajuste(clasificador, 1500) == 11

    def test_2000_msnm(self, clasificador):
        assert self._ajuste(clasificador, 2000) == 14

    def test_2500_msnm(self, clasificador):
        assert self._ajuste(clasificador, 2500) == 18

    def test_3000_msnm(self, clasificador):
        assert self._ajuste(clasificador, 3000) == 21

    def test_3500_msnm(self, clasificador):
        assert self._ajuste(clasificador, 3500) == 25

    def test_4000_msnm(self, clasificador):
        assert self._ajuste(clasificador, 4000) == 29

    def test_4500_msnm(self, clasificador):
        assert self._ajuste(clasificador, 4500) == 33

    def test_4999_msnm(self, clasificador):
        assert self._ajuste(clasificador, 4999) == 33


# ─── Clasificación grupo 6–23 meses (altitud 0, sin ajuste) ──────────────────

class TestClasificacion6a23Meses:
    """
    Umbrales (sin ajuste, altitud 0):
      < 7.0   → SEVERA       (< 70 ddl)
      7.0–9.4 → MODERADA     (70–94 ddl)
      9.5–10.4→ LEVE          (95–104 ddl)
      ≥ 10.5  → SIN_ANEMIA   (≥ 105 ddl)
    """

    def test_severa_limite_superior(self, clasificador):
        # 6.9 g/dL = 69 ddl → SEVERA
        r = clasificador.clasificar(hb_observada_ddl=69, altitud_msnm=0, edad_meses=12)
        assert r.clasificacion == Clasificacion.SEVERA

    def test_frontera_severa_moderada(self, clasificador):
        # 7.0 g/dL = 70 ddl → MODERADA
        r = clasificador.clasificar(hb_observada_ddl=70, altitud_msnm=0, edad_meses=12)
        assert r.clasificacion == Clasificacion.MODERADA

    def test_moderada_interior(self, clasificador):
        r = clasificador.clasificar(hb_observada_ddl=80, altitud_msnm=0, edad_meses=12)
        assert r.clasificacion == Clasificacion.MODERADA

    def test_frontera_moderada_leve(self, clasificador):
        # 9.5 g/dL = 95 ddl → LEVE
        r = clasificador.clasificar(hb_observada_ddl=95, altitud_msnm=0, edad_meses=12)
        assert r.clasificacion == Clasificacion.LEVE

    def test_leve_interior(self, clasificador):
        r = clasificador.clasificar(hb_observada_ddl=100, altitud_msnm=0, edad_meses=12)
        assert r.clasificacion == Clasificacion.LEVE

    def test_frontera_leve_sin_anemia(self, clasificador):
        # 10.5 g/dL = 105 ddl → SIN_ANEMIA
        r = clasificador.clasificar(hb_observada_ddl=105, altitud_msnm=0, edad_meses=12)
        assert r.clasificacion == Clasificacion.SIN_ANEMIA

    def test_sin_anemia_interior(self, clasificador):
        r = clasificador.clasificar(hb_observada_ddl=130, altitud_msnm=0, edad_meses=23)
        assert r.clasificacion == Clasificacion.SIN_ANEMIA


# ─── Clasificación grupo 24–59 meses (altitud 0, sin ajuste) ─────────────────

class TestClasificacion24a59Meses:
    """
    Umbrales (sin ajuste):
      < 7.0    → SEVERA      (< 70 ddl)
      7.0–9.9  → MODERADA    (70–99 ddl)
      10.0–10.9→ LEVE         (100–109 ddl)
      ≥ 11.0   → SIN_ANEMIA  (≥ 110 ddl)
    """

    def test_severa(self, clasificador):
        r = clasificador.clasificar(hb_observada_ddl=65, altitud_msnm=0, edad_meses=36)
        assert r.clasificacion == Clasificacion.SEVERA

    def test_frontera_severa_moderada(self, clasificador):
        r = clasificador.clasificar(hb_observada_ddl=70, altitud_msnm=0, edad_meses=36)
        assert r.clasificacion == Clasificacion.MODERADA

    def test_frontera_moderada_leve(self, clasificador):
        # 10.0 g/dL = 100 ddl → LEVE
        r = clasificador.clasificar(hb_observada_ddl=100, altitud_msnm=0, edad_meses=36)
        assert r.clasificacion == Clasificacion.LEVE

    def test_frontera_leve_sin_anemia(self, clasificador):
        # 11.0 g/dL = 110 ddl → SIN_ANEMIA
        r = clasificador.clasificar(hb_observada_ddl=110, altitud_msnm=0, edad_meses=36)
        assert r.clasificacion == Clasificacion.SIN_ANEMIA

    def test_limite_superior_grupo_59_meses(self, clasificador):
        r = clasificador.clasificar(hb_observada_ddl=115, altitud_msnm=0, edad_meses=59)
        assert r.clasificacion == Clasificacion.SIN_ANEMIA


# ─── Clasificación con ajuste de altitud ─────────────────────────────────────

class TestClasificacionConAjuste:
    def test_clasificacion_con_ajuste_alta_altitud(self, clasificador):
        # Hb observada 11.5 g/dL = 115 ddl, altitud 3271 m (rango 3000–3499: ajuste 2.1 = 21 ddl)
        # Hb ajustada = 115 - 21 = 94 ddl = 9.4 g/dL → MODERADA para grupo 6-23 meses
        r = clasificador.clasificar(hb_observada_ddl=115, altitud_msnm=3271, edad_meses=12)
        assert r.clasificacion == Clasificacion.MODERADA
        assert r.ajuste_ddl == 21
        assert r.hb_ajustada_ddl == 94

    def test_hb_ajustada_negativa(self, clasificador):
        # Hb observada muy baja + altitud alta → negativa → NO_EVALUABLE
        r = clasificador.clasificar(hb_observada_ddl=20, altitud_msnm=4500, edad_meses=12)
        assert r.clasificacion == Clasificacion.NO_EVALUABLE
        assert r.hb_ajustada_ddl < 0
        assert len(r.advertencias) > 0

    def test_version_normativa(self, clasificador):
        r = clasificador.clasificar(hb_observada_ddl=105, altitud_msnm=0, edad_meses=12)
        assert r.version_normativa == "v1"


# ─── Límites de grupo de edad ─────────────────────────────────────────────────

class TestLimitesGrupoEdad:
    def test_exactamente_seis_meses(self, clasificador):
        r = clasificador.clasificar(hb_observada_ddl=105, altitud_msnm=0, edad_meses=6)
        assert r.clasificacion != Clasificacion.NO_EVALUABLE

    def test_exactamente_veinticuatro_meses(self, clasificador):
        # Frontera: 24 meses entra en el grupo 24-59
        r = clasificador.clasificar(hb_observada_ddl=110, altitud_msnm=0, edad_meses=24)
        assert r.clasificacion == Clasificacion.SIN_ANEMIA  # ≥ 11.0

    def test_veintitre_meses_grupo_6_23(self, clasificador):
        # 23 meses: grupo 6-23; 10.5 g/dL → SIN_ANEMIA (≥ 10.5)
        r = clasificador.clasificar(hb_observada_ddl=105, altitud_msnm=0, edad_meses=23)
        assert r.clasificacion == Clasificacion.SIN_ANEMIA

    def test_veintitre_meses_umbral_diferente(self, clasificador):
        # 23 meses (grupo 6-23): 10.4 → LEVE; en grupo 24-59 sería MODERADA
        r = clasificador.clasificar(hb_observada_ddl=104, altitud_msnm=0, edad_meses=23)
        assert r.clasificacion == Clasificacion.LEVE

    def test_veinticuatro_meses_umbral_diferente(self, clasificador):
        # 24 meses (grupo 24-59): 9.4 g/dL = 94 ddl → MODERADA (< 10.0 g/dL)
        # En grupo 6-23, 94 ddl estaría en MODERADA también, pero el límite superior es 9.4
        # La distinción clave: en grupo 24-59, LEVE arranca en 10.0 (100 ddl), no 9.5 (95 ddl)
        r = clasificador.clasificar(hb_observada_ddl=94, altitud_msnm=0, edad_meses=24)
        assert r.clasificacion == Clasificacion.MODERADA


# ─── Bandas de altitud no verificadas (advertencia visible) ──────────────────

class ProveedorConBandaNoVerificada(ProveedorNormativoFake):
    def tabla_ajuste(self) -> list[dict]:
        tabla = [dict(f) for f in super().tabla_ajuste()]
        for fila in tabla:
            if fila["altitud_desde_msnm"] >= 4000:
                fila["verificada"] = False
        return tabla


class TestBandaNoVerificada:
    def test_banda_no_verificada_emite_advertencia(self):
        clasificador = ClasificadorHemoglobina(ProveedorConBandaNoVerificada())
        r = clasificador.clasificar(hb_observada_ddl=140, altitud_msnm=4107, edad_meses=30)
        assert r.clasificacion == Clasificacion.SIN_ANEMIA
        assert any("no verificada" in a for a in r.advertencias)

    def test_banda_verificada_sin_advertencia(self):
        clasificador = ClasificadorHemoglobina(ProveedorConBandaNoVerificada())
        r = clasificador.clasificar(hb_observada_ddl=140, altitud_msnm=3271, edad_meses=30)
        assert r.advertencias == []

    def test_normativa_real_marca_bandas_sobre_4000(self):
        from pathlib import Path

        from anemia_junin.adapters.outbound.normativa.proveedor import ProveedorNormativoJSON

        ruta = Path(__file__).parents[2] / "config" / "normativa_v1.json"
        tabla = ProveedorNormativoJSON(ruta).tabla_ajuste()
        no_verificadas = [f["altitud_desde_msnm"] for f in tabla if f.get("verificada") is False]
        assert no_verificadas == [4000, 4500]
