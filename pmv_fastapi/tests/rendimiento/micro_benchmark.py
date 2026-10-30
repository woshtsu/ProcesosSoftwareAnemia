"""Micro-benchmark de latencia (p50/p95) del listado de seguimiento y de las alertas, en proceso y sin red.

Uso (desde la raíz del proyecto):
    python -m tests.rendimiento.micro_benchmark --ninos 1000 --repeticiones 40

Crea una base SQLite temporal con N niños sintéticos (semilla fija, mismas fechas siempre) y mide, con TestClient,
los endpoints que calculan la agenda de cada niño activo. Sirve para comparar versiones del código (antes/después de
una optimización) en la misma máquina; no reemplaza la prueba de carga con Locust.
"""

import argparse
import random
import statistics
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import crear_app

HOY = date(2026, 9, 28)
ENDPOINTS = ("/api/ninos", "/api/alertas/controles-vencidos", "/api/alertas/resumen")


class _Reloj:
    def hoy(self) -> date:
        return HOY


def _meses_atras(fecha: date, meses: int) -> date:
    indice = fecha.year * 12 + fecha.month - 1 - meses
    return date(indice // 12, indice % 12 + 1, min(fecha.day, 28))


def poblar(app, cantidad: int, semilla: int = 2026) -> None:
    from app.application.servicio_expediente import ServicioExpediente

    azar = random.Random(semilla)
    servicio = ServicioExpediente(app.state.repositorio, _Reloj())
    comunidades = ["Palmayoc", "Chongos Alto", "Llacuas", "Huaycha"]
    for i in range(cantidad):
        edad = azar.randint(8, 50)
        nacimiento = _meses_atras(HOY, edad)
        primera = HOY - timedelta(days=azar.randint(10, 400))
        primera = max(primera, nacimiento + timedelta(days=200))
        datos = dict(
            dni=f"{70000000 + i}",
            nombres="Niño",
            apellidos=f"Sintético {i}",
            sexo="F" if i % 2 else "M",
            fecha_nacimiento=nacimiento,
            establecimiento="P. S. Chongos Alto",
            distrito="Chongos Alto",
            comunidad=comunidades[i % 4],
            altitud_m=3550,
            tutor_nombre="Tutor Sintético",
            tutor_celular="987654321",
        )
        hb = azar.choice([11.9, 12.4, 13.0, 14.0, 15.0, 15.6])  # observada; con 3 550 m hay casos con y sin anemia
        evaluacion = dict(fecha=primera, hemoglobina_observada=hb, peso_kg=9.0, talla_cm=75.0)
        nino = servicio.registrar_nino(datos, evaluacion, "benchmark")
        if azar.random() < 0.5:
            segunda = primera + timedelta(days=azar.randint(25, 70))
            if segunda <= HOY:
                servicio.registrar_evaluacion(nino.id, {**evaluacion, "fecha": segunda}, "benchmark")


def medir(cliente: TestClient, ruta: str, repeticiones: int) -> dict:
    tiempos = []
    cliente.get(ruta)  # calentamiento
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        r = cliente.get(ruta)
        tiempos.append((time.perf_counter() - t0) * 1000)
        assert r.status_code == 200
    tiempos.sort()
    p95 = tiempos[max(0, int(round(0.95 * len(tiempos))) - 1)]
    return {"ruta": ruta, "p50_ms": statistics.median(tiempos), "p95_ms": p95, "min_ms": tiempos[0]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ninos", type=int, default=1000)
    ap.add_argument("--repeticiones", type=int, default=40)
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        app = crear_app(f"sqlite:///{Path(tmp) / 'bench.db'}", reloj=_Reloj())
        poblar(app, args.ninos)
        with TestClient(app) as cliente:
            filas = cliente.get("/api/ninos").json()
            vencidos = cliente.get("/api/alertas/resumen").json()["total_vencidos"]
            print(f"Niños: {len(filas)} · controles vencidos: {vencidos} · repeticiones: {args.repeticiones}")
            print(f"{'endpoint':42s} {'p50 (ms)':>10s} {'p95 (ms)':>10s}")
            for ruta in ENDPOINTS:
                m = medir(cliente, ruta, args.repeticiones)
                print(f"{m['ruta']:42s} {m['p50_ms']:10.1f} {m['p95_ms']:10.1f}")
        app.state.repositorio.engine.dispose()


if __name__ == "__main__":
    main()
