"""
Punto de entrada — PMV Anemia Junín.

Uso (desde la carpeta ``anemia_junin/`` con el entorno virtual activo):

    python -m anemia_junin                   # Waitress en http://127.0.0.1:8000
    python -m anemia_junin --port 8080       # otro puerto
    python -m anemia_junin --dev             # servidor de desarrollo de Flask (recarga)
    python -m anemia_junin --db instance/demo.db

Variables de entorno equivalentes: ANEMIA_DB_PATH, ANEMIA_NORMATIVA_PATH,
ANEMIA_SECRET_KEY, ANEMIA_HOST, ANEMIA_PORT.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys


def _parsear_argumentos(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m anemia_junin",
        description="Levanta el PMV Anemia Junín (INC-1: registro nominal y expediente digital).",
    )
    parser.add_argument(
        "--host", default=os.environ.get("ANEMIA_HOST", "127.0.0.1"),
        help="Interfaz de escucha (por defecto 127.0.0.1)",
    )
    parser.add_argument(
        "--port", type=int, default=int(os.environ.get("ANEMIA_PORT", "8000")),
        help="Puerto (por defecto 8000)",
    )
    parser.add_argument(
        "--db", default=None,
        help="Ruta a la BD SQLite (por defecto instance/anemia.db o ANEMIA_DB_PATH)",
    )
    parser.add_argument(
        "--dev", action="store_true",
        help="Usa el servidor de desarrollo de Flask en lugar de Waitress",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parsear_argumentos(argv)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    from anemia_junin.bootstrap import crear_app

    app = crear_app(db_path=args.db)
    url = f"http://{args.host}:{args.port}/"
    print(f"PMV Anemia Junín escuchando en {url}  (Ctrl+C para detener)", flush=True)
    print(f"Base de datos: {app.config['DB_PATH']}", flush=True)

    if args.dev:
        app.run(host=args.host, port=args.port, debug=True)
    else:
        from waitress import serve

        serve(app, host=args.host, port=args.port, threads=8)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
