# Informe de salida — desarrollador — T-020

- **Agente:** desarrollador
- **Fecha:** 2026-10-30
- **Tareas / solicitudes atendidas:** T-020 (INC-4: recordatorios por WhatsApp y barreras, HIST-4.1 a HIST-4.4)
- **Estado final:** HECHO en el software; tablero EN REVISIÓN (faltan la aprobación de la plantilla por Meta, las credenciales y la validación de las reglas por la microred, ver pendientes)

## Resumen

Se implementó el Incremento 4 completo, versión `4.0.0-inc4`, sin romper el Incremento 3. El sistema genera y envía recordatorios de control por un puerto `Notificador` (simulado por defecto; WhatsApp Cloud API con SMS de respaldo cuando hay credenciales), registra la respuesta del tutor (por el personal o por un webhook firmado), registra barreras de acceso al tratamiento (también sin conexión) y alerta las barreras críticas, que además suman un componente al puntaje de la visita priorizada. **Ninguna prueba hace llamadas de red reales:** WhatsApp y SMS se simulan con `httpx.MockTransport`. Los niños del dataset DIRESA no tienen celular y se cuentan como «sin contacto».

## Archivos creados / modificados / movidos

| Acción | Ruta | Nota |
| --- | --- | --- |
| creado | `pmv_fastapi/app/domain/model/{barrera,notificacion}.py` | Modelos puros |
| creado | `pmv_fastapi/app/domain/service/{barreras,notificaciones}.py` | Reglas de barreras críticas, selección y redacción de recordatorios, interpretación de respuestas, firma y eventos del webhook, métricas |
| creado | `pmv_fastapi/app/ports/inbound/{barreras,notificaciones}.py`, `app/ports/outbound/{notificador,repositorio_barreras,repositorio_recordatorios}.py` | Puertos |
| creado | `pmv_fastapi/app/application/{servicio_barreras,servicio_recordatorios}.py` | Casos de uso |
| creado | `pmv_fastapi/app/adapters/outbound/notificaciones/{__init__,simulado,whatsapp_cloud,sms,respaldo}.py` | Notificadores y `crear_notificador` |
| modificado | `pmv_fastapi/app/domain/model/{errores,sincronizacion}.py`, `app/domain/service/{operaciones,visitas}.py` | Errores nuevos, operación `REGISTRAR_BARRERA`, `PESOS_V2` y componente `BARRERA_CRITICA` |
| modificado | `pmv_fastapi/app/application/{servicio_visitas,servicio_sincronizacion}.py` | Barreras en la lista priorizada y en la cola sin conexión |
| modificado | `pmv_fastapi/app/adapters/inbound/http/{api,esquemas,autenticacion}.py` | 9 endpoints nuevos, DTO, manejadores 409/403 y webhook público (exento de sesión y CSRF solo en esa ruta) |
| modificado | `pmv_fastapi/app/adapters/outbound/persistence/{sqlalchemy_repo,memoria}.py`, `app/main.py`, `pyproject.toml` | Persistencia, composición y versión `4.0.0-inc4` |
| modificado | `pmv_fastapi/app/web/{app.js,index.html,estilos.css,sw.js}` | Pestaña «Recordatorios», barreras en el expediente, barrera asociada a inasistencia y visita, sección «Barreras críticas», service worker `v4` |
| creado | `pmv_fastapi/db/04_migracion_v4_0.sql` | Migración 3.0 a 4.0 (repetible) |
| modificado | `pmv_fastapi/db/{01_esquema_postgresql,02_supabase}.sql`, `docs/openapi.json` | Esquema 4.0, RLS de las tablas nuevas y contrato regenerado (29 rutas) |
| creado | `pmv_fastapi/docs/adr/ADR-014-notificador-y-canales.md` | Decisión; ADR-013 y el índice actualizados |
| modificado | `pmv_fastapi/{CHANGELOG,README,.env.example,docker-compose.yml}`, `docs/DESPLIEGUE.md`, `README.md` (raíz), `coordinacion/TABLERO.md` | Documentación, variables de entorno e historias HIST-4.x con criterios Dado-Cuando-Entonces |
| creado | `pmv_fastapi/tests/unitarias/{test_barreras,test_recordatorios}.py` | 85 pruebas |
| creado | `pmv_fastapi/tests/integracion/{test_notificadores,test_api_inc4,test_repositorio_inc4}.py` | 69 pruebas (notificadores con `MockTransport`, API, repositorio con SQLAlchemy y en memoria) |
| creado | `pmv_fastapi/tests/e2e/test_inc4_notificaciones.py` | 4 E2E |
| modificado | `pmv_fastapi/tests/{conftest.py,arquitectura/test_dependencias.py}`, cinco pruebas de integración y una unitaria (aserciones de versión y constructor) | TRUNCATE de las tablas nuevas y reglas CP-398 a CP-401 |

## Verificación realizada

- `pytest --cov=app` (sin `tests/rendimiento`): **657 aprobadas** (416 unitarias, 216 de integración, 25 de arquitectura; 499 antes del incremento), cobertura total **99,79 %** (línea base 99,70 %); 100 % en todos los archivos nuevos. Solo quedan por debajo `autenticacion.py` (94 %) y `supabase_auth.py` (97 %), anteriores al incremento.
- `pytest tests/e2e`: **28 aprobadas** (24 anteriores y 4 nuevas: recordatorios simulados con respuesta `NO_PUEDE` y alerta de barrera crítica, barrera sin conexión que sincroniza, barrera asociada a una inasistencia, barrera de una visita no lograda con su componente en el puntaje).
- `ruff check .`: sin hallazgos; `ruff format --check .`: correcto. `python -m scripts.exportar_openapi --verificar`: al día.
- PostgreSQL 16 temporal (con los roles `anon` y `authenticated` de Supabase): instalación limpia (01 y 02) y migración desde el esquema 3.0 con `04_migracion_v4_0.sql` ejecutada dos veces más `02_supabase.sql`; los esquemas resultantes son idénticos, RLS activa en `recordatorio` y `barrera` y sin acceso para `anon` ni `authenticated`; las 216 pruebas de integración pasan con `TEST_DATABASE_URL` sobre ambas bases.
- Búsqueda de las palabras prohibidas y de rutas absolutas en `pmv_fastapi/`: sin coincidencias. Los datos son solo sintéticos o del dataset seudonimizado.

## Decisiones y desviaciones de la especificación

- **Vigencia de 90 días de una barrera** para la alerta: la especificación no la fija; sin ella una barrera antigua alertaría para siempre (ADR-014).
- **Barrera desde la inasistencia y la visita:** la barrera se sugiere y se registra desde la interfaz con su fuente (`INASISTENCIA`, `VISITA`), no dentro de los servicios de asistencia y de visita, para no acoplar casos de uso independientes. Desde la respuesta `NO_PUEDE` sí se registra en el mismo acto, validando todo antes de guardar.
- **Operación `REGISTRAR_BARRERA` en la cola sin conexión** (opcional en la especificación): una barrera es un hecho, así que si ya existe se responde `DUPLICADA` con su id en lugar de abrir un conflicto. Los recordatorios y sus respuestas **no** se encolan (el envío ocurre en el servidor y una respuesta sin conexión podría chocar con la del webhook).
- **Puntaje de visita:** `PESOS_V2` suma `BARRERA_CRITICA` (15 o 8 puntos) solo a quien tiene alerta de barreras; el rango es 0 a 100 sin barreras y hasta 115 con ellas. Se conserva `PESOS_V1` para no alterar las pruebas ni el orden de INC-3.
- **Tasa de entrega:** excluye los envíos simulados (no se entregan); la tasa de confirmación se calcula sobre todo lo enviado.
- **Reintento:** un recordatorio `FALLIDO` se reintenta en la siguiente generación sobre el mismo registro (campo `intentos`).
- **Webhook sin secreto:** falla cerrado (corregido en la revisión independiente, ver abajo): sin `WHATSAPP_APP_SECRET` el `POST` responde 503 y no procesa nada; con secreto exige la firma (403 si falta o es inválida). Debe configurarse para recibir eventos de WhatsApp.
- **Prioridad de la alerta de barreras:** solo `ALTA` o `MEDIA` (422 con `BAJA`).
- Las respuestas por SMS no se reciben.

## Pendientes y riesgos

- La plantilla `recordatorio_control` debe ser aprobada por Meta (riesgo S3-4); mientras tanto el modo simulado permite demostrar el flujo. Falta probar el envío real con credenciales de prueba (no se hizo por regla del encargo).
- Configurar `WHATSAPP_APP_SECRET` (obligatorio: sin él el webhook responde 503) y `WHATSAPP_VERIFY_TOKEN` en Render y registrar el webhook en Meta.
- Validar con la microred las reglas de barreras críticas, la vigencia de 90 días y el peso de `BARRERA_CRITICA`.
- El celular del tutor viaja a Meta o al proveedor SMS: requiere el consentimiento de la familia, que el software no gestiona.
- La generación de recordatorios es manual y síncrona; para un volumen mayor convendría una tarea programada y una cola de envío.
- No se agregaron tareas de carga de Locust para los endpoints nuevos.
- Ejecutar `db/04_migracion_v4_0.sql` y luego `db/02_supabase.sql` en Supabase antes de desplegar la versión 4.0 (ver `docs/DESPLIEGUE.md`).

## Solicitudes abiertas a otros agentes

Ninguna.

## Revisión independiente

Revisión de calidad y seguridad hecha después de la entrega, sobre `git diff a8df23b..HEAD`. Veredicto: aprobado con observaciones; las historias HIST-3.1 a 3.4, VIS-3.5 y HIST-4.1 a 4.4 cumplen la especificación.

**Corregido**
- **Seguridad, alta: el webhook aceptaba cuerpos sin firma si no se configuraba `WHATSAPP_APP_SECRET`.** Al ser una ruta pública, cualquiera podía registrar respuestas del tutor o alterar estados de entrega. Ahora falla cerrado: sin secreto el `POST` responde **503** («El webhook está deshabilitado: falta configurar WHATSAPP_APP_SECRET.») y no procesa nada; con secreto exige la firma `X-Hub-Signature-256` (403 si falta o es inválida). Nuevo error de dominio `WebhookNoConfigurado`, manejador único 403/503 en la API, contrato OpenAPI regenerado y documentado en ADR-014, `docs/DESPLIEGUE.md`, `.env.example`, README y CHANGELOG. Pruebas ajustadas (CP-357, CP-391, CP-396) y nueva CP-391b (con secreto se ignora lo irreconocible).
- **Concurrencia, media: reenvío simultáneo del mismo `id_operacion` duplicaba una evaluación** (la base no tiene restricción propia para evaluaciones; la clave primaria de la bitácora solo detenía el registro de la operación, después de crear el recurso). Se reprodujo con hilos y ahora `ServicioSincronizacion` procesa un lote o una resolución a la vez por proceso (cerrojo), de modo que el segundo envío responde `DUPLICADA`. Con varios procesos sigue valiendo la clave primaria como última defensa. Prueba nueva CP-264b (falla sin el cerrojo).
- **Concurrencia, media: dos generaciones simultáneas de recordatorios enviaban dos veces el mismo mensaje** (la restricción UNIQUE solo evitaba la segunda fila). `ServicioRecordatorios` serializa la generación, el registro de respuestas y los avisos de entrega. Prueba nueva CP-382b (falla sin el cerrojo).
- **Interfaz, baja:** en una visita no lograda con barrera, las observaciones (hasta 500 caracteres) se copiaban como detalle de la barrera (máximo 200) y el servidor la rechazaba; ahora se recorta a 200. Los campos DNI y celular de las tablas nuevas («Barreras críticas» y «Visitas») pasan por `esc()` por consistencia (ya los validaba el servidor).

**Observaciones sin corregir (aceptables para el piloto)**
- El caché de datos del service worker se borra solo al cerrar sesión, no al vencer la sesión; se descartó borrarlo ante un 401 porque el vencimiento normal del token de acceso vaciaría el caché sin conexión. La cola de pendientes (IndexedDB) conserva datos clínicos tras cerrar sesión por diseño (ADR-012).
- Un tutor con varios niños que responde sin citar el mensaje (sin `context.id`) se asocia al recordatorio sin respuesta más reciente de su número; con la respuesta citada es exacto.
- `id_operacion` se compara tal cual: un UUID en mayúsculas y el mismo en minúsculas serían operaciones distintas (el cliente siempre genera minúsculas). No hay límite de tamaño del cuerpo del webhook ni de `datos` por operación más allá del que imponga el servidor o el proxy.

**Verificación posterior:** `pytest --cov=app` (sin `tests/rendimiento`): **660 aprobadas**, cobertura total **99,79 %** (100 % en todos los archivos nuevos); `pytest tests/e2e`: **28 aprobadas**; `ruff check .` y `ruff format --check .` limpios; `scripts.exportar_openapi --verificar` al día. Sin las palabras prohibidas ni rutas absolutas en lo nuevo.
