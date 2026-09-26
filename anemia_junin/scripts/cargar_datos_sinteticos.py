"""
Carga de datos SINTÉTICOS — PMV Anemia Junín.

Crea niños y dosajes ficticios para la demostración, más algunos intentos de alta
inválidos para poblar el indicador «% de registros sin error crítico» (HIST-1.5).
Ningún dato corresponde a una persona real: los DNI empiezan en 10000000 y los
nombres se combinan al azar con semilla fija (resultado reproducible).

Todas las altas pasan por la API REST (mismos casos de uso y validaciones que la
interfaz web) usando el cliente de pruebas de Flask, sin abrir puertos.

Uso (desde la carpeta anemia_junin/):
    python scripts/cargar_datos_sinteticos.py
    python scripts/cargar_datos_sinteticos.py --db instance/demo.db

Solo carga sobre una base de datos sin niños (no mezcla con datos existentes).
"""

from __future__ import annotations

import argparse
import calendar
import json
import random
import sqlite3
import sys
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ / "src"))  # permite ejecutar sin `pip install -e .`

from anemia_junin.bootstrap import crear_app  # noqa: E402

_DISTRITOS = [
    ("Huancayo", 3271), ("El Tambo", 3260), ("Chilca", 3280), ("Chupaca", 3263),
    ("Concepción", 3283), ("Junín", 4107), ("Tarma", 3053), ("Satipo", 628),
    ("Mazamari", 690), ("Pampas", 3276),
]
_APELLIDOS = [
    "Quispe", "Mamani", "Huanca", "Condori", "Flores",
    "López", "García", "Torres", "Ccama", "Tapia",
]
_NOMBRES_F = ["Ana María", "Rosa Elena", "Carmen", "Lucía", "Isabel", "María José"]
_NOMBRES_M = ["José Luis", "Carlos", "Miguel Ángel", "Diego", "Sebastián", "Andrés"]

N_NINOS = 30
SEMILLA = 42

# Intentos inválidos intencionales (alimentan el indicador de calidad del registro)
_INTENTOS_INVALIDOS = [
    {"dni": "1234567", "motivo": "DNI de 7 dígitos"},
    {"telefono": "12345", "motivo": "celular sin formato de 9 dígitos"},
    {"dosaje_inicial": {"fecha_dosaje": None, "hb_observada": 30.0},
     "motivo": "hemoglobina fuera de rango (30 g/dL)"},
]


def _restar_meses(d: date, meses: int) -> date:
    total = d.year * 12 + (d.month - 1) - meses
    anio, mes = divmod(total, 12)
    mes += 1
    dia = min(d.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)


def _dni(n: int) -> str:
    return f"{10000000 + n:08d}"


def generar_ninos(hoy: date, rng: random.Random) -> list[dict]:
    ninos = []
    for i in range(N_NINOS):
        sexo = "F" if i % 2 == 0 else "M"
        distrito, altitud = _DISTRITOS[i % len(_DISTRITOS)]
        meses = rng.randint(7, 58)
        nino = {
            "dni": _dni(i),
            "nombres": rng.choice(_NOMBRES_F if sexo == "F" else _NOMBRES_M),
            "apellidos": f"{rng.choice(_APELLIDOS)} {rng.choice(_APELLIDOS)}",
            "fecha_nacimiento": _restar_meses(hoy, meses).isoformat(),
            "sexo": sexo,
            "tipo_nacimiento": rng.choice(["TERMINO", "TERMINO", "PREMATURO"]),
            "peso_kg": round(rng.uniform(6, 18), 2),
            "distrito": distrito,
            "altitud_msnm": altitud,
            "cuidador": f"{rng.choice(_NOMBRES_F)} {rng.choice(_APELLIDOS)}",
            "telefono": f"9{rng.randint(10000000, 99999999):08d}",
        }
        # Uno de cada cinco queda SIN dosaje para mostrar SIN_DOSAJE ≠ SIN_ANEMIA
        if i % 5 != 4:
            nino["dosaje_inicial"] = {
                "fecha_dosaje": (hoy - timedelta(days=rng.randint(40, 120))).isoformat(),
                "hb_observada": round(rng.uniform(8.0, 15.0), 1),
            }
        ninos.append(nino)
    return ninos


def cargar(db_path: str, hoy: date | None = None) -> dict[str, int]:
    """Carga los datos sintéticos y devuelve un resumen de conteos."""
    hoy = hoy or date.today()
    rng = random.Random(SEMILLA)

    app = crear_app(db_path=db_path)  # aplica migraciones
    with closing(sqlite3.connect(db_path)) as conn:
        existentes = conn.execute("SELECT COUNT(*) FROM ninos").fetchone()[0]
    if existentes > 0:
        raise SystemExit(
            f"ERROR: la base de datos ya tiene {existentes} niños. "
            "Use otra ruta con --db o elimine el archivo de la BD de demostración."
        )

    client = app.test_client()
    resumen = {"ninos_aceptados": 0, "ninos_rechazados": 0, "dosajes_adicionales": 0,
               "intentos_invalidos": 0}

    ninos = generar_ninos(hoy, rng)
    for nino in ninos:
        resp = client.post("/api/v1/ninos", data=json.dumps(nino), content_type="application/json")
        if resp.status_code != 201:
            resumen["ninos_rechazados"] += 1
            print(f"  Rechazado DNI {nino['dni']}: {resp.get_json()}")
            continue
        resumen["ninos_aceptados"] += 1
        # La mitad de los niños con dosaje reciben un control posterior (historial)
        if "dosaje_inicial" in nino and rng.random() > 0.5:
            resp_d = client.post(
                f"/api/v1/ninos/{nino['dni']}/dosajes",
                data=json.dumps({
                    "fecha_dosaje": (hoy - timedelta(days=rng.randint(1, 30))).isoformat(),
                    "hb_observada": round(rng.uniform(8.0, 15.0), 1),
                    "altitud_msnm": nino["altitud_msnm"],
                }),
                content_type="application/json",
            )
            if resp_d.status_code == 201:
                resumen["dosajes_adicionales"] += 1

    # Intentos inválidos a propósito (quedan en la traza sin datos personales)
    base_valida = {k: v for k, v in ninos[0].items() if k != "dosaje_inicial"}
    for n, intento in enumerate(_INTENTOS_INVALIDOS):
        datos = {**base_valida, "dni": _dni(900 + n)}
        datos.update({k: v for k, v in intento.items() if k != "motivo"})
        if "dosaje_inicial" in datos:
            datos["dosaje_inicial"]["fecha_dosaje"] = hoy.isoformat()
        resp = client.post("/api/v1/ninos", data=json.dumps(datos), content_type="application/json")
        if resp.status_code == 400:
            resumen["intentos_invalidos"] += 1

    return resumen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cargar datos sintéticos de demostración")
    parser.add_argument("--db", default="instance/anemia.db",
                        help="Ruta a la BD SQLite, relativa a anemia_junin/ "
                             "(por defecto instance/anemia.db)")
    args = parser.parse_args(argv)

    db = Path(args.db)
    if not db.is_absolute():
        db = _RAIZ / db
    db.parent.mkdir(parents=True, exist_ok=True)

    resumen = cargar(str(db))
    print(
        f"\nDatos sintéticos cargados en {db}\n"
        f"  Niños aceptados:        {resumen['ninos_aceptados']}\n"
        f"  Niños rechazados:       {resumen['ninos_rechazados']}\n"
        f"  Dosajes adicionales:    {resumen['dosajes_adicionales']}\n"
        f"  Intentos inválidos:     {resumen['intentos_invalidos']} (para el indicador de calidad)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
