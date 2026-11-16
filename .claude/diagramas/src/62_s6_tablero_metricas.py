#!/usr/bin/env python3
"""Fig. 62: tablero de métricas del Incremento 1 (E-02 corregido).
Fuente: Informe integrador Tabla 14 (SP: EP-1.T 5, HU-01 5, HU-03 3, HU-02 3, HU-04 2, HU-05 3 = 21);
DATOS_PMV_FASTAPI.md §6-§9 y §17."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
fig = plt.figure(figsize=(15, 9))
gs = fig.add_gridspec(3, 3, hspace=0.45, wspace=0.25, top=0.88, bottom=0.12, left=0.04, right=0.98)
fig.suptitle("Tablero de métricas del Incremento 1: proceso, producto y valor (PMV FastAPI)", fontsize=15, fontweight="bold")

tiles = [
    ("5/5 HU", "21/21 puntos de historia\n(incluye EP-1.T, 5 SP)", "#2E6B4E", "#E4F1EA"),
    ("99 %", "cobertura de código\n(2 sentencias sin cubrir)", "#2F5D8A", "#E6EEF7"),
    ("2,0", "defectos/KLOC\n(0 abiertos)", "#B26B00", "#FBF3DF"),
    ("58 ms", "p95 agregado\n(50 usuarios, 60 s)", "#5B3F8C", "#EEE8F6"),
    ("3 → 1", "registros por evaluación\n(datos sintéticos)", "#9E3A30", "#F7E3E1"),
    ("39,56", "solicitudes/s\n(0 % de fallos)", "#1F6F78", "#E0F1F3"),
]
for i, (big, small, fg, bg) in enumerate(tiles):
    ax = fig.add_subplot(gs[i // 3, i % 3]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor=bg, edgecolor=fg, linewidth=2))
    ax.text(0.5, 0.64, big, ha="center", va="center", fontsize=26, fontweight="bold", color=fg)
    ax.text(0.5, 0.25, small, ha="center", va="center", fontsize=11, color="#222")

ax7 = fig.add_subplot(gs[2, :2])
items = ["EP-1.T", "HU-01", "HU-03", "HU-02", "HU-04", "HU-05"]
sp = [5, 5, 3, 3, 2, 3]
assert sum(sp) == 21
x = np.arange(len(items))
bars = ax7.bar(x - 0.19, sp, 0.38, label="Planificado", color="#9AA6B2", edgecolor="#333")
bars2 = ax7.bar(x + 0.19, sp, 0.38, label="Completado (según el tag v1.0-PMV)", color="#2E6B4E", edgecolor="#333")
for b in list(bars) + list(bars2):
    ax7.text(b.get_x() + b.get_width()/2, b.get_height() + 0.1, f"{int(b.get_height())}", ha="center", fontsize=10, fontweight="bold")
ax7.set_xticks(x); ax7.set_xticklabels(items); ax7.set_ylim(0, 6.6)
ax7.set_ylabel("Puntos de historia (SP)")
ax7.set_title("Planificado vs. completado por HU/tarea (total 21 SP)", fontsize=11, fontweight="bold")
ax7.legend(fontsize=9, loc="upper right", ncol=2); ax7.grid(axis="y", alpha=0.3, linestyle=":"); ax7.set_axisbelow(True)

ax8 = fig.add_subplot(gs[2, 2]); ax8.axis("off"); ax8.set_xlim(0, 1); ax8.set_ylim(0, 1)
ax8.add_patch(Rectangle((0, 0), 1, 1, facecolor="#FFFBEA", edgecolor="#B08A2E", linewidth=1.2))
ax8.text(0.04, 0.95, "Resumen del Incremento 1", fontsize=11, fontweight="bold", va="top")
ax8.text(0.04, 0.82,
         "- 77 pruebas declaradas en el tag\n  (62 + 11 + 4); 73 reproducidas\n  el 01/10/2026\n"
         "- 99 % de cobertura\n- 0 defectos abiertos\n- 5 HU entregadas\n- Arquitectura hexagonal\n- PostgreSQL y Docker",
         fontsize=9, va="top", linespacing=1.3)

fig.text(0.5, 0.012, "Fuente: elaboración propia (Tablas 14, 23, 24 y 26). "
         "Datos sintéticos.", ha="center", fontsize=9, color="#4A5A6A")
fig.savefig(RAIZ / "diagramas/png/62_s6_tablero_metricas.png", dpi=200, facecolor="white")
fig.savefig(RAIZ / "diagramas/svg/62_s6_tablero_metricas.svg", format="svg", facecolor="white")
print("62 OK")
