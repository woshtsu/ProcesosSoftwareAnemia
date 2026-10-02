#!/usr/bin/env python3
"""Fig. 59 (variante media, 5,4 x 4 in): pirámide de pruebas, solo cifras clave; texto >= 16 pt.
Cifras idénticas a 59_s6_piramide_pruebas.py: 62 + 11 + 4 = 77 declaradas, 73 reproducidas el 01/10, carga aparte.
Fuente: elaboración propia (§3.3)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch

RAIZ = Path(__file__).resolve().parents[2]
plt.rcParams["font.family"] = ["Arial", "DejaVu Sans"]
W, H = 5.4, 4.0
fig = plt.figure(figsize=(W, H), facecolor="white")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
ax.text(W / 2, 0.25, "Pirámide de pruebas", ha="center", va="center", fontsize=18, fontweight="bold", color="#1F2D3D")

cx, base, apex = W / 2, 5.0, 0.9      # anchos de la base y del vértice truncado
y_top, y_bot = 0.5, 2.2
def ancho(y): return apex + (base - apex) * (y - y_top) / (y_bot - y_top)
niv = [(0.5, 1.05, "#B26B00", "4 E2E"), (1.08, 1.63, "#2F5D8A", "11 integración"), (1.66, 2.2, "#2E6B4E", "62 unitarias")]
for y0, y1, c, t in niv:
    w0, w1 = ancho(y0), ancho(y1)
    ax.add_patch(Polygon([(cx - w0 / 2, y0), (cx + w0 / 2, y0), (cx + w1 / 2, y1), (cx - w1 / 2, y1)],
                         fc=c, ec="white", lw=2))
    ax.text(cx, (y0 + y1) / 2, t, ha="center", va="center", fontsize=16, fontweight="bold", color="white")
ax.text(cx, 2.45, "77 declaradas (62 + 11 + 4)", ha="center", va="center", fontsize=16, fontweight="bold", color="#1F2D3D")
ax.text(cx, 2.78, "73 reproducidas el 01/10", ha="center", va="center", fontsize=16, fontweight="bold", color="#1F2D3D")
ax.add_patch(FancyBboxPatch((0.6, 3.0), 4.2, 0.4, boxstyle="round,pad=0,rounding_size=0.08",
                            fc="#F1F3F5", ec="#6B7785", ls="--", lw=1.5))
ax.text(cx, 3.2, "Carga: aparte", ha="center", va="center", fontsize=16, color="#1F2D3D")
ax.text(cx, 3.7, "Fuente: elaboración propia (§3.3)", ha="center", va="center", fontsize=16, color="#4A5A6A")
fig.savefig(RAIZ / "diagramas/png/59_s6_piramide_pruebas_media.png", dpi=200, facecolor="white")
fig.savefig(RAIZ / "diagramas/svg/59_s6_piramide_pruebas_media.svg", format="svg", facecolor="white")
print("59 media OK")
