"""CP-13 a CP-20: casos de uso con el adaptador en memoria (sin base de datos ni HTTP)."""

from datetime import date

import pytest

from app.domain.errores import ErrorValidacion, NoEncontrado, RegistroDuplicado
from app.domain.reglas_clinicas import Clasificacion
from tests.conftest import datos_eval, datos_nino


def test_registrar_nino_crea_expediente_con_evaluacion_clasificada(servicio):
    nino = servicio.registrar_nino(datos_nino(), datos_eval(), "enf.demo")
    assert nino.dni == "71234567" and len(nino.evaluaciones) == 1
    e = nino.evaluaciones[0]
    assert e.hemoglobina_ajustada == 9.9 and e.clasificacion == Clasificacion.LEVE
    assert e.edad_meses == 11 and e.registrado_por == "enf.demo"


def test_registro_duplicado_por_dni_se_rechaza(servicio):
    servicio.registrar_nino(datos_nino(), datos_eval(), "a")
    with pytest.raises(RegistroDuplicado):
        servicio.registrar_nino(datos_nino(nombres="Otro"), datos_eval(), "a")


def test_registro_invalido_acumula_errores_de_nino_y_evaluacion(servicio):
    with pytest.raises(ErrorValidacion) as exc:
        servicio.registrar_nino(datos_nino(dni="12"), datos_eval(hemoglobina_observada=30), "a")
    assert {e.campo for e in exc.value.errores} == {"dni", "hemoglobina_observada"}


def test_consultar_y_buscar_por_dni(servicio):
    nino = servicio.registrar_nino(datos_nino(), datos_eval(), "a")
    assert servicio.consultar(nino.id).id == nino.id
    assert servicio.consultar_por_dni("71234567").id == nino.id
    with pytest.raises(NoEncontrado):
        servicio.consultar("no-existe")
    with pytest.raises(NoEncontrado):
        servicio.consultar_por_dni("00000000")


def test_actualizar_datos_editables(servicio):
    nino = servicio.registrar_nino(datos_nino(), datos_eval(), "a")
    act = servicio.actualizar_datos(nino.id, {"comunidad": "Llacuas", "tutor_celular": "", "estado": "ALTA"}, "b")
    assert act.comunidad == "Llacuas" and act.tutor_celular is None and act.estado == "ALTA"
    assert len(act.evaluaciones) == 1


@pytest.mark.parametrize(
    "cambios, campo",
    [({"dni": "11111111"}, "dni"), ({"estado": "BORRADO"}, "estado"), ({"altitud_m": 9000}, "altitud_m")],
)
def test_actualizar_rechaza_cambios_invalidos(servicio, cambios, campo):
    nino = servicio.registrar_nino(datos_nino(), datos_eval(), "a")
    with pytest.raises(ErrorValidacion) as exc:
        servicio.actualizar_datos(nino.id, cambios, "b")
    assert campo in {e.campo for e in exc.value.errores}


def test_registrar_nuevo_control(servicio):
    nino = servicio.registrar_nino(datos_nino(), datos_eval(), "a")
    act = servicio.registrar_evaluacion(nino.id, datos_eval(fecha=date(2026, 9, 27), hemoglobina_observada=13.2), "b")
    assert len(act.evaluaciones) == 2
    assert act.ultima_evaluacion.clasificacion == Clasificacion.SIN_ANEMIA
    with pytest.raises(ErrorValidacion):
        servicio.registrar_evaluacion(nino.id, datos_eval(fecha=date(2024, 1, 1)), "b")


def test_vista_previa_no_guarda(servicio):
    e = servicio.previsualizar_evaluacion(date(2025, 10, 15), 3720, datos_eval())
    assert e.clasificacion == Clasificacion.LEVE
    assert servicio.listar_seguimiento() == []


def test_listar_seguimiento_prioriza_casos_graves_y_filtra(servicio):
    servicio.registrar_nino(datos_nino(dni="70000001"), datos_eval(hemoglobina_observada=13.5), "a")
    servicio.registrar_nino(
        datos_nino(dni="70000002", comunidad="Llacuas"),
        datos_eval(hemoglobina_observada=9.0, fecha=date(2026, 8, 1)),
        "a",
    )
    filas = servicio.listar_seguimiento()
    assert [f["nino"].dni for f in filas] == ["70000002", "70000001"]
    assert filas[0]["control_atrasado"] and filas[0]["dias_desde_ultimo_control"] == 58
    assert len(servicio.listar_seguimiento(texto="llacuas")) == 1
    assert len(servicio.listar_seguimiento(clasificacion="SIN_ANEMIA")) == 1
    assert servicio.listar_seguimiento(estado="ALTA") == []


def test_reporte_del_periodo(servicio):
    servicio.registrar_nino(datos_nino(dni="70000001"), datos_eval(hemoglobina_observada=13.5), "a")
    n2 = servicio.registrar_nino(
        datos_nino(dni="70000002", comunidad="Llacuas"), datos_eval(hemoglobina_observada=10.0), "a"
    )
    servicio.registrar_evaluacion(n2.id, datos_eval(fecha=date(2026, 9, 25), hemoglobina_observada=10.5), "a")
    r = servicio.reporte_periodo(date(2026, 9, 1), date(2026, 9, 30))
    assert r["evaluaciones_realizadas"] == 3 and r["ninos_evaluados"] == 2 and r["ninos_con_anemia"] == 1
    assert r["por_clasificacion"]["SIN_ANEMIA"] == 1
    assert [c["comunidad"] for c in r["por_comunidad"]] == ["Llacuas", "Palmayoc"]
    with pytest.raises(ErrorValidacion):
        servicio.reporte_periodo(date(2026, 9, 30), date(2026, 9, 1))


def test_reporte_cuenta_registros_nocturnos_en_el_dia_local(servicio):
    # DEF-02: un niño registrado a las 20:30 en Perú pertenece a ese día, aunque en UTC ya sea el siguiente.
    from datetime import UTC, datetime

    nino = servicio.registrar_nino(datos_nino(dni="70000009"), datos_eval(), "a")
    nino.creado_en = datetime(2026, 9, 29, 1, 30, tzinfo=UTC)
    servicio.repo.actualizar(nino)
    assert servicio.reporte_periodo(date(2026, 9, 28), date(2026, 9, 28))["ninos_registrados"] == 1
    assert servicio.reporte_periodo(date(2026, 9, 29), date(2026, 9, 29))["ninos_registrados"] == 0


def test_reloj_del_sistema_usa_la_fecha_de_peru():
    # DEF-02: un servidor en UTC (p. ej. un contenedor Docker) no debe adelantar el día después de las 19:00.
    from datetime import datetime

    from app.application.casos_uso import RelojSistema
    from app.domain.entidades import ZONA_PERU

    assert RelojSistema().hoy() == datetime.now(ZONA_PERU).date()
