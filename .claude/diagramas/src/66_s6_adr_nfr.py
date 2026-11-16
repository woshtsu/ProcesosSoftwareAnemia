#!/usr/bin/env python3
"""Fig. 66: ADR y atributos de calidad (E-10: ADR-002 «PWA con borrador local»; cabecera sin solapes).
Fuente: pmv_fastapi/docs/adr/ADR-001..006; DATOS_PMV_FASTAPI.md §9 y §13."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

RAIZ = Path(__file__).resolve().parents[2]
adrs = [
    ("ADR-001", "Arquitectura hexagonal\nen monolito modular", "Mantenibilidad y capacidad de prueba", "62 pruebas unitarias en menos de 1 s"),
    ("ADR-002", "PWA con borrador local\n(el registro requiere conexión)", "Portabilidad y red intermitente", "Borrador en el dispositivo;\ncola sin conexión en INC-3"),
    ("ADR-003", "PostgreSQL con UNIQUE,\nFK y CHECK", "Integridad y consistencia", "DNI único; rangos repetidos en la BD"),
    ("ADR-004", "Reglas clínicas parametrizadas", "Exactitud clínica", "Cortes OMS 2024 en un solo módulo"),
    ("ADR-005", "API REST con contrato OpenAPI", "Interoperabilidad", "Errores 422, 409 y 404 con formato único"),
    ("ADR-006", "Consultas por lotes\n(corrección DEF-01)", "Latencia (rendimiento)", "p95 del reporte: 2 200 → 74 ms"),
]
fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
fig.suptitle("Decisiones de arquitectura (ADR) vinculadas a atributos de calidad", fontsize=15, fontweight="bold")
cols = [0.025, 0.12, 0.43, 0.70]
heads = ["ADR", "Decisión", "Atributo de calidad principal", "Evidencia"]
ax.add_patch(Rectangle((0.01, 0.905), 0.98, 0.065, facecolor="#1F3A5F"))
for x, t in zip(cols, heads):
    ax.text(x, 0.9375, t, fontsize=12, fontweight="bold", color="white", va="center")
rh = 0.14
for i, (a, d, n, e) in enumerate(adrs):
    y = 0.895 - (i + 1) * rh + 0.01
    ax.add_patch(Rectangle((0.01, y), 0.98, rh - 0.012, facecolor="#E6EEF7" if i % 2 == 0 else "#F5F6F8", edgecolor="#B8C2CC", linewidth=0.7))
    ym = y + (rh - 0.012) / 2
    ax.text(cols[0], ym, a, fontsize=12, fontweight="bold", va="center")
    ax.text(cols[1], ym, d, fontsize=11, va="center", linespacing=1.3)
    ax.text(cols[2], ym, n, fontsize=11, va="center", color="#1F5FA0", fontweight="bold")
    ax.text(cols[3], ym, e, fontsize=10.5, va="center", color="#333", linespacing=1.3)
fig.text(0.5, 0.012, "Fuente: elaboración propia (Tabla 21).",
         ha="center", fontsize=9, color="#4A5A6A")
fig.subplots_adjust(top=0.92, bottom=0.04, left=0.01, right=0.99)
fig.savefig(RAIZ / "diagramas/png/66_s6_adr_nfr.png", dpi=200, facecolor="white")
fig.savefig(RAIZ / "diagramas/svg/66_s6_adr_nfr.svg", format="svg", facecolor="white")
print("66 OK")
