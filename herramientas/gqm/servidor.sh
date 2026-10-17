#!/usr/bin/env bash
# Arranca/detiene el servidor de una versión sobre su propia base SQLite (sin PostgreSQL).
# Uso: servidor.sh start <v1.0|v1.5> <puerto> <ruta_db.sqlite>
#      servidor.sh stop <puerto>
#      servidor.sh cargar-app <v1.0|v1.5> <ruta_db.sqlite> [--reiniciar]   (cargador sintético propio de la app)
set -u
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
PY="${PY:-python}"
dir_app() { case "$1" in v1.0) echo "${GQM_RAIZ_V10:-$RAIZ/../inc1_v1.0_PMV}";; v1.5) echo "${GQM_RAIZ_V15:-$RAIZ/pmv_fastapi}";; esac; }
PIDS="${GQM_TMP:-/tmp/gqm}/pids"; mkdir -p "$PIDS"
case "${1:-}" in
  start)
    APP="$(dir_app "$2")"; PUERTO="$3"; DB="$4"; mkdir -p "$(dirname "$DB")"
    cd "$APP" || exit 1
    PYTHONDONTWRITEBYTECODE=1 DATABASE_URL="sqlite:///$DB" nohup "$PY" -m uvicorn app.main:crear_app --factory --host 127.0.0.1 --port "$PUERTO" --log-level warning > "${GQM_TMP:-/tmp/gqm}/uvicorn_$PUERTO.log" 2>&1 &
    echo $! > "$PIDS/$PUERTO.pid"
    for _ in $(seq 1 50); do curl -s -o /dev/null "http://127.0.0.1:$PUERTO/api/salud" && { echo "servidor $2 listo en :$PUERTO (pid $(cat "$PIDS/$PUERTO.pid"))"; exit 0; }; sleep 0.2; done
    echo "no arrancó"; exit 1 ;;
  stop)
    [ -f "$PIDS/$2.pid" ] && kill "$(cat "$PIDS/$2.pid")" 2>/dev/null; rm -f "$PIDS/$2.pid"; sleep 0.5; echo "detenido :$2" ;;
  cargar-app)
    APP="$(dir_app "$2")"; DB="$3"; shift 3; mkdir -p "$(dirname "$DB")"; cd "$APP" || exit 1
    PYTHONDONTWRITEBYTECODE=1 DATABASE_URL="sqlite:///$DB" "$PY" -m scripts.cargar_datos_prueba "$@" ;;
  *) echo "uso: ver cabecera"; exit 2 ;;
esac
