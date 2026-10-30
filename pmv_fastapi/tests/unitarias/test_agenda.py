"""CP-44 a CP-60: agenda automática de controles (HIST-2.1). Servicio de dominio puro, sin base de datos ni API.

Convenciones de los escenarios: el niño base nace el 10-mar-2025 y su primera evaluación (a los 3 meses, sin clasificar)
fija el inicio de la agenda; su DHx de 6 meses se programa el 10-sep-2025 y su ventana de cumplimiento va del
26-ago-2025 (-15 d) al 10-oct-2025 (+30 d).
"""

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

import pytest

from app.domain.model.agenda import EstadoControl, TipoControl
from app.domain.service.agenda import ESQUEMA_AGENDA_V1, MOTIVO_ALTA, agregar_meses, generar_agenda
from tests.conftest import evaluacion_de, nino_de

NACIMIENTO = date(2025, 3, 10)
ANCLA = (date(2025, 6, 10), "NO_APLICA")  # primera evaluación: fija el inicio de la agenda
DHX_6M = date(2025, 9, 10)


def por_codigo(agenda, codigo):
    """Primer control (por fecha programada) con ese código; DHx, DHc1 y DHc2 se repiten a lo largo de la agenda."""
    encontrados = [c for c in agenda.controles if c.codigo == codigo]
    assert encontrados, f"{codigo} no está en la agenda"
    return encontrados[0]


def tratamiento(agenda):
    return [c for c in agenda.controles if c.tipo == TipoControl.CONTROL_TRATAMIENTO]


# --- Parámetros y suma segura de meses ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "origen, meses, esperado",
    [
        (date(2026, 1, 31), 1, date(2026, 2, 28)),  # el día 31 pasa al último día del mes
        (date(2028, 1, 31), 1, date(2028, 2, 29)),  # año bisiesto
        (date(2026, 3, 31), 1, date(2026, 4, 30)),
        (date(2025, 8, 31), 6, date(2026, 2, 28)),
        (date(2023, 8, 31), 6, date(2024, 2, 29)),
        (date(2025, 11, 30), 3, date(2026, 2, 28)),
        (date(2024, 2, 29), 12, date(2025, 2, 28)),
        (date(2025, 12, 15), 1, date(2026, 1, 15)),  # cambio de año
        (date(2025, 12, 31), 12, date(2026, 12, 31)),
        (date(2026, 3, 31), -1, date(2026, 2, 28)),  # hacia atrás (usado por los datos de prueba)
    ],
)
def test_cp44_suma_segura_de_meses_calendario(origen, meses, esperado):
    assert agregar_meses(origen, meses) == esperado


def test_cp187_la_suma_rapida_de_meses_equivale_a_la_version_con_calendar():
    """La optimización de agregar_meses (tabla de días por mes) no cambió su resultado: se compara con calendar."""
    import calendar

    def referencia(fecha: date, meses: int) -> date:
        anio, mes0 = divmod(fecha.year * 12 + (fecha.month - 1) + meses, 12)
        return date(anio, mes0 + 1, min(fecha.day, calendar.monthrange(anio, mes0 + 1)[1]))

    dia = date(1999, 12, 29)
    while dia < date(2031, 1, 5):
        for meses in (-13, -1, 0, 1, 3, 6, 15, 51, 60):
            assert agregar_meses(dia, meses) == referencia(dia, meses), (dia, meses)
        dia += timedelta(days=1)


def test_cp45_esquema_v1_tiene_los_parametros_normativos():
    esq = ESQUEMA_AGENDA_V1
    assert esq.version == "AGENDA-V1"
    assert esq.dosajes_por_edad == (
        (6, "DHx"),
        (9, "DHc1"),
        (12, "DHc2"),
        (15, "DHx"),
        (18, "DHc1"),
        (21, "DHc2"),
        (24, "DHx"),
        (30, "DHc1"),
        (36, "DHx"),
        (39, "DHc1"),
        (48, "DHx"),
        (51, "DHc1"),
    )
    assert esq.controles_tratamiento == ((1, "C1M"), (3, "C3M"), (6, "C6M"))
    assert (esq.tolerancia_previa_dias, esq.tolerancia_posterior_dias, esq.dias_proximo_a_vencer) == (15, 30, 7)
    assert "S1" in esq.fuente and "213-MINSA/DGIESP-2024" in esq.fuente


def test_cp46_recien_nacido_tiene_los_12_dosajes_por_edad_pendientes():
    hoy = date(2026, 9, 28)
    agenda = generar_agenda(nino_de(hoy, [(hoy, "NO_APLICA")]), hoy)
    assert agenda.aplica and agenda.version_esquema == "AGENDA-V1" and agenda.fecha_referencia == hoy
    assert [c.codigo for c in agenda.controles] == [c for _, c in ESQUEMA_AGENDA_V1.dosajes_por_edad]
    assert all(c.estado == EstadoControl.PENDIENTE and not c.proximo for c in agenda.controles)
    assert all(c.tipo == TipoControl.TAMIZAJE_EDAD for c in agenda.controles)
    assert agenda.controles[0].fecha_programada == date(2027, 3, 28)
    assert agenda.resumen.total == 12 and agenda.resumen.pendientes == 12
    assert agenda.resumen.proximo_control.codigo == "DHx"


@pytest.mark.parametrize(
    "nacimiento, esperadas",
    [
        (date(2025, 1, 31), ["2025-07-31", "2025-10-31", "2026-01-31", "2026-04-30", "2026-07-31", "2026-10-31"]),
        (date(2025, 8, 31), ["2026-02-28", "2026-05-31", "2026-08-31", "2026-11-30", "2027-02-28", "2027-05-31"]),
        (date(2023, 8, 31), ["2024-02-29", "2024-05-31", "2024-08-31", "2024-11-30", "2025-02-28", "2025-05-31"]),
    ],
)
def test_cp47_fechas_programadas_con_nacimiento_en_fin_de_mes(nacimiento, esperadas):
    hoy = nacimiento
    agenda = generar_agenda(nino_de(nacimiento, [(hoy, "NO_APLICA")]), hoy)
    primeras = [c.fecha_programada.isoformat() for c in agenda.controles[:6]]
    assert primeras == esperadas
    assert [c.edad_meses_programada for c in agenda.controles[:3]] == [6, 9, 12]


def test_cp48_la_agenda_empieza_cuando_el_nino_entra_al_sistema():
    # Un niño que ingresa a los 14 meses no nace con controles «vencidos» de los 6, 9 y 12 meses.
    hoy = date(2026, 9, 28)
    nino = nino_de(date(2025, 7, 28), [(date(2026, 9, 20), "SIN_ANEMIA")])  # 14 meses
    agenda = generar_agenda(nino, hoy)
    assert [c.codigo for c in agenda.controles][:2] == ["DHx", "DHc1"]
    assert agenda.controles[0].fecha_programada == date(2026, 10, 28)  # 15 meses
    assert agenda.resumen.vencidos == 0
    # Frontera: el 12.º mes cae 15 días antes de la primera evaluación -> se incluye; 16 días antes -> se omite.
    incluida = generar_agenda(nino_de(date(2025, 7, 28), [(date(2026, 8, 12), "SIN_ANEMIA")]), hoy)
    assert incluida.controles[0].codigo == "DHc2" and incluida.controles[0].fecha_programada == date(2026, 7, 28)
    omitida = generar_agenda(nino_de(date(2025, 7, 28), [(date(2026, 8, 13), "SIN_ANEMIA")]), hoy)
    assert omitida.controles[0].codigo == "DHx"


# --- Cumplimiento: ventana [programada - 15 d, programada + 30 d] ----------------------------------------------------


@pytest.mark.parametrize(
    "desfase, cumple",
    [(-16, False), (-15, True), (-1, True), (0, True), (30, True), (31, False)],
)
def test_cp49_ventana_de_cumplimiento_valores_frontera(desfase, cumple):
    evaluacion = (DHX_6M + timedelta(days=desfase), "SIN_ANEMIA")
    agenda = generar_agenda(nino_de(NACIMIENTO, [ANCLA, evaluacion]), date(2026, 9, 28))
    dhx = por_codigo(agenda, "DHx")
    assert dhx.fecha_programada == DHX_6M
    assert dhx.fecha_inicio_ventana == date(2025, 8, 26) and dhx.fecha_limite == date(2025, 10, 10)
    if cumple:
        assert dhx.estado == EstadoControl.CUMPLIDO and dhx.evaluacion_id is not None and dhx.dias_vencido is None
    else:
        assert dhx.estado == EstadoControl.VENCIDO and dhx.evaluacion_id is None


@pytest.mark.parametrize(
    "hoy, estado, proximo, dias_vencido",
    [
        (date(2025, 10, 2), EstadoControl.PENDIENTE, False, None),  # faltan 8 días para el límite
        (date(2025, 10, 3), EstadoControl.PENDIENTE, True, None),  # faltan 7 días: próximo
        (date(2025, 10, 10), EstadoControl.PENDIENTE, True, None),  # último día de la ventana: aún no vence
        (date(2025, 10, 11), EstadoControl.VENCIDO, False, 1),  # hoy > programada + 30 d
        (date(2025, 11, 10), EstadoControl.VENCIDO, False, 31),
    ],
)
def test_cp50_estados_pendiente_proximo_y_vencido_en_la_frontera(hoy, estado, proximo, dias_vencido):
    agenda = generar_agenda(nino_de(NACIMIENTO, [ANCLA]), hoy)
    dhx = por_codigo(agenda, "DHx")
    assert (dhx.estado, dhx.proximo, dhx.dias_vencido) == (estado, proximo, dias_vencido)
    assert agenda.resumen.vencidos == (1 if estado == EstadoControl.VENCIDO else 0)


def test_cp51_una_evaluacion_cumple_a_lo_sumo_un_control():
    # C1M (24-dic) y DHc2 (01-ene) tienen ventanas que se traslapan; la evaluación del 27-dic cae en ambas.
    nino = nino_de(date(2025, 1, 1), [(date(2025, 11, 24), "LEVE"), (date(2025, 12, 27), "LEVE")])
    agenda = generar_agenda(nino, date(2026, 2, 15))
    c1m, dhc2 = por_codigo(agenda, "C1M"), por_codigo(agenda, "DHc2")
    assert c1m.fecha_programada == date(2025, 12, 24) and dhc2.fecha_programada == date(2026, 1, 1)
    assert c1m.estado == EstadoControl.CUMPLIDO  # la más cercana (3 d contra 5 d)
    assert dhc2.estado == EstadoControl.VENCIDO and dhc2.dias_vencido == 15 and dhc2.evaluacion_id is None
    # Con una segunda evaluación en ambas ventanas cada control recibe una distinta.
    nino.evaluaciones.append(evaluacion_de(date(2026, 1, 5), "LEVE", nino_id=nino.id))
    agenda = generar_agenda(nino, date(2026, 2, 15))
    c1m, dhc2 = por_codigo(agenda, "C1M"), por_codigo(agenda, "DHc2")
    assert c1m.estado == dhc2.estado == EstadoControl.CUMPLIDO
    assert c1m.evaluacion_id != dhc2.evaluacion_id
    ids = [c.evaluacion_id for c in agenda.controles if c.evaluacion_id]
    assert len(ids) == len(set(ids))


def test_cp52_empate_de_distancia_gana_el_control_mas_antiguo():
    # Evaluación a 4 días de C1M (28-dic -> +4) y de DHc2 (01-ene -> -4): se asigna al control más antiguo (C1M).
    nino = nino_de(date(2025, 1, 1), [(date(2025, 11, 24), "LEVE"), (date(2025, 12, 28), "LEVE")])
    agenda = generar_agenda(nino, date(2026, 2, 15))
    assert por_codigo(agenda, "C1M").estado == EstadoControl.CUMPLIDO
    assert por_codigo(agenda, "DHc2").estado == EstadoControl.VENCIDO


# --- Seguimiento del tratamiento (C1M, C3M, C6M) ---------------------------------------------------------------------


def test_cp53_anemia_programa_c1m_c3m_c6m_con_suma_segura_de_meses():
    nino = nino_de(date(2025, 1, 1), [(date(2026, 1, 31), "LEVE")])
    agenda = generar_agenda(nino, date(2026, 2, 1))
    controles = tratamiento(agenda)
    assert [(c.codigo, c.fecha_programada) for c in controles] == [
        ("C1M", date(2026, 2, 28)),
        ("C3M", date(2026, 4, 30)),
        ("C6M", date(2026, 7, 31)),
    ]
    assert all(c.estado == EstadoControl.PENDIENTE for c in controles)
    assert controles[0].descripcion == "Control de hemoglobina del tratamiento a 1 mes (C1M)"
    assert controles[1].descripcion.endswith("a 3 meses (C3M)")


@pytest.mark.parametrize("clasificacion", ["LEVE", "MODERADA", "SEVERA"])
def test_cp54_las_tres_severidades_de_anemia_abren_seguimiento(clasificacion):
    agenda = generar_agenda(nino_de(date(2025, 1, 1), [(date(2026, 1, 10), clasificacion)]), date(2026, 1, 11))
    assert [c.codigo for c in tratamiento(agenda)] == ["C1M", "C3M", "C6M"]


def test_cp55_sin_anemia_y_no_aplica_no_abren_seguimiento():
    nino = nino_de(date(2025, 1, 1), [(date(2025, 5, 1), "NO_APLICA"), (date(2026, 1, 10), "SIN_ANEMIA")])
    assert tratamiento(generar_agenda(nino, date(2026, 1, 11))) == []


def test_cp56_episodio_con_recuperacion_cierra_los_controles_pendientes():
    # LEVE el 10-ene, SIN_ANEMIA el 12-feb (cumple C1M). C3M y C6M ya no son necesarios -> CERRADO_RECUPERADO.
    nino = nino_de(date(2025, 1, 1), [(date(2026, 1, 10), "LEVE"), (date(2026, 2, 12), "SIN_ANEMIA")])
    agenda = generar_agenda(nino, date(2026, 3, 1))
    c1m, c3m, c6m = (por_codigo(agenda, c) for c in ("C1M", "C3M", "C6M"))
    assert c1m.estado == EstadoControl.CUMPLIDO
    assert c3m.estado == c6m.estado == EstadoControl.CERRADO_RECUPERADO
    assert c3m.dias_vencido is None and not c3m.proximo
    assert agenda.resumen.cerrados == 2
    assert agenda.resumen.vencidos == 0
    assert all(c.estado != EstadoControl.CERRADO_RECUPERADO for c in agenda.controles if c.codigo not in ("C3M", "C6M"))


def test_cp57_controles_ya_vencidos_antes_de_la_recuperacion_siguen_vencidos():
    # C1M vence el 12-mar; la recuperación se registra el 20-mar: el control incumplido queda en el historial.
    nino = nino_de(date(2025, 1, 1), [(date(2026, 1, 10), "LEVE"), (date(2026, 3, 20), "SIN_ANEMIA")])
    agenda = generar_agenda(nino, date(2026, 4, 1))
    c1m = por_codigo(agenda, "C1M")
    assert c1m.estado == EstadoControl.VENCIDO and c1m.dias_vencido == 20
    assert por_codigo(agenda, "C3M").estado == por_codigo(agenda, "C6M").estado == EstadoControl.CERRADO_RECUPERADO
    # El esquema puede configurarse para cerrar también los vencidos.
    agenda = generar_agenda(nino, date(2026, 4, 1), replace(ESQUEMA_AGENDA_V1, cerrar_vencidos_al_recuperar=True))
    assert por_codigo(agenda, "C1M").estado == EstadoControl.CERRADO_RECUPERADO
    assert agenda.resumen.vencidos == 0


def test_cp58_evaluaciones_con_anemia_dentro_del_episodio_no_reinician_el_calendario():
    nino = nino_de(
        date(2025, 1, 1), [(date(2026, 1, 10), "MODERADA"), (date(2026, 2, 20), "LEVE"), (date(2026, 5, 1), "LEVE")]
    )
    controles = tratamiento(generar_agenda(nino, date(2026, 6, 1)))
    assert [(c.codigo, c.fecha_programada) for c in controles] == [
        ("C1M", date(2026, 2, 10)),
        ("C3M", date(2026, 4, 10)),
        ("C6M", date(2026, 7, 10)),
    ]
    assert controles[0].estado == EstadoControl.CUMPLIDO  # la evaluación del 20-feb cumple el C1M
    assert controles[1].estado == EstadoControl.CUMPLIDO  # y la del 1-may cumple el C3M (ventana hasta el 10-may)


def test_cp59_nuevo_episodio_tras_vencer_el_c6m_o_tras_una_recuperacion():
    # Tras C6M (10-jul + 30 d = 9-ago) una nueva anemia abre otro episodio.
    nino = nino_de(date(2025, 1, 1), [(date(2026, 1, 10), "LEVE"), (date(2026, 9, 1), "LEVE")])
    controles = tratamiento(generar_agenda(nino, date(2026, 9, 15)))
    assert len(controles) == 6 and controles[3].fecha_programada == date(2026, 10, 1)
    # Una recaída después de SIN_ANEMIA también abre otro episodio, aunque el C6M anterior no haya vencido.
    nino = nino_de(
        date(2025, 1, 1),
        [(date(2026, 1, 10), "LEVE"), (date(2026, 2, 12), "SIN_ANEMIA"), (date(2026, 4, 20), "MODERADA")],
    )
    controles = tratamiento(generar_agenda(nino, date(2026, 4, 21)))
    assert [(c.codigo, c.fecha_programada.isoformat()) for c in controles] == [
        ("C1M", "2026-02-10"),
        ("C3M", "2026-04-10"),
        ("C1M", "2026-05-20"),  # segundo episodio, desde el 20-abr
        ("C6M", "2026-07-10"),
        ("C3M", "2026-07-20"),
        ("C6M", "2026-10-20"),
    ]
    assert controles[0].estado == EstadoControl.CUMPLIDO  # la recuperación del 12-feb cumple el C1M del primero
    # El C3M del primer episodio (10-abr) quedó cumplido por la evaluación del 20-abr (dentro de su ventana);
    # el C6M del primer episodio, sin evaluación, se cierra por la recuperación.
    assert controles[1].estado == EstadoControl.CUMPLIDO and controles[3].estado == EstadoControl.CERRADO_RECUPERADO


def test_cp60_un_sin_anemia_el_mismo_dia_del_diagnostico_no_cuenta_como_recuperacion():
    nino = nino_de(date(2025, 1, 1), [(date(2026, 1, 10), "LEVE"), (date(2026, 1, 10), "SIN_ANEMIA")])
    controles = tratamiento(generar_agenda(nino, date(2026, 1, 11)))
    assert [c.estado for c in controles] == [EstadoControl.PENDIENTE] * 3


# --- Límite de edad, altas, orden y casos especiales -----------------------------------------------------------------


def test_cp61_los_controles_de_tratamiento_no_pasan_de_los_59_meses():
    nacimiento = date(2021, 10, 1)  # cumple 60 meses el 1-oct-2026
    hoy = date(2026, 9, 15)
    # C1M el 30-sep-2026 (59 meses): se programa; C3M y C6M (>= 60 meses): no.
    agenda = generar_agenda(nino_de(nacimiento, [(date(2026, 8, 30), "LEVE")]), hoy)
    assert [(c.codigo, c.fecha_programada) for c in agenda.controles] == [("C1M", date(2026, 9, 30))]
    # C1M el 1-oct-2026 (60 meses exactos): ningún control.
    agenda = generar_agenda(nino_de(nacimiento, [(date(2026, 9, 1), "LEVE")]), hoy)
    assert agenda.controles == [] and agenda.aplica and agenda.resumen.total == 0
    assert agenda.resumen.proximo_control is None


def test_cp62_un_dosaje_por_edad_de_60_meses_o_mas_no_se_programa():
    esquema = replace(ESQUEMA_AGENDA_V1, dosajes_por_edad=((58, "DHx"), (59, "DHc1"), (60, "DHc2")))
    agenda = generar_agenda(nino_de(date(2021, 10, 1), [(date(2026, 7, 1), "SIN_ANEMIA")]), date(2026, 7, 2), esquema)
    assert [c.codigo for c in agenda.controles] == ["DHx", "DHc1"]


def test_cp63_nino_con_alta_no_tiene_agenda():
    nino = nino_de(NACIMIENTO, [ANCLA], estado="ALTA")
    agenda = generar_agenda(nino, date(2026, 9, 28))
    assert not agenda.aplica and agenda.motivo == MOTIVO_ALTA
    assert agenda.controles == [] and agenda.resumen.total == 0 and agenda.resumen.vencidos == 0


def test_cp64_orden_resumen_y_proximo_control():
    # C1M y DHc2 caen el mismo día (01-ene-2026): el de tratamiento va primero.
    nino = nino_de(date(2025, 1, 1), [(date(2025, 12, 1), "LEVE")])
    agenda = generar_agenda(nino, date(2026, 1, 25))
    claves = [(c.fecha_programada, c.codigo) for c in agenda.controles]
    assert claves == sorted(claves, key=lambda k: k[0])
    assert [c.codigo for c in agenda.controles[:2]] == ["C1M", "DHc2"]
    r = agenda.resumen
    assert (r.vencidos, r.proximos) == (0, 2)  # ambos vencen el 31-ene (6 días): próximos a vencer
    assert r.total == r.cumplidos + r.pendientes + r.vencidos + r.cerrados
    assert r.proximo_control.codigo == "C1M"
    # Pasada la ventana, el próximo control es el primero que sigue PENDIENTE (no uno vencido).
    agenda = generar_agenda(nino, date(2026, 2, 5))
    assert agenda.resumen.vencidos == 2 and agenda.resumen.proximo_control.codigo not in ("C1M", "DHc2")
    assert agenda.resumen.proximo_control.estado == EstadoControl.PENDIENTE


def test_cp65_nino_sin_evaluaciones_usa_su_fecha_de_registro_como_inicio():
    nino = nino_de(date(2025, 3, 28))
    nino.creado_en = datetime(2026, 9, 29, 1, 30, tzinfo=UTC)  # 20:30 del 28-sep en Perú
    agenda = generar_agenda(nino, date(2026, 9, 28))
    assert agenda.controles[0].codigo == "DHc1" and agenda.controles[0].fecha_programada == date(2026, 9, 28)


def test_cp66_cada_control_cumplido_referencia_su_evaluacion_y_describe_el_dosaje():
    nino = nino_de(NACIMIENTO, [ANCLA, (date(2025, 9, 12), "SIN_ANEMIA")])
    agenda = generar_agenda(nino, date(2025, 9, 20))
    dhx = por_codigo(agenda, "DHx")
    assert dhx.evaluacion_id == nino.evaluaciones[1].id
    assert dhx.descripcion == "Dosaje de tamizaje DHx (6 meses)"
    assert por_codigo(agenda, "DHc1").descripcion == "Dosaje de control DHc1 (9 meses)"
    assert agenda.resumen.cumplidos == 1
