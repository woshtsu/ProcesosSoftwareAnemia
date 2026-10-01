import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
from datetime import date, timedelta

AZUL, AMBAR, MORADO, TXT, GRIS = "#2E6FB2", "#D08A00", "#7B3F98", "#1B2B3A", "#5E6E7E"
plt.rcParams["font.family"] = "DejaVu Sans"
sprints = [
    ("Sprint 1", date(2026,9,1), date(2026,9,14), "INC-1 (parte 1)", "Arquitectura base, CI/CD y registro nominal", None),
    ("Sprint 2", date(2026,9,15), date(2026,9,28), "INC-1 (parte 2)", "Expediente completo y reporte", "H1"),
    ("Sprint 3", date(2026,9,29), date(2026,10,12), "INC-2", "Agenda automática NTS 134 y alertas", "H2"),
    ("Sprint 4", date(2026,10,13), date(2026,10,26), "INC-3", "Modo offline y sincronización", "H3"),
    ("Sprint 5", date(2026,10,27), date(2026,11,9), "INC-4", "Notificaciones y barreras", "H4"),
    ("Sprint 6", date(2026,11,10), date(2026,11,23), "INC-5 (parte 1)", "Experimentación, entrenamiento y evaluación", "H5"),
    ("Sprint 7", date(2026,11,24), date(2026,12,7), "INC-5 p.2 + INC-6", "Integración modelo-agenda e inicio del tablero", "H6"),
    ("Sprint 8", date(2026,12,8), date(2026,12,21), "INC-6", "Tablero territorial e integración del MVP", "H7"),
]
fig, ax = plt.subplots(figsize=(16, 9), dpi=150)
filas = len(sprints) + 1
def y(i): return filas - i
for i, (sp, ini, fin, inc, desc, hito) in enumerate(sprints):
    yy = y(i)
    x0 = mdates.date2num(ini); w = mdates.date2num(fin + timedelta(days=1)) - x0
    ax.add_patch(FancyBboxPatch((x0, yy - 0.3), w, 0.6, boxstyle="round,pad=0,rounding_size=1.2",
                                facecolor=AZUL, edgecolor="white", linewidth=2, mutation_aspect=0.05))
    ax.text(x0 + w/2 - 0.9, yy + 0.02, inc, ha="center", va="center", color="white", fontsize=10.5, fontweight="bold")
    ax.text(x0 + w/2, yy - 0.5, desc, ha="center", va="center", color=TXT, fontsize=8.6)
    if hito:
        xh = mdates.date2num(fin) + 0.5
        ax.plot(xh, yy, marker="D", markersize=13, color=MORADO, markeredgecolor="white", markeredgewidth=1.5, zorder=5)
        ax.text(xh, yy + 0.52, f"{hito} · {fin.strftime('%d/%m')}", ha="center", va="center", fontsize=9, color=MORADO, fontweight="bold")
# barra paralela MLOps (preparación de datos HIS, Sprints 4-5)
yy = y(len(sprints))
x0 = mdates.date2num(date(2026,10,13)); w = mdates.date2num(date(2026,11,10)) - x0
ax.add_patch(FancyBboxPatch((x0, yy - 0.3), w, 0.6, boxstyle="round,pad=0,rounding_size=1.2",
                            facecolor=AMBAR, edgecolor="white", linewidth=2, mutation_aspect=0.05, hatch=None))
ax.text(x0 + w/2, yy + 0.02, "MLOps · Datos HIS", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
ax.text(x0 + w/2, yy - 0.5, "Perfilado, limpieza y versionado del dataset (en paralelo a INC-3 e INC-4)", ha="center", fontsize=8.6, color=TXT)

MES = {9: "set", 10: "oct", 11: "nov", 12: "dic"}
etiquetas = [f"{s[0]}\n{s[1].day:02d} {MES[s[1].month]} – {s[2].day:02d} {MES[s[2].month]}" for s in sprints] + ["Actividad\nparalela MLOps"]
ax.set_yticks([y(i) for i in range(filas)]); ax.set_yticklabels(etiquetas, fontsize=9.5, color=TXT)
ax.set_ylim(0.2, filas + 1.1)
ax.set_xlim(mdates.date2num(date(2026,8,29)), mdates.date2num(date(2026,12,24)))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.TU, interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.TU))
ax.tick_params(axis="x", labelsize=9, colors=GRIS); ax.tick_params(axis="y", length=0)
ax.grid(axis="x", which="both", color="#E3E8EE", linewidth=0.8); ax.set_axisbelow(True)
for s in ["top", "right", "left"]: ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#B8C2CC")
hoy = mdates.date2num(date(2026,9,29))
ax.axvline(hoy, color="#B0222B", linestyle="--", linewidth=1.2)
ax.text(hoy, filas + 0.95, "Hoy · 29/09 (PMV entregado en H1)", color="#B0222B", fontsize=9, ha="left", va="top")
ax.set_title("Cronograma del proyecto — 8 Sprints de 2 semanas (01/09/2026 – 21/12/2026)", fontsize=16, fontweight="bold", color="#14355C", loc="left", pad=16)
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=AZUL, label="Sprint / incremento de software"), Patch(color=AMBAR, label="Actividad MLOps en paralelo"),
                   Line2D([0],[0], marker="D", color="w", markerfacecolor=MORADO, markersize=11, label="Hito (fin de sprint)")],
          loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=3, frameon=False, fontsize=10)
plt.tight_layout(); plt.savefig("V1_gantt.png", facecolor="white"); print("ok")
