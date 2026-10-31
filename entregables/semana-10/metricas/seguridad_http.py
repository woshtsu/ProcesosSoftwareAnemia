"""Factor +: pruebas HTTP de seguridad (OWASP Top 10:2025) contra el servidor local en modo supabase con Supabase simulado.

Uso (desde pmv_fastapi/): python ../entregables/semana-10/metricas/seguridad_http.py
* Levanta la aplicacion real (crear_app, auth_mode="supabase") en 127.0.0.1:8765 con un proveedor de identidad simulado
  (httpx.MockTransport: no se llama a ningun Supabase real) y AUTH_COOKIE_SECURE por defecto (true). Sin WHATSAPP_APP_SECRET.
* Cada comprobacion registra: id, categoria OWASP, esperado, observado y estado (CUMPLE / HALLAZGO).
* Salida: stdout y metricas/salidas/OWASP_pruebas_http.json
"""

import json
import os
import socket
import sys
import tempfile
import threading
import time
from pathlib import Path

import httpx
import uvicorn

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "pmv_fastapi"))
for k in ("AUTH_COOKIE_SECURE", "WHATSAPP_APP_SECRET", "WHATSAPP_VERIFY_TOKEN", "WHATSAPP_TOKEN", "AUTH_MODE"):
    os.environ.pop(k, None)

from app.adapters.outbound.supabase_auth import SupabaseAuth  # noqa: E402
from app.application.servicio_sesion import ServicioSesion  # noqa: E402
from app.main import crear_app  # noqa: E402

URL = "http://127.0.0.1:8765"
USER = {"id": "usuario-prueba", "email": "enfermeria@example.test", "email_confirmed_at": "2026-10-23"}
res: list[dict] = []


def chk(id_, owasp, control, esperado, observado, ok, nota=""):
    res.append({"id": id_, "owasp": owasp, "control": control, "esperado": esperado, "observado": observado, "estado": "CUMPLE" if ok else "HALLAZGO", "nota": nota})
    print(f"{id_:<5}{owasp:<8}{'CUMPLE' if ok else 'HALLAZGO':<9}{control} | esperado: {esperado} | observado: {observado}")


def responder(req):
    if req.url.path.endswith("/token"):
        if json.loads(req.content).get("password") != "correcta":
            return httpx.Response(400)
        return httpx.Response(200, json={"access_token": "access-s10", "refresh_token": "refresh-s10", "expires_in": 3600, "user": USER})
    if req.url.path.endswith("/logout"):
        return httpx.Response(204)
    if req.headers.get("authorization") == "Bearer access-s10":
        return httpx.Response(200, json=USER)
    return httpx.Response(401)


def main():
    tmp = tempfile.mkdtemp(prefix="s10sec_")
    import subprocess

    subprocess.run([sys.executable, "-m", "scripts.cargar_datos_prueba"], cwd=RAIZ / "pmv_fastapi", env={**os.environ, "DATABASE_URL": f"sqlite:///{tmp}/sec.db"}, check=True, stdout=subprocess.DEVNULL)
    app = crear_app(f"sqlite:///{tmp}/sec.db", auth_mode="supabase")
    app.state.auth_configurado = True
    app.state.sesiones = ServicioSesion(SupabaseAuth("https://example.test", "publica", transport=httpx.MockTransport(responder)))
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 8765))
    server = uvicorn.Server(uvicorn.Config(app, log_level="error"))
    th = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    th.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    c = httpx.Client(base_url=URL, timeout=10)
    try:
        # --- A01 Broken Access Control (incluye SSRF y CSRF) ---
        r = c.get("/api/ninos")
        chk("T01", "A01", "API clinica sin sesion", "401", r.status_code, r.status_code == 401)
        r = c.get("/api/alertas/resumen")
        chk("T02", "A01", "Alertas sin sesion", "401", r.status_code, r.status_code == 401)
        r = c.post("/api/ninos", json={})
        chk("T03", "A01", "POST sin cabecera CSRF ni sesion", "403", r.status_code, r.status_code == 403)
        contrato = json.loads((RAIZ / "pmv_fastapi" / "docs" / "openapi.json").read_text(encoding="utf-8"))
        publicas = {"/api/salud", "/api/auth/config", "/api/auth/login", "/api/auth/session", "/api/auth/logout", "/api/notificaciones/whatsapp/webhook"}
        ops = [(m.upper(), ruta) for ruta, mm in contrato["paths"].items() for m in mm if ruta not in publicas]
        sin_401 = []
        for m, ruta in ops:
            rr = c.request(m, ruta.replace("{nino_id}", "x").replace("{dni}", "x").replace("{codigo}", "x").replace("{conflicto_id}", "x").replace("{recordatorio_id}", "x"), headers={"X-CSRF-Protection": "1"}, json={} if m in ("POST", "PATCH") else None)
            if rr.status_code != 401:
                sin_401.append((m, ruta, rr.status_code))
        chk("T03b", "A01", f"Las {len(ops)} operaciones del contrato OpenAPI que no son publicas responden 401 sin sesion", "401 en todas", f"{len(ops) - len(sin_401)} de {len(ops)}; excepciones: {sin_401}", not sin_401)
        # login
        mal = c.post("/api/auth/login", json={"email": "enfermeria@example.test", "password": "x"}, headers={"X-CSRF-Protection": "1"})
        ok = c.post("/api/auth/login", json={"email": "enfermeria@example.test", "password": "correcta"}, headers={"X-CSRF-Protection": "1"})
        cookies = ok.headers.get_list("set-cookie")
        banderas = {k.split("=")[0]: v for k, v in ((x.split(";")[0], x) for x in cookies)}
        acceso = next((x for x in cookies if x.startswith("aj_access=")), "")
        chk("T04", "A07", "Mensaje de login incorrecto no revela si el correo existe", "401 generico", f"{mal.status_code} {mal.json()['errores'][0]['mensaje']}", mal.status_code == 401 and "o contraseña" in mal.json()["errores"][0]["mensaje"])
        chk("T05", "A07", "Cookie de sesion HttpOnly", "HttpOnly", "HttpOnly" in acceso, "HttpOnly" in acceso)
        chk("T06", "A07", "Cookie de sesion SameSite=Strict", "SameSite=strict", "SameSite=strict" in acceso or "samesite=strict" in acceso.lower(), "samesite=strict" in acceso.lower())
        chk("T07", "A04", "Cookie de sesion Secure (AUTH_COOKIE_SECURE por defecto true)", "Secure", "Secure" in acceso or "secure" in acceso.lower(), "secure" in acceso.lower())
        chk("T08", "A07", "Cookie con alcance Path=/api (no se envia a /static)", "Path=/api", "path=/api" in acceso.lower(), "path=/api" in acceso.lower())
        tokens = {x.split(";")[0].split("=")[0]: x.split(";")[0].split("=", 1)[1] for x in cookies}
        ck = f"aj_access={tokens['aj_access']}; aj_refresh={tokens['aj_refresh']}"
        r = c.get("/api/ninos", headers={"Cookie": ck})
        chk("T09", "A01", "Con sesion valida la API responde", "200", r.status_code, r.status_code == 200)
        chk("T10", "A02", "Respuestas de la API con Cache-Control: no-store", "no-store", r.headers.get("cache-control"), r.headers.get("cache-control") == "no-store")
        r = c.post("/api/ninos", json={}, headers={"Cookie": ck})
        chk("T11", "A01", "POST con sesion pero sin X-CSRF-Protection (CSRF)", "403", r.status_code, r.status_code == 403)
        r = c.post("/api/ninos", json={}, headers={"Cookie": ck, "X-CSRF-Protection": "1", "Origin": "https://sitio-malicioso.example"})
        chk("T12", "A01", "POST con origen ajeno", "403", r.status_code, r.status_code == 403)
        r = c.post("/api/ninos", json={}, headers={"Cookie": ck, "X-CSRF-Protection": "1", "Origin": URL})
        chk("T13", "A01", "POST del mismo origen con CSRF llega a la validacion", "422", r.status_code, r.status_code == 422)
        r = c.get("/api/ninos", headers={"Cookie": "aj_access=token-falso"})
        chk("T14", "A07", "Token de sesion falso", "401", r.status_code, r.status_code == 401)
        r = c.get("/api/ninos", headers={"Origin": "https://sitio-malicioso.example", "Cookie": ck})
        chk("T15", "A02", "CORS: sin Access-Control-Allow-Origin para origen ajeno", "ausente", r.headers.get("access-control-allow-origin"), "access-control-allow-origin" not in r.headers)
        # --- A05 Inyeccion ---
        base = len(c.get("/api/ninos", headers={"Cookie": ck}).json())
        r1 = c.get("/api/ninos", params={"q": "' OR '1'='1"}, headers={"Cookie": ck})
        r2 = c.get("/api/ninos/dni/1' OR '1'='1", headers={"Cookie": ck})
        r3 = c.get("/api/ninos", params={"estado": "ACTIVO'; DROP TABLE nino;--"}, headers={"Cookie": ck})
        n1 = len(r1.json()) if r1.status_code == 200 else None
        chk("T16", "A05", "Inyeccion SQL en la busqueda de texto (q)", "0 filas o 422", f"{r1.status_code}, {n1} filas", r1.status_code in (200, 422) and (n1 in (0, None)) and base > 0)
        chk("T17", "A05", "Inyeccion SQL en ruta /dni/", "404/422", r2.status_code, r2.status_code in (404, 422))
        r4 = c.get("/api/ninos", headers={"Cookie": ck})
        chk("T18", "A05", "La tabla sigue existente tras `DROP TABLE` en parametro", "200 y mismas filas", f"{r3.status_code}, {len(r4.json())} filas (antes {base})", r4.status_code == 200 and len(r4.json()) == base and base > 0)
        # inyeccion de formulas en el CSV del reporte (CWE-1236)
        from datetime import date as _d

        hoy = _d.today().isoformat()
        cuerpo = {"nino": {"dni": "72777001", "nombres": "=HYPERLINK(\"http://sitio-malicioso.example\",\"clic\")", "apellidos": "+Prueba", "sexo": "F", "fecha_nacimiento": "2025-09-10", "establecimiento": "P. S. Chongos Alto", "distrito": "Chongos Alto", "comunidad": "@SUM(1+1)", "altitud_m": 3720, "tutor_nombre": "Tutor", "tutor_celular": None}, "evaluacion_inicial": {"fecha": hoy, "hemoglobina_observada": 11.6, "peso_kg": 8.4, "talla_cm": 71}}
        rr = c.post("/api/ninos", json=cuerpo, headers={"Cookie": ck, "X-CSRF-Protection": "1", "Origin": URL})
        csv_txt = c.get("/api/reportes/periodo", params={"desde": "2020-01-01", "hasta": hoy, "formato": "csv"}, headers={"Cookie": ck}).text
        celdas_peligrosas = [l for l in csv_txt.splitlines() if "72777001" in l]
        peligro = bool(celdas_peligrosas) and any(t in celdas_peligrosas[0] for t in (',=HYPERLINK', ',"=HYPERLINK', ',@SUM', ',"@SUM'))
        chk("T32", "A05", "Reporte CSV neutraliza celdas que empiezan con = + - @ (inyeccion de formulas, CWE-1236)", "celda con prefijo seguro", f"registro HTTP {rr.status_code}; fila CSV: {celdas_peligrosas[0][:110] if celdas_peligrosas else 'no encontrada'}", rr.status_code == 201 and not peligro, "El CSV escribe nombre y comunidad tal como se registraron: al abrirlo en Excel/LibreOffice una celda con = o @ se evalua como formula.")
        # --- A02 Security Misconfiguration: cabeceras ---
        for ruta, id_ in (("/", "T19"), ("/api/salud", "T20")):
            h = c.get(ruta).headers
            req = {"content-security-policy": "CSP", "x-content-type-options": "nosniff", "x-frame-options": "DENY/SAMEORIGIN o frame-ancestors", "referrer-policy": "Referrer-Policy", "strict-transport-security": "HSTS", "permissions-policy": "Permissions-Policy"}
            faltan = [v for k, v in req.items() if k not in h]
            chk(id_, "A02", f"Cabeceras de seguridad HTTP en {ruta}", "6 de 6 presentes", f"{6 - len(faltan)} de 6; faltan: {', '.join(faltan) or 'ninguna'}", not faltan, "La aplicacion no define estas cabeceras; deben agregarse en la aplicacion o en el proxy (Render).")
        chk("T21", "A02", "Cabecera Server no revela version", "sin Server o generica", c.get("/api/salud").headers.get("server"), "server" not in c.get("/api/salud").headers, "uvicorn identifica el servidor; es informativo.")
        r = c.get("/docs")
        chk("T22", "A02", "Documentacion /docs sin sesion", "401 o 404", r.status_code, r.status_code in (401, 404), "Swagger UI y /openapi.json son publicos: exponen el contrato (no datos).")
        r = c.get("/openapi.json")
        chk("T23", "A02", "/openapi.json sin sesion", "401 o 404", r.status_code, r.status_code in (401, 404))
        # --- A04/A08 webhook ---
        cuerpo = b'{"entry": []}'
        r = c.post("/api/notificaciones/whatsapp/webhook", content=cuerpo, headers={"Content-Type": "application/json"})
        chk("T24", "A08", "Webhook sin WHATSAPP_APP_SECRET falla cerrado", "503", r.status_code, r.status_code == 503)
        r = c.get("/api/notificaciones/whatsapp/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "", "hub.challenge": "1"})
        chk("T25", "A08", "Verificacion del webhook con token vacio", "403", r.status_code, r.status_code == 403)
        # --- A07 fuerza bruta ---
        codigos = [c.post("/api/auth/login", json={"email": "enfermeria@example.test", "password": f"mala{i}"}, headers={"X-CSRF-Protection": "1"}).status_code for i in range(15)]
        chk("T26", "A07", "Limite de intentos de login en la aplicacion (15 intentos fallidos seguidos)", "algun 429/bloqueo", sorted(set(codigos)), 429 in codigos, "No hay bloqueo propio; el limite lo aplica el proveedor (Supabase Auth) y no se pudo medir aqui.")
        # --- A10 manejo de condiciones excepcionales ---
        r = c.post("/api/ninos", content=b"{no es json", headers={"Cookie": ck, "X-CSRF-Protection": "1", "Content-Type": "application/json"})
        chk("T27", "A10", "JSON malformado responde 422 sin traza", "422 sin 'Traceback'", f"{r.status_code}, traza={'Traceback' in r.text}", r.status_code == 422 and "Traceback" not in r.text)
        r = c.get("/api/ninos/00000000-0000-0000-0000-000000000000", headers={"Cookie": ck})
        chk("T28", "A10", "Recurso inexistente responde 404 con mensaje controlado", "404", f"{r.status_code} {r.text[:60]}", r.status_code == 404 and "Traceback" not in r.text)
        r = c.get("/api/ninos/dni/abc", headers={"Cookie": ck})
        chk("T29", "A10", "Parametro invalido no produce 500", "!= 500", r.status_code, r.status_code < 500)
        r = c.post("/api/auth/logout", headers={"Cookie": ck, "X-CSRF-Protection": "1"})
        borradas = [x for x in r.headers.get_list("set-cookie") if "Max-Age=0" in x or "expires" in x.lower()]
        chk("T30", "A07", "Cerrar sesion elimina las cookies", "2 cookies expiradas", len(borradas), len(borradas) == 2)
    finally:
        server.should_exit = True
        th.join(timeout=10)
        sock.close()
        app.state.repositorio.engine.dispose()
    cumple = sum(1 for x in res if x["estado"] == "CUMPLE")
    out = {"comprobaciones": len(res), "cumple": cumple, "hallazgos": len(res) - cumple, "resultados": res}
    (RAIZ / "entregables" / "semana-10" / "metricas" / "salidas" / "OWASP_pruebas_http.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\n{cumple}/{len(res)} comprobaciones CUMPLE; {len(res) - cumple} HALLAZGO")


if __name__ == "__main__":
    main()
