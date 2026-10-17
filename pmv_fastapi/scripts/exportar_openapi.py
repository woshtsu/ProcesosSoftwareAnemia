"""Exporta el contrato OpenAPI de la API a docs/openapi.json (reproducible y sin servidor en ejecución).

Uso:
    python -m scripts.exportar_openapi                    # escribe docs/openapi.json
    python -m scripts.exportar_openapi --salida otra.json
    python -m scripts.exportar_openapi --verificar        # falla (código 1) si docs/openapi.json está desactualizado
"""

import argparse
import json
import sys
from pathlib import Path

from app.main import crear_app

DESTINO = Path(__file__).resolve().parents[1] / "docs" / "openapi.json"


def generar() -> str:
    """Contrato OpenAPI como texto JSON estable (sangría de 2 espacios, UTF-8, sin salto de línea final)."""
    app = crear_app("sqlite:///:memory:")  # la base no se usa: solo se necesita el esquema de las rutas
    try:
        return json.dumps(app.openapi(), indent=2, ensure_ascii=False)
    finally:
        app.state.repositorio.engine.dispose()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--salida", type=Path, default=DESTINO)
    ap.add_argument("--verificar", action="store_true", help="solo comprueba que el archivo esté al día")
    args = ap.parse_args()
    texto = generar()
    if args.verificar:
        vigente = args.salida.read_text(encoding="utf-8") if args.salida.exists() else ""
        if vigente != texto:
            print(f"{args.salida} está desactualizado: ejecute python -m scripts.exportar_openapi", file=sys.stderr)
            return 1
        print(f"{args.salida} está al día.")
        return 0
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(texto, encoding="utf-8")
    version = json.loads(texto)["info"]["version"]
    print(f"OpenAPI {version} escrito en {args.salida} ({len(json.loads(texto)['paths'])} rutas).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
