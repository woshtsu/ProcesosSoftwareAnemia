"""CP-21 a CP-32: pruebas de integración API + persistencia SQLAlchemy (SQLite temporal)."""

from tests.conftest import cuerpo_registro


def registrar(cliente, **cambios):
    return cliente.post("/api/ninos", json=cuerpo_registro(**cambios), headers={"X-Usuario": "enf.rosa"})


def test_salud_e_interfaz(cliente):
    assert cliente.get("/api/salud").json() == {"estado": "ok"}
    assert "Anemia Junín" in cliente.get("/").text
    assert cliente.get("/sw.js").status_code == 200
    assert "/static/vendor/swagger-ui-bundle.js" in cliente.get("/docs").text
    assert cliente.get("/openapi.json").json()["info"]["version"] == "1.0.0-pmv"


def test_registro_exitoso_devuelve_expediente(cliente):
    r = registrar(cliente)
    assert r.status_code == 201
    exp = r.json()
    assert exp["dni"] == "71234567" and exp["registrado_por"] == "enf.rosa"
    assert exp["evaluaciones"][0]["hemoglobina_ajustada"] == 9.9
    assert exp["evaluaciones"][0]["clasificacion"] == "LEVE"


def test_registro_duplicado_devuelve_409(cliente):
    registrar(cliente)
    r = registrar(cliente)
    assert r.status_code == 409 and r.json()["errores"][0]["campo"] == "dni"


def test_datos_fuera_de_rango_devuelven_422_con_mensajes_en_espanol(cliente):
    cuerpo = cuerpo_registro(dni="123")
    cuerpo["evaluacion_inicial"]["hemoglobina_observada"] = 25
    r = cliente.post("/api/ninos", json=cuerpo)
    assert r.status_code == 422
    errores = {e["campo"]: e["mensaje"] for e in r.json()["errores"]}
    assert "8 dígitos" in errores["dni"] and "rango clínico válido" in errores["hemoglobina_observada"]


def test_formato_invalido_devuelve_422_en_espanol(cliente):
    cuerpo = cuerpo_registro()
    cuerpo["evaluacion_inicial"]["hemoglobina_observada"] = "abc"
    del cuerpo["nino"]["nombres"]
    r = cliente.post("/api/ninos", json=cuerpo)
    errores = {e["campo"]: e["mensaje"] for e in r.json()["errores"]}
    assert r.status_code == 422
    assert errores["hemoglobina_observada"] == "Debe ser un número." and errores["nombres"] == "Es obligatorio."


def test_consultar_expediente_por_id_y_dni(cliente):
    exp = registrar(cliente).json()
    assert cliente.get(f"/api/ninos/{exp['id']}").json()["nombres"] == "Luz Mery"
    assert cliente.get("/api/ninos/dni/71234567").json()["id"] == exp["id"]
    assert cliente.get("/api/ninos/no-existe").status_code == 404


def test_actualizar_expediente_y_registrar_control(cliente):
    exp = registrar(cliente).json()
    r = cliente.patch(f"/api/ninos/{exp['id']}", json={"comunidad": "Llacuas", "tutor_celular": "912345678"})
    assert r.status_code == 200 and r.json()["comunidad"] == "Llacuas"
    assert cliente.patch(f"/api/ninos/{exp['id']}", json={"estado": "X"}).status_code == 422
    r = cliente.post(
        f"/api/ninos/{exp['id']}/evaluaciones",
        json={"fecha": "2026-09-27", "hemoglobina_observada": 13.4, "peso_kg": 8.3, "talla_cm": 70},
    )
    assert r.status_code == 201
    evals = r.json()["evaluaciones"]
    assert len(evals) == 2 and evals[0]["fecha"] == "2026-09-27" and evals[0]["clasificacion"] == "SIN_ANEMIA"


def test_vista_previa_de_validacion(cliente):
    r = cliente.post(
        "/api/validaciones/evaluacion",
        json={
            "fecha_nacimiento": "2024-09-01",
            "altitud_m": 3550,
            "evaluacion": {"fecha": "2026-09-20", "hemoglobina_observada": 12.9, "peso_kg": 12, "talla_cm": 86},
        },
    )
    assert r.status_code == 200
    assert (
        r.json()["edad_meses"] == 24
        and r.json()["hemoglobina_ajustada"] == 10.5
        and r.json()["clasificacion"] == "LEVE"
    )


def test_listado_de_seguimiento_con_filtros(cliente):
    registrar(cliente, dni="70000001")
    registrar(cliente, dni="70000002", comunidad="Huaycha")
    assert len(cliente.get("/api/ninos").json()) == 2
    assert [f["dni"] for f in cliente.get("/api/ninos", params={"q": "huaycha"}).json()] == ["70000002"]
    assert len(cliente.get("/api/ninos", params={"clasificacion": "LEVE"}).json()) == 2
    fila = cliente.get("/api/ninos").json()[0]
    assert fila["dias_desde_ultimo_control"] == 8 and fila["control_atrasado"] is False


def test_reporte_json_y_csv(cliente):
    registrar(cliente, dni="70000001")
    r = cliente.get("/api/reportes/periodo", params={"desde": "2026-09-01", "hasta": "2026-09-30"})
    assert r.status_code == 200 and r.json()["evaluaciones_realizadas"] == 1
    csv = cliente.get("/api/reportes/periodo", params={"desde": "2026-09-01", "hasta": "2026-09-30", "formato": "csv"})
    assert csv.headers["content-type"].startswith("text/csv")
    assert "70000001" in csv.text and "hb_ajustada" in csv.text
    assert (
        cliente.get("/api/reportes/periodo", params={"desde": "2026-10-01", "hasta": "2026-09-01"}).status_code == 422
    )
