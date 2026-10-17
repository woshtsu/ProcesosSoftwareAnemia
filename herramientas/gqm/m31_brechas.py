#!/usr/bin/env python
"""M3.1 Cobertura de brechas AS-IS resueltas (B1..B6) por versión, con evidencia comprobada sobre el software real.

Regla de puntuación (decidida por el orquestador): una brecha cuenta 1 si su mecanismo TO-BE completo está operativo y
probado; 0,5 si está parcial (operativo y probado solo en parte); 0 si no.

El script no "calcula" la puntuación (es un juicio de ingeniería), pero SÍ verifica con evidencia ejecutable los hechos
en los que se apoya cada puntuación: rutas HTTP existentes en el código de cada versión, ausencia de palabras clave de
funcionalidad (recordatorio, barrera, riesgo, abandono) en app/, resultados de V2/V3 medidos por API (datos/m32_*_B150.json)
y pruebas que cubren cada requisito (datos/m21_cobertura_rf.json).

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
    r = {v: rutas(v) for v in ("v1.0", "v1.5")}
    kw = {v: {p: ocurrencias(v, p) for p in PALABRAS} for v in ("v1.0", "v1.5")}
    hechos = {
        "rutas_http_relativas_al_prefijo_api": r,
        "palabras_clave_en_app": {v: {p: len(x) for p, x in d.items()} for v, d in kw.items()},
        "palabras_clave_detalle_no_vacias": {v: {p: x for p, x in d.items() if x} for v, d in kw.items()},
        "agenda_v1.0_http": v10["V2"]["codigos_http_agenda"],
        "agenda_v1.5_http": v15["V2"]["codigos_http_agenda"],
        "pct_ninos_activos_con_agenda": {"v1.0": v10["V2"]["pct_agenda"], "v1.5": v15["V2"]["pct_agenda"]},
        "F1_vencidos_vs_oraculo": {"v1.0": round(v10["V3"]["control_atrasado_api_ninos"]["F1"], 4), "v1.5": round(v15["V3"]["control_atrasado_api_ninos"]["F1"], 4)},
        "registros_por_evaluacion": {"v1.0": v10["V1"]["registros_por_evaluacion"], "v1.5": v15["V1"]["registros_por_evaluacion"]},
        "pruebas_RF": {
            v: {rf: {"n_pruebas": p["n_pruebas"], "n_e2e": p["n_e2e"]} for rf, p in m21[v]["por_rf"].items()} for v in ("v1.0", "v1.5")
        },
        "reporte_periodo_en_ambas": "GET /reportes/periodo" in r["v1.0"] and "GET /reportes/periodo" in r["v1.5"],
        "cola_sincronizacion_offline": "No existe: sw.js solo cachea la interfaz (GET fuera de /api/); README: 'El registro definitivo requiere conexión; la cola de sincronización offline es alcance del INC-3'",
    }
    assert "GET /ninos/{nino_id}/agenda" in r["v1.5"], "no se halló la ruta de agenda en v1.5"
    assert not any("agenda" in x for x in r["v1.0"])

    puntuacion = {
        "B1": {
            "brecha": "Triple registro manual sin registro nominal único",
            "mecanismo_to_be": "Registro nominal único validado: un solo registro por evaluación que alimenta expediente, seguimiento y reporte (INC-1).",
            "v1.0": 1.0, "v1.5": 1.0,
            "evidencia": "V1 medido por API: 1 escritura por evaluación (3 en el AS-IS) y el registro se refleja en expediente, seguimiento y reporte; RF-01..RF-05 con prueba automatizada y E2E (m21: 17/17 criterios en v1.0, 33/33 en v1.5); DNI único (409).",
        },
        "B2": {
            "brecha": "Agenda calculada a mano, sin agenda normativa ni recordatorios",
            "mecanismo_to_be": "Agenda de controles según el esquema normativo + detección de vencidos + recordatorios a la familia y agenda del personal (INC-2/INC-4).",
            "v1.0": 0.0, "v1.5": 0.5,
            "evidencia": "v1.0: no existe GET /api/ninos/{id}/agenda (404 en 140/140 activos, m32_v1.0_B150 V2) y control_atrasado es una heurística de 30 días desde la última evaluación, no normativa (F1 0,729 frente al oráculo normativo). v1.5: agenda normativa operativa y probada (RF-06, 23 pruebas, 2 E2E) y detección de vencidos con F1 = 1,000 frente al oráculo (476/476 controles coinciden). Parcial porque faltan los recordatorios a la familia (INC-4), la agenda del personal (HIST-2.3) y el registro de asistencia (HIST-2.4): no hay ninguna ocurrencia de 'recordatorio' en el código.",
        },
        "B3": {
            "brecha": "Barreras ocultas hasta el abandono",
            "mecanismo_to_be": "Registro y análisis de barreras del hogar/servicio (INC-4).",
            "v1.0": 0.0, "v1.5": 0.0,
            "evidencia": "Ni rutas ni campos ni pantallas de barreras en ninguna versión (0 ocurrencias de 'barrera' en app/).",
        },
        "B4": {
            "brecha": "Visita domiciliaria en papel, sin conexión",
            "mecanismo_to_be": "Registro de visita domiciliaria con captura sin conexión y sincronización (INC-3).",
            "v1.0": 0.0, "v1.5": 0.0,
            "evidencia": "No existe ruta ni formulario de visita domiciliaria. El service worker solo guarda en caché la interfaz; el README declara que el registro definitivo requiere conexión.",
        },
        "B5": {
            "brecha": "Riesgo identificado cuando el abandono ya ocurrió",
            "mecanismo_to_be": "Detección anticipada del riesgo de abandono y priorización de la búsqueda activa (INC-5).",
            "v1.0": 0.0, "v1.5": 0.0,
            "evidencia": "La lista de alertas de v1.5 prioriza controles ya vencidos (por días de atraso y gravedad): es reactiva. No hay modelo ni regla que anticipe el riesgo antes del vencimiento; 0 ocurrencias de 'riesgo'/'abandono' en app/. El indicador 'próximo a vencer' (7 días) es aviso de calendario, no estimación de riesgo de abandono.",
        },
        "B6": {
            "brecha": "Conectividad intermitente: información no registrada ni reportada en el momento",
            "mecanismo_to_be": "Registro y reporte en el momento, con operación sin conexión y sincronización (INC-3 e INC-6; en INC-1 parcial con el reporte del periodo HU-05).",
            "v1.0": 0.5, "v1.5": 0.5,
            "evidencia": "Parcial: el reporte consolidado del periodo (HU-05, JSON y CSV) se entrega en el momento y está probado (RF-05, E2E incluido), y la interfaz conserva el borrador del formulario en el dispositivo y abre desde caché. Falta lo esencial del mecanismo TO-BE: no hay operación sin conexión ni cola de sincronización (INC-3). Sin cambios en v1.5 (el avance del Inc. 2 no toca B6). Sensibilidad: si se exigiera operación sin conexión para puntuar > 0, B6 sería 0 en ambas versiones.",
        },
    }
    res = {}
    for v in ("v1.0", "v1.5"):
        suma = sum(b[v] for b in puntuacion.values())
        res[v] = {"suma_puntos": suma, "de_6": 6, "cobertura_pct": round(suma / 6 * 100, 1)}
    comprometidas = {"Inc.1": ["B1"], "Inc.2": ["B1", "B2"]}
    comp = {}
    for inc, v in (("Inc.1", "v1.0"), ("Inc.2", "v1.5")):
        bs = comprometidas[inc]
        s = sum(puntuacion[b][v] for b in bs)
        comp[inc] = {"version": v, "brechas_comprometidas": bs, "puntos": s, "cobertura_pct": round(s / len(bs) * 100, 1)}
    sens = {}
    for v in ("v1.0", "v1.5"):
        s = sum(b[v] for k, b in puntuacion.items() if k != "B6")
        sens[v] = round(s / 6 * 100, 1)
    salida = {
        "regla": "1 = mecanismo TO-BE completo operativo y probado; 0,5 = parcial (operativo y probado solo en parte); 0 = no",
        "formula": "M3.1 = (suma de puntos B1..B6) / 6 x 100; complementaria = (puntos de las brechas comprometidas hasta el incremento) / (n.º de brechas comprometidas) x 100",
        "plan_brechas_por_incremento": "B1->INC-1; B2->INC-2; B3->INC-4; B4->INC-3; B5->INC-5; B6->INC-3 e INC-6 (en INC-1 parcial: reporte del periodo HU-05)",
        "puntuacion": puntuacion,
        "resultado_principal": res,
        "cobertura_brechas_comprometidas_en_el_plan": comp,
        "sensibilidad_B6_igual_a_0": sens,
        "hechos_verificados": hechos,
    }
    (c.DATOS / "m31_brechas.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"principal": res, "comprometidas": comp, "sens_B6=0": sens}, ensure_ascii=False))


if __name__ == "__main__":
    main()
