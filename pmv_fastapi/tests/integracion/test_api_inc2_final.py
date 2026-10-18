"""CP-161 a CP-172: integración API + SQLAlchemy (SQLite) de HIST-2.3, HIST-2.4, el origen de los datos del dataset
DIRESA Junín y la fecha de referencia (ADR-009 y ADR-010).

Escenario de agenda y asistencia (hoy = 28-sep-2026), el mismo de test_api_inc2: V con tres dosajes de edad vencidos
(Palmayoc), T con el C1M de tratamiento vencido (Llacuas), M y B con el DHx de 15 meses vencido hace 8 y 7 días.
"""

import threading
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.adapters.outbound.persistence.sqlalchemy_repo import RepositorioSQLAlchemy
from app.application.servicio_importacion import ServicioImportacion
from app.domain.model.asistencia import AsistenciaControl, EstadoAsistencia
from app.domain.model.errores import ConflictoAsistencia
from app.main import crear_app
from scripts.importador_diresa.lector import leer_registros
from tests.conftest import RelojFijo, cuerpo_registro
from tests.integracion.test_api_inc2 import ESCENARIO, registrar

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "dataset_muestra.csv"
CORTE = date(2024, 6, 30)


@pytest.fixture
def escenario(cliente):
    return {clave: registrar(cliente, **datos) for clave, datos in ESCENARIO.items()}


def asistencia(cliente, nino, codigo, programada, estado="NO_ASISTIO", usuario="enf.rosa", **extra):
    cuerpo = {"fecha_programada": programada, "estado": estado, **extra}
    return cliente.post(f"/api/ninos/{nino}/controles/{codigo}/asistencia", json=cuerpo, headers={"X-Usuario": usuario})


# --- Fecha de referencia ---------------------------------------------------------------------------------------------


def test_cp161_salud_expone_la_fecha_de_hoy_y_la_de_referencia_si_esta_fijada(tmp_path, monkeypatch):
    monkeypatch.delenv("FECHA_REFERENCIA", raising=False)
    url = f"sqlite:///{tmp_path}/ref.db"
    app = crear_app(url, fecha_referencia=CORTE)
    with TestClient(app) as c:
        assert c.get("/api/salud").json() == {
            "estado": "ok",
            "fecha_hoy": "2024-06-30",
            "fecha_referencia": "2024-06-30",
        }
        assert c.get("/api/ninos").status_code == 200
        assert c.get("/api/agenda").json()["fecha_referencia"] == "2024-06-30"  # usa el reloj fijo en toda la API
    app.state.repositorio.engine.dispose()
    monkeypatch.setenv("FECHA_REFERENCIA", "2024-07-15")
    app = crear_app(url)
    with TestClient(app) as c:
        assert c.get("/api/salud").json()["fecha_referencia"] == "2024-07-15"
    app.state.repositorio.engine.dispose()
    app = crear_app(url, reloj=RelojFijo(date(2026, 9, 28)))  # un reloj inyectado manda sobre la variable de entorno
    with TestClient(app) as c:
        assert c.get("/api/salud").json() == {"estado": "ok", "fecha_hoy": "2026-09-28", "fecha_referencia": None}
    app.state.repositorio.engine.dispose()


def test_cp161_sin_fecha_de_referencia_se_usa_el_reloj_real_y_una_fecha_mal_escrita_se_rechaza(tmp_path, monkeypatch):
    monkeypatch.delenv("FECHA_REFERENCIA", raising=False)
    app = crear_app(f"sqlite:///{tmp_path}/real.db")
    with TestClient(app) as c:
        cuerpo = c.get("/api/salud").json()
        assert (
            cuerpo["fecha_referencia"] is None
            and cuerpo["fecha_hoy"] == c.get("/api/agenda").json()["fecha_referencia"]
        )
    app.state.repositorio.engine.dispose()
    monkeypatch.setenv("FECHA_REFERENCIA", "30/06/2024")
    with pytest.raises(ValueError, match="AAAA-MM-DD"):
        crear_app(f"sqlite:///{tmp_path}/mala.db")


# --- HIST-2.3 --------------------------------------------------------------------------------------------------------


def test_cp162_agenda_del_personal_por_defecto_es_la_semana_de_la_fecha_de_referencia(cliente, escenario):
    r = cliente.get("/api/agenda")
    assert r.status_code == 200
    a = r.json()
    assert (a["desde"], a["hasta"], a["fecha_referencia"]) == ("2026-09-28", "2026-10-04", "2026-09-28")
    assert [d["fecha"] for d in a["dias"]][0] == "2026-09-28" and len(a["dias"]) == 7
    assert a["establecimiento"] is None and a["comunidad"] is None
    assert a["establecimientos_disponibles"] == ["P. S. Chongos Alto"]
    assert a["comunidades_disponibles"] == ["Chongos Alto", "Huaycha", "Llacuas", "Palmayoc"]
    assert set(a["resumen"]) == {"total", "cumplidos", "pendientes", "vencidos", "con_inasistencia", "ninos"}
    assert a["resumen"]["total"] == sum(d["total"] for d in a["dias"])
    assert a["resumen"]["ninos"] >= 1  # T: C3M del 1-oct (pendiente)


def test_cp163_agenda_del_personal_campos_totales_y_orden_de_un_rango(cliente, escenario):
    a = cliente.get("/api/agenda", params={"desde": "2026-08-01", "hasta": "2026-08-31"}).json()
    con = {d["fecha"]: d for d in a["dias"] if d["total"]}
    assert sorted(con) == ["2026-08-01", "2026-08-21", "2026-08-22"]
    d1 = con["2026-08-01"]
    assert (d1["total"], d1["vencidos"], d1["pendientes"], d1["cumplidos"], d1["con_inasistencia"]) == (1, 1, 0, 0, 0)
    item = d1["items"][0]
    assert item["nino"] == {
        "id": escenario["T"],
        "codigo_origen": None,
        "dni": "70000002",
        "nombre_completo": "Luz Mery Quispe Rojas",
        "establecimiento": "P. S. Chongos Alto",
        "comunidad": "Llacuas",
    }
    assert (item["control"]["codigo"], item["control"]["estado"], item["prioridad"]) == ("C1M", "VENCIDO", "ALTA")
    assert [con[f]["items"][0]["prioridad"] for f in ("2026-08-21", "2026-08-22")] == ["MEDIA", "BAJA"]
    assert (a["resumen"]["total"], a["resumen"]["vencidos"], a["resumen"]["ninos"]) == (3, 3, 3)
    pendiente = next(
        i
        for d in cliente.get("/api/agenda", params={"desde": "2026-10-01", "hasta": "2026-10-01"}).json()["dias"]
        for i in d["items"]
    )
    assert (pendiente["control"]["estado"], pendiente["prioridad"]) == ("PENDIENTE", None)  # C3M de T


def test_cp164_agenda_del_personal_filtros_y_un_solo_extremo(cliente, escenario):
    base = {"desde": "2026-08-01", "hasta": "2026-08-31"}

    def ninos(**filtros):
        a = cliente.get("/api/agenda", params={**base, **filtros}).json()
        return sorted(i["nino"]["dni"] for d in a["dias"] for i in d["items"])

    assert ninos(comunidad="Llacuas") == ["70000002"]
    assert ninos(comunidad="chongos alto") == ["70000003"]
    assert ninos(establecimiento="P. S. Chongos Alto", comunidad="Huaycha") == ["70000004"]
    assert ninos(establecimiento="Otra posta") == [] and ninos(comunidad="") == ["70000002", "70000003", "70000004"]
    a = cliente.get("/api/agenda", params={"desde": "2026-09-30"}).json()
    assert (a["desde"], a["hasta"]) == ("2026-09-30", "2026-10-06")
    a = cliente.get("/api/agenda", params={"hasta": "2026-09-30"}).json()
    assert (a["desde"], a["hasta"]) == ("2026-09-24", "2026-09-30")
    otro = cliente.get("/api/agenda", params={**base, "establecimiento": "Otra posta"}).json()
    assert otro["resumen"]["total"] == 0 and otro["comunidades_disponibles"] == []


@pytest.mark.parametrize(
    "params, campo",
    [
        ({"desde": "2026-09-01", "hasta": "2026-10-02"}, "hasta"),  # 32 días
        ({"desde": "2026-09-30", "hasta": "2026-09-01"}, "desde"),
        ({"desde": "0001-01-01", "hasta": "0001-01-05"}, "desde"),
        ({"desde": "2026-01-01", "hasta": "9999-12-31"}, "hasta"),
        ({"desde": "ayer"}, "desde"),
        ({"hasta": "2026-13-45"}, "hasta"),
    ],
)
def test_cp165_agenda_del_personal_rango_invalido_devuelve_422(cliente, params, campo):
    r = cliente.get("/api/agenda", params=params)
    assert r.status_code == 422, r.text
    assert r.json()["errores"][0]["campo"] == campo
    assert (
        cliente.get("/api/agenda", params={"desde": "2026-09-01", "hasta": "2026-10-01"}).status_code == 200
    )  # 31 días


# --- HIST-2.4 --------------------------------------------------------------------------------------------------------


def test_cp166_registrar_asistencia_y_su_efecto_en_la_agenda_y_las_alertas(cliente, escenario):
    # B: DHx de 15 meses del 22-ago, vencido hace 7 días (prioridad BAJA).
    antes = {f["nino"]["id"]: f for f in cliente.get("/api/alertas/controles-vencidos").json()}
    assert antes[escenario["B"]]["prioridad"] == "BAJA"
    r = asistencia(cliente, escenario["B"], "DHx", "2026-08-22", motivo="Viaje de la familia", usuario="tec.juan")
    assert r.status_code == 201, r.text
    cuerpo = r.json()
    assert (cuerpo["codigo_control"], cuerpo["fecha_programada"], cuerpo["estado"]) == (
        "DHx",
        "2026-08-22",
        "NO_ASISTIO",
    )
    assert (cuerpo["motivo"], cuerpo["registrado_por"], cuerpo["evaluacion_id"], cuerpo["nino_id"]) == (
        "Viaje de la familia",
        "tec.juan",
        None,
        escenario["B"],
    )
    assert cuerpo["id"] and cuerpo["creado_en"]
    despues = {f["nino"]["id"]: f for f in cliente.get("/api/alertas/controles-vencidos").json()}
    assert despues[escenario["B"]]["prioridad"] == "MEDIA"  # sube un nivel
    ctrl = despues[escenario["B"]]["control"]
    assert (ctrl["estado"], ctrl["inasistencia_registrada"], ctrl["motivo_inasistencia"]) == (
        "VENCIDO",
        True,
        "Viaje de la familia",
    )
    assert len(despues) == len(antes)
    agenda = cliente.get(f"/api/ninos/{escenario['B']}/agenda").json()
    assert agenda["resumen"]["inasistencias"] == 1
    personal = cliente.get("/api/agenda", params={"desde": "2026-08-22", "hasta": "2026-08-22"}).json()
    assert personal["resumen"]["con_inasistencia"] == 1
    # M asistió al DHx del 21-ago: el control queda cumplido sin evaluación y deja de generar alerta.
    r = asistencia(cliente, escenario["M"], "DHx", "2026-08-21", estado="ASISTIO")
    assert r.status_code == 201 and r.json()["motivo"] is None
    ag_m = cliente.get(f"/api/ninos/{escenario['M']}/agenda").json()
    dhx = next(c for c in ag_m["controles"] if c["codigo"] == "DHx" and c["fecha_programada"] == "2026-08-21")
    assert (dhx["estado"], dhx["cumplido_por_asistencia"], dhx["evaluacion_id"]) == ("CUMPLIDO", True, None)
    assert escenario["M"] not in {f["nino"]["id"] for f in cliente.get("/api/alertas/controles-vencidos").json()}
    final = cliente.get("/api/alertas/controles-vencidos").json()
    assert cliente.get("/api/alertas/resumen").json()["total_vencidos"] == len(final)  # B sigue vencido; M ya no


def test_cp167_no_se_registra_dos_veces_ni_con_fecha_futura_ni_con_datos_invalidos(cliente, escenario):
    nino = escenario["B"]
    assert asistencia(cliente, nino, "DHx", "2026-08-22", motivo="Viaje").status_code == 201
    r = asistencia(cliente, nino, "DHx", "2026-08-22", estado="ASISTIO")
    assert (
        r.status_code == 409
        and r.json()["errores"][0]["campo"] == "codigo"
        and "ya tiene una asistencia" in r.json()["mensaje"]
    )
    r = asistencia(cliente, escenario["T"], "C3M", "2026-10-01", estado="ASISTIO")  # control del 1-oct: futuro
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "fecha_programada"
    r = asistencia(cliente, escenario["V"], "DHc1", "2025-12-10")  # falta el motivo
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "motivo"
    r = asistencia(cliente, escenario["V"], "DHc1", "2025-12-10", estado="TAL VEZ")
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "estado"
    r = cliente.post(f"/api/ninos/{nino}/controles/DHx/asistencia", json={"estado": "ASISTIO"})
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "fecha_programada"
    r = asistencia(cliente, nino, "DHx", "no-es-fecha", estado="ASISTIO")
    assert r.status_code == 422
    assert asistencia(cliente, "no-existe", "DHx", "2026-08-22", estado="ASISTIO").status_code == 404
    assert asistencia(cliente, nino, "C6M", "2026-08-22", estado="ASISTIO").status_code == 404  # no hay ese control
    cumplido = asistencia(cliente, escenario["V"], "DHx", "2025-09-10", estado="ASISTIO")  # ya cumplido por evaluación
    assert cumplido.status_code == 409 and "ya está cumplido" in cumplido.json()["mensaje"]
    assert (
        len(cliente.get(f"/api/ninos/{nino}/asistencias").json()) == 1
    )  # las solicitudes rechazadas no guardaron nada


def test_cp168_asistio_con_la_evaluacion_vinculada_y_listado_de_asistencias(cliente, escenario):
    v = escenario["V"]
    exp = cliente.post(
        f"/api/ninos/{v}/evaluaciones",
        json={"fecha": "2026-07-20", "hemoglobina_observada": 13.5, "peso_kg": 11, "talla_cm": 82},
    ).json()
    evaluacion = exp["evaluaciones"][0]["id"]
    r = asistencia(cliente, v, "DHx", "2026-06-10", estado="ASISTIO", evaluacion_id=evaluacion)
    assert r.status_code == 201 and r.json()["evaluacion_id"] == evaluacion
    ag = cliente.get(f"/api/ninos/{v}/agenda").json()
    dhx = next(c for c in ag["controles"] if c["fecha_programada"] == "2026-06-10")
    assert (dhx["estado"], dhx["evaluacion_id"], dhx["cumplido_por_asistencia"]) == ("CUMPLIDO", evaluacion, True)
    ajena = asistencia(cliente, v, "DHc1", "2025-12-10", estado="ASISTIO", evaluacion_id="de-otro-niño")
    assert ajena.status_code == 422 and ajena.json()["errores"][0]["campo"] == "evaluacion_id"
    reusada = asistencia(cliente, v, "DHc1", "2025-12-10", estado="ASISTIO", evaluacion_id=evaluacion)
    assert reusada.status_code == 422
    assert asistencia(cliente, v, "DHc1", "2025-12-10", motivo="Olvido de la cita").status_code == 201
    lista = cliente.get(f"/api/ninos/{v}/asistencias").json()
    assert [(a["codigo_control"], a["fecha_programada"], a["estado"]) for a in lista] == [
        ("DHc1", "2025-12-10", "NO_ASISTIO"),
        ("DHx", "2026-06-10", "ASISTIO"),
    ]
    assert cliente.get("/api/ninos/no-existe/asistencias").status_code == 404
    assert cliente.get(f"/api/ninos/{escenario['T']}/asistencias").json() == []


def test_cp169_dos_registros_simultaneos_del_mismo_control_dan_un_201_y_el_resto_409(cliente, escenario):
    resultados = []

    def registrar_uno():
        resultados.append(asistencia(cliente, escenario["B"], "DHx", "2026-08-22", motivo="Viaje").status_code)

    hilos = [threading.Thread(target=registrar_uno) for _ in range(6)]
    [h.start() for h in hilos]
    [h.join() for h in hilos]
    assert sorted(resultados) == [201] + [409] * 5
    assert len(cliente.get(f"/api/ninos/{escenario['B']}/asistencias").json()) == 1


# --- Registros del dataset -------------------------------------------------------------------------------------------


@pytest.fixture
def cliente_dataset(tmp_path):
    app = crear_app(f"sqlite:///{tmp_path}/dataset.db", fecha_referencia=CORTE)
    registros, _, _ = leer_registros(FIXTURE)
    ServicioImportacion(app.state.repositorio, RelojFijo(CORTE)).importar(registros)
    with TestClient(app) as c:
        yield c
    app.state.repositorio.engine.dispose()


def test_cp170_listado_busqueda_y_expediente_de_un_registro_del_dataset(cliente_dataset):
    c = cliente_dataset
    filas = c.get("/api/ninos").json()
    assert len(filas) == 18
    fila = next(f for f in filas if f["codigo_origen"] == "DJ-00002")
    assert (fila["dni"], fila["origen"], fila["nombre_completo"]) == (
        None,
        "DATASET_DIRESA_JUNIN",
        "Registro DJ-00002 (dataset anonimizado)",
    )
    assert fila["ultima_clasificacion"] == "LEVE"
    assert [f["codigo_origen"] for f in c.get("/api/ninos", params={"q": "dj-00002"}).json()] == ["DJ-00002"]
    exp = c.get(f"/api/ninos/{fila['id']}").json()
    assert exp["dni"] is None and exp["nombres"] is None and exp["tutor_nombre"] is None and exp["sexo"] is None
    assert exp["nombre_completo"] == "Registro DJ-00002 (dataset anonimizado)" and exp["codigo_origen"] == "DJ-00002"
    assert (exp["provincia"], exp["origen"], exp["altitud_m"]) == ("CHUPACA", "DATASET_DIRESA_JUNIN", 3281.0)
    assert exp["red"] and exp["microred"] and exp["tutor_celular"] is None
    (ev,) = exp["evaluaciones"]
    assert (ev["peso_kg"], ev["talla_cm"], ev["clasificacion_origen"]) == (None, None, "SEV")
    assert c.get("/api/ninos/dni/00000000").status_code == 404  # buscar por DNI no aplica al dataset


def test_cp171_agenda_alertas_reporte_y_csv_con_registros_del_dataset(cliente_dataset):
    c = cliente_dataset
    nino = next(f for f in c.get("/api/ninos").json() if f["codigo_origen"] == "DJ-00019")
    agenda = c.get(f"/api/ninos/{nino['id']}/agenda").json()
    assert agenda["aplica"] and agenda["fecha_referencia"] == "2024-06-30" and agenda["resumen"]["total"] > 0
    alertas = c.get("/api/alertas/controles-vencidos").json()
    assert alertas and all(a["nino"]["dni"] is None and a["nino"]["codigo_origen"] for a in alertas)
    assert any(a["nino"]["nombre_completo"] == "Registro DJ-00019 (dataset anonimizado)" for a in alertas)
    semana = c.get("/api/agenda").json()
    assert (semana["desde"], semana["hasta"]) == ("2024-06-24", "2024-06-30")
    assert all(i["nino"]["dni"] is None for d in semana["dias"] for i in d["items"])
    reporte = c.get("/api/reportes/periodo", params={"desde": "2024-06-01", "hasta": "2024-06-30"}).json()
    assert (
        reporte["evaluaciones_realizadas"] > 0 and reporte["ninos_registrados"] > 0
    )  # creado_en sigue la fecha clínica
    csv = c.get("/api/reportes/periodo", params={"desde": "2024-05-01", "hasta": "2024-06-30", "formato": "csv"})
    assert csv.status_code == 200 and "Registro DJ-" in csv.text
    primera = csv.text.splitlines()[1].split(",")
    assert primera[1] == "" and primera[9] == "" and primera[10] == ""  # sin DNI, peso ni talla


def test_cp172_el_cliente_no_puede_elegir_el_origen_y_el_sistema_sigue_exigiendo_todo(cliente_dataset):
    c = cliente_dataset
    cuerpo = cuerpo_registro(dni="79999999")
    cuerpo["nino"].update(origen="DATASET_DIRESA_JUNIN", codigo_origen="DJ-99999", fecha_nacimiento="2023-06-01")
    cuerpo["evaluacion_inicial"]["fecha"] = "2024-06-20"
    r = c.post("/api/ninos", json=cuerpo)
    assert r.status_code == 201, r.text
    assert (r.json()["origen"], r.json()["codigo_origen"], r.json()["dni"]) == ("SISTEMA", None, "79999999")
    sin_dni = cuerpo_registro(dni="")
    sin_dni["nino"]["fecha_nacimiento"] = "2023-06-01"
    sin_dni["evaluacion_inicial"]["fecha"] = "2024-06-20"
    r = c.post("/api/ninos", json=sin_dni)
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "dni"
    sin_peso = cuerpo_registro(dni="79999998")
    sin_peso["nino"]["fecha_nacimiento"] = "2023-06-01"
    sin_peso["evaluacion_inicial"].update(fecha="2024-06-20", peso_kg=None, talla_cm=None)
    r = c.post("/api/ninos", json=sin_peso)
    assert r.status_code == 422 and {e["campo"] for e in r.json()["errores"]} == {"peso_kg", "talla_cm"}
    nino = next(f for f in c.get("/api/ninos").json() if f["codigo_origen"] == "DJ-00002")
    r = c.patch(f"/api/ninos/{nino['id']}", json={"comunidad": "OTRA", "tutor_nombre": ""})
    assert r.status_code == 200 and r.json()["comunidad"] == "OTRA" and r.json()["tutor_nombre"] is None
    nuevo = c.post(
        f"/api/ninos/{nino['id']}/evaluaciones",
        json={"fecha": "2024-06-25", "hemoglobina_observada": 11, "peso_kg": 11, "talla_cm": 80},
    )
    assert nuevo.status_code == 201 and len(nuevo.json()["evaluaciones"]) == 2


# --- Restricciones de la base ----------------------------------------------------------------------------------------


def test_cp173_la_base_exige_los_datos_personales_solo_para_el_origen_sistema(tmp_path):
    repo = RepositorioSQLAlchemy(f"sqlite:///{tmp_path}/restricciones.db")
    repo.crear_esquema()
    insertar = "INSERT INTO nino (id, dni, nombres, apellidos, sexo, fecha_nacimiento, establecimiento, distrito, comunidad, altitud_m, tutor_nombre, estado, origen, codigo_origen, registrado_por, creado_en, actualizado_en) VALUES (:id, :dni, :nombres, :apellidos, :sexo, '2024-01-01', 'E', 'D', 'C', 3000, :tutor, 'ACTIVO', :origen, :codigo, 'x', '2024-01-01', '2024-01-01')"  # noqa: S608
    base = dict(
        id="1",
        dni=None,
        nombres=None,
        apellidos=None,
        sexo=None,
        tutor=None,
        origen="DATASET_DIRESA_JUNIN",
        codigo="DJ-1",
    )

    def ejecutar(**cambios):
        with repo.engine.begin() as con:
            con.execute(text(insertar), {**base, **cambios})

    ejecutar()  # dataset sin datos personales: permitido
    ejecutar(id="2", codigo="DJ-2")  # varios NULL en dni: permitido (UNIQUE solo cuenta los no nulos)
    with pytest.raises(IntegrityError):
        ejecutar(id="3", codigo="DJ-1")  # el código seudónimo es único
    with pytest.raises(IntegrityError):
        ejecutar(id="4", codigo=None)  # un registro del dataset debe tener código
    with pytest.raises(IntegrityError):
        ejecutar(id="5", origen="SISTEMA", codigo=None)  # SISTEMA sin dni ni nombres: la base lo rechaza
    with pytest.raises(IntegrityError):
        ejecutar(id="6", origen="OTRO")
    completo = dict(origen="SISTEMA", codigo=None, dni="71234567", nombres="A", apellidos="B", sexo="F", tutor="T")
    ejecutar(id="7", **completo)
    with pytest.raises(IntegrityError):
        ejecutar(id="8", **completo)  # DNI repetido
    repo.engine.dispose()


def test_cp174_restricciones_de_la_asistencia_y_borrado_en_cascada(tmp_path):
    repo = RepositorioSQLAlchemy(f"sqlite:///{tmp_path}/asistencia.db")
    repo.crear_esquema()
    from tests.conftest import nino_de

    nino = nino_de(date(2025, 3, 10), [(date(2025, 6, 10), "NO_APLICA")])
    repo.guardar(nino)
    repo.agregar_evaluacion(nino.evaluaciones[0])
    a = AsistenciaControl(nino.id, "DHx", date(2025, 9, 10), EstadoAsistencia.NO_ASISTIO, "enf", motivo="Viaje")
    repo.agregar_asistencia(a)
    with pytest.raises(ConflictoAsistencia):
        repo.agregar_asistencia(AsistenciaControl(nino.id, "DHx", date(2025, 9, 10), EstadoAsistencia.ASISTIO, "enf"))
    otra_fecha = AsistenciaControl(nino.id, "DHx", date(2026, 6, 10), EstadoAsistencia.ASISTIO, "enf")
    assert repo.agregar_asistencia(otra_fecha) is otra_fecha  # la misma clave con otra fecha programada es otro control
    with pytest.raises(IntegrityError):  # inasistencia sin motivo: la base lo rechaza
        repo.agregar_asistencia(
            AsistenciaControl(nino.id, "DHc1", date(2025, 12, 10), EstadoAsistencia.NO_ASISTIO, "enf")
        )
    guardado = repo.obtener(nino.id)
    assert [(x.codigo_control, x.estado, x.motivo) for x in guardado.asistencias] == [
        ("DHx", EstadoAsistencia.NO_ASISTIO, "Viaje"),
        ("DHx", EstadoAsistencia.ASISTIO, None),
    ]
    assert repo.contar_por_origen("SISTEMA") == 1 and repo.eliminar_por_origen("SISTEMA") == 1
    with repo.engine.connect() as con:
        assert con.execute(text("SELECT count(*) FROM asistencia_control")).scalar() == 0
        assert con.execute(text("SELECT count(*) FROM evaluacion_hemoglobina")).scalar() == 0
    assert repo.guardar_varios([]) == 0
    sin_evaluaciones = nino_de(date(2025, 3, 10), [])
    assert repo.guardar_varios([sin_evaluaciones]) == 1 and repo.obtener(sin_evaluaciones.id).evaluaciones == []
    repo.engine.dispose()


def test_cp175_una_base_con_el_esquema_1x_se_rechaza_con_un_mensaje_claro(tmp_path):
    ruta = tmp_path / "vieja.db"
    repo = RepositorioSQLAlchemy(f"sqlite:///{ruta}")
    with repo.engine.begin() as con:
        con.execute(text("CREATE TABLE nino (id VARCHAR(36) PRIMARY KEY, dni VARCHAR(8) NOT NULL)"))
    with pytest.raises(RuntimeError, match="esquema de la versión 1.x"):
        repo.crear_esquema()
    repo.engine.dispose()
