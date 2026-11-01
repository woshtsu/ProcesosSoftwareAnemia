"""Factor S: auditoria de la arquitectura hexagonal por analisis AST de los import de pmv_fastapi/app/.

Uso: python entregables/semana-10/metricas/auditoria_hexagonal.py
Salida: texto en stdout y metricas/salidas/S_hexagonal.json (matriz capa x tipo de dependencia, violaciones, archivos y LOC).
Reglas (ADR-001/ADR-008): domain -> solo stdlib y domain; ports -> stdlib, domain y ports;
application -> stdlib, domain, ports (sin adapters ni frameworks); adapters/inbound -> ports.inbound y domain.model (+ frameworks);
adapters/outbound -> ports.outbound, domain (+ frameworks) y nunca application ni adapters/inbound; solo main.py conoce todo.
"""

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
APP = RAIZ / "pmv_fastapi" / "app"
STDLIB = set(sys.stdlib_module_names)
CAPAS = {
    "domain/model": "domain.model",
    "domain/service": "domain.service",
    "ports/inbound": "ports.inbound",
    "ports/outbound": "ports.outbound",
    "application": "application",
    "adapters/inbound": "adapters.inbound",
    "adapters/outbound": "adapters.outbound",
}
PERMITIDO = {
    "domain.model": {"stdlib", "domain.model"},
    "domain.service": {"stdlib", "domain.model", "domain.service"},
    "ports.inbound": {"stdlib", "domain", "ports.inbound"},
    "ports.outbound": {"stdlib", "domain", "ports.outbound"},
    "application": {"stdlib", "domain", "ports", "application"},
    "adapters.inbound": {"stdlib", "tercero", "domain.model", "ports.inbound", "adapters.inbound"},
    "adapters.outbound": {"stdlib", "tercero", "domain", "ports.outbound", "adapters.outbound"},
}


def clasificar(mod: str) -> str:
    if mod.startswith("app."):
        resto = mod[4:]
        for k in ("domain.model", "domain.service", "ports.inbound", "ports.outbound", "adapters.inbound", "adapters.outbound", "application"):
            if resto == k or resto.startswith(k + "."):
                return k
        return resto.split(".")[0]
    raiz = mod.split(".")[0]
    return "stdlib" if raiz in STDLIB else "tercero"


def importaciones(path: Path):
    for n in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(n, ast.Import):
            for a in n.names:
                yield a.name
        elif isinstance(n, ast.ImportFrom):
            yield "." * n.level + (n.module or "")


def main():
    matriz = defaultdict(lambda: defaultdict(int))
    terceros = defaultdict(set)
    violaciones, archivos, loc = [], defaultdict(int), defaultdict(int)
    for sub, capa in CAPAS.items():
        for p in sorted((APP / sub).rglob("*.py")):
            archivos[capa] += 1
            loc[capa] += sum(1 for l in p.read_text(encoding="utf-8").splitlines() if l.strip() and not l.strip().startswith("#"))
            for m in importaciones(p):
                if m.startswith("."):
                    violaciones.append(f"{p.relative_to(APP)} -> {m} (import relativo)")
                    continue
                d = clasificar(m)
                matriz[capa][d] += 1
                if d == "tercero":
                    terceros[capa].add(m.split(".")[0])
                permitido = PERMITIDO[capa]
                familia = {x for x in permitido}
                if not (d in familia or (d.split(".")[0] in familia and d.split(".")[0] in {"domain", "ports"})):
                    violaciones.append(f"{p.relative_to(APP)} -> {m} [{d}]")
    # modulos que importan a la vez application y adapters.outbound: solo main.py
    ambos = []
    for p in sorted(APP.rglob("*.py")):
        ms = set(importaciones(p))
        if any(m.startswith("app.application") for m in ms) and any(m.startswith("app.adapters") for m in ms):
            ambos.append(str(p.relative_to(APP)))
    salida = {
        "archivos_por_capa": dict(archivos),
        "loc_por_capa": dict(loc),
        "matriz_importaciones": {k: dict(v) for k, v in matriz.items()},
        "terceros_por_capa": {k: sorted(v) for k, v in terceros.items()},
        "violaciones": violaciones,
        "modulos_que_conocen_aplicacion_y_adaptadores": ambos,
        "importaciones_de_frameworks_en_dominio": sorted(terceros.get("domain.model", set()) | terceros.get("domain.service", set())),
    }
    (RAIZ / "entregables" / "semana-10" / "metricas" / "salidas" / "S_hexagonal.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    cols = ["stdlib", "tercero", "domain.model", "domain.service", "ports.inbound", "ports.outbound", "application", "adapters.inbound", "adapters.outbound"]
    print(f"{'capa (origen)':<20}{'arch.':>6}{'LOC':>6} | " + " ".join(f"{c[:11]:>11}" for c in cols))
    for capa in CAPAS.values():
        fila = matriz[capa]
        print(f"{capa:<20}{archivos[capa]:>6}{loc[capa]:>6} | " + " ".join(f"{fila.get(c, 0):>11}" for c in cols))
    print()
    for capa, t in sorted(terceros.items()):
        print(f"terceros en {capa}: {', '.join(sorted(t))}")
    print(f"\nImportaciones de frameworks en el dominio: {salida['importaciones_de_frameworks_en_dominio'] or 0}")
    print(f"Violaciones de la regla de dependencias: {len(violaciones)}")
    for v in violaciones:
        print("  -", v)
    print(f"Modulos que conocen a la vez application y adapters: {ambos}")
    sys.exit(1 if violaciones else 0)


if __name__ == "__main__":
    main()
