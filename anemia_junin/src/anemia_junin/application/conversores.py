"""Utilidades compartidas de la capa de aplicación."""

from __future__ import annotations

from anemia_junin.application.dto import DosajeSalidaDTO, NinoSalidaDTO
from anemia_junin.domain.entities import Dosaje, Nino


def nino_a_dto(nino: Nino) -> NinoSalidaDTO:
    return NinoSalidaDTO(
        id=nino.id,
        dni=nino.dni,
        nombres=nino.nombres,
        apellidos=nino.apellidos,
        fecha_nacimiento=nino.fecha_nacimiento,
        sexo=nino.sexo,
        tipo_nacimiento=nino.tipo_nacimiento,
        peso_kg=round(nino.peso_g / 1000, 3),
        distrito=nino.distrito,
        altitud_msnm=nino.altitud_msnm,
        cuidador=nino.cuidador,
        telefono=nino.telefono,
        created_at=nino.created_at,
        updated_at=nino.updated_at,
    )


def dosaje_a_dto(dosaje: Dosaje) -> DosajeSalidaDTO:
    return DosajeSalidaDTO(
        id=dosaje.id,
        nino_id=dosaje.nino_id,
        fecha_dosaje=dosaje.fecha_dosaje,
        hb_observada=round(dosaje.hb_observada_ddl / 10, 1),
        altitud_msnm=dosaje.altitud_msnm,
        ajuste_gdl=round(dosaje.ajuste_ddl / 10, 1),
        hb_ajustada=round(dosaje.hb_ajustada_ddl / 10, 1),
        edad_meses=dosaje.edad_meses,
        clasificacion=dosaje.clasificacion,
        version_normativa=dosaje.version_normativa,
        advertencias=dosaje.advertencias,
        created_at=dosaje.created_at,
    )
