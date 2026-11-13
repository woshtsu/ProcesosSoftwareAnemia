#!/usr/bin/env python
"""Consolida todas las métricas GQM (M1.1, M1.2, M2.1, M2.2, M3.1, M3.2) en datos/resumen_gqm.json.

Lee únicamente los JSON ya generados por los demás scripts y los resultados de capturas (evidencias_capturas/resultados_*.json);
no recalcula nada a mano. Columnas: «Inc. 1» = v1.0-PMV; «avance v1.5» = hito intermedio (v1.5.0-inc2-avance, 50 %); «Inc. 2 (v2.0, cierre)» = v2.0.0-inc2.
Para cada métrica: valor de cada columna, meta de la guía (Inc. 1 / Inc. 2), ¿cumple?, variación % Inc.1->Inc.2 y avance->Inc.2
((v2 - v1) / v1 x 100; si v1 = 0: "n/a (base 0)" y diferencia absoluta) y archivo fuente.

Uso:  python resumen_gqm.py
"""

from __future__ import annotations

import json

import comun as c

CAPT = c.REPO / "entregables" / "semana-09" / "evidencias_capturas"


def cargar(n: str, base=c.DATOS):
    return json.loads((base / n).read_text(encoding="utf-8"))


def variacion(v1: float, v2: float) -> dict:
    """(v2 - v1) / v1 x 100 con los valores SIN redondear (los valores informados se muestran con 1 decimal)."""
    if v1 == 0:
        return {"variacion_pct": "n/a (base 0)", "diferencia_abs": round(v2 - v1, 2)}
    return {"variacion_pct": round((v2 - v1) / v1 * 100, 1), "diferencia_abs": round(v2 - v1, 2)}


def cumple(v: float, meta: float, sentido: str) -> bool:
    return v <= meta if sentido == "<=" else v >= meta


def main() -> None:
    m11, m12, m21, m22 = cargar("m11_contaminacion.json"), cargar("m12_conformidad.json"), cargar("m21_cobertura_rf.json"), cargar("m22_defectos.json")
    m31, m32 = cargar("m31_brechas.json"), cargar("m32_indice_valor.json")
    m13 = cargar("m13_acoplamiento.json")
    r1, r2, r3 = cargar("resultados_inc1.json", CAPT), cargar("resultados_inc2.json", CAPT), cargar("resultados_inc2final.json", CAPT)

    def dominio(v):
        d = m11[v]["dominio"]
        return {"importaciones_externas": d["n_externas"], "clases_dominio": d["n_clases"], "importaciones_totales": d["n_importaciones"]}

    ms = []

    def add(id_, nombre, formula, unidad, v1, v15, v2, meta1, meta2, sentido, fuente, exactos=None, **extra):
        """v1 = Inc. 1 (v1.0); v15 = avance v1.5 (hito intermedio); v2 = Inc. 2 (v2.0, cierre)."""
        e1, e15, e2 = exactos if exactos else (v1, v15, v2)
        e = {"id": id_, "nombre": nombre, "formula": formula, "unidad": unidad, "sentido_meta": sentido,
             "valor_inc1": v1, "valor_avance_v15": v15, "valor_inc2": v2, "meta_inc1": meta1, "meta_inc2": meta2,
             "cumple_inc1": cumple(e1, meta1, sentido), "cumple_avance_v15": cumple(e15, meta2, sentido), "cumple_inc2": cumple(e2, meta2, sentido),
             **variacion(e1, e2),
             "variacion_inc1_a_avance_v15": variacion(e1, e15), "variacion_avance_v15_a_inc2": variacion(e15, e2), "fuente": fuente}
        if exactos:
            e["valores_sin_redondear"] = {"inc1": round(e1, 4), "avance_v15": round(e15, 4), "inc2": round(e2, 4)}
        e.update(extra)
        ms.append(e)

    # M1.1
    add("M1.1", "Índice de contaminación del dominio", "importaciones externas en dominio / clases de dominio x 100", "%",
        m11["v1.0"]["dominio"]["indice_contaminacion_pct"], m11["v1.5"]["dominio"]["indice_contaminacion_pct"], m11["v2.0"]["dominio"]["indice_contaminacion_pct"],
        0.0, 0.0, "<=", "datos/m11_contaminacion.json", detalle={"inc1": dominio("v1.0"), "avance_v15": dominio("v1.5"), "inc2": dominio("v2.0")})
    # M1.2
    add("M1.2", "Conformidad estructural hexagonal", "componentes conformes (criterio estricto: ubicación + contenido) / 5 x 100", "%",
        m12["v1.0"]["m12_pct"], m12["v1.5"]["m12_pct"], m12["v2.0"]["m12_pct"], 100.0, 100.0, ">=", "datos/m12_conformidad.json",
        variante_laxa={"inc1": m12["v1.0"]["sensibilidad"]["laxa_pct"], "avance_v15": m12["v1.5"]["sensibilidad"]["laxa_pct"], "inc2": m12["v2.0"]["sensibilidad"]["laxa_pct"]},
        detalle={"inc1_conformes": f"{m12['v1.0']['conformes']}/5", "avance_v15_conformes": f"{m12['v1.5']['conformes']}/5", "inc2_conformes": f"{m12['v2.0']['conformes']}/5",
                 "inc1_estado": {f["componente"]: f["estado"] for f in m12["v1.0"]["filas"]}, "inc2_estado": {f["componente"]: f["estado"] for f in m12["v2.0"]["filas"]}})
    # M2.1 (capturas): Inc. 1 = RF-01..RF-05; avance = RF-06..RF-07; cierre = RF-06..RF-09 (RF-06 y RF-07 del avance + RF-08 y RF-09 de la v2.0)
    rf1 = ["RF-01", "RF-02", "RF-03", "RF-04", "RF-05"]
    ap1 = [rf for rf in rf1 if r1["criterios"].get(rf, {}).get("cumple")]
    rf_av = ["RF-06", "RF-07"]
    ap_av = [rf for rf in rf_av if r2["criterios"].get(rf, {}).get("cumple")]
    rf_cierre = ["RF-06", "RF-07", "RF-08", "RF-09"]
    ap_cierre = [rf for rf in ("RF-06", "RF-07") if r2["criterios"].get(rf, {}).get("cumple")] + [rf for rf in ("RF-08", "RF-09") if r3["criterios"].get(rf, {}).get("cumple")]
    v1 = round(len(ap1) / len(rf1) * 100, 1)
    v15 = round(len(ap_av) / len(rf_av) * 100, 1)
    v15_total = round(len(ap_av) / 4 * 100, 1)
    v2 = round(len(ap_cierre) / len(rf_cierre) * 100, 1)
    add("M2.1", "Cobertura de requisitos con captura aprobada", "RF con captura de resultado aprobada (criterio Dado-Cuando-Entonces cumplido) / RF del incremento x 100", "%",
        v1, v15, v2, 100.0, 100.0, ">=", "evidencias_capturas/resultados_inc1.json, resultados_inc2.json y resultados_inc2final.json",
        valor_avance_v15_sobre_alcance_total=v15_total, cumple_avance_v15_sobre_alcance_total=cumple(v15_total, 100.0, ">="),
        detalle={"inc1": f"{len(ap1)}/{len(rf1)} RF ({', '.join(ap1)})", "avance_v15": f"{len(ap_av)}/2 RF entregados en el avance ({', '.join(ap_av)}); {len(ap_av)}/4 sobre el alcance total",
                 "inc2": f"{len(ap_cierre)}/{len(rf_cierre)} RF del Inc. 2 ({', '.join(ap_cierre)}); RF-06 y RF-07 con las capturas del avance (v1.5), RF-08 y RF-09 con las capturas de la v2.0"})
    # M2.2
    add("M2.2", "Tasa de defectos funcionales por requisito", "defectos funcionales atribuibles / RF del incremento", "Def/RF",
        m22["inc1"]["tasa_def_por_rf"], m22["inc2_avance"]["tasa_def_por_rf"], m22["inc2"]["tasa_def_por_rf"], 1.0, 0.2, "<=", "datos/m22_defectos.json",
        variantes_inc1={"solo_detectados_antes_de_liberar": m22["inc1"]["variante_solo_detectados_antes_de_liberar"]["tasa_def_por_rf"],
                        "todos_incl_no_funcionales": m22["inc1"]["variante_todos_los_defectos_incl_no_funcionales"]["tasa_def_por_rf"]},
        variante_inc2_escapados_a_produccion={"valor": m22["inc2"]["variante_escapados_a_produccion"]["tasa_def_por_rf"],
                                              "cumple": m22["cumple"]["Inc.2_variante_escapados_a_produccion"],
                                              "regla": "defectos funcionales escapados a producción / 4 RF; la v2.0 aún no se libera y no hay escapados"},
        detalle={"inc1": f"{m22['inc1']['n_funcionales']} funcionales / 5 RF ({', '.join(m22['inc1']['defectos_funcionales_antes_de_liberar'] + m22['inc1']['defectos_funcionales_escapados'])})",
                 "avance_v15": f"{m22['inc2_avance']['n_funcionales_rf06_rf07']} funcionales / 2 RF",
                 "inc2": f"{m22['inc2']['n_funcionales']} funcional / 4 RF ({', '.join(m22['inc2']['defectos_funcionales_antes_de_liberar'])}, RF-08, detectado por E2E antes de liberar)",
                 "densidad_por_kloc": {"inc1": m22["inc1"]["densidad_por_kloc"], "avance_v15": m22["inc2_avance"]["densidad_por_kloc"], "inc2": m22["inc2"]["densidad_por_kloc"]}})
    # M3.1
    P = m31["resultado_principal"]
    C = m31["cobertura_brechas_comprometidas_en_el_plan"]
    add("M3.1", "Cobertura de brechas AS-IS resueltas", "suma de puntajes B1..B6 (1 completa; 0,5 parcial; 0 no) / 6 x 100", "%",
        P["v1.0"]["cobertura_pct"], P["v1.5"]["cobertura_pct"], P["v2.0"]["cobertura_pct"], 60.0, 90.0, ">=", "datos/m31_brechas.json",
        exactos=(P["v1.0"]["suma_puntos"] / 6 * 100, P["v1.5"]["suma_puntos"] / 6 * 100, P["v2.0"]["suma_puntos"] / 6 * 100),
        complementaria_brechas_comprometidas={"inc1_B1": C["Inc.1"]["cobertura_pct"], "avance_v15_B1_B2": C["avance_v1.5"]["cobertura_pct"], "inc2_B1_B2": C["Inc.2"]["cobertura_pct"],
                                              "cumple_inc1": cumple(C["Inc.1"]["cobertura_pct"], 60.0, ">="), "cumple_inc2": cumple(C["Inc.2"]["cobertura_pct"], 90.0, ">="),
                                              "nota": "denominador = brechas que el plan compromete hasta el incremento (Inc.1: B1; Inc.2: B1+B2). B2 sigue en 0,5 porque faltan los recordatorios a la familia (INC-4)"},
        sensibilidad_inc2=m31["sensibilidad_v2.0_B2_y_B3"],
        detalle={"inc1": P["v1.0"], "avance_v15": P["v1.5"], "inc2": P["v2.0"],
                 "puntaje_por_brecha": {b: {"v1.0": x["v1.0"], "v1.5": x["v1.5"], "v2.0": x["v2.0"]} for b, x in m31["puntuacion"].items()},
                 "sensibilidad_B6_igual_a_0": m31["sensibilidad_B6_igual_a_0"]})
    # M3.2
    I = m32["indice_impacto_en_valor_pct"]
    q = lambda v: {"V4_p95_ms": m32["indicadores"][v]["V4_p95_agregado_ms_mix_comun"]["valor_ms"], "V5_disponibilidad_pct": m32["indicadores"][v]["V5_disponibilidad_pct"]["valor_pct"], "V6_criterios_verificados_pct": m32["indicadores"][v]["V6_satisfaccion_proxy_pct_criterios_verificados"]["valor_pct"]}  # noqa: E731
    add("M3.2", "Índice de impacto en valor para el usuario", "promedio simple de las mejoras de V1, V2 y V3 respecto de la línea base AS-IS", "%",
        I["v1.0"]["indice"], I["v1.5"]["indice"], I["v2.0"]["indice"], 50.0, 80.0, ">=", "datos/m32_indice_valor.json",
        exactos=(I["v1.0"]["indice_sin_redondear"], I["v1.5"]["indice_sin_redondear"], I["v2.0"]["indice_sin_redondear"]),
        detalle={"mejoras_inc1": I["v1.0"]["mejoras"], "mejoras_avance_v15": I["v1.5"]["mejoras"], "mejoras_inc2": I["v2.0"]["mejoras"],
                 "calidad_de_servicio_fuera_del_indice": {v: q(v) for v in ("v1.0", "v1.5", "v2.0")},
                 "linea_base_real_DIRESA": "ver datos/m32_indice_valor.json, sección linea_base_real_DIRESA (no entra en el índice)",
                 "pendiente": "SUS real con usuarios (metricas/instrumento_SUS.md) no aplicado"})
    complementarias = {"M1.3_acoplamiento_I_por_capa": {v: {c_["capa"]: c_["I_capas"] for c_ in m13[v]["capas"]} for v in c.VERSIONES},
                       "M1.3_violaciones_regla_dependencia": {v: m13[v]["n_violaciones"] for v in c.VERSIONES},
                       "criterios_DCE_verificados": {v: f"{m21[v]['criterios_verificados']}/{m21[v]['criterios_total']}" for v in c.VERSIONES}}
    out = {"fecha": "17/10/2026",
           "versiones": {"Inc.1": "v1.0-PMV", "avance_v1.5": "v1.5.0-inc2-avance (hito intermedio, 50 %)", "Inc.2": "v2.0.0-inc2 (cierre del incremento)"},
           "metricas": ms, "complementarias": complementarias}
    (c.DATOS / "resumen_gqm.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for e in ms:
        print(f"{e['id']}: Inc1={e['valor_inc1']} avance={e['valor_avance_v15']} Inc2={e['valor_inc2']} meta={e['meta_inc1']}/{e['meta_inc2']} cumple={e['cumple_inc1']}/{e['cumple_avance_v15']}/{e['cumple_inc2']} var={e['variacion_pct']}")


if __name__ == "__main__":
    main()
