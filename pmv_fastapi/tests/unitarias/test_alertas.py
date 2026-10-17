"""CP-67 a CP-72 y CP-114: prioridad, orden y resumen de las alertas de controles vencidos (HIST-2.2). Dominio puro."""

from datetime import date

import pytest

from app.domain.model.agenda import ControlProgramado, EstadoControl, TipoControl
from app.domain.model.alertas import Prioridad
from app.domain.model.clasificacion import Clasificacion
from app.domain.service.agenda import generar_agenda
from app.domain.service.alertas import alertas_de_nino, calcular_prioridad, ordenar_alertas, resumir_alertas
from tests.conftest import nino_de

HOY = date(2026, 9, 28)


def control(tipo=TipoControl.TAMIZAJE_EDAD, dias=1, estado=EstadoControl.VENCIDO, codigo="DHx"):
    return ControlProgramado(
        codigo=codigo,
        tipo=tipo,
        fecha_programada=date(2026, 6, 1),
        fecha_limite=date(2026, 7, 1),
        estado=estado,
        dias_vencido=dias,
        evaluacion_id=None,
        descripcion="control de prueba",
        fecha_inicio_ventana=date(2026, 5, 17),
    )


@pytest.mark.parametrize(
    "tipo, ultima, dias, esperada",
    [
        (TipoControl.TAMIZAJE_EDAD, Clasificacion.SIN_ANEMIA, 1, Prioridad.BAJA),
        (TipoControl.TAMIZAJE_EDAD, Clasificacion.SIN_ANEMIA, 7, Prioridad.BAJA),  # hasta 7 días
        (TipoControl.TAMIZAJE_EDAD, Clasificacion.SIN_ANEMIA, 8, Prioridad.MEDIA),  # de 8 a 30 días
        (TipoControl.TAMIZAJE_EDAD, Clasificacion.SIN_ANEMIA, 30, Prioridad.MEDIA),
        (TipoControl.TAMIZAJE_EDAD, Clasificacion.SIN_ANEMIA, 31, Prioridad.ALTA),  # más de 30 días
        (TipoControl.TAMIZAJE_EDAD, Clasificacion.MODERADA, 1, Prioridad.ALTA),
        (TipoControl.TAMIZAJE_EDAD, Clasificacion.SEVERA, 5, Prioridad.ALTA),
        (TipoControl.TAMIZAJE_EDAD, Clasificacion.LEVE, 5, Prioridad.BAJA),  # la anemia leve no sube la prioridad
        (TipoControl.TAMIZAJE_EDAD, Clasificacion.NO_APLICA, 20, Prioridad.MEDIA),
        (TipoControl.TAMIZAJE_EDAD, None, 3, Prioridad.BAJA),
        (TipoControl.CONTROL_TRATAMIENTO, Clasificacion.SIN_ANEMIA, 1, Prioridad.ALTA),  # tratamiento: siempre alta
        (TipoControl.CONTROL_TRATAMIENTO, Clasificacion.LEVE, 1, Prioridad.ALTA),
        (TipoControl.CONTROL_TRATAMIENTO, None, 1, Prioridad.ALTA),
    ],
)
def test_cp67_prioridad_valores_frontera(tipo, ultima, dias, esperada):
    assert calcular_prioridad(control(tipo=tipo, dias=dias), ultima) == esperada


def test_cp68_una_alerta_por_control_vencido_con_los_datos_para_contactar_a_la_familia():
    # DHx 6 m cumplido; DHc1 9 m, DHc2 12 m y DHx 15 m vencidos; DHc1 18 m pendiente.
    nino = nino_de(
        date(2025, 3, 10), [(date(2025, 9, 12), "SIN_ANEMIA")], comunidad="Llacuas", tutor_celular="955667788"
    )
    agenda = generar_agenda(nino, HOY)
    alertas = alertas_de_nino(nino, agenda)
    assert [a.control.codigo for a in alertas] == ["DHc1", "DHc2", "DHx"]
    assert all(a.control.estado == EstadoControl.VENCIDO for a in alertas)
    primera = alertas[0]
    assert (primera.nino_id, primera.dni) == (nino.id, nino.dni)
    assert (primera.nombre_completo, primera.comunidad, primera.tutor_celular) == (
        "Luz Mery Quispe Rojas",
        "Llacuas",
        "955667788",
    )
    assert primera.ultima_clasificacion == Clasificacion.SIN_ANEMIA and primera.prioridad == Prioridad.ALTA


def test_cp69_sin_controles_vencidos_no_hay_alertas_y_la_ultima_clasificacion_es_la_mas_reciente():
    al_dia = nino_de(date(2026, 3, 28), [(date(2026, 9, 20), "SIN_ANEMIA")])
    assert alertas_de_nino(al_dia, generar_agenda(al_dia, HOY)) == []
    # Dos evaluaciones: la más reciente (MODERADA) es la que se informa en todas las alertas del niño.
    nino = nino_de(date(2025, 3, 10), [(date(2025, 9, 12), "SIN_ANEMIA"), (date(2025, 12, 12), "MODERADA")])
    agenda = generar_agenda(nino, date(2026, 7, 14))
    assert {a.ultima_clasificacion for a in alertas_de_nino(nino, agenda)} == {Clasificacion.MODERADA}


def test_cp70_orden_por_prioridad_y_luego_por_mayor_atraso():
    nino = nino_de(date(2025, 3, 10), [(date(2025, 9, 12), "SIN_ANEMIA")])
    alertas = alertas_de_nino(nino, generar_agenda(nino, HOY))
    desordenadas = list(reversed(alertas))
    ordenadas = ordenar_alertas(desordenadas)
    assert [a.control.dias_vencido for a in ordenadas] == sorted(
        (a.control.dias_vencido for a in alertas), reverse=True
    )
    # Prioridades mezcladas: ALTA (por atraso y por tratamiento), luego MEDIA y al final BAJA.
    ordenadas = ordenar_alertas(
        [
            _alerta(nino, control(dias=5)),
            _alerta(nino, control(dias=20)),
            _alerta(nino, control(dias=90)),
            _alerta(nino, control(dias=2, tipo=TipoControl.CONTROL_TRATAMIENTO, codigo="C1M")),
        ]
    )
    assert [(a.prioridad.value, a.control.dias_vencido) for a in ordenadas] == [
        ("ALTA", 90),
        ("ALTA", 2),
        ("MEDIA", 20),
        ("BAJA", 5),
    ]


def _alerta(nino, ctrl):
    from app.domain.model.alertas import AlertaControl

    return AlertaControl(
        nino_id=nino.id,
        dni=nino.dni,
        nombre_completo=nino.nombre_completo,
        comunidad=nino.comunidad,
        tutor_celular=nino.tutor_celular,
        control=ctrl,
        ultima_clasificacion=Clasificacion.SIN_ANEMIA,
        prioridad=calcular_prioridad(ctrl, Clasificacion.SIN_ANEMIA),
    )


def test_cp71_resumen_cuenta_por_prioridad_y_ninos_distintos():
    a, b = nino_de(date(2025, 3, 10)), nino_de(date(2025, 4, 10), dni="70000002")
    alertas = [
        _alerta(a, control(dias=40)),
        _alerta(a, control(dias=10)),
        _alerta(b, control(dias=3)),
        _alerta(b, control(dias=2, tipo=TipoControl.CONTROL_TRATAMIENTO, codigo="C3M")),
    ]
    r = resumir_alertas(alertas, proximos_7_dias=5)
    assert r.total_vencidos == 4 and r.ninos_con_vencidos == 2 and r.proximos_7_dias == 5
    assert r.por_prioridad == {"ALTA": 2, "MEDIA": 1, "BAJA": 1}


def test_cp72_resumen_vacio_incluye_todas_las_prioridades_en_cero():
    r = resumir_alertas([], proximos_7_dias=0)
    assert r.total_vencidos == 0 and r.ninos_con_vencidos == 0
    assert r.por_prioridad == {"ALTA": 0, "MEDIA": 0, "BAJA": 0}


def test_cp114_nino_sin_evaluaciones_no_tiene_ultima_clasificacion():
    nino = nino_de(date(2025, 3, 10))
    assert nino.ultima_evaluacion is None
    agenda = generar_agenda(nino, HOY)
    assert all(a.ultima_clasificacion is None for a in alertas_de_nino(nino, agenda))
