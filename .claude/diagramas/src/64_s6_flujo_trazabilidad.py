"""Fig. 34 (informe): matriz de trazabilidad con las 8 columnas de la consigna y 2 filas de ejemplo (N-06).
Fuente de datos: Tabla 30 del informe, filas 1 (HU-01) y 5 (HU-05); rangos de CP de la Tabla 23.
Cifras: 3 -> 1 registros (sintético); p95 reporte 2 200 -> 74 ms; p95 agregado 58 ms."""
from _fig import *

W, H, fs = 9.6, 5.4, 12.5
fig, ax = nuevo(W, H)
texto(ax, W / 2, 0.3, "Matriz de trazabilidad integral: dos filas de ejemplo del PMV entregado", fs=15, fontweight="bold")
cols = ["Problema\nOrg.", "Proceso\nTO-BE", "Modelo\nAdaptado", "Categoría/\nActividad",
        "Decisión\nArquitectura", "Caso\nPrueba", "PMV\nEntregado", "Indicador\nValor"]
f1 = ["B1: triple\nregistro sin\nidentidad\núnica", "M1: registro\nnominal único\ny deduplicado",
      "Iterativo-\nincremental\ncon Scrum\n(Sprints 1-2)", "Principal:\nrequisitos,\nconstrucción",
      "ADR-001\nhexagonal;\nADR-003\nUNIQUE(dni)", "CP-13 a\nCP-32\n(incluye el\nduplicado 409)",
      "HU-01:\nPOST\n/api/ninos y\nregistro PWA", "Registros por\nevaluación:\n3 → 1\n(sintético)"]
f5 = ["B6: datos\nconsolidados\ntarde", "M6 parcial:\nreporte del\nperiodo",
      "DevOps:\nmedición y\ncorrección\ncontinua", "Soporte:\nresolución\nde problemas",
      "ADR-006\n(DEF-01);\nzona UTC-5\n(DEF-02)", "CP-14 a\nCP-16, E2E\nde reporte,\nLocust",
      "HU-05: GET\n/api/reportes\n/periodo\n(JSON y CSV)", "p95 reporte:\n2 200 → 74 ms\n(agregado\n58 ms)"]
m = 0.1
cw = (W - 2 * m) / 8
for i, c in enumerate(cols):
    caja(ax, m + i * cw, 0.65, cw - 0.06, 0.7, c, "#2F5D8A", "#1F4266", fs=fs - 0.5, bold=True, color="white")
for r, (fila, y, fc) in enumerate([(f1, 1.45, "#E6EEF7"), (f5, 3.0, "#E4F1EA")]):
    for i, t in enumerate(fila):
        caja(ax, m + i * cw, y, cw - 0.06, 1.45, t, fc, "#9AA6B2", fs=fs, lw=1.0)
caja(ax, m, 4.52, W - 2 * m - 0.06, 0.42,
     "Filas 6 a 8 (INC-2 a INC-6): por definir; sin resultados medidos", "#FFFFFF", "#6B7785",
     fs=12.5, dash=True, color=SUAVE)
texto(ax, W / 2, 5.17, "Muestra: filas 1 y 5 de la Tabla 30; rangos de CP según la Tabla 23. Datos sintéticos. "
      "Fuente: elaboración propia (Tabla 30).", fs=9.5, color=SUAVE)
guardar(fig, ax, "64_s6_flujo_trazabilidad")
