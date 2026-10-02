# DIAG-100 — Diagrama de actividades del proceso de software (Semanas 3-4)

- **Estado:** RESUELTA  <!-- ABIERTA | EN CURSO | RESUELTA | RECHAZADA -->
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-004
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Alta

## Tipo de diagrama

- [ ] BPMN / flujo de proceso (AS-IS / TO-BE, carriles)
- [ ] UML casos de uso
- [ ] UML clases / modelo de dominio
- [ ] UML secuencia
- [x] UML actividad
- [ ] UML componentes / despliegue
- [ ] C4 (contexto / contenedores / componentes)
- [ ] Modelo de datos (ER)
- [ ] Gantt / cronograma / WBS
- [ ] Otro: ____

## Requisito que cubre

- **Guía:** `guias/S3-4_Guia_trabajo_semanas_3_y_4.md` — Actividad 2 (§6): «Construya el flujo específico de actividades de su proyecto. El flujo debe identificar: inicio, actividades, decisiones, iteraciones, productos de trabajo, validaciones, entregas, retroalimentación, mejora». No debe ser un proceso genérico.
- **Entregable destino:** `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` — §4.1, Figura 1 (enlace ya insertado con marcador `<!-- DIAG-100 pendiente -->`).

## Contenido requerido

Diagrama de actividades UML con **tres carriles** (*swimlanes*): **Equipo Scrum** (Porras V., Auqui H., Huamani R.), **Personal de salud / Product Owner** y **Automatización** (pytest + cobertura + ruff; GitHub Actions desde BT-01). Un cuarto bloque o región paralela para el **subciclo MLOps (desde INC-5)**.

Nodos, en este orden (texto exacto; entre corchetes, el producto de trabajo como objeto/nota asociado):

1. **Inicio** (nodo inicial) → «Product Backlog priorizado (TO-BE S1 + orden de incrementos S2)».
2. [Equipo] «Sprint Planning» → [Sprint Backlog].
3. [Equipo + Personal de salud] «Refinamiento de requisitos» → [Historias «Ready» con criterios Dado–Cuando–Entonces].
4. **Decisión 1:** «¿Criterios de aceptación verificables?» — No → vuelve a «Refinamiento de requisitos»; Sí → continúa.
5. [Equipo] «Análisis y diseño» → [ADR, esquema de datos, contrato OpenAPI].
6. [Equipo] «Implementación» → [Código fuente / pull request].
7. [Automatización] «Pruebas automatizadas (unitarias, persistencia, API, arquitectura; sin conexión desde INC-3)» → [Reporte de pruebas y cobertura].
8. **Decisión 2:** «¿Pruebas en verde y cobertura ≥ 80 %?» — No → vuelve a «Implementación»; Sí → continúa.
9. [Equipo] «Revisión de código y análisis estático (ruff)» → [Pull request aprobado].
10. [Automatización] «Integración y verificación automatizada» → [Versión integrada].
11. [Equipo] «Despliegue (INC-1: demostración local; desde INC-3: posta piloto)» → nodo/nota **Entrega del incremento**.
12. [Personal de salud] «Revisión del sprint (validación con el usuario)» → [Acta de revisión].
13. **Decisión 3:** «¿Incremento aceptado?» — No → «Registrar observaciones en el backlog» (flecha de **retroalimentación** que vuelve a «Sprint Planning» del siguiente sprint); Sí → continúa.
14. [Equipo] «Medición de indicadores» → [Tablero de indicadores].
15. [Equipo] «Retrospectiva (mejora)» → [Plan de mejora].
16. **Decisión 4 (iteración):** «¿Quedan incrementos en el backlog?» — Sí → vuelve a «Sprint Planning» (etiqueta «siguiente sprint»); No → **Fin** (nodo final) con nota «Paso a operación con Kanban (S2)».
17. **Subciclo MLOps (desde INC-5), en paralelo (fork/join o región separada) partiendo de «Medición de indicadores»:** «Datos del HIS» → «Limpieza y versionado (MLflow)» → «Experimentación (Random Forest vs. Gradient Boosting)» → «Entrenamiento» → «Evaluación con personal clínico» → «Registro y publicación del artefacto» (flecha hacia «Integración y verificación automatizada») → «Monitoreo por zona» → **Decisión 5:** «¿Desempeño < umbral?» — Sí → «Reentrenamiento» (vuelve a «Entrenamiento»); No → continúa monitoreo.

## Fuentes de verdad

- `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` §3.1 (Tabla 3) y §4.1 (descripción textual numerada del flujo).
- `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md` §6 (ciclo principal y subciclo MLOps).

## Nombre de archivo sugerido

`30_s34_flujo_actividades_proceso` → se producirán:
- `diagramas/src/30_s34_flujo_actividades_proceso.puml`
- `diagramas/png/30_s34_flujo_actividades_proceso.png`
- `diagramas/svg/30_s34_flujo_actividades_proceso.svg`

(Rango NN 30-39 reservado para S3-4 para no chocar con DIAG-001+, que usa 10-15. Si se renumera, avisar para actualizar el enlace.)

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4
- [ ] Texto en español, sin tildes rotas
- [ ] Aparecen los 9 elementos de la guía: inicio, actividades, decisiones, iteraciones, productos de trabajo, validaciones, entregas, retroalimentación, mejora (y fin)
- [ ] Tres carriles + subciclo MLOps marcado «desde INC-5»
- [ ] Coherente con la Tabla 3 y la descripción de §4.1 del entregable

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** 2026-10-01
- **Resultado:** RESUELTA (cierre administrativo del sincronizador, 2026-10-01: existen fuente `diagramas/src/30_s34_flujo_actividades_proceso.puml`, `diagramas/png/30_s34_flujo_actividades_proceso.png` y `diagramas/svg/30_s34_flujo_actividades_proceso.svg`; la verificación del contenido frente al entregable corresponde a revisor-documental / inspector-guia)
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 1. Diagrama de actividades del proceso de software del proyecto (ciclo por sprint y subciclo MLOps), con carriles para el equipo, el personal de salud y la automatización (elaboración propia).](../../diagramas/svg/30_s34_flujo_actividades_proceso.svg)`
- **Notas:**
