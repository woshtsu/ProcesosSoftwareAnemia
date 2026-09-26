"""
Prueba de arquitectura — PMV Anemia Junín.

Verifica que las reglas de importación prohibidas no se violen:
- domain NO importa flask, sqlite3 ni adaptadores
- application NO importa flask, sqlite3 ni adaptadores
"""

from __future__ import annotations

import ast
from pathlib import Path

_SRC = Path(__file__).parents[2] / "src" / "anemia_junin"
_DOMAIN = _SRC / "domain"
_APPLICATION = _SRC / "application"


def _obtener_imports(archivo: Path) -> set[str]:
    """Extrae todos los módulos importados en un archivo Python."""
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    imports = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.module:
                imports.add(nodo.module.split(".")[0])
    return imports


def _archivos_python(directorio: Path) -> list[Path]:
    return [f for f in directorio.rglob("*.py") if f.name != "__init__.py"]


_PROHIBIDOS_DOMINIO = {"flask", "sqlite3", "waitress", "wtforms"}
_PROHIBIDOS_APLICACION = {"flask", "sqlite3", "waitress", "wtforms"}
_PROHIBIDO_ADAPTADORES = {"anemia_junin.domain", "anemia_junin.application"}


class TestDependenciasProhibidas:
    def test_dominio_no_importa_flask(self):
        errores = []
        for archivo in _archivos_python(_DOMAIN):
            imports = _obtener_imports(archivo)
            prohibidos_encontrados = imports & _PROHIBIDOS_DOMINIO
            if prohibidos_encontrados:
                errores.append(f"{archivo.name}: {prohibidos_encontrados}")
        assert errores == [], "El dominio importa módulos prohibidos:\n" + "\n".join(errores)

    def test_dominio_no_importa_adaptadores(self):
        errores = []
        for archivo in _archivos_python(_DOMAIN):
            contenido = archivo.read_text(encoding="utf-8")
            if "anemia_junin.adapters" in contenido:
                errores.append(archivo.name)
        assert errores == [], "El dominio importa adaptadores:\n" + "\n".join(errores)

    def test_aplicacion_no_importa_flask(self):
        errores = []
        for archivo in _archivos_python(_APPLICATION):
            imports = _obtener_imports(archivo)
            prohibidos_encontrados = imports & _PROHIBIDOS_APLICACION
            if prohibidos_encontrados:
                errores.append(f"{archivo.name}: {prohibidos_encontrados}")
        assert errores == [], "La aplicación importa módulos prohibidos:\n" + "\n".join(errores)

    def test_aplicacion_no_importa_sqlite(self):
        """La aplicación puede acceder a conn directamente en el caso de reporte (técnico),
        pero no debe importar sqlite3 directamente en los casos de uso puros."""
        errores = []
        casos_de_uso_dir = _APPLICATION / "casos_de_uso"
        for archivo in _archivos_python(casos_de_uso_dir):
            if archivo.name == "consultar_reporte.py":
                continue  # acceso técnico documentado en el ADR
            imports = _obtener_imports(archivo)
            if "sqlite3" in imports:
                errores.append(archivo.name)
        assert errores == [], "Casos de uso importan sqlite3 directamente:\n" + "\n".join(errores)

    def test_aplicacion_no_importa_adaptadores(self):
        errores = [
            archivo.name
            for archivo in _archivos_python(_APPLICATION)
            if "anemia_junin.adapters" in archivo.read_text(encoding="utf-8")
        ]
        assert errores == [], f"La aplicación importa adaptadores: {errores}"

    def test_adaptadores_de_entrada_no_conocen_los_de_salida(self):
        """Las rutas web/API solo hablan con casos de uso, nunca con SQLite ni la normativa."""
        errores = []
        for archivo in _archivos_python(_SRC / "adapters" / "inbound"):
            contenido = archivo.read_text(encoding="utf-8")
            if "anemia_junin.adapters.outbound" in contenido:
                errores.append(archivo.name)
        assert errores == [], f"Adaptadores de entrada importan los de salida: {errores}"

    def test_adaptadores_de_entrada_no_importan_sqlite(self):
        errores = [
            archivo.name
            for archivo in _archivos_python(_SRC / "adapters" / "inbound")
            if "sqlite3" in _obtener_imports(archivo)
        ]
        assert errores == [], f"Adaptadores de entrada importan sqlite3: {errores}"

    def test_bootstrap_es_unico_punto_de_cableado(self):
        """Solo bootstrap.py debería importar tanto dominio como adaptadores."""
        bootstrap = _SRC / "bootstrap.py"
        contenido = bootstrap.read_text(encoding="utf-8")
        assert "ProveedorNormativoJSON" in contenido, (
            "bootstrap debe importar el proveedor normativo"
        )
        assert "UnidadDeTrabajo" in contenido, "bootstrap debe importar la unidad de trabajo"
        assert "ClasificadorHemoglobina" in contenido, "bootstrap debe importar el clasificador"
