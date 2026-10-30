# Registro de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Los datos incluidos son sintéticos.

## [3.0.0-inc3] — Incremento 3: registro sin conexión, sincronización y visita domiciliaria priorizada (HIST-3.1 a HIST-3.4 y VIS-3.5)

### Agregado
- **HIST-3.1 Registrar sin conexión (ADR-012)**: cola de operaciones en IndexedDB (`app/web/cola.js`) con `id_operacion` UUID, `id_dispositivo` y fecha local; un niño registrado sin conexión recibe un `id_cliente` temporal y su expediente provisional («Pendiente de sincronizar»); los registros sobre él llevan `nino_ref: {id_cliente}`. Se guardan sin conexión: niño con evaluación inicial, evaluación, asistencia a control y visita. Service worker nuevo (`app/web/sw.js`): precache del shell y lecturas de la API con red primero y caché de respaldo (aviso «se muestran los últimos datos guardados»); el caché de datos se borra al cerrar sesión.
- **HIST-3.2 Sincronizar al reconectar**: `POST /api/sincronizacion` (1 a 200 operaciones, ordenadas por fecha local; resultado por operación `APLICADA`, `DUPLICADA`, `CONFLICTO` o `RECHAZADA`; reenviar el lote no crea nada nuevo; mapeo `id_cliente` a `id` persistido para lotes posteriores). Tabla `operacion_sincronizada`. Arranca sola con el evento `online`, al abrir la aplicación con pendientes y cada minuto, y con «Sincronizar ahora» (`app/web/sync.js`). Reutiliza los casos de uso existentes para validar.
- **HIST-3.3 Resolver conflictos**: servicio de dominio puro `app/domain/service/conflictos.py` (niño con DNI existente, evaluación del mismo día, asistencia del mismo control, visita del mismo día); entidad `ConflictoSincronizacion` (tabla `conflicto_sincronizacion`); `GET /api/sincronizacion/conflictos?estado=` y `POST /api/sincronizacion/conflictos/{id}/resolver` con `CONSERVAR_SERVIDOR`, `APLICAR_CLIENTE` o `DESCARTAR`. `APLICAR_CLIENTE` nunca sobrescribe nombres, apellidos, sexo ni fecha de nacimiento, ni una asistencia respaldada por una evaluación. Nunca se sobrescribe a ciegas.
- **HIST-3.4 Ver sincronización pendiente**: indicador en la cabecera («2 pendientes», «Al día»), pestaña «Sincronización» con la lista de pendientes (tipo, resumen con iniciales, hora local, último intento y error), hora de la última sincronización exitosa, reintento o descarte de lo rechazado y los conflictos del servidor con sus botones de resolución.
- **VIS-3.5 Visita domiciliaria priorizada (ADR-013)**: tabla `visita_domiciliaria` (`UNIQUE (nino_id, fecha)`), `POST /api/ninos/{id}/visitas`, `GET /api/ninos/{id}/visitas` y `GET /api/visitas/priorizadas?establecimiento=&limite=` con un puntaje de 0 a 100 explicable (severidad, control vencido, inasistencias de los últimos 90 días y días desde la última visita; `PESOS_V1`, propuesta del equipo y **no** una norma del MINSA). Pestaña «Visitas» con la lista, el desglose del puntaje y el formulario; sección «Visitas domiciliarias» en el expediente.
- ADR-012 y ADR-013; migración `db/03_migracion_v3_0.sql` (probada en PostgreSQL 16: instalación limpia y migración desde 2.0 dan el mismo esquema); RLS de las tablas nuevas en `db/02_supabase.sql`; guía de qué SQL ejecutar en `docs/DESPLIEGUE.md`.
- Pruebas: 150 pruebas nuevas de pytest (de 349 a 499: 331 unitarias, 147 de integración y 21 de arquitectura), con cobertura total de 99,70 % y 100 % en los archivos nuevos, y 7 E2E nuevas con Playwright (de 17 a 24; `context.set_offline(True)`), CP-188 a CP-303.

### Cambiado
- `RepositorioNinos` agrega `actualizar_evaluacion` y `actualizar_asistencia` (solo para aplicar la resolución de un conflicto).
- `db/01_esquema_postgresql.sql` incluye las tablas nuevas. **Una base 2.0 se migra con `db/03_migracion_v3_0.sql`** (sin cambios en las tablas existentes); SQLite se actualiza sola al arrancar.
- Versión: `3.0.0` en `pyproject.toml`; `VERSION = "3.0.0-inc3"` en la API; subtítulo «Incremento 3 · v3.0». Contrato OpenAPI regenerado (22 rutas).

### Limitaciones
- Los datos clínicos registrados sin conexión viven en el navegador del equipo hasta sincronizar (ver riesgos en ADR-012); la clasificación y la agenda de un niño nuevo aparecen al sincronizar.
- Editar los datos de un expediente y dar de alta requieren conexión. Los pesos del puntaje de visitas no están validados por la microred. Despliegue en una posta piloto y WhatsApp quedan fuera del software.

## [2.0.0-inc2] — Incremento 2 al 100 % (HIST-2.3 y HIST-2.4) y dataset DIRESA Junín (tag previsto `v2.0-Inc2`)

### Agregado
- **HIST-2.3 Agenda del personal (RF-08)**: `GET /api/agenda?desde=&hasta=&establecimiento=&comunidad=` (`app/domain/service/agenda_personal.py`). Por defecto la semana (lunes a domingo) de la fecha de referencia; máximo 31 días (422 si el rango es inválido); totales por día y del rango; filtros por establecimiento y comunidad; una sola carga por lotes (sin N+1). Pestaña «Agenda» con tabla por día, navegación «Anterior/Siguiente» y controles cumplidos atenuados.
- **HIST-2.4 Asistencia a un control (RF-09, ADR-010)**: tabla `asistencia_control` (`UNIQUE (nino_id, codigo_control, fecha_programada)`), `POST /api/ninos/{id}/controles/{codigo}/asistencia` (201; 404, 409 si ya hay asistencia o el control está cumplido o cerrado; 422 si la fecha es futura o falta el motivo) y `GET /api/ninos/{id}/asistencias`. Asistió: el control queda cumplido. No asistió: sigue pendiente o vencido con la marca «Inasistencia registrada» y la prioridad de la alerta sube un nivel. Botones «Asistió» y «No asistió» con ventana de confirmación en la agenda del expediente y en la pestaña «Agenda».
- **Origen de los datos y dataset DIRESA Junín (ADR-009)**: `Nino.origen` (`SISTEMA` o `DATASET_DIRESA_JUNIN`), `codigo_origen`, `red`, `microred` y `provincia`; para el dataset `dni`, nombres, apellidos, sexo y tutor pueden ser nulos (solo para ese origen; las validaciones de `SISTEMA` no cambian y la base lo refuerza con `CHECK`); nombre legible «Registro DJ-00002 (dataset anonimizado)»; la búsqueda `q` y la pestaña «Expediente» encuentran por código; `Evaluacion.clasificacion_origen` (severidad del HIS) y peso y talla opcionales en las evaluaciones importadas.
- **Fecha de referencia fija**: variable `FECHA_REFERENCIA=AAAA-MM-DD` (adaptador `reloj_fijo.py`); `GET /api/salud` devuelve `fecha_hoy` y `fecha_referencia`; aviso visible «Fecha de referencia: 30/06/2024 (corte del dataset)»; las fechas por defecto de la interfaz salen del servidor.
- **Importador** `scripts/importar_dataset_diresa.py` (paquete `scripts/importador_diresa/`): lee el CSV (latin-1, `;`), asigna la altitud de la capital de provincia (INEI, *Perú: Compendio Estadístico 2014*, cuadro 1.12; aproximación declarada), no inventa peso ni talla, descarta y cuenta lo inválido, y entrega los registros al servicio de importación por el puerto de entrada (sin SQL directo). Opciones `--muestra 500 --semilla 2026` (estratificada Provincia × severidad, reproducible), `--completo`, `--reiniciar`, `--reporte`, `--fecha-referencia` y `--con-registros-sistema N`. Reportes de la corrida real en `docs/evidencias/inc2/importacion_muestra500.json` e `importacion_completa.json` (concordancia de severidad HIS vs sistema, distribución por provincia, descartes).
- ADR-009 (origen y dataset) y ADR-010 (asistencia persistida); ADR-007 actualizado; migración `db/02_migracion_v2_0.sql` (probada en PostgreSQL 16); `tests/rendimiento/micro_benchmark.py`; registro de defectos con DEF-09; evidencias en `docs/evidencias/inc2/` (pruebas, cobertura, E2E, importaciones, optimización y capturas).
- Pruebas: 98 pruebas nuevas de pytest (de 228 a 326) y 7 E2E nuevas con Playwright (de 8 a 15), numeradas de CP-116 a CP-187 (unitarias, integración con SQLite, arquitectura y E2E), una muestra real de 20 filas en `tests/fixtures/dataset_muestra.csv` (con casos de campos nulos) y 4 reglas nuevas de arquitectura (CP-176 a CP-179).

### Cambiado
- `db/01_esquema_postgresql.sql` incluye las columnas y restricciones nuevas (`nino.dni` admite nulo con `UNIQUE`; `ck_nino_sistema_completo` exige DNI y nombres para el origen `SISTEMA`; `peso_kg` y `talla_cm` admiten nulo; tabla `asistencia_control`). **Una base creada con la versión 1.x se migra con `db/02_migracion_v2_0.sql`; una base SQLite 1.x debe recrearse** (el arranque lo rechaza con un mensaje claro).
- `GET /api/ninos`, expediente, alertas y reporte CSV: `dni`, `nombres` y demás campos personales pueden ser `null`; se agregan `nombre_completo`, `origen`, `codigo_origen`, `provincia`, `red` y `microred`. Los controles de la agenda agregan `inasistencia_registrada`, `motivo_inasistencia`, `cumplido_por_asistencia` y `asistencia_id`; el resumen agrega `inasistencias`.
- **Optimización de la latencia (acción 1 del PDCA)**: carga de niños por Core en tres consultas y suma de meses sin `calendar.monthrange`; con 1 000 niños, p95 del listado de 159,6 a 128,2 ms y de las alertas de 185,7 a 155,3 ms (medianas de tres corridas; `docs/evidencias/inc2/optimizacion_p95.md`).
- Versión: `2.0.0` en `pyproject.toml`; `VERSION = "2.0.0-inc2"` en la API; subtítulo «Incremento 2 · v2.0».

### Corregido
- **DEF-09**: en la pestaña «Agenda», la respuesta de la carga inicial sobrescribía las fechas que la persona acababa de escribir.

### Limitaciones
- Con el dataset completo (11 686 niños) las alertas tardan ≈ 2,5 s y devuelven 22 MiB sin paginar (la agenda del personal ≈ 1,6 s); con la muestra de 500 niños todo responde en menos de 0,1 s. Supera el criterio de revisión de ADR-007.
- No se puede anular ni corregir una asistencia registrada por error; la autenticación por roles sigue pendiente.

## [1.5.0-inc2-avance] — Incremento 2, avance del 50 % (HIST-2.1 y HIST-2.2)

### Agregado
- **HIST-2.1 Agenda de controles** (`app/domain/service/agenda.py`, esquema versionado `ESQUEMA_AGENDA_V1`, ADR-007): dosajes por edad a los 6, 9, 12, 15, 18, 21, 24, 30, 36, 39, 48 y 51 meses; controles de tratamiento C1M, C3M y C6M a +1, +3 y +6 meses de una evaluación con anemia; ventana de cumplimiento de −15 a +30 días; estados CUMPLIDO, PENDIENTE (con indicador `proximo` a 7 días o menos) y VENCIDO; cierre por recuperación; solo niños activos y menores de 60 meses.
- `GET /api/ninos/{id}/agenda`: controles ordenados y resumen. Calculada en línea, sin tabla nueva.
- **HIST-2.2 Alertas internas** (`app/domain/service/alertas.py`): prioridad ALTA, MEDIA y BAJA, orden por prioridad y atraso, filtros por comunidad y prioridad, una sola consulta por lotes (sin N+1).
- `GET /api/alertas/controles-vencidos` y `GET /api/alertas/resumen`.
- Interfaz: sección «Agenda de controles» en el expediente, pestaña «Alertas» con tarjetas de resumen y tabla filtrable, e insignia de controles vencidos en la cabecera.
- Pruebas de arquitectura (`tests/arquitectura/`), unitarias de agenda y alertas con valores frontera, de casos de uso, de integración de los endpoints nuevos, E2E y tareas de carga para agenda y alertas.
- `scripts/exportar_openapi.py` para regenerar y verificar `docs/openapi.json`; verificación en el pipeline.
- ADR-007 (agenda calculada en el dominio) y ADR-008 (puertos de entrada y estructura hexagonal); registro de defectos del incremento y evidencias en `docs/evidencias/inc2/`.

### Cambiado
- **Reestructuración a puertos y adaptadores** (ADR-008): `domain/model`, `domain/service`, `ports/inbound`, `ports/outbound`, `application`, `adapters/inbound/http`, `adapters/outbound/persistence`. El adaptador HTTP depende de los puertos de entrada y no de la implementación; `main.py` es la raíz de composición. Se eliminaron las rutas anteriores (`adapters/entrada`, `adapters/salida`, `application/casos_uso.py`, `application/puertos.py`, `domain/entidades.py`, `domain/errores.py`, `domain/reglas_clinicas.py`) sin dejar módulos puente.
- `GET /api/ninos`: `control_atrasado` significa «tiene al menos un control vencido» (sustituye la heurística de 30 días sin control) y se agrega `controles_vencidos`.
- `scripts/cargar_datos_prueba.py`: conjunto determinista de 27 niños definido respecto de la fecha de hoy, con controles cumplidos, pendientes, próximos y vencidos; conserva los niños del Incremento 1; opción `--reiniciar`.
- Versión: `1.5.0` en `pyproject.toml`; `VERSION = "1.5.0-inc2-avance"` en la API; subtítulo «Incremento 2 (avance 50 %) · v1.5».

### Corregido
- **DEF-03**: el reporte del periodo respondía 500 con fechas extremas (ahora 422; periodo entre 2000 y 2100).
- **DEF-04**: DNI y celular aceptaban dígitos Unicode y un salto de línea final.
- **DEF-05**: la vista previa aceptaba altitudes NaN o absurdas y fechas de nacimiento inválidas (mostraba «SEVERA» sin sentido).
- **DEF-06**: los textos no tenían largo máximo (columnas de 80 y 120 caracteres).
- **DEF-07**: la búsqueda trataba `%` y `_` como comodines de SQL.
- **DEF-08**: dos registros simultáneos con el mismo DNI devolvían 500 (ahora 409).
- Respuestas desordenadas al cambiar rápido los filtros de la pestaña de alertas: se descartan las respuestas de un filtro anterior (medida preventiva).

### Pendiente del incremento
- HIST-2.3 Visualizar agenda del personal (5 SP) y HIST-2.4 Registrar asistencia a control (3 SP) (completadas en la 2.0.0-inc2).

## [1.0.0-pmv] — Incremento 1, PMV (tag `v1.0-PMV`)

### Agregado
- HU-01 registro del niño con su evaluación inicial; HU-02 expediente digital (consulta, actualización y nuevos controles); HU-03 validación clínica con hemoglobina ajustada por altitud (OMS 2024) y vista previa; HU-04 listado de seguimiento; HU-05 reporte del periodo en JSON y CSV.
- API REST con contrato OpenAPI y errores por campo en español (ADR-005); cliente PWA con Swagger UI local (ADR-002); PostgreSQL con restricciones de integridad (ADR-003); reglas clínicas parametrizadas (ADR-004); arquitectura hexagonal (ADR-001).
- 77 pruebas automatizadas (62 unitarias, 11 de integración y 4 E2E), cobertura del 99 %, pipeline de CI y prueba de carga con Locust.

### Corregido
- **DEF-01**: patrón N+1 en el reporte del periodo (p95 de 2 200 ms a 74 ms; ADR-006).
- **DEF-02**: el reporte usaba días UTC y la fecha de «hoy» dependía de la zona horaria del servidor (ahora hora de Perú, UTC-5).
