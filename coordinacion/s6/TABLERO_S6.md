# Tablero S6: cierre del integrador

- **Rama:** `feature/s6-integrador-final`
- **Protocolo:** `coordinacion/s6/PROTOCOLO_S6.md`
- **Requisitos:** `coordinacion/s6/REQUISITOS_S6.md`
- **Datos:** `coordinacion/s6/DATOS_PMV_FASTAPI.md`
- **Estados:** `PENDIENTE` · `EN CURSO` · `BLOQUEADA` · `EN REVISIÓN` · `HECHO`. Las solicitudes usan `ABIERTA` · `EN CURSO` · `RESUELTA` · `RECHAZADA`.
- **Edición:** cada agente cambia solo el estado y la nota de **su** fila. El `sincronizador` crea las filas nuevas.

## Tareas

| ID | Tarea | Responsable | Estado | Entradas | Salida exacta | Depende de | Notas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S6-01 | Extraer requisitos de la consigna S6 (R-01 a R-91) y datos verificables del PMV FastAPI y de S1–S5 | sincronizador | HECHO (2026-10-01) | `guias/S6.CONSIGNA…INTEGRADOR.md`, `pmv_fastapi/`, `entregables/` | `coordinacion/s6/REQUISITOS_S6.md`, `DATOS_PMV_FASTAPI.md`, `CONTEXTO_PROCESOS_S1_S5.md` | — | 91 requisitos en 7 bloques; 10 contradicciones (C-01 a C-10) |
| S6-02 | Definir agentes S6, protocolo, tablero, rutas, README y VIS iniciales | sincronizador | HECHO (2026-10-01) | S6-01 | `.claude/agents/*.md`, `coordinacion/s6/PROTOCOLO_S6.md`, este tablero, `coordinacion/RUTAS.md`, `README.md`, `coordinacion/s6/solicitudes/VIS-001…016.md` | S6-01 | `orquestador` y `diagramador` archivados en `archivo/agentes-anteriores/` |
| S6-03 | Reescribir el Informe Integrador con la estructura de la consigna y el PMV FastAPI | redactor-informe-integrador | PENDIENTE | REQUISITOS (B, C), DATOS, CONTEXTO, SVG existentes | `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md` | S6-01; VIS (puede usar marcadores) | Antes de sobrescribir, el sincronizador archiva la versión Flask en `archivo/versiones-anteriores/semana-06-integrador/`. Eliminar `CARGA_CIERRE`, `[PENDIENTE]`, "tag pendiente" y las cifras Flask |
| S6-04 | Crear las 7 diapositivas (Marp), el guion de 7 min y el script PPTX/PDF | disenador-diapositivas | PENDIENTE | REQUISITOS (D), informe S6-03, VIS de diapositivas | `entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md`, `…/presentacion/Guion_Defensa_7min.md`, `herramientas/conversion/generar_presentacion.*`, `exportados/semana-06/Presentacion_Integrador.{pptx,pdf}` | S6-03, VIS-001/002/003/007–010/012/013 | marp-cli o python-pptx: instalarlos requiere permiso del usuario |
| S6-05 | Exportar el informe a PDF y DOCX | conversor-entregas | PENDIENTE | informe S6-03 inspeccionado | `exportados/semana-06/Informe_Integrador_Anemia_Junin.{pdf,docx}`, `herramientas/conversion/` | S6-03, S6-06 (primera pasada) | pandoc no está instalado; alternativa en Python con permiso |
| S6-06 | Inspección del 100 % de cumplimiento y pasos manuales | inspector-guia | PENDIENTE | REQUISITOS, informe, diapositivas, exportados, repositorio | `coordinacion/s6/INSPECCION_S6.md`, `coordinacion/s6/PASOS_MANUALES.md` | S6-03, S6-04, S6-05 | Se repite tras cada corrección |
| S6-07 | Verificación previa al merge con origin/main | guardian-merge | PENDIENTE | rama de trabajo, `origin/main`, `.gitignore` | `coordinacion/s6/CHECK_MERGE.md` | S6-06 | Sin push ni force |
| S6-08 | Mover o duplicar el CI a `.github/workflows/ci.yml` en la raíz (`working-directory: pmv_fastapi`) y reproducir las evidencias si el entorno lo permite | desarrollador | PENDIENTE | `pmv_fastapi/.github/workflows/ci.yml`, DATOS §10 | `.github/workflows/ci.yml` (raíz); evidencias en `pmv_fastapi/docs/evidencias/` | — | Contradicción C-02. La ejecución en verde en GitHub es un PASO MANUAL (requiere push del usuario) |
| S6-09 | Atender las solicitudes VIS-001 a VIS-016 (PNG + SVG en `diagramas/`) | recursos-visuales | PENDIENTE | `coordinacion/s6/solicitudes/VIS-*.md` | `diagramas/{src,png,svg}/50…68_s6_*` y `diagramas/README.md` | — | `plantuml.jar` no está en `herramientas/plantuml/`. Descargarlo solo de Maven Central y con permiso del usuario |
| S6-10 | Actualizar `README.md` raíz y `coordinacion/TABLERO.md` al estado real | sincronizador | HECHO (2026-10-01) | estado del repositorio | `README.md`, `coordinacion/TABLERO.md` | S6-01 | DIAG-001…006 y DIAG-100…105 cerradas (los SVG existen) |
| S6-11 | Decidir si S5 (`entregables/semana-05/…`) se actualiza al PMV FastAPI o se declara como antecedente Flask | usuario → revisor-documental | BLOQUEADA | DATOS C-03 | `entregables/semana-05/Entregable_Semana5_Anemia_Junin.md` | decisión del usuario | Contiene `CARGA_CIERRE` (l.107) y `[PENDIENTE]` |
| S6-12 | Pasos manuales: portada, video, ensayo, staging, subida al aula, push/PR | personas del equipo | PENDIENTE | `coordinacion/s6/PASOS_MANUALES.md` | evidencias indicadas en cada paso | S6-06 | El tag `v1.0-PMV` ya existe (9ce90c3). No moverlo sin decisión del usuario (C-01) |

## Solicitudes VIS

| ID | Recurso | Uso | Prioridad | Estado | Salida prevista |
| --- | --- | --- | --- | --- | --- |
| VIS-001 | Comparativo AS-IS reactivo vs. TO-BE preventivo + cadena de valor + indicador | Diap. 1 · Inf. §2.1 | Alta | ABIERTA | `50_s6_as_is_vs_to_be` |
| VIS-002 | Ciclo de vida adaptado (tailoring) con rechazo de Cascada y de Scrum puro | Diap. 2 · Inf. §2.2 | Alta | ABIERTA | `51_s6_ciclo_vida_tailoring` |
| VIS-003 | C4 N1, N2 y N3 del PMV FastAPI | Diap. 3 · Inf. §3.2 | Alta | ABIERTA | `52/53/54_s6_c4_*_fastapi` |
| VIS-004 | Modelo de datos PostgreSQL | Inf. §3.2 | Alta | ABIERTA | `55_s6_modelo_datos_postgresql` |
| VIS-005 | Paquetes hexagonales + secuencia de registro HU-01/HU-03 | Inf. §3.2 | Media | ABIERTA | `56_s6_paquetes_hexagonal_fastapi`, `57_s6_secuencia_registro_hu01` |
| VIS-006 | Despliegue Docker Compose + pipeline CI | Inf. §3.4 · Diap. 5 | Alta | ABIERTA | `58_s6_despliegue_docker_ci` |
| VIS-007 | Pirámide de pruebas (62/11/4 + carga) | Diap. 4 · Inf. §3.3 | Alta | ABIERTA | `59_s6_piramide_pruebas` |
| VIS-008 | Cobertura por módulo (99 %, umbral del 80 %) | Diap. 4 · Inf. §3.3 | Alta | ABIERTA | `60_s6_cobertura` |
| VIS-009 | Carga: p95 y req/s antes y después de DEF-01 | Diap. 4 · Inf. §3.3 | Alta | ABIERTA | `61_s6_carga_p95` |
| VIS-010 | Dashboard de proceso + producto + valor | Diap. 6 · Inf. §2.3/§4 | Alta | ABIERTA | `62_s6_tablero_metricas` |
| VIS-011 | Burndown/burnup real del INC-1 (historial git del tag) | Diap. 6 · Inf. §2.3 | Media | ABIERTA | `63_s6_burnup_inc1` |
| VIS-012 | Flujo de trazabilidad Problema → Proceso → Arquitectura → Pruebas → Valor | Diap. 7 · Inf. §4 | Alta | ABIERTA | `64_s6_flujo_trazabilidad` |
| VIS-013 | Collage de capturas de la demo | Diap. 5 | Media | ABIERTA | `65_s6_collage_demo` |
| VIS-014 | Cuadro ADR → NFR | Diap. 3 · Inf. §3.2 | Media | ABIERTA | `66_s6_adr_nfr` |
| VIS-015 | Matriz visual de factores del proyecto | Diap. 2 · Inf. §2.2 | Media | ABIERTA | `67_s6_matriz_factores` |
| VIS-016 | Hoja de ruta de incrementos (siguiente: INC-2) | Diap. 7 · Inf. §5 | Baja | ABIERTA | `68_s6_roadmap_incrementos` |

**Figuras existentes que se reutilizan sin una VIS nueva:**

| Figura | Uso |
| --- | --- |
| `diagramas/svg/10_s1_proceso_as_is.svg` | AS-IS, Inf. §2.1 |
| `diagramas/svg/11_s1_proceso_to_be.svg` | TO-BE, Inf. §2.1 |
| `diagramas/svg/12_s1_cadena_valor.svg` | Cadena de valor, Inf. §2.1 |
| `diagramas/svg/15_s2_modelo_proceso_aplicado.svg` | Modelo de proceso aplicado, Inf. §2.2 |
| `diagramas/svg/30_s34_flujo_actividades_proceso.svg` | Flujo de actividades, Inf. §2.3 |
| `diagramas/svg/31_s34_wbs_proyecto.svg` | WBS, Inf. §2.3 |
| `diagramas/svg/32_s34_gantt_incremento1.svg` | Gantt del INC-1, Inf. §2.3 |
| `diagramas/svg/33_s34_cronograma_sprints_hitos.svg` | Cronograma de sprints e hitos, Inf. §2.3 |
| `diagramas/svg/34_s34_red_ruta_critica_inc1.svg` | Red y ruta crítica del INC-1, Inf. §2.3 |
| `diagramas/svg/35_s34_burndown_sprint1.svg` | Burndown simulado, rotulado así, Inf. §2.3 |

Las figuras `diagramas/svg/03`–`09` y `40` describen el prototipo Flask y **no** se usan como figuras del PMV (C-05).

## Historial

- 2026-10-01 — sincronizador:
  - creó la rama `feature/s6-integrador-final`;
  - creó REQUISITOS_S6, DATOS_PMV_FASTAPI y CONTEXTO_PROCESOS_S1_S5;
  - definió los agentes S6 y archivó los antiguos;
  - creó el protocolo, el tablero y las solicitudes VIS-001…016;
  - actualizó RUTAS, TABLERO y README.
