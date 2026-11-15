"""Genera las evidencias del laboratorio 13 (gestión de la configuración).

Dos tipos de evidencia, guardadas en ``evidencias/``:

* ``web_*.png``: capturas de las páginas públicas del repositorio en GitHub
  (Issues, Pull requests, Actions, Releases, ramas, archivos de configuración).
* ``cli_*.png``: salida real de comandos ``git`` y ``gh`` ejecutados sobre el
  repositorio, renderizada como terminal. Prueban lo que la interfaz web no
  muestra sin permisos de administrador (ruleset, auditoría de revisiones).

Uso (desde la raíz del repositorio, con Playwright y Microsoft Edge):
    pmv_fastapi/.venv/Scripts/python.exe entregables/semana-13/laboratorio-scm/capturar_evidencias_scm.py [--solo web|cli]

Requiere ``gh`` autenticado (basta permiso de lectura). No escribe nada en GitHub.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
SALIDA = AQUI / "evidencias"
REPO = "woshtsu/ProcesosSoftwareAnemia"
URL = f"https://github.com/{REPO}"
API = f"repos/{REPO}"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# (archivo, url, alto máximo en px o None para el viewport, selector a esperar)
WEB = [
    ("web_a1_issue_rfc_18", f"{URL}/issues/18", 1500, None),
    ("web_a1_lista_rfc", f"{URL}/issues?q=label%3Achange-request", 900, None),
    ("web_a1_plantilla_rfc", f"{URL}/blob/main/.github/ISSUE_TEMPLATE/change_request.md", 1400, None),
    ("web_a1_etiquetas", f"{URL}/labels", 1000, None),
    ("web_a2_plantilla_pr", f"{URL}/blob/main/.github/PULL_REQUEST_TEMPLATE.md", 1200, None),
    ("web_a2_pr13_conversacion", f"{URL}/pull/13", 1700, None),
    ("web_a2_pr13_checks", f"{URL}/pull/13/checks", 900, None),
    ("web_a2_pr9_aprobada", f"{URL}/pull/9", 1500, None),
    ("web_a2_lista_pr", f"{URL}/pulls?q=is%3Apr", 1400, None),
    ("web_a2_contributing", f"{URL}/blob/main/CONTRIBUTING.md", 1600, None),
    ("web_a3_ramas", f"{URL}/branches/all", 1400, None),
    ("web_a3_red", f"{URL}/network", 900, "canvas"),
    ("web_a3_commits_main", f"{URL}/commits/main", 1400, None),
    ("web_a4_actions", f"{URL}/actions", 1300, None),
    ("web_a4_run_pr13", f"{URL}/actions/runs/42299328715", 1000, None),
    ("web_a4_run_produccion_fallida", f"{URL}/actions/runs/43447066462", 1000, None),
    ("web_a4_ci_yml", f"{URL}/blob/main/.github/workflows/ci.yml", 1600, None),
    ("web_a5_releases", f"{URL}/releases", 1700, None),
    ("web_a5_release_v1_0", f"{URL}/releases/tag/v1.0-PMV", 1400, None),
    ("web_a5_tags", f"{URL}/tags", 1000, None),
    # Acciones correctivas del 14/11/2026 (noche): GitFlow vía develop, CI, v4.0.1.
    ("web_m_pr28_sync_develop", f"{URL}/pull/28", 1100, None),
    ("web_m_pr29_t024_develop", f"{URL}/pull/29", 1700, None),
    ("web_m_run_pr29_falla_ruff", f"{URL}/actions/runs/43675155453", 900, None),
    ("web_m_run_pr29_verde", f"{URL}/actions/runs/43675249154", 900, None),
    ("web_m_release_v4_0_1", f"{URL}/releases/tag/v4.0.1", 1300, None),
    ("web_m_issue_rfc_18_aprobada", f"{URL}/issues/18", 900, None),
]


def _bash() -> str:
    """Bash de Git for Windows (en Linux/macOS, el del sistema)."""
    if sys.platform != "win32":
        return "bash"
    exec_path = subprocess.run(["git", "--exec-path"], capture_output=True, text=True).stdout.strip()
    for base in Path(exec_path).parents:
        candidato = base / "bin" / "bash.exe"
        if candidato.exists():
            return str(candidato)
    return "bash"


BASH = _bash()


def ejecutar(cmd: str) -> str:
    r = subprocess.run([BASH, "-c", cmd], cwd=RAIZ, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env={**__import__("os").environ, "GH_PAGER": "", "NO_COLOR": "1", "MSYS_NO_PATHCONV": "1"})
    return (r.stdout + r.stderr).rstrip()


def jq(endpoint: str, filtro: str) -> str:
    return f"gh api {endpoint} --jq '{filtro}'"


# (archivo, título, comandos). Cada comando se muestra con su salida real.
CLI = [
    ("cli_a1_rfc_issues", "Solicitudes de cambio (RFC) registradas en GitHub Issues", [
        f"gh issue list -R {REPO} --label change-request --state all",
    ]),
    ("cli_a1_plantilla_rfc", "Plantilla de solicitud de cambio en la línea base", [
        "git log -1 --format='%h %ad %s' --date=short origin/main -- .github/ISSUE_TEMPLATE/change_request.md",
        "git show origin/main:.github/ISSUE_TEMPLATE/change_request.md | head -n 30",
    ]),
    ("cli_a2_ruleset", "Regla de protección de la rama main (ruleset «ownermerge»)", [
        jq(f"{API}/rulesets/26248382",
           '{name, enforcement, ramas: .conditions.ref_name.include, reglas: [.rules[].type], '
           'pull_request: (.rules[] | select(.type == "pull_request").parameters '
           '| {required_approving_review_count, dismiss_stale_reviews_on_push, allowed_merge_methods}), '
           'excepciones: .bypass_actors, actualizado: .updated_at}'),
        jq(f"{API}/branches/main", "{rama: .name, protected}"),
    ]),
    ("cli_a2_auditoria_pr", "Auditoría de pull requests: revisión, issue vinculado y quién integra", [
        "gh pr list -R " + REPO + " --state merged --limit 30 --json number,headRefName,baseRefName,reviewDecision,mergedAt,body "
        "--jq '.[] | [.number, .headRefName + \" -> \" + .baseRefName, (if .reviewDecision == \"\" then \"SIN_REVISION\" else .reviewDecision end), "
        "(if (.body|test(\"(?i)(closes|fixes) #[0-9]+\")) then \"vinculada\" else \"-\" end), .mergedAt[:10]] | @tsv'",
    ]),
    ("cli_a2_plantilla_pr", "Plantilla de pull request con la Definición de Terminado", [
        "git show origin/main:.github/PULL_REQUEST_TEMPLATE.md",
    ]),
    ("cli_a3_gitflow_pmv", "GitFlow en el Incremento 1: feature/* y fix/* integradas en develop antes de la release", [
        "git log --graph --oneline --decorate=short 9ce90c3 -n 24",
    ]),
    ("cli_a3_main_directo", "Historial de primer padre de main: integraciones por PR frente a commits directos", [
        "git log --first-parent --format='%h %ad %s' --date=short origin/main -n 28",
    ]),
    ("cli_a3_indicadores", "Indicadores del proceso: integración por PR y commits convencionales, antes y desde el 06/11/2026", [
        "git log --first-parent --format='%ad|%s' --date=short origin/main | awk -F'|' "
        "'{pr=($2 ~ /\\(#[0-9]+\\)$/ || $2 ~ /^Merge pull request/); p=($1>=\"2026-11-06\")?\"desde_06-11\":\"antes_06-11\"; "
        "t[p]++; if(pr) v[p]++} END{for(p in t) printf \"%s  integraciones_en_main_por_PR: %d/%d\\n\", p, v[p], t[p]}'",
        "git log --all --no-merges --format='%ad|%s' --date=short | awk -F'|' "
        "'{c=($2 ~ /^(feat|fix|docs|chore|ci|build|test|perf|refactor|style|release)(\\([^)]*\\))?!?: /); "
        "p=($1>=\"2026-11-06\")?\"desde_06-11\":\"antes_06-11\"; t[p]++; if(c) v[p]++} "
        "END{for(p in t) printf \"%s  commits_convencionales: %d/%d (%.0f %%)\\n\", p, v[p], t[p], 100*v[p]/t[p]}'",
    ]),
    ("cli_a3_ramas", "Ramas remotas por tipo y estado de develop frente a main", [
        "git branch -r --format='%(refname:short)' | sed 's#origin/##' | grep -v -e HEAD -e '^origin$' | sort",
        "git rev-list --left-right --count origin/main...origin/develop   # main_adelante  develop_adelante",
    ]),
    ("cli_a4_runs", "Ejecuciones del pipeline de integración continua (GitHub Actions)", [
        f"gh run list -R {REPO} --limit 22",
    ]),
    ("cli_a4_jobs", "Trabajos del pipeline: calidad, imagen Docker y producción", [
        f"gh run view 42299328715 -R {REPO}",
        f"gh run view 43447066462 -R {REPO}",
    ]),
    ("cli_a4_ci_triggers", "Disparadores y trabajos del workflow ci.yml", [
        "git show origin/main:.github/workflows/ci.yml | sed -n '1,12p'",
        "git show origin/main:.github/workflows/ci.yml | grep -nE '^  [a-z-]+:$|needs:|name: (Ruff|Pruebas|Cobertura|Construir|Verificar)'",
    ]),
    ("cli_a5_tags", "Etiquetas semánticas anotadas por incremento", [
        "git tag -l -n1",
        "git show v1.0-PMV --no-patch --format='commit %h  %ad  %s' --date=short | tail -n 3",
    ]),
    ("cli_a5_releases", "Releases publicadas en GitHub", [
        f"gh release list -R {REPO}",
        jq(f"{API}/releases", '.[] | [.tag_name, .published_at[:10], (.assets|length|tostring) + " adjuntos", .html_url] | @tsv'),
    ]),
    ("cli_m_gitflow_develop", "GitFlow retomado: PR hacia develop y estado de develop frente a main", [
        f"gh pr list -R {REPO} --state merged --base develop --json number,title,headRefName,mergedAt,reviewDecision "
        "--jq '.[] | [.number, .headRefName + \" -> develop\", .title, .mergedAt[:10], (if .reviewDecision == \"\" then \"SIN_REVISION\" else .reviewDecision end)] | @tsv'",
        "git log --oneline -4 origin/develop",
        "git rev-list --left-right --count origin/main...origin/develop   # main_adelante  develop_adelante",
    ]),
    ("cli_m_rfc_evaluadas", "Evaluación registrada de las solicitudes de cambio (etiquetas)", [
        f"gh issue list -R {REPO} --label change-request --state all --json number,state,labels "
        "--jq '.[] | [.number, .state, ([.labels[].name] | join(\",\"))] | @tsv'",
    ]),
    ("cli_m_respaldo_y_artefactos", "Respaldo antes de borrar ramas y artefactos adjuntos a las releases", [
        "git ls-remote --heads origin",
        "git for-each-ref refs/tags/archivo --format='%(refname:short)  %(*objectname:short)  %(contents:subject)'",
        jq(f"{API}/releases", '.[] | select(.assets|length>0) | [.tag_name, (.assets[] | .name + \" (\" + (.size|tostring) + \" bytes)\")] | @tsv'),
    ]),
]


def capturar_web(navegador) -> None:
    ctx = navegador.new_context(viewport={"width": 1366, "height": 900}, device_scale_factor=1)
    pg = ctx.new_page()
    for nombre, url, alto, selector in WEB:
        try:
            pg.goto(url, wait_until="networkidle", timeout=60_000)
            if selector:
                pg.wait_for_selector(selector, timeout=30_000)
                pg.wait_for_timeout(3000)
            pg.wait_for_timeout(800)
            total = pg.evaluate("document.documentElement.scrollHeight")
            clip_alto = min(total, alto or 900)
            destino = SALIDA / f"{nombre}.png"
            pg.screenshot(path=str(destino), full_page=True,
                          clip={"x": 0, "y": 0, "width": 1366, "height": clip_alto})
            print(f"OK  {destino.name}  ({clip_alto}px)  {url}")
        except Exception as e:  # noqa: BLE001 - se informa y se sigue
            print(f"ERR {nombre}: {e}")
    ctx.close()


PLANTILLA = """<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#fff;font-family:Segoe UI,Arial,sans-serif}}
#t{{width:1180px;background:#0d1117;color:#c9d1d9;border-radius:8px;overflow:hidden;margin:10px}}
.bar{{background:#161b22;padding:8px 14px;font-size:13px;color:#8b949e;display:flex;gap:8px;align-items:center}}
.dot{{width:11px;height:11px;border-radius:50%;display:inline-block}}
pre{{margin:0;padding:12px 16px 16px;font:12.5px/1.42 Consolas,'Cascadia Mono',monospace;white-space:pre-wrap;word-break:break-all}}
.p{{color:#7ee787}} .c{{color:#79c0ff}} .m{{color:#8b949e}}
</style></head><body><div id="t"><div class="bar"><span class="dot" style="background:#ff5f56"></span>
<span class="dot" style="background:#ffbd2e"></span><span class="dot" style="background:#27c93f"></span>
<b style="color:#c9d1d9;margin-left:8px">{titulo}</b><span style="margin-left:auto">{fecha}</span></div>
<pre>{cuerpo}</pre></div></body></html>"""


def presentar(salida: str) -> str:
    """Solo formato: indenta JSON y alinea columnas separadas por tabulador."""
    try:
        texto = json.dumps(json.loads(salida), ensure_ascii=False, indent=2)
        # Listas de valores simples en una sola línea.
        return re.sub(r"\[\s+([^\[\]{}]*?)\s+\]",
                      lambda m: "[" + ", ".join(x.strip() for x in m.group(1).split(",")) + "]", texto)
    except ValueError:
        pass
    filas = [l.split("\t") for l in salida.splitlines()]
    if sum(len(f) > 1 for f in filas) >= 2:
        anchos = [max(len(f[i]) for f in filas if i < len(f)) for i in range(max(map(len, filas)))]
        return "\n".join("  ".join(c.ljust(anchos[i]) for i, c in enumerate(f)).rstrip() for f in filas)
    return salida


def capturar_cli(navegador) -> None:
    pg = navegador.new_page(viewport={"width": 1210, "height": 800})
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M") + " · ProcesosSoftwareAnemia"
    registro = {}
    for nombre, titulo, comandos in CLI:
        partes = []
        for cmd in comandos:
            salida = ejecutar(cmd)
            registro.setdefault(nombre, []).append({"comando": cmd, "salida": salida})
            salida = presentar(salida)
            lineas = salida.splitlines()
            if len(lineas) > 60:
                salida = "\n".join(lineas[:60]) + f"\n… ({len(lineas) - 60} líneas más)"
            partes.append(f'<span class="p">$</span> <span class="c">{html.escape(cmd)}</span>\n{html.escape(salida)}')
        pg.set_content(PLANTILLA.format(titulo=html.escape(titulo), fecha=fecha, cuerpo="\n\n".join(partes)))
        destino = SALIDA / f"{nombre}.png"
        pg.locator("#t").screenshot(path=str(destino))
        print(f"OK  {destino.name}")
    (SALIDA / "salidas_cli.json").write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
    pg.close()


def main() -> None:
    global SALIDA, WEB, CLI
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", choices=["web", "cli"])
    ap.add_argument("--salida", help="carpeta de salida (por defecto evidencias/)")
    ap.add_argument("--filtro", help="solo las evidencias cuyo nombre contiene este texto")
    a = ap.parse_args()
    if a.salida:
        SALIDA = Path(a.salida).resolve()
    if a.filtro:
        WEB = [w for w in WEB if a.filtro in w[0]]
        CLI = [c for c in CLI if a.filtro in c[0]]
    SALIDA.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "fetch", "-q", "--tags", "origin"], cwd=RAIZ, check=False)
    with sync_playwright() as p:
        nav = p.chromium.launch(channel="msedge", headless=True)
        if a.solo != "cli":
            capturar_web(nav)
        if a.solo != "web":
            capturar_cli(nav)
        nav.close()


if __name__ == "__main__":
    main()
