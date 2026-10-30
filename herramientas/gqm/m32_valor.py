#!/usr/bin/env python
"""M3.2 Indicadores de valor del usuario V1, V2, V3 y V6, medidos por HTTP contra servidores reales.

  V1  Registros (escrituras manuales) por evaluación hasta quedar reflejada en expediente + seguimiento + reporte.
  V2  % de niños ACTIVOS con agenda de controles generada automáticamente (GET /api/ninos/{id}/agenda -> 200 y aplica).
  V3  Exactitud de la detección de controles vencidos frente al ORÁCULO independiente (oraculo_agenda.py):
      matriz de confusión, precisión, sensibilidad, exactitud y F1 de ``control_atrasado`` (GET /api/ninos) y, en
      v1.5, de las alertas (GET /api/alertas/controles-vencidos); comparación a nivel de control en v1.5.
  V6  Tiempo (ms) de obtener la lista de controles vencidos de toda la posta: mediana de 30 llamadas.

Uso:
  python m32_valor.py --seccion v2 v3 v6 --version v1.5 --base http://127.0.0.1:8202 \\
        --dataset datos/dataset_B150.json --etiqueta B150 [--db ruta.sqlite --seccion v1]
Salida: datos/m32_<version>_<etiqueta>.json
"""

from __future__ import annotations

import argparse
import json
import random
import sqlite3
import statistics
import time
from datetime import date
from pathlib import Path

import httpx

import comun as c
import oraculo_agenda as o


def hoy_servidor(cli: httpx.Client) -> date:
    """«Hoy» del servidor bajo prueba: fecha_hoy de /api/salud si existe (v2.0) o el reloj de Perú."""
    try:
        f = cli.get("/api/salud").json().get("fecha_hoy")
        return date.fromisoformat(f) if f else o.hoy_peru()
    except Exception:  # noqa: BLE001
        return o.hoy_peru()


def cuenta(db: str) -> tuple[int, int]:
    con = sqlite3.connect(db)
    try:
        return (con.execute("select count(*) from nino").fetchone()[0],
                con.execute("select count(*) from evaluacion_hemoglobina").fetchone()[0])
    finally:
        con.close()


def seccion_v1(cli: httpx.Client, db: str | None, version: str) -> dict:
    """Un único POST registra al niño con su primera evaluación y un único POST agrega cada control posterior."""
    hoy = hoy_servidor(cli)
    antes = cuenta(db) if db else None
    fn = o.sumar_meses(hoy, -14).isoformat()
    cuerpo = {"nino": {"dni": "69999991", "nombres": "Prueba", "apellidos": "Registro Unico", "sexo": "F",
                       "fecha_nacimiento": fn, "establecimiento": "P. S. Chongos Alto", "distrito": "Chongos Alto",
                       "comunidad": "Palmayoc", "altitud_m": 3720, "tutor_nombre": "Tutor Prueba"},
              "evaluacion_inicial": {"fecha": hoy.isoformat(), "hemoglobina_observada": 12.9, "peso_kg": 9.5, "talla_cm": 74}}
    escrituras = 0
    r = cli.post("/api/ninos", json=cuerpo)
    escrituras += 1
    nid = r.json()["id"]
    despues = cuenta(db) if db else None
    # ¿la evaluación aparece sin ninguna digitación adicional en cada vista?
    exp = cli.get(f"/api/ninos/{nid}").json()
    seg = [f for f in cli.get("/api/ninos").json() if f["id"] == nid]
    rep = cli.get("/api/reportes/periodo", params={"desde": hoy.isoformat(), "hasta": hoy.isoformat()}).json()
    vistas = {
        "expediente_con_1_evaluacion": len(exp.get("evaluaciones", [])) == 1,
        "seguimiento_lista_al_nino": len(seg) == 1,
        "reporte_cuenta_la_evaluacion": rep["evaluaciones_realizadas"] >= 1 and rep["ninos_registrados"] >= 1,
    }
    ag = cli.get(f"/api/ninos/{nid}/agenda")
    vistas["agenda_sin_digitacion_adicional"] = ag.status_code == 200
    # segundo control: 1 escritura
    fecha2 = hoy.isoformat()
    r2 = cli.post(f"/api/ninos/{nid}/evaluaciones", json={"fecha": fecha2, "hemoglobina_observada": 12.5, "peso_kg": 9.6, "talla_cm": 74.5})
    escrituras_control = 1
    exp2 = cli.get(f"/api/ninos/{nid}").json()
    return {
        "escrituras_para_registrar_nino_con_evaluacion": escrituras,
        "escrituras_para_agregar_un_control": escrituras_control,
        "registros_por_evaluacion": 1 if escrituras == 1 and escrituras_control == 1 else None,
        "filas_bd_antes": antes, "filas_bd_despues_registro": despues,
        "delta_nino_y_evaluacion": None if not (antes and despues) else [despues[0] - antes[0], despues[1] - antes[1]],
        "status_control": r2.status_code, "evaluaciones_tras_control": len(exp2.get("evaluaciones", [])),
        "vistas_que_reflejan_el_registro": vistas,
        "nota": "Se creó el niño 69999991 (sintético) en la base de prueba; no se reutiliza.",
    }


def seccion_v2(cli: httpx.Client) -> dict:
    filas = cli.get("/api/ninos", params={"estado": "ACTIVO"}).json()
    ok = con_controles = 0
    estados = {}
    for f in filas:
        r = cli.get(f"/api/ninos/{f['id']}/agenda")
        estados[r.status_code] = estados.get(r.status_code, 0) + 1
        if r.status_code == 200 and "controles" in r.json() and r.json().get("aplica"):
            ok += 1
            if r.json()["resumen"]["total"] >= 1:
                con_controles += 1
    n = len(filas)
    return {"activos": n, "con_agenda_generada": ok, "con_agenda_y_al_menos_un_control": con_controles,
            "pct_agenda": round(ok / n * 100, 1) if n else None,
            "pct_agenda_con_controles": round(con_controles / n * 100, 1) if n else None,
            "codigos_http_agenda": estados}


def metricas(tp: int, fp: int, fn: int, tn: int) -> dict:
    d = lambda a, b: (a / b) if b else None  # noqa: E731
    prec, rec = d(tp, tp + fp), d(tp, tp + fn)
    f1 = d(2 * prec * rec, prec + rec) if prec is not None and rec is not None and (prec + rec) else None
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn, "n": tp + fp + fn + tn, "precision": prec, "sensibilidad": rec,
            "exactitud": d(tp + tn, tp + fp + fn + tn), "F1": f1, "especificidad": d(tn, tn + fp)}


def bootstrap_f1(pares: list[tuple[bool, bool]], b: int = 2000, semilla: int = 42) -> list[float | None]:
    rng = random.Random(semilla)
    vals = []
    for _ in range(b):
        m = [pares[rng.randrange(len(pares))] for _ in pares]
        tp = sum(1 for y, p in m if y and p)
        fp = sum(1 for y, p in m if not y and p)
        fn = sum(1 for y, p in m if y and not p)
        den = 2 * tp + fp + fn
        vals.append(2 * tp / den if den else None)
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return [None, None]
    return [round(vals[int(0.025 * len(vals))], 3), round(vals[int(0.975 * len(vals)) - 1], 3)]


def seccion_v3(cli: httpx.Client, dataset: dict, version: str) -> dict:
    hoy = date.fromisoformat(dataset["hoy"])
    if hoy_servidor(cli) != hoy:
        raise SystemExit(f"El dataset se generó para {hoy} pero el servidor tiene {hoy_servidor(cli)}: regenere el dataset o fije FECHA_REFERENCIA={hoy}.")
    etiquetas = o.etiquetar(dataset, hoy)
    estado = {n["dni"]: n["estado"] for n in dataset["ninos"]}
    filas = cli.get("/api/ninos", params={"estado": ""}).json()  # todos los estados
    por_dni = {f["dni"]: f for f in filas}
    activos = [d for d, e in estado.items() if e == "ACTIVO"]
    faltan = [d for d in activos if d not in por_dni]
    pred = {d: bool(por_dni[d]["control_atrasado"]) for d in activos if d in por_dni}
    y = {d: etiquetas[d]["vencido"] for d in pred}

    def conf(p: dict) -> dict:
        tp = sum(1 for d in p if y[d] and p[d])
        fp = sum(1 for d in p if not y[d] and p[d])
        fn = sum(1 for d in p if y[d] and not p[d])
        tn = sum(1 for d in p if not y[d] and not p[d])
        return metricas(tp, fp, fn, tn)

    res = {
        "hoy": hoy.isoformat(), "n_dataset": len(dataset["ninos"]), "n_activos_evaluados": len(pred),
        "n_alta_excluidos": len(dataset["ninos"]) - len(activos), "no_encontrados": faltan,
        "prevalencia_oraculo": round(sum(y.values()) / len(y), 3),
        "control_atrasado_api_ninos": conf(pred),
        "bootstrap95_F1_control_atrasado": bootstrap_f1([(y[d], pred[d]) for d in pred]),
        "discrepancias_ninos": sorted(
            [{"dni": d, "oraculo": y[d], "api": pred[d], "detalle_oraculo": etiquetas[d]["controles"][:3],
              "escenario": next(n["escenario"] for n in dataset["ninos"] if n["dni"] == d)}
             for d in pred if y[d] != pred[d]], key=lambda x: x["dni"]),
    }
    # población ALTA: ¿el listado por defecto los muestra como atrasados? (informativo)
    altas = [d for d, e in estado.items() if e != "ACTIVO" and d in por_dni]
    res["alta_marcados_atrasado_api"] = sum(1 for d in altas if por_dni[d]["control_atrasado"])
    res["alta_total"] = len(altas)
    if version in ("v1.5", "v2.0"):
        al = cli.get("/api/alertas/controles-vencidos").json()
        con_alerta = {a["nino"]["dni"] for a in al}
        pred2 = {d: (d in con_alerta) for d in pred}
        tp = sum(1 for d in pred2 if y[d] and pred2[d]); fp = sum(1 for d in pred2 if not y[d] and pred2[d])
        fn = sum(1 for d in pred2 if y[d] and not pred2[d]); tn = sum(1 for d in pred2 if not y[d] and not pred2[d])
        res["alertas_controles_vencidos"] = metricas(tp, fp, fn, tn)
        # nivel de control: (dni, tipo, fecha_programada)
        del_api = {(a["nino"]["dni"], a["control"]["tipo"], a["control"]["fecha_programada"]) for a in al}
        del_orc = {(d, v["tipo"], v["programada"]) for d in pred for v in etiquetas[d]["controles"]}
        res["nivel_control"] = {
            "controles_oraculo": len(del_orc), "controles_api": len(del_api),
            "coinciden": len(del_api & del_orc), "solo_oraculo": sorted(map(list, del_orc - del_api))[:20],
            "solo_api": sorted(map(list, del_api - del_orc))[:20],
        }
        # resumen vs conteo
        r = cli.get("/api/alertas/resumen").json()
        res["resumen_api"] = r
        res["resumen_coherente_con_alertas"] = r["total_vencidos"] == len(al) and r["ninos_con_vencidos"] == len(con_alerta)
        # prioridad: coherencia del filtro por comunidad (insensible a mayúsculas) no se evalúa aquí
    return res


def seccion_v6(cli: httpx.Client, version: str, n_ninos: int, repeticiones: int = 30, calentamiento: int = 3) -> dict:
    def tiempos(url: str) -> dict:
        for _ in range(calentamiento):
            cli.get(url)
        t = []
        for _ in range(repeticiones):
            t0 = time.perf_counter()
            r = cli.get(url)
            r.raise_for_status()
            t.append((time.perf_counter() - t0) * 1000)
        t.sort()
        return {"n": repeticiones, "mediana_ms": round(statistics.median(t), 1), "min_ms": round(t[0], 1),
                "p95_ms": round(t[int(0.95 * len(t)) - 1], 1), "max_ms": round(t[-1], 1),
                "media_ms": round(statistics.mean(t), 1)}
    res = {"n_ninos": n_ninos, "calentamiento_descartado": calentamiento,
           "GET /api/ninos": tiempos("/api/ninos")}
    if version in ("v1.5", "v2.0"):
        res["GET /api/alertas/controles-vencidos"] = tiempos("/api/alertas/controles-vencidos")
        res["GET /api/alertas/resumen"] = tiempos("/api/alertas/resumen")
    if version == "v2.0":
        res["GET /api/agenda (semana de la fecha de referencia)"] = tiempos("/api/agenda")
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", required=True, choices=["v1.0", "v1.5", "v2.0"])
    ap.add_argument("--base", required=True)
    ap.add_argument("--seccion", nargs="+", default=["v2", "v3", "v6"], choices=["v1", "v2", "v3", "v6"])
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--db", default=None, help="ruta de la base SQLite del servidor (solo para contar filas en V1)")
    ap.add_argument("--etiqueta", default="B150")
    a = ap.parse_args()
    out_path = c.DATOS / f"m32_{a.version}_{a.etiqueta}.json"
    out = json.loads(out_path.read_text()) if out_path.exists() else {}
    ds = json.loads(Path(a.dataset).read_text(encoding="utf-8")) if a.dataset else None
    with httpx.Client(base_url=a.base, timeout=60) as cli:
        if "v1" in a.seccion:
            out["V1"] = seccion_v1(cli, a.db, a.version)
        if "v2" in a.seccion:
            out["V2"] = seccion_v2(cli)
        if "v3" in a.seccion:
            ds2 = o.cargar_dataset(a.dataset)
            ds2["hoy"] = ds["hoy"]
            out["V3"] = seccion_v3(cli, ds2, a.version)
        if "v6" in a.seccion:
            out["V6"] = seccion_v6(cli, a.version, len(ds["ninos"]) if ds else -1)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    corridas = {k.upper(): out[k.upper()] for k in a.seccion}
    if "V3" in corridas:  # no imprimir el detalle de discrepancias (queda en el JSON)
        corridas["V3"] = {k: v for k, v in corridas["V3"].items() if k != "discrepancias_ninos"}
    print(json.dumps(corridas, ensure_ascii=False, indent=1, default=str))
    print("->", out_path)


if __name__ == "__main__":
    main()
