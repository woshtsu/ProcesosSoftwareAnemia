# DIAG-105 — Burndown del Sprint 1 (Semanas 3-4)

- **Estado:** RESUELTA  <!-- ABIERTA | EN CURSO | RESUELTA | RECHAZADA -->
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-004
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Media

## Tipo de diagrama

- [x] Otro: gráfico de burndown (líneas)

## Requisito que cubre

- **Guía:** `guias/S3-4_Guia_trabajo_semanas_3_y_4.md` — Actividad 12 (§16) seguimiento «Planificado → Ejecutado → Medición → Comparación → Desviación → Acción correctiva»; Actividad 13 (§17) indicadores de avance. Consigna S6, diapositiva 6: «Historias Planificadas vs. Completadas (Velocidad / Burndown)».
- **Entregable destino:** `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` — §13.1, Figura 6 (marcador `<!-- DIAG-105 pendiente -->`).

## Contenido requerido

Gráfico de líneas (se sugiere Python + matplotlib; guardar SVG y PNG). Eje X: día del sprint 0-14 (etiqueta secundaria con fecha: día 0 = 31-ago, día 1 = 01-sep … día 14 = 14-sep-2026). Eje Y: «Puntos de historia pendientes» (0-13).

**Serie 1 — «Ideal (planificado)»**, línea discontinua gris: pendiente = 13 − 13 × día / 14.

| Día | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ideal | 13,00 | 12,07 | 11,14 | 10,21 | 9,29 | 8,36 | 7,43 | 6,50 | 5,57 | 4,64 | 3,71 | 2,79 | 1,86 | 0,93 | 0,00 |

**Serie 2 — «Real (escenario simulado)»**, línea continua escalonada (color de énfasis):

| Día | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Real simulado | 13 | 13 | 13 | 13 | 13 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 5 | 5 | 0 |

Anotaciones (flechas o etiquetas sobre la serie real):
- Día 5: «EP-1.T habilitadores terminados (−5)».
- Día 7: «Reunión de seguimiento simulada: A05 retrasada (norma vigente)».
- Día 12: «HIST-1.3 terminada (−3), 1 día tarde».
- Día 14: «HIST-1.1 terminada (−5)».

Subtítulo o nota al pie obligatoria: «Serie real = escenario simulado de la Actividad 15; no son mediciones del equipo».

## Fuentes de verdad

- `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` Tabla 21 (13 puntos del Sprint 1), Tabla 27 (seguimiento simulado) y §13.4 (reunión simulada).

## Nombre de archivo sugerido

`35_s34_burndown_sprint1` → `diagramas/src/35_s34_burndown_sprint1.py`, `diagramas/png/35_s34_burndown_sprint1.png`, `diagramas/svg/35_s34_burndown_sprint1.svg`

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4
- [ ] Texto en español, sin tildes rotas
- [ ] Valores idénticos a las dos tablas; leyenda de ambas series
- [ ] Nota «escenario simulado» visible

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** 2026-10-01
- **Resultado:** RESUELTA (cierre administrativo del sincronizador, 2026-10-01: existen fuente `diagramas/src/35_s34_burndown_sprint1.py`, `diagramas/png/35_s34_burndown_sprint1.png` y `diagramas/svg/35_s34_burndown_sprint1.svg`; la verificación del contenido frente al entregable corresponde a revisor-documental / inspector-guia)
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 6. Burndown del Sprint 1: línea ideal y avance del escenario simulado de seguimiento (elaboración propia).](../../diagramas/svg/35_s34_burndown_sprint1.svg)`
- **Notas:**
