# Checklist de cumplimiento — Semana 2

- **Guía:** `guias/S2_Guia_trabajo_semana_2.md`
- **Entregable revisado:** `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md`
- **Insumos consultados:** `archivo/versiones-anteriores/semana-02/Entregable_Semana2_Anemia_Junin_v1.md`, `archivo/verificaciones/verificacion_s2_y_guia_uml.md`, `anemia_junin/pyproject.toml`, `anemia_junin/docs/adr/`
- **Revisor:** revisor-documental (T-003)
- **Fecha:** 2026-09-25
- **Resultado global:** antes 84,5 % → después 98,0 % (71 CUMPLE, 3 PARCIAL, 0 NO CUMPLE de 74 requisitos). Fórmula: CUMPLE = 1, PARCIAL = 0,5, NO CUMPLE = 0.

## Matriz de requisitos

R-xx: requisitos de la guía (actividades 1-10, productos esperados, preguntas orientadoras, estructura del entregable, preguntas de análisis, reto, criterio clave y rúbrica). F-xx: requisitos de formato del protocolo del proyecto y de la solicitud de revisión.

| ID | Requisito (cita / paráfrasis fiel) | Ubicación en guía | Sección del entregable | Antes | Después | Evidencia / observación |
| --- | --- | --- | --- | --- | --- | --- |
| R-01 | Partir del TO-BE de la Guía 1 (conexión con la Guía 1) | §2 | §0 | CUMPLE | CUMPLE | Ahora referido a M1-M6 y B1-B6 de S1 |
| R-02 | Matriz con los 12 factores de la Actividad 1 | §5 | §1, Tabla 1 | CUMPLE | CUMPLE | 12/12 |
| R-03 | Columnas Factor / Situación / Nivel / **Evidencia** separadas | §5 | §1, Tabla 1 | PARCIAL | CUMPLE | Situación y evidencia estaban fusionadas; se restauró la columna de evidencia de la v1 enlazada a S1 |
| R-04 | Nivel Bajo / Medio / Alto por factor | §5 | Tabla 1 | CUMPLE | CUMPLE | Observación: los 12 factores son "Alto" (criterio del equipo, sustentado en la evidencia) |
| R-05 | Pregunta orientadora: tres características más influyentes | §5 | §1 | CUMPLE | CUMPLE | |
| R-06 | Mínimo seis factores de selección | §6 Actividad 2 | §2, Tabla 2 | CUMPLE | CUMPLE | 8 factores |
| R-07 | Columnas Factor / Importancia / ¿Por qué afecta la selección? | §6 | Tabla 2 | CUMPLE | CUMPLE | |
| R-08 | Comparar los 7 modelos: Cascada, Incremental, Espiral, Scrum, Kanban, DevOps, MLOps/DataOps | §7 Actividad 3 | §3, Tabla 3 | CUMPLE | CUMPLE | 7/7 |
| R-09 | Seis criterios de la matriz (adaptabilidad … adecuación) | §7 | Tabla 3 | CUMPLE | CUMPLE | Totales verificados aritméticamente |
| R-10 | Escala 1-5 declarada | §7 | §3 | CUMPLE | CUMPLE | |
| R-11 | Pregunta orientadora: ¿el de mayor puntuación debe seleccionarse? (naturaleza del proyecto y evidencia) | §7 | §3 | CUMPLE | CUMPLE | |
| R-12 | Comparación "con criterios pertinentes y evidencia" (rúbrica, nivel Excelente) | §19 rúbrica | §3, Tabla 4 | PARCIAL | CUMPLE | Nueva tabla de sustento por modelo |
| R-13 | Matriz de decisión con 8 criterios y pesos | §8 Actividad 4 | §4.1, Tabla 6 | CUMPLE | CUMPLE | Pesos justificados |
| R-14 | Tres alternativas y puntaje total | §8 | Tabla 6 | CUMPLE | CUMPLE | 4,75 / 3,85 / 2,95 verificados |
| R-15 | Decisión explícita "Modelo de proceso seleccionado" | §8 | §4 | CUMPLE | CUMPLE | |
| R-16 | Justificación 1: característica que hace necesario el modelo | §8 | §5.1 | CUMPLE | CUMPLE | |
| R-17 | Justificación 2: problema del proceso de desarrollo que resuelve | §8 | §5.2 | CUMPLE | CUMPLE | |
| R-18 | Justificación 3: cómo entrega valor progresivamente | §8 | §5.3 | CUMPLE | CUMPLE | |
| R-19 | Justificación 4: cómo gestiona cambios | §8 | §5.4 | CUMPLE | CUMPLE | |
| R-20 | Justificación 5: cómo controla riesgos | §8 | §5.5 | CUMPLE | CUMPLE | |
| R-21 | Justificación 6: limitaciones | §8 | §5.6 | CUMPLE | CUMPLE | |
| R-22 | Justificación 7: por qué se descartaron las otras alternativas | §8 | §5.7 | CUMPLE | CUMPLE | |
| R-23 | Pregunta central: ¿qué modelo permite menor riesgo y mayor entrega de valor? | §3 | §4 | PARCIAL | CUMPLE | Antes implícita; ahora respuesta explícita |
| R-24 | Representación gráfica del modelo seleccionado | §9 Actividad 5 | §6, Figura 1 | PARCIAL | PARCIAL | PNG 430×551 ilegible → **DIAG-006** pendiente (el `02_modelo_proceso` existente es genérico y no se reutiliza) |
| R-25 | El diagrama muestra los 10 elementos (entrada … siguiente incremento) | §9 | §6, Tabla 8 | CUMPLE | CUMPLE | Tabla 8 los desglosa uno a uno |
| R-26 | "No copiar un diagrama de Internet": adaptado al proyecto | §9 Importante | §6 | CUMPLE | CUMPLE | Nombra INC-n, actores y subciclo MLOps |
| R-27 | Matriz Incremento / Funcionalidad / Resultado esperado / Valor generado / Indicador (≥5) | §10 Actividad 6 | §7, Tabla 9 | CUMPLE | CUMPLE | 6 incrementos, ahora con identificador INC-n y brecha de origen |
| R-28 | Relación necesidad → incremento → funcionalidad → resultado → valor | §10 | §7 | CUMPLE | CUMPLE | |
| R-29 | Mínimo cinco riesgos (Riesgo / Causa / Impacto / Mecanismo de control) | §11 Actividad 7 | §8, Tabla 10 | CUMPLE | CUMPLE | 7 riesgos |
| R-30 | Tabla Necesidad / Herramienta / Actividad que soporta / **Evidencia** | §12 Actividad 8 | §9, Tabla 11 | PARCIAL | CUMPLE | Faltaba la columna Evidencia (la v1 la tenía); ahora distingue lo que está en uso en `anemia_junin/` de lo planificado |
| R-31 | Pregunta orientadora: ¿la herramienta determina el modelo o al revés? | §12 | §9 | CUMPLE | CUMPLE | Reforzada con el caso Selenium → Playwright |
| R-32 | Matriz de trazabilidad de 10 elementos | §13 Actividad 9 | §10, Tabla 15 | CUMPLE | CUMPLE | |
| R-33 | Caso de decisión P1 | §14 Actividad 10 | §11.1 | CUMPLE | CUMPLE | |
| R-34 | Caso de decisión P2 | §14 | §11.2 | CUMPLE | CUMPLE | |
| R-35 | Caso de decisión P3 | §14 | §11.3 | CUMPLE | CUMPLE | |
| R-36 | Caso de decisión P4 | §14 | §11.4 | CUMPLE | CUMPLE | |
| R-37 | Caso de decisión P5 | §14 | §11.5 | CUMPLE | CUMPLE | |
| R-38 | Caso de decisión P6 | §14 | §11.6 | CUMPLE | CUMPLE | |
| R-39 | Caso de decisión P7 | §14 | §11.7 | CUMPLE | CUMPLE | |
| R-40 | Caso de decisión P8 | §14 | §11.8 | CUMPLE | CUMPLE | |
| R-41 | Caso de decisión P9 | §14 | §11.9 | CUMPLE | CUMPLE | |
| R-42 | Caso de decisión P10 | §14 | §11.10 | CUMPLE | CUMPLE | |
| R-43 | Entregable con las 10 secciones en el orden de la guía | §15 | §1-§10 | PARCIAL | CUMPLE | Antes, §11 y §13 no eran encabezados y la jerarquía saltaba niveles |
| R-44 | Pregunta de análisis 1 | §16 | §12.1 | CUMPLE | CUMPLE | |
| R-45 | Pregunta de análisis 2 | §16 | §12.2 | CUMPLE | CUMPLE | |
| R-46 | Pregunta de análisis 3 | §16 | §12.3 | CUMPLE | CUMPLE | |
| R-47 | Pregunta de análisis 4 | §16 | §12.4 | CUMPLE | CUMPLE | |
| R-48 | Pregunta de análisis 5 | §16 | §12.5 | CUMPLE | CUMPLE | |
| R-49 | Pregunta de análisis 6 | §16 | §12.6 | CUMPLE | CUMPLE | |
| R-50 | Pregunta de análisis 7 | §16 | §12.7 | CUMPLE | CUMPLE | Actualizada con las herramientas reales del PMV |
| R-51 | Pregunta de análisis 8 | §16 | §12.8 | CUMPLE | CUMPLE | |
| R-52 | Pregunta de análisis 9 | §16 | §12.9 | CUMPLE | CUMPLE | |
| R-53 | Pregunta de análisis 10 | §16 | §12.10 | CUMPLE | CUMPLE | |
| R-54 | Reto: ¿qué problema tenemos? | §17 | §13.1 | CUMPLE | CUMPLE | |
| R-55 | Reto: ¿qué características tiene el proyecto? | §17 | §13.2 | CUMPLE | CUMPLE | |
| R-56 | Reto: ¿por qué elegimos este modelo? (evidencia de comparación) | §17 | §13.3 | CUMPLE | CUMPLE | Condensado en 4 viñetas para caber en 2 minutos (observación de la verificación anterior) |
| R-57 | Reto: ¿cómo generará valor? | §17 | §13.4 | CUMPLE | CUMPLE | |
| R-58 | Criterio clave: cadena característica → problema/riesgo → necesidad del proceso → característica del modelo → aplicación → resultado → valor | §18 | §5.8, Tabla 7 | PARCIAL | CUMPLE | Cadena explícita para las tres características determinantes |
| R-59 | Conceptos de la guía (§3) aplicados | §3 | §14, Tabla 16 | NO CUMPLE | CUMPLE | Contenido de la v1 perdido en la v2; restaurado sin emojis |
| R-60 | Rúbrica: análisis de características del proyecto | §19 | §1 | CUMPLE | CUMPLE | |
| R-61 | Rúbrica: comparación de modelos | §19 | §3 | PARCIAL | CUMPLE | Ver R-12 |
| R-62 | Rúbrica: selección y justificación | §19 | §4-§5 | CUMPLE | CUMPLE | |
| R-63 | Rúbrica: aplicación del modelo al proyecto | §19 | §6 | PARCIAL | PARCIAL | Contenido completo (Tabla 8); falta la figura legible → DIAG-006 |
| R-64 | Rúbrica: riesgos, valor y trazabilidad | §19 | §7, §8, §10 | CUMPLE | CUMPLE | |
| R-65 | Transición hacia las siguientes actividades (planificación, Semanas 3-4) | §20 | §15, Tabla 17 | NO CUMPLE | CUMPLE | Coherente con el plan de sprints de dos semanas y el Sprint 1 = INC-1 del entregable S3-4 |
| F-01 | Portada: curso, título, integrantes (tal como están), fecha | Solicitud de revisión | Portada | PARCIAL | CUMPLE | Faltaba la fecha y la universidad |
| F-02 | Índice | Solicitud de revisión | Índice | NO CUMPLE | CUMPLE | Índice general, de tablas y de figuras |
| F-03 | Tablas numeradas | Solicitud de revisión | Tablas 1-17 | NO CUMPLE | CUMPLE | |
| F-04 | Figuras numeradas con leyenda | RUTAS.md regla 5 | Figura 1 | PARCIAL | CUMPLE | |
| F-05 | Imágenes por ruta relativa, sin base64 | RUTAS.md regla 4 | Todo | CUMPLE | CUMPLE | |
| F-06 | Markdown limpio compatible con pandoc | Solicitud de revisión | Todo | PARCIAL | CUMPLE | Sin negritas en encabezados, sin escapes `\.`, sin la nota de "resaltado en amarillo" |
| F-07 | Diagramas con fuente editable (PlantUML), SVG en `../../diagramas/svg/`; Mermaid convertido | RUTAS.md; solicitud | Figura 1 | NO CUMPLE | PARCIAL | DIAG-006 abierta (incluye el Mermaid de la v1 como fuente) |
| F-08 | Coherencia con el software real (Flask/SQLite, hexagonal, pytest) | Definición del revisor §5 | §6, §9, §15 | PARCIAL | CUMPLE | Antes: PostgreSQL, Selenium, SonarCloud y GitHub Actions presentados como si estuvieran en uso |
| F-09 | No inventar datos; marcar pendientes | Definición del revisor §4 | §9 | CUMPLE | CUMPLE | `[PENDIENTE]` en enlaces de tablero, workflow de CI y prototipos |

## Resumen

| Momento | CUMPLE | PARCIAL | NO CUMPLE | Total | Cumplimiento |
| --- | --- | --- | --- | --- | --- |
| Antes de la revisión | 56 | 13 | 5 | 74 | 84,5 % |
| Después de la revisión | 71 | 3 | 0 | 74 | 98,0 % |

Los 3 PARCIAL restantes (R-24, R-63, F-07) dependen de una sola solicitud: DIAG-006. Al resolverse, el cumplimiento será del 100 %.

## Cambios aplicados en esta revisión

- Portada completa e índices general, de tablas y de figuras; tablas numeradas 1-17; encabezados limpios y jerárquicos (§11 caso de decisión y §13 reto pasan a ser encabezados de primer nivel con subsecciones numeradas).
- Eliminada la "nota de versión (v2)" (remitía a un resaltado en amarillo inexistente en Markdown).
- §0: conexión con S1 mediante los códigos M1-M6 / B1-B6 y la cadena lógica de la guía.
- §1: restaurada la columna **Evidencia** separada de la situación, con referencias a S1.
- §3: nueva Tabla 4 con el sustento de cada puntuación.
- §4: respuesta explícita a la pregunta central de la guía.
- §5.8 nuevo: cadena de argumentación del criterio clave (Tabla 7).
- §6: figura enlazada al SVG de DIAG-006 y Tabla 8 con los diez elementos aplicados al proyecto.
- §7: incrementos con identificador INC-1..INC-6 y brecha de origen (coherente con S3-4 y el PMV).
- §9: columna **Evidencia** con el estado real del repositorio (Flask, SQLite, pytest, ruff, Playwright en uso; GitHub Actions, SonarCloud, MLflow, WhatsApp y Figma planificados); fila nueva para el marco de desarrollo (Flask).
- §13.3: defensa condensada en cuatro ideas.
- §14 nuevo: conceptos de la guía aplicados (restaurado de la v1).
- §15 nuevo: conexión con las Semanas 3 y 4 y estado del PMV.
- El PNG anterior `img/image1.png` se conserva en disco como referencia y deja de enlazarse.

## Pendientes (con solicitud asociada)

- [ ] Diagrama del modelo de proceso aplicado → `coordinacion/solicitudes/DIAG-006.md` → `diagramas/svg/15_s2_modelo_proceso_aplicado.svg`
- [ ] `[PENDIENTE]` enlace al tablero de GitHub Projects y a los prototipos de Figma (dato del equipo; no se inventa).
- [ ] `[PENDIENTE]` flujo de trabajo de GitHub Actions: no existe `.github/workflows/` en el repositorio. Si el equipo lo configura, actualizar la Tabla 11 (tarea del desarrollador, T-008).
- [ ] Antes de exportar a PDF/DOCX, verificar que el SVG de DIAG-006 exista.
