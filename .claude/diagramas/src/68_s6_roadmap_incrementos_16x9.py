"""Variante 16:9 de la fig. 68 (hoja de ruta) para la diapositiva 7.
Fuente de datos: Tablas 15 y 16 del informe (sprints 1 a 8, hitos H0 a H7, 01/09 a 21/12/2026). Solo INC-1 entregado."""
from _fig import *

W, H, fs = 11, 6.19, 16
fig, ax = nuevo(W, H)
texto(ax, W / 2, 0.28, "Hoja de ruta: Sprints 1 a 8 (01/09 a 21/12/2026); siguiente, INC-2", fs=18, fontweight="bold")
S = [("Sprint 1 · H0", "01–14/09", "INC-1:\nconstrucción"), ("Sprint 2 · H1", "15–28/09", "INC-1 entregado\nv1.0-PMV"),
     ("Sprint 3 · H2", "29/09–12/10", "INC-2: agenda y\nalertas + backlog\ntécnico"), ("Sprint 4 · H3", "13–26/10", "INC-3: sin conexión\ny sincronización"),
     ("Sprint 5 · H4", "27/10–09/11", "INC-4: mensajería\ny barreras"), ("Sprint 6 · H5", "10–23/11", "INC-5: datos y\nentrenamiento"),
     ("Sprint 7 · H6", "24/11–07/12", "INC-5: integración;\nINC-6: inicio"), ("Sprint 8 · H7", "08–21/12", "INC-6: tablero\nterritorial")]
m, g = 0.2, 0.28
cw = (W - 2 * m - 3 * g) / 4
for k, (t, d, b) in enumerate(S):
    f, c = divmod(k, 4)
    x, y = m + c * (cw + g), 0.8 + f * 2.45
    if k < 2:
        fc, ec, dash = "#CDEBD6", "#2E6B4E", False
    elif k == 2:
        fc, ec, dash = "#FFE8C2", "#B26B00", False
    else:
        fc, ec, dash = "#FFFFFF", "#4A5A6A", True
    caja(ax, x, y, cw, 2.1, d + "\n" + b, fc, ec, fs=fs, titulo=t, tfs=17, dash=dash)
    if c < 3:
        flecha(ax, (x + cw, y + 1.05), (x + cw + g, y + 1.05), lw=2.2)
flecha(ax, (W - m - cw / 2, 0.8 + 2.1), (m + cw / 2, 0.8 + 2.45), lw=2.2)
texto(ax, W / 2, 5.78, "Verde: entregado. Naranja: siguiente. Discontinuo: planificado, no entregado.", fs=15, color=SUAVE)
texto(ax, W / 2, 6.03, "Fuente: elaboración propia (Tablas 15 y 16).", fs=11, color=SUAVE)
guardar(fig, ax, "68_s6_roadmap_incrementos_16x9")
