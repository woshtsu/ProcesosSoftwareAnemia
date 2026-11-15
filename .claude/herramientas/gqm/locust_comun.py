"""Perfil de carga COMÚN (V4): mismas tareas del Incremento 1 contra v1.0 y v1.5, con los mismos pesos.

Tareas y pesos (idénticos a tests/rendimiento/locustfile.py de v1.0): listar seguimiento 5, abrir expediente 4,
vista previa 3, registrar niño 2, reporte 1. Perfil de la corrida: 50 usuarios, 10 usuarios/s de subida, 60 s.

  locust -f .claude/herramientas/gqm/locust_comun.py --host http://127.0.0.1:8201 --headless -u 50 -r 10 -t 60s \
         --csv entregables/semana-09/metricas/salidas/v1.0/locust_comun

El DNI de cada niño registrado se genera con un contador por proceso, de modo que en una base de partida limpia no
hay colisiones (409). La base de partida es la misma copia de dataset_B150.json en ambas versiones.
"""

import itertools
import random

from locust import HttpUser, between, task

_contador = itertools.count(1)


class PersonalPostaComun(HttpUser):
    wait_time = between(0.5, 2)

    def on_start(self):
        self.ids = [f["id"] for f in self.client.get("/api/ninos", name="GET /api/ninos").json()]

    @task(5)
    def listar_seguimiento(self):
        self.client.get("/api/ninos", name="GET /api/ninos")

    @task(4)
    def abrir_expediente(self):
        if self.ids:
            self.client.get(f"/api/ninos/{random.choice(self.ids)}", name="GET /api/ninos/{id}")

    @task(3)
    def vista_previa(self):
        self.client.post(
            "/api/validaciones/evaluacion",
            name="POST /api/validaciones/evaluacion",
            json={
                "fecha_nacimiento": "2025-06-10",
                "altitud_m": 3720,
                "evaluacion": {"fecha": "2026-09-20", "hemoglobina_observada": 11.4, "peso_kg": 9, "talla_cm": 73},
            },
        )

    @task(2)
    def registrar_nino(self):
        dni = f"8{next(_contador):07d}"
        self.client.post(
            "/api/ninos",
            name="POST /api/ninos",
            headers={"X-Usuario": "carga"},
            json={
                "nino": {
                    "dni": dni,
                    "nombres": "Prueba",
                    "apellidos": "Carga",
                    "sexo": "F",
                    "fecha_nacimiento": "2025-03-01",
                    "establecimiento": "P. S. Chongos Alto",
                    "distrito": "Chongos Alto",
                    "comunidad": "Palmayoc",
                    "altitud_m": 3720,
                    "tutor_nombre": "Tutor Prueba",
                },
                "evaluacion_inicial": {
                    "fecha": "2026-09-20",
                    "hemoglobina_observada": 11.9,
                    "peso_kg": 9.5,
                    "talla_cm": 74,
                },
            },
        )

    @task(1)
    def reporte(self):
        self.client.get("/api/reportes/periodo?desde=2026-08-01&hasta=2026-09-30", name="GET /api/reportes/periodo")
