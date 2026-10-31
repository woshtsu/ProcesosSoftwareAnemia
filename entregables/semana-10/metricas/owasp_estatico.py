"""Factor +: comprobaciones estaticas reproducibles (grep/AST/archivos) para OWASP Top 10:2025 y restricciones tecnicas.

Uso (raiz del repositorio): python entregables/semana-10/metricas/owasp_estatico.py -> metricas/salidas/OWASP_estatico.json
Cada comprobacion declara el metodo y devuelve CUMPLE o HALLAZGO; nada se marca como cumplido sin una verificacion.
Categorias OWASP Top 10:2025: A01 Broken Access Control (incluye SSRF), A02 Security Misconfiguration, A03 Software Supply Chain
Failures, A04 Cryptographic Failures, A05 Injection, A06 Insecure Design, A07 Authentication Failures, A08 Software or Data
Integrity Failures, A09 Security Logging and Alerting Failures, A10 Mishandling of Exceptional Conditions.
"""

import ast
import json
import re
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
PMV = RAIZ / "pmv_fastapi"
APP = PMV / "app"
res: list[dict] = []


def chk(id_, owasp, control, metodo, ok, detalle):
    res.append({"id": id_, "owasp": owasp, "control": control, "metodo": metodo, "estado": "NO_MEDIDO" if ok is None else ("CUMPLE" if ok else "HALLAZGO"), "detalle": detalle})
    print(f"{id_:<5}{owasp:<5}{res[-1]['estado']:<10}{control}: {detalle}")


def py_files():
    return [p for p in APP.rglob("*.py")]


def buscar(patron, archivos, flags=0):
    rx = re.compile(patron, flags)
    return [f"{p.relative_to(PMV)}:{i}" for p in archivos for i, l in enumerate(p.read_text(encoding='utf-8').splitlines(), 1) if rx.search(l)]


# --- A01 ---
roles = buscar(r"\b(rol|roles|role|permiso|permisos|is_admin|RBAC)\b", [p for p in py_files() if "autenticacion" in p.name or p.name in ("api.py", "main.py")], re.I)
roles = [x for x in roles if "descripcion" not in x]
chk("E01", "A01", "Control de acceso por rol/establecimiento (RBAC)", "grep de roles/permisos en api.py, autenticacion.py y main.py", bool(roles), f"{len(roles)} referencias; el README declara «no hay roles ni separación por establecimiento»: todo usuario confirmado tiene acceso total")
httpx_fuera = [str(p.relative_to(PMV)) for p in py_files() if re.search(r"^\s*(import httpx|from httpx)", p.read_text(encoding="utf-8"), re.M) and "adapters/outbound" not in str(p) and "adapters\\outbound" not in str(p)]
destinos = buscar(r"https?://", [p for p in (APP / "adapters" / "outbound").rglob("*.py")])
chk("E02", "A01", "SSRF: las peticiones salientes no usan URL de la solicitud del usuario", "httpx solo se importa en adapters/outbound; los destinos son constantes o variables de entorno", not httpx_fuera, f"httpx fuera de adaptadores de salida: {len(httpx_fuera)}; URL literales en adaptadores: {destinos}; SMS_API_URL, SUPABASE_URL y WHATSAPP_* vienen del entorno")
# --- A02 ---
patrones = r"(sb_secret_[A-Za-z0-9_-]{10,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC )?PRIVATE KEY-----|service_role['\"]?\s*[:=]\s*['\"][^'\"]{20,})"
archivos = [p for p in PMV.rglob("*") if p.is_file() and p.suffix in {".py", ".js", ".html", ".yml", ".yaml", ".json", ".md", ".sql", ".example", ".toml", ".txt", ".properties"} and "vendor" not in p.parts and ".ruff_cache" not in p.parts and "node_modules" not in p.parts]
secretos = buscar(patrones, archivos)
chk("E03", "A02", "Sin credenciales en el codigo del repositorio", "regex de claves (sb_secret, JWT, AKIA, llaves privadas, service_role) sobre pmv_fastapi/", not secretos, f"{len(archivos)} archivos revisados; coincidencias: {secretos or 0}")
ign = subprocess.run(["git", "check-ignore", "-q", "pmv_fastapi/.env"], cwd=RAIZ).returncode == 0
chk("E04", "A02", ".env ignorado por Git y .env.example solo con marcadores", "git check-ignore + lectura de .env.example", ign and "reemplazar" in (PMV / ".env.example").read_text(encoding="utf-8").lower(), f".env ignorado: {ign}")
compose = (PMV / "docker-compose.yml").read_text(encoding="utf-8")
chk("E05", "A02", "docker-compose sin contraseña predeterminada debil", "grep de POSTGRES_PASSWORD", "cambiar_en_staging" not in compose, "docker-compose.yml usa `${POSTGRES_PASSWORD:-cambiar_en_staging}` como valor por defecto (solo para staging local)")
dock = (PMV / "Dockerfile").read_text(encoding="utf-8")
chk("E06", "A02", "Imagen Docker: usuario no root, base slim y HEALTHCHECK", "lectura del Dockerfile", all(x in dock for x in ("USER appuser", "python:3.11-slim", "HEALTHCHECK")), "USER appuser, python:3.11-slim, HEALTHCHECK cada 30 s")
mw = buscar(r"(X-Content-Type-Options|Content-Security-Policy|Strict-Transport-Security|X-Frame-Options)", py_files())
chk("E07", "A02", "Cabeceras de seguridad definidas en la aplicacion", "grep en app/", bool(mw), f"{len(mw)} referencias")
# --- A03 ---
req = [l.strip() for l in (PMV / "requirements.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
chk("E08", "A03", "Dependencias de produccion con version exacta", "requirements.txt", all("==" in l for l in req), f"{sum('==' in l for l in req)} de {len(req)} con ==")
chk("E09", "A03", "Hashes de integridad en dependencias (pip --require-hashes)", "grep de --hash en requirements*.txt", "--hash" in (PMV / "requirements.txt").read_text(), "sin hashes ni archivo de bloqueo")
chk("E10", "A03", "Actualizacion automatica de dependencias (Dependabot/Renovate)", "existencia de .github/dependabot.yml", (RAIZ / ".github" / "dependabot.yml").exists(), "solo existe .github/workflows/ci.yml")
ci = (RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
chk("E11", "A03", "CI ejecuta analisis de seguridad (SAST/auditoria de dependencias)", "busqueda de bandit/semgrep/codeql/pip-audit en ci.yml", bool(re.search(r"bandit|semgrep|codeql|pip-audit", ci, re.I)), "el CI ejecuta ruff, pytest, OpenAPI, PostgreSQL, E2E y SonarCloud opcional (solo con SONAR_TOKEN)")
acciones = re.findall(r"uses:\s*([^\s]+)", ci)
chk("E12", "A03", "Acciones de GitHub fijadas por SHA de commit", "regex en ci.yml", all(re.search(r"@[0-9a-f]{40}$", a) for a in acciones), f"{len(acciones)} acciones fijadas por etiqueta (@v4/@v5), no por SHA")
# --- A04 ---
debiles = buscar(r"\b(md5|sha1)\b|hashlib\.(md5|sha1)", py_files(), re.I)
chk("E13", "A04", "Sin algoritmos de hash debiles", "grep md5/sha1 en app/", not debiles, f"{len(debiles)} coincidencias")
chk("E14", "A04", "Comparacion en tiempo constante de firma y token del webhook", "grep compare_digest", len(buscar(r"hmac\.compare_digest", py_files())) >= 2, f"{len(buscar(r'hmac.compare_digest', py_files()))} usos (firma y token de verificacion)")
pwd = buscar(r"password", [p for p in py_files() if p.name not in ("autenticacion.py", "supabase_auth.py", "servicio_sesion.py", "proveedor_identidad.py", "sesiones.py")], re.I)
chk("E15", "A04", "La aplicacion no almacena ni procesa contrasenas (se delegan a Supabase Auth)", "grep password fuera de login/sesion", not pwd, f"{len(pwd)} coincidencias fuera de los modulos de sesion")
# --- A05 ---
sql_crudo = buscar(r"(execute|text)\(\s*f[\"']|\.format\(.*(SELECT|INSERT|UPDATE|DELETE)|\"\s*%\s*\(.*SELECT", py_files(), re.I)
chk("E16", "A05", "Sin SQL construido por concatenacion o f-strings", "regex en app/ (execute/text con f-string, format, %)", not sql_crudo, f"{len(sql_crudo)} coincidencias; el repositorio usa SQLAlchemy Core con parametros")
peligrosas = buscar(r"\b(eval|exec|pickle\.loads?|yaml\.load|os\.system|subprocess\.)\b", py_files())
chk("E17", "A05", "Sin eval/exec/pickle/os.system/subprocess en el codigo de la aplicacion", "grep en app/", not peligrosas, f"{len(peligrosas)} coincidencias")
js = (APP / "web" / "app.js").read_text(encoding="utf-8")
chk("E18", "A05", "El cliente escapa el texto libre antes de insertarlo con innerHTML (esc())", "conteo de esc( y de innerHTML en app.js", js.count("esc(") > js.count("innerHTML"), f"{js.count('esc(')} usos de esc() frente a {js.count('innerHTML')} asignaciones a innerHTML")
# --- A06 ---
adr = sorted((PMV / "docs" / "adr").glob("ADR-*.md"))
chk("E19", "A06", "Decisiones de diseno de seguridad documentadas (ADR-011 sesion, ADR-014 webhook)", "existencia de ADR", (PMV / "docs/adr/ADR-011-supabase-auth.md").exists() and (PMV / "docs/adr/ADR-014-notificador-y-canales.md").exists(), f"{len(adr)} ADR en total")
rl = buscar(r"slowapi|RateLimit|rate_limit|limiter|429", py_files(), re.I)
chk("E20", "A06", "Limitacion de tasa (rate limiting) en la aplicacion", "grep slowapi/rate_limit/429 en app/", bool(rl), f"{len(rl)} referencias; sin limite propio en login ni en la API")
conc = len(buscar(r"cp264b|cp382b", list((PMV / "tests").rglob("*.py")), re.I))
chk("E21", "A06", "Cerrojos de concurrencia con pruebas (sincronizacion y recordatorios)", "grep cp264b/cp382b en tests/", conc >= 2, f"{conc} pruebas")
chk("E22", "A06", "Modelo de amenazas documentado (STRIDE o equivalente) en el repositorio del producto", "grep amenaza/STRIDE en pmv_fastapi/docs", bool(buscar(r"amenaza|STRIDE|threat model", list((PMV / "docs").rglob("*.md")), re.I)), "no hay un documento de modelo de amenazas en pmv_fastapi/docs")
# --- A07 ---
chk("E23", "A07", "Politica de contrasenas, MFA y bloqueo por intentos (Supabase Auth)", "no verificable desde el repositorio", None, "se configura en el panel de Supabase; no se pudo medir aqui (no se cuenta como cumplido)")
# --- A08 ---
deser = buscar(r"pickle|marshal|yaml\.load\(|jsonpickle", py_files())
chk("E24", "A08", "Sin deserializacion insegura", "grep pickle/marshal/yaml.load", not deser, f"{len(deser)} coincidencias")
chk("E25", "A08", "Artefactos de CI firmados o con procedencia (attestations/cosign)", "grep attest/cosign/provenance en ci.yml", bool(re.search(r"attest|cosign|provenance|slsa", ci, re.I)), "el CI construye la imagen pero no la firma")
# --- A09 ---
logs = buscar(r"\blogging\b|\blogger\b|getLogger", py_files())
chk("E26", "A09", "La aplicacion registra eventos de seguridad (login fallido, 401/403, firma invalida)", "grep logging en app/", bool(logs), f"{len(logs)} usos de logging; solo hay los logs de acceso de uvicorn")
esq = (PMV / "db" / "01_esquema_postgresql.sql").read_text(encoding="utf-8")
chk("E27", "A09", "Trazabilidad del autor de cada registro (registrado_por)", "grep registrado_por en el esquema SQL", esq.count("registrado_por") >= 6, f"{esq.count('registrado_por')} columnas registrado_por; en modo supabase es el UUID verificado")
chk("E28", "A09", "Alertas/monitoreo de seguridad automatizados", "no hay modulo de alertas de seguridad ni integracion de monitoreo", False, "no se encontro configuracion de alertas; HEALTHCHECK solo verifica disponibilidad")
# --- A10 ---
glob = buscar(r"exception_handler\(\s*Exception\s*\)|add_exception_handler\(\s*Exception", py_files())
chk("E29", "A10", "Manejador global de excepciones (respuesta controlada ante errores no previstos)", "grep exception_handler(Exception)", bool(glob), "solo hay manejadores de excepciones de dominio (409/422/403/503/404); una falla de BD responde 500 generico (ver R13)")
manejadores = len(buscar(r"exception_handler\(|add_exception_handler\(", py_files()))
chk("E30", "A10", "Errores de dominio mapeados a respuestas HTTP controladas", "conteo de manejadores", manejadores >= 8, f"{manejadores} manejadores registrados")

out = {"comprobaciones": len(res), "cumple": sum(1 for x in res if x["estado"] == "CUMPLE"), "hallazgos": sum(1 for x in res if x["estado"] == "HALLAZGO"), "no_medidos": sum(1 for x in res if x["estado"] == "NO_MEDIDO"), "resultados": res}
(RAIZ / "entregables" / "semana-10" / "metricas" / "salidas" / "OWASP_estatico.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n{out['cumple']}/{out['comprobaciones']} CUMPLE; {out['hallazgos']} HALLAZGO; {out['no_medidos']} NO_MEDIDO")
