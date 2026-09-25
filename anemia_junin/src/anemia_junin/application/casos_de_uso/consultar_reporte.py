"""Caso de uso: Consultar Reporte de Registros — HIST-1.5 / HU-05."""

from __future__ import annotations

from datetime import UTC, date, datetime, time

import pytz

from anemia_junin.application.dto import CalidadRegistroDTO, PeriodoReporteDTO, ReporteRegistrosDTO
from anemia_junin.domain.validators import ErrorValidacion

_TZ_LIMA = pytz.timezone("America/Lima")


def _a_utc_inicio(d: date) -> datetime:
    """Convierte fecha local Lima → UTC inicio del día."""
    local_dt = _TZ_LIMA.localize(datetime.combine(d, time.min))
    return local_dt.astimezone(UTC).replace(tzinfo=None)


def _a_utc_fin(d: date) -> datetime:
    """Convierte fecha local Lima → UTC fin del día."""
    local_dt = _TZ_LIMA.localize(datetime.combine(d, time.max))
    return local_dt.astimezone(UTC).replace(tzinfo=None)


class ConsultarReporte:
    def __init__(self, uow_factory) -> None:
        self._uow_factory = uow_factory

    def ejecutar(self, dto: PeriodoReporteDTO) -> ReporteRegistrosDTO:
        errores: dict[str, list[str]] = {}
        if not isinstance(dto.desde, date):
            errores["desde"] = ["Fecha inválida"]
        if not isinstance(dto.hasta, date):
            errores["hasta"] = ["Fecha inválida"]
        if not errores:
            if dto.hasta < dto.desde:
                errores["hasta"] = ["Debe ser posterior o igual a 'desde'"]
        ErrorValidacion.si_hay_errores(errores)

        desde_utc = _a_utc_inicio(dto.desde)
        hasta_utc = _a_utc_fin(dto.hasta)
        desde_iso = dto.desde.isoformat()
        hasta_iso = dto.hasta.isoformat()

        with self._uow_factory() as uow:
            # Delegar las consultas de reporte al repositorio (que sí conoce SQLite)
            datos_reporte = uow.ninos.consultar_reporte(
                desde_utc=desde_utc,
                hasta_utc=hasta_utc,
                desde_iso=desde_iso,
                hasta_iso=hasta_iso,
            )
            conteos = uow.intentos.contar_en_periodo(desde_utc, hasta_utc)

        ninos_reg = datos_reporte["ninos_registrados"]
        dosajes_reg = datos_reporte["dosajes_registrados"]
        dist_clas = datos_reporte["distribucion_clasificacion"]
        dist_dist = datos_reporte["distribucion_distrito"]

        aceptados = conteos["ACEPTADO"]
        rechazados = conteos["RECHAZADO"]
        total_intentos = aceptados + rechazados

        tasa = None if total_intentos == 0 else round(aceptados / total_intentos * 100, 1)

        return ReporteRegistrosDTO(
            periodo_desde=dto.desde,
            periodo_hasta=dto.hasta,
            ninos_registrados=ninos_reg,
            dosajes_registrados=dosajes_reg,
            distribucion_clasificacion=dist_clas,
            distribucion_distrito=dist_dist,
            calidad_registro=CalidadRegistroDTO(
                intentos_aceptados=aceptados,
                intentos_rechazados=rechazados,
                tasa_aceptacion_pct=tasa,
            ),
        )
