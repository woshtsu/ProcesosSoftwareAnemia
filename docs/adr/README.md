# Registros de Decisiones Arquitectónicas (ADR) — Incremento 1

| ADR | Decisión | Atributo de calidad (NFR) principal | Estado |
|---|---|---|---|
| [ADR-001](ADR-001-arquitectura-hexagonal.md) | Arquitectura hexagonal (puertos y adaptadores) en un monolito modular | Mantenibilidad, capacidad de prueba, evolución por incrementos | Aceptada |
| [ADR-002](ADR-002-pwa-web.md) | Cliente PWA web adaptable en lugar de app nativa | Portabilidad, facilidad de despliegue en postas | Aceptada |
| [ADR-003](ADR-003-postgresql.md) | PostgreSQL como base central con restricciones de integridad | Integridad y confiabilidad del dato | Aceptada |
| [ADR-004](ADR-004-reglas-clinicas-parametrizadas.md) | Reglas clínicas parametrizadas en el dominio | Exactitud clínica, trazabilidad normativa | Aceptada (pendiente de confirmación por la microred) |
| [ADR-005](ADR-005-api-rest-openapi.md) | API REST JSON con contrato OpenAPI y errores por campo en español | Interoperabilidad, usabilidad | Aceptada |
| [ADR-006](ADR-006-consultas-por-lotes.md) | Consultas por lotes en reportes (corrección DEF-01) | Rendimiento (latencia p95) | Aceptada |
