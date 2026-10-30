"""CP-263 a CP-296: integración API + SQLAlchemy (SQLite) del Incremento 3: sincronización de lo registrado sin
conexión (HIST-3.2), conflictos (HIST-3.3) y visita domiciliaria priorizada (VIS-3.5). Hoy = 28-sep-2026.
"""

import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest

from tests.conftest import cuerpo_registro
from tests.integracion.test_api_inc2 import ESCENARIO, registrar
from tests.integracion.test_autenticacion import CSRF, USER, auth_cliente, ingresar  # noqa: F401

USUARIO = {"X-Usuario": "enf.rosa"}


def uid():
    return str(uuid.uuid4())


def op(tipo, datos, minuto=0, **extra):
    return {
        "id_operacion": uid(),
        "tipo": tipo,
        "id_dispositivo": "tableta-posta-1",
        "fecha_local": f"2026-09-27T08:{minuto:02d}:00-05:00",
        "datos": datos,
        **extra,
    }


def sincronizar(cliente, *operaciones, usuario="enf.rosa"):
    r = cliente.post("/api/sincronizacion", json={"operaciones": list(operaciones)}, headers={"X-Usuario": usuario})
    assert r.status_code == 200, r.text
    return r.json()


def resultados(cuerpo):
    return [x["resultado"] for x in cuerpo["resultados"]]


def datos_registro(dni="72000001", hb=12.4, fecha="2026-09-20", **cambios):
    cuerpo = cuerpo_registro(dni=dni, **cambios)
    cuerpo["evaluacion_inicial"].update(fecha=fecha, hemoglobina_observada=hb)
    return cuerpo


def evaluacion(hb=11.0, fecha="2026-09-25"):
    return {"fecha": fecha, "hemoglobina_observada": hb, "peso_kg": 8.4, "talla_cm": 70.0}


def visita(**cambios):
    return {
        "fecha": "2026-09-22",
        "resultado": "REALIZADA",
        "consume_suplemento": "SI",
        "observaciones": "Bien",
    } | cambios


def contar(cliente):
    repo = cliente.app.state.repositorio
    ninos = cliente.get("/api/ninos?estado=").json()
    evaluaciones = sum(len(cliente.get(f"/api/ninos/{n['id']}").json()["evaluaciones"]) for n in ninos)
    return len(ninos), evaluaciones, repo.contar_operaciones()


# --- HIST-3.2: lote mixto e idempotencia --------------------------------------------------------------------------------


def lote_mixto(cliente):
    existente = registrar(
        cliente, **ESCENARIO["V"]
    )  # niño del servidor para la asistencia, la visita y otra evaluación
    return existente, [
        op("REGISTRAR_NINO", datos_registro(), 1, id_cliente="tmp-1"),
        op("REGISTRAR_EVALUACION", evaluacion(), 2, nino_ref={"id_cliente": "tmp-1"}),
        op("REGISTRAR_EVALUACION", evaluacion(hb=12.5, fecha="2026-09-26"), 3, nino_ref={"id": existente}),
        op(
            "REGISTRAR_ASISTENCIA",
            {
                "codigo": "DHc1",
                "fecha_programada": "2025-12-10",
                "estado": "NO_ASISTIO",
                "motivo": "Viaje de la familia",
            },
            4,
            nino_ref={"id": existente},
        ),
        op("REGISTRAR_VISITA", visita(), 5, nino_ref={"id_cliente": "tmp-1"}),
        op("REGISTRAR_EVALUACION", evaluacion(hb=25.0), 6, nino_ref={"id": existente}),  # inválida: Hb fuera de rango
    ]


def test_cp263_lote_mixto_aplica_lo_valido_rechaza_lo_invalido_y_mapea_id_cliente(cliente):
    existente, lote = lote_mixto(cliente)
    cuerpo = sincronizar(cliente, *lote)
    assert resultados(cuerpo) == ["APLICADA"] * 5 + ["RECHAZADA"]
    assert cuerpo["resumen"] == {"aplicadas": 5, "duplicadas": 0, "conflictos": 0, "rechazadas": 1}
    nino = cuerpo["resultados"][0]
    assert nino["id_cliente"] == "tmp-1" and nino["id_recurso"]
    expediente = cliente.get(f"/api/ninos/{nino['id_recurso']}").json()
    assert expediente["registrado_por"] == "enf.rosa" and len(expediente["evaluaciones"]) == 2
    assert expediente["evaluaciones"][0]["id"] == cuerpo["resultados"][1]["id_recurso"]
    rechazada = cuerpo["resultados"][5]
    assert rechazada["errores"][0]["campo"] == "hemoglobina_observada" and rechazada["id_recurso"] is None
    assert cliente.get(f"/api/ninos/{existente}/asistencias").json()[0]["motivo"] == "Viaje de la familia"
    assert cliente.get(f"/api/ninos/{nino['id_recurso']}/visitas").json()[0]["observaciones"] == "Bien"


def test_cp264_reenviar_el_mismo_lote_responde_duplicada_y_no_agrega_filas(cliente):
    _, lote = lote_mixto(cliente)
    lote = lote[:5]  # solo operaciones válidas
    primera = sincronizar(cliente, *lote)
    antes = contar(cliente)
    segunda = sincronizar(cliente, *lote)
    assert resultados(segunda) == ["DUPLICADA"] * 5
    assert segunda["resumen"] == {"aplicadas": 0, "duplicadas": 5, "conflictos": 0, "rechazadas": 0}
    assert [x["resultado_original"] for x in segunda["resultados"]] == ["APLICADA"] * 5
    assert [x["id_recurso"] for x in segunda["resultados"]] == [x["id_recurso"] for x in primera["resultados"]]
    assert segunda["resultados"][0]["id_cliente"] == "tmp-1"
    assert contar(cliente) == antes


def test_cp264b_el_mismo_id_operacion_enviado_a_la_vez_se_aplica_una_sola_vez(cliente):
    """Un reintento tras un tiempo de espera puede llegar mientras el primer envío sigue en curso: la evaluación (que la
    base no protege con una restricción propia) no debe quedar duplicada."""
    existente = registrar(cliente, **ESCENARIO["V"])
    una = op("REGISTRAR_EVALUACION", evaluacion(), 1, nino_ref={"id": existente})
    antes = len(cliente.get(f"/api/ninos/{existente}").json()["evaluaciones"])
    repo = cliente.app.state.repositorio
    agregar = repo.agregar_evaluacion

    def agregar_lento(evaluacion):  # ensancha la ventana entre «no existe» y «guardada»
        time.sleep(0.02)
        return agregar(evaluacion)

    repo.agregar_evaluacion = agregar_lento
    with ThreadPoolExecutor(max_workers=6) as pool:
        respuestas = list(pool.map(lambda _: sincronizar(cliente, una), range(6)))
    todas = [x for r in respuestas for x in resultados(r)]
    assert sorted(todas) == ["APLICADA"] + ["DUPLICADA"] * 5
    assert len(cliente.get(f"/api/ninos/{existente}").json()["evaluaciones"]) == antes + 1


def test_cp265_las_operaciones_se_procesan_por_fecha_local_y_la_respuesta_conserva_el_orden_recibido(cliente):
    nino = op("REGISTRAR_NINO", datos_registro(), 5, id_cliente="tmp-1")
    control = op("REGISTRAR_EVALUACION", evaluacion(), 9, nino_ref={"id_cliente": "tmp-1"})
    cuerpo = sincronizar(cliente, control, nino)  # llegan al revés
    assert [x["id_operacion"] for x in cuerpo["resultados"]] == [control["id_operacion"], nino["id_operacion"]]
    assert resultados(cuerpo) == ["APLICADA", "APLICADA"]


def test_cp266_un_id_cliente_ya_sincronizado_se_resuelve_en_un_lote_posterior(cliente):
    sincronizar(cliente, op("REGISTRAR_NINO", datos_registro(), 1, id_cliente="tmp-1"))
    cuerpo = sincronizar(cliente, op("REGISTRAR_VISITA", visita(), 2, nino_ref={"id_cliente": "tmp-1"}))
    assert resultados(cuerpo) == ["APLICADA"]


def test_cp267_limites_del_lote(cliente):
    def post(operaciones):
        return cliente.post("/api/sincronizacion", json={"operaciones": operaciones}, headers=USUARIO)

    r = post([])
    assert r.status_code == 422 and r.json()["errores"][0] == {
        "campo": "operaciones",
        "mensaje": "No alcanza el largo o la cantidad mínima requerida.",
    }
    ids = [op("REGISTRAR_VISITA", visita(), nino_ref={"id": "no-existe"}) for _ in range(201)]
    r = post(ids)
    assert r.status_code == 422 and "máxima" in r.json()["errores"][0]["mensaje"]
    r = post(ids[:200])  # 200 es el máximo permitido
    assert r.status_code == 200 and r.json()["resumen"]["rechazadas"] == 200
    assert post([{**ids[0], "id_operacion": "no-es-uuid"}]).status_code == 422
    assert post([{**ids[0], "fecha_local": "ayer"}]).status_code == 422
    assert post([{k: v for k, v in ids[0].items() if k != "datos"}]).status_code == 422
    assert cliente.post("/api/sincronizacion", json={}, headers=USUARIO).status_code == 422


def test_cp268_una_operacion_malformada_se_rechaza_sin_afectar_a_las_demas(cliente):
    nino = registrar(cliente, **ESCENARIO["V"])
    cuerpo = sincronizar(
        cliente,
        op("BORRAR_TODO", {}, 1, nino_ref={"id": nino}),
        op("REGISTRAR_VISITA", {"fecha": "hoy", "resultado": 4}, 2, nino_ref={"id": nino}),
        op("REGISTRAR_VISITA", visita(), 3),  # sin nino_ref
        op("REGISTRAR_VISITA", visita(), 4, nino_ref={"id": nino}),
    )
    assert resultados(cuerpo) == ["RECHAZADA", "RECHAZADA", "RECHAZADA", "APLICADA"]
    assert cuerpo["resultados"][0]["errores"] == [{"campo": "tipo", "mensaje": "Tipo de operación desconocido."}]
    assert [e["campo"] for e in cuerpo["resultados"][1]["errores"]] == ["fecha", "resultado"]
    assert cuerpo["resultados"][2]["errores"][0]["campo"] == "nino_ref"
    assert cliente.app.state.repositorio.contar_operaciones() == 1  # solo la aplicada deja huella


# --- HIST-3.3: conflictos ---------------------------------------------------------------------------------------------


def test_cp269_conflicto_de_evaluacion_se_lista_y_se_resuelve_aplicando_el_dato_del_dispositivo(cliente):
    nino = registrar(cliente, **ESCENARIO["V"])
    sincronizar(cliente, op("REGISTRAR_EVALUACION", evaluacion(hb=12.0), 1, nino_ref={"id": nino}))
    cuerpo = sincronizar(cliente, op("REGISTRAR_EVALUACION", evaluacion(hb=7.0), 2, nino_ref={"id": nino}))
    r = cuerpo["resultados"][0]
    assert r["resultado"] == "CONFLICTO" and r["id_conflicto"] and "12.0" in r["mensaje"]
    pendientes = cliente.get("/api/sincronizacion/conflictos?estado=PENDIENTE").json()
    assert len(pendientes) == 1
    c = pendientes[0]
    assert (c["id"], c["tipo"], c["nino_id"], c["estado"], c["resolucion"]) == (
        r["id_conflicto"],
        "REGISTRAR_EVALUACION",
        nino,
        "PENDIENTE",
        None,
    )
    assert c["datos_cliente"]["hemoglobina_observada"] == 7.0 and c["datos_servidor"]["hemoglobina_observada"] == 12.0
    res = cliente.post(
        f"/api/sincronizacion/conflictos/{c['id']}/resolver", json={"resolucion": "APLICAR_CLIENTE"}, headers=USUARIO
    )
    assert res.status_code == 200
    assert (res.json()["estado"], res.json()["resolucion"], res.json()["resuelto_por"]) == (
        "RESUELTO",
        "APLICAR_CLIENTE",
        "enf.rosa",
    )
    guardada = next(e for e in cliente.get(f"/api/ninos/{nino}").json()["evaluaciones"] if e["fecha"] == "2026-09-25")
    assert (guardada["hemoglobina_observada"], guardada["clasificacion"]) == (7.0, "SEVERA")
    assert cliente.get("/api/sincronizacion/conflictos?estado=PENDIENTE").json() == []
    assert len(cliente.get("/api/sincronizacion/conflictos?estado=RESUELTO").json()) == 1
    assert len(cliente.get("/api/sincronizacion/conflictos").json()) == 1


def test_cp270_conflicto_de_nino_por_dni_con_datos_distintos_y_resolucion_conservar_servidor(cliente):
    sincronizar(cliente, op("REGISTRAR_NINO", datos_registro(), 1, id_cliente="tmp-A"))
    cuerpo = sincronizar(cliente, op("REGISTRAR_NINO", datos_registro(comunidad="Llacuas"), 2, id_cliente="tmp-B"))
    r = cuerpo["resultados"][0]
    assert r["resultado"] == "CONFLICTO" and r["id_cliente"] is None and "comunidad" in r["mensaje"]
    res = cliente.post(
        f"/api/sincronizacion/conflictos/{r['id_conflicto']}/resolver",
        json={"resolucion": "CONSERVAR_SERVIDOR"},
        headers=USUARIO,
    )
    assert res.status_code == 200 and res.json()["resolucion"] == "CONSERVAR_SERVIDOR"
    assert cliente.get("/api/ninos/dni/72000001").json()["comunidad"] == "Palmayoc"
    assert (
        sincronizar(cliente, op("REGISTRAR_VISITA", visita(), 3, nino_ref={"id_cliente": "tmp-B"}))["resumen"][
            "aplicadas"
        ]
        == 1
    )


def test_cp271_aplicar_el_cliente_sobre_la_identidad_del_nino_se_rechaza_con_422(cliente):
    sincronizar(cliente, op("REGISTRAR_NINO", datos_registro(), 1, id_cliente="tmp-A"))
    r = sincronizar(cliente, op("REGISTRAR_NINO", datos_registro(nombres="Otra"), 2, id_cliente="tmp-B"))["resultados"][
        0
    ]
    res = cliente.post(
        f"/api/sincronizacion/conflictos/{r['id_conflicto']}/resolver",
        json={"resolucion": "APLICAR_CLIENTE"},
        headers=USUARIO,
    )
    assert res.status_code == 422 and res.json()["errores"][0]["campo"] == "resolucion"
    assert "identidad" in res.json()["errores"][0]["mensaje"]
    assert cliente.get("/api/sincronizacion/conflictos?estado=PENDIENTE").json()[0]["estado"] == "PENDIENTE"


def test_cp272_errores_al_resolver_un_conflicto(cliente):
    nino = registrar(cliente, **ESCENARIO["V"])
    sincronizar(cliente, op("REGISTRAR_VISITA", visita(), 1, nino_ref={"id": nino}))
    c = sincronizar(
        cliente,
        op(
            "REGISTRAR_VISITA",
            visita(resultado="RECHAZADA", consume_suplemento="DESCONOCIDO"),
            2,
            nino_ref={"id": nino},
        ),
    )["resultados"][0]
    ruta = f"/api/sincronizacion/conflictos/{c['id_conflicto']}/resolver"
    assert cliente.post(ruta, json={"resolucion": "BORRAR"}, headers=USUARIO).status_code == 422
    assert cliente.post(ruta, json={}, headers=USUARIO).status_code == 422
    assert (
        cliente.post(
            "/api/sincronizacion/conflictos/no-existe/resolver", json={"resolucion": "DESCARTAR"}, headers=USUARIO
        ).status_code
        == 404
    )
    assert cliente.post(ruta, json={"resolucion": "DESCARTAR"}, headers=USUARIO).status_code == 200
    de_nuevo = cliente.post(ruta, json={"resolucion": "APLICAR_CLIENTE"}, headers=USUARIO)
    assert de_nuevo.status_code == 409 and de_nuevo.json()["errores"][0]["campo"] == "estado"
    assert cliente.get("/api/sincronizacion/conflictos?estado=ABIERTO").status_code == 422
    assert cliente.get(f"/api/ninos/{nino}/visitas").json()[0]["resultado"] == "REALIZADA"  # DESCARTAR no cambió nada


def test_cp273_conflicto_de_asistencia_y_visita_aplicando_el_dato_del_dispositivo(cliente):
    nino = registrar(cliente, **ESCENARIO["V"])
    asistencia = {"codigo": "DHc1", "fecha_programada": "2025-12-10", "estado": "ASISTIO"}
    sincronizar(
        cliente,
        op("REGISTRAR_ASISTENCIA", asistencia, 1, nino_ref={"id": nino}),
        op("REGISTRAR_VISITA", visita(), 2, nino_ref={"id": nino}),
    )
    cuerpo = sincronizar(
        cliente,
        op(
            "REGISTRAR_ASISTENCIA",
            {**asistencia, "estado": "NO_ASISTIO", "motivo": "Enfermó el niño"},
            3,
            nino_ref={"id": nino},
        ),
        op(
            "REGISTRAR_VISITA",
            visita(resultado="NO_ENCONTRADO", consume_suplemento="DESCONOCIDO"),
            4,
            nino_ref={"id": nino},
        ),
    )
    assert resultados(cuerpo) == ["CONFLICTO", "CONFLICTO"]
    for x in cuerpo["resultados"]:
        res = cliente.post(
            f"/api/sincronizacion/conflictos/{x['id_conflicto']}/resolver",
            json={"resolucion": "APLICAR_CLIENTE"},
            headers=USUARIO,
        )
        assert res.status_code == 200
    assert cliente.get(f"/api/ninos/{nino}/asistencias").json()[0]["estado"] == "NO_ASISTIO"
    assert cliente.get(f"/api/ninos/{nino}/visitas").json()[0]["resultado"] == "NO_ENCONTRADO"


def test_cp274_reenviar_una_operacion_en_conflicto_devuelve_el_mismo_conflicto(cliente):
    nino = registrar(cliente, **ESCENARIO["V"])
    sincronizar(cliente, op("REGISTRAR_EVALUACION", evaluacion(hb=12.0), 1, nino_ref={"id": nino}))
    conflictiva = op("REGISTRAR_EVALUACION", evaluacion(hb=7.0), 2, nino_ref={"id": nino})
    primero = sincronizar(cliente, conflictiva)["resultados"][0]
    segundo = sincronizar(cliente, conflictiva)["resultados"][0]
    assert (segundo["resultado"], segundo["resultado_original"]) == ("DUPLICADA", "CONFLICTO")
    assert segundo["id_conflicto"] == primero["id_conflicto"]
    assert len(cliente.get("/api/sincronizacion/conflictos").json()) == 1


# --- Autenticación -----------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "metodo, ruta, cuerpo",
    [
        ("post", "/api/sincronizacion", {"operaciones": []}),
        ("get", "/api/sincronizacion/conflictos", None),
        ("post", "/api/sincronizacion/conflictos/x/resolver", {"resolucion": "DESCARTAR"}),
        ("get", "/api/visitas/priorizadas", None),
        ("get", "/api/ninos/x/visitas", None),
        ("post", "/api/ninos/x/visitas", visita()),
    ],
)
def test_cp275_los_endpoints_del_incremento_3_exigen_sesion(auth_cliente, metodo, ruta, cuerpo):  # noqa: F811
    c, calls, _ = auth_cliente
    r = getattr(c, metodo)(ruta, **({"json": cuerpo} if cuerpo is not None else {}), headers=CSRF)
    assert r.status_code == 401 and r.headers["Cache-Control"] == "no-store"


def test_cp276_con_sesion_el_registrado_por_es_el_usuario_verificado_y_se_exige_el_encabezado_csrf(auth_cliente):  # noqa: F811
    c, _, _ = auth_cliente
    ingresar(c)
    cuerpo = {"operaciones": [op("REGISTRAR_NINO", datos_registro(), 1, id_cliente="tmp-1")]}
    assert c.post("/api/sincronizacion", json=cuerpo).status_code == 403  # sin X-CSRF-Protection
    r = c.post("/api/sincronizacion", json=cuerpo, headers={**CSRF, "X-Usuario": "suplantado"})
    assert r.status_code == 200 and r.json()["resumen"]["aplicadas"] == 1
    assert c.get("/api/ninos/dni/72000001").json()["registrado_por"] == USER["id"]


# --- VIS-3.5: visitas -------------------------------------------------------------------------------------------------


def test_cp277_registrar_y_consultar_visitas_de_un_nino(cliente):
    nino = registrar(cliente, **ESCENARIO["T"])
    r = cliente.post(f"/api/ninos/{nino}/visitas", json=visita(fecha="2026-09-20"), headers=USUARIO)
    assert r.status_code == 201
    v = r.json()
    assert (v["nino_id"], v["resultado"], v["consume_suplemento"], v["registrado_por"]) == (
        nino,
        "REALIZADA",
        "SI",
        "enf.rosa",
    )
    cliente.post(
        f"/api/ninos/{nino}/visitas",
        json={"fecha": "2026-09-25", "resultado": "NO_ENCONTRADO"},
        headers={"X-Usuario": "tec.juan"},
    )
    lista = cliente.get(f"/api/ninos/{nino}/visitas").json()
    assert [(x["fecha"], x["consume_suplemento"], x["registrado_por"]) for x in lista] == [
        ("2026-09-25", "DESCONOCIDO", "tec.juan"),
        ("2026-09-20", "SI", "enf.rosa"),
    ]


@pytest.mark.parametrize(
    "cambios, campo",
    [
        ({"fecha": "2026-09-29"}, "fecha"),
        ({"fecha": "ayer"}, "fecha"),
        ({"resultado": "TAL VEZ"}, "resultado"),
        ({"resultado": "NO_ENCONTRADO", "consume_suplemento": "SI"}, "consume_suplemento"),
        ({"consume_suplemento": "QUIZA"}, "consume_suplemento"),
        ({"observaciones": "x" * 501}, "observaciones"),
    ],
)
def test_cp278_datos_invalidos_de_visita_devuelven_422_por_campo(cliente, cambios, campo):
    nino = registrar(cliente, **ESCENARIO["T"])
    r = cliente.post(f"/api/ninos/{nino}/visitas", json=visita(**cambios), headers=USUARIO)
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == campo


def test_cp279_visita_repetida_el_mismo_dia_niño_inexistente_y_observaciones_de_500(cliente):
    nino = registrar(cliente, **ESCENARIO["T"])
    assert (
        cliente.post(f"/api/ninos/{nino}/visitas", json=visita(observaciones="x" * 500), headers=USUARIO).status_code
        == 201
    )
    r = cliente.post(f"/api/ninos/{nino}/visitas", json=visita(), headers=USUARIO)
    assert r.status_code == 409 and r.json()["errores"][0]["campo"] == "fecha"
    assert cliente.post("/api/ninos/no-existe/visitas", json=visita(), headers=USUARIO).status_code == 404
    assert cliente.get("/api/ninos/no-existe/visitas").status_code == 404


def priorizadas(cliente, **params):
    r = cliente.get("/api/visitas/priorizadas", params=params)
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture
def con_tratamientos(cliente):
    """T: anemia con control de tratamiento vencido (Llacuas); V y A no tienen anemia (hb 13.5) o están de alta."""
    ids = {k: registrar(cliente, **d) for k, d in ESCENARIO.items()}
    cliente.patch(f"/api/ninos/{ids['A']}", json={"estado": "ALTA"})
    return ids


def test_cp280_la_lista_priorizada_solo_trae_ninos_en_tratamiento_con_su_puntaje_explicado(cliente, con_tratamientos):
    lista = priorizadas(cliente)
    assert [i["nino"]["id"] for i in lista] == [con_tratamientos["T"]]
    t = lista[0]
    assert t["posicion"] == 1 and t["nino"]["comunidad"] == "Llacuas" and t["establecimiento"] == "P. S. Chongos Alto"
    assert t["ultima_clasificacion"] == "MODERADA" and t["dias_control_vencido"] == 28
    assert (t["inasistencias_recientes"], t["ultima_visita"], t["dias_desde_ultima_visita"]) == (0, None, None)
    assert [(c["codigo"], c["valor"], c["puntos"], c["maximo"]) for c in t["componentes"]] == [
        ("SEVERIDAD", "MODERADA", 25.0, 40.0),
        ("CONTROL_VENCIDO", "28 días", 14.0, 30.0),
        ("INASISTENCIAS", "0", 0.0, 15.0),
        ("ULTIMA_VISITA", "sin visitas", 15.0, 15.0),
    ]
    assert t["puntaje"] == 54.0 == sum(c["puntos"] for c in t["componentes"])


def test_cp281_una_inasistencia_sube_el_puntaje_y_una_visita_reciente_lo_baja(cliente, con_tratamientos):
    nino = con_tratamientos["T"]
    base = priorizadas(cliente)[0]["puntaje"]
    r = cliente.post(
        f"/api/ninos/{nino}/controles/C1M/asistencia",
        json={"fecha_programada": "2026-08-01", "estado": "NO_ASISTIO", "motivo": "Viaje"},
        headers=USUARIO,
    )
    assert r.status_code == 201
    con_inasistencia = priorizadas(cliente)[0]
    assert (con_inasistencia["inasistencias_recientes"], con_inasistencia["puntaje"]) == (1, base + 5.0)
    cliente.post(f"/api/ninos/{nino}/visitas", json=visita(fecha="2026-09-28"), headers=USUARIO)
    con_visita = priorizadas(cliente)[0]
    assert (con_visita["ultima_visita"], con_visita["dias_desde_ultima_visita"]) == ("2026-09-28", 0)
    assert con_visita["puntaje"] == base + 5.0 - 15.0


def test_cp282_filtros_y_limite_de_la_lista_priorizada(cliente, con_tratamientos):
    otro = registrar(
        cliente, dni="70000099", nacimiento="2025-09-01", evaluacion="2026-06-01", comunidad="Huaycha", hb=8.0
    )
    cliente.patch(f"/api/ninos/{otro}", json={"tutor_nombre": "Rosa Pérez"})
    todos = priorizadas(cliente)
    assert [i["posicion"] for i in todos] == [1, 2] and todos[0]["puntaje"] >= todos[1]["puntaje"]
    assert todos[0]["nino"]["id"] == otro  # anemia moderada/severa pesa más
    assert [i["nino"]["id"] for i in priorizadas(cliente, limite=1)] == [otro]
    assert len(priorizadas(cliente, establecimiento="p. s. chongos alto")) == 2
    assert priorizadas(cliente, establecimiento="Otro establecimiento") == []
    assert len(priorizadas(cliente, establecimiento="")) == 2


@pytest.mark.parametrize("limite", ["0", "201", "-1", "abc"])
def test_cp283_limite_invalido_de_la_lista_priorizada(cliente, limite):
    r = cliente.get("/api/visitas/priorizadas", params={"limite": limite})
    assert r.status_code == 422 and r.json()["errores"][0]["campo"] == "limite"


def test_cp284_una_visita_que_llega_por_la_cola_cuenta_en_la_priorizacion(cliente, con_tratamientos):
    nino = con_tratamientos["T"]
    base = priorizadas(cliente)[0]["puntaje"]
    sincronizar(cliente, op("REGISTRAR_VISITA", visita(fecha="2026-09-28"), 1, nino_ref={"id": nino}))
    assert priorizadas(cliente)[0]["puntaje"] == base - 15.0


# --- Contrato ----------------------------------------------------------------------------------------------------------


def test_cp285_el_contrato_openapi_publica_los_endpoints_del_incremento_3(cliente):
    doc = cliente.get("/openapi.json").json()
    for ruta in (
        "/api/sincronizacion",
        "/api/sincronizacion/conflictos",
        "/api/sincronizacion/conflictos/{conflicto_id}/resolver",
        "/api/visitas/priorizadas",
        "/api/ninos/{nino_id}/visitas",
    ):
        assert ruta in doc["paths"]
    assert doc["info"]["version"] == "4.0.0-inc4"
    assert doc["paths"]["/api/sincronizacion"]["post"]["responses"]["200"]
