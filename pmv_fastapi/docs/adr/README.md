# Registros de Decisiones Arquitectónicas (ADR) — Incrementos 1 y 2

| ADR | Decisión | Atributo de calidad (NFR) principal | Estado |
|---|---|---|---|
| [ADR-001](ADR-001-arquitectura-hexagonal.md) | Arquitectura hexagonal (puertos y adaptadores) en un monolito modular | Mantenibilidad, capacidad de prueba, evolución por incrementos | Aceptada |
| [ADR-002](ADR-002-pwa-web.md) | Cliente PWA web adaptable en lugar de app nativa | Portabilidad, facilidad de despliegue en postas | Aceptada |
| [ADR-003](ADR-003-postgresql.md) | PostgreSQL como base central con restricciones de integridad | Integridad y confiabilidad del dato | Aceptada |
| [ADR-004](ADR-004-reglas-clinicas-parametrizadas.md) | Reglas clínicas parametrizadas en el dominio | Exactitud clínica, trazabilidad normativa | Aceptada (pendiente de confirmación por la microred) |
| [ADR-005](ADR-005-api-rest-openapi.md) | API REST JSON con contrato OpenAPI y errores por campo en español | Interoperabilidad, usabilidad | Aceptada |
| [ADR-006](ADR-006-consultas-por-lotes.md) | Consultas por lotes en reportes (corrección DEF-01) | Rendimiento (latencia p95) | Aceptada |
| [ADR-007](ADR-007-agenda-calculada-en-dominio.md) | Agenda de controles calculada en línea en el dominio (`ESQUEMA_AGENDA_V1`), sin tabla propia (actualizada con la asistencia, ADR-010) | Exactitud normativa, consistencia del dato, capacidad de prueba | Aceptada (parámetros pendientes de confirmación por la microred) |
| [ADR-008](ADR-008-puertos-de-entrada-y-estructura-hexagonal.md) | Puertos de entrada (`typing.Protocol`) y estructura hexagonal verificada por pruebas de arquitectura | Mantenibilidad, evolución por incrementos | Aceptada |
| [ADR-009](ADR-009-origen-de-datos-y-dataset-diresa.md) | Origen de los datos (`SISTEMA` / `DATASET_DIRESA_JUNIN`), registros seudónimos con campos opcionales solo para el dataset, altitud por capital de provincia con fuente y reloj de referencia fijo | Integridad del dato, privacidad, reproducibilidad de la demo | Aceptada (altitud aproximada) |
| [ADR-010](ADR-010-asistencia-a-control-persistida.md) | Asistencia a un control como hecho persistido (`asistencia_control`) que la agenda calculada consulta | Trazabilidad, exactitud de las alertas | Aceptada |

Nota: ADR-008 detalla y hace verificable lo decidido en ADR-001; ADR-010 complementa a ADR-007 (la agenda sigue calculándose).
