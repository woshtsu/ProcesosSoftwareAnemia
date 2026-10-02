#!/usr/bin/env python3
"""Fig. 67: matriz visual de factores del proyecto (E-05: cinco factores en nivel Alto).
Fuente: Informe integrador Tabla 7; S2 §1-§2."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

RAIZ = Path(__file__).resolve().parents[2]
filas = [
    ("Incertidumbre", "Alto", "Requisitos clínicos acotados por la norma, pero la IA, la mensajería\ny el modo sin conexión no; cambios y retroalimentación frecuentes",
     "Incrementos pequeños y revisión por sprint"),
    ("Complejidad", "Alto", "Modelo predictivo, API de mensajería, sincronización sin conexión\ne interfaces por rol",
     "Diseño modular, contratos y pruebas por nivel"),
    ("Riesgo", "Alto", "Pérdida de datos por conectividad intermitente y decisiones\nsobre salud infantil",
     "Validación en varios niveles y entregas cortas"),
    ("Integración", "Alto", "HIS, mensajería, artefacto del modelo y módulo sin conexión",
     "Aislar adaptadores y probar la\nintegración de forma automatizada"),
    ("Datos/IA", "Alto", "Datos históricos de calidad variable, experimentación versionada\ny monitoreo",
     "MLOps desde INC-5, sujeto a la\ndisponibilidad de datos"),
]
color = "#E8A09A"
fig, ax = plt.subplots(figsize=(14, 7.6))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
fig.suptitle("Matriz visual de factores del proyecto: los cinco factores en nivel Alto", fontsize=15, fontweight="bold")
ax.text(0.03, 0.955, "Factor", fontsize=11, fontweight="bold", color="#1F2D3D")
ax.text(0.20, 0.955, "Nivel", fontsize=11, fontweight="bold", color="#1F2D3D")
ax.text(0.29, 0.955, "Situación del proyecto", fontsize=11, fontweight="bold", color="#1F2D3D")
ax.text(0.71, 0.955, "Consecuencia para el proceso", fontsize=11, fontweight="bold", color="#1F2D3D")
h = 0.16
for i, (f, n, s, c) in enumerate(filas):
    y = 0.92 - i * (h + 0.012)
    ax.add_patch(FancyBboxPatch((0.01, y - h), 0.98, h, boxstyle="round,pad=0.003", transform=ax.transAxes,
                                facecolor="#FBEAE8", edgecolor="#9E3A30", linewidth=1))
    ax.text(0.03, y - h/2, f, fontsize=13, fontweight="bold", va="center")
    ax.add_patch(Circle((0.215, y - h/2), 0.014, transform=ax.transAxes, facecolor="#C0392B", edgecolor="#333"))
    ax.text(0.235, y - h/2, n, fontsize=11, va="center", fontweight="bold")
    ax.text(0.29, y - h/2, s, fontsize=10, va="center", color="#222", linespacing=1.3)
    ax.text(0.71, y - h/2, c, fontsize=10, va="center", color="#1F3A5F", wrap=True)
fig.text(0.5, 0.012, "Fuente: Informe integrador, Tabla 7; entregables/semana-02 (S2 §1 y §2). Ocho factores de S2, todos de importancia alta, agrupados en cinco.",
         ha="center", fontsize=9, color="#4A5A6A")
fig.subplots_adjust(top=0.92, bottom=0.05, left=0.01, right=0.99)
fig.savefig(RAIZ / "diagramas/png/67_s6_matriz_factores.png", dpi=200, facecolor="white")
fig.savefig(RAIZ / "diagramas/svg/67_s6_matriz_factores.svg", format="svg", facecolor="white")
print("67 OK")
