"""Genera las figuras derivadas de las mediciones (Locust, arbol hexagonal, resumen axe) como PNG con pie de trazabilidad.

Uso (raiz del repositorio): python entregables/semana-10/metricas/graficos.py
Entrada: metricas/salidas/*.csv|json y el arbol real de pmv_fastapi/app. Salida: evidencias/rendimiento, arquitectura y usabilidad.
"""

import csv
import html
import json
import subprocess
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[3]
BASE = RAIZ / "entregables" / "semana-10"
SAL = BASE / "metricas" / "salidas"
EV = BASE / "evidencias"
COMMIT = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
FECHA = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

CSS = """body{margin:0;font-family:'DejaVu Sans',Arial,sans-serif;color:#1B2B3A;background:#fff}
.t{padding:10px 16px;background:#1F4E79;color:#fff;font-size:15px;font-weight:bold}
.pie{padding:7px 16px;background:#EEF2F6;color:#445;font-size:11px;border-top:1px solid #ccd}
.c{padding:12px 16px}table{border-collapse:collapse;font-size:13px}td,th{border:1px solid #bcc7d3;padding:4px 9px;text-align:right}
th{background:#EAF2FB}td:first-child,th:first-child{text-align:left}.mono{font-family:'DejaVu Sans Mono',monospace;font-size:12.5px;line-height:1.35;white-space:pre}
.ok{background:#E3F4E8}.mal{background:#FBE1E3}"""


def png(ruta, titulo, cuerpo, script, ancho=1000):
    doc = f"<!doctype html><meta charset=utf-8><style>{CSS}</style><div class=t>{html.escape(titulo)}</div><div class=c>{cuerpo}</div><div class=pie>Generado con {script} | fecha: {FECHA} | commit: {COMMIT}</div>"
    with sync_playwright() as p:
        n = p.chromium.launch()
        pg = n.new_page(viewport={"width": ancho, "height": 300}, device_scale_factor=1.5)
        pg.set_content(doc)
        pg.screenshot(path=str(ruta), full_page=True)
        n.close()


def serie(csvpath):
    t, u, p50, p95, rps, fail = [], [], [], [], [], []
    with open(csvpath, encoding="utf-8") as f:
        filas = [r for r in csv.DictReader(f) if r["Name"] == "Aggregated"]
    t0 = int(filas[0]["Timestamp"])
    for r in filas:
        if r["95%"] in ("N/A", ""):
            continue
        t.append(int(r["Timestamp"]) - t0)
        u.append(int(r["User Count"]))
        p50.append(float(r["50%"]))
        p95.append(float(r["95%"]))
        rps.append(float(r["Requests/s"]))
        fail.append(float(r["Failures/s"]))
    return t, u, p50, p95, rps, fail


def svg_linea(t, series, w=900, h=240, ymax=None, etiqueta_y="ms"):
    ymax = ymax or max(max(s[1]) for s in series) * 1.1 or 1
    xm = max(t) or 1
    px = lambda x: 50 + x / xm * (w - 70)
    py = lambda y: h - 30 - y / ymax * (h - 50)
    o = [f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">']
    for k in range(5):
        v = ymax * k / 4
        o.append(f'<line x1="50" x2="{w-20}" y1="{py(v):.1f}" y2="{py(v):.1f}" stroke="#dde"/><text x="46" y="{py(v)+4:.1f}" font-size="11" text-anchor="end">{v:.0f}</text>')
    for k in range(0, int(xm) + 1, 10):
        o.append(f'<text x="{px(k):.1f}" y="{h-12}" font-size="11" text-anchor="middle">{k} s</text>')
    for nombre, ys, color in series:
        pts = " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in zip(t, ys))
        o.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts}"/>')
    lx = 60
    for nombre, ys, color in series:
        o.append(f'<rect x="{lx}" y="6" width="12" height="12" fill="{color}"/><text x="{lx+16}" y="16" font-size="12">{html.escape(nombre)}</text>')
        lx += 190
    o.append(f'<text x="8" y="{h/2}" font-size="11" transform="rotate(-90 8 {h/2})" text-anchor="middle">{etiqueta_y}</text></svg>')
    return "".join(o)


def locust():
    res = {r["corrida"]: r for r in json.load(open(SAL / "P_resumen.json"))["corridas"]}
    for clave, titulo in [("A_inc1_inc2_20u", "Corrida A: Incrementos 1 y 2, 20 usuarios, 60 s"), ("B_inc3_inc4_20u", "Corrida B: Incrementos 3 y 4, 20 usuarios, 60 s"), ("C_inc1_inc2_100u", "Corrida C: Incrementos 1 y 2, 100 usuarios, 60 s")]:
        t, u, p50, p95, rps, fail = serie(SAL / f"P_{clave}_stats_history.csv")
        r = res[clave]
        s1 = svg_linea(t, [("p50 (ms)", p50, "#1F7A3D"), ("p95 (ms)", p95, "#B0222B"), ("umbral 800 ms", [800] * len(t), "#8A6200")], ymax=max(max(p95), 800) * 1.1)
        s2 = svg_linea(t, [("usuarios", u, "#1F4E79"), ("peticiones/s", rps, "#B4530B")], h=170, etiqueta_y="usuarios | req/s")
        tabla = (
            f"<table><tr><th>Peticiones</th><th>Fallos</th><th>p50</th><th>p95</th><th>p99</th><th>RPS medio</th><th>Disponibilidad /api/salud</th><th>RSS</th></tr>"
            f"<tr><td>{r['peticiones']}</td><td>{r['fallos']} ({r['tasa_error_pct']} %)</td><td>{r['p50_ms']:.0f} ms</td><td>{r['p95_ms']:.0f} ms</td><td>{r['p99_ms']:.0f} ms</td><td>{r['rps']}</td><td>{r['disponibilidad_pct']} % ({r['sondeos_salud']} sondeos)</td><td>{r['rss_mb_min']}-{r['rss_mb_max']} MB</td></tr></table>"
        )
        png(EV / "rendimiento" / f"P_locust_{clave}.png", f"Locust - {titulo}", f"{s1}<br>{s2}<br>{tabla}", "metricas/graficos.py a partir de salidas/P_%s_stats_history.csv" % clave, 940)
        print("ok", clave)


def arbol():
    app = RAIZ / "pmv_fastapi" / "app"
    lineas = ["pmv_fastapi/app/"]

    def rec(d, pref, nivel):
        hijos = sorted(x for x in d.iterdir() if x.name not in ("__pycache__", "vendor") and not x.name.endswith(".pyc"))
        dirs = [x for x in hijos if x.is_dir()]
        archivos = [x for x in hijos if x.is_file() and x.suffix == ".py" and x.name != "__init__.py"]
        elementos = dirs + archivos
        for i, x in enumerate(elementos):
            ult = i == len(elementos) - 1
            marca = "└── " if ult else "├── "
            if x.is_dir():
                n = len([y for y in x.rglob("*.py") if y.name != "__init__.py"])
                lineas.append(f"{pref}{marca}{x.name}/  ({n} archivos .py)")
                rec(x, pref + ("    " if ult else "│   "), nivel + 1)
            else:
                lineas.append(f"{pref}{marca}{x.name}")

    # el arbol completo es largo: mostrar carpetas con conteo y, para domain/model y ports, los nombres
    rec(app, "", 0)
    texto = "\n".join(lineas)
    h = json.load(open(SAL / "S_hexagonal.json"))
    png(EV / "arquitectura" / "S_arbol_hexagonal.png", "Estructura real de carpetas de la capa hexagonal (pmv_fastapi/app)", f'<div class="mono">{html.escape(texto)}</div>', "metricas/graficos.py (recorrido del sistema de archivos)", 900)
    capas = list(h["matriz_importaciones"].keys())
    cols = ["stdlib", "tercero"] + capas
    filas = ""
    permitido = {
        "domain.model": {"stdlib", "domain.model"},
        "domain.service": {"stdlib", "domain.model", "domain.service"},
        "ports.inbound": {"stdlib", "domain.model", "ports.inbound"},
        "ports.outbound": {"stdlib", "domain.model", "ports.outbound"},
        "application": {"stdlib", "domain.model", "domain.service", "ports.inbound", "ports.outbound"},
        "adapters.inbound": {"stdlib", "tercero", "domain.model", "ports.inbound", "adapters.inbound"},
        "adapters.outbound": {"stdlib", "tercero", "domain.model", "ports.outbound", "adapters.outbound"},
    }
    for c in capas:
        celdas = ""
        for k in cols:
            v = h["matriz_importaciones"][c].get(k, 0)
            clase = ""
            if v and k not in permitido[c]:
                clase = ' class="mal"'
            elif v:
                clase = ' class="ok"'
            celdas += f"<td{clase}>{v}</td>"
        filas += f"<tr><td>{c}</td><td>{h['archivos_por_capa'][c]}</td><td>{h['loc_por_capa'][c]}</td>{celdas}</tr>"
    cab = "".join(f"<th>{k}</th>" for k in cols)
    tabla = f"<table><tr><th>Capa (origen)</th><th>Archivos</th><th>LOC</th>{cab}</tr>{filas}</table><p>Verde: dependencia permitida por la regla. Rojo: violacion. Cero celdas rojas: la regla de dependencias se cumple.</p>"
    png(EV / "arquitectura" / "S_matriz_importaciones.png", "Matriz de importaciones por capa (analisis AST de import)", tabla, "metricas/auditoria_hexagonal.py y metricas/graficos.py", 1250)
    print("ok arquitectura")


def axe():
    a = json.load(open(SAL / "U_axe_por_pantalla.json"))
    filas = ""
    for p in a["escritorio"]:
        d, m = a["escritorio"][p], a["movil"][p]
        nd = sum(x["nodos"] for x in d["violaciones"])
        nm = sum(x["nodos"] for x in m["violaciones"])
        reglas = sorted({x["id"] for x in d["violaciones"]} | {x["id"] for x in m["violaciones"]})
        filas += f'<tr><td>{html.escape(p)}</td><td class="{"ok" if nd == 0 else "mal"}">{len(d["violaciones"])} reglas / {nd} nodos</td><td class="{"ok" if nm == 0 else "mal"}">{len(m["violaciones"])} reglas / {nm} nodos</td><td style="text-align:left">{html.escape(", ".join(reglas)) or "-"}</td></tr>'
    tabla = f"<table><tr><th>Pantalla</th><th>Escritorio 1366x768</th><th>Movil 390x844</th><th>Reglas violadas (axe-core 4.14.0, wcag2a/2aa/21a/21aa)</th></tr>{filas}</table>"
    png(EV / "usabilidad" / "U_axe_resumen_pantallas.png", "axe-core por pantalla: violaciones WCAG 2.1 A/AA", tabla, "metricas/accesibilidad.py y metricas/graficos.py", 1100)
    print("ok axe")


if __name__ == "__main__":
    for d in ("rendimiento", "arquitectura", "usabilidad"):
        (EV / d).mkdir(parents=True, exist_ok=True)
    locust()
    arbol()
    axe()
