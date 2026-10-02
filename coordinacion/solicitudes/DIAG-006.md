# DIAG-006 — Modelo de proceso aplicado al proyecto (Semana 2)

- **Estado:** RESUELTA
- **Solicitante:** revisor-documental
- **Destino:** diagramador
- **Tarea relacionada:** T-003
- **Fecha de apertura:** 2026-09-25
- **Prioridad:** Alta

## Tipo de diagrama

- [x] UML actividad (ciclo del proceso con particiones Scrum / DevOps / MLOps) en PlantUML.

## Requisito que cubre

- **Guía:** `guias/S2_Guia_trabajo_semana_2.md` — §9 Actividad 5 "Representar el modelo de proceso". Debe mostrar **1) entrada/requerimientos, 2) planificación, 3) desarrollo, 4) integración, 5) pruebas, 6) retroalimentación, 7) entrega, 8) medición, 9) mejora, 10) repetición o siguiente incremento**. "No se debe copiar un diagrama de Scrum, Kanban o DevOps de Internet": debe representar **cómo se aplica el modelo a este proyecto**. Criterio de rúbrica "Aplicación del modelo al proyecto".
- **Entregable destino:** `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md` — §6 "Representación del proceso", Figura 1.
- **Motivo:** la figura actual (`entregables/semana-02/img/image1.png`, 430×551 px) es ilegible. El diagrama existente `02_modelo_proceso` es genérico (no nombra incrementos, actores ni el subciclo MLOps), por eso no se reutiliza.

## Contenido requerido

Título: "Aplicación del modelo al proyecto — base iterativa-incremental · Scrum (gestión) · DevOps (construcción y entrega) · MLOps (modelo predictivo)".

**Particiones / carriles (3 + usuarios):** Usuarios (personal de salud, agente comunitario, microred) · Scrum (gestión) · DevOps (ingeniería) · MLOps (datos y modelo, activo desde INC-5).

**Ciclo principal numerado (cada caja muestra su número de elemento de la guía):**

1. **Entrada / requerimientos** (Usuarios → Scrum): "TO-BE de la Semana 1 → Product Backlog priorizado con el personal de salud (INC-1…INC-6, historias HIST-n.m)".
2. **Planificación** (Scrum): "Sprint Planning: sprint de 2 semanas, historias del incremento vigente".
3. **Desarrollo** (DevOps): "Construcción del incremento (p. ej., INC-1: registro nominal en Flask + SQLite, arquitectura hexagonal) y revisión de código".
4. **Integración** (DevOps): "Integración continua de cada cambio: build, análisis estático (ruff)".
5. **Pruebas** (DevOps): "Pruebas automatizadas (pytest): dominio, persistencia, API y reglas de arquitectura; prueba de sincronización offline desde INC-3". Decisión **¿Cumple la Definición de Hecho?** — No → vuelve a 3.
6. **Retroalimentación** (Scrum + Usuarios): "Sprint Review con la posta, el agente comunitario y la microred (sesiones cortas o remotas)". Decisión **¿Incremento aceptado?** — No → vuelve al backlog (1).
7. **Entrega** (DevOps): "Despliegue en posta piloto antes de extender".
8. **Medición** (Scrum + Usuarios): "Indicadores de la Semana 1 por incremento: registros sin error crítico, cobertura oportuna, sincronización exitosa, entrega de WhatsApp, precisión del modelo".
9. **Mejora** (Scrum): "Retrospectiva: ajuste del proceso y del backlog".
10. **Repetición / siguiente incremento** (Scrum): "INC-(n+1)" → flecha de retorno a 2.

**Subciclo MLOps (partición MLOps, rotular "activo desde INC-5"):**
"Datos HIS, dosajes, adherencia y visitas" → "Validación y limpieza de datos" → "Ingeniería de variables" → "Entrenamiento y evaluación (Random Forest vs. Gradient Boosting)" → "Validación de alertas con criterio profesional" → "Publicación del artefacto del modelo" (flecha hacia 7 Entrega) → "Monitoreo de desempeño y sesgo por zona" (recibe flecha desde 8 Medición) → decisión **¿Degradación?** — Sí → "Reentrenamiento" (vuelve a Entrenamiento).

**Franja inferior (secuencia de incrementos):** INC-1 Registro nominal → INC-2 Agenda NTS y alertas → INC-3 Offline y sincronización → INC-4 WhatsApp y barreras → INC-5 Modelo predictivo → INC-6 Tablero territorial.

## Fuentes de verdad

- `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md` §4, §6 (texto descriptivo del ciclo), §7 (incrementos).
- `entregables/semana-02/img/image1.png` (referencia visual anterior, específica del proyecto).
- `archivo/versiones-anteriores/semana-02/Entregable_Semana2_Anemia_Junin_v1.md` §6 (Mermaid original con Scrum/DevOps/MLOps).
- `anemia_junin/pyproject.toml` (pytest, ruff, Flask) y `anemia_junin/docs/adr/001_arquitectura_hexagonal.md`.

## Nombre de archivo sugerido

`15_s2_modelo_proceso_aplicado` → `diagramas/src/15_s2_modelo_proceso_aplicado.puml`, `diagramas/png/15_s2_modelo_proceso_aplicado.png`, `diagramas/svg/15_s2_modelo_proceso_aplicado.svg`.

## Criterios de aceptación

- [ ] Legible a 100 % de zoom en A4.
- [ ] Texto en español, sin tildes rotas.
- [ ] Los 10 elementos de la guía aparecen numerados 1–10 con su nombre exacto.
- [ ] Se ve el retorno al siguiente incremento y el subciclo MLOps conectado a Entrega y Medición.
- [ ] Nombra incrementos y actores del proyecto (no es un diagrama genérico).
- [ ] Registrado en `diagramas/README.md` (usado en S2).

---

## Respuesta (la rellena el diagramador)

- **Fecha de cierre:** 2026-10-01
- **Resultado:** RESUELTA (cierre administrativo del sincronizador, 2026-10-01: existen fuente `diagramas/src/15_s2_modelo_proceso_aplicado.puml`, `diagramas/png/15_s2_modelo_proceso_aplicado.png` y `diagramas/svg/15_s2_modelo_proceso_aplicado.svg`; la verificación del contenido frente al entregable corresponde a revisor-documental / inspector-guia)
- **Rutas producidas:**
- **Snippet para incrustar en el .md:** `![Figura 1. Aplicación del modelo de proceso al proyecto: ciclo principal con los diez elementos de la guía y subciclo MLOps desde INC-5 (elaboración propia).](../../diagramas/svg/15_s2_modelo_proceso_aplicado.svg)`
- **Notas:**
