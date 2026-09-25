"""Caso de uso: Agregar Dosaje — HIST-1.2 / HU-02."""

from __future__ import annotations

from anemia_junin.application.casos_de_uso.consultar_expediente import NinoNoEncontradoError
from anemia_junin.application.conversores import dosaje_a_dto
from anemia_junin.application.dto import CrearDosajeDTO, DosajeSalidaDTO
from anemia_junin.domain.clasificador import ClasificadorHemoglobina
from anemia_junin.domain.entities import Dosaje
from anemia_junin.domain.ports import Reloj
from anemia_junin.domain.validators import (
    ErrorValidacion,
    validar_altitud,
    validar_fecha_dosaje,
)


class AgregarDosaje:
    def __init__(
        self,
        uow_factory,
        clasificador: ClasificadorHemoglobina,
        reloj: Reloj,
    ) -> None:
        self._uow_factory = uow_factory
        self._clasificador = clasificador
        self._reloj = reloj

    def ejecutar(self, dni: str, dto: CrearDosajeDTO) -> DosajeSalidaDTO:
        ahora = self._reloj.ahora_utc()
        hoy = self._reloj.hoy()

        with self._uow_factory() as uow:
            nino = uow.ninos.obtener_por_dni(dni)
            if nino is None:
                raise NinoNoEncontradoError(f"Niño con DNI {dni} no encontrado")

            errores: dict[str, list[str]] = {}

            err_fecha, edad_meses = validar_fecha_dosaje(
                dto.fecha_dosaje, nino.fecha_nacimiento, hoy
            )
            errores["fecha_dosaje"] = err_fecha
            errores["altitud_msnm"] = validar_altitud(dto.altitud_msnm)

            if not (20 <= dto.hb_observada_ddl <= 250):
                errores["hb_observada"] = ["Fuera de rango permitido (2.0–25.0 g/dL)"]

            ErrorValidacion.si_hay_errores(errores)

            resultado = self._clasificador.clasificar(
                hb_observada_ddl=dto.hb_observada_ddl,
                altitud_msnm=dto.altitud_msnm,
                edad_meses=edad_meses,
            )

            dosaje = Dosaje.nuevo(
                nino_id=nino.id,
                fecha_dosaje=dto.fecha_dosaje,
                hb_observada_ddl=dto.hb_observada_ddl,
                altitud_msnm=dto.altitud_msnm,
                ajuste_ddl=resultado.ajuste_ddl,
                hb_ajustada_ddl=resultado.hb_ajustada_ddl,
                edad_meses=edad_meses,
                clasificacion=resultado.clasificacion,
                version_normativa=resultado.version_normativa,
                advertencias=resultado.advertencias,
                ahora=ahora,
            )

            uow.dosajes.guardar(dosaje)

        return dosaje_a_dto(dosaje)
