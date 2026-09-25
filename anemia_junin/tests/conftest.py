"""
conftest.py — Fixtures compartidas para todas las pruebas.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from anemia_junin.bootstrap import crear_app


@pytest.fixture
def app(tmp_path: Path):
    """Flask app configurada para pruebas, con BD temporal."""
    db = str(tmp_path / "test.db")
    normativa = Path(__file__).parent.parent / "config" / "normativa_v1.json"
    app = crear_app(
        db_path=db,
        normativa_path=normativa,
        secret_key="test-secret",
        testing=True,
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()
