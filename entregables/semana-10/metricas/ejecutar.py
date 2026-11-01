"""Ejecuta un comando, guarda su salida cruda (saneada) y la renderiza como captura PNG con pie de trazabilidad.

Uso (desde la raiz del repositorio):
    python entregables/semana-10/metricas/ejecutar.py ID "Titulo" --cwd pmv_fastapi [--max-lineas 60] -- comando args...

Genera:
    entregables/semana-10/metricas/salidas/ID.txt        salida cruda (stdout+stderr)
    entregables/semana-10/metricas/salidas/ID.meta.json  comando, fecha, commit, codigo de salida, duracion
    entregables/semana-10/evidencias/terminal/ID.png     captura de la salida (fuente monoespaciada)
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
BASE = RAIZ / "entregables" / "semana-10"
SALIDAS = BASE / "metricas" / "salidas"
TERMINAL = BASE / "evidencias" / "terminal"
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def sanear(texto: str) -> str:
    """Quita secuencias ANSI y rutas absolutas de la maquina de medicion."""
    texto = ANSI.sub("", texto)
    texto = texto.replace(str(RAIZ), "<repo>")
    texto = re.sub(r"/[\w./-]*venv[\w./-]*?/(bin|lib)/", r"<venv>/\1/", texto)
    texto = re.sub(r"/home/\w+/", "<home>/", texto)
    return texto


def commit() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()


PLANTILLA = """<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#0f172a;font-family:'DejaVu Sans Mono','Liberation Mono',monospace;color:#e2e8f0}}
.barra{{background:#1e293b;padding:8px 14px;font-size:13px;color:#cbd5e1;border-bottom:1px solid #334155}}
.barra b{{color:#fff}}
pre{{margin:0;padding:12px 14px;font-size:12.5px;line-height:1.38;white-space:pre-wrap;word-break:break-all}}
.pie{{background:#1e293b;padding:7px 14px;font-size:11.5px;color:#94a3b8;border-top:1px solid #334155}}
.omit{{color:#fbbf24}}
</style></head><body>
<div class="barra"><b>{titulo}</b></div>
<pre>{cuerpo}</pre>
<div class="pie">$ {cmd}<br>cwd: {cwd} &nbsp;|&nbsp; fecha: {fecha} &nbsp;|&nbsp; commit: {commit} &nbsp;|&nbsp; salida: {rc} &nbsp;|&nbsp; duraci&oacute;n: {dur:.1f} s</div>
</body></html>"""


def renderizar(png: Path, titulo, lineas, meta, max_lineas):
    from playwright.sync_api import sync_playwright

    if len(lineas) > max_lineas:
        mitad = max_lineas // 2
        omitidas = len(lineas) - 2 * mitad
        lineas = lineas[:mitad] + [f"@@OMIT@@[... {omitidas} líneas omitidas en la captura; salida completa en metricas/salidas/{meta['id']}.txt ...]"] + lineas[-mitad:]
    cuerpo = "\n".join(
        f'<span class="omit">{html.escape(l[8:])}</span>' if l.startswith("@@OMIT@@") else html.escape(l[:230]) for l in lineas
    )
    doc = PLANTILLA.format(titulo=html.escape(titulo), cuerpo=cuerpo, cmd=html.escape(meta["comando"]), cwd=meta["cwd"], fecha=meta["fecha"], commit=meta["commit"], rc=f"c&oacute;digo {meta['codigo_salida']}", dur=meta["duracion_s"])
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(viewport={"width": 1100, "height": 400}, device_scale_factor=1.5)
        pg.set_content(doc)
        pg.screenshot(path=str(png), full_page=True)
        nav.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("titulo")
    ap.add_argument("--cwd", default="pmv_fastapi")
    ap.add_argument("--max-lineas", type=int, default=60)
    ap.add_argument("--entorno", action="append", default=[], help="CLAVE=valor")
    ap.add_argument("--tail", type=int, default=0, help="si >0, la captura muestra solo las ultimas N lineas")
    argv = sys.argv[1:]
    corte = argv.index("--")
    a = ap.parse_args(argv[:corte])
    cmd = argv[corte + 1 :]
    env = {**os.environ, **dict(e.split("=", 1) for e in a.entorno)}
    t0 = time.time()
    r = subprocess.run(cmd, cwd=RAIZ / a.cwd, env=env, capture_output=True, text=True)
    dur = time.time() - t0
    texto = sanear(r.stdout + (("\n" + r.stderr) if r.stderr else ""))
    SALIDAS.mkdir(parents=True, exist_ok=True)
    TERMINAL.mkdir(parents=True, exist_ok=True)
    (SALIDAS / f"{a.id}.txt").write_text(texto, encoding="utf-8")
    mostrado = " ".join(["python" if c == sys.executable else sanear(c) for c in cmd])
    mostrado = " ".join(a.entorno) + " " + mostrado if a.entorno else mostrado
    meta = {"id": a.id, "titulo": a.titulo, "comando": mostrado.strip(), "cwd": a.cwd, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "commit": commit(), "codigo_salida": r.returncode, "duracion_s": round(dur, 1)}
    (SALIDAS / f"{a.id}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    lineas = texto.rstrip("\n").split("\n")
    if a.tail:
        lineas = lineas[-a.tail:]
    renderizar(TERMINAL / f"{a.id}.png", a.titulo, lineas, meta, a.max_lineas)
    print(f"{a.id}: codigo {r.returncode}, {len(texto.splitlines())} lineas, {dur:.1f}s")
    sys.exit(0)


if __name__ == "__main__":
    main()
