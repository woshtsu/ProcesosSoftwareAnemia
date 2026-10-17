#!/usr/bin/env python
"""Acoplamiento eferente/aferente por capa (complemento de G-01), calculado por AST.

Para cada capa hexagonal (ver comun.CAPAS):
  Ce  (eferente)  = n.º de módulos internos distintos, FUERA de la capa, que la capa importa.
  Ca  (aferente)  = n.º de módulos internos distintos, FUERA de la capa, que importan algún módulo de la capa.
  I   (inestabilidad) = Ce / (Ca + Ce)      (0 = estable, 1 = inestable; I = n/a si Ca + Ce = 0)
  Ce_capas / Ca_capas = lo mismo contado en capas distintas (no en módulos).
La raíz de composición (app/main.py) se excluye del cálculo de Ca y Ce de las demás capas porque su función es
conocer todas las implementaciones. También verifica la REGLA DE DEPENDENCIA hexagonal: aristas capa->capa no
permitidas (hacia afuera del dominio).

Uso:  python herramientas/gqm/m13_acoplamiento.py [--version v1.0|v1.5|ambas] [--json ruta]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import comun as c

PERMITIDAS = {
    "dominio": {"dominio"},
    "puertos_entrada": {"puertos_entrada", "dominio"},
    "puertos_salida": {"puertos_salida", "dominio"},
    "aplicacion": {"aplicacion", "dominio", "puertos_entrada", "puertos_salida"},
    "adaptadores_entrada": {"adaptadores_entrada", "dominio", "puertos_entrada"},
    "adaptadores_salida": {"adaptadores_salida", "dominio", "puertos_salida"},
    "composicion": set(c.NOMBRE_CAPA),
}


def medir(version: str) -> dict:
    raiz = c.RAICES[version]
    capas = [k for k, v in c.CAPAS[version].items() if v]
    por_modulo: dict[str, tuple[str, list[c.Importacion]]] = {}
    for capa in capas:
        for a in c.archivos_py(raiz, c.CAPAS[version][capa]):
            if a.name == "__init__.py" and a.stat().st_size == 0:
                continue  # paquetes vacíos: no aportan acoplamiento
            por_modulo[c.modulo_de(raiz, a)] = (capa, c.importaciones(raiz, a))
    aristas_capa: dict[tuple[str, str], list[str]] = {}
    ce_mod = {k: set() for k in capas}
    ca_mod = {k: set() for k in capas}
    for mod, (capa, imps) in por_modulo.items():
        for i in imps:
            if i.tipo != "interno":
                continue
            destino = c.capa_de_modulo(version, raiz, i.modulo)
            if destino is None or destino == capa:
                continue
            aristas_capa.setdefault((capa, destino), []).append(f"{i.archivo}:{i.linea} {i.texto}")
            if capa != "composicion" and destino != "composicion":
                ce_mod[capa].add(i.modulo)
                ca_mod[destino].add(mod)
    filas = []
    for capa in capas:
        if capa == "composicion":
            continue
        ce_c = sorted({d for (o, d) in aristas_capa if o == capa and d != "composicion"})
        ca_c = sorted({o for (o, d) in aristas_capa if d == capa and o != "composicion"})
        ce, ca = len(ce_mod[capa]), len(ca_mod[capa])
        filas.append(
            {
                "capa": capa,
                "nombre": c.NOMBRE_CAPA[capa],
                "modulos": sum(1 for m, (k, _) in por_modulo.items() if k == capa),
                "Ce_modulos": ce,
                "Ca_modulos": ca,
                "I_modulos": None if ce + ca == 0 else round(ce / (ce + ca), 2),
                "Ce_capas": len(ce_c),
                "Ca_capas": len(ca_c),
                "I_capas": None if ce_c == ca_c == [] else round(len(ce_c) / (len(ce_c) + len(ca_c)), 2),
                "depende_de": ce_c,
                "dependen_de_ella": ca_c,
            }
        )
    violaciones = [
        {"origen": o, "destino": d, "evidencia": ev}
        for (o, d), ev in sorted(aristas_capa.items())
        if d not in PERMITIDAS[o]
    ]
    return {"version": version, "capas": filas, "violaciones_regla_dependencia": violaciones,
            "n_violaciones": sum(len(v["evidencia"]) for v in violaciones)}


def imprimir(r: dict) -> None:
    print(f"\n=== {c.ETIQUETA[r['version']]}")
    print(f"{'capa':<26}{'mód':>4}{'Ce':>4}{'Ca':>4}{'I':>6}   Ce_capas  Ca_capas  I_capas")
    for f in r["capas"]:
        i = "n/a" if f["I_modulos"] is None else f"{f['I_modulos']:.2f}"
        ic = "n/a" if f["I_capas"] is None else f"{f['I_capas']:.2f}"
        print(f"{f['nombre']:<26}{f['modulos']:>4}{f['Ce_modulos']:>4}{f['Ca_modulos']:>4}{i:>6}   "
              f"{f['Ce_capas']:>8}  {f['Ca_capas']:>8}  {ic:>7}   -> {f['depende_de']}")
    print(f"Violaciones de la regla de dependencia (aristas hacia fuera del dominio): {r['n_violaciones']}")
    for v in r["violaciones_regla_dependencia"]:
        print(f"  {v['origen']} -> {v['destino']}: {v['evidencia'][:3]}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="ambas", choices=["v1.0", "v1.5", "ambas"])
    ap.add_argument("--json", default=str(c.DATOS / "m13_acoplamiento.json"))
    a = ap.parse_args()
    vs = ["v1.0", "v1.5"] if a.version == "ambas" else [a.version]
    out = {v: medir(v) for v in vs}
    for v in vs:
        imprimir(out[v])
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON: {a.json}")


if __name__ == "__main__":
    main()
