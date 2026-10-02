#!/usr/bin/env python3
"""Fig. 63: avance acumulado del Incremento 1, planificado vs completado por HU/tarea (E-03/E-04).
Fuente: Informe integrador Tabla 14 (21 SP) y Tabla 16 (H1 el 28/09). No es una serie temporal:
todos los commits del tag v1.0-PMV son del 30/09/2026; el eje X es por historia, no por fecha."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
items = ["EP-1.T", "HU-01", "HU-03", "HU-02", "HU-04", "HU-05"]
sp = [5, 5, 3, 3, 2, 3]
acum = np.cumsum(sp)
assert acum[-1] == 21
fig, ax = plt.subplots(figsize=(12, 7))
x = np.arange(len(items))
ax.step(np.r_[-0.5, x + 0.5], np.r_[0, acum], where="post", color="#8A96A3", lw=0, label=None)
b1 = ax.bar(x - 0.19, acum, 0.38, label="Planificado acumulado (plan S3-4, 21 SP)", color="#9AA6B2", edgecolor="#333")
b2 = ax.bar(x + 0.19, acum, 0.38, label="Completado acumulado (según el tag v1.0-PMV)", color="#2E6B4E", edgecolor="#333")
for b in list(b1) + list(b2):
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.3, f"{int(b.get_height())}", ha="center", fontsize=10, fontweight="bold")
ax.axhline(21, color="#9E3A30", linestyle="--", lw=1.2)
ax.text(-0.45, 21.5, "Meta del incremento: 21 SP", color="#9E3A30", fontsize=10, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(items)
ax.set_ylim(0, 26)
ax.set_ylabel("Puntos de historia acumulados (SP)", fontsize=11, fontweight="bold")
ax.set_xlabel("Tareas e historias de usuario, en orden de entrega planificado (Sprint 1: EP-1.T, HU-01, HU-03; Sprint 2: HU-02, HU-04, HU-05)", fontsize=9.5)
ax.set_title("Avance acumulado del Incremento 1: planificado vs. completado por HU/tarea", fontsize=13, fontweight="bold")
ax.legend(fontsize=10, loc="upper left", bbox_to_anchor=(0.0, 0.80))
ax.grid(axis="y", alpha=0.3, linestyle=":"); ax.set_axisbelow(True)
fig.text(0.5, 0.012, "Entrega registrada el 30/09/2026 frente al hito H1 del 28/09/2026 (+2 días). "
         "Fuente: Informe integrador Tablas 14 y 16; git log del tag v1.0-PMV.", ha="center", fontsize=9, color="#4A5A6A")
fig.subplots_adjust(bottom=0.15, top=0.92)
fig.savefig(RAIZ / "diagramas/png/63_s6_burnup_inc1.png", dpi=200, facecolor="white")
fig.savefig(RAIZ / "diagramas/svg/63_s6_burnup_inc1.svg", format="svg", facecolor="white")
print("63 OK")
