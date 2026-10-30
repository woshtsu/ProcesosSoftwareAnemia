# Informe de salida — desarrollador — T-019

- **Agente:** desarrollador
- **Fecha:** 2026-10-30
- **Tareas / solicitudes atendidas:** T-019 (INC-3: sin conexión y sincronización + visita domiciliaria priorizada)
- **Estado final:** HECHO en el software; tablero EN REVISIÓN (faltan validación del equipo y de la microred, ver pendientes)

## Resumen

Se implementó el Incremento 3 completo (HIST-3.1 a HIST-3.4 y VIS-3.5), versión `3.0.0-inc3`, sin tocar el Incremento 4. Sin conexión, la PWA guarda niños, evaluaciones, asistencias y visitas en una cola de IndexedDB y las envía por lotes a `POST /api/sincronizacion`, que es idempotente por `id_operacion`, mapea los niños creados sin conexión, detecta conflictos con reglas de dominio puras y nunca sobrescribe a ciegas. La visita domiciliaria priorizada usa un puntaje explicable cuyos pesos son una propuesta del equipo y no una norma del MINSA. Se documentaron ADR-012 y ADR-013, la migración SQL y qué ejecutar al desplegar.

## Archivos creados / modificados / movidos

| Acción | Ruta | Nota |
| --- | --- | --- |
| creado | `pmv_fastapi/app/domain/model/{visita,sincronizacion}.py` | Modelos puros |
| creado | `pmv_fastapi/app/domain/service/{visitas,conflictos,operaciones}.py` | Puntaje, reglas de conflicto y normalización de operaciones |
| creado | `pmv_fastapi/app/ports/inbound/{visitas,sincronizacion}.py`, `app/ports/outbound/{repositorio_visitas,repositorio_sincronizacion}.py` | Puertos |
| creado | `pmv_fastapi/app/application/{servicio_visitas,servicio_sincronizacion}.py` | Casos de uso |
| modificado | `pmv_fastapi/app/adapters/inbound/http/{api,esquemas}.py`, `app/domain/model/errores.py`, `app/ports/outbound/repositorio_ninos.py` | Endpoints, DTO, errores 409 y dos métodos de repositorio |
| modificado | `pmv_fastapi/app/adapters/outbound/persistence/{sqlalchemy_repo,memoria}.py`, `app/main.py` | Persistencia, composición y `VERSION = "3.0.0-inc3"` |
| creado | `pmv_fastapi/app/web/{cola,sync}.js` | Cola IndexedDB y motor de sincronización |
| modificado | `pmv_fastapi/app/web/{app.js,index.html,estilos.css,sw.js,auth.js}` | Registro sin conexión, indicador, pestañas «Visitas» y «Sincronización», service worker con caché de lecturas, borrado del caché al cerrar sesión |
| creado | `pmv_fastapi/db/03_migracion_v3_0.sql` | Migración 2.0 a 3.0 (repetible) |
| modificado | `pmv_fastapi/db/{01_esquema_postgresql,02_supabase}.sql`, `pmv_fastapi/pyproject.toml`, `pmv_fastapi/docs/openapi.json` | Esquema 3.0, RLS, versión y contrato regenerado |
| creado | `pmv_fastapi/docs/adr/ADR-012-sincronizacion-sin-conexion.md`, `ADR-013-visita-domiciliaria-priorizada.md` | Decisiones; índice en `docs/adr/README.md` |
| modificado | `pmv_fastapi/{CHANGELOG,README}.md`, `pmv_fastapi/docs/DESPLIEGUE.md`, `README.md` (raíz), `coordinacion/TABLERO.md` | Documentación e historias HIST-3.x y VIS-3.5 con criterios Dado-Cuando-Entonces |
| creado | `pmv_fastapi/tests/unitarias/{test_visitas,test_conflictos,test_sincronizacion}.py` | 97 pruebas |
| creado | `pmv_fastapi/tests/integracion/{test_api_inc3,test_repositorio_inc3}.py` | 50 pruebas (el repositorio, con SQLAlchemy y en memoria) |
| creado | `pmv_fastapi/tests/e2e/test_inc3_sin_conexion.py` | 7 E2E con `set_offline` |
| modificado | `pmv_fastapi/tests/{conftest.py,arquitectura/test_dependencias.py}` y 4 pruebas de integración | TRUNCATE de tablas nuevas, reglas CP-294 a CP-296 y aserciones de versión |

## Verificación realizada

- `pytest --cov=app`: **499 aprobadas** (331 unitarias, 147 de integración, 21 de arquitectura; 349 antes del incremento), cobertura total **99,70 %** (umbral exigido 99,55 %); 100 % en todos los archivos nuevos. Solo quedan por debajo `autenticacion.py` (94 %) y `supabase_auth.py` (97 %), anteriores al incremento.
- `pytest tests/e2e`: **24 aprobadas** (17 anteriores y 7 nuevas). La recarga sin conexión se prueba apagando el servidor además de `set_offline(True)`, porque Chromium no aplica `set_offline` a las peticiones del service worker.
- `ruff check .`: sin hallazgos; `ruff format --check .`: correcto. `python -m scripts.exportar_openapi --verificar`: al día.
- PostgreSQL 16 temporal: instalación limpia (01 y 02), migración desde el esquema 2.0 con `03_migracion_v3_0.sql` ejecutada dos veces y `02_supabase.sql`; los esquemas resultantes son idénticos; RLS activa en las tablas nuevas; las 147 pruebas de integración pasan con `TEST_DATABASE_URL` sobre ambas bases.
- Búsqueda de las palabras prohibidas en los archivos creados o modificados: sin coincidencias nuevas.
- Datos: solo sintéticos o del dataset seudonimizado; los niños del dataset no tienen teléfono ni tutor.

## Pendientes y riesgos

- Validación de los pesos de `VISITA-V1` con la microred (propuesta del equipo, no norma del MINSA).
- Datos clínicos en el navegador del equipo (cola y caché de lecturas): conviene bloqueo de pantalla y cerrar sesión al terminar; el caché de datos se borra al cerrar sesión y la cola no, para no perder registros.
- Prueba en un dispositivo real de la posta piloto y con red intermitente (los E2E simulan la desconexión); el despliegue en la posta piloto queda fuera del software.
- Editar un expediente y dar de alta requieren conexión; la clasificación y la agenda de un niño registrado sin conexión aparecen al sincronizar.
- Ejecutar `db/03_migracion_v3_0.sql` y luego `db/02_supabase.sql` en Supabase antes de desplegar la versión 3.0 (ver `docs/DESPLIEGUE.md`).
- No se agregaron tareas de carga de Locust para los endpoints nuevos ni se midió la latencia de la lista priorizada con el dataset completo.
- Incremento 4 (HIST-4.x) no se tocó.

## Solicitudes abiertas a otros agentes

Ninguna.
