"""CP-113: el contrato publicado en docs/openapi.json coincide con el que genera la aplicación."""

import json
from pathlib import Path

from scripts import exportar_openapi


def test_cp113_openapi_publicado_esta_al_dia():
    publicado = Path(exportar_openapi.DESTINO).read_text(encoding="utf-8")
    assert exportar_openapi.generar() == publicado, "ejecute: python -m scripts.exportar_openapi"
    contrato = json.loads(publicado)
    assert contrato["info"]["version"] == "2.0.0-inc2"
    assert "/api/alertas/resumen" in contrato["paths"]


def test_cp113_el_script_verifica_y_exporta(tmp_path, monkeypatch, capsys):
    destino = tmp_path / "openapi.json"
    monkeypatch.setattr("sys.argv", ["exportar_openapi", "--salida", str(destino), "--verificar"])
    assert exportar_openapi.main() == 1  # no existe todavía
    monkeypatch.setattr("sys.argv", ["exportar_openapi", "--salida", str(destino)])
    assert exportar_openapi.main() == 0 and destino.exists()
    monkeypatch.setattr("sys.argv", ["exportar_openapi", "--salida", str(destino), "--verificar"])
    assert exportar_openapi.main() == 0
    assert "al día" in capsys.readouterr().out
