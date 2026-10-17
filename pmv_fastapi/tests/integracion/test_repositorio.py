"""CP-108 y CP-115: el repositorio SQLAlchemy también funciona con SQLite en memoria (desarrollo y pruebas rápidas)."""

from app.adapters.outbound.persistence.sqlalchemy_repo import RepositorioSQLAlchemy
from app.domain.model.entidades import Nino
from tests.conftest import datos_nino


def test_cp108_repositorio_con_sqlite_en_memoria():
    repo = RepositorioSQLAlchemy("sqlite:///:memory:")
    repo.crear_esquema()
    nino = Nino(**datos_nino(), registrado_por="a")
    repo.guardar(nino)
    assert [n.dni for n in repo.listar(estado="ACTIVO")] == ["71234567"]
    assert repo.obtener_por_dni("71234567").id == nino.id
    repo.engine.dispose()


def test_cp115_def08_guardar_traduce_el_dni_duplicado_y_no_oculta_otros_errores_de_integridad():
    """DEF-08: UNIQUE(dni) -> RegistroDuplicado; cualquier otra violación de integridad (p. ej. id repetido) se propaga."""
    import pytest
    from sqlalchemy.exc import IntegrityError

    from app.domain.model.errores import RegistroDuplicado

    repo = RepositorioSQLAlchemy("sqlite:///:memory:")
    repo.crear_esquema()
    repo.guardar(Nino(**datos_nino(), registrado_por="a"))
    with pytest.raises(RegistroDuplicado, match="71234567"):
        repo.guardar(Nino(**datos_nino(), registrado_por="b"))
    primero = repo.obtener_por_dni("71234567")
    otro = Nino(**datos_nino(dni="71234568"), registrado_por="c")
    otro.id = primero.id  # misma clave primaria, distinto DNI: no es un duplicado de DNI
    with pytest.raises(IntegrityError):
        repo.guardar(otro)
    repo.engine.dispose()
