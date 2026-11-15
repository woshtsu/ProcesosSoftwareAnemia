#!/usr/bin/env python
"""Sonda de salud (V5): GET /api/salud cada 1 s; guarda CSV y resume la disponibilidad.

Disponibilidad = respuestas HTTP 200 recibidas en menos de 2 s / sondas enviadas x 100.
Una sonda con error de conexión o tiempo agotado cuenta como no disponible.

Uso:  python sonda_salud.py --base http://127.0.0.1:8201 --segundos 60 --csv salidas/v1.0/sonda_carga.csv [--json r.json]
      python sonda_salud.py --base ... --hasta-archivo /tmp/fin.flag --csv ...   (sondea hasta que exista el archivo)
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path

import httpx


def sondear(base: str, segundos: float | None, hasta_archivo: str | None, csv_ruta: str, umbral_s: float = 2.0) -> dict:
    Path(csv_ruta).parent.mkdir(parents=True, exist_ok=True)
    filas = []
    inicio = time.time()
    siguiente = inicio
    with httpx.Client(base_url=base, timeout=umbral_s) as cli:
        while True:
            ahora = time.time()
            if segundos is not None and ahora - inicio >= segundos:
                break
            if hasta_archivo and Path(hasta_archivo).exists():
                break
            t0 = time.perf_counter()
            try:
                r = cli.get("/api/salud")
                dur = time.perf_counter() - t0
                codigo = r.status_code
                a_tiempo = codigo == 200 and dur < umbral_s
            except httpx.HTTPError as e:
                dur = time.perf_counter() - t0
                codigo = type(e).__name__
                a_tiempo = False
            filas.append((datetime.now().isoformat(timespec="milliseconds"), codigo, round(dur * 1000, 1), int(a_tiempo)))
            siguiente += 1.0
            espera = siguiente - time.time()
            if espera > 0:
                time.sleep(espera)
    with open(csv_ruta, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["marca_tiempo", "codigo", "duracion_ms", "disponible"])
        w.writerows(filas)
    n = len(filas)
    ok = sum(f[3] for f in filas)
    dur = sorted(f[2] for f in filas)
    return {
        "sondas": n,
        "disponibles": ok,
        "disponibilidad_pct": round(ok / n * 100, 2) if n else None,
        "latencia_mediana_ms": dur[len(dur) // 2] if dur else None,
        "latencia_p95_ms": dur[max(int(0.95 * len(dur)) - 1, 0)] if dur else None,
        "latencia_max_ms": dur[-1] if dur else None,
        "fallos": [f for f in filas if not f[3]][:10],
        "umbral_s": umbral_s,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--segundos", type=float, default=None)
    ap.add_argument("--hasta-archivo", default=None)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    res = sondear(a.base, a.segundos, a.hasta_archivo, a.csv)
    print(json.dumps(res, ensure_ascii=False))
    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
