"""CP-152 a CP-160: importador del dataset de la DIRESA Junín (scripts/importar_dataset_diresa.py).

Usa tests/fixtures/dataset_muestra.csv: 20 filas copiadas sin cambios del CSV público (latin-1, «;»). Su número de fila
(1 a 20) es el del código seudónimo; las filas de interés son:
  1 JUNIN (Hb 14,8, LEV) · 2 CHUPACA (SEV, Hb 12,1) · 3 HUANCAYO (valor_lab_dx NULL) · 4 y 7 sin ninguna hemoglobina ·
  9 controles al mes y a los 3 meses con fecha y sin Hb · 18 control a los 6 meses sin Hb ·
  19 Hb 0,7 al mes y 20 Hb 0 a los 6 meses (fuera de rango): las dos únicas del archivo completo.
"""

import json
from datetime import date
from pathlib import Path

import pytest

from app.adapters.outbound.persistence.sqlalchemy_repo import RepositorioSQLAlchemy
from app.domain.model.origen import OrigenDatos
from scripts import importar_dataset_diresa as cli
from scripts.importador_diresa import config as cfg
from scripts.importador_diresa.lector import codigo_de, fila_a_registro, leer_registros
from scripts.importador_diresa.muestreo import asignar_cupos, estrato, muestra_estratificada
from scripts.importador_diresa.reporte import concordancia

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "dataset_muestra.csv"


@pytest.fixture(scope="module")
def leido():
    return leer_registros(FIXTURE)


def fila_base(**cambios):
    base = {
        "fecha_nac": "20/06/2023", "fecha_dx": "21/06/2024", "valor_lab_dx": "LEV", "fecha_dosaje_dx": "21/06/2024",
        "hb_dx": "12.6", "fecha_dosaje_mes": "NULL", "hb": "NULL", "fecha_dosaje_3_meses": "NULL",
        "hb_tresmeses": "NULL", "fecha_dosaje_6_meses": "NULL", "hb_seismeses": "NULL",
        "Red": "VALLE DEL MANTARO", "MicroRed": "CHILCA", "Nombre_Establecimiento": "HUANCAN", "Provincia": "HUANCAYO",
        "Distrito": "HUANCAN",
    }  # fmt: skip
    base.update(cambios)
    return base


def test_cp152_lee_el_csv_completo_con_codigos_por_fila_y_altitud_de_la_capital(leido):
    registros, descartes_de_fila, filas = leido
    assert filas == 20 and len(registros) == 20 and not descartes_de_fila
    assert [r.codigo_origen for r in registros] == [f"DJ-{i:05d}" for i in range(1, 21)]
    primero = registros[0]
    assert (primero.provincia, primero.altitud_m, primero.comunidad, primero.distrito) == (
        "JUNIN",
        4113.0,
        "CARHUAMAYO",
        "CARHUAMAYO",
    )
    assert primero.establecimiento == "CARHUAMAYO" and primero.fecha_nacimiento == date(2023, 5, 21)
    assert {r.provincia: r.altitud_m for r in registros} == {
        k: float(v) for k, v in cfg.ALTITUD_CAPITAL_PROVINCIA.items()
    }
    assert all(r.comunidad == r.distrito for r in registros)  # comunidad = distrito


def test_cp153_los_nulos_y_los_datos_incompletos_no_se_inventan(leido):
    registros = {r.codigo_origen: r for r in leido[0]}
    tipos = lambda c: [e.tipo.value for e in registros[c].evaluaciones]  # noqa: E731
    assert tipos("DJ-00001") == ["DIAGNOSTICO"]
    assert registros["DJ-00001"].evaluaciones[0].clasificacion_origen == "LEV"
    assert registros["DJ-00003"].evaluaciones[0].clasificacion_origen is None  # valor_lab_dx = NULL
    assert (
        registros["DJ-00004"].evaluaciones == ()
        and "diagnostico_sin_hemoglobina" in registros["DJ-00004"].descartes_lectura
    )
    assert tipos("DJ-00007") == [] and "control_1_mes_sin_hemoglobina" in registros["DJ-00007"].descartes_lectura
    assert tipos("DJ-00009") == ["DIAGNOSTICO"]
    assert {"control_1_mes_sin_hemoglobina", "control_3_meses_sin_hemoglobina"} <= set(
        registros["DJ-00009"].descartes_lectura
    )
    assert "control_6_meses_sin_hemoglobina" in registros["DJ-00018"].descartes_lectura
    completo = max(registros.values(), key=lambda r: len(r.evaluaciones))
    assert [e.tipo.value for e in completo.evaluaciones] == [
        "DIAGNOSTICO",
        "CONTROL_1_MES",
        "CONTROL_3_MESES",
        "CONTROL_6_MESES",
    ]


def test_cp154_limpieza_de_una_fila_formatos_y_motivos_de_descarte():
    registro, problemas = fila_a_registro(
        7, fila_base(hb_dx="12,6", fecha_dosaje_dx="NULL", fecha_dosaje_mes="01/07/2024", hb="abc")
    )
    assert registro.codigo_origen == "DJ-00007"
    dx = registro.evaluaciones[0]
    assert (dx.fecha, dx.hemoglobina_observada) == (
        date(2024, 6, 21),
        12.6,
    )  # sin fecha de dosaje usa la fecha del diagnóstico
    assert problemas == ["hemoglobina_ilegible", "control_1_mes_sin_hemoglobina"]
    sin_fecha, p = fila_a_registro(1, fila_base(fecha_dosaje_3_meses="NULL", hb_tresmeses="11.2"))
    assert [e.tipo.value for e in sin_fecha.evaluaciones] == ["DIAGNOSTICO"] and p == ["control_3_meses_sin_fecha"]
    ilegible, p = fila_a_registro(1, fila_base(fecha_dosaje_6_meses="31/02/2024", hb_seismeses="11"))
    assert "fecha_ilegible" in p and "control_6_meses_sin_fecha" in p and len(ilegible.evaluaciones) == 1
    sin_fecha_dx, p = fila_a_registro(1, fila_base(fecha_dosaje_dx="NULL", fecha_dx="NULL"))
    assert sin_fecha_dx.evaluaciones == () and p == ["diagnostico_sin_fecha"]
    assert fila_a_registro(1, fila_base(hb_dx="NaN"))[1] == ["hemoglobina_ilegible", "diagnostico_sin_hemoglobina"]


@pytest.mark.parametrize(
    "cambios, motivo",
    [
        ({"fecha_nac": "NULL"}, "fila_sin_fecha_de_nacimiento_valida"),
        ({"fecha_nac": "99/99/2023"}, "fila_sin_fecha_de_nacimiento_valida"),
        ({"Provincia": "LIMA"}, "fila_con_provincia_sin_altitud"),
        ({"Nombre_Establecimiento": ""}, "fila_sin_establecimiento_o_distrito"),
        ({"Distrito": ""}, "fila_sin_establecimiento_o_distrito"),
    ],
)
def test_cp155_las_filas_inutilizables_se_descartan_con_su_motivo(cambios, motivo):
    registro, problemas = fila_a_registro(3, fila_base(**cambios))
    assert registro is None and problemas[-1] == motivo


def test_cp156_el_codigo_seudonimo_es_estable_y_la_severidad_del_his_se_conserva():
    assert codigo_de(1) == "DJ-00001" and codigo_de(12486) == "DJ-12486"
    registro, _ = fila_a_registro(5, fila_base(valor_lab_dx="OTRO"))
    assert registro.evaluaciones[0].clasificacion_origen is None  # solo LEV, MOD y SEV son valores del HIS


def test_cp157_muestra_estratificada_proporcional_exacta_y_reproducible(leido):
    registros = leido[0]
    a = muestra_estratificada(registros, 10, 2026)
    assert len(a) == 10 and a == muestra_estratificada(registros, 10, 2026)  # misma semilla, misma muestra
    assert [r.codigo_origen for r in a] == sorted(r.codigo_origen for r in a)
    assert a != muestra_estratificada(registros, 10, 7)
    assert len(muestra_estratificada(list(reversed(registros)), 10, 2026)) == 10
    assert muestra_estratificada(list(reversed(registros)), 10, 2026) == a  # no depende del orden de lectura
    assert muestra_estratificada(registros, 500, 1) == sorted(registros, key=lambda r: r.codigo_origen)  # n >= total
    assert estrato(registros[0]) == ("JUNIN", "LEV") and estrato(registros[2]) == ("HUANCAYO", "NULL")


def test_cp157_el_reparto_por_mayor_resto_suma_exactamente_n_y_respeta_la_proporcion():
    tamanos = {("A", "LEV"): 600, ("A", "MOD"): 300, ("B", "LEV"): 90, ("B", "SEV"): 10}
    cupos = asignar_cupos(tamanos, 100)
    assert cupos == {("A", "LEV"): 60, ("A", "MOD"): 30, ("B", "LEV"): 9, ("B", "SEV"): 1}
    irregular = asignar_cupos({("A", "x"): 7, ("B", "x"): 7, ("C", "x"): 7}, 10)
    assert sum(irregular.values()) == 10 and max(irregular.values()) - min(irregular.values()) == 1
    assert asignar_cupos({("A", "x"): 3}, 10) == {("A", "x"): 3}


def test_cp158_la_concordancia_se_calcula_sobre_los_diagnosticos_con_severidad_del_his():
    c = concordancia(
        {
            "LEV": {"LEVE": 6, "SIN_ANEMIA": 2, "MODERADA": 2},
            "MOD": {"MODERADA": 3, "NO_APLICA": 1},
            "SIN_DATO": {"LEVE": 5},
        }
    )
    assert c["diagnosticos_con_severidad_his"] == 14 and c["diagnosticos_sin_severidad_his"] == 5
    assert (c["de_acuerdo"], c["porcentaje_acuerdo"]) == (9, 64.3)
    assert (c["sistema_sin_anemia"], c["porcentaje_sistema_sin_anemia"]) == (3, 21.4)
    assert c["porcentaje_acuerdo_entre_anemicos"] == 81.8
    assert concordancia({})["porcentaje_acuerdo"] is None


@pytest.fixture
def base(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path}/importacion.db"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.delenv("FECHA_REFERENCIA", raising=False)
    return url


def ejecutar(*args):
    return cli.main(["--csv", str(FIXTURE), *args])


def test_cp159_importacion_completa_por_cli_con_reporte_json(base, tmp_path, capsys):
    reporte = tmp_path / "reporte.json"
    assert ejecutar("--completo", "--reiniciar", "--reporte", str(reporte)) == 0
    r = json.loads(reporte.read_text(encoding="utf-8"))
    assert (r["modo"], r["filas_leidas"], r["ninos_importados"], r["ninos_omitidos"]) == ("completo", 20, 18, 2)
    assert r["fecha_referencia"] == "2024-06-30" and r["version"] == "2.0.0-inc2"
    assert r["evaluaciones_importadas"] == {
        "total": 42,
        "por_tipo": {"CONTROL_1_MES": 11, "CONTROL_3_MESES": 9, "CONTROL_6_MESES": 4, "DIAGNOSTICO": 18},
    }
    assert r["descartes_por_motivo"]["evaluacion_con_hemoglobina_fuera_de_rango"] == 2
    assert r["descartes_por_motivo"]["nino_sin_evaluaciones_validas"] == 2
    assert r["calidad_del_archivo_completo"]["diagnostico_sin_hemoglobina"] == 2
    assert sum(r["distribucion_por_provincia"].values()) == 18 and len(r["distribucion_por_provincia"]) == 9
    c = r["concordancia_his_vs_sistema"]
    assert (c["diagnosticos_con_severidad_his"], c["de_acuerdo"], c["porcentaje_acuerdo"]) == (17, 8, 47.1)
    assert r["altitud_por_provincia_m"]["JUNIN"] == 4113
    salida = capsys.readouterr().out
    assert "Niños importados: 18" in salida and "47.1 %" in salida
    repo = RepositorioSQLAlchemy(base)
    ninos = repo.listar()
    assert len(ninos) == 18 and all(n.origen == OrigenDatos.DATASET_DIRESA_JUNIN and n.dni is None for n in ninos)
    assert all(e.peso_kg is None and e.talla_cm is None for n in ninos for e in n.evaluaciones)
    assert len(repo.listar(texto="dj-00001")) == 1
    repo.engine.dispose()


def test_cp160_muestra_reproducible_reiniciar_y_registros_de_prueba_del_sistema(base, tmp_path, capsys):
    reporte = tmp_path / "muestra.json"
    assert (
        ejecutar(
            "--muestra",
            "6",
            "--semilla",
            "2026",
            "--reiniciar",
            "--con-registros-sistema",
            "3",
            "--reporte",
            str(reporte),
        )
        == 0
    )
    r = json.loads(reporte.read_text(encoding="utf-8"))
    assert (r["modo"], r["semilla"], r["muestra_solicitada"], r["filas_enviadas_a_importar"]) == ("muestra", 2026, 6, 6)
    assert (
        r["filas_con_evaluacion_utilizable"] == 18
        and r["ninos_importados"] == 6
        and r["registros_sistema_creados"] == 3
    )
    repo = RepositorioSQLAlchemy(base)
    codigos = sorted(n.codigo_origen for n in repo.listar() if n.es_dataset)
    sistema = [n for n in repo.listar() if not n.es_dataset]
    assert len(codigos) == 6 and len(sistema) == 3
    assert all(
        n.origen == OrigenDatos.SISTEMA and n.dni and n.nombres and n.apellidos and n.tutor_nombre for n in sistema
    )
    assert all("PRUEBA" in n.nombres.upper() and n.registrado_por == "demo.registros-sistema" for n in sistema)
    assert all(e.peso_kg and e.talla_cm for n in sistema for e in n.evaluaciones)
    # Sin --reiniciar no se importa dos veces; con --reiniciar y la misma semilla queda la misma muestra.
    assert ejecutar("--muestra", "6") == 2
    assert "use --reiniciar" in capsys.readouterr().err
    assert ejecutar("--muestra", "6", "--semilla", "2026", "--reiniciar", "--con-registros-sistema", "3") == 0
    assert sorted(n.codigo_origen for n in repo.listar() if n.es_dataset) == codigos
    assert len([n for n in repo.listar() if not n.es_dataset]) == 3  # los de prueba ya existentes se omiten por su DNI
    repo.engine.dispose()


def test_cp160_fecha_de_referencia_por_opcion_o_entorno(base, monkeypatch, tmp_path):
    reporte = tmp_path / "fecha.json"
    monkeypatch.setenv("FECHA_REFERENCIA", "2024-07-31")
    assert ejecutar("--completo", "--reiniciar", "--reporte", str(reporte)) == 0
    assert json.loads(reporte.read_text())["fecha_referencia"] == "2024-07-31"
    assert ejecutar("--completo", "--reiniciar", "--fecha-referencia", "2024-06-30", "--reporte", str(reporte)) == 0
    assert json.loads(reporte.read_text())["fecha_referencia"] == "2024-06-30"
    with pytest.raises(ValueError, match="FECHA_REFERENCIA inválida"):
        ejecutar("--completo", "--fecha-referencia", "30/06/2024")
