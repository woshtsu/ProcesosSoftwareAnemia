# Tablero de coordinación

Protocolo: `coordinacion/PROTOCOLO.md` · Rutas: `coordinacion/RUTAS.md` · Plantillas: `coordinacion/plantillas/`

> **Cierre S6 en curso (desde 2026-10-01):** el detalle vive en [`coordinacion/s6/TABLERO_S6.md`](s6/TABLERO_S6.md), con su protocolo en [`coordinacion/s6/PROTOCOLO_S6.md`](s6/PROTOCOLO_S6.md). **PMV oficial: `pmv_fastapi/`** (FastAPI + PostgreSQL, tag `v1.0-PMV`). `anemia_junin/` (Flask) es el antecedente. Las tareas T-005 a T-009 se reformulan en S6-03 a S6-11.

Estados: `PENDIENTE` · `EN CURSO` · `BLOQUEADA` · `EN REVISIÓN` · `HECHO`

## Tareas

| ID | Tarea | Agente | Estado | Entradas | Salida esperada | Depende de | Notas / informe |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-001 | Reestructurar repositorio, definir agentes, protocolo y README | orquestador | HECHO (2026-09-25) | repo original | estructura actual, `.claude/agents/`, `coordinacion/`, `README.md` | — | `coordinacion/informes/2026-09-25_orquestador_T-001.md` |
| T-002 | Revisión S1: cumplimiento 100 % frente a la guía S1, mejora de redacción, checklist | revisor-documental | EN REVISIÓN (2026-09-25) | `guias/S1.Guía de trabajo semana 1.md`, `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md`, `entregables/semana-01/anexos/Entrevista.md` | entregable S1 corregido + `entregables/semana-01/CHECKLIST_CUMPLIMIENTO_S1.md` | — | `coordinacion/informes/2026-09-25_revisor-documental_T-002_T-003.md` — Checklist actual: 96,3 % (evaluación heredada). Pendiente: DIAG-001..005. INV-001 está RESUELTA; no se auditó su contenido clínico en T-010. |
| T-003 | Revisión S2: cumplimiento 100 % frente a la guía S2, checklist | revisor-documental | EN REVISIÓN (2026-09-25) | `guias/S2.Guía de trabajo semana 2.md`, `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md`, `archivo/verificaciones/verificacion_s2_y_guia_uml.md` | entregable S2 corregido + `entregables/semana-02/CHECKLIST_CUMPLIMIENTO_S2.md` | — | `coordinacion/informes/2026-09-25_revisor-documental_T-002_T-003.md` — 84,5 % → 98,0 %. Pendiente: DIAG-006. |
| T-004 | Revisión S3-4: cumplimiento 100 % frente a la guía S3-4, checklist | revisor-documental | EN REVISIÓN (2026-09-25) | `guias/S3.GUÍA DE TRABAJO SEMANA 3 Y 4.md`, `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` | entregable S3-4 corregido + `entregables/semana-03-04/CHECKLIST_CUMPLIMIENTO_S3-4.md` | T-007 (diagramas) | Cumplimiento 51,4 % → 99,1 % (estricto). Checklist: `entregables/semana-03-04/CHECKLIST_CUMPLIMIENTO_S3-4.md`. Figuras pendientes DIAG-100..105; discrepancias con el código en DEV-100. Informe: `coordinacion/informes/2026-09-25_revisor-documental_T-004.md` |
| T-005 | Crear entregable S5 según guía S5: matrices 1.1, 2.1, 3.1, 4.1 y 5.1, diagramas y evidencias | revisor-documental | BLOQUEADA → S6-11 (2026-10-01): el entregable existe pero describe Flask; el usuario debe decidir si se actualiza al PMV FastAPI | `guias/S5-PSW-GUÍA DE TRABAJO SEMANA 5.md`, `entregables/semana-05/Informe_Actividad5_PMV_AnemiaJunin.pdf`, `entregables/semana-05/_extraccion_Informe_Actividad5.md`, `guias/S6.CONSIGNA DE TRABAJO E INSTRUMENTO DE EVALUACIÓN INTEGRADOR.md` (§3.1 categorización y sastrería, §3.2 arquitectura INC-1, §3.3 pruebas, §3.4 despliegue y demostración), `anemia_junin/` | `entregables/semana-05/Entregable_Semana5_Anemia_Junin.md` + `CHECKLIST_cumplimiento.md` | T-008 (verificación del software) para cifras de pruebas | **Discrepancia detectada**: el PDF de Actividad 5 describe "sin frameworks", `unittest` y `tools/*.py` (`tools/sembrar_datos.py`, `tools/lint.py`, `tools/diagramas.py`), pero el código del repo usa Flask + pytest y `scripts/cargar_datos_sinteticos.py`. No copiar cifras sin verificarlas contra T-008. |
| T-006 | Actualizar integrador S6 con S1-S5 revisados y consigna S6 completa | redactor-informe-integrador (antes revisor-documental) | REASIGNADA → S6-03 (2026-10-01) | `guias/S6.CONSIGNA DE TRABAJO E INSTRUMENTO DE EVALUACIÓN INTEGRADOR.md`, `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md`, anexos | integrador actualizado + `entregables/semana-06-integrador/CHECKLIST_cumplimiento.md` | T-002..T-005, T-007, T-008 | Pendientes heredados (ver `archivo/pdf-generados/LEEME_entregable_integrador_original.md`): portada, repositorio/tag, evidencia de E2E, carga, aceptación de usuario, presentación. Encabezados de sección duplicados ("2.1", "2.2", "3.2" repetidos). |
| T-007 | Diagramas faltantes (S2 modelo de proceso si no cumple; S3-4 actividad, casos de uso, secuencia A07, componentes, WBS/Gantt; S5 C4/despliegue/estrategia de pruebas actualizados al código real) | recursos-visuales (antes diagramador) | HECHO para DIAG-001..006 y DIAG-100..105 (2026-10-01); C4/despliegue/datos del PMV FastAPI → VIS-003..006 (S6-09) | solicitudes `DIAG-###` del revisor; `anemia_junin/src/` | `diagramas/src/`, `diagramas/png/`, `diagramas/svg/` + catálogo en `diagramas/README.md` | solicitudes del revisor | Hay PNG y fuentes 10–12, pero faltan los 12 SVG enlazados por S1–S3/4. Completar DIAG-001..006 y DIAG-100..105; verificar las figuras contra el código. |
| T-008 | Verificar y ejecutar el PMV: instalar, correr pruebas, cobertura, levantar la app; completar `anemia_junin/README.md` y sección "Cómo ejecutar" del README raíz | desarrollador | CERRADA para Flask (antecedente) (2026-10-01); el PMV oficial `pmv_fastapi/` sigue en S6-08 (CI en la raíz) | `anemia_junin/`, `guias/S3.GUÍA DE TRABAJO SEMANA 3 Y 4.md`, `entregables/semana-03-04/...md`, `entregables/semana-05/_extraccion_Informe_Actividad5.md` | `anemia_junin/README.md`, evidencias en `anemia_junin/docs/evidencias/`, informe con cifras reales | — | Avance técnico verificado en T-010: README, entrypoint, E2E HTTP y carga existen; 242 pruebas/96,66 % reproducidos con Python 3.13.7. Falta informe de cierre y respuesta DEV-100; defecto adicional DEV-101. |
| T-009 | Convertir entregables finales a PDF/DOCX para el aula virtual | conversor-entregas | REASIGNADA → S6-05 (2026-10-01) | `entregables/semana-XX/*.md` revisados | `exportados/semana-XX/*.pdf` y `*.docx` | T-002..T-006 | Pandoc **no instalado**; alternativa Python (ver README). |
| T-010 | Revisar avance recibido, guías actualizadas y continuidad de estructura | orquestador | HECHO (2026-09-25) |
| T-011 | Cierre S6: requisitos, datos del PMV FastAPI, agentes S6, protocolo, tablero S6 y solicitudes VIS | sincronizador | HECHO (2026-10-01) | consigna S6, `pmv_fastapi/`, entregables | `coordinacion/s6/*`, `.claude/agents/*`, RUTAS, README | — | Rama `feature/s6-integrador-final`. Seguimiento en `coordinacion/s6/TABLERO_S6.md` | commit b6c6db2, guias/, código y entregables | informe de revisión, rutas y tablero sincronizados | — | `coordinacion/informes/2026-09-25_orquestador_T-010.md`. Revisión completada; quedan tareas de implementación y entrega. |

## Solicitudes abiertas

| ID | Solicitante → Destino | Tema | Estado | Archivo |
| --- | --- | --- | --- | --- |
| DIAG-001 | revisor-documental → diagramador | S1 proceso AS-IS por carriles (`10_s1_proceso_as_is`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-001.md` |
| DIAG-002 | revisor-documental → diagramador | S1 proceso TO-BE con mejoras M1-M6 (`11_s1_proceso_to_be`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-002.md` |
| DIAG-003 | revisor-documental → diagramador | S1 cadena de valor (`12_s1_cadena_valor`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-003.md` |
| DIAG-004 | revisor-documental → diagramador | S1 casos de uso visión TO-BE (`13_s1_casos_uso_vision`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-004.md` |
| DIAG-005 | revisor-documental → diagramador | S1 clases del dominio visión TO-BE (`14_s1_clases_dominio_vision`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-005.md` |
| DIAG-006 | revisor-documental → diagramador | S2 modelo de proceso aplicado (`15_s2_modelo_proceso_aplicado`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-006.md` |
| INV-001 | revisor-documental → investigador | Vigencia NTS 134 vs. NTS 213-2024 (esquema de tamizaje S1) | RESUELTA | `coordinacion/solicitudes/INV-001.md` |
| DIAG-100 | revisor-documental → diagramador | S3-4 diagrama de actividades del proceso (`30_s34_flujo_actividades_proceso`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-100.md` |
| DIAG-101 | revisor-documental → diagramador | S3-4 WBS (`31_s34_wbs_proyecto`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-101.md` |
| DIAG-102 | revisor-documental → diagramador | S3-4 Gantt del INC-1 (`32_s34_gantt_incremento1`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-102.md` |
| DIAG-103 | revisor-documental → diagramador | S3-4 cronograma de sprints e hitos (`33_s34_cronograma_sprints_hitos`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-103.md` |
| DIAG-104 | revisor-documental → diagramador | S3-4 red y ruta crítica del INC-1 (`34_s34_red_ruta_critica_inc1`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-104.md` |
| DIAG-105 | revisor-documental → diagramador | S3-4 burndown del Sprint 1 (`35_s34_burndown_sprint1`) | RESUELTA (2026-10-01; SVG, PNG y fuente existen) | `coordinacion/solicitudes/DIAG-105.md` |
| DEV-100 | revisor-documental → desarrollador | Discrepancias documento-código detectadas en T-004 (11 puntos) | EN CURSO | `coordinacion/solicitudes/DEV-100.md` |
| DEV-101 | orquestador → desarrollador | Entradas numéricas no finitas/desbordadas producen HTTP 500 | ABIERTA | `coordinacion/solicitudes/DEV-101.md` |
| ORQ-001 | orquestador → orquestador | Registrar AGENTS.md y adoptar las guías descargadas | RESUELTA | `coordinacion/solicitudes/ORQ-001.md` |
| ORQ-002 | — | Rutas de cierre (presentación/exportados) | SUSTITUIDA (2026-10-01) por las rutas S6 de `coordinacion/RUTAS.md` | `coordinacion/solicitudes/ORQ-002.md` |
| VIS-001..016 | sincronizador → recursos-visuales | Recursos visuales del informe y de las 7 diapositivas S6 | ABIERTAS | `coordinacion/s6/solicitudes/` (detalle en `coordinacion/s6/TABLERO_S6.md`) |

## Historial

- 2026-09-25 — orquestador: reestructuración inicial del repositorio (T-001).
- 2026-09-25 — revisor-documental: revisión S1 (T-002) y S2 (T-003); checklists y solicitudes DIAG-001..006, INV-001.
- 2026-09-25 — revisor-documental: revisión S3-4 (T-004); checklist, solicitudes DIAG-100..105 y DEV-100.
- 2026-09-25 — orquestador (Codex), T-010: revisión del avance, rutas de guías actualizadas, pruebas reproducidas, defecto DEV-101 y continuidad mediante AGENTS.md. S1–S3/4 pasan a EN REVISIÓN por pendientes efectivos; el cierre histórico no equivale a aceptación final.
- 2026-10-01 — sincronizador, T-011:
  - PMV oficial = `pmv_fastapi/`; rama `feature/s6-integrador-final`;
  - DIAG-001..006 y DIAG-100..105 cerradas porque sus SVG, PNG y fuentes existen (los marcadores `<!-- DIAG-### pendiente -->` de S1 quedan para revisor-documental);
  - orquestador y diagramador archivados en `archivo/agentes-anteriores/`;
  - tareas S6 en `coordinacion/s6/TABLERO_S6.md`.
