"""Pruebas de integración para el parámetro opcional limite en /api/ninos y /api/alertas/controles-vencidos."""

from tests.conftest import cuerpo_registro


def _registrar_ninos(cliente, cantidad: int = 5):
    for i in range(cantidad):
        dni = f"7500000{i}"
        c = cuerpo_registro(dni=dni, nombres=f"Niño {i}")
        # Hacemos que tenga anemia para que genere controles vencidos con fecha antigua
        c["evaluacion_inicial"]["hemoglobina_observada"] = 9.0
        r = cliente.post("/api/ninos", json=c)
        assert r.status_code == 201


def test_limite_ninos_respeta_limite(cliente):
    _registrar_ninos(cliente, 5)

    # Sin límite: devuelve todos los registrados (al menos 5)
    r_todos = cliente.get("/api/ninos?estado=ACTIVO")
    assert r_todos.status_code == 200
    assert len(r_todos.json()) >= 5

    # Con límite 2: devuelve exactamente 2
    r_limite = cliente.get("/api/ninos?estado=ACTIVO&limite=2")
    assert r_limite.status_code == 200
    assert len(r_limite.json()) == 2
    # El orden debe conservarse (los 2 primeros de la lista completa)
    assert r_limite.json() == r_todos.json()[:2]


def test_limite_ninos_422_fuera_de_rango(cliente):
    assert cliente.get("/api/ninos?limite=0").status_code == 422
    assert cliente.get("/api/ninos?limite=-1").status_code == 422
    assert cliente.get("/api/ninos?limite=1001").status_code == 422
    assert cliente.get("/api/ninos?limite=abc").status_code == 422


def test_limite_controles_vencidos_respeta_limite(cliente):
    _registrar_ninos(cliente, 5)

    r_todos = cliente.get("/api/alertas/controles-vencidos")
    assert r_todos.status_code == 200
    total = len(r_todos.json())
    if total >= 2:
        r_limite = cliente.get("/api/alertas/controles-vencidos?limite=2")
        assert r_limite.status_code == 200
        assert len(r_limite.json()) == 2
        assert r_limite.json() == r_todos.json()[:2]


def test_limite_controles_vencidos_422_fuera_de_rango(cliente):
    assert cliente.get("/api/alertas/controles-vencidos?limite=0").status_code == 422
    assert cliente.get("/api/alertas/controles-vencidos?limite=-1").status_code == 422
    assert cliente.get("/api/alertas/controles-vencidos?limite=1001").status_code == 422
    assert cliente.get("/api/alertas/controles-vencidos?limite=invalido").status_code == 422
