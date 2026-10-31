"""Factores P y R: carga con Locust, disponibilidad bajo carga, memoria del proceso y tiempo de reinicio (MTTR local).

Uso (raiz del repositorio): PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python entregables/semana-10/metricas/rendimiento.py
Servidor: uvicorn 127.0.0.1:8765, AUTH_MODE=demo, SQLite temporal con datos sinteticos (1 proceso, 1 worker).
Corridas Locust (headless, 60 s): A) locustfile del repositorio (Inc. 1-2) con 20 usuarios; B) Inc. 3-4 con 20 usuarios;
C) locustfile del repositorio con 100 usuarios (referencia de saturacion). Mientras corre cada una se sondea /api/salud
cada 0.5 s (disponibilidad) y se muestrea la memoria residente (RSS) del servidor.
Al final: se mata el proceso (kill -9) y se mide el tiempo hasta que /api/salud vuelve a responder 200 con los datos intactos.
"""

import csv
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capturar_software as cs  # noqa: E402

SAL = cs.BASE / "metricas" / "salidas"
LF_REPO = cs.PMV / "tests" / "rendimiento" / "locustfile.py"
LF_INC34 = cs.BASE / "metricas" / "locustfile_inc3_inc4.py"


def rss_mb(pid):
    for l in Path(f"/proc/{pid}/status").read_text().splitlines():
        if l.startswith("VmRSS"):
            return int(l.split()[1]) / 1024
    return 0.0


def corrida(nombre, locustfile, usuarios, segundos, proc):
    prefijo = SAL / f"P_{nombre}"
    sondeos = {"ok": 0, "fallo": 0, "lat": []}
    rss = []
    parar = threading.Event()

    def sondear():
        c = httpx.Client(timeout=3)
        while not parar.is_set():
            t0 = time.perf_counter()
            try:
                ok = c.get(cs.URL + "/api/salud").status_code == 200
            except httpx.HTTPError:
                ok = False
            sondeos["ok" if ok else "fallo"] += 1
            sondeos["lat"].append((time.perf_counter() - t0) * 1000)
            rss.append(rss_mb(proc.pid))
            time.sleep(0.5)

    th = threading.Thread(target=sondear)
    th.start()
    cmd = [sys.executable, "-m", "locust", "-f", str(locustfile), "--host", cs.URL, "--headless", "-u", str(usuarios), "-r", str(max(usuarios // 2, 5)), "-t", f"{segundos}s", "--csv", str(prefijo), "--only-summary"]
    r = subprocess.run(cmd, cwd=cs.PMV, capture_output=True, text=True)
    parar.set()
    th.join()
    filas = list(csv.DictReader(open(f"{prefijo}_stats.csv", encoding="utf-8")))
    total = next(f for f in filas if f["Name"] == "Aggregated")
    por_ep = [{"endpoint": f["Name"], "peticiones": int(f["Request Count"]), "fallos": int(f["Failure Count"]), "p50_ms": float(f["50%"]), "p95_ms": float(f["95%"]), "p99_ms": float(f["99%"]), "rps": round(float(f["Requests/s"]), 2)} for f in filas if f["Name"] != "Aggregated"]
    lat = sorted(sondeos["lat"])
    out = {
        "corrida": nombre, "locustfile": str(locustfile.relative_to(cs.RAIZ)), "usuarios": usuarios, "segundos": segundos,
        "peticiones": int(total["Request Count"]), "fallos": int(total["Failure Count"]),
        "tasa_error_pct": round(100 * int(total["Failure Count"]) / max(int(total["Request Count"]), 1), 3),
        "p50_ms": float(total["50%"]), "p95_ms": float(total["95%"]), "p99_ms": float(total["99%"]), "max_ms": float(total["Max Response Time"]),
        "rps": round(float(total["Requests/s"]), 2),
        "sondeos_salud": sondeos["ok"] + sondeos["fallo"], "sondeos_fallidos": sondeos["fallo"],
        "disponibilidad_pct": round(100 * sondeos["ok"] / max(sondeos["ok"] + sondeos["fallo"], 1), 3),
        "salud_p95_ms": round(lat[int(0.95 * (len(lat) - 1))], 1) if lat else None,
        "rss_mb_min": round(min(rss), 1), "rss_mb_max": round(max(rss), 1),
        "por_endpoint": por_ep,
    }
    (SAL / f"P_{nombre}_resumen.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{nombre}: {out['usuarios']} usuarios/{segundos}s: {out['peticiones']} peticiones, fallos {out['fallos']}, p50 {out['p50_ms']} ms, p95 {out['p95_ms']} ms, p99 {out['p99_ms']} ms, {out['rps']} req/s, disp. {out['disponibilidad_pct']} %, RSS {out['rss_mb_min']}-{out['rss_mb_max']} MB")
    for e in sorted(por_ep, key=lambda x: -x["p95_ms"])[:4]:
        print(f"   {e['endpoint']:<44} n={e['peticiones']:<5} p95={e['p95_ms']} ms")
    return out


def esperar_salud(limite=60.0):
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < limite:
        try:
            if httpx.get(cs.URL + "/api/salud", timeout=1).status_code == 200:
                return time.perf_counter() - t0
        except httpx.HTTPError:
            pass
        time.sleep(0.05)
    return None


def main():
    proc = cs.levantar({})
    resultados = [
        corrida("A_inc1_inc2_20u", LF_REPO, 20, 60, proc),
        corrida("B_inc3_inc4_20u", LF_INC34, 20, 60, proc),
        corrida("C_inc1_inc2_100u", LF_REPO, 100, 60, proc),
    ]
    # R: tolerancia a fallas del proceso. kill -9 y reinicio con el mismo comando y la misma base (no hay supervisor aqui).
    antes = len(httpx.get(cs.URL + "/api/ninos?estado=", timeout=10).json())
    proc.kill()
    proc.wait()
    caido = esperar_salud(1.0)
    t0 = time.perf_counter()
    nuevo = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:crear_app", "--factory", "--port", str(cs.PUERTO)], cwd=cs.PMV, env=cs.ULTIMO_ENTORNO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        t_salud = esperar_salud()
        despues = len(httpx.get(cs.URL + "/api/ninos?estado=", timeout=10).json())
        mttr = {"servicio_caido_tras_kill": caido is None, "segundos_hasta_salud_200": round(t_salud, 2) if t_salud else None, "ninos_antes": antes, "ninos_despues": despues, "datos_integros": despues >= antes,
                "nota": "Reinicio manual con el mismo comando; en Render/Docker lo hace el orquestador (HEALTHCHECK cada 30 s en el Dockerfile). No se midio la recuperacion automatica."}
    finally:
        nuevo.terminate()
        nuevo.wait()
    (SAL / "R_mttr_reinicio.json").write_text(json.dumps(mttr, ensure_ascii=False, indent=2), encoding="utf-8")
    print("MTTR/reinicio:", json.dumps(mttr, ensure_ascii=False))
    (SAL / "P_resumen.json").write_text(json.dumps({"fecha": time.strftime("%Y-%m-%d %H:%M:%S"), "commit": cs.commit(), "corridas": [{k: v for k, v in r.items() if k != "por_endpoint"} for r in resultados]}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
