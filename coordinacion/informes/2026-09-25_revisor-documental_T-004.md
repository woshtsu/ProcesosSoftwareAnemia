# Informe de salida — revisor-documental — T-004 (Semanas 3 y 4)

- **Agente:** revisor-documental
- **Fecha:** 2026-09-25
- **Tareas / solicitudes atendidas:** T-004; abre DIAG-100 a DIAG-105 y DEV-100; reutiliza INV-001
- **Estado final:** HECHO (texto al 100 %; solo quedan las figuras SVG, que dependen del diagramador)

## Resumen

Se verificó el entregable S3-4 frente a los 109 requisitos extraídos de la guía (16 productos esperados, 17 secciones más el orden, 31 matrices, flujos y preguntas por actividad, reto A-J, 15 preguntas de análisis, rúbrica y criterio clave, y formato/coherencia con el código). El cumplimiento pasó de **51,4 % estricto (56/109 en CUMPLE) / 72,0 % ponderado** a **99,1 % estricto (108/109) / 99,5 % ponderado**. El único requisito abierto es F-04, las figuras SVG (DIAG-100 a DIAG-105).

El documento se reestructuró en las 17 secciones del §23 y se alineó con el PMV real de `anemia_junin/`: las historias HIST-1.1 a HIST-1.5 (HU-01 a HU-05), sus criterios de aceptación y el plan A01-A21 ahora describen lo que el código implementa. Lo que el plan anterior daba por hecho y el código no tiene (CI, SonarCloud, PostgreSQL, despliegue en la posta, Figma, E2E/carga) pasó al backlog técnico BT-01 a BT-10. Se añadió la §8.4 «Definición técnica del software».

## Archivos creados / modificados / movidos

| Acción | Ruta | Nota |
| --- | --- | --- |
| modificado | `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` | Reescritura estructural (portada, índice, 17 secciones + 18-21, anexo de cambios; 38 tablas, 6 figuras) |
| creado | `entregables/semana-03-04/CHECKLIST_CUMPLIMIENTO_S3-4.md` | 109 requisitos, estado antes/después y evidencia. Nombre según el encargo (RUTAS.md sugiere `CHECKLIST_cumplimiento.md`) |
| creado | `coordinacion/solicitudes/DIAG-100.md` … `DIAG-105.md` | Diagramas con datos exactos |
| creado | `coordinacion/solicitudes/DEV-100.md` | 11 discrepancias entre documento y código |
| modificado | `coordinacion/TABLERO.md` | T-004 → HECHO; solicitudes registradas |

## Verificación realizada

- Lectura íntegra de la guía S3-4, del entregable anterior, del entregable S2, de la consigna S6 (§2.3) y de la extracción del informe S5.
- Contraste con el código (solo lectura): `pyproject.toml`, `config/normativa_v1.json`, `migrations/001_initial.sql`, `openapi.yaml`, ADR-001/002, `domain/*`, `application/casos_de_uso/*`, `adapters/*`, `bootstrap.py` y los nombres de las pruebas en `tests/` (conteo estático: 154 funciones en la versión confirmada y 218 en el árbol de trabajo con los cambios de T-008; **no se ejecutaron**, eso corresponde a T-008).
- Durante la revisión, el desarrollador (T-008) modificó `anemia_junin/` en paralelo (bandas de altitud no verificadas con advertencia, pruebas E2E HTTP, web y Locust, `python -m anemia_junin`, `datetime.now(UTC)`, versiones mínimas en lugar de fijas). El entregable describe ese árbol de trabajo (§8.4) y lo señala como no confirmado en git.
- Script de validación: todas las tablas Markdown del entregable y del checklist tienen un número de columnas coherente; sin base64 ni emojis; imágenes con rutas relativas `../../diagramas/svg/…`.
- Ruta crítica recalculada a mano sobre la Tabla 22 (28 días, holguras en la Tabla 24) y verificada contra la simulación de reunión y la matriz de seguimiento.

## Incremento prioritario tal como quedó (INC-1, PMV)

| ID | Título | Criterios de aceptación (resumen) |
| --- | --- | --- |
| HIST-1.1 (HU-01) | Registrar niño | Datos válidos → 201 con expediente único; DNI existente → 409; dosaje inicial opcional clasificado en la misma transacción (si falla, no se guarda nada); cada intento queda en la auditoría sin datos personales del rechazado |
| HIST-1.2 (HU-02) | Expediente y dosajes | GET por DNI con dosajes ordenados por fecha clínica (404 si no existe); PATCH solo de peso, distrito, altitud, cuidador y teléfono; identidad inmutable; actualización vacía rechazada; nuevo dosaje como evento inmutable; campos calculados del cliente rechazados |
| HIST-1.3 (HU-03) | Validar datos y clasificar la hemoglobina | Dato inválido → 400 con errores por campo y sin persistencia; Hb ajustada = observada − ajuste por altitud; umbrales 6-23 y 24-59 meses desde `config/normativa_v1.json`; < 6 meses o Hb ajustada negativa → NO_EVALUABLE con advertencia; banda de altitud no verificada (≥ 4000 msnm) → advertencia «solo referencial» (T-008); la app no arranca si el JSON es inválido |
| HIST-1.4 (HU-04) | Listado en seguimiento | Solo 6-59 meses; orden SEVERA > MODERADA > LEVE > NO_EVALUABLE > SIN_DOSAJE > SIN_ANEMIA; filtros texto, distrito y clasificación; paginación ≤ 100; SIN_DOSAJE ≠ SIN_ANEMIA |
| HIST-1.5 (HU-05) | Reporte del periodo | `desde`/`hasta` obligatorios, inclusivos, en hora de Lima; conteos y distribución por clasificación y distrito; tasa = aceptados ÷ (aceptados + rechazados) × 100, «no calculable» si no hay intentos |
| Habilitador | API REST `/api/v1` + `openapi.yaml` | Los mismos casos de uso que la interfaz web |

## Pendientes y riesgos

- Figuras 1-6 → DIAG-100 a DIAG-105 (el rango NN 30-35 se eligió para no chocar con el 10-15 del otro revisor).
- Discrepancias con el código → DEV-100.
- Cadena normativa NTS 134 → NTS 213-2024 → INV-001 (ya abierta en T-002).
- `[PENDIENTE]` en el entregable: acta H1, cifras reales de pruebas y cobertura (T-008), horas reales y meta del indicador de calidad del registro.
- Riesgo de coherencia: S5 (T-005) y el integrador (T-006) deben usar los mismos HIST/HU, el mismo archivo normativo (`normativa_v1.json`, no `norma_nts213_2024.json`) y las mismas cifras.

## Solicitudes abiertas a otros agentes

- `coordinacion/solicitudes/DIAG-100.md` — Diagrama de actividades del proceso → `diagramas/svg/30_s34_flujo_actividades_proceso.svg`
- `coordinacion/solicitudes/DIAG-101.md` — WBS → `diagramas/svg/31_s34_wbs_proyecto.svg`
- `coordinacion/solicitudes/DIAG-102.md` — Gantt del INC-1 → `diagramas/svg/32_s34_gantt_incremento1.svg`
- `coordinacion/solicitudes/DIAG-103.md` — Cronograma de 8 sprints e hitos → `diagramas/svg/33_s34_cronograma_sprints_hitos.svg`
- `coordinacion/solicitudes/DIAG-104.md` — Red y ruta crítica → `diagramas/svg/34_s34_red_ruta_critica_inc1.svg`
- `coordinacion/solicitudes/DIAG-105.md` — Burndown del Sprint 1 → `diagramas/svg/35_s34_burndown_sprint1.svg`
- `coordinacion/solicitudes/DEV-100.md` — Discrepancias documento-código (11 puntos)
