# DIAG-103 — Cronograma de los ocho sprints con hitos (Semanas 3-4)

- **Estado:** RESUELTA  <!-- ABIERTA | EN CURSO | RESUELTA | RECHAZADA -->
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-004
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Media

## Tipo de diagrama

- [x] Gantt / cronograma / WBS

## Requisito que cubre

- **Guía:** `guias/S3-4_Guia_trabajo_semanas_3_y_4.md` — Actividad 9 (§13) cronograma; Actividad 11 (§15) hitos y entregas.
- **Entregable destino:** `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` — §11.3, Figura 4 (marcador `<!-- DIAG-103 pendiente -->`).

## Contenido requerido

Gantt semanal (escala por semanas) del **2026-09-01 al 2026-12-21**. Una barra por sprint, rotulada con el incremento; rombos de hitos al final de cada sprint. Color distinto para INC-1 (PMV, prioritario). Leyenda con las semanas del curso.

| Sprint | Semanas del curso | Inicio | Fin | Barra (texto) | Hito (rombo, fecha = fin) |
| --- | --- | --- | --- | --- | --- |
| Sprint 1 | S3-S4 | 2026-09-01 | 2026-09-14 | INC-1 parte 1: habilitadores, validación y clasificación, registro | H0 (2026-09-05: arquitectura base y entorno de calidad) |
| Sprint 2 | S5-S6 | 2026-09-15 | 2026-09-28 | INC-1 parte 2: expediente, listado, reporte | H1 (2026-09-28: INC-1 PMV aceptado) |
| Sprint 3 | S7-S8 | 2026-09-29 | 2026-10-12 | INC-2 agenda y alertas + BT-01/02/03/08/09 (CI, SonarCloud, E2E/carga) | H2 (2026-10-12) |
| Sprint 4 | S9-S10 | 2026-10-13 | 2026-10-26 | INC-3 sin conexión, sincronización, despliegue en posta piloto | H3 (2026-10-26) |
| Sprint 5 | S11-S12 | 2026-10-27 | 2026-11-09 | INC-4 WhatsApp y barreras | H4 (2026-11-09) |
| Sprint 6 | S13-S14 | 2026-11-10 | 2026-11-23 | INC-5 datos del HIS, experimentación, entrenamiento | H5 (2026-11-23) |
| Sprint 7 | S15-S16 | 2026-11-24 | 2026-12-07 | INC-5 integración + inicio INC-6 | H6 (2026-12-07) |
| Sprint 8 | S17-S18 | 2026-12-08 | 2026-12-21 | INC-6 tablero territorial; producto operativo | H7 (2026-12-21) |

Barras auxiliares (opcionales, en gris claro, debajo): «Validación de datos del HIS» 2026-10-13 → 2026-11-09 (Sprints 4-5, paralela); «Solicitud WhatsApp Business» 2026-09-29 → 2026-11-09.

## Fuentes de verdad

- `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` Tabla 23 (calendario) y Tabla 25 (hitos); Tabla 5 (dependencias).

## Nombre de archivo sugerido

`33_s34_cronograma_sprints_hitos` → `diagramas/src/33_s34_cronograma_sprints_hitos.puml`, `diagramas/png/33_s34_cronograma_sprints_hitos.png`, `diagramas/svg/33_s34_cronograma_sprints_hitos.svg`

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4
- [ ] Texto en español, sin tildes rotas
- [ ] Ocho sprints e hitos H0-H7 con las fechas exactas de la tabla

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** 2026-10-01
- **Resultado:** RESUELTA (cierre administrativo del sincronizador, 2026-10-01: existen fuente `diagramas/src/33_s34_cronograma_sprints_hitos.puml`, `diagramas/png/33_s34_cronograma_sprints_hitos.png` y `diagramas/svg/33_s34_cronograma_sprints_hitos.svg`; la verificación del contenido frente al entregable corresponde a revisor-documental / inspector-guia)
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 4. Cronograma de los ocho sprints del proyecto con incrementos e hitos H0 a H7 (elaboración propia).](../../diagramas/svg/33_s34_cronograma_sprints_hitos.svg)`
- **Notas:**
