"""Factor S: complejidad ciclomatica (radon) y mantenibilidad (indice MI) de pmv_fastapi/app/ en cifras agregadas.

Uso: python entregables/semana-10/metricas/resumen_calidad.py  -> metricas/salidas/S_radon_resumen.json y stdout.
"""

import json
from collections import Counter
from pathlib import Path

from radon.complexity import cc_rank, cc_visit
from radon.metrics import mi_rank, mi_visit

RAIZ = Path(__file__).resolve().parents[3]
APP = RAIZ / "pmv_fastapi" / "app"
bloques, mis = [], []
for p in sorted(APP.rglob("*.py")):
    texto = p.read_text(encoding="utf-8")
    for b in cc_visit(texto):
        bloques.append((str(p.relative_to(APP)), b.name, b.complexity))
    if texto.strip():
        mis.append((str(p.relative_to(APP)), mi_visit(texto, multi=True)))
cc = [c for _, _, c in bloques]
rangos = Counter(cc_rank(c) for c in cc)
mi_rangos = Counter(mi_rank(m) for _, m in mis)
peores = sorted(bloques, key=lambda x: -x[2])[:5]
menor_mi = sorted(mis, key=lambda x: x[1])[:5]
res = {
    "bloques_analizados": len(cc),
    "cc_promedio": round(sum(cc) / len(cc), 2),
    "cc_maximo": max(cc),
    "bloques_cc_gt_10": sum(1 for c in cc if c > 10),
    "rangos_cc": dict(sorted(rangos.items())),
    "peores_bloques": [{"archivo": a, "bloque": n, "cc": c} for a, n, c in peores],
    "archivos_analizados": len(mis),
    "mi_promedio": round(sum(m for _, m in mis) / len(mis), 2),
    "rangos_mi": dict(sorted(mi_rangos.items())),
    "menor_mi": [{"archivo": a, "mi": round(m, 1)} for a, m in menor_mi],
}
(RAIZ / "entregables" / "semana-10" / "metricas" / "salidas" / "S_radon_resumen.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=2))
