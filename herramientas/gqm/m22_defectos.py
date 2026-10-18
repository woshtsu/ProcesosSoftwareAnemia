#!/usr/bin/env python
"""M2.2 Tasa de defectos funcionales por requisito (Def/RF) y densidad por KLOC.

Regla (decidida por el orquestador, aplicada tal cual):
  - Cada DEF-01..DEF-nn se clasifica FUNCIONAL o NO FUNCIONAL y se asigna al RF afectado.
  - Inc. 1 (v1.0-PMV): defectos funcionales atribuibles a RF-01..RF-05 = detectados antes de liberar (DEF-02) +
    escapados detectados en el ciclo del Inc. 2 (DEF-03..07)  /  5 RF.  Variantes: solo detectados antes de liberar
    (DEF-02 / 5) y todos los defectos incluidos los no funcionales (DEF-01..07 / 5).
  - Inc. 2 (cierre, v2.0.0-inc2): defectos funcionales en el código NUEVO de RF-06..RF-09 detectados en el ciclo del incremento (antes de liberar) +
    escapados a producción / 4 RF del incremento. Lectura principal = 1/4 = 0,25 Def/RF (DEF-09, hallado por las pruebas E2E de RF-08 antes de
    liberar); variante «escapados a producción» = 0/4 (la versión aún no se libera y las 27 exploratorias de RF-08/RF-09 no hallaron fallas).
  - Inc. 2 (avance, v1.5): defectos funcionales en RF-06 y RF-07 detectados en su propio ciclo / 2 RF entregados. Se verifica con
    pruebas exploratorias reales (exploratorias_inc2.py -> datos/exploratorias_inc2.json) sobre los endpoints NUEVOS; los
    defectos que aparezcan se registran como DEF-08... en registro_defectos_inc2.md (se leen de allí).
  - Densidad: KLOC = líneas sin blancos ni comentarios de app/**/*.py de cada versión (criterio de los registros de defectos).

Salida: datos/m22_defectos.json
"""

from __future__ import annotations

import json
import re
from collections import Counter

import comun as c

REGISTRO1 = c.RAICES["v2.0"] / "docs" / "evidencias" / "registro_defectos.md"
REGISTRO2 = c.RAICES["v2.0"] / "docs" / "evidencias" / "registro_defectos_inc2.md"

# Clasificación por defecto (justificada con el registro y el código). "rf" = RF principal afectado; "rf_secundarios" = otros RF
# que comparten el código defectuoso (no se cuentan dos veces).
CLASIFICACION = {
    "DEF-01": {"tipo": "NO FUNCIONAL", "rf": "RF-05", "momento": "detectado antes de liberar (Inc. 1)",
               "justificacion": "Patrón N+1 en el reporte del periodo: el resultado era correcto pero tardaba p95 = 2 200 ms con 50 usuarios; es un atributo de rendimiento, no de comportamiento funcional."},
    "DEF-02": {"tipo": "FUNCIONAL", "rf": "RF-05", "momento": "detectado antes de liberar (Inc. 1)",
               "justificacion": "El conteo de registrados del periodo comparaba días en UTC y excluía registros posteriores a las 19:00 de Perú: el reporte entregaba cifras incorrectas."},
    "DEF-03": {"tipo": "FUNCIONAL", "rf": "RF-05", "momento": "escapado, detectado en el ciclo del Inc. 2",
               "justificacion": "GET /api/reportes/periodo respondía 500 con fechas extremas (9999-12-31): la funcionalidad del reporte fallaba con una entrada aceptada por el esquema."},
    "DEF-04": {"tipo": "FUNCIONAL", "rf": "RF-01", "rf_secundarios": ["RF-02"], "momento": "escapado, detectado en el ciclo del Inc. 2",
               "justificacion": "El registro aceptaba y guardaba DNI/celular con dígitos Unicode o salto de línea: la validación de datos del registro (RF-01, también en PATCH de RF-02) era incorrecta."},
    "DEF-05": {"tipo": "FUNCIONAL", "rf": "RF-03", "momento": "escapado, detectado en el ciclo del Inc. 2",
               "justificacion": "La vista previa clínica devolvía Hb ajustada y clasificación sin sentido con altitud NaN/99999 o nacimiento absurdo: la validación con reglas clínicas (RF-03) estaba incompleta."},
    "DEF-06": {"tipo": "FUNCIONAL", "rf": "RF-01", "rf_secundarios": ["RF-02"], "momento": "escapado, detectado en el ciclo del Inc. 2",
               "justificacion": "Textos sin largo máximo: se guardaban nombres de 100 000 caracteres aunque la columna es VARCHAR(80); falla la validación de datos del registro (RF-01)."},
    "DEF-07": {"tipo": "FUNCIONAL", "rf": "RF-04", "momento": "escapado, detectado en el ciclo del Inc. 2",
               "justificacion": "La búsqueda del seguimiento (GET /api/ninos?q=) trataba % y _ como comodines SQL y devolvía resultados engañosos (RF-04)."},
    "DEF-08": {"tipo": "FUNCIONAL", "rf": "RF-01", "momento": "escapado, detectado en el ciclo del Inc. 2",
               "justificacion": "Dos registros simultáneos con el mismo DNI: el segundo respondía 500 en lugar de 409 (carrera entre la comprobación previa y la restricción UNIQUE); el registro de niños (RF-01) no manejaba bien el DNI duplicado. Código heredado del Inc. 1, hallado por la exploración EX-42 en el ciclo del Inc. 2."},
    "DEF-09": {"tipo": "FUNCIONAL", "rf": "RF-08", "momento": "detectado antes de liberar (Inc. 2, código nuevo)",
               "justificacion": "En la pestaña Agenda (RF-08), la respuesta de la carga inicial sobrescribía las fechas «Desde» y «Hasta» que la persona acababa de escribir y «Consultar» pedía otro rango: la funcionalidad de elegir el rango de la agenda del personal fallaba. Hallado por las pruebas E2E de RF-08 (CP-180, CP-183 y CP-186) en código nuevo, antes de liberar la v2.0."},
}
RF_INC1 = ["RF-01", "RF-02", "RF-03", "RF-04", "RF-05"]
RF_INC2_AVANCE = ["RF-06", "RF-07"]
RF_INC2_CIERRE = ["RF-06", "RF-07", "RF-08", "RF-09"]
# Casos exploratorios que cubren código HEREDADO del Inc. 1 (no del código nuevo de agenda/alertas)
CASOS_HEREDADOS = {"EX-12", "EX-13", "EX-35", "EX-36", "EX-42", "EX-45"}


def kloc(version: str) -> dict:
    raiz = c.RAICES[version] / "app"
    arch = [p for p in raiz.rglob("*.py") if "__pycache__" not in p.parts]
    n = sum(c.lineas_codigo(p) for p in arch)
    return {"archivos": len(arch), "lineas_sin_blancos_ni_comentarios": n, "kloc": round(n / 1000, 3)}


def defectos_registrados() -> list[str]:
    ids = []
    for ruta in (REGISTRO1, REGISTRO2):
        ids += re.findall(r"^\| (DEF-\d+) \|", ruta.read_text(encoding="utf-8"), re.M)
    return ids


def main() -> None:
    reg = defectos_registrados()
    sin_clasificar = [d for d in reg if d not in CLASIFICACION]
    assert not sin_clasificar, f"defectos del registro sin clasificar en m22_defectos.py: {sin_clasificar}"
    for d in CLASIFICACION:
        assert d in reg, f"{d} no figura en los registros"
    # defectos funcionales hallados en el código NUEVO (RF-06/RF-07) durante el ciclo del Inc. 2
    nuevos = [d for d, v in CLASIFICACION.items() if v["tipo"] == "FUNCIONAL" and v["rf"] in RF_INC2_AVANCE]
    nuevos_info = {d: CLASIFICACION[d]["justificacion"] for d in nuevos}
    expl = json.loads((c.DATOS / "exploratorias_inc2.json").read_text(encoding="utf-8"))
    cnt = Counter(x["estado"] for x in expl)
    nuevos_casos = [x for x in expl if x["id"] not in CASOS_HEREDADOS]
    cnt_nuevo = Counter(x["estado"] for x in nuevos_casos)
    cnt_herd = Counter(x["estado"] for x in expl if x["id"] in CASOS_HEREDADOS)
    fallas_nuevo = [x["id"] for x in nuevos_casos if x["estado"] == "FALLA"]
    fallas_herd = [x["id"] for x in expl if x["id"] in CASOS_HEREDADOS and x["estado"] == "FALLA"]

    # --- Inc. 1 ---
    clas_inc1 = {d: v for d, v in CLASIFICACION.items() if v["rf"] in RF_INC1}  # DEF-01..08: atribuibles a RF-01..RF-05
    func = {d: v for d, v in clas_inc1.items() if v["tipo"] == "FUNCIONAL"}
    antes = [d for d, v in func.items() if v["momento"].startswith("detectado antes")]
    escapados = [d for d, v in func.items() if v["momento"].startswith("escapado")]
    por_rf = {rf: [d for d, v in func.items() if v["rf"] == rf] for rf in RF_INC1}
    por_rf_todos = {rf: [d for d, v in clas_inc1.items() if v["rf"] == rf] for rf in RF_INC1}
    v_main = (len(antes) + len(escapados)) / 5
    k10, k15, k20 = kloc("v1.0"), kloc("v1.5"), kloc("v2.0")
    inc1 = {
        "regla": "(funcionales detectados antes de liberar + funcionales escapados detectados en el ciclo del Inc. 2) / 5 RF",
        "defectos_funcionales_antes_de_liberar": antes,
        "defectos_funcionales_escapados": escapados,
        "n_funcionales": len(antes) + len(escapados),
        "n_rf": 5,
        "tasa_def_por_rf": round(v_main, 2),
        "variante_solo_detectados_antes_de_liberar": {"n": len(antes), "tasa_def_por_rf": round(len(antes) / 5, 2)},
        "variante_sin_DEF-08_valor_antes_de_la_campana_de_exploratorias": {"n": len(antes) + len(escapados) - 1, "tasa_def_por_rf": round((len(antes) + len(escapados) - 1) / 5, 2),
                                                                           "nota": "DEF-08 (RF-01, carrera de DNI duplicado) se halló con las 45 pruebas exploratorias de caja negra; sin él el valor era 6/5."},
        "variante_todos_los_defectos_incl_no_funcionales": {"n": len(clas_inc1), "tasa_def_por_rf": round(len(clas_inc1) / 5, 2)},
        "funcionales_por_rf": {rf: {"defectos": ds, "n": len(ds)} for rf, ds in por_rf.items()},
        "todos_los_defectos_por_rf": {rf: {"defectos": ds, "n": len(ds)} for rf, ds in por_rf_todos.items()},
        "densidad_por_kloc": {
            "kloc_v1.0": k10["kloc"],
            "funcionales_atribuibles": round((len(antes) + len(escapados)) / k10["kloc"], 2),
            "solo_antes_de_liberar": round(len(antes) / k10["kloc"], 2),
            "todos_incl_no_funcionales": round(len(clas_inc1) / k10["kloc"], 2),
            "nota": "KLOC del código del Inc. 1 (v1.0-PMV). Los DEF-03..08 se hallaron en v1.5 pero estaban en código heredado del Inc. 1.",
        },
    }
    # --- Inc. 2 ---
    n_func_inc2 = len(nuevos)  # DEF-08.. registrados (cada uno es funcional en RF-06/07 si así consta en el registro)
    tasa2 = n_func_inc2 / 2
    inc2 = {
        "regla": "defectos funcionales en RF-06 y RF-07 detectados en su ciclo / 2 RF entregados en el avance",
        "n_funcionales_rf06_rf07": n_func_inc2,
        "defectos": list(nuevos),
        "detalle_registro": nuevos_info,
        "n_rf": 2,
        "tasa_def_por_rf": round(tasa2, 2),
        "verificacion_exploratoria": {
            "script": "herramientas/gqm/exploratorias_inc2.py",
            "salida_texto": "entregables/semana-09/metricas/salidas/exploratorias_inc2_resultado.txt",
            "casos_totales": len(expl),
            "estados_todos": dict(cnt),
            "casos_sobre_codigo_nuevo": len(nuevos_casos),
            "estados_codigo_nuevo": dict(cnt_nuevo),
            "fallas_en_codigo_nuevo": fallas_nuevo,
            "casos_sobre_codigo_heredado": len(CASOS_HEREDADOS),
            "estados_codigo_heredado": dict(cnt_herd),
            "fallas_en_codigo_heredado": fallas_herd,
            "nota": "OBS = comportamiento que la especificación no define o decisión de diseño documentada; no se cuenta como defecto.",
            "historial_de_corridas": "corrida 1: 3 FALLA (EX-22 y EX-31 eran errores de diseño de los casos, corregidos; EX-42 era el defecto real DEF-08 en código heredado); corrida 2: 1 FALLA (EX-43, un PATCH con 'database is locked' de SQLite bajo 8 escritores simultáneos, reclasificado como OBS: limitación del motor de desarrollo; las lecturas de alertas, código nuevo, no fallaron); corrida 3 (final): 43 OK, 2 OBS, 0 FALLA. Ver salidas/exploratorias_inc2_resultado*.txt",
        },
        "densidad_por_kloc": {
            "kloc_v1.5": k15["kloc"],
            "por_kloc_total_v1.5": round(n_func_inc2 / k15["kloc"], 2),
            "kloc_neto_incremento_aprox": round((k15["lineas_sin_blancos_ni_comentarios"] - k10["lineas_sin_blancos_ni_comentarios"]) / 1000, 3),
            "por_kloc_neto_incremento_aprox": round(n_func_inc2 / ((k15["lineas_sin_blancos_ni_comentarios"] - k10["lineas_sin_blancos_ni_comentarios"]) / 1000), 2),
            "nota": "KLOC neto = líneas de v1.5 menos líneas de v1.0 (aproximación del código nuevo; v1.5 también modifica código heredado).",
        },
    }
    # --- Inc. 2 (cierre, v2.0.0-inc2) ---
    cierre = {d: v for d, v in CLASIFICACION.items() if v["rf"] in RF_INC2_CIERRE and v["rf"] not in RF_INC1}
    cierre_fun = {d: v for d, v in cierre.items() if v["tipo"] == "FUNCIONAL"}
    antes_c = [d for d, v in cierre_fun.items() if v["momento"].startswith("detectado antes")]
    escapados_c = [d for d, v in cierre_fun.items() if v["momento"].startswith("escapado")]
    explo_final = json.loads((c.DATOS / "exploratorias_inc2_final.json").read_text(encoding="utf-8"))
    cnt_f = Counter(x["estado"] for x in explo_final)
    n_cierre = len(antes_c) + len(escapados_c)
    delta_loc = k20["lineas_sin_blancos_ni_comentarios"] - k15["lineas_sin_blancos_ni_comentarios"]
    inc2_cierre = {
        "regla": "(defectos funcionales del código nuevo de RF-06..RF-09 detectados en el ciclo del incremento, antes de liberar + escapados a producción) / 4 RF del incremento",
        "n_rf": 4, "rf": RF_INC2_CIERRE,
        "defectos_funcionales_antes_de_liberar": antes_c,
        "defectos_funcionales_escapados_a_produccion": escapados_c,
        "n_funcionales": n_cierre,
        "tasa_def_por_rf": round(n_cierre / 4, 2),
        "lectura_principal": "1/4 = 0,25 Def/RF: DEF-09 (RF-08) detectado por las pruebas E2E antes de liberar cuenta como defecto funcional del incremento",
        "variante_escapados_a_produccion": {"n": len(escapados_c), "tasa_def_por_rf": round(len(escapados_c) / 4, 2),
                                            "nota": "La v2.0.0-inc2 aún no se libera (el tag v2.0-Inc2 lo crea el equipo): por definición no hay defectos escapados. Las 27 exploratorias de RF-08/RF-09 no hallaron fallas."},
        "detalle_registro": {d: v["justificacion"] for d, v in cierre_fun.items()},
        "defectos_por_rf": {rf: [d for d, v in cierre_fun.items() if v["rf"] == rf] for rf in RF_INC2_CIERRE},
        "verificacion_exploratoria_rf08_rf09": {
            "script": "herramientas/gqm/exploratorias_inc2_final.py",
            "salida_texto": "entregables/semana-09/metricas/salidas/exploratorias_inc2_final_resultado.txt",
            "casos": len(explo_final), "estados": dict(cnt_f),
            "historial_de_corridas": "corrida 1: 25 OK y 2 FALLA (EXF-28 y EXF-29 eran errores de diseño de los casos: el control cerrado por recuperación elegido tenía fecha futura, por lo que el 422 era el resultado correcto, y la evaluación vinculada elegida era la más antigua, que ya cumplía otro control); corregidos los casos, corrida 2 (final): 27 OK, 0 FALLA, 0 OBS. Ver salidas/exploratorias_inc2_final_resultado*.txt"},
        "densidad_por_kloc": {
            "kloc_v2.0": k20["kloc"], "kloc_v1.5": k15["kloc"],
            "por_kloc_total_v2.0": round(n_cierre / k20["kloc"], 2),
            "kloc_agregado_en_el_cierre_aprox": round(delta_loc / 1000, 3),
            "por_kloc_agregado_en_el_cierre_aprox": round(n_cierre / (delta_loc / 1000), 2),
            "nota": "KLOC agregado = líneas de v2.0 menos líneas de v1.5 (aproximación del código nuevo de RF-08, RF-09 y el dataset; incluye cambios en código existente)."},
    }
    meta = {"Inc.1": 1.0, "Inc.2": 0.2}
    salida = {
        "clasificacion_por_defecto": CLASIFICACION,
        "defectos_en_registros": reg,
        "kloc": {"v1.0": k10, "v1.5": k15, "v2.0": k20},
        "inc1": inc1,
        "inc2_avance": inc2,
        "inc2": inc2_cierre,
        "meta_guia_def_por_rf_max": meta,
        "cumple": {"Inc.1": inc1["tasa_def_por_rf"] <= meta["Inc.1"], "avance_v1.5": inc2["tasa_def_por_rf"] <= meta["Inc.2"],
                   "Inc.2": inc2_cierre["tasa_def_por_rf"] <= meta["Inc.2"],
                   "Inc.2_variante_escapados_a_produccion": inc2_cierre["variante_escapados_a_produccion"]["tasa_def_por_rf"] <= meta["Inc.2"],
                   "Inc.1_variante_solo_antes_de_liberar": inc1["variante_solo_detectados_antes_de_liberar"]["tasa_def_por_rf"] <= meta["Inc.1"]},
    }
    (c.DATOS / "m22_defectos.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"inc1": inc1["tasa_def_por_rf"], "variantes": [inc1["variante_solo_detectados_antes_de_liberar"], inc1["variante_todos_los_defectos_incl_no_funcionales"]], "avance_v1.5": inc2["tasa_def_por_rf"], "inc2_cierre": inc2_cierre["tasa_def_por_rf"],
                      "explo_avance": inc2["verificacion_exploratoria"]["estados_codigo_nuevo"], "explo_cierre": inc2_cierre["verificacion_exploratoria_rf08_rf09"]["estados"], "cumple": salida["cumple"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
