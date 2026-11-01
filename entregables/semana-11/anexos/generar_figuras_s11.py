"""Genera las figuras nuevas del informe S11 (actualizacion al 30/10/2026).

Uso (desde la raiz del repositorio, con el entorno virtual y PLAYWRIGHT_BROWSERS_PATH definidos):
    python entregables/semana-11/anexos/generar_figuras_s11.py

Produce en entregables/semana-11/evidencias/ cuatro PNG de <= 300 KB (cuantizados a 256 colores):
    CMMI01_niveles_antes_despues.png   niveles de capacidad S11 -> 30/10/2026 (grafico)
    CMMI02_hitos_plan_vs_real.png      hitos H2, H3 y H4: fecha del plan frente a la fecha real (grafico)
    CMMI03_higiene_repositorio.png     captura de terminal: artefactos de proceso presentes o ausentes
    CMMI04_regresion_revision_independiente.png  captura de terminal: pruebas de regresion de la revision independiente
    CMMI05_carga_p95_v4.png            captura de terminal: p95 de la corrida de carga de la adenda v4
"""

import html
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[3]
DESTINO = RAIZ / "entregables" / "semana-11" / "evidencias"
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def sanear(t: str) -> str:
    t = ANSI.sub("", t).replace(str(RAIZ), "<repo>")
    t = re.sub(r"/[\w./-]*venv[\w./-]*?/(bin|lib)/", r"<venv>/\1/", t)
    return re.sub(r"/home/\w+/", "<home>/", t)


def optimizar(png: Path) -> None:
    im = Image.open(png).convert("RGB")
    im.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(png, optimize=True)
    kb = png.stat().st_size / 1024
    assert kb <= 300, f"{png.name} pesa {kb:.0f} KB"
    print(f"{png.name}: {kb:.0f} KB")


def commit() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()


PLANTILLA = """<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#0f172a;font-family:'DejaVu Sans Mono','Liberation Mono',monospace;color:#e2e8f0}}
.barra{{background:#1e293b;padding:8px 14px;font-size:13px;color:#fff;font-weight:bold;border-bottom:1px solid #334155}}
pre{{margin:0;padding:12px 14px;font-size:12.5px;line-height:1.38;white-space:pre-wrap;word-break:break-all}}
.pie{{background:#1e293b;padding:7px 14px;font-size:11.5px;color:#94a3b8;border-top:1px solid #334155}}
</style></head><body><div class="barra">{titulo}</div><pre>{cuerpo}</pre>
<div class="pie">$ {cmd}<br>cwd: {cwd} &nbsp;|&nbsp; fecha: {fecha} &nbsp;|&nbsp; commit: {commit} &nbsp;|&nbsp; salida: c&oacute;digo {rc}</div></body></html>"""


def captura_terminal(nombre, titulo, comando, mostrado, cwd=".", entorno=None, max_lineas=50):
    env = {**os.environ, **(entorno or {})}
    comando = re.sub(r"^python ", f"{sys.executable} ", comando)
    r = subprocess.run(comando, cwd=RAIZ / cwd, env=env, capture_output=True, text=True, shell=True, executable="/bin/bash")
    texto = sanear(r.stdout + r.stderr).rstrip("\n")
    lineas = texto.split("\n")
    if len(lineas) > max_lineas:
        lineas = lineas[: max_lineas // 2] + [f"[... {len(lineas) - max_lineas} lineas omitidas ...]"] + lineas[-(max_lineas // 2) :]
    doc = PLANTILLA.format(
        titulo=html.escape(titulo),
        cuerpo=html.escape("\n".join(l[:200] for l in lineas)),
        cmd=html.escape(mostrado),
        cwd=cwd,
        fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        commit=commit(),
        rc=r.returncode,
    )
    from playwright.sync_api import sync_playwright

    png = DESTINO / f"{nombre}.png"
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(viewport={"width": 1100, "height": 100}, device_scale_factor=1.3)
        pg.set_content(doc)
        pg.screenshot(path=str(png), full_page=True)
        nav.close()
    optimizar(png)


def grafico_niveles():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    areas = ["ESTIM", "PLAN", "PQA", "CM", "VER", "VAL", "CAR"]
    s11 = [1, 2, 1, 2, 2, 1, None]
    hoy = [1, 2, 1, 2, 2, 1, 1]
    x = list(range(len(areas)))
    fig, ax = plt.subplots(figsize=(8.6, 4.2), dpi=110)
    ax.bar([i - 0.2 for i in x], [v or 0 for v in s11], 0.38, color="#9db4d1", label="Informe S11 (30/10/2026, v2.0 + login)")
    ax.bar([i + 0.2 for i in x], hoy, 0.38, color="#1f4e8c", label="Actualizado (30/10/2026, v4.0-Inc4)")
    for i, v in enumerate(s11):
        ax.text(i - 0.2, (v or 0) + 0.06, "n/e" if v is None else str(v), ha="center", fontsize=9)
    for i, v in enumerate(hoy):
        ax.text(i + 0.2, v + 0.06, str(v), ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x, areas)
    ax.set_yticks([0, 1, 2, 3], ["0 Incompleto", "1 Ejecutado", "2 Gestionado", "3 Definido"])
    ax.set_ylim(0, 3.3)
    ax.set_title("Nivel de capacidad CMMI por área de práctica (n/e: no evaluada en S11)", fontsize=10.5)
    ax.legend(loc="upper right", fontsize=8.5, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, 0.01, "Fuente: Tabla 6 del informe. Ningún área cambia de nivel; CAR se evalúa por primera vez (PQA sigue en 1: Figuras 54 y 59).", fontsize=7.5, color="#475569")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    png = DESTINO / "CMMI01_niveles_antes_despues.png"
    fig.savefig(png)
    optimizar(png)


def grafico_hitos():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    hitos = [
        ("H2 · INC-2 (Sprint 3)", date(2026, 10, 12), date(2026, 10, 17)),
        ("H3 · INC-3 (Sprint 4)", date(2026, 10, 26), date(2026, 10, 30)),
        ("H4 · INC-4 (Sprint 5)", date(2026, 11, 9), date(2026, 10, 30)),
    ]
    fig, ax = plt.subplots(figsize=(8.6, 3.6), dpi=110)
    for i, (nombre, plan, real) in enumerate(hitos):
        y = len(hitos) - 1 - i
        d = (real - plan).days
        ax.plot([plan, real], [y, y], color="#c0392b" if d > 0 else "#1e8449", lw=3, zorder=1)
        ax.scatter([plan], [y], s=70, marker="D", color="#475569", zorder=2, label="Fecha del plan (S3-4)" if i == 0 else None)
        ax.scatter([real], [y], s=70, marker="o", color="#1f4e8c", zorder=2, label="Fecha real (commit)" if i == 0 else None)
        ax.text(max(plan, real), y + 0.17, f"{'+' if d > 0 else ''}{d} días", ha="center", fontsize=9, fontweight="bold")
    ax.set_yticks(range(len(hitos)), [h[0] for h in reversed(hitos)])
    ax.set_ylim(-0.9, 2.7)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=4))
    ax.grid(axis="x", color="#e2e8f0")
    ax.set_title("Hitos del plan frente a la fecha real (desviación en días calendario)", fontsize=10.5)
    ax.legend(loc="lower left", fontsize=8.5, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, 0.01, "Fuentes: S3-4 (Tabla 23); S9 (Tabla 6); commits fb26626 (18/10), e920820 y 5c1f1eb (30/10). H3 sin aceptación en la posta.", fontsize=7.2, color="#475569")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    png = DESTINO / "CMMI02_hitos_plan_vs_real.png"
    fig.savefig(png)
    optimizar(png)


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    grafico_niveles()
    grafico_hitos()
    higiene = (
        'for f in .github/pull_request_template.md .pre-commit-config.yaml CONTRIBUTING.md .github/CODEOWNERS .github/dependabot.yml; '
        'do if [ -e "$f" ]; then echo "EXISTE     $f"; else echo "NO EXISTE  $f"; fi; done; '
        'echo "contenido de .github/: $(ls .github | tr \'\\n\' \' \')"; '
        'echo "sonar.organization sin definir: $(grep -c REEMPLAZAR_ORGANIZACION pmv_fastapi/sonar-project.properties) coincidencia"; '
        'echo "commits desde la evaluacion S11 (72e7025..HEAD): $(git rev-list --count 72e7025..HEAD)"; '
        'echo "ADR en pmv_fastapi/docs/adr: $(ls pmv_fastapi/docs/adr | grep -c ^ADR-)"; '
        'echo "C4_componentes.puml, menciones de agenda/visita/notificador/sincroniz: $(grep -ciE \'agenda|visita|notificador|sincroniz\' pmv_fastapi/docs/diagramas/C4_componentes.puml)"; '
        'echo "registro de defectos, ultimo identificador: $(grep -rhoE \'DEF-[0-9]+\' pmv_fastapi/docs/evidencias/registro_defectos*.md | sort -u | tail -1)"; '
        'echo "TABLERO.md, coincidencias de \'horas reales\': $(grep -ciE \'horas reales\' coordinacion/TABLERO.md)"'
    )
    captura_terminal(
        "CMMI03_higiene_repositorio",
        "Artefactos de proceso en el repositorio (PQA, CM, VER)",
        higiene,
        "test -e <artefacto>; ls .github; grep -c REEMPLAZAR_ORGANIZACION sonar-project.properties; git rev-list --count 72e7025..HEAD; ls docs/adr; grep -ciE <C4>; grep -oE DEF-[0-9]+ registro_defectos*.md; grep -ciE 'horas reales' TABLERO.md",
    )
    captura_terminal(
        "CMMI04_regresion_revision_independiente",
        "Pruebas de regresión de la revisión independiente (webhook, concurrencia, flujo de barrera de visita)",
        "python -m pytest tests/unitarias tests/integracion tests/e2e -v --no-cov -p no:cacheprovider -k 'cp264b or cp382b or cp357 or cp391b or cp396 or cp405'",
        "python -m pytest tests/unitarias tests/integracion tests/e2e -v --no-cov -p no:cacheprovider -k 'cp264b or cp382b or cp357 or cp391b or cp396 or cp405'",
        cwd="pmv_fastapi",
        entorno={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    carga = (
        "python -c \"import json;d=json.load(open('entregables/semana-09/metricas/salidas/m32_carga_v4.json'));"
        "print('Locust, 50 usuarios, 10/s, 60 s, mix comun, B150, AUTH_MODE=demo; una sola corrida, sin control de v1.0');print();"
        "[print(f\\\"{k:36s} n={v['solicitudes']:5d} fallos={v['fallos']} mediana={v['mediana_ms']:7.0f} ms  p95={v['p95_ms']:7.0f} ms  p99={v['p99_ms']:7.0f} ms\\\") "
        "for k,v in d['escenario']['corridas']['r1'].items()]\""
    )
    captura_terminal(
        "CMMI05_carga_p95_v4",
        "Corrida de carga de la adenda v4 (50 usuarios, 60 s, Inc. 4): p95 por endpoint",
        carga,
        "python -c <imprime m32_carga_v4.json, corrida r1>",
        max_lineas=60,
    )


if __name__ == "__main__":
    main()
