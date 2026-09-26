# Tablero de coordinación

Protocolo: `coordinacion/PROTOCOLO.md` · Rutas: `coordinacion/RUTAS.md` · Plantillas: `coordinacion/plantillas/`

Estados: `PENDIENTE` · `EN CURSO` · `BLOQUEADA` · `EN REVISIÓN` · `HECHO`

## Tareas

| ID | Tarea | Agente | Estado | Entradas | Salida esperada | Depende de | Notas / informe |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-001 | Reestructurar repositorio, definir agentes, protocolo y README | orquestador | HECHO (2026-09-25) | repo original | estructura actual, `.claude/agents/`, `coordinacion/`, `README.md` | — | `coordinacion/informes/2026-09-25_orquestador_T-001.md` |
| T-002 | Revisión S1: cumplimiento 100 % frente a la guía S1, mejora de redacción, checklist | revisor-documental | PENDIENTE | `guias/S1_Guia_trabajo_semana_1.md`, `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md`, `entregables/semana-01/anexos/Entrevista.md` | entregable S1 corregido + `entregables/semana-01/CHECKLIST_cumplimiento.md` | — | Figuras S1 son PNG sin fuente: evaluar si alguna debe rehacerse (→ DIAG). Revisar también la sección 9 (UML complementarios). |
| T-003 | Revisión S2: cumplimiento 100 % frente a la guía S2, checklist | revisor-documental | PENDIENTE | `guias/S2_Guia_trabajo_semana_2.md`, `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md`, `archivo/verificaciones/verificacion_s2_y_guia_uml.md` | entregable S2 corregido + `entregables/semana-02/CHECKLIST_cumplimiento.md` | — | La guía exige un diagrama del modelo de proceso adaptado al proyecto (no genérico): verificar `img/image1.png`; si no cumple → DIAG. |
| T-004 | Revisión S3-4: cumplimiento 100 % frente a la guía S3-4, checklist | revisor-documental | PENDIENTE | `guias/S3-4_Guia_trabajo_semanas_3_y_4.md`, `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` | entregable S3-4 corregido + `entregables/semana-03-04/CHECKLIST_cumplimiento.md` | T-007 (diagramas) | El documento contiene bloques de texto/ASCII y notas "📌 UML — ..." (actividad, casos de uso, secuencia, componentes) que deben sustituirse por diagramas reales. |
| T-005 | Crear entregable S5 a partir del PDF de Actividad 5 y de la consigna S6 §3.1-3.4 | revisor-documental | PENDIENTE | `entregables/semana-05/Informe_Actividad5_PMV_AnemiaJunin.pdf`, `entregables/semana-05/_extraccion_Informe_Actividad5.md`, `guias/S6_Consigna_integrador_extraccion.md` (§3.1 categorización y sastrería, §3.2 arquitectura INC-1, §3.3 pruebas, §3.4 despliegue y demostración), `anemia_junin/` | `entregables/semana-05/Entregable_Semana5_Anemia_Junin.md` + `CHECKLIST_cumplimiento.md` | T-008 (verificación del software) para cifras de pruebas | **Discrepancia detectada**: el PDF de Actividad 5 describe "sin frameworks", `unittest` y `tools/*.py` (`tools/sembrar_datos.py`, `tools/lint.py`, `tools/diagramas.py`), pero el código del repo usa Flask + pytest y `scripts/cargar_datos_sinteticos.py`. No copiar cifras sin verificarlas contra T-008. |
| T-006 | Actualizar integrador S6 con S1-S5 revisados y consigna S6 completa | revisor-documental | PENDIENTE | `guias/S6_Consigna_e_instrumento_evaluacion_integrador.pdf`, `guias/S6_Consigna_integrador_extraccion.md`, `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md`, anexos | integrador actualizado + `entregables/semana-06-integrador/CHECKLIST_cumplimiento.md` | T-002..T-005, T-007, T-008 | Pendientes heredados (ver `archivo/pdf-generados/LEEME_entregable_integrador_original.md`): portada, repositorio/tag, evidencia de E2E, carga, aceptación de usuario, presentación. Encabezados de sección duplicados ("2.1", "2.2", "3.2" repetidos). |
| T-007 | Diagramas faltantes (S2 modelo de proceso si no cumple; S3-4 actividad, casos de uso, secuencia A07, componentes, WBS/Gantt; S5 C4/despliegue/estrategia de pruebas actualizados al código real) | diagramador | PENDIENTE | solicitudes `DIAG-###` del revisor; `anemia_junin/src/` | `diagramas/src/`, `diagramas/png/`, `diagramas/svg/` + catálogo en `diagramas/README.md` | solicitudes del revisor | Herramientas: Java 17 disponible; **faltan** `plantuml.jar` y Graphviz (`dot`) — instalar/descargar de fuente oficial con permiso del usuario, o usar PlantUML con layout `smetana` (no requiere Graphviz). Los 9 diagramas del integrador (ReportLab) deben contrastarse con el código real. |
| T-008 | Verificar y ejecutar el PMV: instalar, correr pruebas, cobertura, levantar la app; completar `anemia_junin/README.md` y sección "Cómo ejecutar" del README raíz | desarrollador | PENDIENTE | `anemia_junin/`, `guias/S3-4_Guia_trabajo_semanas_3_y_4.md`, `entregables/semana-03-04/...md`, `entregables/semana-05/_extraccion_Informe_Actividad5.md` | `anemia_junin/README.md`, evidencias en `anemia_junin/docs/evidencias/`, informe con cifras reales | — | Python local 3.14 (pyproject pide ≥3.12 y fija versiones: verificar compatibilidad). `tests/e2e/` y `tests/carga/` están vacíos. No existe punto de entrada documentado (`bootstrap.crear_app`). |
| T-009 | Convertir entregables finales a PDF/DOCX para el aula virtual | conversor-entregas | BLOQUEADA | `entregables/semana-XX/*.md` revisados | `exportados/semana-XX/*.pdf` y `*.docx` | T-002..T-006 | Pandoc **no instalado**; alternativa Python (ver README). |

## Solicitudes abiertas

| ID | Solicitante → Destino | Tema | Estado | Archivo |
| --- | --- | --- | --- | --- |
| — | — | — | — | — |

## Historial

- 2026-09-25 — orquestador: reestructuración inicial del repositorio (T-001).
