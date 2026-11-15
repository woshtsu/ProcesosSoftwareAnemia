#!/usr/bin/env python
"""M3.1 Cobertura de brechas AS-IS resueltas (B1..B6) por versión, con evidencia comprobada sobre el software real.

Regla de puntuación (decidida por el orquestador): una brecha cuenta 1 si su mecanismo TO-BE completo está operativo y
probado; 0,5 si está parcial (operativo y probado solo en parte); 0 si no.

El script no "calcula" la puntuación (es un juicio de ingeniería), pero SÍ verifica con evidencia ejecutable los hechos
en los que se apoya cada puntuación: rutas HTTP existentes en el código de cada versión, ausencia de palabras clave de
funcionalidad (recordatorio, barrera, riesgo, abandono) en app/, resultados de V2/V3 medidos por API (datos/m32_*_B150.json)
y pruebas que cubren cada requisito (datos/m21_cobertura_rf.json).

Versiones: v1.0 (Inc. 1), v1.5 (avance del Inc. 2) y v2.0 (cierre del Inc. 2). La escala NO cambia (1 / 0,5 / 0). En la v2.0 se re-evalúan B2 y B3
con las funciones nuevas (agenda del personal, asistencia con motivo de inasistencia) y se informan las sensibilidades.

Salida: datos/m31_brechas.json
"""

from __future__ import annotations

import json
import re

import comun as c

PALABRAS = ["recordatorio", "barrera", "riesgo", "abandono", "sms", "whatsapp", "push"]


def rutas(version: str) -> list[str]:
    raiz = c.RAICES[version]
    api = next(p for p in (raiz / "app").rglob("api.py"))
    txt = api.read_text(encoding="utf-8")
    return sorted({f"{m.group(1).upper()} {m.group(2)}" for m in re.finditer(r'@router\.(get|post|patch|put|delete)\(\s*"([^"]+)"', txt)})


def ocurrencias(version: str, palabra: str) -> list[str]:
    raiz = c.RAICES[version]
    res = []
    for p in sorted((raiz / "app").rglob("*")):
        if p.suffix not in {".py", ".js", ".html"} or "vendor" in p.parts or "__pycache__" in p.parts:
            continue
        for i, ln in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if re.search(r"\b" + palabra, ln, re.I):
                res.append(f"{p.relative_to(raiz)}:{i}: {ln.strip()[:100]}")
    return res


def main() -> None:
    m21 = json.loads((c.DATOS / "m21_cobertura_rf.json").read_text())
    v10 = json.loads((c.DATOS / "m32_v1.0_B150.json").read_text())
    v15 = json.loads((c.DATOS / "m32_v1.5_B150.json").read_text())
    v20 = json.loads((c.DATOS / "m32_v2.0_B150.json").read_text())
    real = json.loads((c.DATOS / "m32_dataset_real.json").read_text())
    r = {v: rutas(v) for v in c.VERSIONES}
    kw = {v: {p: ocurrencias(v, p) for p in PALABRAS} for v in c.VERSIONES}
    hechos = {
        "rutas_http_relativas_al_prefijo_api": r,
        "palabras_clave_en_app": {v: {p: len(x) for p, x in d.items()} for v, d in kw.items()},
        "palabras_clave_detalle_no_vacias": {v: {p: x for p, x in d.items() if x} for v, d in kw.items()},
        "agenda_v1.0_http": v10["V2"]["codigos_http_agenda"],
        "agenda_v1.5_http": v15["V2"]["codigos_http_agenda"],
        "agenda_v2.0_http": v20["V2"]["codigos_http_agenda"],
        "pct_ninos_activos_con_agenda": {"v1.0": v10["V2"]["pct_agenda"], "v1.5": v15["V2"]["pct_agenda"], "v2.0": v20["V2"]["pct_agenda"]},
        "F1_vencidos_vs_oraculo": {"v1.0": round(v10["V3"]["control_atrasado_api_ninos"]["F1"], 4), "v1.5": round(v15["V3"]["control_atrasado_api_ninos"]["F1"], 4), "v2.0": round(v20["V3"]["control_atrasado_api_ninos"]["F1"], 4)},
        "registros_por_evaluacion": {"v1.0": v10["V1"]["registros_por_evaluacion"], "v1.5": v15["V1"]["registros_por_evaluacion"], "v2.0": v20["V1"]["registros_por_evaluacion"]},
        "dataset_real_muestra_500": {"pct_ninos_activos_con_agenda": real["V2_real_agenda_por_nino"]["pct_agenda"],
                                     "pct_controles_vencidos_visibles_en_agenda_del_personal": real["visibilidad_agenda_personal"]["pct_visibles"],
                                     "concordancia_con_oraculo_por_control_pct": real["oraculo"]["por_control"]["concordancia_pct"]},
        "pruebas_RF": {
            v: {rf: {"n_pruebas": p["n_pruebas"], "n_e2e": p["n_e2e"]} for rf, p in m21[v]["por_rf"].items()} for v in c.VERSIONES
        },
        "reporte_periodo_en_todas": all("GET /reportes/periodo" in r[v] for v in c.VERSIONES),
        "cola_sincronizacion_offline": "No existe: sw.js solo cachea la interfaz (GET fuera de /api/); README: 'El registro definitivo requiere conexión; la cola de sincronización offline es alcance del INC-3'",
    }
    assert "GET /ninos/{nino_id}/agenda" in r["v1.5"], "no se halló la ruta de agenda en v1.5"
    for ruta in ("GET /agenda", "POST /ninos/{nino_id}/controles/{codigo}/asistencia", "GET /ninos/{nino_id}/asistencias"):
        assert ruta in r["v2.0"], f"no se halló {ruta} en v2.0"
    assert not kw["v2.0"]["recordatorio"], "la v2.0 no debería tener recordatorios (INC-4)"
    assert not any("agenda" in x for x in r["v1.0"])

    puntuacion = {
        "B1": {
            "brecha": "Triple registro manual sin registro nominal único",
            "mecanismo_to_be": "Registro nominal único validado: un solo registro por evaluación que alimenta expediente, seguimiento y reporte (INC-1).",
            "v1.0": 1.0, "v1.5": 1.0, "v2.0": 1.0,
            "evidencia": "V1 medido por API: 1 escritura por evaluación (3 en el AS-IS) y el registro se refleja en expediente, seguimiento y reporte; RF-01..RF-05 con prueba automatizada y E2E (m21: 17/17 criterios en v1.0, 33/33 en v1.5, 48/48 en v2.0 sobre RF-01..RF-09); DNI único (409). En la v2.0 el registro desde la aplicación sigue exigiendo todos los campos (origen SISTEMA) y V1 sigue en 1.",
        },
        "B2": {
            "brecha": "Agenda calculada a mano, sin agenda normativa ni recordatorios",
            "mecanismo_to_be": "Agenda de controles según el esquema normativo + detección de vencidos + recordatorios a la familia y agenda del personal (INC-2/INC-4).",
            "v1.0": 0.0, "v1.5": 0.5, "v2.0": 0.5,
            "evidencia": "v1.0: no existe GET /api/ninos/{id}/agenda (404 en 140/140 activos, m32_v1.0_B150 V2) y control_atrasado es una heurística de 30 días desde la última evaluación, no normativa (F1 0,729 frente al oráculo normativo). v1.5: agenda normativa operativa y probada (RF-06) y detección de vencidos con F1 = 1,000 frente al oráculo (476/476 controles coinciden); parcial porque faltaban los recordatorios a la familia (INC-4), la agenda del personal (HIST-2.3) y el registro de asistencia (HIST-2.4). v2.0: se completan agenda del personal (RF-08: GET /api/agenda, controles por día con filtros y totales) y registro de asistencia (RF-09: asistió/no asistió con motivo y alerta elevada); verificado con B150 (100 % de los activos con agenda, F1 = 1,000, 476/476 controles) y con la muestra real de 500 niños de la DIRESA (100 % con agenda; 1 638/1 638 controles vencidos visibles en la agenda del personal y coincidentes con el oráculo). Sigue siendo parcial (0,5) porque el mecanismo TO-BE de B2 incluye los recordatorios a la familia (HIST-4.1, INC-4) y no hay ninguna ocurrencia de 'recordatorio' en el código: el personal ve y vigila los controles, pero el sistema todavía no avisa a la familia.",
            "sensibilidad": {"b2_limitado_a_lo_comprometido_en_INC2": 1.0,
                             "nota": "Si el mecanismo de B2 se limitara a lo que el plan compromete para INC-2 (agenda normativa, vencidos, agenda del personal y asistencia; sin recordatorios), B2 sería 1,0 en la v2.0: M3.1 = 41,7 % y 100 % de las brechas comprometidas. Se informa solo como sensibilidad: la puntuación oficial conserva la definición original del mecanismo."},
        },
        "B3": {
            "brecha": "Barreras ocultas hasta el abandono",
            "mecanismo_to_be": "Registro y análisis de barreras del hogar/servicio (INC-4).",
            "v1.0": 0.0, "v1.5": 0.0, "v2.0": 0.0,
            "evidencia": "Ni rutas ni campos ni pantallas de barreras en ninguna versión (0 ocurrencias de 'barrera' en app/). La v2.0 registra el motivo de una inasistencia (lista de cinco opciones y un detalle libre, RF-09), pero eso no es un registro ni un análisis de barreras del hogar o del servicio (HIST-4.3) ni genera alertas de barreras críticas (HIST-4.4).",
            "sensibilidad": {"b3_si_el_motivo_de_inasistencia_cuenta_como_registro_parcial": 0.5,
                             "nota": "Si se aceptara el motivo de inasistencia como registro parcial de barreras, B3 sería 0,5 en la v2.0 y M3.1 = 41,7 %. No se adopta: el motivo no se agrega ni se analiza."},
        },
        "B4": {
            "brecha": "Visita domiciliaria en papel, sin conexión",
            "mecanismo_to_be": "Registro de visita domiciliaria con captura sin conexión y sincronización (INC-3).",
            "v1.0": 0.0, "v1.5": 0.0, "v2.0": 0.0,
            "evidencia": "No existe ruta ni formulario de visita domiciliaria. El service worker solo guarda en caché la interfaz; el README declara que el registro definitivo requiere conexión.",
        },
        "B5": {
            "brecha": "Riesgo identificado cuando el abandono ya ocurrió",
            "mecanismo_to_be": "Detección anticipada del riesgo de abandono y priorización de la búsqueda activa (INC-5).",
            "v1.0": 0.0, "v1.5": 0.0, "v2.0": 0.0,
            "evidencia": "La lista de alertas de v1.5 y v2.0 prioriza controles ya vencidos (por días de atraso y gravedad, con un nivel más si hubo inasistencia registrada): es reactiva. No hay modelo ni regla que anticipe el riesgo antes del vencimiento; 0 ocurrencias de 'riesgo'/'abandono' en app/. El indicador 'próximo a vencer' (7 días) es aviso de calendario, no estimación de riesgo de abandono.",
        },
        "B6": {
            "brecha": "Conectividad intermitente: información no registrada ni reportada en el momento",
            "mecanismo_to_be": "Registro y reporte en el momento, con operación sin conexión y sincronización (INC-3 e INC-6; en INC-1 parcial con el reporte del periodo HU-05).",
            "v1.0": 0.5, "v1.5": 0.5, "v2.0": 0.5,
            "evidencia": "Parcial: el reporte consolidado del periodo (HU-05, JSON y CSV) se entrega en el momento y está probado (RF-05, E2E incluido), y la interfaz conserva el borrador del formulario en el dispositivo y abre desde caché. Falta lo esencial del mecanismo TO-BE: no hay operación sin conexión ni cola de sincronización (INC-3). Sin cambios en v1.5 ni en v2.0 (el Inc. 2 no toca B6; la asistencia se registra en línea). Sensibilidad: si se exigiera operación sin conexión para puntuar > 0, B6 sería 0 en ambas versiones.",
        },
    }
    res = {}
    for v in c.VERSIONES:
        suma = sum(b[v] for b in puntuacion.values())
        res[v] = {"suma_puntos": suma, "de_6": 6, "cobertura_pct": round(suma / 6 * 100, 1)}
    comprometidas = {"Inc.1": ["B1"], "avance_v1.5": ["B1", "B2"], "Inc.2": ["B1", "B2"]}
    comp = {}
    for inc, v in (("Inc.1", "v1.0"), ("avance_v1.5", "v1.5"), ("Inc.2", "v2.0")):
        bs = comprometidas[inc]
        s = sum(puntuacion[b][v] for b in bs)
        comp[inc] = {"version": v, "brechas_comprometidas": bs, "puntos": s, "cobertura_pct": round(s / len(bs) * 100, 1)}
    sens = {}
    for v in c.VERSIONES:
        s = sum(b[v] for k, b in puntuacion.items() if k != "B6")
        sens[v] = round(s / 6 * 100, 1)
    sens_b2b3 = {"v2.0_B2_sin_recordatorios": round((sum(b["v2.0"] for b in puntuacion.values()) + 0.5) / 6 * 100, 1),
                 "v2.0_B3_motivo_de_inasistencia_como_parcial": round((sum(b["v2.0"] for b in puntuacion.values()) + 0.5) / 6 * 100, 1),
                 "v2.0_ambas": round((sum(b["v2.0"] for b in puntuacion.values()) + 1.0) / 6 * 100, 1)}
    salida = {
        "regla": "1 = mecanismo TO-BE completo operativo y probado; 0,5 = parcial (operativo y probado solo en parte); 0 = no",
        "formula": "M3.1 = (suma de puntos B1..B6) / 6 x 100; complementaria = (puntos de las brechas comprometidas hasta el incremento) / (n.º de brechas comprometidas) x 100",
        "plan_brechas_por_incremento": "B1->INC-1; B2->INC-2; B3->INC-4; B4->INC-3; B5->INC-5; B6->INC-3 e INC-6 (en INC-1 parcial: reporte del periodo HU-05)",
        "puntuacion": puntuacion,
        "resultado_principal": res,
        "cobertura_brechas_comprometidas_en_el_plan": comp,
        "sensibilidad_B6_igual_a_0": sens,
        "sensibilidad_v2.0_B2_y_B3": sens_b2b3,
        "hechos_verificados": hechos,
    }
    (c.DATOS / "m31_brechas.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"principal": res, "comprometidas": comp, "sens_B6=0": sens, "sens_B2_B3": sens_b2b3}, ensure_ascii=False))


if __name__ == "__main__":
    main()
