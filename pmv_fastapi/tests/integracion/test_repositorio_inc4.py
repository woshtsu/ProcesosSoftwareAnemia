"""CP-304 a CP-309: persistencia del Incremento 4 (recordatorios y barreras) con SQLAlchemy y SQLite en memoria, y
paridad del repositorio en memoria."""

from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria
from app.adapters.outbound.persistence.sqlalchemy_repo import RepositorioSQLAlchemy
from app.domain.model.barrera import Barrera, FuenteBarrera, TipoBarrera
from app.domain.model.entidades import Nino
from app.domain.model.errores import ConflictoBarrera, ConflictoRecordatorio
from app.domain.model.notificacion import (
    CanalEnvio,
    EstadoRecordatorio,
    OrigenRespuesta,
    Recordatorio,
    RespuestaTutor,
    TipoRecordatorio,
)
from tests.conftest import datos_nino


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


def recordatorio(nino, codigo="DHx", programada=date(2026, 9, 28), tipo=TipoRecordatorio.CITA_DEL_DIA, **cambios):
    base = dict(
        nino_id=nino.id,
        codigo_control=codigo,
        fecha_programada=programada,
        tipo=tipo,
        canal=CanalEnvio.WHATSAPP,
        estado=EstadoRecordatorio.ENVIADO,
        destino="987654321",
        mensaje="Hola",
        generado_por="enf",
        id_externo=f"wamid.{codigo}{tipo}",
    )
    base.update(cambios)
    return Recordatorio(**base)


def barrera(nino, tipo=TipoBarrera.TRANSPORTE, fuente=FuenteBarrera.PERSONAL, fecha=date(2026, 9, 20), **cambios):
    return Barrera(nino_id=nino.id, tipo=tipo, fuente=fuente, fecha=fecha, registrado_por="enf", **cambios)


def test_cp304_recordatorios_se_guardan_se_actualizan_y_son_unicos_por_nino_control_y_tipo(repo):
    nino = nuevo_nino(repo)
    r = repo.agregar_recordatorio(recordatorio(nino))
    guardado = repo.obtener_recordatorio(r.id)
    assert guardado.clave == r.clave and guardado.estado == EstadoRecordatorio.ENVIADO and guardado.enviado_en is None
    assert guardado.creado_en.tzinfo is not None and repo.obtener_recordatorio("no-existe") is None
    with pytest.raises(ConflictoRecordatorio):
        repo.agregar_recordatorio(recordatorio(nino, id_externo="otro"))
    # el mismo control con otro tipo, o la misma fecha de otro control, sí se admite
    repo.agregar_recordatorio(recordatorio(nino, tipo=TipoRecordatorio.VENCIDO))
    repo.agregar_recordatorio(recordatorio(nino, codigo="DHc1"))
    guardado.estado = EstadoRecordatorio.LEIDO
    guardado.respuesta, guardado.origen_respuesta = RespuestaTutor.REPROGRAMAR, OrigenRespuesta.WHATSAPP
    guardado.fecha_reprogramada, guardado.respondido_por = date(2026, 10, 5), "whatsapp"
    guardado.respondido_en = guardado.enviado_en = datetime(2026, 9, 28, 15, tzinfo=UTC)
    repo.actualizar_recordatorio(guardado)
    nuevo = repo.obtener_recordatorio(r.id)
    assert nuevo.estado == EstadoRecordatorio.LEIDO and nuevo.respuesta == RespuestaTutor.REPROGRAMAR
    assert nuevo.fecha_reprogramada == date(2026, 10, 5) and nuevo.origen_respuesta == OrigenRespuesta.WHATSAPP
    assert nuevo.respondido_por == "whatsapp" and nuevo.enviado_en == datetime(2026, 9, 28, 15, tzinfo=UTC)
    assert nuevo.id == r.id and nuevo.nino_id == nino.id


def test_cp305_listar_recordatorios_filtra_por_estado_dia_nino_y_limite_y_ordena_el_mas_reciente_primero(repo):
    uno, dos = nuevo_nino(repo), nuevo_nino(repo, dni="71234568")
    ahora_ = datetime.now(UTC)
    a = repo.agregar_recordatorio(recordatorio(uno, creado_en=ahora_ - timedelta(days=3)))
    b = repo.agregar_recordatorio(
        recordatorio(uno, codigo="DHc1", estado=EstadoRecordatorio.FALLIDO, creado_en=ahora_ - timedelta(days=1))
    )
    c = repo.agregar_recordatorio(recordatorio(dos, creado_en=ahora_))
    assert [r.id for r in repo.listar_recordatorios()] == [c.id, b.id, a.id]
    assert [r.id for r in repo.listar_recordatorios(limite=2)] == [c.id, b.id]
    assert [r.id for r in repo.listar_recordatorios(estado="FALLIDO")] == [b.id]
    assert [r.id for r in repo.listar_recordatorios(nino_id=uno.id)] == [b.id, a.id]
    hoy_local = (ahora_ - timedelta(hours=5)).date()
    assert [r.id for r in repo.listar_recordatorios(desde=hoy_local)] == [c.id]
    assert [r.id for r in repo.listar_recordatorios(hasta=hoy_local - timedelta(days=2))] == [a.id]
    assert [r.id for r in repo.listar_recordatorios(desde=hoy_local - timedelta(days=1), hasta=hoy_local)] == [
        c.id,
        b.id,
    ]


def test_cp306_los_recordatorios_se_buscan_por_id_externo_y_para_responder_por_mensaje_o_por_celular(repo):
    uno, dos = nuevo_nino(repo), nuevo_nino(repo, dni="71234568")
    ahora_ = datetime.now(UTC)
    viejo = repo.agregar_recordatorio(recordatorio(uno, creado_en=ahora_ - timedelta(days=2), id_externo="wamid.viejo"))
    nuevo = repo.agregar_recordatorio(recordatorio(uno, codigo="DHc1", creado_en=ahora_, id_externo="wamid.nuevo"))
    respondido = recordatorio(uno, codigo="DHc2", creado_en=ahora_ + timedelta(seconds=1), id_externo="wamid.resp")
    respondido.respuesta, respondido.respondido_en = RespuestaTutor.CONFIRMA, ahora_
    repo.agregar_recordatorio(respondido)
    repo.agregar_recordatorio(
        recordatorio(
            uno,
            codigo="DHx2",
            estado=EstadoRecordatorio.FALLIDO,
            creado_en=ahora_ + timedelta(seconds=2),
            id_externo=None,
        )
    )
    repo.agregar_recordatorio(recordatorio(dos, destino="911111111", canal=CanalEnvio.SMS, id_externo="sms-1"))
    assert repo.obtener_por_id_externo("wamid.viejo").id == viejo.id and repo.obtener_por_id_externo("nada") is None
    # por el mensaje al que responde
    assert repo.buscar_para_respuesta("wamid.viejo", "987654321").id == viejo.id
    # sin contexto: el último enviado por WhatsApp a ese celular que no tiene respuesta ni falló
    assert repo.buscar_para_respuesta(None, "987654321").id == nuevo.id
    assert repo.buscar_para_respuesta("wamid.desconocido", "987654321").id == nuevo.id
    assert repo.buscar_para_respuesta(None, "911111111") is None  # SMS: no recibe respuestas por WhatsApp
    assert (
        repo.buscar_para_respuesta("wamid.desconocido", None) is None and repo.buscar_para_respuesta(None, None) is None
    )
    assert repo.buscar_para_respuesta(None, "900000000") is None


def test_cp307_barreras_se_guardan_se_listan_y_no_se_repiten_por_nino_tipo_fecha_y_fuente(repo):
    nino = nuevo_nino(repo)
    vieja = repo.agregar_barrera(barrera(nino, fecha=date(2026, 8, 1)))
    reciente = repo.agregar_barrera(barrera(nino, TipoBarrera.OLVIDO, fecha=date(2026, 9, 20)))
    misma_fecha = repo.agregar_barrera(barrera(nino, TipoBarrera.OTRA, fecha=date(2026, 9, 20), detalle="Lluvia"))
    assert {b.id for b in repo.listar_barreras(nino.id)[:2]} == {reciente.id, misma_fecha.id}
    assert repo.listar_barreras(nino.id)[2].id == vieja.id and repo.listar_barreras("otro") == []
    guardada = repo.listar_barreras(nino.id)[-1]
    assert guardada.tipo == TipoBarrera.TRANSPORTE and guardada.fuente == FuenteBarrera.PERSONAL
    assert guardada.creado_en.tzinfo is not None and guardada.recordatorio_id is None
    with pytest.raises(ConflictoBarrera) as e:
        repo.agregar_barrera(barrera(nino, fecha=date(2026, 8, 1)))
    assert e.value.id_existente == vieja.id
    # con otra fuente o con otra fecha sí se admite
    repo.agregar_barrera(barrera(nino, fecha=date(2026, 8, 1), fuente=FuenteBarrera.VISITA))
    assert repo.obtener_equivalente(nino.id, "TRANSPORTE", date(2026, 8, 1), "VISITA") is not None
    assert repo.obtener_equivalente(nino.id, "TRANSPORTE", date(2026, 8, 2), "VISITA") is None


def test_cp308_barreras_desde_agrupa_por_nino_en_una_consulta_y_enlaza_el_recordatorio(repo):
    uno, dos = nuevo_nino(repo), nuevo_nino(repo, dni="71234568")
    r = repo.agregar_recordatorio(recordatorio(uno))
    repo.agregar_barrera(barrera(uno, fecha=date(2026, 6, 1)))
    repo.agregar_barrera(
        barrera(
            uno, TipoBarrera.ECONOMICA, FuenteBarrera.RESPUESTA_RECORDATORIO, date(2026, 9, 25), recordatorio_id=r.id
        )
    )
    repo.agregar_barrera(barrera(dos, fecha=date(2026, 9, 1)))
    agrupadas = repo.barreras_desde(date(2026, 8, 1))
    assert set(agrupadas) == {uno.id, dos.id} and len(agrupadas[uno.id]) == 1 and len(agrupadas[dos.id]) == 1
    assert agrupadas[uno.id][0].recordatorio_id == r.id and repo.barreras_desde(date(2026, 10, 1)) == {}
    assert len(repo.barreras_desde(date(2026, 1, 1))[uno.id]) == 2


def test_cp309_eliminar_por_origen_borra_tambien_barreras_y_recordatorios(repo):
    nino = nuevo_nino(repo)
    repo.agregar_barrera(barrera(nino))
    repo.agregar_recordatorio(recordatorio(nino))
    assert repo.eliminar_por_origen("SISTEMA") == 1
    assert repo.listar_barreras(nino.id) == [] and repo.listar_recordatorios() == []


def test_cp309_la_base_rechaza_lo_que_el_dominio_no_permite():
    r = RepositorioSQLAlchemy("sqlite:///:memory:")
    r.crear_esquema()
    nino = nuevo_nino(r)
    with pytest.raises(IntegrityError):  # tipo OTRA sin detalle
        r.agregar_barrera(barrera(nino, TipoBarrera.OTRA))
    sin_celular = recordatorio(nino, codigo="DHc1")
    sin_celular.respuesta = RespuestaTutor.CONFIRMA  # una respuesta exige la hora en que se registró
    with pytest.raises(IntegrityError):
        r.agregar_recordatorio(sin_celular)
    r.engine.dispose()
