"""Caché en memoria de los niños activos con su agenda calculada (ADR-006, optimización).

Mantiene una instantánea en memoria compartida por los casos de uso clínicos (alertas, visitas priorizadas,
barreras críticas, agenda personal y recordatorios). Evita recalcular generar_agenda() para todos los niños
activos en cada petición concurrente.

Clave de validez: (hoy, versión de datos del repositorio).
Single-flight: cerrojo threading.Lock para que peticiones simultáneas esperen al mismo cálculo.
TTL de seguridad: configurable mediante CACHE_AGENDAS_TTL_SEGUNDOS (por defecto 300 s; 0 desactiva la caché).
"""

import os
import threading
import time
from datetime import date

from app.domain.model.agenda import AgendaNino
from app.domain.model.entidades import Nino
from app.domain.service.agenda import generar_agenda
from app.ports.outbound.cache_agendas import ProveedorAgendasActivos
from app.ports.outbound.reloj import Reloj
from app.ports.outbound.repositorio_ninos import RepositorioNinos

CACHE_AGENDAS_TTL_DEFAULT = 300.0


def _obtener_ttl_configurado(ttl: float | None = None) -> float:
    if ttl is not None:
        return float(ttl)
    env_ttl = os.getenv("CACHE_AGENDAS_TTL_SEGUNDOS")
    if env_ttl is not None and env_ttl.strip():
        try:
            return float(env_ttl)
        except ValueError:
            return CACHE_AGENDAS_TTL_DEFAULT
    return CACHE_AGENDAS_TTL_DEFAULT


class CacheAgendas(ProveedorAgendasActivos):
    def __init__(
        self,
        repo: RepositorioNinos,
        reloj: Reloj,
        ttl_segundos: float | None = None,
    ):
        self.repo = repo
        self.reloj = reloj
        self.ttl_segundos = _obtener_ttl_configurado(ttl_segundos)
        self._cerrojo = threading.Lock()
        self._cache: list[tuple[Nino, AgendaNino]] | None = None
        self._clave_cache: tuple[date, int] | None = None
        self._expira_en: float = 0.0

    def _calcular(self, hoy: date) -> list[tuple[Nino, AgendaNino]]:
        return [(nino, generar_agenda(nino, hoy)) for nino in self.repo.listar(estado="ACTIVO")]

    def _obtener_version(self) -> int:
        if hasattr(self.repo, "version_datos"):
            return self.repo.version_datos()
        return 0

    def obtener_agendas(self) -> list[tuple[Nino, AgendaNino]]:
        if self.ttl_segundos <= 0:
            return self._calcular(self.reloj.hoy())

        hoy = self.reloj.hoy()
        version = self._obtener_version()
        clave_actual = (hoy, version)
        ahora = time.monotonic()

        if self._cache is not None and self._clave_cache == clave_actual and ahora < self._expira_en:
            return list(self._cache)

        with self._cerrojo:
            ahora = time.monotonic()
            hoy = self.reloj.hoy()
            version = self._obtener_version()
            clave_actual = (hoy, version)
            if self._cache is not None and self._clave_cache == clave_actual and ahora < self._expira_en:
                return list(self._cache)

            datos = self._calcular(hoy)
            self._cache = datos
            self._clave_cache = clave_actual
            self._expira_en = ahora + self.ttl_segundos
            return list(self._cache)

    def invalidar(self) -> None:
        with self._cerrojo:
            self._cache = None
            self._clave_cache = None
            self._expira_en = 0.0
