#!/usr/bin/env python
"""M3.1 recalculado para las versiones 3.0.0-inc3 y 4.0.0-inc4 con la misma regla y fórmula del informe S9.

Regla (sin cambios): 1 = mecanismo TO-BE completo, operativo y probado; 0,5 = parcial; 0 = no. M3.1 = Σ puntos ÷ 6 × 100;
complementaria = puntos de las brechas comprometidas hasta el incremento ÷ n.º de brechas comprometidas × 100.
El puntaje es un juicio de ingeniería; el script verifica los hechos en que se apoya (rutas HTTP y palabras clave en app/).

Uso:  GQM_RAIZ_V20=<ruta a pmv_fastapi de la versión> python m31_brechas_v4.py [--version v3.0|v4.0]
Salida: entregables/semana-09/metricas/salidas/m31_brechas_v4.json (conserva la clave de la otra versión).
No toca datos/m31_brechas.json (informe S9 entregado).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import comun as c
import m31_brechas as m

PUNTOS = {
    "v3.0": {"B1": 1.0, "B2": 0.5, "B3": 0.0, "B4": 1.0, "B5": 0.0, "B6": 0.5},
    "v4.0": {"B1": 1.0, "B2": 1.0, "B3": 1.0, "B4": 1.0, "B5": 0.0, "B6": 0.5},
}
COMMIT = {"v3.0": "pmv_fastapi en el commit e920820 (3.0.0-inc3)", "v4.0": "pmv_fastapi en el commit e6886e2 (4.0.0-inc4)"}
COMPROMETIDAS = {"v3.0": ["B1", "B2", "B4", "B6"], "v4.0": ["B1", "B2", "B3", "B4", "B6"]}
RUTAS_CLAVE = {
    "B2": ["POST /recordatorios/generar", "GET /recordatorios", "POST /recordatorios/{recordatorio_id}/respuesta", "POST /notificaciones/whatsapp/webhook"],
    "B3": ["POST /ninos/{nino_id}/barreras", "GET /ninos/{nino_id}/barreras", "GET /alertas/barreras"],
    "B4": ["POST /ninos/{nino_id}/visitas", "GET /ninos/{nino_id}/visitas", "GET /visitas/priorizadas"],
    "B6": ["POST /sincronizacion", "GET /sincronizacion/conflictos", "POST /sincronizacion/conflictos/{conflicto_id}/resolver"],
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", required=True, choices=list(PUNTOS))
    a = ap.parse_args()
    v = a.version
    raiz = c.RAICES["v2.0"]  # la variable GQM_RAIZ_V20 apunta a la versión evaluada
    rutas = m.rutas("v2.0")
    web = {f: (raiz / "app" / "web" / f).is_file() for f in ("cola.js", "sync.js")}
    claves = {b: {r: (r in rutas) for r in rs} for b, rs in RUTAS_CLAVE.items()}
    palabras = {p: len(m.ocurrencias("v2.0", p)) for p in m.PALABRAS}
    pts = PUNTOS[v]
    suma = sum(pts.values())
    comp = COMPROMETIDAS[v]
    sc = sum(pts[b] for b in comp)
    estricta = sum(1 for p in pts.values() if p == 1.0)
    res = {
        "codigo_evaluado": COMMIT[v],
        "puntos": pts,
        "principal": {"suma": suma, "de_6": 6, "pct": round(suma / 6 * 100, 1)},
        "complementaria": {"brechas": comp, "puntos": sc, "pct": round(sc / len(comp) * 100, 1)},
        "estricta": {"brechas_con_1": estricta, "pct": round(estricta / 6 * 100, 1)},
        "sensibilidades_pct": {
            "B6_igual_0": round((suma - pts["B6"]) / 6 * 100, 1),
            "B2_a_0_5_si_se_exige_envio_real_probado": round((suma - 0.5) / 6 * 100, 1) if pts["B2"] == 1.0 else None,
            "B5_a_0_5_si_la_visita_priorizada_cuenta_como_busqueda_activa": round((suma + 0.5) / 6 * 100, 1),
        },
        "rutas_clave_presentes": claves,
        "archivos_sin_conexion": web,
        "ocurrencias_palabras_en_app": palabras,
        "n_rutas_http": len(rutas),
    }
    salida = c.SALIDAS / "m31_brechas_v4.json"
    c.fusionar_json(Path(salida), {v: res})
    print(v, res["principal"], res["complementaria"], res["estricta"], res["sensibilidades_pct"])


if __name__ == "__main__":
    main()
