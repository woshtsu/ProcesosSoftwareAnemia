#!/usr/bin/env python3
"""Fig. 61: prueba de carga antes y después de DEF-01 (E-11: coma decimal, anotaciones sin solape).
Fuente: pmv_fastapi/docs/evidencias/carga/*.csv; coordinacion/s6/DATOS_PMV_FASTAPI.md §9."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7), gridspec_kw={"width_ratios": [1.5, 1]})

eps = ["Reporte\n(GET /api/reportes/periodo)", "Listar niños\n(GET /api/ninos)",
       "Obtener niño\n(GET /api/ninos/{id})", "Registrar niño\n(POST /api/ninos)", "Agregado\n(todos)"]
antes = [2200, 250, 56, 100, 310]
despues = [74, 75, 30, 36, 58]
x = np.arange(len(eps)); w = 0.38
b1 = ax1.bar(x - w/2, antes, w, label="Antes de DEF-01", color="#D98324", edgecolor="#333", linewidth=0.8)
b2 = ax1.bar(x + w/2, despues, w, label="Después de DEF-01", color="#2E6B4E", edgecolor="#333", linewidth=0.8)
for bars in (b1, b2):
    for b in bars:
        v = int(b.get_height())
        ax1.text(b.get_x() + b.get_width()/2, v + 35, f"{v:,}".replace(",", " "), ha="center", va="bottom", fontsize=10, fontweight="bold")
ax1.set_ylabel("Latencia p95 (ms)", fontsize=11, fontweight="bold")
ax1.set_title("Latencia p95 por endpoint (50 usuarios, 60 s)", fontsize=12, fontweight="bold")
ax1.set_xticks(x); ax1.set_xticklabels(eps, fontsize=9)
ax1.set_ylim(0, 2750)
ax1.legend(fontsize=10, loc="upper right")
ax1.grid(axis="y", alpha=0.3, linestyle=":")
ax1.set_axisbelow(True)
# anotación del reporte, a la derecha de las barras y sin pisar la leyenda
ax1.annotate("Reporte: 2 200 ms a 74 ms\n(97 % menos latencia p95\nen ese endpoint)",
             xy=(0.2, 1300), xytext=(1.25, 1450), fontsize=10, color="#9E3A30", fontweight="bold",
             arrowprops=dict(arrowstyle="->", color="#9E3A30", lw=1.5),
             bbox=dict(boxstyle="round", facecolor="white", edgecolor="#9E3A30"))

ax2.axis("off"); ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
ax2.set_title("Métricas globales (agregado)", fontsize=12, fontweight="bold")
filas = [
    ("Solicitudes totales", "2 170 → 2 336", "+7,6 % de solicitudes atendidas"),
    ("p95 agregado", "310 ms → 58 ms", "−81,3 % de latencia (agregado)"),
    ("Rendimiento", "36,74 → 39,56 req/s", "+7,7 % de solicitudes por segundo"),
    ("Fallos", "0 → 0 (0 %)", "Sin errores en ambas corridas"),
    ("Escenario", "50 usuarios, 60 s", "Locust 2.46.6, perfil PersonalPosta"),
]
y = 0.92
for t, v, n in filas:
    ax2.add_patch(plt.Rectangle((0.02, y - 0.155), 0.96, 0.165, facecolor="#E6EEF7", edgecolor="#34506B", linewidth=0.8))
    ax2.text(0.05, y - 0.02, t, fontsize=10.5, fontweight="bold", va="top", color="#1F2D3D")
    ax2.text(0.05, y - 0.065, v, fontsize=12, fontweight="bold", va="top", color="#1F3A5F")
    ax2.text(0.05, y - 0.115, n, fontsize=9.5, va="top", color="#4A5A6A", style="italic")
    y -= 0.19

fig.suptitle("Prueba de carga: efecto de DEF-01 (consultas por lotes, ADR-006)", fontsize=14, fontweight="bold")
fig.text(0.5, 0.01, "Fuente: pmv_fastapi/docs/evidencias/carga/linea_base_antes_DEF-01_stats.csv y despues_DEF-01_stats.csv; "
         "coordinacion/s6/DATOS_PMV_FASTAPI.md §9. Datos sintéticos.", ha="center", fontsize=9, color="#4A5A6A")
fig.subplots_adjust(top=0.88, bottom=0.14, left=0.06, right=0.98, wspace=0.12)
fig.savefig(RAIZ / "diagramas/png/61_s6_carga_p95.png", dpi=200, facecolor="white")
fig.savefig(RAIZ / "diagramas/svg/61_s6_carga_p95.svg", format="svg", facecolor="white")
print("61 OK")
