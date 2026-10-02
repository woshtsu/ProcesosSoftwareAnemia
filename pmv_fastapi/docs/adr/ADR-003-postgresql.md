# ADR-003 — PostgreSQL como base central

**Contexto.** El problema organizacional nace del triple registro y la duplicidad. El dato nominal debe ser único y confiable.

**Decisión.** PostgreSQL 16 en staging/producción con `UNIQUE(dni)`, llaves foráneas y restricciones `CHECK` que repiten los rangos de plausibilidad del dominio (`db/01_esquema_postgresql.sql`). SQLite se usa en desarrollo y pruebas locales.

**Consecuencias.** (+) La base rechaza datos imposibles aunque se inserten fuera de la API (defensa en profundidad). (+) Deduplicación garantizada por DNI. (−) Dos motores que mantener; se mitiga ejecutando la suite de integración contra ambos en CI.
