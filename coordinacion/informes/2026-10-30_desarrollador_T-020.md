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
- **Webhook sin secreto:** si no se configura `WHATSAPP_APP_SECRET` acepta cuerpos sin firma (comodidad de la demo); con secreto exige la firma. Debe configurarse en producción.
- **Prioridad de la alerta de barreras:** solo `ALTA` o `MEDIA` (422 con `BAJA`).
- Las respuestas por SMS no se reciben.

## Pendientes y riesgos

- La plantilla `recordatorio_control` debe ser aprobada por Meta (riesgo S3-4); mientras tanto el modo simulado permite demostrar el flujo. Falta probar el envío real con credenciales de prueba (no se hizo por regla del encargo).
- Configurar `WHATSAPP_APP_SECRET` y `WHATSAPP_VERIFY_TOKEN` en Render y registrar el webhook en Meta.
- Validar con la microred las reglas de barreras críticas, la vigencia de 90 días y el peso de `BARRERA_CRITICA`.
- El celular del tutor viaja a Meta o al proveedor SMS: requiere el consentimiento de la familia, que el software no gestiona.
- La generación de recordatorios es manual y síncrona; para un volumen mayor convendría una tarea programada y una cola de envío.
- No se agregaron tareas de carga de Locust para los endpoints nuevos.
- Ejecutar `db/04_migracion_v4_0.sql` y luego `db/02_supabase.sql` en Supabase antes de desplegar la versión 4.0 (ver `docs/DESPLIEGUE.md`).

## Solicitudes abiertas a otros agentes

Ninguna.
