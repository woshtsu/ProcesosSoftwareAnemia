"""
Pruebas del punto de entrada (python -m anemia_junin) y del script de datos sintéticos.
"""

from __future__ import annotations

import importlib.util
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from anemia_junin import __main__ as entrada

_RAIZ = Path(__file__).parents[1]


def _cargar_script():
    ruta = _RAIZ / "scripts" / "cargar_datos_sinteticos.py"
    spec = importlib.util.spec_from_file_location("cargar_datos_sinteticos", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_argumentos_por_defecto(monkeypatch):
    monkeypatch.delenv("ANEMIA_PORT", raising=False)
    monkeypatch.delenv("ANEMIA_HOST", raising=False)
    args = entrada._parsear_argumentos([])
    assert (args.host, args.port, args.dev) == ("127.0.0.1", 8000, False)


def test_main_usa_waitress(monkeypatch, tmp_path, capsys):
    llamadas = {}

    def serve_falso(app, host, port, threads):
        llamadas.update(host=host, port=port, db=app.config["DB_PATH"])

    monkeypatch.setattr("waitress.serve", serve_falso)
    db = str(tmp_path / "m.db")
    assert entrada.main(["--port", "8123", "--db", db]) == 0
    assert llamadas == {"host": "127.0.0.1", "port": 8123, "db": db}
    assert "http://127.0.0.1:8123/" in capsys.readouterr().out


def test_main_modo_dev(monkeypatch, tmp_path):
    llamadas = {}
    monkeypatch.setattr("flask.Flask.run", lambda self, **kw: llamadas.update(kw))
    entrada.main(["--dev", "--db", str(tmp_path / "d.db")])
    assert llamadas["debug"] is True


def test_variables_de_entorno(monkeypatch, tmp_path):
    from anemia_junin.bootstrap import crear_app

    db = str(tmp_path / "env.db")
    monkeypatch.setenv("ANEMIA_DB_PATH", db)
    monkeypatch.setenv("ANEMIA_SECRET_KEY", "desde-entorno")
    monkeypatch.setenv("ANEMIA_NORMATIVA_PATH", str(_RAIZ / "config" / "normativa_v1.json"))
    app = crear_app()
    assert app.config["DB_PATH"] == db
    assert app.config["SECRET_KEY"] == "desde-entorno"


def test_script_carga_datos_sinteticos(tmp_path):
    script = _cargar_script()
    db = str(tmp_path / "demo.db")
    resumen = script.cargar(db)
    assert resumen["ninos_aceptados"] == script.N_NINOS
    assert resumen["ninos_rechazados"] == 0
    assert resumen["intentos_invalidos"] == 3
    with closing(sqlite3.connect(db)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM ninos").fetchone()[0] == script.N_NINOS
        rechazados = conn.execute(
            "SELECT COUNT(*) FROM intentos_registro WHERE resultado = 'RECHAZADO'"
        ).fetchone()[0]
        assert rechazados == 3
    # No mezcla con datos existentes
    with pytest.raises(SystemExit):
        script.cargar(db)


def test_script_main(tmp_path, capsys):
    script = _cargar_script()
    assert script.main(["--db", str(tmp_path / "otra.db")]) == 0
    assert "Niños aceptados" in capsys.readouterr().out


def test_error_interno_sin_trazas(tmp_path):
    from anemia_junin.bootstrap import crear_app

    app = crear_app(db_path=str(tmp_path / "e.db"), secret_key="x", testing=False)

    class Explota:
        def ejecutar(self, *_a, **_k):
            raise RuntimeError("detalle interno que no debe filtrarse")

    app.config["CASOS_DE_USO"]["consultar_expediente"] = Explota()
    c = app.test_client()
    api = c.get("/api/v1/ninos/12345678")
    assert api.status_code == 500
    assert api.get_json()["error"]["code"] == "INTERNAL_ERROR"
    assert "detalle interno" not in api.get_data(as_text=True)
    web = c.get("/ninos/12345678")
    assert web.status_code == 500
    assert "detalle interno" not in web.get_data(as_text=True)
