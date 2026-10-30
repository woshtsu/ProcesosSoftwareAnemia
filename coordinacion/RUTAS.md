# Mapa canónico de rutas

## Producción y CI/CD (ORQ-008)

- `.github/workflows/ci.yml`: CI del monorepositorio y solicitud de despliegue de main en Render; reemplaza por traslado `pmv_fastapi/.github/workflows/ci.yml`.
- `pmv_fastapi/docs/DESPLIEGUE.md`: instrucciones Supabase, GitHub Actions y Render.
- `pmv_fastapi/db/02_supabase.sql`: protección del esquema frente a Data API; ejecutar después de `01_esquema_postgresql.sql`.

## Contexto y coordinación compartida entre IA (ORQ-007)

- Entrada común: `.claude/CLAUDE.md`.
- Resumen vigente de continuidad: `.claude/CONTEXTO_ACTUAL.md`.
- Canal de mensajes: `.claude/intercambios/README.md` y `.claude/intercambios/<T-###>_<autor>_<tema>.md`.
- Plantilla de mensajes: `.claude/plantillas/INTERCAMBIO.md`.
- Los estados de tareas, rutas, solicitudes formales e informes siguen en `coordinacion/`; el protocolo admite el canal adicional de intercambios.

## Autenticación Supabase (ORQ-006)

Previsualizaciones temporales del login: `diagramas/_build/auth/` (ignoradas por Git).

Modelo `pmv_fastapi/app/domain/model/autenticacion.py`; puertos `pmv_fastapi/app/ports/inbound/sesiones.py` y `pmv_fastapi/app/ports/outbound/proveedor_identidad.py`; servicio `pmv_fastapi/app/application/servicio_sesion.py`; proveedor `pmv_fastapi/app/adapters/outbound/supabase_auth.py`; HTTP `pmv_fastapi/app/adapters/inbound/http/autenticacion.py`; cliente `pmv_fastapi/app/web/auth.js`; configuración `pmv_fastapi/.env.example`; pruebas `pmv_fastapi/tests/integracion/test_autenticacion.py` y `pmv_fastapi/tests/e2e/test_login.py`; decisión `pmv_fastapi/docs/adr/ADR-011-supabase-auth.md`.

## Síntesis para feria de proyectos (ORQ-005)

- Fuente vigente: `entregables/feria/Proyecto_Feria_Anemia_Junin.md`.
- PDF de participación: `exportados/feria/Proyecto_Feria_Anemia_Junin.pdf`.
- Generador reproducible: `herramientas/conversion/exportar_feria.py`.
- Previsualizaciones y revisión visual: `diagramas/_build/feria/` (ignorado por Git).

Fuente única de verdad sobre **dónde vive cada cosa**. Todas las rutas son relativas a la raíz del repositorio.
Si un agente necesita crear una ruta nueva, lo pide al `orquestador` mediante una solicitud (`coordinacion/solicitudes/ORQ-###.md`); solo el orquestador edita este archivo.

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
| S5 | `entregables/semana-05/Entregable_Semana5_Anemia_Junin.md` (**POR CREAR**) | `entregables/semana-05/Informe_Actividad5_PMV_AnemiaJunin.pdf`, `entregables/semana-05/_extraccion_Informe_Actividad5.md` |
| S6 | `entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md` | `entregables/semana-06-integrador/anexos/Revision_Cumplimiento_y_Trazabilidad.md`, `entregables/semana-06-integrador/anexos/Prompts_y_guion_de_defensa.md` |

Checklists de cumplimiento del revisor: `entregables/semana-XX/CHECKLIST_CUMPLIMIENTO_S<n>.md` (p. ej. `semana-01/CHECKLIST_CUMPLIMIENTO_S1.md`).

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
| README de ejecución | `anemia_junin/README.md` (existente; verificación local en T-010) |

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

## Instrucciones de continuidad

- `AGENTS.md`: entrada para agentes de programación; remite a este mapa, al protocolo y al tablero. Alta registrada en `coordinacion/solicitudes/ORQ-001.md`.
- Los informes históricos mantienen las rutas que existían al emitirlos; para trabajar se consultan las rutas actuales de este mapa.

## Rutas de cierre autorizadas mediante ORQ-002

- `entregables/semana-06-integrador/Presentacion_Integrador_Anemia_Junin.md`: contenido y guion de siete diapositivas.
- `exportados/semana-06-integrador/Presentacion_Integrador_Anemia_Junin.pptx` y `.pdf`: presentación.
- `herramientas/conversion/`: generadores reproducibles de documentos y presentación.
- `diagramas/_build/cierre/`: borradores y verificaciones visuales regenerables.
- `anemia_junin/docs/evidencias/cierre/`: capturas y mediciones de la sesión actual.
- `anemia_junin/scripts/verificar_navegador.py`: prueba de aceptación técnica en Chromium con capturas.
- `archivo/versiones-anteriores/semana-06-integrador/`: integrador anterior a la conciliación del cierre.
- `exportados/LEEME_ENTREGA.md`: índice del paquete y campos pendientes del equipo.

## Rutas de la Semana 9 (ORQ-003)

Figura heredada del avance 1.5, conservada al resolver el merge (ORQ-004): `diagramas/src/72_s9_hexagonal_v15.dot`, `diagramas/png/72_s9_hexagonal_v15.png` y `diagramas/svg/72_s9_hexagonal_v15.svg`. La figura vigente del Incremento 2 completo sigue siendo `72_s9_hexagonal_v20`.

| Contenido | Ruta |
| --- | --- |
| Guía S9 | `guias/S9-PSW-GUÍA DE TRABAJO.md` |
| Entregable vigente | `entregables/semana-09/Entregable_Semana9_Anemia_Junin.md` |
| Checklist de cumplimiento | `entregables/semana-09/CHECKLIST_CUMPLIMIENTO_S9.md` |
| Capturas por RF (Actividad 5) | `entregables/semana-09/evidencias_capturas/RF-0X/`, `arquitectura/`, `INDICE.md`, `capturar_evidencias.py` |
| Métricas GQM (datos, salidas crudas, gráficos) | `entregables/semana-09/metricas/{datos,salidas,graficos}/`, `metricas/README.md`, `metricas/instrumento_SUS.md` |
| Scripts de medición GQM | `herramientas/gqm/` |
| Conversión MD → DOCX/PDF | `herramientas/conversion/exportar_s9.py` |
| Exportados | `exportados/semana-09/Entregable_Semana9_Anemia_Junin.docx` y `.pdf` |
| Diagramas S9 | `diagramas/{src,png,svg}/70_s9_cadena_trazabilidad`, `71_s9_arbol_gqm`, `72_s9_hexagonal_v20` |
| Avance del Inc. 2 (v1.5.0-inc2-avance) | `pmv_fastapi/` (estructura `app/domain/{model,service}`, `app/ports/{inbound,outbound}`, `app/application`, `app/adapters/{inbound,outbound}`), `pmv_fastapi/CHANGELOG.md`, `pmv_fastapi/docs/adr/ADR-007*`, `ADR-008*`, `pmv_fastapi/docs/evidencias/registro_defectos_inc2.md`, `pmv_fastapi/docs/evidencias/inc2/` |

| Dataset DIRESA Junín (insumo, anonimizado en origen) | `Dataset/` (CSV y diccionario); importador `pmv_fastapi/scripts/importar_dataset_diresa.py`; análisis `herramientas/dataset/analisis_asis.py` |

## Rutas de la Semana 11 (ORQ-009)

| Contenido | Ruta |
| --- | --- |
| Guía S11 (CMMI-DEV) | `guias/S11-PSW-GUÍA DE TRABAJO 11.docx` |
| Entregable vigente | `entregables/semana-11/Entregable_Semana11_Anemia_Junin.md` |
| Evidencias reutilizadas | `entregables/semana-09/evidencias_capturas/` y `entregables/semana-09/metricas/` |
| Exportado PDF | `exportados/semana-11/Entregable_Semana11_Anemia_Junin.pdf` |
| Generador del PDF (Markdown → HTML → Chrome/Edge) | `herramientas/conversion/exportar_s11.py` |
| Reportes exportados del anexo (Ruff, cobertura y pruebas del 30/10/2026) | `entregables/semana-11/anexos/ruff.txt` y `entregables/semana-11/anexos/cobertura_y_pruebas.txt` |
