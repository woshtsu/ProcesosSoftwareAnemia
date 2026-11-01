"""Factor U: contraste de la paleta real de pmv_fastapi/app/web/estilos.css (WCAG 1.4.3 y 1.4.11) y muestras de color.

Uso (raiz del repositorio): PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python entregables/semana-10/metricas/paleta_colores.py
Lee el CSS, resuelve las variables, toma cada regla que fija `color` y `background`, y calcula la razon de contraste con la
formula de luminancia relativa de WCAG 2.1. Genera metricas/salidas/U_contraste_paleta.json y las imagenes
evidencias/usabilidad/U_paleta_colores.png (roles, contraste) y U_semaforo_severidad_daltonismo.png (simulacion de daltonismo).
"""

import html
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[3]
CSS = (RAIZ / "pmv_fastapi" / "app" / "web" / "estilos.css").read_text(encoding="utf-8")
JS = (RAIZ / "pmv_fastapi" / "app" / "web" / "app.js").read_text(encoding="utf-8")
SAL = RAIZ / "entregables" / "semana-10" / "metricas" / "salidas"
IMG = RAIZ / "entregables" / "semana-10" / "evidencias" / "usabilidad"


def lin(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(x * 2 for x in h)
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


variables = {k: v.strip() for k, v in re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{3,6})\s*;", CSS)}


def resolver(v):
    v = v.strip()
    m = re.match(r"var\(--([\w-]+)\)", v)
    if m:
        return variables.get(m.group(1))
    m = re.match(r"(#[0-9A-Fa-f]{3,6})\b", v)
    return m.group(1) if m else None


pares = {}
for sel, cuerpo in re.findall(r"([^{}]+)\{([^{}]*)\}", CSS):
    c = re.search(r"(?<![-\w])color:\s*([^;]+)", cuerpo)
    b = re.search(r"(?<![-\w])background(?:-color)?:\s*([^;]+)", cuerpo)
    if c and b:
        fg, bg = resolver(c.group(1)), resolver(b.group(1))
        if fg and bg:
            pares[(sel.strip().split("\n")[-1][:60], fg.upper(), bg.upper())] = ratio(fg, bg)
# texto sin fondo propio sobre las superficies reales (tarjeta blanca y fondo de pagina)
for nombre, fg in (("texto", variables["texto"]), ("gris (secundario)", variables["gris"]), ("azul (titulos, enlaces)", variables["azul"]), ("azul-2 (h2)", variables["azul-2"]), ("rojo (errores)", variables["rojo"]), ("verde", variables["verde"]), ("naranja", variables["naranja"]), ("ambar", variables["ambar"])):
    for sup, bg in (("tarjeta blanca", "#FFFFFF"), ("fondo de pagina", variables["fondo"])):
        pares[(f"{nombre} sobre {sup}", fg.upper(), bg.upper())] = ratio(fg, bg)
texto = []
for (sel, fg, bg), r in sorted(pares.items(), key=lambda x: x[1]):
    texto.append({"elemento": sel, "texto": fg, "fondo": bg, "razon": round(r, 2), "umbral": 4.5, "cumple_1_4_3": r >= 4.5})
# componentes de interfaz (1.4.11, 3:1): bordes de campos, indicador de foco, graficos de severidad
componentes = []
for nombre, fg, bg in (("borde de campos (--borde) sobre blanco", variables["borde"], "#FFFFFF"), ("borde de boton secundario (#A9C4E2) sobre blanco", "#A9C4E2", "#FFFFFF"), ("contorno de foco de campos (#9CC3EA) sobre blanco", "#9CC3EA", "#FFFFFF"), ("barra SIN_ANEMIA del grafico", "#1F7A3D", "#EEF2F6"), ("barra LEVE del grafico (#C99200)", "#C99200", "#EEF2F6"), ("barra MODERADA del grafico (#D26A1B)", "#D26A1B", "#EEF2F6"), ("barra SEVERA del grafico", "#B0222B", "#EEF2F6"), ("barra NO_APLICA del grafico (#8C99A6)", "#8C99A6", "#EEF2F6")):
    r = ratio(fg, bg)
    componentes.append({"componente": nombre, "color": fg, "fondo": bg, "razon": round(r, 2), "umbral": 3.0, "cumple_1_4_11": r >= 3.0})
res = {
    "variables": variables,
    "colores_del_grafico_en_app_js": re.search(r"const COLOR = (\{[^}]*\})", JS).group(1),
    "pares_texto": texto,
    "pares_texto_total": len(texto),
    "pares_texto_cumplen": sum(1 for x in texto if x["cumple_1_4_3"]),
    "razon_minima_texto": min(x["razon"] for x in texto),
    "razon_maxima_texto": max(x["razon"] for x in texto),
    "componentes": componentes,
    "componentes_total": len(componentes),
    "componentes_cumplen": sum(1 for x in componentes if x["cumple_1_4_11"]),
}
(SAL / "U_contraste_paleta.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Pares de texto: {res['pares_texto_cumplen']}/{res['pares_texto_total']} cumplen 4.5:1 (min {res['razon_minima_texto']}, max {res['razon_maxima_texto']})")
for x in texto:
    print(f"  {'OK ' if x['cumple_1_4_3'] else 'NO '} {x['razon']:>5}:1  {x['texto']} sobre {x['fondo']}  [{x['elemento']}]")
print(f"Componentes (1.4.11): {res['componentes_cumplen']}/{res['componentes_total']} cumplen 3:1")
for x in componentes:
    print(f"  {'OK ' if x['cumple_1_4_11'] else 'NO '} {x['razon']:>5}:1  {x['componente']}")

# ---- imagenes ----
ROLES = [
    ("Primario (dominante)", "--azul", "#1F4E79", "Azul profundo: confianza, calma clinica y estabilidad en datos de salud; es la cabecera, los titulos y las acciones primarias."),
    ("Secundario (acento)", "--azul-2", "#2E5C8A", "Variante del primario para subtitulos (h2) y enlaces."),
    ("Fondo de pagina", "--fondo", "#F4F7FB", "Gris azulado muy claro: reduce el brillo y la fatiga en jornadas largas; las tarjetas blancas resaltan encima."),
    ("Texto", "--texto", "#1B2B3A", "Casi negro azulado: maxima legibilidad sin el contraste duro del negro puro."),
    ("Texto secundario", "--gris", "#5E6E7E", "Gris neutro para metadatos, notas y estados no urgentes."),
    ("Exito / sin anemia", "--verde", "#1F7A3D", "Verde: salud, control cumplido, estado operativo seguro (Al dia, Sin anemia, Cumplido)."),
    ("Precaucion / leve", "--ambar", "#8A6200", "Ambar: atencion sin urgencia (Anemia leve, por vencer, simulado)."),
    ("Advertencia / moderada", "--naranja", "#B4530B", "Naranja: riesgo creciente (Anemia moderada, prioridad media, pendiente de sincronizar)."),
    ("Alerta / severa", "--rojo", "#B0222B", "Rojo: accion inmediata (Anemia severa, control vencido, prioridad alta, conflicto, errores)."),
]
filas = ""
for rol, var, hx, just in ROLES:
    hx = variables[var[2:]]
    fondo_claro = variables.get(var[2:] + "-f")
    filas += f"<tr><td><b>{html.escape(rol)}</b></td><td><div class=sw style='background:{hx}'></div></td><td><code>{hx}</code><br><small>{var}</small></td>"
    filas += f"<td>{('<div class=sw style=background:' + fondo_claro + '></div><code>' + fondo_claro + '</code>') if fondo_claro else '—'}</td>"
    r_b = ratio(hx, "#FFFFFF")
    r_f = ratio(hx, fondo_claro) if fondo_claro else None
    etiqueta_b = f"{r_b:.2f}:1"
    if var == "--fondo":
        etiqueta_b = f"{ratio(variables['texto'], hx):.2f}:1<br><small>(texto sobre este fondo)</small>"
    filas += f"<td>{etiqueta_b}</td><td>{(f'{r_f:.2f}:1') if r_f else '—'}</td><td class=just>{html.escape(just)}</td></tr>"
doc = f"""<!doctype html><meta charset=utf-8><style>
body{{font-family:'DejaVu Sans',sans-serif;margin:0;padding:16px;background:#fff;color:#1B2B3A;font-size:13px;width:1240px}}
h1{{font-size:16px;margin:0 0 8px;color:#1F4E79}} table{{border-collapse:collapse;width:100%}}
th{{background:#1F4E79;color:#fff;padding:7px;text-align:left;font-size:12px}} td{{border-top:1px solid #D7E0EA;padding:6px 7px;vertical-align:middle}}
.sw{{width:64px;height:30px;border-radius:6px;border:1px solid #D7E0EA;display:inline-block}} code{{font-size:12px}} .just{{max-width:460px}} small{{color:#5E6E7E}}
.pie{{margin-top:8px;color:#5E6E7E;font-size:11px}}</style>
<h1>Paleta cromatica real de la interfaz (estilos.css) y su contraste</h1>
<table><tr><th>Rol</th><th>Muestra</th><th>Hexadecimal</th><th>Fondo suave del chip</th><th>Contraste sobre blanco</th><th>Contraste sobre su fondo suave</th><th>Significado y uso en el dominio (salud infantil)</th></tr>{filas}</table>
<div class=pie>Fuente: pmv_fastapi/app/web/estilos.css, variables :root. Razon de contraste = (L1+0.05)/(L2+0.05), luminancia relativa WCAG 2.1. Umbral texto normal 4.5:1.</div>"""
SIM = {
    "Visión normal": "none",
    "Deuteranopía (sin verde)": "url(#deut)",
    "Protanopía (sin rojo)": "url(#prot)",
    "Escala de grises": "grayscale(1)",
}
badges = [("Sin anemia", "SIN_ANEMIA"), ("Anemia leve", "LEVE"), ("Anemia moderada", "MODERADA"), ("Anemia severa", "SEVERA")]
cols = {"SIN_ANEMIA": (variables["verde"], variables["verde-f"]), "LEVE": (variables["ambar"], variables["ambar-f"]), "MODERADA": (variables["naranja"], variables["naranja-f"]), "SEVERA": (variables["rojo"], variables["rojo-f"])}
filas2 = ""
for nombre, filtro in SIM.items():
    celdas = "".join(f"<span class=b style='color:{cols[k][0]};background:{cols[k][1]}'>{t}</span>" for t, k in badges)
    barras = "".join(f"<span class=bar style='background:{c}'></span>" for c in (COL for COL in ("#1F7A3D", "#C99200", "#D26A1B", "#B0222B")))
    filas2 += f"<div class=fila><div class=lab>{nombre}</div><div style='filter:{filtro}'>{celdas}<br>{barras}</div></div>"
doc2 = f"""<!doctype html><meta charset=utf-8><style>
body{{font-family:'DejaVu Sans',sans-serif;margin:0;padding:16px;background:#fff;width:900px;color:#1B2B3A}} h1{{font-size:16px;color:#1F4E79;margin:0 0 10px}}
.fila{{display:flex;align-items:center;gap:14px;margin:8px 0;padding:8px;border:1px solid #D7E0EA;border-radius:8px}} .lab{{width:190px;font-weight:700;font-size:13px}}
.b{{display:inline-block;padding:4px 12px;border-radius:999px;font-size:13px;font-weight:700;margin-right:8px}} .bar{{display:inline-block;width:150px;height:16px;border-radius:5px;margin:8px 8px 0 0}}
.pie{{color:#5E6E7E;font-size:11px;margin-top:8px}}</style>
<svg width=0 height=0><filter id=deut><feColorMatrix type=matrix values="0.367 0.861 -0.228 0 0  0.280 0.673 0.047 0 0  -0.012 0.043 0.969 0 0  0 0 0 1 0"/></filter>
<filter id=prot><feColorMatrix type=matrix values="0.152 1.053 -0.205 0 0  0.115 0.786 0.099 0 0  -0.004 -0.048 1.052 0 0  0 0 0 1 0"/></filter></svg>
<h1>Semaforo de severidad bajo simulacion de daltonismo (matrices de Machado et al. 2009)</h1>{filas2}
<div class=pie>Cada estado conserva su texto («Sin anemia», «Anemia leve», …): el color refuerza, no es el unico canal (WCAG 1.4.1). Barras: colores del grafico de Hb (app.js).</div>"""
with sync_playwright() as p:
    nav = p.chromium.launch()
    for nombre, d, w in (("U_paleta_colores", doc, 1280), ("U_semaforo_severidad_daltonismo", doc2, 940)):
        pg = nav.new_page(viewport={"width": w, "height": 400}, device_scale_factor=1.5)
        pg.set_content(d)
        pg.screenshot(path=str(IMG / f"{nombre}.png"), full_page=True)
    nav.close()
print("imagenes: U_paleta_colores.png, U_semaforo_severidad_daltonismo.png")
