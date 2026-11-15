#!/usr/bin/env python
"""Orquesta la prueba de carga comparativa (M3.2 / Q3.2) y la sonda de disponibilidad, con condiciones idénticas.

Para cada escenario y repetición:
  1. base SQLite NUEVA y vacía; 2. servidor uvicorn (un proceso, sin --reload) de la versión;
  3. carga del MISMO dataset sintético (dataset_B150.json) solo por la API pública (cargar_dataset_api.py);
  4. sonda de salud (GET /api/salud cada 1 s) en paralelo a Locust; 5. Locust headless 50 usuarios, 10/s, 60 s.

Escenarios:  v10_comun   -> v1.0 con locust_comun.py (mix de tareas del Inc. 1)
             v15_comun   -> v1.5 con locust_comun.py (el mismo mix y los mismos pesos)
             v15_agenda  -> v1.5 con locust_v15_agenda.py (mix común + agenda y alertas)
             v20_comun   -> v2.0 con locust_comun.py (el mismo mix y los mismos pesos; reloj fijado al 16/10/2026, la fecha del dataset B150)
             v20_ampliado-> v2.0 con el locustfile propio de la versión (tests/rendimiento/locustfile.py: mix común + agenda, alertas,
                            agenda del personal y asistencias)
Sesiones: las corridas r1 y r2 de v10, v15_* se midieron el 16/10/2026; las de v20_* y las r3 y r4 de v10_comun (repetición de v1.0 para
controlar el ruido de la máquina) el 17/10/2026, en la misma sesión.

Salidas: salidas/carga/<escenario>_r<k>_*.csv (Locust), <escenario>_r<k>_sonda.csv/.json, y datos/m32_carga.json y
datos/m32_disponibilidad.json (resumen por endpoint y agregado; ambas corridas y promedio).

Uso:  python ejecutar_carga.py [--repeticiones 2] [--escenarios v10_comun v15_comun v15_agenda] [--resumir-solo]
      python ejecutar_carga.py --corridas v10_comun:3 v20_comun:1 v20_ampliado:1 v10_comun:4 v20_comun:2 v20_ampliado:2   (lista explícita, en ese orden)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

import comun as c

AQUI = Path(__file__).resolve().parent
PY = os.getenv("PY", sys.executable)
CARGA = c.SALIDAS / "carga"
DATASET = c.DATOS / "dataset_B150.json"
TMP = Path(os.getenv("GQM_TMP", "/tmp/gqm"))
ESCENARIOS = {
    "v10_comun": {"version": "v1.0", "locustfile": "locust_comun.py", "puerto": 8301},
    "v15_comun": {"version": "v1.5", "locustfile": "locust_comun.py", "puerto": 8302},
    "v15_agenda": {"version": "v1.5", "locustfile": "locust_v15_agenda.py", "puerto": 8303},
    "v20_comun": {"version": "v2.0", "locustfile": "locust_comun.py", "puerto": 8304, "fecha_referencia": "2026-10-16"},
    "v20_ampliado": {"version": "v2.0", "locustfile": "<v2.0>/tests/rendimiento/locustfile.py", "puerto": 8305, "fecha_referencia": "2026-10-16"},
}
# Sesión de medición de cada corrida (para comparar versiones medidas en la misma sesión de la máquina)
SESION_16 = "2026-10-16"
SESION_17 = "2026-10-17"
def sesion_de(esc: str, rep: int) -> str:
    if esc in ("v10_comun",):
        return SESION_16 if rep <= 2 else SESION_17
    return SESION_17 if esc.startswith("v20") else SESION_16
# Promedio «de referencia» de cada escenario (se conserva el de las mediciones del 16/10 para v10 y v15)
SESION_REF = {"v10_comun": SESION_16, "v15_comun": SESION_16, "v15_agenda": SESION_16, "v20_comun": SESION_17, "v20_ampliado": SESION_17}
PERFIL = {"usuarios": 50, "subida_por_s": 10, "duracion_s": 60}


def locustfile_de(cfg: dict) -> str:
    lf = cfg["locustfile"]
    if lf.startswith("<v2.0>/"):
        return str(c.RAICES["v2.0"] / lf[len("<v2.0>/"):])
    return str(AQUI / lf)


def sh(args: list[str], extra_env: dict | None = None, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(args, text=True, capture_output=True, env={**os.environ, "GQM_TMP": str(TMP), **(extra_env or {})}, **kw)


def correr(esc: str, rep: int) -> None:
    cfg = ESCENARIOS[esc]
    puerto, ver = cfg["puerto"], cfg["version"]
    prefijo = f"{esc}_r{rep}"
    db = TMP / "db" / f"{prefijo}.sqlite"
    if db.exists():
        db.unlink()
    base = f"http://127.0.0.1:{puerto}"
    print(f"== {prefijo}: arrancando {ver} en :{puerto}", flush=True)
    extra = {"FECHA_REFERENCIA": cfg["fecha_referencia"]} if cfg.get("fecha_referencia") else None
    r = sh(["bash", str(AQUI / "servidor.sh"), "start", ver, str(puerto), str(db)], extra_env=extra)
    print(r.stdout.strip(), r.stderr.strip())
    if r.returncode:
        sys.exit("el servidor no arrancó")
    try:
        t0 = time.time()
        r = sh([PY, str(AQUI / "cargar_dataset_api.py"), "--base", base, "--dataset", str(DATASET)])
        print(r.stdout.strip(), f"({time.time() - t0:.0f} s)")
        if r.returncode:
            sys.exit("la carga del dataset tuvo errores:\n" + r.stdout)
        # calentamiento breve (no medido): una consulta de cada endpoint común
        sh([PY, "-c", f"import httpx;[httpx.get('{base}'+p,timeout=30) for p in ('/api/ninos','/api/salud')]"])
        sonda_csv = CARGA / f"{prefijo}_sonda.csv"
        sonda_json = CARGA / f"{prefijo}_sonda.json"
        # la sonda dura la prueba completa (+ margen para la subida y el cierre de Locust)
        sonda = subprocess.Popen(
            [PY, str(AQUI / "sonda_salud.py"), "--base", base, "--segundos", str(PERFIL["duracion_s"] + 4),
             "--csv", str(sonda_csv), "--json", str(sonda_json)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)
        loc = subprocess.run(
            [PY, "-m", "locust", "-f", locustfile_de(cfg), "--host", base, "--headless",
             "-u", str(PERFIL["usuarios"]), "-r", str(PERFIL["subida_por_s"]), "-t", f"{PERFIL['duracion_s']}s",
             "--csv", str(CARGA / prefijo), "--only-summary"],
            text=True, capture_output=True, cwd=AQUI)
        (CARGA / f"{prefijo}_locust_consola.txt").write_text(loc.stdout + "\n" + loc.stderr, encoding="utf-8")
        sonda.wait()
        print(f"   locust rc={loc.returncode}; sonda rc={sonda.returncode}", flush=True)
    finally:
        sh(["bash", str(AQUI / "servidor.sh"), "stop", str(puerto)])
        shutil.copy(TMP / f"uvicorn_{puerto}.log", CARGA / f"{prefijo}_uvicorn.log") if (TMP / f"uvicorn_{puerto}.log").exists() else None


def sesion_disponibilidad(minutos: float, versiones: tuple[str, ...] = ("v1.0", "v1.5", "v2.0")) -> None:
    """Sesión de observación sin carga: las versiones indicadas en paralelo (puertos distintos), sonda GET /api/salud cada 1 s."""
    puertos = {"v1.0": 8311, "v1.5": 8312, "v2.0": 8313}
    sondas = []
    for ver in versiones:
        puerto = puertos[ver]
        db = TMP / "db" / f"sesion_{ver}.sqlite"
        if db.exists():
            db.unlink()
        r = sh(["bash", str(AQUI / "servidor.sh"), "start", ver, str(puerto), str(db)])
        print(r.stdout.strip())
        r = sh([PY, str(AQUI / "cargar_dataset_api.py"), "--base", f"http://127.0.0.1:{puerto}", "--dataset", str(DATASET)])
        print(r.stdout.strip())
        pref = CARGA / f"sesion_{ver.replace('.', '')}_sonda"
        sondas.append((puerto, subprocess.Popen(
            [PY, str(AQUI / "sonda_salud.py"), "--base", f"http://127.0.0.1:{puerto}", "--segundos", str(minutos * 60),
             "--csv", f"{pref}.csv", "--json", f"{pref}.json"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
    for puerto, p in sondas:
        p.wait()
        sh(["bash", str(AQUI / "servidor.sh"), "stop", str(puerto)])
    print("sesión terminada")


def leer_stats(ruta: Path) -> dict:
    filas = {}
    with open(ruta, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            nombre = r["Name"] if r["Name"] != "Aggregated" else "AGREGADO"
            filas[nombre] = {
                "solicitudes": int(r["Request Count"]),
                "fallos": int(r["Failure Count"]),
                "pct_fallos": round(int(r["Failure Count"]) / int(r["Request Count"]) * 100, 2) if int(r["Request Count"]) else 0.0,
                "mediana_ms": float(r["Median Response Time"]),
                "promedio_ms": round(float(r["Average Response Time"]), 1),
                "p95_ms": float(r["95%"]),
                "p99_ms": float(r["99%"]),
                "max_ms": float(r["Max Response Time"]),
                "rps": round(float(r["Requests/s"]), 2),
            }
    return filas


def promedio(corridas: list[dict]) -> dict:
    """Promedio simple de cada indicador entre repeticiones (solicitudes y fallos: promedio también)."""
    out: dict = {}
    for ep in corridas[0]:
        out[ep] = {}
        for k in corridas[0][ep]:
            vals = [x[ep][k] for x in corridas if ep in x]
            out[ep][k] = round(statistics.mean(vals), 2)
    return out


def resumir(repeticiones: int = 2) -> None:
    carga, disp = {}, {}
    for esc, cfg in ESCENARIOS.items():
        archivos = sorted(CARGA.glob(f"{esc}_r*_stats.csv"), key=lambda p: int(p.name.split("_r")[1].split("_")[0]))
        if not archivos:
            continue
        corridas, sondas, reps = [], [], []
        for p in archivos:
            k = int(p.name.split("_r")[1].split("_")[0])
            reps.append(k)
            corridas.append(leer_stats(p))
            sj = CARGA / f"{esc}_r{k}_sonda.json"
            if sj.exists():
                sondas.append((k, json.loads(sj.read_text())))
        por_sesion: dict[str, list[tuple[int, dict]]] = {}
        for k, x in zip(reps, corridas):
            por_sesion.setdefault(sesion_de(esc, k), []).append((k, x))
        ref = SESION_REF[esc]
        carga[esc] = {
            "version": cfg["version"], "locustfile": cfg["locustfile"].replace("<v2.0>/", "pmv_fastapi/") if cfg["locustfile"].startswith("<v2.0>/") else cfg["locustfile"],
            "sesion_de_referencia": ref,
            "corridas": {f"r{k}": x for k, x in zip(reps, corridas)},
            "sesion_de_cada_corrida": {f"r{k}": sesion_de(esc, k) for k in reps},
            "promedio": promedio([x for _k, x in por_sesion[ref]]),
        }
        if len(por_sesion) > 1:
            carga[esc]["promedio_por_sesion"] = {ses: {"corridas": [f"r{k}" for k, _x in lst], "promedio": promedio([x for _k, x in lst])} for ses, lst in sorted(por_sesion.items())}
        if sondas:
            n = sum(s_["sondas"] for _k, s_ in sondas)
            ok = sum(s_["disponibles"] for _k, s_ in sondas)
            disp[esc] = {
                "version": cfg["version"], "modalidad": "sonda GET /api/salud cada 1 s durante la prueba de carga",
                "corridas": {f"r{k}": {kk: s_[kk] for kk in ("sondas", "disponibles", "disponibilidad_pct", "latencia_mediana_ms", "latencia_p95_ms", "latencia_max_ms")} for k, s_ in sondas},
                "sondas_total": n, "disponibles_total": ok,
                "disponibilidad_pct_global": round(ok / n * 100, 2) if n else None,
            }
    meta = {
        "perfil": {**PERFIL, "servidor": "uvicorn sin --reload, un proceso, 127.0.0.1", "bd": "SQLite nueva por corrida",
                   "dataset": "datos/dataset_B150.json (150 niños, 826 evaluaciones), cargado solo por API con cargar_dataset_api.py en todas las versiones",
                   "locust": "2.x headless; csv en salidas/carga/", "maquina": f"{os.cpu_count()} CPU compartidas entre servidor, Locust y sonda",
                   "v2.0": "servidor con FECHA_REFERENCIA=2026-10-16 (fecha para la que se generó el dataset B150), para que la agenda tenga la misma carga de trabajo que en las mediciones del 16/10/2026"},
        "sesiones": {SESION_16: "v10_comun r1-r2, v15_comun r1-r2, v15_agenda r1-r2", SESION_17: "v10_comun r3-r4 (repetición de v1.0), v20_comun r1-r2, v20_ampliado r1-r2"},
        "criterio": "p95/p99/mediana de Locust (percentiles agregados por ejecución); 'promedio' = promedio simple de las corridas de la sesión de referencia del escenario; 'promedio_por_sesion' cuando hay corridas de dos sesiones",
    }
    (c.DATOS / "m32_carga.json").write_text(json.dumps({"meta": meta, "escenarios": carga}, ensure_ascii=False, indent=1), encoding="utf-8")
    sesion = {}
    for ver in c.VERSIONES:
        sj = CARGA / f"sesion_{ver.replace('.', '')}_sonda.json"
        if sj.exists():
            x = json.loads(sj.read_text())
            sesion[ver] = {k: x[k] for k in ("sondas", "disponibles", "disponibilidad_pct", "latencia_mediana_ms", "latencia_p95_ms", "latencia_max_ms")}
            sesion[ver]["duracion_s_aprox"] = x["sondas"]
            sesion[ver]["modalidad"] = "sesión de observación sin carga, base B150, sonda GET /api/salud cada 1 s"
    glob = {}
    for ver in c.VERSIONES:
        ds = [d for d in disp.values() if d["version"] == ver]
        n = sum(d["sondas_total"] for d in ds)
        ok = sum(d["disponibles_total"] for d in ds)
        if ver in sesion:
            n += sesion[ver]["sondas"]
            ok += sesion[ver]["disponibles"]
        glob[ver] = {"sondas": n, "disponibles": ok, "disponibilidad_pct": round(ok / n * 100, 2) if n else None}
    (c.DATOS / "m32_disponibilidad.json").write_text(json.dumps({
        "meta": {"definicion": "disponibilidad = sondas con HTTP 200 en < 2 s / sondas x 100", "intervalo_s": 1,
                 "decision": "Se sondea durante TODAS las corridas de carga (condición más exigente, 50 usuarios) y además en una sesión de observación de 10 min por versión sin carga; se informa cada modalidad y el total combinado por versión."},
        "durante_carga": disp, "sesion_sin_carga": sesion, "total_por_version": glob}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("resumen escrito")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repeticiones", type=int, default=2)
    ap.add_argument("--escenarios", nargs="+", default=list(ESCENARIOS))
    ap.add_argument("--corridas", nargs="+", metavar="ESCENARIO:N", help="lista explícita de corridas, p. ej. v10_comun:3 v20_comun:1")
    ap.add_argument("--resumir-solo", action="store_true")
    ap.add_argument("--sesion-disponibilidad", type=float, default=None, metavar="MINUTOS", help="solo la sesión de observación sin carga")
    ap.add_argument("--versiones-sesion", nargs="+", default=["v1.0", "v1.5", "v2.0"], choices=["v1.0", "v1.5", "v2.0"])
    a = ap.parse_args()
    CARGA.mkdir(parents=True, exist_ok=True)
    (TMP / "db").mkdir(parents=True, exist_ok=True)
    if a.sesion_disponibilidad:
        sesion_disponibilidad(a.sesion_disponibilidad, tuple(a.versiones_sesion))
        resumir()
        return
    if not a.resumir_solo:
        if a.corridas:
            for item in a.corridas:
                esc, rep = item.split(":")
                correr(esc, int(rep))
        else:
            # alterna versiones entre repeticiones para repartir el ruido de la máquina: r1 de todos, luego r2 de todos
            for k in range(1, a.repeticiones + 1):
                for esc in a.escenarios:
                    correr(esc, k)
    resumir()


if __name__ == "__main__":
    main()
