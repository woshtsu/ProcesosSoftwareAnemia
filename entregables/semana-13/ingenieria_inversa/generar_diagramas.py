"""Ingeniería inversa de pmv_fastapi/app: genera el modelo de datos y el diagrama de componentes.

Uso (desde la raíz del repositorio, con las dependencias de pmv_fastapi instaladas y Graphviz):

    python entregables/semana-13/ingenieria_inversa/generar_diagramas.py

Salida en entregables/semana-13/img/:
- D01_modelo_datos_v4.dot / .png: tablas, columnas, claves y restricciones UNIQUE leídas de
  Base.metadata (modelos SQLAlchemy del adaptador de persistencia).
- D02_componentes_v4.dot / .png: paquetes de app/ y número de importaciones entre ellos,
  contadas con el módulo ast sobre el código fuente (no se ejecuta el código).
"""
from __future__ import annotations

import ast
import subprocess
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
APP = RAIZ / 'pmv_fastapi' / 'app'
SALIDA = RAIZ / 'entregables' / 'semana-13' / 'img'
AZUL = '#1F4E79'


def _tipo(col) -> str:
    try:
        nombre = col.type.compile().lower()
    except Exception:  # tipos sin dialecto por defecto (JSON)
        nombre = type(col.type).__name__.lower()
    nombre = nombre.split('(')[0]
    return nombre + ('' if col.nullable else ' NOT NULL')


def modelo_datos() -> str:
    sys.path.insert(0, str(RAIZ / 'pmv_fastapi'))
    from app.adapters.outbound.persistence.sqlalchemy_repo import Base  # noqa: PLC0415

    lineas = [
        'digraph ERD {',
        'graph [rankdir=LR, splines=spline, nodesep=0.5, ranksep=0.9, fontname="DejaVu Sans", bgcolor="white", '
        'label="Modelo de datos de v4.0-Inc4 obtenido por ingeniería inversa de los modelos SQLAlchemy '
        '(app/adapters/outbound/persistence/sqlalchemy_repo.py)", labelloc=t, fontsize=16];',
        'node [shape=plaintext, fontname="DejaVu Sans", fontsize=10];',
        f'edge [color="{AZUL}", arrowhead=crow, arrowtail=none, fontsize=9, fontname="DejaVu Sans"];',
    ]
    relaciones = []
    for tabla in Base.metadata.sorted_tables:
        filas = [f'<tr><td bgcolor="{AZUL}" colspan="3"><font color="white"><b>{tabla.name}</b></font></td></tr>']
        for col in tabla.columns:
            marca = 'PK' if col.primary_key else ('FK' if col.foreign_keys else '')
            celda = f'<font color="#a12020">{marca}</font>' if marca else ' '
            filas.append(
                f'<tr><td align="left">{celda}</td>'
                f'<td align="left" port="{col.name}">{col.name}</td>'
                f'<td align="left"><font color="#555555">{_tipo(col)}</font></td></tr>'
            )
            for fk in col.foreign_keys:
                relaciones.append((fk.column.table.name, tabla.name, col.name))
        for restr in tabla.constraints:
            if type(restr).__name__ == 'UniqueConstraint':
                cols = ','.join(c.name for c in restr.columns)
                filas.append(f'<tr><td align="left" colspan="3"><font color="#555555">UNIQUE ({cols})</font></td></tr>')
        cuerpo = ''.join(filas)
        lineas.append(f'"{tabla.name}" [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="3">{cuerpo}</table>>];')
    for origen, destino, columna in relaciones:
        lineas.append(f'"{origen}" -> "{destino}" [xlabel="{columna}"];')
    lineas.append('}')
    return '\n'.join(lineas)


def _paquete(modulo: str) -> str | None:
    partes = modulo.split('.')
    if partes[0] != 'app' or len(partes) < 2:
        return None
    if partes[1] == 'main':
        return 'main'
    if partes[1] in ('domain', 'ports') and len(partes) >= 3:
        return '.'.join(partes[1:3])
    if partes[1] == 'adapters' and len(partes) >= 4:
        return '.'.join(partes[1:4])
    return partes[1]


def componentes() -> str:
    modulos: Counter[str] = Counter()
    aristas: Counter[tuple[str, str]] = Counter()
    for archivo in sorted(APP.rglob('*.py')):
        rel = archivo.relative_to(APP.parent).with_suffix('')
        nombre = '.'.join(rel.parts).removesuffix('.__init__')
        origen = _paquete(nombre)
        if origen is None or origen in ('adapters', 'domain', 'ports'):  # __init__ de agrupación
            continue
        modulos[origen] += 1  # archivos .py, igual que la Tabla 26 del informe
        arbol = ast.parse(archivo.read_text(encoding='utf-8'))
        for nodo in ast.walk(arbol):
            destinos = []
            if isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.level == 0:
                destinos.append(nodo.module)
            elif isinstance(nodo, ast.Import):
                destinos.extend(a.name for a in nodo.names)
            for d in destinos:
                p = _paquete(d)
                if p and p != origen:
                    aristas[(origen, p)] += 1
    desc = {
        'application': 'casos de uso (servicios)',
        'domain.model': 'entidades y reglas puras',
        'domain.service': 'reglas clínicas, agenda,\\nalertas, visitas, conflictos',
        'ports.outbound': 'repositorios, reloj,\\nnotificador, identidad',
        'ports.inbound': 'interfaces de casos de uso',
        'main': 'raíz de composición',
        'adapters.inbound.http': 'FastAPI, esquemas, sesión, CSRF',
        'adapters.outbound.notificaciones': 'simulado, WhatsApp Cloud, SMS, respaldo',
        'adapters.outbound.persistence': 'SQLAlchemy (PostgreSQL/SQLite), memoria',
    }
    colores = {'domain.model': AZUL, 'domain.service': AZUL, 'ports.inbound': '#2E75B6',
               'ports.outbound': '#2E75B6', 'application': '#5B9BD5'}
    lineas = [
        'digraph C {',
        'graph [rankdir=LR, fontname="DejaVu Sans", label="Componentes de pmv_fastapi/app en v4.0-Inc4 '
        '(ingeniería inversa de las importaciones; número = importaciones entre paquetes)", labelloc=t, '
        'fontsize=15, compound=true, nodesep=0.4, ranksep=0.7];',
        'node [shape=box, style="rounded,filled", fontname="DejaVu Sans", fontsize=11, fontcolor=white];',
        'edge [fontname="DejaVu Sans", fontsize=10, color="#404040"];',
        f'subgraph cluster_hex {{ label="Hexágono (sin frameworks)"; style="rounded,dashed"; color="{AZUL}"; fontsize=12;',
    ]

    def nodo(p: str) -> str:
        n = modulos[p]
        titulo = p.replace('.', '/') if p != 'main' else 'main.py'
        texto = titulo + (f'\\n{desc[p]}' if p in desc else '') + f'\\n({n} módulo{"s" if n != 1 else ""})'
        if p in colores:
            return f'"{p}" [label="{texto}", fillcolor="{colores[p]}"];'
        relleno = '#7F7F7F' if p == 'main' else '#A5A5A5'
        return f'"{p}" [label="{texto}", fillcolor="{relleno}", fontcolor=black];'

    for p in [p for p in modulos if p in colores]:
        lineas.append(nodo(p))
    lineas.append('}')
    for p in [p for p in modulos if p not in colores]:
        lineas.append(nodo(p))
    lineas.append('"web" [label="web/ (PWA)\\nHTML, CSS, JS, service worker,\\ncola IndexedDB", fillcolor="#FFD966", fontcolor=black];')
    lineas.append('"web" -> "adapters.inbound.http" [label="HTTPS / JSON", style=dashed];')
    for (o, d), n in sorted(aristas.items()):
        lineas.append(f'"{o}" -> "{d}" [label="{n}"];')
    lineas.append('}')
    return '\n'.join(lineas)


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, generar in (('D01_modelo_datos_v4', modelo_datos), ('D02_componentes_v4', componentes)):
        dot = SALIDA / f'{nombre}.dot'
        dot.write_text(generar(), encoding='utf-8')
        subprocess.run(['dot', '-Tpng', '-Gdpi=110', str(dot), '-o', str(SALIDA / f'{nombre}.png')], check=True)
        print('generado', dot.with_suffix('.png'))


if __name__ == '__main__':
    main()
