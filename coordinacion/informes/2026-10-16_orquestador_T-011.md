# Informe T-011 — Entregable S9 (evaluación GQM) y avance del 50 % del Incremento 2

**Agente:** orquestador (con subagentes desarrollador, QA/métricas, redactor y revisor independiente) · **Fecha:** 2026-10-16 · **Estado:** EN REVISIÓN

## Qué se hizo
1. **Avance del Inc. 2 (v1.5.0-inc2-avance)** en `pmv_fastapi/`: HIST-2.1 agenda normativa de controles (RF-06) y HIST-2.2 controles vencidos y alertas priorizadas (RF-07) = 2/4 historias, 10/18 SP; reestructuración a puertos y adaptadores (ADR-008) y agenda calculada en el dominio (ADR-007).
2. **Calidad v1.5:** 228 pruebas (174 unitarias, 40 de integración, 14 de arquitectura) + 8 E2E en verde, cobertura 100 %, Ruff 0 hallazgos. Defectos escapados del Inc. 1 hallados y corregidos con regresión: DEF-03..DEF-08 (`pmv_fastapi/docs/evidencias/registro_defectos_inc2.md`).
3. **Métricas GQM reales** sobre `v1.0-PMV` y v1.5 (`entregables/semana-09/metricas/`, scripts en `herramientas/gqm/`): M1.1 0 %→0 %; M1.2 40 %→100 %; M2.1 100 %→100 % (2/2; 50 % del alcance total); M2.2 1,4→0,0 Def/RF (0,86 si se imputan los hallados en el ciclo); M3.1 25,0 %→33,3 %; M3.2 57,6 %→100 %; p95 175→610 ms (regresión, acción PDCA 1); disponibilidad 100 %.
4. **Capturas reales** por RF (RF-01..RF-07) con Chromium/Playwright, organizadas por RF en `entregables/semana-09/evidencias_capturas/`.
5. **Informe** `entregables/semana-09/Entregable_Semana9_Anemia_Junin.md` (estructura de la guía, 3 pilares) + checklist independiente (97,1 %) + exportación DOCX/PDF en `exportados/semana-09/`.

## Pendientes (del equipo)
- Crear la rama `feature/inc2-agenda-alertas` y el tag `v1.5.0-inc2-avance`, publicar y capturar la vista de GitHub (Anexo B del informe).
- Firmas del QA Lead en las fichas; aplicar el SUS; confirmar expositores.
- HIST-2.3 y HIST-2.4 (RF-08, RF-09) y tag `v2.0-Inc2` al cierre; perfilar el p95; SonarCloud y job de PostgreSQL.

## Notas
- Los archivos CSV/MD heredados que solo difieren en fin de línea (CRLF/LF) no se modificaron en la copia del usuario.
- Sin commits, tags ni pushes.
