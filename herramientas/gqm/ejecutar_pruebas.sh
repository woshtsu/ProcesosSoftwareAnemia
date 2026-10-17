#!/usr/bin/env bash
# Ejecuta ruff, pytest (con cobertura) y E2E Playwright en una versión y guarda las salidas crudas.
# Uso: herramientas/gqm/ejecutar_pruebas.sh <v1.0|v1.5> [ruta_app]
set -u
VER="${1:?versión v1.0 o v1.5}"
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
case "$VER" in
  v1.0) APP="${2:-${GQM_RAIZ_V10:-$RAIZ/../inc1_v1.0_PMV}}" ;;
  v1.5) APP="${2:-$RAIZ/pmv_fastapi}" ;;
  *) echo "versión inválida"; exit 2 ;;
esac
PY="${PY:-python}"
OUT="$RAIZ/entregables/semana-09/metricas/salidas/$VER"
mkdir -p "$OUT"
export PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE="$OUT/.coverage" PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}"
cd "$APP" || exit 1
{ echo "# $(date -Is) ruff $("$PY" -m ruff --version) en $APP"; } > "$OUT/ruff_check.txt"
"$PY" -m ruff check --no-cache . >> "$OUT/ruff_check.txt" 2>&1; echo "exit=$?" >> "$OUT/ruff_check.txt"
{ echo "# $(date -Is) ruff format --check"; } > "$OUT/ruff_format.txt"
"$PY" -m ruff format --check --no-cache . >> "$OUT/ruff_format.txt" 2>&1; echo "exit=$?" >> "$OUT/ruff_format.txt"
# n.º de pruebas por carpeta (recolección)
: > "$OUT/pytest_por_carpeta.txt"
for d in tests/unitarias tests/integracion tests/arquitectura; do
  [ -d "$d" ] && { echo "## $d" >> "$OUT/pytest_por_carpeta.txt"; "$PY" -m pytest "$d" --collect-only -q -p no:cacheprovider --no-cov 2>&1 | tail -3 >> "$OUT/pytest_por_carpeta.txt"; }
done
"$PY" -m pytest tests/unitarias tests/integracion $( [ -d tests/arquitectura ] && echo tests/arquitectura ) --cov=app --cov-report=term-missing --cov-report=xml:"$OUT/cobertura.xml" -p no:cacheprovider -v --durations=5 > "$OUT/pytest_cov.txt" 2>&1; echo "exit=$?" >> "$OUT/pytest_cov.txt"
"$PY" -m pytest tests/e2e -m e2e --no-cov -p no:cacheprovider -v > "$OUT/pytest_e2e.txt" 2>&1; echo "exit=$?" >> "$OUT/pytest_e2e.txt"
echo "listo $VER"
