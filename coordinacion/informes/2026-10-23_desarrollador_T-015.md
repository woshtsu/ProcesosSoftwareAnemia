# Informe de salida — desarrollador — T-015

- **Agente:** desarrollador / orquestador (secuencial)
- **Fecha:** 2026-10-23
- **Tareas / solicitudes atendidas:** T-015, ORQ-006
- **Estado final:** PARCIAL (implementación local verificada; activación de la primera cuenta diferida por el usuario)

## Resumen

Se implementó login por correo y contraseña con Supabase Auth, recuperación/renovación de sesión y cierre. La API clínica y los CSV exigen identidad verificada; el UUID de Supabase reemplaza al selector de auditoría. La sesión se guarda en cookies HttpOnly y la API bloquea peticiones CSRF. Se conserva la arquitectura hexagonal y la persistencia actual, sin migrar tablas. El usuario indicó que creará la primera cuenta después de salir del laboratorio.

## Archivos creados / modificados / movidos

| Acción | Ruta | Nota |
| --- | --- | --- |
| creados | Modelo, puertos, servicio y adaptadores registrados en ORQ-006 | Sesiones independientes del proveedor y del framework |
| modificados | `pmv_fastapi/app/main.py`, `app/adapters/inbound/http/api.py` | Composición, protección global y auditoría con UUID |
| creados / modificados | `pmv_fastapi/app/web/auth.js`, `index.html`, `app.js`, `estilos.css`, `sw.js` | Login adaptable, acceso y cierre; sin tokens ni borradores clínicos persistentes en modo autenticado |
| creado | `pmv_fastapi/.env.example` | Plantilla sin credenciales reales |
| creado localmente | `pmv_fastapi/.env` | Configuración proporcionada por el usuario, ignorada por Git; no se reproducen claves en el informe |
| modificados | `pmv_fastapi/requirements.txt`, `requirements-dev.txt`, `docker-compose.yml` | HTTPX pasa a dependencia de ejecución y variables Auth en Docker |
| creados | `pmv_fastapi/tests/integracion/test_autenticacion.py`, `tests/e2e/test_login.py` | Proveedor simulado, acceso, cookies, CSRF, renovación, auditoría y navegador |
| modificado | `pmv_fastapi/tests/conftest.py` | Demo explícita en pruebas históricas |
| modificados | `pmv_fastapi/README.md`, `docs/openapi.json`, `docs/adr/README.md` | Inicio local, configuración y contrato actualizado |
| creado | `pmv_fastapi/docs/adr/ADR-011-supabase-auth.md` | Decisión, fuentes y límites |
| modificados | `coordinacion/RUTAS.md`, `coordinacion/TABLERO.md` | Registro y continuidad |

## Verificación realizada

- `python -m pytest --cov=app --cov-report=term -q`: **349 pruebas aprobadas**, cobertura **99,50 %** (1 675 sentencias y 308 ramas). Incluye 21 casos nuevos de integración/proveedor; los 328 anteriores siguen aprobados.
- `python -m pytest tests/e2e/test_login.py -m e2e -q --no-cov`: **2 aprobadas** (1366 × 900 y 390 × 844). Comprueban error de credenciales, ingreso, identidad, recarga y cierre; Supabase simulado.
- Regresión completa `python -m pytest tests/e2e -m e2e -q --no-cov`: **17 aprobadas** (las 15 anteriores y las 2 de login). La primera ejecución detectó que los servidores de alcance de módulo arrancaban antes del fixture de modo demo; se corrigieron ambos fixtures E2E para pasar `AUTH_MODE=demo` explícitamente al servidor. La ejecución completa posterior pasó en 24,56 s.
- Capturas temporales `diagramas/_build/auth/login-1366.png` y `login-390.png`: inspección visual sin desbordamientos; no son evidencia de login contra una cuenta remota.
- Ruff: sin hallazgos; formato comprobado y ajustado en los archivos nuevos.
- `python -m scripts.exportar_openapi --verificar`: contrato al día.
- `git check-ignore pmv_fastapi/.env`: configuración real excluida del versionado.
- `git diff --check`: sin errores.
- Conexión real de solo lectura a `/auth/v1/settings` usando la clave pública: HTTP 200, Email habilitado, confirmación automática deshabilitada. El registro público estaba permitido en el momento de la comprobación.
- No se crearon usuarios ni se intentó iniciar sesión contra cuentas reales. No se guardan contraseñas de usuarios.

## Pendientes y riesgos

- El usuario difirió crear la primera cuenta: desactivar **Allow new users to sign up**, crear un usuario de Email con correo confirmado y probar el acceso desde el navegador. Hasta entonces T-015 permanece EN REVISIÓN.
- Todos los usuarios confirmados del proyecto tienen acceso a las mismas funciones. Roles y autorización por establecimiento pendientes; no utilizar el registro público para provisionar personal.
- Para retomar desde `pmv_fastapi/`: `.\.venv\Scripts\python.exe -m uvicorn app.main:crear_app --factory --env-file .env --reload --port 8000`; abrir `http://127.0.0.1:8000`. Usar el correo y contraseña creados en el panel, sin enviarlos al chat.
- Las variables del proyecto quedaron únicamente en el `.env` de este equipo. Si se continúa en otra computadora se deben volver a configurar; `.env.example` contiene la plantilla.
- HTTP local usa `AUTH_COOKIE_SECURE=false`; HTTPS debe usar `true`.
- Se consulta Supabase al validar cada petición clínica; requiere conexión y añade latencia. Una caída del proveedor responde 503 y no habilita acceso anónimo.
- La base de datos aún es la configurada en `DATABASE_URL` (SQLite por defecto). Migración a PostgreSQL de Supabase y RLS pendientes de la siguiente etapa.
- No se crearon commits ni pushes. Los cambios de la síntesis de feria previos se conservaron.

## Solicitudes abiertas a otros agentes

Ninguna nueva. ORQ-006 resuelta para el registro de rutas; la activación remota queda pendiente del usuario.
