#!/usr/bin/env python3
"""
Genera todos los diagramas del proyecto Anemia Junín.

- Compila `diagramas/src/**/NN_*.puml` con PlantUML (local, sin servidores en línea)
  a `diagramas/png/NN_*.png` (alta resolución) y `diagramas/svg/NN_*.svg`.
- Ejecuta los generadores Python `diagramas/src/**/NN_*.py` (p. ej. burndown con
  matplotlib); cada script recibe `--png <ruta>` y `--svg <ruta>`.
- Los archivos que empiezan por `_` (p. ej. `_tema.puml`) son inclusiones y no se
  compilan. `diagramas/src/integrador/` (generador ReportLab heredado) se ignora.

Uso (desde la raíz del repositorio):
    python herramientas/diagramas/generar_diagramas.py            # todos
    python herramientas/diagramas/generar_diagramas.py 03 09_sec   # filtra por prefijo/nombre
    python herramientas/diagramas/generar_diagramas.py --dpi 300

Requisitos: Java 17+ y `herramientas/plantuml/plantuml.jar` (ver herramientas/README.md).
Variables opcionales: PLANTUML_JAR (ruta al jar), JAVA (ejecutable de Java), GRAPHVIZ_DOT.
Motor: Graphviz `dot` si está instalado (recomendado, mejor enrutamiento); si no, smetana.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SRC = RAIZ / "diagramas" / "src"
PNG = RAIZ / "diagramas" / "png"
SVG = RAIZ / "diagramas" / "svg"
BUILD = RAIZ / "diagramas" / "_build" / "plantuml"
JAR = Path(os.environ.get("PLANTUML_JAR", RAIZ / "herramientas" / "plantuml" / "plantuml.jar"))
JAVA = os.environ.get("JAVA", "java")
VENV_PY = RAIZ / "herramientas" / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

def buscar_dot() -> str | None:
    """Localiza Graphviz `dot` (PATH, GRAPHVIZ_DOT o ruta estándar de Windows)."""
    candidatos = [os.environ.get("GRAPHVIZ_DOT"), shutil.which("dot"),
                  "C:/Program Files/Graphviz/bin/dot.exe"]
    for c in candidatos:
        if c and Path(c).exists():
            return str(c)
    return None


PATRON = re.compile(r"^\d{2,3}_[A-Za-z0-9_]+$")
EXCLUIR_DIRS = {"integrador"}
MOTOR = "auto"  # "auto" (dot si existe, si no smetana) o "smetana"


def fuentes(ext: str, filtros: list[str]) -> list[Path]:
    salida = []
    for p in sorted(SRC.rglob(f"*{ext}")):
        if any(parte in EXCLUIR_DIRS for parte in p.relative_to(SRC).parts[:-1]):
            continue
        if p.name.startswith("_") or not PATRON.match(p.stem):
            continue
        if filtros and not any(p.stem.startswith(f) for f in filtros):
            continue
        salida.append(p)
    return salida


def comprobar_duplicados(archivos: list[Path]) -> None:
    vistos: dict[str, Path] = {}
    for p in archivos:
        if p.stem in vistos:
            sys.exit(f"ERROR: nombre base duplicado '{p.stem}': {vistos[p.stem]} y {p}")
        vistos[p.stem] = p


def plantuml(archivos: list[Path], formato: str, dpi: int) -> bool:
    """Compila en un directorio temporal y copia planos a png/ o svg/."""
    destino = PNG if formato == "png" else SVG
    tmp = BUILD / formato
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    cmd = [
        JAVA,
        "-Djava.awt.headless=true",
        "-DPLANTUML_LIMIT_SIZE=16384",
        "-jar", str(JAR),
        "-charset", "UTF-8",
        f"-t{formato}",
        "-o", str(tmp),
    ]
    if formato == "png":
        cmd.append(f"-Sdpi={dpi}")
    cmd += [str(a) for a in archivos]
    entorno = dict(os.environ)
    dot = buscar_dot() if MOTOR != "smetana" else None
    if dot:
        entorno["GRAPHVIZ_DOT"] = dot
        cmd[cmd.index("-charset"):cmd.index("-charset")] = ["-graphvizdot", dot, "-DDIAG_LAYOUT=dot"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=entorno)
    salida = (res.stdout + res.stderr).strip()
    if salida:
        print(salida)
    ok = res.returncode == 0
    # Archivos con error de sintaxis: PlantUML genera una imagen de error; no se copia.
    con_error = {Path(m).resolve() for m in re.findall(r"Error line \d+ in file: (.+)", salida)}
    destino.mkdir(parents=True, exist_ok=True)
    for a in archivos:
        generado = tmp / f"{a.stem}.{formato}"
        if a.resolve() in con_error:
            ok = False
            print(f"  [{formato}] ERROR DE SINTAXIS (no se copia) {a.relative_to(RAIZ)}")
        elif generado.exists():
            shutil.copy2(generado, destino / generado.name)
            print(f"  [{formato}] {destino.relative_to(RAIZ) / generado.name}")
        else:
            ok = False
            print(f"  [{formato}] FALLÓ {a.relative_to(RAIZ)}")
    return ok


def generadores_python(scripts: list[Path], dpi: int) -> bool:
    ok = True
    py = str(VENV_PY) if VENV_PY.exists() else sys.executable
    for s in scripts:
        png = PNG / f"{s.stem}.png"
        svg = SVG / f"{s.stem}.svg"
        res = subprocess.run([py, str(s), "--png", str(png), "--svg", str(svg), "--dpi", str(dpi)],
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode != 0:
            ok = False
            print(f"  [py] FALLÓ {s.relative_to(RAIZ)}\n{res.stdout}{res.stderr}")
        else:
            print(f"  [py] {png.relative_to(RAIZ)} · {svg.relative_to(RAIZ)}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("filtros", nargs="*", help="prefijos de nombre (p. ej. 03 o 09_secuencia)")
    ap.add_argument("--dpi", type=int, default=200, help="resolución de los PNG (defecto 200)")
    ap.add_argument("--motor", choices=["auto", "smetana"], default="auto",
                    help="auto: Graphviz dot si está instalado; smetana: motor interno")
    ap.add_argument("--solo", choices=["png", "svg"], help="generar un único formato")
    args = ap.parse_args()
    global MOTOR
    MOTOR = args.motor

    pumls = fuentes(".puml", args.filtros)
    pys = fuentes(".py", args.filtros)
    comprobar_duplicados(pumls + pys)
    if not pumls and not pys:
        print("No hay fuentes que coincidan.")
        return 1

    ok = True
    if pumls:
        if not JAR.exists():
            sys.exit(f"ERROR: no se encuentra {JAR}. Ver herramientas/README.md para obtenerlo.")
        dot = buscar_dot() if MOTOR != "smetana" else None
        print(f"PlantUML: {len(pumls)} fuente(s) · motor: {'Graphviz dot (' + dot + ')' if dot else 'smetana'}")
        for fmt in (["png", "svg"] if not args.solo else [args.solo]):
            ok &= plantuml(pumls, fmt, args.dpi)
    if pys:
        print(f"Python: {len(pys)} generador(es)")
        ok &= generadores_python(pys, args.dpi)

    print("OK" if ok else "Terminado CON ERRORES")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
