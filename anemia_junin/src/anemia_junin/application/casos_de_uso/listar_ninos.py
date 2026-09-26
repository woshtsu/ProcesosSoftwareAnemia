"""Caso de uso: Listar Niños — HIST-1.4 / HU-04."""

from __future__ import annotations

from anemia_junin.application.dto import FiltroListaDTO, NinoResumenDTO, PaginaDTO
from anemia_junin.domain.ports import FiltroNinos, Reloj


class ListarNinos:
    def __init__(self, uow_factory, reloj: Reloj) -> None:
        self._uow_factory = uow_factory
        self._reloj = reloj

    def ejecutar(self, dto: FiltroListaDTO) -> PaginaDTO:
        filtro = FiltroNinos(
            q=dto.q,
            distrito=dto.distrito,
            clasificacion=dto.clasificacion,
            pagina=dto.pagina,
            tamano=dto.tamano,
            fecha_referencia=self._reloj.hoy(),
        )

        with self._uow_factory() as uow:
            pagina = uow.ninos.listar(filtro)

        items = [
            NinoResumenDTO(
                dni=item["nino"].dni,
                nombres=item["nino"].nombres,
                apellidos=item["nino"].apellidos,
                fecha_nacimiento=item["nino"].fecha_nacimiento,
                sexo=item["nino"].sexo,
                distrito=item["nino"].distrito,
                clasificacion_ultimo_dosaje=item["clasificacion_actual"],
            )
            for item in pagina.items
        ]

        return PaginaDTO(
            items=items,
            total=pagina.total,
            pagina=pagina.pagina,
            tamano=pagina.tamano,
        )
