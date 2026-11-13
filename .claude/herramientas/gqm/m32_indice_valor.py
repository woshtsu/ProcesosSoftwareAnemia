#!/usr/bin/env python
"""M3.2 Índice de impacto en valor: consolida V1..V6 desde las mediciones reales (no inventa líneas base).

Líneas base AS-IS estructurales y demostrables (S1/S6): 3 registros por evaluación (historia clínica, tarjeta y HIS);
0 % de controles programados automáticamente; 0 % de detección automática de controles vencidos.

  V1 registros por evaluación        mejora = (3 - x) / (3 - 1) x 100          (% del recorrido ideal 3 -> 1 logrado)
  V2 % de niños activos con agenda normativa generada   mejora = valor alcanzado (%) (AS-IS = 0)
  V3 F1 de detección de controles vencidos vs oráculo   mejora = F1 x 100 (%)       (AS-IS = 0)
  Índice de impacto en valor = promedio simple de las mejoras de V1, V2 y V3 (los tres con línea base AS-IS).
  V4 p95 agregado, V5 disponibilidad y V6 satisfacción proxy (% de criterios Dado-Cuando-Entonces verificados) se informan
  como indicadores de calidad de servicio, FUERA del promedio: no hay línea base AS-IS medida (el proceso en papel no
  tiene tiempo de respuesta ni disponibilidad comparables) y el SUS real con usuarios sigue pendiente.

Versiones: v1.0 (Inc. 1), v1.5 (avance del Inc. 2) y v2.0 (cierre del Inc. 2). V1..V3 se miden con el dataset sintético B150 (mismo dataset y misma fecha
de referencia, 16/10/2026, en las tres versiones) para que sean comparables.

Sección «linea_base_real_DIRESA»: línea base AS-IS REAL calculada sobre el dataset completo de la DIRESA Junín (12 486 diagnósticos, corte 30/06/2024;
datos/asis_dataset_diresa.json) y, aparte, la capacidad de la v2.0 sobre la muestra de 500 niños importada (datos/m32_dataset_real.json). Son magnitudes de
naturaleza distinta (resultado del proceso actual frente a capacidad del sistema): se presentan lado a lado, NO se promedian ni entran en el índice.

Entradas: datos/m32_v1.0_B150.json, m32_v1.5_B150.json, m32_v2.0_B150.json, m32_carga.json, m32_disponibilidad.json, m21_cobertura_rf.json,
          asis_dataset_diresa.json, m32_dataset_real.json
Salida: datos/m32_indice_valor.json
"""

from __future__ import annotations

import json

import comun as c

BASE = {"V1_registros_por_evaluacion": 3, "V2_pct_agenda": 0.0, "V3_pct_deteccion": 0.0}


def _ind(x: dict) -> dict:
    return {"n": x["n"], "N": x["N"], "pct": x["pct"], "formula": x["formula"]}


def linea_base_real(d) -> dict:
    """Línea base AS-IS real (dataset completo DIRESA Junín) y capacidad de la v2.0 sobre la muestra de 500 niños. No se promedian."""
    asis, real = d("asis_dataset_diresa.json"), d("m32_dataset_real.json")
    g = asis["indicadores_globales"]
    vis = real["visibilidad_agenda_personal"]
    cap = real["capacidad_del_sistema_controles_de_tratamiento"]["por_control"]
    return {
        "fuente_as_is": "datos/asis_dataset_diresa.json (.claude/herramientas/dataset/analisis_asis.py) sobre el dataset completo: 12 486 diagnósticos de anemia en menores de 36 meses, DIRESA Junín, HIS, corte 30/06/2024",
        "fuente_v2_0": "datos/m32_dataset_real.json: muestra estratificada de 500 niños (Provincia x severidad HIS, semilla 2026) importada a la v2.0 con FECHA_REFERENCIA=2024-06-30",
        "regla_seguimiento_posible": asis["parametros"]["regla_seguimiento_posible"] + f" (plazos {asis['parametros']['plazos_dias']}, holgura {asis['parametros']['holgura_dias']} d)",
        "control_de_hemoglobina_registrado": {
            "al_mes": {"bruto": _ind(g["control_mes"]), "con_seguimiento_posible": _ind(g["control_mes_con_seguimiento_posible"])},
            "a_los_3_meses": {"bruto": _ind(g["control_3m"]), "con_seguimiento_posible": _ind(g["control_3m_con_seguimiento_posible"])},
            "a_los_6_meses": {"bruto": _ind(g["control_6m"]), "con_seguimiento_posible": _ind(g["control_6m_con_seguimiento_posible"])},
            "lectura": "«Bruto» divide por todos los diagnosticados (penaliza a quienes aún no podían tener el control por el corte); «con seguimiento posible» divide solo por quienes ya habían cumplido el plazo más la holgura. Mide dosajes registrados en ventana, no asistencia real."},
        "perdida_de_seguimiento_a_6_meses": {"bruto": _ind(g["perdida_seguimiento_6m"]), "con_seguimiento_posible": _ind(g["perdida_seguimiento_6m_con_seguimiento_posible"]),
                                             "sin_ningun_control_bruto": _ind(g["sin_ningun_control"]), "sin_ningun_control_con_seguimiento_posible": _ind(g["sin_ningun_control_con_seguimiento_posible"])},
        "recuperacion_documentada": {"bruta": _ind(g["recuperacion_documentada"]), "con_seguimiento_6m": _ind(g["recuperacion_con_seguimiento_6m"]),
                                     "con_seguimiento_12m": _ind(g["recuperacion_con_seguimiento_12m"]), "sobre_control_de_cierre_6m": _ind(g["recuperados_sobre_control_cierre"])},
        "controles_vencidos_visibles_para_el_personal": {
            "definicion": "% de los controles vencidos (según el oráculo independiente de la agenda normativa) que el personal puede ver como VENCIDO en la agenda del personal (GET /api/agenda) y en la lista de alertas",
            "as_is_pct": 0.0,
            "as_is_justificacion": "No existe agenda ni lista de controles vencidos en el proceso actual (cuaderno, tarjeta e HIS): el control depende de que el niño vuelva y alguien lo registre; un control vencido no es visible hasta que el niño ya no regresa (B2, B5).",
            "v2_0_muestra_500_pct": vis["pct_visibles"],
            "v2_0_n": vis["visibles_en_agenda_del_personal"], "v2_0_N": vis["controles_vencidos_oraculo"],
            "v2_0_visibles_en_alertas_pct": vis["pct_visibles_en_alertas"],
            "ninos_activos_con_agenda_generada": {"as_is_pct": 0.0, "v2_0_pct": real["V2_real_agenda_por_nino"]["pct_agenda"],
                                                  "v2_0_n": real["V2_real_agenda_por_nino"]["con_agenda_generada"], "v2_0_N": real["V2_real_agenda_por_nino"]["activos"]},
            "concordancia_con_el_oraculo": {"por_nino_F1": real["oraculo"]["por_nino"]["F1"], "por_control_pct": real["oraculo"]["por_control"]["concordancia_pct"],
                                            "coinciden": real["oraculo"]["por_control"]["coinciden"], "controles": real["oraculo"]["por_control"]["controles_oraculo"]},
            "controles_vencidos_detectados": real["vencidos_detectados"]["controles_vencidos"], "ninos_con_vencidos": real["vencidos_detectados"]["ninos_con_vencidos"],
            "por_prioridad": real["vencidos_detectados"]["por_prioridad"],
            "capacidad_por_control_de_tratamiento": cap},
        "advertencias_de_lectura": [
            "El AS-IS (resultado del proceso: dosajes registrados en el HIS) y la v2.0 (capacidad del sistema: controles visibles) NO miden lo mismo y no se promedian ni entran en el índice de impacto en valor; se muestran lado a lado.",
            "El 0 % del AS-IS es estructural (no existe agenda), no una medición sobre el dataset; el 100 % de la v2.0 es sobre la muestra de 500 niños importada, no sobre los 12 486 diagnósticos ni sobre los resultados clínicos.",
            "«Vencido» en la v2.0 significa «sin registro en la base importada»: el extracto del HIS solo trae el diagnóstico y los dosajes al mes, 3 y 6 meses, de modo que los dosajes por edad (6, 9, 12 meses...) figuran como vencidos aunque pudieran haberse hecho.",
            "La visibilidad no demuestra mejora clínica ni de asistencia: eso requiere un piloto con usuarios (el SUS y la medición en campo siguen pendientes).",
        ],
    }


def main() -> None:
    d = lambda n: json.loads((c.DATOS / n).read_text(encoding="utf-8"))  # noqa: E731
    m = {"v1.0": d("m32_v1.0_B150.json"), "v1.5": d("m32_v1.5_B150.json"), "v2.0": d("m32_v2.0_B150.json")}
    carga, disp, m21 = d("m32_carga.json"), d("m32_disponibilidad.json"), d("m21_cobertura_rf.json")
    esc = {"v1.0": "v10_comun", "v1.5": "v15_comun", "v2.0": "v20_comun"}
    out = {"lineas_base_as_is": {**BASE, "fuente": "Diagnóstico S1/S6: tres registros manuales por evaluación (historia clínica, tarjeta de control y HIS); sin agenda ni detección automática de vencidos"},
           "formulas": {
               "V1": "mejora_pct = (3 - registros_por_evaluacion) / (3 - 1) x 100",
               "V2": "mejora_pct = % de niños ACTIVOS con agenda normativa generada (GET /api/ninos/{id}/agenda = 200 y aplica); AS-IS = 0",
               "V3": "mejora_pct = F1 x 100 de control_atrasado (GET /api/ninos) frente al oráculo normativo independiente; AS-IS = 0",
               "indice": "promedio simple de mejora_pct de V1, V2 y V3",
               "V4": "p95 agregado de Locust (50 usuarios, 60 s), mix común de tareas, promedio de 2 corridas (ms) - indicador de calidad de servicio",
               "V5": "disponibilidad = sondas GET /api/salud con 200 en < 2 s / sondas x 100 - indicador de calidad de servicio",
               "V6": "% de criterios Dado-Cuando-Entonces con su(s) prueba(s) automatizada(s) en verde (m21) - proxy de satisfacción; el SUS real queda pendiente (metricas/instrumento_SUS.md)"},
           "indicadores": {}, "indice_impacto_en_valor_pct": {}}
    for v in c.VERSIONES:
        x = m[v]
        v1 = x["V1"]["registros_por_evaluacion"]
        v2 = x["V2"]["pct_agenda"]
        f1 = x["V3"]["control_atrasado_api_ninos"]["F1"] * 100
        mej_exacta = {"V1": (3 - v1) / (3 - 1) * 100, "V2": v2, "V3": f1}
        mej = {k: round(x, 1) for k, x in mej_exacta.items()}
        idx_exacto = sum(mej_exacta.values()) / 3
        idx = round(idx_exacto, 1)
        p = carga["escenarios"][esc[v]]["promedio"]["AGREGADO"]
        av = disp["total_por_version"][v]
        crit = m21[v]
        out["indicadores"][v] = {
            "V1_registros_por_evaluacion": {"as_is": 3, "valor": v1, "mejora_pct": mej["V1"], "fuente": f"datos/m32_{v}_B150.json (V1)"},
            "V2_pct_ninos_activos_con_agenda_normativa": {"as_is": 0.0, "valor_pct": v2, "activos": x["V2"]["activos"], "con_agenda": x["V2"]["con_agenda_generada"], "mejora_pct": mej["V2"], "fuente": f"datos/m32_{v}_B150.json (V2)"},
            "V3_F1_deteccion_controles_vencidos": {"as_is": 0.0, "F1": round(x["V3"]["control_atrasado_api_ninos"]["F1"], 4), "precision": round(x["V3"]["control_atrasado_api_ninos"]["precision"], 4), "sensibilidad": round(x["V3"]["control_atrasado_api_ninos"]["sensibilidad"], 4),
                                                   "matriz": {k: x["V3"]["control_atrasado_api_ninos"][k] for k in ("TP", "FP", "FN", "TN")}, "mejora_pct": mej["V3"],
                                                   "criterio": "v1.0: campo control_atrasado heurístico (30 días); v1.5 y v2.0: normativo", "fuente": f"datos/m32_{v}_B150.json (V3)"},
            "V4_p95_agregado_ms_mix_comun": {"valor_ms": p["p95_ms"], "mediana_ms": p["mediana_ms"], "p99_ms": p["p99_ms"], "fallos_pct": p["pct_fallos"], "rps": p["rps"], "fuente": "datos/m32_carga.json"},
            "V5_disponibilidad_pct": {"valor_pct": av["disponibilidad_pct"], "sondas": av["sondas"], "fuente": "datos/m32_disponibilidad.json"},
            "V6_satisfaccion_proxy_pct_criterios_verificados": {"valor_pct": crit["pct_criterios_verificados"], "criterios": f"{crit['criterios_verificados']}/{crit['criterios_total']}", "fuente": "datos/m21_cobertura_rf.json",
                                                                 "pendiente": "SUS real con usuarios (instrumento en metricas/instrumento_SUS.md): no aplicado"},
        }
        out["indice_impacto_en_valor_pct"][v] = {"mejoras": mej, "indice": idx, "indice_sin_redondear": round(idx_exacto, 4)}
    out["indicadores"]["v1.5"]["V4_p95_agregado_ms_mix_ampliado_agenda_alertas"] = {
        "valor_ms": carga["escenarios"]["v15_agenda"]["promedio"]["AGREGADO"]["p95_ms"], "fuente": "datos/m32_carga.json (v15_agenda)"}
    out["indicadores"]["v2.0"]["V4_p95_agregado_ms_mix_ampliado_agenda_personal_asistencia"] = {
        "valor_ms": carga["escenarios"]["v20_ampliado"]["promedio"]["AGREGADO"]["p95_ms"], "fuente": "datos/m32_carga.json (v20_ampliado)",
        "nota": "mix del locustfile de la v2.0: común + agenda del niño, alertas, resumen, agenda del personal y asistencias; no es comparable con el mix común"}
    # V4 de la v1.0 repetida en la misma sesión que la v2.0 (controla el ruido de la máquina)
    v10c = carga["escenarios"]["v10_comun"]
    if "promedio_por_sesion" in v10c:
        s17 = v10c["promedio_por_sesion"]["2026-10-17"]
        out["indicadores"]["v1.0"]["V4_p95_agregado_ms_mix_comun"]["repeticion_misma_sesion_que_v2.0"] = {
            "corridas": s17["corridas"], "valor_ms": s17["promedio"]["AGREGADO"]["p95_ms"], "mediana_ms": s17["promedio"]["AGREGADO"]["mediana_ms"],
            "p99_ms": s17["promedio"]["AGREGADO"]["p99_ms"], "fallos_pct": s17["promedio"]["AGREGADO"]["pct_fallos"], "rps": s17["promedio"]["AGREGADO"]["rps"]}
    out["meta_guia_pct"] = {"Inc.1": 50.0, "Inc.2": 80.0}
    out["cumple"] = {"Inc.1": out["indice_impacto_en_valor_pct"]["v1.0"]["indice"] >= 50.0, "avance_v1.5": out["indice_impacto_en_valor_pct"]["v1.5"]["indice"] >= 80.0,
                     "Inc.2": out["indice_impacto_en_valor_pct"]["v2.0"]["indice"] >= 80.0}
    out["advertencia"] = ("V1 de v1.0, v1.5 y v2.0 es idéntico (un registro nominal único desde el Inc. 1). El índice de v1.5 y el de v2.0 son 100 % porque los tres "
                          "indicadores con línea base alcanzan su máximo en el dataset B150; mide solo los tres indicadores definidos (V1, V2, V3), no el alcance completo del incremento "
                          "ni el valor clínico. La agenda del personal y la asistencia (RF-08 y RF-09) no tienen un indicador propio en el índice: se verifican con los criterios Dado-Cuando-Entonces (M2.1/V6) y con la sección linea_base_real_DIRESA.")
    out["linea_base_real_DIRESA"] = linea_base_real(d)
    (c.DATOS / "m32_indice_valor.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"indice": out["indice_impacto_en_valor_pct"], "cumple": out["cumple"]}, ensure_ascii=False))
    print(json.dumps(out["linea_base_real_DIRESA"]["controles_vencidos_visibles_para_el_personal"], ensure_ascii=False)[:600])


if __name__ == "__main__":
    main()
