"""CP-123 a CP-130: asistencia a un control (HIST-2.4, ADR-010). Reglas de dominio puro: efecto en la agenda, en la
prioridad de las alertas y validación de los datos del registro.

Niño base: nace el 10-mar-2025, primera evaluación el 10-jun-2025 (inicio de la agenda). Su DHx de 6 meses se programa
el 10-sep-2025, con ventana del 26-ago al 10-oct-2025; su DHc1 de 9 meses, el 10-dic-2025.
"""

from datetime import date

import pytest

from app.domain.model.agenda import ControlProgramado, EstadoControl, TipoControl
from app.domain.model.alertas import Prioridad
from app.domain.model.asistencia import AsistenciaControl, EstadoAsistencia
from app.domain.model.clasificacion import Clasificacion
from app.domain.model.errores import ConflictoAsistencia, ErrorValidacion, NoEncontrado
from app.domain.service.agenda import generar_agenda
from app.domain.service.alertas import alertas_de_nino, calcular_prioridad
from app.domain.service.asistencia import localizar_control_registrable, validar_datos_asistencia
from tests.conftest import evaluacion_de, nino_de

NACIMIENTO = date(2025, 3, 10)
ANCLA = (date(2025, 6, 10), "NO_APLICA")
DHX = date(2025, 9, 10)
DHC1 = date(2025, 12, 10)
ASISTIO, NO_ASISTIO = EstadoAsistencia.ASISTIO, EstadoAsistencia.NO_ASISTIO


def asistencia(nino, estado, codigo="DHx", programada=DHX, **cambios):
    a = AsistenciaControl(nino.id, codigo, programada, estado, "enf.rosa", **cambios)
    nino.asistencias.append(a)
    return a


def control(agenda, codigo, programada):
    return next(c for c in agenda.controles if c.codigo == codigo and c.fecha_programada == programada)


def test_cp123_asistio_cumple_el_control_aunque_no_haya_evaluacion():
    nino = nino_de(NACIMIENTO, [ANCLA])
    hoy = date(2025, 9, 15)
    antes = generar_agenda(nino, hoy)
    assert control(antes, "DHx", DHX).estado == EstadoControl.PENDIENTE
    a = asistencia(nino, ASISTIO)
    agenda = generar_agenda(nino, hoy)
    c = control(agenda, "DHx", DHX)
    assert c.estado == EstadoControl.CUMPLIDO and c.cumplido_por_asistencia and c.asistencia_id == a.id
    assert c.evaluacion_id is None and not c.inasistencia_registrada
    assert agenda.resumen.cumplidos == antes.resumen.cumplidos + 1
    assert agenda.resumen.pendientes == antes.resumen.pendientes - 1


def test_cp124_asistio_cumple_un_control_vencido_y_la_evaluacion_vinculada_se_le_asigna_a_el():
    ev = evaluacion_de(date(2025, 12, 1), "SIN_ANEMIA")  # fuera de la ventana del DHx, dentro de la del DHc1
    nino = nino_de(NACIMIENTO, [ANCLA, ev])
    hoy = date(2025, 12, 5)
    sin_vinculo = generar_agenda(nino, hoy)
    assert control(sin_vinculo, "DHx", DHX).estado == EstadoControl.VENCIDO
    assert control(sin_vinculo, "DHc1", DHC1).evaluacion_id == ev.id  # por cercanía cumple el DHc1
    asistencia(nino, ASISTIO, evaluacion_id=ev.id)
    agenda = generar_agenda(nino, hoy)
    dhx, dhc1 = control(agenda, "DHx", DHX), control(agenda, "DHc1", DHC1)
    assert dhx.estado == EstadoControl.CUMPLIDO and dhx.evaluacion_id == ev.id and dhx.cumplido_por_asistencia
    assert dhc1.estado == EstadoControl.PENDIENTE and dhc1.evaluacion_id is None  # cada evaluación sirve a un control


def test_cp125_no_asistio_no_cambia_el_estado_solo_lo_marca():
    nino = nino_de(NACIMIENTO, [ANCLA])
    asistencia(nino, NO_ASISTIO, motivo="Viaje")
    pendiente = control(generar_agenda(nino, date(2025, 9, 15)), "DHx", DHX)
    assert pendiente.estado == EstadoControl.PENDIENTE and pendiente.inasistencia_registrada
    assert pendiente.motivo_inasistencia == "Viaje" and not pendiente.cumplido_por_asistencia
    agenda = generar_agenda(nino, date(2025, 10, 20))
    vencido = control(agenda, "DHx", DHX)
    assert (vencido.estado, vencido.dias_vencido, vencido.inasistencia_registrada) == (EstadoControl.VENCIDO, 10, True)
    assert agenda.resumen.inasistencias == 1
    otro = control(agenda, "DHc1", DHC1)
    assert not otro.inasistencia_registrada  # la marca es solo del control indicado


def test_cp126_si_despues_una_evaluacion_cumple_el_control_deja_de_figurar_la_inasistencia():
    nino = nino_de(NACIMIENTO, [ANCLA, (date(2025, 9, 20), "SIN_ANEMIA")])
    asistencia(nino, NO_ASISTIO, motivo="Enfermedad del niño")
    c = control(generar_agenda(nino, date(2025, 9, 28)), "DHx", DHX)
    assert c.estado == EstadoControl.CUMPLIDO and not c.inasistencia_registrada and c.motivo_inasistencia is None


def test_cp127_una_asistencia_que_no_corresponde_a_ningun_control_se_ignora():
    nino = nino_de(NACIMIENTO, [ANCLA])
    asistencia(nino, ASISTIO, codigo="DHx", programada=date(2025, 9, 11))  # fecha que no es la programada
    asistencia(nino, ASISTIO, codigo="C1M", programada=date(2025, 7, 10))  # el niño no tiene tratamiento
    asistencia(nino, ASISTIO, codigo="DHc1", programada=DHC1, evaluacion_id="evaluacion-inexistente")
    agenda = generar_agenda(nino, date(2025, 9, 15))
    assert control(agenda, "DHx", DHX).estado == EstadoControl.PENDIENTE
    assert (
        agenda.resumen.cumplidos
        == generar_agenda(nino_de(NACIMIENTO, [ANCLA]), date(2025, 9, 15)).resumen.cumplidos + 1
    )


@pytest.mark.parametrize(
    "dias, ultima, base, con_inasistencia",
    [
        (3, Clasificacion.SIN_ANEMIA, Prioridad.BAJA, Prioridad.MEDIA),
        (7, Clasificacion.SIN_ANEMIA, Prioridad.BAJA, Prioridad.MEDIA),
        (8, Clasificacion.SIN_ANEMIA, Prioridad.MEDIA, Prioridad.ALTA),
        (30, Clasificacion.LEVE, Prioridad.MEDIA, Prioridad.ALTA),
        (31, Clasificacion.SIN_ANEMIA, Prioridad.ALTA, Prioridad.ALTA),  # ALTA no sube más
        (3, Clasificacion.MODERADA, Prioridad.ALTA, Prioridad.ALTA),
    ],
)
def test_cp128_la_inasistencia_registrada_sube_la_prioridad_un_nivel(dias, ultima, base, con_inasistencia):
    def ctrl(marcado):
        return ControlProgramado(
            codigo="DHx",
            tipo=TipoControl.TAMIZAJE_EDAD,
            fecha_programada=date(2026, 6, 1),
            fecha_limite=date(2026, 7, 1),
            estado=EstadoControl.VENCIDO,
            dias_vencido=dias,
            evaluacion_id=None,
            descripcion="prueba",
            fecha_inicio_ventana=date(2026, 5, 17),
            inasistencia_registrada=marcado,
        )

    assert calcular_prioridad(ctrl(False), ultima) == base
    assert calcular_prioridad(ctrl(True), ultima) == con_inasistencia


def test_cp128_la_alerta_de_un_control_con_inasistencia_sube_de_prioridad():
    nino = nino_de(NACIMIENTO, [ANCLA])
    hoy = date(2025, 10, 15)  # DHx vencido hace 5 días: BAJA
    assert [a.prioridad for a in alertas_de_nino(nino, generar_agenda(nino, hoy)) if a.control.codigo == "DHx"] == [
        Prioridad.BAJA
    ]
    asistencia(nino, NO_ASISTIO, motivo="Olvido de la cita")
    alerta = next(a for a in alertas_de_nino(nino, generar_agenda(nino, hoy)) if a.control.codigo == "DHx")
    assert alerta.prioridad == Prioridad.MEDIA and alerta.control.inasistencia_registrada


@pytest.mark.parametrize(
    "datos, campos",
    [
        ({"estado": "ASISTIO", "fecha_programada": DHX}, set()),
        ({"estado": "NO_ASISTIO", "fecha_programada": DHX, "motivo": "Viaje"}, set()),
        ({"estado": "TALVEZ", "fecha_programada": DHX}, {"estado"}),
        ({"estado": None, "fecha_programada": DHX}, {"estado"}),
        ({"estado": "ASISTIO", "fecha_programada": None}, {"fecha_programada"}),
        ({"estado": "ASISTIO", "fecha_programada": date(2025, 9, 16)}, {"fecha_programada"}),  # futura (hoy = 15)
        ({"estado": "NO_ASISTIO", "fecha_programada": DHX}, {"motivo"}),
        ({"estado": "NO_ASISTIO", "fecha_programada": DHX, "motivo": "  a "}, {"motivo"}),
        ({"estado": "NO_ASISTIO", "fecha_programada": DHX, "motivo": "x" * 201}, {"motivo"}),
        ({"estado": "ASISTIO", "fecha_programada": DHX, "motivo": "x" * 201}, {"motivo"}),
        (
            {"estado": "NO_ASISTIO", "fecha_programada": DHX, "motivo": "Viaje", "evaluacion_id": "e1"},
            {"evaluacion_id"},
        ),
    ],
)
def test_cp129_validacion_de_los_datos_de_la_asistencia(datos, campos):
    assert {e.campo for e in validar_datos_asistencia(datos, date(2025, 9, 15))} == campos


def test_cp129_la_fecha_programada_de_hoy_se_acepta():
    assert validar_datos_asistencia({"estado": "ASISTIO", "fecha_programada": DHX}, DHX) == []


def test_cp130_localizar_el_control_registrable_y_sus_conflictos():
    ev = evaluacion_de(date(2025, 12, 1), "SIN_ANEMIA")
    nino = nino_de(NACIMIENTO, [ANCLA, ev])
    hoy = date(2025, 12, 5)
    agenda = generar_agenda(nino, hoy)

    def pedir(codigo="DHx", programada=DHX, **extra):
        return localizar_control_registrable(nino, agenda, {"codigo": codigo, "fecha_programada": programada, **extra})

    assert pedir().estado == EstadoControl.VENCIDO
    with pytest.raises(NoEncontrado):
        pedir("DHx", date(2025, 9, 11))
    with pytest.raises(NoEncontrado):
        pedir("C1M", DHX)
    with pytest.raises(ConflictoAsistencia, match="ya está cumplido"):
        pedir("DHc1", DHC1)  # cumplido por la evaluación del 1-dic
    with pytest.raises(ErrorValidacion) as e:
        pedir(evaluacion_id="de-otro-niño")
    assert e.value.errores[0].campo == "evaluacion_id"
    with pytest.raises(ErrorValidacion) as e:
        pedir(evaluacion_id=ev.id)  # ya cumple el DHc1
    assert "ya cumple otro control" in e.value.errores[0].mensaje
    nino.asistencias.append(AsistenciaControl(nino.id, "DHx", DHX, NO_ASISTIO, "a", motivo="Viaje"))
    with pytest.raises(ConflictoAsistencia, match="ya tiene una asistencia"):
        pedir()


def test_cp130_un_control_cerrado_por_recuperacion_no_admite_asistencia():
    # Anemia leve el 10-jun-2025 y recuperación (sin anemia) el 10-jul: C3M y C6M aún no vencían y quedan cerrados.
    nino = nino_de(NACIMIENTO, [(date(2025, 6, 10), "LEVE"), (date(2025, 7, 10), "SIN_ANEMIA")])
    agenda = generar_agenda(nino, date(2025, 7, 20))
    cerrado = next(c for c in agenda.controles if c.estado == EstadoControl.CERRADO_RECUPERADO)
    with pytest.raises(ConflictoAsistencia, match="cerrado por recuperación"):
        localizar_control_registrable(
            nino, agenda, {"codigo": cerrado.codigo, "fecha_programada": cerrado.fecha_programada}
        )


def test_cp189_el_repositorio_en_memoria_rechaza_una_asistencia_repetida_como_la_base():
    from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria

    repo = RepositorioEnMemoria()
    nino = repo.guardar(nino_de(date(2025, 3, 10), [(date(2025, 6, 10), "NO_APLICA")]))
    primera = AsistenciaControl(nino.id, "DHx", date(2025, 9, 10), EstadoAsistencia.NO_ASISTIO, "enf", motivo="Viaje")
    repo.agregar_asistencia(primera)
    with pytest.raises(ConflictoAsistencia, match="ya tiene una asistencia"):
        repo.agregar_asistencia(AsistenciaControl(nino.id, "DHx", date(2025, 9, 10), EstadoAsistencia.ASISTIO, "enf"))
    repo.agregar_asistencia(AsistenciaControl(nino.id, "DHx", date(2026, 6, 10), EstadoAsistencia.ASISTIO, "enf"))
    assert len(repo.obtener(nino.id).asistencias) == 2
