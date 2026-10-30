"""CP-310 a CP-326: barreras de acceso y alerta de barreras críticas (HIST-4.3 y HIST-4.4, ADR-014).

Niño base: nace el 1-sep-2025 y tiene anemia MODERADA el 1-jul-2026; su C1M lleva 28 días vencido con hoy = 28-sep-2026.
"""

from datetime import date, timedelta

import pytest

from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria
from app.application.servicio_barreras import ServicioBarreras
from app.application.servicio_visitas import ServicioVisitas
from app.domain.model.alertas import Prioridad
from app.domain.model.barrera import Barrera, CodigoRazonBarrera, FuenteBarrera, TipoBarrera
from app.domain.model.errores import ConflictoBarrera, ErrorValidacion, NoEncontrado
from app.domain.service.agenda import generar_agenda
from app.domain.service.barreras import (
    REGLAS_BARRERAS_V1,
    ReglasBarrerasCriticas,
    crear_barrera,
    evaluar_barreras_nino,
    fecha_limite_consulta,
    ordenar_alertas_barrera,
    validar_datos_barrera,
)
from app.domain.service.visitas import PESOS_V1, PESOS_V2, priorizar_nino
from tests.conftest import HOY, RelojFijo, nino_de

NACIMIENTO = date(2025, 9, 1)
DIAGNOSTICO = (date(2026, 7, 1), "MODERADA")


def dias_antes(n: int) -> date:
    return HOY - timedelta(days=n)


def barrera(nino, tipo=TipoBarrera.TRANSPORTE, fecha=None, fuente=FuenteBarrera.PERSONAL, **cambios):
    return Barrera(nino.id, tipo, fuente, fecha or dias_antes(5), "enf", **cambios)


def evaluar(nino, barreras, reglas=REGLAS_BARRERAS_V1):
    return evaluar_barreras_nino(nino, generar_agenda(nino, HOY), barreras, HOY, reglas)


def codigos(alerta):
    return [r.codigo for r in alerta.razones]


# --- Validación y creación -------------------------------------------------------------------------------------------


def datos(**cambios):
    return {"tipo": "TRANSPORTE", "detalle": None, "fuente": "PERSONAL", "fecha": dias_antes(3)} | cambios


def test_cp310_una_barrera_valida_no_tiene_errores_y_usa_valores_por_defecto():
    assert validar_datos_barrera(datos(), NACIMIENTO, HOY) == []
    minima = {"tipo": "OLVIDO"}
    assert validar_datos_barrera(minima, NACIMIENTO, HOY) == []
    creada = crear_barrera("n1", minima, "enf", HOY)
    assert (creada.fuente, creada.fecha, creada.detalle, creada.recordatorio_id) == (
        FuenteBarrera.PERSONAL,
        HOY,
        None,
        None,
    )
    assert (creada.nino_id, creada.registrado_por, creada.creado_en.tzinfo is not None) == ("n1", "enf", True)


def test_cp311_con_otra_el_detalle_es_obligatorio_y_se_recorta():
    assert [e.campo for e in validar_datos_barrera(datos(tipo="OTRA", detalle="  "), NACIMIENTO, HOY)] == ["detalle"]
    assert [e.campo for e in validar_datos_barrera(datos(tipo="OTRA", detalle=None), NACIMIENTO, HOY)] == ["detalle"]
    assert validar_datos_barrera(datos(tipo="OTRA", detalle="  Lluvia fuerte "), NACIMIENTO, HOY) == []
    creada = crear_barrera("n1", datos(tipo="OTRA", detalle="  Lluvia fuerte ", recordatorio_id="r1"), "enf", HOY)
    assert (creada.detalle, creada.recordatorio_id, creada.tipo) == ("Lluvia fuerte", "r1", TipoBarrera.OTRA)


@pytest.mark.parametrize(
    "cambios, campo",
    [
        ({"tipo": None}, "tipo"),
        ({"tipo": "TELETRANSPORTE"}, "tipo"),
        ({"fuente": "OTRA_FUENTE"}, "fuente"),
        ({"detalle": 12}, "detalle"),
        ({"detalle": "x" * 201}, "detalle"),
        ({"fecha": "2026-09-20"}, "fecha"),
        ({"fecha": HOY + timedelta(days=1)}, "fecha"),
        ({"fecha": date(2025, 8, 31)}, "fecha"),
    ],
)
def test_cp312_datos_invalidos_de_barrera(cambios, campo):
    assert [e.campo for e in validar_datos_barrera(datos(**cambios), NACIMIENTO, HOY)] == [campo]


def test_cp312_el_detalle_largo_de_otra_se_informa_una_sola_vez():
    errores = validar_datos_barrera(datos(tipo="OTRA", detalle="x" * 201), NACIMIENTO, HOY)
    assert [e.campo for e in errores] == ["detalle"] and "200" in errores[0].mensaje


# --- Reglas de barreras críticas -------------------------------------------------------------------------------------


def test_cp313_rechazo_del_tratamiento_o_efectos_adversos_son_barrera_grave_de_prioridad_alta():
    for tipo in (TipoBarrera.RECHAZO_TRATAMIENTO, TipoBarrera.EFECTOS_ADVERSOS_SUPLEMENTO):
        nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
        alerta = evaluar(nino, [barrera(nino, tipo)])
        assert CodigoRazonBarrera.BARRERA_GRAVE in codigos(alerta) and alerta.prioridad == Prioridad.ALTA


def test_cp314_dos_barreras_distintas_en_60_dias_son_barreras_recurrentes():
    nino = nino_de(NACIMIENTO, [(date(2026, 9, 20), "LEVE")])  # sin control vencido: solo recurrencia
    barreras = [barrera(nino, TipoBarrera.TRANSPORTE, dias_antes(2)), barrera(nino, TipoBarrera.OLVIDO, dias_antes(60))]
    alerta = evaluar(nino, barreras)
    assert codigos(alerta) == [CodigoRazonBarrera.BARRERAS_RECURRENTES] and alerta.prioridad == Prioridad.MEDIA
    assert "60 días" in alerta.razones[0].descripcion
    # a los 61 días la segunda ya no cuenta para la recurrencia
    assert evaluar(nino, [barreras[0], barrera(nino, TipoBarrera.OLVIDO, dias_antes(61))]) is None


def test_cp315_la_misma_barrera_con_otra_fuente_el_mismo_dia_cuenta_una_sola_vez():
    nino = nino_de(NACIMIENTO, [(date(2026, 9, 20), "LEVE")])
    mismas = [
        barrera(nino, fecha=dias_antes(3), fuente=FuenteBarrera.PERSONAL),
        barrera(nino, fecha=dias_antes(3), fuente=FuenteBarrera.VISITA),
    ]
    assert evaluar(nino, mismas) is None
    otro_dia = [mismas[0], barrera(nino, fecha=dias_antes(10))]
    assert codigos(evaluar(nino, otro_dia)) == [CodigoRazonBarrera.BARRERAS_RECURRENTES]


def test_cp316_una_barrera_con_anemia_moderada_y_control_vencido_alerta_con_prioridad_media():
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    alerta = evaluar(nino, [barrera(nino)])
    assert codigos(alerta) == [CodigoRazonBarrera.ANEMIA_CONTROL_VENCIDO] and alerta.prioridad == Prioridad.MEDIA
    assert "moderada" in alerta.razones[0].descripcion
    assert alerta.dias_control_vencido == 28 and alerta.ultima_clasificacion.value == "MODERADA"
    severo = nino_de(NACIMIENTO, [(DIAGNOSTICO[0], "SEVERA")])
    assert "severa" in evaluar(severo, [barrera(severo)]).razones[0].descripcion


def test_cp317_no_alerta_sin_anemia_moderada_o_severa_ni_control_vencido_ni_barrera_vigente():
    leve = nino_de(NACIMIENTO, [(DIAGNOSTICO[0], "LEVE")])
    assert evaluar(leve, [barrera(leve)]) is None  # anemia leve con control vencido no es crítica
    sin_vencido = nino_de(NACIMIENTO, [(date(2026, 9, 20), "MODERADA")])
    assert evaluar(sin_vencido, [barrera(sin_vencido)]) is None
    sin_evaluacion = nino_de(NACIMIENTO, [])
    assert evaluar(sin_evaluacion, [barrera(sin_evaluacion)]) is None
    moderado = nino_de(NACIMIENTO, [DIAGNOSTICO])
    assert evaluar(moderado, []) is None


def test_cp318_la_vigencia_es_de_90_dias():
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    assert evaluar(nino, [barrera(nino, fecha=dias_antes(90))]) is not None
    assert evaluar(nino, [barrera(nino, fecha=dias_antes(91))]) is None
    graves = barrera(nino, TipoBarrera.RECHAZO_TRATAMIENTO, dias_antes(91))
    assert evaluar(nino, [graves]) is None


def test_cp319_dos_o_mas_razones_elevan_la_prioridad_a_alta_y_el_sustento_va_de_reciente_a_antigua():
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    antigua = barrera(nino, TipoBarrera.OLVIDO, dias_antes(40))
    reciente = barrera(nino, TipoBarrera.TRABAJO_CUIDADOR, dias_antes(1))
    fuera = barrera(nino, TipoBarrera.ECONOMICA, dias_antes(120))
    alerta = evaluar(nino, [antigua, reciente, fuera])
    assert codigos(alerta) == [CodigoRazonBarrera.BARRERAS_RECURRENTES, CodigoRazonBarrera.ANEMIA_CONTROL_VENCIDO]
    assert alerta.prioridad == Prioridad.ALTA
    assert [b.id for b in alerta.barreras] == [reciente.id, antigua.id]  # la barrera de 120 días no se muestra
    assert (alerta.dni, alerta.nombre_completo, alerta.tutor_celular) == (nino.dni, nino.nombre_completo, "987654321")


def test_cp320_un_nino_con_alta_no_tiene_alerta_de_barreras():
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO], estado="ALTA")
    assert evaluar(nino, [barrera(nino, TipoBarrera.RECHAZO_TRATAMIENTO)]) is None


def test_cp321_las_reglas_son_parametrizables_y_la_ventana_de_consulta_es_la_mayor():
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    estricta = ReglasBarrerasCriticas(
        version="X", tipos_graves=frozenset({TipoBarrera.TRANSPORTE}), dias_vigencia=3, dias_ventana_recurrentes=120
    )
    assert estricta.dias_consulta == 120 and REGLAS_BARRERAS_V1.dias_consulta == 90
    assert evaluar(nino, [barrera(nino, fecha=dias_antes(5))], estricta) is None
    assert codigos(evaluar(nino, [barrera(nino, fecha=dias_antes(2))], estricta)) == [CodigoRazonBarrera.BARRERA_GRAVE]
    assert fecha_limite_consulta(HOY) == dias_antes(90) and fecha_limite_consulta(HOY, estricta) == dias_antes(120)


def test_cp322_orden_de_las_alertas_prioridad_razones_atraso_y_barrera_reciente():
    def alerta_de(nombre, dni, tipo=TipoBarrera.TRANSPORTE, dias=5):
        nino = nino_de(NACIMIENTO, [DIAGNOSTICO], nombres=nombre, dni=dni)
        return evaluar(nino, [barrera(nino, tipo, dias_antes(dias))])

    grave = alerta_de("Zoe", "70000001", TipoBarrera.RECHAZO_TRATAMIENTO)
    antigua = alerta_de("Ana", "70000002", dias=30)
    reciente = alerta_de("Beto", "70000003", dias=2)
    empate = alerta_de("Carla", "70000004", dias=2)
    orden = ordenar_alertas_barrera([empate, antigua, grave, reciente])
    assert [a.nombre_completo.split()[0] for a in orden] == ["Zoe", "Beto", "Carla", "Ana"]


# --- Puntaje de visita con barreras ----------------------------------------------------------------------------------


def priorizar(nino, alerta=None, pesos=PESOS_V2):
    return priorizar_nino(nino, generar_agenda(nino, HOY), None, HOY, pesos, alerta)


def test_cp323_la_barrera_critica_suma_un_quinto_componente_solo_cuando_existe():
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    base = priorizar(nino)
    assert [c.codigo for c in base.componentes] == ["SEVERIDAD", "CONTROL_VENCIDO", "INASISTENCIAS", "ULTIMA_VISITA"]
    media = evaluar(nino, [barrera(nino)])
    alta = evaluar(nino, [barrera(nino, TipoBarrera.RECHAZO_TRATAMIENTO)])
    con_media, con_alta = priorizar(nino, media), priorizar(nino, alta)
    assert con_media.componentes[-1].codigo == "BARRERA_CRITICA" and con_media.componentes[-1].puntos == 8.0
    assert con_alta.componentes[-1].puntos == 15.0 and con_alta.componentes[-1].maximo == 15.0
    assert con_alta.puntaje == pytest.approx(base.puntaje + 15.0) and con_media.puntaje == pytest.approx(
        base.puntaje + 8.0
    )
    assert "anemia moderada" in con_media.componentes[-1].valor.lower()
    assert PESOS_V2.version == "VISITA-V2" and PESOS_V1.puntos_barrera_critica == {}
    assert priorizar(nino, None, PESOS_V1).puntaje == base.puntaje  # sin barreras V1 y V2 coinciden


def test_cp324_el_maximo_con_barreras_criticas_es_115():
    nino = nino_de(NACIMIENTO, [(DIAGNOSTICO[0], "SEVERA")])
    alta = evaluar(nino, [barrera(nino, TipoBarrera.RECHAZO_TRATAMIENTO)])
    p = priorizar(nino, alta)
    assert sum(c.maximo for c in p.componentes) == 115.0 and p.puntaje <= 115.0


# --- Servicios -------------------------------------------------------------------------------------------------------


@pytest.fixture
def repo():
    return RepositorioEnMemoria()


@pytest.fixture
def servicio(repo):
    return ServicioBarreras(repo, repo, RelojFijo())


def test_cp325_registrar_listar_y_rechazar_la_barrera_repetida(repo, servicio):
    nino = nino_de(NACIMIENTO, [DIAGNOSTICO])
    repo.guardar(nino)
    primera = servicio.registrar_barrera(nino.id, datos(fecha=dias_antes(10)), "enf.rosa")
    segunda = servicio.registrar_barrera(nino.id, datos(tipo="OTRA", detalle="Río crecido", fecha=dias_antes(2)), "tec")
    assert (primera.registrado_por, segunda.detalle) == ("enf.rosa", "Río crecido")
    assert [b.id for b in servicio.listar_barreras(nino.id)] == [segunda.id, primera.id]
    with pytest.raises(ConflictoBarrera) as e:
        servicio.registrar_barrera(nino.id, datos(fecha=dias_antes(10)), "otra")
    assert e.value.id_existente == primera.id and "ya tiene registrada" in str(e.value)
    servicio.registrar_barrera(nino.id, datos(fecha=dias_antes(10), fuente="VISITA"), "otra")  # otra fuente: se admite
    with pytest.raises(ErrorValidacion):
        servicio.registrar_barrera(nino.id, datos(tipo="NADA"), "enf")
    with pytest.raises(NoEncontrado):
        servicio.registrar_barrera("no-existe", datos(), "enf")
    with pytest.raises(NoEncontrado):
        servicio.listar_barreras("no-existe")


def test_cp326_alertas_de_barreras_filtran_por_comunidad_y_prioridad_y_omiten_ninos_sin_barreras(repo, servicio):
    grave = nino_de(NACIMIENTO, [DIAGNOSTICO], dni="70000001", nombres="Gloria", comunidad="Palmayoc")
    media = nino_de(NACIMIENTO, [DIAGNOSTICO], dni="70000002", nombres="Mario", comunidad="Quilcas")
    sin_barreras = nino_de(NACIMIENTO, [DIAGNOSTICO], dni="70000003")
    antigua = nino_de(NACIMIENTO, [DIAGNOSTICO], dni="70000004")
    alta = nino_de(NACIMIENTO, [DIAGNOSTICO], estado="ALTA", dni="70000005")
    for n in (grave, media, sin_barreras, antigua, alta):
        repo.guardar(n)
    servicio.registrar_barrera(grave.id, datos(tipo="RECHAZO_TRATAMIENTO"), "enf")
    servicio.registrar_barrera(media.id, datos(), "enf")
    servicio.registrar_barrera(alta.id, datos(tipo="RECHAZO_TRATAMIENTO"), "enf")
    repo.agregar_barrera(barrera(antigua, fecha=dias_antes(200)))
    todas = servicio.alertas_barreras()
    assert [a.nino_id for a in todas] == [grave.id, media.id]
    assert [a.nino_id for a in servicio.alertas_barreras(comunidad=" quilcas ")] == [media.id]
    assert [a.nino_id for a in servicio.alertas_barreras(prioridad="ALTA")] == [grave.id]
    assert servicio.alertas_barreras(comunidad="Otra") == []
    with pytest.raises(ErrorValidacion) as e:
        servicio.alertas_barreras(prioridad="BAJA")
    assert e.value.errores[0].campo == "prioridad"


def test_cp326_la_lista_de_visitas_priorizadas_suma_el_componente_de_barreras_si_el_servicio_lo_recibe(repo):
    con = nino_de(NACIMIENTO, [DIAGNOSTICO], dni="70000001", nombres="Ana", apellidos="Alva")
    sin = nino_de(NACIMIENTO, [DIAGNOSTICO], dni="70000002", nombres="Beto", apellidos="Bravo")
    repo.guardar(con), repo.guardar(sin)
    repo.agregar_barrera(barrera(con, TipoBarrera.EFECTOS_ADVERSOS_SUPLEMENTO))
    con_barreras = ServicioVisitas(repo, repo, RelojFijo(), repo).visitas_priorizadas(None, 20)
    assert [i.nino_id for i in con_barreras] == [con.id, sin.id]
    assert [c.codigo for c in con_barreras[0].componentes][-1] == "BARRERA_CRITICA" and len(
        con_barreras[1].componentes
    ) == 4
    sin_repo = ServicioVisitas(repo, repo, RelojFijo()).visitas_priorizadas(None, 20)
    assert all(len(i.componentes) == 4 for i in sin_repo) and sin_repo[0].puntaje == sin_repo[1].puntaje
