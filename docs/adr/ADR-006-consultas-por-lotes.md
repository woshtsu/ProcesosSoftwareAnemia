# ADR-006 — Consultas por lotes en reportes (corrección DEF-01)

**Contexto.** La primera prueba de carga (50 usuarios, 60 s) mostró que `GET /api/reportes/periodo` tenía p95 = 2 200 ms. Causa: patrón N+1 (una consulta del expediente completo por cada evaluación).

**Decisión.** El puerto expone `obtener_varios(ids)` y `contar_registrados_en_periodo`; el reporte obtiene todos los niños en una sola consulta sin cargar evaluaciones.

**Consecuencias.** Re-ejecución con la misma carga: p95 del reporte de 2 200 ms a 74 ms; p95 agregado de 310 ms a 58 ms; 39,6 solicitudes/s; 0 fallos (valores de los CSV de Locust). Evidencia en `docs/evidencias/carga/`.
