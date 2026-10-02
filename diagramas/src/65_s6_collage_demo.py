#!/usr/bin/env python3
"""Fig. 65: collage de capturas de la demo del PMV (incluye el panel HU-04).
Fuente: pmv_fastapi/docs/evidencias/capturas/ (datos sintéticos)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "pmv_fastapi/docs/evidencias/capturas"
paneles = [
    ("01_registro_vista_previa.png", "HU-01: registro con vista previa"),
    ("02_validacion_datos_invalidos.png", "HU-03: validación de datos inválidos"),
    ("05_expediente_evolucion.png", "HU-02: expediente y evolución"),
    ("04_seguimiento.png", "HU-04: lista de niños en seguimiento"),
    ("06_reporte_periodo.png", "HU-05: reporte del periodo"),
]
fig, axs = plt.subplots(2, 3, figsize=(18, 10.125))
fig.suptitle("Demostración del PMV FastAPI: interfaz de usuario (HU-01 a HU-05)", fontsize=16, fontweight="bold")
for ax, (archivo, rotulo) in zip(axs.flat, paneles):
    ax.imshow(Image.open(DIR / archivo))
    ax.set_title(rotulo, fontsize=12, fontweight="bold", pad=6)
    ax.axis("off")
ax = axs.flat[5]; ax.axis("off")
ax.text(0.0, 0.85, "Qué muestra el collage", fontsize=12, fontweight="bold", va="top")
ax.text(0.0, 0.72, "HU-01 y HU-03: registro, vista previa\ny rechazo comprensible por campo.\n\n"
        "HU-02: expediente con evolución\nde dosajes.\n\nHU-04: seguimiento con estado de\ncontrol.\n\n"
        "HU-05: reporte del periodo (JSON y CSV).\n\nTodos los datos son sintéticos.",
        fontsize=11, va="top", linespacing=1.3)
fig.text(0.5, 0.01, "Fuente: elaboración propia (Tabla 29). Datos sintéticos.",
         ha="center", fontsize=9.5, color="#4A5A6A")
fig.subplots_adjust(top=0.90, bottom=0.04, left=0.02, right=0.98, hspace=0.12, wspace=0.08)
fig.savefig(RAIZ / "diagramas/png/65_s6_collage_demo.png", dpi=150, facecolor="white")
fig.savefig(RAIZ / "diagramas/svg/65_s6_collage_demo.svg", format="svg", facecolor="white")
print("65 OK")
