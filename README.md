# Sistema de detección temprana y seguimiento de anemia infantil — Junín, Perú

Proyecto de la asignatura **Procesos de Software** (ASUC01702, Universidad Continental, ciclo 2026-20).

El problema organizacional: en las zonas rurales de Junín el tamizaje de hemoglobina, el tratamiento con hierro y el seguimiento de niños con anemia se pierden por falta de trazabilidad, baja adherencia, poca proactividad y conectividad limitada. El proyecto diseña el proceso TO-BE, selecciona y adapta un modelo de proceso de software (iterativo-incremental con Scrum y prácticas DevOps) y construye un **PMV** (Incremento 1: registro nominal validado y expediente digital) con arquitectura hexagonal en Python/Flask.

**Equipo:** Porras Veli, Ricardo (Ingeniero de Proceso) · Auqui Huincho, Tania (Ingeniero de Desarrollo y Prototipado) · Huamani Rodriguez, Jean Piero (Ingeniero de Calidad y Mejora del Proceso).

> Todos los datos del software son **sintéticos**. La clasificación de anemia que muestra el sistema es referencial y no reemplaza el criterio del profesional de salud.

## Historias de usuario del producto

Software: [`pmv_fastapi/`](pmv_fastapi/) (FastAPI + PostgreSQL/SQLite, arquitectura hexagonal). Usuario principal: personal de salud de la posta (enfermería). Las historias provienen del plan de S3-4 (HIST-1.x = HU-0x en el PMV) y cada una se trazó a un requerimiento funcional (RF) en el entregable de la semana 9.

### Incremento 1 — PMV: registro nominal y expediente digital (`v1.0-PMV`)

| HU | RF | Como… quiero… para… | Criterio de aceptación (Dado-Cuando-Entonces) | Interfaz / API | Estado |
| --- | --- | --- | --- | --- | --- |
| HU-01 | RF-01 | Como enfermera, quiero registrar a un niño con su evaluación inicial, para tener un expediente único en lugar del triple registro manual | Dado un formulario con datos válidos, cuando se pulsa «Guardar registro», entonces el sistema almacena el registro, muestra confirmación y abre el expediente en < 2 s (DNI repetido → 409) | Pestaña «Registrar niño» · `POST /api/ninos` | ✅ |
| HU-02 | RF-02 | Como enfermera, quiero consultar y actualizar el expediente y agregar nuevos controles, para ver la evolución del niño | Dado un expediente existente, cuando se consulta, se actualizan campos permitidos y se agrega un nuevo control, entonces persisten los cambios, el historial anterior se conserva y hay confirmación en < 2 s | Pestaña «Expediente» · `GET/PATCH /api/ninos/{id}`, `POST /api/ninos/{id}/evaluaciones` | ✅ |
| HU-03 | RF-03 | Como enfermera, quiero que el sistema valide los datos y calcule la Hb ajustada por altitud y la clasificación, para no cometer errores de digitación ni de cálculo | Dado un formulario con datos clínicos, cuando se digita la Hb, entonces la vista previa muestra la Hb ajustada y la clasificación; y cuando los datos son inválidos, se rechaza con mensaje comprensible por campo (422) | Vista previa en el registro · `POST /api/validaciones/evaluacion` | ✅ |
| HU-04 | RF-04 | Como enfermera, quiero listar a los niños en seguimiento con su estado de control, para priorizar la atención del día | Dado un conjunto de niños en seguimiento, cuando se filtra por clasificación o se busca por comunidad, entonces el listado respeta el filtro y muestra el estado de control de cada niño en < 2 s | Pestaña «Seguimiento» · `GET /api/ninos` | ✅ |
| HU-05 | RF-05 | Como responsable del programa, quiero un reporte del periodo en JSON y CSV, para informar a la microred sin redigitar | Dado un periodo válido, cuando se pulsa «Generar», entonces se muestran los indicadores del periodo y se puede descargar el mismo conjunto como CSV, en < 2 s | Pestaña «Reporte» · `GET /api/reportes/periodo` | ✅ |

### Incremento 2 — Agenda automática y alertas (`v2.0-Inc2`, 18/18 SP)

| HU | RF | SP | Como… quiero… para… | Criterio de aceptación (Dado-Cuando-Entonces) | Interfaz / API | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| HIST-2.1 | RF-06 | 5 | Como enfermera, quiero que el sistema genere la agenda de controles según el esquema normativo, para no calcular las fechas a mano | Dado un niño con anemia en tratamiento, cuando se abre su expediente, entonces el sistema muestra la agenda normativa de controles con el estado de cada uno (cumplido/pendiente/próximo/vencido) en < 2 s | «Agenda de controles» del expediente · `GET /api/ninos/{id}/agenda` | ✅ |
| HIST-2.2 | RF-07 | 5 | Como enfermera, quiero ver los controles vencidos priorizados, para recuperar a los niños antes de que abandonen el tratamiento | Dado un conjunto de niños con controles, cuando se abre la pestaña «Alertas» y se filtra por prioridad o comunidad, entonces se listan los controles vencidos priorizados con su resumen, en < 2 s | Pestaña «Alertas» · `GET /api/alertas/controles-vencidos`, `GET /api/alertas/resumen` | ✅ |
| HIST-2.3 | RF-08 | 5 | Como personal del establecimiento, quiero ver la agenda de controles de un rango de días, para organizar el trabajo de la semana | Dado el personal de un establecimiento, cuando consulta la agenda de un rango de fechas (por defecto la semana de la fecha de referencia, máx. 31 días), entonces ve los controles programados por día (niño, control, tipo, estado), filtrables por establecimiento y comunidad, con totales por día, en < 2 s | Pestaña «Agenda» · `GET /api/agenda` | ✅ |
| HIST-2.4 | RF-09 | 3 | Como enfermera, quiero registrar si el niño asistió o no a su control, para que la agenda y las alertas reflejen lo que realmente pasó | Dado un control programado, cuando se registra «asistió» (opcionalmente con la evaluación del día) o «no asistió» con motivo, entonces se guarda con usuario y fecha, la agenda y las alertas se actualizan (no asistió → marca de inasistencia y mayor prioridad), y no se permite registrar dos veces el mismo control (409) ni fechas futuras (422) | Botones «Asistió» / «No asistió» · `POST /api/ninos/{id}/controles/{codigo}/asistencia`, `GET /api/ninos/{id}/asistencias` | ✅ |

### Incremento 3 — Sin conexión, sincronización y visita priorizada (`3.0.0-inc3`)

| HU | RF | SP | Como… quiero… para… | Criterio de aceptación (Dado-Cuando-Entonces) | Interfaz / API | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| HIST-3.1 | RNF disponibilidad | — | Como enfermera de una posta sin internet, quiero registrar niños, evaluaciones, asistencias y visitas, para no perder el trabajo ni redigitarlo | Dado que no hay conexión, cuando registro un niño, una evaluación, una asistencia o una visita, entonces el registro se guarda en el dispositivo con un identificador único, la pantalla confirma «guardado en el dispositivo» y la aplicación sigue abriendo aunque se recargue | Formularios y botones existentes + indicador de la cabecera · cola en IndexedDB y service worker | ✅ |
| HIST-3.2 | RNF disponibilidad | — | Como enfermera, quiero que lo registrado sin conexión se envíe al volver la red, para que el servidor tenga todos los datos sin duplicados | Dado que hay registros pendientes, cuando vuelve la conexión (o pulso «Sincronizar ahora»), entonces cada uno se aplica una sola vez, el indicador pasa a «Al día» y el niño aparece una sola vez; y si el mismo registro se envía de nuevo, el servidor responde que ya existía y no crea nada | Evento «online» y botón «Sincronizar ahora» · `POST /api/sincronizacion` | ✅ |
| HIST-3.3 | RNF integridad | — | Como enfermera, quiero decidir qué dato queda cuando el servidor ya tenía uno distinto, para no perder ni pisar información clínica | Dado un registro que choca con otro del servidor (mismo DNI con datos distintos, misma evaluación o asistencia con valor distinto), cuando se sincroniza, entonces no se sobrescribe nada, el conflicto queda pendiente con ambos datos a la vista y puedo conservar el del servidor, aplicar el mío (solo donde el dominio lo permite; nunca nombres, apellidos, sexo ni fecha de nacimiento) o descartarlo | Pestaña «Sincronización» · `GET /api/sincronizacion/conflictos`, `POST /api/sincronizacion/conflictos/{id}/resolver` | ✅ |
| HIST-3.4 | RNF usabilidad | — | Como enfermera, quiero ver cuánto falta por sincronizar y desde cuándo, para saber si puedo confiar en que mis datos ya llegaron | Dado un dispositivo con registros pendientes, cuando miro la cabecera o abro «Sincronización», entonces veo el número de pendientes, la lista (tipo, resumen, hora local, último intento y error), la hora de la última sincronización exitosa y los conflictos por resolver | Indicador de la cabecera y pestaña «Sincronización» | ✅ |
| VIS-3.5 | brecha B4 | — | Como personal de salud, quiero una lista de a qué familias visitar primero con el motivo de cada puesto, para usar bien las visitas disponibles | Dado el conjunto de niños en tratamiento, cuando abro «Visitas», entonces veo la lista ordenada por un puntaje de 0 a 100 cuyos componentes (severidad, control vencido, inasistencias de los últimos 90 días y tiempo desde la última visita) se explican al pulsarlo, y puedo registrar la visita (fecha, resultado, si consume el suplemento, observaciones), también sin conexión; los pesos son una propuesta del equipo, no una norma del MINSA | Pestaña «Visitas» · `GET /api/visitas/priorizadas`, `POST/GET /api/ninos/{id}/visitas` | ✅ |

Decisiones: [ADR-012](pmv_fastapi/docs/adr/ADR-012-sincronizacion-sin-conexion.md) y [ADR-013](pmv_fastapi/docs/adr/ADR-013-visita-domiciliaria-priorizada.md). Qué SQL ejecutar al migrar: [`pmv_fastapi/docs/DESPLIEGUE.md`](pmv_fastapi/docs/DESPLIEGUE.md).

**Datos.** La demo usa una muestra estratificada de 500 niños del dataset público «Niños menores de 36 meses con dx de anemia en la Región Junín» (DIRESA Junín, fuente HIS; carpeta [`Dataset/`](Dataset/)), importada con código seudónimo y sin datos personales, con la fecha de referencia fijada en el corte del dataset (30/06/2024). Los niños registrados desde la aplicación exigen todos sus campos. Detalle en [`pmv_fastapi/README.md`](pmv_fastapi/README.md) y en el ADR-009.

## Estructura del repositorio

```
.
├── README.md                    este archivo
├── AGENTS.md                    instrucciones de continuidad para agentes
├── .claude/agents/              definiciones de los subagentes
├── coordinacion/                canal de comunicación entre agentes
│   ├── TABLERO.md               tareas, estado y responsable
│   ├── RUTAS.md                 mapa canónico de rutas (fuente de verdad)
│   ├── PROTOCOLO.md             reglas de comunicación
│   ├── plantillas/              SOLICITUD, SOLICITUD_DIAGRAMA, INFORME, CHECKLIST_CUMPLIMIENTO
│   ├── solicitudes/             <PREFIJO>-###.md (DIAG, DOC, DEV, INV, CONV, ORQ)
│   └── informes/                informes de salida de cada agente
├── guias/                       guías y consigna del docente (solo lectura)
├── entregables/                 versión VIGENTE de cada entregable (.md)
│   ├── semana-01/               + img/, anexos/Entrevista.md
│   ├── semana-02/               + img/
│   ├── semana-03-04/
│   ├── semana-05/               PDF Actividad 5 + extracción de texto (entregable .md por crear)
│   └── semana-06-integrador/    + anexos/
├── diagramas/                   src/ (puml, py) · png/ · svg/ · README.md (catálogo)
├── pmv_fastapi/                 software evaluado: PMV e Incremento 2 (FastAPI, arquitectura hexagonal)
├── Dataset/                     dataset público de la DIRESA Junín (HIS, anonimizado) y su diccionario
├── herramientas/                scripts de medición GQM, análisis del dataset y conversión de documentos
├── anemia_junin/                primer prototipo (Flask); histórico
├── exportados/                  PDF/DOCX generados para el aula virtual
└── archivo/                     histórico: versiones anteriores, PDFs generados, zip, material de revisión
```

El detalle de cada ruta está en [`coordinacion/RUTAS.md`](coordinacion/RUTAS.md).

## Entregables por semana

| Semana | Tema (según guía) | Guía | Entregable vigente | Estado |
| --- | --- | --- | --- | --- |
| S1 | Enfoque de procesos de la organización: problema, actores, AS-IS, brechas, TO-BE, aporte del software, cadena de valor, indicadores | [`guias/S1_…`](guias/S1.Gu%C3%ADa%20de%20trabajo%20semana%201.md) | [`Entregable_Semana1`](entregables/semana-01/Entregable_Semana1_Anemia_Junin.md) | Revisado; faltan figuras (T-002) |
| S2 | Selección y justificación del modelo de proceso de software, representación, incrementos, riesgos, herramientas | [`guias/S2_…`](guias/S2.Gu%C3%ADa%20de%20trabajo%20semana%202.md) | [`Entregable_Semana2`](entregables/semana-02/Entregable_Semana2_Anemia_Junin.md) | Revisado; falta figura (T-003) |
| S3-4 | Actividades, organización, responsabilidades, productos, WBS, priorización, estimación y plan del proyecto | [`guias/S3-4_…`](guias/S3.GU%C3%8DA%20DE%20TRABAJO%20SEMANA%203%20Y%204.md) | [`Entregable_Semana3y4`](entregables/semana-03-04/Entregable_Semana3y4_Anemia_Junin.md) | Revisado; pendientes diagramas y conciliación técnica (T-004, T-007) |
| S5 | Ejecución de procesos principales del PMV: requisitos, diseño, construcción, pruebas y despliegue | [Guía S5](guias/S5-PSW-GU%C3%8DA%20DE%20TRABAJO%20SEMANA%205.md) | `entregables/semana-05/Entregable_Semana5_Anemia_Junin.md` — **por crear**; base: [PDF Actividad 5](entregables/semana-05/Informe_Actividad5_PMV_AnemiaJunin.pdf), [extracción](entregables/semana-05/_extraccion_Informe_Actividad5.md) | Por crear (T-005) |
| S6 | Informe integrador de las Unidades I y II | [Consigna S6](guias/S6.CONSIGNA%20DE%20TRABAJO%20E%20INSTRUMENTO%20DE%20EVALUACI%C3%93N%20INTEGRADOR.md) | [`Informe_Integrador`](entregables/semana-06-integrador/Informe_Integrador_Anemia_Junin.md) | Propuesta de revisión — por actualizar (T-006) |
| S9 | Evaluación GQM del proceso y producto: arquitectura hexagonal, pruebas Inc. 1 y 2 con capturas, entrega de valor (Inc. 2 completo `v2.0.0-inc2` y dataset real de la DIRESA Junín) | [Guía S9](guias/S9-PSW-GU%C3%8DA%20DE%20TRABAJO.md) | [`Entregable_Semana9`](entregables/semana-09/Entregable_Semana9_Anemia_Junin.md) · [checklist](entregables/semana-09/CHECKLIST_CUMPLIMIENTO_S9.md) · PDF/DOCX en `exportados/semana-09/` | En revisión (T-011); pendiente que el equipo cree el tag `v2.0-Inc2` (Anexo B) |

Las versiones anteriores están en `archivo/versiones-anteriores/`. El historial completo se conserva en git (`git log --follow <ruta>`).

## Agentes y comunicación

Para retomar con la IA de cualquier integrante, comenzar por [`.claude/CLAUDE.md`](.claude/CLAUDE.md) y el [contexto actual](.claude/CONTEXTO_ACTUAL.md). Las preguntas, propuestas y traspasos se pueden escribir en [`.claude/intercambios/`](.claude/intercambios/README.md), con autor y tarea, usando su plantilla. El tablero, las solicitudes formales y los informes siguen en `coordinacion/`. Los archivos se comparten entre equipos mediante Git.

| Agente | Modelo | Rol |
| --- | --- | --- |
| `orquestador` | opus | Estructura, rutas, README, tablero, archivo, commits |
| `revisor-documental` | opus | Cumplimiento estricto al 100 % de cada guía, redacción, checklist de cumplimiento |
| `diagramador` | opus | Diagramas con PlantUML/Python → PNG + SVG, fuentes en `diagramas/src` |
| `desarrollador` | opus (Fable 5.1 sin créditos de uso; se usa Opus 5.5) | PMV `anemia_junin/`: código, pruebas, evidencias, README de ejecución |
| `investigador` | haiku | Investigación y resúmenes con fuentes (solo lectura) |
| `conversor-entregas` | opus | Conversión .md → PDF/DOCX en `exportados/` |

Definiciones: `.claude/agents/<agente>.md`. La coordinación formal se registra **por archivos** en `coordinacion/`, complementada por los intercambios compartidos de `.claude/`:

1. Las tareas (`T-###`) se registran en [`coordinacion/TABLERO.md`](coordinacion/TABLERO.md).
2. Un agente que necesita algo de otro crea `coordinacion/solicitudes/<PREFIJO>-###.md` desde la plantilla (p. ej. el revisor pide un diagrama con `DIAG-001.md`). El prefijo indica quién atiende: `ORQ`, `DOC`, `DIAG`, `DEV`, `INV`, `CONV`.
3. El agente destino responde en la misma solicitud (rutas producidas) y la marca `RESUELTA`.
4. Al terminar, cada agente deja su informe en `coordinacion/informes/AAAA-MM-DD_<agente>_<tarea>.md` y actualiza el tablero.

Reglas completas: [`coordinacion/PROTOCOLO.md`](coordinacion/PROTOCOLO.md).

## Convertir Markdown a PDF / DOCX

Ejecutar desde la carpeta del entregable para que se resuelvan las imágenes relativas.

**Con pandoc** (instalar en Windows: `winget install --id JohnMacFarlane.Pandoc`; para PDF se necesita además un motor, p. ej. MiKTeX para `xelatex`):

```bash
cd entregables/semana-01
pandoc Entregable_Semana1_Anemia_Junin.md -o ../../exportados/semana-01/Entregable_Semana1_Anemia_Junin.docx --toc
pandoc Entregable_Semana1_Anemia_Junin.md -o ../../exportados/semana-01/Entregable_Semana1_Anemia_Junin.pdf \
  --pdf-engine=xelatex -V lang=es -V mainfont="Arial" -V geometry:margin=2.5cm --toc
```

Para DOCX conviene usar las versiones PNG de los diagramas (`diagramas/png/`), ya que Word no siempre renderiza SVG.

**Alternativa sin pandoc (Python):**

```bash
pip install markdown python-docx xhtml2pdf
# Markdown → HTML (markdown) → PDF (xhtml2pdf); DOCX con python-docx
```

El agente `conversor-entregas` automatiza ambos caminos y guarda los resultados en `exportados/semana-XX/`.

## Cómo ejecutar el software

Desde la raíz del repositorio, en PowerShell:

```powershell
cd anemia_junin
python -m venv .venv                 # solo si aún no existe
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest --cov --cov-report=term-missing
.\.venv\Scripts\python.exe -m anemia_junin
```

Abrir `http://127.0.0.1:8000/`. Instrucciones completas y carga de datos sintéticos: [README del PMV](anemia_junin/README.md).

Revisión local T-010 (2026-09-25, Python 3.13.7): **242 pruebas aprobadas, cobertura 96,66 %, Ruff sin hallazgos**. Se detectó además un defecto de entrada numérica fuera de la suite (DEV-101). La evidencia de carga conservada corresponde a la ejecución anterior; no se volvió a ejecutar en esta revisión.

Informe y pendientes priorizados: [revisión del avance](coordinacion/informes/2026-09-25_orquestador_T-010.md). Los porcentajes de los checklists anteriores no certifican que el proyecto esté listo para entregar.

## Herramientas registradas en el equipo anterior (2026-09-25)

Inventario histórico; no representa necesariamente este equipo. La revisión T-010 utilizó Python 3.13.7.

| Herramienta | Estado |
| --- | --- |
| Python 3.14.6 + pip 26.1 | Disponible (pypdf instalado) |
| Java (OpenJDK 17.0.19, Temurin) | Disponible |
| Git 2.54 | Disponible |
| PlantUML (`plantuml.jar`) | No instalado |
| Graphviz (`dot`) | No instalado |
| Pandoc | No instalado |
