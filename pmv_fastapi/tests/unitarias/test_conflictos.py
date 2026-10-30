"""CP-206 a CP-224: reglas de conflicto de la sincronización (HIST-3.3, ADR-012) y normalización de las operaciones
(HIST-3.2). Servicios de dominio puros: sin base de datos ni red.
"""

from datetime import UTC, date, datetime

import pytest

from app.domain.model.asistencia import AsistenciaControl, EstadoAsistencia
from app.domain.model.sincronizacion import TipoOperacion
from app.domain.model.visita import ConsumoSuplemento, ResultadoVisita, VisitaDomiciliaria
from app.domain.service.conflictos import (
    AccionSync,
    decidir_asistencia,
    decidir_evaluacion,
    decidir_nino,
    decidir_visita,
    diferencias_nino,
    hemoglobina_igual,
    instantanea_asistencia,
    instantanea_evaluacion,
    instantanea_nino,
    instantanea_visita,
    motivo_no_aplicable,
)
from app.domain.service.operaciones import normalizar_datos, normalizar_fecha_local
from tests.conftest import datos_nino, evaluacion_de, nino_de

NACIMIENTO = date(2025, 10, 15)
FECHA = date(2026, 9, 20)


def datos_cliente(**cambios):
    return datos_nino(**cambios)


def nino_existente(**cambios):
    return nino_de(NACIMIENTO, [(FECHA, "SIN_ANEMIA")], **cambios)


def eval_cliente(hb=12.0, fecha=FECHA):
    return {"fecha": fecha, "hemoglobina_observada": hb, "peso_kg": 8.0, "talla_cm": 70.0}


# --- (a) Niño --------------------------------------------------------------------------------------------------------


def test_cp206_sin_nino_con_ese_dni_se_crea():
    assert decidir_nino(None, datos_cliente(), eval_cliente()).accion == AccionSync.CREAR


def test_cp207_mismo_dni_y_mismos_datos_se_toma_el_existente_y_se_mapea():
    existente = nino_existente()
    # Mayúsculas, espacios dobles y un celular vacío no son diferencias reales.
    cliente = datos_cliente(nombres="  LUZ  mery ", comunidad="PALMAYOC", tutor_celular=existente.tutor_celular)
    d = decidir_nino(existente, cliente, eval_cliente(hb=12.0))
    assert (d.accion, d.id_recurso) == (AccionSync.MAPEAR, existente.id)
    assert diferencias_nino(existente, cliente) == ()


def test_cp208_mismo_dni_y_datos_distintos_es_conflicto_y_nombra_los_campos():
    existente = nino_existente()
    cliente = datos_cliente(apellidos="Otro Apellido", altitud_m=3000, tutor_celular=None)
    d = decidir_nino(existente, cliente, eval_cliente())
    assert d.accion == AccionSync.CONFLICTO and d.id_recurso == existente.id
    assert d.diferencias == ("apellidos", "altitud_m", "tutor_celular")
    assert "71234567" in d.motivo and "apellidos" in d.motivo
    assert d.datos_servidor == instantanea_nino(existente)


def test_cp209_una_fecha_de_nacimiento_o_altitud_ausente_cuenta_como_diferencia():
    existente = nino_existente()
    assert diferencias_nino(existente, datos_cliente(fecha_nacimiento=date(2025, 10, 16))) == ("fecha_nacimiento",)
    assert diferencias_nino(existente, datos_cliente(altitud_m=None)) == ("altitud_m",)


def test_cp210_nino_identico_sin_la_evaluacion_de_ese_dia_agrega_la_evaluacion():
    existente = nino_existente()
    d = decidir_nino(existente, datos_cliente(), eval_cliente(fecha=date(2026, 9, 21)))
    assert (d.accion, d.id_recurso) == (AccionSync.AGREGAR_EVALUACION, existente.id)


def test_cp211_nino_identico_con_la_misma_fecha_y_otra_hemoglobina_es_conflicto_de_evaluacion():
    existente = nino_existente()
    d = decidir_nino(existente, datos_cliente(), eval_cliente(hb=9.0))
    assert d.accion == AccionSync.CONFLICTO and d.id_recurso == existente.id
    assert d.diferencias == ("evaluacion.hemoglobina_observada",)
    assert d.datos_servidor["dni"] == "71234567"
    assert d.datos_servidor["evaluacion"]["hemoglobina_observada"] == 12.0


# --- (b) Evaluación --------------------------------------------------------------------------------------------------


def test_cp212_evaluacion_sin_otra_el_mismo_dia_se_crea():
    assert decidir_evaluacion(nino_existente(), eval_cliente(fecha=date(2026, 9, 25))).accion == AccionSync.CREAR


def test_cp213_misma_fecha_y_misma_hemoglobina_es_duplicada_logica_y_se_mapea():
    nino = nino_existente()
    d = decidir_evaluacion(nino, eval_cliente(hb=12.04))
    assert (d.accion, d.id_recurso) == (AccionSync.MAPEAR, nino.evaluaciones[0].id)
    assert hemoglobina_igual(12.0, 12.04) and not hemoglobina_igual(12.0, 12.1)


def test_cp214_misma_fecha_y_distinta_hemoglobina_es_conflicto_con_los_dos_valores():
    nino = nino_existente()
    d = decidir_evaluacion(nino, eval_cliente(hb=10.5))
    assert d.accion == AccionSync.CONFLICTO and d.id_recurso == nino.evaluaciones[0].id
    assert "12.0" in d.motivo and "10.5" in d.motivo and "2026-09-20" in d.motivo
    assert d.datos_servidor == instantanea_evaluacion(nino.evaluaciones[0])


def test_cp215_con_dos_evaluaciones_el_mismo_dia_basta_que_una_coincida():
    nino = nino_existente()
    nino.evaluaciones.append(evaluacion_de(FECHA, "LEVE", hemoglobina_observada=10.0, nino_id=nino.id))
    d = decidir_evaluacion(nino, eval_cliente(hb=10.0))
    assert (d.accion, d.id_recurso) == (AccionSync.MAPEAR, nino.evaluaciones[1].id)
    assert decidir_evaluacion(nino, eval_cliente(hb=7.0)).id_recurso == nino.evaluaciones[0].id  # compara con la 1.ª


# --- (c) Asistencia ----------------------------------------------------------------------------------------------------


def asistencia_previa(nino, estado=EstadoAsistencia.ASISTIO, **cambios):
    a = AsistenciaControl(nino.id, "DHx", date(2026, 9, 10), estado, "enf.rosa", motivo=cambios.pop("motivo", None))
    for campo, valor in cambios.items():
        setattr(a, campo, valor)
    nino.asistencias.append(a)
    return a


def test_cp216_asistencia_de_un_control_sin_registro_se_crea_con_igual_estado_se_mapea_con_otro_es_conflicto():
    nino = nino_existente()
    datos = {"codigo": "DHx", "fecha_programada": date(2026, 9, 10), "estado": "ASISTIO"}
    assert decidir_asistencia(nino, datos).accion == AccionSync.CREAR
    previa = asistencia_previa(nino)
    assert (decidir_asistencia(nino, datos).accion, decidir_asistencia(nino, datos).id_recurso) == (
        AccionSync.MAPEAR,
        previa.id,
    )
    otro = {**datos, "estado": "NO_ASISTIO"}
    d = decidir_asistencia(nino, otro)
    assert d.accion == AccionSync.CONFLICTO and d.diferencias == ("estado",)
    assert "ASISTIO" in d.motivo and "NO_ASISTIO" in d.motivo
    assert d.datos_servidor == instantanea_asistencia(previa)
    # Otro control u otra fecha programada no chocan.
    assert decidir_asistencia(nino, {**datos, "codigo": "DHc1"}).accion == AccionSync.CREAR
    assert decidir_asistencia(nino, {**datos, "fecha_programada": date(2026, 9, 11)}).accion == AccionSync.CREAR


# --- (d) Visita --------------------------------------------------------------------------------------------------------


def visita_previa(**cambios):
    v = VisitaDomiciliaria("n1", FECHA, ResultadoVisita.REALIZADA, "enf", ConsumoSuplemento.SI, "Todo bien")
    for campo, valor in cambios.items():
        setattr(v, campo, valor)
    return v


def test_cp217_visita_sin_previa_se_crea_igual_se_mapea_y_distinta_es_conflicto():
    datos = {"fecha": FECHA, "resultado": "REALIZADA", "consume_suplemento": "SI", "observaciones": "todo  BIEN"}
    assert decidir_visita(None, datos).accion == AccionSync.CREAR
    previa = visita_previa()
    d = decidir_visita(previa, datos)
    assert (d.accion, d.id_recurso) == (AccionSync.MAPEAR, previa.id)
    distinta = {**datos, "consume_suplemento": "NO", "observaciones": None}
    d = decidir_visita(previa, distinta)
    assert d.accion == AccionSync.CONFLICTO and d.diferencias == ("consume_suplemento", "observaciones")
    assert d.datos_servidor == instantanea_visita(previa)


def test_cp218_visita_sin_consumo_equivale_a_desconocido_y_observaciones_vacias_a_ninguna():
    previa = visita_previa(
        resultado=ResultadoVisita.NO_ENCONTRADO, consume_suplemento=ConsumoSuplemento.DESCONOCIDO, observaciones=None
    )
    datos = {"fecha": FECHA, "resultado": "NO_ENCONTRADO", "observaciones": "  "}
    assert decidir_visita(previa, datos).accion == AccionSync.MAPEAR


# --- Qué se puede reemplazar al aplicar el dato del dispositivo --------------------------------------------------------


def test_cp219_los_datos_de_identidad_del_nino_nunca_se_sobrescriben():
    assert motivo_no_aplicable(TipoOperacion.REGISTRAR_NINO, ("comunidad", "altitud_m", "tutor_celular"), {}) is None
    assert motivo_no_aplicable(TipoOperacion.REGISTRAR_NINO, ("evaluacion.hemoglobina_observada",), {}) is None
    motivo = motivo_no_aplicable(TipoOperacion.REGISTRAR_NINO, ("nombres", "comunidad", "sexo"), {})
    assert "nombres, sexo" in motivo and "identidad" in motivo


def test_cp220_una_asistencia_respaldada_por_una_evaluacion_no_se_cambia():
    assert motivo_no_aplicable(TipoOperacion.REGISTRAR_ASISTENCIA, ("estado",), {"evaluacion_id": None}) is None
    assert "respaldada" in motivo_no_aplicable(TipoOperacion.REGISTRAR_ASISTENCIA, ("estado",), {"evaluacion_id": "e1"})
    assert motivo_no_aplicable(TipoOperacion.REGISTRAR_EVALUACION, ("hemoglobina_observada",), {}) is None
    assert motivo_no_aplicable(TipoOperacion.REGISTRAR_VISITA, ("resultado",), {}) is None


# --- Normalización de las operaciones ------------------------------------------------------------------------------------


def test_cp221_normaliza_un_nino_con_su_evaluacion_inicial():
    datos = {
        "nino": {**datos_nino(), "fecha_nacimiento": "2025-10-15"},
        "evaluacion_inicial": {"fecha": "2026-09-20", "hemoglobina_observada": 12, "peso_kg": 8.1, "talla_cm": 69.5},
    }
    del_dominio, errores = normalizar_datos("REGISTRAR_NINO", datos)
    assert errores == []
    assert del_dominio["nino"]["fecha_nacimiento"] == date(2025, 10, 15) and del_dominio["nino"]["altitud_m"] == 3720.0
    assert del_dominio["evaluacion"] == {
        "fecha": FECHA,
        "hemoglobina_observada": 12.0,
        "peso_kg": 8.1,
        "talla_cm": 69.5,
    }


@pytest.mark.parametrize(
    "tipo, datos, esperado",
    [
        ("REGISTRAR_EVALUACION", {"fecha": FECHA.isoformat(), "hemoglobina_observada": 12.0}, {"peso_kg": None}),
        (
            "REGISTRAR_ASISTENCIA",
            {"codigo": "DHx", "fecha_programada": "2026-09-10", "estado": "ASISTIO"},
            {"motivo": None},
        ),
        ("REGISTRAR_VISITA", {"fecha": "2026-09-20", "resultado": "REALIZADA"}, {"observaciones": None}),
    ],
)
def test_cp222_los_campos_ausentes_quedan_en_none_para_que_los_valide_el_dominio(tipo, datos, esperado):
    del_dominio, errores = normalizar_datos(tipo, datos)
    assert errores == [] and all(del_dominio[c] == v for c, v in esperado.items())


@pytest.mark.parametrize(
    "tipo, datos, campos",
    [
        (
            "REGISTRAR_EVALUACION",
            {"fecha": "20/09/2026", "hemoglobina_observada": "12", "peso_kg": True},
            ["fecha", "hemoglobina_observada", "peso_kg"],
        ),
        ("REGISTRAR_EVALUACION", {"fecha": 20260920, "talla_cm": [70]}, ["fecha", "talla_cm"]),
        ("REGISTRAR_ASISTENCIA", {"codigo": 5, "estado": ["ASISTIO"]}, ["codigo", "estado"]),
        ("REGISTRAR_VISITA", {"fecha": None, "resultado": 3, "observaciones": {}}, ["resultado", "observaciones"]),
        ("REGISTRAR_NINO", {"nino": {"dni": 71234567}, "evaluacion_inicial": 7}, ["dni", "datos"]),
        ("REGISTRAR_NINO", {}, ["datos", "datos"]),
    ],
)
def test_cp223_los_valores_mal_tipados_se_senalan_por_campo(tipo, datos, campos):
    _, errores = normalizar_datos(tipo, datos)
    assert [e.campo for e in errores] == campos


def test_cp224_un_tipo_desconocido_se_senala_y_la_fecha_local_sin_zona_es_hora_de_peru():
    assert normalizar_datos("BORRAR_TODO", {}) == ({}, [normalizar_datos("BORRAR_TODO", {})[1][0]])
    assert normalizar_datos("BORRAR_TODO", {})[1][0].campo == "tipo"
    sin_zona = datetime(2026, 9, 20, 8, 0)
    assert normalizar_fecha_local(sin_zona) == datetime(2026, 9, 20, 13, 0, tzinfo=UTC)
    con_zona = datetime(2026, 9, 20, 8, 0, tzinfo=UTC)
    assert normalizar_fecha_local(con_zona) is con_zona
