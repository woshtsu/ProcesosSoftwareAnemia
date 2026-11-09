"""Pruebas unitarias para la caché de agendas de niños activos (CacheAgendas)."""

import threading
import time
from datetime import date

from app.adapters.outbound.persistence.memoria import RepositorioEnMemoria
from app.application.cache_agendas import CacheAgendas
from app.domain.model.asistencia import AsistenciaControl, EstadoAsistencia
from app.domain.model.clasificacion import Clasificacion
from app.domain.model.entidades import Evaluacion, Nino
from app.domain.model.origen import OrigenDatos
from app.domain.model.tiempo import ahora


class RelojFijo:
    def __init__(self, dia: date):
        self.dia = dia

    def hoy(self) -> date:
        return self.dia


def _crear_nino(nino_id: str = "n-1", dni: str = "71234567") -> Nino:
    return Nino(
        id=nino_id,
        dni=dni,
        nombres="Juan",
        apellidos="Pérez",
        sexo="M",
        fecha_nacimiento=date(2025, 1, 1),
        establecimiento="P. S. Chongos Alto",
        distrito="Chongos Alto",
        comunidad="Palmayoc",
        altitud_m=3500,
        tutor_nombre="María Pérez",
        tutor_celular="987654321",
        registrado_por="enfermera",
        origen=OrigenDatos.SISTEMA,
    )


def _crear_evaluacion(nino_id: str = "n-1", eval_id: str = "ev-1") -> Evaluacion:
    return Evaluacion(
        id=eval_id,
        nino_id=nino_id,
        fecha=date(2026, 1, 15),
        hemoglobina_observada=9.5,
        hemoglobina_ajustada=8.0,
        peso_kg=10.0,
        talla_cm=75.0,
        altitud_m=3500,
        edad_meses=12,
        clasificacion=Clasificacion.MODERADA,
        registrado_por="enfermera",
        creado_en=ahora(),
    )


def test_acierto_cache_evita_recalculo():
    repo = RepositorioEnMemoria()
    repo.guardar(_crear_nino())
    reloj = RelojFijo(date(2026, 9, 28))
    cache = CacheAgendas(repo, reloj, ttl_segundos=60)

    llamadas = 0
    orig_listar = repo.listar

    def spy_listar(*args, **kwargs):
        nonlocal llamadas
        llamadas += 1
        return orig_listar(*args, **kwargs)

    repo.listar = spy_listar

    res1 = cache.obtener_agendas()
    res2 = cache.obtener_agendas()

    assert len(res1) == 1
    assert len(res2) == 1
    assert llamadas == 1


def test_invalidacion_tras_guardar_nino():
    repo = RepositorioEnMemoria()
    repo.guardar(_crear_nino("n-1", "71111111"))
    reloj = RelojFijo(date(2026, 9, 28))
    cache = CacheAgendas(repo, reloj, ttl_segundos=60)

    assert len(cache.obtener_agendas()) == 1

    repo.guardar(_crear_nino("n-2", "72222222"))
    assert len(cache.obtener_agendas()) == 2


def test_invalidacion_tras_agregar_evaluacion():
    repo = RepositorioEnMemoria()
    n = _crear_nino()
    repo.guardar(n)
    reloj = RelojFijo(date(2026, 9, 28))
    cache = CacheAgendas(repo, reloj, ttl_segundos=60)

    agendas1 = cache.obtener_agendas()
    assert len(agendas1[0][0].evaluaciones) == 0

    repo.agregar_evaluacion(_crear_evaluacion(n.id))
    agendas2 = cache.obtener_agendas()
    assert len(agendas2[0][0].evaluaciones) == 1


def test_invalidacion_tras_agregar_asistencia():
    repo = RepositorioEnMemoria()
    n = _crear_nino()
    repo.guardar(n)
    reloj = RelojFijo(date(2026, 9, 28))
    cache = CacheAgendas(repo, reloj, ttl_segundos=60)

    agendas1 = cache.obtener_agendas()
    assert len(agendas1[0][0].asistencias) == 0

    asist = AsistenciaControl(
        id="asist-1",
        nino_id=n.id,
        codigo_control="C1M",
        fecha_programada=date(2026, 2, 1),
        estado=EstadoAsistencia.ASISTIO,
        motivo=None,
        evaluacion_id=None,
        registrado_por="enfermera",
        creado_en=ahora(),
    )
    repo.agregar_asistencia(asist)
    agendas2 = cache.obtener_agendas()
    assert len(agendas2[0][0].asistencias) == 1


def test_cambio_de_dia_invalida_cache():
    repo = RepositorioEnMemoria()
    repo.guardar(_crear_nino())
    reloj = RelojFijo(date(2026, 9, 28))
    cache = CacheAgendas(repo, reloj, ttl_segundos=60)

    llamadas = 0
    orig_listar = repo.listar

    def spy_listar(*args, **kwargs):
        nonlocal llamadas
        llamadas += 1
        return orig_listar(*args, **kwargs)

    repo.listar = spy_listar

    cache.obtener_agendas()
    assert llamadas == 1

    cache.obtener_agendas()
    assert llamadas == 1

    # Cambio de día
    reloj.dia = date(2026, 9, 29)
    cache.obtener_agendas()
    assert llamadas == 2


def test_ttl_cero_desactiva_cache():
    repo = RepositorioEnMemoria()
    repo.guardar(_crear_nino())
    reloj = RelojFijo(date(2026, 9, 28))
    cache = CacheAgendas(repo, reloj, ttl_segundos=0)

    llamadas = 0
    orig_listar = repo.listar

    def spy_listar(*args, **kwargs):
        nonlocal llamadas
        llamadas += 1
        return orig_listar(*args, **kwargs)

    repo.listar = spy_listar

    cache.obtener_agendas()
    cache.obtener_agendas()
    cache.obtener_agendas()
    assert llamadas == 3


def test_concurrencia_calcula_una_sola_vez():
    repo = RepositorioEnMemoria()
    repo.guardar(_crear_nino())
    reloj = RelojFijo(date(2026, 9, 28))
    cache = CacheAgendas(repo, reloj, ttl_segundos=60)

    llamadas = 0
    orig_listar = repo.listar

    def slow_listar(*args, **kwargs):
        nonlocal llamadas
        time.sleep(0.04)
        llamadas += 1
        return orig_listar(*args, **kwargs)

    repo.listar = slow_listar

    resultados = []

    def trabajador():
        res = cache.obtener_agendas()
        resultados.append(res)

    hilos = [threading.Thread(target=trabajador) for _ in range(8)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    assert len(resultados) == 8
    assert llamadas == 1


def test_mutacion_externa_no_afecta_cache():
    repo = RepositorioEnMemoria()
    repo.guardar(_crear_nino())
    reloj = RelojFijo(date(2026, 9, 28))
    cache = CacheAgendas(repo, reloj, ttl_segundos=60)

    items = cache.obtener_agendas()
    items.clear()

    assert len(cache.obtener_agendas()) == 1
