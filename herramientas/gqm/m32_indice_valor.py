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

Entradas: datos/m32_v1.0_B150.json, m32_v1.5_B150.json, m32_carga.json, m32_disponibilidad.json, m21_cobertura_rf.json
Salida: datos/m32_indice_valor.json
"""

from __future__ import annotations

import json

import comun as c

BASE = {"V1_registros_por_evaluacion": 3, "V2_pct_agenda": 0.0, "V3_pct_deteccion": 0.0}


def main() -> None:
    d = lambda n: json.loads((c.DATOS / n).read_text(encoding="utf-8"))  # noqa: E731
    m = {"v1.0": d("m32_v1.0_B150.json"), "v1.5": d("m32_v1.5_B150.json")}
    carga, disp, m21 = d("m32_carga.json"), d("m32_disponibilidad.json"), d("m21_cobertura_rf.json")
    esc = {"v1.0": "v10_comun", "v1.5": "v15_comun"}
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
    for v in ("v1.0", "v1.5"):
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
                                                   "criterio": "v1.0: campo control_atrasado heurístico (30 días); v1.5: normativo", "fuente": f"datos/m32_{v}_B150.json (V3)"},
            "V4_p95_agregado_ms_mix_comun": {"valor_ms": p["p95_ms"], "mediana_ms": p["mediana_ms"], "p99_ms": p["p99_ms"], "fallos_pct": p["pct_fallos"], "rps": p["rps"], "fuente": "datos/m32_carga.json"},
            "V5_disponibilidad_pct": {"valor_pct": av["disponibilidad_pct"], "sondas": av["sondas"], "fuente": "datos/m32_disponibilidad.json"},
            "V6_satisfaccion_proxy_pct_criterios_verificados": {"valor_pct": crit["pct_criterios_verificados"], "criterios": f"{crit['criterios_verificados']}/{crit['criterios_total']}", "fuente": "datos/m21_cobertura_rf.json",
                                                                 "pendiente": "SUS real con usuarios (instrumento en metricas/instrumento_SUS.md): no aplicado"},
        }
        out["indice_impacto_en_valor_pct"][v] = {"mejoras": mej, "indice": idx, "indice_sin_redondear": round(idx_exacto, 4)}
    out["indicadores"]["v1.5"]["V4_p95_agregado_ms_mix_ampliado_agenda_alertas"] = {
        "valor_ms": carga["escenarios"]["v15_agenda"]["promedio"]["AGREGADO"]["p95_ms"], "fuente": "datos/m32_carga.json (v15_agenda)"}
    out["meta_guia_pct"] = {"Inc.1": 50.0, "Inc.2": 80.0}
    out["cumple"] = {"Inc.1": out["indice_impacto_en_valor_pct"]["v1.0"]["indice"] >= 50.0, "Inc.2": out["indice_impacto_en_valor_pct"]["v1.5"]["indice"] >= 80.0}
    out["advertencia"] = ("V1 de v1.0 y v1.5 es idéntico (un registro nominal único desde el Inc. 1). El índice de v1.5 es 100 % porque los tres indicadores "
                          "con línea base alcanzan su máximo; no equivale a 100 % del alcance del Inc. 2 (avance 2/4 historias): mide solo los tres indicadores definidos.")
    (c.DATOS / "m32_indice_valor.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"indice": out["indice_impacto_en_valor_pct"], "cumple": out["cumple"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
