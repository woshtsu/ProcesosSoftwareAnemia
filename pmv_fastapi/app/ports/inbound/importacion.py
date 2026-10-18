"""Puerto de entrada: importación de un dataset externo anonimizado (ADR-009)."""

from collections.abc import Iterable
from typing import Protocol

from app.domain.model.importacion import RegistroImportado, ResultadoImportacion


class ImportarDataset(Protocol):
    def importar(self, registros: Iterable[RegistroImportado]) -> ResultadoImportacion:
        """Persiste los registros como niños de origen DATASET_DIRESA_JUNIN y devuelve el reporte de la importación."""
        ...

    def eliminar_importados(self) -> int:
        """Borra los niños de origen DATASET_DIRESA_JUNIN (con sus evaluaciones); devuelve cuántos eran."""
        ...

    def contar_importados(self) -> int:
        """Cantidad de niños de origen DATASET_DIRESA_JUNIN ya guardados."""
        ...
