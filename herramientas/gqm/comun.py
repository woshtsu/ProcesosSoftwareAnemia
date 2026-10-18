"""Utilidades comunes de las herramientas GQM (análisis estático por AST, solo biblioteca estándar).

Define dónde está cada capa hexagonal en cada versión evaluada y cómo clasificar una importación.
Las rutas de las versiones se pueden cambiar con las variables de entorno GQM_RAIZ_V10 (por omisión, ../inc1_v1.0_PMV respecto de la raíz del repositorio;
se crea con «git worktree add ../inc1_v1.0_PMV v1.0-PMV»), GQM_RAIZ_V15 (por omisión, ../v15_export/pmv_fastapi: copia del avance v1.5, se crea con
«git archive v1.5.0-inc2-avance pmv_fastapi | tar -x -C ../v15_export») y GQM_RAIZ_V20 (por omisión, pmv_fastapi/, la versión actual 2.0.0-inc2).
"""

from __future__ import annotations

import ast
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
METRICAS = REPO / "entregables" / "semana-09" / "metricas"
DATOS = METRICAS / "datos"
SALIDAS = METRICAS / "salidas"

RAICES = {
    "v1.0": Path(os.getenv("GQM_RAIZ_V10", str(REPO.parent / "inc1_v1.0_PMV"))),
    "v1.5": Path(os.getenv("GQM_RAIZ_V15", str(REPO.parent / "v15_export" / "pmv_fastapi"))),
    "v2.0": Path(os.getenv("GQM_RAIZ_V20", str(REPO / "pmv_fastapi"))),
}
ETIQUETA = {
    "v1.0": "v1.0-PMV (Inc. 1)",
    "v1.5": "v1.5.0-inc2-avance (avance del Inc. 2)",
    "v2.0": "v2.0.0-inc2 (Inc. 2, cierre)",
}
VERSIONES = ["v1.0", "v1.5", "v2.0"]

# Capas por versión: nombre -> lista de rutas (relativas a la raíz de la versión; carpeta o archivo .py).
CAPAS = {
    "v1.0": {
        "dominio": ["app/domain"],
        "puertos_entrada": [],  # no existen en el Inc. 1
        "puertos_salida": ["app/application/puertos.py"],
        "aplicacion": ["app/application/casos_uso.py"],
        "adaptadores_entrada": ["app/adapters/entrada"],
        "adaptadores_salida": ["app/adapters/salida"],
        "composicion": ["app/main.py"],
    },
    "v1.5": {
        "dominio": ["app/domain/model", "app/domain/service"],
        "puertos_entrada": ["app/ports/inbound"],
        "puertos_salida": ["app/ports/outbound"],
        "aplicacion": ["app/application"],
        "adaptadores_entrada": ["app/adapters/inbound"],
        "adaptadores_salida": ["app/adapters/outbound"],
        "composicion": ["app/main.py"],
    },
}
CAPAS["v2.0"] = CAPAS["v1.5"]  # misma estructura hexagonal (ADR-008)
NOMBRE_CAPA = {
    "dominio": "Núcleo de dominio",
    "puertos_entrada": "Puertos de entrada",
    "puertos_salida": "Puertos de salida",
    "aplicacion": "Aplicación (casos de uso)",
    "adaptadores_entrada": "Adaptadores de entrada",
    "adaptadores_salida": "Adaptadores de salida",
    "composicion": "Raíz de composición",
}
STDLIB = set(sys.stdlib_module_names)


def archivos_py(raiz: Path, rutas: list[str]) -> list[Path]:
    """Archivos .py (sin __init__.py vacío no se excluye aquí: se filtra por quien lo necesite)."""
    salida: list[Path] = []
    for r in rutas:
        p = raiz / r
        if p.is_file():
            salida.append(p)
        elif p.is_dir():
            salida += sorted(x for x in p.rglob("*.py") if "__pycache__" not in x.parts)
    return salida


def modulo_de(raiz: Path, archivo: Path) -> str:
    rel = archivo.relative_to(raiz).with_suffix("")
    partes = list(rel.parts)
    if partes[-1] == "__init__":
        partes = partes[:-1]
    return ".".join(partes)


def existe_modulo(raiz: Path, nombre: str) -> bool:
    p = raiz / Path(*nombre.split("."))
    return p.with_suffix(".py").is_file() or p.is_dir()


@dataclass
class Importacion:
    archivo: str  # relativo a la raíz
    linea: int
    modulo: str  # módulo resuelto (para 'from a import b' donde a.b es módulo, se resuelve a 'a.b')
    texto: str  # línea original
    tipo: str  # stdlib | interno | externo

    @property
    def raiz_modulo(self) -> str:
        return self.modulo.split(".")[0]


def clasificar(modulo: str) -> str:
    raiz = modulo.split(".")[0]
    if raiz == "app" or modulo.startswith("."):
        return "interno"
    if raiz in STDLIB or raiz == "__future__":
        return "stdlib"
    return "externo"


def importaciones(raiz: Path, archivo: Path) -> list[Importacion]:
    """Todas las importaciones de un archivo (incluye las anidadas en funciones)."""
    texto = archivo.read_text(encoding="utf-8")
    lineas = texto.splitlines()
    rel = str(archivo.relative_to(raiz))
    encontradas: list[Importacion] = []
    for nodo in ast.walk(ast.parse(texto)):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                encontradas.append(
                    Importacion(rel, nodo.lineno, alias.name, lineas[nodo.lineno - 1].strip(), clasificar(alias.name))
                )
        elif isinstance(nodo, ast.ImportFrom):
            base = "." * nodo.level + (nodo.module or "")
            for alias in nodo.names:
                candidato = f"{base}.{alias.name}"
                modulo = candidato if nodo.level == 0 and existe_modulo(raiz, candidato) else base
                encontradas.append(
                    Importacion(rel, nodo.lineno, modulo, lineas[nodo.lineno - 1].strip(), clasificar(base))
                )
    # Una sentencia 'from m import a, b' cuenta como UNA importación del módulo m.
    unicas = {(i.archivo, i.linea, i.modulo): i for i in encontradas}
    return sorted(unicas.values(), key=lambda i: (i.archivo, i.linea, i.modulo))


def clases(archivo: Path) -> list[ast.ClassDef]:
    return [n for n in ast.walk(ast.parse(archivo.read_text(encoding="utf-8"))) if isinstance(n, ast.ClassDef)]


def capa_de_modulo(version: str, raiz: Path, modulo: str) -> str | None:
    """Capa a la que pertenece un módulo interno (según CAPAS); None si no pertenece a ninguna."""
    mejor, largo = None, -1
    for capa, rutas in CAPAS[version].items():
        for r in rutas:
            pref = ".".join(Path(r).with_suffix("").parts)
            if (modulo == pref or modulo.startswith(pref + ".")) and len(pref) > largo:
                mejor, largo = capa, len(pref)
    return mejor


def lineas_codigo(archivo: Path) -> int:
    """Líneas no vacías que no son comentarios puros (cuenta docstrings), criterio de los registros de defectos."""
    return sum(1 for ln in archivo.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#"))


def lineas_codigo_sin_docstrings(archivo: Path) -> int:
    texto = archivo.read_text(encoding="utf-8")
    arbol = ast.parse(texto)
    excluir: set[int] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            cuerpo = nodo.body
            if cuerpo and isinstance(cuerpo[0], ast.Expr) and isinstance(getattr(cuerpo[0], "value", None), ast.Constant):
                if isinstance(cuerpo[0].value.value, str):
                    excluir.update(range(cuerpo[0].lineno, cuerpo[0].end_lineno + 1))
    return sum(
        1
        for i, ln in enumerate(texto.splitlines(), 1)
        if ln.strip() and not ln.strip().startswith("#") and i not in excluir
    )


@dataclass
class Resultado:
    datos: dict = field(default_factory=dict)


def fusionar_json(ruta: Path, nuevo: dict) -> dict:
    """Escribe ``nuevo`` en ``ruta`` conservando las claves (versiones) ya medidas que no se recalculan."""
    previo = {}
    if ruta.exists():
        previo = json.loads(ruta.read_text(encoding="utf-8"))
    previo.update(nuevo)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(previo, ensure_ascii=False, indent=2), encoding="utf-8")
    return previo


def ruta_rel(ruta: Path) -> str:
    """Ruta para mostrar en las salidas: relativa a la raíz del repositorio (sin rutas absolutas de la máquina)."""
    try:
        return ruta.resolve().relative_to(REPO).as_posix() or "."
    except ValueError:
        return os.path.relpath(ruta.resolve(), REPO).replace(os.sep, "/")
