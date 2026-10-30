"""Puerto de salida: bitácora de operaciones sincronizadas y conflictos (HIST-3.2, HIST-3.3)."""

from typing import Protocol

from app.domain.model.sincronizacion import ConflictoSincronizacion, OperacionSincronizada


class RepositorioSincronizacion(Protocol):
    def obtener_operacion(self, id_operacion: str) -> OperacionSincronizada | None: ...

    def registrar_operacion(self, operacion: OperacionSincronizada) -> bool:
        """Guarda la operación; devuelve False (sin cambios) si el ``id_operacion`` ya estaba registrado."""
        ...

    def marcar_operacion_resuelta(self, id_operacion: str) -> None:
        """Pasa a RESUELTA la operación de un niño cuyo conflicto se resolvió, para que sus dependientes la usen."""
        ...

    def id_nino_de_cliente(self, id_dispositivo: str, id_cliente: str) -> str | None:
        """Id del servidor del niño que ese dispositivo registró con el id temporal dado (si ya está aplicado)."""
        ...

    def contar_operaciones(self) -> int: ...

    def guardar_conflicto(self, conflicto: ConflictoSincronizacion) -> ConflictoSincronizacion: ...

    def obtener_conflicto(self, conflicto_id: str) -> ConflictoSincronizacion | None: ...

    def listar_conflictos(self, estado: str | None = None) -> list[ConflictoSincronizacion]:
        """Conflictos (el más antiguo primero), filtrados por estado si se indica."""
        ...

    def obtener_conflicto_de_operacion(self, id_operacion: str) -> ConflictoSincronizacion | None: ...

    def actualizar_conflicto(self, conflicto: ConflictoSincronizacion) -> ConflictoSincronizacion: ...
