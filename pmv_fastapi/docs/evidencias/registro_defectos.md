# Registro de defectos — Incremento 1 (v1.0-PMV)

| ID | Descripción | Severidad | Detectado por | Corrección | Verificación | Estado |
|---|---|---|---|---|---|---|
| DEF-01 | `GET /api/reportes/periodo` consultaba el expediente completo por cada evaluación (patrón N+1): p95 = 2 200 ms con 50 usuarios | Mayor (rendimiento) | CP-15, prueba de carga con Locust | Rama `fix/def-01-reporte-n-mas-1`: consultas por lotes `obtener_varios` y `contar_registrados_en_periodo` (ADR-006) | Misma carga: p95 del reporte 74 ms, p95 agregado 58 ms, 0 fallos | Cerrado |
| DEF-02 | El conteo de niños registrados en el periodo comparaba días en UTC: un registro hecho después de las 19:00 en Perú se contaba en el día siguiente y no aparecía en el reporte del día; además, la fecha de «hoy» del servidor dependía de la zona horaria del equipo (un contenedor en UTC adelanta el día desde las 19:00) | Mayor (exactitud del reporte) | CP-14, prueba E2E re-ejecutada el 30/09/2026 a las 20:40 (hora de Perú) | Rama `fix/def-02-zona-horaria`: `fecha_local` y `limites_utc` en el dominio (UTC-5 fijo) usados por ambos adaptadores, y `RelojSistema` con la fecha de Perú | Nuevas pruebas CP-16 (unitarias, de integración en SQLite y PostgreSQL 16 y E2E con zona horaria de Perú); 77/77 en verde | Cerrado |

Densidad: 2 defectos / 1,02 KLOC de Python = **2,0 defectos/KLOC**, ambos cerrados antes de la liberación; 0 abiertos.
