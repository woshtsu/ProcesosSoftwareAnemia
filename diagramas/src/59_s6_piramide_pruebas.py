#!/usr/bin/env python3
"""Fig. 59: pirámide de pruebas del PMV FastAPI (E-01 corregido).
Fuente: coordinacion/s6/DATOS_PMV_FASTAPI.md §6 y §17.
77 declaradas en el tag v1.0-PMV = 62 unitarias + 11 integración + 4 E2E.
Reproducidas el 01/10/2026: 73 (62 + 11 en SQLite); las 4 E2E no se ejecutaron.
La carga (Locust) es una verificación aparte y NO suma al total.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch

RAIZ = Path(__file__).resolve().parents[2]
fig, ax = plt.subplots(figsize=(13, 7.3))
ax.set_xlim(0, 13); ax.set_ylim(0, 7.3); ax.axis("off")
fig.suptitle("Pirámide de pruebas del PMV FastAPI: 77 declaradas en el tag v1.0-PMV, 73 reproducidas el 01/10/2026",
             fontsize=13.5, fontweight="bold", y=0.975)

niv = [  # (base_izq, base_der, y0, y1, color, texto, texto2)
    (0.4, 8.6, 0.4, 2.9, "#2E6B4E", "62 pruebas unitarias", "dominio y casos de uso, adaptador en memoria | reproducidas"),
    (1.5, 7.5, 3.0, 4.9, "#2F5D8A", "11 pruebas de integración y API", "SQLite reproducidas; PostgreSQL 16 sin reproducir"),
    (2.6, 6.4, 5.0, 6.4, "#B26B00", "4 pruebas E2E (Playwright)", "no reproducidas el 01/10 (falta Chromium)"),
]
for xl, xr, y0, y1, c, t1, t2 in niv:
    # trapecio: el borde superior se estrecha 0,55 por lado
    ax.add_patch(Polygon([(xl, y0), (xr, y0), (xr - 0.55, y1), (xl + 0.55, y1)],
                         facecolor=c, edgecolor="white", linewidth=2))
    ym = (y0 + y1) / 2
    ax.text((xl + xr) / 2, ym + 0.17, t1, ha="center", va="center", fontsize=13, fontweight="bold", color="white")
    ax.text((xl + xr) / 2, ym - 0.28, t2, ha="center", va="center", fontsize=9.5, color="white")

# Llave del total
ax.annotate("", xy=(8.9, 0.4), xytext=(8.9, 6.4),
            arrowprops=dict(arrowstyle="-", color="#1F2D3D", lw=1.5))
ax.text(9.05, 3.4, "62 + 11 + 4 = 77\ndeclaradas en el tag\n\n62 + 11 = 73\nreproducidas\nel 01/10/2026\n\n4 E2E: sin reproducir",
        fontsize=11.5, va="center", ha="left", color="#1F2D3D", fontweight="bold")

# Carga: verificación aparte
ax.add_patch(FancyBboxPatch((9.0, 0.35), 3.8, 1.25, boxstyle="round,pad=0.05",
                            facecolor="#F1F3F5", edgecolor="#6B7785", linestyle="--", linewidth=1.5))
ax.text(10.9, 1.2, "Verificación aparte (no cuenta en el total)", ha="center", fontsize=10, fontweight="bold", color="#1F2D3D")
ax.text(10.9, 0.78, "Escenario de carga con Locust:\n50 usuarios, 60 s; p95 agregado 58 ms", ha="center", va="center", fontsize=9.5, color="#1F2D3D")

fig.text(0.5, 0.012,
         "Fuente: elaboración propia (§3.3, Tablas 23 y 24). Cobertura reproducida: 99,07 %.", ha="center", fontsize=9, color="#4A5A6A")
fig.subplots_adjust(top=0.92, bottom=0.05, left=0.02, right=0.98)
fig.savefig(RAIZ / "diagramas/png/59_s6_piramide_pruebas.png", dpi=200, facecolor="white")
fig.savefig(RAIZ / "diagramas/svg/59_s6_piramide_pruebas.svg", format="svg", facecolor="white")
print("59 OK")
