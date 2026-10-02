# Mapa canónico de rutas

Fuente única de verdad sobre **dónde vive cada cosa**. Todas las rutas son relativas a la raíz del repositorio.
Si un agente necesita crear una ruta nueva, se la pide al `sincronizador` (antes, `orquestador`) mediante una solicitud `coordinacion/solicitudes/ORQ-###.md`. Solo el sincronizador edita este archivo.

## Reglas generales

1. **Una sola versión vigente por entregable**, sin sufijo de versión en el nombre (`Entregable_SemanaN_Anemia_Junin.md`). El historial lo guarda git.
2. Las versiones anteriores y material obsoleto se **mueven** (con `git mv`) a `archivo/`; nunca se borran.
3. Los entregables se escriben siempre en **Markdown** (`.md`, UTF-8). Los PDF/DOCX son derivados y viven en `exportados/`.
4. Las imágenes se enlazan con **rutas relativas**; nunca se incrustan en base64.
5. Los diagramas se incrustan en los `.md` en **SVG** (`../../diagramas/svg/<nombre>.svg` desde `entregables/semana-XX/`). El PNG es para vista previa y para la conversión a DOCX.
6. Las guías descargadas por el usuario conservan su nombre original, incluidos espacios y tildes; son una excepción a la convención siguiente. Nombres de archivo: sin espacios ni tildes; `snake_case` o `Palabras_Con_Guion_Bajo`; prefijo numérico `NN_` en diagramas.

## Guías del docente (solo lectura)

| Semana | Ruta |
| --- | --- |
| S1 | `guias/S1.Guía de trabajo semana 1.md` |
| S2 | `guias/S2.Guía de trabajo semana 2.md` |
| S3-4 | `guias/S3.GUÍA DE TRABAJO SEMANA 3 Y 4.md` |
| S5 | `guias/S5-PSW-GUÍA DE TRABAJO SEMANA 5.md` (fuente primaria); complementar con consigna S6. El PDF de Actividad 5 es antecedente, no guía. |
| S6 (integrador) | `guias/S6.CONSIGNA DE TRABAJO E INSTRUMENTO DE EVALUACIÓN INTEGRADOR.md` (copia Markdown aportada por el usuario) |

## Entregables vigentes

| Semana | Entregable vigente (.md) | Anexos / insumos |
| --- | --- | --- |
| S1 | `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` (ex v5) | `entregables/semana-01/img/image1..11.png`, `entregables/semana-01/anexos/Entrevista.md` |
| S2 | `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md` (ex v2 `.docx.md`) | `entregables/semana-02/img/image1.png` |
| S3-4 | `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` (ex v1) | — |
| S5 | `entregables/semana-05/Entregable_Semana5_Anemia_Junin.md` (existe; describe el antecedente Flask; ver S6-11) | `entregables/semana-05/Informe_Actividad5_PMV_AnemiaJunin.pdf`, `entregables/semana-05/_extraccion_Informe_Actividad5.md` |
| S6 | `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md` | `entregables/semana-06-integrador/anexos/` (`Revision_Cumplimiento_y_Trazabilidad.md`, `Prompts_y_guion_de_defensa.md`); checklist: `entregables/semana-06-integrador/CHECKLIST_CUMPLIMIENTO_S6_INFORME.md`; presentación: `entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md` (fuente Marp, 7 diapositivas), guion `presentacion/GUION_EXPOSICION.md` y generador `presentacion/generar_presentacion.py` (python-pptx, ejecutar con `herramientas/.venv`) |

Checklists de cumplimiento del revisor: `entregables/semana-XX/CHECKLIST_CUMPLIMIENTO_S<n>.md` (p. ej. `semana-01/CHECKLIST_CUMPLIMIENTO_S1.md`).

## Diagramas

| Contenido | Ruta |
| --- | --- |
| Fuentes PlantUML (`.puml`) | `diagramas/src/*.puml` (rango `50–69_s6_*` reservado para las figuras S6) |
| Generadores Python | `diagramas/src/*.py` y `diagramas/src/integrador/` (generador ReportLab del informe integrador: `diagramas.py`, `contenido.py`, `generar.py`) |
| PNG (visualización / DOCX) | `diagramas/png/NN_nombre.png` |
| SVG (incrustar en .md) | `diagramas/svg/NN_nombre.svg` |
| Intermedios regenerables (ignorado por git) | `diagramas/_build/` |
| Catálogo de diagramas | `diagramas/README.md` |

## Software

### PMV oficial: `pmv_fastapi/` (FastAPI + PostgreSQL; tag `v1.0-PMV`)

| Contenido | Ruta |
| --- | --- |
| Código fuente (hexagonal) | `pmv_fastapi/app/` (`domain/`, `application/`, `adapters/`, `web/`, `main.py`) |
| Pruebas | `pmv_fastapi/tests/` (`unitarias/`, `integracion/`, `e2e/`, `rendimiento/locustfile.py`) |
| Base de datos | `pmv_fastapi/db/01_esquema_postgresql.sql`; datos sintéticos en `pmv_fastapi/scripts/cargar_datos_prueba.py` |
| ADR | `pmv_fastapi/docs/adr/ADR-001…006` |
| Contrato API | `pmv_fastapi/docs/openapi.json` |
| Evidencias | `pmv_fastapi/docs/evidencias/` (`cobertura.txt`, `ruff.txt`, `registro_defectos.md`, `carga/*.csv`, `capturas/01…08.png`, `demo_pmv.mp4`) |
| Diagramas propios (PNG y fuentes) | `pmv_fastapi/docs/diagramas/` (solo lectura para recursos-visuales, que los adapta a `diagramas/`) |
| Despliegue | `pmv_fastapi/Dockerfile`, `pmv_fastapi/docker-compose.yml`, `pmv_fastapi/sonar-project.properties` |
| CI efectivo (S6-08 hecha) | `.github/workflows/ci.yml` en la raíz del repositorio (`working-directory: pmv_fastapi`) |
| CI (copia de referencia; GitHub no lo ejecuta desde aquí) | `pmv_fastapi/.github/workflows/ci.yml` |
| Verificación local S6 | `pmv_fastapi/docs/evidencias/verificacion_s6_2026-10-01.md` |
| README de ejecución y despliegue | `pmv_fastapi/README.md` |

### Antecedente: `anemia_junin/` (prototipo Flask del Incremento 1, solo lectura)

| Contenido | Ruta |
| --- | --- |
| Proyecto Python/Flask (hexagonal) | `anemia_junin/` (`src/anemia_junin/`, `tests/`, `docs/adr/`, `docs/evidencias/`, `README.md`) |

## Exportaciones para el aula virtual

| Contenido | Ruta |
| --- | --- |
| PDF / DOCX finales | `exportados/semana-XX/<NombreEntregable>.pdf|.docx` |
| S6 (integrador) | `exportados/semana-06/Informe_Integrador_Anemia_Junin.pdf` y `.docx`; `exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pptx` y `.pdf` |
| Scripts de conversión (plantilla DOCX, CSS, scripts) | `herramientas/conversion/` (lo crea el conversor cuando lo necesita); el script de la presentación es `entregables/semana-06-integrador/presentacion/generar_presentacion.py` (disenador-diapositivas) |
| PlantUML local (no versionado) | `herramientas/plantuml/plantuml.jar` (solo desde Maven Central; ver `herramientas/README.md`) |
| Entorno Python de herramientas (no versionado) | `herramientas/.venv` (matplotlib, pillow, python-pptx); genera las figuras `59–67_s6` y el PPTX |

## Coordinación entre agentes

| Contenido | Ruta |
| --- | --- |
| Tablero de tareas | `coordinacion/TABLERO.md` |
| Este mapa | `coordinacion/RUTAS.md` |
| Protocolo | `coordinacion/PROTOCOLO.md` |
| Solicitudes entre agentes | `coordinacion/solicitudes/<PREFIJO>-###.md` |
| Informes de salida | `coordinacion/informes/AAAA-MM-DD_<agente>_<tarea>.md` |
| Plantillas | `coordinacion/plantillas/` (incluye `SOLICITUD_VIS.md`) |
| Definiciones de agentes | `.claude/agents/` (sincronizador, redactor-informe-integrador, disenador-diapositivas, recursos-visuales, inspector-guia, guardian-merge, conversor-entregas, desarrollador, revisor-documental, investigador) |

### Coordinación del cierre S6 (`coordinacion/s6/`)

| Contenido | Ruta | Escribe |
| --- | --- | --- |
| Requisitos de la consigna (R-01 a R-91) | `coordinacion/s6/REQUISITOS_S6.md` | sincronizador |
| Datos verificables del PMV | `coordinacion/s6/DATOS_PMV_FASTAPI.md` | sincronizador |
| Cifras de procesos S1–S5 | `coordinacion/s6/CONTEXTO_PROCESOS_S1_S5.md` | sincronizador |
| Protocolo S6 | `coordinacion/s6/PROTOCOLO_S6.md` | sincronizador |
| Tablero S6 | `coordinacion/s6/TABLERO_S6.md` | sincronizador (filas); cada agente edita el estado de su fila |
| Solicitudes de recursos visuales | `coordinacion/s6/solicitudes/VIS-###.md` | solicitante; *Respuesta*: recursos-visuales |
| Inspección de cumplimiento (existe; primera pasada) | `coordinacion/s6/INSPECCION_S6.md` | inspector-guia |
| Pasos manuales (existe; 18 pasos) | `coordinacion/s6/PASOS_MANUALES.md` | inspector-guia |
| Verificación previa al merge (por crear, S6-07) | `coordinacion/s6/CHECK_MERGE.md` | guardian-merge |
| Informes de trabajo S6 | `coordinacion/s6/informes/AAAA-MM-DD_<agente>[_<tarea>].md` | cada agente |

## Archivo (histórico, solo lectura)

| Contenido | Ruta |
| --- | --- |
| Versiones anteriores de entregables | `archivo/versiones-anteriores/semana-XX/` |
| PDF generados anteriormente (integrador/revisión) + LEEME original | `archivo/pdf-generados/` |
| Verificaciones antiguas | `archivo/verificaciones/` |
| Paquetes ZIP entregados | `archivo/zip/` |
| Material de trabajo de la revisión anterior (capturas QA, textos extraídos, PDF de diagramas) | `archivo/tmp-revision/` |
| Definiciones de agentes sustituidas (orquestador → sincronizador; diagramador → recursos-visuales) | `archivo/agentes-anteriores/` |

## Instrucciones de continuidad

- `AGENTS.md`: entrada para agentes de programación; remite a este mapa, al protocolo y al tablero. Alta registrada en `coordinacion/solicitudes/ORQ-001.md`.
- Los informes históricos mantienen las rutas que existían al emitirlos; para trabajar se consultan las rutas actuales de este mapa.

## Rutas de cierre autorizadas mediante ORQ-002 (SUSTITUIDAS el 2026-10-01)

> El 2026-10-01 el usuario fijó otras rutas para S6, que prevalecen: `entregables/semana-06-integrador/presentacion/Presentacion_Integrador.md` (fuente), `presentacion/GUION_EXPOSICION.md` (guion), `presentacion/generar_presentacion.py` (generador), `exportados/semana-06/Presentacion_Integrador_Anemia_Junin.pptx` (exportado) y `coordinacion/s6/`. Las rutas de presentación y de exportados que aparecen abajo son históricas y **no deben crearse**. Las rutas `anemia_junin/...` corresponden al antecedente Flask. Siguen vigentes `herramientas/conversion/`, `diagramas/_build/` y `archivo/versiones-anteriores/semana-06-integrador/`.

- `entregables/semana-06-integrador/Presentacion_Integrador_Anemia_Junin.md`: contenido y guion de siete diapositivas.
- `exportados/semana-06-integrador/Presentacion_Integrador_Anemia_Junin.pptx` y `.pdf`: presentación.
- `herramientas/conversion/`: generadores reproducibles de documentos y presentación.
- `diagramas/_build/cierre/`: borradores y verificaciones visuales regenerables.
- `anemia_junin/docs/evidencias/cierre/`: capturas y mediciones de la sesión actual.
- `anemia_junin/scripts/verificar_navegador.py`: prueba de aceptación técnica en Chromium con capturas.
- `archivo/versiones-anteriores/semana-06-integrador/`: integrador anterior a la conciliación del cierre.
- `exportados/LEEME_ENTREGA.md`: índice del paquete y campos pendientes del equipo.
