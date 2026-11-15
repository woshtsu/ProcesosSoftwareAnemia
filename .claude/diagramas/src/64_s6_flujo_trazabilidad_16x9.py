"""Variante 16:9 de la fig. 64 para la diapositiva 7: fila de ejemplo HU-01 (Tabla 30, fila 1) en 8 tarjetas."""
from _fig import *

W, H = 11, 6.19
fig, ax = nuevo(W, H)
texto(ax, W / 2, 0.3, "Trazabilidad del PMV: del problema al indicador de valor (ejemplo HU-01)", fs=19, fontweight="bold")
tarjetas = [
    ("1 Problema\nOrg.", "B1: triple registro\nsin identidad\núnica"),
    ("2 Proceso\nTO-BE", "M1: registro\nnominal único y\ndeduplicado"),
    ("3 Modelo\nAdaptado", "Iterativo-\nincremental\ncon Scrum"),
    ("4 Categoría/\nActividad", "Principal:\nrequisitos y\nconstrucción"),
    ("5 Decisión\nArquitectura", "ADR-001 hexagonal\nADR-003\nUNIQUE(dni)"),
    ("6 Caso\nPrueba", "CP-13 a CP-32\n(incluye duplicado\n409)"),
    ("7 PMV\nEntregado", "HU-01: POST\n/api/ninos y\nregistro en PWA"),
    ("8 Indicador\nValor", "Registros por\nevaluación:\n3 → 1 (sintético)"),
]
m, g = 0.2, 0.28
cw = (W - 2 * m - 3 * g) / 4
for k, (tit, cuerpo) in enumerate(tarjetas):
    f, c = divmod(k, 4)
    x, y = m + c * (cw + g), 0.8 + f * 2.45
    fc = "#E4F1EA" if k == 7 else "#E6EEF7"
    caja(ax, x, y, cw, 2.1, cuerpo, fc, fs=17, titulo=tit, tfs=17)
    if c < 3:
        flecha(ax, (x + cw, y + 1.05), (x + cw + g, y + 1.05), lw=2.2)
flecha(ax, (W - m - cw / 2, 0.8 + 2.1), (m + cw / 2, 0.8 + 2.45), lw=2.2)
texto(ax, W / 2, 5.78, "Filas 6 a 8 de la Tabla 30 (INC-2 a INC-6): por definir, sin resultados medidos.", fs=15, color=SUAVE)
texto(ax, W / 2, 6.03, "Fuente: elaboración propia (Tabla 30). Datos sintéticos.", fs=11, color=SUAVE)
guardar(fig, ax, "64_s6_flujo_trazabilidad_16x9")
