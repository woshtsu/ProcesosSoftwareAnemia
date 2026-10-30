"""CP-225 a CP-262: sincronización de operaciones sin conexión y resolución de conflictos (HIST-3.2 y HIST-3.3,
ADR-012). Caso de uso completo con el repositorio en memoria: idempotencia, mapeo de id_cliente, conflictos y su
resolución. Hoy = 28-sep-2026.
"""

import uuid
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

import pytest

from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria
from app.application.servicio_asistencia import ServicioAsistencia
from app.application.servicio_expediente import ServicioExpediente
from app.application.servicio_sincronizacion import ServicioSincronizacion
from app.application.servicio_visitas import ServicioVisitas
from app.domain.model.asistencia import AsistenciaControl, EstadoAsistencia
from app.domain.model.errores import ConflictoYaResuelto, ErrorValidacion, NoEncontrado
from app.domain.model.sincronizacion import (
    EstadoConflicto,
    OperacionEntrante,
    ResolucionConflicto,
    ResultadoOperacion,
)
from tests.conftest import RelojFijo, datos_nino, evaluacion_de, nino_de

APLICADA, DUPLICADA = ResultadoOperacion.APLICADA, ResultadoOperacion.DUPLICADA
CONFLICTO, RECHAZADA = ResultadoOperacion.CONFLICTO, ResultadoOperacion.RECHAZADA
BASE = datetime(2026, 9, 27, 8, 0)


class Mundo:
    """El servicio con su repositorio en memoria y atajos para armar operaciones."""

    def __init__(self):
        self.repo = RepositorioEnMemoria()
        reloj = RelojFijo()
        self.expediente = ServicioExpediente(self.repo, reloj)
        visitas = ServicioVisitas(self.repo, self.repo, reloj)
        self.servicio = ServicioSincronizacion(
            self.repo,
            self.repo,
            self.repo,
            self.expediente,
            ServicioAsistencia(self.repo, reloj),
            visitas,
            reloj,
        )
        self.minuto = 0

    def op(self, tipo, datos, *, id_cliente=None, nino=None, cliente=None, dispositivo="tab-1", id_operacion=None):
        self.minuto += 1
        return OperacionEntrante(
            id_operacion=id_operacion or str(uuid.uuid4()),
            tipo=tipo,
            id_dispositivo=dispositivo,
            fecha_local=BASE + timedelta(minutes=self.minuto),
            datos=datos,
            id_cliente=id_cliente,
            nino_id=nino,
            nino_id_cliente=cliente,
        )

    def sync(self, *operaciones, usuario="enf.rosa"):
        return self.servicio.sincronizar(list(operaciones), usuario)

    def uno(self, operacion):
        return self.sync(operacion)[0]


@pytest.fixture
def m():
    return Mundo()


def registro(dni="71234567", hb=12.4, fecha="2026-09-20", **cambios):
    nino = datos_nino(dni=dni, **cambios)
    nino["fecha_nacimiento"] = nino["fecha_nacimiento"].isoformat()
    return {
        "nino": nino,
        "evaluacion_inicial": {"fecha": fecha, "hemoglobina_observada": hb, "peso_kg": 8.1, "talla_cm": 69.5},
    }


def evaluacion(hb=11.0, fecha="2026-09-25"):
    return {"fecha": fecha, "hemoglobina_observada": hb, "peso_kg": 8.4, "talla_cm": 70.0}


def visita(**cambios):
    return {
        "fecha": "2026-09-22",
        "resultado": "REALIZADA",
        "consume_suplemento": "SI",
        "observaciones": "Bien",
    } | cambios


def guardar_nino(m, **cambios):
    """Niño del servidor con un DHx de 6 meses vencido (nace el 10-mar-2025), útil para asistencia."""
    nino = nino_de(date(2025, 3, 10), [(date(2025, 6, 10), "NO_APLICA")], **cambios)
    m.repo.guardar(nino)
    return nino


def asistencia(estado="ASISTIO", **cambios):
    return {"codigo": "DHx", "fecha_programada": "2025-09-10", "estado": estado, "motivo": None} | cambios


# --- Niño con su evaluación y mapeo del id temporal ---------------------------------------------------------------


def test_cp225_un_nino_nuevo_se_aplica_y_devuelve_el_mapeo_id_cliente_a_id(m):
    r = m.uno(m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-1"))
    assert (r.resultado, r.id_cliente) == (APLICADA, "tmp-1")
    nino = m.repo.obtener(r.id_recurso)
    assert nino.dni == "71234567" and nino.registrado_por == "enf.rosa" and len(nino.evaluaciones) == 1


def test_cp226_las_operaciones_posteriores_referencian_al_nino_por_su_id_cliente_en_el_mismo_lote(m):
    nuevo = m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-1")
    control = m.op("REGISTRAR_EVALUACION", evaluacion(), cliente="tmp-1")
    consulta = m.op("REGISTRAR_VISITA", visita(), cliente="tmp-1")
    r = m.sync(nuevo, control, consulta)
    assert [x.resultado for x in r] == [APLICADA, APLICADA, APLICADA]
    nino = m.repo.obtener(r[0].id_recurso)
    assert len(nino.evaluaciones) == 2 and r[1].id_recurso in {e.id for e in nino.evaluaciones}
    assert m.repo.listar_visitas(nino.id)[0].id == r[2].id_recurso


def test_cp227_el_lote_se_procesa_por_fecha_local_aunque_llegue_desordenado_y_responde_en_el_orden_recibido(m):
    nuevo = m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-1")
    control = m.op("REGISTRAR_EVALUACION", evaluacion(), cliente="tmp-1")
    r = m.sync(control, nuevo)  # la evaluación llega primero pero se hizo después
    assert [x.id_operacion for x in r] == [control.id_operacion, nuevo.id_operacion]
    assert [x.resultado for x in r] == [APLICADA, APLICADA]


def test_cp228_la_fecha_local_sin_zona_es_hora_de_peru_y_se_ordena_junto_a_las_que_si_la_tienen(m):
    nuevo = replace(m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-1"), fecha_local=datetime(2026, 9, 27, 7, 0))
    control = replace(
        m.op("REGISTRAR_EVALUACION", evaluacion(), cliente="tmp-1"),
        fecha_local=datetime(2026, 9, 27, 13, 0, tzinfo=UTC),
    )  # 07:00 en Perú son las 12:00 UTC: el niño se registró antes que su evaluación
    assert [x.resultado for x in m.sync(control, nuevo)] == [APLICADA, APLICADA]


# --- Idempotencia ------------------------------------------------------------------------------------------------------


def test_cp229_reenviar_el_mismo_lote_responde_duplicada_y_no_crea_nada(m):
    nino = guardar_nino(m)
    lote = [
        m.op("REGISTRAR_NINO", registro(dni="72000001"), id_cliente="tmp-1"),
        m.op("REGISTRAR_EVALUACION", evaluacion(), cliente="tmp-1"),
        m.op("REGISTRAR_ASISTENCIA", asistencia("NO_ASISTIO", motivo="Viaje"), nino=nino.id),
        m.op("REGISTRAR_VISITA", visita(), nino=nino.id),
    ]
    primero = m.sync(*lote)
    assert [r.resultado for r in primero] == [APLICADA] * 4
    antes = (len(m.repo.listar()), m.repo.contar_operaciones(), len(m.repo.listar_visitas(nino.id)))
    segundo = m.sync(*lote)
    assert [r.resultado for r in segundo] == [DUPLICADA] * 4
    assert [r.resultado_original for r in segundo] == [APLICADA] * 4
    assert [r.id_recurso for r in segundo] == [r.id_recurso for r in primero]
    assert segundo[0].id_cliente == "tmp-1" and segundo[1].id_cliente is None  # el mapeo se recupera en el reenvío
    despues = (len(m.repo.listar()), m.repo.contar_operaciones(), len(m.repo.listar_visitas(nino.id)))
    assert despues == antes
    assert sum(len(n.evaluaciones) for n in m.repo.listar()) == 3  # 1 del servidor + 2 del niño nuevo


def test_cp230_el_mismo_id_operacion_repetido_dentro_de_un_lote_se_aplica_una_sola_vez(m):
    operacion = m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-1")
    r = m.sync(operacion, operacion)
    assert [x.resultado for x in r] == [APLICADA, DUPLICADA]
    assert len(m.repo.listar()) == 1


def test_cp231_dos_dispositivos_pueden_usar_el_mismo_id_cliente_sin_mezclarse(m):
    a = m.uno(m.op("REGISTRAR_NINO", registro(dni="72000001"), id_cliente="tmp-1", dispositivo="A"))
    b = m.uno(m.op("REGISTRAR_NINO", registro(dni="72000002"), id_cliente="tmp-1", dispositivo="B"))
    ea = m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(), cliente="tmp-1", dispositivo="A"))
    assert ea.resultado == APLICADA
    assert len(m.repo.obtener(a.id_recurso).evaluaciones) == 2 and len(m.repo.obtener(b.id_recurso).evaluaciones) == 1


def test_cp232_si_otra_solicitud_gana_la_carrera_el_resultado_es_duplicada(m):
    class RepoConCarrera(RepositorioEnMemoria):
        def registrar_operacion(self, operacion):
            super().registrar_operacion(operacion)
            return False  # otra solicitud registró el mismo id_operacion justo antes

    m.repo.__class__ = RepoConCarrera
    r = m.uno(m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-1"))
    assert (r.resultado, r.resultado_original) == (DUPLICADA, APLICADA)
    guardar = guardar_nino(m, dni="73000001")
    conflicto = m.op("REGISTRAR_ASISTENCIA", asistencia("ASISTIO"), nino=guardar.id)
    m.repo.agregar_asistencia(
        AsistenciaControl(guardar.id, "DHx", date(2025, 9, 10), EstadoAsistencia.NO_ASISTIO, "x", "m")
    )
    assert m.uno(conflicto).resultado == DUPLICADA
    assert m.repo.listar_conflictos() == []  # no se abrió un conflicto de más


# --- (a) Niño con DNI existente ---------------------------------------------------------------------------------------


def test_cp233_mismo_dni_y_mismos_datos_se_mapea_sin_conflicto_y_el_id_cliente_apunta_al_existente(m):
    existente = m.uno(m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-A", dispositivo="A"))
    r = m.uno(m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-B", dispositivo="B"))
    assert (r.resultado, r.id_recurso, r.id_cliente) == (DUPLICADA, existente.id_recurso, "tmp-B")
    assert len(m.repo.listar()) == 1 and m.repo.listar_conflictos() == []
    control = m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(), cliente="tmp-B", dispositivo="B"))
    assert control.resultado == APLICADA and len(m.repo.obtener(existente.id_recurso).evaluaciones) == 2


def test_cp234_mismo_dni_y_mismos_datos_con_otra_evaluacion_inicial_agrega_la_evaluacion(m):
    existente = m.uno(m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-A"))
    r = m.uno(m.op("REGISTRAR_NINO", registro(fecha="2026-09-24", hb=11.0), id_cliente="tmp-B", dispositivo="B"))
    assert (r.resultado, r.id_recurso) == (APLICADA, existente.id_recurso) and "agregó" in r.mensaje
    assert sorted(e.fecha.day for e in m.repo.obtener(existente.id_recurso).evaluaciones) == [20, 24]


def test_cp235_mismo_dni_y_datos_distintos_es_conflicto_y_no_toca_al_nino(m):
    existente = m.uno(m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-A"))
    r = m.uno(
        m.op("REGISTRAR_NINO", registro(comunidad="Llacuas", nombres="Otra"), id_cliente="tmp-B", dispositivo="B")
    )
    assert r.resultado == CONFLICTO and r.id_cliente is None and r.id_recurso == existente.id_recurso
    assert "nombres" in r.mensaje and "comunidad" in r.mensaje
    conflicto = m.repo.obtener_conflicto(r.id_conflicto)
    assert conflicto.estado == EstadoConflicto.PENDIENTE and conflicto.nino_id == existente.id_recurso
    assert (
        conflicto.datos_servidor["comunidad"] == "Palmayoc"
        and conflicto.datos_cliente["nino"]["comunidad"] == "Llacuas"
    )
    assert m.repo.obtener(existente.id_recurso).comunidad == "Palmayoc"
    # Mientras el conflicto sigue pendiente, lo que depende del niño temporal se rechaza sin perderse.
    bloqueada = m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(), cliente="tmp-B", dispositivo="B"))
    assert bloqueada.resultado == RECHAZADA and "conflicto" in bloqueada.mensaje


def test_cp236_conservar_el_servidor_confirma_que_es_el_mismo_nino_y_destraba_lo_que_depende_de_el(m):
    existente = m.uno(m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-A"))
    conflictiva = m.op(
        "REGISTRAR_NINO",
        registro(fecha="2026-09-24", hb=11.0, comunidad="Llacuas"),
        id_cliente="tmp-B",
        dispositivo="B",
    )
    id_conflicto = m.uno(conflictiva).id_conflicto
    control = m.op("REGISTRAR_EVALUACION", evaluacion(hb=10.0, fecha="2026-09-26"), cliente="tmp-B", dispositivo="B")
    assert m.uno(control).resultado == RECHAZADA
    c = m.servicio.resolver_conflicto(id_conflicto, "CONSERVAR_SERVIDOR", "enf.rosa")
    assert (c.estado, c.resolucion, c.resuelto_por) == (
        EstadoConflicto.RESUELTO,
        ResolucionConflicto.CONSERVAR_SERVIDOR,
        "enf.rosa",
    )
    assert c.resuelto_en is not None
    nino = m.repo.obtener(existente.id_recurso)
    assert nino.comunidad == "Palmayoc"  # el servidor gana
    assert sorted(e.fecha.day for e in nino.evaluaciones) == [20, 24]  # pero se agrega la evaluación que no existía
    assert m.uno(control).resultado == APLICADA  # reenviada tras la resolución, ya encuentra al niño
    reenvio = m.uno(conflictiva)
    assert (reenvio.resultado, reenvio.resultado_original, reenvio.id_cliente) == (DUPLICADA, CONFLICTO, "tmp-B")
    assert reenvio.id_conflicto == id_conflicto


def test_cp237_aplicar_el_cliente_reemplaza_solo_los_campos_editables_y_agrega_la_evaluacion(m):
    existente = m.uno(m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-A"))
    r = m.uno(
        m.op(
            "REGISTRAR_NINO",
            registro(fecha="2026-09-24", hb=11.0, comunidad="Llacuas", altitud_m=3900, tutor_celular="912345678"),
            id_cliente="tmp-B",
            dispositivo="B",
        )
    )
    m.servicio.resolver_conflicto(r.id_conflicto, "APLICAR_CLIENTE", "tec.juan")
    nino = m.repo.obtener(existente.id_recurso)
    assert (nino.comunidad, nino.altitud_m, nino.tutor_celular) == ("Llacuas", 3900, "912345678")
    assert nino.nombres == "Luz Mery" and len(nino.evaluaciones) == 2
    assert nino.evaluaciones[-1].registrado_por == "enf.rosa"  # la evaluación conserva a quien la registró
    assert m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(), cliente="tmp-B", dispositivo="B")).resultado == APLICADA


def test_cp238_aplicar_el_cliente_no_sobrescribe_la_identidad_del_nino(m):
    m.uno(m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-A"))
    r = m.uno(
        m.op(
            "REGISTRAR_NINO", registro(nombres="Otra Persona", comunidad="Llacuas"), id_cliente="tmp-B", dispositivo="B"
        )
    )
    with pytest.raises(ErrorValidacion, match="identidad"):
        m.servicio.resolver_conflicto(r.id_conflicto, "APLICAR_CLIENTE", "enf")
    assert m.repo.obtener_conflicto(r.id_conflicto).estado == EstadoConflicto.PENDIENTE
    c = m.servicio.resolver_conflicto(
        r.id_conflicto, "DESCARTAR", "enf"
    )  # la salida: descartar o conservar al servidor
    assert c.resolucion == ResolucionConflicto.DESCARTAR
    descartada = m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(), cliente="tmp-B", dispositivo="B"))
    assert descartada.resultado == RECHAZADA  # descartar no confirma al niño: nada se le adjunta


def test_cp239_conflicto_de_evaluacion_inicial_con_el_nino_identico(m):
    existente = m.uno(m.op("REGISTRAR_NINO", registro(hb=12.4), id_cliente="tmp-A"))
    r = m.uno(m.op("REGISTRAR_NINO", registro(hb=9.0), id_cliente="tmp-B", dispositivo="B"))
    assert r.resultado == CONFLICTO and "hemoglobina" in r.mensaje
    conflicto = m.repo.obtener_conflicto(r.id_conflicto)
    assert conflicto.datos_servidor["evaluacion"]["hemoglobina_observada"] == 12.4
    m.servicio.resolver_conflicto(r.id_conflicto, "APLICAR_CLIENTE", "enf")
    evaluaciones = m.repo.obtener(existente.id_recurso).evaluaciones
    assert len(evaluaciones) == 1 and evaluaciones[0].hemoglobina_observada == 9.0
    assert evaluaciones[0].clasificacion.value == "SEVERA" and evaluaciones[0].hemoglobina_ajustada == 6.5


def test_cp239b_conservar_el_servidor_en_un_conflicto_de_evaluacion_inicial_no_cambia_la_hemoglobina(m):
    existente = m.uno(m.op("REGISTRAR_NINO", registro(hb=12.4), id_cliente="tmp-A"))
    r = m.uno(m.op("REGISTRAR_NINO", registro(hb=9.0), id_cliente="tmp-B", dispositivo="B"))
    m.servicio.resolver_conflicto(r.id_conflicto, "CONSERVAR_SERVIDOR", "enf")
    evaluaciones = m.repo.obtener(existente.id_recurso).evaluaciones
    assert [e.hemoglobina_observada for e in evaluaciones] == [12.4]


# --- (b) Evaluación ----------------------------------------------------------------------------------------------------


def test_cp240_misma_fecha_y_misma_hemoglobina_es_duplicada_logica_y_no_agrega_otra(m):
    nino = guardar_nino(m)
    primera = m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(hb=12.0, fecha="2026-09-25"), nino=nino.id))
    otra_tableta = m.uno(
        m.op("REGISTRAR_EVALUACION", evaluacion(hb=12.0, fecha="2026-09-25"), nino=nino.id, dispositivo="B")
    )
    assert (primera.resultado, otra_tableta.resultado) == (APLICADA, DUPLICADA)
    assert otra_tableta.id_recurso == primera.id_recurso
    assert len(m.repo.obtener(nino.id).evaluaciones) == 2


def test_cp241_misma_fecha_y_distinta_hemoglobina_es_conflicto_y_aplicar_cliente_la_reemplaza(m):
    nino = guardar_nino(m)
    primera = m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(hb=12.0, fecha="2026-09-25"), nino=nino.id))
    r = m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(hb=7.0, fecha="2026-09-25"), nino=nino.id, dispositivo="B"))
    assert (r.resultado, r.id_recurso) == (CONFLICTO, primera.id_recurso)
    m.servicio.resolver_conflicto(r.id_conflicto, "APLICAR_CLIENTE", "enf")
    guardada = next(e for e in m.repo.obtener(nino.id).evaluaciones if e.id == primera.id_recurso)
    assert guardada.hemoglobina_observada == 7.0 and guardada.clasificacion.value == "SEVERA"
    assert len(m.repo.obtener(nino.id).evaluaciones) == 2  # se reemplazó, no se duplicó


def test_cp242_conservar_el_servidor_y_descartar_dejan_la_evaluacion_como_estaba(m):
    nino = guardar_nino(m)
    m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(hb=12.0), nino=nino.id))
    for resolucion in ("CONSERVAR_SERVIDOR", "DESCARTAR"):
        r = m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(hb=7.0), nino=nino.id, dispositivo="B"))
        m.servicio.resolver_conflicto(r.id_conflicto, resolucion, "enf")
    assert [e.hemoglobina_observada for e in m.repo.obtener(nino.id).evaluaciones if e.fecha.day == 25] == [12.0]


def test_cp243_una_evaluacion_invalida_se_rechaza_con_errores_por_campo_y_no_se_registra_en_la_bitacora(m):
    nino = guardar_nino(m)
    operacion = m.op("REGISTRAR_EVALUACION", evaluacion(hb=25.0, fecha="2027-01-01"), nino=nino.id)
    r = m.uno(operacion)
    assert r.resultado == RECHAZADA and {e.campo for e in r.errores} == {"fecha", "hemoglobina_observada"}
    assert "hemoglobina_observada" in r.mensaje and m.repo.contar_operaciones() == 0
    assert m.uno(operacion).resultado == RECHAZADA  # sigue pudiendo reenviarse (y volverá a rechazarse)


# --- (c) Asistencia ----------------------------------------------------------------------------------------------------


def test_cp244_asistencia_aplicada_duplicada_y_en_conflicto(m):
    nino = guardar_nino(m)
    a = m.uno(m.op("REGISTRAR_ASISTENCIA", asistencia("NO_ASISTIO", motivo="Viaje"), nino=nino.id))
    b = m.uno(
        m.op("REGISTRAR_ASISTENCIA", asistencia("NO_ASISTIO", motivo="Otro motivo"), nino=nino.id, dispositivo="B")
    )
    c = m.uno(m.op("REGISTRAR_ASISTENCIA", asistencia("ASISTIO"), nino=nino.id, dispositivo="C"))
    assert (a.resultado, b.resultado, c.resultado) == (APLICADA, DUPLICADA, CONFLICTO)
    assert b.id_recurso == a.id_recurso == c.id_recurso
    assert m.repo.obtener(nino.id).asistencias[0].estado == EstadoAsistencia.NO_ASISTIO


def test_cp245_aplicar_el_cliente_cambia_el_estado_de_la_asistencia_si_no_la_respalda_una_evaluacion(m):
    nino = guardar_nino(m)
    m.uno(m.op("REGISTRAR_ASISTENCIA", asistencia("NO_ASISTIO", motivo="Viaje"), nino=nino.id))
    r = m.uno(m.op("REGISTRAR_ASISTENCIA", asistencia("ASISTIO"), nino=nino.id, dispositivo="B"))
    m.servicio.resolver_conflicto(r.id_conflicto, "APLICAR_CLIENTE", "enf")
    guardada = m.repo.obtener(nino.id).asistencias[0]
    assert (guardada.estado, guardada.motivo) == (EstadoAsistencia.ASISTIO, None)
    r = m.uno(m.op("REGISTRAR_ASISTENCIA", asistencia("NO_ASISTIO", motivo="Enfermó"), nino=nino.id, dispositivo="C"))
    m.servicio.resolver_conflicto(r.id_conflicto, "APLICAR_CLIENTE", "enf")
    guardada = m.repo.obtener(nino.id).asistencias[0]
    assert (guardada.estado, guardada.motivo) == (EstadoAsistencia.NO_ASISTIO, "Enfermó")


def test_cp246_una_asistencia_respaldada_por_una_evaluacion_no_se_reemplaza(m):
    nino = guardar_nino(m)
    ev = nino.evaluaciones[0]
    m.repo.agregar_asistencia(
        AsistenciaControl(nino.id, "DHx", date(2025, 9, 10), EstadoAsistencia.ASISTIO, "x", None, ev.id)
    )
    r = m.uno(m.op("REGISTRAR_ASISTENCIA", asistencia("NO_ASISTIO", motivo="Viaje"), nino=nino.id))
    assert r.resultado == CONFLICTO
    with pytest.raises(ErrorValidacion, match="respaldada"):
        m.servicio.resolver_conflicto(r.id_conflicto, "APLICAR_CLIENTE", "enf")
    assert m.repo.obtener(nino.id).asistencias[0].estado == EstadoAsistencia.ASISTIO


def test_cp247_asistencia_a_un_control_inexistente_futuro_o_sin_codigo_se_rechaza(m):
    nino = guardar_nino(m)
    inexistente = m.uno(m.op("REGISTRAR_ASISTENCIA", asistencia(codigo="C6M"), nino=nino.id))
    futuro = m.uno(m.op("REGISTRAR_ASISTENCIA", asistencia(fecha_programada="2027-01-01"), nino=nino.id))
    sin_codigo = m.uno(m.op("REGISTRAR_ASISTENCIA", asistencia(codigo=None), nino=nino.id))
    assert [r.resultado for r in (inexistente, futuro, sin_codigo)] == [RECHAZADA] * 3
    assert "C6M" in inexistente.mensaje and futuro.errores[0].campo == "fecha_programada"
    assert sin_codigo.errores[0].campo == "codigo"


def test_cp248_asistencia_a_un_control_ya_cumplido_se_rechaza_como_en_la_captura_en_linea(m):
    nino = guardar_nino(m)
    m.repo.agregar_evaluacion(evaluacion_de(date(2025, 9, 12), "SIN_ANEMIA", nino_id=nino.id))
    r = m.uno(m.op("REGISTRAR_ASISTENCIA", asistencia("ASISTIO"), nino=nino.id))
    assert r.resultado == RECHAZADA and "cumplido" in r.mensaje


# --- (d) Visita --------------------------------------------------------------------------------------------------------


def test_cp249_visita_aplicada_duplicada_y_en_conflicto_y_aplicar_cliente_la_reemplaza(m):
    nino = guardar_nino(m)
    a = m.uno(m.op("REGISTRAR_VISITA", visita(), nino=nino.id))
    b = m.uno(m.op("REGISTRAR_VISITA", visita(), nino=nino.id, dispositivo="B"))
    c = m.uno(
        m.op(
            "REGISTRAR_VISITA",
            visita(resultado="NO_ENCONTRADO", consume_suplemento="DESCONOCIDO", observaciones=None),
            nino=nino.id,
            dispositivo="C",
        )
    )
    assert (a.resultado, b.resultado, c.resultado) == (APLICADA, DUPLICADA, CONFLICTO)
    assert b.id_recurso == a.id_recurso == c.id_recurso
    m.servicio.resolver_conflicto(c.id_conflicto, "APLICAR_CLIENTE", "enf")
    v = m.repo.listar_visitas(nino.id)
    assert len(v) == 1 and v[0].resultado.value == "NO_ENCONTRADO" and v[0].observaciones is None


def test_cp250_visita_con_consumo_en_un_no_encontrado_o_fecha_futura_se_rechaza(m):
    nino = guardar_nino(m)
    r = m.uno(m.op("REGISTRAR_VISITA", visita(resultado="NO_ENCONTRADO"), nino=nino.id))
    assert r.resultado == RECHAZADA and r.errores[0].campo == "consume_suplemento"
    assert m.uno(m.op("REGISTRAR_VISITA", visita(fecha="2027-01-01"), nino=nino.id)).resultado == RECHAZADA


# --- Rechazos y referencias --------------------------------------------------------------------------------------------


def test_cp251_un_nino_con_datos_invalidos_se_rechaza_con_todos_los_errores(m):
    malo = registro(dni="123", sexo="X", hb=30.0)
    r = m.uno(m.op("REGISTRAR_NINO", malo, id_cliente="tmp-1"))
    assert r.resultado == RECHAZADA and {e.campo for e in r.errores} == {"dni", "sexo", "hemoglobina_observada"}
    assert m.repo.listar() == [] and m.repo.contar_operaciones() == 0


def test_cp252_una_fecha_de_nacimiento_invalida_no_oculta_los_demas_errores(m):
    malo = registro(fecha_nacimiento=date(2020, 1, 1))
    r = m.uno(m.op("REGISTRAR_NINO", malo, id_cliente="tmp-1"))
    assert r.resultado == RECHAZADA and [e.campo for e in r.errores] == ["fecha_nacimiento"]


def test_cp253_datos_mal_tipados_o_tipo_desconocido_se_rechazan_sin_romper_el_lote(m):
    nino = guardar_nino(m)
    r = m.sync(
        m.op("REGISTRAR_EVALUACION", {"fecha": "no-es-fecha", "hemoglobina_observada": "doce"}, nino=nino.id),
        m.op("BORRAR_TODO", {}, nino=nino.id),
        m.op("REGISTRAR_VISITA", visita(), nino=nino.id),
    )
    assert [x.resultado for x in r] == [RECHAZADA, RECHAZADA, APLICADA]
    assert [e.campo for e in r[0].errores] == ["fecha", "hemoglobina_observada"] and r[1].errores[0].campo == "tipo"


def test_cp254_la_referencia_al_nino_es_obligatoria_y_debe_existir(m):
    sin_referencia = m.uno(m.op("REGISTRAR_VISITA", visita()))
    inexistente = m.uno(m.op("REGISTRAR_VISITA", visita(), nino="no-existe"))
    sin_sincronizar = m.uno(m.op("REGISTRAR_VISITA", visita(), cliente="tmp-9"))
    assert [r.resultado for r in (sin_referencia, inexistente, sin_sincronizar)] == [RECHAZADA] * 3
    assert sin_referencia.errores[0].campo == "nino_ref" and "No existe" in inexistente.mensaje
    assert "aún no está sincronizado" in sin_sincronizar.mensaje


def test_cp255_si_el_nino_referenciado_desaparecio_la_operacion_se_rechaza(m):
    nuevo = m.uno(m.op("REGISTRAR_NINO", registro(), id_cliente="tmp-1"))
    m.repo.eliminar_por_origen("SISTEMA")
    r = m.uno(m.op("REGISTRAR_VISITA", visita(), cliente="tmp-1"))
    assert nuevo.resultado == APLICADA and r.resultado == RECHAZADA and "No existe el niño" in r.mensaje


# --- Resolución de conflictos -------------------------------------------------------------------------------------------


def conflicto_de_evaluacion(m):
    nino = guardar_nino(m)
    m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(hb=12.0), nino=nino.id))
    return m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(hb=7.0), nino=nino.id, dispositivo="B")).id_conflicto


def test_cp256_listar_conflictos_por_estado(m):
    pendiente = conflicto_de_evaluacion(m)
    resuelto = conflicto_de_evaluacion(m)
    m.servicio.resolver_conflicto(resuelto, "DESCARTAR", "enf")
    assert [c.id for c in m.servicio.listar_conflictos("PENDIENTE")] == [pendiente]
    assert [c.id for c in m.servicio.listar_conflictos("RESUELTO")] == [resuelto]
    assert {c.id for c in m.servicio.listar_conflictos()} == {pendiente, resuelto}
    with pytest.raises(ErrorValidacion, match="PENDIENTE o RESUELTO"):
        m.servicio.listar_conflictos("ABIERTO")


def test_cp257_un_conflicto_resuelto_no_se_vuelve_a_resolver(m):
    id_conflicto = conflicto_de_evaluacion(m)
    m.servicio.resolver_conflicto(id_conflicto, "CONSERVAR_SERVIDOR", "enf")
    with pytest.raises(ConflictoYaResuelto):
        m.servicio.resolver_conflicto(id_conflicto, "APLICAR_CLIENTE", "enf")


def test_cp258_resolucion_invalida_o_conflicto_inexistente(m):
    id_conflicto = conflicto_de_evaluacion(m)
    with pytest.raises(ErrorValidacion) as e:
        m.servicio.resolver_conflicto(id_conflicto, "BORRAR", "enf")
    assert e.value.errores[0].campo == "resolucion"
    with pytest.raises(NoEncontrado):
        m.servicio.resolver_conflicto("no-existe", "DESCARTAR", "enf")
    assert m.repo.obtener_conflicto(id_conflicto).estado == EstadoConflicto.PENDIENTE


def test_cp259_reenviar_una_operacion_en_conflicto_devuelve_el_mismo_conflicto_sin_abrir_otro(m):
    nino = guardar_nino(m)
    m.uno(m.op("REGISTRAR_EVALUACION", evaluacion(hb=12.0), nino=nino.id))
    operacion = m.op("REGISTRAR_EVALUACION", evaluacion(hb=7.0), nino=nino.id, dispositivo="B")
    primero = m.uno(operacion)
    segundo = m.uno(operacion)
    assert (segundo.resultado, segundo.resultado_original) == (DUPLICADA, CONFLICTO)
    assert segundo.id_conflicto == primero.id_conflicto and len(m.repo.listar_conflictos()) == 1


def test_cp260_el_repositorio_en_memoria_actualiza_evaluaciones_y_asistencias_y_filtra_conflictos(m):
    nino = guardar_nino(m)
    ev = nino.evaluaciones[0]
    ev.hemoglobina_observada = 5.0
    m.repo.actualizar_evaluacion(ev)
    assert m.repo.obtener(nino.id).evaluaciones[0].hemoglobina_observada == 5.0
    a = m.repo.agregar_asistencia(
        AsistenciaControl(nino.id, "DHx", date(2025, 9, 10), EstadoAsistencia.NO_ASISTIO, "x", "m")
    )
    a.estado = EstadoAsistencia.ASISTIO
    m.repo.actualizar_asistencia(a)
    assert m.repo.obtener(nino.id).asistencias[0].estado == EstadoAsistencia.ASISTIO
    assert m.repo.id_nino_de_cliente("tab-1", "nada") is None
    assert m.repo.obtener_conflicto_de_operacion("nada") is None
