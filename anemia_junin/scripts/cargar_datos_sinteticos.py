"""
Script de carga de datos sintéticos — PMV Anemia Junín.

Crea niños y dosajes de ejemplo para la demostración.
Solo funciona sobre una base de datos vacía (sin niños registrados).

Uso:
    python scripts/cargar_datos_sinteticos.py

    O con una BD alternativa:
    python scripts/cargar_datos_sinteticos.py --db instance/demo.db
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

# Añadir src/ al path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from anemia_junin.adapters.outbound.sqlite.migraciones import migrar
from anemia_junin.adapters.outbound.sqlite.unidad_de_trabajo import UnidadDeTrabajo
from anemia_junin.bootstrap import crear_app


_DISTRITOS = [
    "Huancayo", "El Tambo", "Chilca", "San Agustín de Cajas",
    "Chupaca", "Concepción", "Junín", "Tarma", "Satipo", "Mazamari"
]
_APELLIDOS = [
    "Quispe", "Mamani", "Huanca", "Condori", "Flores",
    "López", "García", "Torres", "Ccama", "Tapia"
]
_NOMBRES_F = ["Ana María", "Rosa Elena", "Carmen", "Lucía", "Isabel", "María José"]
_NOMBRES_M = ["José Luis", "Carlos", "Miguel Ángel", "Diego", "Sebastián", "Andrés"]

_HOY = date(2026, 9, 25)
random.seed(42)  # reproducible


def _dni(n: int) -> str:
    return f"{10000000 + n:08d}"


def _fecha_nacimiento_en_meses(meses: int) -> date:
    return _HOY - timedelta(days=meses * 30)


def _generar_ninos() -> list[dict]:
    ninos = []
    for i in range(30):
        sexo = "F" if i % 2 == 0 else "M"
        nombres = random.choice(_NOMBRES_F if sexo == "F" else _NOMBRES_M)
        meses = random.randint(6, 59)
        distrito = random.choice(_DISTRITOS)
        altitud = random.choice([1200, 2500, 3271, 3800, 4000])
        nino = {
            "dni": _dni(i),
            "nombres": nombres,
            "apellidos": f"{random.choice(_APELLIDOS)} {random.choice(_APELLIDOS)}",
            "fecha_nacimiento": _fecha_nacimiento_en_meses(meses).isoformat(),
            "sexo": sexo,
            "tipo_nacimiento": random.choice(["TERMINO", "PREMATURO"]),
            "peso_kg": round(random.uniform(6, 18), 2),
            "distrito": distrito,
            "altitud_msnm": altitud,
            "cuidador": f"{random.choice(_APELLIDOS)} {random.choice(_APELLIDOS)}",
            "telefono": f"9{random.randint(10000000, 99999999):08d}",
        }
        # Algunos con dosaje inicial
        if i % 3 == 0:
            hb = round(random.uniform(7.0, 14.0), 1)
            nino["dosaje_inicial"] = {
                "fecha_dosaje": (_HOY - timedelta(days=random.randint(10, 90))).isoformat(),
                "hb_observada": hb,
            }
        ninos.append(nino)
    return ninos


def cargar(db_path: str) -> None:
    import requests  # type: ignore
    # Verificar que la BD esté vacía
    import sqlite3
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM ninos").fetchone()[0]
    conn.close()

    if count > 0:
        print(f"ERROR: La base de datos ya tiene {count} niños. "
              "Solo cargar sobre una BD vacía.")
        sys.exit(1)

    # Usar la app directamente sin requests
    app = crear_app(db_path=db_path)
    client = app.test_client()

    ninos = _generar_ninos()
    aceptados = 0
    rechazados = 0

    for nino in ninos:
        resp = client.post(
            "/api/v1/ninos",
            data=json.dumps(nino),
            content_type="application/json",
        )
        if resp.status_code == 201:
            aceptados += 1
            dni = resp.get_json()["data"]["dni"]
            # Agregar dosajes adicionales a algunos niños
            if random.random() > 0.5:
                fecha_d = (_HOY - timedelta(days=random.randint(1, 30))).isoformat()
                hb = round(random.uniform(7.0, 14.0), 1)
                altitud = nino["altitud_msnm"]
                client.post(
                    f"/api/v1/ninos/{dni}/dosajes",
                    data=json.dumps({
                        "fecha_dosaje": fecha_d,
                        "hb_observada": hb,
                        "altitud_msnm": altitud,
                    }),
                    content_type="application/json",
                )
        else:
            rechazados += 1
            print(f"  Rechazado DNI {nino['dni']}: {resp.get_json()}")

    print(f"\n✅ Datos cargados: {aceptados} niños aceptados, {rechazados} rechazados")
    print(f"   BD: {db_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cargar datos sintéticos de demostración")
    parser.add_argument("--db", default="instance/anemia.db", help="Ruta a la BD SQLite")
    args = parser.parse_args()

    db = str(Path(__file__).parents[1] / args.db)
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    migrar(db)
    cargar(db)
