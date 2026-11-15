#!/usr/bin/env python
"""Genera los gráficos del informe GQM (PNG a 150 dpi y SVG) en entregables/semana-09/metricas/graficos/.

Todos los valores se leen de los JSON de metricas/datos/ (ningún número está escrito a mano). Estilo sobrio, títulos en español.

  Inc. 1 = v1.0-PMV; Inc. 2 = v2.0.0-inc2 (cierre). El hito intermedio v1.5.0-inc2-avance se dibuja como marcador gris (rombo) cuando cabe.

  g1_comparativa_gqm        Inc.1 vs Inc.2 vs meta de cada métrica (un panel por métrica porque las unidades difieren); rombo gris = avance v1.5
  g2_conformidad_hexagonal  5 componentes x 2 versiones (v1.0 y v2.0): conforme / no conforme (criterio estricto)
  g3_p95_endpoints          p95 por endpoint, v1.0 vs v2.0 (mismo mix de tareas, misma sesión) + endpoints nuevos del Inc. 2; rombo gris = v1.5
  g4_deteccion_vencidos     matrices de confusión y precisión / sensibilidad / F1 frente al oráculo, v1.0 vs v2.0 (rombo gris = v1.5)
  g5_brechas                puntaje de B1..B6 por versión (rombo gris = v1.5)
  g6_defectos               defectos por RF-01..RF-09 e incremento (funcionales, no funcionales, escapados)
  g10_linea_base_vs_inc2    línea base REAL de la DIRESA Junín (control de hemoglobina al mes, 3 y 6 meses) frente a la capacidad de la v2.0
                            (% de niños con controles programados y % de controles vencidos visibles para el personal); con fuente al pie

Uso:  python graficos_gqm.py
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

import comun as c  # noqa: E402

SAL = c.METRICAS / "graficos"
C1, C2, CM = "#5B7C99", "#2F7F79", "#BDBDBD"  # Inc.1 / v1.0 azul grisáceo, Inc.2 / v2.0 verde azulado, meta gris
CV15 = "#8A8A8A"  # marcador gris del avance v1.5
OK, NO, TXT = "#4C8C6B", "#B5584F", "#333333"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": "#888888", "axes.spines.top": False, "axes.spines.right": False,
    "axes.titleweight": "bold", "axes.titlesize": 10, "figure.facecolor": "white", "axes.facecolor": "white", "axes.grid": True,
    "grid.color": "#E6E6E6", "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False,
})


def num(x: float, dec: int = 1) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def cargar(n: str):
    return json.loads((c.DATOS / n).read_text(encoding="utf-8"))


def guardar(fig, nombre: str) -> None:
    SAL.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAL / f"{nombre}.png", dpi=150, bbox_inches="tight")
    fig.savefig(SAL / f"{nombre}.svg", bbox_inches="tight")
    plt.close(fig)
    print("ok", nombre)


def etiquetas(ax, barras, fmt="{:.1f}", dy=0.0, suf=""):
    for b in barras:
        h = b.get_height()
        ax.annotate(fmt.format(h) + suf, (b.get_x() + b.get_width() / 2, h), ha="center", va="bottom", xytext=(0, 2 + dy),
                    textcoords="offset points", fontsize=8, color=TXT)


# ---------------------------------------------------------------------------------------------------------------------
TITULOS = {"M1.1": "Contaminación del dominio", "M1.2": "Conformidad hexagonal (estricta)", "M2.1": "RF con captura aprobada", "M2.2": "Defectos funcionales por RF",
           "M3.1": "Brechas AS-IS resueltas (de 6)", "M3.2": "Índice de impacto en valor"}


def marcador_v15(ax, x, y, texto=None, dx=0.0):
    """Rombo gris del avance v1.5 (hito intermedio) con su valor al costado."""
    ax.plot([x], [y], marker="D", ms=6, color=CV15, mec="white", mew=0.8, ls="none", zorder=6)
    if texto:
        ax.annotate(texto, (x, y), xytext=(8 + dx, -2), textcoords="offset points", fontsize=7, color=CV15, va="center", ha="left", zorder=6)


def EXTRA(m) -> str:
    """Nota breve bajo el panel con la variante o complemento relevante (leída del resumen)."""
    c_ = lambda x: f"{x:.1f}".replace(".", ",")  # noqa: E731
    if m["id"] == "M2.1":
        return f"Avance v1.5 sobre las 4 RF del Inc. 2: {c_(m['valor_avance_v15_sobre_alcance_total'])} %"
    if m["id"] == "M3.1":
        k = m["complementaria_brechas_comprometidas"]
        return f"Brechas comprometidas en el plan: Inc. 1 = {c_(k['inc1_B1'])} %; Inc. 2 = {c_(k['inc2_B1_B2'])} %"
    if m["id"] == "M2.2":
        v = m["variantes_inc1"]
        e = m["variante_inc2_escapados_a_produccion"]["valor"]
        return f"Inc. 1, solo antes de liberar: {c_(v['solo_detectados_antes_de_liberar'])}; Inc. 2, solo escapados a producción: {c_(e)}"
    if m["id"] == "M1.2":
        return f"Criterio laxo: Inc. 1 = {c_(m['variante_laxa']['inc1'])} %; Inc. 2 = {c_(m['variante_laxa']['inc2'])} %"
    return ""


def g1() -> None:
    res = cargar("resumen_gqm.json")["metricas"]
    fig, axes = plt.subplots(2, 3, figsize=(11.5, 7.4))
    for ax, m in zip(axes.flat, res):
        vals = [m["valor_inc1"], m["valor_inc2"], m["meta_inc1"], m["meta_inc2"]]
        x = [0, 1, 2.4, 3.4]
        cols = [C1, C2, CM, CM]
        b = ax.bar(x, vals, color=cols, width=0.8, edgecolor=["none", "none", "#888888", "#888888"], hatch=["", "", "//", "//"], linewidth=0.6)
        suf = " %" if m["unidad"] == "%" else ""
        dec = 2 if m["id"] == "M2.2" else 1
        for bi in b:
            h = bi.get_height()
            ax.annotate(f"{h:.{dec}f}".replace(".", ",") + suf, (bi.get_x() + bi.get_width() / 2, h), ha="center", va="bottom", xytext=(0, 2), textcoords="offset points", fontsize=8, color=TXT)
        marcador_v15(ax, 1.0, m["valor_avance_v15"])
        ax.set_xticks(x)
        ax.set_xticklabels(["Inc. 1", "Inc. 2", "Meta\nInc. 1", "Meta\nInc. 2"], fontsize=8)
        signo = "≤" if m["sentido_meta"] == "<=" else "≥"
        ax.set_title(f"{m['id']} {TITULOS[m['id']]}", fontsize=9)
        ax.set_ylabel("Def/RF" if m["unidad"] == "Def/RF" else "%")
        top = max(vals + [m["valor_avance_v15"]])
        ax.set_ylim(0, 100 * 1.22 if m["unidad"] == "%" else max(top * 1.35, 0.5))
        cu = lambda v: "cumple" if v else "no cumple"  # noqa: E731
        extra = EXTRA(m)
        ax.text(0.5, -0.30, f"Meta {signo}: Inc. 1 {cu(m['cumple_inc1'])} · Inc. 2 {cu(m['cumple_inc2'])} · avance v1.5 = {m['valor_avance_v15']:.{dec}f}".replace(".", ",") + suf + (f"\n{extra}" if extra else ""), transform=ax.transAxes, ha="center", va="top", fontsize=7.5, color="#555555")
    fig.suptitle("Comparativa GQM: Incremento 1 (v1.0-PMV) frente al Incremento 2 (v2.0.0-inc2, cierre) y a las metas de la guía", fontsize=11, fontweight="bold")
    fig.legend(handles=[Patch(color=C1, label="Inc. 1 (v1.0-PMV)"), Patch(color=C2, label="Inc. 2 (v2.0.0-inc2, cierre)"),
                        Line2D([0], [0], marker="D", color="none", markerfacecolor=CV15, markeredgecolor="white", ms=6, label="Avance v1.5 (hito intermedio)"),
                        Patch(facecolor=CM, hatch="//", edgecolor="#888888", label="Meta de la guía")],
               loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.04, 1, 0.95), h_pad=4.6)
    guardar(fig, "g1_comparativa_gqm")


def g2() -> None:
    m12 = cargar("m12_conformidad.json")
    comp = [f["componente"] for f in m12["v1.0"]["filas"]]
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.set_xlim(0, 2); ax.set_ylim(0, len(comp)); ax.invert_yaxis(); ax.grid(False)
    for j, v in enumerate(("v1.0", "v2.0")):
        for i, f in enumerate(m12[v]["filas"]):
            ok = f["estado"] == "CONFORME"
            ax.add_patch(Rectangle((j + 0.04, i + 0.08), 0.92, 0.84, facecolor=OK if ok else NO, alpha=0.88, edgecolor="white"))
            txt = ("CONFORME" if ok else "NO CONFORME") + ("" if f["estado"] == f["estado_laxo"] else "\n(conforme con criterio laxo)")
            ax.text(j + 0.5, i + 0.5, txt, ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    ax.set_yticks([i + 0.5 for i in range(len(comp))]); ax.set_yticklabels(comp)
    ax.set_xticks([0.5, 1.5]); ax.set_xticklabels([f"Inc. 1 · v1.0-PMV\nM1.2 = {str(m12['v1.0']['m12_pct']).replace('.', ',')} % ({m12['v1.0']['conformes']}/5)",
                                                   f"Inc. 2 · v2.0.0-inc2 (cierre)\nM1.2 = {str(m12['v2.0']['m12_pct']).replace('.', ',')} % ({m12['v2.0']['conformes']}/5)"])
    ax.xaxis.tick_top(); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Conformidad de la estructura hexagonal por componente (criterio estricto)", pad=34)
    ax.text(1.0, len(comp) + 0.12, f"Avance v1.5 (hito intermedio): M1.2 = {str(m12['v1.5']['m12_pct']).replace('.', ',')} % ({m12['v1.5']['conformes']}/5)", ha="center", va="top", fontsize=8, color=CV15)
    guardar(fig, "g2_conformidad_hexagonal")


def g3() -> None:
    carga = cargar("m32_carga.json")["escenarios"]
    a, b, ag = carga["v10_comun"], carga["v15_comun"], carga["v20_comun"]
    ampl = carga["v20_ampliado"]
    ses17 = a["promedio_por_sesion"]["2026-10-17"]  # v1.0 repetida en la misma sesión que la v2.0
    comunes = ["GET /api/ninos", "GET /api/ninos/{id}", "POST /api/validaciones/evaluacion", "POST /api/ninos", "GET /api/reportes/periodo", "AGREGADO"]
    nuevos = ["GET /api/agenda", "GET /api/ninos/{id}/agenda", "GET /api/ninos/{id}/asistencias", "GET /api/alertas/controles-vencidos", "GET /api/alertas/resumen"]
    runs10 = [r for r in a["corridas"] if a["sesion_de_cada_corrida"][r] == "2026-10-17"]
    runs20 = list(ag["corridas"])
    filas = [(e, ses17["promedio"][e]["p95_ms"], ag["promedio"][e]["p95_ms"], [a["corridas"][r][e]["p95_ms"] for r in runs10], [ag["corridas"][r][e]["p95_ms"] for r in runs20],
              b["promedio"][e]["p95_ms"]) for e in comunes]
    fig, ax = plt.subplots(figsize=(9.8, 6.6))
    y = list(range(len(filas))) + [len(filas) + 0.6 + k for k in range(len(nuevos))]
    h = 0.36
    for i, (e, p10, p20, r10, r20, p15) in enumerate(filas):
        ax.barh(i - h / 2, p10, h, color=C1, label="v1.0-PMV (Inc. 1)" if i == 0 else None)
        ax.barh(i + h / 2, p20, h, color=C2, label="v2.0.0-inc2 (Inc. 2, cierre)" if i == 0 else None)
        ax.plot(r10, [i - h / 2] * len(r10), "|", color="#222222", ms=7)
        ax.plot(r20, [i + h / 2] * len(r20), "|", color="#222222", ms=7)
        ax.plot([p15], [i + h / 2], marker="D", ms=5, color=CV15, mec="white", mew=0.7, ls="none", zorder=6, label="v1.5 (avance; sesión del 16/10)" if i == 0 else None)
        ax.text(max([p10] + r10) + 30, i - h / 2, f"{p10:.0f}".replace(".", ","), va="center", fontsize=8)
        ax.text(max([p20] + r20 + [p15]) + 30, i + h / 2, f"{p20:.0f}".replace(".", ","), va="center", fontsize=8)
    for k, e in enumerate(nuevos):
        yy = len(filas) + 0.6 + k
        v = ampl["promedio"][e]["p95_ms"]
        rr = [ampl["corridas"][r][e]["p95_ms"] for r in ampl["corridas"]]
        ax.barh(yy, v, h * 1.2, color=C2, alpha=0.65, hatch="..", edgecolor="white", label="v2.0, endpoints del Inc. 2 (mix ampliado)" if k == 0 else None)
        ax.plot(rr, [yy] * len(rr), "|", color="#222222", ms=7)
        ax.text(max([v] + rr) + 30, yy, f"{v:.0f}".replace(".", ","), va="center", fontsize=8)
    ax.axvline(2000, color=NO, ls="--", lw=1); ax.text(1990, -0.75, "Umbral de 2 s", color=NO, ha="right", fontsize=8)
    ax.set_yticks(y); ax.set_yticklabels(comunes[:-1] + ["AGREGADO (mix común)"] + nuevos)
    ax.invert_yaxis(); ax.set_xlim(0, 2100)
    ax.set_xlabel("p95 del tiempo de respuesta (ms) · promedio de 2 corridas; las marcas | son cada corrida\nv1.0 y v2.0 medidas en la misma sesión (17/10/2026); el rombo gris es la v1.5 de la sesión del 16/10/2026", fontsize=8.5)
    ax.set_title("Tiempo de respuesta p95 por endpoint: 50 usuarios, 60 s, SQLite, dataset B150", fontsize=10.5)
    ax.legend(loc="lower right", fontsize=8)
    guardar(fig, "g3_p95_endpoints")


def g4() -> None:
    m = {v: cargar(f"m32_{v}_B150.json")["V3"]["control_atrasado_api_ninos"] for v in ("v1.0", "v1.5", "v2.0")}
    fig = plt.figure(figsize=(12, 4.3))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.5], wspace=0.35)
    for j, (v, col, tit) in enumerate((("v1.0", C1, "Inc. 1 · v1.0 (heurística de 30 días)"), ("v2.0", C2, "Inc. 2 · v2.0 (agenda normativa)"))):
        ax = fig.add_subplot(gs[0, j]); ax.grid(False)
        mm = m[v]
        mat = [[mm["TP"], mm["FP"]], [mm["FN"], mm["TN"]]]  # filas = lo que marca la API; columnas = oráculo
        for i in range(2):
            for k in range(2):
                bien = (i == k)
                ax.add_patch(Rectangle((k, i), 1, 1, facecolor=col if bien else "#E9E9E9", alpha=0.9 if bien else 1, edgecolor="white", lw=2))
                ax.text(k + 0.5, i + 0.5, str(mat[i][k]), ha="center", va="center", fontsize=15, fontweight="bold", color="white" if bien else TXT)
        ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.invert_yaxis()
        ax.set_xticks([0.5, 1.5]); ax.set_xticklabels(["Vencido\n(oráculo)", "No vencido\n(oráculo)"], fontsize=8)
        ax.set_yticks([0.5, 1.5]); ax.set_yticklabels(["Marcado\natrasado", "No marcado"], fontsize=8)
        ax.xaxis.tick_top(); ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(tit + f"\nn = {mm['n']} niños activos", fontsize=9, pad=30)
    ax = fig.add_subplot(gs[0, 2])
    nombres = ["Precisión", "Sensibilidad", "F1"]
    claves = ["precision", "sensibilidad", "F1"]
    xs = range(3); w = 0.36
    b1 = ax.bar([x - w / 2 for x in xs], [m["v1.0"][k] * 100 for k in claves], w, color=C1, label="v1.0 (Inc. 1)")
    b2 = ax.bar([x + w / 2 for x in xs], [m["v2.0"][k] * 100 for k in claves], w, color=C2, label="v2.0 (Inc. 2)")
    for bb in list(b1) + list(b2):
        ax.annotate(f"{bb.get_height():.1f}".replace(".", ",") + " %", (bb.get_x() + bb.get_width() / 2, bb.get_height()), ha="center", xytext=(0, 2), textcoords="offset points", fontsize=8)
    for x, k in zip(xs, claves):
        ax.plot([x + w / 2], [m["v1.5"][k] * 100], marker="D", ms=5, color=CV15, mec="white", mew=0.7, ls="none", zorder=6, label="v1.5 (avance)" if x == 0 else None)
    ax.set_xticks(list(xs)); ax.set_xticklabels(nombres); ax.set_ylim(0, 118); ax.set_ylabel("%"); ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.0), ncol=3, borderaxespad=3.2)
    ax.set_title("Detección de controles vencidos frente al oráculo normativo", fontsize=9, pad=30)
    guardar(fig, "g4_deteccion_vencidos")


def g5() -> None:
    p = cargar("m31_brechas.json")
    bs = list(p["puntuacion"])
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    w = 0.36
    b1 = ax.bar([i - w / 2 for i in range(6)], [p["puntuacion"][b]["v1.0"] for b in bs], w, color=C1,
                label=f"Inc. 1 · v1.0 ({num(p['resultado_principal']['v1.0']['suma_puntos'])}/6 = {num(p['resultado_principal']['v1.0']['cobertura_pct'])} %)")
    b2 = ax.bar([i + w / 2 for i in range(6)], [p["puntuacion"][b]["v2.0"] for b in bs], w, color=C2,
                label=f"Inc. 2 · v2.0 ({num(p['resultado_principal']['v2.0']['suma_puntos'])}/6 = {num(p['resultado_principal']['v2.0']['cobertura_pct'])} %)")
    for bb in list(b1) + list(b2):
        ax.annotate(f"{bb.get_height():.1f}".replace(".", ","), (bb.get_x() + bb.get_width() / 2, bb.get_height()), ha="center", xytext=(0, 2), textcoords="offset points", fontsize=8.5)
    for i, b in enumerate(bs):
        ax.plot([i + w / 2 + 0.2], [p["puntuacion"][b]["v1.5"]], marker="D", ms=6, color=CV15, mec="white", mew=0.8, ls="none", zorder=6,
                label=f"Avance v1.5 ({num(p['resultado_principal']['v1.5']['suma_puntos'])}/6 = {num(p['resultado_principal']['v1.5']['cobertura_pct'])} %)" if i == 0 else None)
    plan = {"B1": "INC-1", "B2": "INC-2", "B3": "INC-4", "B4": "INC-3", "B5": "INC-5", "B6": "INC-3/6"}
    ax.set_xticks(range(6)); ax.set_xticklabels([f"{b}\n(plan: {plan[b]})" for b in bs], fontsize=8.5)
    ax.set_ylim(0, 1.3); ax.set_yticks([0, 0.5, 1]); ax.set_yticklabels(["0 (no)", "0,5 (parcial)", "1 (completa)"])
    ax.set_title("Brechas AS-IS resueltas por versión (1 = mecanismo completo operativo y probado)")
    ax.legend(loc="upper right", fontsize=8)
    guardar(fig, "g5_brechas")


def g6() -> None:
    d = cargar("m22_defectos.json")
    rfs = [f"RF-0{i}" for i in range(1, 10)]
    inc2_rf = {"RF-06", "RF-07", "RF-08", "RF-09"}
    cat = {"fun_antes": ("Funcional, detectado antes de liberar (Inc. 1)", C1), "fun_escapado": ("Funcional escapado, hallado en el ciclo del Inc. 2", "#8FA9C0"),
           "no_fun": ("No funcional (rendimiento)", "#B8A17A"), "fun_inc2": ("Funcional en código nuevo del Inc. 2, detectado antes de liberar", C2)}
    datos = {rf: {k: [] for k in cat} for rf in rfs}
    for did, v in d["clasificacion_por_defecto"].items():
        if v["tipo"] == "NO FUNCIONAL":
            datos[v["rf"]]["no_fun"].append(did)
        elif v["rf"] in inc2_rf:
            datos[v["rf"]]["fun_inc2"].append(did)
        elif v["momento"].startswith("detectado antes"):
            datos[v["rf"]]["fun_antes"].append(did)
        else:
            datos[v["rf"]]["fun_escapado"].append(did)
    fig, ax = plt.subplots(figsize=(10.4, 4.9))
    fondo = [0] * len(rfs)
    for k, (etq, col) in cat.items():
        vals = [len(datos[rf][k]) for rf in rfs]
        ax.bar(rfs, vals, bottom=fondo, color=col, label=etq, width=0.6)
        for i, rf in enumerate(rfs):
            if vals[i]:
                ax.text(i, fondo[i] + vals[i] / 2, "\n".join(datos[rf][k]), ha="center", va="center", color="white", fontsize=8, fontweight="bold")
        fondo = [a + b for a, b in zip(fondo, vals)]
    for i, t in enumerate(fondo):
        ax.annotate(str(t), (i, t), ha="center", xytext=(0, 3), textcoords="offset points", fontsize=9)
    ax.axvspan(-0.5, 4.5, color="#F2F5F8", zorder=0); ax.axvspan(4.5, 8.5, color="#EEF5F4", zorder=0)
    ax.text(2, max(fondo) + 1.15, "Inc. 1 (RF-01..RF-05)", ha="center", color=C1, fontweight="bold")
    ax.text(6.5, max(fondo) + 1.15, "Inc. 2 (RF-06..RF-09; avance v1.5: RF-06, RF-07)", ha="center", color=C2, fontweight="bold")
    ax.set_ylim(0, max(fondo) + 1.8); ax.set_ylabel("N.º de defectos"); ax.set_yticks(range(0, max(fondo) + 2))
    ax.set_title(f"Defectos por requisito e incremento · M2.2: Inc. 1 = {num(d['inc1']['tasa_def_por_rf'], 2)} Def/RF; Inc. 2 = {num(d['inc2']['tasa_def_por_rf'], 2)} Def/RF "
                 f"(avance v1.5 = {num(d['inc2_avance']['tasa_def_por_rf'], 2)})", fontsize=10.5)
    ax.legend(loc="upper center", fontsize=8, bbox_to_anchor=(0.5, -0.08), ncol=2)
    guardar(fig, "g6_defectos")


def g10() -> None:
    """Línea base REAL de la DIRESA Junín frente a la capacidad de la v2.0. Magnitudes de distinta naturaleza: se muestran lado a lado, sin promediar."""
    lb = cargar("m32_indice_valor.json")["linea_base_real_DIRESA"]
    ctl = lb["control_de_hemoglobina_registrado"]
    vis = lb["controles_vencidos_visibles_para_el_personal"]
    ag = vis["ninos_activos_con_agenda_generada"]
    per = lb["perdida_de_seguimiento_a_6_meses"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.2, 5.4), gridspec_kw={"width_ratios": [1.25, 1]})
    # Panel izquierdo: proceso actual (AS-IS real, dataset completo)
    etiquetas_ = [("al_mes", "Control al mes"), ("a_los_3_meses", "Control a los 3 meses"), ("a_los_6_meses", "Control a los 6 meses")]
    w = 0.36
    xs = range(3)
    br = [ctl[k]["bruto"] for k, _ in etiquetas_]
    sp = [ctl[k]["con_seguimiento_posible"] for k, _ in etiquetas_]
    b1 = a1.bar([x - w / 2 for x in xs], [x["pct"] for x in br], w, color="#B8A17A", label=f"Sobre todos los diagnosticados (N = {br[0]['N']:,})".replace(",", " "))
    b2 = a1.bar([x + w / 2 for x in xs], [x["pct"] for x in sp], w, color="#8C7A4F", label="Solo con seguimiento posible (plazo + holgura cumplidos)")
    for bb in list(b1) + list(b2):
        a1.annotate(f"{bb.get_height():.1f}".replace(".", ",") + " %", (bb.get_x() + bb.get_width() / 2, bb.get_height()), ha="center", xytext=(0, 2), textcoords="offset points", fontsize=8)
    a1.set_xticks(list(xs)); a1.set_xticklabels([t for _, t in etiquetas_], fontsize=8.5)
    a1.set_ylim(0, 100); a1.set_ylabel("% de niños con dosaje de hemoglobina registrado en el HIS")
    a1.set_title("Hoy (AS-IS real): control registrado tras el diagnóstico\nDIRESA Junín, 12 486 diagnósticos, corte 30/06/2024", fontsize=9.5)
    a1.legend(loc="upper right", fontsize=7.5)
    a1.text(0.0, -0.17, f"Pérdida de seguimiento a 6 meses (sin dosaje a los 6 meses):{num(per['bruto']['pct'])} % bruta; {num(per['con_seguimiento_posible']['pct'])} % con seguimiento posible.",
            transform=a1.transAxes, fontsize=7.5, color="#555555", va="top")
    # Panel derecho: capacidad del sistema (v2.0, muestra de 500 niños)
    cats = ["Niños activos con\ncontroles programados", "Controles vencidos\nvisibles para el personal"]
    asis = [ag["as_is_pct"], vis["as_is_pct"]]
    v20 = [ag["v2_0_pct"], vis["v2_0_muestra_500_pct"]]
    w2 = 0.36
    c1 = a2.bar([x - w2 / 2 for x in range(2)], asis, w2, color=C1, label="Proceso actual (cuaderno, tarjeta e HIS)")
    c2 = a2.bar([x + w2 / 2 for x in range(2)], v20, w2, color=C2, label="Sistema v2.0 (muestra de 500 niños)")
    for bb in list(c1) + list(c2):
        a2.annotate(f"{bb.get_height():.0f}".replace(".", ",") + " %", (bb.get_x() + bb.get_width() / 2, bb.get_height()), ha="center", xytext=(0, 2), textcoords="offset points", fontsize=9)
    a2.set_xticks(range(2)); a2.set_xticklabels(cats, fontsize=8.5)
    a2.set_ylim(0, 135); a2.set_yticks([0, 20, 40, 60, 80, 100]); a2.set_ylabel("%")
    a2.set_title("Capacidad del sistema: programar y mostrar\nlos controles (v2.0, muestra de 500, corte 30/06/2024)", fontsize=9.5, pad=10)
    a2.legend(loc="upper left", fontsize=7.5)
    a2.text(0.0, -0.17, f"Vencidos detectados en la muestra: {vis['controles_vencidos_detectados']:,} controles de {vis['ninos_con_vencidos']} niños;".replace(",", " ") +
            f" concordancia con el oráculo: {num(vis['concordancia_con_el_oraculo']['por_control_pct'])} %.", transform=a2.transAxes, fontsize=7.5, color="#555555", va="top")
    fig.suptitle("Línea base real de la DIRESA Junín frente a la capacidad de la v2.0 (Incremento 2)", fontsize=11.5, fontweight="bold", y=0.99)
    fig.text(0.5, 0.005, "Fuente: izquierda, dataset «Niños menores de 36 meses con dx de anemia, Región Junín» (HIS, DIRESA Junín; corte 30/06/2024), calculado en datos/asis_dataset_diresa.json. "
                         "Derecha, v2.0.0-inc2 con la muestra estratificada de 500 niños (semilla 2026) y FECHA_REFERENCIA = 2024-06-30, datos/m32_dataset_real.json.\n"
                         "Los dos paneles miden cosas distintas (resultado del proceso actual frente a capacidad del sistema): no se promedian ni entran en el índice de valor. "
                         "No demuestran mejora clínica ni de asistencia.",
             ha="center", va="bottom", fontsize=7, color="#555555", wrap=True)
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    guardar(fig, "g10_linea_base_vs_inc2")


def main() -> None:
    for f in (g1, g2, g3, g4, g5, g6, g10):
        f()


if __name__ == "__main__":
    main()
