#!/usr/bin/env python3
"""Fig. 53 (variante panorámica para diapositiva, 11 x 4,3 in): C4 nivel 2 de contenedores del PMV FastAPI.
Mismos contenedores y relaciones que 53_s6_c4_contenedores_fastapi.puml; texto >= 16 pt.
Fuente: elaboración propia (§3.2 del informe)."""
import sys
sys.path.insert(0, __import__("pathlib").Path(__file__).parent.as_posix())
from _fig import nuevo, caja, flecha, texto, guardar, TINTA, SUAVE, BORDE
from matplotlib.patches import FancyBboxPatch

fig, ax = nuevo(11, 4.3)
FS = 16
texto(ax, 5.5, 0.25, "C4 nivel 2: contenedores del PMV FastAPI", fs=17, fontweight="bold")
ax.add_patch(FancyBboxPatch((2.45, 0.55), 8.5, 3.1, boxstyle="round,pad=0,rounding_size=0.1",
                            fc="white", ec=BORDE, lw=1.6, ls=(0, (6, 3))))
texto(ax, 6.7, 0.8, "Sistema de detección temprana de anemia", fs=FS, color=SUAVE)
caja(ax, 0.15, 1.05, 1.95, 1.1, "Personal\nde salud", fc="#DCE9F7", fs=FS)
caja(ax, 0.15, 2.4, 1.95, 1.1, "Gestión\nterritorial", fc="#DCE9F7", fs=FS)
caja(ax, 2.7, 1.05, 2.3, 1.25, "HTML, CSS, JS\nService Worker", fc="#EAF2FB", fs=FS, titulo="Cliente PWA")
caja(ax, 2.7, 2.5, 2.3, 1.05, "navegador:\nborrador y caché", fc="#E6F5EA", fs=FS, titulo="Almacenamiento")
caja(ax, 5.5, 1.05, 2.6, 1.25, "FastAPI, Python 3.11\nOpenAPI 3.1", fc="#EAF2FB", fs=FS, titulo="API REST")
caja(ax, 8.45, 1.05, 2.35, 1.25, "PostgreSQL 16\nSQLite (desarr.)", fc="#E6F5EA", fs=FS, titulo="Base de datos")
caja(ax, 5.5, 3.8, 2.6, 0.45, "GitHub Actions · CI/CD", fc="#F0F0F0", fs=FS, bold=True)
flecha(ax, (2.1, 1.4), (2.7, 1.6)); flecha(ax, (2.1, 3.0), (2.7, 2.1))
flecha(ax, (3.85, 2.3), (3.85, 2.5))
flecha(ax, (5.0, 1.675), (5.5, 1.675)); flecha(ax, (8.1, 1.675), (8.45, 1.675))
flecha(ax, (6.8, 3.8), (6.8, 2.3), dash=True)
texto(ax, 0.15, 4.0, "Fuente: elaboración propia (§3.2)", fs=FS, ha="left", color=SUAVE)
texto(ax, 9.1, 3.0, "Monolito modular\nsin gateway", fs=FS, color=SUAVE)
guardar(fig, ax, "53_s6_c4_contenedores_fastapi_16x9")
