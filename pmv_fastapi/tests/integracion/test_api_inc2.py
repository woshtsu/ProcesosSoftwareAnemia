"""CP-89 a CP-107 y CP-115: integración API + SQLAlchemy (SQLite) del avance del Incremento 2.

HIST-2.1 agenda de un niño, HIST-2.2 alertas, cambio de /api/ninos y regresión de DEF-03 a DEF-08.
Escenario (hoy = 28-sep-2026): V vencidos de edad, T tratamiento vencido, M atraso medio, B atraso bajo, A con alta.
"""

import json

import pytest

from tests.conftest import cuerpo_registro

ESCENARIO = {
    "V": dict(dni="70000001", nacimiento="2025-03-10", evaluacion="2025-09-12", comunidad="Palmayoc", hb=13.5),
    "T": dict(dni="70000002", nacimiento="2025-09-01", evaluacion="2026-07-01", comunidad="Llacuas", hb=11.0),
    "M": dict(dni="70000003", nacimiento="2025-05-21", evaluacion="2026-08-01", comunidad="Chongos Alto", hb=13.5),
    "B": dict(dni="70000004", nacimiento="2025-05-22", evaluacion="2026-08-01", comunidad="Huaycha", hb=13.5),
    "A": dict(dni="70000005", nacimiento="2025-03-10", evaluacion="2025-09-12", comunidad="Palmayoc", hb=13.5),
}


def registrar(cliente, dni, nacimiento, evaluacion, comunidad, hb):
    cuerpo = cuerpo_registro(dni=dni, comunidad=comunidad)
    cuerpo["nino"]["fecha_nacimiento"] = nacimiento
    cuerpo["evaluacion_inicial"].update(fecha=evaluacion, hemoglobina_observada=hb)
    r = cliente.post("/api/ninos", json=cuerpo, headers={"X-Usuario": "enf.rosa"})
    assert r.status_code == 201, r.text
    return r.json()["id"]


@pytest.fixture
def escenario(cliente):
    ids = {clave: registrar(cliente, **datos) for clave, datos in ESCENARIO.items()}
    assert cliente.patch(f"/api/ninos/{ids['A']}", json={"estado": "ALTA"}).status_code == 200
    return ids


# --- HIST-2.1 ---------------------------------------------------------------------------------------------------------


def test_cp89_agenda_de_un_nino(cliente, escenario):
    r = cliente.get(f"/api/ninos/{escenario['V']}/agenda")
    assert r.status_code == 200
    ag = r.json()
    assert ag["nino_id"] == escenario["V"] and ag["version_esquema"] == "AGENDA-V1"
    assert ag["fecha_referencia"] == "2026-09-28" and ag["aplica"] is True and ag["motivo"] is None
    assert ag["resumen"] == {
        "total": 12,
        "cumplidos": 1,
        "pendientes": 8,
        "vencidos": 3,
        "cerrados": 0,
        "proximos": 0,
        "inasistencias": 0,
        "proximo_control": ag["resumen"]["proximo_control"],
    }
    assert ag["resumen"]["proximo_control"]["codigo"] == "DHc1"  # 18 meses, aún dentro de la ventana
    assert ag["resumen"]["proximo_control"]["fecha_programada"] == "2026-09-10"
    fechas = [c["fecha_programada"] for c in ag["controles"]]
    assert fechas == sorted(fechas)


def test_cp90_campos_de_cada_control(cliente, escenario):
    controles = cliente.get(f"/api/ninos/{escenario['V']}/agenda").json()["controles"]
    cumplido, vencido = controles[0], controles[1]
    assert cumplido == {
        "codigo": "DHx",
        "tipo": "TAMIZAJE_EDAD",
        "descripcion": "Dosaje de tamizaje DHx (6 meses)",
        "fecha_programada": "2025-09-10",
        "fecha_inicio_ventana": "2025-08-26",
        "fecha_limite": "2025-10-10",
        "estado": "CUMPLIDO",
        "proximo": False,
        "dias_vencido": None,
        "evaluacion_id": cumplido["evaluacion_id"],
        "edad_meses_programada": 6,
        "inasistencia_registrada": False,
        "motivo_inasistencia": None,
        "cumplido_por_asistencia": False,
    }
    assert cumplido["evaluacion_id"]
    assert (vencido["codigo"], vencido["estado"], vencido["dias_vencido"]) == ("DHc1", "VENCIDO", 262)
    assert vencido["evaluacion_id"] is None


def test_cp91_agenda_de_tratamiento_y_proximo_a_vencer(cliente, escenario):
    ag = cliente.get(f"/api/ninos/{escenario['T']}/agenda").json()
    c1m = next(c for c in ag["controles"] if c["codigo"] == "C1M")
    assert (c1m["tipo"], c1m["fecha_programada"], c1m["estado"], c1m["dias_vencido"]) == (
        "CONTROL_TRATAMIENTO",
        "2026-08-01",
        "VENCIDO",
        28,
    )
    proximo = [c for c in ag["controles"] if c["proximo"]]
    assert [(c["codigo"], c["fecha_limite"]) for c in proximo] == [("DHc2", "2026-10-01")]
    assert ag["resumen"]["proximos"] == 1 and ag["resumen"]["vencidos"] == 1


def test_cp92_agenda_de_nino_inexistente_devuelve_404(cliente):
    r = cliente.get("/api/ninos/no-existe/agenda")
    assert r.status_code == 404 and r.json() == {"mensaje": "No existe el expediente solicitado.", "errores": []}


def test_cp93_nino_con_alta_no_tiene_agenda(cliente, escenario):
    ag = cliente.get(f"/api/ninos/{escenario['A']}/agenda").json()
    assert ag["aplica"] is False and "alta" in ag["motivo"]
    assert ag["controles"] == [] and ag["resumen"]["total"] == 0 and ag["resumen"]["proximo_control"] is None


def test_cp94_registrar_un_control_cumple_el_pendiente_vigente_pero_no_rescata_los_vencidos(cliente, escenario):
    antes = cliente.get(f"/api/ninos/{escenario['V']}/agenda").json()["resumen"]
    r = cliente.post(
        f"/api/ninos/{escenario['V']}/evaluaciones",
        json={"fecha": "2026-09-27", "hemoglobina_observada": 13.5, "peso_kg": 11, "talla_cm": 82},
    )
    assert r.status_code == 201
    despues = cliente.get(f"/api/ninos/{escenario['V']}/agenda").json()["resumen"]
    assert (despues["cumplidos"], despues["pendientes"]) == (antes["cumplidos"] + 1, antes["pendientes"] - 1)
    assert despues["vencidos"] == antes["vencidos"] == 3  # los controles ya vencidos quedan en el historial


# --- HIST-2.2 ---------------------------------------------------------------------------------------------------------


def test_cp95_controles_vencidos_ordenados_con_los_datos_del_nino(cliente, escenario):
    r = cliente.get("/api/alertas/controles-vencidos")
    assert r.status_code == 200
    filas = r.json()
    assert [
        (f["nino"]["dni"], f["control"]["codigo"], f["control"]["dias_vencido"], f["prioridad"]) for f in filas
    ] == [
        ("70000001", "DHc1", 262, "ALTA"),
        ("70000001", "DHc2", 172, "ALTA"),
        ("70000001", "DHx", 80, "ALTA"),
        ("70000002", "C1M", 28, "ALTA"),
        ("70000003", "DHx", 8, "MEDIA"),
        ("70000004", "DHx", 7, "BAJA"),
    ]
    assert filas[3] == {
        "nino": {
            "id": escenario["T"],
            "dni": "70000002",
            "codigo_origen": None,
            "nombre_completo": "Luz Mery Quispe Rojas",
            "comunidad": "Llacuas",
            "tutor_celular": "987654321",
        },
        "control": filas[3]["control"],
        "ultima_clasificacion": "MODERADA",
        "prioridad": "ALTA",
    }
    assert (
        filas[3]["control"]["tipo"] == "CONTROL_TRATAMIENTO" and filas[3]["control"]["fecha_programada"] == "2026-08-01"
    )


def test_cp96_filtros_por_comunidad_y_prioridad(cliente, escenario):
    def dnis(**params):
        return [f["nino"]["dni"] for f in cliente.get("/api/alertas/controles-vencidos", params=params).json()]

    assert dnis(comunidad="Huaycha") == ["70000004"]
    assert dnis(comunidad="huaycha") == ["70000004"]
    assert dnis(prioridad="MEDIA") == ["70000003"]
    assert dnis(prioridad="ALTA", comunidad="Palmayoc") == ["70000001"] * 3
    assert dnis(comunidad="Inexistente") == []
    assert len(dnis(comunidad="", prioridad="")) == 6  # filtros vacíos = sin filtro


def test_cp97_prioridad_invalida_devuelve_422(cliente, escenario):
    r = cliente.get("/api/alertas/controles-vencidos", params={"prioridad": "URGENTE"})
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "prioridad"


def test_cp98_resumen_de_alertas(cliente, escenario):
    r = cliente.get("/api/alertas/resumen")
    assert r.status_code == 200
    assert r.json() == {
        "total_vencidos": 6,
        "por_prioridad": {"ALTA": 4, "MEDIA": 1, "BAJA": 1},
        "ninos_con_vencidos": 4,
        "proximos_7_dias": 1,
    }


def test_cp99_sin_ninos_las_alertas_estan_vacias(cliente):
    assert cliente.get("/api/alertas/controles-vencidos").json() == []
    assert cliente.get("/api/alertas/resumen").json() == {
        "total_vencidos": 0,
        "por_prioridad": {"ALTA": 0, "MEDIA": 0, "BAJA": 0},
        "ninos_con_vencidos": 0,
        "proximos_7_dias": 0,
    }


def test_cp100_listado_de_seguimiento_usa_los_controles_vencidos(cliente, escenario):
    filas = {f["dni"]: f for f in cliente.get("/api/ninos").json()}
    assert "70000005" not in filas  # con alta
    assert (filas["70000001"]["control_atrasado"], filas["70000001"]["controles_vencidos"]) == (True, 3)
    assert (filas["70000002"]["control_atrasado"], filas["70000002"]["controles_vencidos"]) == (True, 1)
    # Registrar un niño al día no lo marca como atrasado (antes bastaba con superar 30 días sin control).
    registrar(cliente, "70000006", "2026-01-28", "2026-09-20", "Palmayoc", 13.5)
    fila = {f["dni"]: f for f in cliente.get("/api/ninos").json()}["70000006"]
    assert (fila["control_atrasado"], fila["controles_vencidos"], fila["dias_desde_ultimo_control"]) == (False, 0, 8)
    todos = cliente.get("/api/ninos", params={"estado": ""}).json()
    assert {f["dni"] for f in todos} >= {"70000005"}  # sin filtro de estado también se listan los de alta
    alta = next(f for f in todos if f["dni"] == "70000005")
    assert (alta["control_atrasado"], alta["controles_vencidos"]) == (False, 0)


def test_cp101_openapi_documenta_los_endpoints_nuevos(cliente):
    doc = cliente.get("/openapi.json").json()
    assert doc["info"]["version"] == "2.0.0-inc2"
    for ruta in ("/api/ninos/{nino_id}/agenda", "/api/alertas/controles-vencidos", "/api/alertas/resumen"):
        assert ruta in doc["paths"]
    esquemas = doc["components"]["schemas"]
    assert {"AgendaSalida", "ControlSalida", "AlertaSalida", "ResumenAlertasSalida"} <= set(esquemas)
    assert "controles_vencidos" in esquemas["FilaSeguimiento"]["properties"]


# --- Regresión de defectos (DEF-03 a DEF-07) ---------------------------------------------------------------------------


def test_cp102_def03_reporte_con_fechas_extremas_devuelve_422_y_no_500(cliente):
    for desde, hasta in (("2026-01-01", "9999-12-31"), ("0001-01-01", "2026-01-01")):
        for formato in ("json", "csv"):
            r = cliente.get("/api/reportes/periodo", params={"desde": desde, "hasta": hasta, "formato": formato})
            assert r.status_code == 422, (desde, hasta, formato)
    assert (
        cliente.get("/api/reportes/periodo", params={"desde": "2026-09-01", "hasta": "2026-09-30"}).status_code == 200
    )


def test_cp103_def04_dni_y_celular_solo_digitos_ascii_y_coincidencia_completa(cliente):
    r = cliente.post("/api/ninos", json=cuerpo_registro(dni="7123456٤"))
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "dni"
    r = cliente.post("/api/ninos", json=cuerpo_registro(tutor_celular="987654321\n"))
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "tutor_celular"
    ok = cliente.post("/api/ninos", json=cuerpo_registro(dni=" 71234567 "))
    assert ok.status_code == 201 and ok.json()["dni"] == "71234567"
    assert cliente.patch(f"/api/ninos/{ok.json()['id']}", json={"tutor_celular": "987654321\n"}).status_code == 422


@pytest.mark.parametrize("altitud", ["NaN", "Infinity", "-Infinity", "99999", "-5"])
def test_cp104_def05_vista_previa_rechaza_altitudes_invalidas(cliente, altitud):
    cuerpo = (
        '{"fecha_nacimiento":"2025-01-01","altitud_m":' + altitud + ","
        '"evaluacion":{"fecha":"2026-09-20","hemoglobina_observada":12,"peso_kg":8,"talla_cm":70}}'
    )
    r = cliente.post("/api/validaciones/evaluacion", content=cuerpo, headers={"content-type": "application/json"})
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "altitud_m"


def test_cp104_def05_vista_previa_rechaza_fechas_de_nacimiento_absurdas(cliente):
    evaluacion = {"fecha": "2026-09-20", "hemoglobina_observada": 12, "peso_kg": 8, "talla_cm": 70}
    for nacimiento in ("0001-01-01", "2020-01-01"):
        r = cliente.post(
            "/api/validaciones/evaluacion",
            json={"fecha_nacimiento": nacimiento, "altitud_m": 3000, "evaluacion": evaluacion},
        )
        assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "fecha_nacimiento"


def test_cp105_def06_textos_con_largo_mayor_al_de_la_base_devuelven_422(cliente):
    for campo, largo in (("nombres", 81), ("comunidad", 81), ("tutor_nombre", 121)):
        r = cliente.post("/api/ninos", json=cuerpo_registro(**{campo: "x" * largo}))
        assert r.status_code == 422, campo
        assert r.json()["errores"][0] == {"campo": campo, "mensaje": f"No puede superar {largo - 1} caracteres."}
    assert cliente.post("/api/ninos", json=cuerpo_registro(comunidad="x" * 80)).status_code == 201


def test_cp106_def07_la_busqueda_trata_los_comodines_como_texto(cliente):
    registrar(cliente, "70000001", "2025-03-10", "2025-09-12", "Palmayoc", 13.5)
    registrar(cliente, "70000002", "2025-03-10", "2025-09-12", "San_Pedro", 13.5)
    registrar(cliente, "70000003", "2025-03-10", "2025-09-12", "Cien%Cumbres", 13.5)

    def dnis(q):
        return sorted(f["dni"] for f in cliente.get("/api/ninos", params={"q": q}).json())

    assert dnis("%") == ["70000003"] and dnis("_") == ["70000002"]
    assert dnis("n_p") == ["70000002"] and dnis("n%x") == []
    assert dnis("\\") == [] and dnis("san_") == ["70000002"] and dnis("palma") == ["70000001"]
    assert len(dnis("7000000")) == 3  # el DNI también se busca por coincidencia parcial


def test_cp107_nan_o_infinito_en_la_evaluacion_se_rechazan_con_mensaje_claro(cliente):
    cuerpo = cuerpo_registro()
    texto = json.dumps(cuerpo).replace('"hemoglobina_observada": 12.4', '"hemoglobina_observada": NaN')
    assert "NaN" in texto
    r = cliente.post("/api/ninos", content=texto, headers={"content-type": "application/json"})
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "hemoglobina_observada"


def test_cp115_def08_registro_simultaneo_del_mismo_dni_devuelve_409_y_no_500(cliente):
    """DEF-08: si la comprobación previa de DNI no ve al otro registro (carrera), la restricción UNIQUE debe dar 409."""
    cuerpo = cuerpo_registro(dni="70000099")
    assert cliente.post("/api/ninos", json=cuerpo).status_code == 201
    repo = cliente.app.state.repositorio
    original = repo.obtener_por_dni
    consultas = []

    def ciego_en_la_primera_consulta(dni):  # simula que el otro hilo aún no había confirmado su inserción
        consultas.append(dni)
        return None if len(consultas) == 1 else original(dni)

    repo.obtener_por_dni = ciego_en_la_primera_consulta
    try:
        r = cliente.post("/api/ninos", json=cuerpo)
    finally:
        repo.obtener_por_dni = original
    assert r.status_code == 409 and "70000099" in r.json()["mensaje"]
    assert len([f for f in cliente.get("/api/ninos", params={"q": "70000099"}).json() if f["dni"] == "70000099"]) == 1
