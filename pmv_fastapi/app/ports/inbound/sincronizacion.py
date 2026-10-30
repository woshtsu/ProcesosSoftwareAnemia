"""Puertos de entrada: sincronización de operaciones sin conexión y resolución de conflictos (HIST-3.2, HIST-3.3)."""

from typing import Protocol

from app.domain.model.sincronizacion import ConflictoSincronizacion, OperacionEntrante, ResultadoSincronizacion


class SincronizarOperaciones(Protocol):
    def sincronizar(self, operaciones: list[OperacionEntrante], usuario: str) -> list[ResultadoSincronizacion]:
        """Procesa un lote ordenado por fecha local; devuelve un resultado por operación, en el orden recibido."""
        ...


class GestionarConflictos(Protocol):
    def listar_conflictos(self, estado: str | None = None) -> list[ConflictoSincronizacion]: ...

    def resolver_conflicto(self, conflicto_id: str, resolucion: str, usuario: str) -> ConflictoSincronizacion: ...
