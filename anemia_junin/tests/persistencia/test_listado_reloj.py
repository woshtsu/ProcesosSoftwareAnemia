"""
El listado de seguimiento activo (6-59 meses) usa el puerto Reloj, no date.today()
(ADR-001: tiempo testeable). Atiende DEV-100 punto 7.
"""

from __future__ import annotations

from datetime import date, datetime
from functools import partial

import pytest

from anemia_junin.adapters.outbound.sqlite.migraciones import migrar
from anemia_junin.adapters.outbound.sqlite.unidad_de_trabajo import UnidadDeTrabajo
from anemia_junin.application.casos_de_uso.listar_ninos import ListarNinos
from anemia_junin.application.dto import FiltroListaDTO
from anemia_junin.domain.entities import Nino, Sexo, TipoNacimiento
from anemia_junin.domain.ports import FiltroNinos


class RelojFijo:
    def __init__(self, hoy: date) -> None:
        self._hoy = hoy

    def ahora_utc(self) -> datetime:
        return datetime.combine(self._hoy, datetime.min.time())

    def hoy(self) -> date:
        return self._hoy


@pytest.fixture
def uow_factory(tmp_path):
    db = str(tmp_path / "reloj.db")
    migrar(db)
    fabrica = partial(UnidadDeTrabajo, db)
    with fabrica() as uow:
        uow.ninos.guardar(Nino.nuevo(
            dni="40000001", nombres="Andrés", apellidos="Tapia Huanca",
            fecha_nacimiento=date(2020, 1, 15), sexo=Sexo.M,
            tipo_nacimiento=TipoNacimiento.TERMINO, peso_g=12000, distrito="Pampas",
            altitud_msnm=3276, cuidador="Carmen Huanca", telefono=None,
            ahora=datetime(2021, 1, 1),
        ))
    return fabrica


@pytest.mark.parametrize(
    ("hoy", "esperado"),
    [
        (date(2020, 7, 14), 0),   # 5 meses: aún no entra al seguimiento
        (date(2020, 7, 15), 1),   # 6 meses exactos
        (date(2024, 12, 15), 1),  # 59 meses
        (date(2025, 1, 15), 0),   # 60 meses: sale del seguimiento
    ],
)
def test_ventana_6_59_meses_segun_reloj(uow_factory, hoy, esperado):
    resultado = ListarNinos(uow_factory, RelojFijo(hoy)).ejecutar(FiltroListaDTO())
    assert resultado.total == esperado


def test_repositorio_exige_fecha_referencia(uow_factory):
    with uow_factory() as uow, pytest.raises(ValueError, match="Reloj"):
        uow.ninos.listar(FiltroNinos())
