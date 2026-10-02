"""Variante 16:9 de la fig. 1/50 (AS-IS vs TO-BE) para la diapositiva 1.
Fuente de datos: Tablas 4 (brechas B1-B6) y 5 (mejoras M1-M6 e incrementos) del informe. Solo M1 entregada."""
from _fig import *

W, H, fs = 11, 6.19, 16
fig, ax = nuevo(W, H)
texto(ax, W / 2, 0.28, "Proceso actual (AS-IS reactivo) frente al propuesto (TO-BE preventivo)", fs=18, fontweight="bold")
texto(ax, 0.15 + 2.4, 0.72, "AS-IS: brechas (Tabla 4)", fs=15, fontweight="bold")
texto(ax, 6.05 + 2.4, 0.72, "TO-BE: mejoras (Tabla 5)", fs=15, fontweight="bold")
B = ["B1: triple registro manual", "B2: agenda de controles\ncalculada a mano", "B3: barreras ocultas\nhasta el abandono",
     "B4: visita en papel,\nsin conexión", "B5: riesgo detectado\ncuando ya hubo abandono", "B6: cobertura intermitente\ny consolidación tardía"]
M = ["M1: registro nominal único\nINC-1 · entregado", "M2: agenda de controles\nINC-2", "M3: recordatorio y barreras\nINC-4",
     "M4: visita priorizada\nINC-3", "M5: riesgo explicable\nINC-5", "M6: captura local e indicadores\nINC-3 e INC-6 (parcial)"]
for i in range(6):
    y = 0.95 + i * 0.72
    caja(ax, 0.15, y, 4.8, 0.62, B[i], "#FDE3E1", "#9E3A30", fs=fs)
    entregado = i == 0
    caja(ax, 6.05, y, 4.8, 0.62, M[i], "#CDEBD6" if entregado else "#FFFFFF", "#2E6B4E" if entregado else "#4A5A6A",
         fs=fs, dash=not entregado)
    flecha(ax, (4.95, y + 0.31), (6.05, y + 0.31), lw=2.2)
caja(ax, 0.15, 5.27, 10.7, 0.5, "Indicador de valor (datos sintéticos): 3 registros por evaluación → 1 expediente único",
     "#E4F1EA", "#2E6B4E", fs=fs, bold=True)
texto(ax, W / 2, 5.98, "Trazo continuo: entregado (M1). Discontinuo: planificado. Fuente: elaboración propia (Tablas 4 y 5).", fs=11, color=SUAVE)
guardar(fig, ax, "50_s6_as_is_vs_to_be_16x9")
