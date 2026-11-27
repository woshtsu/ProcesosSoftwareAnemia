"""Reporte de ingeniería inversa de pmv_fastapi/app (equivalente propio a SciTools Understand).

Uso (desde cualquier carpeta):

    pmv_fastapi/.venv/Scripts/python.exe entregables/semana-15/ingenieria_inversa/reporte_ingenieria_inversa.py

Solo usa la biblioteca estándar (módulo ast). No ejecuta el código analizado.
Salidas en esta misma carpeta: metricas.json, metricas_archivos.csv, metricas_funciones.csv,
metricas_clases.csv, metricas_capas.csv, dependencias_paquetes.dot, img/dependencias_paquetes.svg
(y .png si existe Graphviz `dot`).
"""
from __future__ import annotations

import ast
import csv
import json
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
APP = RAIZ / 'pmv_fastapi' / 'app'
SALIDA = Path(__file__).resolve().parent
IMG = SALIDA / 'img'
ESTDLIB = set(sys.stdlib_module_names)
CAPAS = ['domain', 'ports', 'application', 'adapters', 'main']


def modulo_de(archivo: Path) -> str:
    rel = archivo.relative_to(APP.parent).with_suffix('')
    return '.'.join(rel.parts).removesuffix('.__init__')


def capa_de(modulo: str) -> str | None:
    p = modulo.split('.')
    return p[1] if p[0] == 'app' and len(p) > 1 else None


def paquete_de(modulo: str) -> str | None:
    """Paquete de granularidad media (el mismo criterio del diagrama D02 de la semana 13)."""
    p = modulo.split('.')
    if p[0] != 'app' or len(p) < 2:
        return None
    if p[1] == 'main':
        return 'main'
    if p[1] in ('domain', 'ports') and len(p) >= 3:
        return '.'.join(p[1:3])
    if p[1] == 'adapters' and len(p) >= 4:
        return '.'.join(p[1:4])
    return p[1]


def lineas_archivo(texto: str, arbol: ast.AST) -> dict:
    lineas = texto.splitlines()
    doc: set[int] = set()
    for n in ast.walk(arbol):
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.body:
            p = n.body[0]
            if isinstance(p, ast.Expr) and isinstance(p.value, ast.Constant) and isinstance(p.value.value, str):
                doc.update(range(p.lineno, p.end_lineno + 1))
    blanco = comentario = codigo = 0
    for i, linea in enumerate(lineas, 1):
        s = linea.strip()
        if not s:
            blanco += 1
        elif s.startswith('#') or i in doc:
            comentario += 1
        else:
            codigo += 1
    return {'total': len(lineas), 'codigo': codigo, 'comentarios': comentario, 'blanco': blanco}


def complejidad(fn: ast.AST) -> int:
    """Complejidad ciclomática aproximada de McCabe, sin contar funciones anidadas."""
    c = 1
    pila = list(ast.iter_child_nodes(fn))
    while pila:
        n = pila.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        if isinstance(n, (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)):
            c += 1
        elif isinstance(n, ast.BoolOp):
            c += len(n.values) - 1
        elif isinstance(n, ast.comprehension):
            c += 1 + len(n.ifs)
        elif isinstance(n, ast.match_case):
            c += 1
        pila.extend(ast.iter_child_nodes(n))
    return c


def atributos_clase(c: ast.ClassDef) -> set[str]:
    a: set[str] = set()
    for n in c.body:
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            a.add(n.target.id)
        elif isinstance(n, ast.Assign):
            a.update(t.id for t in n.targets if isinstance(t, ast.Name))
    for n in ast.walk(c):
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            objetivos = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in objetivos:
                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == 'self':
                    a.add(t.attr)
    return a


def imports(arbol: ast.AST, modulo: str, es_paquete: bool) -> list[str]:
    res = []
    base = modulo.split('.') if es_paquete else modulo.split('.')[:-1]
    for n in ast.walk(arbol):
        if isinstance(n, ast.Import):
            res.extend(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            if n.level == 0 and n.module:
                res.append(n.module)
            elif n.level > 0:
                b = base[: len(base) - (n.level - 1)]
                res.append('.'.join(b + ([n.module] if n.module else [])))
    return res


def analizar() -> dict:
    archivos, funciones, clases = [], [], []
    aristas_paq: Counter = Counter()
    matriz: Counter = Counter()
    terceros: dict[str, Counter] = defaultdict(Counter)
    violaciones = []
    for f in sorted(APP.rglob('*.py')):
        if '__pycache__' in f.parts:
            continue
        texto = f.read_text(encoding='utf-8')
        arbol = ast.parse(texto)
        mod = modulo_de(f)
        capa = capa_de(mod) or 'main'
        rel = f.relative_to(RAIZ).as_posix()
        cont = {'nf': 0, 'nm': 0}

        def visitar(nodo, clase=None):
            for h in ast.iter_child_nodes(nodo):
                if isinstance(h, ast.ClassDef):
                    visitar(h, h.name)
                elif isinstance(h, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    cont['nm' if clase else 'nf'] += 1
                    funciones.append({'archivo': rel, 'capa': capa, 'clase': clase or '', 'funcion': h.name,
                                      'linea': h.lineno, 'lineas': h.end_lineno - h.lineno + 1,
                                      'complejidad': complejidad(h)})
                    visitar(h, None)
                else:
                    visitar(h, clase)

        visitar(arbol)
        nc = 0
        for n in ast.walk(arbol):
            if isinstance(n, ast.ClassDef):
                nc += 1
                metodos = [m for m in n.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                clases.append({'archivo': rel, 'capa': capa, 'clase': n.name,
                               'bases': ';'.join(ast.unparse(b) for b in n.bases),
                               'metodos': len(metodos), 'atributos': len(atributos_clase(n)),
                               'lineas': n.end_lineno - n.lineno + 1})
        archivos.append({'archivo': rel, 'capa': capa, 'modulo': mod, **lineas_archivo(texto, arbol),
                         'clases': nc, 'funciones': cont['nf'], 'metodos': cont['nm']})
        origen = paquete_de(mod)
        for d in imports(arbol, mod, f.name == '__init__.py'):
            raiz = d.split('.')[0]
            if raiz == 'app':
                capa_d = capa_de(d) or 'main'
                if capa_d != capa:
                    matriz[(capa, capa_d)] += 1
                dp = paquete_de(d)
                if origen and dp and origen != dp and origen not in ('adapters', 'domain', 'ports'):
                    aristas_paq[(origen, dp)] += 1
                if capa == 'domain' and capa_d in ('adapters', 'application', 'main'):
                    violaciones.append({'archivo': rel, 'import': d, 'regla': 'domain no importa adapters/application/main'})
                if capa == 'ports' and capa_d == 'adapters':
                    violaciones.append({'archivo': rel, 'import': d, 'regla': 'ports no importa adapters'})
            elif raiz not in ESTDLIB and raiz != '__future__':
                terceros[capa][raiz] += 1
                if capa == 'domain':
                    violaciones.append({'archivo': rel, 'import': d, 'regla': 'domain no importa frameworks ni terceros'})
    return {'archivos': archivos, 'funciones': funciones, 'clases': clases, 'matriz': matriz,
            'aristas_paq': aristas_paq, 'terceros': terceros, 'violaciones': violaciones}


def por_capa(archivos, funciones) -> list[dict]:
    res = []
    for capa in CAPAS:
        a = [x for x in archivos if x['capa'] == capa]
        cx = [x['complejidad'] for x in funciones if x['capa'] == capa]
        res.append({'capa': capa, 'archivos': len(a),
                    **{k: sum(x[k] for x in a) for k in ('total', 'codigo', 'comentarios', 'blanco', 'clases', 'funciones', 'metodos')},
                    'complejidad_media': round(sum(cx) / len(cx), 2) if cx else 0,
                    'complejidad_max': max(cx) if cx else 0})
    return res


def escribir_csv(nombre: str, filas: list[dict]) -> None:
    with open(SALIDA / nombre, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)


def diagrama(aristas: Counter, paquetes: Counter) -> list[str]:
    nivel = {'main': 0, 'application': 2, 'ports.inbound': 3, 'ports.outbound': 3,
             'domain.service': 4, 'domain.model': 5}
    color = {0: '#7F7F7F', 1: '#A5A5A5', 2: '#5B9BD5', 3: '#2E75B6', 4: '#1F4E79', 5: '#1F4E79'}
    nodos = sorted(paquetes, key=lambda p: (nivel.get(p, 1), p))
    filas: dict[int, list[str]] = defaultdict(list)
    for p in nodos:
        filas[nivel.get(p, 1)].append(p)
    W, H, bw, bh = 1100, 660, 210, 46
    pos = {}
    for nv, ps in filas.items():
        for i, p in enumerate(ps):
            pos[p] = ((W / (len(ps) + 1)) * (i + 1), 60 + nv * 105)
    dot = ['digraph D {', 'rankdir=TB; node [shape=box, style="rounded,filled", fontcolor=white, fontname="Helvetica"];']
    for p in nodos:
        dot.append(f'"{p}" [label="{p}\\n({paquetes[p]} módulos)", fillcolor="{color[nivel.get(p, 1)]}"];')
    for (o, d), n in sorted(aristas.items()):
        dot.append(f'"{o}" -> "{d}" [label="{n}"];')
    dot.append('}')
    (SALIDA / 'dependencias_paquetes.dot').write_text('\n'.join(dot), encoding='utf-8')
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
         '<defs><marker id="f" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#404040"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         '<text x="10" y="22" font-size="15" font-weight="bold">Dependencias entre paquetes de pmv_fastapi/app (numero = importaciones)</text>']
    for (o, d), n in sorted(aristas.items()):
        if o not in pos or d not in pos:
            continue
        (x1, y1), (x2, y2) = pos[o], pos[d]
        if y2 > y1:
            y1 += bh / 2
            y2 -= bh / 2
        elif y2 < y1:
            y1 -= bh / 2
            y2 += bh / 2
        else:
            sg = 1 if x2 > x1 else -1
            x1 += bw / 2 * sg
            x2 -= bw / 2 * sg
        rojo = (o.startswith('domain') and not d.startswith('domain')) or (o.startswith('ports') and d.startswith('adapters'))
        c = '#C00000' if rojo else '#404040'
        s.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{c}" stroke-width="1.2" marker-end="url(#f)" opacity="0.7"/>')
        s.append(f'<text x="{(x1 + x2) / 2 + 4:.0f}" y="{(y1 + y2) / 2:.0f}" font-size="11" fill="{c}">{n}</text>')
    for p in nodos:
        x, y = pos[p]
        fc = 'black' if nivel.get(p, 1) == 1 else 'white'
        s.append(f'<rect x="{x - bw / 2:.0f}" y="{y - bh / 2:.0f}" width="{bw}" height="{bh}" rx="8" fill="{color[nivel.get(p, 1)]}"/>')
        s.append(f'<text x="{x:.0f}" y="{y - 3:.0f}" text-anchor="middle" font-size="12" font-weight="bold" fill="{fc}">{p}</text>')
        s.append(f'<text x="{x:.0f}" y="{y + 13:.0f}" text-anchor="middle" font-size="11" fill="{fc}">{paquetes[p]} modulos</text>')
    s.append('</svg>')
    IMG.mkdir(exist_ok=True)
    (IMG / 'dependencias_paquetes.svg').write_text('\n'.join(s), encoding='utf-8')
    salidas = ['img/dependencias_paquetes.svg']
    if shutil.which('dot'):
        subprocess.run(['dot', '-Tpng', '-Gdpi=110', str(SALIDA / 'dependencias_paquetes.dot'),
                        '-o', str(IMG / 'dependencias_paquetes.png')], check=True)
        salidas.append('img/dependencias_paquetes.png')
    return salidas


def main() -> None:
    r = analizar()
    A, F, C = r['archivos'], r['funciones'], r['clases']
    capas = por_capa(A, F)
    paquetes = Counter(paquete_de(a['modulo']) for a in A if paquete_de(a['modulo']) not in (None, 'adapters', 'domain', 'ports'))
    salidas = diagrama(r['aristas_paq'], paquetes)
    cx = [f['complejidad'] for f in F]
    top = sorted(F, key=lambda f: -f['complejidad'])[:10]
    tot = {k: sum(a[k] for a in A) for k in ('total', 'codigo', 'comentarios', 'blanco', 'clases', 'funciones', 'metodos')}
    matriz = {o: {d: r['matriz'].get((o, d), 0) for d in CAPAS} for o in CAPAS}
    resumen = {
        'carpeta': 'pmv_fastapi/app', 'archivos': len(A), 'totales': tot,
        'funciones_y_metodos': len(F), 'complejidad_media': round(sum(cx) / len(cx), 2), 'complejidad_max': max(cx),
        'funciones_complejidad_mayor_10': sum(1 for c in cx if c > 10),
        'top10': top, 'por_capa': capas, 'matriz_capas': matriz,
        'terceros_por_capa': {k: dict(v.most_common()) for k, v in r['terceros'].items()},
        'violaciones_hexagonales': r['violaciones'], 'num_violaciones': len(r['violaciones']),
        'aristas_paquetes': {f'{o} -> {d}': n for (o, d), n in sorted(r['aristas_paq'].items())},
        'paquetes': dict(paquetes), 'clases_top_metodos': sorted(C, key=lambda c: -c['metodos'])[:10],
        'imagenes': salidas, 'graphviz_disponible': bool(shutil.which('dot')),
    }
    (SALIDA / 'metricas.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding='utf-8')
    escribir_csv('metricas_archivos.csv', A)
    escribir_csv('metricas_funciones.csv', F)
    escribir_csv('metricas_clases.csv', C)
    escribir_csv('metricas_capas.csv', capas)
    print(json.dumps({k: resumen[k] for k in ('archivos', 'totales', 'funciones_y_metodos', 'complejidad_media',
                                               'complejidad_max', 'num_violaciones', 'imagenes')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
