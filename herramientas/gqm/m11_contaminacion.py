#!/usr/bin/env python
"""M1.1 Índice de contaminación del dominio (GQM G-01 / Q1.1).

    M1.1 = (n.º de importaciones de frameworks/librerías EXTERNAS en módulos de dominio)
           / (n.º total de clases de dominio) x 100

Recorre por AST la capa de dominio de cada versión (v1.0: app/domain; v1.5: app/domain/model y app/domain/service),
cuenta clases (ClassDef, incluidas las anidadas) y clasifica TODAS las importaciones en stdlib / interno / externo.
Cualquier módulo que no sea de la biblioteca estándar ni del propio paquete ``app`` cuenta como externo.
Como dato complementario calcula el mismo índice para la capa de puertos/aplicación.

Uso:  python herramientas/gqm/m11_contaminacion.py [--version v1.0|v1.5|ambas] [--json ruta]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import comun as c

CAPAS_EVALUADAS = ("dominio", "puertos_entrada", "puertos_salida", "aplicacion")


def medir_capa(version: str, capa: str) -> dict:
    raiz = c.RAICES[version]
    archivos = c.archivos_py(raiz, c.CAPAS[version][capa])
    imports, n_clases, detalle_clases = [], 0, []
    for a in archivos:
        imports += c.importaciones(raiz, a)
        cs = c.clases(a)
        n_clases += len(cs)
        detalle_clases += [f"{a.relative_to(raiz)}:{k.lineno} {k.name}" for k in cs]
    por_tipo = {t: [i for i in imports if i.tipo == t] for t in ("stdlib", "interno", "externo")}
    externos = por_tipo["externo"]
    indice = (len(externos) / n_clases * 100) if n_clases else None
    return {
        "capa": capa,
        "rutas": c.CAPAS[version][capa],
        "archivos": [str(a.relative_to(raiz)) for a in archivos],
        "n_clases": n_clases,
        "clases": detalle_clases,
        "n_importaciones": len(imports),
        "n_stdlib": len(por_tipo["stdlib"]),
        "n_internas": len(por_tipo["interno"]),
        "n_externas": len(externos),
        "modulos_externos_distintos": sorted({i.raiz_modulo for i in externos}),
        "indice_contaminacion_pct": None if indice is None else round(indice, 2),
        "importaciones": [
            {"archivo": i.archivo, "linea": i.linea, "modulo": i.modulo, "tipo": i.tipo, "texto": i.texto}
            for i in imports
        ],
    }


def medir(version: str) -> dict:
    return {capa: medir_capa(version, capa) for capa in CAPAS_EVALUADAS}


def imprimir(version: str, res: dict) -> None:
    print(f"\n=== {c.ETIQUETA[version]}  (raíz: {c.RAICES[version]})")
    print(f"{'capa':<20}{'clases':>7}{'imports':>9}{'stdlib':>8}{'interno':>9}{'externo':>9}{'índice %':>10}")
    for capa, r in res.items():
        ind = "n/a" if r["indice_contaminacion_pct"] is None else f"{r['indice_contaminacion_pct']:.2f}"
        print(
            f"{capa:<20}{r['n_clases']:>7}{r['n_importaciones']:>9}{r['n_stdlib']:>8}{r['n_internas']:>9}"
            f"{r['n_externas']:>9}{ind:>10}"
        )
    d = res["dominio"]
    print(f"\nM1.1 ({version}) = {d['n_externas']} / {d['n_clases']} x 100 = {d['indice_contaminacion_pct']} %")
    print("Importaciones externas en dominio:", d["modulos_externos_distintos"] or "ninguna")
    print("Importaciones de dominio:")
    for i in d["importaciones"]:
        print(f"  [{i['tipo']:<7}] {i['archivo']}:{i['linea']}  {i['texto']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="ambas", choices=["v1.0", "v1.5", "ambas"])
    ap.add_argument("--json", default=str(c.DATOS / "m11_contaminacion.json"))
    a = ap.parse_args()
    versiones = ["v1.0", "v1.5"] if a.version == "ambas" else [a.version]
    salida = {}
    for v in versiones:
        salida[v] = medir(v)
        imprimir(v, salida[v])
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON: {a.json}")


if __name__ == "__main__":
    main()
