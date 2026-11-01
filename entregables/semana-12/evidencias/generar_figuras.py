"""Genera la figura de evolución GQM/pruebas del informe S12.

Fuente de los valores: entregables/semana-09/ADENDA_v4_REFERENCIA_S12.md (secciones 2 y 4) y
entregables/semana-09/Entregable_Semana9_Anemia_Junin.md (metas acumuladas propuestas, sección 6.4).
Uso: python generar_figuras.py   (escribe GQM_v4_evolucion.png junto a este archivo)
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SALIDA = Path(__file__).with_name("GQM_v4_evolucion.png")
INCS = ["Inc. 1\nv1.0-PMV", "Inc. 2\nv2.0-Inc2", "Inc. 3\nv3.0-Inc3", "Inc. 4\nv4.0-Inc4"]
M31 = [25.0, 33.3, 50.0, 75.0]
META_ACUM = [16.7, 33.3, 50.0, 66.7]  # metas acumuladas propuestas en S9 (no aprobadas)
UNIT = [73, 328, 499, 660]  # unitarias + integración + arquitectura
E2E = [4, 15, 24, 28]
COBERTURA = [99.0, 100.0, 99.70, 99.79]

AZUL, VERDE, NARANJA, GRIS = "#1F4E79", "#1F7A3D", "#B4530B", "#5B6B7B"

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=160)

x = range(4)
a1.bar([i - 0.2 for i in x], M31, width=0.4, color=AZUL, label="M3.1 principal (Σ puntos ÷ 6)")
a1.bar([i + 0.2 for i in x], META_ACUM, width=0.4, color="#A9C4E2", label="Meta acumulada propuesta (S9, no aprobada)")
for i, v in enumerate(M31):
    a1.text(i - 0.2, v + 1.2, f"{v:.1f} %".replace(".", ","), ha="center", fontsize=8.5, color=AZUL, fontweight="bold")
for i, v in enumerate(META_ACUM):
    a1.text(i + 0.2, v + 1.2, f"{v:.1f} %".replace(".", ","), ha="center", fontsize=8, color=GRIS)
a1.set_xticks(list(x), INCS, fontsize=8.5)
a1.set_ylim(0, 100)
a1.set_ylabel("Brechas AS-IS resueltas (%)")
a1.set_title("GQM M3.1: cobertura de brechas por incremento", fontsize=10.5, loc="left")
a1.legend(fontsize=8, loc="upper left", frameon=False)

a2.bar(list(x), UNIT, width=0.5, color=AZUL, label="Unitarias + integración + arquitectura")
a2.bar(list(x), E2E, width=0.5, bottom=UNIT, color=VERDE, label="E2E (Playwright)")
for i, (u, e) in enumerate(zip(UNIT, E2E)):
    a2.text(i, u + e + 14, f"{u} + {e}", ha="center", fontsize=8.5, fontweight="bold")
etiquetas = [f"{n}\ncobertura " + f"{c:.2f} %".replace(".", ",") for n, c in zip(INCS, COBERTURA)]
a2.set_xticks(list(x), etiquetas, fontsize=8)
a2.set_ylim(0, 800)
a2.set_ylabel("Pruebas automatizadas aprobadas")
a2.set_title("Pruebas aprobadas y cobertura de app/ por incremento", fontsize=10.5, loc="left")
a2.legend(fontsize=8, loc="upper left", frameon=False)

for a in (a1, a2):
    a.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.005, "Fuente: adenda GQM v4 (entregables/semana-09). Cobertura Inc. 1: 99 % y Inc. 2: 100 % según S9; Inc. 3 y 4: pytest --cov=app.",
         fontsize=7.5, color=GRIS)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(SALIDA)
print("escrito", SALIDA)
