# Mapa canónico de rutas

Fuente única de verdad sobre **dónde vive cada cosa**. Todas las rutas son relativas a la raíz del repositorio.
Si un agente necesita crear una ruta nueva, lo pide al `orquestador` mediante una solicitud (`coordinacion/solicitudes/ORQ-###.md`); solo el orquestador edita este archivo.

## Reglas generales

1. **Una sola versión vigente por entregable**, sin sufijo de versión en el nombre (`Entregable_SemanaN_Anemia_Junin.md`). El historial lo guarda git.
2. Las versiones anteriores y material obsoleto se **mueven** (con `git mv`) a `archivo/`; nunca se borran.
3. Los entregables se escriben siempre en **Markdown** (`.md`, UTF-8). Los PDF/DOCX son derivados y viven en `exportados/`.
4. Las imágenes se enlazan con **rutas relativas**; nunca se incrustan en base64.
5. Los diagramas se incrustan en los `.md` en **SVG** (`../../diagramas/svg/<nombre>.svg` desde `entregables/semana-XX/`). El PNG es para vista previa y para la conversión a DOCX.
6. Nombres de archivo: sin espacios ni tildes; `snake_case` o `Palabras_Con_Guion_Bajo`; prefijo numérico `NN_` en diagramas.

## Guías del docente (solo lectura)

| Semana | Ruta |
| --- | --- |
| S1 | `guias/S1_Guia_trabajo_semana_1.md` |
| S2 | `guias/S2_Guia_trabajo_semana_2.md` |
| S3-4 | `guias/S3-4_Guia_trabajo_semanas_3_y_4.md` |
| S5 | *No hay guía en el repositorio.* Requisitos de S5 = consigna S6, secciones 3.1 a 3.4 + `entregables/semana-05/Informe_Actividad5_PMV_AnemiaJunin.pdf` |
| S6 (integrador) | `guias/S6_Consigna_e_instrumento_evaluacion_integrador.pdf` (original) y `guias/S6_Consigna_integrador_extraccion.md` (texto extraído) |

## Entregables vigentes

| Semana | Entregable vigente (.md) | Anexos / insumos |
| --- | --- | --- |
| S1 | `entregables/semana-01/Entregable_Semana1_Anemia_Junin.md` (ex v5) | `entregables/semana-01/img/image1..11.png`, `entregables/semana-01/anexos/Entrevista.md` |
| S2 | `entregables/semana-02/Entregable_Semana2_Anemia_Junin.md` (ex v2 `.docx.md`) | `entregables/semana-02/img/image1.png` |
| S3-4 | `entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md` (ex v1) | — |
| S5 | `entregables/semana-05/Entregable_Semana5_Anemia_Junin.md` (**POR CREAR**) | `entregables/semana-05/Informe_Actividad5_PMV_AnemiaJunin.pdf`, `entregables/semana-05/_extraccion_Informe_Actividad5.md` |
| S6 | `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md` | `entregables/semana-06-integrador/anexos/Revision_Cumplimiento_y_Trazabilidad.md`, `entregables/semana-06-integrador/anexos/Prompts_y_guion_de_defensa.md` |

Checklists de cumplimiento del revisor: `entregables/semana-XX/CHECKLIST_cumplimiento.md`.

## Diagramas

| Contenido | Ruta |
| --- | --- |
| Fuentes PlantUML (`.puml`) | `diagramas/src/*.puml` |
| Generadores Python | `diagramas/src/*.py` y `diagramas/src/integrador/` (generador ReportLab del informe integrador: `diagramas.py`, `contenido.py`, `generar.py`) |
| PNG (visualización / DOCX) | `diagramas/png/NN_nombre.png` |
| SVG (incrustar en .md) | `diagramas/svg/NN_nombre.svg` |
| Intermedios regenerables (ignorado por git) | `diagramas/_build/` |
| Catálogo de diagramas | `diagramas/README.md` |

## Software (PMV)

| Contenido | Ruta |
| --- | --- |
| Proyecto Python/Flask (hexagonal) | `anemia_junin/` |
| Código fuente | `anemia_junin/src/anemia_junin/` |
| Pruebas | `anemia_junin/tests/` |
| ADR | `anemia_junin/docs/adr/` |
| README de ejecución | `anemia_junin/README.md` (**POR CREAR** por el desarrollador) |

## Exportaciones para el aula virtual

| Contenido | Ruta |
| --- | --- |
| PDF / DOCX finales | `exportados/semana-XX/<NombreEntregable>.pdf|.docx` |
| Scripts de conversión (plantilla DOCX, CSS, scripts) | `herramientas/conversion/` (se crea cuando el conversor lo necesite) |

## Coordinación entre agentes

| Contenido | Ruta |
| --- | --- |
| Tablero de tareas | `coordinacion/TABLERO.md` |
| Este mapa | `coordinacion/RUTAS.md` |
| Protocolo | `coordinacion/PROTOCOLO.md` |
| Solicitudes entre agentes | `coordinacion/solicitudes/<PREFIJO>-###.md` |
| Informes de salida | `coordinacion/informes/AAAA-MM-DD_<agente>_<tarea>.md` |
| Plantillas | `coordinacion/plantillas/` |

## Archivo (histórico, solo lectura)

| Contenido | Ruta |
| --- | --- |
| Versiones anteriores de entregables | `archivo/versiones-anteriores/semana-XX/` |
| PDF generados anteriormente (integrador/revisión) + LEEME original | `archivo/pdf-generados/` |
| Verificaciones antiguas | `archivo/verificaciones/` |
| Paquetes ZIP entregados | `archivo/zip/` |
| Material de trabajo de la revisión anterior (capturas QA, textos extraídos, PDF de diagramas) | `archivo/tmp-revision/` |
