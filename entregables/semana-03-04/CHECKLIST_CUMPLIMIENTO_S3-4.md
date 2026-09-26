# Checklist de cumplimiento — Semanas 3 y 4

- **Guía:** `guias/S3-4_Guia_trabajo_semanas_3_y_4.md` (y consigna S6 §2.3 para la terminología RAE, DoD y WBS)
- **Entregable revisado:** `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md`
- **Código contrastado (solo lectura):** `anemia_junin/` (src, tests, config, migrations, openapi.yaml, pyproject.toml, docs/adr)
- **Revisor:** revisor-documental · **Tarea:** T-004
- **Fecha:** 2026-09-25
- **Resultado ANTES de la revisión:** 56 / 109 requisitos en CUMPLE (51,4 %); cumplimiento ponderado (CUMPLE = 1; PARCIAL = 0,5) **72,0 %**
- **Resultado DESPUÉS de la revisión:** 108 / 109 requisitos en CUMPLE (99,1 %); cumplimiento ponderado **99,5 %**
- **Único requisito no cerrado:** F-04 (los SVG de las Figuras 1-6 dependen de DIAG-100 a DIAG-105). Con ellos, el cumplimiento llega al 100 %.

> Nota: la guía enumera **16** productos esperados en su §1; las **17** corresponden a las secciones de la estructura del §23. Ambos conjuntos se verifican abajo.

## Matriz de requisitos


### A. Productos esperados (§1 de la guía: 16 viñetas)

| ID | Requisito de la guía (cita / paráfrasis fiel) | Ubicación en guía | Sección del entregable | Estado antes | Estado después | Evidencia / observación |
| --- | --- | --- | --- | --- | --- | --- |
| P-01 | Identificación de las actividades necesarias del proceso | §1 | §3 (Tablas 3-4) | CUMPLE | CUMPLE | Se añade la columna «Origen en el modelo» y se ajustan las actividades al PMV. |
| P-02 | Relación entre actividades, modelo de proceso y entregas de valor | §1 | §2, §3.1, §8.1 (Tabla 10) | CUMPLE | CUMPLE | Columna de origen en el modelo + matriz actividad-incremento-valor. |
| P-03 | Secuencia y dependencias de las actividades | §1 | §4 (Fig. 1, Tabla 5), §11.4 | PARCIAL | CUMPLE | Antes: flujo ASCII y dependencias aisladas en §12. Después: §4 reúne flujo (Figura 1, DIAG-100) y matriz de dependencias. |
| P-04 | Identificación de entradas, actividades, productos de trabajo y salidas | §1 | §3.1 (Tabla 3) | CUMPLE | CUMPLE | Matriz con las 5 columnas exigidas. |
| P-05 | Asignación de responsables | §1 | §5 (Tabla 6) | CUMPLE | CUMPLE | Convertida en matriz RAE. |
| P-06 | Definición de criterios de terminación | §1 | §7 (Tablas 8-9) | PARCIAL | CUMPLE | Antes: criterios basados en SonarCloud, GitHub Actions y Android, inexistentes en el PMV. Después: criterios verificables en el repositorio + DoD por historia. |
| P-07 | Descomposición del proyecto en entregables e incrementos | §1 | §8.2 (Tablas 11-12, Fig. 2) | PARCIAL | CUMPLE | Antes: árbol sin niveles Entregables ni Épicas. Después: 6 niveles. |
| P-08 | Planificación de actividades e iteraciones | §1 | §11 (Tablas 21-23) | PARCIAL | CUMPLE | Antes: «inicio 20 agosto» contradecía el calendario (01-sep) y solo se detallaba el Sprint 1. Después: A01-A21 para los dos sprints de INC-1. |
| P-09 | Estimación de esfuerzo y duración | §1 | §10 (Tablas 19-20), Tabla 22 | PARCIAL | CUMPLE | Antes: 21 SP del INC-1 frente a 54 h solo del Sprint 1 (incoherente). Después: 21 SP / 113 h-persona / 28 días. |
| P-10 | Identificación de dependencias y ruta crítica | §1 | §4.2, §11.4 (Tabla 24, Fig. 5) | PARCIAL | CUMPLE | Antes: sin ruta crítica (solo «cadena crítica IA»). Después: ruta crítica con holguras. |
| P-11 | Elaboración de un cronograma o tablero de planificación | §1 | §11.2-11.3 (Figs. 3-4) | PARCIAL | CUMPLE | Antes: remitía a «instrucciones UML» inexistentes. Después: tablero en GitHub Projects + Gantt (DIAG-102) + cronograma (DIAG-103). |
| P-12 | Definición de mecanismos de seguimiento | §1 | §13.1 (Tabla 26, Fig. 6) | CUMPLE | CUMPLE | Ciclo de seguimiento con mecanismo por paso + burndown. |
| P-13 | Definición de indicadores de avance y desempeño | §1 | §14 (Tabla 30) | CUMPLE | CUMPLE | Se completan indicadores de tiempo y de valor. |
| P-14 | Identificación y control de desviaciones | §1 | §15 (Tablas 31-33) | CUMPLE | CUMPLE | Se añaden desviaciones reales (CI, E2E) además de las simuladas. |
| P-15 | Relación entre planificación, seguimiento y entrega de valor | §1 | §17; §20 pregunta 14 | CUMPLE | CUMPLE | Nueva sección 17 «Valor generado». |
| P-16 | Actualización de la trazabilidad construida en la Guía 2 | §1 | §16 (Tablas 34-35) | CUMPLE | CUMPLE | Extendida hacia S5/S6 (Tabla 35). |

### B. Estructura del documento (§23 de la guía: 17 secciones en orden)

| ID | Requisito de la guía (cita / paráfrasis fiel) | Ubicación en guía | Sección del entregable | Estado antes | Estado después | Evidencia / observación |
| --- | --- | --- | --- | --- | --- | --- |
| E-01 | Sección «1. Características del proyecto» | §23 | §1 | CUMPLE | CUMPLE | Sección presente con el número correcto. Después: sección con el número y el orden de la guía. |
| E-02 | Sección «2. Modelo de proceso seleccionado» | §23 | §2 | CUMPLE | CUMPLE | Sección presente con el número correcto. Después: sección con el número y el orden de la guía. |
| E-03 | Sección «3. Actividades del proceso» | §23 | §3 | CUMPLE | CUMPLE | Sección presente con el número correcto. Después: sección con el número y el orden de la guía. |
| E-04 | Sección «4. Secuencia y dependencias» | §23 | §4 | PARCIAL | CUMPLE | Antes: §4 solo flujo; dependencias en §12. Después: sección con el número y el orden de la guía. |
| E-05 | Sección «5. Responsables» | §23 | §5 | CUMPLE | CUMPLE | Sección presente con el número correcto. Después: sección con el número y el orden de la guía. |
| E-06 | Sección «6. Productos de trabajo» | §23 | §6 | PARCIAL | CUMPLE | Antes: fusionada con criterios en §6. Después: sección con el número y el orden de la guía. |
| E-07 | Sección «7. Criterios de terminación» | §23 | §7 | PARCIAL | CUMPLE | Antes: sin sección propia. Después: sección con el número y el orden de la guía. |
| E-08 | Sección «8. Incrementos de software» | §23 | §8 | PARCIAL | CUMPLE | Antes: existía con otra numeración (desfase por la fusión de §6 y la ubicación de las dependencias en §12). Después: sección con el número y el orden de la guía. |
| E-09 | Sección «9. Priorización» | §23 | §9 | PARCIAL | CUMPLE | Antes: existía con otra numeración (desfase por la fusión de §6 y la ubicación de las dependencias en §12). Después: sección con el número y el orden de la guía. |
| E-10 | Sección «10. Estimación» | §23 | §10 | PARCIAL | CUMPLE | Antes: existía con otra numeración (desfase por la fusión de §6 y la ubicación de las dependencias en §12). Después: sección con el número y el orden de la guía. |
| E-11 | Sección «11. Planificación» | §23 | §11 | PARCIAL | CUMPLE | Antes: existía con otra numeración (desfase por la fusión de §6 y la ubicación de las dependencias en §12). Después: sección con el número y el orden de la guía. |
| E-12 | Sección «12. Hitos y entregables» | §23 | §12 | PARCIAL | CUMPLE | Antes: existía con otra numeración (desfase por la fusión de §6 y la ubicación de las dependencias en §12). Después: sección con el número y el orden de la guía. |
| E-13 | Sección «13. Seguimiento» | §23 | §13 | PARCIAL | CUMPLE | Antes: existía con otra numeración (desfase por la fusión de §6 y la ubicación de las dependencias en §12). Después: sección con el número y el orden de la guía. |
| E-14 | Sección «14. Indicadores» | §23 | §14 | PARCIAL | CUMPLE | Antes: existía con otra numeración (desfase por la fusión de §6 y la ubicación de las dependencias en §12). Después: sección con el número y el orden de la guía. |
| E-15 | Sección «15. Riesgos y desviaciones» | §23 | §15 | PARCIAL | CUMPLE | Antes: solo «Control de desviaciones», sin registro de riesgos. Después: sección con el número y el orden de la guía. |
| E-16 | Sección «16. Trazabilidad» | §23 | §16 | PARCIAL | CUMPLE | Antes: existía con otra numeración (desfase por la fusión de §6 y la ubicación de las dependencias en §12). Después: sección con el número y el orden de la guía. |
| E-17 | Sección «17. Valor generado» | §23 | §17 | NO CUMPLE | CUMPLE | Antes: no existía; el valor estaba disperso en el reto (J). Después: sección con el número y el orden de la guía. |
| E-18 | Orden de las 17 secciones idéntico al de la guía; actividades complementarias al final | §23 | Índice; §18-20 | PARCIAL | CUMPLE | Caso de decisión (§18), reto (§19) y preguntas (§20) después de las 17 secciones. |

### C. Matrices, flujos y preguntas por actividad

| ID | Requisito de la guía (cita / paráfrasis fiel) | Ubicación en guía | Sección del entregable | Estado antes | Estado después | Evidencia / observación |
| --- | --- | --- | --- | --- | --- | --- |
| M-01 | Act. 1: Matriz de actividades (Actividad, Propósito, Entrada, Producto de trabajo, Salida); no genérica | §5 | Tabla 3 | CUMPLE | CUMPLE | Añadida la columna de origen para demostrar que no es genérica. |
| M-02 | Act. 1: 5 preguntas orientadoras respondidas | §5 | §3.3 | CUMPLE | CUMPLE | Respuestas actualizadas al PMV. |
| M-03 | Act. 2: Flujo con inicio, actividades, decisiones, iteraciones, productos, validaciones, entregas, retroalimentación y mejora | §6 | §4.1, Figura 1 | PARCIAL | CUMPLE | Antes: ASCII sin inicio/fin ni productos. Después: descripción de 14 pasos + DIAG-100. |
| M-04 | Act. 2: Pregunta orientadora (¿modelo seleccionado o proceso tradicional?) | §6 | §4.1 | CUMPLE | CUMPLE |  |
| M-05 | Act. 3: Matriz de responsabilidades con filas Requisitos, Análisis, Diseño, Implementación, Pruebas, Integración, Despliegue, Evaluación (RAE en S6 §2.3) | §7 | Tabla 6 | PARCIAL | CUMPLE | Antes: sin filas separadas de Despliegue y Evaluación, y revisor/aprobador fusionados. Después: RAE completa. |
| M-06 | Act. 3: Pregunta orientadora | §7 | §5 | CUMPLE | CUMPLE |  |
| M-07 | Act. 4: Matriz Actividad / Producto / Criterio de terminación / Evidencia (DoD, S6 §2.3) | §8 | Tablas 7-9 | CUMPLE | CUMPLE | Añadida la DoD por historia. |
| M-08 | Act. 4: Pregunta clave (demostrar objetivamente la terminación) | §8 | §7 | CUMPLE | CUMPLE |  |
| M-09 | Act. 5: Matriz Incremento / Funcionalidad / Actividades / Resultado / Valor / Indicador (≥ 5 filas) | §9 | Tabla 10 | CUMPLE | CUMPLE | 6 incrementos. |
| M-10 | Act. 6: WBS Proyecto → Entregables → Incrementos → Épicas → HU → Tareas | §10 | Tabla 11, Figura 2 | PARCIAL | CUMPLE | DIAG-101. |
| M-11 | Act. 6: Tabla Incremento / Funcionalidad / Historia / Tarea / Prioridad | §10 | Tabla 12 | CUMPLE | CUMPLE | 16 tareas T01-T16 alineadas con el código. |
| M-12 | Act. 7: Matriz Valor / Riesgo / Dependencia / Complejidad / Prioridad (1-5) considerando validación y factibilidad técnica | §11 | Tablas 17-18 | PARCIAL | CUMPLE | Antes: factibilidad técnica implícita y sin priorización de HU. Después: explicitada + matriz de HU. |
| M-13 | Act. 7: Pregunta orientadora (¿lo fácil o lo de mayor valor/riesgo?) | §11 | §9 | CUMPLE | CUMPLE |  |
| M-14 | Act. 8: Matriz Elemento / Estimación / Unidad / Complejidad / Incertidumbre; técnica coherente con el modelo | §12 | Tablas 19-20 | CUMPLE | CUMPLE | Unidad añadida a la tabla de puntos. |
| M-15 | Act. 8: Pregunta clave (incertidumbre y su control) | §12 | §10 | CUMPLE | CUMPLE |  |
| M-16 | Act. 9: Plan de trabajo con IDs A01… (ID, Actividad, Incremento, Responsable, Inicio, Fin, Dependencia, Entregable) | §13 | Tabla 22 | PARCIAL | CUMPLE | Antes: A01-A15 con actividades no reales (PostgreSQL, Figma, SonarCloud, despliegue en posta). Después: A01-A21 alineadas con el repositorio. |
| M-17 | Act. 9: Cronograma o tablero que represente el proceso | §13 | §11.2-11.3, Figs. 3-4 | PARCIAL | CUMPLE | DIAG-102, DIAG-103. |
| M-18 | Act. 10: Matriz Actividad / Depende de / Tipo / Riesgo / Acción | §14 | Tabla 5 | PARCIAL | CUMPLE | Antes: dependencia de WhatsApp atribuida a INC-5 (error). Corregida a INC-4. |
| M-19 | Ruta crítica (producto esperado) | §1, §14 | §11.4, Tabla 24, Figura 5 | NO CUMPLE | CUMPLE | DIAG-104. |
| M-20 | Act. 10: Pregunta orientadora | §14 | §4.2 | CUMPLE | CUMPLE |  |
| M-21 | Act. 11: Matriz de hitos (Hito, Condición, Entregable, Fecha, Evidencia; ≥ H1-H4) | §15 | Tabla 25 | CUMPLE | CUMPLE | H0-H7; evidencias no disponibles marcadas [PENDIENTE]. |
| M-22 | Act. 11: Pregunta clave (¿avance o valor?) | §15 | §12 | CUMPLE | CUMPLE |  |
| M-23 | Act. 12: Flujo Planificado → … → Actualización del plan | §16 | Tabla 26 | CUMPLE | CUMPLE |  |
| M-24 | Act. 12: Matriz de seguimiento con filas Actividades, Historias, Horas, Incrementos, Pruebas | §16 | Tablas 27-28 | PARCIAL | CUMPLE | Antes: faltaban las filas Actividades e Incrementos y el «real» no se declaraba simulado. Después: completas + tabla de estado verificable. |
| M-25 | Act. 13: Matriz de indicadores con filas Avance, Cumplimiento, Calidad, Tiempo, Valor | §17 | Tabla 30 | PARCIAL | CUMPLE | Antes: sin indicador de Tiempo (duración real/planificada, ciclo, entrega). Después: completos. |
| M-26 | Act. 13: Pregunta orientadora (valor frente a consumo de recursos) | §17 | §14 | CUMPLE | CUMPLE |  |
| M-27 | Act. 14: Matriz Desviación / Causa / Impacto / Decisión / Responsable / Nueva fecha | §18 | Tabla 33 | CUMPLE | CUMPLE |  |
| M-28 | Act. 14: Pregunta clave (seguimiento frente a modificar el plan) | §18 | §15 | CUMPLE | CUMPLE | Ejemplos ligados a las holguras calculadas. |
| M-29 | Act. 15: Simulación de reunión con los roles sugeridos y las 10 preguntas | §19 | §13.4, Tabla 29 | PARCIAL | CUMPLE | Antes: sin mapeo de roles (producto, datos/IA). Después: tabla de roles; 10 respuestas coherentes con la ruta crítica. |
| M-30 | Act. 16: Matriz de trazabilidad (12 elementos) | §20 | Tabla 34 | CUMPLE | CUMPLE | Más la Tabla 35 hacia S5/S6. |
| M-31 | Act. 17: Caso de decisión, 10 preguntas | §21 | §18 | CUMPLE | CUMPLE |  |

### D. Reto de aplicación (§22): incremento prioritario, apartados A-J

| ID | Requisito de la guía (cita / paráfrasis fiel) | Ubicación en guía | Sección del entregable | Estado antes | Estado después | Evidencia / observación |
| --- | --- | --- | --- | --- | --- | --- |
| RT-A | Reto A. Objetivo del incremento | §22 | §19.A | CUMPLE | CUMPLE |  |
| RT-B | Reto B. Funcionalidades | §22 | §19.B | PARCIAL | CUMPLE | Antes: HU con campos y reglas distintos del PMV (p. ej. «estado de control», umbrales NTS 134). Después: HIST-1.1 a 1.5 = código. |
| RT-C | Reto C. Actividades | §22 | §19.C | PARCIAL | CUMPLE | Antes: Figma, SonarCloud, GitHub Actions y despliegue en posta (no existen). Después: A01-A21 reales; el resto al backlog. |
| RT-D | Reto D. Responsables | §22 | §19.D | CUMPLE | CUMPLE |  |
| RT-E | Reto E. Estimación | §22 | §19.E | PARCIAL | CUMPLE | Antes: 21 SP / 54 h incoherentes. Después: 21 SP / 113 h-persona / 28 días. |
| RT-F | Reto F. Dependencias | §22 | §19.F | CUMPLE | CUMPLE |  |
| RT-G | Reto G. Riesgos | §22 | §19.G | CUMPLE | CUMPLE | El riesgo de Android se sustituye por riesgos reales del PMV. |
| RT-H | Reto H. Indicadores | §22 | §19.H | PARCIAL | CUMPLE | Antes: SonarCloud. Después: ruff, cobertura, burndown, aceptación. |
| RT-I | Reto I. Criterios de aceptación | §22 | §19.I | PARCIAL | CUMPLE | Antes: 4 criterios generales, uno no medible (< 3 min) y un acta firmada inexistente. Después: criterios Dado-Cuando-Entonces por HU verificados contra el código; < 3 min → BT-08; acta [PENDIENTE]. |
| RT-J | Reto J. Valor | §22 | §19.J | CUMPLE | CUMPLE |  |

### E. Preguntas de análisis (§24: 15 preguntas)

| ID | Requisito de la guía (cita / paráfrasis fiel) | Ubicación en guía | Sección del entregable | Estado antes | Estado después | Evidencia / observación |
| --- | --- | --- | --- | --- | --- | --- |
| Q-01 | Pregunta de análisis 1 respondida | §24 | §20, n.° 1 | CUMPLE | CUMPLE | Actualizada a la nueva numeración y al PMV. |
| Q-02 | Pregunta de análisis 2 respondida | §24 | §20, n.° 2 | CUMPLE | CUMPLE |  |
| Q-03 | Pregunta de análisis 3 respondida | §24 | §20, n.° 3 | CUMPLE | CUMPLE | Actualizada a la nueva numeración y al PMV. |
| Q-04 | Pregunta de análisis 4 respondida | §24 | §20, n.° 4 | CUMPLE | CUMPLE | Actualizada a la nueva numeración y al PMV. |
| Q-05 | Pregunta de análisis 5 respondida | §24 | §20, n.° 5 | CUMPLE | CUMPLE | Actualizada a la nueva numeración y al PMV. |
| Q-06 | Pregunta de análisis 6 respondida | §24 | §20, n.° 6 | CUMPLE | CUMPLE | Actualizada a la nueva numeración y al PMV. |
| Q-07 | Pregunta de análisis 7 respondida | §24 | §20, n.° 7 | CUMPLE | CUMPLE | Actualizada a la nueva numeración y al PMV. |
| Q-08 | Pregunta de análisis 8 respondida | §24 | §20, n.° 8 | CUMPLE | CUMPLE |  |
| Q-09 | Pregunta de análisis 9 respondida | §24 | §20, n.° 9 | CUMPLE | CUMPLE | Actualizada a la nueva numeración y al PMV. |
| Q-10 | Pregunta de análisis 10 respondida | §24 | §20, n.° 10 | CUMPLE | CUMPLE |  |
| Q-11 | Pregunta de análisis 11 respondida | §24 | §20, n.° 11 | CUMPLE | CUMPLE |  |
| Q-12 | Pregunta de análisis 12 respondida | §24 | §20, n.° 12 | CUMPLE | CUMPLE |  |
| Q-13 | Pregunta de análisis 13 respondida | §24 | §20, n.° 13 | CUMPLE | CUMPLE |  |
| Q-14 | Pregunta de análisis 14 respondida | §24 | §20, n.° 14 | CUMPLE | CUMPLE |  |
| Q-15 | Pregunta de análisis 15 respondida | §24 | §20, n.° 15 | CUMPLE | CUMPLE | Actualizada a la nueva numeración y al PMV. |

### F. Rúbrica (§26, nivel «Excelente») y criterio clave (§25)

| ID | Requisito de la guía (cita / paráfrasis fiel) | Ubicación en guía | Sección del entregable | Estado antes | Estado después | Evidencia / observación |
| --- | --- | --- | --- | --- | --- | --- |
| RB-01 | Diseño de actividades: identifica, organiza y sustenta según el modelo | §26 | Todo el documento | PARCIAL | CUMPLE | Antes: actividades no coherentes con el PMV. |
| RB-02 | Planificación y estimación: descompone, prioriza, estima y planifica con dependencias e hitos sustentados | §26 | Todo el documento | PARCIAL | CUMPLE | Antes: sin ruta crítica ni Gantt; estimación incoherente. |
| RB-03 | Seguimiento y control: indicadores, mecanismos y acciones ante desviaciones | §26 | Todo el documento | CUMPLE | CUMPLE |  |
| RB-04 | Integración proceso-proyecto: actividades, responsables, productos, riesgos, planificación e incrementos relacionados | §26 | Todo el documento | CUMPLE | CUMPLE |  |
| RB-05 | Entrega de valor y trazabilidad: actividades → entregas → resultados → indicadores → valor | §26 | Todo el documento | PARCIAL | CUMPLE | Antes: sin sección de valor ni trazabilidad hacia S5/S6. |
| CK-01 | Criterio clave: cadena necesidad → modelo → actividad → producto → responsable → planificación → ejecución → seguimiento → resultado → valor | §25 | §17 | PARCIAL | CUMPLE | Antes: cadena implícita. Después: párrafo explícito en §17. |

### G. Formato, coherencia con el código y requisitos del encargo

| ID | Requisito de la guía (cita / paráfrasis fiel) | Ubicación en guía | Sección del entregable | Estado antes | Estado después | Evidencia / observación |
| --- | --- | --- | --- | --- | --- | --- |
| F-01 | Portada (institución, curso, proyecto, equipo, fecha) | Encargo / S6 | Portada | PARCIAL | CUMPLE | Antes: encabezado sin institución ni fecha. |
| F-02 | Índice | Encargo | Índice | NO CUMPLE | CUMPLE | Índice textual (compatible con pandoc y con GitHub). |
| F-03 | Tablas numeradas y tituladas | Encargo | Tablas 1-38 | NO CUMPLE | CUMPLE |  |
| F-04 | Figuras numeradas; diagramas reales (no ASCII ni notas «UML») | Encargo, T-004 | Figuras 1-6 | NO CUMPLE | PARCIAL | Enlaces SVG insertados; los SVG los produce el diagramador (DIAG-100 a DIAG-105). Pasa a CUMPLE cuando existan los archivos. |
| F-05 | Sin base64; imágenes con ruta relativa | RUTAS.md | Todo | CUMPLE | CUMPLE | Rutas ../../diagramas/svg/… |
| F-06 | Markdown limpio compatible con pandoc (sin emojis ni bloques ASCII) | Encargo | Todo | PARCIAL | CUMPLE | Eliminados los emojis y los bloques de texto preformateado. |
| F-07 | HU, criterios e incremento prioritario coinciden con el PMV real | Encargo | §8.4, §19 | NO CUMPLE | CUMPLE | Contrastado con src/, tests/, openapi.yaml, config/, migrations/ y ADR. |
| F-08 | Lo no implementado figura como backlog, no como hecho | Encargo | Tabla 13 | NO CUMPLE | CUMPLE | BT-01 a BT-10. |
| F-09 | Sección «Definición técnica del software» (stack, arquitectura hexagonal, módulos) | Encargo | §8.4 (Tablas 14-16) | NO CUMPLE | CUMPLE |  |
| F-10 | Trazabilidad con S2 y hacia S5/S6 | Encargo | §16 (Tablas 34-35) | PARCIAL | CUMPLE |  |
| F-11 | Redacción académica sin afirmaciones no sustentadas; datos faltantes como [PENDIENTE] | Agente | Todo | PARCIAL | CUMPLE | Simulación rotulada como tal; actas y cifras reales marcadas [PENDIENTE]. |
| F-12 | Un solo archivo vigente, sin sufijo de versión | RUTAS.md | Pie del documento | PARCIAL | CUMPLE | Eliminado «— v1». |
| F-13 | Referencias en formato académico | Agente | §21 | PARCIAL | CUMPLE | Formato APA; NTS 213 pendiente de verificación (INV-001). |

## Resumen por bloque

| Bloque | N.° de requisitos | CUMPLE antes | CUMPLE después |
| --- | --- | --- | --- |
| A. Productos esperados (§1 de la guía: 16 viñetas) | 16 | 9 | 16 |
| B. Estructura del documento (§23 de la guía: 17 secciones en orden) | 18 | 4 | 18 |
| C. Matrices, flujos y preguntas por actividad | 31 | 20 | 31 |
| D. Reto de aplicación (§22): incremento prioritario, apartados A-J | 10 | 5 | 10 |
| E. Preguntas de análisis (§24: 15 preguntas) | 15 | 15 | 15 |
| F. Rúbrica (§26, nivel «Excelente») y criterio clave (§25) | 6 | 2 | 6 |
| G. Formato, coherencia con el código y requisitos del encargo | 13 | 1 | 12 |
| **Total** | **109** | **56** | **108** |

## Cambios aplicados en esta revisión

- Reestructuración completa según las 17 secciones del §23 de la guía, con portada, índice, tablas numeradas (1-38) y figuras numeradas (1-6); caso de decisión, reto y preguntas de análisis en las secciones 18-20.
- Historias HIST-1.1 a HIST-1.5 (HU-01 a HU-05) y sus criterios de aceptación reescritos según lo que el PMV implementa: registro con dosaje inicial atómico y DNI único (409), expediente con edición restringida y dosajes inmutables, validación por campo (400) y clasificación de la hemoglobina con ajuste por altitud y umbrales por edad leídos de `config/normativa_v1.json`, listado 6-59 meses ordenado por severidad, reporte con indicador de aceptación, API REST `/api/v1` con OpenAPI.
- Nueva §8.4 «Definición técnica del software» (pila, arquitectura hexagonal, módulos, contrato de API, modelo de datos, configuración normativa, decisiones y fuera de alcance).
- Nueva Tabla 13 (backlog técnico BT-01 a BT-10) con todo lo que el plan anterior daba por hecho y el código no tiene.
- Plan A01-A21, estimación (21 SP / 113 h-persona), ruta crítica y holguras recalculados; simulación de reunión y matriz de seguimiento reescritas para ser coherentes con la ruta crítica y rotuladas como simuladas; nueva Tabla 28 con el estado verificable del repositorio.
- Matriz RAE, DoD por historia, WBS de 6 niveles, priorización de HU, indicadores de tiempo y de valor, registro de riesgos, trazabilidad hacia S5/S6 (Tabla 35) y sección 17 «Valor generado».
- Corregidos: dependencia de WhatsApp atribuida a INC-5; «inicio 20 agosto»; referencias a una «Sección 13» de instrucciones UML inexistente; emojis y bloques ASCII; sufijo «v1».

## Pendientes (con solicitud asociada)

- [ ] Figura 1, diagrama de actividades del proceso → `coordinacion/solicitudes/DIAG-100.md` → `diagramas/svg/30_s34_flujo_actividades_proceso.svg`
- [ ] Figura 2, WBS → `DIAG-101` → `diagramas/svg/31_s34_wbs_proyecto.svg`
- [ ] Figura 3, Gantt del INC-1 → `DIAG-102` → `diagramas/svg/32_s34_gantt_incremento1.svg`
- [ ] Figura 4, cronograma de sprints e hitos → `DIAG-103` → `diagramas/svg/33_s34_cronograma_sprints_hitos.svg`
- [ ] Figura 5, red y ruta crítica → `DIAG-104` → `diagramas/svg/34_s34_red_ruta_critica_inc1.svg`
- [ ] Figura 6, burndown del Sprint 1 → `DIAG-105` → `diagramas/svg/35_s34_burndown_sprint1.svg`
- [ ] Discrepancias documento-código (11 puntos) → `coordinacion/solicitudes/DEV-100.md`
- [ ] Vigencia NTS 134 frente a NTS 213-2024 y valores transcritos → `coordinacion/solicitudes/INV-001.md` (abierta por T-002; se reutiliza)
- [ ] `[PENDIENTE]` en el entregable: acta de revisión/aceptación H1, cifras reales de ejecución de pruebas y cobertura (T-008), registro real de horas, meta del indicador de calidad del registro acordada con la posta.
- [ ] Nombre del checklist: el encargo pidió `CHECKLIST_CUMPLIMIENTO_S3-4.md`; `RUTAS.md` indica `CHECKLIST_cumplimiento.md`. Se respetó el encargo; el orquestador decide si renombra.
