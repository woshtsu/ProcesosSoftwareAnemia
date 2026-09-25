"""Caso de uso: Consultar Expediente — HIST-1.2 / HU-02."""

from __future__ import annotations

from anemia_junin.application.conversores import dosaje_a_dto, nino_a_dto
from anemia_junin.application.dto import ExpedienteDTO
from anemia_junin.domain.entities import Clasificacion


class NinoNoEncontradoError(Exception):
    pass


class ConsultarExpediente:
    def __init__(self, uow_factory) -> None:
        self._uow_factory = uow_factory

    def ejecutar(self, dni: str) -> ExpedienteDTO:
        with self._uow_factory() as uow:
            nino = uow.ninos.obtener_por_dni(dni)
            if nino is None:
                raise NinoNoEncontradoError(f"Niño con DNI {dni} no encontrado")

            historial = uow.dosajes.listar_por_nino(nino.id)

        historial_dto = [dosaje_a_dto(d) for d in historial]

        if historial_dto:
            clasificacion_actual = historial_dto[0].clasificacion
        else:
            clasificacion_actual = Clasificacion.SIN_DOSAJE

        return ExpedienteDTO(
            nino=nino_a_dto(nino),
            clasificacion_actual=clasificacion_actual,
            historial_dosajes=historial_dto,
        )
