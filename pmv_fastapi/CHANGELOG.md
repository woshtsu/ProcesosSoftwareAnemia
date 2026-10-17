# Registro de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Los datos incluidos son sintéticos.

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
- HIST-2.3 Visualizar agenda del personal (5 SP) y HIST-2.4 Registrar asistencia a control (3 SP).

## [1.0.0-pmv] — Incremento 1, PMV (tag `v1.0-PMV`)

### Agregado
- HU-01 registro del niño con su evaluación inicial; HU-02 expediente digital (consulta, actualización y nuevos controles); HU-03 validación clínica con hemoglobina ajustada por altitud (OMS 2024) y vista previa; HU-04 listado de seguimiento; HU-05 reporte del periodo en JSON y CSV.
- API REST con contrato OpenAPI y errores por campo en español (ADR-005); cliente PWA con Swagger UI local (ADR-002); PostgreSQL con restricciones de integridad (ADR-003); reglas clínicas parametrizadas (ADR-004); arquitectura hexagonal (ADR-001).
- 77 pruebas automatizadas (62 unitarias, 11 de integración y 4 E2E), cobertura del 99 %, pipeline de CI y prueba de carga con Locust.

### Corregido
- **DEF-01**: patrón N+1 en el reporte del periodo (p95 de 2 200 ms a 74 ms; ADR-006).
- **DEF-02**: el reporte usaba días UTC y la fecha de «hoy» dependía de la zona horaria del servidor (ahora hora de Perú, UTC-5).
