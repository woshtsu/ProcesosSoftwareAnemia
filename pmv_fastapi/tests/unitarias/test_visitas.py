"""CP-188 a CP-205: visita domiciliaria priorizada (VIS-3.5, ADR-013). Reglas de dominio puro y caso de uso con el
repositorio en memoria.

Niño base: nace el 1-sep-2025 y tiene anemia MODERADA el 1-jul-2026; su C1M se programó el 1-ago-2026 (límite 31-ago),
de modo que con hoy = 28-sep-2026 lleva 28 días vencido. Su C3M (1-oct) y su DHc2 (1-sep) siguen pendientes.
"""

from datetime import date

import pytest

from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria
from app.application.servicio_visitas import ServicioVisitas
from app.domain.model.asistencia import AsistenciaControl, EstadoAsistencia
from app.domain.model.errores import ConflictoVisita, ErrorValidacion, NoEncontrado
from app.domain.model.visita import ConsumoSuplemento, ResultadoVisita, VisitaDomiciliaria
from app.domain.service.agenda import generar_agenda
from app.domain.service.visitas import (
    PESOS_V1,
    crear_visita,
    en_tratamiento,
    ordenar_priorizados,
    priorizar_nino,
    validar_datos_visita,
    validar_limite,
)
from tests.conftest import HOY, RelojFijo, nino_de

NACIMIENTO = date(2025, 9, 1)
DIAGNOSTICO = (date(2026, 7, 1), "MODERADA")


def visita_valida(**cambios):
    return {
        "fecha": date(2026, 9, 20),
        "resultado": "REALIZADA",
        "consume_suplemento": "SI",
        "observaciones": None,
    } | cambios


def priorizar(nino, ultima_visita=None):
    return priorizar_nino(nino, generar_agenda(nino, HOY), ultima_visita, HOY)


def componente(p, codigo):
    return next(c for c in p.componentes if c.codigo == codigo)


# --- Validación de la visita -----------------------------------------------------------------------------------------


def test_cp188_una_visita_valida_no_tiene_errores_y_el_consumo_por_defecto_es_desconocido():
    assert validar_datos_visita(visita_valida(), NACIMIENTO, HOY) == []
    sin_consumo = {"fecha": HOY, "resultado": "NO_ENCONTRADO"}
    assert validar_datos_visita(sin_consumo, NACIMIENTO, HOY) == []
    assert crear_visita("n1", sin_consumo, "enf").consume_suplemento == ConsumoSuplemento.DESCONOCIDO


@pytest.mark.parametrize(
    "cambios, campo",
    [
        ({"fecha": None}, "fecha"),
        ({"fecha": "2026-09-20"}, "fecha"),
        ({"fecha": date(2026, 9, 29)}, "fecha"),
        ({"fecha": date(2025, 8, 31)}, "fecha"),
        ({"resultado": "OTRO"}, "resultado"),
        ({"resultado": None}, "resultado"),
        ({"consume_suplemento": "TAL VEZ"}, "consume_suplemento"),
        ({"observaciones": "x" * 501}, "observaciones"),
        ({"observaciones": 7}, "observaciones"),
    ],
)
def test_cp189_datos_de_visita_invalidos_se_rechazan_por_campo(cambios, campo):
    assert [e.campo for e in validar_datos_visita(visita_valida(**cambios), NACIMIENTO, HOY)] == [campo]


def test_cp190_el_limite_de_500_caracteres_es_inclusivo_y_se_cuenta_sin_espacios_en_los_bordes():
    assert validar_datos_visita(visita_valida(observaciones="x" * 500), NACIMIENTO, HOY) == []
    assert validar_datos_visita(visita_valida(observaciones="  " + "x" * 500 + "  "), NACIMIENTO, HOY) == []


@pytest.mark.parametrize("resultado", ["NO_ENCONTRADO", "RECHAZADA"])
def test_cp191_solo_una_visita_realizada_puede_decir_si_o_no_consume_el_suplemento(resultado):
    errores = validar_datos_visita(visita_valida(resultado=resultado, consume_suplemento="NO"), NACIMIENTO, HOY)
    assert [e.campo for e in errores] == ["consume_suplemento"]
    assert (
        validar_datos_visita(visita_valida(resultado=resultado, consume_suplemento="DESCONOCIDO"), NACIMIENTO, HOY)
        == []
    )


def test_cp192_crear_visita_normaliza_las_observaciones():
    v = crear_visita("n1", visita_valida(observaciones="  Tomó el sulfato  "), "enf.rosa")
    assert (v.observaciones, v.registrado_por, v.resultado, v.consume_suplemento) == (
        "Tomó el sulfato",
        "enf.rosa",
        ResultadoVisita.REALIZADA,
        ConsumoSuplemento.SI,
    )
    assert crear_visita("n1", visita_valida(observaciones="   "), "enf").observaciones is None


@pytest.mark.parametrize("limite, errores", [(0, 1), (1, 0), (200, 0), (201, 1), (-5, 1)])
def test_cp193_el_limite_de_la_lista_va_de_1_a_200(limite, errores):
    assert len(validar_limite(limite)) == errores


# --- Puntaje -----------------------------------------------------------------------------------------------------------


def test_cp194_solo_los_ninos_activos_con_anemia_en_la_ultima_evaluacion_estan_en_tratamiento():
    assert en_tratamiento(nino_de(NACIMIENTO, [DIAGNOSTICO]))
    assert not en_tratamiento(nino_de(NACIMIENTO, [DIAGNOSTICO, (date(2026, 8, 1), "SIN_ANEMIA")]))
    assert not en_tratamiento(nino_de(NACIMIENTO, [DIAGNOSTICO], estado="ALTA"))
    assert not en_tratamiento(nino_de(NACIMIENTO, []))


def test_cp195_el_puntaje_suma_cuatro_componentes_explicables_y_sin_visita_recibe_el_maximo():
    p = priorizar(nino_de(NACIMIENTO, [DIAGNOSTICO]))
    assert [c.codigo for c in p.componentes] == ["SEVERIDAD", "CONTROL_VENCIDO", "INASISTENCIAS", "ULTIMA_VISITA"]
    assert (componente(p, "SEVERIDAD").puntos, componente(p, "SEVERIDAD").valor) == (25.0, "MODERADA")
    assert (componente(p, "CONTROL_VENCIDO").puntos, componente(p, "CONTROL_VENCIDO").valor) == (14.0, "28 días")
    assert componente(p, "INASISTENCIAS").puntos == 0
    assert (componente(p, "ULTIMA_VISITA").puntos, componente(p, "ULTIMA_VISITA").valor) == (15.0, "sin visitas")
    assert p.puntaje == 54.0 == round(sum(c.puntos for c in p.componentes), 1)
    assert (p.dias_control_vencido, p.inasistencias_recientes, p.ultima_visita) == (28, 0, None)
    assert sum(c.maximo for c in p.componentes) == 100.0


@pytest.mark.parametrize("clasificacion, puntos", [("SEVERA", 40.0), ("MODERADA", 25.0), ("LEVE", 10.0)])
def test_cp196_la_severidad_pesa_sev_mayor_que_mod_mayor_que_lev(clasificacion, puntos):
    p = priorizar(nino_de(NACIMIENTO, [(DIAGNOSTICO[0], clasificacion)]))
    assert componente(p, "SEVERIDAD").puntos == puntos


def test_cp197_los_dias_de_control_vencido_son_proporcionales_y_tienen_tope():
    sin_vencidos = nino_de(NACIMIENTO, [(date(2026, 9, 10), "LEVE")])  # su C1M es el 10-oct: nada vencido
    assert componente(priorizar(sin_vencidos), "CONTROL_VENCIDO").puntos == 0
    muy_vencido = nino_de(NACIMIENTO, [(date(2026, 3, 1), "LEVE")])  # C1M vencido hace ~148 días
    c = componente(priorizar(muy_vencido), "CONTROL_VENCIDO")
    assert c.puntos == PESOS_V1.maximo_control_vencido == 30.0
    assert priorizar(muy_vencido).dias_control_vencido > PESOS_V1.dias_tope_control_vencido


def test_cp198_las_inasistencias_de_los_ultimos_90_dias_suman_5_puntos_hasta_15():
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    registro = lambda codigo, programada, estado: nino.asistencias.append(  # noqa: E731
        AsistenciaControl(nino.id, codigo, programada, estado, "enf", motivo="Viaje")
    )
    registro("DHx", date(2026, 3, 1), EstadoAsistencia.NO_ASISTIO)  # hace más de 90 días: no cuenta
    registro("DHc1", date(2026, 6, 30), EstadoAsistencia.NO_ASISTIO)  # exactamente 90 días: cuenta
    registro("C1M", date(2026, 8, 1), EstadoAsistencia.NO_ASISTIO)
    registro("DHc2", date(2026, 9, 1), EstadoAsistencia.ASISTIO)  # una asistencia no cuenta
    p = priorizar(nino)
    assert (p.inasistencias_recientes, componente(p, "INASISTENCIAS").puntos) == (2, 10.0)
    registro("C3M", date(2026, 9, 10), EstadoAsistencia.NO_ASISTIO)
    registro("C6M", date(2026, 9, 11), EstadoAsistencia.NO_ASISTIO)
    assert componente(priorizar(nino), "INASISTENCIAS").puntos == 15.0  # tope: 4 inasistencias valen 15, no 20


def test_cp199_los_dias_desde_la_ultima_visita_son_proporcionales_con_tope_de_90_dias():
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    ayer = priorizar(nino, date(2026, 9, 27))
    assert (componente(ayer, "ULTIMA_VISITA").puntos, ayer.dias_desde_ultima_visita) == (0.2, 1)
    mitad = priorizar(nino, date(2026, 8, 14))
    assert (componente(mitad, "ULTIMA_VISITA").puntos, componente(mitad, "ULTIMA_VISITA").valor) == (7.5, "45 días")
    assert componente(priorizar(nino, date(2025, 1, 1)), "ULTIMA_VISITA").puntos == 15.0
    assert componente(priorizar(nino, HOY), "ULTIMA_VISITA").puntos == 0


def test_cp200_el_puntaje_es_determinista_y_el_orden_desempata_por_atraso_nombre_e_id():
    a = priorizar(nino_de(NACIMIENTO, [DIAGNOSTICO], nombres="Ana", apellidos="Zeta"))
    assert priorizar(nino_de(NACIMIENTO, [DIAGNOSTICO], nombres="Ana", apellidos="Zeta")).puntaje == a.puntaje
    mismo_puntaje = [
        a,
        priorizar(nino_de(NACIMIENTO, [DIAGNOSTICO], nombres="Ana", apellidos="Alva")),
    ]
    assert [i.nombre_completo for i in ordenar_priorizados(mismo_puntaje)] == ["Ana Alva", "Ana Zeta"]
    severa = priorizar(nino_de(NACIMIENTO, [(DIAGNOSTICO[0], "SEVERA")]))
    assert ordenar_priorizados([a, severa])[0] is severa


# --- Caso de uso -------------------------------------------------------------------------------------------------------


@pytest.fixture
def repo():
    return RepositorioEnMemoria()


@pytest.fixture
def servicio(repo):
    return ServicioVisitas(repo, repo, RelojFijo())


def test_cp201_registrar_y_listar_visitas_con_la_ultima_primero(repo, servicio):
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    repo.guardar(nino)
    primera = servicio.registrar_visita(nino.id, visita_valida(fecha=date(2026, 9, 1)), "enf.rosa")
    segunda = servicio.registrar_visita(
        nino.id, visita_valida(fecha=date(2026, 9, 20), consume_suplemento="NO"), "tec.juan"
    )
    assert (segunda.registrado_por, segunda.consume_suplemento) == ("tec.juan", ConsumoSuplemento.NO)
    assert [v.id for v in servicio.listar_visitas(nino.id)] == [segunda.id, primera.id]


def test_cp202_no_se_registran_dos_visitas_el_mismo_dia_ni_a_un_nino_inexistente_ni_datos_invalidos(repo, servicio):
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    repo.guardar(nino)
    servicio.registrar_visita(nino.id, visita_valida(), "enf")
    with pytest.raises(ConflictoVisita, match="2026-09-20"):
        servicio.registrar_visita(
            nino.id, visita_valida(resultado="RECHAZADA", consume_suplemento="DESCONOCIDO"), "enf"
        )
    with pytest.raises(ErrorValidacion):
        servicio.registrar_visita(nino.id, visita_valida(fecha=date(2026, 12, 1)), "enf")
    with pytest.raises(NoEncontrado):
        servicio.registrar_visita("no-existe", visita_valida(), "enf")
    with pytest.raises(NoEncontrado):
        servicio.listar_visitas("no-existe")


def test_cp203_la_lista_priorizada_solo_trae_ninos_en_tratamiento_ordenados_y_limitados(repo, servicio):
    severo = nino_de(NACIMIENTO, [(DIAGNOSTICO[0], "SEVERA")], dni="70000001", nombres="Sev", apellidos="A")
    moderado = nino_de(NACIMIENTO, [DIAGNOSTICO], dni="70000002", nombres="Mod", apellidos="B")
    recuperado = nino_de(NACIMIENTO, [DIAGNOSTICO, (date(2026, 8, 5), "SIN_ANEMIA")], dni="70000003")
    con_alta = nino_de(NACIMIENTO, [DIAGNOSTICO], estado="ALTA", dni="70000004")
    for n in (moderado, recuperado, severo, con_alta):
        repo.guardar(n)
    items = servicio.visitas_priorizadas(None, 20)
    assert [i.nino_id for i in items] == [severo.id, moderado.id]
    assert [i.nino_id for i in servicio.visitas_priorizadas(None, 1)] == [severo.id]
    assert servicio.visitas_priorizadas("  p. s. chongos ALTO ", 20) == items  # sin distinguir mayúsculas ni espacios
    assert servicio.visitas_priorizadas("Otro establecimiento", 20) == []


def test_cp204_una_visita_reciente_baja_al_nino_en_la_lista(repo, servicio):
    a = nino_de(NACIMIENTO, [DIAGNOSTICO], dni="70000001", nombres="Ana", apellidos="Alva")
    b = nino_de(NACIMIENTO, [DIAGNOSTICO], dni="70000002", nombres="Beto", apellidos="Bravo")
    repo.guardar(a), repo.guardar(b)
    assert servicio.visitas_priorizadas(None, 20)[0].nino_id == a.id  # empate: por nombre
    servicio.registrar_visita(a.id, visita_valida(fecha=HOY), "enf")
    orden = servicio.visitas_priorizadas(None, 20)
    assert [i.nino_id for i in orden] == [b.id, a.id]
    assert orden[1].ultima_visita == HOY and orden[1].dias_desde_ultima_visita == 0


def test_cp205_limite_invalido_en_la_lista_priorizada(servicio):
    with pytest.raises(ErrorValidacion) as e:
        servicio.visitas_priorizadas(None, 0)
    assert e.value.errores[0].campo == "limite"


def test_cp205_el_repositorio_en_memoria_rechaza_la_visita_duplicada_y_actualiza(repo):
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    repo.guardar(nino)
    v = repo.agregar_visita(VisitaDomiciliaria(nino.id, HOY, ResultadoVisita.REALIZADA, "enf"))
    with pytest.raises(ConflictoVisita):
        repo.agregar_visita(VisitaDomiciliaria(nino.id, HOY, ResultadoVisita.RECHAZADA, "enf"))
    v.resultado = ResultadoVisita.RECHAZADA
    repo.actualizar_visita(v)
    assert repo.obtener_visita_del_dia(nino.id, HOY).resultado == ResultadoVisita.RECHAZADA
    assert repo.obtener_visita_del_dia(nino.id, date(2020, 1, 1)) is None
    assert repo.ultimas_visitas({nino.id, "otro"}) == {nino.id: HOY}
