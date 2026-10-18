"""CP-146 a CP-151: caso de uso de importación del dataset anonimizado (ADR-009) con el repositorio en memoria."""

from datetime import date

import pytest

from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria
from app.application.servicio_importacion import ServicioImportacion
from app.domain.model.clasificacion import Clasificacion
from app.domain.model.importacion import EvaluacionImportada, RegistroImportado, TipoEvaluacionImportada
from app.domain.model.origen import OrigenDatos
from tests.conftest import RelojFijo

CORTE = date(2024, 6, 30)
DX, M1, M3, M6 = (
    TipoEvaluacionImportada.DIAGNOSTICO,
    TipoEvaluacionImportada.CONTROL_1_MES,
    TipoEvaluacionImportada.CONTROL_3_MESES,
    TipoEvaluacionImportada.CONTROL_6_MESES,
)


def registro(codigo="DJ-00001", nacimiento=date(2023, 6, 20), evaluaciones=(), **cambios):
    base = dict(
        codigo_origen=codigo,
        fecha_nacimiento=nacimiento,
        establecimiento="PILCOMAYO",
        distrito="PILCOMAYO",
        comunidad="PILCOMAYO",
        altitud_m=3245.0,
        red="VALLE DEL MANTARO",
        microred="EL TAMBO",
        provincia="HUANCAYO",
        evaluaciones=tuple(evaluaciones),
    )
    base.update(cambios)
    return RegistroImportado(**base)


@pytest.fixture
def importador():
    return ServicioImportacion(RepositorioEnMemoria(), RelojFijo(CORTE))


def test_cp146_importa_un_nino_sin_datos_personales_con_sus_evaluaciones(importador):
    dx = EvaluacionImportada(DX, date(2024, 5, 20), 11.0, "MOD")
    control = EvaluacionImportada(M1, date(2024, 6, 20), 12.5)
    res = importador.importar([registro(evaluaciones=[control, dx])])
    assert (res.registros_recibidos, res.ninos_importados, res.ninos_omitidos) == (1, 1, 0)
    assert res.evaluaciones_importadas == {"DIAGNOSTICO": 1, "CONTROL_1_MES": 1}
    (nino,) = importador.repo.listar()
    assert nino.origen == OrigenDatos.DATASET_DIRESA_JUNIN and nino.codigo_origen == "DJ-00001"
    assert (nino.dni, nino.nombres, nino.apellidos, nino.sexo, nino.tutor_nombre, nino.tutor_celular) == (None,) * 6
    assert (nino.provincia, nino.red, nino.microred, nino.comunidad, nino.altitud_m) == (
        "HUANCAYO",
        "VALLE DEL MANTARO",
        "EL TAMBO",
        "PILCOMAYO",
        3245.0,
    )
    assert nino.estado == "ACTIVO" and nino.nombre_completo == "Registro DJ-00001 (dataset anonimizado)"
    ev_dx, ev_m1 = sorted(nino.evaluaciones, key=lambda e: e.fecha)
    assert (ev_dx.peso_kg, ev_dx.talla_cm) == (None, None)  # el dataset no los trae: no se inventan
    assert ev_dx.clasificacion_origen == "MOD" and ev_m1.clasificacion_origen is None
    assert ev_dx.edad_meses == 11 and ev_dx.registrado_por == "importador.dataset-diresa"
    assert ev_dx.hemoglobina_ajustada == 8.9 and ev_dx.clasificacion == Clasificacion.MODERADA  # 11,0 - 2,1 a 3 245 m
    assert nino.creado_en.date() == date(2024, 5, 20)  # la marca de creación sigue la fecha de la primera evaluación


def test_cp147_descarta_y_cuenta_las_evaluaciones_fuera_de_las_reglas_del_dominio(importador):
    nac = date(2021, 5, 1)
    evaluaciones = [
        EvaluacionImportada(DX, date(2024, 5, 20), 11.0, "LEV"),  # 36 meses: válida
        EvaluacionImportada(M1, date(2026, 5, 1), 12.0),  # 60 meses: se descarta
        EvaluacionImportada(M3, date(2024, 6, 20), 0.7),  # hemoglobina imposible
        EvaluacionImportada(M6, date(2020, 1, 1), 12.0),  # anterior al nacimiento
    ]
    res = importador.importar([registro(nacimiento=nac, evaluaciones=evaluaciones)])
    assert res.evaluaciones_importadas == {"DIAGNOSTICO": 1}
    assert res.descartes == {
        "evaluacion_posterior_a_la_fecha_de_referencia": 1,  # la de 2026 supera el corte; la edad se evalúa después
        "evaluacion_con_hemoglobina_fuera_de_rango": 1,
        "evaluacion_anterior_al_nacimiento": 1,
    }


def test_cp147_una_evaluacion_con_60_meses_o_mas_antes_del_corte_se_descarta_por_edad():
    corte_tardio = ServicioImportacion(RepositorioEnMemoria(), RelojFijo(date(2027, 1, 1)))
    nac = date(2021, 5, 1)
    res = corte_tardio.importar(
        [
            registro(
                nacimiento=nac,
                evaluaciones=[
                    EvaluacionImportada(DX, date(2026, 4, 30), 11.0),  # 59 meses: válida (borde)
                    EvaluacionImportada(M1, date(2026, 5, 1), 11.0),  # 60 meses cumplidos: se descarta
                ],
            )
        ]
    )
    assert res.evaluaciones_importadas == {"DIAGNOSTICO": 1}
    assert res.descartes == {"evaluacion_con_edad_de_60_meses_o_mas": 1}
    assert (
        res.ninos_con_alta_por_edad == 1
    )  # a la fecha de referencia ya tiene 68 meses: fuera de la población objetivo
    assert corte_tardio.repo.listar(estado="ALTA")[0].codigo_origen == "DJ-00001"


def test_cp148_omite_al_nino_sin_evaluaciones_validas_y_al_de_datos_invalidos(importador):
    sin_evaluaciones = registro("DJ-00001", descartes_lectura=("diagnostico_sin_hemoglobina",))
    nacido_en_el_futuro = registro(
        "DJ-00002", nacimiento=date(2024, 7, 1), evaluaciones=[EvaluacionImportada(DX, date(2024, 7, 2), 11.0)]
    )
    texto_largo = registro(
        "DJ-00003", establecimiento="X" * 121, evaluaciones=[EvaluacionImportada(DX, date(2024, 5, 20), 11.0)]
    )
    valido = registro("DJ-00004", evaluaciones=[EvaluacionImportada(DX, date(2024, 5, 20), 11.0)])
    res = importador.importar([sin_evaluaciones, nacido_en_el_futuro, texto_largo, valido])
    assert (res.registros_recibidos, res.ninos_importados, res.ninos_omitidos) == (4, 1, 3)
    assert res.descartes == {
        "diagnostico_sin_hemoglobina": 1,
        "nino_sin_evaluaciones_validas": 1,
        "nino_con_datos_invalidos": 2,
    }
    assert [n.codigo_origen for n in importador.repo.listar()] == ["DJ-00004"]


def test_cp149_matriz_de_concordancia_entre_la_severidad_del_his_y_la_clasificacion_del_sistema(importador):
    def con(codigo, hb, severidad, nac=date(2023, 6, 20)):
        return registro(codigo, nac, [EvaluacionImportada(DX, date(2024, 5, 20), hb, severidad)])

    res = importador.importar(
        [
            con("DJ-00001", 11.0, "MOD"),  # Hb ajustada 8,9 a 12 meses: moderada = coincide
            con("DJ-00002", 12.6, "LEV"),  # ajustada 10,5: sin anemia pese a LEV
            con("DJ-00003", 13.0, None),  # sin severidad en el HIS
            con("DJ-00004", 12.0, "LEV", nac=date(2024, 3, 1)),  # menor de 6 meses: no aplica
        ]
    )
    assert res.matriz_concordancia == {
        "MOD": {"MODERADA": 1},
        "LEV": {"SIN_ANEMIA": 1, "NO_APLICA": 1},
        "SIN_DATO": {"SIN_ANEMIA": 1},
    }
    assert res.ninos_por_provincia == {"HUANCAYO": 4}


def test_cp150_la_importacion_es_reproducible_y_se_puede_reiniciar(importador):
    registros = [registro(evaluaciones=[EvaluacionImportada(DX, date(2024, 5, 20), 11.0, "MOD")])]
    importador.importar(registros)
    primero = importador.repo.listar()[0]
    assert importador.contar_importados() == 1
    assert importador.eliminar_importados() == 1 and importador.contar_importados() == 0
    importador.importar(registros)
    segundo = importador.repo.listar()[0]
    assert (segundo.id, segundo.evaluaciones[0].id) == (
        primero.id,
        primero.evaluaciones[0].id,
    )  # identificadores estables
    assert importador.eliminar_importados() == 1 and importador.repo.listar() == []


def test_cp151_importa_por_lotes_y_no_toca_a_los_ninos_del_sistema(servicio):
    servicio.registrar_nino(*_sistema(), "enf.rosa")
    importador = ServicioImportacion(servicio.repo, RelojFijo(CORTE), tamano_lote=2)
    registros = [
        registro(f"DJ-{i:05d}", evaluaciones=[EvaluacionImportada(DX, date(2024, 5, 20), 11.0)]) for i in range(1, 6)
    ]
    assert importador.importar(registros).ninos_importados == 5
    assert importador.contar_importados() == 5 and len(servicio.repo.listar()) == 6
    assert importador.eliminar_importados() == 5
    assert [n.origen for n in servicio.repo.listar()] == [OrigenDatos.SISTEMA]


def test_cp188_un_total_multiplo_del_lote_no_guarda_un_lote_vacio(importador):
    importador = ServicioImportacion(importador.repo, RelojFijo(CORTE), tamano_lote=2)
    registros = [
        registro(f"DJ-{i:05d}", evaluaciones=[EvaluacionImportada(DX, date(2024, 5, 20), 11.0)]) for i in range(1, 5)
    ]
    assert importador.importar(registros).ninos_importados == 4 and len(importador.repo.listar()) == 4


def _sistema():
    from tests.conftest import datos_eval, datos_nino

    return datos_nino(), datos_eval()
