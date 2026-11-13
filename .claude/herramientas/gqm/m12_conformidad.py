#!/usr/bin/env python
"""M1.2 Cohesión / conformidad de módulos hexagonales (Matriz 4.1 de la guía S9, GQM G-01 / Q1.2).

Un componente es CONFORME solo si cumple DOS criterios verificables automáticamente (AST):
  (a) Ubicación: existe como módulo/carpeta independiente propio. Regla objetiva: la ruta existe y es un PAQUETE
      (carpeta) propio, o un módulo (.py) cuyo paquete contenedor NO aloja módulos de otra capa. Equivalencia
      aceptada /src/... de la guía -> app/... en Python.
  (b) Desacoplamiento, según el componente:
      Dominio ............ 0 importaciones externas y no importa puertos / aplicación / adaptadores / main.
      Puertos de entrada . todas sus clases son interfaces puras (Protocol/ABC, métodos sin lógica) y definen
                           casos de uso (>= 1 interfaz); importan solo dominio y stdlib.
      Puertos de salida .. interfaces sin implementación (Protocol/ABC) y sin importar infraestructura (externos,
                           aplicación, adaptadores).
      Adaptadores entrada  controladores que dependen de puertos de ENTRADA (importan app.ports.inbound) y NO
                           importan clases concretas de aplicación ni adaptadores de salida.
      Adaptadores salida . implementan el puerto de persistencia (RepositorioNinos: herencia explícita o todos sus
                           métodos presentes) usando la tecnología concreta (importan sqlalchemy) y no importan
                           aplicación ni adaptadores de entrada.
%  M1.2 = componentes conformes / 5 x 100.

Hallazgos adicionales (no cambian el estado) se listan en 'observaciones' y se calcula una lectura de sensibilidad:
  laxa ........ criterio (a) = la ruta existe (aunque comparta paquete con otra capa).
  ultra-estricta  el criterio (b) de adaptadores de salida exige además que TODOS los puertos de salida (incl. Reloj)
                  tengan su implementación dentro del paquete de adaptadores de salida.

Uso:  python .claude/herramientas/gqm/m12_conformidad.py [--version v1.0|v1.5|v2.0|todas] [--json ruta]
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

import comun as c

COMPONENTES = ["dominio", "puertos_entrada", "puertos_salida", "adaptadores_entrada", "adaptadores_salida"]
RUTA_GUIA = {
    "dominio": "/src/domain/model/",
    "puertos_entrada": "/src/ports/inbound/",
    "puertos_salida": "/src/ports/outbound/",
    "adaptadores_entrada": "/src/adapters/inbound/rest/",
    "adaptadores_salida": "/src/adapters/outbound/persistence/",
}


def _capa_import(version: str, raiz: Path, imp: c.Importacion) -> str | None:
    if imp.tipo != "interno":
        return None
    return c.capa_de_modulo(version, raiz, imp.modulo)


def _bases(cls: ast.ClassDef) -> list[str]:
    nombres = []
    for b in cls.bases:
        if isinstance(b, ast.Name):
            nombres.append(b.id)
        elif isinstance(b, ast.Attribute):
            nombres.append(b.attr)
        elif isinstance(b, ast.Subscript):
            nombres.append(getattr(b.value, "id", getattr(b.value, "attr", "?")))
    return nombres


def _metodo_vacio(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Cuerpo = solo docstring, '...' o 'pass' (sin lógica)."""
    for n in fn.body:
        if isinstance(n, ast.Pass):
            continue
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant):
            continue  # docstring o Ellipsis
        return False
    return True


def analizar_interfaces(archivos: list[Path], raiz: Path) -> dict:
    interfaces, violaciones = [], []
    for a in archivos:
        if a.name == "__init__.py":
            continue
        for cls in [n for n in ast.parse(a.read_text(encoding="utf-8")).body if isinstance(n, ast.ClassDef)]:
            bases = _bases(cls)
            es_iface = any(b in ("Protocol", "ABC") for b in bases)
            metodos = [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            con_logica = [m.name for m in metodos if not _metodo_vacio(m)]
            ref = f"{a.relative_to(raiz)}:{cls.lineno}"
            interfaces.append(
                {"clase": cls.name, "ref": ref, "bases": bases, "es_protocol_abc": es_iface,
                 "metodos": [m.name for m in metodos], "metodos_con_logica": con_logica}
            )
            if not es_iface:
                violaciones.append(f"{ref} {cls.name} no es Protocol/ABC (bases: {bases or 'ninguna'})")
            if con_logica:
                violaciones.append(f"{ref} {cls.name} tiene lógica en: {', '.join(con_logica)}")
    return {"interfaces": interfaces, "violaciones": violaciones}


def ubicacion(version: str, capa: str) -> tuple[bool, bool, str, str]:
    """(estricta, laxa, detalle, ruta_real)"""
    raiz = c.RAICES[version]
    rutas = c.CAPAS[version][capa]
    if not rutas:
        return False, False, "No existe ninguna carpeta ni módulo de este componente.", "(no existe)"
    ok_estricto, ok_laxo, det = True, True, []
    for r in rutas:
        p = raiz / r
        if not p.exists():
            ok_estricto = ok_laxo = False
            det.append(f"{r}: no existe")
        elif p.is_dir():
            det.append(f"{r}/: paquete propio")
        else:
            otros = [x.name for x in p.parent.glob("*.py") if x.name not in ("__init__.py", p.name)]
            if otros:
                ok_estricto = False
                det.append(f"{r}: módulo dentro del paquete {p.parent.relative_to(raiz)}/ que también aloja {otros}")
            else:
                det.append(f"{r}: módulo propio en paquete propio")
    return ok_estricto, ok_laxo, "; ".join(det), ", ".join(rutas)


def evaluar(version: str) -> dict:
    raiz = c.RAICES[version]
    filas, observaciones = [], []
    arch = {k: c.archivos_py(raiz, c.CAPAS[version][k]) for k in c.CAPAS[version]}
    imps = {k: [i for a in v for i in c.importaciones(raiz, a)] for k, v in arch.items()}
    puertos_salida = analizar_interfaces(arch["puertos_salida"], raiz)

    def ev(imp_list, prefijos):  # evidencia: importaciones que empiecen con prefijos
        return [f"{i.archivo}:{i.linea} {i.texto}" for i in imp_list if any(i.modulo.startswith(p) for p in prefijos)]

    for comp in COMPONENTES:
        est_a, laxa_a, det_a, ruta_real = ubicacion(version, comp)
        lista = imps[comp]
        externos = [i for i in lista if i.tipo == "externo"]
        capas_imp = [(i, _capa_import(version, raiz, i)) for i in lista]
        evid, det_b, ok_b = [], "", False

        if comp == "dominio":
            fuera = [i for i, k in capas_imp if k and k != "dominio"]
            ok_b = not externos and not fuera
            det_b = f"{len(externos)} importaciones externas; {len(fuera)} importaciones de otras capas."
            evid = [f"{i.archivo}:{i.linea} {i.texto}" for i in externos + fuera] or [
                f"Sin importaciones externas ({len(lista)} importaciones: stdlib e internas de dominio)"
            ]
        elif comp in ("puertos_entrada", "puertos_salida"):
            if not arch[comp]:
                ok_b, det_b, evid = False, "No hay puertos de entrada: ningún caso de uso se define como interfaz.", []
            else:
                info = analizar_interfaces(arch[comp], raiz)
                no_dom = [i for i, k in capas_imp if i.tipo == "externo" or (k and k not in ("dominio", comp))]
                ok_b = bool(info["interfaces"]) and not info["violaciones"] and not no_dom
                det_b = (
                    f"{len(info['interfaces'])} interfaces; violaciones de pureza: {len(info['violaciones'])}; "
                    f"importaciones de infraestructura/otras capas: {len(no_dom)}."
                )
                evid = (
                    [f"{x['ref']} {x['clase']}({', '.join(x['bases'])}): {len(x['metodos'])} métodos sin lógica"
                     for x in info["interfaces"]]
                    + info["violaciones"]
                    + [f"{i.archivo}:{i.linea} {i.texto}" for i in no_dom]
                )
        elif comp == "adaptadores_entrada":
            usa_puertos = [i for i, k in capas_imp if k == "puertos_entrada"]
            concretos = [i for i, k in capas_imp if k == "aplicacion"]
            sal = [i for i, k in capas_imp if k == "adaptadores_salida"]
            ok_b = bool(usa_puertos) and not concretos and not sal
            det_b = (
                f"Importa {len(usa_puertos)} puerto(s) de entrada; importa {len(concretos)} módulo(s) de aplicación "
                f"(clases concretas); {len(sal)} de adaptadores de salida."
            )
            evid = [f"{i.archivo}:{i.linea} {i.texto}" for i in usa_puertos + concretos + sal] or [
                "No importa ningún puerto de entrada (no existen)"
            ]
        else:  # adaptadores_salida
            sqla = [i for i in lista if i.modulo.split(".")[0] == "sqlalchemy"]
            apl = [i for i, k in capas_imp if k in ("aplicacion", "adaptadores_entrada")]
            repo_iface = next((x for x in puertos_salida["interfaces"] if x["clase"] == "RepositorioNinos"), None)
            impl = []
            for a in arch[comp]:
                for cls in c.clases(a):
                    mets = {n.name for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
                    if repo_iface and set(repo_iface["metodos"]) <= mets:
                        explicita = "RepositorioNinos" in _bases(cls)
                        impl.append(f"{a.relative_to(raiz)}:{cls.lineno} {cls.name} "
                                    f"({'hereda' if explicita else 'implementa estructuralmente'} RepositorioNinos)")
            ok_b = bool(impl) and bool(sqla) and not apl
            det_b = (
                f"{len(impl)} clase(s) implementan RepositorioNinos; {len(sqla)} importaciones de SQLAlchemy; "
                f"{len(apl)} importaciones de aplicación/adaptadores de entrada."
            )
            evid = impl + [f"{i.archivo}:{i.linea} {i.texto}" for i in sqla[:3]] + [
                f"{i.archivo}:{i.linea} {i.texto}" for i in apl
            ]
        filas.append(
            {
                "componente": c.NOMBRE_CAPA[comp],
                "clave": comp,
                "ruta_guia": RUTA_GUIA[comp],
                "ruta_real": ruta_real,
                "criterio_a": est_a,
                "detalle_a": det_a,
                "criterio_a_laxo": laxa_a,
                "criterio_b": ok_b,
                "detalle_b": det_b,
                "estado": "CONFORME" if est_a and ok_b else "NO CONFORME",
                "estado_laxo": "CONFORME" if laxa_a and ok_b else "NO CONFORME",
                "evidencia": evid,
            }
        )

    # Observaciones (hallazgos que no cambian el estado)
    # Puertos de salida que no tienen implementación dentro del paquete de adaptadores de salida
    nombres_adapt = {cl.name for a in arch["adaptadores_salida"] for cl in c.clases(a)}
    impl_fuera = []
    for p in puertos_salida["interfaces"]:
        if p["clase"] == "RepositorioNinos":
            continue
        for capa in ("aplicacion", "composicion", "adaptadores_entrada"):
            for a in arch[capa]:
                for cls in c.clases(a):
                    mets = {n.name for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
                    if set(p["metodos"]) <= mets and cls.name not in nombres_adapt and p["metodos"]:
                        impl_fuera.append(f"{a.relative_to(raiz)}:{cls.lineno} {cls.name} implementa el puerto {p['clase']}")
    if impl_fuera:
        observaciones.append("Implementación de un puerto de salida fuera de adaptadores de salida: " + "; ".join(impl_fuera))
    conformes = sum(1 for f in filas if f["estado"] == "CONFORME")
    conformes_laxo = sum(1 for f in filas if f["estado_laxo"] == "CONFORME")
    ultra = conformes - (
        1
        if impl_fuera
        and next(f for f in filas if f["clave"] == "adaptadores_salida")["estado"] == "CONFORME"
        else 0
    )
    return {
        "version": version,
        "raiz": c.ruta_rel(raiz),
        "filas": filas,
        "conformes": conformes,
        "total": len(filas),
        "m12_pct": round(conformes / len(filas) * 100, 1),
        "sensibilidad": {
            "laxa_pct": round(conformes_laxo / len(filas) * 100, 1),
            "estricta_pct": round(conformes / len(filas) * 100, 1),
            "ultra_estricta_pct": round(ultra / len(filas) * 100, 1),
        },
        "observaciones": observaciones,
    }


def imprimir(res: dict) -> None:
    print(f"\n=== {c.ETIQUETA[res['version']]}")
    for f in res["filas"]:
        print(f"- {f['componente']:<24} {f['ruta_real']:<34} a={'SI' if f['criterio_a'] else 'NO':<3} "
              f"b={'SI' if f['criterio_b'] else 'NO':<3} -> {f['estado']}")
        print(f"    a) {f['detalle_a']}")
        print(f"    b) {f['detalle_b']}")
        for e in f["evidencia"][:8]:
            print(f"       · {e}")
    print(f"M1.2 = {res['conformes']}/{res['total']} x 100 = {res['m12_pct']} %   sensibilidad: {res['sensibilidad']}")
    for o in res["observaciones"]:
        print("  observación:", o)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="todas", choices=["v1.0", "v1.5", "v2.0", "todas"])
    ap.add_argument("--json", default=str(c.DATOS / "m12_conformidad.json"))
    a = ap.parse_args()
    vs = c.VERSIONES if a.version == "todas" else [a.version]
    out = {v: evaluar(v) for v in vs}
    for v in vs:
        imprimir(out[v])
    c.fusionar_json(Path(a.json), out)
    print(f"\nJSON: {a.json}")


if __name__ == "__main__":
    main()
