"""
Prueba de carga con Locust — PMV Anemia Junín.

Simula personal de salud que consulta la lista, abre expedientes, registra niños
y dosajes, y un coordinador que genera el reporte del periodo.

Requisitos: servidor levantado (python -m anemia_junin) con datos sintéticos.

Ejecución sin interfaz (desde anemia_junin/), 20 usuarios durante 60 s:

    locust -f tests/carga/locustfile.py --host http://127.0.0.1:8000 ^
           --headless -u 20 -r 5 -t 60s --csv tests/carga/results/carga

Con interfaz web de Locust: omitir --headless y abrir http://localhost:8089
Criterio de aceptación propuesto: 0 % de errores 5xx y p95 < 2000 ms.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from itertools import count

from locust import HttpUser, between, task

_HOY = date.today()
_SECUENCIA = count()
_DISTRITOS = [("Huancayo", 3271), ("El Tambo", 3260), ("Satipo", 628), ("Junín", 4107)]


def _dni_nuevo() -> str:
    # Rango 5xxxxxxx reservado a la prueba de carga (datos sintéticos)
    return f"{50000000 + random.randint(0, 9_000_000) + next(_SECUENCIA):08d}"


class PersonalDeSalud(HttpUser):
    wait_time = between(0.5, 2)
    weight = 4

    def on_start(self) -> None:
        self.dnis: list[str] = []
        resp = self.client.get("/api/v1/ninos?tamano=50", name="/api/v1/ninos")
        if resp.ok:
            self.dnis = [n["dni"] for n in resp.json()["data"]]

    @task(5)
    def ver_lista_web(self) -> None:
        self.client.get("/ninos", name="/ninos [web]")

    @task(4)
    def ver_expediente(self) -> None:
        if self.dnis:
            dni = random.choice(self.dnis)
            self.client.get(f"/api/v1/ninos/{dni}", name="/api/v1/ninos/{dni}")
            self.client.get(f"/ninos/{dni}", name="/ninos/{dni} [web]")

    @task(3)
    def filtrar_lista(self) -> None:
        clasificacion = random.choice(["SEVERA", "MODERADA", "LEVE", "SIN_DOSAJE"])
        self.client.get(
            f"/api/v1/ninos?clasificacion={clasificacion}", name="/api/v1/ninos?clasificacion"
        )

    @task(2)
    def registrar_nino(self) -> None:
        distrito, altitud = random.choice(_DISTRITOS)
        datos = {
            "dni": _dni_nuevo(),
            "nombres": "Carga Sintetica",
            "apellidos": "Prueba Locust",
            "fecha_nacimiento": (_HOY - timedelta(days=random.randint(200, 1700))).isoformat(),
            "sexo": random.choice(["F", "M"]),
            "tipo_nacimiento": "TERMINO",
            "peso_kg": round(random.uniform(6, 18), 2),
            "distrito": distrito,
            "altitud_msnm": altitud,
            "cuidador": "Cuidador Sintetico",
            "telefono": None,
            "dosaje_inicial": {
                "fecha_dosaje": _HOY.isoformat(),
                "hb_observada": round(random.uniform(8, 15), 1),
            },
        }
        with self.client.post("/api/v1/ninos", json=datos, name="POST /api/v1/ninos",
                              catch_response=True) as resp:
            if resp.status_code == 201:
                self.dnis.append(datos["dni"])
                resp.success()
            elif resp.status_code == 409:
                resp.success()  # colisión de DNI aleatorio: comportamiento esperado
            else:
                resp.failure(f"HTTP {resp.status_code}")

    @task(1)
    def agregar_dosaje(self) -> None:
        if self.dnis:
            dni = random.choice(self.dnis)
            self.client.post(
                f"/api/v1/ninos/{dni}/dosajes",
                json={"fecha_dosaje": _HOY.isoformat(),
                      "hb_observada": round(random.uniform(8, 15), 1),
                      "altitud_msnm": 3271},
                name="POST /api/v1/ninos/{dni}/dosajes",
            )


class Coordinador(HttpUser):
    wait_time = between(2, 5)
    weight = 1

    @task
    def reporte(self) -> None:
        desde = (_HOY - timedelta(days=30)).isoformat()
        self.client.get(
            f"/api/v1/reportes/registros?desde={desde}&hasta={_HOY.isoformat()}",
            name="/api/v1/reportes/registros",
        )
