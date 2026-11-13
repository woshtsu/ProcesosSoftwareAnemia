#!/usr/bin/env python
"""M3.2 sobre la base de demostración con la muestra de 500 niños del dataset real de la DIRESA Junín (v2.0.0-inc2).

El servidor debe estar iniciado con ``FECHA_REFERENCIA=2024-06-30`` (corte del dataset) sobre la base creada con
``python -m scripts.importar_dataset_diresa --muestra 500 --semilla 2026 --reiniciar [--reporte ruta.json]`` (ver README de la app).
Solo usa la API pública. Mide, para los niños de origen DATASET_DIRESA_JUNIN y estado ACTIVO:

  V2r  % de niños activos con agenda normativa generada (GET /api/ninos/{id}/agenda = 200, aplica y >= 1 control).
  Vencidos detectados: total, niños afectados y prioridad (GET /api/alertas/resumen y /controles-vencidos).
  Concordancia con el ORÁCULO independiente (oraculo_agenda.py, que no importa la aplicación): a partir de los datos que el sistema
  guardó de cada niño (nacimiento, altitud, estado, fecha y Hb observada de cada evaluación) el oráculo recalcula los controles vencidos
  por su cuenta y se compara por niño y por control (tipo, fecha programada). Verifica el cálculo de la agenda sobre datos reales; NO
  verifica la importación del CSV (eso lo cubren las pruebas CP-152 a CP-160 y el reporte de importación).
  Visibilidad para el personal: cada control vencido del oráculo debe figurar como VENCIDO en la agenda del personal (GET /api/agenda),
  recorriendo el calendario en ventanas de 31 días; y la agenda del personal debe coincidir con la agenda de cada niño (coherencia RF-06/RF-08).
  Tiempos de respuesta con 500 niños.

Uso:  python m32_dataset_real.py --base http://127.0.0.1:8404 [--reporte-importacion ruta.json] [--json ruta]
Salida: datos/m32_dataset_real.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import httpx

import comun as c
import oraculo_agenda as o


def tiempos(cli: httpx.Client, url: str, n: int = 20, params: dict | None = None) -> dict:
    for _ in range(2):
        cli.get(url, params=params)
    t = []
    for _ in range(n):
        t0 = time.perf_counter()
        r = cli.get(url, params=params)
        r.raise_for_status()
        t.append((time.perf_counter() - t0) * 1000)
    t.sort()
    return {"n": n, "mediana_ms": round(statistics.median(t), 1), "p95_ms": round(t[int(0.95 * len(t)) - 1], 1),
            "max_ms": round(t[-1], 1)}


def metricas(tp: int, fp: int, fn: int, tn: int) -> dict:
    d = lambda a, b: round(a / b, 4) if b else None  # noqa: E731
    prec, rec = d(tp, tp + fp), d(tp, tp + fn)
    f1 = round(2 * tp / (2 * tp + fp + fn), 4) if (2 * tp + fp + fn) else None
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn, "n": tp + fp + fn + tn, "precision": prec, "sensibilidad": rec,
            "exactitud": d(tp + tn, tp + fp + fn + tn), "F1": f1}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--reporte-importacion", default=None)
    ap.add_argument("--json", default=str(c.DATOS / "m32_dataset_real.json"))
    a = ap.parse_args()
    with httpx.Client(base_url=a.base, timeout=120) as cli:
        salud = cli.get("/api/salud").json()
        hoy = date.fromisoformat(salud["fecha_hoy"])
        if salud.get("fecha_referencia") is None:
            raise SystemExit("El servidor no tiene FECHA_REFERENCIA: la medición debe hacerse con el corte del dataset (2024-06-30).")
        filas = cli.get("/api/ninos", params={"estado": ""}).json()
        origen = Counter((f["origen"], f["estado"]) for f in filas)
        dataset = [f for f in filas if f["origen"] == "DATASET_DIRESA_JUNIN"]
        activos = [f for f in dataset if f["estado"] == "ACTIVO"]

        # ---------------- V2r: agenda por niño + datos para el oráculo ----------------
        con_agenda = con_controles = 0
        codigos_http = Counter()
        estados = Counter()
        por_nino_agenda: dict[str, list[dict]] = {}
        nino_orac: dict[str, dict] = {}
        for f in activos:
            r = cli.get(f"/api/ninos/{f['id']}/agenda")
            codigos_http[r.status_code] += 1
            ag = r.json()
            if r.status_code == 200 and ag.get("aplica"):
                con_agenda += 1
                if ag["resumen"]["total"] >= 1:
                    con_controles += 1
            por_nino_agenda[f["id"]] = ag.get("controles", [])
            for ctl in ag.get("controles", []):
                estados[ctl["estado"] + ("+PROXIMO" if ctl.get("proximo") else "")] += 1
            exp = cli.get(f"/api/ninos/{f['id']}").json()
            nino_orac[f["id"]] = {
                "codigo": exp["codigo_origen"], "nacimiento": date.fromisoformat(exp["fecha_nacimiento"]), "estado": exp["estado"],
                "altitud": exp["altitud_m"],
                "evaluaciones": [{"fecha": date.fromisoformat(e["fecha"]), "hb_obs": e["hemoglobina_observada"]} for e in exp["evaluaciones"]],
            }
        n_act = len(activos)

        # ---------------- Alertas del sistema ----------------
        resumen = cli.get("/api/alertas/resumen").json()
        alertas = [x for x in cli.get("/api/alertas/controles-vencidos").json() if (x["nino"]["codigo_origen"] or "").startswith("DJ-")]
        api_ctl = {(x["nino"]["codigo_origen"], x["control"]["tipo"], x["control"]["fecha_programada"]) for x in alertas}
        api_ninos = {x["nino"]["codigo_origen"] for x in alertas}
        por_prioridad = Counter(x["prioridad"] for x in alertas)

        # ---------------- Oráculo ----------------
        orc_ctl, orc_ninos, orc_cod = set(), set(), set()
        for nid, n in nino_orac.items():
            for v in o.controles_vencidos(n, hoy):
                orc_ctl.add((n["codigo"], v["tipo"], v["programada"]))
                orc_cod.add((n["codigo"], v["codigo"], v["programada"]))
                orc_ninos.add(n["codigo"])
        todos = {n["codigo"] for n in nino_orac.values()}
        tp = len(orc_ninos & api_ninos)
        fp = len(api_ninos - orc_ninos)
        fn = len(orc_ninos - api_ninos)
        tn = len(todos) - tp - fp - fn
        nivel_nino = metricas(tp, fp, fn, tn)
        nivel_control = {
            "controles_oraculo": len(orc_ctl), "controles_sistema": len(api_ctl), "coinciden": len(orc_ctl & api_ctl),
            "solo_oraculo": sorted(map(list, orc_ctl - api_ctl))[:20], "solo_sistema": sorted(map(list, api_ctl - orc_ctl))[:20],
            "concordancia_pct": round(len(orc_ctl & api_ctl) / len(orc_ctl | api_ctl) * 100, 2) if (orc_ctl | api_ctl) else None,
        }

        # ---------------- Visibilidad en la agenda del personal (RF-08) ----------------
        ini = date.fromisoformat(min(p for (_c, _t, p) in (orc_ctl | api_ctl)))
        fin = hoy + timedelta(days=0)
        vistos_agenda, vistos_cod, items_total, ventanas = set(), set(), 0, 0
        estados_agenda = Counter()
        d0 = ini
        while d0 <= fin:
            d1 = min(d0 + timedelta(days=30), fin)
            ag = cli.get("/api/agenda", params={"desde": d0.isoformat(), "hasta": d1.isoformat()}).json()
            ventanas += 1
            for dia in ag["dias"]:
                for it in dia["items"]:
                    if not (it["nino"]["codigo_origen"] or "").startswith("DJ-"):
                        continue
                    items_total += 1
                    estados_agenda[it["control"]["estado"]] += 1
                    if it["control"]["estado"] == "VENCIDO":
                        vistos_agenda.add((it["nino"]["codigo_origen"], it["control"]["tipo"], it["control"]["fecha_programada"]))
                        vistos_cod.add((it["nino"]["codigo_origen"], it["control"]["codigo"], it["control"]["fecha_programada"]))
            d0 = d1 + timedelta(days=1)
        visibles = len(orc_ctl & vistos_agenda)
        # coherencia: controles de las agendas por niño (sin cerrados por recuperación) vs. ítems de la agenda del personal en el calendario recorrido
        n_agendas = sum(1 for lst in por_nino_agenda.values() for k in lst if k["estado"] != "CERRADO_RECUPERADO" and ini <= date.fromisoformat(k["fecha_programada"]) <= fin)

        # ---------------- Contraste con la línea base AS-IS (no es una prueba: las ventanas y la muestra difieren) ----------------
        tipos_venc = Counter(k[1] for k in orc_ctl)
        contraste = {}
        for cod in ("C1M", "C3M", "C6M"):
            cumpl = venc = pend = 0
            for lst in por_nino_agenda.values():
                for k in lst:
                    if k["codigo"] == cod and k["estado"] == "CUMPLIDO":
                        cumpl += 1
                    elif k["codigo"] == cod and k["estado"] == "VENCIDO":
                        venc += 1
                    elif k["codigo"] == cod and k["estado"] == "PENDIENTE":
                        pend += 1
            debidos = cumpl + venc
            contraste[cod] = {"cumplidos": cumpl, "vencidos": venc, "pendientes_aun_en_plazo": pend,
                              "pct_cumplidos_entre_los_ya_exigibles": round(cumpl / debidos * 100, 1) if debidos else None}
        edad_venc = sum(1 for k in orc_ctl if k[1] == "TAMIZAJE_EDAD")
        # Programados y vencidos visibles por control de tratamiento (capacidad del sistema frente a la línea base AS-IS)
        capacidad = {}
        for cod in ("C1M", "C3M", "C6M"):
            con_prog = sum(1 for lst in por_nino_agenda.values() if any(k["codigo"] == cod for k in lst))
            v_orc = {x for x in orc_cod if x[1] == cod}
            capacidad[cod] = {"ninos_con_el_control_programado": con_prog, "pct_ninos_con_el_control_programado": round(con_prog / n_act * 100, 1),
                              "vencidos_oraculo": len(v_orc), "vencidos_visibles_en_agenda_del_personal": len(v_orc & vistos_cod),
                              "pct_vencidos_visibles": round(len(v_orc & vistos_cod) / len(v_orc) * 100, 1) if v_orc else None}

        t = {
            "GET /api/agenda (semana de la fecha de referencia)": tiempos(cli, "/api/agenda"),
            "GET /api/agenda (31 días hasta el corte)": tiempos(cli, "/api/agenda", params={"desde": (hoy - timedelta(days=30)).isoformat(), "hasta": hoy.isoformat()}),
            "GET /api/alertas/controles-vencidos": tiempos(cli, "/api/alertas/controles-vencidos"),
            "GET /api/alertas/resumen": tiempos(cli, "/api/alertas/resumen"),
            "GET /api/ninos": tiempos(cli, "/api/ninos"),
        }

    reporte = json.loads(Path(a.reporte_importacion).read_text(encoding="utf-8")) if a.reporte_importacion else {}
    out = {
        "fecha_referencia": hoy.isoformat(),
        "base": "muestra estratificada de 500 niños (Provincia x severidad HIS, semilla 2026) del dataset DIRESA Junín, importada con scripts.importar_dataset_diresa",
        "poblacion": {"registros_por_origen_y_estado": {f"{k[0]}|{k[1]}": v for k, v in origen.items()},
                      "dataset_total": len(dataset), "dataset_activos": n_act},
        "importacion": {k: reporte.get(k) for k in ("filas_leidas", "ninos_importados", "evaluaciones_importadas", "descartes_por_motivo", "concordancia_his_vs_sistema")} if reporte else "no se indicó el reporte de importación",
        "V2_real_agenda_por_nino": {
            "activos": n_act, "con_agenda_generada": con_agenda, "con_agenda_y_al_menos_un_control": con_controles,
            "pct_agenda": round(con_agenda / n_act * 100, 1), "pct_agenda_con_controles": round(con_controles / n_act * 100, 1),
            "codigos_http": dict(codigos_http), "controles_por_estado_en_las_agendas": dict(estados),
            "formula": "% de niños ACTIVOS del dataset con GET /api/ninos/{id}/agenda = 200, aplica=true y >= 1 control; AS-IS = 0 (no existe agenda)"},
        "vencidos_detectados": {
            "controles_vencidos": len(alertas), "ninos_con_vencidos": len(api_ninos), "pct_ninos_con_vencidos": round(len(api_ninos) / n_act * 100, 1),
            "por_prioridad": dict(por_prioridad), "resumen_api_toda_la_base": resumen,
            "nota": "El resumen de la API incluye también los registros de prueba del sistema si se crearon; las cifras de este bloque son solo del dataset."},
        "oraculo": {
            "por_nino": nivel_nino, "por_control": nivel_control,
            "entrada_del_oraculo": "datos guardados por el sistema (API de expediente): nacimiento, altitud, estado, fecha y Hb observada de cada evaluación; el oráculo no importa la aplicación",
            "alcance": "verifica el cálculo de la agenda sobre datos reales, no la importación del CSV"},
        "visibilidad_agenda_personal": {
            "formula": "controles vencidos del oráculo que figuran como VENCIDO en GET /api/agenda ÷ controles vencidos del oráculo",
            "controles_vencidos_oraculo": len(orc_ctl), "visibles_en_agenda_del_personal": visibles,
            "pct_visibles": round(visibles / len(orc_ctl) * 100, 2) if orc_ctl else None,
            "visibles_en_lista_de_alertas": len(orc_ctl & api_ctl),
            "pct_visibles_en_alertas": round(len(orc_ctl & api_ctl) / len(orc_ctl) * 100, 2) if orc_ctl else None,
            "ventanas_de_31_dias_consultadas": ventanas, "calendario_recorrido": [ini.isoformat(), fin.isoformat()],
            "items_en_agenda_del_personal": items_total, "estados_en_agenda_del_personal": dict(estados_agenda),
            "controles_en_agendas_por_nino_sin_cerrados_en_el_calendario": n_agendas,
            "coherencia_rf06_rf08": items_total == n_agendas},
        "vencidos_por_tipo": {"CONTROL_TRATAMIENTO": len(orc_ctl) - edad_venc, "TAMIZAJE_EDAD": edad_venc, "detalle_por_tipo_oraculo": dict(tipos_venc),
                              "advertencia": "El extracto del HIS solo trae el diagnóstico y los dosajes al mes, 3 y 6 meses: un dosaje por edad (6, 9, 12 meses...) sin registro en el extracto se muestra como vencido aunque haya podido hacerse. «Vencido» significa «sin registro en la base importada», no «no realizado»."},
        "capacidad_del_sistema_controles_de_tratamiento": {
            "por_control": capacidad,
            "nota": "Un niño no tiene el control programado si su diagnóstico no es de anemia en la fecha de la evaluación (p. ej. el sistema clasifica «sin anemia» el 18,7 % de los diagnósticos HIS, por la altitud de la capital de provincia) o si el control caería a los 60 meses o más."},
        "contraste_controles_de_tratamiento_con_el_as_is": {
            "por_control": contraste,
            "referencia_as_is_con_seguimiento_posible_pct": {"C1M": 70.2, "C3M": 63.8, "C6M": 66.1},
            "fuente_referencia": "datos/asis_dataset_diresa.json (dataset completo, 12 486 filas); la muestra de 500 es estratificada y la ventana del sistema (−15/+30 días del mes calendario) difiere de la del extracto: comparación orientativa, no una prueba",
        },
        "tiempos_respuesta_500_ninos_ms": t,
    }
    Path(a.json).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("V2_real_agenda_por_nino", "vencidos_detectados", "visibilidad_agenda_personal")}, ensure_ascii=False, indent=1))
    print(json.dumps(out["oraculo"], ensure_ascii=False, indent=1))
    print("->", a.json)


if __name__ == "__main__":
    main()
