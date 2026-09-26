"""Caso de uso: Actualizar Niño — HIST-1.2 / HU-02."""

from __future__ import annotations

from anemia_junin.application.casos_de_uso.consultar_expediente import NinoNoEncontradoError
from anemia_junin.application.conversores import nino_a_dto
from anemia_junin.application.dto import ActualizarNinoDTO, NinoSalidaDTO
from anemia_junin.domain.ports import Reloj
from anemia_junin.domain.validators import (
    ErrorValidacion,
    normalizar_distrito,
    normalizar_nombre,
    validar_altitud,
    validar_distrito,
    validar_nombre,
    validar_peso_kg,
    validar_telefono,
)


class ActualizacionVaciaError(Exception):
    pass


class ActualizarNino:
    def __init__(self, uow_factory, reloj: Reloj) -> None:
        self._uow_factory = uow_factory
        self._reloj = reloj

    def ejecutar(self, dni: str, dto: ActualizarNinoDTO) -> NinoSalidaDTO:
        # Verificar que haya al menos un campo
        campos = [dto.peso_g, dto.distrito, dto.altitud_msnm, dto.cuidador, dto.telefono]
        if all(v is None for v in campos):
            raise ActualizacionVaciaError("Se requiere al menos un campo para actualizar")

        errores: dict[str, list[str]] = {}

        if dto.peso_g is not None:
            err, _ = validar_peso_kg(dto.peso_g / 1000)
            errores["peso_kg"] = err

        if dto.distrito is not None:
            errores["distrito"] = validar_distrito(dto.distrito)

        if dto.altitud_msnm is not None:
            errores["altitud_msnm"] = validar_altitud(dto.altitud_msnm)

        if dto.cuidador is not None:
            errores["cuidador"] = validar_nombre(dto.cuidador)

        if dto.telefono is not None:
            errores["telefono"] = validar_telefono(dto.telefono)

        ErrorValidacion.si_hay_errores(errores)

        ahora = self._reloj.ahora_utc()

        with self._uow_factory() as uow:
            nino = uow.ninos.obtener_por_dni(dni)
            if nino is None:
                raise NinoNoEncontradoError(f"Niño con DNI {dni} no encontrado")

            if dto.peso_g is not None:
                nino.peso_g = dto.peso_g
            if dto.distrito is not None:
                nino.distrito = normalizar_distrito(dto.distrito)
            if dto.altitud_msnm is not None:
                nino.altitud_msnm = int(dto.altitud_msnm)
            if dto.cuidador is not None:
                nino.cuidador = normalizar_nombre(dto.cuidador)
            if dto.telefono is not None:
                nino.telefono = dto.telefono if dto.telefono else None

            nino.updated_at = ahora
            uow.ninos.actualizar(nino)

        return nino_a_dto(nino)
