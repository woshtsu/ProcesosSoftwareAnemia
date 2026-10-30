"""Puerto de salida: persistencia de los recordatorios de control (HIST-4.1 y HIST-4.2)."""

from datetime import date
from typing import Protocol

from app.domain.model.notificacion import Recordatorio


class RepositorioRecordatorios(Protocol):
    def agregar_recordatorio(self, recordatorio: Recordatorio) -> Recordatorio:
        """Guarda el recordatorio; lanza ConflictoRecordatorio si ya existe uno para (niño, control, tipo)."""
        ...

    def actualizar_recordatorio(self, recordatorio: Recordatorio) -> Recordatorio:
        """Reemplaza canal, estado, envío y respuesta de un recordatorio existente."""
        ...

    def obtener_recordatorio(self, recordatorio_id: str) -> Recordatorio | None: ...

    def obtener_por_id_externo(self, id_externo: str) -> Recordatorio | None:
        """Recordatorio cuyo mensaje tiene ese identificador del proveedor (para los avisos de entrega)."""
        ...

    def buscar_para_respuesta(self, id_externo: str | None, destino: str | None) -> Recordatorio | None:
        """Recordatorio al que responde un mensaje entrante: primero por el id del mensaje al que responde; si no hay,
        el último enviado por WhatsApp a ese celular que aún no tiene respuesta."""
        ...

    def listar_recordatorios(
        self,
        estado: str | None = None,
        desde: date | None = None,
        hasta: date | None = None,
        nino_id: str | None = None,
        limite: int | None = None,
    ) -> list[Recordatorio]:
        """Recordatorios (el más reciente primero) generados entre los días locales ``desde`` y ``hasta``."""
        ...
