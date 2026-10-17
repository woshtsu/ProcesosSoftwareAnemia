"""CP-37 a CP-43: pruebas de arquitectura. Verifican por análisis estático (AST) la regla de dependencias de la
arquitectura de puertos y adaptadores (ADR-001 y ADR-008): las dependencias apuntan siempre hacia el dominio.

Solo se leen los ``import`` de cada módulo de ``app/``; no se importa ni se ejecuta nada.
"""

import ast
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
APP = RAIZ / "app"

FRAMEWORKS = {"fastapi", "pydantic", "sqlalchemy", "starlette", "uvicorn", "psycopg2"}
CAPAS_EXTERNAS = ("app.ports", "app.application", "app.adapters")
STDLIB = set(sys.stdlib_module_names)


def modulos(subruta: str) -> list[Path]:
    """Archivos .py de un paquete de ``app/`` (o el propio archivo si ``subruta`` termina en .py)."""
    destino = APP / subruta
    if destino.is_file():
        return [destino]
    return sorted(p for p in destino.rglob("*.py") if p.name != "__init__.py")


def importaciones(origen: str | Path) -> set[str]:
    """Nombres de módulo importados (absolutos) por un archivo o por un texto de código fuente."""
    texto = origen if isinstance(origen, str) else Path(origen).read_text(encoding="utf-8")
    encontrados: set[str] = set()
    for nodo in ast.walk(ast.parse(texto)):
        if isinstance(nodo, ast.Import):
            encontrados.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom):
            # Un import relativo (nivel > 0) ocultaría la capa de destino: se marca para que la prueba lo rechace.
            encontrados.add("." * nodo.level + (nodo.module or ""))
    return encontrados


def empieza_con(modulo: str, prefijos) -> bool:
    return any(modulo == p or modulo.startswith(p + ".") for p in prefijos)


def prohibidos(origen, prefijos) -> list[str]:
    return sorted(m for m in importaciones(origen) if empieza_con(m, prefijos))


def comprobar(subruta: str, prefijos) -> list[str]:
    """Violaciones «archivo -> módulo importado» de un paquete contra una lista de prefijos prohibidos."""
    return [f"{p.relative_to(APP)} -> {m}" for p in modulos(subruta) for m in prohibidos(p, prefijos)]


def test_cp37_el_dominio_no_depende_de_frameworks_ni_de_otras_capas():
    assert len(modulos("domain")) >= 10
    assert comprobar("domain", FRAMEWORKS | set(CAPAS_EXTERNAS)) == []


def test_cp38_los_puertos_solo_importan_dominio_stdlib_y_typing():
    assert len(modulos("ports")) >= 7
    violaciones = []
    for archivo in modulos("ports"):
        for modulo in importaciones(archivo):
            raiz = modulo.split(".")[0]
            if not (modulo.startswith("app.domain") or raiz in STDLIB):
                violaciones.append(f"{archivo.relative_to(APP)} -> {modulo}")
    assert violaciones == []


def test_cp39_la_aplicacion_no_importa_adaptadores_ni_frameworks():
    assert len(modulos("application")) >= 3
    assert comprobar("application", FRAMEWORKS | {"app.adapters"}) == []


def test_cp40_el_adaptador_de_entrada_no_importa_aplicacion_ni_adaptadores_de_salida():
    assert len(modulos("adapters/inbound")) >= 2
    assert comprobar("adapters/inbound", {"app.application", "app.adapters.outbound"}) == []
    # Solo habla con los puertos de entrada y con el modelo de dominio (nunca con servicios ni puertos de salida).
    permitidos = ("app.adapters.inbound", "app.ports.inbound", "app.domain.model")
    for archivo in modulos("adapters/inbound"):
        internos = [m for m in importaciones(archivo) if m == "app" or m.startswith(("app.", "."))]
        assert [m for m in internos if not empieza_con(m, permitidos)] == [], archivo.name


def test_cp41_el_adaptador_de_salida_no_importa_aplicacion_ni_adaptadores_de_entrada():
    assert len(modulos("adapters/outbound")) >= 3
    assert comprobar("adapters/outbound", {"app.application", "app.adapters.inbound"}) == []


def test_cp42_solo_main_conoce_a_la_vez_aplicacion_y_adaptadores():
    mixtos = []
    for archivo in sorted(APP.rglob("*.py")):
        if "web" in archivo.relative_to(APP).parts:
            continue
        modulos_importados = importaciones(archivo)
        usa_aplicacion = any(empieza_con(m, {"app.application"}) for m in modulos_importados)
        usa_adaptadores = any(empieza_con(m, {"app.adapters"}) for m in modulos_importados)
        if usa_aplicacion and usa_adaptadores:
            mixtos.append(str(archivo.relative_to(APP)))
    assert mixtos == ["main.py"]


def test_cp43_no_quedan_modulos_puente_en_las_rutas_anteriores():
    anteriores = [
        "adapters/entrada",
        "adapters/salida",
        "application/casos_uso.py",
        "application/puertos.py",
        "domain/entidades.py",
        "domain/errores.py",
        "domain/reglas_clinicas.py",
    ]
    assert [r for r in anteriores if (APP / r).exists()] == []


# --- El verificador debe detectar de verdad las violaciones (prueba de la prueba) -------------------------------------


@pytest.mark.parametrize(
    "codigo, esperado",
    [
        ("import fastapi", ["fastapi"]),
        ("from sqlalchemy.orm import Session", ["sqlalchemy.orm"]),
        ("from app.adapters.outbound import x", ["app.adapters.outbound"]),
        ("def f():\n    import psycopg2", ["psycopg2"]),
        ("from . import hermano", ["."]),
        ("import json\nfrom app.domain.model import x", []),
    ],
)
def test_el_verificador_detecta_importaciones_prohibidas(codigo, esperado):
    prefijos = FRAMEWORKS | set(CAPAS_EXTERNAS) | {"."}
    assert prohibidos(codigo, prefijos) == esperado


def test_el_prefijo_no_confunde_paquetes_con_nombre_parecido():
    assert not empieza_con("app.applications", {"app.application"})
    assert empieza_con("app.application.servicio_agenda", {"app.application"})
