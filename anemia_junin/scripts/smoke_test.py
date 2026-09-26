"""
Smoke test HTTP contra un servidor levantado — PMV Anemia Junín.

Verifica los flujos principales (HIST-1.1 a HIST-1.5) contra una URL real y mide
la latencia de cada petición. No requiere dependencias externas (solo stdlib).

Uso (con el servidor corriendo, p. ej. `python -m anemia_junin`):
    python scripts/smoke_test.py
    python scripts/smoke_test.py --url http://127.0.0.1:8000 --umbral-ms 2000

Crea (si no existe) el niño sintético con DNI 90099999 y le agrega un dosaje.
Código de salida 0 si todas las verificaciones pasan; 1 en caso contrario.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import date, timedelta

DNI_PRUEBA = "90099999"


class _SinRedireccion(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


_OPENER = urllib.request.build_opener(_SinRedireccion)


def _peticion(base: str, metodo: str, ruta: str, cuerpo: dict | None = None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(base + ruta, data=datos, method=metodo)
    if datos is not None:
        req.add_header("Content-Type", "application/json")
    inicio = time.perf_counter()
    try:
        with _OPENER.open(req, timeout=10) as r:
            status, texto = r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        with e:
            status, texto = e.code, e.read().decode("utf-8")
    ms = (time.perf_counter() - inicio) * 1000
    try:
        cuerpo_json = json.loads(texto)
    except ValueError:
        cuerpo_json = None
    return status, cuerpo_json, texto, ms


def ejecutar(base: str, umbral_ms: float) -> int:
    hoy = date.today()
    nino = {
        "dni": DNI_PRUEBA, "nombres": "Prueba Humo", "apellidos": "Sintetico Demo",
        "fecha_nacimiento": (hoy - timedelta(days=700)).isoformat(), "sexo": "F",
        "tipo_nacimiento": "TERMINO", "peso_kg": 10.4, "distrito": "Huancayo",
        "altitud_msnm": 3271, "cuidador": "Cuidadora Demo", "telefono": "900000000",
        "dosaje_inicial": {"fecha_dosaje": hoy.isoformat(), "hb_observada": 10.9},
    }
    invalido = {**nino, "dni": "1234567", "dosaje_inicial": {"fecha_dosaje": hoy.isoformat(),
                                                              "hb_observada": 30.0}}
    periodo = f"desde={(hoy - timedelta(days=365)).isoformat()}&hasta={hoy.isoformat()}"

    existe = _peticion(base, "GET", f"/api/v1/ninos/{DNI_PRUEBA}")[0] == 200
    verificaciones = [
        ("Salud del servicio", "GET", "/api/v1/salud", None, {200}),
        ("Alta válida (HIST-1.1)", "POST", "/api/v1/ninos", nino, {409} if existe else {201}),
        ("Rechazo de duplicado", "POST", "/api/v1/ninos", nino, {409}),
        ("Rechazo de datos inválidos (HIST-1.3)", "POST", "/api/v1/ninos", invalido, {400}),
        ("Consulta de expediente (HIST-1.2)", "GET", f"/api/v1/ninos/{DNI_PRUEBA}", None, {200}),
        ("Actualización parcial (HIST-1.2)", "PATCH", f"/api/v1/ninos/{DNI_PRUEBA}",
         {"peso_kg": 10.6}, {200}),
        ("Nuevo dosaje (HIST-1.2)", "POST", f"/api/v1/ninos/{DNI_PRUEBA}/dosajes",
         {"fecha_dosaje": hoy.isoformat(), "hb_observada": 12.0, "altitud_msnm": 3271}, {201}),
        ("Listado (HIST-1.4)", "GET", "/api/v1/ninos", None, {200}),
        ("Listado filtrado SEVERA", "GET", "/api/v1/ninos?clasificacion=SEVERA", None, {200}),
        ("Reporte del periodo (HIST-1.5)", "GET", f"/api/v1/reportes/registros?{periodo}",
         None, {200}),
        ("Web: raíz redirige", "GET", "/", None, {303}),
        ("Web: lista", "GET", "/ninos", None, {200}),
        ("Web: formulario de alta", "GET", "/ninos/nuevo", None, {200}),
        ("Web: expediente", "GET", f"/ninos/{DNI_PRUEBA}", None, {200}),
        ("Web: reporte", "GET", f"/reportes/registros?{periodo}", None, {200}),
    ]

    fallos, maximo = 0, 0.0
    print(f"Smoke test contra {base}\n")
    for nombre, metodo, ruta, cuerpo, esperados in verificaciones:
        status, _, _, ms = _peticion(base, metodo, ruta, cuerpo)
        maximo = max(maximo, ms)
        ok = status in esperados and ms <= umbral_ms
        fallos += 0 if ok else 1
        estado = "OK  " if ok else "FALLA"
        print(f"  [{estado}] {nombre:<42} {metodo:<5} {status}  {ms:7.1f} ms")

    total = len(verificaciones)
    resultado = "APROBADO" if fallos == 0 else "REPROBADO"
    print(f"\n{total} verificaciones, {fallos} fallos, latencia máxima {maximo:.1f} ms "
          f"(umbral {umbral_ms:.0f} ms) -> RESULTADO: {resultado}")
    return 0 if fallos == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke test HTTP del PMV Anemia Junín")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--umbral-ms", type=float, default=2000.0)
    args = parser.parse_args(argv)
    return ejecutar(args.url.rstrip("/"), args.umbral_ms)


if __name__ == "__main__":
    sys.exit(main())
