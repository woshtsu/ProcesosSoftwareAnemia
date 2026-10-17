#!/usr/bin/env python
"""Cobertura de RF por pruebas automatizadas y criterios de aceptación Dado-Cuando-Entonces verificados (G-02, V7 proxy).

Complementa a M2.1 (que usa capturas): aquí se calcula, por RF y por versión,
  * qué pruebas automatizadas (archivo::prueba) lo verifican (mapa curado por QA, validado contra el código por AST);
  * % de RF con >= 1 prueba automatizada y con >= 1 prueba E2E;
  * % de criterios de aceptación Dado-Cuando-Entonces (DCE) cuyas pruebas están TODAS en verde, EJECUTANDO las pruebas
    de cada versión con pytest (JUnit XML) y leyendo el resultado real.
  * como verificación cruzada, las pruebas que "mencionan" los endpoints del RF según búsqueda por patrón (grep).

Los criterios DCE los redactó QA a partir de la descripción de cada RF (spec S9), de las historias HIST-1.x del
entregable S5 y de ADR-007; la guía S5 no trae criterios DCE para el PMV FastAPI. Pueden sustituirse por los de las fichas
de prueba sin cambiar el método.

Uso:  python m21_cobertura_rf.py [--version v1.0|v1.5|ambas] [--sin-ejecutar]
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import comun as c

PY = os.getenv("PY", sys.executable)
A = "tests/integracion/test_api.py"
Z = "tests/integracion/test_zona_horaria.py"
UE = "tests/unitarias/test_entidades.py"
UR = "tests/unitarias/test_reglas_clinicas.py"
UC = "tests/unitarias/test_casos_uso.py"
E = "tests/e2e/test_interfaz.py"
A2 = "tests/integracion/test_api_inc2.py"
UA = "tests/unitarias/test_agenda.py"
UAL = "tests/unitarias/test_alertas.py"
UC2 = "tests/unitarias/test_casos_uso_inc2.py"
UR2 = "tests/unitarias/test_regresion_inc2.py"


def t(archivo: str, *nombres: str) -> list[str]:
    return [f"{archivo}::{n}" for n in nombres]


# Criterios DCE por RF. Cada criterio: (id, texto Dado-Cuando-Entonces, [pruebas])
COMUN = {
    "RF-01": [
        ("RF-01-C1", "Dado un niño con datos válidos y su evaluación inicial, cuando se registra (POST /api/ninos), entonces responde 201 con un único expediente y la evaluación clasificada.",
         t(A, "test_registro_exitoso_devuelve_expediente") + t(UC, "test_registrar_nino_crea_expediente_con_evaluacion_clasificada")),
        ("RF-01-C2", "Dado un DNI ya registrado, cuando se intenta registrar de nuevo, entonces responde 409 y no se duplica el expediente.",
         t(A, "test_registro_duplicado_devuelve_409") + t(UC, "test_registro_duplicado_por_dni_se_rechaza")),
        ("RF-01-C3", "Dado un dato inválido o ausente, cuando se registra, entonces responde 422 con un mensaje por campo y no se guarda nada.",
         t(A, "test_datos_fuera_de_rango_devuelven_422_con_mensajes_en_espanol", "test_formato_invalido_devuelve_422_en_espanol")
         + t(UC, "test_registro_invalido_acumula_errores_de_nino_y_evaluacion") + t(UE, "test_dni_debe_tener_8_digitos", "test_campos_obligatorios_vacios")),
        ("RF-01-C4", "Dado el formulario de registro con datos válidos, cuando el personal pulsa Guardar, entonces la interfaz muestra el expediente creado.",
         t(E, "test_hu01_hu03_registro_con_vista_previa_y_expediente")),
    ],
    "RF-02": [
        ("RF-02-C1", "Dado un niño registrado, cuando se consulta su expediente por id o por DNI, entonces se muestran sus datos y evaluaciones; un id inexistente responde 404.",
         t(A, "test_consultar_expediente_por_id_y_dni") + t(UC, "test_consultar_y_buscar_por_dni")),
        ("RF-02-C2", "Dado un expediente, cuando se actualizan campos editables, entonces se guardan; un cambio inválido se rechaza con mensaje por campo.",
         t(A, "test_actualizar_expediente_y_registrar_control") + t(UC, "test_actualizar_datos_editables", "test_actualizar_rechaza_cambios_invalidos")),
        ("RF-02-C3", "Dado un expediente, cuando se registra un nuevo control, entonces se agrega a la evolución sin perder los anteriores.",
         t(A, "test_actualizar_expediente_y_registrar_control") + t(UC, "test_registrar_nuevo_control")),
        ("RF-02-C4", "Dado el listado de seguimiento, cuando el personal abre un niño, entonces la interfaz muestra la tabla de evaluaciones del expediente.",
         t(E, "test_hu04_seguimiento_y_busqueda")),
    ],
    "RF-03": [
        ("RF-03-C1", "Dado un control sin guardar, cuando se solicita la vista previa, entonces se devuelven la Hb ajustada por altitud y la clasificación, sin persistir nada.",
         t(A, "test_vista_previa_de_validacion") + t(UC, "test_vista_previa_no_guarda") + t(UR, "test_ajuste_por_altitud_segun_ecuacion", "test_hemoglobina_ajustada_resta_el_ajuste")),
        ("RF-03-C2", "Dado un valor de Hb en los límites de los puntos de corte por edad, cuando se clasifica, entonces el resultado respeta los umbrales (SIN_ANEMIA, LEVE, MODERADA, SEVERA, NO_APLICA).",
         t(UR, "test_clasificacion_en_limites_de_los_puntos_de_corte", "test_fuera_de_rango_de_edad_no_aplica") + t(UE, "test_evaluacion_calcula_ajuste_y_clasificacion")),
        ("RF-03-C3", "Dado un valor fuera del rango clínico, cuando se valida, entonces se rechaza con un mensaje comprensible por campo (422).",
         t(UE, "test_evaluacion_fuera_de_rango", "test_mensaje_de_hemoglobina_es_comprensible") + t(A, "test_datos_fuera_de_rango_devuelven_422_con_mensajes_en_espanol")),
        ("RF-03-C4", "Dado un formulario con datos inválidos, cuando se intenta guardar, entonces la interfaz marca los campos y explica el error.",
         t(E, "test_hu03_datos_invalidos_muestran_mensaje_comprensible")),
    ],
    "RF-04": [
        ("RF-04-C1", "Dados niños activos, cuando se lista el seguimiento, entonces se muestran con su última clasificación, ordenados por severidad, con filtros.",
         t(A, "test_listado_de_seguimiento_con_filtros") + t(UC, "test_listar_seguimiento_prioriza_casos_graves_y_filtra")),
        ("RF-04-C2", "Dado el listado, cuando el personal busca por DNI o nombre, entonces la interfaz filtra y permite abrir el expediente.",
         t(E, "test_hu04_seguimiento_y_busqueda")),
    ],
    "RF-05": [
        ("RF-05-C1", "Dado un periodo válido, cuando se solicita el reporte, entonces se entregan conteos por clasificación y comunidad en JSON y en CSV.",
         t(A, "test_reporte_json_y_csv") + t(UC, "test_reporte_del_periodo")),
        ("RF-05-C2", "Dado un registro hecho de noche (hora de Perú), cuando se genera el reporte del día, entonces se cuenta en el día local correcto.",
         t(Z, "test_registro_nocturno_cuenta_en_el_dia_local") + t(UC, "test_reporte_cuenta_registros_nocturnos_en_el_dia_local") + t(UE, "test_fecha_local_usa_hora_de_peru")),
        ("RF-05-C3", "Dado el módulo de reporte, cuando el personal genera el reporte, entonces la interfaz muestra los indicadores del periodo.",
         t(E, "test_hu05_reporte_del_periodo")),
    ],
}
INC2 = {
    "RF-01": [("RF-01-C5", "Dado un DNI o celular con dígitos no ASCII o salto de línea final, cuando se registra o se actualiza, entonces se rechaza (regresión DEF-04).",
               t(A2, "test_cp103_def04_dni_y_celular_solo_digitos_ascii_y_coincidencia_completa") + t(UR2, "test_cp85_def04_dni_solo_acepta_digitos_ascii", "test_cp86_def04_celular_exige_coincidencia_completa_y_digitos_ascii"))],
    "RF-03": [("RF-03-C5", "Dada una vista previa con altitud NaN/absurda o fecha de nacimiento absurda, cuando se solicita, entonces se rechaza con 422 (regresión DEF-05).",
               t(A2, "test_cp104_def05_vista_previa_rechaza_altitudes_invalidas", "test_cp107_nan_o_infinito_en_la_evaluacion_se_rechazan_con_mensaje_claro") + t(UR2, "test_cp87_def05_la_vista_previa_valida_la_altitud"))],
    "RF-04": [("RF-04-C3", "Dado el seguimiento, cuando un niño tiene al menos un control vencido de la agenda normativa, entonces control_atrasado es verdadero y se informa controles_vencidos.",
               t(A2, "test_cp100_listado_de_seguimiento_usa_los_controles_vencidos") + t(UC2, "test_cp82_seguimiento_marca_atrasado_solo_con_controles_vencidos")),
              ("RF-04-C4", "Dada una búsqueda con % o _, cuando se lista, entonces se tratan como texto y no como comodines (regresión DEF-07).",
               t(A2, "test_cp106_def07_la_busqueda_trata_los_comodines_como_texto"))],
    "RF-05": [("RF-05-C4", "Dado un periodo con fechas extremas, cuando se solicita el reporte, entonces responde 422 y no 500 (regresión DEF-03).",
               t(A2, "test_cp102_def03_reporte_con_fechas_extremas_devuelve_422_y_no_500") + t(UR2, "test_cp84_def03_el_servicio_rechaza_el_periodo_extremo"))],
    "RF-06": [
        ("RF-06-C1", "Dado un niño activo, cuando se consulta su agenda, entonces se devuelven los 12 dosajes por edad y los controles de tratamiento con fecha programada y ventana -15/+30 días.",
         t(A2, "test_cp89_agenda_de_un_nino", "test_cp90_campos_de_cada_control") + t(UA, "test_cp46_recien_nacido_tiene_los_12_dosajes_por_edad_pendientes", "test_cp47_fechas_programadas_con_nacimiento_en_fin_de_mes", "test_cp49_ventana_de_cumplimiento_valores_frontera")),
        ("RF-06-C2", "Dada una evaluación con anemia, cuando se genera la agenda, entonces se programan C1M, C3M y C6M, sin reiniciar el calendario y con cierre por recuperación.",
         t(A2, "test_cp91_agenda_de_tratamiento_y_proximo_a_vencer") + t(UA, "test_cp53_anemia_programa_c1m_c3m_c6m_con_suma_segura_de_meses", "test_cp56_episodio_con_recuperacion_cierra_los_controles_pendientes", "test_cp57_controles_ya_vencidos_antes_de_la_recuperacion_siguen_vencidos", "test_cp58_evaluaciones_con_anemia_dentro_del_episodio_no_reinician_el_calendario", "test_cp59_nuevo_episodio_tras_vencer_el_c6m_o_tras_una_recuperacion")),
        ("RF-06-C3", "Dados controles en la frontera de la ventana, cuando se calcula el estado, entonces se distinguen CUMPLIDO, PENDIENTE (con próximo a 7 días) y VENCIDO; no se programan controles de 60 meses o más.",
         t(UA, "test_cp48_la_agenda_empieza_cuando_el_nino_entra_al_sistema", "test_cp50_estados_pendiente_proximo_y_vencido_en_la_frontera", "test_cp61_los_controles_de_tratamiento_no_pasan_de_los_59_meses", "test_cp62_un_dosaje_por_edad_de_60_meses_o_mas_no_se_programa")),
        ("RF-06-C4", "Dado un id inexistente o un niño con alta, cuando se consulta la agenda, entonces responde 404 o aplica=false, respectivamente.",
         t(A2, "test_cp92_agenda_de_nino_inexistente_devuelve_404", "test_cp93_nino_con_alta_no_tiene_agenda") + t(UA, "test_cp63_nino_con_alta_no_tiene_agenda") + t(UC2, "test_cp74_agenda_de_un_nino_inexistente_es_no_encontrado")),
        ("RF-06-C5", "Dado un control pendiente vigente, cuando se registra una evaluación en su ventana, entonces lo cumple (una evaluación cumple a lo sumo un control).",
         t(A2, "test_cp94_registrar_un_control_cumple_el_pendiente_vigente_pero_no_rescata_los_vencidos") + t(UA, "test_cp51_una_evaluacion_cumple_a_lo_sumo_un_control")),
        ("RF-06-C6", "Dado el expediente de un niño, cuando el personal lo abre, entonces la interfaz muestra la sección Agenda de controles (casos especiales incluidos).",
         t(E, "test_cp109_hist21_agenda_de_controles_en_el_expediente", "test_cp110_hist21_agenda_casos_especiales")),
    ],
    "RF-07": [
        ("RF-07-C1", "Dados niños con controles vencidos, cuando se consultan las alertas, entonces se listan ordenadas por prioridad (ALTA, MEDIA, BAJA) y por mayor atraso, con datos para contactar a la familia.",
         t(A2, "test_cp95_controles_vencidos_ordenados_con_los_datos_del_nino") + t(UAL, "test_cp67_prioridad_valores_frontera", "test_cp68_una_alerta_por_control_vencido_con_los_datos_para_contactar_a_la_familia", "test_cp70_orden_por_prioridad_y_luego_por_mayor_atraso") + t(UC2, "test_cp76_controles_vencidos_ordenados_por_prioridad_y_atraso")),
        ("RF-07-C2", "Dados filtros por comunidad y prioridad, cuando se consultan las alertas, entonces se filtran; una prioridad inválida responde 422.",
         t(A2, "test_cp96_filtros_por_comunidad_y_prioridad", "test_cp97_prioridad_invalida_devuelve_422") + t(UC2, "test_cp78_filtro_por_comunidad", "test_cp79_filtro_por_prioridad_y_combinado")),
        ("RF-07-C3", "Dadas las alertas, cuando se pide el resumen, entonces se informan total, por prioridad, niños distintos y próximos a vencer; sin niños, todo en cero.",
         t(A2, "test_cp98_resumen_de_alertas", "test_cp99_sin_ninos_las_alertas_estan_vacias") + t(UAL, "test_cp71_resumen_cuenta_por_prioridad_y_ninos_distintos", "test_cp72_resumen_vacio_incluye_todas_las_prioridades_en_cero") + t(UC2, "test_cp80_resumen_de_alertas")),
        ("RF-07-C4", "Dado un niño con alta, cuando se consultan las alertas, entonces no genera alertas.",
         t(UC2, "test_cp77_los_ninos_con_alta_no_generan_alertas")),
        ("RF-07-C5", "Dada la pestaña Alertas, cuando el personal la abre y filtra, entonces se muestran el resumen, la tabla filtrable y la navegación al expediente; la vista móvil no desborda.",
         t(E, "test_cp111_hist22_pestana_de_alertas_resumen_filtros_y_navegacion", "test_cp112_hist22_vista_movil_sin_desborde_horizontal")),
    ],
}

# Patrones para la verificación cruzada por búsqueda (grep) sobre el código fuente de cada prueba.
PATRONES = {
    "RF-01": r'registrar_nino\(|cuerpo_registro|\.post\(\s*"/api/ninos"|validar_datos_nino|llenar_registro',
    "RF-02": r'consultar\(|consultar_por_dni|actualizar_datos|registrar_evaluacion\(|/evaluaciones|\.patch\(|/api/ninos/dni',
    "RF-03": r'previsualizar_evaluacion|/api/validaciones/evaluacion|clasificar_anemia|hemoglobina_ajustada|validar_datos_evaluacion',
    "RF-04": r'listar_seguimiento|get\(\s*"/api/ninos"|control_atrasado|tab-seguimiento',
    "RF-05": r'reporte_periodo|/api/reportes/periodo|tab-reporte',
    "RF-06": r'generar_agenda|/agenda|ServicioAgenda|escenario\.agenda',
    "RF-07": r'/api/alertas|ServicioAlertas|alertas_de_nino|listar_controles_vencidos|resumen_alertas|tab-alertas',
}


def criterios(version: str) -> dict:
    cr = {rf: list(v) for rf, v in COMUN.items()}
    if version == "v1.5":
        for rf, extra in INC2.items():
            cr.setdefault(rf, [])
            cr[rf] += extra
    return cr


def funciones_de_prueba(raiz: Path) -> dict[str, str]:
    """{archivo::nombre: código fuente} de todas las pruebas (def test_*) de la versión."""
    res = {}
    for p in sorted((raiz / "tests").rglob("test_*.py")):
        src = p.read_text(encoding="utf-8")
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"):
                res[f"{p.relative_to(raiz)}::{n.name}"] = ast.get_source_segment(src, n) or ""
    return res


def ejecutar(raiz: Path, ids: list[str], salida_xml: Path) -> dict[str, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "COVERAGE_FILE": str(salida_xml.with_suffix(".cov"))}
    cmd = [PY, "-m", "pytest", *ids, "--no-cov", "-p", "no:cacheprovider", "-q", f"--junitxml={salida_xml}"]
    proc = subprocess.run(cmd, cwd=raiz, env=env, capture_output=True, text=True)
    salida_xml.with_suffix(".txt").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    est: dict[str, list[str]] = {}
    for tc in ET.parse(salida_xml).getroot().iter("testcase"):
        archivo = tc.get("classname", "").replace(".", "/")
        # classname = tests.unitarias.test_agenda -> tests/unitarias/test_agenda.py
        nombre = tc.get("name", "").split("[")[0]
        clave = f"{archivo}.py::{nombre}"
        r = "passed"
        if tc.find("failure") is not None or tc.find("error") is not None:
            r = "failed"
        elif tc.find("skipped") is not None:
            r = "skipped"
        est.setdefault(clave, []).append(r)
    return {k: ("passed" if all(x == "passed" for x in v) else ("skipped" if "skipped" in v else "failed")) for k, v in est.items()}


def evaluar(version: str, ejecutar_pruebas: bool) -> dict:
    raiz = c.RAICES[version]
    funcs = funciones_de_prueba(raiz)
    cr = criterios(version)
    ids = sorted({x for lst in cr.values() for (_i, _t, p) in lst for x in p})
    inexistentes = [i for i in ids if i not in funcs]
    ids_ok = [i for i in ids if i in funcs]
    estado: dict[str, str] = {}
    if ejecutar_pruebas:
        xml = c.SALIDAS / version / "m21_criterios_dce.xml"
        estado = ejecutar(raiz, ids_ok, xml)
    por_rf = {}
    for rf, lst in sorted(cr.items()):
        pruebas = sorted({x for (_i, _t, p) in lst for x in p if x in funcs})
        crit = []
        for cid, texto, p in lst:
            res = [estado.get(x, "no_ejecutada" if ejecutar_pruebas else "sin_ejecutar") for x in p if x in funcs]
            ok = bool(res) and all(r == "passed" for r in res)
            crit.append({"id": cid, "criterio": texto, "pruebas": p, "estados": res, "verificado_en_verde": ok})
        grep = sorted(k for k, src in funcs.items() if re.search(PATRONES[rf], src))
        por_rf[rf] = {
            "pruebas_curadas": pruebas, "n_pruebas": len(pruebas),
            "n_e2e": sum(1 for x in pruebas if "/e2e/" in x),
            "n_integracion": sum(1 for x in pruebas if "/integracion/" in x),
            "n_unitarias": sum(1 for x in pruebas if "/unitarias/" in x),
            "criterios": crit,
            "pct_criterios_verificados": round(sum(1 for k in crit if k["verificado_en_verde"]) / len(crit) * 100, 1),
            "menciones_grep": len(grep), "menciones_grep_pruebas": grep,
        }
    rfs = sorted(por_rf)
    return {
        "version": version, "rfs_evaluados": rfs, "pruebas_inexistentes_en_codigo": inexistentes,
        "n_rf": len(rfs),
        "rf_con_prueba_automatizada": sum(1 for r in rfs if por_rf[r]["n_pruebas"] >= 1),
        "rf_con_e2e": sum(1 for r in rfs if por_rf[r]["n_e2e"] >= 1),
        "pct_rf_con_prueba": round(sum(1 for r in rfs if por_rf[r]["n_pruebas"] >= 1) / len(rfs) * 100, 1),
        "pct_rf_con_e2e": round(sum(1 for r in rfs if por_rf[r]["n_e2e"] >= 1) / len(rfs) * 100, 1),
        "criterios_total": sum(len(por_rf[r]["criterios"]) for r in rfs),
        "criterios_verificados": sum(sum(1 for k in por_rf[r]["criterios"] if k["verificado_en_verde"]) for r in rfs),
        "pct_criterios_verificados": round(
            sum(sum(1 for k in por_rf[r]["criterios"] if k["verificado_en_verde"]) for r in rfs)
            / sum(len(por_rf[r]["criterios"]) for r in rfs) * 100, 1),
        "por_rf": por_rf,
        "ejecutadas": ejecutar_pruebas,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="ambas", choices=["v1.0", "v1.5", "ambas"])
    ap.add_argument("--sin-ejecutar", action="store_true")
    ap.add_argument("--json", default=str(c.DATOS / "m21_cobertura_rf.json"))
    a = ap.parse_args()
    vs = ["v1.0", "v1.5"] if a.version == "ambas" else [a.version]
    out = {v: evaluar(v, not a.sin_ejecutar) for v in vs}
    for v in vs:
        r = out[v]
        print(f"\n=== {c.ETIQUETA[v]}: RF con prueba {r['rf_con_prueba_automatizada']}/{r['n_rf']}, con E2E {r['rf_con_e2e']}/{r['n_rf']}, "
              f"criterios DCE verificados {r['criterios_verificados']}/{r['criterios_total']} ({r['pct_criterios_verificados']} %)")
        if r["pruebas_inexistentes_en_codigo"]:
            print("  PRUEBAS INEXISTENTES:", r["pruebas_inexistentes_en_codigo"])
        for rf, d in r["por_rf"].items():
            print(f"  {rf}: {d['n_pruebas']} pruebas (u={d['n_unitarias']} i={d['n_integracion']} e2e={d['n_e2e']}), "
                  f"criterios {d['pct_criterios_verificados']} %, menciones grep={d['menciones_grep']}")
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("->", a.json)


if __name__ == "__main__":
    main()
