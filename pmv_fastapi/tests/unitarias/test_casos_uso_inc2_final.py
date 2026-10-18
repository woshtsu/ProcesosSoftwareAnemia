"""CP-131 a CP-139: casos de uso de HIST-2.3 (agenda del personal) y HIST-2.4 (asistencia) con el repositorio en memoria.

Mismo escenario de test_casos_uso_inc2 (hoy = 28-sep-2026): V con tres dosajes de edad vencidos (palmayoc), T con el C1M
de tratamiento vencido (Llacuas), M y B con el DHx de 15 meses vencido hace 8 y 7 días (Chongos Alto y Huaycha) y A con alta.
"""

from datetime import date

import pytest

from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria
from app.application.servicio_agenda import ServicioAgenda
from app.application.servicio_agenda_personal import ServicioAgendaPersonal
from app.application.servicio_alertas import ServicioAlertas
from app.application.servicio_asistencia import ServicioAsistencia
from app.application.servicio_contexto import ServicioContexto
from app.domain.model.agenda import EstadoControl
from app.domain.model.alertas import Prioridad
from app.domain.model.asistencia import EstadoAsistencia
from app.domain.model.errores import ConflictoAsistencia, ErrorValidacion, NoEncontrado
from app.domain.service.agenda_personal import resolver_rango, semana_de
from tests.conftest import HOY, RelojFijo, datos_eval, datos_nino


def registrar(servicio, dni, nacimiento, fecha_eval, comunidad, hb=13.5, **extra):
    return servicio.registrar_nino(
        datos_nino(dni=dni, fecha_nacimiento=nacimiento, comunidad=comunidad, **extra),
        datos_eval(fecha=fecha_eval, hemoglobina_observada=hb),
        "a",
    )


@pytest.fixture
def escenario(servicio):
    ninos = {
        "V": registrar(servicio, "70000001", date(2025, 3, 10), date(2025, 9, 12), "Palmayoc"),
        "T": registrar(servicio, "70000002", date(2025, 9, 1), date(2026, 7, 1), "Llacuas", hb=11.0),
        "M": registrar(servicio, "70000003", date(2025, 5, 21), date(2026, 8, 1), "Chongos Alto"),
        "B": registrar(servicio, "70000004", date(2025, 5, 22), date(2026, 8, 1), "Huaycha"),
        "A": registrar(servicio, "70000005", date(2025, 3, 10), date(2025, 9, 12), "Palmayoc"),
    }
    servicio.actualizar_datos(ninos["A"].id, {"estado": "ALTA"}, "a")
    return servicio, ninos


@pytest.fixture
def asistencia(escenario, reloj):
    return ServicioAsistencia(escenario[0].repo, reloj)


@pytest.fixture
def personal(escenario, reloj):
    return ServicioAgendaPersonal(escenario[0].repo, reloj)


def control_de(servicio, nino, codigo, programada=None):
    agenda = ServicioAgenda(servicio.repo, RelojFijo()).generar_agenda(nino.id)
    return next(
        c for c in agenda.controles if c.codigo == codigo and (programada is None or c.fecha_programada == programada)
    )


# --- HIST-2.4 -------------------------------------------------------------------------------------------------------


def test_cp131_registrar_asistio_guarda_usuario_y_fecha_y_cumple_el_control(escenario, asistencia):
    servicio, ninos = escenario
    c = control_de(servicio, ninos["V"], "DHc1")
    assert c.estado == EstadoControl.VENCIDO
    a = asistencia.registrar_asistencia(
        ninos["V"].id, "DHc1", {"fecha_programada": c.fecha_programada, "estado": "ASISTIO"}, "enf.rosa"
    )
    assert (a.codigo_control, a.fecha_programada, a.estado, a.registrado_por) == (
        "DHc1",
        c.fecha_programada,
        "ASISTIO",
        "enf.rosa",
    )
    assert a.id and a.creado_en and a.motivo is None and a.evaluacion_id is None
    despues = control_de(servicio, ninos["V"], "DHc1")
    assert despues.estado == EstadoControl.CUMPLIDO and despues.cumplido_por_asistencia


def test_cp132_no_asistio_deja_el_control_vencido_con_marca_y_sube_la_prioridad_de_la_alerta(
    escenario, asistencia, reloj
):
    servicio, ninos = escenario
    alertas = ServicioAlertas(servicio.repo, reloj)
    antes = {a.nino_id: a for a in alertas.listar_controles_vencidos()}
    assert antes[ninos["B"].id].prioridad == Prioridad.BAJA and antes[ninos["M"].id].prioridad == Prioridad.MEDIA
    for clave in ("B", "M"):
        c = control_de(servicio, ninos[clave], "DHx")
        asistencia.registrar_asistencia(
            ninos[clave].id,
            "DHx",
            {"fecha_programada": c.fecha_programada, "estado": "NO_ASISTIO", "motivo": "Viaje"},
            "tec.juan",
        )
    despues = {a.nino_id: a for a in alertas.listar_controles_vencidos()}
    assert despues[ninos["B"].id].prioridad == Prioridad.MEDIA  # BAJA sube a MEDIA
    assert despues[ninos["M"].id].prioridad == Prioridad.ALTA  # MEDIA sube a ALTA
    assert all(despues[ninos[k].id].control.inasistencia_registrada for k in ("B", "M"))
    assert len(despues) == len(antes)  # la alerta no desaparece: el control sigue vencido
    assert alertas.resumen_alertas().por_prioridad["ALTA"] == 4 + 1  # V x3, T y ahora M


def test_cp133_no_se_registra_dos_veces_el_mismo_control(escenario, asistencia):
    servicio, ninos = escenario
    c = control_de(servicio, ninos["V"], "DHc1")
    datos = {"fecha_programada": c.fecha_programada, "estado": "NO_ASISTIO", "motivo": "Viaje"}
    asistencia.registrar_asistencia(ninos["V"].id, "DHc1", datos, "a")
    with pytest.raises(ConflictoAsistencia, match="ya tiene una asistencia"):
        asistencia.registrar_asistencia(ninos["V"].id, "DHc1", {**datos, "estado": "ASISTIO"}, "a")
    assert len(asistencia.listar_asistencias(ninos["V"].id)) == 1


def test_cp134_errores_de_registro_404_409_y_422(escenario, asistencia):
    servicio, ninos = escenario
    c = control_de(servicio, ninos["V"], "DHc1")
    base = {"fecha_programada": c.fecha_programada, "estado": "ASISTIO"}
    with pytest.raises(NoEncontrado):
        asistencia.registrar_asistencia("no-existe", "DHc1", base, "a")
    with pytest.raises(NoEncontrado):
        asistencia.listar_asistencias("no-existe")
    with pytest.raises(NoEncontrado, match="no tiene programado"):
        asistencia.registrar_asistencia(ninos["V"].id, "C6M", base, "a")
    with pytest.raises(NoEncontrado):  # el niño con alta no tiene agenda
        asistencia.registrar_asistencia(ninos["A"].id, "DHc1", base, "a")
    futura = control_de(servicio, ninos["T"], "C3M")  # programado para el 1-oct-2026, hoy es 28-sep
    with pytest.raises(ErrorValidacion) as e:
        asistencia.registrar_asistencia(
            ninos["T"].id, "C3M", {"fecha_programada": futura.fecha_programada, "estado": "ASISTIO"}, "a"
        )
    assert e.value.errores[0].campo == "fecha_programada" and "futura" in e.value.errores[0].mensaje
    with pytest.raises(ErrorValidacion) as e:
        asistencia.registrar_asistencia(ninos["V"].id, "DHc1", {**base, "estado": "NO_ASISTIO"}, "a")
    assert e.value.errores[0].campo == "motivo"
    cumplido = control_de(servicio, ninos["V"], "DHx", date(2025, 9, 10))
    assert cumplido.estado == EstadoControl.CUMPLIDO
    with pytest.raises(ConflictoAsistencia, match="ya está cumplido"):
        asistencia.registrar_asistencia(
            ninos["V"].id,
            "DHx",
            {"fecha_programada": cumplido.fecha_programada, "estado": "NO_ASISTIO", "motivo": "Viaje"},
            "a",
        )


def test_cp135_asistio_con_la_evaluacion_del_dia_vinculada(escenario, asistencia):
    servicio, ninos = escenario
    v = ninos["V"]
    # El niño volvió el 20-jul-2026: fuera de la ventana del DHx de 15 meses (10-jun) y de la del siguiente control.
    exp = servicio.registrar_evaluacion(v.id, datos_eval(fecha=date(2026, 7, 20)), "a")
    ev = max(exp.evaluaciones, key=lambda e: e.fecha)
    dhx_15 = control_de(servicio, v, "DHx", date(2026, 6, 10))
    assert dhx_15.estado == EstadoControl.VENCIDO
    a = asistencia.registrar_asistencia(
        v.id, "DHx", {"fecha_programada": dhx_15.fecha_programada, "estado": "ASISTIO", "evaluacion_id": ev.id}, "a"
    )
    assert a.evaluacion_id == ev.id
    despues = control_de(servicio, v, "DHx", date(2026, 6, 10))
    assert despues.estado == EstadoControl.CUMPLIDO and despues.evaluacion_id == ev.id
    with pytest.raises(ErrorValidacion):  # esa evaluación ya cumple un control
        asistencia.registrar_asistencia(
            v.id, "DHc1", {"fecha_programada": date(2025, 12, 10), "estado": "ASISTIO", "evaluacion_id": ev.id}, "a"
        )


def test_cp136_listar_asistencias_ordenadas_por_fecha_programada(escenario, asistencia):
    servicio, ninos = escenario
    v = ninos["V"]
    for codigo, programada in (("DHx", date(2026, 6, 10)), ("DHc1", date(2025, 12, 10))):
        asistencia.registrar_asistencia(
            v.id, codigo, {"fecha_programada": programada, "estado": "NO_ASISTIO", "motivo": "Olvido de la cita"}, "a"
        )
    lista = asistencia.listar_asistencias(v.id)
    assert [a.fecha_programada for a in lista] == [date(2025, 12, 10), date(2026, 6, 10)]
    assert all(a.estado == EstadoAsistencia.NO_ASISTIO for a in lista)


# --- HIST-2.3 -------------------------------------------------------------------------------------------------------


def test_cp137_rango_por_defecto_y_validacion(personal, reloj):
    lunes, domingo = semana_de(HOY)
    assert (lunes.weekday(), domingo.weekday(), (domingo - lunes).days) == (0, 6, 6)
    assert lunes <= HOY <= domingo
    por_defecto = personal.agenda_personal()
    assert (por_defecto.desde, por_defecto.hasta, por_defecto.fecha_referencia) == (lunes, domingo, HOY)
    assert len(por_defecto.dias) == 7
    assert resolver_rango(date(2026, 9, 1), None, HOY) == (date(2026, 9, 1), date(2026, 9, 7))
    assert resolver_rango(None, date(2026, 9, 30), HOY) == (date(2026, 9, 24), date(2026, 9, 30))
    assert len(personal.agenda_personal(date(2026, 9, 1), date(2026, 10, 1)).dias) == 31  # 31 días exactos: permitido
    for desde, hasta, campo in (
        (date(2026, 9, 1), date(2026, 10, 2), "hasta"),  # 32 días
        (date(2026, 9, 30), date(2026, 9, 1), "desde"),
        (date(1999, 1, 1), date(1999, 1, 5), "desde"),
        (date(2026, 1, 1), date(2101, 1, 1), "hasta"),
    ):
        with pytest.raises(ErrorValidacion) as e:
            personal.agenda_personal(desde, hasta)
        assert e.value.errores[0].campo == campo


def test_cp138_agenda_por_dia_con_totales_estado_y_prioridad(personal):
    ag = personal.agenda_personal(date(2026, 8, 1), date(2026, 8, 31))
    assert len(ag.dias) == 31
    con_controles = {d.fecha: d for d in ag.dias if d.total}
    assert sorted(con_controles) == [date(2026, 8, 1), date(2026, 8, 21), date(2026, 8, 22)]
    primero = con_controles[date(2026, 8, 1)]
    (item,) = primero.items
    assert (item.control.codigo, item.control.estado, item.prioridad) == ("C1M", EstadoControl.VENCIDO, Prioridad.ALTA)
    assert item.nombre_completo == "Luz Mery Quispe Rojas" and item.comunidad == "Llacuas"
    assert (primero.total, primero.vencidos, primero.pendientes, primero.cumplidos) == (1, 1, 0, 0)
    assert con_controles[date(2026, 8, 21)].items[0].prioridad == Prioridad.MEDIA
    assert con_controles[date(2026, 8, 22)].items[0].prioridad == Prioridad.BAJA
    assert (ag.resumen.total, ag.resumen.vencidos, ag.resumen.ninos) == (3, 3, 3)
    assert all(d.total == 0 and d.items == [] for d in ag.dias if d.fecha not in con_controles)


def test_cp139_incluye_pendientes_y_cumplidos_ordenados_y_excluye_cerrados_y_altas(escenario, personal):
    servicio, ninos = escenario
    ag = personal.agenda_personal(date(2025, 9, 1), date(2025, 9, 30))  # el DHx de 6 meses de V y A (A tiene alta)
    dia = next(d for d in ag.dias if d.fecha == date(2025, 9, 10))
    assert [i.nino_id for i in dia.items] == [ninos["V"].id] and dia.cumplidos == 1
    assert dia.items[0].prioridad is None and dia.items[0].control.estado == EstadoControl.CUMPLIDO
    septiembre = personal.agenda_personal(date(2026, 9, 1), date(2026, 9, 30))
    estados = {(i.control.codigo, i.control.estado) for d in septiembre.dias for i in d.items}
    assert ("DHc2", EstadoControl.PENDIENTE) in estados  # T: DHc2 del 1-sep, vence el 1-oct
    assert septiembre.resumen.pendientes == sum(d.pendientes for d in septiembre.dias) >= 2


def test_cp139_filtros_por_establecimiento_y_comunidad_con_opciones_disponibles(escenario, personal):
    servicio, ninos = escenario
    otro = registrar(
        servicio, "70000009", date(2025, 3, 10), date(2025, 9, 12), "Palmayoc", establecimiento="P. S. Palmayoc"
    )
    rango = (date(2025, 12, 1), date(2025, 12, 31))  # DHc1 de 9 meses de V, A (alta) y del nuevo niño
    todos = personal.agenda_personal(*rango)
    assert {i.nino_id for d in todos.dias for i in d.items} == {ninos["V"].id, otro.id}
    assert todos.establecimientos_disponibles == ["P. S. Chongos Alto", "P. S. Palmayoc"]
    assert todos.comunidades_disponibles == ["Chongos Alto", "Huaycha", "Llacuas", "Palmayoc"]
    solo = personal.agenda_personal(*rango, establecimiento="p. s. palmayoc")
    assert {i.nino_id for d in solo.dias for i in d.items} == {otro.id}
    assert solo.establecimiento == "p. s. palmayoc" and solo.comunidades_disponibles == ["Palmayoc"]
    assert solo.establecimientos_disponibles == todos.establecimientos_disponibles  # las opciones no se acotan solas
    assert {i.nino_id for d in personal.agenda_personal(*rango, comunidad="PALMAYOC").dias for i in d.items} == {
        ninos["V"].id,
        otro.id,
    }
    assert (
        personal.agenda_personal(*rango, establecimiento="P. S. Chongos Alto", comunidad="Llacuas").resumen.total == 0
    )
    assert personal.agenda_personal(*rango, establecimiento="", comunidad="").resumen.total == todos.resumen.total


def test_cp140_la_asistencia_se_refleja_en_la_agenda_del_personal(escenario, personal, asistencia):
    servicio, ninos = escenario
    rango = (date(2026, 8, 20), date(2026, 8, 22))
    antes = personal.agenda_personal(*rango)
    assert (antes.resumen.vencidos, antes.resumen.con_inasistencia) == (2, 0)
    asistencia.registrar_asistencia(
        ninos["M"].id, "DHx", {"fecha_programada": date(2026, 8, 21), "estado": "ASISTIO"}, "a"
    )
    asistencia.registrar_asistencia(
        ninos["B"].id, "DHx", {"fecha_programada": date(2026, 8, 22), "estado": "NO_ASISTIO", "motivo": "Viaje"}, "a"
    )
    despues = personal.agenda_personal(*rango)
    assert (despues.resumen.cumplidos, despues.resumen.vencidos, despues.resumen.con_inasistencia) == (1, 1, 1)
    dia22 = next(d for d in despues.dias if d.fecha == date(2026, 8, 22))
    assert dia22.con_inasistencia == 1 and dia22.items[0].prioridad == Prioridad.MEDIA  # BAJA subió un nivel


def test_cp141_la_agenda_del_personal_se_calcula_con_una_sola_consulta_por_lotes(escenario, reloj):
    servicio, _ = escenario

    class Espia(RepositorioEnMemoria):
        llamadas: list[str] = []

        def listar(self, *a, **k):
            self.llamadas.append("listar")
            return super().listar(*a, **k)

        def obtener(self, *a, **k):
            self.llamadas.append("obtener")
            return super().obtener(*a, **k)

    espia = Espia()
    espia._ninos = servicio.repo._ninos
    ServicioAgendaPersonal(espia, reloj).agenda_personal(date(2026, 8, 1), date(2026, 8, 31))
    assert Espia.llamadas == ["listar"]  # una consulta, sin consultas por niño


def test_cp142_contexto_con_y_sin_fecha_de_referencia():
    sin = ServicioContexto(RelojFijo(date(2026, 9, 28))).contexto()
    assert (sin.fecha_hoy, sin.fecha_referencia) == (date(2026, 9, 28), None)
    con = ServicioContexto(RelojFijo(date(2024, 6, 30)), date(2024, 6, 30)).contexto()
    assert (con.fecha_hoy, con.fecha_referencia) == (date(2024, 6, 30), date(2024, 6, 30))
