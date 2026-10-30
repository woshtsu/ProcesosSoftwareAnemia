"""CP-286 a CP-293: persistencia del Incremento 3 (visitas, bitácora de operaciones y conflictos) con SQLAlchemy y SQLite
en memoria, y paridad del repositorio en memoria."""

from datetime import date

import pytest
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria
from app.adapters.outbound.persistence.sqlalchemy_repo import _OPERACION, RepositorioSQLAlchemy
from app.domain.model.entidades import Nino
from app.domain.model.errores import ConflictoVisita
from app.domain.model.origen import OrigenDatos
from app.domain.model.sincronizacion import (
    ConflictoSincronizacion,
    EstadoConflicto,
    OperacionSincronizada,
    ResolucionConflicto,
    ResultadoOperacion,
)
from app.domain.model.tiempo import ahora
from app.domain.model.visita import ConsumoSuplemento, ResultadoVisita, VisitaDomiciliaria
from tests.conftest import datos_nino, evaluacion_de


@pytest.fixture(params=["sqlalchemy", "memoria"])
def repo(request):
    if request.param == "memoria":
        yield RepositorioEnMemoria()
        return
    r = RepositorioSQLAlchemy("sqlite:///:memory:")
    r.crear_esquema()
    yield r
    r.engine.dispose()


def nuevo_nino(repo, **cambios):
    nino = Nino(**datos_nino(**cambios), registrado_por="enf")
    repo.guardar(nino)
    return nino


def operacion(id_operacion="op-1", resultado=ResultadoOperacion.APLICADA, id_cliente="tmp-1", **cambios):
    return OperacionSincronizada(
        id_operacion, "REGISTRAR_NINO", "tab-1", resultado, "nino-1", id_cliente, ahora(), **cambios
    )


def test_cp286_visitas_se_guardan_se_listan_y_se_actualizan(repo):
    nino = nuevo_nino(repo)
    otro = nuevo_nino(repo, dni="71234568")
    viejo = repo.agregar_visita(
        VisitaDomiciliaria(
            nino.id, date(2026, 9, 1), ResultadoVisita.REALIZADA, "enf", ConsumoSuplemento.NO, "Sin sulfato"
        )
    )
    reciente = repo.agregar_visita(VisitaDomiciliaria(nino.id, date(2026, 9, 20), ResultadoVisita.NO_ENCONTRADO, "tec"))
    repo.agregar_visita(VisitaDomiciliaria(otro.id, date(2026, 9, 5), ResultadoVisita.RECHAZADA, "enf"))
    assert [v.id for v in repo.listar_visitas(nino.id)] == [reciente.id, viejo.id]
    assert repo.listar_visitas("nadie") == []
    del_dia = repo.obtener_visita_del_dia(nino.id, date(2026, 9, 1))
    assert (del_dia.consume_suplemento, del_dia.observaciones, del_dia.creado_en.tzinfo is not None) == (
        ConsumoSuplemento.NO,
        "Sin sulfato",
        True,
    )
    assert repo.obtener_visita_del_dia(nino.id, date(2026, 9, 2)) is None
    assert repo.ultimas_visitas({nino.id, otro.id, "nadie"}) == {nino.id: date(2026, 9, 20), otro.id: date(2026, 9, 5)}
    assert repo.ultimas_visitas({otro.id}) == {otro.id: date(2026, 9, 5)}
    del_dia.resultado, del_dia.observaciones = ResultadoVisita.REALIZADA, None
    del_dia.consume_suplemento = ConsumoSuplemento.SI
    repo.actualizar_visita(del_dia)
    assert repo.obtener_visita_del_dia(nino.id, date(2026, 9, 1)).observaciones is None


def test_cp287_una_segunda_visita_el_mismo_dia_se_traduce_a_conflicto_de_visita(repo):
    nino = nuevo_nino(repo)
    repo.agregar_visita(VisitaDomiciliaria(nino.id, date(2026, 9, 1), ResultadoVisita.REALIZADA, "enf"))
    with pytest.raises(ConflictoVisita, match="2026-09-01"):
        repo.agregar_visita(VisitaDomiciliaria(nino.id, date(2026, 9, 1), ResultadoVisita.RECHAZADA, "otra"))
    assert len(repo.listar_visitas(nino.id)) == 1


def test_cp288_la_bitacora_es_idempotente_por_id_operacion(repo):
    assert repo.registrar_operacion(operacion()) is True
    assert repo.registrar_operacion(operacion(resultado=ResultadoOperacion.DUPLICADA)) is False
    guardada = repo.obtener_operacion("op-1")
    assert (guardada.resultado, guardada.id_recurso, guardada.id_cliente) == (
        ResultadoOperacion.APLICADA,
        "nino-1",
        "tmp-1",
    )
    assert guardada.recibida_en.tzinfo is not None and guardada.fecha_local.tzinfo is not None
    assert repo.obtener_operacion("nada") is None and repo.contar_operaciones() == 1


def test_cp289_el_id_cliente_solo_mapea_operaciones_aplicadas_duplicadas_o_resueltas(repo):
    repo.registrar_operacion(operacion("op-1", ResultadoOperacion.CONFLICTO, id_cliente="tmp-1"))
    assert repo.id_nino_de_cliente("tab-1", "tmp-1") is None  # en conflicto todavía no se confirma
    repo.marcar_operacion_resuelta("op-1")
    assert repo.id_nino_de_cliente("tab-1", "tmp-1") == "nino-1"
    assert repo.obtener_operacion("op-1").resultado == ResultadoOperacion.RESUELTA
    assert repo.id_nino_de_cliente("otra-tableta", "tmp-1") is None
    repo.registrar_operacion(operacion("op-2", ResultadoOperacion.DUPLICADA, id_cliente="tmp-2"))
    assert repo.id_nino_de_cliente("tab-1", "tmp-2") == "nino-1"


def conflicto_de(nino_id, id_operacion="op-1", **cambios):
    return ConflictoSincronizacion(
        id_operacion=id_operacion,
        tipo="REGISTRAR_EVALUACION",
        motivo="x" * 600,
        nino_id=nino_id,
        id_recurso="ev-1",
        datos_cliente={"fecha": "2026-09-25", "hemoglobina_observada": 7.0, "anidado": {"a": [1, 2]}},
        datos_servidor={"id": "ev-1", "hemoglobina_observada": 12.0},
        registrado_por="enf",
        **cambios,
    )


def test_cp290_conflictos_se_guardan_con_json_se_filtran_y_se_actualizan(repo):
    nino = nuevo_nino(repo)
    repo.registrar_operacion(operacion("op-1"))
    repo.registrar_operacion(operacion("op-2", id_cliente=None))
    primero = repo.guardar_conflicto(conflicto_de(nino.id, "op-1"))
    segundo = repo.guardar_conflicto(conflicto_de(nino.id, "op-2"))
    leido = repo.obtener_conflicto(primero.id)
    assert leido.datos_cliente["anidado"] == {"a": [1, 2]} and leido.datos_servidor["id"] == "ev-1"
    assert (leido.estado, leido.resolucion, leido.resuelto_en) == (EstadoConflicto.PENDIENTE, None, None)
    assert len(leido.motivo) <= 600 and leido.creado_en.tzinfo is not None
    assert repo.obtener_conflicto("nada") is None
    assert repo.obtener_conflicto_de_operacion("op-2").id == segundo.id
    assert repo.obtener_conflicto_de_operacion("nada") is None
    leido.estado, leido.resolucion, leido.resuelto_en, leido.resuelto_por = (
        EstadoConflicto.RESUELTO,
        ResolucionConflicto.APLICAR_CLIENTE,
        ahora(),
        "tec",
    )
    repo.actualizar_conflicto(leido)
    assert [c.id for c in repo.listar_conflictos("PENDIENTE")] == [segundo.id]
    resuelto = repo.listar_conflictos("RESUELTO")[0]
    assert (resuelto.resolucion, resuelto.resuelto_por, resuelto.resuelto_en.tzinfo is not None) == (
        ResolucionConflicto.APLICAR_CLIENTE,
        "tec",
        True,
    )
    assert {c.id for c in repo.listar_conflictos()} == {primero.id, segundo.id}


def test_cp291_actualizar_evaluacion_y_asistencia_persiste_los_cambios(repo):
    nino = nuevo_nino(repo)
    ev = repo.agregar_evaluacion(evaluacion_de(date(2026, 9, 1), "SIN_ANEMIA", nino_id=nino.id))
    ev.hemoglobina_observada, ev.peso_kg = 7.0, None
    ev.clasificacion = type(ev.clasificacion)("SEVERA")
    repo.actualizar_evaluacion(ev)
    guardada = repo.obtener(nino.id).evaluaciones[0]
    assert (guardada.hemoglobina_observada, guardada.peso_kg, guardada.clasificacion.value) == (7.0, None, "SEVERA")


def test_cp292_eliminar_por_origen_tambien_borra_visitas_y_conflictos():
    repo = RepositorioSQLAlchemy("sqlite:///:memory:")
    repo.crear_esquema()
    dataset = Nino(
        **{**datos_nino(dni=None, nombres=None, apellidos=None, sexo=None, tutor_nombre=None, tutor_celular=None)},
        registrado_por="importador",
        origen=OrigenDatos.DATASET_DIRESA_JUNIN,
        codigo_origen="DJ-00001",
    )
    sistema = nuevo_nino(repo)
    repo.guardar(dataset)
    for n in (dataset, sistema):
        repo.agregar_visita(VisitaDomiciliaria(n.id, date(2026, 9, 1), ResultadoVisita.REALIZADA, "enf"))
    repo.registrar_operacion(operacion("op-1"))
    repo.guardar_conflicto(conflicto_de(dataset.id, "op-1"))
    assert repo.eliminar_por_origen("DATASET_DIRESA_JUNIN") == 1
    assert repo.listar_visitas(dataset.id) == [] and len(repo.listar_visitas(sistema.id)) == 1
    assert repo.listar_conflictos() == []
    repo.engine.dispose()


def test_cp293_otras_violaciones_de_integridad_no_se_confunden_con_duplicados():
    repo = RepositorioSQLAlchemy("sqlite:///:memory:")
    repo.crear_esquema()
    nino = nuevo_nino(repo)
    malo = VisitaDomiciliaria(nino.id, date(2026, 9, 1), ResultadoVisita.NO_ENCONTRADO, "enf", ConsumoSuplemento.SI)
    with pytest.raises(IntegrityError):  # la base también exige que solo una visita realizada diga si consume
        repo.agregar_visita(malo)
    sin_dispositivo = OperacionSincronizada("op-9", "REGISTRAR_NINO", None, ResultadoOperacion.APLICADA)
    with pytest.raises(IntegrityError):  # una violación distinta de la clave primaria no se trata como reenvío
        repo.registrar_operacion(sin_dispositivo)
    with pytest.raises(IntegrityError), repo.Sesion.begin() as s:
        s.execute(
            insert(_OPERACION).values(
                id_operacion="op-8", tipo="X", id_dispositivo="d", resultado="BORRADA", recibida_en=ahora()
            )
        )
    repo.engine.dispose()
