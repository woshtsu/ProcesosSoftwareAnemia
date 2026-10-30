"""Prueba de carga (Locust): PMV del Incremento 1 y Incremento 2 (agenda, alertas, agenda del personal y asistencia).

Ejecución:
  locust -f tests/rendimiento/locustfile.py --host http://127.0.0.1:8000 \
         --headless -u 50 -r 10 -t 60s --csv docs/evidencias/carga
Perfil: 50 usuarios concurrentes simulando personal de postas de una microred. Tareas y pesos:
listar seguimiento 5, abrir expediente 4, agenda del niño 3 (HIST-2.1), vista previa 3, alertas de controles
vencidos 2 y resumen de alertas 2 (HIST-2.2; el resumen alimenta la insignia de la cabecera), agenda del personal 3
(HIST-2.3), asistencias del niño 1 (HIST-2.4), registrar niño 2, reporte 1. Conviene cargar antes los datos sintéticos: python -m scripts.cargar_datos_prueba
"""

import itertools
import random
import uuid

from locust import HttpUser, between, task

_contador = itertools.count(1)


class PersonalPosta(HttpUser):
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
    def agenda_del_nino(self):
        if self.ids:
            self.client.get(f"/api/ninos/{random.choice(self.ids)}/agenda", name="GET /api/ninos/{id}/agenda")

    @task(2)
    def alertas_controles_vencidos(self):
        filtros = random.choice(["", "?prioridad=ALTA", "?comunidad=Palmayoc", "?comunidad=Llacuas&prioridad=MEDIA"])
        self.client.get(f"/api/alertas/controles-vencidos{filtros}", name="GET /api/alertas/controles-vencidos")

    @task(2)
    def resumen_alertas(self):
        self.client.get("/api/alertas/resumen", name="GET /api/alertas/resumen")

    @task(3)
    def agenda_del_personal(self):
        filtros = random.choice(
            ["", "?comunidad=Palmayoc", "?comunidad=Llacuas", "?establecimiento=P. S. Chongos Alto"]
        )
        self.client.get(f"/api/agenda{filtros}", name="GET /api/agenda")

    @task(1)
    def asistencias_del_nino(self):
        if self.ids:
            self.client.get(f"/api/ninos/{random.choice(self.ids)}/asistencias", name="GET /api/ninos/{id}/asistencias")

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
        dni = f"8{next(_contador) + int(uuid.uuid4().int % 1000) * 10000:07d}"[:8]
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
