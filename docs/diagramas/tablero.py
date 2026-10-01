"""Tablero de métricas integradas del Incremento 1 (proceso + producto + valor)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

AZUL, AMBAR, MORADO, TXT, GRIS, SUAVE = "#2E6FB2", "#D08A00", "#7B3F98", "#1B2B3A", "#5E6E7E", "#A9C3E0"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#C8D0D8", "axes.labelcolor": TXT,
                     "xtick.color": GRIS, "ytick.color": GRIS})

fig = plt.figure(figsize=(13, 7.2), dpi=160)
fig.patch.set_facecolor("white")
fig.text(0.02, 0.965, "Tablero de métricas del Incremento 1 (PMV v1.0)", fontsize=17, weight="bold", color=TXT)
fig.text(0.02, 0.93, "Proceso · Producto · Valor — valores medidos en el repositorio, las pruebas y la carga (30/09/2026)",
         fontsize=10.5, color=GRIS)

# ---- fila de indicadores (stat tiles)
tiles = [
    ("5 / 5", "HU completadas", "21 / 21 SP del INC-1", "Proceso"),
    ("99 %", "Cobertura de código", "umbral DoD 80 %", "Producto"),
    ("2,0", "Defectos / KLOC", "2 detectados y cerrados · 0 abiertos", "Producto"),
    ("58 ms", "Latencia p95 agregada", "50 usuarios · 39,6 req/s · 0 % error", "Producto"),
    ("3 → 1", "Registros por evaluación", "triple registro → expediente único", "Valor"),
]
ancho = 0.184
for i, (valor, titulo, sub, cat) in enumerate(tiles):
    x = 0.02 + i * (ancho + 0.012)
    ax = fig.add_axes([x, 0.70, ancho, 0.20])
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.01, 0.02), 0.98, 0.96, boxstyle="round,pad=0,rounding_size=0.06",
                                fc="#F4F8FC", ec="#D5E1EE", lw=1, transform=ax.transAxes))
    color = {"Proceso": AZUL, "Producto": AZUL, "Valor": AMBAR}[cat]
    ax.text(0.07, 0.80, cat.upper(), fontsize=8.5, color=GRIS, weight="bold", transform=ax.transAxes)
    ax.text(0.07, 0.43, valor, fontsize=24, weight="bold", color=color, transform=ax.transAxes)
    ax.text(0.07, 0.22, titulo, fontsize=10, color=TXT, weight="bold", transform=ax.transAxes)
    ax.text(0.07, 0.07, sub, fontsize=8, color=GRIS, transform=ax.transAxes)

# ---- panel 1: story points planificados vs entregados por HU
ax1 = fig.add_axes([0.05, 0.09, 0.26, 0.48])
hus = ["HU-01", "HU-02", "HU-03", "HU-04", "HU-05", "Infra\n+CI"]
plan = [5, 3, 3, 2, 3, 5]
real = [5, 3, 3, 2, 3, 5]
x = range(len(hus))
ax1.bar([i - 0.19 for i in x], plan, 0.36, color=SUAVE, label="Planificados (S3-4)")
ax1.bar([i + 0.19 for i in x], real, 0.36, color=AZUL, label="Entregados (v1.0-PMV)")
for i in x:
    ax1.text(i + 0.19, real[i] + 0.1, str(real[i]), ha="center", fontsize=9, color=TXT, weight="bold")
ax1.set_xticks(list(x), hus, fontsize=8.5)
ax1.set_ylim(0, 6.5)
ax1.set_ylabel("Story points")
ax1.set_title("INC-1: story points planificados vs. entregados", fontsize=11, color=TXT, loc="left", weight="bold")
ax1.legend(frameon=False, fontsize=8, loc="upper center", ncol=1)
ax1.spines[["top", "right"]].set_visible(False)
ax1.grid(axis="y", color="#EEF2F6")
ax1.set_axisbelow(True)

# ---- panel 2: pruebas por nivel
ax2 = fig.add_axes([0.43, 0.09, 0.22, 0.48])
niveles = ["Unitarias", "Integración/API", "E2E (UI)", "Carga"]
cant = [62, 11, 4, 1]
ax2.barh(niveles[::-1], cant[::-1], color=AZUL, height=0.55)
for i, v in enumerate(cant[::-1]):
    ax2.text(v + 1, i, f"{v}", va="center", fontsize=9.5, color=TXT, weight="bold")
ax2.set_xlim(0, 70)
ax2.set_title("Pruebas por nivel (100 % en verde)", fontsize=11, color=TXT, loc="left", weight="bold")
ax2.spines[["top", "right"]].set_visible(False)
ax2.set_xlabel("Casos (carga = escenario de 50 usuarios)")

# ---- panel 3: latencia p95 antes/después DEF-01
ax3 = fig.add_axes([0.745, 0.09, 0.235, 0.48])
ops = ["Reporte del\nperiodo", "Agregado"]
antes = [2200, 310]
despues = [74, 58]
xs = range(len(ops))
ax3.bar([i - 0.19 for i in xs], antes, 0.36, color=SUAVE, label="Antes (DEF-01)")
ax3.bar([i + 0.19 for i in xs], despues, 0.36, color=AZUL, label="Después (ADR-006)")
for i in xs:
    ax3.text(i - 0.19, antes[i] + 40, f"{antes[i]:,}".replace(",", " "), ha="center", fontsize=9, color=GRIS)
    ax3.text(i + 0.19, despues[i] + 40, str(despues[i]), ha="center", fontsize=9, color=TXT, weight="bold")
ax3.set_xticks(list(xs), ops, fontsize=9)
ax3.set_ylabel("Latencia p95 (ms)")
ax3.set_ylim(0, 2500)
ax3.set_title("DEF-01: latencia p95 antes y después", fontsize=11, color=TXT, loc="left", weight="bold")
ax3.legend(frameon=False, fontsize=8.5)
ax3.spines[["top", "right"]].set_visible(False)
ax3.grid(axis="y", color="#EEF2F6")
ax3.set_axisbelow(True)

fig.savefig("G4_tablero_metricas.png", bbox_inches="tight", facecolor="white")
print("ok")
