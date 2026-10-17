#!/usr/bin/env python
"""Consolida todas las métricas GQM (M1.1, M1.2, M2.1, M2.2, M3.1, M3.2) en datos/resumen_gqm.json.

Lee únicamente los JSON ya generados por los demás scripts y los resultados de capturas (evidencias_capturas/resultados_inc*.json);
no recalcula nada a mano. Para cada métrica: valor Inc. 1, valor Inc. 2, meta de la guía, ¿cumple?, variación % Inc.1->Inc.2
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
    r1, r2 = cargar("resultados_inc1.json", CAPT), cargar("resultados_inc2.json", CAPT)

    def dominio(v):
        d = m11[v]["dominio"]
        return {"importaciones_externas": d["n_externas"], "clases_dominio": d["n_clases"], "importaciones_totales": d["n_importaciones"]}

    ms = []

    def add(id_, nombre, formula, unidad, v1, v2, meta1, meta2, sentido, fuente, exactos=None, **extra):
        e1, e2 = exactos if exactos else (v1, v2)
        e = {"id": id_, "nombre": nombre, "formula": formula, "unidad": unidad, "sentido_meta": sentido,
             "valor_inc1": v1, "valor_inc2": v2, "meta_inc1": meta1, "meta_inc2": meta2,
             "cumple_inc1": cumple(e1, meta1, sentido), "cumple_inc2": cumple(e2, meta2, sentido),
             **variacion(e1, e2), "fuente": fuente}
        if exactos:
            e["valores_sin_redondear"] = {"inc1": round(e1, 4), "inc2": round(e2, 4)}
        e.update(extra)
        ms.append(e)

    # M1.1
    add("M1.1", "Índice de contaminación del dominio", "importaciones externas en dominio / clases de dominio x 100", "%",
        m11["v1.0"]["dominio"]["indice_contaminacion_pct"], m11["v1.5"]["dominio"]["indice_contaminacion_pct"], 0.0, 0.0, "<=",
        "datos/m11_contaminacion.json", detalle={"inc1": dominio("v1.0"), "inc2": dominio("v1.5")})
    # M1.2
    add("M1.2", "Conformidad estructural hexagonal", "componentes conformes (criterio estricto: ubicación + contenido) / 5 x 100", "%",
        m12["v1.0"]["m12_pct"], m12["v1.5"]["m12_pct"], 100.0, 100.0, ">=", "datos/m12_conformidad.json",
        variante_laxa={"inc1": m12["v1.0"]["sensibilidad"]["laxa_pct"], "inc2": m12["v1.5"]["sensibilidad"]["laxa_pct"]},
        detalle={"inc1_conformes": f"{m12['v1.0']['conformes']}/5", "inc2_conformes": f"{m12['v1.5']['conformes']}/5",
                 "inc1_estado": {f["componente"]: f["estado"] for f in m12["v1.0"]["filas"]}, "inc2_estado": {f["componente"]: f["estado"] for f in m12["v1.5"]["filas"]}})
    # M2.1
    rf1 = [rf for rf in ("RF-01", "RF-02", "RF-03", "RF-04", "RF-05")]
    ap1 = [rf for rf in rf1 if r1["criterios"].get(rf, {}).get("cumple")]
    rf2 = ["RF-06", "RF-07"]
    ap2 = [rf for rf in rf2 if r2["criterios"].get(rf, {}).get("cumple")]
    v1 = round(len(ap1) / len(rf1) * 100, 1)
    v2 = round(len(ap2) / len(rf2) * 100, 1)
    v2_total = round(len(ap2) / 4 * 100, 1)
    add("M2.1", "Cobertura de requisitos con captura aprobada", "RF con captura de resultado aprobada (criterio Dado-Cuando-Entonces cumplido) / RF del incremento x 100", "%",
        v1, v2, 100.0, 100.0, ">=", "evidencias_capturas/resultados_inc1.json y resultados_inc2.json",
        valor_inc2_sobre_alcance_total=v2_total, cumple_inc2_sobre_alcance_total=cumple(v2_total, 100.0, ">="),
        detalle={"inc1": f"{len(ap1)}/{len(rf1)} RF ({', '.join(ap1)})", "inc2_avance": f"{len(ap2)}/2 RF entregados en el avance ({', '.join(ap2)})",
                 "inc2_alcance_total": f"{len(ap2)}/4 RF del Inc. 2 (RF-06..RF-09); RF-08 y RF-09 pendientes (8 SP de 18)"})
    # M2.2
    add("M2.2", "Tasa de defectos funcionales por requisito", "defectos funcionales atribuibles / RF del incremento", "Def/RF",
        m22["inc1"]["tasa_def_por_rf"], m22["inc2"]["tasa_def_por_rf"], 1.0, 0.2, "<=", "datos/m22_defectos.json",
        variantes_inc1={"solo_detectados_antes_de_liberar": m22["inc1"]["variante_solo_detectados_antes_de_liberar"]["tasa_def_por_rf"],
                        "todos_incl_no_funcionales": m22["inc1"]["variante_todos_los_defectos_incl_no_funcionales"]["tasa_def_por_rf"]},
        detalle={"inc1": f"{m22['inc1']['n_funcionales']} funcionales / 5 RF ({', '.join(m22['inc1']['defectos_funcionales_antes_de_liberar'] + m22['inc1']['defectos_funcionales_escapados'])})",
                 "inc2": f"{m22['inc2']['n_funcionales_rf06_rf07']} funcionales / 2 RF",
                 "densidad_por_kloc": {"inc1": m22["inc1"]["densidad_por_kloc"], "inc2": m22["inc2"]["densidad_por_kloc"]}})
    # M3.1
    p1, p2 = m31["resultado_principal"]["v1.0"]["cobertura_pct"], m31["resultado_principal"]["v1.5"]["cobertura_pct"]
    c1, c2 = m31["cobertura_brechas_comprometidas_en_el_plan"]["Inc.1"]["cobertura_pct"], m31["cobertura_brechas_comprometidas_en_el_plan"]["Inc.2"]["cobertura_pct"]
    add("M3.1", "Cobertura de brechas AS-IS resueltas", "suma de puntajes B1..B6 (1 completa; 0,5 parcial; 0 no) / 6 x 100", "%",
        p1, p2, 60.0, 90.0, ">=", "datos/m31_brechas.json",
        exactos=(m31["resultado_principal"]["v1.0"]["suma_puntos"] / 6 * 100, m31["resultado_principal"]["v1.5"]["suma_puntos"] / 6 * 100),
        complementaria_brechas_comprometidas={"inc1_B1": c1, "inc2_B1_B2": c2,
                                              "cumple_inc1": cumple(c1, 60.0, ">="), "cumple_inc2": cumple(c2, 90.0, ">="),
                                              "nota": "denominador = brechas que el plan compromete hasta el incremento (Inc.1: B1; Inc.2: B1+B2)"},
        detalle={"inc1": m31["resultado_principal"]["v1.0"], "inc2": m31["resultado_principal"]["v1.5"],
                 "puntaje_por_brecha": {b: {"v1.0": x["v1.0"], "v1.5": x["v1.5"]} for b, x in m31["puntuacion"].items()},
                 "sensibilidad_B6_igual_a_0": m31["sensibilidad_B6_igual_a_0"]})
    # M3.2
    i1, i2 = m32["indice_impacto_en_valor_pct"]["v1.0"]["indice"], m32["indice_impacto_en_valor_pct"]["v1.5"]["indice"]
    add("M3.2", "Índice de impacto en valor para el usuario", "promedio simple de las mejoras de V1, V2 y V3 respecto de la línea base AS-IS", "%",
        i1, i2, 50.0, 80.0, ">=", "datos/m32_indice_valor.json",
        exactos=(m32["indice_impacto_en_valor_pct"]["v1.0"]["indice_sin_redondear"], m32["indice_impacto_en_valor_pct"]["v1.5"]["indice_sin_redondear"]),
        detalle={"mejoras_inc1": m32["indice_impacto_en_valor_pct"]["v1.0"]["mejoras"], "mejoras_inc2": m32["indice_impacto_en_valor_pct"]["v1.5"]["mejoras"],
                 "calidad_de_servicio_fuera_del_indice": {v: {"V4_p95_ms": m32["indicadores"][v]["V4_p95_agregado_ms_mix_comun"]["valor_ms"],
                                                              "V5_disponibilidad_pct": m32["indicadores"][v]["V5_disponibilidad_pct"]["valor_pct"],
                                                              "V6_criterios_verificados_pct": m32["indicadores"][v]["V6_satisfaccion_proxy_pct_criterios_verificados"]["valor_pct"]} for v in ("v1.0", "v1.5")},
                 "pendiente": "SUS real con usuarios (metricas/instrumento_SUS.md) no aplicado"})
    complementarias = {"M1.3_acoplamiento_I_por_capa": {v: {c_["capa"]: c_["I_capas"] for c_ in m13[v]["capas"]} for v in ("v1.0", "v1.5")},
                       "M1.3_violaciones_regla_dependencia": {v: m13[v]["n_violaciones"] for v in ("v1.0", "v1.5")}}
    out = {"fecha": "16/10/2026", "versiones": {"Inc.1": "v1.0-PMV", "Inc.2": "v1.5.0-inc2-avance (avance 50 %)"}, "metricas": ms, "complementarias": complementarias}
    (c.DATOS / "resumen_gqm.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for e in ms:
        print(f"{e['id']}: Inc1={e['valor_inc1']} Inc2={e['valor_inc2']} meta={e['meta_inc1']}/{e['meta_inc2']} cumple={e['cumple_inc1']}/{e['cumple_inc2']} var={e['variacion_pct']}")


if __name__ == "__main__":
    main()
