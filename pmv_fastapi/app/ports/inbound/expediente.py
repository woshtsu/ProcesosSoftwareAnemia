"""Puerto de entrada: registro, validación y expediente digital (HU-01, HU-02, HU-03)."""

from datetime import date
from typing import Protocol

from app.domain.model.entidades import Evaluacion, Nino


class GestionarExpediente(Protocol):
    def fecha_actual(self) -> date:
        """Fecha de hoy en Perú según el reloj del sistema."""
        ...

    def previsualizar_evaluacion(self, fecha_nacimiento: date, altitud_m: float, datos_eval: dict) -> Evaluacion: ...

    def registrar_nino(self, datos_nino: dict, datos_eval: dict, usuario: str) -> Nino: ...

    def consultar(self, nino_id: str) -> Nino: ...

    def consultar_por_dni(self, dni: str) -> Nino: ...

    def actualizar_datos(self, nino_id: str, cambios: dict, usuario: str) -> Nino: ...

    def registrar_evaluacion(self, nino_id: str, datos_eval: dict, usuario: str) -> Nino: ...
