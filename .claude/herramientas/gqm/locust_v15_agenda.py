"""Perfil de carga ADICIONAL, solo v1.5 (V4): tareas comunes + agenda y alertas del Incremento 2.

Mismos pesos de las tareas comunes que en locust_comun.py y se suman las del Incremento 2, con los pesos de
tests/rendimiento/locustfile.py de v1.5: agenda del niño 3, alertas de controles vencidos 2 (con filtros), resumen
de alertas 2.

  locust -f .claude/herramientas/gqm/locust_v15_agenda.py --host http://127.0.0.1:8202 --headless -u 50 -r 10 -t 60s \
         --csv entregables/semana-09/metricas/salidas/v1.5/locust_agenda
"""

import random

from locust import task

from locust_comun import PersonalPostaComun


class PersonalPostaAgenda(PersonalPostaComun):
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
