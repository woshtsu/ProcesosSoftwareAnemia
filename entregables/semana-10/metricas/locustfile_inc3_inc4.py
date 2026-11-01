"""Carga de los endpoints de los Incrementos 3 y 4 (el locustfile del repositorio solo cubre los Incrementos 1 y 2).

Perfil de personal de posta: visitas priorizadas, alertas de barreras, recordatorios y su metrica, conflictos pendientes,
barreras del nino, sincronizacion de un lote pequeno (idempotente por id_operacion) y generacion de recordatorios (idempotente).
"""

import random
import uuid
from datetime import datetime

from locust import HttpUser, between, task


class PersonalPostaInc3Inc4(HttpUser):
    wait_time = between(0.5, 2)

    def on_start(self):
        self.ids = [f["id"] for f in self.client.get("/api/ninos", name="GET /api/ninos").json()]

    @task(5)
    def visitas_priorizadas(self):
        self.client.get("/api/visitas/priorizadas?limite=50", name="GET /api/visitas/priorizadas")

    @task(3)
    def alertas_barreras(self):
        self.client.get("/api/alertas/barreras", name="GET /api/alertas/barreras")

    @task(3)
    def recordatorios(self):
        self.client.get("/api/recordatorios", name="GET /api/recordatorios")

    @task(2)
    def metricas_recordatorios(self):
        self.client.get("/api/recordatorios/metricas", name="GET /api/recordatorios/metricas")

    @task(2)
    def conflictos(self):
        self.client.get("/api/sincronizacion/conflictos?estado=PENDIENTE", name="GET /api/sincronizacion/conflictos")

    @task(2)
    def barreras_del_nino(self):
        self.client.get(f"/api/ninos/{random.choice(self.ids)}/barreras", name="GET /api/ninos/{id}/barreras")

    @task(2)
    def visitas_del_nino(self):
        self.client.get(f"/api/ninos/{random.choice(self.ids)}/visitas", name="GET /api/ninos/{id}/visitas")

    @task(2)
    def sincronizar_visita(self):
        self.client.post(
            "/api/sincronizacion",
            name="POST /api/sincronizacion",
            json={"operaciones": [{
                "id_operacion": str(uuid.uuid4()),
                "tipo": "REGISTRAR_VISITA",
                "id_dispositivo": "carga-locust",
                "fecha_local": datetime.now().astimezone().isoformat(),
                "nino_ref": {"id": random.choice(self.ids)},
                "datos": {"fecha": datetime.now().date().isoformat(), "resultado": "NO_ENCONTRADO", "observaciones": "carga"},
            }]},
        )

    @task(1)
    def generar_recordatorios(self):
        self.client.post("/api/recordatorios/generar", name="POST /api/recordatorios/generar")
