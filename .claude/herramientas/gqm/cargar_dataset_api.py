#!/usr/bin/env python
"""Carga un dataset sintético (generar_dataset.py) en un servidor en ejecución SOLO mediante su API pública.

Mismo procedimiento para v1.0 y v1.5 (el contrato de registro es el mismo): POST /api/ninos con la evaluación más
antigua, POST /api/ninos/{id}/evaluaciones por cada evaluación posterior (en orden cronológico) y PATCH estado=ALTA
cuando corresponda. Devuelve/guarda el mapa dni -> id.

Uso:  python cargar_dataset_api.py --base http://127.0.0.1:8201 --dataset datos/dataset_B150.json [--mapa ids.json]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx


def cargar(base: str, dataset: dict) -> tuple[dict, list[str]]:
    ids, errores = {}, []
    h = {"X-Usuario": "gqm.carga"}
    with httpx.Client(base_url=base, timeout=30, headers=h) as c:
        for n in dataset["ninos"]:
            evs = sorted(n["evaluaciones"], key=lambda e: e["fecha"])
            body = {
                "nino": {
                    "dni": n["dni"], "nombres": n["nombres"], "apellidos": n["apellidos"], "sexo": n["sexo"],
                    "fecha_nacimiento": n["nacimiento"], "establecimiento": n["establecimiento"],
                    "distrito": n["distrito"], "comunidad": n["comunidad"], "altitud_m": n["altitud"],
                    "tutor_nombre": n["tutor"], "tutor_celular": n["celular"],
                },
                "evaluacion_inicial": {"fecha": evs[0]["fecha"], "hemoglobina_observada": evs[0]["hb_obs"],
                                       "peso_kg": evs[0]["peso_kg"], "talla_cm": evs[0]["talla_cm"]},
            }
            r = c.post("/api/ninos", json=body)
            if r.status_code != 201:
                errores.append(f"{n['dni']} registro {r.status_code}: {r.text[:200]}")
                continue
            nid = r.json()["id"]
            ids[n["dni"]] = nid
            for e in evs[1:]:
                r = c.post(f"/api/ninos/{nid}/evaluaciones", json={
                    "fecha": e["fecha"], "hemoglobina_observada": e["hb_obs"], "peso_kg": e["peso_kg"], "talla_cm": e["talla_cm"]})
                if r.status_code != 201:
                    errores.append(f"{n['dni']} evaluación {e['fecha']} {r.status_code}: {r.text[:200]}")
            if n["estado"] != "ACTIVO":
                r = c.patch(f"/api/ninos/{nid}", json={"estado": n["estado"]})
                if r.status_code != 200:
                    errores.append(f"{n['dni']} estado {r.status_code}: {r.text[:200]}")
    return ids, errores


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--mapa", default=None)
    a = ap.parse_args()
    ds = json.loads(Path(a.dataset).read_text(encoding="utf-8"))
    t0 = time.time()
    ids, errores = cargar(a.base, ds)
    print(f"{len(ids)}/{len(ds['ninos'])} niños cargados en {time.time() - t0:.1f} s; errores: {len(errores)}")
    for e in errores[:20]:
        print("  ", e)
    if a.mapa:
        Path(a.mapa).write_text(json.dumps(ids, indent=1))
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
