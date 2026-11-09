# Avance de la sesión en curso

Archivo vivo para continuar el trabajo en un chat nuevo. Actualizarlo durante la sesión. Al cerrar la tarea, mover el detalle a `coordinacion/informes/` y dejar aquí solo el enlace.

## Tarea actual

- **Responsable humano:** Porras Veli, Ricardo
- **Asistente:** Claude (orquestador)
- **Rama / commit base:** `main` / `e0f8760`
- **Fecha:** 09/11/2026

## Hecho

- `AGENTS.md`: nueva sección «Forma de trabajo de las IA» (agy para trabajo pesado, subagentes baratos, graphify, este archivo, skills).
- graphify instalado y grafo generado en `graphify-out/` (ignorado por Git).
- Skills de `addyosmani/agent-skills` copiadas en `.claude/skills/`.
- Análisis de rendimiento del despliegue en Render (plan gratuito) con propuesta de optimizaciones.

## Hallazgos de rendimiento (09/11/2026)

- Arranque en frío medido: `GET /api/salud` tardó 22,5 s; en caliente responde en unos 0,33 s. Render ya comprime con gzip.
- Cada petición clínica llama a Supabase `/auth/v1/user` y abre un `httpx.AsyncClient` nuevo, con un handshake TLS cada vez (`supabase_auth.py:34`).
- Alertas, visitas, agenda, barreras y recordatorios hacen `repo.listar(estado="ACTIVO")` y cargan todos los niños con todas sus evaluaciones y asistencias para calcular en Python. Con el dataset (unos 12.500 registros) esto es caro para 0,1 CPU.
- Los estáticos no tienen `Cache-Control`.
- Decisión: no migrar a Go. El cuello de botella son el arranque en frío, la red y las consultas, no el lenguaje.

## Pendientes / siguiente paso

- Tarea **T-021** registrada en el tablero; informe: `coordinacion/informes/2026-11-09_orquestador_T-021.md`.
- Código implementado y verificado (678 pruebas, ruff). **Sin commit ni push.**
- Siguiente: commit/PR → desplegar en Render (autoDeploy desactivado) → recrear el servicio en Virginia → medir de nuevo.

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
