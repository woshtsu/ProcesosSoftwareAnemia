"""Factor R: prueba de caos con un cluster PostgreSQL 16 TEMPORAL (kill -9) y reconexion automatica del pool.

Uso (raiz del repositorio): python entregables/semana-10/metricas/caos_postgres.py
1) initdb + arranque de un cluster propio en /tmp/s10pg, 127.0.0.1:5433 (usuario de sistema `postgres` solo para ejecutar el
   cluster); esquema db/01_esquema_postgresql.sql.
2) La aplicacion (uvicorn 127.0.0.1:8765, AUTH_MODE=demo, datos sinteticos) usa ese cluster (SQLAlchemy, pool_pre_ping=True).
3) Un sondeo pide GET /api/ninos y GET /api/salud cada 100 ms. Se mata con kill -9 SOLO el arbol de procesos de ese cluster
   temporal y se reinicia a los 5 s.
4) Se mide: codigos HTTP durante la caida, si la aplicacion sigue viva y los segundos desde que la BD acepta conexiones hasta la
   primera respuesta 200 de la API, sin reiniciar la aplicacion.
Salida: metricas/salidas/R_caos_postgres.json
"""

import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capturar_software as cs  # noqa: E402

BIN = Path("/usr/lib/postgresql/16/bin")
DIR = Path("/tmp/s10pg")
PUERTO_PG = 5433
URL_DB = f"postgresql+psycopg2://postgres@127.0.0.1:{PUERTO_PG}/anemia"


def como_pg(*cmd):
    return subprocess.run(["runuser", "-u", "postgres", "--", *map(str, cmd)], capture_output=True, text=True)


def iniciar_pg():
    opciones = f"-p {PUERTO_PG} -c listen_addresses=127.0.0.1 -c unix_socket_directories={DIR}"
    return como_pg(BIN / "pg_ctl", "-D", DIR / "data", "-o", opciones, "-l", DIR / "pg.log", "-w", "start")


def matar_cluster_temporal():
    """kill -9 del postmaster de /tmp/s10pg y de sus procesos hijos (nunca de otros PostgreSQL del equipo)."""
    raiz = int((DIR / "data" / "postmaster.pid").read_text().splitlines()[0])
    padres = {}
    for d in Path("/proc").iterdir():
        if d.name.isdigit():
            try:
                padres[int(d.name)] = int((d / "stat").read_text().rsplit(")", 1)[1].split()[1])
            except (OSError, ValueError, IndexError):
                continue
    arbol, nuevos = {raiz}, {raiz}
    while nuevos:
        nuevos = {pid for pid, pp in padres.items() if pp in arbol and pid not in arbol}
        arbol |= nuevos
    for pid in arbol:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    return len(arbol)


def main():
    if DIR.exists():
        shutil.rmtree(DIR)
    DIR.mkdir()
    shutil.chown(DIR, "postgres", "postgres")
    r = como_pg(BIN / "initdb", "-D", DIR / "data", "-A", "trust", "-U", "postgres")
    assert r.returncode == 0, r.stderr
    r = iniciar_pg()
    assert r.returncode == 0, r.stderr
    como_pg(BIN / "createdb", "-h", "127.0.0.1", "-p", PUERTO_PG, "-U", "postgres", "anemia")
    esquema = cs.PMV / "db" / "01_esquema_postgresql.sql"
    cmd = [str(BIN / "psql"), "-h", "127.0.0.1", "-p", str(PUERTO_PG), "-U", "postgres", "-d", "anemia", "-v", "ON_ERROR_STOP=1", "-q", "-f", str(esquema)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    entorno = {**os.environ, "DATABASE_URL": URL_DB, "AUTH_MODE": "demo"}
    subprocess.run([sys.executable, "-m", "scripts.cargar_datos_prueba"], cwd=cs.PMV, env=entorno, check=True, stdout=subprocess.DEVNULL)
    app = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:crear_app", "--factory", "--port", str(cs.PUERTO)], cwd=cs.PMV, env=entorno, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    registro = []
    parar = threading.Event()
    marca = {"t0": time.perf_counter()}

    def sondear():
        while not parar.is_set():
            t = time.perf_counter() - marca["t0"]
            try:
                code = httpx.get(cs.URL + "/api/ninos", timeout=5).status_code
            except httpx.HTTPError as e:
                code = type(e).__name__
            try:
                salud = httpx.get(cs.URL + "/api/salud", timeout=5).status_code
            except httpx.HTTPError as e:
                salud = type(e).__name__
            registro.append((round(t, 2), code, salud))
            time.sleep(0.1)

    res = {}
    try:
        for _ in range(100):
            try:
                if httpx.get(cs.URL + "/api/salud").status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.2)
        marca["t0"] = time.perf_counter()
        th = threading.Thread(target=sondear)
        th.start()
        time.sleep(2)
        t_kill = time.perf_counter() - marca["t0"]
        procesos = matar_cluster_temporal()
        time.sleep(5)
        r = iniciar_pg()
        t_listo = time.perf_counter() - marca["t0"]
        time.sleep(4)
        parar.set()
        th.join()
        tras = [x for x in registro if x[0] >= t_listo]
        primera_ok = next((x[0] for x in tras if x[1] == 200), None)
        durante = [x for x in registro if t_kill <= x[0] < t_listo]
        antes = [x for x in registro if x[0] < t_kill]
        res = {
            "procesos_terminados_con_kill_9": procesos,
            "bd_reiniciada_ok": r.returncode == 0,
            "t_kill_s": round(t_kill, 2),
            "bd_aceptando_conexiones_en_s": round(t_listo, 2),
            "peticiones_antes": len(antes),
            "antes_200": sum(1 for x in antes if x[1] == 200),
            "peticiones_durante_caida": len(durante),
            "codigos_durante_caida": {str(k): sum(1 for x in durante if x[1] == k) for k in {x[1] for x in durante}},
            "salud_durante_caida_200": sum(1 for x in durante if x[2] == 200),
            "codigos_salud_durante_caida": {str(k): sum(1 for x in durante if x[2] == k) for k in {x[2] for x in durante}},
            "aplicacion_viva_tras_caida": app.poll() is None,
            "segundos_hasta_primer_200_tras_volver_la_bd": round(primera_ok - t_listo, 2) if primera_ok is not None else None,
            "peticiones_despues": len(tras),
            "despues_200": sum(1 for x in tras if x[1] == 200),
            "reinicio_de_la_aplicacion_necesario": not (primera_ok is not None and app.poll() is None),
            "nota": "La BD se reinicio manualmente a los 5 s; no se mide la recuperacion automatica de la propia BD (la gestiona el proveedor).",
        }
    finally:
        parar.set()
        app.terminate()
        app.wait()
        como_pg(BIN / "pg_ctl", "-D", DIR / "data", "-m", "immediate", "stop")
        shutil.rmtree(DIR, ignore_errors=True)
    (cs.BASE / "metricas" / "salidas" / "R_caos_postgres.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
