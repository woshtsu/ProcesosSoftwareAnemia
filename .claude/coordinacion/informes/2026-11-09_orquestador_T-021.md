# Informe T-021 — Rendimiento en Render y forma de trabajo de las IA

- **Responsable humano:** Porras Veli, Ricardo · **Asistente:** Claude (orquestador) con Antigravity CLI (`agy`) como desarrollador
- **Rama / commit base:** `main` / `e0f8760` · **Fecha:** 09/11/2026 · **Estado:** HECHO

## Diagnóstico (medido)

| Hallazgo | Evidencia |
| --- | --- |
| Arranque en frío del plan gratuito | `GET /api/salud`: 22,5 s la primera vez, ~0,33 s después |
| Regiones distintas | Render `SoftwareAnemia` en **oregon** (conector de Render); Supabase en **us-east-1** (captura del usuario) |
| Verificación de sesión en cada petición | `supabase_auth.py` abría un `httpx.AsyncClient` por petición |
| Listados completos en memoria | Alertas, visitas, agenda, barreras y recordatorios usan `repo.listar(estado="ACTIVO")` |
| Estáticos sin `Cache-Control` | `swagger-ui-bundle.js` (~1,5 MB) se descargaba en cada visita a `/docs` |

Descartado: migrar a Go. El cuello de botella es la infraestructura y la red, no el lenguaje.

## Cambios

- `pmv_fastapi/app/application/servicio_sesion.py`: caché TTL de la verificación de sesión (60 s, `AUTH_CACHE_TTL_SEGUNDOS`, clave SHA-256, acotada por `exp` del JWT, se invalida en logout).
- `pmv_fastapi/app/adapters/outbound/supabase_auth.py`: cliente `httpx` reutilizado, cerrado en el lifespan.
- `pmv_fastapi/app/adapters/outbound/persistence/sqlalchemy_repo.py`: pool PostgreSQL (3+2, recycle 300 s) y retorno temprano en `_cargar`.
- `pmv_fastapi/app/main.py`: `Cache-Control` (vendor e iconos un día; código propio `no-cache` con ETag/304).
- `pmv_fastapi/Dockerfile`: `exec uvicorn`, `--workers 1`, `--proxy-headers`, puerto `PORT`.
- `.github/workflows/mantener-activo.yml`: ping a `/api/salud` cada 10 min de 07:00 a 22:00 (Lima).
- `AGENTS.md`: sección «Forma de trabajo de las IA»; graphify y skills de `addyosmani/agent-skills` instalados.

Revisión de Claude sobre lo entregado por `agy`: se quitó `db/05_indices_rendimiento.sql` (los índices ya estaban en `01_esquema_postgresql.sql`), se revirtió el versionado `?v=` de `index.html`/`sw.js` (dejaba `auth.js`, `cola.js` y `sync.js` con 1 h de caché sin versión) y se corrigió la documentación.

## Verificación

- `ruff check .` y `ruff format --check .`: conformes.
- `pytest -m "not e2e" --no-cov`: **678 passed** (660 previas + 18 nuevas). E2E no ejecutadas.

## Pendientes

1. Commit, PR y despliegue (Render tiene `autoDeploy` desactivado: desplegar a mano).
2. Recrear el servicio en la región **Virginia** (Render no permite cambiar la región de un servicio existente) y copiar sus variables de entorno.
3. Medir de nuevo en producción. Siguiente optimización si sigue lento: calcular alertas y visitas en SQL en vez de cargar todos los niños.
4. Las 750 h gratuitas se comparten con los 6 servicios `green-ai-*` del mismo workspace.

## Actualización: servicio nuevo en Virginia

- Creado con el conector de Render: `softwareanemia-virginia` (`srv-dbp1fnpsrm7s73aqv7hg`), región **virginia**, plan free, rama `main`, **autoDeploy sí** (por commit), Docker con contexto `pmv_fastapi`.
- Primer despliegue (`e0f8760`) en línea: `https://softwareanemia-virginia.onrender.com/api/salud` responde 200; `/api/auth/config` → `configurado:false`.
- Variables cargadas: `AUTH_MODE=supabase`, `AUTH_CACHE_TTL_SEGUNDOS=60`. **Faltan las secretas**, que el responsable copia desde el servicio anterior: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` y, si se usan, `WHATSAPP_*` y `SMS_*`. Sin `DATABASE_URL` el servicio usa un SQLite efímero.
- El conector no permite fijar el Health Check Path: configurarlo en el panel como `/api/salud`.
- Supabase Auth: añadir la URL nueva en Authentication → URL Configuration si se usan redirecciones.
- `.github/workflows/mantener-activo.yml` ya apunta a la URL nueva. Suspender el servicio antiguo `SoftwareAnemia` (Oregon) lo hace el usuario.

## Actualización: 502 en el servicio de Virginia

- Causa (logs, métricas y medición local con el dataset completo de 11 686 niños): alertas, visitas, agenda, barreras y seguimiento recalculaban `generar_agenda` para todos los niños en cada petición (3-11 s en un PC; minutos con 0,1 CPU). Al abrir la app se lanzan 6-8 de estas peticiones a la vez, el health check `/api/salud` deja de responder y Render reinicia el contenedor (19:11:32 «Shutting down»), lo que produce los 502. No hubo eventos de caída por memoria.
- Corrección (implementada por agy y revisada por Claude): `app/application/cache_agendas.py` guarda una instantánea compartida de niños activos con su agenda, calculada una sola vez aunque haya peticiones concurrentes, invalidada por `version_datos()` en cada escritura de niño, evaluación o asistencia y con TTL `CACHE_AGENDAS_TTL_SEGUNDOS` (300). `PRECALCULAR_AGENDAS=1` la calcula en un hilo al arrancar. Se añadió `limite` opcional en `/api/alertas/controles-vencidos` y `/api/ninos`, y el frontend pide 200.
- Medición local con dataset completo: primer cálculo 2,4 s y luego 0,01-0,3 s por endpoint (antes 6-11 s cada uno). `controles-vencidos` pasa de 23 MB a 131 KB y `ninos` de 4,7 MB a 81 KB.
- Verificación: 690 pruebas y Ruff conformes. E2E no ejecutadas.
- Render: `PRECALCULAR_AGENDAS=1` y `CACHE_AGENDAS_TTL_SEGUNDOS=300` cargadas. **El código sigue sin commit**: los 502 continuarán hasta que se publique en `main` (el despliegue es automático).

## Cierre

- PR #22 fusionado en `main` (`e6d8c4c`) con CI en verde; Render lo desplegó automáticamente en `softwareanemia-virginia`.
- El usuario verificó en producción que los tiempos de respuesta mejoraron y no encontró errores (09/11/2026).
- `main` integrado en `develop` y URL del README actualizada.
- Pendiente fuera de la tarea: suspender el servicio antiguo `SoftwareAnemia` (Oregon).
