#!/usr/bin/env python3
"""
VIS-008: Cobertura de código por módulo
Fuente: pmv_fastapi/docs/evidencias/cobertura.txt
Umbral DoD: 80%
Total: 99% (641 sentencias declaradas en el tag v1.0-PMV; 548 reproducidas el
01/10/2026 con 99,07 %, 2 sin cubrir; 98 ramas, 4 parciales). Ver DATOS §17.
"""

import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 8), dpi=100)

# Datos de cobertura por módulo (de cobertura.txt)
modulos = [
    'api.py',
    'esquemas.py',
    'memoria.py',
    'sqlalchemy_repo.py',
    'casos_uso.py',
    'puertos.py',
    'entidades.py',
    'errores.py',
    'reglas_clinicas.py',
    'main.py'
]

cobertura = [100, 100, 100, 97, 100, 100, 99, 100, 100, 100]

# Colores: verde si >= 80%, rojo si < 80%
colores = ['#4CAF50' if c >= 80 else '#FF6B6B' for c in cobertura]

# Gráfico de barras horizontal
y_pos = np.arange(len(modulos))
bars = ax.barh(y_pos, cobertura, color=colores, alpha=0.8, edgecolor='black', linewidth=1)

# Línea vertical en el umbral del DoD (80%)
ax.axvline(x=80, color='red', linestyle='--', linewidth=2, label='Umbral DoD (80%)')

# Etiquetas y valores
ax.set_yticks(y_pos)
ax.set_yticklabels(modulos, fontsize=10)
ax.set_xlabel('Cobertura (%)', fontsize=11, fontweight='bold')
ax.set_title('Cobertura de Código por Módulo — PMV FastAPI\n'
             'Total: 99 % · 548 sentencias reproducidas el 01/10/2026 (641 declaradas en el tag) · 98 ramas',
             fontsize=13, fontweight='bold', pad=34)
ax.set_xlim(0, 105)

# Agregar valores en las barras
for i, (bar, val) in enumerate(zip(bars, cobertura)):
    ax.text(val + 1.5, bar.get_y() + bar.get_height()/2, f'{val}%',
            va='center', fontsize=9, fontweight='bold')

# Leyenda
ax.legend(loc='lower right', bbox_to_anchor=(1.0, 1.0), fontsize=10, frameon=False)

# Grid
ax.grid(axis='x', alpha=0.3, linestyle=':')

# Nota al pie
footer = (
    'Fuente: pmv_fastapi/docs/evidencias/cobertura.txt (tag) y verificacion_s6_2026-10-01.md (reproducción: 99,07 %)\n'
    'Medición con pytest-cov; umbral configurado en pyproject.toml: fail_under=80'
)
fig.text(0.5, 0.01, footer, ha='center', fontsize=8,
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('diagramas/png/60_s6_cobertura.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.savefig('diagramas/svg/60_s6_cobertura.svg', format='svg', bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("60_s6_cobertura creada (PNG + SVG)")
plt.close()
