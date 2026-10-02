#!/usr/bin/env python3
"""Fig. 61 (variante media, 5,9 x 4 in): carga antes y después de DEF-01, solo cifras clave; texto >= 16 pt.
Cifras idénticas a 61_s6_carga_p95.py: p95 agregado 310 -> 58 ms, 39,56 req/s, 0 % de errores.
Fuente: elaboración propia (Tabla 26)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[2]
plt.rcParams["font.family"] = ["Arial", "DejaVu Sans"]
W, H = 5.9, 4.0
fig = plt.figure(figsize=(W, H), facecolor="white")
T = "#1F2D3D"
fig.text(0.5, 1 - 0.25 / H, "Carga: p95 agregado", ha="center", va="center", fontsize=18, fontweight="bold", color=T)
ax = fig.add_axes([0.06, 0.50, 0.88, 0.35])
b = ax.bar(["Antes", "Después"], [310, 58], width=0.55, color=["#D98324", "#2E6B4E"], edgecolor="#333", lw=0.8)
for r, v in zip(b, (310, 58)):
    ax.text(r.get_x() + r.get_width() / 2, v + 8, f"{v} ms", ha="center", va="bottom", fontsize=16, fontweight="bold", color=T)
ax.set_ylim(0, 380); ax.set_yticks([])
ax.tick_params(axis="x", labelsize=16, length=0)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
fig.text(0.5, 0.335, "310 → 58 ms", ha="center", va="center", fontsize=18, fontweight="bold", color="#2E6B4E")
fig.text(0.5, 0.225, "39,56 req/s", ha="center", va="center", fontsize=18, fontweight="bold", color="#1F3A5F")
fig.text(0.5, 0.125, "0 % de errores", ha="center", va="center", fontsize=18, fontweight="bold", color="#1F3A5F")
fig.text(0.5, 0.035, "Fuente: elaboración propia (Tabla 26)", ha="center", va="center", fontsize=16, color="#4A5A6A")
fig.savefig(RAIZ / "diagramas/png/61_s6_carga_p95_media.png", dpi=200, facecolor="white")
fig.savefig(RAIZ / "diagramas/svg/61_s6_carga_p95_media.svg", format="svg", facecolor="white")
print("61 media OK")
