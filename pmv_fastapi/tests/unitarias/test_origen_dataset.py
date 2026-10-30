"""CP-116 a CP-122: origen de los datos (SISTEMA o DATASET_DIRESA_JUNIN), campos opcionales solo para el dataset
y antropometría opcional solo en la importación (ADR-009). Dominio y casos de uso con el repositorio en memoria."""

from datetime import date

import pytest

from app.domain.model.entidades import Evaluacion, Nino
from app.domain.model.errores import ErrorValidacion
from app.domain.model.origen import OrigenDatos
from app.domain.service.validaciones import validar_datos_evaluacion, validar_datos_nino
from tests.conftest import HOY, datos_eval, datos_nino, nino_de

DATASET = OrigenDatos.DATASET_DIRESA_JUNIN


def nino_dataset(**cambios):
    base = dict(
        dni=None,
        nombres=None,
        apellidos=None,
        sexo=None,
        fecha_nacimiento=date(2025, 6, 1),
        establecimiento="PILCOMAYO",
        distrito="PILCOMAYO",
        comunidad="PILCOMAYO",
        altitud_m=3245,
        tutor_nombre=None,
        registrado_por="importador.dataset-diresa",
        origen=DATASET,
        codigo_origen="DJ-00001",
    )
    base.update(cambios)
    return Nino(**base)


def test_cp116_nombre_legible_de_un_registro_del_dataset():
    n = nino_dataset()
    assert n.es_dataset and n.nombre_completo == "Registro DJ-00001 (dataset anonimizado)"
    assert nino_dataset(codigo_origen=None).nombre_completo == "Registro sin nombre"
    sistema = nino_de(date(2025, 3, 10))
    assert not sistema.es_dataset and sistema.origen == OrigenDatos.SISTEMA
    assert sistema.nombre_completo == "Luz Mery Quispe Rojas"


def test_cp117_el_registro_desde_el_sistema_sigue_exigiendo_todos_los_campos():
    vacio = datos_nino(dni="", nombres=None, apellidos="", sexo="X", tutor_nombre=None)
    campos = {e.campo for e in validar_datos_nino(vacio, HOY)}
    assert {"dni", "nombres", "apellidos", "sexo", "tutor_nombre"} <= campos
    # El resultado es idéntico al de pedir el origen SISTEMA de forma explícita.
    assert validar_datos_nino(vacio, HOY) == validar_datos_nino(vacio, HOY, OrigenDatos.SISTEMA)
    assert validar_datos_nino(datos_nino(), HOY) == []


def test_cp118_el_dataset_admite_campos_vacios_pero_valida_el_formato_de_los_que_vienen():
    vacio = datos_nino(dni=None, nombres=None, apellidos=None, sexo=None, tutor_nombre=None, tutor_celular=None)
    assert validar_datos_nino(vacio, HOY, DATASET) == []
    assert validar_datos_nino({**vacio, "dni": "", "nombres": "  ", "sexo": ""}, HOY, DATASET) == []
    malos = validar_datos_nino({**vacio, "dni": "123", "sexo": "X", "tutor_celular": "123"}, HOY, DATASET)
    assert {e.campo for e in malos} == {"dni", "sexo", "tutor_celular"}
    # Los textos de ubicación siguen siendo obligatorios también en el dataset.
    assert {e.campo for e in validar_datos_nino({**vacio, "comunidad": None}, HOY, DATASET)} == {"comunidad"}


def test_cp119_la_antropometria_es_obligatoria_salvo_en_la_importacion():
    sin_antropometria = datos_eval(peso_kg=None, talla_cm=None)
    assert {e.campo for e in validar_datos_evaluacion(sin_antropometria, None, HOY)} == {"peso_kg", "talla_cm"}
    assert validar_datos_evaluacion(sin_antropometria, None, HOY, antropometria_obligatoria=False) == []
    fuera = datos_eval(peso_kg=99, talla_cm=10)  # si vienen, sus rangos se validan siempre
    assert {e.campo for e in validar_datos_evaluacion(fuera, None, HOY, antropometria_obligatoria=False)} == {
        "peso_kg",
        "talla_cm",
    }


def test_cp120_el_registro_desde_el_sistema_es_siempre_origen_sistema(servicio):
    nino = servicio.registrar_nino(
        {**datos_nino(), "origen": "DATASET_DIRESA_JUNIN", "codigo_origen": "DJ-99999"}, datos_eval(), "enf.rosa"
    )
    assert nino.origen == OrigenDatos.SISTEMA and nino.codigo_origen is None
    with pytest.raises(ErrorValidacion) as e:
        servicio.registrar_nino(datos_nino(dni=None), datos_eval(), "enf.rosa")
    assert [x.campo for x in e.value.errores] == ["dni"]
    with pytest.raises(ErrorValidacion) as e:  # registrar un control desde el sistema exige peso y talla
        servicio.registrar_evaluacion(nino.id, datos_eval(peso_kg=None, talla_cm=None), "enf.rosa")
    assert {x.campo for x in e.value.errores} == {"peso_kg", "talla_cm"}


def test_cp121_actualizar_un_registro_del_dataset_no_exige_datos_personales(servicio):
    n = nino_dataset()
    servicio.repo.guardar(n)
    actualizado = servicio.actualizar_datos(n.id, {"comunidad": "OTRA", "tutor_nombre": "", "estado": "ALTA"}, "a")
    assert (actualizado.comunidad, actualizado.tutor_nombre, actualizado.estado) == ("OTRA", None, "ALTA")
    assert actualizado.dni is None and actualizado.origen == DATASET
    with pytest.raises(ErrorValidacion):  # el formato de lo que se informa sí se valida
        servicio.actualizar_datos(n.id, {"tutor_celular": "123"}, "a")


def test_cp122_listar_y_buscar_por_codigo_en_memoria(servicio):
    servicio.repo.guardar(nino_dataset())
    servicio.registrar_nino(datos_nino(), datos_eval(), "a")
    por_codigo = servicio.listar_seguimiento(estado="ACTIVO", texto="dj-00001")
    assert [f["nino"].codigo_origen for f in por_codigo] == ["DJ-00001"]
    assert servicio.listar_seguimiento(texto="dataset") == []  # el rótulo legible no es un criterio de búsqueda
    assert len(servicio.listar_seguimiento(estado="ACTIVO")) == 2
    fila = por_codigo[0]
    assert fila["ultima_evaluacion"] is None and fila["dias_desde_ultimo_control"] is None


def test_evaluacion_importada_conserva_la_severidad_del_origen_sin_peso_ni_talla():
    e = Evaluacion(
        fecha=date(2026, 9, 1),
        hemoglobina_observada=10.0,
        peso_kg=None,
        talla_cm=None,
        altitud_m=3245,
        edad_meses=12,
        registrado_por="importador.dataset-diresa",
        clasificacion_origen="LEV",
    )
    assert e.clasificacion_origen == "LEV" and e.peso_kg is None
