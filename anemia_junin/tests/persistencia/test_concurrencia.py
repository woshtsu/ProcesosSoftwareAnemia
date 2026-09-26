"""
Prueba de concurrencia SQLite — PMV Anemia Junín.

Regresión del defecto hallado con Locust (20 usuarios): dos POST de dosaje
simultáneos devolvían 500 «database is locked» porque la transacción empezaba
con BEGIN diferido (lectura) y luego intentaba escribir. Los casos de uso de
escritura usan ahora BEGIN IMMEDIATE.
"""

from __future__ import annotations

import threading
from datetime import date, datetime

_NINO = {
    "dni": "30000001", "nombres": "Lucía", "apellidos": "Torres Ccama",
    "fecha_nacimiento": "2024-02-01", "sexo": "F", "tipo_nacimiento": "TERMINO",
    "peso_kg": 9.0, "distrito": "Chilca", "altitud_msnm": 3280, "cuidador": "Rosa Ccama",
}


def test_dosajes_concurrentes_sin_bloqueos(app):
    cliente = app.test_client()
    assert cliente.post("/api/v1/ninos", json=_NINO).status_code == 201

    hilos, por_hilo = 8, 10
    codigos: list[int] = []
    candado = threading.Lock()

    def trabajador() -> None:
        c = app.test_client()
        for _ in range(por_hilo):
            r = c.post("/api/v1/ninos/30000001/dosajes", json={
                "fecha_dosaje": date.today().isoformat(), "hb_observada": 11.5,
                "altitud_msnm": 3280,
            })
            with candado:
                codigos.append(r.status_code)
            # lectura intercalada para forzar el patrón lectura→escritura
            c.get("/api/v1/ninos/30000001")

    ts = [threading.Thread(target=trabajador) for _ in range(hilos)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()

    assert codigos.count(201) == hilos * por_hilo, codigos
    historial = cliente.get("/api/v1/ninos/30000001").get_json()["data"]["historial_dosajes"]
    assert len(historial) == hilos * por_hilo


def test_unidad_de_trabajo_inmediata_revierte_ante_error(tmp_path):
    import pytest

    from anemia_junin.adapters.outbound.sqlite.migraciones import migrar
    from anemia_junin.adapters.outbound.sqlite.unidad_de_trabajo import UnidadDeTrabajo
    from anemia_junin.domain.entities import IntentoRegistro

    db = str(tmp_path / "uow.db")
    migrar(db)
    intento = IntentoRegistro.nuevo(
        operacion="CREAR_NINO", resultado="ACEPTADO", codigos_error=[],
        ahora=datetime(2026, 1, 1),
    )

    def guardar_y_fallar() -> None:
        with UnidadDeTrabajo(db, inmediata=True) as uow:
            uow.intentos.guardar(intento)
            raise RuntimeError("fallo simulado")

    with pytest.raises(RuntimeError):
        guardar_y_fallar()
    with UnidadDeTrabajo(db) as uow:
        conteo = uow.intentos.contar_en_periodo(datetime(2025, 1, 1), datetime(2027, 1, 1))
    assert conteo == {"ACEPTADO": 0, "RECHAZADO": 0}  # rollback efectivo
