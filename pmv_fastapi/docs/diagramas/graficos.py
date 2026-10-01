import csv, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "DejaVu Sans"
AZUL, AMBAR, MORADO, TXT, GRIS, VERDE, ROJO = "#2E6FB2", "#D08A00", "#7B3F98", "#1B2B3A", "#5E6E7E", "#1F7A3D", "#B0222B"
def limpiar(ax):
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#B8C2CC"); ax.spines["bottom"].set_color("#B8C2CC")
    ax.tick_params(colors=GRIS)

# 1. Pirámide de pruebas
fig, ax = plt.subplots(figsize=(9, 5.6), dpi=170)
niveles = [("Unitarias (dominio y casos de uso)", 62, AZUL, "Pytest · adaptador en memoria · < 1 s"),
           ("Integración / API", 11, VERDE, "TestClient + SQLite y PostgreSQL 16"),
           ("UI / E2E", 4, MORADO, "Playwright (Chromium)"),
           ("Rendimiento / carga", 1, AMBAR, "Locust: 50 usuarios · 60 s")]
anchos = [1.0, 0.72, 0.46, 0.24]
for i, ((nom, n, c, det), w) in enumerate(zip(niveles, anchos)):
    y = i
    ax.fill([0.5-w/2, 0.5+w/2, 0.5+anchos[i+1]/2 if i+1 < 4 else 0.5+0.06, 0.5-anchos[i+1]/2 if i+1 < 4 else 0.5-0.06],
            [y, y, y+0.92, y+0.92], color=c, edgecolor="white", linewidth=2)
    ax.text(0.5, y+0.52, f"{n}", ha="center", va="center", color="white", fontsize=17 if i < 3 else 12, fontweight="bold")
    ax.text(0.5+w/2+0.03, y+0.58, nom, ha="left", va="center", fontsize=11, color=TXT, fontweight="bold")
    ax.text(0.5+w/2+0.03, y+0.28, det, ha="left", va="center", fontsize=9.5, color=GRIS)
ax.set_xlim(-0.02, 1.55); ax.set_ylim(-0.1, 4.1); ax.axis("off")
ax.set_title("Pirámide de pruebas del PMV — 77 casos automatizados + 1 escenario de carga", fontsize=13, fontweight="bold", color="#14355C", loc="left")
plt.tight_layout(); plt.savefig("G1_piramide_pruebas.png", facecolor="white"); plt.close()

# 2. Cobertura por módulo
mods = [("dominio/reglas_clinicas", 100), ("dominio/entidades", 99), ("dominio/errores", 100), ("aplicación/casos_uso", 100),
        ("aplicación/puertos", 100), ("entrada/http/api", 100), ("entrada/http/esquemas", 100),
        ("salida/sqlalchemy_repo", 97), ("salida/memoria", 100), ("main (composición)", 100)]
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=170)
nombres = [m[0] for m in mods][::-1]; vals = [m[1] for m in mods][::-1]
b = ax.barh(nombres, vals, color=AZUL, height=0.62, edgecolor="white")
for r, v in zip(b, vals): ax.text(v - 1.2, r.get_y()+r.get_height()/2, f"{v} %", va="center", ha="right", color="white", fontsize=9.5, fontweight="bold")
ax.axvline(80, color=ROJO, linestyle="--", linewidth=1.3); ax.text(80.5, len(mods)-0.35, "Umbral DoD 80 %", color=ROJO, fontsize=9.5)
ax.set_xlim(0, 104); ax.set_xlabel("Cobertura de líneas y ramas (%)", color=GRIS); limpiar(ax)
ax.tick_params(axis="y", colors=TXT, labelsize=10)
ax.set_title("Cobertura por módulo — total 99 % (líneas 99,7 % · ramas 95,9 %)", fontsize=11.5, fontweight="bold", color="#14355C", loc="left")
plt.tight_layout(); plt.savefig("G2_cobertura.png", facecolor="white"); plt.close()

# 3. Carga antes / después DEF-01
def leer(p):
    d = {}
    for r in csv.DictReader(open(p)):
        d[r["Name"]] = (float(r["95%"]), float(r["Requests/s"]), int(r["Failure Count"]))
    return d
A = leer("../evidencias/carga/linea_base_antes_DEF-01_stats.csv")
D = leer("../evidencias/carga/despues_DEF-01_stats.csv")
ends = [("GET /api/reportes/periodo", "Reporte del periodo"), ("GET /api/ninos", "Listar seguimiento"), ("GET /api/ninos/{id}", "Abrir expediente"),
        ("POST /api/ninos", "Registrar niño"), ("POST /api/validaciones/evaluacion", "Vista previa HU-03"), ("Aggregated", "Agregado")]
import numpy as np
fig, ax = plt.subplots(figsize=(10, 5.4), dpi=170)
x = np.arange(len(ends)); w = 0.36
va = [A[e][0] for e,_ in ends]; vd = [D[e][0] for e,_ in ends]
ba = ax.bar(x - w/2 - 0.01, va, w, color="#9DB7D5", label="Línea base (con DEF-01)", edgecolor="white")
bd = ax.bar(x + w/2 + 0.01, vd, w, color=AZUL, label="Después de corregir DEF-01", edgecolor="white")
for r, v in list(zip(ba, va)) + list(zip(bd, vd)):
    ax.text(r.get_x()+r.get_width()/2, v + 25, f"{v:.0f}", ha="center", fontsize=9.5, color=TXT)
ax.set_xticks(x); ax.set_xticklabels([n for _, n in ends], fontsize=10, color=TXT)
ax.set_ylabel("Latencia p95 (ms)", color=GRIS); limpiar(ax); ax.grid(axis="y", color="#E3E8EE"); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=10, loc="upper right")
agg_a, agg_d = A["Aggregated"], D["Aggregated"]
ax.set_title(f"Prueba de carga (Locust · 50 usuarios · 60 s) — p95 agregado {agg_a[0]:.0f} → {agg_d[0]:.0f} ms · {agg_d[1]:.1f} req/s · 0 errores",
             fontsize=11.5, fontweight="bold", color="#14355C", loc="left")
plt.tight_layout(); plt.savefig("G3_carga.png", facecolor="white"); plt.close()
print(A["Aggregated"], D["Aggregated"])
